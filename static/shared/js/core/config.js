/**
 * Configuration for API endpoints
 * This file provides exports for the old api-client.js
 * @version 2025-12-04
 */

// API Keys
export const API_KEYS = {
  // Never hardcode secrets in client-side code.
  ETHERSCAN: '',
  ETHERSCAN_BACKUP: '',
  BSCSCAN: '',
  TRONSCAN: '',
  CMC: '',
  CMC_BACKUP: '',
  NEWSAPI: '',
  CRYPTOCOMPARE: '',
  HUGGINGFACE: ''
};

// Backend API Endpoints (HuggingFace Space)
export const API_BASE_URL = window.location.origin;

// Complete API Endpoints mapping
export const API_ENDPOINTS = {
  // Health & Status
  health: '/api/health',
  status: '/api/status',
  routers: '/api/routers',
  monitoring: '/api/monitoring/status',
  
  // Market Data
  rate: '/api/service/rate',
  rateBatch: '/api/service/rate/batch',
  coinsTop: '/api/coins/top',
  trending: '/api/trending',
  market: '/api/market',
  marketTop: '/api/market/top',
  marketTrending: '/api/market/trending',
  history: '/api/service/history',
  ohlc: '/api/market/ohlc',
  
  // Sentiment & AI
  sentimentGlobal: '/api/sentiment/global',
  sentimentAsset: '/api/sentiment/asset',
  sentimentAnalyze: '/api/service/sentiment',
  aiSignals: '/api/ai/signals',
  aiDecision: '/api/ai/decision',
  
  // News
  news: '/api/news',
  newsLatest: '/api/news/latest',
  
  // Models
  modelsList: '/api/models/list',
  modelsStatus: '/api/models/status',
  modelsSummary: '/api/models/summary',
  modelsHealth: '/api/models/health',
  modelsTest: '/api/models/test',
  modelsReinitialize: '/api/models/reinitialize',
  
  // Trading
  ohlcv: '/api/ohlcv',
  backtest: '/api/trading/backtest',
  futuresPositions: '/api/futures/positions',
  
  // Technical Analysis
  technicalQuick: '/api/technical/quick',
  technicalComprehensive: '/api/technical/comprehensive',
  technicalRisk: '/api/technical/risk',
  
  // Resources
  resources: '/api/resources',
  resourcesSummary: '/api/resources/summary',
  resourcesStats: '/api/resources/stats',
  resourcesCategories: '/api/resources/categories',
  resourcesCategory: '/api/resources/category',
  resourcesApis: '/api/resources/apis',
  providers: '/api/providers',
  
  // Advanced
  multiSourceData: '/api/multi-source/data',
  sourcesAll: '/api/sources/all',
  testSource: '/api/test-source',
  
  // External APIs (for reference)
  external: {
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
    
    alternativeMe: {
      baseUrl: 'https://api.alternative.me',
      endpoints: {
        fng: '/fng'
      }
    },
    
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
  }
};

// Page metadata for navigation
export const PAGE_METADATA = [
  { page: 'dashboard', title: 'Dashboard | Crypto Hub', icon: 'dashboard' },
  { page: 'market', title: 'Market Data | Crypto Hub', icon: 'trending_up' },
  { page: 'models', title: 'AI Models | Crypto Hub', icon: 'psychology' },
  { page: 'sentiment', title: 'Sentiment Analysis | Crypto Hub', icon: 'sentiment_satisfied' },
  { page: 'ai-analyst', title: 'AI Analyst | Crypto Hub', icon: 'smart_toy' },
  { page: 'trading-assistant', title: 'Trading Assistant | Crypto Hub', icon: 'show_chart' },
  { page: 'news', title: 'Crypto News | Crypto Hub', icon: 'article' },
  { page: 'providers', title: 'API Providers | Crypto Hub', icon: 'cloud' },
  { page: 'diagnostics', title: 'System Diagnostics | Crypto Hub', icon: 'monitor_heart' },
  { page: 'api-explorer', title: 'API Explorer | Crypto Hub', icon: 'code' }
];

// Polling intervals (milliseconds)
export const POLLING_INTERVALS = {
  health: 30000,      // 30 seconds
  market: 10000,      // 10 seconds
  sentiment: 60000,   // 1 minute
  news: 300000,       // 5 minutes
  models: 60000       // 1 minute
};

// Cache TTL (milliseconds)
export const CACHE_TTL = {
  health: 10000,      // 10 seconds
  market: 30000,      // 30 seconds
  sentiment: 60000,   // 1 minute
  news: 300000,       // 5 minutes
  static: 3600000     // 1 hour
};

// API configuration
export const API_CONFIG = {
  timeout: 10000,
  retries: 3,
  cacheTimeout: 60000, // 1 minute
  
  corsProxies: [
    // Disabled on Hugging Face Spaces (avoid third-party proxy dependencies)
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
