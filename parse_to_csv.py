import csv
import re

input_filename = "ucsd_info.txt"   # your text file with batch classification logs
output_filename = "alerts.csv"  # the CSV file to create

# We'll extract these columns:
# Crime Type, Alert Type, Location Address, Latitude, Longitude, Time, Severity, Is Update

records = []
current_record = {}

# Regular expression patterns for each field.
patterns = {
    "Crime Type": re.compile(r"^Crime Type:\s*(.*)"),
    "Alert Type": re.compile(r"^Alert Type:\s*(.*)"),
    "Location Address": re.compile(r"^Location Address:\s*(.*)"),
    "LatitudeLongitude": re.compile(r"^Latitude:\s*([0-9\.\-]+),\s*Longitude:\s*([0-9\.\-]+)"),
    "Time": re.compile(r"^Time:\s*(.*)"),
    "Severity": re.compile(r"^Severity:\s*(.*)"),
    "Is Update": re.compile(r"^Is Update:\s*(.*)")
}

with open(input_filename, "r", encoding="utf-8") as f:
    for line in f:
        line = line.strip()
        # Skip lines that are empty or that denote batch separators.
        if not line or "Batch Classification" in line:
            continue

        # If line is a delimiter (e.g. "------") and we have a record, save it.
        if line.startswith("------"):
            if current_record:
                records.append(current_record)
                current_record = {}
            continue

        # Try matching each field.
        for key, pattern in patterns.items():
            match = pattern.match(line)
            if match:
                if key == "LatitudeLongitude":
                    current_record["Latitude"] = match.group(1)
                    current_record["Longitude"] = match.group(2)
                else:
                    current_record[key] = match.group(1)
                break  # move to the next line

# If there's a record in progress, add it.
if current_record:
    records.append(current_record)

# Define CSV fieldnames.
fieldnames = ["Crime Type", "Alert Type", "Location Address", "Latitude", "Longitude", "Time", "Severity", "Is Update"]

with open(output_filename, "w", newline="", encoding="utf-8") as csvfile:
    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
    writer.writeheader()
    for record in records:
        writer.writerow(record)

print(f"Parsed {len(records)} records into '{output_filename}'.")
