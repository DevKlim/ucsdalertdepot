// static/js/safe_campus_agent.js

document.addEventListener('DOMContentLoaded', function() {
    // Add listener for quick test form if it exists on the page
    const testAgentButton = document.getElementById('test-agent-button');
    if (testAgentButton) {
      testAgentButton.addEventListener('click', function() {
        testSafeCampusAgent();
      });
    }
    
    // Add sample data button listener if it exists
    const loadSampleButton = document.getElementById('load-sample-button');
    if (loadSampleButton) {
      loadSampleButton.addEventListener('click', function() {
        loadSampleData();
      });
    }
  });
  
  function testSafeCampusAgent() {
    // Get the test transcript
    const transcript = document.getElementById('test-transcript').value;
    if (!transcript) {
      alert('Please enter a test transcript');
      return;
    }
  
    // Show loading state
    const resultArea = document.getElementById('agent-test-result');
    resultArea.innerHTML = '<div class="loading">Processing transcript...</div>';
    
    // Call the API
    fetch('/api/process_call', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({ transcript: transcript })
    })
    .then(response => {
      if (!response.ok) {
        throw new Error('Network response was not ok');
      }
      return response.json();
    })
    .then(data => {
      // Display a simplified result
      resultArea.innerHTML = `
        <div class="agent-result">
          <h4>Processing Result:</h4>
          <p><strong>Incident Type:</strong> ${data.classification.incidentType.toUpperCase()}</p>
          <p><strong>Priority:</strong> ${data.classification.priority}/5</p>
          <p><strong>Location:</strong> ${data.location.name}</p>
          <p><strong>Notification Radius:</strong> ${data.notification_results.notification_radius_meters} meters</p>
          <p><strong>Recipients to Notify:</strong> ${data.notification_results.recipients_count}</p>
          <p><a href="/safe-campus-agent" class="btn btn-small">View Full Demo</a></p>
        </div>
      `;
    })
    .catch(error => {
      resultArea.innerHTML = `<div class="error">Error: ${error.message}</div>`;
    });
  }
  
  function loadSampleData() {
    // Sample transcript for quick testing
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
  
    // Set the sample transcript in the textarea
    const transcriptElement = document.getElementById('test-transcript');
    if (transcriptElement) {
      transcriptElement.value = sampleTranscript;
    }
  }