/**
 * ============================================
 * PROVIDER AUTO-DISCOVERY ENGINE
 * Enterprise Edition - Crypto Monitor Ultimate
 * ============================================
 *
 * Automatically discovers and manages 200+ API providers
 * Features:
 * - Auto-loads providers from JSON config
 * - Categorizes providers (market, exchange, defi, news, etc.)
 * - Health checking & status monitoring
 * - Dynamic UI injection
 * - Search & filtering
 * - Rate limit tracking
 */

class ProviderDiscoveryEngine {
    constructor() {
        this.providers = [];
        this.categories = new Map();
        this.healthStatus = new Map();
        this.configPath = '/static/providers_config_ultimate.json'; // Fallback path
        this.initialized = false;
    }

    /**
     * Initialize the discovery engine
     */
    async init() {
        if (this.initialized) return;

        console.log('[Provider Discovery] Initializing...');

        try {
            // Try to load from backend API first
            await this.loadProvidersFromAPI();
        } catch (error) {
            console.warn('[Provider Discovery] API load failed, trying JSON file:', error);
            // Fallback to JSON file
            await this.loadProvidersFromJSON();
        }

        this.categorizeProviders();
        this.startHealthMonitoring();

        this.initialized = true;
        console.log(`[Provider Discovery] Initialized with ${this.providers.length} providers in ${this.categories.size} categories`);
    }

    /**
     * Load providers from backend API
     */
    async loadProvidersFromAPI() {
        try {
            // Try the new /api/providers/config endpoint first
            const response = await fetch('/api/providers/config');
            if (!response.ok) throw new Error(`HTTP ${response.status}`);

            const data = await response.json();
            this.processProviderData(data);
        } catch (error) {
            throw new Error(`Failed to load from API: ${error.message}`);
        }
    }

    /**
     * Load providers from JSON file
     */
    async loadProvidersFromJSON() {
        try {
            const response = await fetch(this.configPath);
            if (!response.ok) throw new Error(`HTTP ${response.status}`);

            const data = await response.json();
            this.processProviderData(data);
        } catch (error) {
            console.error('[Provider Discovery] Failed to load JSON:', error);
            // Use fallback minimal config
            this.useFallbackConfig();
        }
    }

    /**
     * Process provider data from any source
     */
    processProviderData(data) {
        if (!data || !data.providers) {
            throw new Error('Invalid provider data structure');
        }

        // Convert object to array
        this.providers = Object.entries(data.providers).map(([id, provider]) => ({
            id,
            ...provider,
            status: 'unknown',
            lastCheck: null,
            responseTime: null
        }));

        console.log(`[Provider Discovery] Loaded ${this.providers.length} providers`);
    }

    /**
     * Categorize providers
     */
    categorizeProviders() {
        this.categories.clear();

        this.providers.forEach(provider => {
            const category = provider.category || 'other';

            if (!this.categories.has(category)) {
                this.categories.set(category, []);
            }

            this.categories.get(category).push(provider);
        });

        // Sort providers within each category by priority
        this.categories.forEach((providers, category) => {
            providers.sort((a, b) => (b.priority || 0) - (a.priority || 0));
        });

        console.log(`[Provider Discovery] Categorized into: ${Array.from(this.categories.keys()).join(', ')}`);
    }

    /**
     * Get all providers
     */
    getAllProviders() {
        return this.providers;
    }

    /**
     * Get providers by category
     */
    getProvidersByCategory(category) {
        return this.categories.get(category) || [];
    }

    /**
     * Get all categories
     */
    getCategories() {
        return Array.from(this.categories.keys());
    }

    /**
     * Search providers
     */
    searchProviders(query) {
        const lowerQuery = query.toLowerCase();
        return this.providers.filter(provider =>
            provider.name.toLowerCase().includes(lowerQuery) ||
            provider.id.toLowerCase().includes(lowerQuery) ||
            (provider.category || '').toLowerCase().includes(lowerQuery)
        );
    }

    /**
     * Filter providers
     */
    filterProviders(filters = {}) {
        let filtered = [...this.providers];

        if (filters.category) {
            filtered = filtered.filter(p => p.category === filters.category);
        }

        if (filters.free !== undefined) {
            filtered = filtered.filter(p => p.free === filters.free);
        }

        if (filters.requiresAuth !== undefined) {
            filtered = filtered.filter(p => p.requires_auth === filters.requiresAuth);
        }

        if (filters.status) {
            filtered = filtered.filter(p => p.status === filters.status);
        }

        return filtered;
    }

