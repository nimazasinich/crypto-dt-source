/**
 * Feature Detection Utility
 * Safely checks for browser feature support before use
 */

/**
 * Feature detection map
 * @type {Object<string, Function>}
 */
const FeatureDetection = {
  /**
   * Check if ambient light sensor is supported
   * @returns {boolean}
   */
  ambientLightSensor() {
    return 'AmbientLightSensor' in window;
  },

  /**
   * Check if battery API is supported
   * @returns {boolean}
   */
  battery() {
    return 'getBattery' in navigator;
  },

  /**
   * Check if wake lock is supported
   * @returns {boolean}
   */
  wakeLock() {
    return 'wakeLock' in navigator;
  },

  /**
   * Check if VR is supported
   * @returns {boolean}
   */
  vr() {
    return 'getVRDisplays' in navigator || 'xr' in navigator;
  },

  /**
   * Check if a feature is supported
   * @param {string} featureName - Name of the feature
   * @returns {boolean}
   */
  isSupported(featureName) {
    const detector = this[featureName];
    if (typeof detector === 'function') {
      try {
        return detector();
      } catch (e) {
        return false;
      }
    }
    return false;
  },

  /**
   * Get all supported features
   * @returns {Object<string, boolean>}
   */
  getAllSupported() {
    return {
      ambientLightSensor: this.ambientLightSensor(),
      battery: this.battery(),
      wakeLock: this.wakeLock(),
      vr: this.vr()
    };
  }
};

/**
 * Suppress console warnings for unrecognized features
 * Only logs if feature is actually being used
 * This suppresses warnings from Hugging Face Space iframe Permissions-Policy
 */
(function suppressFeatureWarnings() {
  // Only suppress if not already suppressed
  if (window._featureWarningsSuppressed) {
    return;
  }
  
  const originalWarn = console.warn;
  const ignoredFeatures = [
    'ambient-light-sensor',
    'battery',
    'document-domain',
    'layout-animations',
    'legacy-image-formats',
    'oversized-images',
    'vr',
    'wake-lock'
  ];

  console.warn = function(...args) {
    const message = args[0]?.toString() || '';
    
    // Check for Permissions-Policy warnings from Hugging Face Space
    const isPermissionsPolicyWarning = message.includes('Unrecognized feature:') && 
      ignoredFeatures.some(feature => message.includes(feature));
    
    // Also check for other common HF Space warnings
    const isHFSpaceWarning = message.includes('Datasourceforcryptocurrency') && 
      message.includes('Unrecognized feature:');
    
    if (isPermissionsPolicyWarning || isHFSpaceWarning) {
      // Suppress these warnings - they come from HF Space iframe and can't be controlled
      return;
    }

    // Allow all other warnings
    originalWarn.apply(console, args);
  };
  
  // Mark as suppressed
  window._featureWarningsSuppressed = true;
})();

// Export for use in modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = FeatureDetection;
}

// Make available globally
window.FeatureDetection = FeatureDetection;
