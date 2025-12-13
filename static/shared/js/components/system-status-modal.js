/**
 * System Status Modal - Comprehensive system status monitoring
 * Modal-based (closed by default), opens on user interaction
 * Shows real-time data: services, endpoints, coins, system resources
 * Safe polling that pauses when modal is closed
 * Data-driven animations only
 */

class SystemStatusModal {
  constructor(options = {}) {
    this.options = {
      apiEndpoint: options.apiEndpoint || '/api/system/status',
      updateInterval: options.updateInterval || 3000, // 3 seconds
      onUpdate: options.onUpdate || null,
      onError: options.onError || null,
      ...options
    };
    
    this.isOpen = false;
    this.pollTimer = null;
    this.lastData = null;
    this.errorCount = 0;
    this.maxErrors = 3;
    this.modalElement = null;
    
    this.createModal();
  }
  
  /**
   * Create modal structure in DOM
   */
  createModal() {
    // Check if modal already exists
    if (document.getElementById('system-status-modal')) {
      this.modalElement = document.getElementById('system-status-modal');
      return;
    }
    
    // Create modal
    const modal = document.createElement('div');
    modal.id = 'system-status-modal';
    modal.className = 'system-status-modal-overlay';
    modal.style.display = 'none';
    modal.innerHTML = `
      <div class="system-status-modal">
        <div class="system-status-modal-header">
          <div class="modal-title-group">
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <path d="M12 6v6l4 2"/>
            </svg>
            <h2>System Status</h2>
          </div>
          <button class="modal-close" onclick="window.systemStatusModal.close()" aria-label="Close modal">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>
        
        <div class="system-status-modal-body">
          <!-- Overall Health -->
          <div class="status-section">
            <div class="section-header">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
              </svg>
              <h3>Overall Health</h3>
            </div>
            <div class="overall-health" id="overall-health">
              <div class="health-status">
                <span class="status-indicator status-loading"></span>
                <span class="status-text">Loading...</span>
              </div>
              <div class="health-timestamp" id="health-timestamp">--</div>
            </div>
          </div>
          
          <!-- Services Status -->
          <div class="status-section">
            <div class="section-header">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="2" y="3" width="20" height="14" rx="2"/>
                <line x1="8" y1="21" x2="16" y2="21"/>
                <line x1="12" y1="17" x2="12" y2="21"/>
              </svg>
              <h3>Services Status</h3>
            </div>
            <div class="services-grid" id="services-grid">
              <div class="loading-placeholder">Loading services...</div>
            </div>
          </div>
          
          <!-- Endpoints Health -->
          <div class="status-section">
            <div class="section-header">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <circle cx="12" cy="12" r="10"/>
                <polyline points="12 6 12 12 16 14"/>
              </svg>
              <h3>API Endpoints</h3>
            </div>
            <div class="endpoints-list" id="endpoints-list">
              <div class="loading-placeholder">Loading endpoints...</div>
            </div>
          </div>
          
          <!-- Coins & Market Feeds -->
          <div class="status-section">
            <div class="section-header">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <line x1="12" y1="1" x2="12" y2="23"/>
                <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
              </svg>
              <h3>Coin Feeds</h3>
            </div>
            <div class="coins-grid" id="coins-grid">
              <div class="loading-placeholder">Loading coin feeds...</div>
            </div>
          </div>
          
          <!-- System Resources -->
          <div class="status-section">
            <div class="section-header">
              <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="4" y="4" width="16" height="16" rx="2"/>
                <rect x="9" y="9" width="6" height="6"/>
                <line x1="9" y1="1" x2="9" y2="4"/>
                <line x1="15" y1="1" x2="15" y2="4"/>
                <line x1="9" y1="20" x2="9" y2="23"/>
                <line x1="15" y1="20" x2="15" y2="23"/>
                <line x1="20" y1="9" x2="23" y2="9"/>
                <line x1="20" y1="14" x2="23" y2="14"/>
                <line x1="1" y1="9" x2="4" y2="9"/>
                <line x1="1" y1="14" x2="4" y2="14"/>
              </svg>
              <h3>System Resources</h3>
            </div>
            <div class="resources-grid" id="resources-grid">
              <div class="loading-placeholder">Loading resources...</div>
            </div>
          </div>
        </div>
      </div>
    `;
    
    document.body.appendChild(modal);
    this.modalElement = modal;
    
    // Close on overlay click
    modal.addEventListener('click', (e) => {
      if (e.target === modal) {
        this.close();
      }
    });
    
    // Close on ESC key
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape' && this.isOpen) {
        this.close();
      }
    });
  }
  
  /**
   * Open modal and start polling
   */
  open() {
    if (this.isOpen) return;
    
    this.isOpen = true;
    this.errorCount = 0;
    
    if (this.modalElement) {
      this.modalElement.style.display = 'flex';
      // Add animation class
      setTimeout(() => {
        this.modalElement.classList.add('modal-visible');
      }, 10);
    }
    
    // Start polling
    this.startPolling();
  }
  
  /**
   * Close modal and stop polling
   */
  close() {
    if (!this.isOpen) return;
    
    this.isOpen = false;
    
    if (this.modalElement) {
      this.modalElement.classList.remove('modal-visible');
      setTimeout(() => {
        this.modalElement.style.display = 'none';
      }, 300);
    }
    
    // Stop polling
    this.stopPolling();
  }
  
  /**
   * Start polling (only when modal is open)
   */
  startPolling() {
    if (!this.isOpen) return;
    
    // Immediate fetch
    this.fetchStatus();
    
    // Schedule next poll
    this.pollTimer = setTimeout(() => {
      this.startPolling();
    }, this.options.updateInterval);
  }
  
  /**
   * Stop polling
   */
  stopPolling() {
    if (this.pollTimer) {
      clearTimeout(this.pollTimer);
      this.pollTimer = null;
    }
  }
  
  /**
   * Fetch system status from API
   */
  async fetchStatus() {
    if (!this.isOpen) return;
    
    try {
      const response = await fetch(this.options.apiEndpoint);
      
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }
      
      const data = await response.json();
      
      // Reset error count on success
      this.errorCount = 0;
      
      // Update UI
      this.updateUI(data);
      
      // Call user callback
      if (this.options.onUpdate) {
        this.options.onUpdate(data);
      }
      
    } catch (error) {
      this.errorCount++;
      console.error('System Status Modal: Failed to fetch status:', error);
      
      // Show error in UI
      this.showError(error);
      
      // Call error callback
      if (this.options.onError) {
        this.options.onError(error);
      }
      
      // If too many errors, show degraded state
      if (this.errorCount >= this.maxErrors) {
        console.error('System Status Modal: Too many errors');
        this.showDegradedState();
      }
    }
  }
  
  /**
   * Update UI with new data
   */
  updateUI(data) {
    const oldData = this.lastData;
    this.lastData = data;
    
    // Update overall health
    this.updateOverallHealth(data.overall_health, data.timestamp);
    
    // Update services
    this.updateServices(data.services, oldData?.services);
    
    // Update endpoints
    this.updateEndpoints(data.endpoints, oldData?.endpoints);
    
    // Update coins
    this.updateCoins(data.coins, oldData?.coins);
    
    // Update resources
    this.updateResources(data.resources, oldData?.resources);
  }
  
  /**
   * Update overall health status
   */
  updateOverallHealth(health, timestamp) {
    const container = document.getElementById('overall-health');
    if (!container) return;
    
    const statusMap = {
      'online': { class: 'status-online', text: 'All Systems Operational', color: '#10b981' },
      'degraded': { class: 'status-degraded', text: 'Degraded Performance', color: '#f59e0b' },
      'partial': { class: 'status-partial', text: 'Partial Outage', color: '#ef4444' },
      'offline': { class: 'status-offline', text: 'System Offline', color: '#ef4444' }
    };
    
    const status = statusMap[health] || statusMap['offline'];
    
    container.innerHTML = `
      <div class="health-status">
        <span class="status-indicator ${status.class}" data-status="${health}"></span>
        <span class="status-text" style="color: ${status.color};">${status.text}</span>
      </div>
      <div class="health-timestamp">${this.formatTimestamp(timestamp)}</div>
    `;
    
    // Animate status change
    const indicator = container.querySelector('.status-indicator');
    if (indicator) {
      indicator.classList.add('status-pulse');
      setTimeout(() => indicator.classList.remove('status-pulse'), 300);
    }
  }
  
  /**
   * Update services grid
   */
  updateServices(services, oldServices) {
    const container = document.getElementById('services-grid');
    if (!container) return;
    
    container.innerHTML = services.map(service => {
      const statusClass = service.status === 'online' ? 'service-online' : 
                         service.status === 'degraded' ? 'service-degraded' : 'service-offline';
      
      const responseTime = service.response_time_ms ? 
        `<span class="service-response">${service.response_time_ms.toFixed(0)}ms</span>` : '';
      
      return `
        <div class="service-card ${statusClass}" data-service="${service.name}">
          <div class="service-header">
            <span class="service-name">${service.name}</span>
            <span class="service-status-dot"></span>
          </div>
          <div class="service-meta">
            <span class="service-status-text">${service.status}</span>
            ${responseTime}
          </div>
        </div>
      `;
    }).join('');
    
    // Animate changes
    if (oldServices) {
      this.animateChanges(container, oldServices, services, 'name');
    }
  }
  
  /**
   * Update endpoints list
   */
  updateEndpoints(endpoints, oldEndpoints) {
    const container = document.getElementById('endpoints-list');
    if (!container) return;
    
    container.innerHTML = endpoints.map(endpoint => {
      const statusClass = endpoint.status === 'online' ? 'endpoint-online' : 'endpoint-degraded';
      
      return `
        <div class="endpoint-item ${statusClass}" data-endpoint="${endpoint.path}">
          <div class="endpoint-header">
            <span class="endpoint-path">${endpoint.path}</span>
            <span class="endpoint-status-dot"></span>
          </div>
          <div class="endpoint-metrics">
            <span class="metric-item">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
              </svg>
              ${endpoint.avg_response_ms?.toFixed(0) || '--'}ms
            </span>
            <span class="metric-item">
              <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"/>
                <polyline points="22 4 12 14.01 9 11.01"/>
              </svg>
              ${endpoint.success_rate?.toFixed(1) || '--'}%
            </span>
          </div>
        </div>
      `;
    }).join('');
    
    // Animate changes
    if (oldEndpoints) {
      this.animateChanges(container, oldEndpoints, endpoints, 'path');
    }
  }
  
  /**
   * Update coins grid
   */
  updateCoins(coins, oldCoins) {
    const container = document.getElementById('coins-grid');
    if (!container) return;
    
    container.innerHTML = coins.map(coin => {
      const statusClass = coin.status === 'online' ? 'coin-online' : 'coin-offline';
      const price = coin.price ? `$${coin.price.toLocaleString('en-US', {maximumFractionDigits: 2})}` : '--';
      
      return `
        <div class="coin-card ${statusClass}" data-coin="${coin.symbol}">
          <div class="coin-header">
            <span class="coin-symbol">${coin.symbol}</span>
            <span class="coin-status-dot"></span>
          </div>
          <div class="coin-price">${price}</div>
          <div class="coin-updated">${this.formatRelativeTime(coin.last_update)}</div>
        </div>
      `;
    }).join('');
    
    // Animate price changes
    if (oldCoins) {
      this.animateCoinPriceChanges(container, oldCoins, coins);
    }
  }
  
  /**
   * Update resources grid
   */
  updateResources(resources, oldResources) {
    const container = document.getElementById('resources-grid');
    if (!container) return;
    
    container.innerHTML = `
      <div class="resource-card">
        <div class="resource-label">CPU</div>
        <div class="resource-value" data-metric="cpu">${resources.cpu_percent.toFixed(1)}%</div>
        <div class="resource-bar">
          <div class="resource-bar-fill" style="width: ${resources.cpu_percent}%; background: ${this.getResourceColor(resources.cpu_percent)}"></div>
        </div>
      </div>
      
      <div class="resource-card">
        <div class="resource-label">Memory</div>
        <div class="resource-value" data-metric="memory">${resources.memory_percent.toFixed(1)}%</div>
        <div class="resource-bar">
          <div class="resource-bar-fill" style="width: ${resources.memory_percent}%; background: ${this.getResourceColor(resources.memory_percent)}"></div>
        </div>
        <div class="resource-detail">${resources.memory_used_mb.toFixed(0)} / ${resources.memory_total_mb.toFixed(0)} MB</div>
      </div>
      
      <div class="resource-card">
        <div class="resource-label">Uptime</div>
        <div class="resource-value">${this.formatUptime(resources.uptime_seconds)}</div>
      </div>
      
      ${resources.load_avg ? `
        <div class="resource-card">
          <div class="resource-label">Load Average</div>
          <div class="resource-value">${resources.load_avg.map(v => v.toFixed(2)).join(', ')}</div>
        </div>
      ` : ''}
    `;
    
    // Animate value changes (data-driven)
    if (oldResources) {
      this.animateResourceChanges(container, oldResources, resources);
    }
  }
  
  /**
   * Animate changes (data-driven only)
   */
  animateChanges(container, oldData, newData, keyField) {
    // Find changed items
    const oldMap = new Map(oldData.map(item => [item[keyField], item]));
    
    newData.forEach(newItem => {
      const oldItem = oldMap.get(newItem[keyField]);
      if (oldItem && oldItem.status !== newItem.status) {
        // Status changed - animate
        const element = container.querySelector(`[data-${keyField.toLowerCase()}="${newItem[keyField]}"]`);
        if (element) {
          element.classList.add('status-changed');
          setTimeout(() => element.classList.remove('status-changed'), 300);
        }
      }
    });
  }
  
  /**
   * Animate coin price changes (data-driven)
   */
  animateCoinPriceChanges(container, oldCoins, newCoins) {
    const oldMap = new Map(oldCoins.map(c => [c.symbol, c]));
    
    newCoins.forEach(newCoin => {
      const oldCoin = oldMap.get(newCoin.symbol);
      if (oldCoin && oldCoin.price && newCoin.price && oldCoin.price !== newCoin.price) {
        const element = container.querySelector(`[data-coin="${newCoin.symbol}"] .coin-price`);
        if (element) {
          element.classList.add(newCoin.price > oldCoin.price ? 'price-up' : 'price-down');
          setTimeout(() => {
            element.classList.remove('price-up', 'price-down');
          }, 300);
        }
      }
    });
  }
  
  /**
   * Animate resource changes (data-driven)
   */
  animateResourceChanges(container, oldResources, newResources) {
    // CPU
    if (oldResources.cpu_percent !== newResources.cpu_percent) {
      const cpuValue = container.querySelector('[data-metric="cpu"]');
      if (cpuValue) {
        cpuValue.classList.add('value-changed');
        setTimeout(() => cpuValue.classList.remove('value-changed'), 300);
      }
    }
    
    // Memory
    if (oldResources.memory_percent !== newResources.memory_percent) {
      const memValue = container.querySelector('[data-metric="memory"]');
      if (memValue) {
        memValue.classList.add('value-changed');
        setTimeout(() => memValue.classList.remove('value-changed'), 300);
      }
    }
  }
  
  /**
   * Show error state
   */
  showError(error) {
    const overallHealth = document.getElementById('overall-health');
    if (overallHealth) {
      overallHealth.innerHTML = `
        <div class="health-status">
          <span class="status-indicator status-error"></span>
          <span class="status-text" style="color: #ef4444;">Failed to fetch status</span>
        </div>
        <div class="health-timestamp">${error.message}</div>
      `;
    }
  }
  
  /**
   * Show degraded state after multiple errors
   */
  showDegradedState() {
    // Show last known data with warning
    const overallHealth = document.getElementById('overall-health');
    if (overallHealth && this.lastData) {
      overallHealth.innerHTML = `
        <div class="health-status">
          <span class="status-indicator status-degraded"></span>
          <span class="status-text" style="color: #f59e0b;">Showing last known data</span>
        </div>
        <div class="health-timestamp">Data may be stale</div>
      `;
    }
  }
  
  /**
   * Get color for resource usage
   */
  getResourceColor(percent) {
    if (percent < 50) return '#10b981';
    if (percent < 75) return '#22d3ee';
    if (percent < 90) return '#f59e0b';
    return '#ef4444';
  }
  
  /**
   * Format timestamp
   */
  formatTimestamp(timestamp) {
    const date = new Date(timestamp * 1000);
    return date.toLocaleTimeString();
  }
  
  /**
   * Format relative time
   */
  formatRelativeTime(isoString) {
    if (!isoString) return 'Never';
    const diff = Date.now() - new Date(isoString).getTime();
    const seconds = Math.floor(diff / 1000);
    
    if (seconds < 60) return 'Just now';
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m ago`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ago`;
    return `${Math.floor(seconds / 86400)}d ago`;
  }
  
  /**
   * Format uptime
   */
  formatUptime(seconds) {
    if (seconds < 60) return `${seconds}s`;
    if (seconds < 3600) return `${Math.floor(seconds / 60)}m`;
    if (seconds < 86400) return `${Math.floor(seconds / 3600)}h ${Math.floor((seconds % 3600) / 60)}m`;
    return `${Math.floor(seconds / 86400)}d ${Math.floor((seconds % 86400) / 3600)}h`;
  }
  
  /**
   * Destroy modal
   */
  destroy() {
    this.stopPolling();
    if (this.modalElement) {
      this.modalElement.remove();
      this.modalElement = null;
    }
  }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
  module.exports = SystemStatusModal;
}

// Make available globally
if (typeof window !== 'undefined') {
  window.SystemStatusModal = SystemStatusModal;
}
