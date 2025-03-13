#!/usr/bin/env python3
"""
geocode_comparison_tool.py

A comprehensive tool for comparing different geocoding services and their results.
This script combines and enhances the functionality of bulk_geocoding.py and 
geocode_replacer.py to create a more streamlined workflow.

Usage:
    python geocode_comparison_tool.py [--generate-all] [--service SERVICE_NAME] [--apply SERVICE_NAME]

Options:
    --generate-all         Generate files for all available geocoding services
    --service SERVICE_NAME Generate files only for the specified service
    --apply SERVICE_NAME   Apply the geocoding from a service to the main alerts file
    --restore              Restore the original alerts file from backup
    --backup               Create a backup of the current alerts file
    --list                 List all available geocoding services
    --help                 Show this help message

Examples:
    # Generate files for all services
    python geocode_comparison_tool.py --generate-all
    
    # Generate files only for the mistral service
    python geocode_comparison_tool.py --service mistral
    
    # Apply mistral geocoding to the main alerts file
    python geocode_comparison_tool.py --apply mistral
    
    # Restore the original alerts file
    python geocode_comparison_tool.py --restore
"""

import json
import sys
import os
import copy
import glob
import shutil
import argparse
from datetime import datetime

# Constants
ALERTS_FILE = "ucsd_alerts_geocoded.json"
BACKUP_DIR = "geocode_backups"
ORIG_BACKUP = os.path.join(BACKUP_DIR, "ucsd_alerts_geocoded_original.json")
SERVICES_DIR = "geocode_services"
GEOJSON_DIR = "geocode_geojson"
SERVICE_METADATA_FILE = "geocode_services.json"

def ensure_directories():
    """Ensure that necessary directories exist."""
    for directory in [BACKUP_DIR, SERVICES_DIR, GEOJSON_DIR]:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")

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

def backup_alerts_file():
    """Create a backup of the current alerts file."""
    ensure_directories()
    
    # Check if alerts file exists
    if not os.path.exists(ALERTS_FILE):
        print(f"Error: {ALERTS_FILE} not found")
        return False
    
    # Create timestamp backup
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(BACKUP_DIR, f"ucsd_alerts_geocoded_{timestamp}.json")
    
    try:
        shutil.copy2(ALERTS_FILE, backup_file)
        print(f"Created backup: {backup_file}")
        
        # Also create/update the original backup if it doesn't exist
        if not os.path.exists(ORIG_BACKUP):
            shutil.copy2(ALERTS_FILE, ORIG_BACKUP)
            print(f"Created original backup: {ORIG_BACKUP}")
        
        return True
    except Exception as e:
        print(f"Error creating backup: {e}")
        return False

def restore_alerts_file():
    """Restore the alerts file from the original backup."""
    if not os.path.exists(ORIG_BACKUP):
        print(f"Error: Original backup file not found: {ORIG_BACKUP}")
        return False
    
    try:
        shutil.copy2(ORIG_BACKUP, ALERTS_FILE)
        print(f"Restored alerts file from original backup")
        return True
    except Exception as e:
        print(f"Error restoring alerts file: {e}")
        return False

def find_geocoding_services():
    """Find all available geocoding service files."""
    geocode_files = glob.glob("*_geocode.json")
    services = []
    
    for file in geocode_files:
        service_name = file.replace("_geocode.json", "")
        services.append({
            "id": service_name,
            "file": file
        })
    
    return services

