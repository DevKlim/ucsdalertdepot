# app.py
import json
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
from scraper import scrape_ucsd_alerts

app = FastAPI()

# Mount the static folder for CSS/JS
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

DATA_FILE = "ucsd_alerts.json"

def update_data():
    """Run the scraper and save the alerts to a JSON file."""
    print("Scraping UCSD alerts...")
    alerts = scrape_ucsd_alerts()
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(alerts, f, indent=2)
    print(f"Updated data with {len(alerts)} alerts.")

# Schedule the scraper to run daily (e.g., at 2:00 AM)
scheduler = AsyncIOScheduler()
scheduler.add_job(update_data, 'cron', hour=2, minute=0)
scheduler.start()

# On startup, update the data once.
@app.on_event("startup")
async def startup_event():
    # Run the update in a separate thread so as not to block startup
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(None, update_data)

@app.get("/", response_class=HTMLResponse)
async def read_index(request: Request):
    """Serve the main HTML page."""
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/api/crimes", response_class=JSONResponse)
async def get_crimes():
    """
    Read the alerts JSON file and return a GeoJSON FeatureCollection.
    Only alerts with lat/lng are included.
    """
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception as e:
        return JSONResponse({"error": f"Data file not found: {e}"}, status_code=500)

    features = []
    for alert in data:
        # Create a GeoJSON feature if lat/lng are present.
        if "lat" in alert and "lng" in alert:
            feature = {
                "type": "Feature",
                "properties": {
                    "title": alert["alert_title"],
                    "crime_type": alert["crime_type"],
                    "alert_type": alert["alert_type"],
                    "date": alert["date"],
                    "is_update": alert["is_update"],
                    "suspect_info": alert["suspect_info"],
                    "details_url": alert["details_url"],
                    "location_text": alert["location_text"]
                },
                "geometry": {
                    "type": "Point",
                    "coordinates": [alert["lng"], alert["lat"]]
                }
            }
            features.append(feature)
    geojson = {
        "type": "FeatureCollection",
        "features": features
    }
    return geojson
