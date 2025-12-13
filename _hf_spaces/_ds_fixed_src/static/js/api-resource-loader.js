/**
 * ═══════════════════════════════════════════════════════════════════
 * API RESOURCE LOADER
 * Loads and manages API resources from api-resources JSON files
 * ═══════════════════════════════════════════════════════════════════
 */

class APIResourceLoader {
    constructor() {
        this.resources = {
            unified: null,
            ultimate: null,
            config: null
        };
        this.cache = new Map();
        this.initialized = false;
        this.failedResources = new Set(); // Track failed resources to prevent infinite retries
        this.initPromise = null; // Prevent multiple simultaneous init calls
    }

    /**
     * Initialize and load all API resource files
     */
    async init() {
        // Return existing promise if already initializing
        if (this.initPromise) {
            return this.initPromise;
        }
        
        // Return immediately if already initialized
        if (this.initialized) {
            return this.resources;
        }

        // Create a promise that will be reused if init is called multiple times
        this.initPromise = (async () => {
            // Don't log initialization - only log if resources are successfully loaded
            try {
                // Load all resource files in parallel (gracefully handle failures silently)
                // Use Promise.allSettled to ensure all complete even if some fail
                const [unified, ultimate, config] = await Promise.allSettled([
                    this.loadResource('/api-resources/crypto_resources_unified_2025-11-11.json').catch(() => null),
                    this.loadResource('/api-resources/ultimate_crypto_pipeline_2025_NZasinich.json').catch(() => null),
                    this.loadResource('/api-resources/api-config-complete__1_.txt')
                        .then(text => {
                            // Handle both text and null responses
                            if (typeof text === 'string' && text.trim()) {
                                return this.parseConfigText(text);
                            }
                            return null;
                        })
                        .catch(() => null)
                ]);

            // Only log if resources were successfully loaded
            if (unified.status === 'fulfilled' && unified.value) {
                this.resources.unified = unified.value;
                const count = this.resources.unified?.registry?.metadata?.total_entries || 0;
                if (count > 0) {
                    console.log('[API Resource Loader] Unified resources loaded:', count, 'entries');
                }
            }
            // Silently skip failures - resources are optional

            if (ultimate.status === 'fulfilled' && ultimate.value) {
                this.resources.ultimate = ultimate.value;
                const count = this.resources.ultimate?.total_sources || 0;
                if (count > 0) {
                    console.log('[API Resource Loader] Ultimate resources loaded:', count, 'sources');
                }
            }
            // Silently skip failures - resources are optional

            if (config.status === 'fulfilled' && config.value) {
                this.resources.config = config.value;
                // Config loaded silently (not critical enough to log)
            }
            // Silently skip failures - resources are optional

                this.initialized = true;
                
                // Only log success if resources were actually loaded
                const stats = this.getStats();
                if (stats.unified.count > 0 || stats.ultimate.count > 0) {
                    console.log('[API Resource Loader] Initialized successfully');
                }
                
                return this.resources;
            } catch (error) {
                // Silently mark as initialized - resources are optional
                this.initialized = true;
                return this.resources;
            } finally {
                // Clear the promise so we can re-init if needed
                this.initPromise = null;
            }
        })();
        
        return this.initPromise;
    }

