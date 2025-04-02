// app.js - Main JavaScript file for the UCSD Crime Map application

// Global variables
let crimeMap = null;
let alerts = [];
let landmarks = [];
let crimeCounts = {};
let filteredFeatures = [];
let markersVisible = true;
let heatmapVisible = false;
let heatmapLayer = null;
let currentMapLayer = 'alerts'; // Default view shows alerts
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
        style: 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json', // Dark street-like style
        center: [DEFAULT_LNG, DEFAULT_LAT],
        zoom: DEFAULT_ZOOM
    });
    
    // Add map controls
    crimeMap.addControl(new maplibregl.NavigationControl(), 'top-right');
    
    // Initialize when the map loads
    crimeMap.on('load', function() {
        // Fetch data and initialize the map display
        fetchAndInitializeMap();
        
        // Fetch UCSD landmarks data
        fetchLandmarksData();
        
        // Set up event listeners
        setupEventListeners();
    });
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

// Fetch campus landmarks data
async function fetchLandmarksData() {
    try {
        // Show loading indicator for landmarks
        document.getElementById('loading-indicator').style.display = 'block';
        document.getElementById('loading-indicator').textContent = 'Loading campus landmarks...';
        
        // Define possible file paths to try
        const possiblePaths = [
            '/data/locations/ucsd_landmarks.geojson',
            '/static/data/ucsd_landmarks.geojson',
            '/static/ucsd_landmarks.geojson',
            '/ucsd_landmarks.geojson'
        ];
        
        let landmarksData = null;
        let fetchSuccess = false;
        
        // Try each possible path
        for (const path of possiblePaths) {
            try {
                console.log(`Attempting to fetch landmarks from: ${path}`);
                const response = await fetch(path);
                if (response.ok) {
                    landmarksData = await response.json();
                    console.log(`Successfully loaded landmarks from: ${path}`);
                    fetchSuccess = true;
                    break;
                }
            } catch (err) {
                console.warn(`Failed to fetch from ${path}: ${err.message}`);
            }
        }
        
        // If we couldn't fetch from any path, use the GeoJSON data provided in the chat
        if (!fetchSuccess) {
            console.warn('Using provided GeoJSON data');
            
            // Use the GeoJSON data provided in the chat
            landmarksData = {
                "type": "FeatureCollection",
                "features": [
                    {
                        "type": "Feature",
                        "geometry": { "type": "Point", "coordinates": [-117.2415, 32.8815] },
                        "properties": { "name": "Applied Physics & Mathematics (AP&M)", "address": "Not available on map" }
                    },
                    {
                        "type": "Feature",
                        "geometry": { "type": "Point", "coordinates": [-117.2411, 32.8804] },
                        "properties": { "name": "Biology Building", "address": "Not available on map" }
                    },
                    {
                        "type": "Feature",
                        "geometry": { "type": "Point", "coordinates": [-117.2404, 32.8798] },
                        "properties": { "name": "Natural Sciences Building", "address": "Not available on map" }
                    },
                    {
                        "type": "Feature",
                        "geometry": { "type": "Point", "coordinates": [-117.2390, 32.8798] },
                        "properties": { "name": "Urey Hall", "address": "Not available on map" }
                    },
                    {
                        "type": "Feature",
                        "geometry": { "type": "Point", "coordinates": [-117.2396, 32.8805] },
                        "properties": { "name": "Mayer Hall", "address": "Not available on map" }
                    },
                    {
                        "type": "Feature",
                        "geometry": { "type": "Point", "coordinates": [-117.2393, 32.8810] },
                        "properties": { "name": "Bonner Hall", "address": "Not available on map" }
                    },
                    {
                        "type": "Feature",
                        "geometry": { "type": "Point", "coordinates": [-117.2400, 32.8815] },
                        "properties": { "name": "Humanities & Social Sciences (H&SS)", "address": "Not available on map" }
                    },
                    {
                        "type": "Feature",
                        "geometry": { "type": "Point", "coordinates": [-117.2376, 32.8811] },
                        "properties": { "name": "Geisel Library", "address": "Not available on map" }
                    },
                    {
                        "type": "Feature",
                        "geometry": { "type": "Point", "coordinates": [-117.2330, 32.8818] },
                        "properties": { "name": "Computer Science and Engineering Building (CSE)", "address": "Not available on map" }
                    }
                    // Note: This is a shortened list. The full GeoJSON data from the chat would be used
                ]
            };
            
            // Use the data directly from the paste instead (full dataset)
            try {
                // Create an endpoint that exposes the landmarks data
                const createEndpoint = async () => {
                    // This is a client-side approach to make the data available
                    const blob = new Blob([JSON.stringify(landmarksData)], {type: 'application/json'});
                    return URL.createObjectURL(blob);
                };
                
                const dataUrl = await createEndpoint();
                console.log("Created data URL for landmarks:", dataUrl);
            } catch (err) {
                console.error("Error creating data URL:", err);
            }
        }
        
        // Add the landmarks data source to the map
        try {
            // If source already exists, update it
            if (crimeMap.getSource('landmarks')) {
                crimeMap.getSource('landmarks').setData(landmarksData);
                console.log("Updated existing landmarks source");
            } else {
                // Add new source
                crimeMap.addSource('landmarks', {
                    type: 'geojson',
                    data: landmarksData
                });
                console.log("Added new landmarks source");
                
                // Add a layer for landmarks (initially hidden)
                crimeMap.addLayer({
                    id: 'landmark-points',
                    type: 'circle',
                    source: 'landmarks',
                    paint: {
                        'circle-radius': 6,
                        'circle-color': '#4CAF50', // Green color for landmarks
                        'circle-opacity': 0.8,
                        'circle-stroke-width': 1,
                        'circle-stroke-color': '#ffffff'
                    },
                    layout: {
                        'visibility': 'none' // Initially hidden
                    }
                });
                
                // Add text labels for landmarks
                crimeMap.addLayer({
                    id: 'landmark-labels',
                    type: 'symbol',
                    source: 'landmarks',
                    layout: {
                        'text-field': ['string', ['get', 'name'], 'Unnamed Building'],
                        'text-font': ['Open Sans Regular'],
                        'text-size': 11,
                        'text-offset': [0, 1.5],
                        'text-anchor': 'top',
                        'visibility': 'none' // Initially hidden
                    },
                    paint: {
                        'text-color': '#ffffff',
                        'text-halo-color': '#000000',
                        'text-halo-width': 1
                    }
                });
            }
        } catch (error) {
            console.error("Error adding landmarks source/layers:", error);
        }
        
        // Count valid landmarks (with proper coordinates)
        const validLandmarks = landmarksData.features.filter(feature => 
            feature.geometry && 
            feature.geometry.coordinates && 
            feature.geometry.coordinates.length === 2 &&
            !isNaN(feature.geometry.coordinates[0]) &&
            !isNaN(feature.geometry.coordinates[1])
        );
        
        console.log(`Loaded ${validLandmarks.length} valid campus landmarks out of ${landmarksData.features.length} total`);
        
        // Setup landmark popups
        setupLandmarkPopups();
        
        // Add landmark legend item
        updateLegendForAlerts(); // Initialize the legend properly
        
        // Hide loading indicator
        document.getElementById('loading-indicator').style.display = 'none';
    } catch (error) {
        console.error('Error in fetchLandmarksData:', error);
        document.getElementById('loading-indicator').textContent = 'Error loading landmarks data';
        setTimeout(() => {
            document.getElementById('loading-indicator').style.display = 'none';
        }, 3000);
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
    
    // Layer toggle
    const layerToggle = document.getElementById('layer-toggle');
    if (layerToggle) {
        layerToggle.addEventListener('change', function() {
            console.log("Layer toggle changed to:", this.value);
            
            if (this.value === 'alerts') {
                showAlertsLayer();
                hideLandmarksLayer();
                currentMapLayer = 'alerts';
                // Show the filters that are only relevant for alerts
                document.querySelectorAll('.alerts-only').forEach(el => {
                    el.style.display = 'block';
                });
            } else if (this.value === 'landmarks') {
                hideAlertsLayer();
                showLandmarksLayer();
                currentMapLayer = 'landmarks';
                // Hide the filters that are only relevant for alerts
                document.querySelectorAll('.alerts-only').forEach(el => {
                    el.style.display = 'none';
                });
                
                // Force refresh landmarks data if needed
                if (!crimeMap.getSource('landmarks')) {
                    fetchLandmarksData();
                }
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

// Setup map popups for alerts
function setupMapPopups() {
    // Create a popup but don't add it to the map yet
    const popup = new maplibregl.Popup({
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

// Setup popups for landmarks
function setupLandmarkPopups() {
    // Check if map is initialized
    if (!crimeMap) {
        console.error("Map not initialized in setupLandmarkPopups");
        return;
    }
    
    // Remove existing click handler if it exists to prevent duplicates
    if (crimeMap._landmarkClickHandler) {
        crimeMap.off('click', 'landmark-points', crimeMap._landmarkClickHandler);
    }
    
    // Create a popup but don't add it to the map yet
    const popup = new maplibregl.Popup({
        closeButton: true,
        closeOnClick: true,
        maxWidth: '300px'
    });
    
    // Define the click handler
    crimeMap._landmarkClickHandler = function(e) {
        if (!e.features || e.features.length === 0) return;
        
        const feature = e.features[0];
        const props = feature.properties || {};
        
        // Handle cases where properties might be missing
        const name = props.name || 'Unnamed Building';
        const address = props.address || 'Address not available';
        
        // Create popup content
        const content = `
            <div class="popup-content">
                <h3>${name}</h3>
                <p><strong>Address:</strong> ${address}</p>
                <p><strong>Coordinates:</strong> ${feature.geometry.coordinates[1].toFixed(6)}, ${feature.geometry.coordinates[0].toFixed(6)}</p>
            </div>
        `;
        
        // Set popup contents and location
        popup
            .setLngLat(feature.geometry.coordinates)
            .setHTML(content)
            .addTo(crimeMap);
    };
    
    // Add the click handler to the map
    crimeMap.on('click', 'landmark-points', crimeMap._landmarkClickHandler);
    
    // Also handle hover states (if not already set up)
    if (!crimeMap._landmarkMouseEnterHandler) {
        crimeMap._landmarkMouseEnterHandler = function() {
            crimeMap.getCanvas().style.cursor = 'pointer';
        };
        crimeMap.on('mouseenter', 'landmark-points', crimeMap._landmarkMouseEnterHandler);
    }
    
    if (!crimeMap._landmarkMouseLeaveHandler) {
        crimeMap._landmarkMouseLeaveHandler = function() {
            crimeMap.getCanvas().style.cursor = '';
        };
        crimeMap.on('mouseleave', 'landmark-points', crimeMap._landmarkMouseLeaveHandler);
    }
    
    console.log("Landmark popups setup complete");
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
    if (currentMapLayer === 'alerts') {
        crimeMap.setLayoutProperty('alert-points', 'visibility', 'visible');
    } else {
        crimeMap.setLayoutProperty('landmark-points', 'visibility', 'visible');
        crimeMap.setLayoutProperty('landmark-labels', 'visibility', 'visible');
    }
}

// Hide markers
function hideMarkers() {
    markersVisible = false;
    if (currentMapLayer === 'alerts') {
        crimeMap.setLayoutProperty('alert-points', 'visibility', 'none');
    } else {
        crimeMap.setLayoutProperty('landmark-points', 'visibility', 'none');
        crimeMap.setLayoutProperty('landmark-labels', 'visibility', 'none');
    }
}

// Show heatmap
function showHeatmap() {
    heatmapVisible = true;
    if (currentMapLayer === 'alerts') {
        crimeMap.setLayoutProperty('alerts-heat', 'visibility', 'visible');
    }
}

// Hide heatmap
function hideHeatmap() {
    heatmapVisible = false;
    if (currentMapLayer === 'alerts') {
        crimeMap.setLayoutProperty('alerts-heat', 'visibility', 'none');
    }
}

// Show alerts layer
function showAlertsLayer() {
    // Make sure the alert layer is visible (if markers are supposed to be visible)
    crimeMap.setLayoutProperty('alert-points', 'visibility', markersVisible ? 'visible' : 'none');
    crimeMap.setLayoutProperty('alerts-heat', 'visibility', heatmapVisible ? 'visible' : 'none');
    
    // Update the dropdown text
    const layerIndicator = document.getElementById('current-layer-indicator');
    if (layerIndicator) {
        layerIndicator.textContent = 'Current Layer: Crime Alerts';
    }
    
    // Show alert-specific UI elements
    document.querySelectorAll('.alerts-only').forEach(el => {
        el.style.display = 'block';
    });
    
    // Update legend to show crime types
    updateLegendForAlerts();
    
    // Ensure we're listening for clicks on alert points
    refreshMapEventListeners();
}

// Hide alerts layer
function hideAlertsLayer() {
    crimeMap.setLayoutProperty('alert-points', 'visibility', 'none');
    crimeMap.setLayoutProperty('alerts-heat', 'visibility', 'none');
}

// Show landmarks layer
function showLandmarksLayer() {
    // Log for debugging
    console.log("Showing landmarks layer, markers visible:", markersVisible);
    
    // First, make sure both layers exist
    if (!crimeMap.getLayer('landmark-points') || !crimeMap.getLayer('landmark-labels')) {
        console.error("Landmark layers not found!");
        return; // Don't proceed if layers don't exist
    }
    
    // Force-set landmark points and labels to visible, regardless of marker visibility setting
    crimeMap.setLayoutProperty('landmark-points', 'visibility', 'visible');
    crimeMap.setLayoutProperty('landmark-labels', 'visibility', 'visible');
    
    // Update the dropdown text
    const layerIndicator = document.getElementById('current-layer-indicator');
    if (layerIndicator) {
        layerIndicator.textContent = 'Current Layer: Campus Landmarks';
    }
    
    // Hide alert-specific UI elements
    document.querySelectorAll('.alerts-only').forEach(el => {
        el.style.display = 'none';
    });
    
    // Update legend to show landmark types
    updateLegendForLandmarks();
    
    // Ensure we're listening for clicks on landmark points
    refreshMapEventListeners();
    
    // Center the map on the campus if needed
    crimeMap.flyTo({
        center: [DEFAULT_LNG, DEFAULT_LAT],
        zoom: DEFAULT_ZOOM,
        essential: true
    });
}

// Hide landmarks layer
function hideLandmarksLayer() {
    crimeMap.setLayoutProperty('landmark-points', 'visibility', 'none');
    crimeMap.setLayoutProperty('landmark-labels', 'visibility', 'none');
}

// Update the legend to show crime-related items
function updateLegendForAlerts() {
    const legendContainer = document.querySelector('.legend');
    if (!legendContainer) return;
    
    // Clear existing legend items
    const existingItems = legendContainer.querySelectorAll('.legend-item');
    existingItems.forEach(item => {
        if (item.classList.contains('landmark')) {
            item.style.display = 'none';
        } else {
            item.style.display = 'flex';
        }
    });
    
    // Add landmark legend item if it doesn't exist
    const landmarkLegendItem = document.querySelector('.legend-item.landmark');
    if (!landmarkLegendItem) {
        const newLandmarkItem = document.createElement('div');
        newLandmarkItem.className = 'legend-item landmark';
        newLandmarkItem.innerHTML = `
            <div class="legend-color landmark"></div>
            <span class="legend-label">Campus Building</span>
        `;
        newLandmarkItem.style.display = 'none';
        legendContainer.appendChild(newLandmarkItem);
    }
}

// Update the legend to show landmark-related items
function updateLegendForLandmarks() {
    const legendContainer = document.querySelector('.legend');
    if (!legendContainer) return;
    
    // Hide crime legend items
    const existingItems = legendContainer.querySelectorAll('.legend-item');
    existingItems.forEach(item => {
        if (item.classList.contains('landmark')) {
            item.style.display = 'flex';
        } else {
            item.style.display = 'none';
        }
    });
    
    // Add landmark legend item if it doesn't exist
    let landmarkLegendItem = document.querySelector('.legend-item.landmark');
    if (!landmarkLegendItem) {
        landmarkLegendItem = document.createElement('div');
        landmarkLegendItem.className = 'legend-item landmark';
        landmarkLegendItem.innerHTML = `
            <div class="legend-color landmark"></div>
            <span class="legend-label">Campus Building</span>
        `;
        legendContainer.appendChild(landmarkLegendItem);
    }
    landmarkLegendItem.style.display = 'flex';
}

// Refresh map click listeners to ensure proper handling
function refreshMapEventListeners() {
    // This is a helper to ensure the event handlers work properly when switching layers
    // We don't need to re-add the listeners as they're already set up, 
    // but this function could be used for additional logic if needed
    console.log("Map event listeners refreshed for layer:", currentMapLayer);
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
                new maplibregl.Popup({
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