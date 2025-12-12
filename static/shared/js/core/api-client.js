/**
 * API Client for Crypto Monitor ULTIMATE
 * 
 * Features:
 * - Pure HTTP/Fetch API (NO WEBSOCKET)
 * - Simple caching mechanism
 * - Automatic retry logic
 * - Request/error logging
 * - ES6 module exports
 */

import { CONFIG, API_BASE_URL, API_ENDPOINTS, CACHE_TTL, buildApiUrl, getCacheKey } from './config.js';

/**
 * Base API Client with caching and retry
 */
class APIClient {
  constructor(baseURL = API_BASE_URL) {
    this.baseURL = baseURL;
    this.cache = new Map();
    this.cacheTTL = CACHE_TTL.market || 30000;
    this.maxRetries = CONFIG.MAX_RETRIES || 3;
    this.retryDelay = CONFIG.RETRY_DELAY || 1000;
    this.requestLog = [];
    this.errorLog = [];
    this.maxLogSize = 100;
    this.pendingRequests = new Map();
  }

  /**
   * Core request method with retry logic
   */
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const method = options.method || 'GET';
    const cacheKey = this._getCacheKey(url, options.params);
    const startTime = performance.now();

    // Check cache for GET requests (but skip cache for models/status to get fresh data)
    if (method === 'GET' && !options.skipCache) {
      // Don't cache models status/summary - always get fresh data
      const shouldSkipCache = endpoint.includes('/models/status') || 
                             endpoint.includes('/models/summary') ||
                             options.forceRefresh;
      
      if (!shouldSkipCache) {
        const cached = this._getFromCache(cacheKey, options.ttl);
        if (cached) {
          console.log(`[APIClient] Cache hit: ${endpoint}`);
          return cached;
        }
      }
    }
    
    // Deduplicate pending requests
    if (this.pendingRequests.has(cacheKey)) {
      console.log(`[APIClient] Deduplicating request: ${endpoint}`);
      return this.pendingRequests.get(cacheKey);
    }
    
    // Build URL with params
    const urlWithParams = this._buildURL(url, options.params);

