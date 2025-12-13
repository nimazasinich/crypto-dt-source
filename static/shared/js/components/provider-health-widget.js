/**
 * Provider Health Widget - Real-time monitoring of data provider status
 * Shows health, circuit breaker status, and performance metrics
 * @version 1.0.0
 */

import logger from '../utils/logger.js';

class ProviderHealthWidget {
  constructor(containerId = 'provider-health-widget') {
    this.containerId = containerId;
    this.updateInterval = null;
    this.isVisible = false;
    this.autoRefresh = true;
    this.refreshRate = 10000; // 10 seconds
  }

  async init() {
    try {
      logger.info('ProviderHealth', 'Initializing provider health widget...');
      await this.render();
      if (this.autoRefresh) {
        this.startAutoRefresh();
      }
    } catch (error) {
      logger.error('ProviderHealth', 'Init error:', error);
    }
  }

  async fetchProviderHealth() {
    try {
      const response = await fetch('/api/system/providers/health');
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch (error) {
      logger.error('ProviderHealth', 'Fetch error:', error);
      return null;
    }
  }

  async fetchBinanceHealth() {
    try {
      const response = await fetch('/api/system/binance/health');
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch (error) {
      logger.error('ProviderHealth', 'Binance fetch error:', error);
      return null;
    }
  }

  async fetchCircuitBreakers() {
    try {
      const response = await fetch('/api/system/circuit-breakers');
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      return await response.json();
    } catch (error) {
      logger.error('ProviderHealth', 'Circuit breaker fetch error:', error);
      return null;
    }
  }

  getStatusColor(status) {
    const colors = {
      'healthy': '#10b981',
      'degraded': '#f59e0b',
      'down': '#ef4444'
    };
    return colors[status] || '#6b7280';
  }

  getStatusIcon(status) {
    const icons = {
      'healthy': '✓',
      'degraded': '⚠',
      'down': '✕'
    };
    return icons[status] || '?';
  }

  async render() {
    const container = document.getElementById(this.containerId);
    if (!container) {
      logger.warn('ProviderHealth', 'Container not found:', this.containerId);
      return;
    }

    // Show loading state
    container.innerHTML = `
      <div class="provider-health-widget loading">
        <div class="widget-header">
          <h3>Provider Health</h3>
          <div class="loading-spinner"></div>
        </div>
      </div>
    `;

    // Fetch data
    const [healthData, binanceData, circuitData] = await Promise.all([
      this.fetchProviderHealth(),
      this.fetchBinanceHealth(),
      this.fetchCircuitBreakers()
    ]);

    if (!healthData || !healthData.success) {
      container.innerHTML = `
        <div class="provider-health-widget error">
          <div class="widget-header">
            <h3>Provider Health</h3>
            <span class="status-badge error">Unavailable</span>
          </div>
          <p class="error-message">Failed to load provider health data</p>
        </div>
      `;
      return;
    }

    // Render widget
    container.innerHTML = this.generateHTML(healthData, binanceData, circuitData);
    this.attachEventListeners();
  }

  generateHTML(healthData, binanceData, circuitData) {
    const summary = healthData.summary || {};
    const providers = healthData.providers || {};

    return `
      <div class="provider-health-widget">
        <!-- Header -->
        <div class="widget-header">
          <h3>
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M22 12h-4l-3 9L9 3l-3 9H2"/>
            </svg>
            Provider Health
          </h3>
          <div class="widget-actions">
            <button class="btn-icon refresh-btn" title="Refresh">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <path d="M21 12a9 9 0 1 1-9-9c2.52 0 4.93 1 6.74 2.74L21 8"/>
                <path d="M21 3v5h-5"/>
              </svg>
            </button>
            <button class="btn-icon expand-btn" title="Expand">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="15 3 21 3 21 9"/>
                <polyline points="9 21 3 21 3 15"/>
                <line x1="21" y1="3" x2="14" y2="10"/>
                <line x1="3" y1="21" x2="10" y2="14"/>
              </svg>
            </button>
          </div>
        </div>

        <!-- Summary -->
        <div class="health-summary">
          <div class="summary-stat">
            <div class="stat-value" style="color: #10b981">${summary.healthy_providers || 0}</div>
            <div class="stat-label">Healthy</div>
          </div>
          <div class="summary-stat">
            <div class="stat-value" style="color: #f59e0b">${summary.degraded_providers || 0}</div>
            <div class="stat-label">Degraded</div>
          </div>
          <div class="summary-stat">
            <div class="stat-value" style="color: #ef4444">${summary.down_providers || 0}</div>
            <div class="stat-label">Down</div>
          </div>
        </div>

        <!-- Providers by Category -->
        <div class="providers-list">
          ${this.generateProvidersList(providers)}
        </div>

        ${binanceData && binanceData.success ? this.generateBinanceSection(binanceData) : ''}
        
        ${circuitData && circuitData.success ? this.generateCircuitBreakerSection(circuitData) : ''}

        <!-- Footer -->
        <div class="widget-footer">
          <small>Last updated: ${new Date().toLocaleTimeString()}</small>
          <label class="auto-refresh-toggle">
            <input type="checkbox" ${this.autoRefresh ? 'checked' : ''}>
            <span>Auto-refresh</span>
          </label>
        </div>
      </div>
    `;
  }

  generateProvidersList(providers) {
    if (!providers || Object.keys(providers).length === 0) {
      return '<p class="no-data">No provider data available</p>';
    }

    return Object.entries(providers)
      .filter(([key, _]) => key !== 'binance_dns')
      .map(([category, providerList]) => {
        if (!Array.isArray(providerList) || providerList.length === 0) return '';

        const categoryName = category.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
        
        return `
          <div class="provider-category">
            <h4>${categoryName}</h4>
            <div class="provider-items">
              ${providerList.map(provider => `
                <div class="provider-item" data-status="${provider.status}">
                  <div class="provider-info">
                    <span class="provider-name">${provider.name}</span>
                    <span class="provider-priority">P${provider.priority}</span>
                  </div>
                  <div class="provider-status">
                    <span class="status-badge ${provider.status}" 
                          style="background: ${this.getStatusColor(provider.status)}22; 
                                 color: ${this.getStatusColor(provider.status)}">
                      ${this.getStatusIcon(provider.status)} ${provider.status}
                    </span>
                    ${provider.success_rate ? `<span class="success-rate">${provider.success_rate}</span>` : ''}
                  </div>
                </div>
              `).join('')}
            </div>
          </div>
        `;
      }).join('');
  }

  generateBinanceSection(binanceData) {
    const health = binanceData.binance_health || {};
    const summary = binanceData.summary || {};

    return `
      <div class="binance-dns-section">
        <h4>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"/>
            <path d="M12 6v6l4 2"/>
          </svg>
          Binance DNS Failover
        </h4>
        <div class="binance-summary">
          <span class="available">${summary.available_endpoints || 0}/${summary.total_endpoints || 0} Available</span>
          ${summary.in_backoff > 0 ? `<span class="backoff">${summary.in_backoff} In Backoff</span>` : ''}
        </div>
        <div class="binance-endpoints">
          ${(health.endpoints || []).slice(0, 5).map(ep => `
            <div class="binance-endpoint ${ep.available ? 'available' : 'unavailable'}">
              <span class="endpoint-url">${ep.url.replace('https://', '')}</span>
              <span class="endpoint-status">
                ${ep.available ? '✓' : '✕'} 
                ${ep.success_rate ? `${ep.success_rate.toFixed(0)}%` : 'N/A'}
              </span>
            </div>
          `).join('')}
        </div>
      </div>
    `;
  }

  generateCircuitBreakerSection(circuitData) {
    const breakers = circuitData.circuit_breakers || {};
    const summary = circuitData.summary || {};

    const openBreakers = Object.values(breakers)
      .flat()
      .filter(b => b.circuit_open);

    if (openBreakers.length === 0) {
      return `
        <div class="circuit-breaker-section success">
          <h4>Circuit Breakers</h4>
          <p class="all-good">✓ All circuit breakers closed</p>
        </div>
      `;
    }

    return `
      <div class="circuit-breaker-section warning">
        <h4>Circuit Breakers</h4>
        <p class="warning-message">⚠ ${openBreakers.length} circuit breaker(s) open</p>
        <div class="open-breakers">
          ${openBreakers.map(b => `
            <div class="breaker-item">
              <span>${b.provider}</span>
              <span class="failure-count">${b.consecutive_failures} failures</span>
            </div>
          `).join('')}
        </div>
      </div>
    `;
  }

  attachEventListeners() {
    // Refresh button
    const refreshBtn = document.querySelector('.provider-health-widget .refresh-btn');
    if (refreshBtn) {
      refreshBtn.addEventListener('click', () => {
        this.render();
      });
    }

    // Auto-refresh toggle
    const autoRefreshToggle = document.querySelector('.provider-health-widget .auto-refresh-toggle input');
    if (autoRefreshToggle) {
      autoRefreshToggle.addEventListener('change', (e) => {
        this.autoRefresh = e.target.checked;
        if (this.autoRefresh) {
          this.startAutoRefresh();
        } else {
          this.stopAutoRefresh();
        }
      });
    }

    // Expand button
    const expandBtn = document.querySelector('.provider-health-widget .expand-btn');
    if (expandBtn) {
      expandBtn.addEventListener('click', () => {
        this.openDetailedView();
      });
    }
  }

  openDetailedView() {
    // Open detailed provider health in modal or new page
    window.open('/api/system/providers/health', '_blank');
  }

  startAutoRefresh() {
    if (this.updateInterval) {
      clearInterval(this.updateInterval);
    }
    this.updateInterval = setInterval(() => {
      this.render();
    }, this.refreshRate);
  }

  stopAutoRefresh() {
    if (this.updateInterval) {
      clearInterval(this.updateInterval);
      this.updateInterval = null;
    }
  }

  destroy() {
    this.stopAutoRefresh();
  }
}

// Export singleton
let instance = null;

export function initProviderHealthWidget(containerId) {
  if (!instance) {
    instance = new ProviderHealthWidget(containerId);
  }
  return instance.init();
}

export function getProviderHealthWidget() {
  return instance;
}

export default ProviderHealthWidget;
