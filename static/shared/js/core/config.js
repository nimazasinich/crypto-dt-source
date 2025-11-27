/**
 * Central Configuration for Crypto Monitor ULTIMATE
 * All constants, API endpoints, and settings in one place
 */

// ============================================================================
// API CONFIGURATION
// ============================================================================

export const CONFIG = {
  // Base API URL (relative to current origin)
  API_BASE_URL: window.location.origin + '/api',
  
  // Polling intervals (milliseconds)
  POLLING_INTERVALS: {
    dashboard: 30000,      // 30 seconds
    market: 30000,         // 30 seconds
    providers: 60000,      // 1 minute
    news: 120000,          // 2 minutes
    diagnostics: 0,        // Manual refresh only
  },
  
  // Cache configuration
  CACHE_TTL: 60000,        // Default cache TTL: 1 minute
  MAX_RETRIES: 3,          // Max retry attempts for failed requests
  RETRY_DELAY: 3000,       // Delay between retries (ms)
  
  // Pagination
  PAGINATION: {
    defaultLimit: 50,
    maxLimit: 100,
  },
  
  // Chart timeframes
  TIMEFRAMES: ['1D', '7D', '30D', '1Y'],
  
  // Theme options
  THEMES: {
    DARK: 'dark',
    LIGHT: 'light',
    SYSTEM: 'system',
  },
  
  // LocalStorage keys
  STORAGE_KEYS: {
    THEME: 'crypto_monitor_theme',
    PREFERENCES: 'crypto_monitor_preferences',
    CACHE_PREFIX: 'cm_cache_',
  },
  
  // Toast notification defaults
  TOAST: {
    DEFAULT_DURATION: 5000,
    ERROR_DURATION: 7000,
    MAX_VISIBLE: 5,
  },
};

// ============================================================================
// ROUTE DEFINITIONS
// ============================================================================

export const ROUTES = {
  DASHBOARD: '/',
  MARKET: '/market',
  MODELS: '/models',
  SENTIMENT: '/sentiment',
  AI_ANALYST: '/ai-analyst',
  TRADING: '/trading-assistant',
  NEWS: '/news',
  PROVIDERS: '/providers',
  DIAGNOSTICS: '/diagnostics',
  API_EXPLORER: '/api-explorer',
};

// ============================================================================
// API ENDPOINTS
// ============================================================================

export const API_ENDPOINTS = {
  // Health & Status
  HEALTH: '/health',
  STATUS: '/status',
  STATS: '/stats',
  
  // Market Data
  MARKET: '/market',
  TRENDING: '/trending',
  SENTIMENT: '/sentiment',
  DEFI: '/defi',
  COINS_TOP: '/coins/top',
  COIN_DETAILS: (symbol) => `/coins/${symbol}`,
  COIN_HISTORY: (symbol) => `/coins/${symbol}/history`,
  
  // Charts
  PRICE_CHART: (symbol) => `/charts/price/${symbol}`,
  ANALYZE_CHART: '/charts/analyze',
  
  // News
  NEWS_LATEST: '/news/latest',
  NEWS_ANALYZE: '/news/analyze',
  NEWS_SUMMARIZE: '/news/summarize',
  
  // AI/ML Models
  MODELS_LIST: '/models/list',
  MODELS_STATUS: '/models/status',
  MODELS_STATS: '/models/data/stats',
  MODELS_TEST: '/models/test',
  
  // Sentiment Analysis
  SENTIMENT_ANALYZE: '/sentiment/analyze',
  SENTIMENT_GLOBAL: '/sentiment/global',
  
  // AI Advisor
  AI_DECISION: '/ai/decision',
  AI_SIGNALS: '/ai/signals',
  
  // Datasets
  DATASETS_LIST: '/datasets/list',
  DATASET_PREVIEW: (name) => `/datasets/${name}/preview`,
  
  // Providers
  PROVIDERS: '/providers',
  PROVIDER_DETAILS: (id) => `/providers/${id}`,
  PROVIDER_HEALTH: (id) => `/providers/${id}/health-check`,
  PROVIDERS_CONFIG: '/providers/config',
  
  // Resources
  RESOURCES: '/resources',
  RESOURCES_DISCOVERY: '/resources/discovery/run',
  
  // Pools
  POOLS: '/pools',
  POOL_DETAILS: (id) => `/pools/${id}`,
  POOL_CREATE: '/pools',
  POOL_ROTATE: (id) => `/pools/${id}/rotate`,
  
  // Logs & Diagnostics
  LOGS: '/logs',
  LOGS_RECENT: '/logs/recent',
  LOGS_ERRORS: '/logs/errors',
  LOGS_CLEAR: '/logs',
  
  // HuggingFace Integration
  HF_HEALTH: '/hf/health',
  HF_RUN_SENTIMENT: '/hf/run-sentiment',
  
  // Feature Flags
  FEATURE_FLAGS: '/feature-flags',
  FEATURE_FLAG_UPDATE: (name) => `/feature-flags/${name}`,
  FEATURE_FLAGS_RESET: '/feature-flags/reset',
};

