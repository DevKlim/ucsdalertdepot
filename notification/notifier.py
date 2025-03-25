"""
notifier.py

This module analyzes EIDO objects and determines who should be notified and how.
It's the core intelligent notification system for the Safe Campus Agent.
"""

import json
import datetime
import time
import math
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

@dataclass
class Recipient:
    """Represents a notification recipient"""
    id: str
    name: str
    role: str
    groups: List[str]
    location: Dict[str, float]  # lat/lng of current or default location
    notification_preferences: Dict[str, Any]
    active: bool = True

@dataclass
class NotificationChannel:
    """Represents a notification channel"""
    id: str
    name: str
    type: str  # sms, email, app_push, etc.
    priority: int  # 1-5, 1 being highest
    rate_limit: int  # in seconds
    template: str

class SafeCampusNotifier:
    """
    Analyzes EIDO objects and determines who should be notified and how.
    This demonstrates how AI can be used to make intelligent notification decisions.
    """
    
    def __init__(self):
        # In a real implementation, these would be loaded from a database
        self.recipients = self._load_recipients()
        self.notification_channels = self._load_notification_channels()
        self.notification_history = {}  # Track notification history by recipient
        self.location_data = self._load_location_data()
        
    def _load_recipients(self) -> List[Recipient]:
        """Load recipient data (would be from a database in a real system)"""
        # Sample recipients for demo purposes
        return [
            Recipient(
                id="r001",
                name="Chief Roberts",
                role="campus_police_chief",
                groups=["emergency_responders", "leadership", "police"],
                location={"latitude": 32.8801, "longitude": -117.2340},
                notification_preferences={
                    "channels": ["sms", "phone", "email"],
                    "severity_threshold": "low"  # Receive all notifications
                }
            ),
            Recipient(
                id="r002",
                name="Dr. Chen",
                role="dean",
                groups=["leadership", "faculty"],
                location={"latitude": 32.8795, "longitude": -117.2381},
                notification_preferences={
                    "channels": ["email", "app_push"],
                    "severity_threshold": "medium"
                }
            ),
            Recipient(
                id="r003",
                name="Facilities Team",
                role="facilities",
                groups=["staff", "emergency_responders"],
                location={"latitude": 32.8788, "longitude": -117.2410},
                notification_preferences={
                    "channels": ["sms", "radio"],
                    "severity_threshold": "low"
                }
            ),
            # Students in different campus locations
            *[self._generate_student_recipient(i, loc) for i, loc in enumerate([
                {"latitude": 32.8782, "longitude": -117.2392},  # Pepper Canyon
                {"latitude": 32.8852, "longitude": -117.2406},  # North Campus
                {"latitude": 32.8815, "longitude": -117.2350},  # Warren College
                {"latitude": 32.8789, "longitude": -117.2410},  # Muir College
                {"latitude": 32.8836, "longitude": -117.2425},  # Marshall College
            ], start=1)]
        ]
    
    def _generate_student_recipient(self, index: int, location: Dict[str, float]) -> Recipient:
        """Generate a sample student recipient"""
        return Recipient(
            id=f"s00{index}",
            name=f"Student {index}",
            role="student",
            groups=["students"],
            location=location,
            notification_preferences={
                "channels": ["app_push", "sms"],
                "severity_threshold": "medium"
            }
        )
    
    def _load_notification_channels(self) -> List[NotificationChannel]:
        """Load notification channel data"""
        return [
            NotificationChannel(
                id="sms",
                name="SMS Text Message",
                type="sms",
                priority=1,  # Highest priority
                rate_limit=300,  # No more than once per 5 minutes
                template="ALERT: {incident_type} at {location}. {action_required}. More info: {details_url}"
            ),
            NotificationChannel(
                id="app_push",
                name="Mobile App Push Notification",
                type="app_push",
                priority=2,
                rate_limit=60,
                template="🚨 {severity} ALERT: {summary}. {action_required}"
            ),
            NotificationChannel(
                id="email",
                name="Email Notification",
                type="email",
                priority=3,
                rate_limit=600,  # No more than once per 10 minutes
                template="CAMPUS ALERT: {incident_type}\n\nLocation: {location}\n\nDetails: {description}\n\nRecommended action: {action_required}\n\nUpdates will be provided as available."
            ),
            NotificationChannel(
                id="phone",
                name="Automated Phone Call",
                type="phone",
                priority=1,  # Highest priority
                rate_limit=1800,  # No more than once per 30 minutes
                template="This is an automated emergency notification from UC San Diego. {summary}. {action_required}."
            ),
            NotificationChannel(
                id="radio",
                name="Radio System",
                type="radio",
                priority=1,
                rate_limit=120,
                template="Attention all units. {incident_type} reported at {location}. {action_required}."
            )
        ]
    
    def _load_location_data(self) -> Dict[str, Dict[str, Any]]:
        """
        Load campus location data for geocoding and area determination.
        In a real implementation, this would be more comprehensive and possibly use a GIS system.
        """
        return {
            "buildings": {
                "Warren College": {
                    "center": {"latitude": 32.8815, "longitude": -117.2350},
                    "radius": 200,  # meters
                    "type": "residential"
                },
                "Muir College": {
                    "center": {"latitude": 32.8789, "longitude": -117.2410},
                    "radius": 180,
                    "type": "residential"
                },
                "Geisel Library": {
                    "center": {"latitude": 32.8810, "longitude": -117.2380},
                    "radius": 80,
                    "type": "academic"
                },
                "RIMAC Arena": {
                    "center": {"latitude": 32.8869, "longitude": -117.2406},
                    "radius": 150,
                    "type": "athletic"
                }
            },
            "areas": {
                "North Campus": {
                    "center": {"latitude": 32.8852, "longitude": -117.2406},
                    "radius": 500
                },
                "Central Campus": {
                    "center": {"latitude": 32.8801, "longitude": -117.2340},
                    "radius": 400
                },
                "South Campus": {
                    "center": {"latitude": 32.8750, "longitude": -117.2340},
                    "radius": 450
                }
            }
        }
    
    def process_eido(self, eido: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process an EIDO object and determine notification requirements.
        
        Args:
            eido: The EIDO object to process
            
        Returns:
            Dictionary with notification decisions and actions
        """
        try:
            # Extract key incident information
            incident = eido["eido"]["incident"]
            incident_type = incident["incidentType"]
            incident_subtype = incident.get("incidentSubType", "")
            priority = incident["priority"]
            status = incident["status"]
            location_data = incident["location"]
            incident_coords = self._get_incident_coordinates(location_data)
            
            # Get notification recommendations from the EIDO
            notification_recommendations = eido["eido"].get("notification", {})
            recommended_scope = notification_recommendations.get("recommendedNotificationScope", {})
            recommended_actions = notification_recommendations.get("recommendedActions", [])
            
            # Determine notification parameters
            notification_radius = self._determine_notification_radius(
                incident_type, 
                priority,
                recommended_scope.get("radius_meters", 100)
            )
            
            target_groups = self._determine_target_groups(
                incident_type,
                priority,
                recommended_scope.get("population", [])
            )
            
            # Find recipients who should be notified
            recipients_to_notify = self._find_recipients_to_notify(
                incident_coords,
                notification_radius,
                target_groups,
                priority
            )
            
            # Create notification content
            notification_content = self._create_notification_content(
                incident,
                recommended_actions
            )
            
            # Determine channels for each recipient
            notification_plan = self._create_notification_plan(
                recipients_to_notify,
                notification_content,
                priority
            )
            
            # Return the notification results
            return {
                "incident_id": incident["incidentID"],
                "timestamp": datetime.datetime.now().isoformat(),
                "notification_radius_meters": notification_radius,
                "target_groups": target_groups,
                "recipients_count": len(recipients_to_notify),
                "notification_plan": notification_plan,
                "content": notification_content
            }
            
        except Exception as e:
            print(f"Error processing EIDO for notifications: {e}")
            return {
                "error": str(e),
                "incident_id": eido.get("eido", {}).get("incident", {}).get("incidentID", "unknown"),
                "timestamp": datetime.datetime.now().isoformat(),
                "status": "failed"
            }
    
    def _get_incident_coordinates(self, location_data: Dict[str, Any]) -> Optional[Dict[str, float]]:
        """Extract coordinates from location data or geocode if needed."""
        # Try to get coordinates directly
        coordinates = location_data.get("coordinates", {})
        
        if coordinates and coordinates.get("latitude") is not None and coordinates.get("longitude") is not None:
            return coordinates
        
        # If no coordinates, try to geocode the address
        address = location_data.get("address", {}).get("fullAddress", "")
        if address:
            # In a real implementation, this would call a geocoding service
            # For the demo, we'll check if the address contains known locations
            for building_name, building_data in self.location_data["buildings"].items():
                if building_name.lower() in address.lower():
                    return building_data["center"]
            
            for area_name, area_data in self.location_data["areas"].items():
                if area_name.lower() in address.lower():
                    return area_data["center"]
            
            # Default to campus center if no match found
            return {"latitude": 32.8801, "longitude": -117.2340}
        
        return None
    
    def _determine_notification_radius(self, incident_type: str, priority: int, recommended_radius: int) -> int:
        """
        Determine the appropriate notification radius in meters.
        
        Args:
            incident_type: Type of incident
            priority: Priority level (1-5)
            recommended_radius: Recommended radius from EIDO
            
        Returns:
            Radius in meters
        """
        # Start with the recommended radius
        radius = recommended_radius
        
        # Adjust based on incident type and priority
        if incident_type.lower() == "fire":
            # Fires need wider notification
            radius = max(radius, 300)
            
        elif incident_type.lower() == "active_threat" or "shooter" in incident_type.lower():
            # Active threats need campus-wide notification
            radius = 2000  # Cover most of campus
            
        # Adjust based on priority (1 is highest)
        if priority == 1:
            radius = max(radius, 500)
        elif priority == 2:
            radius = max(radius, 300)
            
        return radius
    
    def _determine_target_groups(self, incident_type: str, priority: int, recommended_groups: List[str]) -> List[str]:
        """
        Determine which groups should be notified.
        
        Args:
            incident_type: Type of incident
            priority: Priority level (1-5)
            recommended_groups: Groups recommended in the EIDO
            
        Returns:
            List of group identifiers
        """
        # Start with emergency responders always being notified
        groups = {"emergency_responders"}
        
        # Add recommended groups
        groups.update(recommended_groups)
        
        # Add groups based on incident type
        if incident_type.lower() == "fire":
            groups.update(["facilities", "building_managers"])
            
        elif incident_type.lower() in ["crime", "assault", "robbery"]:
            groups.update(["police", "security"])
            
        elif incident_type.lower() in ["hazard", "chemical", "gas_leak"]:
            groups.update(["facilities", "environmental_safety"])
            
        # Adjust based on priority (1 is highest)
        if priority == 1:
            # Highest priority incidents involve campus leadership
            groups.update(["leadership", "campus_police"])
            
        # Convert set to list before returning
        return list(groups)
    
    def _find_recipients_to_notify(self, 
                                  incident_coords: Dict[str, float], 
                                  radius_meters: int,
                                  target_groups: List[str],
                                  priority: int) -> List[Dict[str, Any]]:
        """
        Find recipients who should be notified based on location and groups.
        
        Args:
            incident_coords: Coordinates of the incident
            radius_meters: Radius for notifications in meters
            target_groups: Groups to notify
            priority: Priority level (1-5)
            
        Returns:
            List of recipients to notify with metadata
        """
        recipients_to_notify = []
        
        # Determine severity level based on priority
        severity_map = {
            1: "critical",
            2: "high",
            3: "medium",
            4: "low",
            5: "information"
        }
        severity = severity_map.get(priority, "medium")
        
        for recipient in self.recipients:
            # Skip inactive recipients
            if not recipient.active:
                continue
                
            # Check if recipient is part of a target group
            recipient_groups = set(recipient.groups)
            target_groups_set = set(target_groups)
            
            is_in_target_group = bool(recipient_groups.intersection(target_groups_set))
            
            # Check if recipient is within notification radius
            distance = self._calculate_distance(
                incident_coords.get("latitude", 0), 
                incident_coords.get("longitude", 0),
                recipient.location.get("latitude", 0),
                recipient.location.get("longitude", 0)
            )
            
            is_in_radius = distance <= radius_meters
            
            # Check severity threshold
            recipient_threshold = recipient.notification_preferences.get("severity_threshold", "medium")
            severity_levels = ["low", "medium", "high", "critical"]
            recipient_threshold_idx = severity_levels.index(recipient_threshold) if recipient_threshold in severity_levels else 1
            severity_idx = severity_levels.index(severity) if severity in severity_levels else 1
            meets_severity_threshold = severity_idx >= recipient_threshold_idx
            
            # Determine if recipient should be notified
            # Special case: emergency responders are always notified for high priority
            is_emergency_responder = "emergency_responders" in recipient_groups
            
            should_notify = (
                (is_in_target_group and is_in_radius and meets_severity_threshold) or
                (is_emergency_responder and priority <= 2)  # Always notify emergency responders for priority 1-2
            )
            
            if should_notify:
                recipients_to_notify.append({
                    "recipient": recipient,
                    "distance_meters": distance,
                    "reason": {
                        "in_target_group": is_in_target_group,
                        "in_radius": is_in_radius,
                        "meets_severity": meets_severity_threshold,
                        "is_emergency_responder": is_emergency_responder
                    }
                })
        
        return recipients_to_notify
    
    def _calculate_distance(self, lat1: float, lon1: float, lat2: float, lon2: float) -> float:
        """
        Calculate distance between two points in meters using Haversine formula.
        
        Args:
            lat1, lon1: Coordinates of first point
            lat2, lon2: Coordinates of second point
            
        Returns:
            Distance in meters
        """
        # Earth radius in meters
        R = 6371000
        
        # Convert degrees to radians
        lat1_rad = math.radians(lat1)
        lon1_rad = math.radians(lon1)
        lat2_rad = math.radians(lat2)
        lon2_rad = math.radians(lon2)
        
        # Differences
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        # Haversine formula
        a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance = R * c
        
        return distance
    
    def _create_notification_content(self, incident: Dict[str, Any], recommended_actions: List[str]) -> Dict[str, str]:
        """
        Create notification content for different channels.
        
        Args:
            incident: Incident information from the EIDO
            recommended_actions: Recommended actions from the EIDO
            
        Returns:
            Dictionary with content formatted for different channels
        """
        # Extract key information
        incident_type = incident["incidentType"]
        incident_subtype = incident.get("incidentSubType", "")
        description = incident["details"].get("description", "")
        location_address = incident["location"]["address"].get("fullAddress", "Unknown location")
        
        # Create notification summary
        summary = f"{incident_type}{': ' + incident_subtype if incident_subtype else ''}"
        
        # Format recommended actions as a single string
        action_required = ""
        if recommended_actions:
            action_required = "; ".join(recommended_actions)
        else:
            action_required = "Please remain aware of your surroundings"
        
        # Create a short unique ID for the incident
        short_id = incident["incidentID"][-6:]
        
        # Format for different channels
        return {
            "summary": summary,
            "description": description,
            "location": location_address,
            "incident_type": incident_type,
            "action_required": action_required,
            "details_url": f"https://alerts.ucsd.edu/details/{short_id}",
            "severity": self._map_priority_to_severity(incident["priority"])
        }
    
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
    
    def _create_notification_plan(self, 
                                 recipients: List[Dict[str, Any]],
                                 content: Dict[str, str],
                                 priority: int) -> List[Dict[str, Any]]:
        """
        Create a notification plan for each recipient.
        
        Args:
            recipients: List of recipients to notify with metadata
            content: Notification content
            priority: Priority level (1-5)
            
        Returns:
            List of notifications to send
        """
        notifications = []
        
        for recipient_data in recipients:
            recipient = recipient_data["recipient"]
            
            # Get preferred channels
            preferred_channels = recipient.notification_preferences.get("channels", [])
            
            # Determine appropriate channels based on priority
            channels_to_use = []
            
            # For highest priority (1), use all available channels
            if priority == 1:
                # Use all preferred channels
                channels_to_use = preferred_channels
                
            # For high priority (2), use at least the two highest priority channels
            elif priority == 2:
                # Get the two highest priority channels that the recipient prefers
                high_priority_channels = []
                for channel in sorted(self.notification_channels, key=lambda c: c.priority):
                    if channel.id in preferred_channels:
                        high_priority_channels.append(channel.id)
                    if len(high_priority_channels) >= 2:
                        break
                        
                channels_to_use = high_priority_channels
                
            # For medium priority (3), use the highest priority channel
            elif priority == 3:
                # Get the highest priority channel that the recipient prefers
                for channel in sorted(self.notification_channels, key=lambda c: c.priority):
                    if channel.id in preferred_channels:
                        channels_to_use = [channel.id]
                        break
                        
            # For low priority (4-5), use a single non-intrusive channel
            else:
                # Prefer email or app_push over more intrusive channels
                if "email" in preferred_channels:
                    channels_to_use = ["email"]
                elif "app_push" in preferred_channels:
                    channels_to_use = ["app_push"]
                elif preferred_channels:
                    channels_to_use = [preferred_channels[0]]
            
            # Create a notification for each channel
            for channel_id in channels_to_use:
                # Find the channel object
                channel = next((c for c in self.notification_channels if c.id == channel_id), None)
                if not channel:
                    continue
                    
                # Check rate limiting
                last_notified = self.notification_history.get(f"{recipient.id}:{channel_id}", 0)
                current_time = time.time()
                
                if current_time - last_notified < channel.rate_limit:
                    # Skip if within rate limit period
                    continue
                    
                # Format message for this channel
                try:
                    message = channel.template.format(**content)
                except KeyError:
                    # Fallback if template has missing keys
                    message = f"ALERT: {content['incident_type']} at {content['location']}. {content['action_required']}"
                
                # Add to notification list
                notifications.append({
                    "recipient_id": recipient.id,
                    "recipient_name": recipient.name,
                    "channel": channel_id,
                    "message": message,
                    "priority": priority,
                    "timestamp": datetime.datetime.now().isoformat()
                })
                
                # Update notification history for rate limiting
                self.notification_history[f"{recipient.id}:{channel_id}"] = current_time
        
        return notifications


# Example usage
if __name__ == "__main__":
    # Create a sample EIDO
    sample_eido = {
        "eido": {
            "eidoVersion": "1.0",
            "eidoType": "incident",
            "eidoID": "12345",
            "timestamp": datetime.datetime.now().isoformat(),
            "incident": {
                "incidentID": "12345",
                "incidentType": "fire",
                "incidentSubType": "building",
                "priority": 2,
                "status": "active",
                "createdAt": datetime.datetime.now().isoformat(),
                "reportingParty": {
                    "role": "staff",
                    "name": "John Doe"
                },
                "location": {
                    "address": {
                        "fullAddress": "Warren College, UC San Diego",
                        "additionalInfo": "3rd floor"
                    },
                    "coordinates": {
                        "latitude": 32.8815,
                        "longitude": -117.2350
                    }
                },
                "details": {
                    "description": "Fire reported in kitchen of Warren College residence hall.",
                    "timeline": [
                        {
                            "timestamp": datetime.datetime.now().isoformat(),
                            "action": "Incident reported",
                            "notes": "Initial report received"
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
                    "keyFacts": [
                        "Fire started in kitchen",
                        "Building evacuation in progress",
                        "No injuries reported"
                    ]
                }
            },
            "notification": {
                "recommendedActions": [
                    "Evacuate the building",
                    "Dispatch fire department"
                ],
                "recommendedNotificationScope": {
                    "geographic": "affected_buildings",
                    "population": ["students", "building_managers"],
                    "radius_meters": 200,
                    "notify_authorities": True
                }
            }
        }
    }
    
    notifier = SafeCampusNotifier()
    notification_results = notifier.process_eido(sample_eido)
    
    print(json.dumps(notification_results, indent=2))