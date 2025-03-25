"""
eido_schema.py

Defines the Emergency Incident Data Object (EIDO) format and provides validation functions.
Based on NENA (National Emergency Number Association) standards.
"""

import json
from typing import Dict, Any, List, Optional, Union
from datetime import datetime
import re

# EIDO Schema Definition
EIDO_SCHEMA = {
    "eido": {
        "eidoVersion": str,
        "eidoType": str,  # "incident", "update", "closure", etc.
        "eidoID": str,
        "timestamp": str,
        "incident": {
            "incidentID": str,
            "incidentType": str,
            "incidentSubType": Optional[str],
            "priority": int,  # 1-5, where 1 is highest priority
            "status": str,  # "active", "contained", "resolved", etc.
            "createdAt": str,
            "updatedAt": Optional[str],
            "reportingParty": {
                "role": str,
                "name": Optional[str],
                "contact": Optional[str]
            },
            "location": {
                "address": {
                    "fullAddress": str,
                    "additionalInfo": Optional[str]
                },
                "coordinates": {
                    "latitude": Optional[float],
                    "longitude": Optional[float]
                }
            },
            "details": {
                "description": str,
                "timeline": List[Dict],
                "victims": {
                    "count": int,
                    "details": Optional[str]
                },
                "suspects": {
                    "description": Optional[str],
                    "weaponsInvolved": bool
                },
                "keyFacts": Optional[List[str]],
                "rawReport": Optional[str]
            }
        },
        "notification": {
            "recommendedActions": List[str],
            "recommendedNotificationScope": {
                "geographic": str,
                "radius_meters": Optional[int],
                "population": List[str],
                "notify_authorities": bool
            },
            "updateFrequency": Optional[str]
        }
    }
}

class EIDOValidationError(Exception):
    """Exception raised for EIDO validation errors."""
    pass

def validate_eido(eido_object: Dict[str, Any]) -> bool:
    """
    Validates an EIDO object against the schema.
    
    Args:
        eido_object: Dictionary containing the EIDO object
        
    Returns:
        True if valid, raises an exception if invalid
    """
    try:
        _validate_object(eido_object, EIDO_SCHEMA)
        return True
    except Exception as e:
        raise EIDOValidationError(f"EIDO validation failed: {str(e)}")

def _validate_object(obj: Any, schema: Any, path: str = "") -> None:
    """
    Recursively validates an object against a schema.
    
    Args:
        obj: The object to validate
        schema: The schema to validate against
        path: Current path in the object for error reporting
    """
    if schema is None:
        return
    
    # Handle Optional types
    if isinstance(schema, type) and schema.__module__ == "typing" and hasattr(schema, "__origin__"):
        if schema.__origin__ is Union and type(None) in schema.__args__:
            # This is an Optional[...] type
            if obj is None:
                return
            # Extract the actual type from Optional
            actual_type = next(arg for arg in schema.__args__ if arg is not type(None))
            _validate_object(obj, actual_type, path)
            return
    
    # Handle List types
    if isinstance(schema, type) and schema.__module__ == "typing" and schema.__origin__ is list:
        if not isinstance(obj, list):
            raise EIDOValidationError(f"{path} should be a list")
        # Validate each item in the list
        item_type = schema.__args__[0]
        for i, item in enumerate(obj):
            _validate_object(item, item_type, f"{path}[{i}]")
        return
    
    # Handle Dict types with structure
    if isinstance(schema, dict):
        if not isinstance(obj, dict):
            raise EIDOValidationError(f"{path} should be a dictionary")
        
        # Check required fields
        for key, value_schema in schema.items():
            if key not in obj:
                raise EIDOValidationError(f"{path}.{key} is required but missing")
            _validate_object(obj[key], value_schema, f"{path}.{key}")
        
        return
    
    # Handle basic types
    if schema is str:
        if not isinstance(obj, str):
            raise EIDOValidationError(f"{path} should be a string")
    elif schema is int:
        if not isinstance(obj, int):
            raise EIDOValidationError(f"{path} should be an integer")
    elif schema is float:
        if not isinstance(obj, (int, float)):
            raise EIDOValidationError(f"{path} should be a number")
    elif schema is bool:
        if not isinstance(obj, bool):
            raise EIDOValidationError(f"{path} should be a boolean")
    elif schema is Any:
        # Any type is valid
        pass
    else:
        raise EIDOValidationError(f"Unknown schema type at {path}: {schema}")

