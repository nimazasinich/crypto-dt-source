/**
 * Service Status Modal Initializer
 * Auto-loads and initializes the service status modal component
 */

(function() {
  // Load Font Awesome if not already loaded (for icons)
  if (!document.querySelector('link[href*="font-awesome"]')) {
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css';
    link.crossOrigin = 'anonymous';
    document.head.appendChild(link);
  }
  
  // Load the service status modal component
  const script = document.createElement('script');
  script.src = '/static/shared/js/components/service-status-modal.js';
  script.async = true;
  script.onerror = () => {
    console.warn('Failed to load service status modal component');
  };
  
  document.head.appendChild(script);
})();
