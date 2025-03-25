# app.py
import json
import datetime
import copy
import os
import subprocess
import shutil
from fastapi import FastAPI, Request, Response, Query, Body
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from typing import Optional, List, Dict, Any

# Import Safe Campus Agent
from safe_campus_agent import SafeCampusAgent

app = FastAPI()

# Global toggle for scraping (default OFF)
SCRAPING_ENABLED = False

# Mount the static folder
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Initialize the Safe Campus Agent
safe_campus_agent = SafeCampusAgent()

# Data file and directories
DATA_FILE = "ucsd_alerts_geocoded.json"
BACKUP_DIR = "data_backups"
GEOCODE_LOC_DIR = "geocoded_loc"  # Custom directory for geocoding service files

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

# Main index page
@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    """Serve the main HTML page."""
    return templates.TemplateResponse("index.html", {"request": request, "scraping_enabled": SCRAPING_ENABLED})

@app.get("/safe-campus-agent", response_class=HTMLResponse)
async def safe_campus_agent_demo(request: Request):
    """Serve the Safe Campus Agent demo page."""
    return templates.TemplateResponse("safe_campus_demo.html", {"request": request})

@app.post("/api/process_call", response_class=JSONResponse)
async def process_call(data: Dict[str, Any] = Body(...)):
    """Process an emergency call transcript."""
    transcript = data.get("transcript", "")
    if not transcript:
        return JSONResponse({"error": "No transcript provided"}, status_code=400)
    
    try:
        result = safe_campus_agent.process_emergency_call(transcript)
        return result
    except Exception as e:
        return JSONResponse({"error": f"Error processing call: {str(e)}"}, status_code=500)

@app.post("/api/process_report", response_class=JSONResponse)
async def process_report(data: Dict[str, Any] = Body(...)):
    """
    Process a written incident report.
    
    Args:
        data: Dictionary with 'report' key
        
    Returns:
        Processing results
    """
    report = data.get("report", "")
    if not report:
        return JSONResponse({"error": "No report provided"}, status_code=400)
    
    try:
        result = safe_campus_agent.process_incident_report(report)
        return result
    except Exception as e:
        return JSONResponse({"error": f"Error processing report: {str(e)}"}, status_code=500)

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

# Keep the process.html route
@app.get("/process", response_class=HTMLResponse)
async def process(request: Request):
    """Serve the project process page with scrollama visualization."""
    return templates.TemplateResponse("process.html", {"request": request})

@app.get("/favicon.ico", response_class=FileResponse)
async def favicon():
    """Serve the favicon."""
    return FileResponse("static/favicon.ico")

@app.get("/health")
async def health_check():
    """Return basic health information about the application."""
    import os
    
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
    
    return {
        "status": "ok",
        "timestamp": datetime.datetime.now().isoformat(),
        "version": "1.0.0",
        "data_file": DATA_FILE,
        "data_stats": data_stats,
        "safe_campus_agent": "active"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)