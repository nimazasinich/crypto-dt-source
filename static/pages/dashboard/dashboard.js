/**
 * Dashboard Page Controller
 * Displays system overview, stats, and resource categories
 */

import { api } from '../../shared/js/core/api-client.js';
import { pollingManager } from '../../shared/js/core/polling-manager.js';
import { LayoutManager } from '../../shared/js/core/layout-manager.js';
import { Toast } from '../../shared/js/components/toast.js';
import { Loading } from '../../shared/js/components/loading.js';
import { ChartComponent, loadChartJS } from '../../shared/js/components/chart.js';
import { formatNumber } from '../../shared/js/utils/formatters.js';

/**
 * Dashboard Page Class
 */
class DashboardPage {
  constructor() {
    this.chart = null;
    this.data = null;
    this.isChartJSLoaded = false;
  }

  /**
   * Initialize the dashboard
   */
  async init() {
    try {
      console.log('[Dashboard] Initializing...');

      // Inject shared layouts (header, sidebar, footer)
      await LayoutManager.injectLayouts();
      
      // Set active navigation
      LayoutManager.setActiveNav('dashboard');

      // Update API status in header
      this.updateApiStatus();

      // Bind event listeners
      this.bindEvents();

      // Load Chart.js
      await loadChartJS();
      this.isChartJSLoaded = true;

      // Load initial data
      await this.loadData();

      // Setup auto-refresh polling (30 seconds)
      this.setupPolling();

      // Setup "last updated" UI updates
      this.setupLastUpdateUI();

      console.log('[Dashboard] Initialized successfully');
    } catch (error) {
      console.error('[Dashboard] Initialization error:', error);
      Toast.error('Failed to initialize dashboard');
    }
  }

  /**
   * Bind event listeners
   */
  bindEvents() {
    // Manual refresh button
    const refreshBtn = document.getElementById('refresh-btn');
    if (refreshBtn) {
      refreshBtn.addEventListener('click', () => {
        console.log('[Dashboard] Manual refresh triggered');
        this.loadData();
        Toast.info('Refreshing dashboard...');
      });
    }
  }

  /**
   * Fetch data from API
   */
  async fetchData() {
    const [resources, status] = await Promise.all([
      api.getResources(),
      api.getStatus()
    ]);

    return { resources, status };
  }

  /**
   * Load dashboard data
   */
  async loadData() {
    try {
      // Show loading state
      Loading.addSkeleton('.stat-card');

      // Fetch data
      const data = await this.fetchData();
      this.data = data;

      // Render all sections
      this.renderData(data);

      // Remove loading state
      Loading.removeSkeleton('.stat-card');

    } catch (error) {
      console.error('[Dashboard] Load error:', error);
      Toast.error('Failed to load dashboard data');
      Loading.removeSkeleton('.stat-card');
    }
  }

  /**
   * Render all dashboard data
   */
  renderData({ resources, status }) {
    this.renderStatsGrid(resources);
    this.renderSystemAlert(status);
    this.renderCategoriesChart(resources.categories || []);
  }

  /**
   * Render stats grid (4 cards)
   */
  renderStatsGrid(resources) {
    const grid = document.getElementById('stats-grid');
    if (!grid) return;

    grid.innerHTML = `
      <div class="stat-card">
        <div class="stat-icon">📦</div>
        <div class="stat-content">
          <div class="stat-value">${formatNumber(resources.total || 0)}</div>
          <div class="stat-label">Total Resources</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">🆓</div>
        <div class="stat-content">
          <div class="stat-value">${formatNumber(resources.free || 0)}</div>
          <div class="stat-label">Free Resources</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">🤖</div>
        <div class="stat-content">
          <div class="stat-value">${formatNumber(resources.models || 0)}</div>
          <div class="stat-label">AI Models</div>
        </div>
      </div>
      <div class="stat-card">
        <div class="stat-icon">🔌</div>
        <div class="stat-content">
          <div class="stat-value">${formatNumber(resources.providers || 0)}</div>
          <div class="stat-label">Active Providers</div>
        </div>
      </div>
    `;
  }

