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

import { CONFIG, API_ENDPOINTS, buildApiUrl, getCacheKey } from './config.js';

/**
 * Base API Client with caching and retry
 */
class APIClient {
  constructor(baseURL = CONFIG.API_BASE_URL) {
    this.baseURL = baseURL;
    this.cache = new Map();
    this.cacheTTL = CONFIG.CACHE_TTL;
    this.maxRetries = CONFIG.MAX_RETRIES;
    this.retryDelay = CONFIG.RETRY_DELAY;
    this.requestLog = [];
    this.errorLog = [];
    this.maxLogSize = 100;
  }

  /**
   * Core request method with retry logic
   */
  async request(endpoint, options = {}) {
    const url = `${this.baseURL}${endpoint}`;
    const method = options.method || 'GET';
    const startTime = performance.now();

    // Check cache for GET requests
    if (method === 'GET' && !options.skipCache) {
      const cached = this._getFromCache(endpoint);
      if (cached) {
        console.log(`[APIClient] Cache hit: ${endpoint}`);
        return cached;
      }
    }

    // Retry logic
    let lastError;
    for (let attempt = 1; attempt <= this.maxRetries; attempt++) {
      try {
        const response = await fetch(url, {
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

        // Cache successful GET responses
        if (method === 'GET') {
          this._saveToCache(endpoint, data);
        }

        // Log successful request
        this._logRequest({
          method,
          endpoint,
          status: response.status,
          duration: Math.round(duration),
          timestamp: Date.now(),
        });

        return data;

      } catch (error) {
        lastError = error;
        console.warn(`[APIClient] Attempt ${attempt}/${this.maxRetries} failed for ${endpoint}:`, error.message);

        if (attempt < this.maxRetries) {
          await this._sleep(this.retryDelay);
        }
      }
    }

    // All retries failed
    const duration = performance.now() - startTime;
    this._logError({
      method,
      endpoint,
      message: lastError.message,
      duration: Math.round(duration),
      timestamp: Date.now(),
    });

    throw new Error(`Failed after ${this.maxRetries} attempts: ${lastError.message}`);
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
  _getFromCache(key) {
    const cacheKey = getCacheKey(key);
    const cached = this.cache.get(cacheKey);

    if (!cached) return null;

    const now = Date.now();
    if (now - cached.timestamp > this.cacheTTL) {
      this.cache.delete(cacheKey);
      return null;
    }

    return cached.data;
  }

  /**
   * Save data to cache with timestamp
   */
  _saveToCache(key, data) {
    const cacheKey = getCacheKey(key);
    this.cache.set(cacheKey, {
      data,
      timestamp: Date.now(),
    });
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
   * Log error
   */
  _logError(entry) {
    this.errorLog.unshift(entry);
    if (this.errorLog.length > this.maxLogSize) {
      this.errorLog.pop();
    }
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
}

// ============================================================================
// EXPORT SINGLETON INSTANCE
// ============================================================================

export const api = new CryptoMonitorAPI();
export default api;

console.log('[APIClient] Initialized (HTTP-only, no WebSocket)');
