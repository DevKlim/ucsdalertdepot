"""
channels.py

This module defines the notification channels used by the Safe Campus Agent.
Each channel represents a different method for delivering emergency notifications.
"""

from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Union, Callable
import json
import os
import logging
import time
import datetime
import requests
from enum import Enum

logger = logging.getLogger(__name__)

class DeliveryStatus(Enum):
    """Enum for notification delivery status."""
    PENDING = "pending"
    SENT = "sent"
    DELIVERED = "delivered"
    FAILED = "failed"
    RATE_LIMITED = "rate_limited"

@dataclass
class NotificationChannel:
    """Base class for notification channels."""
    id: str
    name: str
    priority: int  # 1-5, where 1 is highest priority
    rate_limit: int  # in seconds, minimum time between notifications
    
    def format_message(self, template: str, content: Dict[str, str]) -> str:
        """
        Format a message using the template and content.
        
        Args:
            template: The message template with placeholders
            content: Dictionary with values for placeholders
            
        Returns:
            Formatted message string
        """
        try:
            return template.format(**content)
        except KeyError as e:
            logger.warning(f"Missing key in template: {e}")
            # Fallback if template has missing keys
            return f"ALERT: {content.get('incident_type', 'Emergency')} at {content.get('location', 'campus')}. {content.get('action_required', 'Stay alert.')}."
    
    def send(self, recipient: Dict[str, Any], message: str) -> Dict[str, Any]:
        """
        Send a notification to a recipient.
        Must be implemented by subclasses.
        
        Args:
            recipient: Recipient information
            message: Formatted message to send
            
        Returns:
            Dictionary with result information
        """
        raise NotImplementedError("Subclasses must implement send method")


@dataclass
class SMSChannel(NotificationChannel):
    """SMS text message notification channel."""
    
    # Additional SMS-specific configuration
    api_key: Optional[str] = None
    api_endpoint: str = "https://api.example.com/sms"  # Placeholder API endpoint
    
    def __post_init__(self):
        """Initialize SMS channel with API key."""
        if not self.api_key:
            # Try to get API key from environment variable
            self.api_key = os.environ.get("SMS_API_KEY")
    
    def send(self, recipient: Dict[str, Any], message: str) -> Dict[str, Any]:
        """
        Send an SMS notification.
        
        Args:
            recipient: Recipient information
            message: Formatted message to send
            
        Returns:
            Dictionary with result information
        """
        phone_number = recipient.get("phone_number")
        if not phone_number:
            return {
                "status": DeliveryStatus.FAILED.value,
                "timestamp": datetime.datetime.now().isoformat(),
                "error": "No phone number provided"
            }
        
        # In a real implementation, this would call an SMS service API
        # For the demo, we'll simulate sending
        logger.info(f"Sending SMS to {phone_number}: {message}")
        
        # Simulate API call in demo
        if not self.api_key:
            logger.warning("No SMS API key available. Message not sent.")
            return {
                "status": DeliveryStatus.FAILED.value,
                "timestamp": datetime.datetime.now().isoformat(),
                "error": "No API key configured"
            }
        
        # In a real implementation, we would do something like:
        # try:
        #     response = requests.post(
        #         self.api_endpoint,
        #         json={
        #             "to": phone_number,
        #             "body": message
        #         },
        #         headers={"Authorization": f"Bearer {self.api_key}"}
        #     )
        #     response.raise_for_status()
        #     return {
        #         "status": DeliveryStatus.SENT.value,
        #         "timestamp": datetime.datetime.now().isoformat(),
        #         "message_id": response.json().get("message_id")
        #     }
        # except Exception as e:
        #     logger.error(f"Error sending SMS: {e}")
        #     return {
        #         "status": DeliveryStatus.FAILED.value,
        #         "timestamp": datetime.datetime.now().isoformat(),
        #         "error": str(e)
        #     }
        
        # For demo purposes, simulate successful sending
        time.sleep(0.1)  # Simulate API latency
        return {
            "status": DeliveryStatus.SENT.value,
            "timestamp": datetime.datetime.now().isoformat(),
            "message_id": f"sms_{int(time.time())}_{hash(phone_number) % 10000}"
        }


