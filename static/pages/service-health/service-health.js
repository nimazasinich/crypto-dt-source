/**
 * Service Health Monitor
 * Real-time monitoring dashboard for all API services
 */

import { Toast } from '../../shared/js/components/toast.js';

class ServiceHealthMonitor {
    constructor() {
        this.services = [];
        this.autoRefresh = true;
        this.refreshInterval = null;
        this.refreshDelay = 10000; // 10 seconds
        this.isLoading = false;
    }

    async init() {
        console.log('[HealthMonitor] Initializing...');
        
        this.bindEvents();
        await this.loadServiceHealth();
        this.startAutoRefresh();
        
        console.log('[HealthMonitor] Ready');
    }

    bindEvents() {
        // Refresh button
        const refreshBtn = document.getElementById('refresh-btn');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => {
                this.loadServiceHealth(true);
            });
        }

        // Auto-refresh toggle
        const autoRefreshToggle = document.getElementById('auto-refresh-toggle');
        if (autoRefreshToggle) {
            autoRefreshToggle.addEventListener('change', (e) => {
                this.autoRefresh = e.target.checked;
                if (this.autoRefresh) {
                    this.startAutoRefresh();
                    this.showToast('✅ Auto-refresh enabled', 'success');
                } else {
                    this.stopAutoRefresh();
                    this.showToast('ℹ️ Auto-refresh disabled', 'info');
                }
            });
        }
    }

    async loadServiceHealth(forceRefresh = false) {
        if (this.isLoading && !forceRefresh) {
            console.log('[HealthMonitor] Already loading, skipping...');
            return;
        }

        this.isLoading = true;
        this.showLoading(true);

        try {
            console.log('[HealthMonitor] Fetching service health...');
            
            const response = await fetch('/api/health/monitor', {
                method: 'GET',
                headers: {
                    'Accept': 'application/json',
                },
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const data = await response.json();
            
            console.log('[HealthMonitor] Received data:', data);
            
            this.services = data.services || [];
            this.renderOverallHealth(data);
            this.renderHealthOverview(data);
            this.renderServices(data.services);
            
            if (forceRefresh) {
                this.showToast('✅ Health status updated', 'success');
            }
            
        } catch (error) {
            console.error('[HealthMonitor] Failed to load health data:', error);
            this.showError(error.message);
            this.showToast('❌ Failed to load health data', 'error');
        } finally {
            this.isLoading = false;
            this.showLoading(false);
        }
    }

    renderOverallHealth(data) {
        const healthStatusEl = document.getElementById('health-status');
        const lastUpdateEl = document.getElementById('last-update');
        
        if (!healthStatusEl || !lastUpdateEl) return;

        const healthClass = data.overall_health || 'unknown';
        const healthText = healthClass.toUpperCase();
        
        healthStatusEl.className = `health-status ${healthClass}`;
        healthStatusEl.textContent = healthText;
        
        const timestamp = data.timestamp ? new Date(data.timestamp).toLocaleString() : 'Unknown';
        lastUpdateEl.textContent = `Last checked: ${timestamp}`;
    }

    renderHealthOverview(data) {
        const container = document.getElementById('health-overview');
        if (!container) return;

        const stats = [
            {
                label: 'Total Services',
                value: data.total_services || 0,
                color: '#3b82f6'
            },
            {
                label: 'Online',
                value: data.online || 0,
                color: '#22c55e'
            },
            {
                label: 'Offline',
                value: data.offline || 0,
                color: '#ef4444'
            },
            {
                label: 'Rate Limited',
                value: data.rate_limited || 0,
                color: '#fbbf24'
            },
            {
                label: 'Degraded',
                value: data.degraded || 0,
                color: '#f97316'
            }
        ];

        container.innerHTML = stats.map(stat => `
            <div class="health-stat-card">
                <div class="health-stat-label">${stat.label}</div>
                <div class="health-stat-value" style="color: ${stat.color};">${stat.value}</div>
            </div>
        `).join('');
    }

    renderServices(services) {
        const container = document.getElementById('services-container');
        if (!container) return;

        if (!services || services.length === 0) {
            container.innerHTML = `
                <div style="text-align: center; padding: 3rem; color: var(--text-muted);">
                    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-bottom: 1rem;">
                        <circle cx="12" cy="12" r="10"></circle>
                        <line x1="12" y1="8" x2="12" y2="12"></line>
                        <line x1="12" y1="16" x2="12.01" y2="16"></line>
                    </svg>
                    <h3>No Services Found</h3>
                    <p>Unable to load service information</p>
                </div>
            `;
            return;
        }

        container.innerHTML = services.map(service => this.renderServiceCard(service)).join('');
    }

    renderServiceCard(service) {
        const statusClass = service.status || 'offline';
        const statusText = this.formatStatus(statusClass);
        const iconBg = this.getStatusColor(statusClass);
        
        const responseTime = service.response_time_ms 
            ? `${service.response_time_ms.toFixed(0)}ms` 
            : 'N/A';
        
        const successRate = service.success_rate !== null && service.success_rate !== undefined
            ? `${service.success_rate.toFixed(1)}%`
            : 'N/A';

        const lastError = service.last_error 
            ? `<div style="margin-top: 0.5rem; padding: 0.75rem; background: rgba(239, 68, 68, 0.1); border-radius: 8px; font-size: 0.875rem; color: #ef4444;">
                <strong>Last Error:</strong> ${this.escapeHtml(service.last_error)}
               </div>`
            : '';

        const subServices = service.details && service.details.sub_services && service.details.sub_services.length > 0
            ? `<div class="sub-services">
                ${service.details.sub_services.map(sub => `<span class="sub-service-tag">${sub}</span>`).join('')}
               </div>`
            : '';

        return `
            <div class="service-card">
                <div class="service-icon" style="background: ${iconBg};">
                    ${this.getServiceIcon(service.name)}
                </div>
                <div class="service-info">
                    <div class="service-name">${this.escapeHtml(service.name)}</div>
                    <div class="service-category">${service.details?.category || 'Unknown'}</div>
                    ${subServices}
                    ${lastError}
                </div>
                <div class="service-metrics">
                    <div class="metric">
                        <div class="metric-label">Status</div>
                        <div class="metric-value">
                            <span class="status-badge ${statusClass}">
                                <span class="status-dot ${statusClass}"></span>
                                ${statusText}
                            </span>
                        </div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Response</div>
                        <div class="metric-value">${responseTime}</div>
                    </div>
                    <div class="metric">
                        <div class="metric-label">Success Rate</div>
                        <div class="metric-value">${successRate}</div>
                    </div>
                </div>
            </div>
        `;
    }

    getServiceIcon(name) {
        const icons = {
            'CoinGecko': '🦎',
            'Binance': '🔶',
            'CoinCap': '📊',
            'CryptoCompare': '💹',
            'HuggingFace Space': '🤗',
            'Technical Indicators': '📈',
            'Market Data API': '💰',
            'Etherscan': '⛓️'
        };
        return icons[name] || '🔧';
    }

    getStatusColor(status) {
        const colors = {
            'online': 'rgba(34, 197, 94, 0.2)',
            'offline': 'rgba(239, 68, 68, 0.2)',
            'rate_limited': 'rgba(251, 191, 36, 0.2)',
            'degraded': 'rgba(249, 115, 22, 0.2)'
        };
        return colors[status] || 'rgba(156, 163, 175, 0.2)';
    }

    formatStatus(status) {
        const formats = {
            'online': 'Online',
            'offline': 'Offline',
            'rate_limited': 'Rate Limited',
            'degraded': 'Degraded'
        };
        return formats[status] || 'Unknown';
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    startAutoRefresh() {
        this.stopAutoRefresh();
        
        if (this.autoRefresh) {
            this.refreshInterval = setInterval(() => {
                if (!document.hidden && !this.isLoading) {
                    this.loadServiceHealth();
                }
            }, this.refreshDelay);
            
            console.log('[HealthMonitor] Auto-refresh started');
        }
    }

    stopAutoRefresh() {
        if (this.refreshInterval) {
            clearInterval(this.refreshInterval);
            this.refreshInterval = null;
            console.log('[HealthMonitor] Auto-refresh stopped');
        }
    }

    showLoading(show) {
        const overlay = document.getElementById('loading-overlay');
        const refreshBtn = document.getElementById('refresh-btn');
        
        if (overlay) {
            overlay.style.display = show ? 'flex' : 'none';
        }
        
        if (refreshBtn) {
            refreshBtn.disabled = show;
        }
    }

    showError(message) {
        const container = document.getElementById('services-container');
        if (container) {
            container.innerHTML = `
                <div style="text-align: center; padding: 3rem; color: var(--text-muted);">
                    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="color: #ef4444; margin-bottom: 1rem;">
                        <circle cx="12" cy="12" r="10"></circle>
                        <line x1="15" y1="9" x2="9" y2="15"></line>
                        <line x1="9" y1="9" x2="15" y2="15"></line>
                    </svg>
                    <h3>Failed to Load Health Data</h3>
                    <p>${this.escapeHtml(message)}</p>
                    <button class="btn btn-primary" onclick="location.reload()">Retry</button>
                </div>
            `;
        }
    }

    showToast(message, type = 'info') {
        if (typeof Toast !== 'undefined' && Toast.show) {
            Toast.show(message, type);
        } else {
            console.log(`[Toast ${type}]`, message);
        }
    }

    destroy() {
        this.stopAutoRefresh();
    }
}

// Initialize on page load
let healthMonitorInstance = null;

document.addEventListener('DOMContentLoaded', async () => {
    try {
        healthMonitorInstance = new ServiceHealthMonitor();
        await healthMonitorInstance.init();
    } catch (error) {
        console.error('[HealthMonitor] Fatal error:', error);
    }
});

// Cleanup on unload
window.addEventListener('beforeunload', () => {
    if (healthMonitorInstance) {
        healthMonitorInstance.destroy();
    }
});

export { ServiceHealthMonitor };
export default ServiceHealthMonitor;
