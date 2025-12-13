/**
 * System Monitor Component - Real-time system metrics monitoring
 * Displays CPU, memory, uptime, request rate, response time, and error rate
 * Uses lightweight polling (safe for HF Space)
 * All metrics are REAL and measured, no fake data
 */

class SystemMonitor {
  constructor(containerId, options = {}) {
    this.containerId = containerId;
    this.container = null;
    this.options = {
      updateInterval: options.updateInterval || 2000, // 2 seconds default
      maxUpdateInterval: options.maxUpdateInterval || 5000, // Max 5 seconds
      minUpdateInterval: options.minUpdateInterval || 1000, // Min 1 second
      apiEndpoint: options.apiEndpoint || '/api/system/metrics',
      autoStart: options.autoStart !== false,
      onUpdate: options.onUpdate || null,
      onError: options.onError || null,
      ...options
    };
    
    this.isRunning = false;
    this.pollTimer = null;
    this.lastMetrics = null;
    this.errorCount = 0;
    this.maxErrors = 3;
    
    if (this.options.autoStart) {
      this.init();
    }
  }
  
  /**
   * Initialize the system monitor
   */
  init() {
    this.container = document.getElementById(this.containerId);
    if (!this.container) {
      console.error(`System Monitor: Container #${this.containerId} not found`);
      return;
    }
    
    this.render();
    this.start();
  }
  
  /**
   * Render the monitor UI
   */
  render() {
    this.container.innerHTML = `
      <div class="system-monitor">
        <div class="system-monitor-header">
          <div class="system-monitor-title">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="2" y="3" width="20" height="14" rx="2" ry="2"></rect>
              <line x1="8" y1="21" x2="16" y2="21"></line>
              <line x1="12" y1="17" x2="12" y2="21"></line>
            </svg>
            <span>System Monitor</span>
          </div>
          <div class="system-monitor-status">
            <span class="status-dot status-dot-loading"></span>
            <span class="status-text">Loading...</span>
          </div>
        </div>
        
        <div class="system-monitor-grid">
          <!-- CPU -->
          <div class="metric-card">
            <div class="metric-header">
              <span class="metric-label">CPU Usage</span>
              <span class="metric-value" data-metric="cpu">--%</span>
            </div>
            <div class="metric-bar">
              <div class="metric-bar-fill" data-metric-bar="cpu" style="width: 0%"></div>
            </div>
          </div>
          
          <!-- Memory -->
          <div class="metric-card">
            <div class="metric-header">
              <span class="metric-label">Memory</span>
              <span class="metric-value" data-metric="memory">-- MB / -- MB</span>
            </div>
            <div class="metric-bar">
              <div class="metric-bar-fill" data-metric-bar="memory" style="width: 0%"></div>
            </div>
          </div>
          
          <!-- Uptime -->
          <div class="metric-card">
            <div class="metric-header">
              <span class="metric-label">Uptime</span>
              <span class="metric-value" data-metric="uptime">--</span>
            </div>
            <div class="metric-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"></circle>
                <polyline points="12 6 12 12 16 14"></polyline>
              </svg>
            </div>
          </div>
          
          <!-- Request Rate -->
          <div class="metric-card">
            <div class="metric-header">
              <span class="metric-label">Requests/min</span>
              <span class="metric-value" data-metric="requests">--</span>
            </div>
            <div class="metric-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="12" y1="1" x2="12" y2="23"></line>
                <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"></path>
              </svg>
            </div>
          </div>
          
          <!-- Response Time -->
          <div class="metric-card">
            <div class="metric-header">
              <span class="metric-label">Avg Response</span>
              <span class="metric-value" data-metric="response">-- ms</span>
            </div>
            <div class="metric-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
              </svg>
            </div>
          </div>
          
          <!-- Error Rate -->
          <div class="metric-card">
            <div class="metric-header">
              <span class="metric-label">Error Rate</span>
              <span class="metric-value" data-metric="errors">--%</span>
            </div>
            <div class="metric-icon">
              <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"></circle>
                <line x1="12" y1="8" x2="12" y2="12"></line>
                <line x1="12" y1="16" x2="12.01" y2="16"></line>
              </svg>
            </div>
          </div>
        </div>
      </div>
    `;
  }
  
  /**
   * Start polling for metrics
   */
  start() {
    if (this.isRunning) return;
    
    this.isRunning = true;
    this.errorCount = 0;
    this.updateStatus('active', 'Live');
    this.poll();
  }
  
  /**
   * Stop polling
   */
  stop() {
    this.isRunning = false;
    if (this.pollTimer) {
      clearTimeout(this.pollTimer);
      this.pollTimer = null;
    }
    this.updateStatus('inactive', 'Stopped');
  }
  
