// app.js - Fixed version

document.addEventListener('DOMContentLoaded', function() {
  // Initialize the map with alerts data
  fetchAndInitializeMap();
  
  // Set up event listeners for the UI
  setupEventListeners();
  
  // Set up filter functionality
  setupFilters();
});

// Get crime data and initialize map
async function fetchAndInitializeMap() {
  // Show loading indicator
  document.querySelector('.map-loading').style.display = 'block';
  
  try {
    // Fetch crime data from API
    const response = await fetch('/api/crimes');
    if (!response.ok) {
      throw new Error('Network response was not ok');
    }
    const data = await response.json();
    
    // Initialize map with the data
    initializeMap(data);
    
    // Fetch filter options
    fetchFilterOptions();
  } catch (error) {
    console.error('Error fetching data:', error);
    document.querySelector('.map-loading').textContent = 'Error loading data. Please try again later.';
  }
}

// Initialize the map with GeoJSON data
function initializeMap(geojson) {
  // Create the map
  const map = new maplibregl.Map({
    container: 'map',
    style: 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json', // Dark theme style
    center: [-117.2340, 32.8801], // UCSD campus
    zoom: 14,
    maxZoom: 18,
    minZoom: 10
  });
  
  // Add navigation controls
  map.addControl(new maplibregl.NavigationControl(), 'top-right');
  
  // Fix map container size to fit window
  adjustMapSize();
  window.addEventListener('resize', adjustMapSize);
  
  // Handle missing images
  map.on('styleimagemissing', (e) => {
    const id = e.id; // Get the missing image id
    console.log(`Creating placeholder for missing image: ${id}`);
    
    // Create a new blank canvas
    const canvas = document.createElement('canvas');
    canvas.width = 16;
    canvas.height = 16;
    
    // Add a simple colored square as a placeholder
    const ctx = canvas.getContext('2d');
    ctx.fillStyle = '#ffd700'; // Gold color
    ctx.fillRect(0, 0, 16, 16);
    
    // Add the canvas as a new image to the map
    map.addImage(id, canvas);
  });
  
  // Once the map is loaded, add the data
  map.on('load', function() {
    // Hide loading indicator
    document.querySelector('.map-loading').style.display = 'none';
    
    // Add the geojson as a source
    map.addSource('alerts', {
      type: 'geojson',
      data: geojson
    });
    
    // Add a layer to visualize the points
    map.addLayer({
      id: 'alerts-layer',
      type: 'circle',
      source: 'alerts',
      paint: {
        'circle-radius': 8,
        'circle-color': getCrimeColor(),
        'circle-opacity': 0.8,
        'circle-stroke-width': 2,
        'circle-stroke-color': '#ffffff'
      }
    });
    
    // Add click event for popups
    map.on('click', 'alerts-layer', function(e) {
      const properties = e.features[0].properties;
      
      // Create popup content
      const popupContent = `
        <div class="popup-title">${properties.title}</div>
        <div class="popup-date">Date: ${properties.date}</div>
        <div class="popup-location">Location: ${properties.location_text}</div>
        <div class="popup-type ${getCrimeTypeClass(properties.crime_type)}">${properties.crime_type}</div>
        ${properties.suspect_info && properties.suspect_info !== 'Not specified' 
          ? `<div class="popup-suspect">Suspect Info: ${properties.suspect_info}</div>` 
          : ''}
      `;
      
      // Create and display popup
      new maplibregl.Popup({
        closeButton: true,
        closeOnClick: true,
        maxWidth: '300px',
        className: 'custom-popup',
        offset: [0, -10]
      })
      .setLngLat(e.features[0].geometry.coordinates)
      .setHTML(popupContent)
      .addTo(map);
    });
    
    // Change cursor to pointer when hovering over alerts
    map.on('mouseenter', 'alerts-layer', function() {
      map.getCanvas().style.cursor = 'pointer';
    });
    
    map.on('mouseleave', 'alerts-layer', function() {
      map.getCanvas().style.cursor = '';
    });
    
    // Store the map in window for filter access
    window.crimeMap = map;
    window.crimeData = geojson;
    
    // Add crime data to recent alerts panel
    updateRecentAlerts(geojson.features);
  });
}

// Adjust map container size
function adjustMapSize() {
  const mapContainer = document.querySelector('.map-container');
  if (mapContainer) {
    const headerHeight = document.querySelector('header').offsetHeight;
    const windowHeight = window.innerHeight;
    const maxHeight = windowHeight - headerHeight - 40; // 40px for margins
    mapContainer.style.height = `${maxHeight}px`;
  }
}