@dataclass
class EmailChannel(NotificationChannel):
    """Email notification channel."""
    
    smtp_host: str = "smtp.example.com"  # Placeholder SMTP server
    smtp_port: int = 587
    smtp_username: Optional[str] = None
    smtp_password: Optional[str] = None
    sender_email: str = "alerts@ucsd.edu"
    
    def __post_init__(self):
        """Initialize email channel with credentials."""
        if not self.smtp_username:
            self.smtp_username = os.environ.get("SMTP_USERNAME")
        if not self.smtp_password:
            self.smtp_password = os.environ.get("SMTP_PASSWORD")
    
    def send(self, recipient: Dict[str, Any], message: str) -> Dict[str, Any]:
        """
        Send an email notification.
        
        Args:
            recipient: Recipient information
            message: Formatted message to send
            
        Returns:
            Dictionary with result information
        """
        email = recipient.get("email")
        if not email:
            return {
                "status": DeliveryStatus.FAILED.value,
                "timestamp": datetime.datetime.now().isoformat(),
                "error": "No email address provided"
            }
        
        # In a real implementation, this would use smtplib to send an email
        # For the demo, we'll simulate sending
        logger.info(f"Sending email to {email}: {message[:100]}...")
        
        # Simulate email sending in demo
        if not (self.smtp_username and self.smtp_password):
            logger.warning("No email credentials available. Message not sent.")
            return {
                "status": DeliveryStatus.FAILED.value,
                "timestamp": datetime.datetime.now().isoformat(),
                "error": "No email credentials configured"
            }
        
        # In a real implementation, we would use smtplib to send the email
        time.sleep(0.2)  # Simulate sending latency
        return {
            "status": DeliveryStatus.SENT.value,
            "timestamp": datetime.datetime.now().isoformat(),
            "message_id": f"email_{int(time.time())}_{hash(email) % 10000}"
        }


@dataclass
class AppPushChannel(NotificationChannel):
    """Mobile app push notification channel."""
    
    api_endpoint: str = "https://api.example.com/push"  # Placeholder API endpoint
    api_key: Optional[str] = None
    
    def __post_init__(self):
        """Initialize push notification channel with API key."""
        if not self.api_key:
            self.api_key = os.environ.get("PUSH_API_KEY")
    
    def send(self, recipient: Dict[str, Any], message: str) -> Dict[str, Any]:
        """
        Send a push notification.
        
        Args:
            recipient: Recipient information
            message: Formatted message to send
            
        Returns:
            Dictionary with result information
        """
        device_token = recipient.get("device_token")
        if not device_token:
            return {
                "status": DeliveryStatus.FAILED.value,
                "timestamp": datetime.datetime.now().isoformat(),
                "error": "No device token provided"
            }
        
        # In a real implementation, this would call a push notification API
        logger.info(f"Sending push notification to {device_token[:10]}...: {message[:50]}...")
        
        # Simulate API call
        time.sleep(0.1)
        return {
            "status": DeliveryStatus.SENT.value,
            "timestamp": datetime.datetime.now().isoformat(),
            "message_id": f"push_{int(time.time())}_{hash(device_token) % 10000}"
        }


@dataclass
class PhoneCallChannel(NotificationChannel):
    """Automated phone call notification channel."""
    
    api_endpoint: str = "https://api.example.com/calls"  # Placeholder API endpoint
    api_key: Optional[str] = None
    voice_type: str = "female"  # Voice type for text-to-speech
    
    def __post_init__(self):
        """Initialize phone call channel with API key."""
        if not self.api_key:
            self.api_key = os.environ.get("CALL_API_KEY")
    
    def send(self, recipient: Dict[str, Any], message: str) -> Dict[str, Any]:
        """
        Send an automated phone call notification.
        
        Args:
            recipient: Recipient information
            message: Formatted message to send
            
        Returns:
            Dictionary with result information
        """
        phone_number = recipient.get("phone_number")
        if not phone_number:
            return {
                "status": DeliveryStatus.FAILED.value,
                "timestamp": datetime.datetime.now().isoformat(),
                "error": "No phone number provided"
            }
        
        # In a real implementation, this would call a telephony API
        logger.info(f"Initiating automated call to {phone_number}: {message[:100]}...")
        
        # Simulate API call
        time.sleep(0.3)  # Calls take longer to set up
        return {
            "status": DeliveryStatus.SENT.value,
            "timestamp": datetime.datetime.now().isoformat(),
            "call_id": f"call_{int(time.time())}_{hash(phone_number) % 10000}"
        }


