# building_geocoder.py
"""
Enhanced geocoder using extracted building locations.

This module:
1. Loads building locations from the generated JSON
2. Provides functions to match text descriptions to buildings
3. Returns precise geocoordinates for alert locations
"""

import json
import os
import re
from typing import Dict, Any, List, Tuple, Optional
from fuzzywuzzy import process, fuzz
import math
import random

# Default paths
BUILDING_LOCATIONS_FILE = "output/building_locations.json"
KNOWN_LOCATIONS_FILE = "known_locations.json"

# Default center of UCSD campus
DEFAULT_CENTER = (32.8801, -117.2340)
DEFAULT_ADDRESS = "UC San Diego, 9500 Gilman Dr, La Jolla, CA 92093"

class BuildingGeocoder:
    def __init__(self, 
                 building_locations_path=None, 
                 known_locations_path=None,
                 match_threshold=70):
        """
        Initialize the building geocoder with building locations data.
        
        Args:
            building_locations_path: Path to the building locations JSON file
            known_locations_path: Path to the known locations JSON file
            match_threshold: Threshold for fuzzy matching (0-100)
        """
        self.match_threshold = match_threshold
        self.building_locations = self._load_json(building_locations_path or BUILDING_LOCATIONS_FILE)
        self.known_locations = self._load_json(known_locations_path or KNOWN_LOCATIONS_FILE)
        
        # Combine both sources for comprehensive matching
        self.combined_locations = {}
        
        # Add building locations
        for name, info in self.building_locations.items():
            self.combined_locations[name.lower()] = {
                "name": name,
                "lat": info["lat"],
                "lng": info["lng"],
                "source": "building_locations",
                "pixels": info.get("pixels", [0, 0])
            }
        
        # Add known locations
        for name, info in self.known_locations.items():
            self.combined_locations[name.lower()] = {
                "name": name,
                "lat": info["lat"],
                "lng": info["lng"],
                "source": "known_locations",
                "address": info.get("address", DEFAULT_ADDRESS),
                "pixels": [0, 0]  # No pixel coordinates for known locations
            }
            
        # Prepare patterns for location extraction
        self._prepare_patterns()
    
    def _load_json(self, file_path: str) -> dict:
        """Load JSON data from a file, returning empty dict if file doesn't exist."""
        try:
            if os.path.exists(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                print(f"Warning: {file_path} not found. Using empty dictionary.")
                return {}
        except Exception as e:
            print(f"Error loading {file_path}: {e}")
            return {}
    
    def _prepare_patterns(self):
        """Prepare regex patterns for location matching."""
        # Common location patterns
        self.location_patterns = [
            # "at Location"
            re.compile(r"(?:at|in|near|by)\s+([A-Za-z0-9\s&\-,']+?)(?:\.|\,|\s+on|\s+in|\s+at|\s+near|$)"),
            # "Location Building/Hall/Center"
            re.compile(r"([A-Za-z0-9\s&\-,']+?)\s+(?:Building|Hall|Center|Complex|Library|College)(?:\.|\,|$)"),
            # "Specific address"
            re.compile(r"(\d+\s+[A-Za-z0-9\s&\-,']+?)(?:\.|\,|$)")
        ]
        
        # Create a list of all building names for direct matching
        self.building_names = list(self.combined_locations.keys())
    
    def _add_jitter(self, lat: float, lng: float, meters: int = 10) -> Tuple[float, float]:
        """Add a small random offset to coordinates for visual separation on maps."""
        # Convert meters to approximate degrees
        lat_jitter = (random.uniform(-meters, meters) / 111111)
        lng_jitter = (random.uniform(-meters, meters) / (111111 * abs(math.cos(math.radians(lat)))))
        
        return lat + lat_jitter, lng + lng_jitter
    
    def _extract_location_mentions(self, text: str) -> List[str]:
        """Extract potential location mentions from text."""
        if not text:
            return []
        
        mentions = []
        
        # Try direct matching first
        for name in self.building_names:
            if name in text.lower():
                mentions.append(name)
        
        # Apply regex patterns
        for pattern in self.location_patterns:
            matches = pattern.findall(text)
            mentions.extend([match.strip() for match in matches if match.strip()])
        
        return mentions
    
    def _find_best_match(self, location_text: str) -> Optional[Dict[str, Any]]:
        """Find the best match for a location in our combined locations."""
        # Check for exact matches first (case insensitive)
        location_lower = location_text.lower()
        if location_lower in self.combined_locations:
            return self.combined_locations[location_lower]
        
        # Try fuzzy matching
        matches = process.extract(
            location_lower,
            self.combined_locations.keys(),
            scorer=fuzz.token_sort_ratio,
            limit=5
        )
        
        # Get best match above threshold
        for match_name, score in matches:
            if score >= self.match_threshold:
                return self.combined_locations[match_name]
        
        return None
    
    def geocode(self, text: str) -> Dict[str, Any]:
        """
        Geocode a location description to coordinates.
        
        Args:
            text: Location description text
            
        Returns:
            Dictionary with geocoding result
        """
        if not text:
            return {
                "lat": DEFAULT_CENTER[0],
                "lng": DEFAULT_CENTER[1],
                "address": DEFAULT_ADDRESS,
                "building_name": "UC San Diego",
                "confidence": 0,
                "source": "default"
            }
        
        # First try direct matching with the full text
        match = self._find_best_match(text)
        
        if match:
            lat, lng = self._add_jitter(match["lat"], match["lng"])
            return {
                "lat": lat,
                "lng": lng,
                "address": match.get("address", DEFAULT_ADDRESS),
                "building_name": match["name"],
                "confidence": 100,
                "source": match["source"]
            }
        
        # Extract potential location mentions
        mentions = self._extract_location_mentions(text)
        
        for mention in mentions:
            match = self._find_best_match(mention)
            if match:
                lat, lng = self._add_jitter(match["lat"], match["lng"])
                return {
                    "lat": lat,
                    "lng": lng,
                    "address": match.get("address", DEFAULT_ADDRESS),
                    "building_name": match["name"],
                    "confidence": 80,
                    "source": match["source"]
                }
        
        # If no matches found, check if text contains "UCSD" or "UC San Diego"
        if re.search(r'\b(?:UCSD|UC\s+San\s+Diego)\b', text, re.IGNORECASE):
            # Random point on campus
            lat = random.uniform(32.8750, 32.8850)
            lng = random.uniform(-117.2400, -117.2300)
            return {
                "lat": lat,
                "lng": lng,
                "address": DEFAULT_ADDRESS,
                "building_name": "UC San Diego",
                "confidence": 50,
                "source": "campus_mention"
            }
        
        # Last resort - default to center with jitter
        lat, lng = self._add_jitter(DEFAULT_CENTER[0], DEFAULT_CENTER[1], meters=200)
        return {
            "lat": lat,
            "lng": lng,
            "address": DEFAULT_ADDRESS,
            "building_name": "Unknown Location",
            "confidence": 0,
            "source": "fallback"
        }
    
    def batch_geocode(self, alerts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Geocode a batch of alerts.
        
        Args:
            alerts: List of alert dictionaries
            
        Returns:
            Updated alerts with geocoded information
        """
        for alert in alerts:
            # Determine location text to use
            location_text = alert.get("location_text", "")
            
            # Also check precise_location if available
            if "precise_location" in alert and alert["precise_location"] and alert["precise_location"] != "Unknown":
                result1 = self.geocode(location_text)
                result2 = self.geocode(alert["precise_location"])
                
                # Use the better match (higher confidence)
                if result1["confidence"] > result2["confidence"]:
                    result = result1
                else:
                    result = result2
            else:
                result = self.geocode(location_text)
            
            # Update alert with geocoded info
            alert["lat"] = result["lat"]
            alert["lng"] = result["lng"]
            alert["address"] = result["address"]
            alert["building_name"] = result["building_name"]
            alert["geocode_confidence"] = result["confidence"]
            alert["geocode_source"] = result["source"]
        
        return alerts


def process_alerts_file(input_file, output_file, geocoder=None):
    """
    Process alerts JSON file with the building geocoder.
    
    Args:
        input_file: Path to input JSON file
        output_file: Path to output JSON file
        geocoder: Optional geocoder instance (will create one if None)
    """
    try:
        # Load alerts
        with open(input_file, 'r', encoding='utf-8') as f:
            alerts = json.load(f)
        
        print(f"Loaded {len(alerts)} alerts from {input_file}")
        
        # Initialize geocoder if not provided
        if geocoder is None:
            geocoder = BuildingGeocoder()
        
        # Process alerts
        updated_alerts = geocoder.batch_geocode(alerts)
        
        # Save updated alerts
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(updated_alerts, f, indent=2)
        
        print(f"Saved {len(updated_alerts)} geocoded alerts to {output_file}")
        
    except Exception as e:
        print(f"Error processing alerts: {e}")


def process_csv_alerts(input_file, output_file, geocoder=None):
    """
    Process alerts CSV file with the building geocoder.
    
    Args:
        input_file: Path to input CSV file
        output_file: Path to output CSV file
        geocoder: Optional geocoder instance (will create one if None)
    """
    import csv
    
    try:
        # Load alerts from CSV
        alerts = []
        with open(input_file, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                alerts.append(row)
        
        print(f"Loaded {len(alerts)} alerts from {input_file}")
        
        # Initialize geocoder if not provided
        if geocoder is None:
            geocoder = BuildingGeocoder()
        
        # Process each alert
        for alert in alerts:
            # Get location text
            location_text = alert.get("Location Address", "")
            
            # Geocode
            result = geocoder.geocode(location_text)
            
            # Update alert
            alert["Latitude"] = result["lat"]
            alert["Longitude"] = result["lng"]
            alert["Address"] = result["address"]
            alert["Building Name"] = result["building_name"]
            alert["Geocode Confidence"] = result["confidence"]
            alert["Geocode Source"] = result["source"]
        
        # Determine output fields
        fieldnames = list(alerts[0].keys())
        
        # Write to output CSV
        with open(output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(alerts)
        
        print(f"Saved {len(alerts)} geocoded alerts to {output_file}")
        
    except Exception as e:
        print(f"Error processing CSV alerts: {e}")


def convert_to_geojson(alerts, output_file):
    """
    Convert alerts to GeoJSON format.
    
    Args:
        alerts: List of alert dictionaries
        output_file: Path to output GeoJSON file
    """
    # Create feature collection
    feature_collection = {
        "type": "FeatureCollection",
        "features": []
    }
    
    # Create features for each alert
    for alert in alerts:
        # Extract coordinates
        try:
            lat = float(alert.get("lat", alert.get("Latitude", 0)))
            lng = float(alert.get("lng", alert.get("Longitude", 0)))
        except (ValueError, TypeError):
            # Skip alerts with invalid coordinates
            continue
        
        # Create properties from alert
        properties = {}
        for key, value in alert.items():
            if key not in ["lat", "lng", "Latitude", "Longitude"]:
                properties[key] = value
        
        # Create feature
        feature = {
            "type": "Feature",
            "geometry": {
                "type": "Point",
                "coordinates": [lng, lat]  # GeoJSON uses [lng, lat] order
            },
            "properties": properties
        }
        
        feature_collection["features"].append(feature)
    
    # Write to file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(feature_collection, f, indent=2)
    
    print(f"Saved {len(feature_collection['features'])} features to {output_file}")


def main():
    """Main function to demonstrate geocoder usage."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Geocode UCSD alerts using building locations')
    parser.add_argument('--json', help='Path to JSON alerts file')
    parser.add_argument('--csv', help='Path to CSV alerts file')
    parser.add_argument('--output-dir', default='output', help='Output directory')
    parser.add_argument('--threshold', type=int, default=70, help='Fuzzy matching threshold (0-100)')
    args = parser.parse_args()
    
    # Ensure output directory exists
    os.makedirs(args.output_dir, exist_ok=True)
    
    # Initialize geocoder
    geocoder = BuildingGeocoder(match_threshold=args.threshold)
    
    # Process JSON file if provided
    if args.json:
        output_file = os.path.join(args.output_dir, 'geocoded_alerts.json')
        process_alerts_file(args.json, output_file, geocoder)
        
        # Also create GeoJSON
        geojson_file = os.path.join(args.output_dir, 'geocoded_alerts.geojson')
        with open(output_file, 'r', encoding='utf-8') as f:
            alerts = json.load(f)
        convert_to_geojson(alerts, geojson_file)
    
    # Process CSV file if provided
    if args.csv:
        output_file = os.path.join(args.output_dir, 'geocoded_alerts.csv')
        process_csv_alerts(args.csv, output_file, geocoder)
    
    # If no files provided, show usage example
    if not args.json and not args.csv:
        print("Usage example:")
        location_text = "Incident occurred at Geisel Library entrance"
        result = geocoder.geocode(location_text)
        print(f"Location: {location_text}")
        print(f"Geocoded to: {result['building_name']} ({result['lat']}, {result['lng']})")
        print(f"Confidence: {result['confidence']}%")
        print(f"Source: {result['source']}")


if __name__ == "__main__":
    main()