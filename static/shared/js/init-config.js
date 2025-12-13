/**
 * Configuration Initializer
 * Ensures CONFIG is available before other modules load
 * This should be loaded as the first module on any page
 */

// Minimal CONFIG defaults that work without full config.js
if (typeof window !== 'undefined' && !window.CONFIG) {
  window.CONFIG = {
    API_BASE_URL: window.location.origin,
    API_TIMEOUT: 10000,
    CACHE_TTL: 60000,
    MAX_RETRIES: 3,
    RETRY_DELAY: 1000,
    RETRIES: 3,
    TOAST: {
      MAX_VISIBLE: 3,
      DEFAULT_DURATION: 3500,
      ERROR_DURATION: 6000
    },
    IS_HUGGINGFACE: window.location.hostname.includes('hf.space') || window.location.hostname.includes('huggingface.co'),
    IS_LOCALHOST: window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1'
  };
  
  window.CONFIG.ENVIRONMENT = window.CONFIG.IS_HUGGINGFACE ? 'huggingface' : 
                              window.CONFIG.IS_LOCALHOST ? 'local' : 'production';
}

// Dynamically load and merge full config if available
(async function loadFullConfig() {
  try {
    const configModule = await import('./core/config.js');
    if (configModule.CONFIG) {
      // Merge full config over defaults
      window.CONFIG = { ...window.CONFIG, ...configModule.CONFIG };
    }
  } catch (e) {
    // Full config not available, defaults already set
    console.log('[Config] Using default configuration');
  }
})();

export default window.CONFIG;