    /**
     * Load a resource file (tries backend API first, then direct file)
     */
    async loadResource(path) {
        const cacheKey = `resource_${path}`;
        
        // Check cache first
        if (this.cache.has(cacheKey)) {
            return this.cache.get(cacheKey);
        }
        
        // Don't retry if this resource has already failed
        if (this.failedResources && this.failedResources.has(path)) {
            return null;
        }

        try {
            // Try backend API endpoint first
            let endpoint = null;
            if (path.includes('crypto_resources_unified')) {
                endpoint = '/api/resources/unified';
            } else if (path.includes('ultimate_crypto_pipeline')) {
                endpoint = '/api/resources/ultimate';
            }
            
            if (endpoint) {
                try {
                    // Use fetch with timeout and silent error handling
                    // Suppress browser console errors by catching all errors
                    const controller = new AbortController();
                    const timeoutId = setTimeout(() => controller.abort(), 5000);
                    
                    let response = null;
                    try {
                        response = await fetch(endpoint, {
                            signal: controller.signal
                        });
                    } catch (fetchError) {
                        // Completely suppress fetch errors - these are expected if server isn't running
                        // Don't log, don't throw, just return null
                        clearTimeout(timeoutId);
                        return null;
                    }
                    clearTimeout(timeoutId);
                    
                    if (response && response.ok) {
                        try {
                            const result = await response.json();
                            if (result.success && result.data) {
                                this.cache.set(cacheKey, result.data);
                                return result.data;
                            }
                        } catch (jsonError) {
                            // Silently handle JSON parse errors
                            return null;
                        }
                    }
                    // Silently fall through to direct file access if endpoint fails
                    return null;
                } catch (apiError) {
                    // Silently continue - resources are optional
                    return null;
                }
            }
            
            // Fallback to direct file access
            try {
                // Suppress fetch errors for 404s - wrap in try-catch to prevent console errors
                const controller = new AbortController();
                const timeoutId = setTimeout(() => controller.abort(), 5000);
                
                let response = null;
                try {
                    response = await fetch(path, {
                        signal: controller.signal
                    });
                } catch (fetchError) {
                    // Completely suppress browser console errors for optional resources
                    clearTimeout(timeoutId);
                    this.failedResources.add(path);
                    return null;
                }
                clearTimeout(timeoutId);
                if (!response || !response.ok) {
                    // File not found, try alternative paths
                    if (response && response.status === 404) {
                        // Try alternative paths silently
                        const altPaths = [
                            path.replace('/api-resources/', '/static/api-resources/'),
                            path.replace('/api-resources/', 'static/api-resources/'),
                            path.replace('/api-resources/', 'api-resources/')
                        ];
                        
                        for (const altPath of altPaths) {
                            try {
                                const altResponse = await fetch(altPath).catch(() => null);
                                if (altResponse && altResponse.ok) {
                                    // Check if it's a text file
                                    if (path.endsWith('.txt')) {
                                        return await altResponse.text();
                                    }
                                    const data = await altResponse.json();
                                    this.cache.set(cacheKey, data);
                                    return data;
                                }
                            } catch (e) {
                                // Continue to next path
                            }
                        }
                    }
                    // Return null if all paths fail (not critical)
                    return null;
                }

                // Check if it's a text file
                if (path.endsWith('.txt')) {
                    return await response.text();
                }

                const data = await response.json();
                this.cache.set(cacheKey, data);
                return data;
            } catch (fileError) {
                // Last resort: try with /static/ prefix
                if (!path.startsWith('/static/') && !path.startsWith('static/')) {
                    try {
                        const staticPath = path.startsWith('/') ? `/static${path}` : `static/${path}`;
                        const controller2 = new AbortController();
                        const timeoutId2 = setTimeout(() => controller2.abort(), 5000);
                        const response = await fetch(staticPath, {
                            signal: controller2.signal
                        }).catch(() => null);
                        clearTimeout(timeoutId2);
                        
                        if (response && response.ok) {
                            if (path.endsWith('.txt')) {
                                return await response.text();
                            }
                            const data = await response.json();
                            this.cache.set(cacheKey, data);
                            return data;
                        }
                    } catch (staticError) {
                        // Ignore - will return null
                    }
                }
                // Return null instead of throwing (not critical)
                // Mark as failed to prevent future retries
                this.failedResources.add(path);
                return null;
            }
        } catch (error) {
            // Mark as failed to prevent infinite retries
            this.failedResources.add(path);
            
            // Completely silent - resources are optional
            // Don't log anything - these are expected failures
            return null;
        }
    }

