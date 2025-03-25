"""
recipients.py

This module manages recipients and recipient groups for the notification system.
It defines data models and functions for working with notification recipients.
"""

from dataclasses import dataclass, field, asdict
from typing import Dict, Any, List, Optional, Set, Tuple
import json
import os
import logging
import time
import datetime
import math
import uuid

logger = logging.getLogger(__name__)

@dataclass
class NotificationPreferences:
    """Recipient notification preferences."""
    channels: List[str] = field(default_factory=lambda: ["email", "app_push"])
    severity_threshold: str = "medium"  # low, medium, high, critical
    quiet_hours_start: Optional[int] = None  # Hour of day (0-23)
    quiet_hours_end: Optional[int] = None
    opt_out_categories: List[str] = field(default_factory=list)
    language: str = "en"
    format_preferences: Dict[str, Any] = field(default_factory=dict)


@dataclass
class Recipient:
    """
    Represents a notification recipient.
    """
    id: str
    name: str
    role: str  # student, faculty, staff, emergency_responder, etc.
    groups: List[str] = field(default_factory=list)
    email: Optional[str] = None
    phone_number: Optional[str] = None
    device_token: Optional[str] = None  # For push notifications
    radio_id: Optional[str] = None  # For radio notifications
    location: Dict[str, float] = field(default_factory=lambda: {"latitude": 0, "longitude": 0})
    notification_preferences: NotificationPreferences = field(default_factory=NotificationPreferences)
    metadata: Dict[str, Any] = field(default_factory=dict)
    active: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Recipient':
        """Create a recipient from a dictionary."""
        # Handle nested NotificationPreferences
        preferences_data = data.pop("notification_preferences", {})
        preferences = NotificationPreferences(**preferences_data)
        
        return cls(
            **{k: v for k, v in data.items() if k != "notification_preferences"},
            notification_preferences=preferences
        )
    
    def is_in_group(self, group: str) -> bool:
        """Check if recipient is in a group."""
        return group in self.groups
    
    def meets_severity_threshold(self, severity: str) -> bool:
        """
        Check if a severity level meets the recipient's threshold.
        
        Args:
            severity: One of "low", "medium", "high", "critical"
            
        Returns:
            True if the severity meets or exceeds the threshold
        """
        severity_levels = ["low", "medium", "high", "critical"]
        try:
            threshold_idx = severity_levels.index(self.notification_preferences.severity_threshold.lower())
            severity_idx = severity_levels.index(severity.lower())
            return severity_idx >= threshold_idx
        except ValueError:
            # Default to showing medium and above if invalid values
            return severity.lower() in ["medium", "high", "critical"]
    
    def is_during_quiet_hours(self) -> bool:
        """
        Check if current time is during the recipient's quiet hours.
        
        Returns:
            True if current time is during quiet hours
        """
        start = self.notification_preferences.quiet_hours_start
        end = self.notification_preferences.quiet_hours_end
        
        if start is None or end is None:
            return False
            
        current_hour = datetime.datetime.now().hour
        
        if start <= end:
            # Normal range (e.g., 22-6)
            return start <= current_hour <= end
        else:
            # Overnight range (e.g., 22-6)
            return current_hour >= start or current_hour <= end
    
    def calculate_distance(self, lat: float, lng: float) -> float:
        """
        Calculate distance between recipient and a point in meters.
        
        Args:
            lat: Latitude of the point
            lng: Longitude of the point
            
        Returns:
            Distance in meters
        """
        # Earth radius in meters
        R = 6371000
        
        # Convert degrees to radians
        lat1_rad = math.radians(self.location["latitude"])
        lon1_rad = math.radians(self.location["longitude"])
        lat2_rad = math.radians(lat)
        lon2_rad = math.radians(lng)
        
        # Differences
        dlat = lat2_rad - lat1_rad
        dlon = lon2_rad - lon1_rad
        
        # Haversine formula
        a = math.sin(dlat/2)**2 + math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(dlon/2)**2
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1-a))
        distance = R * c
        
        return distance