// Set up event listeners
function setupEventListeners() {
  // Toggle sidebar
  document.getElementById('toggleSidebar').addEventListener('click', function() {
    document.getElementById('sidebar').classList.toggle('open');
  });
  
  // Close sidebar
  document.getElementById('closeSidebar').addEventListener('click', function() {
    document.getElementById('sidebar').classList.remove('open');
  });
  
  // Reset filters
  document.getElementById('reset-filters').addEventListener('click', function() {
    // Reset all filter checkboxes
    document.querySelectorAll('#crime-type-filters input[type="checkbox"]').forEach(checkbox => {
      checkbox.checked = true;
    });
    
    document.querySelectorAll('.filter-checkbox input[type="checkbox"]').forEach(checkbox => {
      checkbox.checked = true;
    });
    
    // Reset date inputs
    document.getElementById('date-from').value = '';
    document.getElementById('date-to').value = '';
    
    // Apply filters (in this case, reset to show all)
    applyFilters();
  });
}

// Set up filter functionality
function setupFilters() {
  // Alert type filter checkboxes
  document.getElementById('filter-timely-warning').addEventListener('change', applyFilters);
  document.getElementById('filter-triton-alert').addEventListener('change', applyFilters);
  document.getElementById('filter-community-alert').addEventListener('change', applyFilters);
  document.getElementById('filter-other-alert').addEventListener('change', applyFilters);
  
  // Date range inputs
  document.getElementById('date-from').addEventListener('change', applyFilters);
  document.getElementById('date-to').addEventListener('change', applyFilters);
}

// Get crime type CSS class
function getCrimeTypeClass(crimeType) {
  if (!crimeType) return 'popup-type-other';
  
  const violentCrimes = ['Assault', 'Battery', 'Sexual Assault', 'Robbery', 'Hate Crime', 'Aggravated Assault'];
  const propertyCrimes = ['Burglary', 'Theft', 'Auto Theft', 'Vandalism', 'Break-in'];
  
  if (violentCrimes.some(crime => crimeType.includes(crime))) {
    return 'popup-type-violent';
  } else if (propertyCrimes.some(crime => crimeType.includes(crime))) {
    return 'popup-type-property';
  } else {
    return 'popup-type-other';
  }
}

// Get color for crime circle based on type
function getCrimeColor() {
  return [
    'match',
    ['get', 'crime_type'],
    // Violent crimes - red
    'Assault', '#FF495C',
    'Sexual Assault', '#FF495C',
    'Robbery', '#FF495C',
    'Battery', '#FF495C',
    'Hate Crime', '#FF495C',
    'Aggravated Assault', '#FF495C',
    
    // Property crimes - gold
    'Burglary', '#FFD700',
    'Theft', '#FFD700',
    'Auto Theft', '#FFD700',
    'Vandalism', '#FFD700',
    'Break-in', '#FFD700',
    
    // Default - green
    '#3DDC97'
  ];
}

// Apply filters to the map
function applyFilters() {
  const map = window.crimeMap;
  if (!map || !window.crimeData) return;
  
  // Get selected alert types
  const alertTypes = [];
  if (document.getElementById('filter-timely-warning').checked) alertTypes.push('Timely Warning');
  if (document.getElementById('filter-triton-alert').checked) alertTypes.push('Triton Alert');
  if (document.getElementById('filter-community-alert').checked) alertTypes.push('Community Alert Bulletin');
  if (document.getElementById('filter-other-alert').checked) alertTypes.push('Other');
  
  // Get selected crime types
  const crimeTypes = [];
  document.querySelectorAll('#crime-type-filters input[type="checkbox"]:checked').forEach(checkbox => {
    crimeTypes.push(checkbox.value);
  });
  
  // Get date range
  const dateFrom = document.getElementById('date-from').value;
  const dateTo = document.getElementById('date-to').value;
  
  // Convert HTML dates to MM/DD/YYYY for API
  const fromDateFormatted = dateFrom ? formatDateForAPI(dateFrom) : null;
  const toDateFormatted = dateTo ? formatDateForAPI(dateTo) : null;
  
  // Build API URL with filters
  let url = '/api/crimes';
  const params = new URLSearchParams();
  
  if (alertTypes.length > 0 && alertTypes.length < 4) {
    alertTypes.forEach(type => params.append('alert_types', type));
  }
  
  if (crimeTypes.length > 0 && crimeTypes.length < document.querySelectorAll('#crime-type-filters input[type="checkbox"]').length) {
    crimeTypes.forEach(type => params.append('crime_types', type));
  }
  
  if (fromDateFormatted) params.append('date_from', fromDateFormatted);
  if (toDateFormatted) params.append('date_to', toDateFormatted);
  
  if (params.toString()) {
    url += '?' + params.toString();
  }
  
  // Fetch filtered data
  fetch(url)
    .then(response => response.json())
    .then(data => {
      // Update the map source
      map.getSource('alerts').setData(data);
      
      // Update recent alerts panel
      updateRecentAlerts(data.features);
    })
    .catch(error => {
      console.error('Error applying filters:', error);
    });
}

