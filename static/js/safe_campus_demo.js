import React, { useState, useEffect } from 'react';

const SafeCampusDemo = () => {
  const [transcript, setTranscript] = useState('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState(null);
  const [activeTab, setActiveTab] = useState('summary');
  const [location, setLocation] = useState({ lat: 32.8801, lng: -117.2340 });
  const [mapLoaded, setMapLoaded] = useState(false);
  const [llmClassification, setLlmClassification] = useState(null);
  const [viewMode, setViewMode] = useState('transcript'); // transcript or conversation
  const [demoMode, setDemoMode] = useState('call'); // call or report

  // Sample transcript for 911 call
  const sampleTranscript = `Dispatcher: 911, what's your emergency?

Caller: Hi, I'm at Geisel Library on campus, and there's someone acting very suspicious. They're walking around looking at people's belongings and trying doors to locked rooms.

Dispatcher: Can you describe this person?

Caller: Yes, it's a man wearing a black hoodie and jeans. He's about 6 feet tall with short dark hair. He keeps looking around nervously and checking if people are watching him.

Dispatcher: Where exactly are you seeing this?

Caller: I'm on the 2nd floor in the east wing. He's gone into the study rooms a few times, and I saw him try to open someone's backpack when they stepped away.

Dispatcher: Is he there right now?

Caller: Yes, he's still here walking around. He's now heading toward the elevator area.

Dispatcher: OK, I'm sending campus security. Are you in a safe location?

Caller: Yes, I'm sitting with a group of people. He's not paying attention to me.

Dispatcher: Good. What's your name?

Caller: Alex Chen. I'm a student here.

Dispatcher: OK Alex, officers are on the way. Stay where you are and call back if anything changes.`;

  // Sample written report
  const sampleReport = `Incident Report
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
Contact: 555-123-4567`;

  // Sample conversation format
  const sampleConversation = [
    { speaker: "Dispatcher", text: "911, what's your emergency?" },
    { speaker: "Caller", text: "I need to report a gas leak at the Warren College apartments. There's a really strong smell in the hallway of Building C." },
    { speaker: "Dispatcher", text: "Are people evacuating the building?" },
    { speaker: "Caller", text: "Some people have left, but I'm not sure everyone knows about it. The smell is really strong near apartment 305." },
    { speaker: "Dispatcher", text: "I'll dispatch emergency services right away. Are you in a safe location away from the smell?" },
    { speaker: "Caller", text: "Yes, I'm outside the building now." },
    { speaker: "Dispatcher", text: "Good. Can you tell me your name and contact information?" },
    { speaker: "Caller", text: "My name is Jamie Rodriguez. My phone number is 555-123-4567." },
    { speaker: "Dispatcher", text: "Thank you, Jamie. Emergency services are on their way. Please stay clear of the building and warn others not to enter." },
    { speaker: "Caller", text: "I will. Thank you." },
  ];

  const [conversation, setConversation] = useState(sampleConversation);
  const [newMessage, setNewMessage] = useState({ speaker: "Caller", text: "" });
  const [writtenReport, setWrittenReport] = useState(sampleReport);

  // Initialize map after component mounts
  useEffect(() => {
    if (results && !mapLoaded) {
      setMapLoaded(true);
    }
  }, [results, mapLoaded]);

  const loadSample = () => {
    if (demoMode === 'call') {
      if (viewMode === 'transcript') {
        setTranscript(sampleTranscript);
      } else {
        setConversation(sampleConversation);
      }
    } else {
      setWrittenReport(sampleReport);
    }
  };

  const toggleViewMode = () => {
    setViewMode(viewMode === 'transcript' ? 'conversation' : 'transcript');
  };

  const toggleDemoMode = () => {
    setDemoMode(demoMode === 'call' ? 'report' : 'call');
    setResults(null);
    setActiveTab('summary');
  };

  const addMessage = () => {
    if (newMessage.text.trim()) {
      setConversation([...conversation, { ...newMessage }]);
      setNewMessage({ ...newMessage, text: "" });
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      addMessage();
    }
  };

  const deleteMessage = (index) => {
    const updatedConversation = [...conversation];
    updatedConversation.splice(index, 1);
    setConversation(updatedConversation);
  };

  // Convert conversation to transcript format
  const conversationToTranscript = () => {
    return conversation.map(msg => `${msg.speaker}: ${msg.text}`).join('\n\n');
  };

  // Process transcript or report using LLM
  const processInput = () => {
    let textToProcess;
    
    if (demoMode === 'call') {
      textToProcess = viewMode === 'transcript' ? transcript : conversationToTranscript();
      if (!textToProcess.trim()) {
        alert('Please enter a transcript or conversation first.');
        return;
      }
    } else {
      textToProcess = writtenReport;
      if (!textToProcess.trim()) {
        alert('Please enter a written report first.');
        return;
      }
    }

    setLoading(true);
    
    // Simulate LLM processing
    setTimeout(() => {
      // Extract location using "LLM"
      const locationInfo = extractLocationWithLLM(textToProcess);
      setLocation(locationInfo);
      
      // Classify incident using "LLM"
      const classification = classifyWithLLM(textToProcess);
      setLlmClassification(classification);
      
      // Generate complete results
      const mockResults = generateMockResults(
        textToProcess, 
        locationInfo, 
        classification, 
        demoMode === 'call' ? 'emergency_call' : 'written_report'
      );
      
      setResults(mockResults);
      setLoading(false);
      setActiveTab('summary');
    }, 2000);
  };

  // Simulate LLM location extraction
  const extractLocationWithLLM = (text) => {
    // Look for known locations in the text
    const locations = {
      "geisel library": { lat: 32.8810, lng: -117.2370, name: "Geisel Library" },
      "price center": { lat: 32.8794, lng: -117.2359, name: "Price Center" },
      "warren college": { lat: 32.8815, lng: -117.2350, name: "Warren College" },
      "warren apartments": { lat: 32.8825, lng: -117.2355, name: "Warren Apartments" },
      "sixth college": { lat: 32.8806, lng: -117.2325, name: "Sixth College" },
      "muir college": { lat: 32.8789, lng: -117.2410, name: "Muir College" },
      "revelle college": { lat: 32.8745, lng: -117.2410, name: "Revelle College" },
      "rimac": { lat: 32.8869, lng: -117.2406, name: "RIMAC Arena" },
      "library walk": { lat: 32.8794, lng: -117.2370, name: "Library Walk" },
      "la jolla": { lat: 32.8328, lng: -117.2712, name: "La Jolla" },
      "downtown": { lat: 32.7157, lng: -117.1611, name: "Downtown San Diego" }
    };

    const textLower = text.toLowerCase();
    
    // Check for known locations
    for (const [keyword, locationData] of Object.entries(locations)) {
      if (textLower.includes(keyword)) {
        return {
          ...locationData,
          source: `LLM extracted "${keyword}" from the transcript`,
          confidence: 0.92
        };
      }
    }
    
    // Default to UCSD campus
    return {
      lat: 32.8801,
      lng: -117.2340,
      name: "UC San Diego Campus",
      source: "Default location (no specific location found)",
      confidence: 0.6
    };
  };

  // Simulate LLM classification
  const classifyWithLLM = (text) => {
    const textLower = text.toLowerCase();
    
    // Classification logic based on keywords
    let incidentType = "unknown";
    let priority = 3;
    let confidence = 0.7;
    
    if (/fire|burning|flames|smoke/.test(textLower)) {
      incidentType = "fire";
      priority = 1;
      confidence = 0.95;
    } else if (/gas leak|gas smell|fume|strong smell/.test(textLower)) {
      incidentType = "hazard";
      priority = 1;
      confidence = 0.93;
    } else if (/suspicious|theft|steal|threat|weapon|gun/.test(textLower)) {
      incidentType = "crime";
      priority = 2;
      confidence = 0.88;
    } else if (/injured|hurt|medical|ambulance|blood/.test(textLower)) {
      incidentType = "medical";
      priority = 2;
      confidence = 0.91;
    } else if (/leak|chemical|hazard|spill/.test(textLower)) {
      incidentType = "hazard";
      priority = 1;
      confidence = 0.89;
    } else if (/power|outage|electricity/.test(textLower)) {
      incidentType = "infrastructure";
      priority = 3;
      confidence = 0.85;
    }
    
    // Additional subtype classification
    let subtype = "";
    if (incidentType === "crime") {
      if (/theft|steal|took|missing/.test(textLower)) {
        subtype = "theft";
      } else if (/suspicious|strange|odd/.test(textLower)) {
        subtype = "suspicious_person";
      } else if (/assault|attack|hit|punch/.test(textLower)) {
        subtype = "assault";
      } else if (/break|broke|breaking/.test(textLower)) {
        subtype = "break_in";
      }
    } else if (incidentType === "hazard") {
      if (/gas|smell/.test(textLower)) {
        subtype = "gas_leak";
      } else if (/chemical|spill/.test(textLower)) {
        subtype = "chemical_spill";
      } else if (/water|flood/.test(textLower)) {
        subtype = "flooding";
      }
    }
    
    // Extract key details using "LLM"
    const keyDetails = [];
    
    // Look for potential victims
    let victimCount = 0;
    let victimDetails = "";
    if (/injured|hurt|victim|bleeding/.test(textLower)) {
      const victimMatch = textLower.match(/(\d+)\s+(?:person|people|individuals|victims)/);
      victimCount = victimMatch ? parseInt(victimMatch[1]) : 1;
      victimDetails = "Details extracted from transcript";
      keyDetails.push(`${victimCount} person(s) potentially injured`);
    }
    
    // Look for suspect information
    let suspectInfo = "";
    let weaponsInvolved = /weapon|gun|knife|armed/.test(textLower);
    if (/suspect|suspicious|man|woman|person|wearing/.test(textLower)) {
      // Extract description if available
      const descriptionMatch = text.match(/wearing[^.]*/i);
      if (descriptionMatch) {
        suspectInfo = descriptionMatch[0];
        keyDetails.push(`Suspect description: ${suspectInfo}`);
      } else {
        suspectInfo = "Suspicious person reported";
        keyDetails.push(suspectInfo);
      }
    }
    
    if (weaponsInvolved) {
      keyDetails.push("Weapons may be involved");
    }
    
    return {
      incidentType,
      subtype,
      priority,
      confidence,
      victimCount,
      victimDetails,
      suspectInfo,
      weaponsInvolved,
      keyDetails: keyDetails.length > 0 ? keyDetails : ["Incident reported", "Details pending"],
      analysis: `LLM classified this as a ${incidentType} incident with ${confidence.toFixed(2)} confidence.`
    };
  };

  // Generate mock results based on text content, location and classification
  const generateMockResults = (text, locationInfo, classification, source) => {
    // Create EIDO
    const eido = {
      eido: {
        eidoVersion: "1.0",
        eidoType: "incident",
        eidoID: "EIDO-" + Date.now(),
        timestamp: new Date().toISOString(),
        incident: {
          incidentID: "INC-" + Date.now(),
          incidentType: classification.incidentType,
          incidentSubType: classification.subtype,
          priority: classification.priority,
          status: "active",
          createdAt: new Date().toISOString(),
          reportingParty: {
            role: source === "emergency_call" ? "caller" : "reporter",
            name: "Anonymous"
          },
          location: {
            address: {
              fullAddress: locationInfo.name,
              additionalInfo: ""
            },
            coordinates: {
              latitude: locationInfo.lat,
              longitude: locationInfo.lng
            }
          },
          details: {
            description: `Reported ${classification.incidentType} incident at ${locationInfo.name}. Priority assessed as ${classification.priority}/5.`,
            timeline: [
              {
                timestamp: new Date().toISOString(),
                action: source === "emergency_call" ? "Emergency call received" : "Written report submitted",
                notes: source === "emergency_call" ? "Initial 911 call transcribed and processed" : "Report processed through classification system"
              }
            ],
            victims: {
              count: classification.victimCount,
              details: classification.victimDetails
            },
            suspects: {
              description: classification.suspectInfo,
              weaponsInvolved: classification.weaponsInvolved
            },
            keyFacts: classification.keyDetails,
            rawReport: text
          }
        },
        notification: {
          recommendedActions: getRecommendedActions(classification.incidentType, classification.priority),
          recommendedNotificationScope: {
            geographic: getGeographicScope(classification.incidentType, classification.priority),
            radius_meters: getNotificationRadius(classification.incidentType, classification.priority),
            population: getTargetPopulation(classification.incidentType, classification.priority),
            notify_authorities: true
          },
          updateFrequency: "as_needed"
        }
      }
    };
    
    // Create notification results
    const notificationResults = {
      incident_id: eido.eido.incident.incidentID,
      timestamp: new Date().toISOString(),
      notification_radius_meters: eido.eido.notification.recommendedNotificationScope.radius_meters,
      target_groups: eido.eido.notification.recommendedNotificationScope.population,
      recipients_count: Math.floor(Math.random() * 50) + 5,
      notification_plan: generateNotificationPlan(eido),
      content: {
        summary: `${classification.incidentType.toUpperCase()}${classification.subtype ? ': ' + classification.subtype.replace('_', ' ') : ''} at ${locationInfo.name}`,
        description: eido.eido.incident.details.description,
        location: locationInfo.name,
        incident_type: classification.incidentType,
        action_required: eido.eido.notification.recommendedActions.join(" "),
        details_url: `https://alerts.ucsd.edu/details/${eido.eido.incident.incidentID.slice(-6)}`,
        severity: ["CRITICAL", "HIGH", "MEDIUM", "LOW", "INFORMATION"][classification.priority - 1]
      }
    };
    
    return {
      eido: eido,
      notification_results: notificationResults,
      processing_time: (Math.random() * 0.5 + 0.2).toFixed(2),
      notification_time: (Math.random() * 0.3 + 0.1).toFixed(2),
      location: locationInfo,
      classification: classification,
      source: source
    };
  };
  
  // Helper functions for generating mock data
  function getRecommendedActions(incidentType, priority) {
    if (incidentType === "fire") {
      return ["Evacuate the building immediately", "Move to designated assembly areas"];
    } else if (incidentType === "crime") {
      if (priority <= 2) {
        return ["Shelter in place", "Lock doors", "Report suspicious activity to campus police"];
      } else {
        return ["Be aware of your surroundings", "Report suspicious activity to campus police"];
      }
    } else if (incidentType === "medical") {
      return ["Clear the area for emergency responders", "Direct responders to the location"];
    } else if (incidentType === "hazard") {
      return ["Avoid the affected area", "Follow instructions from emergency personnel"];
    } else {
      return ["Stay alert", "Follow official instructions"];
    }
  }
  
  function getGeographicScope(incidentType, priority) {
    if (priority === 1) {
      return "campus_wide";
    } else if (priority === 2) {
      return "campus_section";
    } else if (incidentType === "fire") {
      return "affected_building";
    } else {
      return "immediate_vicinity";
    }
  }
  
  function getNotificationRadius(incidentType, priority) {
    if (priority === 1) {
      return 1000;
    } else if (priority === 2) {
      return 500;
    } else if (incidentType === "fire") {
      return 300;
    } else {
      return 100;
    }
  }
  
  function getTargetPopulation(incidentType, priority) {
    const groups = ["emergency_responders"];
    
    if (priority === 1) {
      groups.push("all_students", "all_staff", "all_faculty", "leadership");
    } else if (priority === 2) {
      groups.push("area_occupants", "leadership");
    } else {
      groups.push("area_occupants");
    }
    
    if (incidentType === "fire") {
      groups.push("facilities");
    } else if (incidentType === "crime") {
      groups.push("police", "security");
    } else if (incidentType === "medical") {
      groups.push("health_services");
    } else if (incidentType === "hazard") {
      groups.push("environmental_safety", "facilities");
    }
    
    return [...new Set(groups)]; // Remove duplicates
  }
  
  function generateNotificationPlan(eido) {
    const channels = ["sms", "email", "app_push", "phone"];
    const plan = [];
    
    // Generate fake recipients
    const recipients = [
      { id: "r001", name: "Chief Roberts", role: "campus_police_chief" },
      { id: "r002", name: "Officer Garcia", role: "campus_police" },
      { id: "r003", name: "Dr. Chen", role: "dean" },
      { id: "r004", name: "Facilities Team", role: "facilities" },
      { id: "r005", name: "Campus Security", role: "security" },
      { id: "r006", name: "Student Health Center", role: "health_services" },
      { id: "r007", name: "Environmental Safety", role: "environmental_safety" },
      { id: "s001", name: "Alex Smith", role: "student" },
      { id: "s002", name: "Jordan Lee", role: "student" },
      { id: "s003", name: "Taylor Wilson", role: "student" }
    ];
    
    // Based on priority, determine which channels to use
    let priority = eido.eido.incident.priority;
    let channelsToUse = [];
    
    if (priority === 1) {
      channelsToUse = channels; // Use all channels for highest priority
    } else if (priority === 2) {
      channelsToUse = ["sms", "app_push", "email"]; // Use most channels for high priority
    } else {
      channelsToUse = ["app_push", "email"]; // Use fewer channels for lower priority
    }
    
    // Create notifications
    for (const recipient of recipients) {
      for (const channel of channelsToUse) {
        plan.push({
          recipient_id: recipient.id,
          recipient_name: recipient.name,
          channel: channel,
          message: `${eido.eido.incident.incidentType.toUpperCase()} ALERT: Incident at ${eido.eido.incident.location.address.fullAddress}. ${eido.eido.notification.recommendedActions[0]}`,
          priority: priority,
          timestamp: new Date().toISOString()
        });
      }
    }
    
    return plan;
  }

  // Simple map rendering
  const renderMap = () => {
    if (!results) return null;
    
    return (
      <div className="bg-white rounded-lg shadow-md p-4 mb-4">
        <h3 className="text-lg font-bold mb-2">Incident Location</h3>
        <div className="bg-gray-100 p-3 mb-3 rounded-md">
          <p><strong>Location:</strong> {results.location.name}</p>
          <p><strong>Coordinates:</strong> ({results.location.lat.toFixed(4)}, {results.location.lng.toFixed(4)})</p>
          <p><strong>Extraction Source:</strong> {results.location.source}</p>
          <p><strong>Confidence:</strong> {(results.location.confidence * 100).toFixed(1)}%</p>
        </div>
        <div className="h-64 bg-blue-50 flex items-center justify-center rounded-md border border-blue-200 relative">
          {/* This would be a real map in a production implementation */}
          <div className="text-center text-gray-600">
            <p className="mb-2">Interactive Map</p>
            <p className="text-sm">In a real implementation, this would show a map centered at:</p>
            <p className="font-bold">{results.location.name}</p>
            <p>({results.location.lat.toFixed(6)}, {results.location.lng.toFixed(6)})</p>
          </div>
          <div 
            className="absolute h-4 w-4 bg-red-500 rounded-full top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2"
            style={{ boxShadow: '0 0 0 8px rgba(239, 68, 68, 0.3)' }}
          ></div>
        </div>
      </div>
    );
  };

  return (
    <div className="max-w-4xl mx-auto p-4">
      <div className="bg-blue-700 text-white p-6 rounded-t-lg shadow-md">
        <h1 className="text-3xl font-bold">Safe Campus Agent Demo</h1>
        <p className="mt-2">
          {demoMode === 'call' 
            ? "Process 911 calls into standardized EIDO format for emergency notifications" 
            : "Analyze written incident reports for emergency notification decisions"}
        </p>
      </div>
      
      <div className="bg-white p-6 rounded-b-lg shadow-md mb-8">
        <div className="mb-4 flex justify-between items-center">
          <div className="font-medium text-lg">
            {demoMode === 'call' ? 'Emergency Call Processing' : 'Written Report Analysis'}
          </div>
          <button
            className="bg-gray-200 hover:bg-gray-300 text-gray-800 text-sm py-1 px-3 rounded-md"
            onClick={toggleDemoMode}
          >
            Switch to {demoMode === 'call' ? 'Report Analysis' : 'Call Processing'}
          </button>
        </div>
        
        {demoMode === 'call' ? (
          <>
            <div className="mb-4 flex justify-between items-center">
              <div className="font-medium text-md">
                {viewMode === 'transcript' ? 'Transcript Mode' : 'Conversation Mode'}
              </div>
              <button
                className="bg-gray-200 hover:bg-gray-300 text-gray-800 text-sm py-1 px-3 rounded-md"
                onClick={toggleViewMode}
              >
                Switch to {viewMode === 'transcript' ? 'Conversation' : 'Transcript'} Mode
              </button>
            </div>
            
            {viewMode === 'transcript' ? (
              <div className="mb-4">
                <label htmlFor="transcript" className="block text-lg font-medium mb-2">
                  911 Call Transcript
                </label>
                <textarea
                  id="transcript"
                  className="w-full h-64 p-3 border border-gray-300 rounded-md shadow-sm"
                  placeholder="Enter the 911 call transcript here..."
                  value={transcript}
                  onChange={(e) => setTranscript(e.target.value)}
                />
              </div>
            ) : (
              <div className="mb-4">
                <label className="block text-lg font-medium mb-2">
                  911 Call Conversation
                </label>
                <div className="border border-gray-300 rounded-md shadow-sm p-3 h-64 overflow-y-auto mb-3">
                  {conversation.map((msg, index) => (
                    <div key={index} className="mb-3 flex">
                      <div className={`p-2 rounded-lg max-w-3/4 ${msg.speaker === "Dispatcher" ? "bg-blue-100 mr-auto" : "bg-green-100 ml-auto"}`}>
                        <div className="font-bold text-sm text-gray-700">{msg.speaker}</div>
                        <div>{msg.text}</div>
                      </div>
                      <button 
                        onClick={() => deleteMessage(index)}
                        className="ml-2 text-red-500 hover:text-red-700 self-center"
                      >
                        ×
                      </button>
                    </div>
                  ))}
                </div>
                <div className="flex">
                  <select 
                    className="p-2 border border-gray-300 rounded-l-md"
                    value={newMessage.speaker}
                    onChange={(e) => setNewMessage({ ...newMessage, speaker: e.target.value })}
                  >
                    <option value="Dispatcher">Dispatcher</option>
                    <option value="Caller">Caller</option>
                  </select>
                  <input
                    type="text"
                    className="flex-grow p-2 border-t border-b border-gray-300"
                    placeholder="Type a message..."
                    value={newMessage.text}
                    onChange={(e) => setNewMessage({ ...newMessage, text: e.target.value })}
                    onKeyPress={handleKeyPress}
                  />
                  <button
                    className="p-2 bg-blue-600 text-white rounded-r-md"
                    onClick={addMessage}
                  >
                    Add
                  </button>
                </div>
              </div>
            )}
          </>
        ) : (
          <div className="mb-4">
            <label htmlFor="report" className="block text-lg font-medium mb-2">
              Written Incident Report
            </label>
            <textarea
              id="report"
              className="w-full h-64 p-3 border border-gray-300 rounded-md shadow-sm"
              placeholder="Enter the incident report text here..."
              value={writtenReport}
              onChange={(e) => setWrittenReport(e.target.value)}
            />
          </div>
        )}
        
        <div className="flex gap-4">
          <button
            className="bg-blue-600 hover:bg-blue-700 text-white py-2 px-4 rounded-md"
            onClick={processInput}
            disabled={loading}
          >
            {loading ? 'Processing...' : demoMode === 'call' ? 'Process Emergency Call' : 'Analyze Report'}
          </button>
          <button
            className="bg-gray-200 hover:bg-gray-300 text-gray-800 py-2 px-4 rounded-md"
            onClick={loadSample}
            disabled={loading}
          >
            Load Sample
          </button>
        </div>
      </div>
      
      {results && (
        <div className="bg-white rounded-lg shadow-md overflow-hidden mb-8">
          <div className="bg-green-600 text-white p-4">
            <h2 className="text-xl font-bold">Results</h2>
            <p className="text-sm">
              {results.source === "emergency_call" ? "Call" : "Report"} processing time: {results.processing_time}s | 
              Notification planning time: {results.notification_time}s
            </p>
          </div>
          
          <div className="border-b border-gray-200">
            <nav className="flex flex-wrap">
              <button
                className={`px-4 py-2 font-medium ${activeTab === 'summary' ? 'border-b-2 border-blue-500 text-blue-600' : 'text-gray-600 hover:text-blue-500'}`}
                onClick={() => setActiveTab('summary')}
              >
                Summary
              </button>
              <button
                className={`px-4 py-2 font-medium ${activeTab === 'classification' ? 'border-b-2 border-blue-500 text-blue-600' : 'text-gray-600 hover:text-blue-500'}`}
                onClick={() => setActiveTab('classification')}
              >
                LLM Classification
              </button>
              <button
                className={`px-4 py-2 font-medium ${activeTab === 'location' ? 'border-b-2 border-blue-500 text-blue-600' : 'text-gray-600 hover:text-blue-500'}`}
                onClick={() => setActiveTab('location')}
              >
                Location
              </button>
              <button
                className={`px-4 py-2 font-medium ${activeTab === 'eido' ? 'border-b-2 border-blue-500 text-blue-600' : 'text-gray-600 hover:text-blue-500'}`}
                onClick={() => setActiveTab('eido')}
              >
                EIDO Details
              </button>
              <button
                className={`px-4 py-2 font-medium ${activeTab === 'notifications' ? 'border-b-2 border-blue-500 text-blue-600' : 'text-gray-600 hover:text-blue-500'}`}
                onClick={() => setActiveTab('notifications')}
              >
                Notification Plan
              </button>
            </nav>
          </div>
          
          <div className="p-6">
            {activeTab === 'summary' && (
              <div>
                <div className="mb-6">
                  <h3 className="text-lg font-bold mb-2">Incident Summary</h3>
                  <div className="bg-gray-50 p-4 rounded-md">
                    <p className="mb-1"><strong>Type:</strong> {results.eido.eido.incident.incidentType.toUpperCase()}</p>
                    {results.eido.eido.incident.incidentSubType && (
                      <p className="mb-1"><strong>Subtype:</strong> {results.eido.eido.incident.incidentSubType.replace('_', ' ').toUpperCase()}</p>
                    )}
                    <p className="mb-1"><strong>Priority:</strong> {results.eido.eido.incident.priority}/5 ({['CRITICAL', 'HIGH', 'MEDIUM', 'LOW', 'INFORMATION'][results.eido.eido.incident.priority-1]})</p>
                    <p className="mb-1"><strong>Location:</strong> {results.eido.eido.incident.location.address.fullAddress}</p>
                    <p className="mb-1"><strong>Status:</strong> {results.eido.eido.incident.status.toUpperCase()}</p>
                    <p className="mt-3"><strong>Description:</strong> {results.eido.eido.incident.details.description}</p>
                  </div>
                </div>
                
                <div className="mb-6">
                  <h3 className="text-lg font-bold mb-2">Recommended Actions</h3>
                  <ul className="bg-yellow-50 p-4 rounded-md">
                    {results.eido.eido.notification.recommendedActions.map((action, i) => (
                      <li key={i} className="mb-1">• {action}</li>
                    ))}
                  </ul>
                </div>
                
                <div className="mb-6">
                  <h3 className="text-lg font-bold mb-2">Key Facts</h3>
                  <ul className="bg-blue-50 p-4 rounded-md">
                    {results.eido.eido.incident.details.keyFacts.map((fact, i) => (
                      <li key={i} className="mb-1">• {fact}</li>
                    ))}
                  </ul>
                </div>
                
                <div>
                  <h3 className="text-lg font-bold mb-2">Notification Overview</h3>
                  <div className="bg-purple-50 p-4 rounded-md">
                    <p className="mb-1"><strong>Notification Radius:</strong> {results.notification_results.notification_radius_meters} meters</p>
                    <p className="mb-1"><strong>Target Groups:</strong> {results.notification_results.target_groups.join(', ')}</p>
                    <p className="mb-1"><strong>Total Recipients:</strong> {results.notification_results.recipients_count}</p>
                  </div>
                </div>
              </div>
            )}
            
            {activeTab === 'classification' && (
              <div>
                <h3 className="text-lg font-bold mb-2">LLM Classification Results</h3>
                
                <div className="bg-yellow-50 p-4 rounded-md mb-4">
                  <p className="text-sm italic">{results.classification.analysis}</p>
                </div>
                
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
                  <div className="bg-gray-50 p-4 rounded-md">
                    <h4 className="font-bold mb-2">Primary Classification</h4>
                    <p className="mb-1"><strong>Incident Type:</strong> {results.classification.incidentType}</p>
                    {results.classification.subtype && (
                      <p className="mb-1"><strong>Subtype:</strong> {results.classification.subtype.replace('_', ' ')}</p>
                    )}
                    <p className="mb-1"><strong>Priority:</strong> {results.classification.priority}/5</p>
                    <p className="mb-1"><strong>Confidence:</strong> {(results.classification.confidence * 100).toFixed(1)}%</p>
                  </div>
                  
                  <div className="bg-gray-50 p-4 rounded-md">
                    <h4 className="font-bold mb-2">Extracted Details</h4>
                    <p className="mb-1"><strong>Victims:</strong> {results.classification.victimCount > 0 ? `${results.classification.victimCount} reported` : 'None reported'}</p>
                    <p className="mb-1"><strong>Weapons:</strong> {results.classification.weaponsInvolved ? 'Potentially involved' : 'None reported'}</p>
                    {results.classification.suspectInfo && (
                      <p className="mb-1"><strong>Suspect Info:</strong> {results.classification.suspectInfo}</p>
                    )}
                  </div>
                </div>
                
                <div className="bg-blue-50 p-4 rounded-md">
                  <h4 className="font-bold mb-2">Key Details Extracted</h4>
                  <ul>
                    {results.classification.keyDetails.map((detail, i) => (
                      <li key={i} className="mb-1">• {detail}</li>
                    ))}
                  </ul>
                </div>
                
                <div className="mt-4 pt-4 border-t border-gray-200">
                  <h4 className="font-bold mb-2">Classification Explanation</h4>
                  <p className="text-sm">
                    The LLM analyzed the {results.source === "emergency_call" ? "emergency call transcript" : "written report"} and classified it based on keywords, 
                    context, and patterns. It identified this as a <strong>{results.classification.incidentType}</strong> incident
                    with {(results.classification.confidence * 100).toFixed(1)}% confidence. The severity was assessed as 
                    priority <strong>{results.classification.priority}/5</strong> based on the nature of the incident and potential 
                    impact.
                  </p>
                </div>
              </div>
            )}
            
            {activeTab === 'location' && (
              <div>
                <h3 className="text-lg font-bold mb-2">Location Extraction</h3>
                
                {renderMap()}
                
                <div className="bg-gray-50 p-4 rounded-md mb-4">
                  <h4 className="font-bold mb-2">Location Details</h4>
                  <p className="mb-1"><strong>Location Name:</strong> {results.location.name}</p>
                  <p className="mb-1"><strong>Coordinates:</strong> ({results.location.lat.toFixed(6)}, {results.location.lng.toFixed(6)})</p>
                  <p className="mb-1"><strong>Extraction Method:</strong> {results.location.source}</p>
                  <p className="mb-1"><strong>Confidence:</strong> {(results.location.confidence * 100).toFixed(1)}%</p>
                </div>
                
                <div className="mt-4 pt-4 border-t border-gray-200">
                  <h4 className="font-bold mb-2">Location Processing Explanation</h4>
                  <p className="text-sm">
                    The LLM extracted location information from the {results.source === "emergency_call" ? "emergency call" : "written report"} by identifying specific location
                    references and keywords. It analyzed the context to determine the most likely location of the incident.
                    The system then geocoded this location to obtain precise coordinates for emergency response and
                    notification purposes.
                  </p>
                </div>
              </div>
            )}
            
            {activeTab === 'eido' && (
              <div>
                <h3 className="text-lg font-bold mb-2">EIDO Object (Emergency Incident Data Object)</h3>
                <p className="mb-4 text-sm">
                  This is the standardized EIDO format following NENA (National Emergency Number Association) standards.
                  This structured format enables interoperability between emergency systems.
                </p>
                <pre className="bg-gray-100 p-4 rounded-md overflow-auto h-96 text-sm">
                  {JSON.stringify(results.eido, null, 2)}
                </pre>
              </div>
            )}
            
            {activeTab === 'notifications' && (
              <div>
                <h3 className="text-lg font-bold mb-2">Notification Plan</h3>
                
                <div className="mb-4 bg-blue-50 p-4 rounded-md">
                  <p className="font-medium">Notification Content:</p>
                  <p className="mb-1"><strong>Summary:</strong> {results.notification_results.content.summary}</p>
                  <p className="mb-1"><strong>Action Required:</strong> {results.notification_results.content.action_required}</p>
                  <p className="mb-1"><strong>Severity:</strong> {results.notification_results.content.severity}</p>
                </div>
                
                <div className="mb-4">
                  <h4 className="font-bold mb-2">Notification Scope</h4>
                  <div className="bg-green-50 p-4 rounded-md">
                    <p className="mb-1"><strong>Geographic Scope:</strong> {results.eido.eido.notification.recommendedNotificationScope.geographic.replace('_', ' ')}</p>
                    <p className="mb-1"><strong>Radius:</strong> {results.notification_results.notification_radius_meters} meters</p>
                    <p className="mb-1"><strong>Target Groups:</strong> {results.notification_results.target_groups.join(', ')}</p>
                    <p className="mb-1"><strong>Notify Authorities:</strong> {results.eido.eido.notification.recommendedNotificationScope.notify_authorities ? 'Yes' : 'No'}</p>
                  </div>
                </div>
                
                <div className="overflow-auto">
                  <h4 className="font-bold mb-2">Recipients by Channel</h4>
                  <table className="min-w-full bg-white">
                    <thead className="bg-gray-100">
                      <tr>
                        <th className="py-2 px-4 text-left">Recipient</th>
                        <th className="py-2 px-4 text-left">Channel</th>
                        <th className="py-2 px-4 text-left">Message</th>
                      </tr>
                    </thead>
                    <tbody>
                      {results.notification_results.notification_plan.slice(0, 10).map((notification, i) => (
                        <tr key={i} className={i % 2 === 0 ? "bg-gray-50" : ""}>
                          <td className="py-2 px-4">{notification.recipient_name}</td>
                          <td className="py-2 px-4">
                            <span className={`px-2 py-1 rounded-full text-xs ${
                              notification.channel === 'sms' ? 'bg-blue-100 text-blue-800' :
                              notification.channel === 'email' ? 'bg-green-100 text-green-800' :
                              notification.channel === 'app_push' ? 'bg-purple-100 text-purple-800' :
                              notification.channel === 'phone' ? 'bg-red-100 text-red-800' :
                              'bg-gray-100 text-gray-800'
                            }`}>
                              {notification.channel}
                            </span>
                          </td>
                          <td className="py-2 px-4 truncate max-w-xs">{notification.message}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                  {results.notification_results.notification_plan.length > 10 && (
                    <p className="text-center text-gray-500 text-sm mt-2">
                      Showing 10 of {results.notification_results.notification_plan.length} notifications
                    </p>
                  )}
                </div>
              </div>
            )}
          </div>
        </div>
      )}
      
      <div className="bg-white rounded-lg shadow-md p-6">
        <h2 className="text-lg font-bold mb-2">About Safe Campus Agent</h2>
        <p className="mb-4">
          The Safe Campus Agent is an intelligent emergency notification system that uses AI to process 911 calls 
          and incident reports into the NENA EIDO (Emergency Incident Data Object) format, enabling sophisticated 
          context-aware notification decisions.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div className="border border-gray-200 rounded-md p-3">
            <h3 className="font-bold text-blue-700 mb-2">LLM Classification</h3>
            <p className="text-sm">
              Uses AI to analyze emergency calls and reports, extract key information, and classify incidents by type and severity.
            </p>
          </div>
          <div className="border border-gray-200 rounded-md p-3">
            <h3 className="font-bold text-blue-700 mb-2">EIDO Standardization</h3>
            <p className="text-sm">
              Converts unstructured emergency data into standardized EIDO format for interoperability between systems.
            </p>
          </div>
          <div className="border border-gray-200 rounded-md p-3">
            <h3 className="font-bold text-blue-700 mb-2">Intelligent Notifications</h3>
            <p className="text-sm">
              Determines who should be notified and through which channels based on incident context and severity.
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}