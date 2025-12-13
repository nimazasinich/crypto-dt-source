/**
 * Feature Flags Manager - Frontend
 * Handles feature flag state and synchronization with backend
 */

class FeatureFlagsManager {
    constructor() {
        this.flags = {};
        this.localStorageKey = 'crypto_monitor_feature_flags';
        this.apiEndpoint = '/api/feature-flags';
        this.listeners = [];
    }

    /**
     * Initialize feature flags from backend and localStorage
     */
    async init() {
        // Load from localStorage first (for offline/fast access)
        this.loadFromLocalStorage();

        // Sync with backend
        await this.syncWithBackend();

        // Set up periodic sync (every 30 seconds)
        setInterval(() => this.syncWithBackend(), 30000);

        return this.flags;
    }

    /**
     * Load flags from localStorage
     */
    loadFromLocalStorage() {
        try {
            const stored = localStorage.getItem(this.localStorageKey);
            if (stored) {
                const data = JSON.parse(stored);
                this.flags = data.flags || {};
                console.log('[FeatureFlags] Loaded from localStorage:', this.flags);
            }
        } catch (error) {
            console.error('[FeatureFlags] Error loading from localStorage:', error);
        }
    }

    /**
     * Save flags to localStorage
     */
    saveToLocalStorage() {
        try {
            const data = {
                flags: this.flags,
                updated_at: new Date().toISOString()
            };
            localStorage.setItem(this.localStorageKey, JSON.stringify(data));
            console.log('[FeatureFlags] Saved to localStorage');
        } catch (error) {
            console.error('[FeatureFlags] Error saving to localStorage:', error);
        }
    }

    /**
     * Sync with backend
     */
    async syncWithBackend() {
        try {
            const response = await fetch(this.apiEndpoint);
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const data = await response.json();
            this.flags = data.flags || {};
            this.saveToLocalStorage();
            this.notifyListeners();

            console.log('[FeatureFlags] Synced with backend:', this.flags);
            return this.flags;
        } catch (error) {
            console.error('[FeatureFlags] Error syncing with backend:', error);
            // Fall back to localStorage
            return this.flags;
        }
    }

    /**
     * Check if a feature is enabled
     */
    isEnabled(flagName) {
        return this.flags[flagName] === true;
    }

    /**
     * Get all flags
     */
    getAll() {
        return { ...this.flags };
    }