def update_alerts_with_geocoding(alerts, geocoding_data):
    """
    Update alerts with geocoding data.
    
    Args:
        alerts: List of alert dictionaries
        geocoding_data: Dictionary mapping location_text to geocoding info
        
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
        
        # Add a source field to track which service provided this geocoding
        alert["geocode_source"] = service_name
        
        stats["updated"] += 1
    
    return updated_alerts, stats

def generate_geojson(alerts, output_file, service_name=None):
    """Generate a GeoJSON file from alerts data."""
    # Convert to GeoJSON
    features = []
    for alert in alerts:
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
                    "geocode_source": alert.get("geocode_source") or service_name or "unknown"
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
    
    return save_json_file(geojson, output_file)

def process_service(service_name, service_file, alerts, update_main=False):
    """Process a single geocoding service."""
    # Load geocoding data
    geocoding_data = load_json_file(service_file)
    if geocoding_data is None:
        return None
    
    print(f"Loaded {len(geocoding_data)} geocoded locations from {service_file}")
    
    # Update alerts
    updated_alerts, stats = update_alerts_with_geocoding(alerts, geocoding_data)
    
    # Save updated alerts to service-specific file
    service_alerts_file = os.path.join(SERVICES_DIR, f"ucsd_alerts_geocoded_{service_name}.json")
    if not save_json_file(updated_alerts, service_alerts_file):
        return None
    
    # Generate GeoJSON
    geojson_file = os.path.join(GEOJSON_DIR, f"ucsd_alerts_{service_name}_geojson.json")
    generate_geojson(updated_alerts, geojson_file, service_name)
    
    # If update_main is True, also update the main alerts file
    if update_main:
        # First, create a backup
        if not backup_alerts_file():
            print("Warning: Failed to create backup. Not updating main alerts file.")
            return stats
        
        # Save to main alerts file
        if save_json_file(updated_alerts, ALERTS_FILE):
            print(f"Updated main alerts file with {service_name} geocoding")
    
    return stats

def update_service_metadata(services_with_stats):
    """Update the service metadata file with stats."""
    metadata = {
        "services": services_with_stats,
        "updated_at": datetime.now().isoformat()
    }
    
    return save_json_file(metadata, SERVICE_METADATA_FILE)

def print_stats(stats, service_name):
    """Print statistics for a service."""
    if not stats:
        return
    
    print(f"\nStatistics for {service_name}:")
    print(f"Total alerts: {stats['total_alerts']}")
    print(f"Updated: {stats['updated']} ({stats['updated'] / stats['total_alerts'] * 100:.1f}%)")
    print(f"Skipped (no match): {stats['skipped_no_match']} ({stats['skipped_no_match'] / stats['total_alerts'] * 100:.1f}%)")
    print(f"Skipped (null coords): {stats['skipped_null_coords']} ({stats['skipped_null_coords'] / stats['total_alerts'] * 100:.1f}%)")

def main():
    parser = argparse.ArgumentParser(description="Geocode Comparison Tool")
    parser.add_argument("--generate-all", action="store_true", help="Generate files for all available geocoding services")
    parser.add_argument("--service", help="Generate files only for the specified service")
    parser.add_argument("--apply", help="Apply the geocoding from a service to the main alerts file")
    parser.add_argument("--restore", action="store_true", help="Restore the original alerts file from backup")
    parser.add_argument("--backup", action="store_true", help="Create a backup of the current alerts file")
    parser.add_argument("--list", action="store_true", help="List all available geocoding services")
    
    args = parser.parse_args()
    
    # Ensure directories exist
    ensure_directories()
    
    # Handle restore operation
    if args.restore:
        if restore_alerts_file():
            print("Successfully restored alerts file to original state")
        else:
            print("Failed to restore alerts file")
        return
    
    # Handle backup operation
    if args.backup:
        if backup_alerts_file():
            print("Successfully created backup of alerts file")
        else:
            print("Failed to create backup")
        return
    
    # Find available services
    services = find_geocoding_services()
    if not services:
        print("No geocoding services found (*_geocode.json)")
        return
    
    # Handle list operation
    if args.list:
        print(f"Found {len(services)} geocoding services:")
        for i, service in enumerate(services, 1):
            print(f"{i}. {service['id']} ({service['file']})")
        return
    
    # Load alerts
    alerts = load_json_file(ALERTS_FILE)
    if alerts is None:
        return
    
    print(f"Loaded {len(alerts)} alerts from {ALERTS_FILE}")
    
    # Initialize storage for service stats
    services_with_stats = []
    
    # Handle apply operation
    if args.apply:
        target_service = None
        for service in services:
            if service["id"] == args.apply:
                target_service = service
                break
        
        if not target_service:
            print(f"Error: Service '{args.apply}' not found")
            print("Available services:")
            for service in services:
                print(f"- {service['id']}")
            return
        
        print(f"Applying {args.apply} geocoding to main alerts file...")
        stats = process_service(target_service["id"], target_service["file"], alerts, update_main=True)
        if stats:
            print_stats(stats, target_service["id"])
        return
    
    # Handle service operation
    if args.service:
        target_service = None
        for service in services:
            if service["id"] == args.service:
                target_service = service
                break
        
        if not target_service:
            print(f"Error: Service '{args.service}' not found")
            print("Available services:")
            for service in services:
                print(f"- {service['id']}")
            return
        
        print(f"Processing {args.service} geocoding...")
        stats = process_service(target_service["id"], target_service["file"], alerts)
        if stats:
            print_stats(stats, target_service["id"])
            
            # Add to services with stats
            services_with_stats.append({
                "id": target_service["id"],
                "file": target_service["file"],
                "alerts_file": os.path.join(SERVICES_DIR, f"ucsd_alerts_geocoded_{target_service['id']}.json"),
                "geojson_file": os.path.join(GEOJSON_DIR, f"ucsd_alerts_{target_service['id']}_geojson.json"),
                "stats": stats
            })
            
            # Update metadata
            update_service_metadata(services_with_stats)
        return
    
    # Handle generate-all operation
    if args.generate_all:
        print(f"Processing all {len(services)} geocoding services...")
        
        # Process each service
        for service in services:
            print(f"\nProcessing {service['id']} geocoding...")
            stats = process_service(service["id"], service["file"], alerts)
            if stats:
                print_stats(stats, service["id"])
                
                # Add to services with stats
                services_with_stats.append({
                    "id": service["id"],
                    "file": service["file"],
                    "alerts_file": os.path.join(SERVICES_DIR, f"ucsd_alerts_geocoded_{service['id']}.json"),
                    "geojson_file": os.path.join(GEOJSON_DIR, f"ucsd_alerts_{service['id']}_geojson.json"),
                    "stats": stats
                })
        
        # Update metadata
        if services_with_stats:
            update_service_metadata(services_with_stats)
            
            print("\n=== Summary ===")
            print(f"{'Service':<15} {'Updated':<15} {'No Match':<15} {'Null Coords':<15}")
            print("-" * 60)
            for service in services_with_stats:
                stats = service["stats"]
                updated_percent = f"{stats['updated'] / stats['total_alerts'] * 100:.1f}%"
                print(f"{service['id']:<15} {updated_percent:<15} {stats['skipped_no_match']:<15} {stats['skipped_null_coords']:<15}")
        return
    
    # If no specific operation was requested, show help
    parser.print_help()

if __name__ == "__main__":
    main()