    // Retry logic
    let lastError;
    const requestPromise = (async () => {
      for (let attempt = 1; attempt <= this.maxRetries; attempt++) {
        try {
          const response = await fetch(urlWithParams, {
            method,
            headers: {
              'Content-Type': 'application/json',
              ...options.headers,
            },
            body: options.body ? JSON.stringify(options.body) : undefined,
            signal: options.signal,
          });

          if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
          }

          const data = await response.json();
          const duration = performance.now() - startTime;

          // Cache successful GET responses (but not models status/summary)
          if (method === 'GET' && !endpoint.includes('/models/status') && !endpoint.includes('/models/summary')) {
            this._saveToCache(cacheKey, data, options.ttl);
          }

          // Log successful request
          this._logRequest({
            method,
            endpoint,
            status: response.status,
            duration: Math.round(duration),
            timestamp: Date.now(),
          });
          
          this.pendingRequests.delete(cacheKey);
          return data;

        } catch (error) {
          lastError = error;
        const errorDetails = {
          attempt,
          maxRetries: this.maxRetries,
          endpoint,
          message: error.message,
          name: error.name,
          stack: error.stack
        };
        
        console.warn(`[APIClient] Attempt ${attempt}/${this.maxRetries} failed for ${endpoint}:`, error.message);
        
        // Log detailed error info for debugging
        if (attempt === this.maxRetries) {
          console.error('[APIClient] All retries exhausted. Error details:', errorDetails);
        }

        if (attempt < this.maxRetries) {
          await this._sleep(this.retryDelay);
        }
      }
    }

      // All retries failed - return fallback data instead of throwing
      const duration = performance.now() - startTime;
      this._logError({
        method,
        endpoint,
        message: lastError?.message || lastError?.toString() || 'Unknown error',
        duration: Math.round(duration),
        timestamp: Date.now(),
      });

      this.pendingRequests.delete(cacheKey);
      
      // Return fallback data based on endpoint type
      return this._getFallbackData(endpoint, lastError);
    })();
    
    this.pendingRequests.set(cacheKey, requestPromise);
    return requestPromise;
  }

  /**
   * GET request
   */
  async get(endpoint, options = {}) {
    return this.request(endpoint, { ...options, method: 'GET' });
  }

  /**
   * POST request
   */
  async post(endpoint, data, options = {}) {
    return this.request(endpoint, {
      ...options,
      method: 'POST',
      body: data,
    });
  }

  /**
   * PUT request
   */
  async put(endpoint, data, options = {}) {
    return this.request(endpoint, {
      ...options,
      method: 'PUT',
      body: data,
    });
  }

  /**
   * DELETE request
   */
  async delete(endpoint, options = {}) {
    return this.request(endpoint, { ...options, method: 'DELETE' });
  }

  // ========================================================================
  // CACHE MANAGEMENT
  // ========================================================================

  /**
   * Get data from cache if not expired
   */
  _getFromCache(key, ttl) {
    const cached = this.cache.get(key);

    if (!cached) return null;

    const now = Date.now();
    const cacheTTL = ttl || this.cacheTTL;
    if (now - cached.timestamp > cacheTTL) {
      this.cache.delete(key);
      return null;
    }

    return cached.data;
  }

  /**
   * Save data to cache with timestamp
   */
  _saveToCache(key, data, ttl) {
    this.cache.set(key, {
      data,
      timestamp: Date.now(),
      ttl: ttl || this.cacheTTL
    });
  }
  
  /**
   * Build URL with query params
   * @private
   */
  _buildURL(url, params) {
    if (!params || Object.keys(params).length === 0) return url;
    const searchParams = new URLSearchParams();
    for (const [key, value] of Object.entries(params)) {
      if (value !== null && value !== undefined) {
        searchParams.append(key, String(value));
      }
    }
    const queryString = searchParams.toString();
    return queryString ? `${url}?${queryString}` : url;
  }
  
  /**
   * Get cache key for request
   * @private
   */
  _getCacheKey(url, params) {
    return params ? `${url}?${JSON.stringify(params)}` : url;
  }

  /**
   * Clear all cache
   */
  clearCache() {
    this.cache.clear();
    console.log('[APIClient] Cache cleared');
  }

  /**
   * Clear specific cache entry
   */
  clearCacheEntry(key) {
    const cacheKey = getCacheKey(key);
    this.cache.delete(cacheKey);
  }

  // ========================================================================
  // LOGGING
  // ========================================================================

  /**
   * Log successful request
   */
  _logRequest(entry) {
    this.requestLog.unshift(entry);
    if (this.requestLog.length > this.maxLogSize) {
      this.requestLog.pop();
    }
  }

  /**
   * Log error with enhanced details
   */
  _logError(entry) {
    // Add timestamp if not present
    if (!entry.timestamp) {
      entry.timestamp = Date.now();
    }
    
    // Add formatted time for readability
    entry.time = new Date(entry.timestamp).toISOString();
    
    this.errorLog.unshift(entry);
    if (this.errorLog.length > this.maxLogSize) {
      this.errorLog.pop();
    }
    
    // Also log to console for immediate visibility
    console.error('[APIClient] Error logged:', {
      endpoint: entry.endpoint,
      method: entry.method,
      message: entry.message,
      duration: entry.duration
    });
  }

  /**
   * Get request logs
   */
  getRequestLogs(limit = 20) {
    return this.requestLog.slice(0, limit);
  }

  /**
   * Get error logs
   */
  getErrorLogs(limit = 20) {
    return this.errorLog.slice(0, limit);
  }

  // ========================================================================
  // UTILITY
  // ========================================================================

  /**
   * Sleep utility for retry delays
   */
  _sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Get fallback data for failed requests
   * @private
   */
  _getFallbackData(endpoint, error) {
    // Return appropriate fallback based on endpoint
    if (endpoint.includes('/resources/summary')) {
      return {
        success: false,
        error: error.message,
        summary: {
          total_resources: 0,
          free_resources: 0,
          models_available: 0,
          local_routes_count: 0,
          total_api_keys: 0,
          categories: {}
        },
        fallback: true,
        timestamp: new Date().toISOString()
      };
    }
    
    if (endpoint.includes('/models/status')) {
      return {
        success: false,
        error: error.message,
        status: 'error',
        status_message: `Error: ${error.message}`,
        models_loaded: 0,
        models_failed: 0,
        hf_mode: 'unknown',
        transformers_available: false,
        fallback: true,
        timestamp: new Date().toISOString()
      };
    }
    
    if (endpoint.includes('/models/summary')) {
      return {
        ok: false,
        error: error.message,
        summary: {
          total_models: 0,
          loaded_models: 0,
          failed_models: 0,
          hf_mode: 'error',
          transformers_available: false
        },
        categories: {},
        health_registry: [],
        fallback: true,
        timestamp: new Date().toISOString()
      };
    }
    
    if (endpoint.includes('/health') || endpoint.includes('/status')) {
      return {
        status: 'offline',
        healthy: false,
        error: error.message,
        fallback: true,
        timestamp: new Date().toISOString()
      };
    }
    
    // Generic fallback
    return {
      error: error.message,
      fallback: true,
      data: null,
      timestamp: new Date().toISOString()
    };
  }
}

