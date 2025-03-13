// static/simple-geoswitcher.js
// Simplified version of the geocoding service switcher

document.addEventListener('DOMContentLoaded', function() {
  console.log('Simple GeoSwitcher loaded');
  
  // Try to find the sidebar or filters section
  setTimeout(initGeoSwitcher, 1000); // Delay initialization to ensure the page has loaded
});

// Initialize the Geo Switcher
function initGeoSwitcher() {
  console.log('Initializing Geo Switcher');
  
  // Find a place to put our controls
  const sidebar = document.querySelector('.sidebar') || 
                  document.querySelector('#map-controls') || 
                  document.querySelector('.filters');
  
  if (!sidebar) {
      console.warn('Could not find sidebar. Creating floating control panel.');
      createFloatingPanel();
      return;
  }
  
  // Create the geocoding controls
  const geoControls = document.createElement('div');
  geoControls.className = 'geo-controls';
  geoControls.innerHTML = `
      <h3 style="margin-top: 20px; border-top: 1px solid rgba(255,255,255,0.2); padding-top: 15px;">
          Geocoding Services
      </h3>
      <p style="font-size: 14px; margin-bottom: 10px;">
          Try different geocoding services to see how they place locations on the map.
      </p>
      <div class="geo-service-list" style="margin-bottom: 15px;">
          <p style="font-style: italic;">Loading services...</p>
      </div>
      <div class="geo-actions" style="display: flex; gap: 10px; margin-bottom: 15px;">
          <button id="apply-geo-service" style="padding: 8px 12px; background-color: #1976d2; color: white; border: none; border-radius: 4px; cursor: pointer;">
              Apply Selected Service
          </button>
          <button id="restore-geo-original" style="padding: 8px 12px; background-color: #424242; color: white; border: none; border-radius: 4px; cursor: pointer;">
              Restore Original
          </button>
      </div>
  `;
  
  // Add the controls to the sidebar
  sidebar.appendChild(geoControls);
  
  // Load the available geocoding services
  loadGeocodingServices();
  
  // Add event listeners
  document.getElementById('apply-geo-service').addEventListener('click', applySelectedService);
  document.getElementById('restore-geo-original').addEventListener('click', restoreOriginalGeocoding);
}

// Create a floating panel if no sidebar is found
function createFloatingPanel() {
  const panel = document.createElement('div');
  panel.className = 'floating-geo-panel';
  panel.style.cssText = `
      position: absolute;
      top: 20px;
      right: 20px;
      width: 300px;
      background-color: rgba(0, 0, 0, 0.8);
      color: white;
      padding: 15px;
      border-radius: 5px;
      z-index: 1000;
      box-shadow: 0 2px 10px rgba(0, 0, 0, 0.3);
  `;
  
  panel.innerHTML = `
      <h3 style="margin-top: 0; margin-bottom: 15px;">Geocoding Services</h3>
      <p style="font-size: 14px; margin-bottom: 10px;">
          Try different geocoding services to see how they place locations on the map.
      </p>
      <div class="geo-service-list" style="margin-bottom: 15px;">
          <p style="font-style: italic;">Loading services...</p>
      </div>
      <div class="geo-actions" style="display: flex; gap: 10px; margin-bottom: 15px;">
          <button id="apply-geo-service" style="padding: 8px 12px; background-color: #1976d2; color: white; border: none; border-radius: 4px; cursor: pointer;">
              Apply Selected Service
          </button>
          <button id="restore-geo-original" style="padding: 8px 12px; background-color: #424242; color: white; border: none; border-radius: 4px; cursor: pointer;">
              Restore Original
          </button>
      </div>
  `;
  
  document.body.appendChild(panel);
  
  // Load the available geocoding services
  loadGeocodingServices();
  
  // Add event listeners
  document.getElementById('apply-geo-service').addEventListener('click', applySelectedService);
  document.getElementById('restore-geo-original').addEventListener('click', restoreOriginalGeocoding);
}

// Load the available geocoding services
function loadGeocodingServices() {
  fetch('/api/geocoding-metadata')
      .then(response => {
          if (!response.ok) {
              throw new Error('Failed to fetch geocoding services');
          }
          return response.json();
      })
      .then(data => {
          updateServiceList(data.services);
      })
      .catch(error => {
          console.error('Error loading geocoding services:', error);
          const serviceList = document.querySelector('.geo-service-list');
          if (serviceList) {
              serviceList.innerHTML = `
                  <p style="color: #ff6b6b;">Error loading services. Please check the console.</p>
              `;
          }
      });
}

