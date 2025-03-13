// app.js - Main JavaScript file for the UCSD Crime Map application

// Global variables

let crimeMap = null;
let alerts = [];
let crimeCounts = {};
let filteredFeatures = [];
let markersVisible = true;
let heatmapVisible = false;
let heatmapLayer = null;
const DEFAULT_LAT = 32.8801;
const DEFAULT_LNG = -117.2340;
const DEFAULT_ZOOM = 14;

// Initialize the map when the page loads
document.addEventListener('DOMContentLoaded', function() {
    // Check if maplibregl is defined
    if (typeof maplibregl === 'undefined') {
        console.error('MapLibre GL JS is not loaded. Please make sure the library is included.');
        return;
    }
    
    // Load the map
    crimeMap = new maplibregl.Map({
        container: 'map',
        style: 'https://demotiles.maplibre.org/style.json', // MapLibre demo style or your custom style
        center: [DEFAULT_LNG, DEFAULT_LAT],
        zoom: DEFAULT_ZOOM
    });
    
    // Add map controls
    crimeMap.addControl(new maplibregl.NavigationControl(), 'top-right');
    
    // Initialize when the map loads
    crimeMap.on('load', function() {
        // Fetch data and initialize the map display
        fetchAndInitializeMap();
        
        // Set up event listeners
        setupEventListeners();
    });
});

// Fetch crime data and initialize the map
async function fetchAndInitializeMap() {
    try {
        // Show loading indicator
        document.getElementById('loading-indicator').style.display = 'block';
        
        // Fetch the data
        const response = await fetch('/api/crimes');
        if (!response.ok) {
            throw new Error('Failed to fetch crime data');
        }
        
        // Parse the response
        const data = await response.json();
        alerts = data.features;
        
        // Process the data
        processAlertData();
        
        // Add the data source to the map
        crimeMap.addSource('alerts', {
            type: 'geojson',
            data: data
        });
        
        // Add a layer for the markers
        crimeMap.addLayer({
            id: 'alert-points',
            type: 'circle',
            source: 'alerts',
            paint: {
                'circle-radius': 6,
                'circle-color': [
                    'match',
                    ['get', 'crime_type'],
                    'Burglary', '#FF5733',
                    'Robbery', '#C70039',
                    'Motor Vehicle Theft', '#900C3F',
                    'Sexual Assault Known Perpetrator', '#581845',
                    'Sexual Battery', '#581845',
                    'Aggravated Assault', '#FFC300',
                    'Arson', '#FF5733',
                    'Weapons Law Violation', '#C70039',
                    'Micromobility Device Theft (Motor Vehicle)', '#FFC300',
                    'Sexual Battery Unknown Perpetrator', '#581845',
                    '#2874A6' // Default color for other types
                ],
                'circle-opacity': 0.8,
                'circle-stroke-width': 1,
                'circle-stroke-color': '#ffffff'
            }
        });
        
        // Add a layer for heat map (initially hidden)
        createHeatmapLayer();
        
        // Add popup on click
        setupMapPopups();
        
        // Update the filters
        updateFilters();
        
        // Show recent alerts
        updateRecentAlerts(alerts);
        
        // Hide loading indicator
        document.getElementById('loading-indicator').style.display = 'none';
        
    } catch (error) {
        console.error('Error initializing map:', error);
        document.getElementById('loading-indicator').textContent = 'Error loading data';
    }
}

// Process the alert data to extract types and counts
function processAlertData() {
    // Extract all unique crime types
    const crimeTypes = new Set();
    const alertTypes = new Set();
    crimeCounts = {};
    
    alerts.forEach(feature => {
        const props = feature.properties;
        const crimeType = props.crime_type;
        const alertType = props.alert_type;
        
        crimeTypes.add(crimeType);
        alertTypes.add(alertType);
        
        // Count crimes by type
        if (crimeCounts[crimeType]) {
            crimeCounts[crimeType]++;
        } else {
            crimeCounts[crimeType] = 1;
        }
    });
    
    // Update crime type selector
    updateCrimeTypeSelector(Array.from(crimeTypes));
    
    // Update alert type selector
    updateAlertTypeSelector(Array.from(alertTypes));
}

