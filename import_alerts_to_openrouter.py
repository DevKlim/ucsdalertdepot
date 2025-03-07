import json
import time
from mistralai import Mistral

# Use your Mistral API key. It is recommended to set this in your environment.
# For example: export MISTRAL_API_KEY="YOUR_MISTRAL_API_KEY"
import os
API_KEY = os.environ.get("MISTRAL_API_KEY", "0y7ZgwMeDjtawMwmAcpo7i9polWc3TKM")
model = "mistral-large-latest"  # Choose the relevant model

client = Mistral(api_key=API_KEY)

# Load alerts from JSON file
with open("ucsd_alerts.json", "r", encoding="utf-8") as f:
    alerts = json.load(f)

# Configuration: batch size, max attempts, and pause duration (seconds)
BATCH_SIZE = 5
MAX_ATTEMPTS = 3
PAUSE_SECONDS = 5

def build_batch_prompt(batch):
    """
    Constructs a prompt listing a batch of alerts.
    Instruct the model to output a JSON array of objects, each with the keys:
      - crime_type
      - alert_type
      - location_address
      - lat
      - lon
      - time
      - severity
      - is_update
    The prompt also includes each alert's details as context.
    """
    prompt_lines = [
        "Classify the following UCSD crime alerts and provide for each alert a JSON object with these keys:",
        "  - crime_type: the specific type of crime (e.g., 'Burglary', 'Robbery', etc.)",
        "  - alert_type: the type of warning/alert (e.g., 'Timely Warning', 'Triton Alert', etc.)",
        "  - location_address: the best location address you can extract (e.g., 'BCB Café Coffee Cart, Warren Mall, UC San Diego')",
        "  - lat: the latitude of the location",
        "  - lon: the longitude of the location",
        "  - time: the time or date of the alert",
        "  - severity: a one-word severity rating (e.g., 'High', 'Medium', 'Low') based solely on the alert's description",
        "  - is_update: a boolean indicating if this alert is an update",
        "Output only a JSON array containing these objects and no additional text.",
        "",
        "The alerts are listed below:"
    ]
    for idx, alert in enumerate(batch, start=1):
        details = (
            f"Alert {idx}:\n"
            f"Title: {alert.get('alert_title', 'N/A')}\n"
            f"Date: {alert.get('date', 'N/A')}\n"
            f"Alert Type: {alert.get('alert_type', 'N/A')}\n"
            f"Crime Type: {alert.get('crime_type', 'N/A')}\n"
            f"Location: {alert.get('location_text', 'N/A')} (Precise: {alert.get('precise_location', 'N/A')})\n"
            f"Suspect Info: {alert.get('suspect_info', 'N/A')}\n"
            f"Description: {alert.get('description', 'N/A')}"
        )
        prompt_lines.append(details)
    return "\n\n".join(prompt_lines)

def clean_response_text(response_text):
    """
    Removes markdown code fences (triple backticks) if present.
    """
    response_text = response_text.strip()
    if response_text.startswith("```"):
        lines = response_text.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip().startswith("```"):
            lines = lines[:-1]
        response_text = "\n".join(lines).strip()
    return response_text

# Process alerts in batches
for i in range(0, len(alerts), BATCH_SIZE):
    batch = alerts[i : i + BATCH_SIZE]
    prompt = build_batch_prompt(batch)
    
    attempts = MAX_ATTEMPTS
    while attempts > 0:
        try:
            chat_response = client.chat.complete(
                model=model,
                messages=[
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ]
            )
            if not chat_response or not hasattr(chat_response, "choices") or not chat_response.choices:
                raise ValueError("No completion choices returned.")
            result_text = chat_response.choices[0].message.content.strip()
            # Clean markdown formatting if present
            result_text = clean_response_text(result_text)
            # Attempt to parse the result as JSON
            try:
                classifications = json.loads(result_text)
            except Exception as parse_err:
                raise ValueError(f"Failed to parse JSON: {parse_err}\nResponse: {result_text}")
            
            # Expected format: a JSON array of objects with the required keys.
            print("----- Batch Classification -----")
            for obj in classifications:
                print(f"Crime Type: {obj.get('crime_type', 'N/A')}")
                print(f"Alert Type: {obj.get('alert_type', 'N/A')}")
                print(f"Location Address: {obj.get('location_address', 'N/A')}")
                print(f"Latitude: {obj.get('lat', 'N/A')}, Longitude: {obj.get('lon', 'N/A')}")
                print(f"Time: {obj.get('time', 'N/A')}")
                print(f"Severity: {obj.get('severity', 'N/A')}")
                print(f"Is Update: {obj.get('is_update', 'N/A')}")
                print("------")
            print("--------------------------------\n")
            break  # Success: exit retry loop.
        except Exception as e:
            attempts -= 1
            if attempts > 0:
                print(f"Error processing batch starting at index {i}: {e}. Retrying in {PAUSE_SECONDS} seconds...")
                time.sleep(PAUSE_SECONDS)
            else:
                print(f"Error processing batch starting at index {i}: {e}. Giving up on this batch.")
