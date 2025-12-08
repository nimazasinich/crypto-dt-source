/**
 * Global Error Handler
 * Comprehensive error handling and user-friendly error messages
 */

class ErrorHandler {
  constructor() {
    this.errors = [];
    this.maxErrors = 100;
    this.init();
  }

  init() {
    // Catch all unhandled errors
    window.addEventListener('error', (event) => {
      this.handleError(event.error || event.message, 'Global Error');
      event.preventDefault();
    });

    // Catch unhandled promise rejections
    window.addEventListener('unhandledrejection', (event) => {
      this.handleError(event.reason, 'Unhandled Promise');
      event.preventDefault();
    });

    console.log('✅ Error Handler initialized');
  }

  /**
   * Handle error with fallback
   */
  handleError(error, context = 'Unknown') {
    const errorInfo = {
      message: this.getErrorMessage(error),
      context,
      timestamp: Date.now(),
      stack: error?.stack || null,
      url: window.location.href
    };

    // Log error
    console.error(`[${context}]`, error);

    // Store error
    this.errors.push(errorInfo);
    if (this.errors.length > this.maxErrors) {
      this.errors.shift();
    }

    // Show user-friendly message
    this.showUserError(errorInfo);
  }

  /**
   * Get user-friendly error message
   */
  getErrorMessage(error) {
    if (typeof error === 'string') return error;
    if (error?.message) return error.message;
    if (error?.toString) return error.toString();
    return 'An unknown error occurred';
  }

  /**
   * Show error to user
   */
  showUserError(errorInfo) {
    const message = this.getUserFriendlyMessage(errorInfo.message);
    
    if (window.uiManager) {
      window.uiManager.showToast(message, 'error', 5000);
    } else {
      // Fallback if UI Manager not loaded
      console.error('Error:', message);
      alert(message);
    }
  }

  /**
   * Convert technical error to user-friendly message
   */
  getUserFriendlyMessage(technicalMessage) {
    const lowerMessage = technicalMessage.toLowerCase();

    // Network errors
    if (lowerMessage.includes('network') || lowerMessage.includes('fetch')) {
      return '🌐 Network error. Please check your connection.';
    }

    // Timeout errors
    if (lowerMessage.includes('timeout') || lowerMessage.includes('timed out')) {
      return '⏱️ Request timed out. Please try again.';
    }

    // Not found errors
    if (lowerMessage.includes('404') || lowerMessage.includes('not found')) {
      return '🔍 Resource not found. It may have been moved or deleted.';
    }

    // Authorization errors
    if (lowerMessage.includes('401') || lowerMessage.includes('unauthorized')) {
      return '🔒 Authentication required. Please log in.';
    }

    // Forbidden errors
    if (lowerMessage.includes('403') || lowerMessage.includes('forbidden')) {
      return '🚫 Access denied. You don\'t have permission.';
    }

    // Server errors
    if (lowerMessage.includes('500') || lowerMessage.includes('server error')) {
      return '⚠️ Server error. We\'re working on it!';
    }

    // Database errors
    if (lowerMessage.includes('database') || lowerMessage.includes('sql')) {
      return '💾 Database error. Please try again later.';
    }

    // API errors
    if (lowerMessage.includes('api')) {
      return '🔌 API error. Using fallback data.';
    }

    // Default message
    return `⚠️ ${technicalMessage}`;
  }

  /**
   * Get error logs
   */
  getErrors() {
    return this.errors;
  }

  /**
   * Clear error logs
   */
  clearErrors() {
    this.errors = [];
  }

  /**
   * Export errors for debugging
   */
  exportErrors() {
    const data = JSON.stringify(this.errors, null, 2);
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = `errors-${Date.now()}.json`;
    a.click();
    
    URL.revokeObjectURL(url);
  }
}

