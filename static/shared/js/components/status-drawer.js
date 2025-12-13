/**
 * Status Drawer - Slide-out panel from right side
 * Shows ONLY: Resources, Endpoints, Providers status
 * Real-time updates, NO CPU/Memory stats
 */

class StatusDrawer {
  constructor(options = {}) {
    this.options = {
      apiEndpoint: options.apiEndpoint || '/api/system/status',
      updateInterval: options.updateInterval || 3000, // 3 seconds
      ...options
    };
    
    this.isOpen = false;
    this.pollTimer = null;
    this.lastData = null;
    this.drawerElement = null;
    this.buttonElement = null;
    
    this.createDrawer();
    this.createFloatingButton();
  }
  
  /**
   * Create floating button
   */
  createFloatingButton() {
    const button = document.createElement('button');
    button.id = 'status-drawer-btn';
    button.className = 'status-drawer-floating-btn';
    button.setAttribute('aria-label', 'Open status panel');
    button.innerHTML = `
      <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
        <circle cx="12" cy="12" r="10"/>
        <path d="M12 6v6l4 2"/>
      </svg>
    `;
    
    button.addEventListener('click', () => this.toggle());
    
    document.body.appendChild(button);
    this.buttonElement = button;
  }
  
  /**
   * Create drawer panel - ENHANCED with detailed provider metrics
   */
  createDrawer() {
    const drawer = document.createElement('div');
    drawer.id = 'status-drawer';
    drawer.className = 'status-drawer status-drawer-enhanced';
    drawer.innerHTML = `
      <div class="status-drawer-header">
        <h3>System Status</h3>
        <div class="header-actions">
          <button class="refresh-btn" id="refresh-status" aria-label="Refresh">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="23 4 23 10 17 10"></polyline>
              <polyline points="1 20 1 14 7 14"></polyline>
              <path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>
            </svg>
          </button>
          <button class="drawer-close" aria-label="Close">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M9 18l6-6-6-6"/>
            </svg>
          </button>
        </div>
      </div>
      
      <div class="status-drawer-body">
        <!-- ALL PROVIDER STATUS -->
        <div class="status-section providers-detailed">
          <div class="section-title collapsible" data-target="providers-list">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="2" y="3" width="20" height="14" rx="2"/>
              <line x1="8" y1="21" x2="16" y2="21"/>
              <line x1="12" y1="17" x2="12" y2="21"/>
            </svg>
            <span>All Providers</span>
            <svg class="chevron" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="6 9 12 15 18 9"></polyline>
            </svg>
          </div>
          <div class="collapsible-content" id="providers-list">
            <div class="summary-loading">Loading...</div>
          </div>
        </div>
        
        <!-- AI MODELS -->
        <div class="status-section ai-models">
          <div class="section-title collapsible" data-target="ai-models-list">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
            </svg>
            <span>AI Models</span>
            <svg class="chevron" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="6 9 12 15 18 9"></polyline>
            </svg>
          </div>
          <div class="collapsible-content" id="ai-models-list">
            <div class="summary-loading">Loading...</div>
          </div>
        </div>
        
        <!-- INFRASTRUCTURE -->
        <div class="status-section infrastructure">
          <div class="section-title collapsible" data-target="infrastructure-list">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="2" y="2" width="20" height="8" rx="2" ry="2"></rect>
              <rect x="2" y="14" width="20" height="8" rx="2" ry="2"></rect>
              <line x1="6" y1="6" x2="6" y2="6"></line>
              <line x1="6" y1="18" x2="6" y2="18"></line>
            </svg>
            <span>Infrastructure</span>
            <svg class="chevron" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="6 9 12 15 18 9"></polyline>
            </svg>
          </div>
          <div class="collapsible-content" id="infrastructure-list">
            <div class="summary-loading">Loading...</div>
          </div>
        </div>
        
        <!-- RESOURCE BREAKDOWN -->
        <div class="status-section resource-breakdown">
          <div class="section-title collapsible" data-target="resources-breakdown">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="8" y1="6" x2="21" y2="6"></line>
              <line x1="8" y1="12" x2="21" y2="12"></line>
              <line x1="8" y1="18" x2="21" y2="18"></line>
              <line x1="3" y1="6" x2="3" y2="6"></line>
              <line x1="3" y1="12" x2="3" y2="12"></line>
              <line x1="3" y1="18" x2="3" y2="18"></line>
            </svg>
            <span>Resource Breakdown</span>
            <svg class="chevron" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="6 9 12 15 18 9"></polyline>
            </svg>
          </div>
          <div class="collapsible-content" id="resources-breakdown">
            <div class="summary-loading">Loading...</div>
          </div>
        </div>
        
        <!-- ERROR DETAILS -->
        <div class="status-section error-details">
          <div class="section-title collapsible" data-target="error-list">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="12" y1="8" x2="12" y2="12"></line>
              <line x1="12" y1="16" x2="12" y2="16"></line>
            </svg>
            <span>Recent Errors</span>
            <svg class="chevron" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="6 9 12 15 18 9"></polyline>
            </svg>
          </div>
          <div class="collapsible-content collapsed" id="error-list">
            <div class="summary-loading">Loading...</div>
          </div>
        </div>
        
        <!-- PERFORMANCE -->
        <div class="status-section performance">
          <div class="section-title collapsible" data-target="performance-metrics">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
            </svg>
            <span>Performance</span>
            <svg class="chevron" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="6 9 12 15 18 9"></polyline>
            </svg>
          </div>
          <div class="collapsible-content" id="performance-metrics">
            <div class="summary-loading">Loading...</div>
          </div>
        </div>
        
        <!-- Last Update -->
        <div class="drawer-footer">
          <span class="last-update-label">Last update:</span>
          <span class="last-update-time" id="last-update-time">--</span>
        </div>
      </div>
    `;
    
    document.body.appendChild(drawer);
    this.drawerElement = drawer;
    
    // Close button
    drawer.querySelector('.drawer-close').addEventListener('click', () => this.close());
    
    // Refresh button
    drawer.querySelector('#refresh-status').addEventListener('click', () => this.fetchStatus());
    
    // Collapsible sections
    drawer.querySelectorAll('.section-title.collapsible').forEach(title => {
      title.addEventListener('click', (e) => {
        const target = title.dataset.target;
        const content = document.getElementById(target);
        if (content) {
          content.classList.toggle('collapsed');
          title.classList.toggle('collapsed');
        }
      });
    });
  }
  
