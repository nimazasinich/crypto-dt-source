/**
 * API Client - Centralized API Communication
 * Crypto Monitor HF - Enterprise Edition
 */

class APIClient {
    constructor(baseURL = '') {
        this.baseURL = baseURL;
        this.defaultHeaders = {
            'Content-Type': 'application/json',
        };
    }

    /**
     * Generic fetch wrapper with error handling
     */
    async request(endpoint, options = {}) {
        const url = `${this.baseURL}${endpoint}`;
        const config = {
            headers: { ...this.defaultHeaders, ...options.headers },
            ...options,
        };

        try {
            const response = await fetch(url, config);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }

            // Handle different content types
            const contentType = response.headers.get('content-type');
            if (contentType && contentType.includes('application/json')) {
                return await response.json();
            } else if (contentType && contentType.includes('text')) {
                return await response.text();
            }

            return response;
        } catch (error) {
            console.error(`[APIClient] Error fetching ${endpoint}:`, error);
            throw error;
        }
    }

    /**
     * GET request
     */
    async get(endpoint) {
        return this.request(endpoint, { method: 'GET' });
    }

    /**
     * POST request
     */
    async post(endpoint, data) {
        return this.request(endpoint, {
            method: 'POST',
            body: JSON.stringify(data),
        });
    }

    /**
     * PUT request
     */
    async put(endpoint, data) {
        return this.request(endpoint, {
            method: 'PUT',
            body: JSON.stringify(data),
        });
    }

    /**
     * DELETE request
     */
    async delete(endpoint) {
        return this.request(endpoint, { method: 'DELETE' });
    }

    // ===== Core API Methods =====

    /**
     * Get system health
     */
    async getHealth() {
        return this.get('/api/health');
    }

    /**
     * Get system status
     */
    async getStatus() {
        return this.get('/api/status');
    }

    /**
     * Get system stats
     */
    async getStats() {
        return this.get('/api/stats');
    }

    /**
     * Get system info
     */
    async getInfo() {
        return this.get('/api/info');
    }

    // ===== Market Data =====

    /**
     * Get market overview
     */
    async getMarket() {
        return this.get('/api/market');
    }

    /**
     * Get trending coins
     */
    async getTrending() {
        return this.get('/api/trending');
    }

    /**
     * Get sentiment analysis
     */
    async getSentiment() {
        return this.get('/api/sentiment');
    }

    /**
     * Get DeFi protocols
     */
    async getDefi() {
        return this.get('/api/defi');
    }

    // ===== Providers API =====

    /**
     * Get all providers
     */
    async getProviders() {
        return this.get('/api/providers');
    }

    /**
     * Get specific provider
     */
    async getProvider(providerId) {
        return this.get(`/api/providers/${providerId}`);
    }

    /**
     * Get providers by category
     */
    async getProvidersByCategory(category) {
        return this.get(`/api/providers/category/${category}`);
    }

    /**
     * Health check for provider
     */
    async checkProviderHealth(providerId) {
        return this.post(`/api/providers/${providerId}/health-check`);
    }

    /**
     * Add custom provider
     */
    async addProvider(providerData) {
        return this.post('/api/providers', providerData);
    }

    /**
     * Remove provider
     */
    async removeProvider(providerId) {
        return this.delete(`/api/providers/${providerId}`);
    }

    // ===== Pools API =====

    /**
     * Get all pools
     */
    async getPools() {
        return this.get('/api/pools');
    }

    /**
     * Get specific pool
     */
    async getPool(poolId) {
        return this.get(`/api/pools/${poolId}`);
    }

    /**
     * Create new pool
     */
    async createPool(poolData) {
        return this.post('/api/pools', poolData);
    }

    /**
     * Delete pool
     */
    async deletePool(poolId) {
        return this.delete(`/api/pools/${poolId}`);
    }

    /**
     * Add member to pool
     */
    async addPoolMember(poolId, providerId) {
        return this.post(`/api/pools/${poolId}/members`, { provider_id: providerId });
    }

    /**
     * Remove member from pool
     */
    async removePoolMember(poolId, providerId) {
        return this.delete(`/api/pools/${poolId}/members/${providerId}`);
    }

    /**
     * Rotate pool
     */
    async rotatePool(poolId) {
        return this.post(`/api/pools/${poolId}/rotate`);
    }

    /**
     * Get pool history
     */
    async getPoolHistory() {
        return this.get('/api/pools/history');
    }

    // ===== Logs API =====

    /**
     * Get logs
     */
    async getLogs(params = {}) {
        const query = new URLSearchParams(params).toString();
        return this.get(`/api/logs${query ? '?' + query : ''}`);
    }

    /**
     * Get recent logs
     */
    async getRecentLogs() {
        return this.get('/api/logs/recent');
    }

    /**
     * Get error logs
     */
    async getErrorLogs() {
        return this.get('/api/logs/errors');
    }

    /**
     * Get log stats
     */
    async getLogStats() {
        return this.get('/api/logs/stats');
    }

    /**
     * Export logs as JSON
     */
    async exportLogsJSON() {
        return this.get('/api/logs/export/json');
    }

    /**
     * Export logs as CSV
     */
    async exportLogsCSV() {
        return this.get('/api/logs/export/csv');
    }

    /**
     * Clear logs
     */
    async clearLogs() {
        return this.delete('/api/logs');
    }

    // ===== Resources API =====

    /**
     * Get resources
     */
    async getResources() {
        return this.get('/api/resources');
    }

    /**
     * Get resources by category
     */
    async getResourcesByCategory(category) {
        return this.get(`/api/resources/category/${category}`);
    }

    /**
     * Import resources from JSON
     */
    async importResourcesJSON(data) {
        return this.post('/api/resources/import/json', data);
    }

    /**
     * Export resources as JSON
     */
    async exportResourcesJSON() {
        return this.get('/api/resources/export/json');
    }

    /**
     * Export resources as CSV
     */
    async exportResourcesCSV() {
        return this.get('/api/resources/export/csv');
    }

    /**
     * Backup resources
     */
    async backupResources() {
        return this.post('/api/resources/backup');
    }

    /**
     * Add resource provider
     */
    async addResourceProvider(providerData) {
        return this.post('/api/resources/provider', providerData);
    }

    /**
     * Delete resource provider
     */
    async deleteResourceProvider(providerId) {
        return this.delete(`/api/resources/provider/${providerId}`);
    }

    /**
     * Get discovery status
     */
    async getDiscoveryStatus() {
        return this.get('/api/resources/discovery/status');
    }

    /**
     * Run discovery
     */
    async runDiscovery() {
        return this.post('/api/resources/discovery/run');
    }

    // ===== HuggingFace API =====

    /**
     * Get HuggingFace health
     */
    async getHFHealth() {
        return this.get('/api/hf/health');
    }

    /**
     * Run HuggingFace sentiment analysis
     */
    async runHFSentiment(data) {
        return this.post('/api/hf/run-sentiment', data);
    }

    // ===== Reports API =====

    /**
     * Get discovery report
     */
    async getDiscoveryReport() {
        return this.get('/api/reports/discovery');
    }

    /**
     * Get models report
     */
    async getModelsReport() {
        return this.get('/api/reports/models');
    }

    // ===== Diagnostics API =====

    /**
     * Run diagnostics
     */
    async runDiagnostics() {
        return this.post('/api/diagnostics/run');
    }

    /**
     * Get last diagnostics
     */
    async getLastDiagnostics() {
        return this.get('/api/diagnostics/last');
    }

    // ===== Sessions API =====

    /**
     * Get active sessions
     */
    async getSessions() {
        return this.get('/api/sessions');
    }

    /**
     * Get session stats
     */
    async getSessionStats() {
        return this.get('/api/sessions/stats');
    }

    /**
     * Broadcast message
     */
    async broadcast(message) {
        return this.post('/api/broadcast', { message });
    }

    // ===== Feature Flags API =====

    /**
     * Get all feature flags
     */
    async getFeatureFlags() {
        return this.get('/api/feature-flags');
    }

    /**
     * Get single feature flag
     */
    async getFeatureFlag(flagName) {
        return this.get(`/api/feature-flags/${flagName}`);
    }

    /**
     * Update feature flags
     */
    async updateFeatureFlags(flags) {
        return this.put('/api/feature-flags', { flags });
    }

    /**
     * Update single feature flag
     */
    async updateFeatureFlag(flagName, value) {
        return this.put(`/api/feature-flags/${flagName}`, { flag_name: flagName, value });
    }

    /**
     * Reset feature flags to defaults
     */
    async resetFeatureFlags() {
        return this.post('/api/feature-flags/reset');
    }

    // ===== Proxy API =====

    /**
     * Get proxy status
     */
    async getProxyStatus() {
        return this.get('/api/proxy-status');
    }
}

// Create global instance
window.apiClient = new APIClient();

console.log('[APIClient] Initialized');
