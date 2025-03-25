import csv
import json
import time
import os
import random
import math
from mistralai import Mistral

# Configuration
INPUT_CSV = "alerts.csv"
OUTPUT_CSV = "alerts_geocoded.csv"
OUTPUT_JSON = "ucsd_alerts_geocoded.json"
KNOWN_LOCATIONS_FILE = "known_locations.json"
BATCH_SIZE = 5  # Process this many unknown locations at once
MAX_ATTEMPTS = 3  # Max retry attempts for API calls
PAUSE_SECONDS = 2  # Pause between retries

# Mistral API configuration
API_KEY = os.environ.get("MISTRAL_API_KEY", "0y7ZgwMeDjtawMwmAcpo7i9polWc3TKM")
MODEL = "mistral-large-latest"

# Initialize with default locations (these will be updated from the JSON file if it exists)
DEFAULT_KNOWN_LOCATIONS = {
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
    }
}

def load_known_locations():
    """Load known locations from JSON file or use defaults if file doesn't exist."""
    try:
        if os.path.exists(KNOWN_LOCATIONS_FILE):
            with open(KNOWN_LOCATIONS_FILE, 'r', encoding='utf-8') as f:
                locations = json.load(f)
            print(f"Loaded {len(locations)} known locations from {KNOWN_LOCATIONS_FILE}")
            return locations
        else:
            print(f"Known locations file not found. Using default locations.")
            return DEFAULT_KNOWN_LOCATIONS
    except Exception as e:
        print(f"Error loading known locations: {e}. Using default locations.")
        return DEFAULT_KNOWN_LOCATIONS

def save_known_locations(locations):
    """Save updated known locations to JSON file."""
    try:
        with open(KNOWN_LOCATIONS_FILE, 'w', encoding='utf-8') as f:
            json.dump(locations, f, indent=2)
        print(f"Saved {len(locations)} known locations to {KNOWN_LOCATIONS_FILE}")
    except Exception as e:
        print(f"Error saving known locations: {e}")

def jitter_coordinates(lat, lng, meters=30):
    """
    Add a small random jitter to coordinates (up to specified meters) 
    to avoid multiple points plotting exactly on top of each other.
    """
    lat_jitter = (random.uniform(-meters, meters) / 111111)
    lng_jitter = (random.uniform(-meters, meters) / (111111 * abs(math.cos(math.radians(lat)))))
    
    return lat + lat_jitter, lng + lng_jitter

def is_known_location(location_text, known_locations):
    """Check if location contains any known landmarks."""
    if not location_text:
        return False
        
    for landmark in known_locations.keys():
        if landmark.lower() in location_text.lower():
            return True
    return False

def get_coordinates_and_address_for_known_location(location_text, known_locations):
    """If location contains a known landmark, return its coordinates with jitter and address."""
    if not location_text:
        return None, None, None
        
    for landmark, info in known_locations.items():
        if landmark.lower() in location_text.lower():
            lat, lng = jitter_coordinates(info["lat"], info["lng"])
            return lat, lng, info["address"]
    return None, None, None

def build_geocoding_prompt(locations):
    """Create a prompt for the LLM to geocode unknown locations."""
    prompt_lines = [
        "You are a geocoding assistant specializing in determining specific addresses, latitude, and longitude coordinates for any location in the world.",
        "For each of the following locations, determine the precise address and coordinates.",
        "While many of these locations may be near UC San Diego, don't limit your search to just the campus area.",
        "",
        "For each location:",
        "1. Identify the precise building, landmark, or area described (make sure the lat and lng is extremely exact and not based off address)",
        "2. Determine the most accurate and complete address (including building number, street, city, state, and zip code if available)",
        "3. Provide the exact latitude and longitude coordinates",
        "4. For locations at UC San Diego, use your knowledge of the campus layout to provide detailed addresses",
        "5. For locations outside UC San Diego, determine their real-world addresses and coordinates",
        "",
        "IMPORTANT GUIDELINES:",
        "- Provide coordinates with 6 decimal precision",
        "- For UC San Diego campus locations, include '9500 Gilman Dr, La Jolla, CA 92093' as part of the address if appropriate",
        "- For locations with building numbers, include those in the address",
        "- If a location is completely unidentifiable, use the address for San Diego downtown",
        "- DO NOT restrict your geocoding to just the UCSD area",
        "- If the location mentions a specific address or neighborhood outside UCSD, find those real coordinates and address",
        "",
        "OUTPUT FORMAT: Return ONLY a JSON array of objects, where each object has:",
        "- 'location': the original location string",
        "- 'name': a standardized shorter name for this location (for future reference)",
        "- 'address': the full detailed address for this location",
        "- 'lat': latitude as a float",
        "- 'lng': longitude as a float",
        "",
        "LOCATIONS TO GEOCODE:"
    ]
    
    for idx, location in enumerate(locations, start=1):
        prompt_lines.append(f"{idx}. {location}")
    
    return "\n".join(prompt_lines)

