# geocode_routes.py
# Simple version of geocoding routes that can be included in your app.py

import os
import json
import shutil
import copy
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse

# Create a router
geocode_router = APIRouter()

# Constants
DATA_FILE = "ucsd_alerts_geocoded.json"
BACKUP_DIR = "data_backups"
GEOCODE_LOC_DIR = "geocoded_loc"  # Custom directory for geocoding service files

# Function to find geocoding services
def find_geocoding_services():
    """Find all available geocoding service files in the geocoded_loc directory."""
    services = {}
    if os.path.exists(GEOCODE_LOC_DIR):
        for file in os.listdir(GEOCODE_LOC_DIR):
            if file.endswith("_geocode.json"):
                service_name = file.replace("_geocode.json", "")
                services[service_name] = os.path.join(GEOCODE_LOC_DIR, file)
    return services

# Route to get metadata about available geocoding services
@geocode_router.get("/api/geocoding-metadata")
async def get_geocoding_metadata():
    """Return metadata about available geocoding services."""
    services = []
    
    # Add current service
    services.append({
        "id": "current",
        "name": "Current (Custom)",
        "description": "Our specialized database for UCSD campus"
    })
    
    # Find service files in the geocoded_loc directory
    geocoding_services = find_geocoding_services()
    
    # Add each service
    for service_id, file_path in geocoding_services.items():
        service_info = {
            "id": service_id,
            "file": file_path,
            "name": format_service_name(service_id),
            "description": get_service_description(service_id)
        }
        
        # Add to services list
        services.append(service_info)
    
    return {"services": services}

# Route to apply a geocoding service
@geocode_router.post("/api/apply-geocoding/{service_id}")
async def apply_geocoding_service(service_id: str):
    """Apply a geocoding service to the main alerts file."""
    # If restoring current, use the original backup
    if service_id == "current":
        return await restore_original_geocoding()
    
    # Find the service file
    geocoding_services = find_geocoding_services()
    if service_id not in geocoding_services:
        return JSONResponse({"error": f"Geocoding service '{service_id}' not found"}, status_code=404)
    
    service_file = geocoding_services[service_id]
    
    # Ensure backup directory exists
    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    # Create a backup
    backup_file = os.path.join(BACKUP_DIR, f"alerts_before_{service_id}.json")
    try:
        shutil.copy2(DATA_FILE, backup_file)
    except Exception as e:
        return JSONResponse({"error": f"Failed to create backup: {str(e)}"}, status_code=500)
    
    # Create original backup if it doesn't exist
    original_backup = os.path.join(BACKUP_DIR, "alerts_original.json")
    if not os.path.exists(original_backup):
        try:
            shutil.copy2(DATA_FILE, original_backup)
        except Exception as e:
            pass
    
    # Apply the geocoding
    try:
        # Load original alerts
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            alerts = json.load(f)
        
        # Load geocoding data
        with open(service_file, "r", encoding="utf-8") as f:
            geocoding_data = json.load(f)
        
        # Apply geocoding
        updated_alerts = []
        updated_count = 0
        
        for alert in alerts:
            location_text = alert.get("location_text")
            if location_text in geocoding_data:
                geo_info = geocoding_data[location_text]
                if geo_info.get("lat") is not None and geo_info.get("lng") is not None:
                    # Create a copy of the alert
                    updated_alert = copy.deepcopy(alert)
                    # Update coordinates
                    updated_alert["lat"] = geo_info["lat"]
                    updated_alert["lng"] = geo_info["lng"]
                    updated_alert["address"] = geo_info["address"]
                    updated_alerts.append(updated_alert)
                    updated_count += 1
                else:
                    # Keep original if missing coordinates
                    updated_alerts.append(alert)
            else:
                # Keep original if not in geocoding data
                updated_alerts.append(alert)
        
        # Save updated alerts
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(updated_alerts, f, indent=2)
        
        return {
            "success": True, 
            "message": f"Applied {service_id} geocoding",
            "updated_count": updated_count,
            "total_count": len(alerts)
        }
    except Exception as e:
        # Restore from backup on error
        try:
            shutil.copy2(backup_file, DATA_FILE)
        except:
            pass
        return JSONResponse({"error": f"Error applying geocoding: {str(e)}"}, status_code=500)

# Route to restore original geocoding
@geocode_router.post("/api/restore-geocoding")
async def restore_original_geocoding():
    """Restore the original geocoding from backup."""
    original_backup = os.path.join(BACKUP_DIR, "alerts_original.json")
    
    # Check if original backup exists
    if not os.path.exists(original_backup):
        return JSONResponse({"error": "Original backup not found - no changes have been applied yet"}, status_code=404)
    
    # Restore from backup
    try:
        shutil.copy2(original_backup, DATA_FILE)
        return {"success": True, "message": "Restored original geocoding"}
    except Exception as e:
        return JSONResponse({"error": f"Error restoring original geocoding: {str(e)}"}, status_code=500)

# Route to get metrics for a service
@geocode_router.get("/api/geocoding-metrics/{service_id}")
async def get_geocoding_metrics(service_id: str):
    """Return metrics for a geocoding service."""
    # Simulated metrics for demonstration
    metrics = {
        'current': {
            'locationsFound': '98%',
            'avgDistance': '15 meters',
            'campusAccuracy': '97%'
        },
        'deepseek': {
            'locationsFound': '87%',
            'avgDistance': '112 meters',
            'campusAccuracy': '82%'
        },
        'gemini-pro': {
            'locationsFound': '85%',
            'avgDistance': '145 meters',
            'campusAccuracy': '79%'
        },
        'mistral': {
            'locationsFound': '73%',
            'avgDistance': '210 meters',
            'campusAccuracy': '68%'
        },
        'openstreetmaps': {
            'locationsFound': '62%',
            'avgDistance': '323 meters',
            'campusAccuracy': '45%'
        }
    }
    
    # Return metrics or defaults
    if service_id in metrics:
        return metrics[service_id]
    else:
        return {
            'locationsFound': '-',
            'avgDistance': '-',
            'campusAccuracy': '-'
        }

# Helper Functions for geocoding services
def format_service_name(service_id: str) -> str:
    """Format a service ID into a user-friendly name."""
    name_map = {
        'current': 'Current (Custom)',
        'deepseek': 'DeepSeek-R1 LLM',
        'gemini-pro': 'Google Gemini Pro',
        'mistral': 'Mistral Large',
        'openstreetmaps': 'OpenStreetMaps'
    }
    
    return name_map.get(service_id, service_id.capitalize())

def get_service_description(service_id: str) -> str:
    """Get a description for a service ID."""
    description_map = {
        'current': 'Our specialized database for UCSD campus',
        'deepseek': 'A large language model with general knowledge',
        'gemini-pro': 'Google\'s advanced language model',
        'mistral': 'An open-source language model',
        'openstreetmaps': 'Traditional geocoding service'
    }
    
    return description_map.get(service_id, 'Alternative geocoding service')