    /**
     * Get provider statistics
     */
    getStats() {
        const total = this.providers.length;
        const free = this.providers.filter(p => p.free).length;
        const paid = total - free;
        const requiresAuth = this.providers.filter(p => p.requires_auth).length;

        const statuses = {
            online: this.providers.filter(p => p.status === 'online').length,
            offline: this.providers.filter(p => p.status === 'offline').length,
            unknown: this.providers.filter(p => p.status === 'unknown').length
        };

        return {
            total,
            free,
            paid,
            requiresAuth,
            categories: this.categories.size,
            statuses
        };
    }

    /**
     * Health check for a single provider
     */
    async checkProviderHealth(providerId) {
        const provider = this.providers.find(p => p.id === providerId);
        if (!provider) return null;

        const startTime = Date.now();

        try {
            // Call backend health check endpoint
            const response = await fetch(`/api/providers/${providerId}/health`, {
                timeout: 5000
            });

            const responseTime = Date.now() - startTime;
            const status = response.ok ? 'online' : 'offline';

            // Update provider status
            provider.status = status;
            provider.lastCheck = new Date();
            provider.responseTime = responseTime;

            this.healthStatus.set(providerId, {
                status,
                lastCheck: provider.lastCheck,
                responseTime
            });

            return { status, responseTime };
        } catch (error) {
            provider.status = 'offline';
            provider.lastCheck = new Date();
            provider.responseTime = null;

            this.healthStatus.set(providerId, {
                status: 'offline',
                lastCheck: provider.lastCheck,
                error: error.message
            });

            return { status: 'offline', error: error.message };
        }
    }

    /**
     * Start health monitoring (periodic checks)
     */
    startHealthMonitoring(interval = 60000) {
        // Check a few high-priority providers periodically
        setInterval(async () => {
            const highPriorityProviders = this.providers
                .filter(p => (p.priority || 0) >= 8)
                .slice(0, 5);

            for (const provider of highPriorityProviders) {
                await this.checkProviderHealth(provider.id);
            }

            console.log('[Provider Discovery] Health check completed');
        }, interval);
    }