    /**
     * Parse config text file
     */
    parseConfigText(text) {
        if (!text) return null;
        
        // Simple parsing - extract key-value pairs
        const config = {};
        const lines = text.split('\n');
        
        for (const line of lines) {
            const match = line.match(/^([^=]+)=(.*)$/);
            if (match) {
                config[match[1].trim()] = match[2].trim();
            }
        }
        
        return config;
    }

    /**
     * Get all market data APIs
     */
    getMarketDataAPIs() {
        const apis = [];
        
        if (this.resources.unified?.registry?.market_data_apis) {
            apis.push(...this.resources.unified.registry.market_data_apis);
        }
        
        if (this.resources.ultimate?.files?.[0]?.content?.resources) {
            const marketAPIs = this.resources.ultimate.files[0].content.resources.filter(
                r => r.category === 'Market Data'
            );
            apis.push(...marketAPIs.map(r => ({
                id: r.name.toLowerCase().replace(/\s+/g, '_'),
                name: r.name,
                base_url: r.url,
                auth: r.key ? { type: 'apiKeyQuery', key: r.key } : { type: 'none' },
                rateLimit: r.rateLimit,
                notes: r.desc
            })));
        }
        
        return apis;
    }

    /**
     * Get all news APIs
     */
    getNewsAPIs() {
        const apis = [];
        
        if (this.resources.unified?.registry?.news_apis) {
            apis.push(...this.resources.unified.registry.news_apis);
        }
        
        if (this.resources.ultimate?.files?.[0]?.content?.resources) {
            const newsAPIs = this.resources.ultimate.files[0].content.resources.filter(
                r => r.category === 'News'
            );
            apis.push(...newsAPIs.map(r => ({
                id: r.name.toLowerCase().replace(/\s+/g, '_'),
                name: r.name,
                base_url: r.url,
                auth: r.key ? { type: 'apiKeyQuery', key: r.key } : { type: 'none' },
                rateLimit: r.rateLimit,
                notes: r.desc
            })));
        }
        
        return apis;
    }

    /**
     * Get all sentiment APIs
     */
    getSentimentAPIs() {
        const apis = [];
        
        if (this.resources.unified?.registry?.sentiment_apis) {
            apis.push(...this.resources.unified.registry.sentiment_apis);
        }
        
        if (this.resources.ultimate?.files?.[0]?.content?.resources) {
            const sentimentAPIs = this.resources.ultimate.files[0].content.resources.filter(
                r => r.category === 'Sentiment'
            );
            apis.push(...sentimentAPIs.map(r => ({
                id: r.name.toLowerCase().replace(/\s+/g, '_'),
                name: r.name,
                base_url: r.url,
                auth: r.key ? { type: 'apiKeyQuery', key: r.key } : { type: 'none' },
                rateLimit: r.rateLimit,
                notes: r.desc
            })));
        }
        
        return apis;
    }

    /**
     * Get all RPC nodes
     */
    getRPCNodes() {
        if (this.resources.unified?.registry?.rpc_nodes) {
            return this.resources.unified.registry.rpc_nodes;
        }
        return [];
    }

    /**
     * Get all block explorers
     */
    getBlockExplorers() {
        if (this.resources.unified?.registry?.block_explorers) {
            return this.resources.unified.registry.block_explorers;
        }
        return [];
    }