// Update the service list with available services
function updateServiceList(services) {
  const serviceList = document.querySelector('.geo-service-list');
  if (!serviceList) return;
  
  // Create radio buttons for each service
  let html = '';
  
  services.forEach(service => {
      const isChecked = service.id === 'current' ? 'checked' : '';
      
      html += `
          <div style="margin-bottom: 10px; display: flex; align-items: flex-start;">
              <input type="radio" id="geo-service-${service.id}" name="geo-service" value="${service.id}" ${isChecked}>
              <label for="geo-service-${service.id}" style="margin-left: 8px; cursor: pointer;">
                  <div style="font-weight: bold; color: gold;">${service.name}</div>
                  <div style="font-size: 12px; color: #ccc;">${service.description}</div>
              </label>
          </div>
      `;
  });
  
  serviceList.innerHTML = html;
}

// Apply the selected service
function applySelectedService() {
  const selectedService = document.querySelector('input[name="geo-service"]:checked');
  if (!selectedService) {
      showNotification('Please select a service first', 'error');
      return;
  }
  
  const serviceId = selectedService.value;
  
  // Disable the button while processing
  const applyButton = document.getElementById('apply-geo-service');
  const originalText = applyButton.textContent;
  applyButton.textContent = 'Applying...';
  applyButton.disabled = true;
  
  // Call the API to apply the service
  fetch(`/api/apply-geocoding/${serviceId}`, {
      method: 'POST'
  })
      .then(response => {
          if (!response.ok) {
              throw new Error('Failed to apply service');
          }
          return response.json();
      })
      .then(data => {
          showNotification(`Applied ${serviceId} geocoding service. Reloading map...`, 'success');
          
          // Reload the page to see the changes
          setTimeout(() => {
              window.location.reload();
          }, 1500);
      })
      .catch(error => {
          console.error('Error applying service:', error);
          showNotification('Error applying service', 'error');
          
          // Re-enable the button
          applyButton.textContent = originalText;
          applyButton.disabled = false;
      });
}

// Restore the original geocoding
function restoreOriginalGeocoding() {
  // Disable the button while processing
  const restoreButton = document.getElementById('restore-geo-original');
  const originalText = restoreButton.textContent;
  restoreButton.textContent = 'Restoring...';
  restoreButton.disabled = true;
  
  // Call the API to restore the original geocoding
  fetch('/api/restore-geocoding', {
      method: 'POST'
  })
      .then(response => {
          if (!response.ok) {
              throw new Error('Failed to restore original geocoding');
          }
          return response.json();
      })
      .then(data => {
          showNotification('Restored original geocoding. Reloading map...', 'success');
          
          // Reload the page to see the changes
          setTimeout(() => {
              window.location.reload();
          }, 1500);
      })
      .catch(error => {
          console.error('Error restoring original geocoding:', error);
          showNotification('Error restoring original geocoding', 'error');
          
          // Re-enable the button
          restoreButton.textContent = originalText;
          restoreButton.disabled = false;
      });
}

// Show a notification
function showNotification(message, type = 'info') {
  // Create or get the notification element
  let notification = document.querySelector('.geo-notification');
  if (!notification) {
      notification = document.createElement('div');
      notification.className = 'geo-notification';
      notification.style.cssText = `
          position: fixed;
          top: 20px;
          right: 20px;
          padding: 12px 16px;
          border-radius: 4px;
          color: white;
          z-index: 9999;
          display: none;
          box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
          font-size: 14px;
      `;
      document.body.appendChild(notification);
  }
  
  // Set the message and type
  notification.textContent = message;
  
  // Set the background color based on the type
  if (type === 'success') {
      notification.style.backgroundColor = 'rgba(46, 125, 50, 0.9)';
  } else if (type === 'error') {
      notification.style.backgroundColor = 'rgba(198, 40, 40, 0.9)';
  } else {
      notification.style.backgroundColor = 'rgba(33, 150, 243, 0.9)';
  }
  
  // Show the notification
  notification.style.display = 'block';
  
  // Hide after a few seconds
  setTimeout(() => {
      notification.style.display = 'none';
  }, 3000);
}