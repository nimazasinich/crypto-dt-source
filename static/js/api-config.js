/**
 * API Configuration for Frontend
 * Connects to Smart Fallback System with 305+ resources
 */

// Auto-detect API base URL
const API_BASE_URL = window.location.origin;

// API Configuration
window.API_CONFIG = {
    // Base URLs
    baseUrl: API_BASE_URL,
    apiUrl: `${API_BASE_URL}/api`,
    smartApiUrl: `${API_BASE_URL}/api/smart`,
    
    // Endpoints - Smart Fallback (NEVER 404)
    endpoints: {
        // Smart endpoints (use these - they never fail)
        smart: {
            market: `${API_BASE_URL}/api/smart/market`,
            news: `${API_BASE_URL}/api/smart/news`,
            sentiment: `${API_BASE_URL}/api/smart/sentiment`,
            whaleAlerts: `${API_BASE_URL}/api/smart/whale-alerts`,
            blockchain: `${API_BASE_URL}/api/smart/blockchain`,
            healthReport: `${API_BASE_URL}/api/smart/health-report`,
            stats: `${API_BASE_URL}/api/smart/stats`,
        },
        
        // Original endpoints (fallback to these if needed)
        market: `${API_BASE_URL}/api/market`,
        marketHistory: `${API_BASE_URL}/api/market/history`,
        sentiment: `${API_BASE_URL}/api/sentiment/analyze`,
        health: `${API_BASE_URL}/api/health`,
        
        // Alpha Vantage
        alphavantage: {
            health: `${API_BASE_URL}/api/alphavantage/health`,
            prices: `${API_BASE_URL}/api/alphavantage/prices`,
            ohlcv: `${API_BASE_URL}/api/alphavantage/ohlcv`,
            marketStatus: `${API_BASE_URL}/api/alphavantage/market-status`,
            cryptoRating: `${API_BASE_URL}/api/alphavantage/crypto-rating`,
            quote: `${API_BASE_URL}/api/alphavantage/quote`,
        },
        
        // Massive.com
        massive: {
            health: `${API_BASE_URL}/api/massive/health`,
            dividends: `${API_BASE_URL}/api/massive/dividends`,
            splits: `${API_BASE_URL}/api/massive/splits`,
            quotes: `${API_BASE_URL}/api/massive/quotes`,
            trades: `${API_BASE_URL}/api/massive/trades`,
            aggregates: `${API_BASE_URL}/api/massive/aggregates`,
            ticker: `${API_BASE_URL}/api/massive/ticker`,
            marketStatus: `${API_BASE_URL}/api/massive/market-status`,
        },
        
        // Documentation
        docs: `${API_BASE_URL}/docs`,
        redoc: `${API_BASE_URL}/redoc`,
    },
    
    // Feature flags
    features: {
        useSmartFallback: true,      // Always use smart fallback
        resourceRotation: true,       // Rotate through resources
        proxySupport: true,           // Use proxy for sanctioned exchanges
        backgroundCollection: true,   // 24/7 data collection
        healthMonitoring: true,       // Monitor resource health
        autoCleanup: true,            // Auto-remove dead resources
    },
    
    // Request configuration
    request: {
        timeout: 30000,               // 30 seconds
        retries: 3,                   // Retry 3 times
        retryDelay: 1000,            // Wait 1 second between retries
    },
    
    // Resource information
    resources: {
        total: '305+',
        categories: {
            marketData: 21,
            blockExplorers: 40,
            news: 15,
            sentiment: 12,
            whaleTracking: 9,
            onchainAnalytics: 13,
            rpcNodes: 24,
            localBackend: 106,
            corsProxies: 7,
        }
    }
};

/**
 * API Client with Smart Fallback
 */
class SmartAPIClient {
    constructor(config = window.API_CONFIG) {
        this.config = config;
        this.authToken = this.getAuthToken();
    }
    
    /**
     * Get auth token from localStorage or environment
     */
    getAuthToken() {
        // Try localStorage first
        let token = localStorage.getItem('hf_token');
        
        // Try sessionStorage
        if (!token) {
            token = sessionStorage.getItem('hf_token');
        }
        
        // Try from URL params (for testing)
        if (!token) {
            const params = new URLSearchParams(window.location.search);
            token = params.get('token');
        }
        
        return token;
    }
    
    /**
     * Set auth token
     */
    setAuthToken(token) {
        this.authToken = token;
        localStorage.setItem('hf_token', token);
    }
    
    /**
     * Get headers for API requests
     */
    getHeaders() {
        const headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        };
        
        if (this.authToken) {
            headers['Authorization'] = `Bearer ${this.authToken}`;
        }
        
