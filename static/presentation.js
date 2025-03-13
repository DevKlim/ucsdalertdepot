// static/presentation.js

document.addEventListener('DOMContentLoaded', function() {
  // Initialize animations for sections
  initAnimations();
  
  // Initialize the demo map
  initDemoMap();
  
  // Handle smooth scrolling for navigation links
  initSmoothScrolling();
  
  // Initialize the demo controls
  initDemoControls();
  
  // Add parallax effects
  initParallaxEffects();
  
  // Add card shimmer effects on hover
  initShimmerEffects();
});

// Initialize parallax effects
function initParallaxEffects() {
  window.addEventListener('scroll', function() {
    const scrollY = window.scrollY;
    
    // Apply parallax to hero section
    const heroLogo = document.querySelector('.hero-logo');
    if (heroLogo) {
      heroLogo.style.transform = `translateY(${scrollY * 0.2}px)`;
    }
    
    // Apply subtle rotation to sections
    document.querySelectorAll('section').forEach((section, index) => {
      if (isElementInViewport(section)) {
        const rotateValue = Math.sin(scrollY * 0.001) * 0.5;
        section.style.transform = `perspective(1000px) rotateX(${rotateValue}deg)`;
      }
    });
  });
}

// Check if element is in viewport
function isElementInViewport(el) {
  const rect = el.getBoundingClientRect();
  return (
    rect.top <= (window.innerHeight || document.documentElement.clientHeight) &&
    rect.bottom >= 0
  );
}

// Initialize shimmer effects for cards
function initShimmerEffects() {
  const cards = document.querySelectorAll('.feature-card, .tech-card');
  
  cards.forEach(card => {
    card.addEventListener('mouseenter', function() {
      // Remove existing shimmer elements
      const existingShimmer = this.querySelector('.shimmer');
      if (existingShimmer) {
        existingShimmer.remove();
      }
      
      // Create and add shimmer element
      const shimmer = document.createElement('div');
      shimmer.classList.add('shimmer');
      this.appendChild(shimmer);
      
      // Remove shimmer after animation completes
      shimmer.addEventListener('animationend', function() {
        this.remove();
      });
    });
  });
}

// Demo data - sample of alerts for the demo map
const demoAlerts = [
  {
    crime_type: "Burglary",
    alert_type: "Timely Warning",
    location_text: "BCB Café Coffee Cart, Warren Mall, UC San Diego",
    lat: 32.8820504581951,
    lng: -117.23474443943455,
    date: "2025-02-04",
    title: "Burglary at BCB Café",
    severity: "Medium",
    is_update: false,
    address: "Warren Mall, UC San Diego, 9500 Gilman Dr, La Jolla, CA 92093"
  },
  {
    crime_type: "Burglary",
    alert_type: "Timely Warning",
    location_text: "Pepper Canyon Apartments, UC San Diego",
    lat: 32.87820616198307,
    lng: -117.23932170109032,
    date: "2025-01-30",
    title: "Burglary at Pepper Canyon",
    severity: "Medium",
    is_update: false,
    address: "Pepper Canyon, UC San Diego, 9500 Gilman Dr, La Jolla, CA 92093"
  },
  {
    crime_type: "Burglary",
    alert_type: "Timely Warning",
    location_text: "Muir College Residential Housing, UC San Diego",
    lat: 32.878987778802426,
    lng: -117.24075016240717,
    date: "2025-01-30",
    title: "Burglary at Muir College",
    severity: "Medium",
    is_update: false,
    address: "Muir College, UC San Diego, 9500 Gilman Dr, La Jolla, CA 92093"
  },
  {
    crime_type: "Sexual Assault",
    alert_type: "Timely Warning",
    location_text: "Eighth College, UC San Diego",
    lat: 32.885117054136956,
    lng: -117.24054108492939,
    date: "2025-01-27",
    title: "Sexual Assault at Eighth College",
    severity: "High",
    is_update: false,
    address: "Eighth College, UC San Diego, 9500 Gilman Dr, La Jolla, CA 92093"
  },
  {
    crime_type: "Robbery",
    alert_type: "Triton Alert",
    location_text: "Price Center, UC San Diego",
    lat: 32.8794,
    lng: -117.2359,
    date: "2025-01-25",
    title: "Armed Robbery at Price Center",
    severity: "High",
    is_update: false,
    address: "Price Center, UC San Diego, 9500 Gilman Dr, La Jolla, CA 92093"
  },
  {
    crime_type: "Theft",
    alert_type: "Community Alert",
    location_text: "Geisel Library, UC San Diego",
    lat: 32.8810,
    lng: -117.2370,
    date: "2025-01-22",
    title: "Laptop Theft at Geisel Library",
    severity: "Medium",
    is_update: false,
    address: "Geisel Library, UC San Diego, 9500 Gilman Dr, La Jolla, CA 92093"
  },
  {
    crime_type: "Theft",
    alert_type: "Community Alert",
    location_text: "Hopkins Parking Structure, UC San Diego",
    lat: 32.8780,
    lng: -117.2330,
    date: "2025-01-20",
    title: "Bicycle Theft at Hopkins Parking",
    severity: "Low",
    is_update: false,
    address: "Hopkins Parking Structure, UC San Diego, 9500 Gilman Dr, La Jolla, CA 92093"
  },
  {
    crime_type: "Vandalism",
    alert_type: "Community Alert",
    location_text: "Revelle College, UC San Diego",
    lat: 32.8740,
    lng: -117.2410,
    date: "2025-01-19",
    title: "Vandalism at Revelle College",
    severity: "Low",
    is_update: false,
    address: "Revelle College, UC San Diego, 9500 Gilman Dr, La Jolla, CA 92093"
  }
];

