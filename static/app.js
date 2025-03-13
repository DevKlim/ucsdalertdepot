// static/app.js
document.addEventListener('DOMContentLoaded', function() {
    // Sidebar toggle
    const sidebar = document.getElementById('sidebar');
    const toggleSidebarBtn = document.getElementById('toggleSidebar');
    const closeSidebarBtn = document.getElementById('closeSidebar');
    
    if (toggleSidebarBtn) {
      toggleSidebarBtn.addEventListener('click', function() {
        sidebar.style.display = sidebar.style.display === 'none' ? 'block' : 'none';
      });
    }
    
    if (closeSidebarBtn) {
      closeSidebarBtn.addEventListener('click', function() {
        sidebar.style.display = 'none';
      });
    }
    
    // Toggle scraping functionality - Only execute this block if the button exists
    const toggleScrapingBtn = document.getElementById('toggleScraping');
    if (toggleScrapingBtn) {
      const statusIndicator = toggleScrapingBtn.querySelector('.status-indicator');
      
      toggleScrapingBtn.addEventListener('click', function() {
        fetch('/toggle_scraping')
          .then(response => response.json())
          .then(data => {
            if (statusIndicator) {
              statusIndicator.className = data.scraping_enabled ? 
                'status-indicator status-on' : 
                'status-indicator status-off';
            }
            
            const status = data.scraping_enabled ? "enabled" : "disabled";
            const toast = document.createElement('div');
            toast.className = 'toast';
            toast.textContent = `Data scraping is now ${status}`;
            document.body.appendChild(toast);
            
            setTimeout(() => {
              toast.remove();
            }, 3000);
          })
          .catch(err => console.error("Error toggling scraping:", err));
      });
    }
    
    // Initialize the map
    // Initialize the map with a MapBox style that shows buildings
    // const map = new maplibregl.Map({
    //     container: 'map',
    //     style: 'mapbox://styles/mapbox/streets-v11', // This format works with a valid token
    //     center: [-117.2340, 32.8801],
    //     zoom: 15,
    //     maxZoom: 19,
    //     minZoom: 12,
    //     accessToken: 'pk.eyJ1IjoiZ2xhemVkZG9uMHQiLCJhIjoiY203OXNzNnFsMDhwNjJrb2w1aW83NHZkOCJ9.12PWM4MHEGlYYWYuQNk9GQ' // Add your token here
    //   }); // pk.eyJ1IjoiZ2xhemVkZG9uMHQiLCJhIjoiY203OXNzNnFsMDhwNjJrb2w1aW83NHZkOCJ9.12PWM4MHEGlYYWYuQNk9GQ
    
    // Alternative using MapTiler (requires MapTiler account but has a free tier)
    const map = new maplibregl.Map({
      container: 'map',
      style: 'https://api.maptiler.com/maps/streets/style.json?key=461GbvnST4uBqnwn5GDZ',
      center: [-117.2340, 32.8801],
      zoom: 14,
      maxZoom: 19,
      minZoom: 12
    });
    
    // Alternative using OpenStreetMap data with Stadia Maps (no API key required)
    // const map = new maplibregl.Map({
    //   container: 'map',
    //   style: 'https://tiles.stadiamaps.com/styles/osm_bright.json',
    //   center: [-117.2340, 32.8801],
    //   zoom: 14,
    //   maxZoom: 19,
    //   minZoom: 12
    // });
    
    // Add 3D building extrusion layer (works with MapBox style)
    map.on('styledata', function() {
        // Check if the style has already loaded
        if (!map.getLayer('3d-buildings')) {
        // Wait for the map style to finish loading
        if (map.isStyleLoaded()) {
            // Add 3D building extrusion layer
            map.addLayer({
            'id': '3d-buildings',
            'source': 'composite',
            'source-layer': 'building',
            'filter': ['==', 'extrude', 'true'],
            'type': 'fill-extrusion',
            'minzoom': 15,
            'paint': {
                'fill-extrusion-color': '#aaa',
                'fill-extrusion-height': [
                'interpolate', ['linear'], ['zoom'],
                15, 0,
                15.05, ['get', 'height']
                ],
                'fill-extrusion-base': [
                'interpolate', ['linear'], ['zoom'],
                15, 0,
                15.05, ['get', 'min_height']
                ],
                'fill-extrusion-opacity': 0.6
            }
            }, labelLayerId);
        }
        }
    });
    
    // Add zoom and rotation controls
    map.addControl(new maplibregl.NavigationControl(), 'top-left');
    
    // Add fullscreen control
    map.addControl(new maplibregl.FullscreenControl(), 'top-left');
    
    // Add geolocation control
    map.addControl(new maplibregl.GeolocateControl({
      positionOptions: {
        enableHighAccuracy: true
      },
      trackUserLocation: true
    }), 'top-left');
    
    // Add scale control to help users understand distances
    map.addControl(new maplibregl.ScaleControl({
      maxWidth: 150,
      unit: 'imperial' // Can be set to 'metric' or 'imperial'
    }), 'bottom-left');
    
    // Global state for filters and data
    const state = {
      allData: null,
      filteredData: null,
      crimeTypes: new Set(),
      alertTypes: ['Timely Warning', 'Triton Alert', 'Community Alert Bulletin', 'Other'],
      dateRange: {
        from: null,
        to: null
      },
      filters: {
        alertTypes: new Set(['Timely Warning', 'Triton Alert', 'Community Alert Bulletin', 'Other']),
        crimeTypes: new Set(),
        dateFrom: null,
        dateTo: null
      }
    };
    
    // Crime category mapping for colors
    const crimeCategories = {
      violent: [
        'Robbery', 'Assault', 'Battery', 'Sexual Assault', 'Sexual Battery',
        'Rape', 'Domestic Violence', 'Hate Crime', 'Homicide', 'Aggravated Assault'
      ],
      property: [
        'Burglary', 'Theft', 'Auto Theft', 'Bike Theft', 'Vandalism',
        'Breaking and Entering', 'Shoplifting'
      ],
      other: [
        'Suspicious Activity', 'Disorderly Conduct', 'Trespassing', 'Drug Violation',
        'Alcohol Violation', 'Weapons Violation', 'Fire', 'Medical Emergency', 'Unspecified'
      ]
    };
    
    function getCrimeCategory(crimeType) {
      if (!crimeType) return 'other';
      
      const lowerCrime = crimeType.toLowerCase();
      
      // Check in violent crimes
      if (crimeCategories.violent.some(crime => 
        lowerCrime.includes(crime.toLowerCase()))) {
        return 'violent';
      }
      
      // Check in property crimes
      if (crimeCategories.property.some(crime => 
        lowerCrime.includes(crime.toLowerCase()))) {
        return 'property';
      }
      
      // Default to other
      return 'other';
    }
    
    function getCrimeColor(crimeType) {
      const category = getCrimeCategory(crimeType);
      
      switch(category) {
        case 'violent':
          return '#FF495C'; // Red
        case 'property':
          return '#FFCD00'; // Yellow
        default:
          return '#3DDC97'; // Green
      }
    }
    
    // Format date to MM/DD/YYYY
    function formatDate(dateStr) {
      const date = new Date(dateStr);
      return `${date.getMonth() + 1}/${date.getDate()}/${date.getFullYear()}`;
    }
    
    // Parse MM/DD/YYYY to Date object
    function parseDate(dateStr) {
      if (!dateStr) return null;
      const parts = dateStr.split('/');
      if (parts.length === 3) {
        const month = parseInt(parts[0], 10) - 1; // 0-based month
        const day = parseInt(parts[1], 10);
        const year = parseInt(parts[2], 10);
        return new Date(year, month, day);
      }
      return null;
    }
    
    // Filter data based on current filter state
    function filterData() {
      if (!state.allData) return;
      
      state.filteredData = {
        type: "FeatureCollection",
        features: state.allData.features.filter(feature => {
          const props = feature.properties;
          
          // Filter by alert type
          if (!state.filters.alertTypes.has(props.alert_type)) {
            return false;
          }
          
          // Filter by crime type if any are selected
          if (state.filters.crimeTypes.size > 0 && 
              !state.filters.crimeTypes.has(props.crime_type)) {
            return false;
          }
          
          // Filter by date range
          const alertDate = parseDate(props.date);
          if (alertDate) {
            if (state.filters.dateFrom && alertDate < state.filters.dateFrom) {
              return false;
            }
            if (state.filters.dateTo && alertDate > state.filters.dateTo) {
              return false;
            }
          }
          
          return true;
        })
      };
      
      // Update map data source
      if (map.getSource('crimeData')) {
        map.getSource('crimeData').setData(state.filteredData);
      }
      
      // Update recent alerts sidebar
      updateRecentAlerts();
    }
    
    // Update the recent alerts list in the sidebar
    function updateRecentAlerts() {
      const alertsList = document.getElementById('recent-alerts');
      if (!alertsList) return;
      
      alertsList.innerHTML = '';
      
      if (!state.filteredData || !state.filteredData.features.length) {
        alertsList.innerHTML = '<div class="alert-item">No alerts match your filters</div>';
        return;
      }
      
      // Sort by date (newest first)
      const sortedFeatures = [...state.filteredData.features]
        .sort((a, b) => {
          const dateA = parseDate(a.properties.date);
          const dateB = parseDate(b.properties.date);
          return dateB - dateA;
        })
        .slice(0, 5); // Show only 5 most recent
      
      sortedFeatures.forEach(feature => {
        const props = feature.properties;
        const alertEl = document.createElement('div');
        alertEl.className = 'alert-item';
        
        alertEl.innerHTML = `
          <h4>${props.title}</h4>
          <p>${props.date} - ${props.crime_type}</p>
        `;
        
        // Click to fly to the location
        alertEl.addEventListener('click', () => {
          map.flyTo({
            center: feature.geometry.coordinates,
            zoom: 17
          });
          
          // Open popup
          new maplibregl.Popup()
            .setLngLat(feature.geometry.coordinates)
            .setHTML(createPopupHTML(props))
            .addTo(map);
        });
        
        alertsList.appendChild(alertEl);
      });
    }
    
    // Create HTML content for popups
    function createPopupHTML(props) {
        // Determine severity class based on crime type
        const category = getCrimeCategory(props.crime_type);
        let severityClass = 'severity-low';
        if (category === 'violent') {
          severityClass = 'severity-high';
        } else if (category === 'property') {
          severityClass = 'severity-medium';
        }
        
        // Location information - prioritize address display
        const locationDisplay = `
          <div class="location-info">
            <p><strong>Location:</strong> ${props.location_text}</p>
            ${props.address ? `<p><strong>Address:</strong> ${props.address}</p>` : ''}
            ${props.precise_location && props.precise_location !== props.location_text && props.precise_location !== props.address ? 
              `<p><strong>Precise Location:</strong> ${props.precise_location}</p>` : ''}
          </div>
        `;
        
        return `
          <div class="popup-content">
            <h3>${props.title}</h3>
            <div class="tags">
              <span class="tag ${severityClass}">${props.crime_type}</span>
              <span class="tag">${props.alert_type}</span>
            </div>
            <p><strong>Date:</strong> ${props.date}</p>
            ${locationDisplay}
            <p><strong>Suspect Info:</strong> ${props.suspect_info || 'Not specified'}</p>
            ${props.details_url ? `<a href="${props.details_url}" class="details-link" target="_blank">View Full Details</a>` : ''}
          </div>
        `;
      }
    
    // Set up crime type filter checkboxes
    function setupCrimeTypeFilters() {
      const container = document.getElementById('crime-type-filters');
      if (!container) return;
      
      container.innerHTML = '';
      
      // Sort crime types alphabetically
      const sortedCrimeTypes = Array.from(state.crimeTypes).sort();
      
      sortedCrimeTypes.forEach(crimeType => {
        const checkboxDiv = document.createElement('div');
        checkboxDiv.className = 'filter-checkbox';
        
        const id = `filter-crime-${crimeType.replace(/\s+/g, '-').toLowerCase()}`;
        
        checkboxDiv.innerHTML = `
          <input type="checkbox" id="${id}" value="${crimeType}">
          <label for="${id}">${crimeType}</label>
        `;
        
        const checkbox = checkboxDiv.querySelector('input');
        
        // Set up event listener
        checkbox.addEventListener('change', function() {
          if (this.checked) {
            state.filters.crimeTypes.add(crimeType);
          } else {
            state.filters.crimeTypes.delete(crimeType);
          }
          filterData();
        });
        
        container.appendChild(checkboxDiv);
      });
    }
    
    // Set up alert type filter checkboxes
    function setupAlertTypeFilters() {
      // Set up event listeners for alert type checkboxes
      const timely = document.getElementById('filter-timely-warning');
      const triton = document.getElementById('filter-triton-alert');
      const community = document.getElementById('filter-community-alert');
      const other = document.getElementById('filter-other-alert');
      
      if (timely) {
        timely.addEventListener('change', function() {
          toggleAlertTypeFilter('Timely Warning', this.checked);
        });
      }
      
      if (triton) {
        triton.addEventListener('change', function() {
          toggleAlertTypeFilter('Triton Alert', this.checked);
        });
      }
      
      if (community) {
        community.addEventListener('change', function() {
          toggleAlertTypeFilter('Community Alert Bulletin', this.checked);
        });
      }
      
      if (other) {
        other.addEventListener('change', function() {
          toggleAlertTypeFilter('Other', this.checked);
        });
      }
    }
    
    function toggleAlertTypeFilter(alertType, isChecked) {
      if (isChecked) {
        state.filters.alertTypes.add(alertType);
      } else {
        state.filters.alertTypes.delete(alertType);
      }
      filterData();
    }
    
    // Set up date range filters
    function setupDateFilters() {
      const dateFromInput = document.getElementById('date-from');
      const dateToInput = document.getElementById('date-to');
      
      if (dateFromInput) {
        dateFromInput.addEventListener('change', function() {
          const dateValue = this.value ? new Date(this.value) : null;
          state.filters.dateFrom = dateValue;
          filterData();
        });
      }
      
      if (dateToInput) {
        dateToInput.addEventListener('change', function() {
          const dateValue = this.value ? new Date(this.value) : null;
          // Set time to end of day for inclusive filtering
          if (dateValue) {
            dateValue.setHours(23, 59, 59, 999);
          }
          state.filters.dateTo = dateValue;
          filterData();
        });
      }
    }
    
    // Reset all filters
    const resetFiltersBtn = document.getElementById('reset-filters');
    if (resetFiltersBtn) {
      resetFiltersBtn.addEventListener('click', function() {
        // Reset alert type filters
        const timely = document.getElementById('filter-timely-warning');
        const triton = document.getElementById('filter-triton-alert');
        const community = document.getElementById('filter-community-alert');
        const other = document.getElementById('filter-other-alert');
        
        if (timely) timely.checked = true;
        if (triton) triton.checked = true;
        if (community) community.checked = true;
        if (other) other.checked = true;
        
        // Reset crime type filters
        const crimeCheckboxes = document.querySelectorAll('#crime-type-filters input');
        crimeCheckboxes.forEach(checkbox => {
          checkbox.checked = false;
        });
        
        // Reset date filters
        const dateFromInput = document.getElementById('date-from');
        const dateToInput = document.getElementById('date-to');
        
        if (dateFromInput) dateFromInput.value = '';
        if (dateToInput) dateToInput.value = '';
        
        // Reset state filters
        state.filters.alertTypes = new Set(['Timely Warning', 'Triton Alert', 'Community Alert Bulletin', 'Other']);
        state.filters.crimeTypes = new Set();
        state.filters.dateFrom = null;
        state.filters.dateTo = null;
        
        // Apply filters
        filterData();
      });
    }
    
    // Find loading indicator if it exists
    const loadingIndicator = document.querySelector('.map-loading');
    
    // Load the crime data and initialize map
    map.on('load', () => {
      // Show loading indicator if it exists
      if (loadingIndicator) {
        loadingIndicator.classList.remove('hidden');
      }
      
      // Fetch crime data from API
      fetch('/api/crimes')
        .then(response => response.json())
        .then(data => {
          // Hide loading indicator
          if (loadingIndicator) {
            loadingIndicator.classList.add('hidden');
          }
          
          // Store the data
          state.allData = data;
          state.filteredData = data;
          
          // Extract unique crime types for filters
          data.features.forEach(feature => {
            if (feature.properties.crime_type) {
              state.crimeTypes.add(feature.properties.crime_type);
            }
          });
          
          // Setup filters
          setupCrimeTypeFilters();
          setupAlertTypeFilters();
          setupDateFilters();
          
          // Add source to map
          map.addSource('crimeData', {
            type: 'geojson',
            data: data
          });
          
          // Add layer for crime points
          map.addLayer({
            id: 'crime-circles',
            type: 'circle',
            source: 'crimeData',
            paint: {
              'circle-radius': [
                'interpolate', ['linear'], ['zoom'],
                14, 5,
                19, 10
              ],
              'circle-color': [
                'case',
                ['in', ['get', 'crime_type'], ['literal', crimeCategories.violent]],
                '#FF495C', // Violent crimes (red)
                ['in', ['get', 'crime_type'], ['literal', crimeCategories.property]],
                '#FFCD00', // Property crimes (yellow)
                '#3DDC97' // Other (green)
              ],
              'circle-opacity': 0.8,
              'circle-stroke-width': 1,
              'circle-stroke-color': '#fff'
            }
          });
          
          // Add layer for crime labels
          map.addLayer({
            id: 'crime-labels',
            type: 'symbol',
            source: 'crimeData',
            minzoom: 16, // Only show labels at higher zoom levels
            layout: {
              'text-field': ['get', 'crime_type'],
              'text-size': 12,
              'text-font': ['Open Sans Regular'],
              'text-offset': [0, 1.5],
              'text-anchor': 'top'
            },
            paint: {
              'text-color': '#333',
              'text-halo-color': '#fff',
              'text-halo-width': 1
            }
          });
          
          // Handle click events on crime points
          map.on('click', 'crime-circles', (e) => {
            if (!e.features.length) return;
            
            const feature = e.features[0];
            const props = feature.properties;
            const coordinates = feature.geometry.coordinates.slice();
            
            // Create a popup
            new maplibregl.Popup()
              .setLngLat(coordinates)
              .setHTML(createPopupHTML(props))
              .addTo(map);
          });
          
          // Change cursor on hover
          map.on('mouseenter', 'crime-circles', () => {
            map.getCanvas().style.cursor = 'pointer';
          });
          
          map.on('mouseleave', 'crime-circles', () => {
            map.getCanvas().style.cursor = '';
          });
          
          // Update recent alerts list
          updateRecentAlerts();
        })
        .catch(err => {
          console.error("Error fetching crime data:", err);
          // Update loading indicator to show error if it exists
          if (loadingIndicator) {
            loadingIndicator.innerHTML = '<span>Error loading data. Please refresh the page.</span>';
          } else {
            alert("Failed to load crime data. Please refresh the page to try again.");
          }
        });
    });
    
    // Add fit bounds button to show entire campus
    const ucsdBounds = [
      [-117.2520, 32.8650], // Southwest corner
      [-117.2150, 32.8950]  // Northeast corner
    ];
  
    // Create custom control for the fit bounds button
    class FitBoundsControl {
      onAdd(map) {
        this._map = map;
        this._container = document.createElement('div');
        this._container.className = 'maplibregl-ctrl maplibregl-ctrl-group';
        
        const fitBoundsButton = document.createElement('button');
        fitBoundsButton.className = 'maplibregl-ctrl-icon maplibregl-ctrl-fitbounds';
        fitBoundsButton.type = 'button';
        fitBoundsButton.title = 'Fit to UCSD Campus';
        fitBoundsButton.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="3" width="18" height="18" rx="2" ry="2"></rect><line x1="9" y1="3" x2="9" y2="21"></line><line x1="15" y1="3" x2="15" y2="21"></line><line x1="3" y1="9" x2="21" y2="9"></line><line x1="3" y1="15" x2="21" y2="15"></line></svg>';
        
        this._container.appendChild(fitBoundsButton);
        
        fitBoundsButton.addEventListener('click', () => {
          map.fitBounds(ucsdBounds, {
            padding: 50
          });
        });
        
        return this._container;
      }
  
      onRemove() {
        this._container.parentNode.removeChild(this._container);
        this._map = undefined;
      }
    }
  
    // Add the custom fit bounds control
    map.addControl(new FitBoundsControl(), 'top-left');
    
    // Add custom CSS for toast notifications
    const style = document.createElement('style');
    style.textContent = `
      .toast {
        position: fixed;
        bottom: 20px;
        left: 50%;
        transform: translateX(-50%);
        background-color: rgba(0, 0, 0, 0.8);
        color: white;
        padding: 12px 24px;
        border-radius: 4px;
        z-index: 1000;
        animation: fadeInOut 3s ease;
      }
      
      @keyframes fadeInOut {
        0% { opacity: 0; }
        10% { opacity: 1; }
        90% { opacity: 1; }
        100% { opacity: 0; }
      }
      
      .maplibregl-ctrl-icon.maplibregl-ctrl-fitbounds {
        background-color: #fff;
        border: none;
        border-radius: 4px;
        cursor: pointer;
        display: block;
        padding: 5px;
        width: 30px;
        height: 30px;
      }
  
      .maplibregl-ctrl-icon.maplibregl-ctrl-fitbounds svg {
        width: 20px;
        height: 20px;
        display: block;
      }
  
      .maplibregl-ctrl-icon.maplibregl-ctrl-fitbounds:hover {
        background-color: #f0f0f0;
      }
    `;
    document.head.appendChild(style);
  });

  function addAlertMarkers(map, alerts) {
    // Clear existing markers...
    
    alerts.forEach(alert => {
      // Determine marker color...
      
      // Create popup with offset to prevent jumping
      const popup = new maplibregl.Popup({
        closeButton: false,
        closeOnClick: true,
        maxWidth: '300px',
        className: 'custom-popup',
        offset: [0, -15], // This offset prevents the popup from appearing under cursor
        anchor: 'bottom'
      }).setHTML(/* your popup content */);
      
      // Create marker element
      const el = document.createElement('div');
      el.className = 'custom-marker';
      // Style your marker here...
      
      // Handle hover events
      el.onmouseover = function() {
        this.style.transform = 'scale(1.2)';
        popup.addTo(map); // Add popup on hover
      };
      
      el.onmouseout = function() {
        this.style.transform = 'scale(1)';
        popup.remove(); // Remove popup when not hovering
      };
      
      // Create marker
      const marker = new maplibregl.Marker({
        element: el,
        anchor: 'center'
      })
      .setLngLat([alert.lng, alert.lat])
      .addTo(map);
      
      // Store popup with marker for reference
      marker.getElement()._popup = popup;
      marker.getElement()._popupLngLat = [alert.lng, alert.lat];
      
      // Optional: Add click handler for toggling popup
      marker.getElement().addEventListener('click', function(e) {
        e.stopPropagation();
        // Toggle popup logic...
      });
    });
  }