// process-visualizations.js
// This file contains visualization components for the process page

document.addEventListener('DOMContentLoaded', function() {
    // Hide all visualizations by default (using display property)
    const allVisContainers = document.querySelectorAll('[id$="-vis"]');
    allVisContainers.forEach(container => {
      container.style.display = 'none';
    });
    
    // Show only the first visualization
    const firstVis = document.getElementById('challenge-vis');
    if (firstVis) {
      firstVis.style.display = 'flex';
    }
    
    // Call regular initialization
    initProcessVisualizations();
  });

// window.addEventListener('DOMContentLoaded', function() {
//     // Make all visualizations hidden by default
//     const allVisContainers = document.querySelectorAll('[id$="-vis"]');
//     allVisContainers.forEach(container => {
//       container.style.display = 'none';
//     });
    
//     // Show first visualization by default
//     const firstVis = document.getElementById('challenge-vis');
//     if (firstVis) {
//       firstVis.style.display = 'flex';
//     }
    
//     // Initialize all visualizations
//     initProcessVisualizations();
//   });
  
// Expose a visualization handler function that process.js can use
window.visualizationHandler = function(stepId) {
    // Hide all visualizations using display property
    const allVisContainers = document.querySelectorAll('[id$="-vis"]');
    allVisContainers.forEach(container => {
      container.style.display = 'none';
    });
    
    // Show the visualization for the current step
    const currentVis = document.getElementById(`${stepId}-vis`);
    if (currentVis) {
      currentVis.style.display = 'flex';
    }
  };
  
  function initProcessVisualizations() {
    // Create all visualization content
    createChallengeVis();
    createOCRVis();
    createGeocodingVis();
    createRealtimeVis();
    createDataVisualizationVis();
    createDashboardVis(); // Add new visualization
    createPrivacyVis();
    createMistralVis();
    createAPIVis();
    createSanDiegoIntegrationVis();
    createLLMComparisonVis(); // Add new visualization
    createNLPFutureVis();
    createRoadmapVis();
    createConclusionVis();
  }
  
  function createChallengeVis() {
    const container = document.getElementById('challenge-vis');
    if (!container) return;
    
    container.innerHTML = `
      <div class="vis-container">
        <h3>Standard Geocoding Failure</h3>
        <div class="geocoding-failure-demo">
          <div class="terminal">
            <div class="terminal-header">
              <div class="terminal-button"></div>
              <div class="terminal-button"></div>
              <div class="terminal-button"></div>
              <div class="terminal-title">Geocoding Terminal</div>
            </div>
            <div class="terminal-body">
              <div class="terminal-line">$ geocode "Sixth College, UCSD"</div>
              <div class="terminal-line error">ERROR: No clear address</div>
              <div class="terminal-line">$ geocode "Bus Stop by Pangaea"</div>
              <div class="terminal-line error">ERROR: Ambiguous location (multiple results)</div>
              <div class="terminal-line">$ geocode "Eighth College"</div>
              <div class="terminal-line error">ERROR: No results</div>
              <div class="terminal-line">$ geocode "Trolley Station"</div>
              <div class="terminal-line error">ERROR: Ambiguous location</div>
              <div class="terminal-line blink">_</div>
            </div>
          </div>
        </div>
        <div class="vis-caption">
          Traditional geocoding services tend to fail at recognizing campus-specific locations
        </div>
      </div>
    `;
    
    // Add animation for terminal blinking cursor
    setInterval(() => {
      const cursor = container.querySelector('.terminal-line.blink');
      if (cursor) {
        cursor.style.opacity = cursor.style.opacity === '0' ? '1' : '0';
      }
    }, 700);
  }
  
  // OCR Map Extraction Visualization (Step 2)
  function createOCRVis() {
    const container = document.getElementById('ocr-vis');
    if (!container) return;
    
    container.innerHTML = `
      <div class="vis-container">
        <h3>OCR Map Scanning</h3>
        <div class="map-ocr-demo">
          <div class="campus-map">
            <div class="map-overlay"></div>
            <div class="scan-line"></div>
            
            <!-- Detected building labels -->
            <div class="map-label" style="top: 25%; left: 40%;">Geisel Library</div>
            <div class="map-label" style="top: 35%; left: 60%;">Price Center</div>
            <div class="map-label" style="top: 50%; left: 25%;">Sixth College</div>
            <div class="map-label" style="top: 70%; left: 55%;">Center Hall</div>
            <div class="map-label" style="top: 40%; left: 75%;">Trolley Station</div>
          </div>
          
          <div class="ocr-results">
            <div class="ocr-header">OCR Results</div>
            <div class="ocr-body">
              <div class="ocr-item">
                <span class="ocr-label">Geisel Library</span>
                <span class="ocr-coords">(32.8810, -117.2370)</span>
              </div>
              <div class="ocr-item">
                <span class="ocr-label">Price Center</span>
                <span class="ocr-coords">(32.8794, -117.2359)</span>
              </div>
              <div class="ocr-item">
                <span class="ocr-label">Sixth College</span>
                <span class="ocr-coords">(32.8822, -117.2345)</span>
              </div>
              <div class="ocr-item">
                <span class="ocr-label">Trolley Station</span>
                <span class="ocr-coords">(32.5242, -117.1355)</span>
              </div>
              <div class="ocr-item">
                <span class="ocr-label">Center Hall</span>
                <span class="ocr-coords">(32.8740, -117.2410)</span>
              </div>
            </div>
          </div>
        </div>
        <div class="vis-caption">
          OCR technology extracts building names and locations from campus maps
        </div>
      </div>
    `;
  }
  
  // Campus-Specific Geocoding Visualization (Step 3)
  function createGeocodingVis() {
    const container = document.getElementById('geocoding-vis');
    if (!container) return;
    
    container.innerHTML = `
      <div class="vis-container">
        <h3>Custom Geocoding Database</h3>
        <div class="geocoding-db-demo">
          <div class="campus-map-mini">
            <!-- Campus outline -->
            <div class="campus-outline"></div>
            
            <!-- Location pins -->
            <div class="location-pin" style="top: 25%; left: 40%;" data-name="Geisel Library"></div>
            <div class="location-pin" style="top: 35%; left: 60%;" data-name="Price Center"></div>
            <div class="location-pin" style="top: 50%; left: 25%;" data-name="Sixth College"></div>
            <div class="location-pin" style="top: 70%; left: 55%;" data-name="Center Hall"></div>
            <div class="location-pin" style="top: 40%; left: 75%;" data-name="Central Campus Station"></div>
          </div>
          
          <div class="geocode-database">
            <div class="db-header">
              <div class="db-title">Campus Location Database</div>
            </div>
            <div class="db-body">
              <pre>{
    "Geisel Library": {
      "lat": 32.8810,
      "lng": -117.2370,
      "address": "Geisel Library, UC San Diego"
    },
    "Price Center": {
      "lat": 32.8794,
      "lng": -117.2359,
      "address": "Price Center, UC San Diego"
    },
    "Warren College": {
      "lat": 32.8822,
      "lng": -117.2345,
      "address": "Warren College, UC San Diego"
    },
    "Pepper Canyon": {
      "lat": 32.8782,
      "lng": -117.2392,
      "address": "Pepper Canyon, UC San Diego"
    }
  }</pre>
            </div>
          </div>
        </div>
        <div class="vis-caption">
          Our custom database maps campus-specific locations to precise coordinates
        </div>
      </div>
    `;
    
    // Add interactive behavior
    const locationPins = container.querySelectorAll('.location-pin');
    const dbBody = container.querySelector('.db-body pre');
    const originalText = dbBody.innerHTML;
    
    locationPins.forEach(pin => {
      pin.addEventListener('mouseenter', () => {
        const locationName = pin.getAttribute('data-name');
        
        // Highlight corresponding entry in database
        const highlightedText = originalText.replace(
          `"${locationName}": {`,
          `"<span class="highlight">${locationName}</span>": {`
        );
        dbBody.innerHTML = highlightedText;
      });
      
      pin.addEventListener('mouseleave', () => {
        dbBody.innerHTML = originalText;
      });
    });
  }
  
  // LLM Comparison Visualization
  function createLLMComparisonVis() {
    const container = document.getElementById('llm-comparison-vis');
    if (!container) return;
    
    container.innerHTML = `
      <div class="vis-container">
        <h3>LLM Geocoding Accuracy Comparison</h3>
        <div class="llm-comparison-chart">
          <div class="comparison-table">
            <table>
              <thead>
                <tr>
                  <th>Location Description</th>
                  <th>Deepseek R1</th>
                  <th>GPT-o1</th>
                  <th>Mistral Large</th>
                  <th>ArcGIS</th>
                </tr>
              </thead>
              <tbody>
                <tr>
                  <td>"Geisel Library UCSD"</td>
                  <td class="accuracy high">97%</td>
                  <td class="accuracy high">95%</td>
                  <td class="accuracy high">96%</td>
                  <td class="accuracy high">94%</td>
                </tr>
                <tr>
                  <td>"Near the coffee cart at Warren"</td>
                  <td class="accuracy high">94%</td>
                  <td class="accuracy medium">86%</td>
                  <td class="accuracy high">91%</td>
                  <td class="accuracy low">23%</td>
                </tr>
                <tr>
                  <td>"Parking lot P103"</td>
                  <td class="accuracy high">93%</td>
                  <td class="accuracy medium">87%</td>
                  <td class="accuracy medium">85%</td>
                  <td class="accuracy low">15%</td>
                </tr>
                <tr>
                  <td>"Behind Revelle College"</td>
                  <td class="accuracy high">90%</td>
                  <td class="accuracy medium">82%</td>
                  <td class="accuracy medium">84%</td>
                  <td class="accuracy low">21%</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>
        <div class="vis-caption">
          Comparison of geocoding accuracy across different models for campus-specific locations
        </div>
      </div>
    `;
  }
  
  // Real-Time Processing Visualization (Step 4)
  function createRealtimeVis() {
    const container = document.getElementById('realtime-vis');
    if (!container) return;
    
    container.innerHTML = `
      <div class="vis-container">
        <h3>Real-Time Processing Pipeline</h3>
        <div class="data-pipeline-demo">
          <div class="pipeline-node">
            <div class="node-icon">🌐</div>
            <div class="node-label">UCSD Alerts Endpoint</div>
          </div>
          <div class="pipeline-arrow">⟶</div>
          
          <div class="pipeline-node">
            <div class="node-icon">🤖</div>
            <div class="node-label">Web Scraper</div>
          </div>
          <div class="pipeline-arrow">⟶</div>
          
          <div class="pipeline-node">
            <div class="node-icon">📝</div>
            <div class="node-label">Text Processing</div>
          </div>
          <div class="pipeline-arrow">⟶</div>
          
          <div class="pipeline-node">
            <div class="node-icon">🗺️</div>
            <div class="node-label">Geocoding Module</div>
          </div>
          <div class="pipeline-arrow">⟶</div>
          
          <div class="pipeline-node">
            <div class="node-icon">💾</div>
            <div class="node-label">Database Storage</div>
          </div>
          <div class="pipeline-arrow">⟶</div>
          
          <div class="pipeline-node">
            <div class="node-icon">📊</div>
            <div class="node-label">Visualization Engine</div>
          </div>
        </div>
        <div class="vis-caption">
          Automated pipeline processes alerts from scraping to visualization
        </div>
      </div>
    `;
    
    // Add animation to highlight each node sequentially
    let currentNodeIndex = 0;
    const nodes = container.querySelectorAll('.pipeline-node');
    
    function highlightNextNode() {
      // Reset all nodes
      nodes.forEach(node => node.classList.remove('active'));
      
      // Highlight current node
      nodes[currentNodeIndex].classList.add('active');
      
      // Move to next node
      currentNodeIndex = (currentNodeIndex + 1) % nodes.length;
      
      setTimeout(highlightNextNode, 2000);
    }
    
    // Start the animation
    setTimeout(highlightNextNode, 1000);
  }
  
  // Interactive Visualization Demo (Step 5)
  function createDataVisualizationVis() {
    const container = document.getElementById('visualization-vis');
    if (!container) return;
    
    container.innerHTML = `
      <div class="vis-container">
        <h3>Interactive Alert Map</h3>
        <div class="map-interface-demo">
          <div class="map-header">
            <div class="map-title">UCSD Campus Alerts</div>
            <div class="map-controls">
              <select class="map-filter">
                <option>All Alerts</option>
                <option>Timely Warnings</option>
                <option>Triton Alerts</option>
              </select>
            </div>
          </div>
          <div class="map-body">
            <!-- Demo map with incident markers -->
            <div class="demo-map">
              <div class="map-marker violent" style="top: 30%; left: 40%;" data-type="Assault"></div>
              <div class="map-marker property" style="top: 50%; left: 60%;" data-type="Burglary"></div>
              <div class="map-marker property" style="top: 70%; left: 30%;" data-type="Theft"></div>
              <div class="map-marker other" style="top: 40%; left: 75%;" data-type="Suspicious Activity"></div>
              
              <!-- Popup that shows when marker is clicked -->
              <div class="map-popup" style="top: 25%; left: 40%; display: none;">
                <div class="popup-header">Assault at Geisel Library</div>
                <div class="popup-body">
                  <p><strong>Date:</strong> 2/15/2025</p>
                  <p><strong>Time:</strong> 10:30 PM</p>
                  <p><strong>Location:</strong> Near the east entrance</p>
                  <div class="alert-type violent">Violent Crime</div>
                </div>
              </div>
            </div>
            
            <div class="map-sidebar">
              <div class="sidebar-header">Recent Alerts</div>
              <div class="alert-list">
                <div class="alert-item">
                  <div class="alert-title">Assault at Geisel Library</div>
                  <div class="alert-meta">2/15/2025 • Timely Warning</div>
                </div>
                <div class="alert-item">
                  <div class="alert-title">Burglary at Warren College</div>
                  <div class="alert-meta">2/10/2025 • Timely Warning</div>
                </div>
                <div class="alert-item">
                  <div class="alert-title">Theft at Price Center</div>
                  <div class="alert-meta">2/5/2025 • Community Alert</div>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="vis-caption">
          Interactive map interface with filtering and detailed information
        </div>
      </div>
    `;
    
    // Add interactivity for markers and popup
    const mapMarkers = container.querySelectorAll('.map-marker');
    const mapPopup = container.querySelector('.map-popup');
    const alertItems = container.querySelectorAll('.alert-item');
    
    mapMarkers.forEach(marker => {
      marker.addEventListener('click', () => {
        // Update popup position and content
        mapPopup.style.top = `${parseFloat(marker.style.top) - 10}%`;
        mapPopup.style.left = marker.style.left;
        
        // Update popup content based on marker type
        const crimeType = marker.getAttribute('data-type');
        const popupHeader = mapPopup.querySelector('.popup-header');
        popupHeader.textContent = `${crimeType} at Location`;
        
        // Show popup
        mapPopup.style.display = 'block';
        
        // Highlight marker
        mapMarkers.forEach(m => m.classList.remove('active'));
        marker.classList.add('active');
      });
    });
    
    alertItems.forEach(item => {
      item.addEventListener('click', () => {
        mapPopup.style.display = 'block';
        alertItems.forEach(i => i.classList.remove('active'));
        item.classList.add('active');
      });
    });
  }
  
  // Dashboard Visualization
  function createDashboardVis() {
    const container = document.getElementById('dashboard-vis');
    if (!container) return;
    
    container.innerHTML = `
      <div class="vis-container">
        <h3>Dashboard Analytics</h3>
        <div class="dashboard-preview">
          <div class="dashboard-header">
            <div class="dashboard-title">UCSD Safety Analytics</div>
            <div class="dashboard-controls">
              <div class="dashboard-control">Filter</div>
              <div class="dashboard-control">Export</div>
            </div>
          </div>
          <div class="dashboard-body">
            <div class="dashboard-map">
              <!-- Mini campus map with data points -->
              <div class="map-markers">
                <!-- Sample markers representing incidents -->
                <div class="mini-marker violent" style="top: 30%; left: 40%;"></div>
                <div class="mini-marker property" style="top: 50%; left: 60%;"></div>
                <div class="mini-marker violent" style="top: 40%; left: 20%;"></div>
                <div class="mini-marker other" style="top: 70%; left: 30%;"></div>
                <div class="mini-marker property" style="top: 40%; left: 75%;"></div>
                <div class="mini-marker other" style="top: 60%; left: 50%;"></div>
              </div>
            </div>
            <div class="dashboard-sidebar">
              <div class="sidebar-section">
                <div class="sidebar-title">Alert Statistics</div>
                <div class="sidebar-content">
                  <div class="stat-item">
                    <span class="stat-label">Total Alerts:</span>
                    <span class="stat-value">156</span>
                  </div>
                  <div class="stat-item">
                    <span class="stat-label">Violent Crime:</span>
                    <span class="stat-value">32</span>
                  </div>
                  <div class="stat-item">
                    <span class="stat-label">Property Crime:</span>
                    <span class="stat-value">78</span>
                  </div>
                </div>
              </div>
              <div class="sidebar-section">
                <div class="sidebar-title">Trend Analysis</div>
                <div class="chart-placeholder">
                  Incident Trend Chart
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="vis-caption">
          Our dashboard provides real-time analytics on campus safety trends
        </div>
      </div>
    `;
  }
  
  // Add the rest of the visualization functions
  function createPrivacyVis() {
    const container = document.getElementById('privacy-vis');
    if (!container) return;
    
    container.innerHTML = `
      <div class="vis-container">
        <h3>Privacy & Security Framework</h3>
        <div class="security-framework-demo">
          <div class="security-layers">
            <div class="security-layer" id="layer-https">
              <div class="layer-label">HTTPS Encryption</div>
            </div>
            <div class="security-layer" id="layer-access">
              <div class="layer-label">Access Control</div>
            </div>
            <div class="security-layer" id="layer-sanitization">
              <div class="layer-label">Data Sanitization</div>
            </div>
            <div class="security-core">
              <div class="core-label">Alert Data</div>
            </div>
          </div>
          
          <div class="security-details">
            <div class="security-item">
              <div class="item-header">Security Layers</div>
              <div class="item-body">
                Our system implements multiple security layers to protect sensitive information while making alert data accessible to the community. From encryption to data sanitization, each layer plays a crucial role in ensuring privacy and security.
              </div>
            </div>
          </div>
        </div>
        <div class="vis-caption">
          Layered security approach protects data while maintaining accessibility
        </div>
      </div>
    `;
  }
  
  function createMistralVis() {
    const container = document.getElementById('mistral-vis');
    if (!container) return;
    
    container.innerHTML = `
      <div class="vis-container">
        <h3>AI-Powered Geocoding</h3>
        <div class="llm-geocoding-demo">
          <div class="llm-process">
            <div class="process-step active">
              <div class="step-number">1</div>
              <div class="step-content">
                <div class="step-header">Location Input</div>
                <div class="step-body">
                  <div class="input-text">"near the coffee cart at Warren Mall"</div>
                </div>
              </div>
            </div>
            
            <div class="process-connector">⟶</div>
            
            <div class="process-step">
              <div class="step-number">2</div>
              <div class="step-content">
                <div class="step-header">Mistral LLM Processing</div>
                <div class="step-body">
                  <div class="llm-processing">
                    <div class="processing-animation">
                      <div class="processing-dot"></div>
                      <div class="processing-dot"></div>
                      <div class="processing-dot"></div>
                    </div>
                    <div class="processing-text">Analyzing context and location entities...</div>
                  </div>
                </div>
              </div>
            </div>
            
            <div class="process-connector">⟶</div>
            
            <div class="process-step">
              <div class="step-number">3</div>
              <div class="step-content">
                <div class="step-header">Structured Output</div>
                <div class="step-body">
                  <pre class="output-json">{
    "location": "near the coffee cart at Warren Mall",
    "name": "BCB Coffee Cart",
    "address": "BCB Coffee Cart, Warren Mall, UC San Diego",
    "lat": 32.8822,
    "lng": -117.2345
  }</pre>
                </div>
              </div>
            </div>
          </div>
        </div>
        <div class="vis-caption">
          Mistral LLM interprets complex location descriptions for precise geocoding
        </div>
      </div>
    `;
  }
  
  function createAPIVis() {
    const container = document.getElementById('api-vis');
    if (!container) return;
    
    container.innerHTML = `
      <div class="vis-container">
        <h3>REST API Architecture</h3>
        <div class="api-example">
          <div class="example-header">API Request Example</div>
          <div class="example-body">
            <div class="example-url">GET /api/crimes?alert_types=Timely+Warning&date_from=01/01/2025</div>
            <div class="example-response">
              <pre>{
    "type": "FeatureCollection",
    "features": [{
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [-117.235, 32.882]
      },
      "properties": {
        "title": "Burglary at Warren College",
        "date": "01/15/2025",
        "alert_type": "Timely Warning",
        "crime_type": "Burglary"
      }
    }]
  }</pre>
            </div>
          </div>
        </div>
        <div class="vis-caption">
          Flexible API architecture enables integration with external applications
        </div>
      </div>
    `;
  }

  function createNLPFutureVis() {
    const container = document.getElementById('nlp-future-vis');
    if (!container) return;
    
    container.innerHTML = `
      <div class="vis-container">
        <h3>Advanced NLP Processing</h3>
        <div style="width: 100%; background-color: rgba(30, 30, 30, 0.7); border-radius: 8px; overflow: hidden; border: 1px solid rgba(212, 175, 55, 0.3); padding: 15px;">
          <div style="font-family: monospace; padding: 10px; background-color: rgba(10, 10, 10, 0.3); border-radius: 4px; margin-bottom: 15px;">
            "The incident occurred <span style="background-color: rgba(255, 205, 0, 0.2); color: #ffe066; padding: 0 3px; border-radius: 3px;">200 feet northwest</span> of <span style="background-color: rgba(61, 220, 151, 0.2); color: #7dedb6; padding: 0 3px; border-radius: 3px;">Geisel Library</span>"
          </div>
          <div style="margin-top: 15px; text-align: center;">
            <div style="display: inline-block; background-color: rgba(255, 205, 0, 0.2); color: #ffe066; padding: 2px 8px; border-radius: 12px; margin: 5px; font-size: 0.8rem;">Direction Recognition</div>
            <div style="display: inline-block; background-color: rgba(61, 220, 151, 0.2); color: #7dedb6; padding: 2px 8px; border-radius: 12px; margin: 5px; font-size: 0.8rem;">Landmark Recognition</div>
          <div style="display: inline-block; background-color: rgba(255, 73, 92, 0.2); color: #ff8c96; padding: 2px 8px; border-radius: 12px; margin: 5px; font-size: 0.8rem;">Distance Calculation</div>
        </div>
      </div>
      <div class="vis-caption">
        Next-generation NLP features extract spatial relationships from natural language
      </div>
    </div>
  `;
}
  
  function createSanDiegoIntegrationVis() {
    const container = document.getElementById('sd-integration-vis');
    if (!container) return;
    
    container.innerHTML = `
      <div class="vis-container">
        <h3>San Diego Expansion</h3>
        <div class="sd-map">
          <div style="width: 100%; height: 250px; background-color: #2a2a2a; border-radius: 8px; position: relative; overflow: hidden; border: 1px solid rgba(212, 175, 55, 0.3);">
            <div style="position: absolute; top: 15%; left: 20%; width: 15%; height: 15%; border-radius: 50%; background-color: rgba(212, 175, 55, 0.3); box-shadow: 0 0 20px rgba(212, 175, 55, 0.2);">
              <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 0.8rem; color: white;">UCSD</div>
            </div>
            <div style="position: absolute; top: 25%; left: 25%; width: 20%; height: 20%; border-radius: 50%; background-color: rgba(212, 175, 55, 0.15);">
              <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 0.8rem; color: white;">La Jolla</div>
            </div>
            <div style="position: absolute; top: 60%; left: 55%; width: 12%; height: 12%; border-radius: 50%; background-color: rgba(212, 175, 55, 0.08);">
              <div style="position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); font-size: 0.8rem; color: white;">Downtown</div>
            </div>
          </div>
        </div>
        <div class="vis-caption">
          Phased expansion from UCSD campus to the broader San Diego region
        </div>
      </div>
    `;
  }
  
  // API Development Visualization (Step 8)
  function createAPIVis() {
    const container = document.getElementById('api-vis');
    if (!container) return;
    
    container.innerHTML = `
      <div class="vis-container">
        <h3>REST API Architecture</h3>
        <div class="api-architecture-demo">
          <div class="api-diagram">
            <!-- External Applications -->
            <div class="api-section" id="external-apps">
              <div class="section-header"></div>
              <div class="section-body">
                <div class="app-icon"></div>
                <div class="app-icon"></div>
                <div class="app-icon"></div>
              </div>
            </div>
            
            <!-- API Layer -->
            <div class="api-arrows down">
              <div class="arrow"></div>
              <div class="arrow"></div>
              <div class="arrow"></div>
            </div>
            
            <div class="api-section" id="api-layer">
              <div class="section-header">API Endpoints</div>
              <div class="section-body api-endpoints">
                <div class="endpoint"></div>
                <div class="endpoint"></div>
                <div class="endpoint">-range</div>
              </div>
            </div>
            
            <!-- Core Systems -->
            <div class="api-arrows down">
              <div class="arrow"></div>
              <div class="arrow"></div>
              <div class="arrow"></div>
            </div>
            
            <div class="api-section" id="core-systems">
              <div class="section-header"></div>
              <div class="section-body">
                <div class="system-item"></div>
                <div class="system-item"></div>
                <div class="system-item"></div>
              </div>
            </div>
          </div>
          
          <div class="api-example">
            <div class="example-header">API Request Example</div>
            <div class="example-body">
              <div class="example-url">GET /api/crimes?alert_types=Timely+Warning&date_from=01/01/2025</div>
              <div class="example-response">
                <pre>{
    "type": "FeatureCollection",
    "features": [{
      "type": "Feature",
      "geometry": {
        "type": "Point",
        "coordinates": [-117.235, 32.882]
      },
      "properties": {
        "title": "Burglary at Warren College",
        "date": "01/15/2025",
        "alert_type": "Timely Warning",
        "crime_type": "Burglary"
      }
    }]
  }</pre>
              </div>
            </div>
          </div>
        </div>
        <div class="vis-caption">
          Flexible API architecture enables integration with external applications
        </div>
      </div>
    `;
    
    // Add animation for data flow
    function animateAPIDataFlow() {
      const apiArrows = container.querySelectorAll('.api-arrows .arrow');
      
      apiArrows.forEach((arrow, index) => {
        setTimeout(() => {
          arrow.classList.add('pulse');
          setTimeout(() => {
            arrow.classList.remove('pulse');
          }, 1000);
        }, index * 300);
      });
      
      setTimeout(animateAPIDataFlow, 3000);
    }
    
    // Highlight different endpoints
    function rotateAPIEndpoints() {
      const endpoints = container.querySelectorAll('.endpoint');
      const currentActive = container.querySelector('.endpoint.active');
      const currentIndex = currentActive ? Array.from(endpoints).indexOf(currentActive) : -1;
      const nextIndex = (currentIndex + 1) % endpoints.length;
      
      endpoints.forEach(ep => ep.classList.remove('active'));
      endpoints[nextIndex].classList.add('active');
      
      setTimeout(rotateAPIEndpoints, 2000);
    }
    
    animateAPIDataFlow();
    rotateAPIEndpoints();}
    function createRoadmapVis() {
        const container = document.getElementById('integration-roadmap-vis');
        if (!container) return;
        
        container.innerHTML = `
          <div class="vis-container">
            <h3>Development Roadmap</h3>
            <div style="width: 100%; background-color: rgba(30, 30, 30, 0.7); border-radius: 8px; overflow: hidden; border: 1px solid rgba(212, 175, 55, 0.3); padding: 15px;">
              <div style="display: flex; flex-direction: column; gap: 15px;">
                <div style="display: flex; align-items: center; gap: 10px;">
                  <div style="width: 16px; height: 16px; border-radius: 50%; background-color: var(--secondary); box-shadow: 0 0 10px rgba(212, 175, 55, 0.5);"></div>
                  <div style="font-weight: 500; color: var(--secondary);">Phase 1: Core Platform (Current)</div>
                </div>
                <div style="display: flex; align-items: center; gap: 10px;">
                  <div style="width: 16px; height: 16px; border-radius: 50%; background-color: rgba(212, 175, 55, 0.3); border: 2px solid rgba(212, 175, 55, 0.5);"></div>
                  <div style="font-weight: 500; color: var(--secondary);">Phase 2: Expansion (Q2 2025)</div>
                </div>
                <div style="display: flex; align-items: center; gap: 10px;">
                  <div style="width: 16px; height: 16px; border-radius: 50%; background-color: rgba(212, 175, 55, 0.3); border: 2px solid rgba(212, 175, 55, 0.5);"></div>
                  <div style="font-weight: 500; color: var(--secondary);">Phase 3: San Diego-Wide (Q4 2025)</div>
                </div>
                <div style="display: flex; align-items: center; gap: 10px;">
                  <div style="width: 16px; height: 16px; border-radius: 50%; background-color: rgba(212, 175, 55, 0.3); border: 2px solid rgba(212, 175, 55, 0.5);"></div>
                  <div style="font-weight: 500; color: var(--secondary);">Phase 4: Advanced Features (2026)</div>
                </div>
              </div>
            </div>
            <div class="vis-caption">
              Phased development approach with continuous expansion of capabilities
            </div>
          </div>
        `;
      }
      function createConclusionVis() {
        const container = document.getElementById('conclusion-vis');
        if (!container) return;
        
        container.innerHTML = `
          <div class="vis-container">
            <h3>Project Vision</h3>
            <div style="width: 150px; height: 150px; margin: 0 auto 20px; position: relative;">
              <div style="position: absolute; top: 0; left: 0; width: 100%; height: 100%; border-radius: 50%; background-color: rgba(212, 175, 55, 0.1); animation: pulsate 3s ease-out infinite;"></div>
              <div style="position: absolute; top: 10%; left: 10%; width: 80%; height: 80%; border-radius: 50%; background-color: rgba(212, 175, 55, 0.15); animation: pulsate 3s ease-out infinite 0.5s;"></div>
              <div style="position: absolute; top: 20%; left: 20%; width: 60%; height: 60%; border-radius: 50%; background-color: rgba(212, 175, 55, 0.2); animation: pulsate 3s ease-out infinite 1s;"></div>
              <div style="position: absolute; top: 30%; left: 30%; width: 40%; height: 40%; border-radius: 50%; background-color: rgba(212, 175, 55, 0.3); display: flex; align-items: center; justify-content: center; font-size: 1.5rem;">🔍</div>
            </div>
            <div style="text-align: center; font-size: 1.1rem; margin-bottom: 15px; color: var(--secondary);">Democratizing Safety Intelligence</div>
            <div class="vis-caption">
              Creating tools that empower communities through accessible safety awareness
            </div>
          </div>
        `;
      }
      
      // Initialize everything when DOM is loaded
      document.addEventListener('DOMContentLoaded', function() {
        initProcessVisualizations();
        
        // Add event listeners for any interactive elements
        addEventListeners();
      });
      
      // Add any additional event listeners for interactive elements
      function addEventListeners() {
        // Add hover effects for location pins
        const locationPins = document.querySelectorAll('.location-pin');
        locationPins.forEach(pin => {
          pin.addEventListener('mouseenter', () => {
            pin.style.transform = 'translate(-50%, -50%) scale(1.5)';
            pin.style.boxShadow = '0 0 20px rgba(212, 175, 55, 0.8)';
          });
          
          pin.addEventListener('mouseleave', () => {
            pin.style.transform = 'translate(-50%, -50%)';
            pin.style.boxShadow = '0 0 10px rgba(212, 175, 55, 0.5)';
          });
        });
        
        // Add click effects for map markers
        const mapMarkers = document.querySelectorAll('.map-marker');
        mapMarkers.forEach(marker => {
          marker.addEventListener('click', () => {
            // Reset all markers
            mapMarkers.forEach(m => m.classList.remove('active'));
            // Highlight clicked marker
            marker.classList.add('active');
          });
        });
      }
      
      // Helper function for animation
      function animateCSS(element, animation, prefix = 'animate__') {
        return new Promise((resolve, reject) => {
          const animationName = `${prefix}${animation}`;
          
          element.classList.add(`${prefix}animated`, animationName);
          
          function handleAnimationEnd(event) {
            event.stopPropagation();
            element.classList.remove(`${prefix}animated`, animationName);
            resolve('Animation ended');
          }
          
          element.addEventListener('animationend', handleAnimationEnd, {once: true});
        });
      }