    /**
     * Search APIs by keyword
     */
    searchAPIs(keyword) {
        const results = [];
        const lowerKeyword = keyword.toLowerCase();
        
        // Search in unified resources
        if (this.resources.unified?.registry) {
            const categories = ['market_data_apis', 'news_apis', 'sentiment_apis', 'rpc_nodes', 'block_explorers'];
            for (const category of categories) {
                const items = this.resources.unified.registry[category] || [];
                for (const item of items) {
                    if (item.name?.toLowerCase().includes(lowerKeyword) ||
                        item.id?.toLowerCase().includes(lowerKeyword) ||
                        item.base_url?.toLowerCase().includes(lowerKeyword)) {
                        results.push({ ...item, category });
                    }
                }
            }
        }
        
        // Search in ultimate resources
        if (this.resources.ultimate?.files?.[0]?.content?.resources) {
            for (const resource of this.resources.ultimate.files[0].content.resources) {
                if (resource.name?.toLowerCase().includes(lowerKeyword) ||
                    resource.desc?.toLowerCase().includes(lowerKeyword) ||
                    resource.url?.toLowerCase().includes(lowerKeyword)) {
                    results.push({
                        id: resource.name.toLowerCase().replace(/\s+/g, '_'),
                        name: resource.name,
                        base_url: resource.url,
                        category: resource.category,
                        auth: resource.key ? { type: 'apiKeyQuery', key: resource.key } : { type: 'none' },
                        rateLimit: resource.rateLimit,
                        notes: resource.desc
                    });
                }
            }
        }
        
        return results;
    }

    /**
     * Get API by ID
     */
    getAPIById(id) {
        // Search in unified resources
        if (this.resources.unified?.registry) {
            const categories = ['market_data_apis', 'news_apis', 'sentiment_apis', 'rpc_nodes', 'block_explorers'];
            for (const category of categories) {
                const items = this.resources.unified.registry[category] || [];
                const found = items.find(item => item.id === id);
                if (found) return { ...found, category };
            }
        }
        
        // Search in ultimate resources
        if (this.resources.ultimate?.files?.[0]?.content?.resources) {
            const found = this.resources.ultimate.files[0].content.resources.find(
                r => r.name.toLowerCase().replace(/\s+/g, '_') === id
            );
            if (found) {
                return {
                    id: found.name.toLowerCase().replace(/\s+/g, '_'),
                    name: found.name,
                    base_url: found.url,
                    category: found.category,
                    auth: found.key ? { type: 'apiKeyQuery', key: found.key } : { type: 'none' },
                    rateLimit: found.rateLimit,
                    notes: found.desc
                };
            }
        }
        
        return null;
    }

    /**
     * Get statistics
     */
    getStats() {
        return {
            unified: {
                count: this.resources.unified?.registry?.metadata?.total_entries || 0,
                market: this.resources.unified?.registry?.market_data_apis?.length || 0,
                news: this.resources.unified?.registry?.news_apis?.length || 0,
                sentiment: this.resources.unified?.registry?.sentiment_apis?.length || 0,
                rpc: this.resources.unified?.registry?.rpc_nodes?.length || 0,
                explorers: this.resources.unified?.registry?.block_explorers?.length || 0
            },
            ultimate: {
                count: this.resources.ultimate?.total_sources || 0,
                loaded: this.resources.ultimate?.files?.[0]?.content?.resources?.length || 0
            },
            initialized: this.initialized
        };
    }
}

// Initialize global instance
window.apiResourceLoader = new APIResourceLoader();

// Auto-initialize when DOM is ready (only once, prevent infinite retries)
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        if (!window.apiResourceLoader.initialized && !window.apiResourceLoader.initPromise) {
            window.apiResourceLoader.init().then(() => {
                const stats = window.apiResourceLoader.getStats();
                if (stats.unified.count > 0 || stats.ultimate.count > 0) {
                    console.log('[API Resource Loader] Ready!', stats);
                }
            }).catch(() => {
                // Silent fail - resources are optional
            });
        }
    }, { once: true });
} else {
    if (!window.apiResourceLoader.initialized && !window.apiResourceLoader.initPromise) {
        window.apiResourceLoader.init().then(() => {
            const stats = window.apiResourceLoader.getStats();
            if (stats.unified.count > 0 || stats.ultimate.count > 0) {
                console.log('[API Resource Loader] Ready!', stats);
            }
        }).catch(() => {
            // Silent fail - resources are optional
        });
    }
}

