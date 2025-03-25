# geocode.py
"""
Geocoding services for the Safe Campus Agent.
Provides functions to convert location text to coordinates.
"""

import os
import logging
import json
import re
from typing import Dict, Any, List, Optional, Tuple, Union
import time
import random
import math

from geocoding.locations import LocationDatabase

logger = logging.getLogger(__name__)

# Initialize location database
_location_db = None

def get_location_database() -> LocationDatabase:
    """Get or initialize the location database."""
    global _location_db
    if _location_db is None:
        _location_db = LocationDatabase(
            storage_path="data/locations.json",
            known_locations_path="data/known_locations.json"
        )
    return _location_db

def geocode_location(location_text: str) -> Optional[Dict[str, float]]:
    """
    Geocode a location string to coordinates.
    Uses a hierarchy of geocoding methods, falling back as needed.
    
    Args:
        location_text: Location text to geocode
        
    Returns:
        Dictionary with "lat" and "lng" keys, or None if geocoding fails
    """
    if not location_text:
        return None
    
    # Try campus geocoding first
    coordinates = simple_campus_geocode(location_text)
    if coordinates:
        logger.debug(f"Found coordinates for '{location_text}' using campus geocoding: {coordinates}")
        return coordinates
    
    # Try geocoding using the location database
    coordinates = database_geocode(location_text)
    if coordinates:
        logger.debug(f"Found coordinates for '{location_text}' using database geocoding: {coordinates}")
        return coordinates
    
    # Try fuzzy matching for locations
    coordinates = fuzzy_location_match(location_text)
    if coordinates:
        logger.debug(f"Found coordinates for '{location_text}' using fuzzy matching: {coordinates}")
        return coordinates
    
    # Fall back to default coordinates for San Diego with jitter
    logger.info(f"Could not geocode location: '{location_text}', using default coordinates")
    return get_default_coordinates()

def simple_campus_geocode(location_text: str) -> Optional[Dict[str, float]]:
    """
    Checks if any known campus landmark is mentioned in the location_text.
    
    Args:
        location_text: Location text to geocode
        
    Returns:
        Dictionary with "lat" and "lng" keys, or None if not found
    """
    # Use existing simple campus geocode function for backward compatibility
    CAMPUS_LOCATIONS = {
        "Geisel Library": (32.8810, -117.2370),
        "Price Center": (32.8794, -117.2359),
        "Warren Mall": (32.8822, -117.2345),
        "BCB Café": (32.8820, -117.2350),
        "UCSD": (32.8801, -117.2340),
        "UC San Diego": (32.8801, -117.2340),
        "La Jolla": (32.8328, -117.2712),
        "San Diego": (32.7157, -117.1611)
    }
    
    if not location_text:
        return None
        
    for name, coords in CAMPUS_LOCATIONS.items():
        if name.lower() in location_text.lower():
            lat, lng = jitter_coordinates(coords[0], coords[1])
            return {"lat": lat, "lng": lng}
            
    return None

def database_geocode(location_text: str) -> Optional[Dict[str, float]]:
    """
    Geocode a location using the location database.
    
    Args:
        location_text: Location text to geocode
        
    Returns:
        Dictionary with "lat" and "lng" keys, or None if not found
    """
    db = get_location_database()
    coordinates = db.get_coordinates(location_text)
    
    if coordinates:
        # Add jitter to avoid exact overlaps
        lat, lng = jitter_coordinates(coordinates["lat"], coordinates["lng"])
        return {"lat": lat, "lng": lng}
        
    return None

