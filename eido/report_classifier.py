"""
report_classifier.py

This module processes written incident reports and classifies them for emergency notification.
It extracts key information using a large language model and formats it for notification decisions.
"""

import json
import datetime
import uuid
import re
import os
from typing import Dict, Any, List, Optional
from enum import Enum

# Import Mistral API client
from mistralai import Mistral

# Import local modules
from eido.eido_schema import validate_eido
from geocoding.geocode import geocode_location

class ReportClassifier:
    """
    Classifies written incident reports into structured alert information.
    Demo #2 - taking written reports and classifying them for notifications.
    """
    
    def __init__(self, api_key=None):
        """
        Initialize the report classifier.
        
        Args:
            api_key: API key for Mistral LLM (optional, will use env var if not provided)
        """
        self.api_key = api_key or os.environ.get("MISTRAL_API_KEY")
        if not self.api_key:
            raise ValueError("Mistral API key is required. Set MISTRAL_API_KEY environment variable or pass as argument.")
            
        self.client = Mistral(api_key=self.api_key)
        self.model = "mistral-large-latest"
    
    def classify_report(self, report_text: str) -> Dict[str, Any]:
        """
        Classifies a written incident report into structured alert information.
        
        Args:
            report_text: The text of the incident report
            
        Returns:
            Structured alert information
        """
        # Extract key information using the LLM
        classification = self._extract_classification(report_text)
        
        # Create alert object from classification
        alert = {
            "alert_id": str(uuid.uuid4()),
            "timestamp": datetime.datetime.now().isoformat(),
            "classification": classification,
            "alert_level": self._determine_alert_level(classification),
            "alert_type": self._determine_alert_type(classification),
            "notification_scope": self._determine_notification_scope(classification),
            "original_report": report_text
        }
        
        return alert
    
    def _extract_classification(self, report_text: str) -> Dict[str, Any]:
        """
        Extract structured classification from the report text using LLM.
        
        Args:
            report_text: The report text
            
        Returns:
            Dictionary containing extracted classification
        """
        prompt = f"""
        Analyze this campus incident report and extract key information for emergency notification purposes:
        
        REPORT TEXT:
        {report_text}
        
        Extract and return ONLY a JSON object with these fields:
        - incident_type: Primary category (e.g., "fire", "crime", "medical", "hazard", "infrastructure")
        - incident_subtype: More specific classification
        - severity: Assessed severity level (1-5, with 5 being most severe)
        - location: The specific location mentioned
        - location_details: Building, floor, room number, etc.
        - time_occurred: When the incident occurred
        - time_reported: When the incident was reported
        - ongoing: Boolean indicating if the incident is ongoing
        - affected_area_size: Estimated size of affected area in meters (radius from incident)
        - immediate_danger: Boolean indicating if there's immediate danger to people
        - evacuate: Boolean indicating if evacuation is needed
        - shelter_in_place: Boolean indicating if people should shelter in place
        - key_details: Array of 3-5 most important details from the report
        - recommended_response: Brief recommendation for appropriate response
        
        Output ONLY the JSON with no additional text.
        """
        
        try:
            response = self.client.chat.complete(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an emergency management expert who analyzes incident reports."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            result_text = response.choices[0].message.content
            
            # Clean up the result
            result_text = self._clean_json_text(result_text)
            
            return json.loads(result_text)
                
        except Exception as e:
            print(f"Error classifying report: {e}")
            # Fallback classification if API fails
            return self._fallback_classification(report_text)
    
    def _clean_json_text(self, text: str) -> str:
        """Clean up JSON text that might be wrapped in markdown code blocks."""
        # Remove markdown code blocks if present
        if "```json" in text or "```" in text:
            lines = text.split("\n")
            # Remove the first line if it's a code block start
            if lines and "```" in lines[0]:
                lines = lines[1:]
            # Remove the last line if it's a code block end
            if lines and "```" in lines[-1]:
                lines = lines[:-1]
            text = "\n".join(lines)
        
        # Remove any surrounding whitespace
        text = text.strip()
        
        return text
    
    def _fallback_classification(self, report_text: str) -> Dict[str, Any]:
        """Simple keyword-based classification as fallback if API fails."""
        # Extract incident type based on keywords
        incident_type = "other"
        if re.search(r'fire|burn|smoke|flames', report_text, re.I):
            incident_type = "fire"
        elif re.search(r'assault|robbery|theft|break|break-in|weapon', report_text, re.I):
            incident_type = "crime"
        elif re.search(r'injured|medical|ambulance|heart|breathing|blood', report_text, re.I):
            incident_type = "medical"
        elif re.search(r'leak|spill|chemical|gas|hazard|toxic', report_text, re.I):
            incident_type = "hazard"
        elif re.search(r'power|outage|water|flooding|building|damage|elevator', report_text, re.I):
            incident_type = "infrastructure"
            
        # Extract location with a simple regex
        location_match = re.search(r'at\s+([A-Za-z0-9\s,&\-]+?)(?:\.|\n)', report_text)
        location = location_match.group(1).strip() if location_match else "Unknown location"
        
        # Determine if it's ongoing based on tense
        ongoing = not bool(re.search(r'resolved|contained|fixed|ended|secured', report_text, re.I))
        
        # Simple severity assessment
        severity = 3  # Default to medium
        if re.search(r'severe|serious|critical|emergency|immediate|life.?threatening', report_text, re.I):
            severity = 5
        elif re.search(r'moderate|significant', report_text, re.I):
            severity = 3
        elif re.search(r'minor|small|contained|limited', report_text, re.I):
            severity = 1
            
        return {
            "incident_type": incident_type,
            "incident_subtype": "",
            "severity": severity,
            "location": location,
            "location_details": "",
            "time_occurred": "",
            "time_reported": "",
            "ongoing": ongoing,
            "affected_area_size": 100,  # Default radius
            "immediate_danger": severity >= 4,
            "evacuate": incident_type == "fire" or severity >= 4,
            "shelter_in_place": incident_type == "crime" and severity >= 3,
            "key_details": ["Incident extracted through fallback system"],
            "recommended_response": "Assess situation and respond according to incident type"
        }
    
    def _determine_alert_level(self, classification: Dict[str, Any]) -> str:
        """Determine the appropriate alert level based on the classification."""
        severity = classification.get("severity", 3)
        immediate_danger = classification.get("immediate_danger", False)
        
        if severity >= 5 or immediate_danger:
            return "EMERGENCY"
        elif severity == 4:
            return "WARNING"
        elif severity == 3:
            return "WATCH"
        elif severity == 2:
            return "ADVISORY"
        else:
            return "INFORMATION"
    
    def _determine_alert_type(self, classification: Dict[str, Any]) -> str:
        """Determine the alert type based on the classification."""
        incident_type = classification.get("incident_type", "").upper()
        
        # Map incident_type to alert type
        type_mapping = {
            "FIRE": "FIRE",
            "MEDICAL": "MEDICAL",
            "CRIME": "CRIME",
            "HAZARD": "HAZMAT",
            "INFRASTRUCTURE": "INFRASTRUCTURE",
            "WEATHER": "WEATHER"
        }
        
        # Return mapped type or default to OTHER
        return type_mapping.get(incident_type, "OTHER")
    
    def _determine_notification_scope(self, classification: Dict[str, Any]) -> Dict[str, Any]:
        """Determine the notification scope based on the classification."""
        severity = classification.get("severity", 3)
        affected_area_size = classification.get("affected_area_size", 100)
        immediate_danger = classification.get("immediate_danger", False)
        
        # Default scope
        scope = {
            "geographic": "immediate_vicinity",
            "radius_meters": affected_area_size,
            "population": ["emergency_responders"],
            "notify_authorities": True
        }
        
        # Expand scope based on severity
        if severity >= 5 or immediate_danger:
            # Critical incidents require wide notification
            scope["geographic"] = "campus_wide"
            scope["radius_meters"] = max(affected_area_size, 1000)
            scope["population"].extend(["all_students", "all_staff", "all_faculty"])
        elif severity == 4:
            # High severity
            scope["geographic"] = "campus_section"
            scope["radius_meters"] = max(affected_area_size, 500)
            scope["population"].extend(["area_occupants", "security"])
        elif severity == 3:
            # Medium severity
            scope["geographic"] = "campus_section"
            scope["radius_meters"] = max(affected_area_size, 300)
            scope["population"].extend(["area_occupants"])
            
        # Add specific groups based on incident type
        incident_type = classification.get("incident_type", "").lower()
        if incident_type == "fire":
            scope["population"].extend(["facilities", "building_managers"])
        elif incident_type == "medical":
            scope["population"].extend(["health_services"])
        elif incident_type in ["crime", "active_threat"]:
            scope["population"].extend(["security", "police"])
            
        return scope
    
    def convert_to_eido(self, alert: Dict[str, Any]) -> Dict[str, Any]:
        """Convert alert to EIDO format for notification processing."""
        classification = alert["classification"]
        incident_type = classification.get("incident_type", "unknown")
        
        # Create a basic EIDO structure
        eido = {
            "eido": {
                "eidoVersion": "1.0",
                "eidoType": "incident",
                "eidoID": alert["alert_id"],
                "timestamp": alert["timestamp"],
                "incident": {
                    "incidentID": alert["alert_id"],
                    "incidentType": incident_type,
                    "incidentSubType": classification.get("incident_subtype", ""),
                    "priority": self._map_severity_to_priority(classification.get("severity", 3)),
                    "status": "active" if classification.get("ongoing", True) else "contained",
                    "createdAt": alert["timestamp"],
                    "reportingParty": {
                        "role": "reporter",
                        "name": ""
                    },
                    "location": {
                        "address": {
                            "fullAddress": classification.get("location", "Unknown location"),
                            "additionalInfo": classification.get("location_details", "")
                        },
                        "coordinates": self._get_coordinates(classification.get("location", ""))
                    },
                    "details": {
                        "description": self._create_description(classification),
                        "timeline": [
                            {
                                "timestamp": alert["timestamp"],
                                "action": "Incident reported",
                                "notes": "Report processed through classification system"
                            }
                        ],
                        "victims": {
                            "count": 0,
                            "details": ""
                        },
                        "suspects": {
                            "description": "",
                            "weaponsInvolved": False
                        },
                        "keyFacts": classification.get("key_details", []),
                        "rawReport": alert["original_report"]
                    }
                },
                "notification": {
                    "recommendedActions": [classification.get("recommended_response", "")],
                    "recommendedNotificationScope": alert["notification_scope"],
                    "updateFrequency": "hourly"
                }
            }
        }
        
        return eido
    
    def _map_severity_to_priority(self, severity: int) -> int:
        """Map severity (1-5) to priority (1-5, where 1 is highest)."""
        # Invert the scale (5=critical becomes priority 1)
        return 6 - severity
    
    def _get_coordinates(self, location: str) -> Dict[str, Optional[float]]:
        """Get coordinates for a location using the geocoding service."""
        try:
            # Call the geocoding service
            geocode_result = geocode_location(location)
            
            if geocode_result and 'lat' in geocode_result and 'lng' in geocode_result:
                return {
                    "latitude": geocode_result['lat'],
                    "longitude": geocode_result['lng']
                }
        except Exception as e:
            print(f"Error geocoding location '{location}': {e}")
        
        # Return null coordinates if geocoding fails
        return {
            "latitude": None,
            "longitude": None
        }
    
    def _create_description(self, classification: Dict[str, Any]) -> str:
        """Create a description from classification data."""
        incident_type = classification.get("incident_type", "Incident")
        location = classification.get("location", "unknown location")
        ongoing = "ongoing" if classification.get("ongoing", True) else "resolved"
        
        return f"{incident_type.capitalize()} reported at {location}. " \
               f"Severity assessed as {classification.get('severity', 3)}/5. " \
               f"Situation appears to be {ongoing}."


# Example usage
if __name__ == "__main__":
    # Sample incident report
    sample_report = """
    Incident Report
    Date: March 23, 2025
    Time: 3:15 PM
    
    Location: Geisel Library, 2nd floor, west wing
    
    I am reporting a suspicious individual who has been wandering around the library for the past hour. 
    This person appears to be in their 30s, wearing a dark hoodie and a backpack. They have been looking 
    into study rooms and examining unattended belongings. When approached by library staff, they claimed 
    to be looking for a friend but couldn't provide a name. The person has been seen attempting to open 
    several backpacks when students stepped away momentarily.
    
    The individual is currently still in the building, moving between the 2nd and 3rd floors. They appear 
    to be targeting areas where students leave belongings unattended while using the restroom or getting 
    food. No thefts have been confirmed yet, but the behavior is concerning.
    
    Campus security has been verbally notified but I wanted to submit a formal report as well.
    
    Reported by: Alex Chen, Library Staff
    Contact: 555-123-4567
    """
    
    classifier = ReportClassifier()
    alert = classifier.classify_report(sample_report)
    
    print(json.dumps(alert, indent=2))
    
    # Convert to EIDO format
    eido = classifier.convert_to_eido(alert)
    print("\nEIDO FORMAT:")
    print(json.dumps(eido, indent=2))