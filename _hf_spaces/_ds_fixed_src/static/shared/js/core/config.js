/**
 * Configuration for API endpoints
 * This file provides exports for the old api-client.js
 * @version 2025-12-04
 */

// API Keys
// Note: HuggingFace token should be obtained from backend or user settings
// Do not hardcode API keys in frontend code
export const API_KEYS = {
  ETHERSCAN: 'ETHERSCAN_API_KEY_HERE',
  ETHERSCAN_BACKUP: 'ETHERSCAN_API_KEY_HERE',
  BSCSCAN: 'BSCSCAN_API_KEY_HERE',
  TRONSCAN: 'TRONSCAN_API_KEY_HERE',
  CMC: 'COINMARKETCAP_API_KEY_HERE',
  CMC_BACKUP: 'COINMARKETCAP_API_KEY_HERE',
  NEWSAPI: 'NEWSAPI_API_KEY_HERE',
  CRYPTOCOMPARE: 'CRYPTOCOMPARE_API_KEY_HERE',
  // HUGGINGFACE: Should be retrieved from backend API or user settings
  // Backend reads from HF_API_TOKEN or HF_TOKEN environment variables
  HUGGINGFACE: null
};

// API Endpoints configuration
export const API_ENDPOINTS = {
  // Market Data
  coingecko: {
    baseUrl: 'https://api.coingecko.com/api/v3',
    endpoints: {
      simplePrice: '/simple/price',
      coins: '/coins',
      trending: '/search/trending',
      global: '/global'
    }
  },
  
  coinmarketcap: {
    baseUrl: 'https://pro-api.coinmarketcap.com/v1',
    key: API_KEYS.CMC,
    endpoints: {
      quotes: '/cryptocurrency/quotes/latest',
      listings: '/cryptocurrency/listings/latest'
    }
  },
  
  binance: {
    baseUrl: 'https://api.binance.com/api/v3',
    endpoints: {
      ticker: '/ticker/price',
      ticker24hr: '/ticker/24hr',
      klines: '/klines'
    }
  },
  
  coincap: {
    baseUrl: 'https://api.coincap.io/v2',
    endpoints: {
      assets: '/assets',
      history: '/assets/{id}/history'
    }
  },
  
  // News
  cryptopanic: {
    baseUrl: 'https://cryptopanic.com/api/v1',
    endpoints: {
      posts: '/posts'
    }
  },
  
  // Sentiment
  alternativeMe: {
    baseUrl: 'https://api.alternative.me',
    endpoints: {
      fng: '/fng'
    }
  },
  
  // Block Explorers
  etherscan: {
    baseUrl: 'https://api.etherscan.io/api',
    key: API_KEYS.ETHERSCAN,
    endpoints: {
      balance: '?module=account&action=balance',
      txlist: '?module=account&action=txlist'
    }
  },
  
  bscscan: {
    baseUrl: 'https://api.bscscan.com/api',
    key: API_KEYS.BSCSCAN,
    endpoints: {
      balance: '?module=account&action=balance',
      txlist: '?module=account&action=txlist'
    }
  },
  
  tronscan: {
    baseUrl: 'https://apilist.tronscanapi.com/api',
    key: API_KEYS.TRONSCAN,
    endpoints: {
      account: '/account',
      transactions: '/transaction'
    }
  }
};

// Page metadata for navigation
export const PAGE_METADATA = [
  { page: 'dashboard', title: 'Dashboard | Crypto Hub', icon: 'dashboard' },
  { page: 'market', title: 'Market | Crypto Hub', icon: 'trending_up' },
  { page: 'models', title: 'AI Models | Crypto Hub', icon: 'psychology' },
  { page: 'sentiment', title: 'Sentiment | Crypto Hub', icon: 'mood' },
  { page: 'ai-analyst', title: 'AI Analyst | Crypto Hub', icon: 'analytics' },
  { page: 'technical-analysis', title: 'Technical Analysis | Crypto Hub', icon: 'show_chart' },
  { page: 'trading-assistant', title: 'Trading | Crypto Hub', icon: 'attach_money' },
  { page: 'news', title: 'News | Crypto Hub', icon: 'newspaper' },
  { page: 'providers', title: 'Providers | Crypto Hub', icon: 'cloud' },
  { page: 'help', title: 'Help | Crypto Hub', icon: 'help' },
  { page: 'settings', title: 'Settings | Crypto Hub', icon: 'settings' }
];

// API configuration
export const API_CONFIG = {
  timeout: 10000,
  retries: 3,
  cacheTimeout: 60000, // 1 minute
  
  corsProxies: [
    'https://api.allorigins.win/get?url=',
    'https://proxy.cors.sh/',
    'https://api.codetabs.com/v1/proxy?quest='
  ]
};

// Detect environment
const IS_HUGGINGFACE = window.location.hostname.includes('hf.space') || window.location.hostname.includes('huggingface.co');
const IS_LOCALHOST = window.location.hostname === 'localhost' || window.location.hostname === '127.0.0.1';

// CONFIG object for api-client.js compatibility
export const CONFIG = {
  API_BASE_URL: window.location.origin,
  API_TIMEOUT: 10000,
  CACHE_TTL: 60000,
  MAX_RETRIES: 3,
  RETRY_DELAY: 1000,
  RETRIES: 3,
  IS_HUGGINGFACE: IS_HUGGINGFACE,
  IS_LOCALHOST: IS_LOCALHOST,
  ENVIRONMENT: IS_HUGGINGFACE ? 'huggingface' : IS_LOCALHOST ? 'local' : 'production'
};

// Helper function to build API URLs
export function buildApiUrl(endpoint, params = {}) {
  const base = CONFIG.API_BASE_URL;
  let url = `${base}${endpoint}`;
  
  if (Object.keys(params).length > 0) {
    const queryString = new URLSearchParams(params).toString();
    url += (url.includes('?') ? '&' : '?') + queryString;
  }
  
  return url;
}

// Helper function to get cache key
export function getCacheKey(endpoint, params = {}) {
  return `${endpoint}:${JSON.stringify(params)}`;
}

// Export default configuration
export default {
  CONFIG,
  API_KEYS,
  API_ENDPOINTS,
  PAGE_METADATA,
  API_CONFIG,
  buildApiUrl,
  getCacheKey
};