    /**
     * Generate provider card HTML
     */
    generateProviderCard(provider) {
        const statusColors = {
            online: 'var(--color-accent-green)',
            offline: 'var(--color-accent-red)',
            unknown: 'var(--color-text-secondary)'
        };

        const statusColor = statusColors[provider.status] || statusColors.unknown;
        const icon = this.getCategoryIcon(provider.category);

        return `
            <div class="provider-card glass-effect" data-provider-id="${provider.id}">
                <div class="provider-card-header">
                    <div class="provider-icon">
                        ${window.getIcon ? window.getIcon(icon, 32) : ''}
                    </div>
                    <div class="provider-info">
                        <h3 class="provider-name">${provider.name}</h3>
                        <span class="provider-category">${this.formatCategory(provider.category)}</span>
                    </div>
                    <div class="provider-status" style="color: ${statusColor}">
                        <span class="status-dot" style="background: ${statusColor}"></span>
                        ${provider.status}
                    </div>
                </div>

                <div class="provider-card-body">
                    <div class="provider-meta">
                        <div class="meta-item">
                            <span class="meta-label">Type:</span>
                            <span class="meta-value">${provider.free ? 'Free' : 'Paid'}</span>
                        </div>
                        <div class="meta-item">
                            <span class="meta-label">Auth:</span>
                            <span class="meta-value">${provider.requires_auth ? 'Required' : 'No'}</span>
                        </div>
                        <div class="meta-item">
                            <span class="meta-label">Priority:</span>
                            <span class="meta-value">${provider.priority || 'N/A'}/10</span>
                        </div>
                    </div>

                    ${this.generateRateLimitInfo(provider)}

                    <div class="provider-actions">
                        <button class="btn-secondary btn-sm" onclick="providerDiscovery.checkProviderHealth('${provider.id}')">
                            ${window.getIcon ? window.getIcon('refresh', 16) : ''} Test
                        </button>
                        ${provider.docs_url ? `
                            <a href="${provider.docs_url}" target="_blank" class="btn-secondary btn-sm">
                                ${window.getIcon ? window.getIcon('fileText', 16) : ''} Docs
                            </a>
                        ` : ''}
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Generate rate limit information
     */
    generateRateLimitInfo(provider) {
        if (!provider.rate_limit) return '';

        const limits = [];
        if (provider.rate_limit.requests_per_second) {
            limits.push(`${provider.rate_limit.requests_per_second}/sec`);
        }
        if (provider.rate_limit.requests_per_minute) {
            limits.push(`${provider.rate_limit.requests_per_minute}/min`);
        }
        if (provider.rate_limit.requests_per_hour) {
            limits.push(`${provider.rate_limit.requests_per_hour}/hr`);
        }
        if (provider.rate_limit.requests_per_day) {
            limits.push(`${provider.rate_limit.requests_per_day}/day`);
        }

        if (limits.length === 0) return '';

        return `
            <div class="provider-rate-limit">
                <span class="rate-limit-label">Rate Limit:</span>
                <span class="rate-limit-value">${limits.join(', ')}</span>
            </div>
        `;
    }

    /**
     * Get icon for category
     */
    getCategoryIcon(category) {
        const icons = {
            market_data: 'barChart',
            exchange: 'activity',
            blockchain_explorer: 'database',
            defi: 'layers',
            sentiment: 'activity',
            news: 'newspaper',
            social: 'users',
            rpc: 'server',
            analytics: 'pieChart',
            whale_tracking: 'trendingUp',
            ml_model: 'brain'
        };

        return icons[category] || 'globe';
    }

    /**
     * Format category name
     */
    formatCategory(category) {
        if (!category) return 'Other';
        return category.split('_').map(word =>
            word.charAt(0).toUpperCase() + word.slice(1)
        ).join(' ');
    }

    /**
     * Render providers in container
     */
    renderProviders(containerId, options = {}) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.error(`Container "${containerId}" not found`);
            return;
        }

        let providers = this.providers;

        // Apply filters
        if (options.category) {
            providers = this.getProvidersByCategory(options.category);
        }
        if (options.search) {
            providers = this.searchProviders(options.search);
        }
        if (options.filters) {
            providers = this.filterProviders(options.filters);
        }

        // Sort
        if (options.sortBy) {
            providers = [...providers].sort((a, b) => {
                if (options.sortBy === 'name') {
                    return a.name.localeCompare(b.name);
                }
                if (options.sortBy === 'priority') {
                    return (b.priority || 0) - (a.priority || 0);
                }
                return 0;
            });
        }

        // Limit
        if (options.limit) {
            providers = providers.slice(0, options.limit);
        }

        // Generate HTML
        const html = providers.map(p => this.generateProviderCard(p)).join('');
        container.innerHTML = html;

        console.log(`[Provider Discovery] Rendered ${providers.length} providers`);
    }

    /**
     * Render category tabs
     */
    renderCategoryTabs(containerId) {
        const container = document.getElementById(containerId);
        if (!container) return;

        const categories = this.getCategories();
        const html = categories.map(category => {
            const count = this.getProvidersByCategory(category).length;
            return `
                <button class="category-tab" data-category="${category}">
                    ${window.getIcon ? window.getIcon(this.getCategoryIcon(category), 20) : ''}
                    <span>${this.formatCategory(category)}</span>
                    <span class="category-count">${count}</span>
                </button>
            `;
        }).join('');

        container.innerHTML = html;
    }

    /**
     * Use fallback minimal config
     */
    useFallbackConfig() {
        console.warn('[Provider Discovery] Using minimal fallback config');
        this.providers = [
            {
                id: 'coingecko',
                name: 'CoinGecko',
                category: 'market_data',
                free: true,
                requires_auth: false,
                priority: 10,
                status: 'unknown'
            },
            {
                id: 'binance',
                name: 'Binance',
                category: 'exchange',
                free: true,
                requires_auth: false,
                priority: 10,
                status: 'unknown'
            }
        ];
    }
}

// Export singleton instance
window.providerDiscovery = new ProviderDiscoveryEngine();

console.log('[Provider Discovery] Engine loaded');
