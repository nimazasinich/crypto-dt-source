/**
 * Crypto API Hub Self-Healing Module
 * 
 * This module provides automatic recovery, fallback mechanisms,
 * and health monitoring for the Crypto API Hub dashboard.
 * 
 * Features:
 * - Automatic API health checks
 * - Fallback to alternative endpoints
 * - Retry logic with exponential backoff
 * - Data caching for offline resilience
 * - Automatic error recovery
 */

class SelfHealingAPIHub {
    constructor(config = {}) {
        this.config = {
            retryAttempts: config.retryAttempts || 3,
            retryDelay: config.retryDelay || 1000,
            healthCheckInterval: config.healthCheckInterval || 60000, // 1 minute
            cacheExpiry: config.cacheExpiry || 300000, // 5 minutes
            backendUrl: config.backendUrl || '/api',
            enableAutoRecovery: config.enableAutoRecovery !== false,
            enableCaching: config.enableCaching !== false,
            ...config
        };

        this.cache = new Map();
        this.healthStatus = new Map();
        this.failedEndpoints = new Map();
        this.activeRecoveries = new Set();
        
        if (this.config.enableAutoRecovery) {
            this.startHealthMonitoring();
        }
    }

    /**
     * Start continuous health monitoring
     */
    startHealthMonitoring() {
        console.log('🏥 Self-Healing System: Health monitoring started');
        
        setInterval(() => {
            this.performHealthChecks();
            this.cleanupFailedEndpoints();
            this.cleanupExpiredCache();
        }, this.config.healthCheckInterval);
    }

    /**
     * Perform health checks on all registered endpoints
     */
    async performHealthChecks() {
        const endpoints = this.getRegisteredEndpoints();
        
        for (const endpoint of endpoints) {
            if (!this.activeRecoveries.has(endpoint)) {
                await this.checkEndpointHealth(endpoint);
            }
        }
    }

    /**
     * Check health of a specific endpoint
     */
    async checkEndpointHealth(endpoint) {
        try {
            const response = await this.fetchWithTimeout(endpoint, {
                method: 'HEAD',
                timeout: 5000
            });

            this.healthStatus.set(endpoint, {
                status: response.ok ? 'healthy' : 'degraded',
                lastCheck: Date.now(),
                responseTime: response.headers.get('X-Response-Time') || 'N/A'
            });

            if (response.ok && this.failedEndpoints.has(endpoint)) {
                console.log(`✅ Self-Healing: Endpoint recovered: ${endpoint}`);
                this.failedEndpoints.delete(endpoint);
            }

            return response.ok;
        } catch (error) {
            this.healthStatus.set(endpoint, {
                status: 'unhealthy',
                lastCheck: Date.now(),
                error: error.message
            });

            this.recordFailure(endpoint, error);
            return false;
        }
    }

    /**
     * Fetch with automatic retry and fallback
     */
    async fetchWithRecovery(url, options = {}) {
        const cacheKey = `${options.method || 'GET'}:${url}`;

        // Try cache first if enabled
        if (this.config.enableCaching && options.method === 'GET') {
            const cached = this.getFromCache(cacheKey);
            if (cached) {
                console.log(`💾 Using cached data for: ${url}`);
                return cached;
            }
        }

        // Try primary endpoint with retry
        for (let attempt = 1; attempt <= this.config.retryAttempts; attempt++) {
            try {
                const response = await this.fetchWithTimeout(url, options);
                
                if (response.ok) {
                    const data = await response.json();
                    
                    // Cache successful response
                    if (this.config.enableCaching && options.method === 'GET') {
                        this.setCache(cacheKey, data);
                    }

                    // Clear any failure records
                    if (this.failedEndpoints.has(url)) {
                        console.log(`✅ Self-Healing: Recovery successful for ${url}`);
                        this.failedEndpoints.delete(url);
                    }

                    return { success: true, data, source: 'primary' };
                }

                // If response not OK, try fallback on last attempt
                if (attempt === this.config.retryAttempts) {
                    return await this.tryFallback(url, options);
                }

            } catch (error) {
                console.warn(`⚠️ Attempt ${attempt}/${this.config.retryAttempts} failed for ${url}:`, error.message);

                if (attempt < this.config.retryAttempts) {
                    // Exponential backoff
                    await this.delay(this.config.retryDelay * Math.pow(2, attempt - 1));
                } else {
                    // Last attempt - try fallback
                    return await this.tryFallback(url, options, error);
                }
            }
        }

        // All attempts failed
        return this.handleFailure(url, options);
    }