  /**
   * Render system status alert
   */
  renderSystemAlert(status) {
    const container = document.getElementById('system-alert');
    if (!container) return;

    const alertClass = status.health === 'healthy' ? 'alert-success' :
                       status.health === 'degraded' ? 'alert-warning' : 'alert-error';

    const icon = status.health === 'healthy' ? '✅' :
                 status.health === 'degraded' ? '⚠️' : '❌';

    container.innerHTML = `
      <div class="alert ${alertClass}" role="alert">
        <div class="alert-icon">${icon}</div>
        <div class="alert-content">
          <div class="alert-title">System Status: ${status.health.toUpperCase()}</div>
          <div class="alert-body">
            Online APIs: ${status.online || 0} | 
            Offline: ${status.offline || 0} | 
            ${status.degraded ? `Degraded: ${status.degraded} | ` : ''}
            Avg Response Time: ${status.avg_response_time || 'N/A'}ms
          </div>
        </div>
      </div>
    `;
  }

  /**
   * Render categories chart (Bar chart with Chart.js)
   */
  renderCategoriesChart(categories) {
    if (!this.isChartJSLoaded) {
      console.warn('[Dashboard] Chart.js not loaded yet');
      return;
    }

    if (!categories || categories.length === 0) {
      console.warn('[Dashboard] No categories data');
      return;
    }

    // Create chart if not exists
    if (!this.chart) {
      this.chart = new ChartComponent('categories-chart', 'bar');
    }

    const data = {
      labels: categories.map(c => c.name || 'Unknown'),
      datasets: [{
        label: 'Resource Count',
        data: categories.map(c => c.count || 0),
        backgroundColor: 'rgba(59, 130, 246, 0.6)',
        borderColor: 'rgba(59, 130, 246, 1)',
        borderWidth: 1,
      }]
    };

    const options = {
      indexAxis: 'y', // Horizontal bar chart
      scales: {
        x: {
          beginAtZero: true,
          ticks: {
            precision: 0
          }
        }
      },
      plugins: {
        legend: {
          display: false
        }
      }
    };

    this.chart.create(data, options);
  }

  /**
   * Setup polling for auto-refresh
   */
  setupPolling() {
    pollingManager.start(
      'dashboard-data',
      () => this.fetchData(),
      (data, error) => {
        if (data) {
          console.log('[Dashboard] Polling update received');
          this.renderData(data);
        } else {
          console.error('[Dashboard] Polling error:', error);
          // Don't show toast on polling errors (would be too annoying)
        }
      },
      30000 // 30 seconds
    );

    console.log('[Dashboard] Polling started (30s interval)');
  }

  /**
   * Setup "last updated" UI updates
   */
  setupLastUpdateUI() {
    const el = document.getElementById('last-update');
    if (!el) return;

    pollingManager.onLastUpdate((key, text) => {
      if (key === 'dashboard-data') {
        el.textContent = `Last updated: ${text}`;
      }
    });
  }

  /**
   * Update API status in header
   */
  async updateApiStatus() {
    try {
      const health = await api.getHealth();
      LayoutManager.updateApiStatus('online', '✅ System Active');
    } catch (error) {
      LayoutManager.updateApiStatus('offline', '❌ Connection Failed');
    }
  }

  /**
   * Cleanup on page unload
   */
  destroy() {
    console.log('[Dashboard] Cleaning up...');
    pollingManager.stop('dashboard-data');
    if (this.chart) {
      this.chart.destroy();
    }
  }
}

// ============================================================================
// INITIALIZE ON DOM READY
// ============================================================================

function initDashboard() {
  const page = new DashboardPage();
  page.init();

  // Cleanup on page unload
  window.addEventListener('beforeunload', () => {
    page.destroy();
  });
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initDashboard);
} else {
  initDashboard();
}
