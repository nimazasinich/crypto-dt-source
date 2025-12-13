/**
 * API Client with Request Throttling, Caching, and Error Handling
 * Prevents excessive API calls and handles security challenges gracefully
 */

class APIClient {
  constructor() {
    this.cache = new Map();
    this.requestQueue = new Map();
    this.retryDelays = new Map();
    this.maxRetries = 3;
    this.defaultCacheTTL = 30000; // 30 seconds
    this.requestTimeout = 8000; // 8 seconds
  }

  /**
   * Make a fetch request with throttling, caching, and retry logic
   * @param {string} url - Request URL
   * @param {Object} options - Fetch options
   * @param {number} cacheTTL - Cache TTL in milliseconds
   * @returns {Promise<Response>}
   */
  async fetch(url, options = {}, cacheTTL = this.defaultCacheTTL) {
    const cacheKey = `${url}:${JSON.stringify(options)}`;
    
    // Check cache first
    if (cacheTTL > 0 && this.cache.has(cacheKey)) {
      const cached = this.cache.get(cacheKey);
      if (Date.now() - cached.timestamp < cacheTTL) {
        return cached.response.clone();
      }
      this.cache.delete(cacheKey);
    }

    // Throttle duplicate requests
    if (this.requestQueue.has(cacheKey)) {
      return this.requestQueue.get(cacheKey);
    }

    // Create request promise
    const requestPromise = this._makeRequest(url, options, cacheKey, cacheTTL);
    this.requestQueue.set(cacheKey, requestPromise);

    try {
      const response = await requestPromise;
      return response;
    } finally {
      // Clean up queue after a delay to allow concurrent requests to share the promise
      setTimeout(() => {
        this.requestQueue.delete(cacheKey);
      }, 100);
    }
  }

  /**
   * Internal method to make the actual request with retry logic
   * @private
   */
  async _makeRequest(url, options, cacheKey, cacheTTL) {
    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), this.requestTimeout);

    let lastError;
    let retryCount = 0;

    while (retryCount <= this.maxRetries) {
      try {
        const response = await fetch(url, {
          ...options,
          signal: controller.signal,
          headers: {
            'Accept': 'application/json',
            ...options.headers
          }
        });

        clearTimeout(timeoutId);

        // Handle security challenges (AWS WAF, etc.)
        if (response.status === 403 || response.status === 429) {
          // Rate limited or blocked - use exponential backoff
          const delay = Math.min(1000 * Math.pow(2, retryCount), 10000);
          await this._delay(delay);
          
          if (retryCount < this.maxRetries) {
            retryCount++;
            continue;
          }
          
          // Return a fallback response instead of throwing
          return this._createFallbackResponse(url);
        }

        // Cache successful responses
        if (response.ok && cacheTTL > 0) {
          this.cache.set(cacheKey, {
            response: response.clone(),
            timestamp: Date.now()
          });
        }

        return response;
      } catch (error) {
        clearTimeout(timeoutId);
        lastError = error;

        // Don't retry on abort (timeout)
        if (error.name === 'AbortError') {
          break;
        }

        // Retry on network errors
        if (retryCount < this.maxRetries) {
          const delay = this._getRetryDelay(retryCount);
          await this._delay(delay);
          retryCount++;
          
          // Create new controller for retry
          const newController = new AbortController();
          const newTimeoutId = setTimeout(() => newController.abort(), this.requestTimeout);
          Object.assign(controller, newController);
          timeoutId = newTimeoutId;
        } else {
          break;
        }
      }
    }

    // All retries failed - return fallback
    console.warn(`[APIClient] Request failed after ${retryCount} retries:`, url);
    return this._createFallbackResponse(url);
  }

  /**
   * Get retry delay with exponential backoff
   * @private
   */
  _getRetryDelay(retryCount) {
    const baseDelay = 500;
    return Math.min(baseDelay * Math.pow(2, retryCount), 5000);
  }

  /**
   * Delay helper
   * @private
   */
  _delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }

  /**
   * Create a fallback response for failed requests
   * @private
   */
  _createFallbackResponse(url) {
    return new Response(
      JSON.stringify({ 
        error: 'Service temporarily unavailable',
        fallback: true,
        url 
      }),
      {
        status: 200,
        statusText: 'OK',
        headers: { 'Content-Type': 'application/json' }
      }
    );
  }

  /**
   * Clear cache
   */
  clearCache() {
    this.cache.clear();
  }

  /**
   * Clear cache for specific URL pattern
   */
  clearCacheFor(urlPattern) {
    for (const key of this.cache.keys()) {
      if (key.includes(urlPattern)) {
        this.cache.delete(key);
      }
    }
  }
}

// Export singleton instance
export const apiClient = new APIClient();
export default apiClient;
