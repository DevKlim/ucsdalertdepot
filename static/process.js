// static/process.js

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    // Initialize the scrollama
    initScrollama();
    
    // Initialize visualizations
    initVisualizations();
    
    // Set up smooth scrolling
    initSmoothScrolling();
  });
  
  // Initialize scrollama instance
  function initScrollama() {
    // Initialize the scrollama
    const scroller = scrollama();
    
    // Setup the instance, pass callback functions
    scroller
      .setup({
        step: '.step',
        offset: 0.5,
        debug: false
      })
      .onStepEnter(handleStepEnter)
      .onStepExit(handleStepExit);
    
    // Handle window resize
    window.addEventListener('resize', scroller.resize);
  }
  
  // Callback for scrollama step enter
  function handleStepEnter(response) {
    // Add 'is-active' class to the current step
    response.element.classList.add('is-active');
    
    // Update the visualization based on the current step
    updateVisualization(response.index, response.direction, response.element.dataset.step);
  }
  
  // Callback for scrollama step exit
  function handleStepExit(response) {
    // Remove 'is-active' class from the exited step
    response.element.classList.remove('is-active');
  }
  
  // Create and manage visualizations for each step
  function initVisualizations() {
    const visualizationContainer = document.getElementById('visualization');
    
    // Create visualizations for each step
    const visualizations = [
      createChallengeVis(),      // Challenge visualization
      createOCRVis(),            // OCR visualization
      createGeocodingVis(),      // Geocoding visualization
      createRealtimeVis(),       // Real-time data vis
      createDataVis(),           // Data visualization
      createPrivacyVis(),        // Privacy & security vis
      createComparisonVis(),     // Comparison vis
      createDevelopmentVis(),    // Development process
      createMistralVis(),        // Mistral LLM vis
      createFutureVis(),         // Future expansion
      createTechStackVis(),      // Tech stack
      createConclusionVis()      // Conclusion
    ];
    
    // Add all visualizations to the container
    visualizations.forEach(vis => {
      visualizationContainer.appendChild(vis);
    });
  }
  
  // Update which visualization is currently visible
  function updateVisualization(index, direction, stepId) {
    // Hide all visualizations
    const allVisualizations = document.querySelectorAll('.visualization-content');
    allVisualizations.forEach(vis => vis.classList.remove('active'));
    
    // Show the current visualization based on step ID
    const currentVis = document.querySelector(`.vis-${stepId}`);
    if (currentVis) {
      currentVis.classList.add('active');
    }
  }
  
  // Create visualization for Challenge step
  function createChallengeVis() {
    const vis = document.createElement('div');
    vis.className = 'visualization-content vis-challenge';
    
    // Create a mock geocoding failure illustration
    const content = document.createElement('div');
    content.innerHTML = `
      <div style="text-align: center; max-width: 90%;">
        <div style="font-size: 1.5rem; margin-bottom: 1rem; color: var(--secondary);">
          Geocoding Failures on Campus
        </div>
        <div style="position: relative; width: 100%; height: 300px; background-color: rgba(30, 30, 30, 0.7); border-radius: 8px; margin-bottom: 1rem; border: 1px solid rgba(212, 175, 55, 0.3); overflow: hidden;">
          <div style="position: absolute; top: 10px; left: 10px; font-family: monospace; color: var(--light); font-size: 0.9rem; max-width: 90%;">
            <div>Geocoding "Price Center, UCSD"...</div>
            <div style="color: #FF5555; margin-top: 5px;">ERROR: Location not found</div>
            <div style="margin-top: 20px;">Geocoding "Geisel Library"...</div>
            <div style="color: #FF5555; margin-top: 5px;">ERROR: Ambiguous location (multiple results)</div>
            <div style="margin-top: 20px;">Geocoding "Pepper Canyon Apartments"...</div>
            <div style="color: #FF5555; margin-top: 5px;">ERROR: Location not found</div>
            <div style="margin-top: 20px;">Geocoding "Warren Mall"...</div>
            <div style="color: #FF5555; margin-top: 5px;">ERROR: No results</div>
          </div>
        </div>
        <div style="font-style: italic; opacity: 0.7; font-size: 0.9rem;">
          Standard geocoding services fail to recognize most campus-specific locations
        </div>
      </div>
    `;
    
    vis.appendChild(content);
    return vis;
  }
  
  // Create visualization for OCR step
  function createOCRVis() {
    const vis = document.createElement('div');
    vis.className = 'visualization-content vis-ocr';
    
    // Add OCR scanning animation
    const scanOverlay = document.createElement('div');
    scanOverlay.style.position = 'absolute';
    scanOverlay.style.top = '0';
    scanOverlay.style.left = '0';
    scanOverlay.style.width = '100%';
    scanOverlay.style.height = '100%';
    scanOverlay.style.zIndex = '2';
    
    // Create scan line
    const scanLine = document.createElement('div');
    scanLine.style.position = 'absolute';
    scanLine.style.top = '0';
    scanLine.style.left = '0';
    scanLine.style.width = '100%';
    scanLine.style.height = '2px';
    scanLine.style.backgroundColor = 'var(--secondary)';
    scanLine.style.boxShadow = '0 0 10px var(--secondary), 0 0 20px var(--secondary)';
    scanLine.style.animation = 'scanMove 3s infinite';
    
    // Create style for scan animation
    const scanStyle = document.createElement('style');
    scanStyle.textContent = `
      @keyframes scanMove {
        0% { top: 0; }
        100% { top: 100%; }
      }
    `;
    
    // Add text overlay with detected building names
    const textOverlay = document.createElement('div');
    textOverlay.style.position = 'absolute';
    textOverlay.style.top = '20px';
    textOverlay.style.right = '20px';
    textOverlay.style.width = '180px';
    textOverlay.style.backgroundColor = 'rgba(10, 10, 10, 0.8)';
    textOverlay.style.borderRadius = '8px';
    textOverlay.style.padding = '15px';
    textOverlay.style.fontFamily = 'monospace';
    textOverlay.style.fontSize = '0.8rem';
    textOverlay.style.color = 'var(--light)';
    textOverlay.style.border = '1px solid rgba(212, 175, 55, 0.3)';
    
    textOverlay.innerHTML = `
      <div style="margin-bottom: 5px; color: var(--secondary);">Detected Labels:</div>
      <div style="margin-bottom: 3px;">• Geisel Library</div>
      <div style="margin-bottom: 3px;">• Price Center</div>
      <div style="margin-bottom: 3px;">• Warren College</div>
      <div style="margin-bottom: 3px;">• Pepper Canyon</div>
      <div style="margin-bottom: 3px;">• RIMAC Field</div>
      <div style="margin-bottom: 3px;">• Revelle College</div>
      <div style="margin-bottom: 3px;">• Library Walk</div>
      <div style="color: var(--secondary); margin-top: 10px;">Extracting coordinates...</div>
    `;
    
    document.head.appendChild(scanStyle);
    scanOverlay.appendChild(scanLine);
    vis.appendChild(scanOverlay);
    vis.appendChild(textOverlay);
    
    return vis;
  }
  
  // Create visualization for Geocoding step
  function createGeocodingVis() {
    const vis = document.createElement('div');
    vis.className = 'visualization-content vis-geocoding';
    
    const mapPreview = document.createElement('div');
    mapPreview.className = 'map-preview';
    
    // Add the map overlay effect
    const overlay = document.createElement('div');
    overlay.className = 'map-overlay';
    mapPreview.appendChild(overlay);
    
    // Add pins to the map
    const pins = [
      { top: '30%', left: '40%', label: 'Geisel Library' },
      { top: '35%', left: '55%', label: 'Price Center' },
      { top: '25%', left: '70%', label: 'Revelle College' },
      { top: '45%', left: '35%', label: 'Warren College' },
      { top: '60%', left: '50%', label: 'Pepper Canyon' }
    ];
    
    pins.forEach((pin, index) => {
      const mapPin = document.createElement('div');
      mapPin.className = 'map-pin';
      mapPin.style.top = pin.top;
      mapPin.style.left = pin.left;
      
      // Add label
      const label = document.createElement('div');
      label.style.position = 'absolute';
      label.style.top = '25px';
      label.style.left = '0';
      label.style.transform = 'translateX(-50%)';
      label.style.whiteSpace = 'nowrap';
      label.style.backgroundColor = 'rgba(10, 10, 10, 0.8)';
      label.style.padding = '3px 8px';
      label.style.borderRadius = '4px';
      label.style.fontSize = '0.7rem';
      label.style.color = 'var(--light)';
      label.style.fontWeight = 'bold';
      label.textContent = pin.label;
      
      mapPin.appendChild(label);
      mapPreview.appendChild(mapPin);
      
      // Stagger the animation slightly
      setTimeout(() => {
        mapPin.style.animation = 'ping 1.5s cubic-bezier(0, 0, 0.2, 1) infinite';
      }, index * 300);
    });
    
    vis.appendChild(mapPreview);
    
    // Add caption
    const caption = document.createElement('div');
    caption.style.marginTop = '2rem';
    caption.style.textAlign = 'center';
    caption.style.color = 'var(--secondary)';
    caption.style.maxWidth = '80%';
    caption.textContent = 'Custom campus-specific geocoding database with precise coordinates';
    vis.appendChild(caption);
    
    return vis;
  }
  
  // Create visualization for Real-time data step
  function createRealtimeVis() {
    const vis = document.createElement('div');
    vis.className = 'visualization-content vis-realtime';
    
    const dataFlow = document.createElement('div');
    dataFlow.className = 'data-flow-diagram';
    
    // Create flow nodes
    const nodes = [
      { label: 'UCSD Police Website', icon: '🔍' },
      { label: 'Web Scraper', icon: '🤖' },
      { label: 'Text Processing & Location Extraction', icon: '📝' },
      { label: 'Geocoding Module', icon: '📍' },
      { label: 'Database Storage', icon: '💾' },
      { label: 'API Endpoints', icon: '⚙️' },
      { label: 'Interactive Map Display', icon: '🗺️' }
    ];
    
    nodes.forEach(node => {
      const flowNode = document.createElement('div');
      flowNode.className = 'flow-node';
      flowNode.innerHTML = `<span style="font-size: 1.2rem; margin-right: 0.5rem;">${node.icon}</span> ${node.label}`;
      dataFlow.appendChild(flowNode);
    });
    
    // Add flow animation
    for (let i = 0; i < 3; i++) {
      const flowBall = document.createElement('div');
      flowBall.className = 'flow-animation';
      flowBall.style.left = `${30 + (i * 20)}%`;
      flowBall.style.animationDelay = `${i * 1.5}s`;
      dataFlow.appendChild(flowBall);
    }
    
    vis.appendChild(dataFlow);
    return vis;
  }
  
  // Create placeholder visualizations for remaining steps
  function createDataVis() {
    return createPlaceholderVis('visualization', 'Data Visualization', 'Chart showing campus alert trends over time');
  }
  
  function createPrivacyVis() {
    return createPlaceholderVis('privacy', 'Privacy & Security', 'Secure data handling process');
  }
  
  function createComparisonVis() {
    return createPlaceholderVis('comparison', 'System Comparison', 'UCSD Alert Depot vs. Existing Solutions');
  }
  
  function createDevelopmentVis() {
    return createPlaceholderVis('development', 'Development Process', 'Our systematic approach to building the system');
  }
  
  function createMistralVis() {
    return createPlaceholderVis('mistral', 'Mistral LLM Integration', 'Using AI for advanced location parsing');
  }
  
  function createFutureVis() {
    return createPlaceholderVis('future', 'Future Expansion Plans', 'City-wide coverage and advanced features');
  }
  
  function createTechStackVis() {
    return createPlaceholderVis('tech-stack', 'Technology Stack', 'Components powering our solution');
  }
  
  function createConclusionVis() {
    return createPlaceholderVis('conclusion', 'Impact & Results', 'Making campus safety information more accessible');
  }
  
  // Helper to create placeholder visualizations
  function createPlaceholderVis(id, title, subtitle) {
    const vis = document.createElement('div');
    vis.className = `visualization-content vis-${id}`;
    vis.innerHTML = `
      <div style="text-align: center; max-width: 90%;">
        <div style="font-size: 2rem; margin-bottom: 1rem; color: var(--secondary);">
          ${title}
        </div>
        <div style="position: relative; width: 100%; height: 300px; background-color: rgba(30, 30, 30, 0.7); border-radius: 8px; margin-bottom: 1rem; border: 1px solid rgba(212, 175, 55, 0.3); display: flex; align-items: center; justify-content: center;">
          <div style="font-size: 5rem; opacity: 0.3; margin-bottom: 2rem;">🔍</div>
        </div>
        <div style="font-style: italic; opacity: 0.7; font-size: 1.1rem;">
          ${subtitle}
        </div>
      </div>
    `;
    return vis;
  }
  
  // Initialize smooth scrolling
  function initSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
      anchor.addEventListener('click', function (e) {
        e.preventDefault();
        
        document.querySelector(this.getAttribute('href')).scrollIntoView({
          behavior: 'smooth'
        });
      });
    });
  }