/**
 * Dashboard Application Controller
 * Crypto Monitor HF - Enterprise Edition
 */

class DashboardApp {
    constructor() {
        this.initialized = false;
        this.charts = {};
        this.refreshIntervals = {};
    }

    /**
     * Initialize dashboard
     */
    async init() {
        if (this.initialized) return;

        console.log('[Dashboard] Initializing...');

        // Wait for dependencies
        await this.waitForDependencies();

        // Set up global error handler
        this.setupErrorHandler();

        // Set up refresh intervals
        this.setupRefreshIntervals();

        this.initialized = true;
        console.log('[Dashboard] Initialized successfully');
    }

    /**
     * Wait for required dependencies to load
     */
    async waitForDependencies() {
        const maxWait = 5000;
        const startTime = Date.now();

        while (!window.apiClient || !window.tabManager || !window.themeManager) {
            if (Date.now() - startTime > maxWait) {
                throw new Error('Timeout waiting for dependencies');
            }
            await new Promise(resolve => setTimeout(resolve, 100));
        }
    }

    /**
     * Set up global error handler
     */
    setupErrorHandler() {
        window.addEventListener('error', (event) => {
            console.error('[Dashboard] Global error:', event.error);
        });

        window.addEventListener('unhandledrejection', (event) => {
            console.error('[Dashboard] Unhandled rejection:', event.reason);
        });
    }

    /**
     * Set up automatic refresh intervals
     */
    setupRefreshIntervals() {
        // Refresh market data every 60 seconds
        this.refreshIntervals.market = setInterval(() => {
            if (window.tabManager.currentTab === 'market') {
                window.tabManager.loadMarketTab();
            }
        }, 60000);

        // Refresh API monitor every 30 seconds
        this.refreshIntervals.apiMonitor = setInterval(() => {
            if (window.tabManager.currentTab === 'api-monitor') {
                window.tabManager.loadAPIMonitorTab();
            }
        }, 30000);
    }

    /**
     * Clear all refresh intervals
     */
    clearRefreshIntervals() {
        Object.values(this.refreshIntervals).forEach(interval => {
            clearInterval(interval);
        });
        this.refreshIntervals = {};
    }

    // ===== Tab Rendering Methods =====

    /**
     * Render Market tab
     */
    renderMarketTab(data) {
        const container = document.querySelector('#market-tab .tab-body');
        if (!container) return;

        try {
            let html = '<div class="stats-grid">';

            // Market stats
            if (data.market_cap_usd) {
                html += this.createStatCard('💰', 'Market Cap', this.formatCurrency(data.market_cap_usd), 'primary');
            }
            if (data.total_volume_usd) {
                html += this.createStatCard('📊', '24h Volume', this.formatCurrency(data.total_volume_usd), 'purple');
            }
            if (data.btc_dominance) {
                html += this.createStatCard('₿', 'BTC Dominance', `${data.btc_dominance.toFixed(2)}%`, 'yellow');
            }
            if (data.active_cryptocurrencies) {
                html += this.createStatCard('🪙', 'Active Coins', data.active_cryptocurrencies.toLocaleString(), 'green');
            }

            html += '</div>';

            // Trending coins if available
            if (data.trending && data.trending.length > 0) {
                html += '<div class="card"><div class="card-header"><h3 class="card-title">🔥 Trending Coins</h3></div><div class="card-body">';
                html += this.renderTrendingCoins(data.trending);
                html += '</div></div>';
            }

            container.innerHTML = html;

        } catch (error) {
            console.error('[Dashboard] Error rendering market tab:', error);
            this.showError(container, 'Failed to render market data');
        }
    }

