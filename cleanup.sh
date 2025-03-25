#!/bin/bash
# Script to remove unnecessary files from the ucsdalertdepot repository for the agentic AI branch

echo "Starting cleanup of ucsdalertdepot for agentic AI branch..."

# Files to remove
files_to_remove=(
    # Original geocoding and alerts files
    "alerts.csv"
    "alerts.ipynb"
    "alerts_geocoded.csv"
    "bulk_geocoding.py"
    "geocode_comparison_tool.py"
    "geocode_replacer.py"
    "geocode_routes.py"
    "geocoding.ipynb"
    "import_alerts_to_openrouter.py"
    "parse_to_csv.py"
    "scraper.py"
    "ucsd_alerts.json"
    "ucsd_alerts_geocoded.json"
    "ucsd_info.txt"
    "print_struc.py"
    
    # Directories to remove
    ".ipynb_checkpoints"
    "exploration"
    "geocoded_loc"
    "geocode_backups"
    "geocode_geojson"
    "geocode_services"
    "map_converter"
    "__pycache__"
)

# Count how many files will be removed
count=0
for file in "${files_to_remove[@]}"; do
    if [ -e "$file" ]; then
        count=$((count+1))
    fi
done

echo "Found $count files/directories to remove."
echo "Files to be removed:"
for file in "${files_to_remove[@]}"; do
    if [ -e "$file" ]; then
        echo "  - $file"
    fi
done

# Ask for confirmation
read -p "Do you want to proceed with removal? (y/n): " confirm
if [[ $confirm != [yY] ]]; then
    echo "Cleanup cancelled."
    exit 0
fi

# Remove files
for file in "${files_to_remove[@]}"; do
    if [ -e "$file" ]; then
        if [ -d "$file" ]; then
            echo "Removing directory: $file"
            rm -rf "$file"
        else
            echo "Removing file: $file"
            rm "$file"
        fi
    fi
done

# Remove data_backups, but keep example data
echo "Cleaning up data_backups directory..."
if [ -d "data_backups" ]; then
    rm -rf data_backups
fi

echo "Cleanup complete!"
echo ""
echo "Your repository is now focused on the agentic AI project."
echo "Make sure to commit these changes to your new branch."