/**
 * Crypto Monitor API Client with pre-configured endpoints
 */
export class CryptoMonitorAPI extends APIClient {
  // ========================================================================
  // HEALTH & STATUS
  // ========================================================================

  async getHealth() {
    return this.get(API_ENDPOINTS.HEALTH);
  }

  async getStatus() {
    return this.get(API_ENDPOINTS.STATUS);
  }

  async getStats() {
    return this.get(API_ENDPOINTS.STATS);
  }

  async getResources() {
    return this.get(API_ENDPOINTS.RESOURCES);
  }

  // ========================================================================
  // MARKET DATA
  // ========================================================================

  async getMarket() {
    return this.get(API_ENDPOINTS.MARKET);
  }

  async getTrending() {
    return this.get(API_ENDPOINTS.TRENDING);
  }

  async getSentiment() {
    return this.get(API_ENDPOINTS.SENTIMENT);
  }

  async getDefi() {
    return this.get(API_ENDPOINTS.DEFI);
  }

  async getTopCoins(limit = 50) {
    return this.get(`${API_ENDPOINTS.COINS_TOP}?limit=${limit}`);
  }

  async getCoinDetails(symbol) {
    return this.get(API_ENDPOINTS.COIN_DETAILS(symbol));
  }

  // ========================================================================
  // CHARTS
  // ========================================================================

  async getPriceChart(symbol, timeframe = '7D') {
    return this.get(`${API_ENDPOINTS.PRICE_CHART(symbol)}?timeframe=${timeframe}`);
  }

  async analyzeChart(symbol, timeframe, indicators) {
    return this.post(API_ENDPOINTS.ANALYZE_CHART, {
      symbol,
      timeframe,
      indicators,
    });
  }

  // ========================================================================
  // NEWS
  // ========================================================================

  async getLatestNews(limit = 40) {
    return this.get(`${API_ENDPOINTS.NEWS_LATEST}?limit=${limit}`);
  }

  async analyzeNews(title, content) {
    return this.post(API_ENDPOINTS.NEWS_ANALYZE, { title, content });
  }

  async summarizeNews(title, content) {
    return this.post(API_ENDPOINTS.NEWS_SUMMARIZE, { title, content });
  }

  // ========================================================================
  // AI/ML MODELS
  // ========================================================================

  async getModelsList() {
    return this.get(API_ENDPOINTS.MODELS_LIST);
  }

  async getModelsStatus() {
    return this.get(API_ENDPOINTS.MODELS_STATUS);
  }

  async getModelsStats() {
    return this.get(API_ENDPOINTS.MODELS_STATS);
  }

  async testModel(modelName, input) {
    return this.post(API_ENDPOINTS.MODELS_TEST, {
      model: modelName,
      input,
    });
  }

  // ========================================================================
  // SENTIMENT ANALYSIS
  // ========================================================================

  async analyzeSentiment(text, mode = 'crypto', model = null) {
    return this.post(API_ENDPOINTS.SENTIMENT_ANALYZE, {
      text,
      mode,
      model,
    });
  }

  async getGlobalSentiment() {
    return this.get(API_ENDPOINTS.SENTIMENT_GLOBAL);
  }

  // ========================================================================
  // AI ADVISOR
  // ========================================================================

  async getAIDecision(symbol, horizon, riskTolerance, context, model) {
    return this.post(API_ENDPOINTS.AI_DECISION, {
      symbol,
      horizon,
      risk_tolerance: riskTolerance,
      context,
      model,
    });
  }

  async getAISignals(symbol) {
    return this.get(`${API_ENDPOINTS.AI_SIGNALS}?symbol=${symbol}`);
  }

  // ========================================================================
  // DATASETS
  // ========================================================================

  async getDatasetsList() {
    return this.get(API_ENDPOINTS.DATASETS_LIST);
  }

  async previewDataset(name, limit = 10) {
    return this.get(`${API_ENDPOINTS.DATASET_PREVIEW(name)}?limit=${limit}`);
  }

  // ========================================================================
  // PROVIDERS
  // ========================================================================

  async getProviders() {
    return this.get(API_ENDPOINTS.PROVIDERS);
  }

  async getProviderDetails(id) {
    return this.get(API_ENDPOINTS.PROVIDER_DETAILS(id));
  }

