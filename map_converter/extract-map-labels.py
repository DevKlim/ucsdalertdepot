# extract_map_labels.py
"""
Extract building labels from a map image and convert to geocoordinates.

This script:
1. Uses OCR to detect text on the map image
2. Identifies building names and their pixel coordinates
3. Converts pixel coordinates to geocoordinates using known reference points
4. Outputs a JSON file mapping building names to coordinates
"""

import cv2
import numpy as np
import pytesseract
import json
import os
import argparse
from math import sqrt
from scipy.spatial import Delaunay
import matplotlib.pyplot as plt

# Default paths
OUTPUT_DIR = "output"
LABELS_JSON = "building_locations.json"

# Known reference points (building name, pixel coordinates, geocoordinates)
REFERENCE_POINTS = [
    ("Geisel Library", (1340, 2400), (32.88116, -117.237651)),
    ("Price Center", (1460, 2720), (32.88, -117.237)),
    ("Center Hall", (1575, 2605), (32.87985, -117.2364)),
    ("RIMAC", (1270, 1975), (32.8882, -117.2383)),
    ("Warren College", (950, 2450), (32.8825, -117.2335)),
    ("Jacobs School", (1900, 2390), (32.8817, -117.2334))
]

def preprocess_image(image_path):
    """Preprocess the image for OCR text detection."""
    # Load image
    img = cv2.imread(image_path)
    if img is None:
        raise ValueError(f"Could not load image from {image_path}")
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Apply slight blur to reduce noise
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    
    # Apply threshold to get black text on white background
    _, thresh = cv2.threshold(blur, 150, 255, cv2.THRESH_BINARY_INV)
    
    return img, gray, thresh

