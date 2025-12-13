/**
 * Tab Navigation Manager
 * Crypto Monitor HF - Enterprise Edition
 */

class TabManager {
    constructor() {
        this.currentTab = 'market';
        this.tabs = {};
        this.onChangeCallbacks = [];
    }

    /**
     * Initialize tab system
     */
    init() {
        // Register all tabs
        this.registerTab('market', '📊', 'Market', this.loadMarketTab.bind(this));
        this.registerTab('api-monitor', '📡', 'API Monitor', this.loadAPIMonitorTab.bind(this));
        this.registerTab('advanced', '⚡', 'Advanced', this.loadAdvancedTab.bind(this));
        this.registerTab('admin', '⚙️', 'Admin', this.loadAdminTab.bind(this));
        this.registerTab('huggingface', '🤗', 'HuggingFace', this.loadHuggingFaceTab.bind(this));
        this.registerTab('pools', '🔄', 'Pools', this.loadPoolsTab.bind(this));
        this.registerTab('providers', '🧩', 'Providers', this.loadProvidersTab.bind(this));
        this.registerTab('logs', '📝', 'Logs', this.loadLogsTab.bind(this));
        this.registerTab('reports', '📊', 'Reports', this.loadReportsTab.bind(this));

        // Set up event listeners
        this.setupEventListeners();

        // Load initial tab from URL hash or default
        const hash = window.location.hash.slice(1);
        const initialTab = hash && this.tabs[hash] ? hash : 'market';
        this.switchTab(initialTab);

        // Handle browser back/forward
        window.addEventListener('popstate', () => {
            const tabId = window.location.hash.slice(1) || 'market';
            this.switchTab(tabId, false);
        });

        console.log('[TabManager] Initialized with', Object.keys(this.tabs).length, 'tabs');
    }

    /**
     * Register a tab
     */
    registerTab(id, icon, label, loadFn) {
        this.tabs[id] = {
            id,
            icon,
            label,
            loadFn,
            loaded: false,
        };
    }

    /**
     * Set up event listeners for tab buttons
     */
    setupEventListeners() {
        // Desktop navigation
        document.querySelectorAll('.nav-tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const tabId = btn.dataset.tab;
                if (tabId && this.tabs[tabId]) {
                    this.switchTab(tabId);
                }
            });

