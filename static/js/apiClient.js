const DEFAULT_TTL = 60 * 1000; // 1 minute cache

class ApiClient {
    constructor() {
        const origin = window?.location?.origin ?? '';
        this.baseURL = origin.replace(/\/$/, '');
        this.cache = new Map();
        this.requestLogs = [];
        this.errorLogs = [];
        this.logSubscribers = new Set();
        this.errorSubscribers = new Set();
    }

    buildUrl(endpoint) {
        if (!endpoint.startsWith('/')) {
            return `${this.baseURL}/${endpoint}`;
        }
        return `${this.baseURL}${endpoint}`;
    }

    notifyLog(entry) {
        this.requestLogs.push(entry);
        this.requestLogs = this.requestLogs.slice(-100);
        this.logSubscribers.forEach((cb) => cb(entry));
    }

    notifyError(entry) {
        this.errorLogs.push(entry);
        this.errorLogs = this.errorLogs.slice(-100);
        this.errorSubscribers.forEach((cb) => cb(entry));
    }

    onLog(callback) {
        this.logSubscribers.add(callback);
        return () => this.logSubscribers.delete(callback);
    }

    onError(callback) {
        this.errorSubscribers.add(callback);
        return () => this.errorSubscribers.delete(callback);
    }

    getLogs() {
        return [...this.requestLogs];
    }

    getErrors() {
        return [...this.errorLogs];
    }

    async request(method, endpoint, { body, cache = true, ttl = DEFAULT_TTL } = {}) {
        const url = this.buildUrl(endpoint);
        const cacheKey = `${method}:${url}`;

        if (method === 'GET' && cache && this.cache.has(cacheKey)) {
            const cached = this.cache.get(cacheKey);
            if (Date.now() - cached.timestamp < ttl) {
                return { ok: true, data: cached.data, cached: true };
            }
        }

        const started = performance.now();
        const randomId = (window.crypto && window.crypto.randomUUID && window.crypto.randomUUID())
            || `${Date.now()}-${Math.random()}`;
        const entry = {
            id: randomId,
            method,
            endpoint,
            status: 'pending',
            duration: 0,
            time: new Date().toISOString(),
        };

        try {
            const response = await fetch(url, {
                method,
                headers: {
                    'Content-Type': 'application/json',
                },
                body: body ? JSON.stringify(body) : undefined,
            });

            const duration = performance.now() - started;
            entry.duration = Math.round(duration);
            entry.status = response.status;

            const contentType = response.headers.get('content-type') || '';
            let data = null;
            if (contentType.includes('application/json')) {
                data = await response.json();
            } else if (contentType.includes('text')) {
                data = await response.text();
            }

            if (!response.ok) {
                const error = new Error((data && data.message) || response.statusText || 'Unknown error');
                error.status = response.status;
                throw error;
            }

            if (method === 'GET' && cache) {
                this.cache.set(cacheKey, { timestamp: Date.now(), data });
            }

            this.notifyLog({ ...entry, success: true });
            return { ok: true, data };
        } catch (error) {
            const duration = performance.now() - started;
            entry.duration = Math.round(duration);
            entry.status = error.status || 'error';
            this.notifyLog({ ...entry, success: false, error: error.message });
            this.notifyError({
                message: error.message,
                endpoint,
                method,
                time: new Date().toISOString(),
            });
            return { ok: false, error: error.message };
        }
    }

    get(endpoint, options) {
        return this.request('GET', endpoint, options);
    }

    post(endpoint, body, options = {}) {
        return this.request('POST', endpoint, { ...options, body });
    }

    // ===== Specific API helpers =====
    getHealth() {
        return this.get('/api/health');
    }

    getTopCoins(limit = 10) {
        return this.get(`/api/coins/top?limit=${limit}`);
    }

    getCoinDetails(symbol) {
        return this.get(`/api/coins/${symbol}`);
    }

    getMarketStats() {
        return this.get('/api/market/stats');
    }

    getLatestNews(limit = 20) {
        return this.get(`/api/news/latest?limit=${limit}`);
    }

    getProviders() {
        return this.get('/api/providers');
    }

    getPriceChart(symbol, timeframe = '7d') {
        return this.get(`/api/charts/price/${symbol}?timeframe=${timeframe}`);
    }

    runQuery(payload) {
        return this.post('/api/query', payload);
    }

    getDatasetsList() {
        return this.get('/api/datasets/list');
    }

    getDatasetSample(name) {
        return this.get(`/api/datasets/sample?name=${encodeURIComponent(name)}`);
    }

    getModelsList() {
        return this.get('/api/models/list');
    }

    testModel(payload) {
        return this.post('/api/models/test', payload);
    }
}

const apiClient = new ApiClient();
export default apiClient;