  async checkProviderHealth(id) {
    return this.get(API_ENDPOINTS.PROVIDER_HEALTH(id));
  }

  async getProvidersConfig() {
    return this.get(API_ENDPOINTS.PROVIDERS_CONFIG);
  }

  // ========================================================================
  // LOGS & DIAGNOSTICS
  // ========================================================================

  async getLogs() {
    return this.get(API_ENDPOINTS.LOGS);
  }

  async getRecentLogs(limit = 50) {
    return this.get(`${API_ENDPOINTS.LOGS_RECENT}?limit=${limit}`);
  }

  async getErrorLogs(limit = 50) {
    return this.get(`${API_ENDPOINTS.LOGS_ERRORS}?limit=${limit}`);
  }

  async clearLogs() {
    return this.delete(API_ENDPOINTS.LOGS_CLEAR);
  }

  // ========================================================================
  // RESOURCES
  // ========================================================================

  async runResourceDiscovery() {
    return this.post(API_ENDPOINTS.RESOURCES_DISCOVERY);
  }

  // ========================================================================
  // HUGGINGFACE INTEGRATION
  // ========================================================================

  async getHFHealth() {
    return this.get(API_ENDPOINTS.HF_HEALTH);
  }

  async runHFSentiment(text) {
    return this.post(API_ENDPOINTS.HF_RUN_SENTIMENT, { text });
  }

  // ========================================================================
  // FEATURE FLAGS
  // ========================================================================

  async getFeatureFlags() {
    return this.get(API_ENDPOINTS.FEATURE_FLAGS);
  }

  async updateFeatureFlag(name, value) {
    return this.put(API_ENDPOINTS.FEATURE_FLAG_UPDATE(name), { value });
  }

  async resetFeatureFlags() {
    return this.post(API_ENDPOINTS.FEATURE_FLAGS_RESET);
  }

  // ========================================================================
  // SETTINGS
  // ========================================================================

  async getSettings() {
    return this.get(API_ENDPOINTS.SETTINGS);
  }

  async saveTokens(tokens) {
    return this.post(API_ENDPOINTS.SETTINGS_TOKENS, tokens);
  }

  async saveTelegramSettings(settings) {
    return this.post(API_ENDPOINTS.SETTINGS_TELEGRAM, settings);
  }

  async saveSignalSettings(settings) {
    return this.post(API_ENDPOINTS.SETTINGS_SIGNALS, settings);
  }

  async saveSchedulingSettings(settings) {
    return this.post(API_ENDPOINTS.SETTINGS_SCHEDULING, settings);
  }

  async saveNotificationSettings(settings) {
    return this.post(API_ENDPOINTS.SETTINGS_NOTIFICATIONS, settings);
  }

  async saveAppearanceSettings(settings) {
    return this.post(API_ENDPOINTS.SETTINGS_APPEARANCE, settings);
  }
}

// ============================================================================
// EXPORT SINGLETON INSTANCE
// ============================================================================

export const api = new CryptoMonitorAPI();
export default api;

/**
 * Export apiClient alias with fetch method for compatibility
 * This allows files to use apiClient.fetch() pattern
 */
export const apiClient = {
  async fetch(url, options = {}) {
    // Convert fetch-style call to api method
    const method = (options.method || 'GET').toUpperCase();
    const endpoint = url.replace(/^.*\/api/, '/api');
    
    try {
      let data;
      if (method === 'GET') {
        data = await api.get(endpoint, { skipCache: options.skipCache, forceRefresh: options.forceRefresh });
      } else if (method === 'POST') {
        const body = options.body ? (typeof options.body === 'string' ? JSON.parse(options.body) : options.body) : {};
        data = await api.post(endpoint, body);
      } else if (method === 'PUT') {
        const body = options.body ? (typeof options.body === 'string' ? JSON.parse(options.body) : options.body) : {};
        data = await api.put(endpoint, body);
      } else if (method === 'DELETE') {
        data = await api.delete(endpoint);
      } else {
        data = await api.get(endpoint);
      }
      
      // Return a Response-like object
      return new Response(JSON.stringify(data), {
        status: 200,
        statusText: 'OK',
        headers: { 'Content-Type': 'application/json' }
      });
    } catch (error) {
      // Return error response
      return new Response(JSON.stringify({ 
        error: error.message || 'Request failed',
        success: false 
      }), {
        status: error.status || 500,
        statusText: error.statusText || 'Internal Server Error',
        headers: { 'Content-Type': 'application/json' }
      });
    }
  }
};

console.log('[APIClient] Initialized (HTTP-only, no WebSocket)');