// Update the crime type selector with available types
function updateCrimeTypeSelector(crimeTypes) {
    const crimeTypeFilter = document.getElementById('crime-type-filter');
    if (!crimeTypeFilter) return;
    
    // Clear loading text
    crimeTypeFilter.innerHTML = '';
    
    // Add "All" option
    const allOption = document.createElement('div');
    allOption.className = 'filter-option';
    allOption.innerHTML = `
        <input type="checkbox" id="crime-all" name="crime-type" value="all" checked>
        <label for="crime-all">All Types</label>
    `;
    crimeTypeFilter.appendChild(allOption);
    
    // Sort crime types by count (descending)
    crimeTypes.sort((a, b) => {
        return (crimeCounts[b] || 0) - (crimeCounts[a] || 0);
    });
    
    // Add each crime type
    crimeTypes.forEach(type => {
        if (!type) return; // Skip empty types
        
        const count = crimeCounts[type] || 0;
        const option = document.createElement('div');
        option.className = 'filter-option';
        option.innerHTML = `
            <input type="checkbox" id="crime-${type.replace(/\s+/g, '-').toLowerCase()}" name="crime-type" value="${type}" checked>
            <label for="crime-${type.replace(/\s+/g, '-').toLowerCase()}">${type} (${count})</label>
        `;
        crimeTypeFilter.appendChild(option);
    });
    
    // Add event listeners to checkboxes
    const crimeCheckboxes = document.querySelectorAll('input[name="crime-type"]');
    crimeCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            if (this.value === 'all') {
                // If "All" is clicked, update all other checkboxes
                const checked = this.checked;
                crimeCheckboxes.forEach(cb => {
                    if (cb.value !== 'all') {
                        cb.checked = checked;
                    }
                });
            } else {
                // If individual type is clicked, update the "All" checkbox
                const allChecked = document.getElementById('crime-all');
                const typeCheckboxes = Array.from(document.querySelectorAll('input[name="crime-type"]:not([value="all"])'));
                const allTypesChecked = typeCheckboxes.every(cb => cb.checked);
                const noTypesChecked = typeCheckboxes.every(cb => !cb.checked);
                
                if (allTypesChecked) {
                    allChecked.checked = true;
                    allChecked.indeterminate = false;
                } else if (noTypesChecked) {
                    allChecked.checked = false;
                    allChecked.indeterminate = false;
                } else {
                    allChecked.indeterminate = true;
                }
            }
            
            // Apply filters
            applyFilters();
        });
    });
}

// Update the alert type selector with available types
function updateAlertTypeSelector(alertTypes) {
    const alertTypeFilter = document.getElementById('alert-type-filter');
    if (!alertTypeFilter) return;
    
    // Clear loading text
    alertTypeFilter.innerHTML = '';
    
    // Add "All" option
    const allOption = document.createElement('div');
    allOption.className = 'filter-option';
    allOption.innerHTML = `
        <input type="checkbox" id="alert-all" name="alert-type" value="all" checked>
        <label for="alert-all">All Types</label>
    `;
    alertTypeFilter.appendChild(allOption);
    
    // Add each alert type
    alertTypes.forEach(type => {
        if (!type) return; // Skip empty types
        
        const option = document.createElement('div');
        option.className = 'filter-option';
        option.innerHTML = `
            <input type="checkbox" id="alert-${type.replace(/\s+/g, '-').toLowerCase()}" name="alert-type" value="${type}" checked>
            <label for="alert-${type.replace(/\s+/g, '-').toLowerCase()}">${type}</label>
        `;
        alertTypeFilter.appendChild(option);
    });
    
    // Add event listeners to checkboxes
    const alertCheckboxes = document.querySelectorAll('input[name="alert-type"]');
    alertCheckboxes.forEach(checkbox => {
        checkbox.addEventListener('change', function() {
            if (this.value === 'all') {
                // If "All" is clicked, update all other checkboxes
                const checked = this.checked;
                alertCheckboxes.forEach(cb => {
                    if (cb.value !== 'all') {
                        cb.checked = checked;
                    }
                });
            } else {
                // If individual type is clicked, update the "All" checkbox
                const allChecked = document.getElementById('alert-all');
                const typeCheckboxes = Array.from(document.querySelectorAll('input[name="alert-type"]:not([value="all"])'));
                const allTypesChecked = typeCheckboxes.every(cb => cb.checked);
                const noTypesChecked = typeCheckboxes.every(cb => !cb.checked);
                
                if (allTypesChecked) {
                    allChecked.checked = true;
                    allChecked.indeterminate = false;
                } else if (noTypesChecked) {
                    allChecked.checked = false;
                    allChecked.indeterminate = false;
                } else {
                    allChecked.indeterminate = true;
                }
            }
            
            // Apply filters
            applyFilters();
        });
    });
}