// Initialize animations with Intersection Observer
function initAnimations() {
  const sections = document.querySelectorAll('section');
  
  const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
      if (entry.isIntersecting) {
        entry.target.classList.add('fade-in');
        
        // Add slide-up animation to child elements
        const childElements = entry.target.querySelectorAll('.feature-card, .tech-card, .team-member');
        childElements.forEach((el, i) => {
          setTimeout(() => {
            el.classList.add('slide-up');
          }, i * 100); // Stagger animation
        });
      }
    });
  }, { threshold: 0.2 });
  
  sections.forEach(section => {
    observer.observe(section);
  });
}

const map = new maplibregl.Map({
  container: 'map',
  style: 'https://basemaps.cartocdn.com/gl/dark-matter-gl-style/style.json', // Dark theme style
  // Alternative options:
  // style: 'https://demotiles.maplibre.org/style.json', // Default MapLibre style
  // style: 'https://basemaps.cartocdn.com/gl/positron-gl-style/style.json', // Light theme
  center: [-117.2340, 32.8801], // UCSD campus
  zoom: 14
});

// Fix for the "labelLayerId is not defined" error - remove or fix the code at line 109
// If you're trying to add 3D buildings, you should define labelLayerId first:

map.on('load', function() {
  // Add markers, etc.
  
  // If you want to add 3D buildings, do it like this:
  const layers = map.getStyle().layers;
  // Find the first symbol layer in the map style to place buildings underneath it
  let labelLayerId;
  for (let i = 0; i < layers.length; i++) {
    if (layers[i].type === 'symbol' && layers[i].layout['text-field']) {
      labelLayerId = layers[i].id;
      break;
    }
  }
  
  // Now you can use labelLayerId for adding 3D buildings
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
});

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