def extract_json_from_response(response_text):
    """Extract and clean JSON from the response text."""
    response_text = response_text.strip()
    
    # Handle markdown code blocks
    if "```json" in response_text or "```" in response_text:
        # Extract content between code fences
        start = response_text.find("```") + 3
        if response_text[start:start+4] == "json":
            start += 4
        end = response_text.rfind("```")
        if start < end:
            response_text = response_text[start:end].strip()
    
    return response_text

def geocode_unknown_locations_with_mistral(unknown_locations):
    """
    Use Mistral AI to geocode unknown location addresses to coordinates.
    Returns: Dictionary mapping each location to its coordinates and address
    """
    if not unknown_locations:
        return {}
        
    # Initialize Mistral client
    client = Mistral(api_key=API_KEY)
    
    # Process in batches
    location_batches = [unknown_locations[i:i+BATCH_SIZE] 
                        for i in range(0, len(unknown_locations), BATCH_SIZE)]
    
    results = {}
    
    for batch_idx, batch in enumerate(location_batches):
        print(f"Geocoding batch {batch_idx+1}/{len(location_batches)} ({len(batch)} locations)")
        
        prompt = build_geocoding_prompt(batch)
        
        attempts = MAX_ATTEMPTS
        while attempts > 0:
            try:
                response = client.chat.complete(
                    model=MODEL,
                    messages=[{"role": "user", "content": prompt}]
                )
                
                if not response or not hasattr(response, "choices") or not response.choices:
                    raise ValueError("No completion choices returned.")
                
                result_text = response.choices[0].message.content
                json_text = extract_json_from_response(result_text)
                
                try:
                    geocoded_results = json.loads(json_text)
                    
                    # Validate results format
                    if not isinstance(geocoded_results, list):
                        raise ValueError(f"Expected JSON array, got: {type(geocoded_results)}")
                    
                    for result in geocoded_results:
                        # Check required fields
                        if not all(k in result for k in ["location", "name", "address", "lat", "lng"]):
                            print(f"Warning: Missing required keys in result: {result}")
                            continue
                        
                        location = result["location"]
                        name = result["name"]
                        address = result["address"]
                        lat = float(result["lat"])
                        lng = float(result["lng"])
                        
                        # Add to results without any boundary restrictions
                        results[location] = {
                            "name": name, 
                            "address": address,
                            "lat": lat, 
                            "lng": lng
                        }
                        print(f"Geocoded: {name} | {address} | ({lat}, {lng})")
                    
                    break  # Success - exit retry loop
                    
                except json.JSONDecodeError as e:
                    raise ValueError(f"Failed to parse JSON response: {e}\nResponse: {json_text}")
                
            except Exception as e:
                attempts -= 1
                print(f"Error in geocoding attempt: {e}")
                if attempts > 0:
                    print(f"Retrying in {PAUSE_SECONDS} seconds... ({attempts} attempts left)")
                    time.sleep(PAUSE_SECONDS)
                else:
                    print(f"All attempts failed for batch. Using default coordinates.")
                    # Use default coordinates for failed locations
                    for location in batch:
                        # Use San Diego coordinates and address as fallback
                        results[location] = {
                            "name": location.split(',')[0] if ',' in location else location,
                            "address": "San Diego, California, USA",
                            "lat": 32.7157, 
                            "lng": -117.1611
                        }
        
        # Pause between batches to avoid rate limits
        if batch_idx < len(location_batches) - 1:
            time.sleep(PAUSE_SECONDS)
    
    return results

