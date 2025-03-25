Safe Campus Agent
The Safe Campus Agent is an intelligent emergency notification system that uses agentic AI to process 911 calls and incident reports into the NENA EIDO (Emergency Incident Data Object) format, enabling sophisticated context-aware notification decisions.
Project Overview
This project represents a shift from traditional passive alert systems to an intelligent agent that can:

Process emergency calls and written reports through natural language understanding
Transform unstructured information into standardized EIDO objects
Make context-aware decisions about who to notify and through what channels
Provide continuous situational awareness as incidents evolve

Key Files and Directories
Core Components

app.py: Main Flask application that serves the demo interfaces
eido/: Emergency Incident Data Object processing

emergency_call_processor.py: Processes 911 calls into structured EIDO format
report_classifier.py: Classifies written incident reports
eido_schema.py: Defines the EIDO format and validation
location_extractor.py: Extracts location information from text


notification/: Alert notification system

notifier.py: Determines who to notify based on incident context
recipients.py: Recipient data models and management
channels.py: Communication channel definitions
templates.py: Notification templates for different channels


geocoding/: Location processing

geocode.py: Core geocoding functions
locations.py: Campus location database
providers/: Multiple geocoding providers



Data Files

data/examples/: Contains sample data for demo purposes

emergency_calls/: Sample emergency call transcripts
incident_reports/: Sample incident reports


data/locations/: Campus location information

campus_buildings.json: Building information with coordinates
known_locations.json: Database of geocoded locations



Web Interface

templates/: HTML templates for the web interface

index.html: Main dashboard
emergency-demo.html: Emergency call processing demo
report-demo.html: Report classification demo


static/: Web assets (JS, CSS, images)

Documentation

docs/: Project documentation

api.md: API documentation
eido-format.md: EIDO format specification
use-cases.md: Use case examples
architecture.md: System architecture



How It Works
Demo 1: Emergency Call Processing

Input: A 911 call transcript is provided
Processing: The emergency call processor uses an LLM to extract key information
Standardization: The information is formatted as an EIDO object
Notification: The notifier determines who to alert based on the incident context
Output: A notification plan is generated showing who would be alerted and through what channels

Demo 2: Report Classification

Input: A written incident report is provided
Classification: The report classifier analyzes the text to extract key information
Conversion: The classification is converted to an EIDO object
Notification: The notifier determines who to alert based on the incident context
Output: A notification plan is generated showing who would be alerted and through what channels

Technical Implementation

LLM Integration: Uses Mistral AI for natural language understanding
EIDO Standard: Follows NENA's Emergency Incident Data Object format
Geocoding: Leverages existing geocoding expertise to locate incidents precisely
Intelligent Routing: Uses spatial awareness and context to determine notification scope
Multi-Channel Delivery: Supports SMS, email, app notifications, and more

Project Value
This project addresses critical challenges in campus safety:

Speed: Automates the processing of emergency information for faster response
Accuracy: Standardizes information to reduce miscommunication
Context-Awareness: Makes notification decisions based on incident context
Personalization: Delivers alerts through appropriate channels based on recipient preferences
Continuity: Provides a framework for continuous updates as incidents evolve

Future Directions

Real-time Audio Processing: Direct processing of 911 call audio
Integration with Campus Systems: Connection to existing alert systems
Machine Learning Enhancements: Improving notification decisions with historical data
Mobile App Integration: Providing location-aware alerts to campus community
Expanded Notification Channels: Adding digital signage, PA systems, etc.

Setup and Usage
See the installation and usage instructions in the project's main README.md file.
Acknowledgements
This project builds on the foundations of:

NENA (National Emergency Number Association) EIDO standards
UC San Diego's campus safety initiatives
Original UCSD Crime Map project for geocoding expertise