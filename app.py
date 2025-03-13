# app.py
import json
import csv
import datetime
import copy
import os
import subprocess
import shutil
from fastapi import FastAPI, Request, Response, Query
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from geocode_routes import geocode_router
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
from typing import Optional, List

app = FastAPI()
app.include_router(geocode_router)

# Global toggle for scraping (default OFF)
SCRAPING_ENABLED = False

# Mount the static folder
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Data file and directories
DATA_FILE = "ucsd_alerts_geocoded.json"
BACKUP_DIR = "data_backups"
GEOCODE_LOC_DIR = "geocoded_loc"  # Custom directory for geocoding service files

# Geocoding service files - look in the geocoded_loc directory
def find_geocoding_services():
    """Find all available geocoding service files in the geocoded_loc directory."""
    services = {}
    if os.path.exists(GEOCODE_LOC_DIR):
        for file in os.listdir(GEOCODE_LOC_DIR):
            if file.endswith("_geocode.json"):
                service_name = file.replace("_geocode.json", "")
                services[service_name] = os.path.join(GEOCODE_LOC_DIR, file)
    return services

# Directories for processing
GEOCODE_BACKUPS_DIR = os.path.join(BACKUP_DIR, "geocode_backups")
GEOCODE_SERVICES_DIR = "geocode_services"
GEOCODE_GEOJSON_DIR = "geocode_geojson"

# Perform startup checks
@app.on_event("startup")
async def startup_event():
    # Check if data file exists, create empty one if it doesn't
    if not os.path.exists(DATA_FILE):
        print(f"Data file {DATA_FILE} not found. Creating empty data file.")
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)
    else:
        print(f"Found data file: {DATA_FILE}")
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            print(f"Successfully loaded {len(data)} alerts from data file.")
        except Exception as e:
            print(f"Error loading data file: {e}")
    
    # Ensure directories exist
    for directory in [BACKUP_DIR, GEOCODE_BACKUPS_DIR, GEOCODE_SERVICES_DIR, GEOCODE_GEOJSON_DIR]:
        if not os.path.exists(directory):
            os.makedirs(directory)
            print(f"Created directory: {directory}")
    
    # Create original backup if it doesn't exist
    original_backup = os.path.join(GEOCODE_BACKUPS_DIR, "ucsd_alerts_geocoded_original.json")
    if not os.path.exists(original_backup) and os.path.exists(DATA_FILE):
        try:
            shutil.copy2(DATA_FILE, original_backup)
            print(f"Created original backup: {original_backup}")
        except Exception as e:
            print(f"Error creating original backup: {e}")
    
    # Find available geocoding services
    services = find_geocoding_services()
    print(f"Found {len(services)} geocoding services: {list(services.keys())}")

# Main index page
@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    """Serve the main HTML page."""
    return templates.TemplateResponse("index.html", {"request": request, "scraping_enabled": SCRAPING_ENABLED})

# API Routes for geocoding service operations
@app.get("/api/geocoding-metadata")
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

@app.post("/api/apply-geocoding/{service_id}")
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
    
    # Create a backup
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = os.path.join(GEOCODE_BACKUPS_DIR, f"ucsd_alerts_geocoded_{timestamp}.json")
    try:
        shutil.copy2(DATA_FILE, backup_file)
    except Exception as e:
        return JSONResponse({"error": f"Failed to create backup: {str(e)}"}, status_code=500)
    
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
                    updated_alert["geocode_source"] = service_id
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

@app.post("/api/restore-geocoding")
async def restore_original_geocoding():
    """Restore the original geocoding from backup."""
    original_backup = os.path.join(GEOCODE_BACKUPS_DIR, "ucsd_alerts_geocoded_original.json")
    
    # Check if original backup exists
    if not os.path.exists(original_backup):
        return JSONResponse({"error": "Original backup not found"}, status_code=404)
    
    # Restore from backup
    try:
        shutil.copy2(original_backup, DATA_FILE)
        return {"success": True, "message": "Restored original geocoding"}
    except Exception as e:
        return JSONResponse({"error": f"Error restoring original geocoding: {str(e)}"}, status_code=500)

@app.get("/api/geocoding-metrics/{service_id}")
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

# Original API Routes
@app.get("/api/crimes", response_class=JSONResponse)
async def get_crimes(
    alert_types: Optional[List[str]] = Query(None),
    crime_types: Optional[List[str]] = Query(None),
    date_from: Optional[str] = None,
    date_to: Optional[str] = None,
):
    """
    Return a GeoJSON FeatureCollection of alerts with optional filtering.
    
    Query parameters:
    - alert_types: List of alert types to include
    - crime_types: List of crime types to include
    - date_from: Filter alerts from this date (MM/DD/YYYY)
    - date_to: Filter alerts to this date (MM/DD/YYYY)
    """
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        return JSONResponse({"error": f"Data file not found or invalid: {e}"}, status_code=500)
    
    # Apply filters if provided
    if alert_types or crime_types or date_from or date_to:
        filtered_data = []
        
        # Parse date strings to datetime objects for comparison
        from_date = None
        to_date = None
        if date_from:
            try:
                parts = date_from.split('/')
                from_date = datetime.datetime(int(parts[2]), int(parts[0]), int(parts[1]))
            except:
                pass
        
        if date_to:
            try:
                parts = date_to.split('/')
                to_date = datetime.datetime(int(parts[2]), int(parts[0]), int(parts[1]))
                # Set to end of day for inclusive filtering
                to_date = to_date.replace(hour=23, minute=59, second=59)
            except:
                pass
        
        for alert in data:
            # Filter by alert type
            if alert_types and alert["alert_type"] not in alert_types:
                continue
                
            # Filter by crime type
            if crime_types and alert["crime_type"] not in crime_types:
                continue
                
            # Filter by date range
            if from_date or to_date:
                try:
                    parts = alert["date"].split('/')
                    alert_date = datetime.datetime(int(parts[2]), int(parts[0]), int(parts[1]))
                    
                    if from_date and alert_date < from_date:
                        continue
                        
                    if to_date and alert_date > to_date:
                        continue
                except:
                    # If date parsing fails, include the alert anyway
                    pass
                    
            # Alert passed all filters
            filtered_data.append(alert)
        
        data = filtered_data

    # Convert to GeoJSON
    features = []
    for alert in data:
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
                    "geocode_source": alert.get("geocode_source", "custom")  # Add geocoding source
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
    
    return geojson

