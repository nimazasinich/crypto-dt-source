/**
 * Diagnostics Page
 * System health monitoring and logs
 */

import { api } from '../../shared/js/core/api-client.js';
import { LayoutManager } from '../../shared/js/core/layout-manager.js';
import { Toast } from '../../shared/js/components/toast.js';

class DiagnosticsPage {
  constructor() {
    this.logType = 'recent';
  }

  async init() {
    try {
      await LayoutManager.injectLayouts();
      LayoutManager.setActiveNav('diagnostics');
      
      this.bindEvents();
      await this.loadAll();
    } catch (error) {
      console.error('[Diagnostics] Init error:', error);
      Toast.error('Failed to initialize diagnostics page');
    }
  }

  bindEvents() {
    document.getElementById('refresh-btn')?.addEventListener('click', () => this.loadAll());
    document.getElementById('health-refresh')?.addEventListener('click', () => this.loadHealth());
    document.getElementById('logs-refresh')?.addEventListener('click', () => this.loadLogs());
    document.getElementById('logs-clear')?.addEventListener('click', () => this.clearLogs());
    
    document.getElementById('log-type')?.addEventListener('change', (e) => {
      this.logType = e.target.value;
      this.loadLogs();
    });
  }

  async loadAll() {
    await Promise.all([
      this.loadHealth(),
      this.loadLogs(),
      this.loadRequests()
    ]);
    this.updateLastUpdate();
  }

  async loadHealth() {
    const container = document.getElementById('health-grid');
    container.innerHTML = '<div class="loading-container"><div class="spinner"></div></div>';

    try {
      const [health, status] = await Promise.all([
        api.getHealth().catch(() => null),
        api.getStatus().catch(() => null)
      ]);

      this.renderHealth(health, status);
    } catch (error) {
      console.error('[Diagnostics] Health error:', error);
      container.innerHTML = `<div class="error-state"><p>Failed to load health data</p></div>`;
    }
  }

  renderHealth(health, status) {
    const container = document.getElementById('health-grid');
    
    const items = [
      {
        label: 'API Status',
        value: health?.status || 'unknown',
        status: health?.status === 'healthy' || health?.status === 'ok' ? 'success' : 'error'
      },
      {
        label: 'Database',
        value: status?.database || health?.database || 'unknown',
        status: (status?.database === 'connected' || health?.database === 'ok') ? 'success' : 'warning'
      },
      {
        label: 'Uptime',
        value: this.formatUptime(health?.uptime || status?.uptime),
        status: 'info'
      },
      {
        label: 'Version',
        value: health?.version || status?.version || 'N/A',
        status: 'info'
      },
      {
        label: 'Memory',
        value: status?.memory_usage ? `${status.memory_usage.toFixed(1)}%` : 'N/A',
        status: status?.memory_usage > 80 ? 'warning' : 'success'
      },
      {
        label: 'CPU',
        value: status?.cpu_usage ? `${status.cpu_usage.toFixed(1)}%` : 'N/A',
        status: status?.cpu_usage > 80 ? 'warning' : 'success'
      }
    ];

    container.innerHTML = items.map(item => `
      <div class="health-card ${item.status}">
        <div class="health-icon">
          ${this.getStatusIcon(item.status)}
        </div>
        <div class="health-info">
          <span class="health-label">${item.label}</span>
          <span class="health-value">${item.value}</span>
        </div>
      </div>
    `).join('');
  }

  getStatusIcon(status) {
    switch (status) {
      case 'success':
        return '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M22 11.08V12a10 10 0 1 1-5.93-9.14"></path><polyline points="22 4 12 14.01 9 11.01"></polyline></svg>';
      case 'warning':
        return '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>';
      case 'error':
        return '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>';
      default:
        return '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>';
    }
  }

  formatUptime(seconds) {
    if (!seconds) return 'N/A';
    const days = Math.floor(seconds / 86400);
    const hours = Math.floor((seconds % 86400) / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    
    if (days > 0) return `${days}d ${hours}h`;
    if (hours > 0) return `${hours}h ${minutes}m`;
    return `${minutes}m`;
  }

  async loadLogs() {
    const container = document.getElementById('logs-container');
    container.innerHTML = '<div class="loading-container"><div class="spinner"></div></div>';

    try {
      const data = this.logType === 'errors' 
        ? await api.getErrorLogs(50)
        : await api.getRecentLogs(50);
      
      this.renderLogs(data.logs || data.entries || []);
    } catch (error) {
      console.error('[Diagnostics] Logs error:', error);
      container.innerHTML = `<div class="error-state"><p>Failed to load logs</p></div>`;
    }
  }

  renderLogs(logs) {
    const container = document.getElementById('logs-container');
    
    if (logs.length === 0) {
      container.innerHTML = `<div class="empty-state"><p>No logs available</p></div>`;
      return;
    }

    container.innerHTML = `
      <div class="logs-list">
        ${logs.map(log => `
          <div class="log-entry ${this.getLogLevel(log)}">
            <span class="log-time">${this.formatTime(log.timestamp || log.time)}</span>
            <span class="log-level">${(log.level || 'INFO').toUpperCase()}</span>
            <span class="log-message">${log.message || log.msg}</span>
            ${log.details || log.extra ? `<pre class="log-details">${JSON.stringify(log.details || log.extra, null, 2)}</pre>` : ''}
          </div>
        `).join('')}
      </div>
    `;
  }

  getLogLevel(log) {
    const level = (log.level || '').toLowerCase();
    if (level.includes('error') || level.includes('critical')) return 'error';
    if (level.includes('warn')) return 'warning';
    if (level.includes('debug')) return 'debug';
    return 'info';
  }

  formatTime(timestamp) {
    if (!timestamp) return '--:--:--';
    const date = new Date(timestamp);
    return date.toLocaleTimeString();
  }

  async loadRequests() {
    const tbody = document.getElementById('requests-tbody');
    
    // Get requests from API client's internal log
    const requests = api.getRequestLogs(20);
    
    if (requests.length === 0) {
      tbody.innerHTML = '<tr><td colspan="5" class="text-center">No requests logged yet</td></tr>';
      return;
    }

    tbody.innerHTML = requests.map(req => `
      <tr>
        <td>${new Date(req.timestamp).toLocaleTimeString()}</td>
        <td><span class="method-badge method-${req.method.toLowerCase()}">${req.method}</span></td>
        <td>${req.endpoint}</td>
        <td><span class="status-badge ${req.status < 400 ? 'success' : 'error'}">${req.status}</span></td>
        <td>${req.duration}ms</td>
      </tr>
    `).join('');
  }

  async clearLogs() {
    if (!confirm('Are you sure you want to clear all logs?')) return;

    try {
      await api.clearLogs();
      Toast.success('Logs cleared');
      this.loadLogs();
    } catch (error) {
      Toast.error('Failed to clear logs');
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
const page = new DiagnosticsPage();

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => page.init());
} else {
  page.init();
}