@dataclass
class RadioChannel(NotificationChannel):
    """Campus radio system notification channel for emergency responders."""
    
    radio_system: str = "campus_radio"
    dispatch_endpoint: str = "https://api.example.com/radio/dispatch"
    api_key: Optional[str] = None
    
    def __post_init__(self):
        """Initialize radio channel with API key."""
        if not self.api_key:
            self.api_key = os.environ.get("RADIO_API_KEY")
    
    def send(self, recipient: Dict[str, Any], message: str) -> Dict[str, Any]:
        """
        Send a radio dispatch notification.
        
        Args:
            recipient: Recipient information
            message: Formatted message to send
            
        Returns:
            Dictionary with result information
        """
        radio_id = recipient.get("radio_id")
        if not radio_id:
            return {
                "status": DeliveryStatus.FAILED.value,
                "timestamp": datetime.datetime.now().isoformat(),
                "error": "No radio ID provided"
            }
        
        # In a real implementation, this would call a radio dispatch API
        logger.info(f"Sending radio dispatch to {radio_id}: {message}")
        
        # Simulate API call
        time.sleep(0.1)
        return {
            "status": DeliveryStatus.SENT.value,
            "timestamp": datetime.datetime.now().isoformat(),
            "dispatch_id": f"radio_{int(time.time())}_{hash(radio_id) % 10000}"
        }


@dataclass
class DigitalSignageChannel(NotificationChannel):
    """Campus digital signage notification channel."""
    
    api_endpoint: str = "https://api.example.com/signs"
    api_key: Optional[str] = None
    
    def __post_init__(self):
        """Initialize digital signage channel with API key."""
        if not self.api_key:
            self.api_key = os.environ.get("SIGNAGE_API_KEY")
    
    def send(self, location: Dict[str, Any], message: str) -> Dict[str, Any]:
        """
        Send a notification to digital signs in a location.
        
        Args:
            location: Location information (building, area, etc.)
            message: Formatted message to display
            
        Returns:
            Dictionary with result information
        """
        area_id = location.get("area_id")
        if not area_id:
            return {
                "status": DeliveryStatus.FAILED.value,
                "timestamp": datetime.datetime.now().isoformat(),
                "error": "No area ID provided"
            }
        
        # In a real implementation, this would call a digital signage API
        logger.info(f"Displaying message on digital signs in area {area_id}: {message}")
        
        # Simulate API call
        time.sleep(0.2)
        return {
            "status": DeliveryStatus.SENT.value,
            "timestamp": datetime.datetime.now().isoformat(),
            "display_id": f"sign_{int(time.time())}_{hash(area_id) % 10000}"
        }