// Set up event listeners for the UI
function setupEventListeners() {
    // View toggle
    const viewToggle = document.getElementById('view-toggle');
    if (viewToggle) {
        viewToggle.addEventListener('change', function() {
            if (this.value === 'markers') {
                showMarkers();
                hideHeatmap();
            } else if (this.value === 'heatmap') {
                hideMarkers();
                showHeatmap();
            } else if (this.value === 'both') {
                showMarkers();
                showHeatmap();
            }
        });
    }
    
    // Date range filter
    const dateFilterBtn = document.getElementById('apply-date-filter');
    if (dateFilterBtn) {
        dateFilterBtn.addEventListener('click', function() {
            applyFilters();
        });
    }
    
    // Reset filters
    const resetBtn = document.getElementById('reset-filters');
    if (resetBtn) {
        resetBtn.addEventListener('click', function() {
            resetFilters();
        });
    }
    
    // Fetch date range
    fetchDateRange();
}

// Setup map popups
function setupMapPopups() {
    // Create a popup but don't add it to the map yet
    const popup = new mapboxgl.Popup({
        closeButton: true,
        closeOnClick: true,
        maxWidth: '300px'
    });
    
    // Show popup on click
    crimeMap.on('click', 'alert-points', function(e) {
        const feature = e.features[0];
        const props = feature.properties;
        
        // Format date
        const date = props.date;
        
        // Create popup content
        const content = `
            <div class="popup-content">
                <h3>${props.title}</h3>
                <p><strong>Date:</strong> ${date}</p>
                <p><strong>Type:</strong> ${props.alert_type}</p>
                <p><strong>Crime:</strong> ${props.crime_type}</p>
                <p><strong>Location:</strong> ${props.location_text}</p>
                ${props.address ? `<p><strong>Address:</strong> ${props.address}</p>` : ''}
                ${props.suspect_info !== 'Not specified' ? `<p><strong>Suspect Info:</strong> ${props.suspect_info}</p>` : ''}
                ${props.geocode_source ? `<p><small>Geocoded by: ${props.geocode_source}</small></p>` : ''}
            </div>
        `;
        
        // Set popup contents and location
        popup
            .setLngLat(feature.geometry.coordinates)
            .setHTML(content)
            .addTo(crimeMap);
    });
    
    // Change cursor to pointer when hovering over a point
    crimeMap.on('mouseenter', 'alert-points', function() {
        crimeMap.getCanvas().style.cursor = 'pointer';
    });
    
    // Change cursor back when leaving a point
    crimeMap.on('mouseleave', 'alert-points', function() {
        crimeMap.getCanvas().style.cursor = '';
    });
}

// Create heatmap layer
function createHeatmapLayer() {
    crimeMap.addLayer({
        id: 'alerts-heat',
        type: 'heatmap',
        source: 'alerts',
        maxzoom: 15,
        paint: {
            // Increase weight based on frequency
            'heatmap-weight': 1,
            // Increase intensity as zoom level increases
            'heatmap-intensity': [
                'interpolate',
                ['linear'],
                ['zoom'],
                0, 1,
                15, 3
            ],
            // Color heatmap based on density
            'heatmap-color': [
                'interpolate',
                ['linear'],
                ['heatmap-density'],
                0, 'rgba(33,102,172,0)',
                0.2, 'rgb(103,169,207)',
                0.4, 'rgb(209,229,240)',
                0.6, 'rgb(253,219,199)',
                0.8, 'rgb(239,138,98)',
                1, 'rgb(178,24,43)'
            ],
            // Adjust radius with zoom level
            'heatmap-radius': [
                'interpolate',
                ['linear'],
                ['zoom'],
                0, 2,
                12, 20,
                15, 30
            ],
            // Opacity based on zoom level
            'heatmap-opacity': 0.7
        }
    }, 'alert-points');
    
    // Initially hide heatmap
    hideHeatmap();
}