// API Error Handler
class APIErrorHandler {
  static async handleAPIError(response, fallbackData = null) {
    let error = {
      status: response?.status || 500,
      statusText: response?.statusText || 'Unknown',
      url: response?.url || 'unknown'
    };

    try {
      const data = await response.json();
      error.message = data.message || data.error || 'API Error';
      error.details = data.details || null;
    } catch (e) {
      error.message = `HTTP ${error.status}: ${error.statusText}`;
    }

    console.error('API Error:', error);

    // Show user-friendly error
    if (window.errorHandler) {
      window.errorHandler.handleError(error, 'API Error');
    }

    // Return fallback data if provided
    if (fallbackData) {
      console.warn('Using fallback data due to API error');
      return {
        success: false,
        error: error.message,
        data: fallbackData,
        fallback: true
      };
    }

    throw error;
  }

  static async fetchWithFallback(url, options = {}, fallbackData = null) {
    try {
      const response = await fetch(url, {
        ...options,
        signal: options.signal || AbortSignal.timeout(options.timeout || 10000)
      });

      if (!response.ok) {
        return await this.handleAPIError(response, fallbackData);
      }

      const data = await response.json();
      return {
        success: true,
        data,
        fallback: false
      };
    } catch (error) {
      console.error('Fetch error:', error);

      if (window.errorHandler) {
        window.errorHandler.handleError(error, 'Fetch Error');
      }

      if (fallbackData) {
        return {
          success: false,
          error: error.message,
          data: fallbackData,
          fallback: true
        };
      }

      throw error;
    }
  }
}

// Form Validation Helper
class FormValidator {
  static validateRequired(value, fieldName) {
    if (!value || (typeof value === 'string' && value.trim() === '')) {
      return `${fieldName} is required`;
    }
    return null;
  }

  static validateEmail(email) {
    const re = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    if (!re.test(email)) {
      return 'Invalid email address';
    }
    return null;
  }

  static validateURL(url) {
    try {
      new URL(url);
      return null;
    } catch {
      return 'Invalid URL';
    }
  }

  static validateNumber(value, min = null, max = null) {
    const num = Number(value);
    if (isNaN(num)) {
      return 'Must be a number';
    }
    if (min !== null && num < min) {
      return `Must be at least ${min}`;
    }
    if (max !== null && num > max) {
      return `Must be at most ${max}`;
    }
    return null;
  }

  static validateForm(formElement) {
    const errors = {};
    const inputs = formElement.querySelectorAll('[data-validate]');

    inputs.forEach(input => {
      const rules = input.dataset.validate.split('|');
      const fieldName = input.name || input.id;

      rules.forEach(rule => {
        let error = null;

        if (rule === 'required') {
          error = this.validateRequired(input.value, fieldName);
        } else if (rule === 'email') {
          error = this.validateEmail(input.value);
        } else if (rule === 'url') {
          error = this.validateURL(input.value);
        } else if (rule.startsWith('number')) {
          const params = rule.match(/number\((\d+),(\d+)\)/);
          error = this.validateNumber(
            input.value,
            params ? parseInt(params[1]) : null,
            params ? parseInt(params[2]) : null
          );
        }

        if (error) {
          errors[fieldName] = error;
        }
      });
    });

    return {
      valid: Object.keys(errors).length === 0,
      errors
    };
  }
}

// Retry Helper
class RetryHelper {
  static async retry(fn, options = {}) {
    const {
      maxAttempts = 3,
      delay = 1000,
      backoff = 2,
      onRetry = null
    } = options;

    let lastError;

    for (let attempt = 1; attempt <= maxAttempts; attempt++) {
      try {
        return await fn();
      } catch (error) {
        lastError = error;
        
        if (attempt < maxAttempts) {
          const waitTime = delay * Math.pow(backoff, attempt - 1);
          console.warn(`Attempt ${attempt} failed, retrying in ${waitTime}ms...`);
          
          if (onRetry) {
            onRetry(attempt, error);
          }
          
          await new Promise(resolve => setTimeout(resolve, waitTime));
        }
      }
    }

    throw lastError;
  }
}

// Create global instances
const errorHandler = new ErrorHandler();

// Export
if (typeof module !== 'undefined' && module.exports) {
  module.exports = {
    ErrorHandler,
    APIErrorHandler,
    FormValidator,
    RetryHelper,
    errorHandler
  };
}

// Make available globally
window.errorHandler = errorHandler;
window.APIErrorHandler = APIErrorHandler;
window.FormValidator = FormValidator;
window.RetryHelper = RetryHelper;

console.log('✅ Error Handler loaded and ready');
