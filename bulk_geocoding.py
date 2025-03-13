#!/usr/bin/env python3
"""
bulk_geocode_replacer.py

This script processes all available geocoding JSON files and creates updated
versions of ucsd_alerts_geocoded.json for each geocoding service.

Usage:
    python bulk_geocode_replacer.py

This will:
1. Read the alerts from ucsd_alerts_geocoded.json
2. Look for all *_geocode.json files in the current directory
3. For each geocoding file, create an updated version of the alerts
4. Save each version to a separate file
"""

import json
import sys
import os
import copy
import glob
from datetime import datetime

def load_json_file(filename):
    """Load a JSON file and return its contents."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return None

def save_json_file(data, filename):
    """Save data to a JSON file."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        print(f"Successfully saved to {filename}")
        return True
    except Exception as e:
        print(f"Error saving to {filename}: {e}")
        return False

def update_alerts_with_geocoding(alerts, geocoding_data, service_name):
    """
    Update alerts with geocoding data.
    
    Args:
        alerts: List of alert dictionaries
        geocoding_data: Dictionary mapping location_text to geocoding info
        service_name: Name of the geocoding service (for logging)
        
    Returns:
        Tuple of (updated_alerts, stats)
    """
    updated_alerts = copy.deepcopy(alerts)
    
    # Stats tracking
    stats = {
        "total_alerts": len(alerts),
        "updated": 0,
        "skipped_no_match": 0,
        "skipped_null_coords": 0
    }
    
    # Process each alert
    for alert in updated_alerts:
        location_text = alert.get("location_text")
        
        # Skip if location_text is not in geocoding data
        if location_text not in geocoding_data:
            stats["skipped_no_match"] += 1
            continue
        
        # Get geocoding info
        geo_info = geocoding_data[location_text]
        
        # Skip if lat or lng is null
        if geo_info.get("lat") is None or geo_info.get("lng") is None:
            stats["skipped_null_coords"] += 1
            continue
        
        # Update alert
        alert["lat"] = geo_info["lat"]
        alert["lng"] = geo_info["lng"]
        alert["address"] = geo_info["address"]
        stats["updated"] += 1
    
    return updated_alerts, stats

def main():
    alerts_file = "ucsd_alerts_geocoded.json"
    
    # Check if alerts file exists
    if not os.path.exists(alerts_file):
        print(f"Error: {alerts_file} not found")
        sys.exit(1)
    
    # Load alerts
    print(f"Loading alerts from {alerts_file}...")
    alerts = load_json_file(alerts_file)
    if alerts is None:
        sys.exit(1)
    print(f"Loaded {len(alerts)} alerts")
    
    # Find all geocoding files
    geocode_files = glob.glob("*_geocode.json")
    if not geocode_files:
        print("No geocoding files found (*_geocode.json)")
        sys.exit(1)
    
    print(f"Found {len(geocode_files)} geocoding files")
    
    # Create a summary for all services
    summary = []
    
    # Process each geocoding file
    for geocode_file in geocode_files:
        # Extract service name from filename
        service_name = geocode_file.replace("_geocode.json", "")
        output_file = f"ucsd_alerts_geocoded_{service_name}.json"
        
        print(f"\nProcessing {service_name} geocoding data from {geocode_file}...")
        
        # Load geocoding data
        geocoding_data = load_json_file(geocode_file)
        if geocoding_data is None:
            continue
        
        print(f"Loaded {len(geocoding_data)} geocoded locations")
        
        # Update alerts
        print(f"Updating alerts with {service_name} geocoding data...")
        updated_alerts, stats = update_alerts_with_geocoding(alerts, geocoding_data, service_name)
        
        # Print stats
        print("\nUpdate Statistics:")
        print(f"Total alerts: {stats['total_alerts']}")
        print(f"Updated: {stats['updated']} ({stats['updated'] / stats['total_alerts'] * 100:.1f}%)")
        print(f"Skipped (no match): {stats['skipped_no_match']} ({stats['skipped_no_match'] / stats['total_alerts'] * 100:.1f}%)")
        print(f"Skipped (null coordinates): {stats['skipped_null_coords']} ({stats['skipped_null_coords'] / stats['total_alerts'] * 100:.1f}%)")
        
        # Save updated alerts
        print(f"Saving updated alerts to {output_file}...")
        if save_json_file(updated_alerts, output_file):
            # Add to summary
            summary.append({
                "service": service_name,
                "file": output_file,
                "total": stats['total_alerts'],
                "updated": stats['updated'],
                "updated_percent": f"{stats['updated'] / stats['total_alerts'] * 100:.1f}%",
                "no_match": stats['skipped_no_match'],
                "null_coords": stats['skipped_null_coords']
            })
    
    # Print summary
    if summary:
        print("\n=== Summary ===")
        print(f"{'Service':<15} {'Updated':<15} {'No Match':<15} {'Null Coords':<15}")
        print("-" * 60)
        for item in summary:
            print(f"{item['service']:<15} {item['updated_percent']:<15} {item['no_match']:<15} {item['null_coords']:<15}")
    
    # Create geoJSON files for each service
    print("\nCreating GeoJSON files for map visualization...")
    for service_info in summary:
        service = service_info["service"]
        input_file = service_info["file"]
        geojson_file = f"ucsd_alerts_{service}_geojson.json"
        
        # Load updated alerts
        updated_alerts = load_json_file(input_file)
        if updated_alerts is None:
            continue
        
        # Convert to GeoJSON
        features = []
        for alert in updated_alerts:
            # Make sure the alert has the required location data
            if "lat" in alert and "lng" in alert and alert["lat"] is not None and alert["lng"] is not None:
                feature = {
                    "type": "Feature",
                    "properties": {
                        "title": alert["alert_title"],
                        "crime_type": alert["crime_type"],
                        "alert_type": alert["alert_type"],
                        "date": alert["date"],
                        "is_update": alert["is_update"],
                        "suspect_info": alert["suspect_info"],
                        "details_url": alert.get("details_url", ""),
                        "location_text": alert["location_text"],
                        "precise_location": alert.get("precise_location", alert["location_text"]),
                        "address": alert.get("address", ""),
                        "service": service  # Add service info
                    },
                    "geometry": {
                        "type": "Point",
                        "coordinates": [alert["lng"], alert["lat"]]  # GeoJSON format is [longitude, latitude]
                    }
                }
                features.append(feature)
        
        geojson = {
            "type": "FeatureCollection",
            "features": features
        }
        
        # Save GeoJSON
        if save_json_file(geojson, geojson_file):
            print(f"Created GeoJSON file: {geojson_file} with {len(features)} features")
    
    print("\nDone!")

if __name__ == "__main__":
    main()