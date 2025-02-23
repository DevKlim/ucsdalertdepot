# scraper.py
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin
from geocode import simple_campus_geocode

BASE_URL = "https://police.ucsd.edu"
ALERTS_URL = "https://police.ucsd.edu/alerts/warnings.html"

def scrape_alert_detail_page(url):
    """
    Given a detail page URL, return a dict with additional fields:
      - description: full text of the alert (or the first 2000 characters)
      - location_text: a text snippet indicating a location (if found)
      - suspect_info: any suspect information found (if available)
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return {}

    soup = BeautifulSoup(response.text, "html.parser")
    raw_text = soup.get_text(separator="\n")

    # Try to extract a location using a simple regex: look for "at ..." or "near ..."
    location_text = None
    loc_match = re.search(r"(?:at|near)\s+([A-Za-z0-9\s,&\-]+)(?:\.|\n)", raw_text)
    if loc_match:
        location_text = loc_match.group(1).strip()

    # Try to extract suspect info with a naive pattern
    suspect_info = None
    suspect_match = re.search(r"(suspect(?:s)?\s+[^\.]+\.)", raw_text, re.IGNORECASE)
    if suspect_match:
        suspect_info = suspect_match.group(1).strip()

    return {
        "description": raw_text[:2000],
        "location_text": location_text or "Unknown",
        "suspect_info": suspect_info or "Not specified"
    }

def scrape_ucsd_alerts():
    """
    Scrapes the main alerts page, then for each alert link, scrapes the detail page.
    Returns a list of dictionaries representing each alert.
    """
    try:
        main_resp = requests.get(ALERTS_URL)
        main_resp.raise_for_status()
    except Exception as e:
        print(f"Error fetching main alerts page: {e}")
        return []

    soup_main = BeautifulSoup(main_resp.text, "html.parser")

    # Find all alert links. The page is structured in <ul> lists by year.
    alerts = []
    all_a_tags = soup_main.select("ul li a")
    for a_tag in all_a_tags:
        link_text = a_tag.get_text(strip=True)
        href = a_tag.get("href")
        if not href:
            continue
        full_url = urljoin(ALERTS_URL, href)

        # Extract date (assume date format mm/dd/yyyy appears at start)
        date_match = re.search(r"(\d{1,2}/\d{1,2}/\d{4})", link_text)
        alert_date = date_match.group(1) if date_match else "Unknown"

        # Determine alert type based on keywords in link text
        if "Timely Warning" in link_text:
            alert_type = "Timely Warning"
        elif "Triton Alert" in link_text:
            alert_type = "Triton Alert"
        elif "Community Alert" in link_text:
            alert_type = "Community Alert Bulletin"
        else:
            alert_type = "Other"

        # Determine if the alert is an update (look for "UPDATE" in text)
        is_update = "UPDATE" in link_text.upper()

        # Attempt to extract crime type (e.g., after a dash)
        crime_type = None
        crime_match = re.search(r"(?:Warning\s*[–-]\s*)(.+)$", link_text, re.IGNORECASE)
        if crime_match:
            crime_type = crime_match.group(1).strip()
        else:
            crime_type = "Unspecified"

        # Scrape detail page for further info
        details = scrape_alert_detail_page(full_url)

        # Determine geocode (if location text available)
        coords = simple_campus_geocode(details.get("location_text", ""))
        if coords:
            lat, lng = coords
        else:
            # If not found, default to a central coordinate on campus
            lat, lng = (32.8801, -117.2340)

        alert_record = {
            "date": alert_date,
            "alert_title": link_text,
            "alert_type": alert_type,
            "crime_type": crime_type,
            "is_update": is_update,
            "details_url": full_url,
            "location_text": details.get("location_text", ""),
            "suspect_info": details.get("suspect_info", ""),
            "description": details.get("description", ""),
            "lat": lat,
            "lng": lng
        }
        alerts.append(alert_record)

    return alerts

if __name__ == "__main__":
    alerts = scrape_ucsd_alerts()
    print(f"Found {len(alerts)} alerts.")
    # For testing, write results to a JSON file
    import json
    with open("ucsd_alerts.json", "w", encoding="utf-8") as f:
        json.dump(alerts, f, indent=2)
