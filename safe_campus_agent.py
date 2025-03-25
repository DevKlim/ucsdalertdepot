# safe_campus_agent.py
import json
import time
import datetime
import re
import uuid
import math
import random
from typing import Dict, Any, List

class SafeCampusAgent:
    """
    Safe Campus Agent for processing emergency calls and incident reports.
    This agent analyzes text inputs and creates standardized EIDO objects for 
    intelligent notification decisions.
    """
    
    def __init__(self):
        """Initialize the Safe Campus Agent."""
        self.known_locations = self._load_known_locations()
    
    def _load_known_locations(self):
        """Load known campus locations for geocoding."""
        return {
            "Geisel Library": {"lat": 32.8810, "lng": -117.2370, "name": "Geisel Library"},
            "Price Center": {"lat": 32.8794, "lng": -117.2359, "name": "Price Center"},
            "Warren College": {"lat": 32.8815, "lng": -117.2350, "name": "Warren College"},
            "Warren Apartments": {"lat": 32.8825, "lng": -117.2355, "name": "Warren Apartments"},
            "Sixth College": {"lat": 32.8806, "lng": -117.2325, "name": "Sixth College"},
            "Muir College": {"lat": 32.8789, "lng": -117.2410, "name": "Muir College"},
            "Revelle College": {"lat": 32.8745, "lng": -117.2410, "name": "Revelle College"},
            "RIMAC Arena": {"lat": 32.8869, "lng": -117.2406, "name": "RIMAC Arena"},
            "Library Walk": {"lat": 32.8794, "lng": -117.2370, "name": "Library Walk"},
            "La Jolla": {"lat": 32.8328, "lng": -117.2712, "name": "La Jolla"},
            "UC San Diego": {"lat": 32.8801, "lng": -117.2340, "name": "UC San Diego Campus"}
        }
    
    def process_emergency_call(self, transcript: str) -> Dict[str, Any]:
        """
        Process an emergency call transcript into a structured EIDO object.
        
        Args:
            transcript: The call transcript text
            
        Returns:
            Dictionary with processing results
        """
        start_time = time.time()
        
        # Extract location using simulated LLM
        location_info = self._extract_location(transcript)
        
        # Classify incident using simulated LLM
        classification = self._classify_incident(transcript)
        
        # Generate EIDO object
        eido = self._generate_eido(transcript, location_info, classification)
        
        # Generate notification plan
        notification_results = self._generate_notification_plan(eido)
        
        # Calculate processing times
        processing_time = time.time() - start_time
        notification_time = processing_time * 0.3  # Simulated notification planning time
        
        # Assemble complete results
        results = {
            "eido": eido,
            "notification_results": notification_results,
            "processing_time": round(processing_time, 2),
            "notification_time": round(notification_time, 2),
            "location": location_info,
            "classification": classification
        }
        
        return results
    
    def process_incident_report(self, report: str) -> Dict[str, Any]:
        """
        Process a written incident report into a structured EIDO object.
        
        Args:
            report: The incident report text
            
        Returns:
            Dictionary with processing results
        """
        # Similar to process_emergency_call but adapted for reports
        start_time = time.time()
        
        # Extract location using simulated LLM
        location_info = self._extract_location(report)
        
        # Classify incident using simulated LLM
        classification = self._classify_incident(report)
        
        # Generate EIDO object
        eido = self._generate_eido(report, location_info, classification, is_report=True)
        
        # Generate notification plan
        notification_results = self._generate_notification_plan(eido)
        
        # Calculate processing times
        processing_time = time.time() - start_time
        notification_time = processing_time * 0.3  # Simulated notification planning time
        
        # Assemble complete results
        results = {
            "eido": eido,
            "notification_results": notification_results,
            "processing_time": round(processing_time, 2),
            "notification_time": round(notification_time, 2),
            "location": location_info,
            "classification": classification
        }
        
        return results
    
    def _extract_location(self, text: str) -> Dict[str, Any]:
        """
        Extract location information from text using NLP (simulated).
        
        Args:
            text: The text to analyze
            
        Returns:
            Dictionary with location data
        """
        text_lower = text.lower()
        
        # Check for known locations
        for keyword, loc_data in self.known_locations.items():
            if keyword.lower() in text_lower:
                return {
                    "lat": loc_data["lat"],
                    "lng": loc_data["lng"],
                    "name": loc_data["name"],
                    "source": f"LLM extracted \"{keyword}\" from the text",
                    "confidence": 0.92
                }
        
        # Default to UCSD campus
        return {
            "lat": 32.8801,
            "lng": -117.2340,
            "name": "UC San Diego Campus",
            "source": "Default location (no specific location found)",
            "confidence": 0.6
        }
    
    def _classify_incident(self, text: str) -> Dict[str, Any]:
        """
        Classify incident type and details from text (simulated LLM).
        
        Args:
            text: The text to analyze
            
        Returns:
            Dictionary with classification data
        """
        text_lower = text.lower()
        
        # Incident type classification based on keywords
        incident_type = "unknown"
        priority = 3
        confidence = 0.7
        
        if re.search(r'fire|burning|flames|smoke', text_lower):
            incident_type = "fire"
            priority = 1
            confidence = 0.95
        elif re.search(r'gas leak|gas smell|fume|strong smell', text_lower):
            incident_type = "hazard"
            priority = 1
            confidence = 0.93
        elif re.search(r'suspicious|theft|steal|threat|weapon|gun', text_lower):
            incident_type = "crime"
            priority = 2
            confidence = 0.88
        elif re.search(r'injured|hurt|medical|ambulance|blood', text_lower):
            incident_type = "medical"
            priority = 2
            confidence = 0.91
        elif re.search(r'leak|chemical|hazard|spill', text_lower):
            incident_type = "hazard"
            priority = 1
            confidence = 0.89
        elif re.search(r'power|outage|electricity', text_lower):
            incident_type = "infrastructure"
            priority = 3
            confidence = 0.85
        
        # Determine subtype
        subtype = ""
        if incident_type == "crime":
            if re.search(r'theft|steal|took|missing', text_lower):
                subtype = "theft"
            elif re.search(r'suspicious|strange|odd', text_lower):
                subtype = "suspicious_person"
            elif re.search(r'assault|attack|hit|punch', text_lower):
                subtype = "assault"
            elif re.search(r'break|broke|breaking', text_lower):
                subtype = "break_in"
        elif incident_type == "hazard":
            if re.search(r'gas|smell', text_lower):
                subtype = "gas_leak"
            elif re.search(r'chemical|spill', text_lower):
                subtype = "chemical_spill"
            elif re.search(r'water|flood', text_lower):
                subtype = "flooding"
        
        # Extract victim info
        victim_count = 0
        victim_details = ""
        if re.search(r'injured|hurt|victim|bleeding', text_lower):
            victim_match = re.search(r'(\d+)\s+(?:person|people|individuals|victims)', text_lower)
            victim_count = int(victim_match.group(1)) if victim_match else 1
            victim_details = "Details extracted from text"
        
        # Extract suspect info
        suspect_info = ""
        weapons_involved = bool(re.search(r'weapon|gun|knife|armed', text_lower))
        if re.search(r'suspect|suspicious|man|woman|person|wearing', text_lower):
            description_match = re.search(r'wearing[^.]*', text, re.I)
            if description_match:
                suspect_info = description_match.group(0)
            else:
                suspect_info = "Suspicious person reported"
        
        # Extract key details
        key_details = []
        if victim_count > 0:
            key_details.append(f"{victim_count} person(s) potentially injured")
        if suspect_info:
            key_details.append(f"Suspect description: {suspect_info}")
        if weapons_involved:
            key_details.append("Weapons may be involved")
        
        # Add default details if none extracted
        if not key_details:
            key_details = ["Incident reported", "Details pending"]
        
        return {
            "incidentType": incident_type,
            "subtype": subtype,
            "priority": priority,
            "confidence": confidence,
            "victimCount": victim_count,
            "victimDetails": victim_details,
            "suspectInfo": suspect_info,
            "weaponsInvolved": weapons_involved,
            "keyDetails": key_details,
            "analysis": f"LLM classified this as a {incident_type} incident with {confidence:.2f} confidence."
        }
    
    def _generate_eido(self, text: str, location: Dict[str, Any], classification: Dict[str, Any], is_report=False) -> Dict[str, Any]:
        """
        Generate a standardized EIDO object from processed information.
        
        Args:
            text: The original text
            location: Location information
            classification: Incident classification
            is_report: Whether this is a report (vs. emergency call)
            
        Returns:
            EIDO object dictionary
        """
        incident_id = f"INC-{int(time.time())}"
        eido_id = f"EIDO-{int(time.time())}"
        timestamp = datetime.datetime.now().isoformat()
        
        # Get recommended actions based on incident type and priority
        recommended_actions = self._get_recommended_actions(
            classification["incidentType"], 
            classification["priority"]
        )
        
        # Determine notification scope
        notification_scope = {
            "geographic": self._get_geographic_scope(classification["incidentType"], classification["priority"]),
            "radius_meters": self._get_notification_radius(classification["incidentType"], classification["priority"]),
            "population": self._get_target_population(classification["incidentType"], classification["priority"]),
            "notify_authorities": True
        }
        
        # Create the EIDO object
        eido = {
            "eido": {
                "eidoVersion": "1.0",
                "eidoType": "incident",
                "eidoID": eido_id,
                "timestamp": timestamp,
                "incident": {
                    "incidentID": incident_id,
                    "incidentType": classification["incidentType"],
                    "incidentSubType": classification["subtype"],
                    "priority": classification["priority"],
                    "status": "active",
                    "createdAt": timestamp,
                    "reportingParty": {
                        "role": "reporter" if is_report else "caller",
                        "name": ""
                    },
                    "location": {
                        "address": {
                            "fullAddress": location["name"],
                            "additionalInfo": ""
                        },
                        "coordinates": {
                            "latitude": location["lat"],
                            "longitude": location["lng"]
                        }
                    },
                    "details": {
                        "description": f"Reported {classification['incidentType']} incident at {location['name']}. Priority assessed as {classification['priority']}/5.",
                        "timeline": [
                            {
                                "timestamp": timestamp,
                                "action": "Incident reported",
                                "notes": "Initial report received"
                            }
                        ],
                        "victims": {
                            "count": classification["victimCount"],
                            "details": classification["victimDetails"]
                        },
                        "suspects": {
                            "description": classification["suspectInfo"],
                            "weaponsInvolved": classification["weaponsInvolved"]
                        },
                        "keyFacts": classification["keyDetails"],
                        "rawReport": text
                    }
                },
                "notification": {
                    "recommendedActions": recommended_actions,
                    "recommendedNotificationScope": notification_scope,
                    "updateFrequency": "as_needed"
                }
            }
        }
        
        return eido
    
    def _generate_notification_plan(self, eido: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a notification plan based on the EIDO.
        
        Args:
            eido: The EIDO object
            
        Returns:
            Notification plan dictionary
        """
        incident = eido["eido"]["incident"]
        notification_recommendations = eido["eido"]["notification"]
        
        # Create notification content
        content = {
            "summary": f"{incident['incidentType'].upper()}: {incident['location']['address']['fullAddress']}",
            "description": incident["details"]["description"],
            "location": incident["location"]["address"]["fullAddress"],
            "action_required": "; ".join(notification_recommendations["recommendedActions"]),
            "details_url": f"https://alerts.ucsd.edu/details/{incident['incidentID'][-6:]}",
            "severity": self._map_priority_to_severity(incident["priority"])
        }
        
        # Create notification plan
        notification_plan = self._create_notification_plan(eido)
        
        # Assemble notification results
        notification_results = {
            "incident_id": incident["incidentID"],
            "timestamp": datetime.datetime.now().isoformat(),
            "notification_radius_meters": notification_recommendations["recommendedNotificationScope"]["radius_meters"],
            "target_groups": notification_recommendations["recommendedNotificationScope"]["population"],
            "recipients_count": len(notification_plan),
            "notification_plan": notification_plan,
            "content": content
        }
        
        return notification_results
    
    def _get_recommended_actions(self, incident_type: str, priority: int) -> List[str]:
        """Get recommended actions based on incident type and priority."""
        if incident_type == "fire":
            return ["Evacuate the building immediately", "Move to designated assembly areas"]
        elif incident_type == "crime":
            return ["Be aware of your surroundings", "Report suspicious activity to campus police"]
        elif incident_type == "medical":
            return ["Clear the area for emergency responders", "Direct responders to the location"]
        elif incident_type == "hazard":
            return ["Avoid the affected area", "Follow instructions from emergency personnel"]
        else:
            return ["Stay alert", "Follow official instructions"]
    
    def _get_geographic_scope(self, incident_type: str, priority: int) -> str:
        """Determine the geographic scope for notifications."""
        if priority == 1:
            return "campus_wide"
        elif priority == 2:
            return "campus_section"
        elif incident_type == "fire":
            return "affected_building"
        else:
            return "immediate_vicinity"
    
    def _get_notification_radius(self, incident_type: str, priority: int) -> int:
        """Determine notification radius in meters."""
        if priority == 1:
            return 1000
        elif priority == 2:
            return 500
        elif incident_type == "fire":
            return 300
        else:
            return 100
    
    def _get_target_population(self, incident_type: str, priority: int) -> List[str]:
        """Determine target population groups for notification."""
        groups = ["emergency_responders"]
        
        if priority == 1:
            groups.extend(["all_students", "all_staff", "all_faculty", "leadership"])
        elif priority == 2:
            groups.extend(["area_occupants", "leadership"])
        else:
            groups.append("area_occupants")
        
        if incident_type == "fire":
            groups.append("facilities")
        elif incident_type == "crime":
            groups.extend(["police", "security"])
        elif incident_type == "medical":
            groups.append("health_services")
        elif incident_type == "hazard":
            groups.extend(["environmental_safety", "facilities"])
        
        # Remove duplicates
        return list(set(groups))
    
    def _map_priority_to_severity(self, priority: int) -> str:
        """Map numerical priority to text severity."""
        severity_map = {
            1: "CRITICAL",
            2: "HIGH",
            3: "MEDIUM",
            4: "LOW",
            5: "INFORMATION"
        }
        return severity_map.get(priority, "MEDIUM")
    
    def _create_notification_plan(self, eido: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Create a detailed notification plan based on the EIDO.
        
        Args:
            eido: The EIDO object
            
        Returns:
            List of notification instructions
        """
        channels = ["sms", "email", "app_push", "phone"]
        plan = []
        
        # Sample recipients
        recipients = [
            {"id": "r001", "name": "Chief Roberts", "role": "campus_police_chief"},
            {"id": "r002", "name": "Officer Garcia", "role": "campus_police"},
            {"id": "r003", "name": "Dr. Chen", "role": "dean"},
            {"id": "r004", "name": "Facilities Team", "role": "facilities"},
            {"id": "r005", "name": "Campus Security", "role": "security"},
            {"id": "r006", "name": "Student Health Center", "role": "health_services"},
            {"id": "r007", "name": "Environmental Safety", "role": "environmental_safety"},
            {"id": "s001", "name": "Alex Smith", "role": "student"},
            {"id": "s002", "name": "Jordan Lee", "role": "student"},
            {"id": "s003", "name": "Taylor Wilson", "role": "student"}
        ]
        
        # Determine which channels to use based on priority
        priority = eido["eido"]["incident"]["priority"]
        channels_to_use = []
        
        if priority == 1:
            channels_to_use = channels  # Use all channels for highest priority
        elif priority == 2:
            channels_to_use = ["sms", "app_push", "email"]  # Use most channels for high priority
        else:
            channels_to_use = ["app_push", "email"]  # Use fewer channels for lower priority
        
        # Create notification entries
        for recipient in recipients:
            for channel in channels_to_use:
                plan.append({
                    "recipient_id": recipient["id"],
                    "recipient_name": recipient["name"],
                    "channel": channel,
                    "message": f"{eido['eido']['incident']['incidentType'].upper()} ALERT: Incident at {eido['eido']['incident']['location']['address']['fullAddress']}. {eido['eido']['notification']['recommendedActions'][0]}",
                    "priority": priority,
                    "timestamp": datetime.datetime.now().isoformat()
                })
        
        return plan