// Show markers
function showMarkers() {
    markersVisible = true;
    crimeMap.setLayoutProperty('alert-points', 'visibility', 'visible');
}

// Hide markers
function hideMarkers() {
    markersVisible = false;
    crimeMap.setLayoutProperty('alert-points', 'visibility', 'none');
}

// Show heatmap
function showHeatmap() {
    heatmapVisible = true;
    crimeMap.setLayoutProperty('alerts-heat', 'visibility', 'visible');
}

// Hide heatmap
function hideHeatmap() {
    heatmapVisible = false;
    crimeMap.setLayoutProperty('alerts-heat', 'visibility', 'none');
}

// Apply filters
function applyFilters() {
    // Get selected crime types
    const crimeCheckboxes = document.querySelectorAll('input[name="crime-type"]:checked:not([value="all"])');
    const selectedCrimeTypes = Array.from(crimeCheckboxes).map(cb => cb.value);
    
    // Get selected alert types
    const alertCheckboxes = document.querySelectorAll('input[name="alert-type"]:checked:not([value="all"])');
    const selectedAlertTypes = Array.from(alertCheckboxes).map(cb => cb.value);
    
    // Get date range
    const dateFrom = document.getElementById('date-from').value;
    const dateTo = document.getElementById('date-to').value;
    
    // Build filter query
    let queryParams = [];
    
    if (selectedCrimeTypes.length > 0) {
        const crimeTypesParam = selectedCrimeTypes.map(type => `crime_types=${encodeURIComponent(type)}`).join('&');
        queryParams.push(crimeTypesParam);
    }
    
    if (selectedAlertTypes.length > 0) {
        const alertTypesParam = selectedAlertTypes.map(type => `alert_types=${encodeURIComponent(type)}`).join('&');
        queryParams.push(alertTypesParam);
    }
    
    if (dateFrom) {
        queryParams.push(`date_from=${encodeURIComponent(dateFrom)}`);
    }
    
    if (dateTo) {
        queryParams.push(`date_to=${encodeURIComponent(dateTo)}`);
    }
    
    // Fetch filtered data
    const url = '/api/crimes' + (queryParams.length > 0 ? '?' + queryParams.join('&') : '');
    
    fetch(url)
        .then(response => response.json())
        .then(data => {
            // Update map data source
            crimeMap.getSource('alerts').setData(data);
            
            // Update filtered features
            filteredFeatures = data.features;
            
            // Update recent alerts
            updateRecentAlerts(filteredFeatures);
            
            // Update filter status
            updateFilterStatus(filteredFeatures.length, alerts.length);
        })
        .catch(error => {
            console.error('Error applying filters:', error);
        });
}

// Reset filters to show all data
function resetFilters() {
    // Reset crime type checkboxes
    document.querySelectorAll('input[name="crime-type"]').forEach(cb => {
        cb.checked = true;
    });
    
    // Reset alert type checkboxes
    document.querySelectorAll('input[name="alert-type"]').forEach(cb => {
        cb.checked = true;
    });
    
    // Reset date range
    document.getElementById('date-from').value = '';
    document.getElementById('date-to').value = '';
    
    // Apply filters (which will now show all)
    applyFilters();
}

// Update filter status text
function updateFilterStatus(filteredCount, totalCount) {
    const filterStatus = document.getElementById('filter-status');
    if (filterStatus) {
        if (filteredCount === totalCount) {
            filterStatus.textContent = `Showing all ${totalCount} alerts`;
        } else {
            filterStatus.textContent = `Showing ${filteredCount} of ${totalCount} alerts`;
        }
    }
}

