/**
 * API Helper Utilities
 * Shared utilities for API requests across all pages
 */

export class APIHelper {
  /**
   * Get request headers with optional authorization
   * @returns {Object} Headers object
   */
  static getHeaders() {
    const token = localStorage.getItem('HF_TOKEN');
    const headers = {
      'Content-Type': 'application/json'
    };
    
    if (token && token.trim()) {
      // Check if token is expired
      if (this.isTokenExpired(token)) {
        console.warn('[APIHelper] Token expired, removing from storage');
        localStorage.removeItem('HF_TOKEN');
      } else {
        headers['Authorization'] = `Bearer ${token}`;
      }
    }
    
    return headers;
  }

  /**
   * Check if JWT token is expired
   * @param {string} token - JWT token
   * @returns {boolean} True if expired
   */
  static isTokenExpired(token) {
    try {
      // Basic JWT expiration check
      const parts = token.split('.');
      if (parts.length !== 3) return false; // Not a JWT
      
      const payload = JSON.parse(atob(parts[1]));
      if (!payload.exp) return false; // No expiration
      
      const now = Math.floor(Date.now() / 1000);
      return payload.exp < now;
    } catch (e) {
      console.warn('[APIHelper] Token validation error:', e);
      return false;
    }
  }

  /**
   * Fetch data from API with automatic error handling
   * @param {string} url - API endpoint
   * @param {Object} options - Fetch options
   * @returns {Promise<any>} Response data
   */
  static async fetchAPI(url, options = {}) {
    const headers = this.getHeaders();
    
    try {
      const response = await fetch(url, {
        ...options,
        headers: {
          ...headers,
          ...options.headers
        }
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}: ${response.statusText}`);
      }

      const contentType = response.headers.get('content-type');
      if (contentType && contentType.includes('application/json')) {
        return await response.json();
      }
      
      return await response.text();
    } catch (error) {
      console.error(`[APIHelper] Fetch error for ${url}:`, error);
      
      // Return fallback data instead of throwing
      return this._getFallbackData(url, error);
    }
  }

  /**
   * Get fallback data for failed API requests
   * @private
   */
  static _getFallbackData(url, error) {
    // Return appropriate fallback based on URL
    if (url.includes('/resources/summary') || url.includes('/resources')) {
      return {
        success: false,
        error: error.message,
        summary: {
          total_resources: 0,
          free_resources: 0,
          models_available: 0,
          total_api_keys: 0,
          categories: {}
        },
        fallback: true
      };
    }
    
    if (url.includes('/models/status')) {
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
    
    if (url.includes('/models/summary') || url.includes('/models')) {
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
    
    if (url.includes('/health') || url.includes('/status')) {
      return {
        status: 'offline',
        healthy: false,
        error: error.message,
        fallback: true
      };
    }
    
    // Generic fallback
    return {
      error: error.message,
      fallback: true,
      data: null
    };
  }

  /**
   * Extract array from various response formats
   * @param {any} data - API response data
   * @param {string[]} keys - Possible keys containing array data
   * @returns {Array} Extracted array or empty array
   */
  static extractArray(data, keys = ['data', 'items', 'results', 'list']) {
    // Direct array
    if (Array.isArray(data)) {
      return data;
    }

    // Check common keys
    for (const key of keys) {
      if (data && Array.isArray(data[key])) {
        return data[key];
      }
    }

    // Object values
    if (data && typeof data === 'object' && !Array.isArray(data)) {
      const values = Object.values(data);
      if (values.length > 0 && values.every(v => typeof v === 'object')) {
        return values;
      }
    }

    console.warn('[APIHelper] Could not extract array from:', data);
    return [];
  }

  /**
   * Check API health
   * @returns {Promise<Object>} Health status
   */
  static async checkHealth() {
    try {
      const controller = new AbortController();
      const timeoutId = setTimeout(() => controller.abort(), 5000);
      
      const response = await fetch('/api/health', {
        signal: controller.signal,
        cache: 'no-cache'
      });
      
      clearTimeout(timeoutId);
      
      if (response.ok) {
        const data = await response.json();
        return {
          status: 'online',
          healthy: true,
          data: data
        };
      } else {
        return {
          status: 'degraded',
          healthy: false,
          httpStatus: response.status
        };
      }
    } catch (error) {
      return {
        status: 'offline',
        healthy: false,
        error: error.message
      };
    }
  }

  /**
   * Setup periodic health monitoring
   * @param {Function} callback - Callback function with health status
   * @param {number} interval - Check interval in ms (default: 30000)
   * @returns {number} Interval ID
   */
  static monitorHealth(callback, interval = 30000) {
    // Initial check
    this.checkHealth().then(callback);
    
    // Periodic checks
    return setInterval(async () => {
      if (!document.hidden) {
        const health = await this.checkHealth();
        callback(health);
      }
    }, interval);
  }

  /**
   * Show toast notification
   * @param {string} message - Message to display
   * @param {string} type - Type: success, error, warning, info
   * @param {number} duration - Display duration in ms
   */
  static showToast(message, type = 'info', duration = 3000) {
    const colors = {
      success: '#22c55e',
      error: '#ef4444',
      warning: '#f59e0b',
      info: '#3b82f6'
    };
    
    const toast = document.createElement('div');
    toast.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      padding: 12px 20px;
      border-radius: 8px;
      background: ${colors[type] || colors.info};
      color: white;
      font-weight: 500;
      z-index: 9999;
      box-shadow: 0 4px 12px rgba(0,0,0,0.3);
      animation: slideIn 0.3s ease;
    `;
    toast.textContent = message;
    
    document.body.appendChild(toast);
    setTimeout(() => {
      toast.style.animation = 'slideOut 0.3s ease';
      setTimeout(() => toast.remove(), 300);
    }, duration);
  }

  /**
   * Format number with locale
   * @param {number} num - Number to format
   * @param {Object} options - Intl.NumberFormat options
   * @returns {string} Formatted number
   */
  static formatNumber(num, options = {}) {
    return new Intl.NumberFormat('en-US', options).format(num);
  }

  /**
   * Format currency
   * @param {number} amount - Amount to format
   * @param {string} currency - Currency code (default: USD)
   * @returns {string} Formatted currency
   */
  static formatCurrency(amount, currency = 'USD') {
    return this.formatNumber(amount, {
      style: 'currency',
      currency: currency,
      minimumFractionDigits: 2,
      maximumFractionDigits: 2
    });
  }

  /**
   * Format percentage
   * @param {number} value - Value to format
   * @param {number} decimals - Decimal places
   * @returns {string} Formatted percentage
   */
  static formatPercentage(value, decimals = 2) {
    return `${value >= 0 ? '+' : ''}${value.toFixed(decimals)}%`;
  }

  /**
   * Debounce function
   * @param {Function} func - Function to debounce
   * @param {number} wait - Wait time in ms
   * @returns {Function} Debounced function
   */
  static debounce(func, wait = 300) {
    let timeout;
    return function executedFunction(...args) {
      const later = () => {
        clearTimeout(timeout);
        func(...args);
      };
      clearTimeout(timeout);
      timeout = setTimeout(later, wait);
    };
  }

  /**
   * Throttle function
   * @param {Function} func - Function to throttle
   * @param {number} limit - Time limit in ms
   * @returns {Function} Throttled function
   */
  static throttle(func, limit = 300) {
    let inThrottle;
    return function executedFunction(...args) {
      if (!inThrottle) {
        func(...args);
        inThrottle = true;
        setTimeout(() => (inThrottle = false), limit);
      }
    };
  }
}

export default APIHelper;

