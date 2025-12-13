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
   * Create drawer panel
   */
  createDrawer() {
    const drawer = document.createElement('div');
    drawer.id = 'status-drawer';
    drawer.className = 'status-drawer';
    drawer.innerHTML = `
      <div class="status-drawer-header">
        <h3>System Status</h3>
        <button class="drawer-close" aria-label="Close">
          <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <path d="M9 18l6-6-6-6"/>
          </svg>
        </button>
      </div>
      
      <div class="status-drawer-body">
        <!-- Resources Status -->
        <div class="status-section">
          <div class="section-title">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M21 16V8a2 2 0 0 0-1-1.73l-7-4a2 2 0 0 0-2 0l-7 4A2 2 0 0 0 3 8v8a2 2 0 0 0 1 1.73l7 4a2 2 0 0 0 2 0l7-4A2 2 0 0 0 21 16z"/>
            </svg>
            <span>Resources</span>
          </div>
          <div class="resources-summary" id="resources-summary">
            <div class="summary-loading">Loading...</div>
          </div>
        </div>
        
        <!-- Endpoints Status -->
        <div class="status-section">
          <div class="section-title">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"/>
              <polyline points="12 6 12 12 16 14"/>
            </svg>
            <span>API Endpoints</span>
          </div>
          <div class="endpoints-status" id="endpoints-status">
            <div class="summary-loading">Loading...</div>
          </div>
        </div>
        
        <!-- Providers Status -->
        <div class="status-section">
          <div class="section-title">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <rect x="2" y="3" width="20" height="14" rx="2"/>
              <line x1="8" y1="21" x2="16" y2="21"/>
              <line x1="12" y1="17" x2="12" y2="21"/>
            </svg>
            <span>Service Providers</span>
          </div>
          <div class="providers-status" id="providers-status">
            <div class="summary-loading">Loading...</div>
          </div>
        </div>
        
        <!-- Coins Status -->
        <div class="status-section">
          <div class="section-title">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="12" y1="1" x2="12" y2="23"/>
              <path d="M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
            </svg>
            <span>Market Feeds</span>
          </div>
          <div class="coins-status" id="coins-status">
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
   * Update UI with data
   */
  updateUI(data) {
    this.lastData = data;
    
    // Update resources summary
    this.updateResourcesSummary(data);
    
    // Update endpoints
    this.updateEndpoints(data.endpoints || []);
    
    // Update providers
    this.updateProviders(data.services || []);
    
    // Update coins
    this.updateCoins(data.coins || []);
    
    // Update timestamp
    this.updateTimestamp(data.timestamp);
  }
  
  /**
   * Update resources summary
   */
  updateResourcesSummary(data) {
    const container = document.getElementById('resources-summary');
    if (!container) return;
    
    // Count total resources from services
    const totalServices = (data.services || []).length;
    const onlineServices = (data.services || []).filter(s => s.status === 'online').length;
    
    const totalEndpoints = (data.endpoints || []).length;
    const onlineEndpoints = (data.endpoints || []).filter(e => e.status === 'online').length;
    
    const totalCoins = (data.coins || []).length;
    const onlineCoins = (data.coins || []).filter(c => c.status === 'online').length;
    
    const totalResources = totalServices + totalEndpoints + totalCoins;
    const availableResources = onlineServices + onlineEndpoints + onlineCoins;
    const unavailableResources = totalResources - availableResources;
    
    container.innerHTML = `
      <div class="resource-stat">
        <div class="stat-value">${totalResources}</div>
        <div class="stat-label">Total Resources</div>
      </div>
      <div class="resource-stat success">
        <div class="stat-value">${availableResources}</div>
        <div class="stat-label">Available</div>
      </div>
      <div class="resource-stat ${unavailableResources > 0 ? 'danger' : ''}">
        <div class="stat-value">${unavailableResources}</div>
        <div class="stat-label">Unavailable</div>
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