@dataclass
class RecipientGroup:
    """
    Represents a group of recipients for notification targeting.
    """
    id: str
    name: str
    description: str
    members: List[str] = field(default_factory=list)  # List of recipient IDs
    parent_groups: List[str] = field(default_factory=list)  # List of parent group IDs
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RecipientGroup':
        """Create a group from a dictionary."""
        return cls(**data)
    
    def add_member(self, recipient_id: str) -> None:
        """Add a recipient to the group."""
        if recipient_id not in self.members:
            self.members.append(recipient_id)
    
    def remove_member(self, recipient_id: str) -> None:
        """Remove a recipient from the group."""
        if recipient_id in self.members:
            self.members.remove(recipient_id)
    
    def is_member(self, recipient_id: str) -> bool:
        """Check if a recipient is a member of the group."""
        return recipient_id in self.members


class RecipientManager:
    """
    Manages recipients and recipient groups.
    """
    
    def __init__(self, storage_path: Optional[str] = None):
        """
        Initialize the recipient manager.
        
        Args:
            storage_path: Path to save recipient data (optional)
        """
        self.recipients: Dict[str, Recipient] = {}
        self.groups: Dict[str, RecipientGroup] = {}
        self.storage_path = storage_path
        
        # Load recipients and groups if path provided
        if storage_path:
            self._load_data()
    
    def add_recipient(self, recipient: Recipient) -> str:
        """
        Add a recipient to the manager.
        
        Args:
            recipient: The recipient to add
            
        Returns:
            The recipient ID
        """
        self.recipients[recipient.id] = recipient
        self._save_data()
        return recipient.id
    
    def get_recipient(self, recipient_id: str) -> Optional[Recipient]:
        """
        Get a recipient by ID.
        
        Args:
            recipient_id: The recipient ID
            
        Returns:
            The recipient, or None if not found
        """
        return self.recipients.get(recipient_id)
    
    def update_recipient(self, recipient_id: str, updates: Dict[str, Any]) -> Optional[Recipient]:
        """
        Update a recipient.
        
        Args:
            recipient_id: The recipient ID
            updates: Dictionary with fields to update
            
        Returns:
            The updated recipient, or None if not found
        """
        recipient = self.get_recipient(recipient_id)
        if not recipient:
            return None
            
        # Update each field
        for key, value in updates.items():
            if key == "notification_preferences":
                # Handle nested update of preferences
                for pref_key, pref_value in value.items():
                    setattr(recipient.notification_preferences, pref_key, pref_value)
            else:
                setattr(recipient, key, value)
        
        self._save_data()
        return recipient
    
    def delete_recipient(self, recipient_id: str) -> bool:
        """
        Delete a recipient.
        
        Args:
            recipient_id: The recipient ID
            
        Returns:
            True if deleted, False if not found
        """
        if recipient_id not in self.recipients:
            return False
            
        # Remove from all groups
        for group in self.groups.values():
            group.remove_member(recipient_id)
            
        # Delete the recipient
        del self.recipients[recipient_id]
        self._save_data()
        return True
    
    def add_group(self, group: RecipientGroup) -> str:
        """
        Add a group to the manager.
        
        Args:
            group: The group to add
            
        Returns:
            The group ID
        """
        self.groups[group.id] = group
        self._save_data()
        return group.id
    
    def get_group(self, group_id: str) -> Optional[RecipientGroup]:
        """
        Get a group by ID.
        
        Args:
            group_id: The group ID
            
        Returns:
            The group, or None if not found
        """
        return self.groups.get(group_id)
    
    def update_group(self, group_id: str, updates: Dict[str, Any]) -> Optional[RecipientGroup]:
        """
        Update a group.
        
        Args:
            group_id: The group ID
            updates: Dictionary with fields to update
            
        Returns:
            The updated group, or None if not found
        """
        group = self.get_group(group_id)
        if not group:
            return None
            
        # Update each field
        for key, value in updates.items():
            setattr(group, key, value)
        
        self._save_data()
        return group
    
    def delete_group(self, group_id: str) -> bool:
        """
        Delete a group.
        
        Args:
            group_id: The group ID
            
        Returns:
            True if deleted, False if not found
        """
        if group_id not in self.groups:
            return False
            
        # Delete the group
        del self.groups[group_id]
        
        # Remove from parent_groups lists in other groups
        for group in self.groups.values():
            if group_id in group.parent_groups:
                group.parent_groups.remove(group_id)
        
        self._save_data()
        return True
    
    def add_recipient_to_group(self, recipient_id: str, group_id: str) -> bool:
        """
        Add a recipient to a group.
        
        Args:
            recipient_id: The recipient ID
            group_id: The group ID
            
        Returns:
            True if added, False if recipient or group not found
        """
        recipient = self.get_recipient(recipient_id)
        group = self.get_group(group_id)
        
        if not recipient or not group:
            return False
            
        group.add_member(recipient_id)
        self._save_data()
        return True
    
    def remove_recipient_from_group(self, recipient_id: str, group_id: str) -> bool:
        """
        Remove a recipient from a group.
        
        Args:
            recipient_id: The recipient ID
            group_id: The group ID
            
        Returns:
            True if removed, False if recipient or group not found
        """
        recipient = self.get_recipient(recipient_id)
        group = self.get_group(group_id)
        
        if not recipient or not group:
            return False
            
        group.remove_member(recipient_id)
        self._save_data()
        return True
    
    def find_recipients_by_group(self, group_id: str) -> List[Recipient]:
        """
        Get all recipients in a group.
        
        Args:
            group_id: The group ID
            
        Returns:
            List of recipients in the group
        """
        group = self.get_group(group_id)
        if not group:
            return []
            
        return [self.recipients[r_id] for r_id in group.members if r_id in self.recipients]
    
    def find_recipients_by_groups(self, group_ids: List[str]) -> List[Recipient]:
        """
        Get all recipients in any of the specified groups.
        
        Args:
            group_ids: List of group IDs
            
        Returns:
            List of recipients in any of the groups
        """
        recipients_set = set()
        
        for group_id in group_ids:
            group = self.get_group(group_id)
            if group:
                recipients_set.update(group.members)
        
        return [self.recipients[r_id] for r_id in recipients_set if r_id in self.recipients]
    
    def find_recipients_in_radius(self, lat: float, lng: float, radius_meters: float) -> List[Tuple[Recipient, float]]:
        """
        Find recipients within a radius of a point.
        
        Args:
            lat: Latitude of the center point
            lng: Longitude of the center point
            radius_meters: Radius in meters
            
        Returns:
            List of (recipient, distance) tuples for recipients within the radius
        """
        results = []
        
        for recipient in self.recipients.values():
            distance = recipient.calculate_distance(lat, lng)
            if distance <= radius_meters:
                results.append((recipient, distance))
        
        # Sort by distance
        return sorted(results, key=lambda x: x[1])
    
    def find_recipients_by_role(self, role: str) -> List[Recipient]:
        """
        Find recipients by role.
        
        Args:
            role: The role to search for
            
        Returns:
            List of recipients with the specified role
        """
        return [r for r in self.recipients.values() if r.role == role]
    
    def _save_data(self) -> None:
        """Save recipient and group data to storage."""
        if not self.storage_path:
            return
            
        try:
            data = {
                "recipients": {r_id: recipient.to_dict() for r_id, recipient in self.recipients.items()},
                "groups": {g_id: group.to_dict() for g_id, group in self.groups.items()}
            }
            
            os.makedirs(os.path.dirname(self.storage_path), exist_ok=True)
            
            with open(self.storage_path, 'w') as f:
                json.dump(data, f, indent=2)
                
            logger.info(f"Saved recipient data to {self.storage_path}")
        except Exception as e:
            logger.error(f"Error saving recipient data: {e}")
    
    def _load_data(self) -> None:
        """Load recipient and group data from storage."""
        if not self.storage_path or not os.path.exists(self.storage_path):
            # Create sample data if no file exists
            self._create_sample_data()
            return
            
        try:
            with open(self.storage_path, 'r') as f:
                data = json.load(f)
                
            # Load recipients
            self.recipients = {
                r_id: Recipient.from_dict(r_data)
                for r_id, r_data in data.get("recipients", {}).items()
            }
            
            # Load groups
            self.groups = {
                g_id: RecipientGroup.from_dict(g_data)
                for g_id, g_data in data.get("groups", {}).items()
            }
            
            logger.info(f"Loaded {len(self.recipients)} recipients and {len(self.groups)} groups from {self.storage_path}")
        except Exception as e:
            logger.error(f"Error loading recipient data: {e}")
            # Create sample data as fallback
            self._create_sample_data()
    
    def _create_sample_data(self) -> None:
        """Create sample recipient and group data for demo purposes."""
        # Create sample groups
        groups = [
            RecipientGroup(
                id="g001",
                name="Emergency Responders",
                description="Campus emergency response personnel",
                members=[]
            ),
            RecipientGroup(
                id="g002",
                name="Campus Leadership",
                description="University leadership team",
                members=[]
            ),
            RecipientGroup(
                id="g003",
                name="Students",
                description="All enrolled students",
                members=[]
            ),
            RecipientGroup(
                id="g004",
                name="Faculty",
                description="All faculty members",
                members=[]
            ),
            RecipientGroup(
                id="g005",
                name="Staff",
                description="All staff members",
                members=[]
            ),
            RecipientGroup(
                id="g006",
                name="Facilities",
                description="Facilities and maintenance personnel",
                members=[]
            )
        ]
        
        # Add groups to manager
        for group in groups:
            self.groups[group.id] = group
        
        # Create sample recipients
        recipients = [
            # Emergency responders
            Recipient(
                id="r001",
                name="Chief Roberts",
                role="campus_police_chief",
                groups=["g001", "g002"],
                email="chief.roberts@ucsd.edu",
                phone_number="+15551234567",
                device_token="device_token_001",
                radio_id="radio_001",
                location={"latitude": 32.8801, "longitude": -117.2340},
                notification_preferences=NotificationPreferences(
                    channels=["sms", "phone", "radio", "email", "app_push"],
                    severity_threshold="low"  # Receive all notifications
                )
            ),
            Recipient(
                id="r002",
                name="Officer Garcia",
                role="campus_police",
                groups=["g001"],
                email="officer.garcia@ucsd.edu",
                phone_number="+15551234568",
                device_token="device_token_002",
                radio_id="radio_002",
                location={"latitude": 32.8795, "longitude": -117.2360},
                notification_preferences=NotificationPreferences(
                    channels=["radio", "app_push", "sms"],
                    severity_threshold="low"
                )
            ),
            
            # Leadership
            Recipient(
                id="r003",
                name="Dr. Chen",
                role="dean",
                groups=["g002", "g004"],
                email="dean.chen@ucsd.edu",
                phone_number="+15551234569",
                device_token="device_token_003",
                location={"latitude": 32.8785, "longitude": -117.2330},
                notification_preferences=NotificationPreferences(
                    channels=["email", "app_push", "sms"],
                    severity_threshold="medium"
                )
            ),
            
            # Facilities
            Recipient(
                id="r004",
                name="Maintenance Team",
                role="facilities",
                groups=["g005", "g006"],
                email="maintenance@ucsd.edu",
                phone_number="+15551234570",
                device_token="device_token_004",
                radio_id="radio_003",
                location={"latitude": 32.8788, "longitude": -117.2410},
                notification_preferences=NotificationPreferences(
                    channels=["radio", "sms"],
                    severity_threshold="low"
                )
            ),
            
            # Students - varied locations across campus
            Recipient(
                id="r005",
                name="Alex Smith",
                role="student",
                groups=["g003"],
                email="alex.smith@ucsd.edu",
                phone_number="+15551234571",
                device_token="device_token_005",
                location={"latitude": 32.8782, "longitude": -117.2392},  # Pepper Canyon
                notification_preferences=NotificationPreferences(
                    channels=["app_push", "email"],
                    severity_threshold="medium"
                )
            ),
            Recipient(
                id="r006",
                name="Jordan Lee",
                role="student",
                groups=["g003"],
                email="jordan.lee@ucsd.edu",
                phone_number="+15551234572",
                device_token="device_token_006",
                location={"latitude": 32.8810, "longitude": -117.2380},  # Library
                notification_preferences=NotificationPreferences(
                    channels=["app_push", "sms"],
                    severity_threshold="medium",
                    quiet_hours_start=23,
                    quiet_hours_end=7
                )
            ),
            
            # Faculty
            Recipient(
                id="r007",
                name="Prof. Taylor",
                role="faculty",
                groups=["g004"],
                email="prof.taylor@ucsd.edu",
                phone_number="+15551234573",
                device_token="device_token_007",
                location={"latitude": 32.8800, "longitude": -117.2355},  # Faculty building
                notification_preferences=NotificationPreferences(
                    channels=["email", "app_push", "sms"],
                    severity_threshold="medium"
                )
            )
        ]
        
        # Add recipients to manager
        for recipient in recipients:
            self.recipients[recipient.id] = recipient
            
            # Add to groups
            for group_id in recipient.groups:
                if group_id in self.groups:
                    self.groups[group_id].add_member(recipient.id)
        
        logger.info(f"Created {len(self.recipients)} sample recipients and {len(self.groups)} sample groups")
        
        # Save the data
        self._save_data()
    
    def get_all_recipients(self) -> List[Recipient]:
        """Get all recipients."""
        return list(self.recipients.values())
    
    def get_all_groups(self) -> List[RecipientGroup]:
        """Get all groups."""
        return list(self.groups.values())
    
    def create_recipient(self, data: Dict[str, Any]) -> Recipient:
        """
        Create a new recipient from data.
        
        Args:
            data: Dictionary with recipient data
            
        Returns:
            The created recipient
        """
        # Generate ID if not provided
        if "id" not in data:
            data["id"] = f"r{str(uuid.uuid4())[:8]}"
            
        # Create recipient
        recipient = Recipient.from_dict(data)
        
        # Add to manager
        self.add_recipient(recipient)
        
        # Add to groups
        for group_id in recipient.groups:
            if group_id in self.groups:
                self.groups[group_id].add_member(recipient.id)
        
        return recipient
    
    def create_group(self, data: Dict[str, Any]) -> RecipientGroup:
        """
        Create a new group from data.
        
        Args:
            data: Dictionary with group data
            
        Returns:
            The created group
        """
        # Generate ID if not provided
        if "id" not in data:
            data["id"] = f"g{str(uuid.uuid4())[:8]}"
            
        # Create group
        group = RecipientGroup.from_dict(data)
        
        # Add to manager
        self.add_group(group)
        
        return group


# Example usage
if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Create recipient manager
    manager = RecipientManager(storage_path="data/recipients.json")
    
    # Print summary
    print(f"Loaded {len(manager.get_all_recipients())} recipients and {len(manager.get_all_groups())} groups")
    
    # Test finding recipients within radius
    test_point = (32.8801, -117.2340)  # Campus center
    radius = 300  # meters
    
    nearby = manager.find_recipients_in_radius(test_point[0], test_point[1], radius)
    print(f"Found {len(nearby)} recipients within {radius}m of test point:")
    
    for recipient, distance in nearby:
        print(f"- {recipient.name} ({recipient.role}): {distance:.1f}m")