    /**
     * Render API Monitor tab
     */
    renderAPIMonitorTab(data) {
        const container = document.querySelector('#api-monitor-tab .tab-body');
        if (!container) return;

        try {
            const providers = data.providers || data || [];

            let html = '<div class="card"><div class="card-header"><h3 class="card-title">📡 API Providers Status</h3></div><div class="card-body">';

            if (providers.length === 0) {
                html += this.createEmptyState('No providers configured', 'Add providers in the Providers tab');
            } else {
                html += '<div class="table-container table-responsive"><table class="table"><thead><tr>';
                html += '<th>Provider</th><th>Status</th><th>Category</th><th>Health</th><th>Route</th><th>Actions</th>';
                html += '</tr></thead><tbody>';

                providers.forEach(provider => {
                    const status = provider.status || 'unknown';
                    const health = provider.health_status || provider.health || 'unknown';
                    const route = provider.last_route || provider.route || 'direct';
                    const category = provider.category || 'general';

                    html += '<tr>';
                    html += `<td data-label="Provider"><strong>${provider.name || provider.id}</strong></td>`;
                    html += `<td data-label="Status">${this.createStatusBadge(status)}</td>`;
                    html += `<td data-label="Category"><span class="badge badge-primary">${category}</span></td>`;
                    html += `<td data-label="Health">${this.createHealthIndicator(health)}</td>`;
                    html += `<td data-label="Route">${this.createRouteBadge(route, provider.proxy_enabled)}</td>`;
                    html += `<td data-label="Actions"><button class="btn btn-sm btn-secondary" onclick="window.dashboardApp.checkProviderHealth('${provider.id}')">Check</button></td>`;
                    html += '</tr>';
                });

                html += '</tbody></table></div>';
            }

            html += '</div></div>';
            container.innerHTML = html;

        } catch (error) {
            console.error('[Dashboard] Error rendering API monitor tab:', error);
            this.showError(container, 'Failed to render API monitor data');
        }
    }

    /**
     * Render Providers tab
     */
    renderProvidersTab(data) {
        const container = document.querySelector('#providers-tab .tab-body');
        if (!container) return;

        try {
            const providers = data.providers || data || [];

            let html = '<div class="cards-grid">';

            if (providers.length === 0) {
                html += this.createEmptyState('No providers found', 'Configure providers to monitor APIs');
            } else {
                providers.forEach(provider => {
                    html += this.createProviderCard(provider);
                });
            }

            html += '</div>';
            container.innerHTML = html;

        } catch (error) {
            console.error('[Dashboard] Error rendering providers tab:', error);
            this.showError(container, 'Failed to render providers');
        }
    }

    /**
     * Render Pools tab
     */
    renderPoolsTab(data) {
        const container = document.querySelector('#pools-tab .tab-body');
        if (!container) return;

        try {
            const pools = data.pools || data || [];

            let html = '<div class="tab-actions"><button class="btn btn-primary" onclick="window.dashboardApp.createPool()">+ Create Pool</button></div>';

            html += '<div class="cards-grid">';

            if (pools.length === 0) {
                html += this.createEmptyState('No pools configured', 'Create a pool to manage provider groups');
            } else {
                pools.forEach(pool => {
                    html += this.createPoolCard(pool);
                });
            }

            html += '</div>';
            container.innerHTML = html;

        } catch (error) {
            console.error('[Dashboard] Error rendering pools tab:', error);
            this.showError(container, 'Failed to render pools');
        }
    }

    /**
     * Render Logs tab
     */
    renderLogsTab(data) {
        const container = document.querySelector('#logs-tab .tab-body');
        if (!container) return;

        try {
            const logs = data.logs || data || [];

            let html = '<div class="card"><div class="card-header">';
            html += '<h3 class="card-title">📝 Recent Logs</h3>';
            html += '<button class="btn btn-sm btn-danger" onclick="window.dashboardApp.clearLogs()">Clear All</button>';
            html += '</div><div class="card-body">';

            if (logs.length === 0) {
                html += this.createEmptyState('No logs available', 'Logs will appear here as the system runs');
            } else {
                html += '<div class="logs-container">';
                logs.forEach(log => {
                    const level = log.level || 'info';
                    const timestamp = log.timestamp ? new Date(log.timestamp).toLocaleString() : '';
                    const message = log.message || '';

                    html += `<div class="log-entry log-${level}">`;
                    html += `<span class="log-timestamp">${timestamp}</span>`;
                    html += `<span class="badge badge-${this.getLogLevelClass(level)}">${level.toUpperCase()}</span>`;
                    html += `<span class="log-message">${this.escapeHtml(message)}</span>`;
                    html += `</div>`;
                });
                html += '</div>';
            }

            html += '</div></div>';
            container.innerHTML = html;

        } catch (error) {
            console.error('[Dashboard] Error rendering logs tab:', error);
            this.showError(container, 'Failed to render logs');
        }
    }