@app.get("/api/crime-types", response_class=JSONResponse)
async def get_crime_types():
    """Return a list of all unique crime types in the dataset."""
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        return JSONResponse({"error": f"Data file not found: {e}"}, status_code=500)
    
    # Extract unique crime types
    crime_types = set()
    for alert in data:
        if "crime_type" in alert and alert["crime_type"]:
            crime_types.add(alert["crime_type"])
    
    return {"crime_types": sorted(list(crime_types))}

@app.get("/api/alert-types", response_class=JSONResponse)
async def get_alert_types():
    """Return a list of all unique alert types in the dataset."""
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        return JSONResponse({"error": f"Data file not found: {e}"}, status_code=500)
    
    # Extract unique alert types
    alert_types = set()
    for alert in data:
        if "alert_type" in alert and alert["alert_type"]:
            alert_types.add(alert["alert_type"])
    
    return {"alert_types": sorted(list(alert_types))}

@app.get("/api/date-range", response_class=JSONResponse)
async def get_date_range():
    """Return the earliest and latest dates in the dataset."""
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        return JSONResponse({"error": f"Data file not found: {e}"}, status_code=500)
    
    from datetime import datetime
    
    earliest_date = None
    latest_date = None
    
    for alert in data:
        if "date" in alert and alert["date"] and alert["date"] != "Unknown":
            try:
                # Parse date from MM/DD/YYYY format
                parts = alert["date"].split('/')
                alert_date = datetime(int(parts[2]), int(parts[0]), int(parts[1]))
                
                if earliest_date is None or alert_date < earliest_date:
                    earliest_date = alert_date
                
                if latest_date is None or alert_date > latest_date:
                    latest_date = alert_date
            except:
                # Skip dates that can't be parsed
                continue
    
    result = {
        "start_date": earliest_date.strftime("%m/%d/%Y") if earliest_date else None,
        "end_date": latest_date.strftime("%m/%d/%Y") if latest_date else None
    }
    
    return result

@app.get("/export_csv")
async def export_csv():
    """
    Exports all alert data as CSV with columns including geocoded information.
    """
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        return JSONResponse({"error": f"Data file not found: {e}"}, status_code=500)
    
    # Include all fields, including geocoded fields
    headers = ["date", "alert_title", "alert_type", "crime_type", "is_update", 
               "location_text", "precise_location", "address", "suspect_info", 
               "description", "lat", "lng", "geocode_source"]
    
    def iter_csv():
        from io import StringIO
        csv_file = StringIO()
        writer = csv.DictWriter(csv_file, fieldnames=headers)
        writer.writeheader()
        yield csv_file.getvalue()
        csv_file.seek(0)
        csv_file.truncate(0)
        for row in data:
            # Filter row to only include fields in headers
            filtered_row = {k: row.get(k, "") for k in headers}
            writer.writerow(filtered_row)
            yield csv_file.getvalue()
            csv_file.seek(0)
            csv_file.truncate(0)
    
    return StreamingResponse(iter_csv(), media_type="text/csv", 
                             headers={"Content-Disposition": "attachment; filename=ucsd_alerts_geocoded.csv"})

@app.get("/instructions", response_class=HTMLResponse)
async def instructions(request: Request):
    """Provide detailed instructions for using the application."""
    return templates.TemplateResponse("instructions.html", {"request": request})

@app.get("/favicon.ico", response_class=FileResponse)
async def favicon():
    """Serve the favicon."""
    return FileResponse("static/favicon.ico")

@app.get("/health")
async def health_check():
    """Return basic health information about the application."""
    import psutil
    import os
    
    process = psutil.Process(os.getpid())
    
    # Get basic stats about the data file
    data_stats = {"count": 0, "file_size_kb": 0}
    try:
        if os.path.exists(DATA_FILE):
            data_stats["file_size_kb"] = round(os.path.getsize(DATA_FILE) / 1024, 2)
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
            data_stats["count"] = len(data)
    except Exception as e:
        data_stats["error"] = str(e)
    
    # Get info about geocoding services
    geocoding_stats = {"services": list(find_geocoding_services().keys())}
    
    return {
        "status": "ok",
        "timestamp": datetime.datetime.now().isoformat(),
        "version": "1.0.0",
        "data_file": DATA_FILE,
        "data_stats": data_stats,
        "memory_usage_mb": round(process.memory_info().rss / (1024 * 1024), 2),
        "cpu_percent": process.cpu_percent(interval=0.1),
        "geocoding_stats": geocoding_stats
    }

@app.get("/presentation", response_class=HTMLResponse)
async def presentation(request: Request):
    """Serve the project presentation page."""
    return templates.TemplateResponse("presentation.html", {"request": request})

@app.get("/process", response_class=HTMLResponse)
async def process(request: Request):
    """Serve the project process page with scrollama visualization."""
    return templates.TemplateResponse("process.html", {"request": request})