    /**
     * Set a single flag
     */
    async setFlag(flagName, value) {
        try {
            const response = await fetch(`${this.apiEndpoint}/${flagName}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    flag_name: flagName,
                    value: value
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const data = await response.json();
            if (data.success) {
                this.flags[flagName] = value;
                this.saveToLocalStorage();
                this.notifyListeners();
                console.log(`[FeatureFlags] Set ${flagName} = ${value}`);
                return true;
            }

            return false;
        } catch (error) {
            console.error(`[FeatureFlags] Error setting flag ${flagName}:`, error);
            return false;
        }
    }

    /**
     * Update multiple flags
     */
    async updateFlags(updates) {
        try {
            const response = await fetch(this.apiEndpoint, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    flags: updates
                })
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const data = await response.json();
            if (data.success) {
                this.flags = data.flags;
                this.saveToLocalStorage();
                this.notifyListeners();
                console.log('[FeatureFlags] Updated flags:', updates);
                return true;
            }

            return false;
        } catch (error) {
            console.error('[FeatureFlags] Error updating flags:', error);
            return false;
        }
    }

    /**
     * Reset to defaults
     */
    async resetToDefaults() {
        try {
            const response = await fetch(`${this.apiEndpoint}/reset`, {
                method: 'POST'
            });

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const data = await response.json();
            if (data.success) {
                this.flags = data.flags;
                this.saveToLocalStorage();
                this.notifyListeners();
                console.log('[FeatureFlags] Reset to defaults');
                return true;
            }

            return false;
        } catch (error) {
            console.error('[FeatureFlags] Error resetting flags:', error);
            return false;
        }
    }

    /**
     * Add change listener
     */
    onChange(callback) {
        this.listeners.push(callback);
        return () => {
            const index = this.listeners.indexOf(callback);
            if (index > -1) {
                this.listeners.splice(index, 1);
            }
        };
    }

    /**
     * Notify all listeners of changes
     */
    notifyListeners() {
        this.listeners.forEach(callback => {
            try {
                callback(this.flags);
            } catch (error) {
                console.error('[FeatureFlags] Error in listener:', error);
            }
        });
    }

    /**
     * Render feature flags UI
     */
    renderUI(containerId) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.error(`[FeatureFlags] Container #${containerId} not found`);
            return;
        }

        const flagDescriptions = {
            enableWhaleTracking: 'Show whale transaction tracking',
            enableMarketOverview: 'Display market overview dashboard',
            enableFearGreedIndex: 'Show Fear & Greed sentiment index',
            enableNewsFeed: 'Display cryptocurrency news feed',
            enableSentimentAnalysis: 'Enable sentiment analysis features',
            enableMlPredictions: 'Show ML-powered price predictions',
            enableProxyAutoMode: 'Automatic proxy for failing APIs',
            enableDefiProtocols: 'Display DeFi protocol data',
            enableTrendingCoins: 'Show trending cryptocurrencies',
            enableGlobalStats: 'Display global market statistics',
            enableProviderRotation: 'Enable provider rotation system',
            enableWebSocketStreaming: 'Real-time WebSocket updates',
            enableDatabaseLogging: 'Log provider health to database',
            enableRealTimeAlerts: 'Show real-time alert notifications',
            enableAdvancedCharts: 'Display advanced charting',
            enableExportFeatures: 'Enable data export functions',
            enableCustomProviders: 'Allow custom API providers',
            enablePoolManagement: 'Enable provider pool management',
            enableHFIntegration: 'HuggingFace model integration'
        };

        let html = '<div class="feature-flags-container">';
        html += '<h3>Feature Flags</h3>';
        html += '<div class="feature-flags-list">';

        Object.keys(this.flags).forEach(flagName => {
            const enabled = this.flags[flagName];
            const description = flagDescriptions[flagName] || flagName;

            html += `
                <div class="feature-flag-item">
                    <label class="feature-flag-label">
                        <input
                            type="checkbox"
                            class="feature-flag-toggle"
                            data-flag="${flagName}"
                            ${enabled ? 'checked' : ''}
                        />
                        <span class="feature-flag-name">${description}</span>
                    </label>
                    <span class="feature-flag-status ${enabled ? 'enabled' : 'disabled'}">
                        ${enabled ? '✓ Enabled' : '✗ Disabled'}
                    </span>
                </div>
            `;
        });

        html += '</div>';
        html += '<div class="feature-flags-actions">';
        html += '<button id="ff-reset-btn" class="btn btn-secondary">Reset to Defaults</button>';
        html += '</div>';
        html += '</div>';

        container.innerHTML = html;

        // Add event listeners
        container.querySelectorAll('.feature-flag-toggle').forEach(toggle => {
            toggle.addEventListener('change', async (e) => {
                const flagName = e.target.dataset.flag;
                const value = e.target.checked;
                await this.setFlag(flagName, value);
            });
        });

        const resetBtn = container.querySelector('#ff-reset-btn');
        if (resetBtn) {
            resetBtn.addEventListener('click', async () => {
                if (confirm('Reset all feature flags to defaults?')) {
                    await this.resetToDefaults();
                    this.renderUI(containerId);
                }
            });
        }

        // Listen for changes and re-render
        this.onChange(() => {
            this.renderUI(containerId);
        });
    }
}

// Global instance
window.featureFlagsManager = new FeatureFlagsManager();

// Auto-initialize on DOMContentLoaded
document.addEventListener('DOMContentLoaded', () => {
    window.featureFlagsManager.init().then(() => {
        console.log('[FeatureFlags] Initialized');
    });
});