    /**
     * Render HuggingFace tab
     */
    renderHuggingFaceTab(data) {
        const container = document.querySelector('#huggingface-tab .tab-body');
        if (!container) return;

        try {
            let html = '<div class="card"><div class="card-header"><h3 class="card-title">🤗 HuggingFace Integration</h3></div><div class="card-body">';

            if (data.status === 'available' || data.available) {
                html += '<div class="alert alert-success">✅ HuggingFace API is available</div>';
                html += `<p>Models loaded: ${data.models_count || 0}</p>`;
                html += '<button class="btn btn-primary" onclick="window.dashboardApp.runSentiment()">Run Sentiment Analysis</button>';
            } else {
                html += '<div class="alert alert-warning">⚠️ HuggingFace API is not available</div>';
                if (data.error) {
                    html += `<p class="text-secondary">${this.escapeHtml(data.error)}</p>`;
                }
            }

            html += '</div></div>';
            container.innerHTML = html;

        } catch (error) {
            console.error('[Dashboard] Error rendering HuggingFace tab:', error);
            this.showError(container, 'Failed to render HuggingFace data');
        }
    }

    /**
     * Render Reports tab
     */
    renderReportsTab(data) {
        const container = document.querySelector('#reports-tab .tab-body');
        if (!container) return;

        try {
            let html = '';

            // Discovery Report
            if (data.discoveryReport) {
                html += this.renderDiscoveryReport(data.discoveryReport);
            }

            // Models Report
            if (data.modelsReport) {
                html += this.renderModelsReport(data.modelsReport);
            }

            container.innerHTML = html || this.createEmptyState('No reports available', 'Reports will appear here when data is available');

        } catch (error) {
            console.error('[Dashboard] Error rendering reports tab:', error);
            this.showError(container, 'Failed to render reports');
        }
    }

    /**
     * Render Admin tab
     */
    renderAdminTab(data) {
        const container = document.querySelector('#admin-tab .tab-body');
        if (!container) return;

        try {
            let html = '<div class="card"><div class="card-header"><h3 class="card-title">⚙️ Feature Flags</h3></div><div class="card-body">';
            html += '<div id="feature-flags-container"></div>';
            html += '</div></div>';

            container.innerHTML = html;

            // Render feature flags using the existing manager
            if (window.featureFlagsManager) {
                window.featureFlagsManager.renderUI('feature-flags-container');
            }

        } catch (error) {
            console.error('[Dashboard] Error rendering admin tab:', error);
            this.showError(container, 'Failed to render admin panel');
        }
    }

    /**
     * Render Advanced tab
     */
    renderAdvancedTab(data) {
        const container = document.querySelector('#advanced-tab .tab-body');
        if (!container) return;

        try {
            let html = '<div class="card"><div class="card-header"><h3 class="card-title">⚡ System Statistics</h3></div><div class="card-body">';
            html += '<pre>' + JSON.stringify(data, null, 2) + '</pre>';
            html += '</div></div>';

            container.innerHTML = html;

        } catch (error) {
            console.error('[Dashboard] Error rendering advanced tab:', error);
            this.showError(container, 'Failed to render advanced data');
        }
    }

    // ===== Helper Methods =====

    createStatCard(icon, label, value, variant = 'primary') {
        return `
            <div class="stat-card">
                <div class="stat-icon">${icon}</div>
                <div class="stat-value">${value}</div>
                <div class="stat-label">${label}</div>
            </div>
        `;
    }

    createStatusBadge(status) {
        const statusMap = {
            'online': 'success',
            'offline': 'danger',
            'degraded': 'warning',
            'unknown': 'secondary'
        };
        const badgeClass = statusMap[status] || 'secondary';
        return `<span class="badge badge-${badgeClass}">${status}</span>`;
    }

    createHealthIndicator(health) {
        const healthMap = {
            'healthy': { icon: '✅', class: 'provider-health-online' },
            'degraded': { icon: '⚠️', class: 'provider-health-degraded' },
            'unhealthy': { icon: '❌', class: 'provider-health-offline' },
            'unknown': { icon: '❓', class: '' }
        };
        const indicator = healthMap[health] || healthMap.unknown;
        return `<span class="provider-status ${indicator.class}">${indicator.icon} ${health}</span>`;
    }

    createRouteBadge(route, proxyEnabled) {
        if (proxyEnabled || route === 'proxy') {
            return '<span class="proxy-indicator">🔀 Proxy</span>';
        }
        return '<span class="badge badge-primary">Direct</span>';
    }

    createProviderCard(provider) {
        const status = provider.status || 'unknown';
        const health = provider.health_status || provider.health || 'unknown';

        return `
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">${provider.name || provider.id}</h3>
                    ${this.createStatusBadge(status)}
                </div>
                <div class="card-body">
                    <p><strong>Category:</strong> ${provider.category || 'N/A'}</p>
                    <p><strong>Health:</strong> ${this.createHealthIndicator(health)}</p>
                    <p><strong>Endpoint:</strong> <code>${provider.endpoint || provider.url || 'N/A'}</code></p>
                </div>
            </div>
        `;
    }

