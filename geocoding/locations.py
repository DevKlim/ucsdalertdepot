"""
locations.py

This module manages campus location data for geocoding and spatial awareness.
It provides a database of known campus locations with coordinates and metadata.
"""

import json
import os
import logging
import random
import math
from typing import Dict, Any, List, Optional, Tuple, Union
import time

logger = logging.getLogger(__name__)

class LocationDatabase:
    """
    Campus location database for geocoding and spatial queries.
    """
    
    def __init__(self, storage_path: Optional[str] = None, known_locations_path: Optional[str] = None):
        """
        Initialize the location database.
        
        Args:
            storage_path: Path to save location data (optional)
            known_locations_path: Path to load known locations (optional)
        """
        self.storage_path = storage_path
        self.known_locations_path = known_locations_path
        
        # Data structures
        self.buildings: Dict[str, Dict[str, Any]] = {}
        self.landmarks: Dict[str, Dict[str, Any]] = {}
        self.areas: Dict[str, Dict[str, Any]] = {}
        self.known_locations: Dict[str, Dict[str, Any]] = {}
        
        # Load data
        self._load_data()
    
    def _load_data(self) -> None:
        """Load location data from storage."""
        # Try to load from storage
        if self.storage_path and os.path.exists(self.storage_path):
            try:
                with open(self.storage_path, 'r') as f:
                    data = json.load(f)
                    
                self.buildings = data.get("buildings", {})
                self.landmarks = data.get("landmarks", {})
                self.areas = data.get("areas", {})
                
                logger.info(f"Loaded {len(self.buildings)} buildings, {len(self.landmarks)} landmarks, and {len(self.areas)} areas from {self.storage_path}")
            except Exception as e:
                logger.error(f"Error loading location data: {e}")
                # Create sample data as fallback
                self._create_sample_data()
        else:
            # Create sample data if no file exists
            self._create_sample_data()
        
        # Load known locations if path provided
        if self.known_locations_path and os.path.exists(self.known_locations_path):
            try:
                with open(self.known_locations_path, 'r') as f:
                    self.known_locations = json.load(f)
                    
                logger.info(f"Loaded {len(self.known_locations)} known locations from {self.known_locations_path}")
            except Exception as e:
                logger.error(f"Error loading known locations: {e}")
                # Use default known locations
                self._create_default_known_locations()
        else:
            # Use default known locations
            self._create_default_known_locations()
    
    def _save_data(self) -> None:
        """Save location data to storage."""
        if not self.storage_path:
            return
            
        try:
            data = {
                "buildings": self.buildings,
                "landmarks": self.landmarks,
                "areas": self.areas
            }
            
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)
                
            logger.info(f"Saved location data to {self.storage_path}")
        except Exception as e:
            logger.error(f"Error saving location data: {e}")
    
    def _create_sample_data(self) -> None:
        """Create sample location data for demo purposes."""
        # Sample buildings
        self.buildings = {
            "geisel_library": {
                "name": "Geisel Library",
                "address": "9500 Gilman Dr, La Jolla, CA 92093",
                "coordinates": {"latitude": 32.8810, "longitude": -117.2370},
                "type": "academic",
                "floors": 8,
                "description": "Main campus library"
            },
            "price_center": {
                "name": "Price Center",
                "address": "9500 Gilman Dr, La Jolla, CA 92093",
                "coordinates": {"latitude": 32.8794, "longitude": -117.2359},
                "type": "student_center",
                "floors": 3,
                "description": "Student center with food and services"
            },
            "warren_lecture_hall": {
                "name": "Warren Lecture Hall",
                "address": "9500 Gilman Dr, La Jolla, CA 92093",
                "coordinates": {"latitude": 32.8815, "longitude": -117.2342},
                "type": "academic",
                "floors": 2,
                "description": "Lecture halls in Warren College"
            },
            "peterson_hall": {
                "name": "Peterson Hall",
                "address": "9500 Gilman Dr, La Jolla, CA 92093",
                "coordinates": {"latitude": 32.8798, "longitude": -117.2372},
                "type": "academic",
                "floors": 1,
                "description": "Lecture halls and classrooms"
            },
            "center_hall": {
                "name": "Center Hall",
                "address": "9500 Gilman Dr, La Jolla, CA 92093",
                "coordinates": {"latitude": 32.8782, "longitude": -117.2375},
                "type": "academic",
                "floors": 2,
                "description": "Large lecture hall building"
            },
            "york_hall": {
                "name": "York Hall",
                "address": "9500 Gilman Dr, La Jolla, CA 92093",
                "coordinates": {"latitude": 32.8745, "longitude": -117.2401},
                "type": "academic",
                "floors": 5,
                "description": "Science laboratories and classrooms"
            },
            "applied_physics_math": {
                "name": "Applied Physics & Mathematics",
                "address": "9500 Gilman Dr, La Jolla, CA 92093",
                "coordinates": {"latitude": 32.8794, "longitude": -117.2411},
                "type": "academic",
                "floors": 7,
                "description": "Physics and mathematics department"
            },
            "jacobs_hall": {
                "name": "Jacobs Hall",
                "address": "9500 Gilman Dr, La Jolla, CA 92093",
                "coordinates": {"latitude": 32.8829, "longitude": -117.2333},
                "type": "academic",
                "floors": 6,
                "description": "Engineering building"
            },
            "rimac": {
                "name": "RIMAC/Liontree Arena",
                "address": "9730 Hopkins Dr, La Jolla, CA 92093",
                "coordinates": {"latitude": 32.8869, "longitude": -117.2406},
                "type": "athletics",
                "floors": 3,
                "description": "Recreation and athletic center"
            },
            "student_health": {
                "name": "Student Health Services",
                "address": "9500 Gilman Dr, La Jolla, CA 92093",
                "coordinates": {"latitude": 32.8751, "longitude": -117.2359},
                "type": "health",
                "floors": 3,
                "description": "Student health center"
            }
        }
        
        # Sample landmarks
        self.landmarks = {
            "sun_god": {
                "name": "Sun God Statue",
                "address": "9500 Gilman Dr, La Jolla, CA 92093",
                "coordinates": {"latitude": 32.8786, "longitude": -117.2400},
                "description": "Iconic campus statue"
            },
            "warren_bear": {
                "name": "Warren Bear",
                "address": "9500 Gilman Dr, La Jolla, CA 92093",
                "coordinates": {"latitude": 32.8822, "longitude": -117.2339},
                "description": "Warren College mascot statue"
            },
            "fallen_star": {
                "name": "Fallen Star",
                "address": "9500 Gilman Dr, La Jolla, CA 92093",
                "coordinates": {"latitude": 32.8814, "longitude": -117.2353},
                "description": "Stuart Collection art installation"
            },
            "silent_tree": {
                "name": "Silent Tree",
                "address": "9500 Gilman Dr, La Jolla, CA 92093",
                "coordinates": {"latitude": 32.8780, "longitude": -117.2392},
                "description": "Stuart Collection art installation"
            },
            "warren_mall": {
                "name": "Warren Mall",
                "address": "9500 Gilman Dr, La Jolla, CA 92093",
                "coordinates": {"latitude": 32.8822, "longitude": -117.2345},
                "description": "Warren College central mall"
            },
            "library_walk": {
                "name": "Library Walk",
                "address": "9500 Gilman Dr, La Jolla, CA 92093",
                "coordinates": {"latitude": 32.8794, "longitude": -117.2370},
                "description": "Main pedestrian walkway"
            }
        }
        
        # Sample areas
        self.areas = {
            "revelle_college": {
                "name": "Revelle College",
                "address": "9500 Gilman Dr, La Jolla, CA 92093",
                "coordinates": {"latitude": 32.8745, "longitude": -117.2410},
                "radius": 200,
                "type": "college",
                "description": "First college established at UCSD"
            },
            "muir_college": {
                "name": "Muir College",
                "address": "9500 Gilman Dr, La Jolla, CA 92093",
                "coordinates": {"latitude": 32.8789, "longitude": -117.2410},
                "radius": 180,
                "type": "college",
                "description": "Second college established at UCSD"
            },
            "marshall_college": {
                "name": "Marshall College",
                "address": "9500 Gilman Dr, La Jolla, CA 92093",
                "coordinates": {"latitude": 32.8836, "longitude": -117.2425},
                "radius": 190,
                "type": "college",
                "description": "Third college established at UCSD"
            },
            "warren_college": {
                "name": "Warren College",
                "address": "9500 Gilman Dr, La Jolla, CA 92093",
                "coordinates": {"latitude": 32.8815, "longitude": -117.2350},
                "radius": 200,
                "type": "college",
                "description": "Fourth college established at UCSD"
            },
            "roosevelt_college": {
                "name": "Eleanor Roosevelt College",
                "address": "9500 Gilman Dr, La Jolla, CA 92093",
                "coordinates": {"latitude": 32.8851, "longitude": -117.2420},
                "radius": 170,
                "type": "college",
                "description": "Fifth college established at UCSD"
            },
            "sixth_college": {
                "name": "Sixth College",
                "address": "9500 Gilman Dr, La Jolla, CA 92093",
                "coordinates": {"latitude": 32.8806, "longitude": -117.2325},
                "radius": 160,
                "type": "college",
                "description": "Sixth college established at UCSD"
            },
            "seventh_college": {
                "name": "Seventh College",
                "address": "9500 Gilman Dr, La Jolla, CA 92093",
                "coordinates": {"latitude": 32.8890, "longitude": -117.2405},
                "radius": 150,
                "type": "college",
                "description": "Seventh college established at UCSD"
            },
            "eighth_college": {
                "name": "Eighth College",
                "address": "9500 Gilman Dr, La Jolla, CA 92093",
                "coordinates": {"latitude": 32.8851, "longitude": -117.2408},
                "radius": 150,
                "type": "college",
                "description": "Eighth college established at UCSD"
            },
            "north_campus": {
                "name": "North Campus",
                "address": "9500 Gilman Dr, La Jolla, CA 92093",
                "coordinates": {"latitude": 32.8852, "longitude": -117.2406},
                "radius": 500,
                "type": "campus_section",
                "description": "Northern section of campus"
            },
            "central_campus": {
                "name": "Central Campus",
                "address": "9500 Gilman Dr, La Jolla, CA 92093",
                "coordinates": {"latitude": 32.8801, "longitude": -117.2340},
                "radius": 400,
                "type": "campus_section",
                "description": "Central section of campus"
            },
            "south_campus": {
                "name": "South Campus",
                "address": "9500 Gilman Dr, La Jolla, CA 92093",
                "coordinates": {"latitude": 32.8750, "longitude": -117.2340},
                "radius": 450,
                "type": "campus_section",
                "description": "Southern section of campus"
            },
            "scripps_institution": {
                "name": "Scripps Institution of Oceanography",
                "address": "8622 Kennel Way, La Jolla, CA 92037",
                "coordinates": {"latitude": 32.8662, "longitude": -117.2546},
                "radius": 400,
                "type": "campus_section",
                "description": "Oceanography campus"
            }
        }
        
        logger.info(f"Created {len(self.buildings)} sample buildings, {len(self.landmarks)} sample landmarks, and {len(self.areas)} sample areas")
        
        # Save the data
        self._save_data()
    
    def _create_default_known_locations(self) -> None:
        """Create default known locations for geocoding."""
        self.known_locations = {
            "Warren Mall": {
                "lat": 32.8822, 
                "lng": -117.2345,
                "address": "Warren Mall, UC San Diego, 9500 Gilman Dr, La Jolla, CA 92093"
            },
            "BCB Café": {
                "lat": 32.8822, 
                "lng": -117.2345,
                "address": "BCB Café, Warren Mall, UC San Diego, 9500 Gilman Dr, La Jolla, CA 92093"
            },
            "Pepper Canyon": {
                "lat": 32.8782, 
                "lng": -117.2392,
                "address": "Pepper Canyon, UC San Diego, 9500 Gilman Dr, La Jolla, CA 92093"
            },
            "Muir College": {
                "lat": 32.8789, 
                "lng": -117.2410,
                "address": "Muir College, UC San Diego, 9500 Gilman Dr, La Jolla, CA 92093"
            },
            "Eighth College": {
                "lat": 32.8851, 
                "lng": -117.2408,
                "address": "Eighth College, UC San Diego, 9500 Gilman Dr, La Jolla, CA 92093"
            },
            "UC San Diego": {
                "lat": 32.8801, 
                "lng": -117.2340,
                "address": "University of California San Diego, 9500 Gilman Dr, La Jolla, CA 92093"
            },
            "La Jolla": {
                "lat": 32.8449, 
                "lng": -117.2740,
                "address": "La Jolla, San Diego, CA 92037"
            },
            "San Diego": {
                "lat": 32.7157, 
                "lng": -117.1611,
                "address": "San Diego, CA"
            },
            "Geisel Library": {
                "lat": 32.8810, 
                "lng": -117.2370,
                "address": "Geisel Library, UC San Diego, 9500 Gilman Dr, La Jolla, CA 92093"
            },
            "Price Center": {
                "lat": 32.8794, 
                "lng": -117.2359,
                "address": "Price Center, UC San Diego, 9500 Gilman Dr, La Jolla, CA 92093"
            },
            "Library Walk": {
                "lat": 32.8794, 
                "lng": -117.2370,
                "address": "Library Walk, UC San Diego, 9500 Gilman Dr, La Jolla, CA 92093"
            },
            "RIMAC Arena": {
                "lat": 32.8869, 
                "lng": -117.2406,
                "address": "RIMAC Arena, UC San Diego, 9730 Hopkins Dr, La Jolla, CA 92093"
            }
        }
        
        # Also add buildings and landmarks to known locations
        for building_id, building in self.buildings.items():
            name = building["name"]
            coords = building["coordinates"]
            self.known_locations[name] = {
                "lat": coords["latitude"],
                "lng": coords["longitude"],
                "address": building["address"]
            }
            
        for landmark_id, landmark in self.landmarks.items():
            name = landmark["name"]
            coords = landmark["coordinates"]
            self.known_locations[name] = {
                "lat": coords["latitude"],
                "lng": coords["longitude"],
                "address": landmark["address"]
            }
            
        logger.info(f"Created {len(self.known_locations)} known locations")
    
    def get_coordinates(self, location_name: str) -> Optional[Dict[str, float]]:
        """
        Get coordinates for a location name.
        
        Args:
            location_name: Name of the location
            
        Returns:
            Dictionary with "lat" and "lng" keys, or None if not found
        """
        # Check if location is in known locations
        for known_name, data in self.known_locations.items():
            if known_name.lower() in location_name.lower():
                return {"lat": data["lat"], "lng": data["lng"]}
        
        # Check if location is in buildings, landmarks, or areas
        for collection in [self.buildings, self.landmarks, self.areas]:
            for item_id, item in collection.items():
                if item["name"].lower() in location_name.lower():
                    coords = item["coordinates"]
                    return {"lat": coords["latitude"], "lng": coords["longitude"]}
        
        # Location not found
        return None
    
    def get_location_details(self, location_name: str) -> Optional[Dict[str, Any]]:
        """
        Get details for a location name.
        
        Args:
            location_name: Name of the location
            
        Returns:
            Dictionary with location details, or None if not found
        """
        # Check if location is in buildings
        for building_id, building in self.buildings.items():
            if building["name"].lower() in location_name.lower():
                return {
                    "name": building["name"],
                    "type": "building",
                    "coordinates": building["coordinates"],
                    "address": building["address"],
                    "description": building.get("description", ""),
                    "details": building
                }
        
        # Check if location is in landmarks
        for landmark_id, landmark in self.landmarks.items():
            if landmark["name"].lower() in location_name.lower():
                return {
                    "name": landmark["name"],
                    "type": "landmark",
                    "coordinates": landmark["coordinates"],
                    "address": landmark["address"],
                    "description": landmark.get("description", ""),
                    "details": landmark
                }
        
        # Check if location is in areas
        for area_id, area in self.areas.items():
            if area["name"].lower() in location_name.lower():
                return {
                    "name": area["name"],
                    "type": "area",
                    "coordinates": area["coordinates"],
                    "address": area["address"],
                    "description": area.get("description", ""),
                    "radius": area.get("radius", 100),
                    "details": area
                }
        
        # Check if location is in known locations
        for known_name, data in self.known_locations.items():
            if known_name.lower() in location_name.lower():
                return {
                    "name": known_name,
                    "type": "known_location",
                    "coordinates": {"latitude": data["lat"], "longitude": data["lng"]},
                    "address": data["address"],
                    "description": ""
                }
        
        # Location not found
        return None
    
    def find_locations_in_radius(self, lat: float, lng: float, radius_meters: float, location_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Find locations within a radius of a point.
        
        Args:
            lat: Latitude of the center point
            lng: Longitude of the center point
            radius_meters: Radius in meters
            location_type: Optional type filter ("building", "landmark", "area")
            
        Returns:
            List of locations within the radius
        """
        results = []
        
        # Helper function to calculate distance
        def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
            # Earth radius in meters
            R = 6371000
            
            # Convert degrees to radians
            lat1_rad = math.radians(lat1)
            lon1_rad = math.radians(lon1)
            lat2_rad = math.radians(lat2)
            lon2_rad = math.radians(lon2)
            
            # Differences
            dlat = lat2_rad - lat1_rad
            dlon = lon2_rad - lon1_rad
            
            # Haversine formula
            a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
            c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
            distance = R * c
            
            return distance
        
        # Check buildings
        if not location_type or location_type == "building":
            for building_id, building in self.buildings.items():
                coords = building["coordinates"]
                distance = calculate_distance(lat, lng, coords["latitude"], coords["longitude"])
                
                if distance <= radius_meters:
                    results.append({
                        "name": building["name"],
                        "type": "building",
                        "coordinates": coords,
                        "distance": distance,
                        "details": building
                    })
        
        # Check landmarks
        if not location_type or location_type == "landmark":
            for landmark_id, landmark in self.landmarks.items():
                coords = landmark["coordinates"]
                distance = calculate_distance(lat, lng, coords["latitude"], coords["longitude"])
                
                if distance <= radius_meters:
                    results.append({
                        "name": landmark["name"],
                        "type": "landmark",
                        "coordinates": coords,
                        "distance": distance,
                        "details": landmark
                    })
        
        # Check areas
        if not location_type or location_type == "area":
            for area_id, area in self.areas.items():
                coords = area["coordinates"]
                distance = calculate_distance(lat, lng, coords["latitude"], coords["longitude"])
                
                if distance <= radius_meters:
                    results.append({
                        "name": area["name"],
                        "type": "area",
                        "coordinates": coords,
                        "distance": distance,
                        "details": area
                    })
        
        # Sort by distance
        return sorted(results, key=lambda x: x["distance"])
    
    def jitter_coordinates(self, lat: float, lng: float, meters: int = 30) -> Tuple[float, float]:
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
    
    def add_location(self, location_data: Dict[str, Any]) -> str:
        """
        Add a new location to the database.
        
        Args:
            location_data: Dictionary with location data
            
        Returns:
            ID of the added location
        """
        location_type = location_data.get("type", "building")
        name = location_data.get("name", "")
        
        if not name:
            raise ValueError("Location name is required")
            
        # Create an ID from the name
        location_id = name.lower().replace(" ", "_").replace("-", "_")
        
        if location_type == "building":
            self.buildings[location_id] = location_data
        elif location_type == "landmark":
            self.landmarks[location_id] = location_data
        elif location_type == "area":
            self.areas[location_id] = location_data
        else:
            raise ValueError(f"Unknown location type: {location_type}")
            
        # Add to known locations for geocoding
        coords = location_data["coordinates"]
        self.known_locations[name] = {
            "lat": coords["latitude"],
            "lng": coords["longitude"],
            "address": location_data.get("address", "")
        }
        
        # Save the data
        self._save_data()
        
        return location_id
    
    def update_location(self, location_id: str, location_type: str, updates: Dict[str, Any]) -> bool:
        """
        Update a location in the database.
        
        Args:
            location_id: ID of the location to update
            location_type: Type of location ("building", "landmark", "area")
            updates: Dictionary with fields to update
            
        Returns:
            True if updated, False if not found
        """
        # Get the appropriate collection
        if location_type == "building":
            collection = self.buildings
        elif location_type == "landmark":
            collection = self.landmarks
        elif location_type == "area":
            collection = self.areas
        else:
            raise ValueError(f"Unknown location type: {location_type}")
            
        # Check if location exists
        if location_id not in collection:
            return False
            
        # Update the location
        for key, value in updates.items():
            collection[location_id][key] = value
            
        # Update known locations if name or coordinates changed
        if "name" in updates or "coordinates" in updates:
            name = collection[location_id]["name"]
            coords = collection[location_id]["coordinates"]
            address = collection[location_id].get("address", "")
            
            self.known_locations[name] = {
                "lat": coords["latitude"],
                "lng": coords["longitude"],
                "address": address
            }
            
        # Save the data
        self._save_data()
        
        return True
    
    def delete_location(self, location_id: str, location_type: str) -> bool:
        """
        Delete a location from the database.
        
        Args:
            location_id: ID of the location to delete
            location_type: Type of location ("building", "landmark", "area")
            
        Returns:
            True if deleted, False if not found
        """
        # Get the appropriate collection
        if location_type == "building":
            collection = self.buildings
        elif location_type == "landmark":
            collection = self.landmarks
        elif location_type == "area":
            collection = self.areas
        else:
            raise ValueError(f"Unknown location type: {location_type}")
            
        # Check if location exists
        if location_id not in collection:
            return False
            
        # Remove from known locations
        name = collection[location_id]["name"]
        if name in self.known_locations:
            del self.known_locations[name]
            
        # Delete the location
        del collection[location_id]
        
        # Save the data
        self._save_data()
        
        return True
    
    def get_all_locations(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get all locations."""
        return {
            "buildings": list(self.buildings.values()),
            "landmarks": list(self.landmarks.values()),
            "areas": list(self.areas.values())
        }
    
    def get_all_known_locations(self) -> Dict[str, Dict[str, Any]]:
        """Get all known locations for geocoding."""
        return self.known_locations
    
    def add_san_diego_locations(self) -> None:
        """Add key San Diego locations to the database (beyond just UCSD campus)."""
        # Major San Diego neighborhoods and areas
        san_diego_areas = {
            "downtown_sd": {
                "name": "Downtown San Diego",
                "address": "Downtown, San Diego, CA",
                "coordinates": {"latitude": 32.7157, "longitude": -117.1611},
                "radius": 2000,
                "type": "neighborhood",
                "description": "Downtown San Diego area"
            },
            "hillcrest": {
                "name": "Hillcrest",
                "address": "Hillcrest, San Diego, CA",
                "coordinates": {"latitude": 32.7480, "longitude": -117.1604},
                "radius": 1000,
                "type": "neighborhood",
                "description": "Hillcrest neighborhood"
            },
            "north_park": {
                "name": "North Park",
                "address": "North Park, San Diego, CA",
                "coordinates": {"latitude": 32.7475, "longitude": -117.1292},
                "radius": 1000,
                "type": "neighborhood",
                "description": "North Park neighborhood"
            },
            "pacific_beach": {
                "name": "Pacific Beach",
                "address": "Pacific Beach, San Diego, CA",
                "coordinates": {"latitude": 32.7997, "longitude": -117.2437},
                "radius": 1500,
                "type": "neighborhood",
                "description": "Pacific Beach neighborhood"
            },
            "mission_beach": {
                "name": "Mission Beach",
                "address": "Mission Beach, San Diego, CA",
                "coordinates": {"latitude": 32.7697, "longitude": -117.2520},
                "radius": 800,
                "type": "neighborhood",
                "description": "Mission Beach neighborhood"
            },
            "ocean_beach": {
                "name": "Ocean Beach",
                "address": "Ocean Beach, San Diego, CA",
                "coordinates": {"latitude": 32.7494, "longitude": -117.2495},
                "radius": 1000,
                "type": "neighborhood",
                "description": "Ocean Beach neighborhood"
            },
            "la_jolla": {
                "name": "La Jolla",
                "address": "La Jolla, San Diego, CA",
                "coordinates": {"latitude": 32.8328, "longitude": -117.2712},
                "radius": 3000,
                "type": "neighborhood",
                "description": "La Jolla community"
            },
            "university_city": {
                "name": "University City",
                "address": "University City, San Diego, CA",
                "coordinates": {"latitude": 32.8591, "longitude": -117.2075},
                "radius": 2000,
                "type": "neighborhood",
                "description": "University City community"
            },
            "mira_mesa": {
                "name": "Mira Mesa",
                "address": "Mira Mesa, San Diego, CA",
                "coordinates": {"latitude": 32.9134, "longitude": -117.1487},
                "radius": 3000,
                "type": "neighborhood",
                "description": "Mira Mesa community"
            },
            "mission_valley": {
                "name": "Mission Valley",
                "address": "Mission Valley, San Diego, CA",
                "coordinates": {"latitude": 32.7675, "longitude": -117.1511},
                "radius": 2500,
                "type": "neighborhood",
                "description": "Mission Valley area"
            }
        }
        
        # Major San Diego landmarks
        san_diego_landmarks = {
            "balboa_park": {
                "name": "Balboa Park",
                "address": "1549 El Prado, San Diego, CA 92101",
                "coordinates": {"latitude": 32.7341, "longitude": -117.1446},
                "description": "Large urban cultural park"
            },
            "seaworld": {
                "name": "SeaWorld",
                "address": "500 Sea World Dr, San Diego, CA 92109",
                "coordinates": {"latitude": 32.7644, "longitude": -117.2273},
                "description": "Theme park and marine zoological park"
            },
            "san_diego_zoo": {
                "name": "San Diego Zoo",
                "address": "2920 Zoo Dr, San Diego, CA 92101",
                "coordinates": {"latitude": 32.7353, "longitude": -117.1490},
                "description": "Urban zoo in Balboa Park"
            },
            "petco_park": {
                "name": "Petco Park",
                "address": "100 Park Blvd, San Diego, CA 92101",
                "coordinates": {"latitude": 32.7076, "longitude": -117.1569},
                "description": "Major league baseball stadium"
            },
            "gaslamp_quarter": {
                "name": "Gaslamp Quarter",
                "address": "Gaslamp Quarter, San Diego, CA",
                "coordinates": {"latitude": 32.7099, "longitude": -117.1609},
                "description": "Historic district in downtown San Diego"
            },
            "coronado_bridge": {
                "name": "Coronado Bridge",
                "address": "Coronado Bridge, San Diego, CA",
                "coordinates": {"latitude": 32.6902, "longitude": -117.1545},
                "description": "Bridge connecting San Diego to Coronado"
            },
            "torrey_pines": {
                "name": "Torrey Pines State Natural Reserve",
                "address": "12600 N Torrey Pines Rd, La Jolla, CA 92037",
                "coordinates": {"latitude": 32.9196, "longitude": -117.2535},
                "description": "State park and beach"
            },
            "mission_bay": {
                "name": "Mission Bay Park",
                "address": "2688 E Mission Bay Dr, San Diego, CA 92109",
                "coordinates": {"latitude": 32.7743, "longitude": -117.2322},
                "description": "Recreational water park"
            }
        }
        
        # Major San Diego buildings
        san_diego_buildings = {
            "sdsu": {
                "name": "San Diego State University",
                "address": "5500 Campanile Dr, San Diego, CA 92182",
                "coordinates": {"latitude": 32.7757, "longitude": -117.0739},
                "type": "university",
                "floors": 8,
                "description": "Public research university"
            },
            "sd_convention_center": {
                "name": "San Diego Convention Center",
                "address": "111 W Harbor Dr, San Diego, CA 92101",
                "coordinates": {"latitude": 32.7066, "longitude": -117.1625},
                "type": "convention_center",
                "floors": 3,
                "description": "Major convention center downtown"
            },
            "sd_airport": {
                "name": "San Diego International Airport",
                "address": "3225 N Harbor Dr, San Diego, CA 92101",
                "coordinates": {"latitude": 32.7336, "longitude": -117.1897},
                "type": "airport",
                "floors": 2,
                "description": "International airport"
            },
            "sd_city_hall": {
                "name": "San Diego City Hall",
                "address": "202 C St, San Diego, CA 92101",
                "coordinates": {"latitude": 32.7175, "longitude": -117.1625},
                "type": "government",
                "floors": 13,
                "description": "San Diego city government building"
            },
            "uss_midway": {
                "name": "USS Midway Museum",
                "address": "910 N Harbor Dr, San Diego, CA 92101",
                "coordinates": {"latitude": 32.7137, "longitude": -117.1751},
                "type": "museum",
                "floors": 4,
                "description": "Aircraft carrier museum"
            },
            "sd_central_library": {
                "name": "San Diego Central Library",
                "address": "330 Park Blvd, San Diego, CA 92101",
                "coordinates": {"latitude": 32.7098, "longitude": -117.1534},
                "type": "library",
                "floors": 9,
                "description": "Main public library"
            },
            "ucsd_medical_center_hillcrest": {
                "name": "UCSD Medical Center Hillcrest",
                "address": "200 W Arbor Dr, San Diego, CA 92103",
                "coordinates": {"latitude": 32.7542, "longitude": -117.1670},
                "type": "hospital",
                "floors": 11,
                "description": "Major medical center in Hillcrest"
            },
            "scripps_mercy_hospital": {
                "name": "Scripps Mercy Hospital",
                "address": "4077 5th Ave, San Diego, CA 92103",
                "coordinates": {"latitude": 32.7510, "longitude": -117.1602},
                "type": "hospital",
                "floors": 8,
                "description": "Major hospital in Hillcrest"
            },
            "sharp_memorial_hospital": {
                "name": "Sharp Memorial Hospital",
                "address": "7901 Frost St, San Diego, CA 92123",
                "coordinates": {"latitude": 32.7972, "longitude": -117.1559},
                "type": "hospital",
                "floors": 10,
                "description": "Major hospital in Kearny Mesa"
            }
        }
        
        # Add San Diego areas to the database
        for area_id, area in san_diego_areas.items():
            self.areas[area_id] = area
            
            # Add to known locations for geocoding
            self.known_locations[area["name"]] = {
                "lat": area["coordinates"]["latitude"],
                "lng": area["coordinates"]["longitude"],
                "address": area["address"]
            }
        
        # Add San Diego landmarks to the database
        for landmark_id, landmark in san_diego_landmarks.items():
            self.landmarks[landmark_id] = landmark
            
            # Add to known locations for geocoding
            self.known_locations[landmark["name"]] = {
                "lat": landmark["coordinates"]["latitude"],
                "lng": landmark["coordinates"]["longitude"],
                "address": landmark["address"]
            }
        
        # Add San Diego buildings to the database
        for building_id, building in san_diego_buildings.items():
            self.buildings[building_id] = building
            
            # Add to known locations for geocoding
            self.known_locations[building["name"]] = {
                "lat": building["coordinates"]["latitude"],
                "lng": building["coordinates"]["longitude"],
                "address": building["address"]
            }
        
        logger.info(f"Added {len(san_diego_areas)} San Diego areas, {len(san_diego_landmarks)} landmarks, and {len(san_diego_buildings)} buildings")
        
        # Save the data
        self._save_data()


# Example usage
if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Create location database
    db = LocationDatabase(storage_path="data/locations.json")
    
    # Add San Diego locations
    db.add_san_diego_locations()
    
    # Print summary
    locations = db.get_all_locations()
    print(f"Location database contains:")
    print(f"- {len(locations['buildings'])} buildings")
    print(f"- {len(locations['landmarks'])} landmarks")
    print(f"- {len(locations['areas'])} areas")
    print(f"- {len(db.get_all_known_locations())} known locations for geocoding")
    
    # Test geocoding
    test_locations = [
        "Geisel Library",
        "La Jolla",
        "Downtown San Diego",
        "Petco Park",
        "Nonexistent Location"
    ]
    
    print("\nGeocoding test:")
    for location in test_locations:
        coords = db.get_coordinates(location)
        if coords:
            print(f"- {location}: ({coords['lat']}, {coords['lng']})")
        else:
            print(f"- {location}: Not found")
            
    # Test radius search
    test_point = (32.7157, -117.1611)  # Downtown San Diego
    radius = 1000  # meters
    
    print(f"\nLocations within {radius}m of Downtown San Diego:")
    nearby = db.find_locations_in_radius(test_point[0], test_point[1], radius)
    
    for location in nearby:
        print(f"- {location['name']} ({location['type']}): {location['distance']:.1f}m")