// Add alert markers to the map
function addAlertMarkers(map, alerts) {
  // Remove existing markers
  const existingMarkers = document.querySelectorAll('.maplibregl-marker');
  existingMarkers.forEach(marker => marker.remove());
  
  // Add new markers
  alerts.forEach(alert => {
    // Determine marker color based on crime type
    let color = '#3DDC97'; // Default green for other incidents
    
    if (['Assault', 'Sexual Assault', 'Robbery', 'Battery'].includes(alert.crime_type)) {
      color = '#FF495C'; // Red for violent crimes
    } else if (['Burglary', 'Theft', 'Vandalism'].includes(alert.crime_type)) {
      color = '#FFD700'; // Gold for property crimes
    }
    
    // Create popup content
    const popupContent = `
      <div class="popup-title">${alert.title}</div>
      <div class="popup-date">Date: ${formatDate(alert.date)}</div>
      <div class="popup-location">Location: ${alert.location_text}</div>
      <div class="popup-type ${getCrimeTypeClass(alert.crime_type)}">${alert.crime_type}</div>
    `;
    
    // Create popup with offset to prevent it from jumping under cursor
    const popup = new maplibregl.Popup({
      closeButton: false,
      closeOnClick: true,
      maxWidth: '300px',
      className: 'custom-popup',
      offset: [0, -15], // Offset popup upward so it doesn't appear under cursor
      anchor: 'bottom'
    }).setHTML(popupContent);
    
    // Create and add marker with more sophisticated design
    const el = document.createElement('div');
    el.className = 'custom-marker';
    el.style.backgroundColor = color;
    el.style.width = '24px';
    el.style.height = '24px';
    el.style.borderRadius = '50%';
    el.style.border = '2px solid #fff';
    el.style.boxShadow = `0 0 15px ${color}`;
    el.style.cursor = 'pointer';
    el.style.transition = 'all 0.3s ease';
    el.style.position = 'relative';
    
    // Add pulse effect
    const pulse = document.createElement('div');
    pulse.className = 'marker-pulse';
    pulse.style.position = 'absolute';
    pulse.style.width = '40px';
    pulse.style.height = '40px';
    pulse.style.borderRadius = '50%';
    pulse.style.backgroundColor = color;
    pulse.style.opacity = '0';
    pulse.style.top = '-8px';
    pulse.style.left = '-8px';
    pulse.style.animation = 'pulse 2s infinite';
    el.appendChild(pulse);
    
    // Add internal circle for design
    const inner = document.createElement('div');
    inner.style.position = 'absolute';
    inner.style.width = '12px';
    inner.style.height = '12px';
    inner.style.borderRadius = '50%';
    inner.style.backgroundColor = '#fff';
    inner.style.top = '6px';
    inner.style.left = '6px';
    el.appendChild(inner);
    
    // Add hover effect
    el.onmouseover = function() {
      this.style.transform = 'scale(1.2)';
      this.style.boxShadow = `0 0 20px ${color}`;
      popup.addTo(map); // Add popup on hover
    };
    
    el.onmouseout = function() {
      this.style.transform = 'scale(1)';
      this.style.boxShadow = `0 0 15px ${color}`;
      popup.remove(); // Remove popup when not hovering
    };
    
    // Create marker
    const marker = new maplibregl.Marker({
      element: el,
      anchor: 'center'
    })
    .setLngLat([alert.lng, alert.lat])
    .addTo(map);
    
    // Store popup in marker element for reference
    marker.getElement()._popup = popup;
    marker.getElement()._popupLngLat = [alert.lng, alert.lat];
    
    // Add click handler to toggle popup
    marker.getElement().addEventListener('click', function(e) {
      e.stopPropagation(); // Prevent click from being captured by map
      
      // Check if popup is already on map
      const popupOnMap = this._popup.isOpen();
      
      // Remove any existing popups
      document.querySelectorAll('.maplibregl-popup').forEach(p => p.remove());
      
      // If popup wasn't already open, add it
      if (!popupOnMap) {
        this._popup.setLngLat(this._popupLngLat).addTo(map);
      }
    });
  });
  
  // Add keyframe animation to the document if it doesn't exist
  if (!document.getElementById('marker-animations')) {
    const style = document.createElement('style');
    style.id = 'marker-animations';
    style.textContent = `
      @keyframes pulse {
        0% {
          transform: scale(0.5);
          opacity: 0.5;
        }
        70% {
          transform: scale(1.5);
          opacity: 0;
        }
        100% {
          transform: scale(0.5);
          opacity: 0;
        }
      }
    `;
    document.head.appendChild(style);
  }
}

// Format date from YYYY-MM-DD to MM/DD/YYYY
function formatDate(dateString) {
  if (!dateString) return 'Unknown';
  
  const parts = dateString.split('-');
  if (parts.length !== 3) return dateString;
  
  return `${parts[1]}/${parts[2]}/${parts[0]}`;
}

// Get CSS class for crime type
function getCrimeTypeClass(crimeType) {
  if (['Assault', 'Sexual Assault', 'Robbery', 'Battery'].includes(crimeType)) {
    return 'popup-type-violent';
  } else if (['Burglary', 'Theft', 'Vandalism'].includes(crimeType)) {
    return 'popup-type-property';
  }
  return 'popup-type-other';
}

// Initialize smooth scrolling for navigation links
function initSmoothScrolling() {
  const navLinks = document.querySelectorAll('nav a[href^="#"]');
  
  navLinks.forEach(link => {
    link.addEventListener('click', function(e) {
      e.preventDefault();
      
      const targetId = this.getAttribute('href');
      const targetSection = document.querySelector(targetId);
      
      if (targetSection) {
        window.scrollTo({
          top: targetSection.offsetTop,
          behavior: 'smooth'
        });
      }
    });
  });
}

// Initialize demo controls
function initDemoControls() {
  const alertTypeSelect = document.getElementById('demo-alert-type');
  const crimeTypeSelect = document.getElementById('demo-crime-type');
  const updateButton = document.getElementById('update-demo');
  
  if (!updateButton || !alertTypeSelect || !crimeTypeSelect) return;
  
  updateButton.addEventListener('click', function() {
    const selectedAlertType = alertTypeSelect.value;
    const selectedCrimeType = crimeTypeSelect.value;
    
    // Filter alerts based on selection
    let filteredAlerts = [...demoAlerts];
    
    if (selectedAlertType !== 'all') {
      filteredAlerts = filteredAlerts.filter(alert => alert.alert_type === selectedAlertType);
    }
    
    if (selectedCrimeType !== 'all') {
      filteredAlerts = filteredAlerts.filter(alert => alert.crime_type === selectedCrimeType);
    }
    
    // Update map markers
    if (window.demoMap) {
      addAlertMarkers(window.demoMap, filteredAlerts);
    }
  });
}