    createPoolCard(pool) {
        const members = pool.members || [];
        return `
            <div class="card">
                <div class="card-header">
                    <h3 class="card-title">${pool.name || pool.id}</h3>
                    <span class="badge badge-primary">${members.length} members</span>
                </div>
                <div class="card-body">
                    <p><strong>Strategy:</strong> ${pool.strategy || 'round-robin'}</p>
                    <p><strong>Members:</strong> ${members.join(', ') || 'None'}</p>
                    <button class="btn btn-sm btn-secondary" onclick="window.dashboardApp.rotatePool('${pool.id}')">Rotate</button>
                </div>
            </div>
        `;
    }

    createEmptyState(title, description) {
        return `
            <div class="empty-state">
                <div class="empty-state-icon">📭</div>
                <div class="empty-state-title">${title}</div>
                <div class="empty-state-description">${description}</div>
            </div>
        `;
    }

    renderTrendingCoins(coins) {
        let html = '<div class="trending-coins">';
        coins.slice(0, 5).forEach((coin, index) => {
            html += `<div class="trending-coin"><span class="rank">${index + 1}</span> ${coin.name || coin.symbol}</div>`;
        });
        html += '</div>';
        return html;
    }

    renderDiscoveryReport(report) {
        return `
            <div class="card">
                <div class="card-header"><h3 class="card-title">🔍 Discovery Report</h3></div>
                <div class="card-body">
                    <p><strong>Enabled:</strong> ${report.enabled ? '✅ Yes' : '❌ No'}</p>
                    <p><strong>Last Run:</strong> ${report.last_run ? new Date(report.last_run.started_at).toLocaleString() : 'Never'}</p>
                </div>
            </div>
        `;
    }

    renderModelsReport(report) {
        return `
            <div class="card">
                <div class="card-header"><h3 class="card-title">🤖 Models Report</h3></div>
                <div class="card-body">
                    <p><strong>Total Models:</strong> ${report.total_models || 0}</p>
                    <p><strong>Available:</strong> ${report.available || 0}</p>
                    <p><strong>Errors:</strong> ${report.errors || 0}</p>
                </div>
            </div>
        `;
    }

    showError(container, message) {
        container.innerHTML = `<div class="alert alert-error">❌ ${message}</div>`;
    }

    formatCurrency(value) {
        return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', notation: 'compact' }).format(value);
    }

    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }

    getLogLevelClass(level) {
        const map = { error: 'danger', warning: 'warning', info: 'primary', debug: 'secondary' };
        return map[level] || 'secondary';
    }

    // ===== Action Handlers =====

    async checkProviderHealth(providerId) {
        try {
            const result = await window.apiClient.checkProviderHealth(providerId);
            alert(`Provider health check result: ${JSON.stringify(result)}`);
        } catch (error) {
            alert(`Failed to check provider health: ${error.message}`);
        }
    }

    async clearLogs() {
        if (confirm('Clear all logs?')) {
            try {
                await window.apiClient.clearLogs();
                window.tabManager.loadLogsTab();
            } catch (error) {
                alert(`Failed to clear logs: ${error.message}`);
            }
        }
    }

    async runSentiment() {
        try {
            const result = await window.apiClient.runHFSentiment({ text: 'Bitcoin is going to the moon!' });
            alert(`Sentiment result: ${JSON.stringify(result)}`);
        } catch (error) {
            alert(`Failed to run sentiment: ${error.message}`);
        }
    }

    async rotatePool(poolId) {
        try {
            await window.apiClient.rotatePool(poolId);
            window.tabManager.loadPoolsTab();
        } catch (error) {
            alert(`Failed to rotate pool: ${error.message}`);
        }
    }

    createPool() {
        alert('Create pool functionality - to be implemented with a modal form');
    }

    /**
     * Cleanup
     */
    destroy() {
        this.clearRefreshIntervals();
        Object.values(this.charts).forEach(chart => {
            if (chart && chart.destroy) chart.destroy();
        });
        this.charts = {};
    }
}

// Create global instance
window.dashboardApp = new DashboardApp();

// Auto-initialize
document.addEventListener('DOMContentLoaded', () => {
    window.dashboardApp.init();
});

// Cleanup on unload
window.addEventListener('beforeunload', () => {
    window.dashboardApp.destroy();
});

console.log('[Dashboard] Module loaded');