// Fetch date range for the data
function fetchDateRange() {
    fetch('/api/date-range')
        .then(response => response.json())
        .then(data => {
            const dateFrom = document.getElementById('date-from');
            const dateTo = document.getElementById('date-to');
            
            if (dateFrom && data.start_date) {
                dateFrom.placeholder = data.start_date;
            }
            
            if (dateTo && data.end_date) {
                dateTo.placeholder = data.end_date;
            }
        })
        .catch(error => {
            console.error('Error fetching date range:', error);
        });
}

// Update list of filters
function updateFilters() {
    // Fetch crime types
    fetch('/api/crime-types')
        .then(response => response.json())
        .then(data => {
            console.log('Crime types loaded from API');
        })
        .catch(error => {
            console.error('Error fetching crime types:', error);
        });
    
    // Fetch alert types
    fetch('/api/alert-types')
        .then(response => response.json())
        .then(data => {
            console.log('Alert types loaded from API');
        })
        .catch(error => {
            console.error('Error fetching alert types:', error);
        });
}

// Update the recent alerts panel
function updateRecentAlerts(features) {
    const recentAlertsList = document.getElementById('recent-alerts-list');
    if (!recentAlertsList) return;
    
    // Sort by date (newest first)
    const sortedFeatures = [...features].sort((a, b) => {
        const dateA = parseAlertDate(a.properties.date);
        const dateB = parseAlertDate(b.properties.date);
        return dateB - dateA;
    });
    
    // Take the top 10
    const recentFeatures = sortedFeatures.slice(0, 10);
    
    // Clear the list
    recentAlertsList.innerHTML = '';
    
    // Add each alert to the list
    if (recentFeatures.length === 0) {
        recentAlertsList.innerHTML = '<li class="no-alerts">No alerts match the current filters</li>';
    } else {
        recentFeatures.forEach(feature => {
            const props = feature.properties;
            const date = props.date;
            
            const alertItem = document.createElement('li');
            alertItem.className = 'alert-item';
            alertItem.innerHTML = `
                <div class="alert-date">${date}</div>
                <div class="alert-title">${props.title}</div>
                <div class="alert-location">${props.location_text}</div>
            `;
            
            // Add click event to center map on this alert
            alertItem.addEventListener('click', function() {
                const coords = feature.geometry.coordinates;
                crimeMap.flyTo({
                    center: coords,
                    zoom: 15
                });
                
                // Create a popup for this alert
                new mapboxgl.Popup({
                    closeButton: true,
                    closeOnClick: true,
                    maxWidth: '300px'
                })
                    .setLngLat(coords)
                    .setHTML(`
                        <div class="popup-content">
                            <h3>${props.title}</h3>
                            <p><strong>Date:</strong> ${date}</p>
                            <p><strong>Type:</strong> ${props.alert_type}</p>
                            <p><strong>Crime:</strong> ${props.crime_type}</p>
                            <p><strong>Location:</strong> ${props.location_text}</p>
                            ${props.address ? `<p><strong>Address:</strong> ${props.address}</p>` : ''}
                            ${props.suspect_info !== 'Not specified' ? `<p><strong>Suspect Info:</strong> ${props.suspect_info}</p>` : ''}
                            ${props.geocode_source ? `<p><small>Geocoded by: ${props.geocode_source}</small></p>` : ''}
                        </div>
                    `)
                    .addTo(crimeMap);
            });
            
            recentAlertsList.appendChild(alertItem);
        });
    }
}

// Parse alert date string into a Date object
function parseAlertDate(dateStr) {
    // Handle various date formats
    if (!dateStr || dateStr === 'Unknown') {
        return new Date(0); // Default to epoch for unknown dates
    }
    
    // Try MM/DD/YYYY format
    const parts = dateStr.split('/');
    if (parts.length === 3) {
        return new Date(parseInt(parts[2]), parseInt(parts[0]) - 1, parseInt(parts[1]));
    }
    
    // Try other formats
    return new Date(dateStr);
}

// Add geocoding service comparison functionality
// This function is called by the geocoding-service.js script
function setupGeocodingComparison() {
    // This function will be implemented in a separate file
    console.log('Geocoding comparison setup function called');
}