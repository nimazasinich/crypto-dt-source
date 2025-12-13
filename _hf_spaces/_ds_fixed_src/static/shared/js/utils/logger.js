/**
 * Logger Utility
 * Controls console output based on environment and log level
 */

class Logger {
  constructor() {
    this.enabled = true;
    this.level = this.getLogLevel();
    this.prefix = '';
  }

  /**
   * Get log level from localStorage or default to 'info' (balanced visibility)
   * @returns {string} Log level: 'debug', 'info', 'warn', 'error', 'silent'
   */
  getLogLevel() {
    if (typeof localStorage === 'undefined') return 'info';
    // Default to 'info' for better debugging, but allow override
    // Users can set to 'warn' or 'error' to reduce noise if needed
    return localStorage.getItem('logLevel') || 'info';
  }

  /**
   * Set log level
   * @param {string} level - Log level
   */
  setLevel(level) {
    this.level = level;
    if (typeof localStorage !== 'undefined') {
      localStorage.setItem('logLevel', level);
    }
  }

  /**
   * Check if level should be logged
   * @param {string} level - Log level to check
   * @returns {boolean}
   */
  shouldLog(level) {
    if (!this.enabled) return false;
    if (this.level === 'silent') return false;
    
    const levels = ['debug', 'info', 'warn', 'error'];
    const currentIndex = levels.indexOf(this.level);
    const checkIndex = levels.indexOf(level);
    
    return checkIndex >= currentIndex;
  }

  /**
   * Format log message
   * @param {string} prefix - Component prefix
   * @param {string} message - Log message
   * @returns {string}
   */
  formatMessage(prefix, message) {
    return prefix ? `[${prefix}] ${message}` : message;
  }

  /**
   * Debug log
   * @param {string} prefix - Component prefix
   * @param {...any} args - Log arguments
   */
  debug(prefix, ...args) {
    if (!this.shouldLog('debug')) return;
    const message = this.formatMessage(prefix, args[0]);
    console.debug(message, ...args.slice(1));
  }

  /**
   * Info log
   * @param {string} prefix - Component prefix
   * @param {...any} args - Log arguments
   */
  info(prefix, ...args) {
    if (!this.shouldLog('info')) return;
    const message = this.formatMessage(prefix, args[0]);
    console.log(message, ...args.slice(1));
  }

  /**
   * Warn log
   * @param {string} prefix - Component prefix
   * @param {...any} args - Log arguments
   */
  warn(prefix, ...args) {
    if (!this.shouldLog('warn')) return;
    const message = this.formatMessage(prefix, args[0]);
    console.warn(message, ...args.slice(1));
  }

  /**
   * Error log (always shown unless silent)
   * @param {string} prefix - Component prefix
   * @param {...any} args - Log arguments
   */
  error(prefix, ...args) {
    if (!this.shouldLog('error')) return;
    const message = this.formatMessage(prefix, args[0]);
    console.error(message, ...args.slice(1));
  }

  /**
   * Disable all logging
   */
  disable() {
    this.enabled = false;
  }

  /**
   * Enable logging
   */
  enable() {
    this.enabled = true;
  }
}

// Create singleton instance
const logger = new Logger();

// Expose to window for debugging
if (typeof window !== 'undefined') {
  window.logger = logger;
  window.setLogLevel = (level) => logger.setLevel(level);
}

export default logger;