def fuzzy_location_match(location_text: str) -> Optional[Dict[str, float]]:
    """
    Try to fuzzy match a location from text.
    Looks for partial matches and keywords.
    
    Args:
        location_text: Location text to geocode
        
    Returns:
        Dictionary with "lat" and "lng" keys, or None if not found
    """
    db = get_location_database()
    location_text = location_text.lower()
    
    # Try to match by extracting keywords
    # Common location prefixes/suffixes to extract
    keywords = [
        "near", "at", "in", "by", "close to", "next to", "across from",
        "hall", "building", "center", "library", "commons", "plaza",
        "quad", "park", "field", "lab", "campus", "college"
    ]
    
    # Extract potential location names
    for keyword in keywords:
        if keyword in location_text:
            parts = location_text.split(keyword)
            for part in parts:
                # Try to geocode each part
                cleaned_part = part.strip()
                if cleaned_part:
                    coords = db.get_coordinates(cleaned_part)
                    if coords:
                        lat, lng = jitter_coordinates(coords["lat"], coords["lng"])
                        return {"lat": lat, "lng": lng}
    
    # Try checking all known locations for partial matches
    all_known = db.get_all_known_locations()
    best_match = None
    best_match_score = 0
    
    for known_name, data in all_known.items():
        # Simple scoring: count how many words from the known name appear in the text
        words = known_name.lower().split()
        score = sum(1 for word in words if word in location_text)
        
        # Require at least one word match with 3+ characters
        if score > 0 and any(len(word) >= 3 and word in location_text for word in words):
            if score > best_match_score:
                best_match = data
                best_match_score = score
    
    if best_match:
        lat, lng = jitter_coordinates(best_match["lat"], best_match["lng"])
        return {"lat": lat, "lng": lng}
    
    return None

def jitter_coordinates(lat: float, lng: float, meters: int = 30) -> Tuple[float, float]:
    """
    Add a small random jitter to coordinates (up to specified meters) 
    to avoid multiple points plotting exactly on top of each other.
    
    Args:
        lat: Latitude
        lng: Longitude
        meters: Maximum jitter in meters
        
    Returns:
        (latitude, longitude) with added jitter
    """
    lat_jitter = (random.uniform(-meters, meters) / 111111)
    lng_jitter = (random.uniform(-meters, meters) / (111111 * abs(math.cos(math.radians(lat)))))
    
    return lat + lat_jitter, lng + lng_jitter

def get_default_coordinates() -> Dict[str, float]:
    """
    Get default coordinates for San Diego with jitter.
    
    Returns:
        Dictionary with "lat" and "lng" keys
    """
    # Default to San Diego downtown coordinates with jitter
    lat, lng = jitter_coordinates(32.7157, -117.1611, meters=1000)
    return {"lat": lat, "lng": lng}

def get_location_details(location_text: str) -> Optional[Dict[str, Any]]:
    """
    Get details about a location.
    
    Args:
        location_text: Location text
        
    Returns:
        Dictionary with location details, or None if not found
    """
    db = get_location_database()
    return db.get_location_details(location_text)

def find_locations_in_radius(lat: float, lng: float, radius_meters: float) -> List[Dict[str, Any]]:
    """
    Find locations within a radius of a point.
    
    Args:
        lat: Latitude of the center point
        lng: Longitude of the center point
        radius_meters: Radius in meters
        
    Returns:
        List of locations within the radius
    """
    db = get_location_database()
    return db.find_locations_in_radius(lat, lng, radius_meters)

def batch_geocode(location_texts: List[str]) -> Dict[str, Dict[str, float]]:
    """
    Geocode multiple locations at once.
    
    Args:
        location_texts: List of location texts to geocode
        
    Returns:
        Dictionary mapping location texts to coordinates
    """
    results = {}
    
    for location_text in location_texts:
        coordinates = geocode_location(location_text)
        if coordinates:
            results[location_text] = coordinates
            
            # Small delay to avoid overloading any services
            time.sleep(0.1)
    
    return results

# Example usage
if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Test geocoding
    test_locations = [
        "Geisel Library",
        "Price Center at UCSD",
        "La Jolla Shores",
        "Downtown San Diego",
        "Balboa Park",
        "Near the RIMAC arena",
        "Somewhere in Hillcrest",
        "Nonexistent Location"
    ]
    
    print("Geocoding test:")
    for location in test_locations:
        coords = geocode_location(location)
        if coords:
            print(f"- {location}: ({coords['lat']}, {coords['lng']})")
        else:
            print(f"- {location}: Not found")
            
    # Test location details
    print("\nLocation details test:")
    for location in test_locations[:3]:  # Test first 3 locations
        details = get_location_details(location)
        if details:
            print(f"- {location}: {details['name']} ({details['type']})")
            print(f"  Address: {details['address']}")
            print(f"  Coordinates: ({details['coordinates']['latitude']}, {details['coordinates']['longitude']})")
        else:
            print(f"- {location}: No details found")