  /**
   * Poll for metrics
   */
  async poll() {
    if (!this.isRunning) return;
    
    try {
      const response = await fetch(this.options.apiEndpoint);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      const metrics = await response.json();
      
      // Reset error count on success
      this.errorCount = 0;
      
      // Update UI with new metrics
      this.updateMetrics(metrics);
      
      // Call user callback if provided
      if (this.options.onUpdate) {
        this.options.onUpdate(metrics);
      }
      
      // Update status
      this.updateStatus('active', 'Live');
      
      // Adaptive polling: slow down if CPU is high
      let nextInterval = this.options.updateInterval;
      if (metrics.cpu > 80) {
        nextInterval = Math.min(this.options.maxUpdateInterval, nextInterval * 1.5);
      } else if (metrics.cpu < 30) {
        nextInterval = Math.max(this.options.minUpdateInterval, nextInterval * 0.8);
      }
      
      // Schedule next poll
      this.pollTimer = setTimeout(() => this.poll(), nextInterval);
      
    } catch (error) {
      this.errorCount++;
      console.error('System Monitor: Failed to fetch metrics:', error);
      
      // Update status to show error
      this.updateStatus('error', 'Error');
      
      // Call error callback if provided
      if (this.options.onError) {
        this.options.onError(error);
      }
      
      // If too many errors, stop polling
      if (this.errorCount >= this.maxErrors) {
        console.error('System Monitor: Too many errors, stopping...');
        this.stop();
        this.updateStatus('inactive', 'Failed');
        return;
      }
      
      // Retry with exponential backoff
      const retryInterval = this.options.updateInterval * Math.pow(2, this.errorCount);
      this.pollTimer = setTimeout(() => this.poll(), retryInterval);
    }
  }
  
  /**
   * Update metrics display
   */
  updateMetrics(metrics) {
    // Store last metrics for animation detection
    const oldMetrics = this.lastMetrics;
    this.lastMetrics = metrics;
    
    // CPU
    this.updateMetric('cpu', `${metrics.cpu.toFixed(1)}%`, metrics.cpu, oldMetrics?.cpu);
    this.updateBar('cpu', metrics.cpu);
    
    // Memory
    const memoryPercent = (metrics.memory.used / metrics.memory.total) * 100;
    this.updateMetric('memory', 
      `${metrics.memory.used.toFixed(0)} MB / ${metrics.memory.total.toFixed(0)} MB`,
      memoryPercent,
      oldMetrics ? (oldMetrics.memory.used / oldMetrics.memory.total) * 100 : null
    );
    this.updateBar('memory', memoryPercent);
    
    // Uptime
    this.updateMetric('uptime', this.formatUptime(metrics.uptime), null, null);
    
    // Requests per minute
    this.updateMetric('requests', metrics.requests_per_min.toString(), 
      metrics.requests_per_min, oldMetrics?.requests_per_min);
    
    // Response time
    this.updateMetric('response', `${metrics.avg_response_ms.toFixed(0)} ms`,
      metrics.avg_response_ms, oldMetrics?.avg_response_ms);
    
    // Error rate
    this.updateMetric('errors', `${metrics.error_rate.toFixed(1)}%`,
      metrics.error_rate, oldMetrics?.error_rate);
  }
  
  /**
   * Update a single metric with optional animation
   */
  updateMetric(name, value, newVal, oldVal) {
    const element = this.container.querySelector(`[data-metric="${name}"]`);
    if (!element) return;
    
    element.textContent = value;
    
    // Animate on change (data-driven animation)
    if (oldVal !== null && newVal !== null && oldVal !== newVal) {
      element.classList.remove('metric-changed', 'metric-increased', 'metric-decreased');
      
      // Force reflow
      void element.offsetWidth;
      
      element.classList.add('metric-changed');
      if (newVal > oldVal) {
        element.classList.add('metric-increased');
      } else if (newVal < oldVal) {
        element.classList.add('metric-decreased');
      }
      
      // Remove animation class after animation completes
      setTimeout(() => {
        element.classList.remove('metric-changed', 'metric-increased', 'metric-decreased');
      }, 300);
    }
  }
  
  /**
   * Update a progress bar
   */
  updateBar(name, percent) {
    const bar = this.container.querySelector(`[data-metric-bar="${name}"]`);
    if (!bar) return;
    
    // Clamp between 0 and 100
    percent = Math.max(0, Math.min(100, percent));
    
    // Smooth transition
    bar.style.width = `${percent}%`;
    
    // Color based on value
    bar.classList.remove('bar-low', 'bar-medium', 'bar-high', 'bar-critical');
    if (percent < 50) {
      bar.classList.add('bar-low');
    } else if (percent < 75) {
      bar.classList.add('bar-medium');
    } else if (percent < 90) {
      bar.classList.add('bar-high');
    } else {
      bar.classList.add('bar-critical');
    }
  }
  
  /**
   * Update status indicator
   */
  updateStatus(status, text) {
    const dot = this.container.querySelector('.status-dot');
    const statusText = this.container.querySelector('.status-text');
    
    if (dot) {
      dot.className = 'status-dot';
      dot.classList.add(`status-dot-${status}`);
    }
    
    if (statusText) {
      statusText.textContent = text;
    }
  }
  
  /**
   * Format uptime in human-readable format
   */
  formatUptime(seconds) {
    if (seconds < 60) {
      return `${seconds}s`;
    } else if (seconds < 3600) {
      const minutes = Math.floor(seconds / 60);
      return `${minutes}m`;
    } else if (seconds < 86400) {
      const hours = Math.floor(seconds / 3600);
      const minutes = Math.floor((seconds % 3600) / 60);
      return `${hours}h ${minutes}m`;
    } else {
      const days = Math.floor(seconds / 86400);
      const hours = Math.floor((seconds % 86400) / 3600);
      return `${days}d ${hours}h`;
    }
  }
  
  /**
   * Destroy the monitor
   */
  destroy() {
    this.stop();
    if (this.container) {
      this.container.innerHTML = '';
    }
  }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = SystemMonitor;
}

// Also make available globally
if (typeof window !== 'undefined') {
  window.SystemMonitor = SystemMonitor;
}
