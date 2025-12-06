/**
 * API Configuration for Crypto API Monitoring System
 * Automatically detects environment (localhost, HuggingFace Spaces, or custom deployment)
 */

const CONFIG = (() => {
    // Detect if running on HuggingFace Spaces
    const isHuggingFaceSpaces = window.location.hostname.includes('hf.space') ||
                                window.location.hostname.includes('huggingface.co');

    // Detect if running locally
    const isLocalhost = window.location.hostname === 'localhost' ||
                       window.location.hostname === '127.0.0.1' ||
                       window.location.hostname === '';

    // Get base API URL based on environment
    const getApiBaseUrl = () => {
        // Always use current origin - works in all environments (local, HF Spaces, production)
        // The backend should be served from the same origin
        return window.location.origin;
    };

    // Get WebSocket URL based on environment
    const getWebSocketUrl = () => {
        const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        // Always use current host - works in all environments
        const host = window.location.host;
        return `${protocol}//${host}`;
    };

    const API_BASE = getApiBaseUrl();
    const WS_BASE = getWebSocketUrl();

    return {
        // API Configuration
        API_BASE: API_BASE,
        WS_BASE: WS_BASE,

        // Environment flags
        IS_HUGGINGFACE_SPACES: isHuggingFaceSpaces,
        IS_LOCALHOST: isLocalhost,

        // API Endpoints
        ENDPOINTS: {
            // Health & Status
            HEALTH: `${API_BASE}/health`,
            API_INFO: `${API_BASE}/api-info`,
            STATUS: `${API_BASE}/api/status`,

            // Provider Management
            PROVIDERS: `${API_BASE}/api/providers`,
            CATEGORIES: `${API_BASE}/api/categories`,

            // Data Collection
            PRICES: `${API_BASE}/api/prices`,
            NEWS: `${API_BASE}/api/news`,
            SENTIMENT: `${API_BASE}/api/sentiment/current`,
            WHALES: `${API_BASE}/api/whales/transactions`,

            // HuggingFace Integration
            HF_HEALTH: `${API_BASE}/api/hf/health`,
            HF_REGISTRY: `${API_BASE}/api/hf/registry`,
            HF_SEARCH: `${API_BASE}/api/hf/search`,
            HF_REFRESH: `${API_BASE}/api/hf/refresh`,
            HF_RUN_SENTIMENT: `${API_BASE}/api/hf/run-sentiment`,

            // Monitoring
            LOGS: `${API_BASE}/api/logs`,
            ALERTS: `${API_BASE}/api/alerts`,
            SCHEDULER: `${API_BASE}/api/scheduler/status`,

            // Analytics
            ANALYTICS: `${API_BASE}/api/analytics/failures`,
            RATE_LIMITS: `${API_BASE}/api/rate-limits`,
        },

        // WebSocket Endpoints
        WEBSOCKETS: {
            MASTER: `${WS_BASE}/ws`,
            LIVE: `${WS_BASE}/ws/live`,
            DATA: `${WS_BASE}/ws/data`,
            MARKET_DATA: `${WS_BASE}/ws/market_data`,
            NEWS: `${WS_BASE}/ws/news`,
            SENTIMENT: `${WS_BASE}/ws/sentiment`,
            WHALE_TRACKING: `${WS_BASE}/ws/whale_tracking`,
            HEALTH: `${WS_BASE}/ws/health`,
            MONITORING: `${WS_BASE}/ws/monitoring`,
            HUGGINGFACE: `${WS_BASE}/ws/huggingface`,
        },

        // Utility Functions
        buildUrl: (path) => {
            return `${API_BASE}${path}`;
        },

        buildWsUrl: (path) => {
            return `${WS_BASE}${path}`;
        },

        // Fetch helper with error handling
        fetchJSON: async (url, options = {}) => {
            try {
                const response = await fetch(url, options);
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                return await response.json();
            } catch (error) {
                console.error(`Fetch error for ${url}:`, error);
                throw error;
            }
        },

        // POST helper
        postJSON: async (url, body = {}) => {
            return CONFIG.fetchJSON(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(body),
            });
        },
    };
})();

// Export for use in modules (if needed)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = CONFIG;
}

// Log configuration on load (for debugging)
console.log('🚀 Crypto API Monitor - Configuration loaded:', {
    environment: CONFIG.IS_HUGGINGFACE_SPACES ? 'HuggingFace Spaces' :
                 CONFIG.IS_LOCALHOST ? 'Localhost' : 'Custom Deployment',
    apiBase: CONFIG.API_BASE,
    wsBase: CONFIG.WS_BASE,
});
