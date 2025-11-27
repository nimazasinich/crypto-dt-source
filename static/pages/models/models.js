/**
 * AI Models Page
 * Displays available ML models and their status
 */

import { api } from '../../shared/js/core/api-client.js';
import { LayoutManager } from '../../shared/js/core/layout-manager.js';
import { Toast } from '../../shared/js/components/toast.js';

class ModelsPage {
  constructor() {
    this.models = [];
    this.stats = null;
  }

  async init() {
    try {
      await LayoutManager.injectLayouts();
      LayoutManager.setActiveNav('models');
      
      this.bindEvents();
      await this.loadData();
      this.updateLastUpdate();
    } catch (error) {
      console.error('[Models] Init error:', error);
      Toast.error('Failed to initialize models page');
    }
  }

  bindEvents() {
    document.getElementById('refresh-btn')?.addEventListener('click', () => this.loadData());
  }

  async loadData() {
    try {
      const grid = document.getElementById('models-grid');
      grid.innerHTML = '<div class="loading-container"><div class="spinner"></div><p>Loading models...</p></div>';
      
      const [modelsData, statsData] = await Promise.all([
        api.getModelsList().catch(() => ({ models: [] })),
        api.getModelsStats().catch(() => null)
      ]);
      
      this.models = modelsData.models || [];
      this.stats = statsData;
      
      this.renderStats();
      this.renderModels();
      this.updateLastUpdate();
      
      Toast.success('Models data loaded');
    } catch (error) {
      console.error('[Models] Load error:', error);
      Toast.error('Failed to load models data');
    }
  }

  renderStats() {
    const total = this.models.length;
    const active = this.models.filter(m => m.status === 'active' || m.status === 'ready').length;
    
    document.getElementById('total-models').textContent = total;
    document.getElementById('active-models').textContent = active;
    document.getElementById('avg-response').textContent = this.stats?.avg_response_time ? 
      `${this.stats.avg_response_time}ms` : 'N/A';
    document.getElementById('total-requests').textContent = this.stats?.total_requests ? 
      this.formatNumber(this.stats.total_requests) : '0';
  }

  renderModels() {
    const grid = document.getElementById('models-grid');
    
    if (this.models.length === 0) {
      grid.innerHTML = `
        <div class="empty-state">
          <div class="empty-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="4" y="4" width="16" height="16" rx="2" ry="2"></rect><rect x="9" y="9" width="6" height="6"></rect><line x1="9" y1="1" x2="9" y2="4"></line><line x1="15" y1="1" x2="15" y2="4"></line></svg>
          </div>
          <p>No models available</p>
        </div>
      `;
      return;
    }

    grid.innerHTML = this.models.map(model => `
      <div class="model-card">
        <div class="model-header">
          <div class="model-icon">
            <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 4.44-2z"></path><path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-4.44-2z"></path></svg>
          </div>
          <div class="model-info">
            <h3 class="model-name">${model.name || model.id}</h3>
            <span class="model-type">${model.type || 'ML Model'}</span>
          </div>
          <span class="badge badge-${this.getStatusClass(model.status)}">${model.status || 'unknown'}</span>
        </div>
        <div class="model-body">
          <div class="model-description">${model.description || 'No description available'}</div>
          <div class="model-meta">
            ${model.version ? `<span class="meta-item"><strong>Version:</strong> ${model.version}</span>` : ''}
            ${model.accuracy ? `<span class="meta-item"><strong>Accuracy:</strong> ${(model.accuracy * 100).toFixed(1)}%</span>` : ''}
            ${model.latency ? `<span class="meta-item"><strong>Latency:</strong> ${model.latency}ms</span>` : ''}
          </div>
        </div>
        <div class="model-footer">
          <button class="btn btn-sm btn-secondary" onclick="window.modelsPage.testModel('${model.id || model.name}')">
            <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
            Test Model
          </button>
        </div>
      </div>
    `).join('');
  }

  getStatusClass(status) {
    const statusMap = {
      'active': 'success',
      'ready': 'success',
      'loading': 'warning',
      'inactive': 'secondary',
      'error': 'error'
    };
    return statusMap[status] || 'secondary';
  }

  formatNumber(num) {
    if (num >= 1000000) return (num / 1000000).toFixed(1) + 'M';
    if (num >= 1000) return (num / 1000).toFixed(1) + 'K';
    return num.toString();
  }

  async testModel(modelId) {
    Toast.info(`Testing model: ${modelId}`);
    try {
      const result = await api.testModel(modelId, { test: true });
      Toast.success(`Model ${modelId} test completed`);
      console.log('[Models] Test result:', result);
    } catch (error) {
      Toast.error(`Model test failed: ${error.message}`);
    }
  }

  updateLastUpdate() {
    const el = document.getElementById('last-update');
    if (el) {
      el.textContent = `Updated: ${new Date().toLocaleTimeString()}`;
    }
  }
}

// Initialize page
const page = new ModelsPage();
window.modelsPage = page; // Expose for button handlers

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => page.init());
} else {
  page.init();
}