        return headers;
    }
    
    /**
     * Fetch with retry logic
     */
    async fetchWithRetry(url, options = {}, retries = 3) {
        for (let i = 0; i < retries; i++) {
            try {
                const response = await fetch(url, {
                    ...options,
                    headers: {
                        ...this.getHeaders(),
                        ...options.headers,
                    },
                    timeout: this.config.request.timeout,
                });
                
                if (!response.ok) {
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                }
                
                return await response.json();
            } catch (error) {
                console.warn(`Attempt ${i + 1} failed:`, error);
                
                if (i === retries - 1) {
                    throw error;
                }
                
                // Wait before retry
                await new Promise(resolve => 
                    setTimeout(resolve, this.config.request.retryDelay * (i + 1))
                );
            }
        }
    }
    
    /**
     * Get market data using smart fallback
     */
    async getMarketData(limit = 100) {
        try {
            // Try smart endpoint first (NEVER fails)
            return await this.fetchWithRetry(
                `${this.config.endpoints.smart.market}?limit=${limit}`
            );
        } catch (error) {
            console.error('Smart market data failed:', error);
            
            // Fallback to original endpoint
            try {
                return await this.fetchWithRetry(
                    `${this.config.endpoints.market}?limit=${limit}`
                );
            } catch (fallbackError) {
                console.error('All market data endpoints failed');
                throw fallbackError;
            }
        }
    }
    
    /**
     * Get news using smart fallback
     */
    async getNews(limit = 20) {
        try {
            return await this.fetchWithRetry(
                `${this.config.endpoints.smart.news}?limit=${limit}`
            );
        } catch (error) {
            console.error('Smart news failed:', error);
            throw error;
        }
    }
    
    /**
     * Get sentiment analysis
     */
    async getSentiment(symbol = null) {
        const url = symbol 
            ? `${this.config.endpoints.smart.sentiment}?symbol=${symbol}`
            : this.config.endpoints.smart.sentiment;
        
        try {
            return await this.fetchWithRetry(url);
        } catch (error) {
            console.error('Smart sentiment failed:', error);
            throw error;
        }
    }
    
    /**
     * Get whale alerts
     */
    async getWhaleAlerts(limit = 20) {
        try {
            return await this.fetchWithRetry(
                `${this.config.endpoints.smart.whaleAlerts}?limit=${limit}`
            );
        } catch (error) {
            console.error('Smart whale alerts failed:', error);
            throw error;
        }
    }
    
    /**
     * Get blockchain data
     */
    async getBlockchainData(chain = 'ethereum') {
        try {
            return await this.fetchWithRetry(
                `${this.config.endpoints.smart.blockchain}/${chain}`
            );
        } catch (error) {
            console.error('Smart blockchain data failed:', error);
            throw error;
        }
    }
    
    /**
     * Get health report
     */
    async getHealthReport() {
        try {
            return await this.fetchWithRetry(
                this.config.endpoints.smart.healthReport
            );
        } catch (error) {
            console.error('Health report failed:', error);
            throw error;
        }
    }
    
    /**
     * Get system statistics
     */
    async getStats() {
        try {
            return await this.fetchWithRetry(
                this.config.endpoints.smart.stats
            );
        } catch (error) {
            console.error('Stats failed:', error);
            throw error;
        }
    }
    
    /**
     * Get Alpha Vantage data
     */
    async getAlphaVantageData(endpoint, params = {}) {
        const url = new URL(endpoint);
        Object.keys(params).forEach(key => 
            url.searchParams.append(key, params[key])
        );
        
        try {
            return await this.fetchWithRetry(url.toString());
        } catch (error) {
            console.error('Alpha Vantage request failed:', error);
            throw error;
        }
    }
    
    /**
     * Get Massive.com data
     */
    async getMassiveData(endpoint, params = {}) {
        const url = new URL(endpoint);
        Object.keys(params).forEach(key => 
            url.searchParams.append(key, params[key])
        );
        
        try {
            return await this.fetchWithRetry(url.toString());
        } catch (error) {
            console.error('Massive.com request failed:', error);
            throw error;
        }
    }
}

// Create global API client instance
window.apiClient = new SmartAPIClient();

// Export for modules
if (typeof module !== 'undefined' && module.exports) {
    module.exports = { API_CONFIG, SmartAPIClient };
}

console.log('✅ API Configuration loaded successfully');
console.log('📊 Smart Fallback System: 305+ resources available');
console.log('🔄 Resource rotation: ENABLED');
console.log('🔒 Proxy support: ENABLED');
console.log('✨ Features:', window.API_CONFIG.features);
