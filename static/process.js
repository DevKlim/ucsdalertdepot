// static/process.js - Updated to work with visualizations

document.addEventListener('DOMContentLoaded', function() {
    // Initialize visualizations
    initProcessVisualizations();
    
    // Initialize scrollama for highlighting steps only (no visualization switching)
    initScrollama();
    
    // Initialize smooth scrolling for navigation links
    initSmoothScrolling();
  });
  
  // Initialize scrollama instance
  function initScrollama() {
    // Initialize the scrollama
    const scroller = scrollama();
    
    // Setup the instance with minimal configuration
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
  
  function handleStepEnter(response) {
    // Just add 'is-active' class to the current step
    response.element.classList.add('is-active');
  }
  
  // Callback for scrollama step exit
  function handleStepExit(response) {
    // Remove 'is-active' class from the exited step
    response.element.classList.remove('is-active');
  }
  
  // Initialize smooth scrolling for navigation links
  function initSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
      anchor.addEventListener('click', function (e) {
        e.preventDefault();
        
        const targetId = this.getAttribute('href');
        const targetElement = document.querySelector(targetId);
        
        if (targetElement) {
          targetElement.scrollIntoView({
            behavior: 'smooth'
          });
        }
      });
    });
  }
  
  // Update which visualization is active based on the current step
  function updateActiveVisualization(stepId) {
    if (window.visualizationHandler) {
      // If the visualization handler from process-visualizations.js exists, use it
      window.visualizationHandler(stepId);
      return;
    }
    
    // Fallback implementation if visualization handler isn't available
    const allVisContainers = document.querySelectorAll('[id$="-vis"]');
    allVisContainers.forEach(container => {
      container.style.display = 'none';
    });
    
    // Show the visualization for the current step
    const currentVis = document.getElementById(`${stepId}-vis`);
    if (currentVis) {
      currentVis.style.display = 'flex';
    }
  }
  
  // Initialize smooth scrolling for navigation links
  function initSmoothScrolling() {
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
      anchor.addEventListener('click', function (e) {
        e.preventDefault();
        
        const targetId = this.getAttribute('href');
        const targetElement = document.querySelector(targetId);
        
        if (targetElement) {
          targetElement.scrollIntoView({
            behavior: 'smooth'
          });
        }
      });
    });
  }
  
  // Helper function to check if an element is in the viewport
  function isElementInViewport(el) {
    const rect = el.getBoundingClientRect();
    return (
      rect.top <= (window.innerHeight || document.documentElement.clientHeight) &&
      rect.bottom >= 0
    );
  }
  
  // Add parallax effect to sections as user scrolls
  function initParallaxEffects() {
    window.addEventListener('scroll', function() {
      const scrollY = window.scrollY;
      
      // Apply parallax to hero section
      const heroLogo = document.querySelector('.hero-logo');
      if (heroLogo) {
        heroLogo.style.transform = `translateY(${scrollY * 0.2}px)`;
      }
      
      // Apply subtle effect to sections in view
      document.querySelectorAll('section, .step').forEach((section) => {
        if (isElementInViewport(section)) {
          const offsetY = section.getBoundingClientRect().top;
          const opacity = 1 - Math.abs(offsetY) / (window.innerHeight * 0.5);
          section.style.opacity = Math.max(1, opacity);
        }
      });
    });
  }
  
  // Initialize on load
  initParallaxEffects();
  
  // Auto-rotate roadmap phases
  function autoRotateRoadmapPhases() {
    const phases = document.querySelectorAll('.roadmap-phase');
    if (phases.length === 0) return;
    
    let currentIndex = 0;
    
    // Find current phase
    phases.forEach((phase, index) => {
      if (phase.querySelector('.phase-dot.current')) {
        currentIndex = index;
      }
    });
    
    // Remove current class from all phases
    phases.forEach(phase => {
      phase.querySelector('.phase-dot').classList.remove('current');
    });
    
    // Move to next phase
    currentIndex = (currentIndex + 1) % phases.length;
    phases[currentIndex].querySelector('.phase-dot').classList.add('current');
    
    // Schedule next rotation
    setTimeout(autoRotateRoadmapPhases, 3000);
  }
  
  // Start auto-rotation when the roadmap is in view
  function initRoadmapRotation() {
    const roadmap = document.querySelector('.roadmap');
    if (!roadmap) return;
    
    const observer = new IntersectionObserver((entries) => {
      if (entries[0].isIntersecting) {
        autoRotateRoadmapPhases();
        observer.disconnect(); // Only start it once
      }
    });
    
    observer.observe(roadmap);
  }
  
  // Initialize roadmap rotation
  initRoadmapRotation();
  
  // Highlight focus points on the Core Mission section
  function highlightFocusPoints() {
    const focusPoints = document.querySelectorAll('.focus-point');
    if (focusPoints.length === 0) return;
    
    // Just add the highlight class to the first point
    focusPoints[0].classList.add('highlight');
    
    // No animation or rotation
  }
  
  // Initialize focus point highlighting
  highlightFocusPoints();
  
  // Add animations to project goals
  function animateProjectGoals() {
    const goalsList = document.querySelector('.goals-list');
    if (!goalsList) return;
    
    const goals = goalsList.querySelectorAll('li');
    
    const observer = new IntersectionObserver((entries) => {
      if (entries[0].isIntersecting) {
        goals.forEach((goal, index) => {
          setTimeout(() => {
            goal.style.opacity = 0;
            goal.style.transform = 'translateX(-20px)';
            goal.style.transition = 'opacity 0.5s ease, transform 0.5s ease';
            
            setTimeout(() => {
              goal.style.opacity = 1;
              goal.style.transform = 'translateX(0)';
            }, 50);
          }, index * 300);
        });
        
        observer.disconnect(); // Only animate once
      }
    });
    
    observer.observe(goalsList);
  }
  
  // Initialize goal animations
  animateProjectGoals();
  
  // Enhance the technology highlight sections with hover effects
  function enhanceTechHighlights() {
    const highlights = document.querySelectorAll('.tech-highlight');
    
    highlights.forEach(highlight => {
      highlight.addEventListener('mouseenter', () => {
        const icon = highlight.querySelector('.tech-icon');
        if (icon) {
          icon.style.transform = 'scale(1.1) rotate(5deg)';
          icon.style.backgroundColor = 'rgba(212, 175, 55, 0.3)';
        }
      });
      
      highlight.addEventListener('mouseleave', () => {
        const icon = highlight.querySelector('.tech-icon');
        if (icon) {
          icon.style.transform = 'scale(1) rotate(0)';
          icon.style.backgroundColor = 'rgba(212, 175, 55, 0.2)';
        }
      });
    });
  }
  
  // Initialize tech highlight enhancements
  enhanceTechHighlights();
  
  // Add code formatting animation
  function animateCodeSnippets() {
    const codeSnippets = document.querySelectorAll('.code-snippet');
    
    codeSnippets.forEach(snippet => {
      // Create observer for each snippet
      const observer = new IntersectionObserver((entries) => {
        if (entries[0].isIntersecting) {
          const codeLines = snippet.querySelectorAll('code line');
          if (codeLines.length > 0) {
            codeLines.forEach((line, index) => {
              setTimeout(() => {
                line.style.opacity = 0;
                line.style.transform = 'translateX(-10px)';
                line.style.transition = 'opacity 0.3s ease, transform 0.3s ease';
                
                setTimeout(() => {
                  line.style.opacity = 1;
                  line.style.transform = 'translateX(0)';
                }, 50);
              }, index * 100);
            });
          } else {
            // If code isn't separated into lines, animate the whole block
            const code = snippet.querySelector('code');
            if (code) {
              code.style.opacity = 0;
              code.style.transition = 'opacity 0.5s ease';
              
              setTimeout(() => {
                code.style.opacity = 1;
              }, 200);
            }
          }
          
          observer.disconnect(); // Only animate once
        }
      }, { threshold: 0.3 });
      
      observer.observe(snippet);
    });
  }
  
  // Initialize code snippet animations
  animateCodeSnippets();
  
  // Coordinate with visualizations
  function coordinateWithVisualizations() {
    // This function ensures that the text content and visualizations 
    // are properly coordinated during scrolling
    
    window.addEventListener('scroll', () => {
      // Find which step is closest to the middle of the viewport
      const steps = document.querySelectorAll('.step');
      let closestStep = null;
      let closestDistance = Infinity;
      
      steps.forEach(step => {
        const rect = step.getBoundingClientRect();
        const distance = Math.abs(rect.top + rect.height/2 - window.innerHeight/2);
        
        if (distance < closestDistance) {
          closestDistance = distance;
          closestStep = step;
        }
      });
      
      // Update visualization if we have a closest step
      if (closestStep) {
        const stepId = closestStep.getAttribute('data-step');
        updateActiveVisualization(stepId);
      }
    });
  }
  
  // Initialize visualization coordination
  coordinateWithVisualizations();
  
  // Handle the window load event to ensure proper initial state
  window.addEventListener('load', function() {
    // Update active visualization based on scroll position
    setTimeout(() => {
      // Trigger a scroll event to initialize the active visualization
      window.dispatchEvent(new Event('scroll'));
    }, 500);
  });