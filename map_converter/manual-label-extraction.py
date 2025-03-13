# manual_label_extraction.py
"""
Tool for manually adding building labels to a map image.

This script allows you to:
1. Click on a building on the map to mark its position
2. Enter the building name and get geocoordinates
3. Save the building locations to a JSON file
"""

import cv2
import numpy as np
import json
import os
import sys
from datetime import datetime
import argparse

# Default paths
OUTPUT_DIR = "output"
OUTPUT_JSON = "building_locations.json"

# Constants
DEFAULT_UCSD_CENTER = (32.8801, -117.2340)  # Center of UCSD campus

# Known reference points for coordinate conversion
REFERENCE_POINTS = [
    ("Geisel Library", (1340, 2400), (32.88116, -117.237651)),
    ("Price Center", (1460, 2720), (32.88, -117.237)),
    ("Center Hall", (1575, 2605), (32.87985, -117.2364)),
    ("RIMAC", (1270, 1975), (32.8882, -117.2383)),
    ("Warren College", (950, 2450), (32.8825, -117.2335)),
    ("Jacobs School", (1900, 2390), (32.8817, -117.2334))
]

# Global variables
image = None
window_name = "UCSD Map - Manual Building Labeler"
labels = []  # List to store labels
transform_matrix = None  # For affine transformation

def init_affine_transform():
    """Initialize the affine transformation matrix for pixel to geo conversion."""
    global transform_matrix
    
    # Need at least 3 reference points
    if len(REFERENCE_POINTS) < 3:
        print("Warning: Need at least 3 reference points for affine transformation.")
        return False
    
    # Extract source and destination points (pixel to geo)
    src_points = np.array([point[1] for point in REFERENCE_POINTS[:3]], dtype=np.float32)
    dst_points = np.array([point[2] for point in REFERENCE_POINTS[:3]], dtype=np.float32)
    
    # Calculate transformation matrix
    transform_matrix = cv2.getAffineTransform(src_points, dst_points)
    return True

def pixel_to_geo(x, y):
    """Convert pixel coordinates to geocoordinates using affine transformation."""
    global transform_matrix
    
    if transform_matrix is None:
        if not init_affine_transform():
            # Fallback if affine transform fails
            return DEFAULT_UCSD_CENTER
    
    # Apply transformation
    pixel_array = np.array([[x, y]], dtype=np.float32)
    transformed = cv2.transform(pixel_array.reshape(-1, 1, 2), transform_matrix)
    
    return (transformed[0][0][0], transformed[0][0][1])

def click_event(event, x, y, flags, params):
    """Handle mouse clicks for placing building labels."""
    global image, labels
    
    if event == cv2.EVENT_LBUTTONDOWN:
        # Add a new label
        print(f"\nClick at pixel coordinates: ({x}, {y})")
        
        # Get building name from user
        building_name = input("Enter building name: ")
        
        if building_name:
            # Convert to geocoordinates
            lat, lng = pixel_to_geo(x, y)
            print(f"Geocoordinates: ({lat}, {lng})")
            
            # Add to labels list
            labels.append({
                "name": building_name,
                "pixel": (x, y),
                "geo": (lat, lng)
            })
            
            # Add marker to image
            cv2.circle(image, (x, y), 5, (0, 0, 255), -1)
            cv2.putText(image, building_name, (x + 10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
            cv2.imshow(window_name, image)
            
            print(f"Added {building_name} at ({lat}, {lng})")

def save_labels():
    """Save building labels to JSON file."""
    # Ensure output directory exists
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    # Create dictionary to store building data
    building_data = {}
    
    for label in labels:
        building_data[label["name"]] = {
            "pixels": list(label["pixel"]),
            "lat": label["geo"][0],
            "lng": label["geo"][1]
        }
    
    # Save to JSON file
    output_path = os.path.join(OUTPUT_DIR, OUTPUT_JSON)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(building_data, f, indent=2)
    
    print(f"\nSaved {len(labels)} building locations to {output_path}")

def draw_reference_points():
    """Draw the reference points on the image."""
    global image
    
    for name, pixel, _ in REFERENCE_POINTS:
        cv2.circle(image, pixel, 8, (255, 0, 0), -1)
        cv2.putText(image, name, (pixel[0]+10, pixel[1]), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 0, 0), 2)

def main():
    """Main function for manual building label extraction."""
    global image
    
    # Parse arguments
    parser = argparse.ArgumentParser(description='Manually label buildings on UCSD map image')
    parser.add_argument('image_path', help='Path to the UCSD map image')
    parser.add_argument('--show-reference', action='store_true', help='Show reference points on the image')
    parser.add_argument('--output', default=OUTPUT_JSON, help='Output JSON filename')
    args = parser.parse_args()
    
    # Set output filename
    global OUTPUT_JSON
    OUTPUT_JSON = args.output
    
    # Load image
    image = cv2.imread(args.image_path)
    if image is None:
        print(f"Error: Could not load image from {args.image_path}")
        sys.exit(1)
    
    # Initialize affine transformation
    init_affine_transform()
    
    # Create window and set up mouse callback
    cv2.namedWindow(window_name)
    cv2.setMouseCallback(window_name, click_event)
    
    # Draw reference points if requested
    if args.show_reference:
        draw_reference_points()
    
    # Instructions
    print("\nInstructions:")
    print("  - Left-click on a building to mark its position")
    print("  - Enter the building name in the console")
    print("  - Press 'q' to quit and save")
    print("  - Press 'r' to reset (delete all labels)")
    print("  - Press 'd' to delete the last label")
    
    # Main loop
    while True:
        cv2.imshow(window_name, image)
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('q'):
            # Quit and save
            break
        
        elif key == ord('r'):
            # Reset all labels
            print("\nResetting all labels")
            labels.clear()
            
            # Reload image
            image = cv2.imread(args.image_path)
            
            # Redraw reference points if needed
            if args.show_reference:
                draw_reference_points()
        
        elif key == ord('d'):
            # Delete last label
            if labels:
                removed = labels.pop()
                print(f"\nRemoved {removed['name']}")
                
                # Reload image and redraw remaining labels
                image = cv2.imread(args.image_path)
                
                # Redraw reference points if needed
                if args.show_reference:
                    draw_reference_points()
                
                # Redraw remaining labels
                for label in labels:
                    x, y = label["pixel"]
                    cv2.circle(image, (x, y), 5, (0, 0, 255), -1)
                    cv2.putText(image, label["name"], (x + 10, y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 2)
    
    # Save labels to JSON
    if labels:
        save_labels()
    
    # Create a visualization image
    vis_img = image.copy()
    cv2.imwrite(os.path.join(OUTPUT_DIR, "labeled_map.jpg"), vis_img)
    
    # Close windows
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
