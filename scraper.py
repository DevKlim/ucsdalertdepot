# scraper.py
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from geocode import simple_campus_geocode
import spacy

# Load spaCy English model (do this once)
nlp = spacy.load("en_core_web_sm")

BASE_URL = "https://police.ucsd.edu"
ALERTS_URL = "https://police.ucsd.edu/alerts/warnings.html"

def extract_precise_location(text):
    """
    Uses spaCy to extract a candidate location entity from text.
    Returns the first entity found labeled as GPE, LOC, or FAC.
    """
    doc = nlp(text)
    for ent in doc.ents:
        if ent.label_ in ["GPE", "LOC", "FAC"]:
            return ent.text
    return None

def scrape_alert_detail_page(url):
    """
    Given a detail page URL, returns a dict with:
      - description: first 2000 characters of full text
      - location_text: a location snippet found via regex
      - precise_location: the location extracted via spaCy NLP
      - suspect_info: a naive extraction of suspect details (if any)
    """
    try:
        response = requests.get(url)
        response.raise_for_status()
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return {}
    soup = BeautifulSoup(response.text, "html.parser")
    raw_text = soup.get_text(separator="\n")
    
    # Naively extract a location using regex ("at ..." or "near ...")
    location_text = None
    loc_match = re.search(r"(?:at|near)\s+([A-Za-z0-9\s,&\-]+?)(?:\.|\n)", raw_text)
    if loc_match:
        location_text = loc_match.group(1).strip()

    # Use spaCy to extract a more precise location from the full text
    precise_location = extract_precise_location(raw_text)
    
    # Naively extract suspect information
    suspect_info = None
    suspect_match = re.search(r"(suspect(?:s)?\s+[^\.]+\.)", raw_text, re.IGNORECASE)
    if suspect_match:
        suspect_info = suspect_match.group(1).strip()

    return {
        "description": raw_text[:2000],
        "location_text": location_text or "Unknown",
        "precise_location": precise_location or "Unknown",
        "suspect_info": suspect_info or "Not specified"
    }

def extract_date_from_url(url):
    """
    If the URL matches the pattern /Notices/YYYY/YYYY-M-D-*.html,
    extract and return a date string in MM/DD/YYYY format.
    """
    match = re.search(r"/Notices/(\d{4})/(\d{1,2})-(\d{1,2})-\d+\.html", url)
    if match:
        year, month, day = match.groups()
        return f"{int(month):02d}/{int(day):02d}/{year}"
    return "Unknown"

def scrape_ucsd_alerts():
    """
    Scrapes the main alerts page, then for each alert link that points to a Notice,
    scrapes its detail page.
    Returns a list of dictionaries representing each alert.
    """
    try:
        main_resp = requests.get(ALERTS_URL)
        main_resp.raise_for_status()
    except Exception as e:
        print(f"Error fetching main alerts page: {e}")
        return []

    soup_main = BeautifulSoup(main_resp.text, "html.parser")
    alerts = []
    # Process only links that point to adminrecords.ucsd.edu/Notices
    all_a_tags = soup_main.select("ul li a")
    for a_tag in all_a_tags:
        link_text = a_tag.get_text(strip=True)
        href = a_tag.get("href")
        if not href:
            continue
        full_url = urljoin(ALERTS_URL, href)
        # Only process if URL is a Notice (report) page
        if not full_url.startswith("https://adminrecords.ucsd.edu/Notices/"):
            continue

        # Extract date from link text if possible; otherwise, try URL
        date_match = re.search(r"(\d{1,2}/\d{1,2}/\d{4})", link_text)
        alert_date = date_match.group(1) if date_match else extract_date_from_url(full_url)

        # Determine alert type
        if "Timely Warning" in link_text:
            alert_type = "Timely Warning"
        elif "Triton Alert" in link_text:
            alert_type = "Triton Alert"
        elif "Community Alert" in link_text:
            alert_type = "Community Alert Bulletin"
        else:
            alert_type = "Other"

        is_update = "UPDATE" in link_text.upper()

        # Extract crime type from link text (after a dash)
        crime_type = None
        crime_match = re.search(r"(?:Warning\s*[–-]\s*)(.+)$", link_text, re.IGNORECASE)
        if crime_match:
            crime_type = crime_match.group(1).strip()
        else:
            crime_type = "Unspecified"

        # Scrape detail page for additional info
        details = scrape_alert_detail_page(full_url)
        # Determine geocode using the detailed location_text (or precise_location)
        coords = simple_campus_geocode(details.get("precise_location", "")) or \
                 simple_campus_geocode(details.get("location_text", ""))
        if coords:
            lat, lng = coords
        else:
            # Default center for campus if no match found
            lat, lng = (32.8801, -117.2340)

        alert_record = {
            "date": alert_date,
            "alert_title": link_text,
            "alert_type": alert_type,
            "crime_type": crime_type,
            "is_update": is_update,
            "details_url": full_url,
            "location_text": details.get("location_text", ""),
            "precise_location": details.get("precise_location", ""),
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