    /**
     * Try fallback endpoints
     */
    async tryFallback(primaryUrl, options = {}, primaryError = null) {
        console.log(`🔄 Self-Healing: Attempting fallback for ${primaryUrl}`);

        const fallbacks = this.getFallbackEndpoints(primaryUrl);

        for (const fallbackUrl of fallbacks) {
            try {
                const response = await this.fetchWithTimeout(fallbackUrl, options);
                
                if (response.ok) {
                    const data = await response.json();
                    console.log(`✅ Self-Healing: Fallback successful using ${fallbackUrl}`);
                    
                    // Cache fallback data
                    const cacheKey = `${options.method || 'GET'}:${primaryUrl}`;
                    this.setCache(cacheKey, data);

                    return { success: true, data, source: 'fallback', fallbackUrl };
                }
            } catch (error) {
                console.warn(`⚠️ Fallback attempt failed for ${fallbackUrl}:`, error.message);
            }
        }

        // No fallback worked - try backend proxy
        return await this.tryBackendProxy(primaryUrl, options, primaryError);
    }

    /**
     * Try backend proxy as last resort
     */
    async tryBackendProxy(url, options = {}, originalError = null) {
        console.log(`🔄 Self-Healing: Attempting backend proxy for ${url}`);

        try {
            const proxyUrl = `${this.config.backendUrl}/proxy`;
            const response = await fetch(proxyUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    url,
                    method: options.method || 'GET',
                    headers: options.headers || {},
                    body: options.body
                })
            });

            if (response.ok) {
                const data = await response.json();
                console.log(`✅ Self-Healing: Backend proxy successful`);
                return { success: true, data, source: 'backend-proxy' };
            }
        } catch (error) {
            console.error(`❌ Backend proxy failed:`, error);
        }

        // Everything failed - return cached data if available
        const cacheKey = `${options.method || 'GET'}:${url}`;
        const cached = this.getFromCache(cacheKey, true); // Get even expired cache

        if (cached) {
            console.log(`💾 Self-Healing: Using stale cache as last resort`);
            return { success: true, data: cached, source: 'stale-cache', warning: 'Data may be outdated' };
        }

        return this.handleFailure(url, options, originalError);
    }

    /**
     * Handle complete failure
     */
    handleFailure(url, options, error) {
        this.recordFailure(url, error);

        return {
            success: false,
            error: error?.message || 'All recovery attempts failed',
            url,
            timestamp: Date.now(),
            recoveryAttempts: this.config.retryAttempts,
            suggestions: this.getRecoverySuggestions(url)
        };
    }

    /**
     * Record endpoint failure
     */
    recordFailure(endpoint, error) {
        if (!this.failedEndpoints.has(endpoint)) {
            this.failedEndpoints.set(endpoint, {
                count: 0,
                firstFailure: Date.now(),
                errors: []
            });
        }

        const record = this.failedEndpoints.get(endpoint);
        record.count++;
        record.lastFailure = Date.now();
        record.errors.push({
            timestamp: Date.now(),
            message: error?.message || 'Unknown error'
        });

        // Keep only last 10 errors
        if (record.errors.length > 10) {
            record.errors = record.errors.slice(-10);
        }

        console.error(`❌ Endpoint failure recorded: ${endpoint} (${record.count} failures)`);
    }

    /**
     * Get recovery suggestions
     */
    getRecoverySuggestions(url) {
        return [
            'Check your internet connection',
            'Verify API key is valid and not expired',
            'Check if API service is operational',
            'Try again in a few moments',
            'Consider using alternative data sources'
        ];
    }

    /**
     * Get fallback endpoints for a given URL
     */
    getFallbackEndpoints(url) {
        const fallbacks = [];

        // Define fallback mappings
        const fallbackMap = {
            'etherscan.io': ['blockchair.com/ethereum', 'ethplorer.io'],
            'bscscan.com': ['api.bscscan.com'],
            'coingecko.com': ['api.coinpaprika.com', 'api.coincap.io'],
            'coinmarketcap.com': ['api.coingecko.com', 'api.coinpaprika.com'],
            'cryptopanic.com': ['newsapi.org'],
        };

        // Find matching fallbacks
        for (const [primary, alternatives] of Object.entries(fallbackMap)) {
            if (url.includes(primary)) {
                // Transform URL to fallback format
                alternatives.forEach(alt => {
                    const fallbackUrl = this.transformToFallback(url, alt);
                    if (fallbackUrl) fallbacks.push(fallbackUrl);
                });
            }
        }

        return fallbacks;
    }

    /**
     * Transform URL to fallback format
     */
    transformToFallback(originalUrl, fallbackBase) {
        // This is a simplified transformation
        // In production, you'd need more sophisticated URL transformation logic
        return null; // Override in specific implementations
    }

    /**
     * Get registered endpoints
     */
    getRegisteredEndpoints() {
        // This should be populated with actual endpoints from SERVICES object
        return Array.from(this.healthStatus.keys());
    }

    /**
     * Fetch with timeout
     */
    async fetchWithTimeout(url, options = {}) {
        const timeout = options.timeout || 10000;
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), timeout);

        try {
            const response = await fetch(url, {
                ...options,
                signal: controller.signal
            });
            clearTimeout(timeoutId);
            return response;
        } catch (error) {
            clearTimeout(timeoutId);
            if (error.name === 'AbortError') {
                throw new Error(`Request timeout after ${timeout}ms`);
            }
            throw error;
        }
    }

    /**
     * Cache management
     */
    setCache(key, data) {
        this.cache.set(key, {
            data,
            timestamp: Date.now(),
            expiry: Date.now() + this.config.cacheExpiry
        });
    }

    getFromCache(key, allowExpired = false) {
        const cached = this.cache.get(key);
        if (!cached) return null;

        if (allowExpired || cached.expiry > Date.now()) {
            return cached.data;
        }

        return null;
    }

    cleanupExpiredCache() {
        const now = Date.now();
        for (const [key, value] of this.cache.entries()) {
            if (value.expiry < now) {
                this.cache.delete(key);
            }
        }
    }

    /**
     * Clean up old failed endpoints
     */
    cleanupFailedEndpoints() {
        const maxAge = 3600000; // 1 hour
        const now = Date.now();

        for (const [endpoint, record] of this.failedEndpoints.entries()) {
            if (now - record.lastFailure > maxAge) {
                console.log(`🧹 Cleaning up old failure record: ${endpoint}`);
                this.failedEndpoints.delete(endpoint);
            }
        }
    }

    /**
     * Get system health status
     */
    getHealthStatus() {
        const total = this.healthStatus.size;
        const healthy = Array.from(this.healthStatus.values()).filter(s => s.status === 'healthy').length;
        const degraded = Array.from(this.healthStatus.values()).filter(s => s.status === 'degraded').length;
        const unhealthy = Array.from(this.healthStatus.values()).filter(s => s.status === 'unhealthy').length;

        return {
            total,
            healthy,
            degraded,
            unhealthy,
            healthPercentage: total > 0 ? Math.round((healthy / total) * 100) : 0,
            failedEndpoints: this.failedEndpoints.size,
            cacheSize: this.cache.size,
            lastCheck: Date.now()
        };
    }

    /**
     * Utility: Delay
     */
    delay(ms) {
        return new Promise(resolve => setTimeout(resolve, ms));
    }

    /**
     * Manual recovery trigger
     */
    async triggerRecovery(endpoint) {
        console.log(`🔧 Manual recovery triggered for: ${endpoint}`);
        this.activeRecoveries.add(endpoint);

        try {
            const isHealthy = await this.checkEndpointHealth(endpoint);
            if (isHealthy) {
                this.failedEndpoints.delete(endpoint);
                return { success: true, message: 'Endpoint recovered' };
            } else {
                return { success: false, message: 'Endpoint still unhealthy' };
            }
        } finally {
            this.activeRecoveries.delete(endpoint);
        }
    }

    /**
     * Get diagnostics information
     */
    getDiagnostics() {
        return {
            health: this.getHealthStatus(),
            failedEndpoints: Array.from(this.failedEndpoints.entries()).map(([url, record]) => ({
                url,
                ...record
            })),
            cache: {
                size: this.cache.size,
                entries: Array.from(this.cache.keys())
            },
            config: {
                retryAttempts: this.config.retryAttempts,
                retryDelay: this.config.retryDelay,
                healthCheckInterval: this.config.healthCheckInterval,
                cacheExpiry: this.config.cacheExpiry,
                enableAutoRecovery: this.config.enableAutoRecovery,
                enableCaching: this.config.enableCaching
            }
        };
    }
}

// Export for use in other modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = SelfHealingAPIHub;
}
