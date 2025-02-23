# geocode.py
CAMPUS_LOCATIONS = {
    "Geisel Library": (32.8810, -117.2370),
    "Price Center": (32.8794, -117.2359),
    "Warren Mall": (32.8822, -117.2345),
    "BCB Café": (32.8820, -117.2350)
    # Add more campus landmarks as needed
}

def simple_campus_geocode(location_text: str):
    """
    Checks if any known campus landmark name is in the location_text.
    Returns a (lat, lng) tuple if found; otherwise, returns None.
    """
    if not location_text:
        return None
    for name, coords in CAMPUS_LOCATIONS.items():
        if name.lower() in location_text.lower():
            return coords
    return None
