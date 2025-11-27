import { api } from '../../shared/js/core/api-client.js';
import { pollingManager } from '../../shared/js/core/polling-manager.js';
import { LayoutManager } from '../../shared/js/core/layout-manager.js';
import { Toast } from '../../shared/js/components/toast.js';
import { Loading } from '../../shared/js/components/loading.js';
import { formatNumber } from '../../shared/js/utils/formatters.js';

class ProvidersPage {
  constructor() {
    this.providers = [];
    this.filteredProviders = [];
  }

  async init() {
    try {
      await LayoutManager.injectLayouts();
      LayoutManager.setActiveNav('providers');
      
      this.bindEvents();
      await this.loadData();
      this.setupPolling();
      this.setupLastUpdateUI();
    } catch (error) {
      console.error('[Providers] Init error:', error);
      Toast.error('Failed to initialize providers page');
    }
  }

  bindEvents() {
    document.getElementById('refresh-btn')?.addEventListener('click', () => this.loadData());
    document.getElementById('search-input')?.addEventListener('input', (e) => this.filterProviders());
    document.getElementById('category-select')?.addEventListener('change', () => this.filterProviders());
  }

  async loadData() {
    try {
      const tbody = document.getElementById('providers-tbody');
      tbody.innerHTML = '<tr><td colspan="5" class="text-center"><div class="loading-container"><div class="spinner"></div></div></td></tr>';
      
      const data = await api.getProviders();
      this.providers = data.providers || [];
      this.filteredProviders = [...this.providers];
      
      this.renderSummary();
      this.renderTable();
    } catch (error) {
      console.error('[Providers] Load error:', error);
      Toast.error('Failed to load providers');
    }
  }

  renderSummary() {
    const total = this.providers.length;
    const healthy = this.providers.filter(p => p.status === 'healthy').length;
    const issues = total - healthy;

    const container = document.getElementById('summary-cards');
    container.innerHTML = `
      <div class="summary-card">
        <div class="summary-value">${total}</div>
        <div class="summary-label">Total Providers</div>
      </div>
      <div class="summary-card healthy">
        <div class="summary-value">${healthy}</div>
        <div class="summary-label">Healthy</div>
      </div>
      <div class="summary-card issues">
        <div class="summary-value">${issues}</div>
        <div class="summary-label">Issues</div>
      </div>
    `;
  }

  renderTable() {
    const tbody = document.getElementById('providers-tbody');
    
    if (this.filteredProviders.length === 0) {
      tbody.innerHTML = '<tr><td colspan="5" class="text-center">No providers found</td></tr>';
      return;
    }

    tbody.innerHTML = this.filteredProviders.map(provider => `
      <tr>
        <td><strong>${provider.name}</strong></td>
        <td>${this.formatCategory(provider.category)}</td>
        <td><span class="badge badge-${provider.status === 'healthy' ? 'success' : 'error'}">${provider.status}</span></td>
        <td>${provider.latency ? provider.latency + 'ms' : 'N/A'}</td>
        <td>${provider.error || 'OK'}</td>
      </tr>
    `).join('');
  }

  filterProviders() {
    const searchTerm = document.getElementById('search-input').value.toLowerCase();
    const category = document.getElementById('category-select').value;

    this.filteredProviders = this.providers.filter(p => {
      const matchesSearch = p.name.toLowerCase().includes(searchTerm) || 
                           p.category.toLowerCase().includes(searchTerm);
      const matchesCategory = !category || p.category === category;
      return matchesSearch && matchesCategory;
    });

    this.renderTable();
  }

  formatCategory(cat) {
    return cat.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase());
  }

  setupPolling() {
    pollingManager.start(
      'providers-data',
      () => api.getProviders(),
      (data, error) => {
        if (data) {
          this.providers = data.providers || [];
          this.filterProviders();
          this.renderSummary();
        }
      },
      60000 // 60 seconds
    );
  }

  setupLastUpdateUI() {
    const el = document.getElementById('last-update');
    pollingManager.onLastUpdate((key, text) => {
      if (key === 'providers-data') el.textContent = `Last updated: ${text}`;
    });
  }

  destroy() {
    pollingManager.stop('providers-data');
  }
}

function initProviders() {
  const page = new ProvidersPage();
  page.init();
  window.addEventListener('beforeunload', () => page.destroy());
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initProviders);
} else {
  initProviders();
}