def process_alerts():
    """Process alerts CSV file, geocode locations, and save results."""
    # Load known locations
    known_locations = load_known_locations()
    
    # Read input CSV
    with open(INPUT_CSV, 'r', newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        alerts = list(reader)
    
    print(f"Read {len(alerts)} alerts from {INPUT_CSV}")
    
    # Find locations that need geocoding
    unknown_locations = []
    for alert in alerts:
        location = alert['Location Address']
        if location and not is_known_location(location, known_locations):
            if location not in unknown_locations:
                unknown_locations.append(location)
    
    print(f"Found {len(unknown_locations)} unknown locations that need geocoding")
    
    # Geocode unknown locations
    if unknown_locations:
        new_locations = geocode_unknown_locations_with_mistral(unknown_locations)
        
        # Add new locations to known locations
        for location, details in new_locations.items():
            known_locations[details["name"]] = {
                "lat": details["lat"], 
                "lng": details["lng"],
                "address": details["address"]
            }
            print(f"Added new location: {details['name']} | {details['address']} | ({details['lat']}, {details['lng']})")
        
        # Save updated known locations
        save_known_locations(known_locations)
    
    # Update alerts with geocoded coordinates and addresses
    for alert in alerts:
        location = alert['Location Address']
        
        # Try to get coordinates and address from known locations
        lat, lng, address = get_coordinates_and_address_for_known_location(location, known_locations)
        
        # If not found, use San Diego default with jitter
        if lat is None or lng is None or address is None:
            lat, lng = jitter_coordinates(32.7157, -117.1611)
            address = "San Diego, California, USA"
            print(f"Using default coordinates for: {location}")
        
        # Update the alert
        alert['Latitude'] = lat
        alert['Longitude'] = lng
        
        # Add address to the alert if it doesn't already have one
        if 'Address' not in alert:
            alert['Address'] = address
    
    # Add 'Address' field to the fieldnames if it's not there
    if 'Address' not in alerts[0]:
        for alert in alerts:
            alert['Address'] = ''
    
    # Write updated alerts to output CSV
    with open(OUTPUT_CSV, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = list(alerts[0].keys())
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(alerts)
    
    print(f"Wrote {len(alerts)} geocoded alerts to {OUTPUT_CSV}")
    
    # Format alerts into the structure used by the application
    json_alerts = []
    for alert in alerts:
        # Convert date format if needed
        date_str = alert["Time"]
        if "T" in date_str:
            # If ISO format, convert to MM/DD/YYYY
            parts = date_str.split("T")[0].split("-")
            if len(parts) == 3:
                date_str = f"{parts[1]}/{parts[2]}/{parts[0]}"
                
        json_alert = {
            "date": date_str,
            "alert_title": f"{alert['Alert Type']} - {alert['Crime Type']}",
            "alert_type": alert["Alert Type"],
            "crime_type": alert["Crime Type"],
            "is_update": alert["Is Update"].lower() == "true",
            "details_url": "",  # No URL in the CSV
            "location_text": alert["Location Address"],
            "precise_location": alert.get("Address", alert["Location Address"]),  # Use new Address field if available
            "suspect_info": "Not specified",  # Not in the CSV
            "description": f"Crime severity: {alert['Severity']}",
            "lat": float(alert["Latitude"]),
            "lng": float(alert["Longitude"]),
            "address": alert.get("Address", alert["Location Address"])  # Include address in JSON
        }
        json_alerts.append(json_alert)
    
    # Write formatted alerts to JSON
    with open(OUTPUT_JSON, 'w', encoding='utf-8') as jsonfile:
        json.dump(json_alerts, jsonfile, indent=2)
    
    print(f"Wrote {len(json_alerts)} formatted alerts to {OUTPUT_JSON}")
    print(f"Known locations database now has {len(known_locations)} entries")

if __name__ == "__main__":
    print("Starting enhanced geocoding with address lookup...")
    process_alerts()
    print("Geocoding complete!")