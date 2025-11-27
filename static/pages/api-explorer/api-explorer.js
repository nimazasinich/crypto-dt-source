/**
 * API Explorer Page
 * Interactive API testing tool
 */

import { LayoutManager } from '../../shared/js/core/layout-manager.js';
import { Toast } from '../../shared/js/components/toast.js';
import { CONFIG } from '../../shared/js/core/config.js';

class APIExplorerPage {
  constructor() {
    this.history = [];
    this.maxHistory = 20;
  }

  async init() {
    try {
      await LayoutManager.injectLayouts();
      LayoutManager.setActiveNav('api-explorer');
      
      this.bindEvents();
      this.loadHistory();
    } catch (error) {
      console.error('[APIExplorer] Init error:', error);
      Toast.error('Failed to initialize API Explorer');
    }
  }

  bindEvents() {
    document.getElementById('send-btn')?.addEventListener('click', () => this.sendRequest());
    document.getElementById('copy-btn')?.addEventListener('click', () => this.copyResponse());
    document.getElementById('clear-btn')?.addEventListener('click', () => this.clearResponse());
    document.getElementById('clear-history-btn')?.addEventListener('click', () => this.clearHistory());
    
    document.getElementById('method-select')?.addEventListener('change', () => this.toggleBodyInput());
    document.getElementById('endpoint-select')?.addEventListener('change', (e) => {
      const option = e.target.selectedOptions[0];
      if (option.dataset.method) {
        document.getElementById('method-select').value = option.dataset.method;
        this.toggleBodyInput();
      }
    });

    // Keyboard shortcut
    document.addEventListener('keydown', (e) => {
      if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        e.preventDefault();
        this.sendRequest();
      }
    });
  }

  toggleBodyInput() {
    const method = document.getElementById('method-select').value;
    const bodyGroup = document.getElementById('body-group');
    bodyGroup.style.display = ['POST', 'PUT'].includes(method) ? 'block' : 'none';
  }

  async sendRequest() {
    const method = document.getElementById('method-select').value;
    const endpoint = document.getElementById('endpoint-select').value;
    const bodyText = document.getElementById('request-body').value.trim();
    
    const responseContent = document.getElementById('response-content');
    const responseStatus = document.getElementById('response-status');
    const responseTime = document.getElementById('response-time');
    
    responseContent.textContent = 'Loading...';
    responseStatus.textContent = '--';
    responseStatus.className = 'status';
    responseTime.textContent = '--';

    const startTime = performance.now();
    
    try {
      let body = null;
      if (['POST', 'PUT'].includes(method) && bodyText) {
        try {
          body = JSON.parse(bodyText);
        } catch (e) {
          Toast.error('Invalid JSON in request body');
          responseContent.textContent = 'Error: Invalid JSON in request body';
          return;
        }
      }

      const response = await fetch(`${CONFIG.API_BASE_URL}${endpoint.replace('/api', '')}`, {
        method,
        headers: {
          'Content-Type': 'application/json',
        },
        body: body ? JSON.stringify(body) : undefined,
      });

      const duration = Math.round(performance.now() - startTime);
      const data = await response.json();

      responseStatus.textContent = `${response.status} ${response.statusText}`;
      responseStatus.className = `status ${response.ok ? 'success' : 'error'}`;
      responseTime.textContent = `${duration}ms`;
      responseContent.textContent = JSON.stringify(data, null, 2);

      // Add to history
      this.addToHistory({
        method,
        endpoint,
        status: response.status,
        duration,
        timestamp: new Date().toISOString(),
      });

      Toast.success(`Request completed: ${response.status}`);

    } catch (error) {
      const duration = Math.round(performance.now() - startTime);
      
      responseStatus.textContent = 'Error';
      responseStatus.className = 'status error';
      responseTime.textContent = `${duration}ms`;
      responseContent.textContent = JSON.stringify({
        error: error.message,
        type: error.name,
      }, null, 2);

      Toast.error(`Request failed: ${error.message}`);
    }
  }

  copyResponse() {
    const content = document.getElementById('response-content').textContent;
    navigator.clipboard.writeText(content).then(() => {
      Toast.success('Response copied to clipboard');
    }).catch(() => {
      Toast.error('Failed to copy response');
    });
  }

  clearResponse() {
    document.getElementById('response-content').textContent = '{\n  "message": "Response cleared"\n}';
    document.getElementById('response-status').textContent = '--';
    document.getElementById('response-status').className = 'status';
    document.getElementById('response-time').textContent = '--';
  }

  addToHistory(entry) {
    this.history.unshift(entry);
    if (this.history.length > this.maxHistory) {
      this.history.pop();
    }
    this.saveHistory();
    this.renderHistory();
  }

  renderHistory() {
    const list = document.getElementById('history-list');
    
    if (this.history.length === 0) {
      list.innerHTML = '<div class="empty-state">No requests yet</div>';
      return;
    }

    list.innerHTML = this.history.map((entry, index) => `
      <div class="history-item" data-index="${index}">
        <span class="method method-${entry.method.toLowerCase()}">${entry.method}</span>
        <span class="endpoint">${entry.endpoint}</span>
        <span class="status ${entry.status < 400 ? 'success' : 'error'}">${entry.status}</span>
        <span class="time">${entry.duration}ms</span>
        <button class="btn-icon btn-replay" title="Replay">
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
        </button>
      </div>
    `).join('');

    // Bind replay buttons
    list.querySelectorAll('.btn-replay').forEach((btn, index) => {
      btn.addEventListener('click', () => this.replayRequest(index));
    });
  }

  replayRequest(index) {
    const entry = this.history[index];
    if (!entry) return;

    document.getElementById('method-select').value = entry.method;
    document.getElementById('endpoint-select').value = entry.endpoint;
    this.toggleBodyInput();
    this.sendRequest();
  }

  saveHistory() {
    try {
      localStorage.setItem('api_explorer_history', JSON.stringify(this.history));
    } catch (e) {
      console.warn('[APIExplorer] Could not save history:', e);
    }
  }

  loadHistory() {
    try {
      const saved = localStorage.getItem('api_explorer_history');
      if (saved) {
        this.history = JSON.parse(saved);
        this.renderHistory();
      }
    } catch (e) {
      console.warn('[APIExplorer] Could not load history:', e);
    }
  }

  clearHistory() {
    this.history = [];
    this.saveHistory();
    this.renderHistory();
    Toast.info('History cleared');
  }
}

// Initialize page
const page = new APIExplorerPage();

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => page.init());
} else {
  page.init();
}