class ChannelManager:
    """
    Manages notification channels and handles selection and sending.
    """
    
    def __init__(self):
        """Initialize the channel manager with default channels."""
        self.channels = self._create_default_channels()
        self.rate_limit_records = {}  # Track when a recipient was last notified on each channel
    
    def _create_default_channels(self) -> Dict[str, NotificationChannel]:
        """Create default notification channels."""
        return {
            "sms": SMSChannel(
                id="sms",
                name="SMS Text Message",
                priority=1,  # High priority
                rate_limit=300  # 5 minutes
            ),
            "email": EmailChannel(
                id="email",
                name="Email Notification",
                priority=3,  # Medium priority
                rate_limit=600  # 10 minutes
            ),
            "app_push": AppPushChannel(
                id="app_push",
                name="Mobile App Push Notification",
                priority=2,  # High priority
                rate_limit=60  # 1 minute
            ),
            "phone": PhoneCallChannel(
                id="phone",
                name="Automated Phone Call",
                priority=1,  # Highest priority
                rate_limit=1800  # 30 minutes
            ),
            "radio": RadioChannel(
                id="radio",
                name="Radio System",
                priority=1,  # Highest priority
                rate_limit=120  # 2 minutes
            ),
            "digital_signage": DigitalSignageChannel(
                id="digital_signage",
                name="Digital Signage",
                priority=2,  # High priority
                rate_limit=300  # 5 minutes
            )
        }
    
    def get_channel(self, channel_id: str) -> Optional[NotificationChannel]:
        """Get a channel by ID."""
        return self.channels.get(channel_id)
    
    def get_all_channels(self) -> List[NotificationChannel]:
        """Get all channels."""
        return list(self.channels.values())
    
    def get_highest_priority_channels(self, count: int = 1) -> List[NotificationChannel]:
        """
        Get the highest priority channels.
        
        Args:
            count: Number of channels to return
            
        Returns:
            List of highest priority channels
        """
        return sorted(self.channels.values(), key=lambda c: c.priority)[:count]
    
    def check_rate_limit(self, recipient_id: str, channel_id: str) -> bool:
        """
        Check if a recipient is rate-limited on a channel.
        
        Args:
            recipient_id: Recipient ID
            channel_id: Channel ID
            
        Returns:
            True if rate-limited, False otherwise
        """
        channel = self.get_channel(channel_id)
        if not channel:
            return False
        
        key = f"{recipient_id}:{channel_id}"
        last_time = self.rate_limit_records.get(key, 0)
        current_time = time.time()
        
        return (current_time - last_time) < channel.rate_limit
    
    def record_notification(self, recipient_id: str, channel_id: str) -> None:
        """
        Record that a notification was sent to a recipient on a channel.
        
        Args:
            recipient_id: Recipient ID
            channel_id: Channel ID
        """
        key = f"{recipient_id}:{channel_id}"
        self.rate_limit_records[key] = time.time()
    
    def send_notification(
        self,
        recipient: Dict[str, Any],
        content: Dict[str, str],
        template: str,
        channel_id: str
    ) -> Dict[str, Any]:
        """
        Send a notification to a recipient on a channel.
        
        Args:
            recipient: Recipient information
            content: Dictionary with content for the template
            template: Message template
            channel_id: Channel ID
            
        Returns:
            Dictionary with result information
        """
        channel = self.get_channel(channel_id)
        if not channel:
            return {
                "status": DeliveryStatus.FAILED.value,
                "timestamp": datetime.datetime.now().isoformat(),
                "error": f"Unknown channel: {channel_id}"
            }
        
        # Check rate limit
        if self.check_rate_limit(recipient["id"], channel_id):
            return {
                "status": DeliveryStatus.RATE_LIMITED.value,
                "timestamp": datetime.datetime.now().isoformat(),
                "error": "Rate limited"
            }
        
        # Format the message
        message = channel.format_message(template, content)
        
        # Send the notification
        result = channel.send(recipient, message)
        
        # Record the notification for rate limiting
        if result["status"] == DeliveryStatus.SENT.value:
            self.record_notification(recipient["id"], channel_id)
        
        return result


# Example usage
if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(level=logging.INFO)
    
    # Create a channel manager
    manager = ChannelManager()
    
    # Create a sample recipient
    recipient = {
        "id": "r001",
        "name": "John Doe",
        "email": "john.doe@example.com",
        "phone_number": "+1234567890",
        "device_token": "abcdef123456"
    }
    
    # Create sample content
    content = {
        "incident_type": "Fire",
        "location": "Geisel Library, 2nd Floor",
        "description": "Small fire in study room",
        "action_required": "Evacuate the building immediately"
    }
    
    # Send test notifications
    for channel_id in ["sms", "email", "app_push"]:
        template = "{incident_type} alert at {location}. {action_required}"
        result = manager.send_notification(recipient, content, template, channel_id)
        print(f"Notification sent via {channel_id}: {result}")