// ============================================================================
// PAGE METADATA
// ============================================================================

export const PAGE_METADATA = [
  {
    path: '/',
    page: 'dashboard',
    title: 'Dashboard | Crypto Monitor ULTIMATE',
    icon: 'dashboard',
    description: 'System overview and statistics',
    polling: true,
    interval: 30000,
  },
  {
    path: '/market',
    page: 'market',
    title: 'Market | Crypto Monitor ULTIMATE',
    icon: 'market',
    description: 'Real-time market data and charts',
    polling: true,
    interval: 30000,
  },
  {
    path: '/models',
    page: 'models',
    title: 'AI Models | Crypto Monitor ULTIMATE',
    icon: 'models',
    description: 'Machine learning models status',
    polling: false,
    interval: 0,
  },
  {
    path: '/sentiment',
    page: 'sentiment',
    title: 'Sentiment Analysis | Crypto Monitor ULTIMATE',
    icon: 'sentiment',
    description: 'AI-powered sentiment analysis',
    polling: false,
    interval: 0,
  },
  {
    path: '/ai-analyst',
    page: 'ai-analyst',
    title: 'AI Analyst | Crypto Monitor ULTIMATE',
    icon: 'aiAnalyst',
    description: 'AI trading advisor and decision support',
    polling: false,
    interval: 0,
  },
  {
    path: '/trading-assistant',
    page: 'trading-assistant',
    title: 'Trading Assistant | Crypto Monitor ULTIMATE',
    icon: 'trading',
    description: 'Trading signals and recommendations',
    polling: false,
    interval: 0,
  },
  {
    path: '/news',
    page: 'news',
    title: 'News | Crypto Monitor ULTIMATE',
    icon: 'news',
    description: 'Curated cryptocurrency news',
    polling: true,
    interval: 120000,
  },
  {
    path: '/providers',
    page: 'providers',
    title: 'Providers | Crypto Monitor ULTIMATE',
    icon: 'providers',
    description: 'API provider management',
    polling: true,
    interval: 60000,
  },
  {
    path: '/diagnostics',
    page: 'diagnostics',
    title: 'Diagnostics | Crypto Monitor ULTIMATE',
    icon: 'diagnostics',
    description: 'System diagnostics and logs',
    polling: false,
    interval: 0,
  },
  {
    path: '/api-explorer',
    page: 'api-explorer',
    title: 'API Explorer | Crypto Monitor ULTIMATE',
    icon: 'apiExplorer',
    description: 'Interactive API testing tool',
    polling: false,
    interval: 0,
  },
];

// ============================================================================
// UTILITY FUNCTIONS
// ============================================================================

/**
 * Get page metadata by path
 */
export function getPageMetadata(path) {
  return PAGE_METADATA.find(p => p.path === path) || PAGE_METADATA[0];
}

/**
 * Get polling interval for current page
 */
export function getPollingInterval(pageName) {
  const metadata = PAGE_METADATA.find(p => p.page === pageName);
  return metadata?.polling ? metadata.interval : 0;
}

/**
 * Build full API URL
 */
export function buildApiUrl(endpoint) {
  return `${CONFIG.API_BASE_URL}${endpoint}`;
}

/**
 * Get cache key for endpoint
 */
export function getCacheKey(endpoint) {
  return `${CONFIG.STORAGE_KEYS.CACHE_PREFIX}${endpoint}`;
}

// Export as default for convenience
export default {
  CONFIG,
  ROUTES,
  API_ENDPOINTS,
  PAGE_METADATA,
  getPageMetadata,
  getPollingInterval,
  buildApiUrl,
  getCacheKey,
};