  /**
   * Toggle drawer
   */
  toggle() {
    if (this.isOpen) {
      this.close();
    } else {
      this.open();
    }
  }
  
  /**
   * Open drawer
   */
  open() {
    if (this.isOpen) return;
    
    this.isOpen = true;
    this.drawerElement.classList.add('open');
    this.buttonElement.classList.add('hidden');
    
    // Start polling
    this.startPolling();
  }
  
  /**
   * Close drawer
   */
  close() {
    if (!this.isOpen) return;
    
    this.isOpen = false;
    this.drawerElement.classList.remove('open');
    this.buttonElement.classList.remove('hidden');
    
    // Stop polling
    this.stopPolling();
  }
  
  /**
   * Start polling (only when open)
   */
  startPolling() {
    if (!this.isOpen) return;
    
    this.fetchStatus();
    this.pollTimer = setTimeout(() => this.startPolling(), this.options.updateInterval);
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
   * Fetch status from API
   */
  async fetchStatus() {
    if (!this.isOpen) return;
    
    try {
      const response = await fetch(this.options.apiEndpoint);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      
      const data = await response.json();
      this.updateUI(data);
      
    } catch (error) {
      console.error('Status Drawer: Failed to fetch:', error);
      this.showError();
    }
  }
  
  /**
   * Update UI with data - ENHANCED
   */
  updateUI(data) {
    this.lastData = data;
    
    // Update all providers with detailed metrics
    this.updateProvidersDetailed(data.providers_detailed || data.services || []);
    
    // Update AI models
    this.updateAIModels(data.ai_models || {});
    
    // Update infrastructure
    this.updateInfrastructure(data.infrastructure || {});
    
    // Update resource breakdown
    this.updateResourceBreakdown(data.resource_breakdown || {});
    
    // Update error details
    this.updateErrorDetails(data.error_details || []);
    
    // Update performance
    this.updatePerformance(data.performance || {});
    
    // Update timestamp
    this.updateTimestamp(data.timestamp);
  }
  
  /**
   * Update providers with detailed metrics
   */
  updateProvidersDetailed(providers) {
    const container = document.getElementById('providers-list');
    if (!container) return;
    
    if (!providers.length) {
      container.innerHTML = '<div class="empty-state">No providers configured</div>';
      return;
    }
    
    container.innerHTML = providers.map(provider => {
      const isOnline = provider.status === 'online' || provider.status === 'active';
      const statusEmoji = isOnline ? '🟢' : 
                         provider.status === 'rate_limited' ? '🔴' : 
                         provider.status === 'degraded' ? '🟡' : '⚫';
      
      let statusText = '';
      if (isOnline) {
        statusText = `${provider.response_time_ms || 0}ms | Success: ${provider.success_rate || 100}%`;
        if (provider.last_check) {
          const elapsed = Math.floor((Date.now() / 1000) - new Date(provider.last_check).getTime() / 1000);
          statusText += ` | Last: ${elapsed}s ago`;
        }
      } else if (provider.status === 'rate_limited') {
        statusText = `Rate Limited (${provider.status_code || 429})`;
        if (provider.cached_until) {
          statusText += ` | Cached ${provider.cached_until}`;
        }
      } else if (provider.status === 'degraded') {
        statusText = provider.error || 'Degraded performance';
      } else {
        statusText = provider.error || 'Offline';
      }
      
      const resourceInfo = provider.resource_count ? ` | ${provider.resource_count} resources` : '';
      
      return `
        <div class="provider-item ${isOnline ? 'online' : 'offline'}">
          <div class="provider-status">
            <span class="status-emoji">${statusEmoji}</span>
            <span class="provider-name">${provider.name}</span>
          </div>
          <div class="provider-metrics">${statusText}${resourceInfo}</div>
        </div>
      `;
    }).join('');
  }
  
  /**
   * Update AI models section
   */
  updateAIModels(aiModels) {
    const container = document.getElementById('ai-models-list');
    if (!container) return;
    
    const transformersStatus = aiModels.transformers_loaded ? '🟢 Loaded (CPU mode)' : '🔴 Not loaded';
    const sentimentModels = aiModels.sentiment_models || 0;
    const hfApiStatus = aiModels.hf_api_active ? '🟢 Active' : '🔴 Inactive';
    
    container.innerHTML = `
      <div class="metric-item">
        <span class="metric-label">Transformers:</span>
        <span class="metric-value">${transformersStatus}</span>
      </div>
      <div class="metric-item">
        <span class="metric-label">Sentiment Models:</span>
        <span class="metric-value">${sentimentModels} available</span>
      </div>
      <div class="metric-item">
        <span class="metric-label">HuggingFace API:</span>
        <span class="metric-value">${hfApiStatus}</span>
      </div>
    `;
  }
  
  /**
   * Update infrastructure section
   */
  updateInfrastructure(infrastructure) {
    const container = document.getElementById('infrastructure-list');
    if (!container) return;
    
    const dbStatus = infrastructure.database_status || 'unknown';
    const dbEntries = infrastructure.database_entries || 0;
    const workerStatus = infrastructure.background_worker || 'unknown';
    const workerNextRun = infrastructure.worker_next_run || 'N/A';
    const wsStatus = infrastructure.websocket_active ? '🟢 Active' : '⚫ Inactive';
    
    container.innerHTML = `
      <div class="metric-item">
        <span class="metric-label">Database:</span>
        <span class="metric-value">${dbStatus === 'online' ? '🟢' : '🔴'} SQLite (${dbEntries} cached)</span>
      </div>
      <div class="metric-item">
        <span class="metric-label">Background Worker:</span>
        <span class="metric-value">${workerStatus === 'active' ? '🟢' : '⚫'} ${workerNextRun}</span>
      </div>
      <div class="metric-item">
        <span class="metric-label">WebSocket:</span>
        <span class="metric-value">${wsStatus}</span>
      </div>
    `;
  }
  
  /**
   * Update resource breakdown section
   */
  updateResourceBreakdown(breakdown) {
    const container = document.getElementById('resources-breakdown');
    if (!container) return;
    
    const total = breakdown.total || 0;
    const bySource = breakdown.by_source || {};
    const byCategory = breakdown.by_category || {};
    
    let sourceHTML = '';
    for (const [source, count] of Object.entries(bySource)) {
      sourceHTML += `
        <div class="breakdown-item">
          <span class="breakdown-label">${source}:</span>
          <span class="breakdown-value">${count}</span>
        </div>
      `;
    }
    
    let categoryHTML = '';
    for (const [category, count] of Object.entries(byCategory)) {
      categoryHTML += `
        <div class="breakdown-item">
          <span class="breakdown-label">${category}:</span>
          <span class="breakdown-value">${count} online</span>
        </div>
      `;
    }
    
    container.innerHTML = `
      <div class="breakdown-section">
        <div class="breakdown-title">Total: ${total}+ resources</div>
        ${sourceHTML}
      </div>
      <div class="breakdown-section">
        <div class="breakdown-title">By Category:</div>
        ${categoryHTML}
      </div>
    `;
  }
  
  /**
   * Update error details section
   */
  updateErrorDetails(errors) {
    const container = document.getElementById('error-list');
    if (!container) return;
    
    if (!errors || errors.length === 0) {
      container.innerHTML = '<div class="empty-state">No recent errors</div>';
      return;
    }
    
    container.innerHTML = errors.map(error => `
      <div class="error-item">
        <div class="error-provider">${error.provider || 'Unknown'}: ${error.count || 1}x ${error.type || 'error'}</div>
        <div class="error-message">${error.message || 'Unknown error'}</div>
        ${error.action ? `<div class="error-action">Action: ${error.action}</div>` : ''}
      </div>
    `).join('');
  }
  
  /**
   * Update performance section
   */
  updatePerformance(performance) {
    const container = document.getElementById('performance-metrics');
    if (!container) return;
    
    const avgResponse = performance.avg_response_ms || 0;
    const fastest = performance.fastest_provider || 'N/A';
    const fastestTime = performance.fastest_time_ms || 0;
    const cacheHit = performance.cache_hit_rate || 0;
    
    container.innerHTML = `
      <div class="metric-item">
        <span class="metric-label">Avg Response:</span>
        <span class="metric-value">${avgResponse}ms</span>
      </div>
      <div class="metric-item">
        <span class="metric-label">Fastest:</span>
        <span class="metric-value">${fastest} (${fastestTime}ms)</span>
      </div>
      <div class="metric-item">
        <span class="metric-label">Cache Hit:</span>
        <span class="metric-value">${cacheHit}%</span>
      </div>
    `;
  }
  
  /**
   * Update endpoints
   */
  updateEndpoints(endpoints) {
    const container = document.getElementById('endpoints-status');
    if (!container) return;
    
    if (!endpoints.length) {
      container.innerHTML = '<div class="empty-state">No endpoints</div>';
      return;
    }
    
    container.innerHTML = endpoints.map(endpoint => {
      const statusClass = endpoint.status === 'online' ? 'status-online' : 'status-offline';
      return `
        <div class="status-item ${statusClass}">
          <div class="status-dot"></div>
          <div class="status-info">
            <div class="status-name">${endpoint.path}</div>
            <div class="status-meta">
              ${endpoint.avg_response_ms ? `${endpoint.avg_response_ms.toFixed(0)}ms` : '--'} • 
              ${endpoint.success_rate ? `${endpoint.success_rate.toFixed(1)}%` : '--'}
            </div>
          </div>
        </div>
      `;
    }).join('');
  }
  
  /**
   * Update providers
   */
  updateProviders(services) {
    const container = document.getElementById('providers-status');
    if (!container) return;
    
    if (!services.length) {
      container.innerHTML = '<div class="empty-state">No providers</div>';
      return;
    }
    
    container.innerHTML = services.map(service => {
      const statusClass = service.status === 'online' ? 'status-online' : 'status-offline';
      return `
        <div class="status-item ${statusClass}">
          <div class="status-dot"></div>
          <div class="status-info">
            <div class="status-name">${service.name}</div>
            <div class="status-meta">
              ${service.response_time_ms ? `${service.response_time_ms.toFixed(0)}ms` : 'Offline'}
            </div>
          </div>
        </div>
      `;
    }).join('');
  }
  
  /**
   * Update coins
   */
  updateCoins(coins) {
    const container = document.getElementById('coins-status');
    if (!container) return;
    
    if (!coins.length) {
      container.innerHTML = '<div class="empty-state">No coins</div>';
      return;
    }
    
    container.innerHTML = coins.map(coin => {
      const statusClass = coin.status === 'online' ? 'status-online' : 'status-offline';
      return `
        <div class="status-item ${statusClass}">
          <div class="status-dot"></div>
          <div class="status-info">
            <div class="status-name">${coin.symbol}</div>
            <div class="status-meta">
              ${coin.price ? `$${coin.price.toLocaleString()}` : 'Unavailable'}
            </div>
          </div>
        </div>
      `;
    }).join('');
  }
  
  /**
   * Update timestamp
   */
  updateTimestamp(timestamp) {
    const element = document.getElementById('last-update-time');
    if (element) {
      const date = new Date(timestamp * 1000);
      element.textContent = date.toLocaleTimeString();
    }
  }
  
  /**
   * Show error state
   */
  showError() {
    const sections = ['resources-summary', 'endpoints-status', 'providers-status', 'coins-status'];
    sections.forEach(id => {
      const element = document.getElementById(id);
      if (element) {
        element.innerHTML = '<div class="error-state">Failed to load</div>';
      }
    });
  }
  
  /**
   * Destroy drawer
   */
  destroy() {
    this.stopPolling();
    if (this.drawerElement) this.drawerElement.remove();
    if (this.buttonElement) this.buttonElement.remove();
  }
}

// Export
if (typeof window !== 'undefined') {
  window.StatusDrawer = StatusDrawer;
}
