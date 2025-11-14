/**
 * Crypto Monitor Ultimate Dashboard Controller
 * Enterprise-grade cryptocurrency monitoring dashboard
 */

class UltimateDashboard {
    constructor() {
        this.currentTab = 'market';
        this.wsClient = null;
        this.apiClient = null;
        this.theme = localStorage.getItem('theme') || 'light';
        this.marketData = [];
        this.providerData = [];
        this.charts = {};
        this.refreshIntervals = {};

        this.init();
    }

    async init() {
        console.log('🚀 Initializing Crypto Monitor Ultimate Dashboard');

        // Initialize theme
        this.initTheme();

        // Initialize API client
        this.initAPIClient();

        // Initialize WebSocket
        this.initWebSocket();

        // Initialize navigation
        this.initNavigation();

        // Initialize event listeners
        this.initEventListeners();

        // Initialize tab implementations
        if (window.TabImplementations) {
            this.tabImpl = new TabImplementations(this);
        }

        // Load initial tab content
        await this.loadTabContent(this.currentTab);

        // Start auto-refresh
        this.startAutoRefresh();

        console.log('✅ Dashboard initialized successfully');
    }

    initTheme() {
        if (this.theme === 'dark') {
            document.body.classList.add('dark-mode');
        }
    }

    initAPIClient() {
        // Use existing API client if available, otherwise create basic fetch wrapper
        if (window.APIClient) {
            this.apiClient = new APIClient();
        } else {
            this.apiClient = {
                get: async (endpoint) => {
                    const response = await fetch(endpoint);
                    if (!response.ok) throw new Error(`HTTP ${response.status}`);
                    return await response.json();
                },
                post: async (endpoint, data) => {
                    const response = await fetch(endpoint, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify(data)
                    });
                    if (!response.ok) throw new Error(`HTTP ${response.status}`);
                    return await response.json();
                }
            };
        }
    }

    initWebSocket() {
        const wsProtocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
        const wsUrl = `${wsProtocol}//${window.location.host}/ws`;

        try {
            this.wsClient = new WebSocket(wsUrl);

            this.wsClient.onopen = () => {
                console.log('✅ WebSocket connected');
                this.updateConnectionStatus('online', 'WebSocket Connected');
            };

            this.wsClient.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleWebSocketMessage(data);
                } catch (error) {
                    console.error('WebSocket message parse error:', error);
                }
            };

            this.wsClient.onerror = (error) => {
                console.error('WebSocket error:', error);
                this.updateConnectionStatus('degraded', 'Connection Error');
            };

            this.wsClient.onclose = () => {
                console.log('❌ WebSocket disconnected');
                this.updateConnectionStatus('offline', 'WebSocket Disconnected');

                // Attempt reconnection after 5 seconds
                setTimeout(() => this.initWebSocket(), 5000);
            };
        } catch (error) {
            console.error('WebSocket initialization error:', error);
            this.updateConnectionStatus('offline', 'WebSocket Unavailable');
        }
    }

    handleWebSocketMessage(data) {
        console.log('📨 WebSocket message:', data);

        switch (data.type) {
            case 'market_data':
                this.updateMarketData(data.data);
                break;
            case 'provider_status':
                this.updateProviderStatus(data.data);
                break;
            case 'alert':
                this.showAlert(data.data);
                break;
            default:
                console.log('Unknown WebSocket message type:', data.type);
        }

        // Update last sync time
        this.updateLastSync();
    }

    updateConnectionStatus(status, text) {
        const dotEl = document.getElementById('wsStatusDot');
        const textEl = document.getElementById('wsStatusText');

        if (dotEl) {
            dotEl.className = `status-dot ${status}`;
        }

        if (textEl) {
            textEl.textContent = text;
        }
    }

    updateLastSync() {
        const el = document.getElementById('lastSync');
        if (el) {
            el.textContent = 'Last sync: Just now';
        }
    }

    initNavigation() {
        // Desktop tabs
        const desktopTabs = document.querySelectorAll('.nav-tab');
        desktopTabs.forEach(tab => {
            tab.addEventListener('click', () => {
                const tabName = tab.dataset.tab;
                this.switchTab(tabName);
            });
        });

        // Mobile tabs
        const mobileTabs = document.querySelectorAll('.mobile-nav-btn');
        mobileTabs.forEach(tab => {
            tab.addEventListener('click', () => {
                const tabName = tab.dataset.tab;
                this.switchTab(tabName);
            });
        });
    }

    switchTab(tabName) {
        console.log(`📑 Switching to tab: ${tabName}`);

        // Update current tab
        this.currentTab = tabName;

        // Update active states for desktop tabs
        document.querySelectorAll('.nav-tab').forEach(tab => {
            if (tab.dataset.tab === tabName) {
                tab.classList.add('active');
            } else {
                tab.classList.remove('active');
            }
        });

        // Update active states for mobile tabs
        document.querySelectorAll('.mobile-nav-btn').forEach(tab => {
            if (tab.dataset.tab === tabName) {
                tab.classList.add('active');
            } else {
                tab.classList.remove('active');
            }
        });

        // Show/hide tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            const contentId = content.id.replace('Tab', '');
            if (contentId === tabName) {
                content.classList.add('active');
            } else {
                content.classList.remove('active');
            }
        });

        // Load tab content if not already loaded
        this.loadTabContent(tabName);
    }

    async loadTabContent(tabName) {
        console.log(`📥 Loading content for tab: ${tabName}`);

        switch (tabName) {
            case 'market':
                await this.loadMarketTab();
                break;
            case 'monitor':
                await this.loadMonitorTab();
                break;
            case 'advanced':
                await this.loadAdvancedTab();
                break;
            case 'admin':
                await this.loadAdminTab();
                break;
            case 'huggingface':
                await this.loadHuggingFaceTab();
                break;
            case 'pools':
                await this.loadPoolsTab();
                break;
            case 'providers':
                await this.loadProvidersTab();
                break;
            case 'logs':
                await this.loadLogsTab();
                break;
            case 'reports':
                await this.loadReportsTab();
                break;
            default:
                console.warn(`Unknown tab: ${tabName}`);
        }
    }

    async loadMarketTab() {
        try {
            console.log('📊 Loading market data...');

            // Fetch market data from API
            const data = await this.apiClient.get('/api/market');

            if (data && data.success) {
                this.marketData = data.data || [];
                this.renderMarketTable(this.marketData);
                this.updateMarketStats(data);
            } else {
                throw new Error('Failed to fetch market data');
            }
        } catch (error) {
            console.error('Error loading market tab:', error);
            this.showError('marketTableContainer', 'Failed to load market data. Please try again.');
        }
    }

    updateMarketStats(data) {
        // Update global stats cards
        if (data.global) {
            const { total_market_cap, total_volume, market_cap_change_percentage_24h_usd } = data.global;

            if (total_market_cap) {
                document.getElementById('totalMarketCap').textContent =
                    this.formatCurrency(total_market_cap.usd, true);
            }

            if (total_volume) {
                document.getElementById('totalVolume').textContent =
                    this.formatCurrency(total_volume.usd, true);
            }

            if (market_cap_change_percentage_24h_usd) {
                const changeEl = document.getElementById('marketCapChange');
                if (changeEl) {
                    changeEl.textContent = `${market_cap_change_percentage_24h_usd > 0 ? '+' : ''}${market_cap_change_percentage_24h_usd.toFixed(2)}%`;
                }
            }
        }
    }

    renderMarketTable(data) {
        const container = document.getElementById('marketTableContainer');
        if (!container) return;

        if (!data || data.length === 0) {
            container.innerHTML = `
                <div style="text-align: center; padding: var(--space-3xl);">
                    <p style="color: var(--color-text-secondary);">No market data available</p>
                </div>
            `;
            return;
        }

        const tableHTML = `
            <table class="data-table">
                <thead>
                    <tr>
                        <th>#</th>
                        <th>Coin</th>
                        <th>Price</th>
                        <th>24h Change</th>
                        <th>Market Cap</th>
                        <th>Volume (24h)</th>
                        <th>7d Trend</th>
                    </tr>
                </thead>
                <tbody>
                    ${data.slice(0, 50).map(coin => this.renderCoinRow(coin)).join('')}
                </tbody>
            </table>
        `;

        container.innerHTML = tableHTML;
    }

    renderCoinRow(coin) {
        const priceChange = coin.price_change_percentage_24h || 0;
        const changeClass = priceChange >= 0 ? 'positive' : 'negative';
        const changeSymbol = priceChange >= 0 ? '↑' : '↓';

        return `
            <tr>
                <td>${coin.market_cap_rank || '-'}</td>
                <td>
                    <div style="display: flex; align-items: center; gap: 8px;">
                        ${coin.image ? `<img src="${coin.image}" alt="${coin.name}" style="width: 24px; height: 24px; border-radius: 50%;">` : ''}
                        <div>
                            <div style="font-weight: 600;">${coin.name}</div>
                            <div style="font-size: 12px; color: var(--color-text-secondary); text-transform: uppercase;">${coin.symbol}</div>
                        </div>
                    </div>
                </td>
                <td style="font-weight: 600;">${this.formatCurrency(coin.current_price)}</td>
                <td>
                    <span class="stat-change ${changeClass}">
                        ${changeSymbol} ${Math.abs(priceChange).toFixed(2)}%
                    </span>
                </td>
                <td>${this.formatCurrency(coin.market_cap, true)}</td>
                <td>${this.formatCurrency(coin.total_volume, true)}</td>
                <td>
                    <canvas id="sparkline-${coin.id}" width="80" height="30"></canvas>
                </td>
            </tr>
        `;
    }

    async loadMonitorTab() {
        try {
            console.log('🔍 Loading provider monitor data...');

            const data = await this.apiClient.get('/api/providers/stats');

            if (data) {
                this.providerData = data.providers || [];
                this.renderMonitorDashboard(data);
            }
        } catch (error) {
            console.error('Error loading monitor tab:', error);
            this.showError('monitorContent', 'Failed to load provider data. Please try again.');
        }
    }

    renderMonitorDashboard(data) {
        const container = document.getElementById('monitorContent');
        if (!container) return;

        const stats = data.summary || {};
        const providers = data.providers || [];

        const html = `
            <!-- Summary Cards -->
            <div class="stats-grid">
                <div class="card stat-card glass-card">
                    <div class="stat-card-header">
                        <span class="stat-label">Total Providers</span>
                        <div class="stat-icon">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="white" stroke="white" stroke-width="2">
                                <path d="M17 21v-2a4 4 0 0 0-4-4H5a4 4 0 0 0-4 4v2"></path>
                                <circle cx="9" cy="7" r="4"></circle>
                                <path d="M23 21v-2a4 4 0 0 0-3-3.87"></path>
                                <path d="M16 3.13a4 4 0 0 1 0 7.75"></path>
                            </svg>
                        </div>
                    </div>
                    <div class="stat-value">${stats.total || providers.length}</div>
                    <div class="stat-change" style="color: var(--color-text-secondary);">
                        <span>Configured providers</span>
                    </div>
                </div>

                <div class="card stat-card glass-card">
                    <div class="stat-card-header">
                        <span class="stat-label">Operational</span>
                        <div class="stat-icon" style="background: linear-gradient(135deg, #10b981, #059669);">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="white" stroke="white" stroke-width="2">
                                <polyline points="20 6 9 17 4 12"></polyline>
                            </svg>
                        </div>
                    </div>
                    <div class="stat-value">${stats.operational || 0}</div>
                    <div class="stat-change positive">
                        <span>${stats.uptime_percentage || 0}% uptime</span>
                    </div>
                </div>

                <div class="card stat-card glass-card">
                    <div class="stat-card-header">
                        <span class="stat-label">Degraded</span>
                        <div class="stat-icon" style="background: linear-gradient(135deg, #f59e0b, #d97706);">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="white" stroke="white" stroke-width="2">
                                <path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path>
                                <line x1="12" y1="9" x2="12" y2="13"></line>
                                <line x1="12" y1="17" x2="12.01" y2="17"></line>
                            </svg>
                        </div>
                    </div>
                    <div class="stat-value">${stats.degraded || 0}</div>
                    <div class="stat-change" style="color: var(--color-warning);">
                        <span>Performance issues</span>
                    </div>
                </div>

                <div class="card stat-card glass-card">
                    <div class="stat-card-header">
                        <span class="stat-label">Offline</span>
                        <div class="stat-icon" style="background: linear-gradient(135deg, #ef4444, #dc2626);">
                            <svg width="20" height="20" viewBox="0 0 24 24" fill="white" stroke="white" stroke-width="2">
                                <circle cx="12" cy="12" r="10"></circle>
                                <line x1="15" y1="9" x2="9" y2="15"></line>
                                <line x1="9" y1="9" x2="15" y2="15"></line>
                            </svg>
                        </div>
                    </div>
                    <div class="stat-value">${stats.offline || 0}</div>
                    <div class="stat-change negative">
                        <span>Unavailable</span>
                    </div>
                </div>
            </div>

            <!-- Provider Grid -->
            <div style="margin-top: var(--space-2xl);">
                <h2 style="font-size: 24px; font-weight: 700; margin-bottom: var(--space-lg);">Provider Status</h2>
                <div class="stats-grid">
                    ${providers.slice(0, 12).map(provider => this.renderProviderCard(provider)).join('')}
                </div>
            </div>
        `;

        container.innerHTML = html;
    }

    renderProviderCard(provider) {
        const status = provider.status || 'unknown';
        const statusClass = status === 'online' ? 'online' : status === 'offline' ? 'offline' : 'degraded';
        const statusColor = status === 'online' ? 'var(--color-success)' : status === 'offline' ? 'var(--color-danger)' : 'var(--color-warning)';

        return `
            <div class="card glass-card" style="position: relative;">
                <div style="position: absolute; top: 12px; right: 12px;">
                    <span class="status-dot ${statusClass}"></span>
                </div>

                <div style="margin-bottom: var(--space-md);">
                    <h3 style="font-size: 16px; font-weight: 600; margin-bottom: 4px;">${provider.name || 'Unknown'}</h3>
                    <div style="font-size: 12px; color: var(--color-text-secondary);">
                        ${provider.category || 'General'}
                    </div>
                </div>

                <div style="display: flex; flex-direction: column; gap: var(--space-sm); font-size: 13px;">
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: var(--color-text-secondary);">Uptime:</span>
                        <span style="font-weight: 600;">${provider.uptime || '0'}%</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: var(--color-text-secondary);">Avg Response:</span>
                        <span style="font-weight: 600;">${provider.avg_response_time || '0'}ms</span>
                    </div>
                    <div style="display: flex; justify-content: space-between;">
                        <span style="color: var(--color-text-secondary);">Status:</span>
                        <span style="font-weight: 600; color: ${statusColor}; text-transform: capitalize;">${status}</span>
                    </div>
                </div>
            </div>
        `;
    }

    async loadAdvancedTab() {
        console.log('⚡ Loading advanced analytics...');
        if (this.tabImpl) {
            await this.tabImpl.renderAdvancedTab();
        }
    }

    async loadAdminTab() {
        console.log('⚙️ Loading admin configuration...');
        if (this.tabImpl) {
            await this.tabImpl.renderAdminTab();
        }
    }

    async loadHuggingFaceTab() {
        console.log('🧠 Loading HuggingFace integration...');
        if (this.tabImpl) {
            await this.tabImpl.renderHuggingFaceTab();
        }
    }

    async loadPoolsTab() {
        console.log('🔄 Loading provider pools...');
        if (this.tabImpl) {
            await this.tabImpl.renderPoolsTab();
        }
    }

    async loadProvidersTab() {
        console.log('🔌 Loading provider details...');
        if (this.tabImpl) {
            await this.tabImpl.renderProvidersTab();
        }
    }

    async loadLogsTab() {
        console.log('📝 Loading system logs...');
        if (this.tabImpl) {
            await this.tabImpl.renderLogsTab();
        }
    }

    async loadReportsTab() {
        console.log('📈 Loading reports...');
        if (this.tabImpl) {
            await this.tabImpl.renderReportsTab();
        }
    }

    initEventListeners() {
        // Theme toggle
        const themeToggle = document.getElementById('themeToggle');
        if (themeToggle) {
            themeToggle.addEventListener('click', () => this.toggleTheme());
        }

        // Refresh market button
        const refreshMarketBtn = document.getElementById('refreshMarketBtn');
        if (refreshMarketBtn) {
            refreshMarketBtn.addEventListener('click', () => this.loadMarketTab());
        }

        // Export market button
        const exportMarketBtn = document.getElementById('exportMarketBtn');
        if (exportMarketBtn) {
            exportMarketBtn.addEventListener('click', () => this.exportMarketData());
        }

        // Global search
        const globalSearch = document.getElementById('globalSearch');
        if (globalSearch) {
            globalSearch.addEventListener('input', (e) => this.handleSearch(e.target.value));
        }
    }

    toggleTheme() {
        this.theme = this.theme === 'light' ? 'dark' : 'light';
        document.body.classList.toggle('dark-mode');
        localStorage.setItem('theme', this.theme);
        console.log(`🎨 Theme switched to: ${this.theme}`);
    }

    handleSearch(query) {
        console.log('🔍 Search query:', query);
        // TODO: Implement search functionality
    }

    exportMarketData() {
        if (!this.marketData || this.marketData.length === 0) {
            this.showToast('No data to export', 'warning');
            return;
        }

        // Convert to CSV
        const headers = ['Rank', 'Name', 'Symbol', 'Price', '24h Change %', 'Market Cap', 'Volume'];
        const rows = this.marketData.map(coin => [
            coin.market_cap_rank || '',
            coin.name || '',
            coin.symbol || '',
            coin.current_price || '',
            coin.price_change_percentage_24h || '',
            coin.market_cap || '',
            coin.total_volume || ''
        ]);

        const csv = [headers, ...rows].map(row => row.join(',')).join('\n');

        // Download
        const blob = new Blob([csv], { type: 'text/csv' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `crypto-market-${Date.now()}.csv`;
        a.click();
        URL.revokeObjectURL(url);

        this.showToast('Market data exported successfully', 'success');
    }

    startAutoRefresh() {
        // Refresh market data every 60 seconds
        this.refreshIntervals.market = setInterval(() => {
            if (this.currentTab === 'market') {
                this.loadMarketTab();
            }
        }, 60000);

        // Refresh provider data every 30 seconds
        this.refreshIntervals.monitor = setInterval(() => {
            if (this.currentTab === 'monitor') {
                this.loadMonitorTab();
            }
        }, 30000);
    }

    showError(containerId, message) {
        const container = document.getElementById(containerId);
        if (container) {
            container.innerHTML = `
                <div style="text-align: center; padding: var(--space-3xl);">
                    <svg width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="var(--color-danger)" stroke-width="2" style="margin: 0 auto;">
                        <circle cx="12" cy="12" r="10"></circle>
                        <line x1="15" y1="9" x2="9" y2="15"></line>
                        <line x1="9" y1="9" x2="15" y2="15"></line>
                    </svg>
                    <p style="margin-top: var(--space-md); color: var(--color-danger); font-weight: 600;">${message}</p>
                    <button class="btn btn-primary" style="margin-top: var(--space-lg);" onclick="location.reload()">
                        Retry
                    </button>
                </div>
            `;
        }
    }

    showToast(message, type = 'info') {
        // Use existing toast system if available
        if (window.showToast) {
            window.showToast(message, type);
        } else {
            console.log(`[${type.toUpperCase()}] ${message}`);
        }
    }

    showAlert(alert) {
        this.showToast(alert.message, alert.severity || 'info');
    }

    updateMarketData(data) {
        console.log('📊 Updating market data from WebSocket');
        this.marketData = data;
        if (this.currentTab === 'market') {
            this.renderMarketTable(data);
        }
    }

    updateProviderStatus(data) {
        console.log('🔍 Updating provider status from WebSocket');
        this.providerData = data;
        if (this.currentTab === 'monitor') {
            this.renderMonitorDashboard({ providers: data });
        }
    }

    formatCurrency(value, compact = false) {
        if (value === null || value === undefined) return '-';

        if (compact) {
            if (value >= 1e12) return `$${(value / 1e12).toFixed(2)}T`;
            if (value >= 1e9) return `$${(value / 1e9).toFixed(2)}B`;
            if (value >= 1e6) return `$${(value / 1e6).toFixed(2)}M`;
            if (value >= 1e3) return `$${(value / 1e3).toFixed(2)}K`;
        }

        return new Intl.NumberFormat('en-US', {
            style: 'currency',
            currency: 'USD',
            minimumFractionDigits: value < 1 ? 4 : 2,
            maximumFractionDigits: value < 1 ? 4 : 2
        }).format(value);
    }

    destroy() {
        // Clean up intervals
        Object.values(this.refreshIntervals).forEach(interval => clearInterval(interval));

        // Close WebSocket
        if (this.wsClient) {
            this.wsClient.close();
        }

        console.log('🧹 Dashboard destroyed');
    }
}

// Initialize dashboard when DOM is ready
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        window.dashboard = new UltimateDashboard();
    });
} else {
    window.dashboard = new UltimateDashboard();
}