def detect_text_regions(thresh_img):
    """Detect regions that potentially contain text."""
    # Find contours in the thresholded image
    contours, _ = cv2.findContours(thresh_img, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    # Filter contours by size to identify potential text regions
    min_area = 100
    max_area = 5000
    text_regions = []
    
    for contour in contours:
        area = cv2.contourArea(contour)
        if min_area <= area <= max_area:
            x, y, w, h = cv2.boundingRect(contour)
            aspect_ratio = w / h
            
            # Most text has a reasonable aspect ratio
            if 0.5 <= aspect_ratio <= 10:
                text_regions.append((x, y, w, h))
    
    return text_regions

def perform_ocr(img, text_regions):
    """Perform OCR on identified text regions."""
    building_labels = []
    
    for x, y, w, h in text_regions:
        # Extract region
        roi = img[y:y+h, x:x+w]
        
        # Convert to grayscale if not already
        if len(roi.shape) == 3:
            roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        
        # Perform OCR
        text = pytesseract.image_to_string(roi, config='--psm 7')
        text = text.strip()
        
        # Filter out short or empty text
        if len(text) > 3:
            # Calculate center of the text region
            center_x = x + w // 2
            center_y = y + h // 2
            
            building_labels.append({
                "text": text,
                "confidence": 1.0,  # Placeholder for confidence
                "center": (center_x, center_y),
                "box": (x, y, w, h)
            })
    
    return building_labels

def better_ocr_approach(img):
    """Use pytesseract's more advanced data extraction for better results."""
    # Convert to grayscale if needed
    if len(img.shape) == 3:
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    else:
        gray = img
    
    # Use pytesseract's image_to_data to get bounding boxes and confidence
    data = pytesseract.image_to_data(gray, config='--psm 11', output_type=pytesseract.Output.DICT)
    
    building_labels = []
    for i in range(len(data['text'])):
        # Filter out empty text and low confidence results
        if data['text'][i].strip() and int(data['conf'][i]) > 30:
            x = data['left'][i]
            y = data['top'][i]
            w = data['width'][i]
            h = data['height'][i]
            
            # Calculate center
            center_x = x + w // 2
            center_y = y + h // 2
            
            building_labels.append({
                "text": data['text'][i].strip(),
                "confidence": int(data['conf'][i]),
                "center": (center_x, center_y),
                "box": (x, y, w, h)
            })
    
    return building_labels

def pixel_to_geo_simple(pixel_coord, reference_points):
    """
    Convert pixel coordinates to geocoordinates using the closest reference point.
    This is a simple approach using the relative distances.
    """
    # Find closest reference point
    closest_ref = None
    min_dist = float('inf')
    
    for _, ref_pixel, ref_geo in reference_points:
        dist = sqrt((pixel_coord[0] - ref_pixel[0])**2 + (pixel_coord[1] - ref_pixel[1])**2)
        if dist < min_dist:
            min_dist = dist
            closest_ref = (ref_pixel, ref_geo)
    
    # Calculate offset from closest reference point
    dx = pixel_coord[0] - closest_ref[0][0]
    dy = pixel_coord[1] - closest_ref[0][1]
    
    # Approximate conversion factors (will vary across the map)
    # You may need to adjust these based on your map scale
    lat_per_pixel = 0.000010  # Approximate degrees latitude per pixel
    lng_per_pixel = 0.000015  # Approximate degrees longitude per pixel
    
    # Apply offset to get geocoordinates
    lat = closest_ref[1][0] - dy * lat_per_pixel  # Subtract for y since image origin is top-left
    lng = closest_ref[1][1] + dx * lng_per_pixel
    
    return (lat, lng)

def pixel_to_geo_interpolation(pixel_coord, reference_points):
    """
    Convert pixel coordinates to geocoordinates using interpolation.
    This method uses triangulation to interpolate within the area covered by reference points.
    """
    # Extract pixel and geo coordinates from reference points
    pixel_coords = np.array([point[1] for point in reference_points])
    geo_coords = np.array([point[2] for point in reference_points])
    
    # Create Delaunay triangulation of pixel coordinates
    try:
        tri = Delaunay(pixel_coords)
        
        # Find which triangle contains the point
        simplex = tri.find_simplex(pixel_coord)
        
        if simplex >= 0:
            # Get barycentric coordinates
            b = tri.transform[simplex, :2].dot(np.array(pixel_coord) - tri.transform[simplex, 2])
            b = np.append(b, 1 - b.sum())
            
            # Get vertices of the triangle
            vertices = tri.simplices[simplex]
            
            # Interpolate geo coordinates using barycentric coordinates
            lat = (geo_coords[vertices, 0] * b).sum()
            lng = (geo_coords[vertices, 1] * b).sum()
            
            return (lat, lng)
    except:
        # Fall back to simple method if triangulation fails
        pass
    
    return pixel_to_geo_simple(pixel_coord, reference_points)

def affine_transform_method(pixel_coord, reference_points):
    """
    Convert pixel coordinates to geocoordinates using an affine transformation.
    Requires at least 3 reference points.
    """
    if len(reference_points) < 3:
        return pixel_to_geo_simple(pixel_coord, reference_points)
    
    # Extract pixel and geo coordinates from reference points
    src_points = np.array([point[1] for point in reference_points[:3]], dtype=np.float32)
    dst_points = np.array([point[2] for point in reference_points[:3]], dtype=np.float32)
    
    # Calculate affine transformation matrix
    transform_matrix = cv2.getAffineTransform(src_points, dst_points)
    
    # Apply transformation
    pixel_array = np.array([[pixel_coord[0], pixel_coord[1]]], dtype=np.float32)
    transformed = cv2.transform(pixel_array.reshape(-1, 1, 2), transform_matrix)
    
    return (transformed[0][0][0], transformed[0][0][1])

def filter_building_labels(labels, min_confidence=40, building_keywords=None):
    """Filter and clean up extracted building labels."""
    if building_keywords is None:
        building_keywords = [
            "hall", "library", "center", "building", "college", "plaza", "complex",
            "school", "institute", "facility", "lab", "laboratory", "geisel", "price"
        ]
    
    filtered_labels = []
    
    for label in labels:
        # Skip low confidence items
        if label["confidence"] < min_confidence:
            continue
        
        text = label["text"].lower()
        
        # Check if text contains any building keywords
        is_building = any(keyword in text for keyword in building_keywords)
        
        # Clean up text
        clean_text = label["text"].strip()
        
        # Add to filtered list if it's likely a building
        if is_building and len(clean_text) > 3:
            label["text"] = clean_text
            filtered_labels.append(label)
    
    return filtered_labels

def save_to_json(building_labels, output_path):
    """Save building labels and coordinates to JSON file."""
    building_data = {}
    
    for label in building_labels:
        building_data[label["text"]] = {
            "pixels": list(label["center"]),
            "lat": label["geo"][0],
            "lng": label["geo"][1]
        }
    
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(building_data, f, indent=2)
    
    print(f"Saved {len(building_labels)} building locations to {output_path}")

def visualize_results(img, building_labels, reference_points):
    """Visualize the detected buildings and reference points on the image."""
    # Create a copy of the image
    vis_img = img.copy()
    
    # Draw reference points in blue
    for name, pixel, _ in reference_points:
        cv2.circle(vis_img, pixel, 10, (255, 0, 0), -1)
        cv2.putText(vis_img, name, (pixel[0]+10, pixel[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 0, 0), 2)
    
    # Draw detected buildings in green
    for label in building_labels:
        cv2.circle(vis_img, label["center"], 5, (0, 255, 0), -1)
        cv2.rectangle(vis_img, (label["box"][0], label["box"][1]), 
                     (label["box"][0]+label["box"][2], label["box"][1]+label["box"][3]), (0, 255, 0), 2)
        cv2.putText(vis_img, label["text"], (label["center"][0], label["center"][1]-10), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
    
    # Save visualization
    vis_path = os.path.join(OUTPUT_DIR, "detection_visualization.jpg")
    cv2.imwrite(vis_path, vis_img)
    print(f"Saved visualization to {vis_path}")
    
    # Show image if not running in a headless environment
    try:
        cv2.imshow("Building Label Detection", vis_img)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    except:
        pass

def main():
    """Main function to extract building labels from a map image."""
    # Parse arguments
    parser = argparse.ArgumentParser(description='Extract building labels from UCSD map image')
    parser.add_argument('image_path', help='Path to the UCSD map image')
    parser.add_argument('--method', choices=['simple', 'interpolation', 'affine'], default='affine',
                       help='Method for pixel to geocoordinate conversion')
    parser.add_argument('--visualize', action='store_true', help='Visualize the detection results')
    args = parser.parse_args()
    
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    try:
        # Load and preprocess image
        print("Loading and preprocessing image...")
        img, gray, thresh = preprocess_image(args.image_path)
        
        # Detect text with OCR
        print("Performing OCR to detect building labels...")
        building_labels = better_ocr_approach(img)
        
        # Filter and clean up labels
        print("Filtering building labels...")
        filtered_labels = filter_building_labels(building_labels)
        
        # Convert pixel coordinates to geocoordinates
        print(f"Converting to geocoordinates using {args.method} method...")
        for label in filtered_labels:
            if args.method == 'simple':
                label["geo"] = pixel_to_geo_simple(label["center"], REFERENCE_POINTS)
            elif args.method == 'interpolation':
                label["geo"] = pixel_to_geo_interpolation(label["center"], REFERENCE_POINTS)
            else:  # affine
                label["geo"] = affine_transform_method(label["center"], REFERENCE_POINTS)
        
        # Save results to JSON
        output_path = os.path.join(OUTPUT_DIR, LABELS_JSON)
        save_to_json(filtered_labels, output_path)
        
        # Visualize if requested
        if args.visualize:
            print("Generating visualization...")
            visualize_results(img, filtered_labels, REFERENCE_POINTS)
        
        print("Done!")
        
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    main()