            // Keyboard navigation
            btn.addEventListener('keydown', (e) => {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    const tabId = btn.dataset.tab;
                    if (tabId && this.tabs[tabId]) {
                        this.switchTab(tabId);
                    }
                }
            });
        });

        // Mobile navigation
        document.querySelectorAll('.mobile-nav-tab-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                const tabId = btn.dataset.tab;
                if (tabId && this.tabs[tabId]) {
                    this.switchTab(tabId);
                }
            });
        });
    }

    /**
     * Switch to a different tab
     */
    switchTab(tabId, updateHistory = true) {
        if (!this.tabs[tabId]) {
            console.warn(`[TabManager] Tab ${tabId} not found`);
            return;
        }

        // Check if feature flag disables this tab
        if (window.featureFlagsManager && this.isTabDisabled(tabId)) {
            this.showFeatureDisabledMessage(tabId);
            return;
        }

        console.log(`[TabManager] Switching to tab: ${tabId}`);

        // Update active state on buttons
        document.querySelectorAll('[data-tab]').forEach(btn => {
            if (btn.dataset.tab === tabId) {
                btn.classList.add('active');
                btn.setAttribute('aria-selected', 'true');
            } else {
                btn.classList.remove('active');
                btn.setAttribute('aria-selected', 'false');
            }
        });

        // Hide all tab content
        document.querySelectorAll('.tab-content').forEach(content => {
            content.classList.remove('active');
            content.setAttribute('aria-hidden', 'true');
        });

        // Show current tab content
        const tabContent = document.getElementById(`${tabId}-tab`);
        if (tabContent) {
            tabContent.classList.add('active');
            tabContent.setAttribute('aria-hidden', 'false');
        }

        // Load tab content if not already loaded
        const tab = this.tabs[tabId];
        if (!tab.loaded && tab.loadFn) {
            tab.loadFn();
            tab.loaded = true;
        }

        // Update URL hash
        if (updateHistory) {
            window.location.hash = tabId;
        }

        // Update current tab
        this.currentTab = tabId;

        // Notify listeners
        this.notifyChange(tabId);

        // Announce to screen readers
        this.announceTabChange(tab.label);
    }

    /**
     * Check if tab is disabled by feature flags
     */
    isTabDisabled(tabId) {
        if (!window.featureFlagsManager) return false;

        const flagMap = {
            'market': 'enableMarketOverview',
            'huggingface': 'enableHFIntegration',
            'pools': 'enablePoolManagement',
            'advanced': 'enableAdvancedCharts',
        };

        const flagName = flagMap[tabId];
        if (flagName) {
            return !window.featureFlagsManager.isEnabled(flagName);
        }

        return false;
    }

    /**
     * Show feature disabled message
     */
    showFeatureDisabledMessage(tabId) {
        const tab = this.tabs[tabId];
        alert(`The "${tab.label}" feature is currently disabled. Enable it in Admin > Feature Flags.`);
    }

    /**
     * Announce tab change to screen readers
     */
    announceTabChange(label) {
        const liveRegion = document.getElementById('sr-live-region');
        if (liveRegion) {
            liveRegion.textContent = `Switched to ${label} tab`;
        }
    }

    /**
     * Register change callback
     */
    onChange(callback) {
        this.onChangeCallbacks.push(callback);
    }

    /**
     * Notify change callbacks
     */
    notifyChange(tabId) {
        this.onChangeCallbacks.forEach(callback => {
            try {
                callback(tabId);
            } catch (error) {
                console.error('[TabManager] Error in change callback:', error);
            }
        });
    }

    // ===== Tab Load Functions =====

    async loadMarketTab() {
        console.log('[TabManager] Loading Market tab');
        try {
            const marketData = await window.apiClient.getMarket();
            this.renderMarketData(marketData);
        } catch (error) {
            console.error('[TabManager] Error loading market data:', error);
            this.showError('market-tab', 'Failed to load market data');
        }
    }

    async loadAPIMonitorTab() {
        console.log('[TabManager] Loading API Monitor tab');
        try {
            const providers = await window.apiClient.getProviders();
            this.renderAPIMonitor(providers);
        } catch (error) {
            console.error('[TabManager] Error loading API monitor:', error);
            this.showError('api-monitor-tab', 'Failed to load API monitor data');
        }
    }

    async loadAdvancedTab() {
        console.log('[TabManager] Loading Advanced tab');
        try {
            const stats = await window.apiClient.getStats();
            this.renderAdvanced(stats);
        } catch (error) {
            console.error('[TabManager] Error loading advanced data:', error);
            this.showError('advanced-tab', 'Failed to load advanced data');
        }
    }

    async loadAdminTab() {
        console.log('[TabManager] Loading Admin tab');
        try {
            const flags = await window.apiClient.getFeatureFlags();
            this.renderAdmin(flags);
        } catch (error) {
            console.error('[TabManager] Error loading admin data:', error);
            this.showError('admin-tab', 'Failed to load admin data');
        }
    }

    async loadHuggingFaceTab() {
        console.log('[TabManager] Loading HuggingFace tab');
        try {
            const hfHealth = await window.apiClient.getHFHealth();
            this.renderHuggingFace(hfHealth);
        } catch (error) {
            console.error('[TabManager] Error loading HuggingFace data:', error);
            this.showError('huggingface-tab', 'Failed to load HuggingFace data');
        }
    }

    async loadPoolsTab() {
        console.log('[TabManager] Loading Pools tab');
        try {
            const pools = await window.apiClient.getPools();
            this.renderPools(pools);
        } catch (error) {
            console.error('[TabManager] Error loading pools data:', error);
            this.showError('pools-tab', 'Failed to load pools data');
        }
    }

    async loadProvidersTab() {
        console.log('[TabManager] Loading Providers tab');
        try {
            const providers = await window.apiClient.getProviders();
            this.renderProviders(providers);
        } catch (error) {
            console.error('[TabManager] Error loading providers data:', error);
            this.showError('providers-tab', 'Failed to load providers data');
        }
    }

    async loadLogsTab() {
        console.log('[TabManager] Loading Logs tab');
        try {
            const logs = await window.apiClient.getRecentLogs();
            this.renderLogs(logs);
        } catch (error) {
            console.error('[TabManager] Error loading logs:', error);
            this.showError('logs-tab', 'Failed to load logs');
        }
    }

    async loadReportsTab() {
        console.log('[TabManager] Loading Reports tab');
        try {
            const discoveryReport = await window.apiClient.getDiscoveryReport();
            const modelsReport = await window.apiClient.getModelsReport();
            this.renderReports({ discoveryReport, modelsReport });
        } catch (error) {
            console.error('[TabManager] Error loading reports:', error);
            this.showError('reports-tab', 'Failed to load reports');
        }
    }

    // ===== Render Functions (Delegated to dashboard.js) =====

    renderMarketData(data) {
        if (window.dashboardApp && window.dashboardApp.renderMarketTab) {
            window.dashboardApp.renderMarketTab(data);
        }
    }

    renderAPIMonitor(data) {
        if (window.dashboardApp && window.dashboardApp.renderAPIMonitorTab) {
            window.dashboardApp.renderAPIMonitorTab(data);
        }
    }

    renderAdvanced(data) {
        if (window.dashboardApp && window.dashboardApp.renderAdvancedTab) {
            window.dashboardApp.renderAdvancedTab(data);
        }
    }

    renderAdmin(data) {
        if (window.dashboardApp && window.dashboardApp.renderAdminTab) {
            window.dashboardApp.renderAdminTab(data);
        }
    }

    renderHuggingFace(data) {
        if (window.dashboardApp && window.dashboardApp.renderHuggingFaceTab) {
            window.dashboardApp.renderHuggingFaceTab(data);
        }
    }

    renderPools(data) {
        if (window.dashboardApp && window.dashboardApp.renderPoolsTab) {
            window.dashboardApp.renderPoolsTab(data);
        }
    }

    renderProviders(data) {
        if (window.dashboardApp && window.dashboardApp.renderProvidersTab) {
            window.dashboardApp.renderProvidersTab(data);
        }
    }

    renderLogs(data) {
        if (window.dashboardApp && window.dashboardApp.renderLogsTab) {
            window.dashboardApp.renderLogsTab(data);
        }
    }

    renderReports(data) {
        if (window.dashboardApp && window.dashboardApp.renderReportsTab) {
            window.dashboardApp.renderReportsTab(data);
        }
    }

    /**
     * Show error message in tab
     */
    showError(tabId, message) {
        const tabElement = document.getElementById(tabId);
        if (tabElement) {
            const contentArea = tabElement.querySelector('.tab-body') || tabElement;
            contentArea.innerHTML = `
                <div class="alert alert-error">
                    <strong>❌ Error:</strong> ${message}
                </div>
            `;
        }
    }
}

// Create global instance
window.tabManager = new TabManager();

// Auto-initialize on DOMContentLoaded
document.addEventListener('DOMContentLoaded', () => {
    window.tabManager.init();
});

console.log('[TabManager] Module loaded');