// Format date from HTML input (YYYY-MM-DD) to API format (MM/DD/YYYY)
function formatDateForAPI(htmlDate) {
  const parts = htmlDate.split('-');
  if (parts.length !== 3) return null;
  return `${parts[1]}/${parts[2]}/${parts[0]}`;
}

// Fetch filter options (crime types, alert types, date range)
function fetchFilterOptions() {
  // Fetch crime types
  fetch('/api/crime-types')
    .then(response => response.json())
    .then(data => {
      populateCrimeTypeFilters(data.crime_types);
    })
    .catch(error => {
      console.error('Error fetching crime types:', error);
    });
  
  // Fetch date range
  fetch('/api/date-range')
    .then(response => response.json())
    .then(data => {
      // Set min/max dates on date inputs
      if (data.start_date) {
        const startDate = formatDateFromAPI(data.start_date);
        document.getElementById('date-from').min = startDate;
        document.getElementById('date-to').min = startDate;
      }
      
      if (data.end_date) {
        const endDate = formatDateFromAPI(data.end_date);
        document.getElementById('date-from').max = endDate;
        document.getElementById('date-to').max = endDate;
      }
    })
    .catch(error => {
      console.error('Error fetching date range:', error);
    });
}

// Format date from API (MM/DD/YYYY) to HTML input format (YYYY-MM-DD)
function formatDateFromAPI(apiDate) {
  const parts = apiDate.split('/');
  if (parts.length !== 3) return '';
  return `${parts[2]}-${parts[0].padStart(2, '0')}-${parts[1].padStart(2, '0')}`;
}

// Populate crime type filter checkboxes
function populateCrimeTypeFilters(crimeTypes) {
  const container = document.getElementById('crime-type-filters');
  
  // Clear loading placeholder
  container.innerHTML = '';
  
  // Add a checkbox for each crime type
  crimeTypes.forEach(crimeType => {
    const checkbox = document.createElement('div');
    checkbox.className = 'filter-checkbox';
    checkbox.innerHTML = `
      <input type="checkbox" id="filter-crime-${crimeType.replace(/\s+/g, '-').toLowerCase()}" 
             value="${crimeType}" checked>
      <label for="filter-crime-${crimeType.replace(/\s+/g, '-').toLowerCase()}">${crimeType}</label>
    `;
    container.appendChild(checkbox);
    
    // Add event listener to the new checkbox
    checkbox.querySelector('input').addEventListener('change', applyFilters);
  });
}

// Update recent alerts panel
function updateRecentAlerts(features) {
  const container = document.getElementById('recent-alerts');
  
  // Sort by date (newest first)
  const sortedFeatures = [...features].sort((a, b) => {
    const dateA = new Date(convertToISODate(a.properties.date));
    const dateB = new Date(convertToISODate(b.properties.date));
    return dateB - dateA;
  });
  
  // Take only the 5 most recent
  const recentFeatures = sortedFeatures.slice(0, 5);
  
  // Clear container
  container.innerHTML = '';
  
  if (recentFeatures.length === 0) {
    container.innerHTML = '<div class="loading-placeholder">No alerts match current filters</div>';
    return;
  }
  
  // Add each alert
  recentFeatures.forEach(feature => {
    const props = feature.properties;
    const alertItem = document.createElement('div');
    alertItem.className = 'alert-item';
    alertItem.innerHTML = `
      <div class="alert-title">${props.title}</div>
      <div class="alert-meta">
        <span>${props.date}</span>
        <span class="popup-type ${getCrimeTypeClass(props.crime_type)}">${props.crime_type}</span>
      </div>
    `;
    
    // Add click event to center map on this alert
    alertItem.addEventListener('click', function() {
      // Center map on this location
      window.crimeMap.flyTo({
        center: feature.geometry.coordinates,
        zoom: 16,
        essential: true
      });
      
      // Create popup for this alert
      new maplibregl.Popup({
        closeButton: true,
        closeOnClick: true,
        maxWidth: '300px',
        className: 'custom-popup',
        offset: [0, -10]
      })
      .setLngLat(feature.geometry.coordinates)
      .setHTML(`
        <div class="popup-title">${props.title}</div>
        <div class="popup-date">Date: ${props.date}</div>
        <div class="popup-location">Location: ${props.location_text}</div>
        <div class="popup-type ${getCrimeTypeClass(props.crime_type)}">${props.crime_type}</div>
        ${props.suspect_info && props.suspect_info !== 'Not specified' 
          ? `<div class="popup-suspect">Suspect Info: ${props.suspect_info}</div>` 
          : ''}
      `)
      .addTo(window.crimeMap);
    });
    
    container.appendChild(alertItem);
  });
}

// Convert MM/DD/YYYY to ISO date (YYYY-MM-DD)
function convertToISODate(dateStr) {
  const parts = dateStr.split('/');
  if (parts.length !== 3) return dateStr;
  return `${parts[2]}-${parts[0]}-${parts[1]}`;
}