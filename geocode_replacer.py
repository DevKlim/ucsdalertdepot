#!/usr/bin/env python3
"""
geocode_replacer.py

This script takes a source geocoding JSON file and updates alerts in 
ucsd_alerts_geocoded.json with new coordinates and addresses.

Usage:
    python geocode_replacer.py service_name geocode_file.json

Example:
    python geocode_replacer.py mistral mistral_geocode.json
    
This will:
1. Read the alerts from ucsd_alerts_geocoded.json
2. Read the geocoding data from mistral_geocode.json
3. For each alert, if its location_text matches a key in the geocoding data,
   update its lat, lng, and address fields
4. Save the updated alerts to a new file: ucsd_alerts_geocoded_mistral.json
"""

import json
import sys
import os
import copy
from datetime import datetime

def load_json_file(filename):
    """Load a JSON file and return its contents."""
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        sys.exit(1)

def save_json_file(data, filename):
    """Save data to a JSON file."""
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2)
        print(f"Successfully saved to {filename}")
    except Exception as e:
        print(f"Error saving to {filename}: {e}")
        sys.exit(1)

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
    # Check arguments
    if len(sys.argv) != 3:
        print("Usage: python geocode_replacer.py service_name geocode_file.json")
        sys.exit(1)
    
    service_name = sys.argv[1]
    geocode_file = sys.argv[2]
    alerts_file = "ucsd_alerts_geocoded.json"
    output_file = f"ucsd_alerts_geocoded_{service_name}.json"
    
    # Check if files exist
    if not os.path.exists(alerts_file):
        print(f"Error: {alerts_file} not found")
        sys.exit(1)
    
    if not os.path.exists(geocode_file):
        print(f"Error: {geocode_file} not found")
        sys.exit(1)
    
    # Load data
    print(f"Loading alerts from {alerts_file}...")
    alerts = load_json_file(alerts_file)
    print(f"Loaded {len(alerts)} alerts")
    
    print(f"Loading geocoding data from {geocode_file}...")
    geocoding_data = load_json_file(geocode_file)
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
    print(f"\nSaving updated alerts to {output_file}...")
    save_json_file(updated_alerts, output_file)
    
    print("\nDone!")

if __name__ == "__main__":
    main()