def create_empty_eido() -> Dict[str, Any]:
    """
    Creates an empty EIDO object with default values.
    
    Returns:
        An EIDO object with default values
    """
    current_time = datetime.now().isoformat()
    return {
        "eido": {
            "eidoVersion": "1.0",
            "eidoType": "incident",
            "eidoID": generate_eido_id(),
            "timestamp": current_time,
            "incident": {
                "incidentID": generate_incident_id(),
                "incidentType": "",
                "incidentSubType": "",
                "priority": 3,  # Default to medium priority
                "status": "active",
                "createdAt": current_time,
                "updatedAt": None,
                "reportingParty": {
                    "role": "unknown",
                    "name": "",
                    "contact": ""
                },
                "location": {
                    "address": {
                        "fullAddress": "",
                        "additionalInfo": ""
                    },
                    "coordinates": {
                        "latitude": None,
                        "longitude": None
                    }
                },
                "details": {
                    "description": "",
                    "timeline": [
                        {
                            "timestamp": current_time,
                            "action": "Incident created",
                            "notes": ""
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
                    "keyFacts": [],
                    "rawReport": ""
                }
            },
            "notification": {
                "recommendedActions": [],
                "recommendedNotificationScope": {
                    "geographic": "immediate_vicinity",
                    "radius_meters": 100,
                    "population": ["emergency_responders"],
                    "notify_authorities": True
                },
                "updateFrequency": "as_needed"
            }
        }
    }

def generate_eido_id() -> str:
    """Generate a unique EIDO ID."""
    time_component = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"EIDO-{time_component}-{generate_random_string(6)}"

def generate_incident_id() -> str:
    """Generate a unique incident ID."""
    time_component = datetime.now().strftime("%Y%m%d%H%M%S")
    return f"INC-{time_component}-{generate_random_string(4)}"

def generate_random_string(length: int) -> str:
    """Generate a random alphanumeric string of specified length."""
    import random
    import string
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def update_eido(original_eido: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
    """
    Updates an existing EIDO with new information and creates a new version.
    
    Args:
        original_eido: The original EIDO object
        updates: Dictionary with fields to update
        
    Returns:
        An updated EIDO object
    """
    # Create a deep copy of the original
    import copy
    updated_eido = copy.deepcopy(original_eido)
    
    # Update timestamp
    updated_eido["eido"]["timestamp"] = datetime.now().isoformat()
    
    # Update eidoType to indicate this is an update
    updated_eido["eido"]["eidoType"] = "update"
    
    # Update incident.updatedAt
    updated_eido["eido"]["incident"]["updatedAt"] = datetime.now().isoformat()
    
    # Add a timeline entry for the update
    updated_eido["eido"]["incident"]["details"]["timeline"].append({
        "timestamp": datetime.now().isoformat(),
        "action": "Information updated",
        "notes": "EIDO updated with new information"
    })
    
    # Apply the updates
    for key, value in updates.items():
        if key.startswith("incident."):
            # Handle nested updates with dot notation
            parts = key.split(".")
            target = updated_eido["eido"]
            for part in parts[:-1]:
                if part not in target:
                    target[part] = {}
                target = target[part]
            target[parts[-1]] = value
        elif key in updated_eido["eido"]["incident"]:
            updated_eido["eido"]["incident"][key] = value
    
    return updated_eido

def merge_eidos(eidos: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Merges multiple EIDOs related to the same incident.
    Useful when multiple reports come in about the same event.
    
    Args:
        eidos: List of EIDO objects to merge
        
    Returns:
        A merged EIDO representing the combined information
    """
    if not eidos:
        raise ValueError("No EIDOs provided for merging")
    
    if len(eidos) == 1:
        return eidos[0]
    
    # Use the newest EIDO as the base
    sorted_eidos = sorted(eidos, key=lambda e: e["eido"]["timestamp"], reverse=True)
    merged = copy.deepcopy(sorted_eidos[0])
    
    # Collect all unique timeline entries
    all_timeline_entries = {}
    for eido in eidos:
        for entry in eido["eido"]["incident"]["details"]["timeline"]:
            entry_key = f"{entry['timestamp']}_{entry['action']}"
            all_timeline_entries[entry_key] = entry
    
    # Sort timeline by timestamp
    merged_timeline = sorted(
        all_timeline_entries.values(),
        key=lambda e: e["timestamp"]
    )
    
    # Update the merged EIDO
    merged["eido"]["incident"]["details"]["timeline"] = merged_timeline
    
    # Add a note about the merge
    merged["eido"]["incident"]["details"]["timeline"].append({
        "timestamp": datetime.now().isoformat(),
        "action": "Incident reports merged",
        "notes": f"Merged information from {len(eidos)} related reports"
    })
    
    return merged

def extract_eido_summary(eido: Dict[str, Any]) -> Dict[str, Any]:
    """
    Extracts a summary of an EIDO for quick reference.
    
    Args:
        eido: The EIDO object
        
    Returns:
        A summary dictionary with key information
    """
    incident = eido["eido"]["incident"]
    
    return {
        "eidoID": eido["eido"]["eidoID"],
        "incidentID": incident["incidentID"],
        "type": incident["incidentType"],
        "subType": incident.get("incidentSubType", ""),
        "priority": incident["priority"],
        "status": incident["status"],
        "location": incident["location"]["address"]["fullAddress"],
        "created": incident["createdAt"],
        "updated": incident.get("updatedAt", incident["createdAt"]),
        "description": incident["details"]["description"],
        "recommendedActions": eido["eido"]["notification"]["recommendedActions"]
    }

# Example usage
if __name__ == "__main__":
    # Create an empty EIDO
    empty_eido = create_empty_eido()
    print(json.dumps(empty_eido, indent=2))
    
    # Validate the empty EIDO
    is_valid = validate_eido(empty_eido)
    print(f"Empty EIDO is valid: {is_valid}")