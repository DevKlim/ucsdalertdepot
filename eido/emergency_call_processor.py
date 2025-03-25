"""
Emergency call processor for converting 911 transcripts to EIDO format.

This module processes emergency call transcripts and extracts key information
to create a standardized EIDO object for notification decisions.
"""

import json
import os
import re
import uuid
import datetime
from typing import Dict, Any, List, Optional, Tuple

# Import local modules
from mistralai import Mistral
from eido.eido_schema import create_empty_eido, validate_eido
from eido.location_extractor import extract_json_from_response
from geocoding.geocode import geocode_location

class EmergencyCallProcessor:
    """
    Processes emergency call transcripts into structured EIDO format.
    Demo #1 - taking a 911 call transcript and converting it to an EIDO.
    """
    
    def __init__(self, api_key=None):
        """
        Initialize the emergency call processor.
        
        Args:
            api_key: API key for Mistral LLM (optional, will use env var if not provided)
        """
        self.api_key = api_key or os.environ.get("MISTRAL_API_KEY")
        if not self.api_key:
            raise ValueError("Mistral API key is required. Set MISTRAL_API_KEY environment variable or pass as argument.")
            
        self.client = Mistral(api_key=self.api_key)
        self.model = "mistral-large-latest"
    
    def process_call(self, transcript: str) -> Dict[str, Any]:
        """
        Process an emergency call transcript and create an EIDO object.
        
        Args:
            transcript: The text transcript of the emergency call
            
        Returns:
            EIDO object as a dictionary
        """
        # Create an empty EIDO to start with
        eido = create_empty_eido()
        
        # Extract key information using the LLM
        extracted_info = self._extract_information(transcript)
        
        # Update the EIDO with extracted information
        self._update_eido_with_extracted_info(eido, extracted_info, transcript)
        
        # Validate the EIDO
        validate_eido(eido)
        
        return eido
    
    def _extract_information(self, transcript: str) -> Dict[str, Any]:
        """
        Extract key information from the call transcript using an LLM.
        
        Args:
            transcript: The call transcript
            
        Returns:
            Dictionary with extracted information
        """
        prompt = f"""
        You are an emergency call processing expert. Analyze this 911 call transcript and extract key information needed for emergency response.
        
        TRANSCRIPT:
        {transcript}
        
        Extract and return ONLY a JSON object with these fields:
        - incident_type: Primary category (e.g., "fire", "medical", "crime", "hazard", "infrastructure")
        - incident_subtype: More specific classification 
        - priority: Assessed emergency priority (1-5, with 1 being highest priority)
        - location: The specific location mentioned
        - location_details: Building, floor, room number, etc.
        - reporter_info: Information about the person reporting the incident
        - victim_count: Estimated number of affected/injured people
        - victim_details: Details about victims' conditions
        - suspect_info: Any information about suspects (for criminal incidents)
        - weapons_involved: Boolean indicating if weapons are involved
        - immediate_danger: Boolean indicating if there's immediate danger to people
        - key_details: Array of 3-5 most important details from the transcript
        - recommended_response: Brief recommendation for appropriate emergency response
        - quote: A direct quote from the transcript that best illustrates the situation
        
        Output ONLY the JSON with no additional text.
        """
        
        try:
            response = self.client.chat.complete(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an emergency call processing expert who extracts key information from 911 call transcripts."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            result_text = response.choices[0].message.content
            
            # Clean up the result
            result_text = extract_json_from_response(result_text)
            
            return json.loads(result_text)
                
        except Exception as e:
            print(f"Error extracting information: {e}")
            # Fallback extraction if API fails
            return self._fallback_extraction(transcript)
    
    def _fallback_extraction(self, transcript: str) -> Dict[str, Any]:
        """Simple rule-based extraction as fallback if LLM API fails."""
        # Extract incident type based on keywords
        incident_type = "unknown"
        if re.search(r'fire|burning|smoke|flames', transcript, re.I):
            incident_type = "fire"
        elif re.search(r'hurt|injured|bleeding|pain|medical|ambulance|heart', transcript, re.I):
            incident_type = "medical"
        elif re.search(r'steal|robber|thief|assault|attack|threat|suspicious|weapon|gun', transcript, re.I):
            incident_type = "crime"
        elif re.search(r'leak|spill|chemical|gas|hazard|toxic|explosion', transcript, re.I):
            incident_type = "hazard"
        elif re.search(r'power|outage|water|flooding|building|damage|elevator', transcript, re.I):
            incident_type = "infrastructure"
            
        # Extract location with a simple regex
        location_match = re.search(r'at\s+([A-Za-z0-9\s,&\-]+?)(?:\.|\n)', transcript)
        location = location_match.group(1).strip() if location_match else "Unknown location"
        
        # Determine priority based on keywords
        priority = 3  # Default to medium
        if re.search(r'emergency|immediate|life.?threatening|critical|severe|grave', transcript, re.I):
            priority = 1
        elif re.search(r'urgent|serious|bad|quickly|asap', transcript, re.I):
            priority = 2
        elif re.search(r'minor|small|not urgent|not serious|not bad', transcript, re.I):
            priority = 4
            
        # Determine if weapons are involved
        weapons_involved = bool(re.search(r'gun|knife|weapon|armed', transcript, re.I))
        
        # Extract a quote
        sentences = re.split(r'[.!?]', transcript)
        quote = sentences[1].strip() if len(sentences) > 1 else transcript[:100]
            
        return {
            "incident_type": incident_type,
            "incident_subtype": "",
            "priority": priority,
            "location": location,
            "location_details": "",
            "reporter_info": "",
            "victim_count": 1 if incident_type == "medical" else 0,
            "victim_details": "",
            "suspect_info": "",
            "weapons_involved": weapons_involved,
            "immediate_danger": priority <= 2,
            "key_details": ["Extracted through fallback system due to API error"],
            "recommended_response": "Dispatch appropriate emergency services",
            "quote": quote
        }
    
    def _update_eido_with_extracted_info(self, eido: Dict[str, Any], extracted_info: Dict[str, Any], transcript: str) -> None:
        """
        Update the EIDO object with the extracted information.
        
        Args:
            eido: The EIDO object to update
            extracted_info: The extracted information from the call
            transcript: The original transcript
        """
        # Map the incident type
        eido["eido"]["incident"]["incidentType"] = extracted_info.get("incident_type", "unknown")
        
        # Set incident subtype if available
        subtype = extracted_info.get("incident_subtype")
        if subtype:
            eido["eido"]["incident"]["incidentSubType"] = subtype
        
        # Set priority (convert from 1-5 scale where 1 is highest priority)
        priority = extracted_info.get("priority", 3)
        eido["eido"]["incident"]["priority"] = priority
        
        # Set location information
        location = extracted_info.get("location", "Unknown location")
        location_details = extracted_info.get("location_details", "")
        
        eido["eido"]["incident"]["location"]["address"]["fullAddress"] = location
        if location_details:
            eido["eido"]["incident"]["location"]["address"]["additionalInfo"] = location_details
        
        # Try to geocode the location
        try:
            coordinates = geocode_location(location)
            if coordinates:
                eido["eido"]["incident"]["location"]["coordinates"]["latitude"] = coordinates.get("lat")
                eido["eido"]["incident"]["location"]["coordinates"]["longitude"] = coordinates.get("lng")
        except Exception as e:
            print(f"Warning: Failed to geocode location '{location}': {e}")
        
        # Set reporting party information
        reporter_info = extracted_info.get("reporter_info", "Unknown caller")
        eido["eido"]["incident"]["reportingParty"]["name"] = reporter_info
        eido["eido"]["incident"]["reportingParty"]["role"] = "caller"
        
        # Set victim information
        victim_count = extracted_info.get("victim_count", 0)
        victim_details = extracted_info.get("victim_details", "")
        
        eido["eido"]["incident"]["details"]["victims"]["count"] = victim_count
        if victim_details:
            eido["eido"]["incident"]["details"]["victims"]["details"] = victim_details
        
        # Set suspect information
        suspect_info = extracted_info.get("suspect_info", "")
        weapons_involved = extracted_info.get("weapons_involved", False)
        
        if suspect_info:
            eido["eido"]["incident"]["details"]["suspects"]["description"] = suspect_info
        eido["eido"]["incident"]["details"]["suspects"]["weaponsInvolved"] = weapons_involved
        
        # Set incident description
        key_details = extracted_info.get("key_details", [])
        quote = extracted_info.get("quote", "")
        
        # Create a comprehensive description
        description_parts = []
        if key_details:
            description_parts.append("Key details: " + "; ".join(key_details))
        if quote:
            description_parts.append(f"Caller quote: \"{quote}\"")
            
        description = " ".join(description_parts) if description_parts else "No details available"
        eido["eido"]["incident"]["details"]["description"] = description
        
        # Store key facts
        if key_details:
            eido["eido"]["incident"]["details"]["keyFacts"] = key_details
        
        # Store raw report
        eido["eido"]["incident"]["details"]["rawReport"] = transcript
        
        # Set notification recommendations
        recommended_response = extracted_info.get("recommended_response", "")
        immediate_danger = extracted_info.get("immediate_danger", False)
        
        if recommended_response:
            eido["eido"]["notification"]["recommendedActions"] = [recommended_response]
            
        # Determine notification scope based on incident type and priority
        scope = self._determine_notification_scope(
            incident_type=eido["eido"]["incident"]["incidentType"],
            priority=priority,
            immediate_danger=immediate_danger,
            weapons_involved=weapons_involved
        )
        
        eido["eido"]["notification"]["recommendedNotificationScope"] = scope
    
    def _determine_notification_scope(
        self, 
        incident_type: str, 
        priority: int,
        immediate_danger: bool,
        weapons_involved: bool
    ) -> Dict[str, Any]:
        """
        Determine the recommended notification scope based on incident details.
        
        Args:
            incident_type: Type of incident
            priority: Priority level (1-5, where 1 is highest)
            immediate_danger: Whether there's immediate danger
            weapons_involved: Whether weapons are involved
            
        Returns:
            Dictionary with recommended notification scope
        """
        # Default scope - minimal
        scope = {
            "geographic": "immediate_vicinity",
            "radius_meters": 100,
            "population": ["emergency_responders"],
            "notify_authorities": True
        }
        
        # Adjust based on incident type
        if incident_type == "fire":
            scope["geographic"] = "affected_building"
            scope["radius_meters"] = 300
            scope["population"].extend(["building_occupants", "facilities"])
            
        elif incident_type == "crime":
            scope["geographic"] = "campus_section"
            scope["radius_meters"] = 500
            scope["population"].extend(["security", "police"])
            
            # For armed incidents, increase the scope
            if weapons_involved:
                scope["geographic"] = "campus_wide"
                scope["radius_meters"] = 1000
                scope["population"].extend(["all_students", "all_staff", "all_faculty"])
                
        elif incident_type == "hazard":
            scope["geographic"] = "affected_area"
            scope["radius_meters"] = 500
            scope["population"].extend(["area_occupants", "environmental_safety"])
            
        elif incident_type == "medical":
            scope["geographic"] = "immediate_vicinity"
            scope["radius_meters"] = 50
            scope["population"].extend(["health_services"])
            
        # Adjust based on priority and danger
        if priority <= 2 or immediate_danger:
            # High priority or immediate danger
            if scope["geographic"] != "campus_wide":
                scope["geographic"] = "campus_section"
                scope["radius_meters"] = max(scope["radius_meters"], 500)
                
            # Always notify leadership for high priority incidents
            if "leadership" not in scope["population"]:
                scope["population"].append("leadership")
                
        if priority == 1:
            # Highest priority - campus-wide
            scope["geographic"] = "campus_wide"
            scope["radius_meters"] = 1000
            scope["population"] = list(set(scope["population"] + ["all_students", "all_staff", "all_faculty"]))
                
        return scope


# Example usage
if __name__ == "__main__":
    # Sample emergency call transcript
    sample_transcript = """
    Dispatcher: 911, what's your emergency?
    
    Caller: Hi, um, I'm at Geisel Library on the UC San Diego campus, and there's a fire in one of the study rooms on the 2nd floor, east wing.
    
    Dispatcher: Is anyone injured?
    
    Caller: I don't think so. People are evacuating, but the fire is spreading quickly. It looks like it started from someone's laptop that overheated or something.
    
    Dispatcher: OK, I'm dispatching the fire department. How big is the fire?
    
    Caller: It's getting bigger. The whole study room is on fire now and it's spreading to the bookshelves. There's a lot of smoke. People are running out.
    
    Dispatcher: Are the fire alarms going off?
    
    Caller: Yes, they just started. Everyone is leaving the building now.
    
    Dispatcher: Good. What's your name?
    
    Caller: Sarah Johnson. I'm a student here.
    
    Dispatcher: OK Sarah, can you get to a safe location outside the building?
    
    Caller: Yes, I'm outside now. But please hurry, it's getting worse.
    
    Dispatcher: Help is on the way. The fire department has been dispatched. Stay safe and stay on the line if you can.
    """
    
    processor = EmergencyCallProcessor()
    eido = processor.process_call(sample_transcript)
    
    print(json.dumps(eido, indent=2))