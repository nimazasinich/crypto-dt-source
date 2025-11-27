/**
 * Polling Manager
 * Replaces WebSocket with intelligent HTTP polling
 * 
 * Features:
 * - Multiple concurrent polls with different intervals
 * - Auto-pause when page is hidden (Page Visibility API)
 * - Manual start/stop control
 * - Last update timestamp tracking
 * - Error handling and retry
 */

export class PollingManager {
  constructor() {
    this.polls = new Map();
    this.lastUpdates = new Map();
    this.isVisible = !document.hidden;
    this.updateCallbacks = new Map();
    
    // Listen to page visibility changes
    document.addEventListener('visibilitychange', () => {
      this.isVisible = !document.hidden;
      console.log(`[PollingManager] Page visibility changed: ${this.isVisible ? 'visible' : 'hidden'}`);
      
      if (this.isVisible) {
        this.resumeAll();
      } else {
        this.pauseAll();
      }
    });

    // Cleanup on page unload
    window.addEventListener('beforeunload', () => {
      this.stopAll();
    });

    console.log('[PollingManager] Initialized');
  }

  /**
   * Start polling an endpoint
   * @param {string} key - Unique identifier for this poll
   * @param {Function} fetchFunction - Async function that fetches data
   * @param {Function} callback - Function to call with fetched data
   * @param {number} interval - Polling interval in milliseconds
   */
  start(key, fetchFunction, callback, interval) {
    // Stop existing poll if any
    this.stop(key);

    const poll = {
      fetchFunction,
      callback,
      interval,
      timerId: null,
      isPaused: false,
      errorCount: 0,
      consecutiveErrors: 0,
      maxConsecutiveErrors: 5,
    };

    // Initial fetch (don't wait for interval)
    this._executePoll(key, poll);

    // Setup recurring interval
    poll.timerId = setInterval(() => {
      if (!poll.isPaused && this.isVisible) {
        this._executePoll(key, poll);
      }
    }, interval);

    this.polls.set(key, poll);
    console.log(`[PollingManager] Started polling: ${key} every ${interval}ms`);
  }

  /**
   * Execute a single poll
   */
  async _executePoll(key, poll) {
    try {
      console.log(`[PollingManager] Fetching: ${key}`);
      const data = await poll.fetchFunction();
      
      // Reset error count on success
      poll.consecutiveErrors = 0;
      
      // Update timestamp
      this.lastUpdates.set(key, Date.now());
      
      // Call success callback
      poll.callback(data, null);
      
      // Notify update callbacks
      this._notifyUpdateCallbacks(key);

    } catch (error) {
      poll.consecutiveErrors++;
      poll.errorCount++;
      
      console.error(`[PollingManager] Error in ${key} (${poll.consecutiveErrors}/${poll.maxConsecutiveErrors}):`, error);
      
      // Call error callback
      poll.callback(null, error);
      
      // Stop polling after too many consecutive errors
      if (poll.consecutiveErrors >= poll.maxConsecutiveErrors) {
        console.error(`[PollingManager] Too many consecutive errors, stopping ${key}`);
        this.stop(key);
      }
    }
  }

  /**
   * Stop polling for a specific key
   */
  stop(key) {
    const poll = this.polls.get(key);
    if (poll && poll.timerId) {
      clearInterval(poll.timerId);
      this.polls.delete(key);
      this.lastUpdates.delete(key);
      console.log(`[PollingManager] Stopped polling: ${key}`);
    }
  }

  /**
   * Pause a specific poll (keeps in memory, stops fetching)
   */
  pause(key) {
    const poll = this.polls.get(key);
    if (poll) {
      poll.isPaused = true;
      console.log(`[PollingManager] Paused: ${key}`);
    }
  }

  /**
   * Resume a specific poll
   */
  resume(key) {
    const poll = this.polls.get(key);
    if (poll) {
      poll.isPaused = false;
      // Immediate fetch on resume
      this._executePoll(key, poll);
      console.log(`[PollingManager] Resumed: ${key}`);
    }
  }

  /**
   * Pause all active polls (e.g., when page is hidden)
   */
  pauseAll() {
    console.log('[PollingManager] Pausing all polls');
    for (const [key, poll] of this.polls) {
      poll.isPaused = true;
    }
  }

  /**
   * Resume all paused polls (e.g., when page becomes visible)
   */
  resumeAll() {
    console.log('[PollingManager] Resuming all polls');
    for (const [key, poll] of this.polls) {
      if (poll.isPaused) {
        poll.isPaused = false;
        // Immediate fetch on resume
        this._executePoll(key, poll);
      }
    }
  }

  /**
   * Stop all polls and clear
   */
  stopAll() {
    console.log('[PollingManager] Stopping all polls');
    for (const key of this.polls.keys()) {
      this.stop(key);
    }
  }

  /**
   * Get last update timestamp for a poll
   */
  getLastUpdate(key) {
    return this.lastUpdates.get(key) || null;
  }

  /**
   * Get formatted "last updated" string
   */
  getLastUpdateText(key) {
    const timestamp = this.getLastUpdate(key);
    if (!timestamp) return 'Never';
    
    const seconds = Math.floor((Date.now() - timestamp) / 1000);
    
    if (seconds < 5) return 'Just now';
    if (seconds < 60) return `${seconds}s ago`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    return `${Math.floor(seconds / 86400)}d ago`;
  }

  /**
   * Check if a poll is active
   */
  isActive(key) {
    return this.polls.has(key);
  }

  /**
   * Check if a poll is paused
   */
  isPaused(key) {
    const poll = this.polls.get(key);
    return poll ? poll.isPaused : false;
  }

  /**
   * Get all active poll keys
   */
  getActivePolls() {
    return Array.from(this.polls.keys());
  }

  /**
   * Get poll info
   */
  getPollInfo(key) {
    const poll = this.polls.get(key);
    if (!poll) return null;

    return {
      key,
      interval: poll.interval,
      isPaused: poll.isPaused,
      errorCount: poll.errorCount,
      consecutiveErrors: poll.consecutiveErrors,
      lastUpdate: this.getLastUpdateText(key),
      isActive: true,
    };
  }

  /**
   * Register callback for last update changes
   * Returns unsubscribe function
   */
  onLastUpdate(callback) {
    const id = Date.now() + Math.random();
    this.updateCallbacks.set(id, callback);
    
    // Return unsubscribe function
    return () => this.updateCallbacks.delete(id);
  }

  /**
   * Notify all update callbacks
   */
  _notifyUpdateCallbacks(key) {
    const text = this.getLastUpdateText(key);
    for (const callback of this.updateCallbacks.values()) {
      try {
        callback(key, text);
      } catch (error) {
        console.error('[PollingManager] Error in update callback:', error);
      }
    }
  }

  /**
   * Update all UI elements showing "last updated"
   * Call this in an interval (e.g., every second)
   */
  updateAllLastUpdateTexts() {
    for (const key of this.polls.keys()) {
      this._notifyUpdateCallbacks(key);
    }
  }
}

// ============================================================================
// EXPORT SINGLETON INSTANCE
// ============================================================================

export const pollingManager = new PollingManager();

// Auto-update "last updated" text every second
setInterval(() => {
  pollingManager.updateAllLastUpdateTexts();
}, 1000);

export default pollingManager;
