import apiClient from './apiClient.js';

const ENDPOINTS = [
    { label: 'Health', method: 'GET', path: '/api/health', description: 'Core service health check' },
    { label: 'Market Stats', method: 'GET', path: '/api/market/stats', description: 'Global market metrics' },
    { label: 'Top Coins', method: 'GET', path: '/api/coins/top', description: 'Top market cap coins', params: 'limit=10' },
    { label: 'Latest News', method: 'GET', path: '/api/news/latest', description: 'Latest curated news', params: 'limit=20' },
    { label: 'Chart History', method: 'GET', path: '/api/charts/price/BTC', description: 'Historical price data', params: 'timeframe=7d' },
    { label: 'Chart AI Analysis', method: 'POST', path: '/api/charts/analyze', description: 'AI chart insights', body: '{"symbol":"BTC","timeframe":"7d"}' },
    { label: 'Sentiment Analysis', method: 'POST', path: '/api/sentiment/analyze', description: 'Run sentiment models', body: '{"text":"Bitcoin rally","mode":"auto"}' },
    { label: 'News Summarize', method: 'POST', path: '/api/news/summarize', description: 'Summarize a headline', body: '{"title":"Headline","body":"Full article"}' },
];

class ApiExplorerView {
    constructor(section) {
        this.section = section;
        this.endpointSelect = section?.querySelector('[data-api-endpoint]');
        this.methodSelect = section?.querySelector('[data-api-method]');
        this.paramsInput = section?.querySelector('[data-api-params]');
        this.bodyInput = section?.querySelector('[data-api-body]');
        this.sendButton = section?.querySelector('[data-api-send]');
        this.responseNode = section?.querySelector('[data-api-response]');
        this.metaNode = section?.querySelector('[data-api-meta]');
    }

    init() {
        if (!this.section) return;
        this.populateEndpoints();
        this.bindEvents();
        this.applyPreset(ENDPOINTS[0]);
    }

    populateEndpoints() {
        if (!this.endpointSelect) return;
        this.endpointSelect.innerHTML = ENDPOINTS.map((endpoint, index) => `<option value="${index}">${endpoint.label}</option>`).join('');
    }

    bindEvents() {
        this.endpointSelect?.addEventListener('change', () => {
            const index = Number(this.endpointSelect.value);
            this.applyPreset(ENDPOINTS[index]);
        });
        this.sendButton?.addEventListener('click', () => this.sendRequest());
    }

    applyPreset(preset) {
        if (!preset) return;
        if (this.methodSelect) {
            this.methodSelect.value = preset.method;
        }
        if (this.paramsInput) {
            this.paramsInput.value = preset.params || '';
        }
        if (this.bodyInput) {
            this.bodyInput.value = preset.body || '';
        }
        this.section.querySelector('[data-api-description]').textContent = preset.description;
        this.section.querySelector('[data-api-path]').textContent = preset.path;
    }

    async sendRequest() {
        const index = Number(this.endpointSelect?.value || 0);
        const preset = ENDPOINTS[index];
        const method = this.methodSelect?.value || preset.method;
        let endpoint = preset.path;
        const params = (this.paramsInput?.value || '').trim();
        if (params) {
            endpoint += endpoint.includes('?') ? `&${params}` : `?${params}`;
        }

        let body = this.bodyInput?.value.trim();
        if (!body) body = undefined;
        let parsedBody;
        if (body && method !== 'GET') {
            try {
                parsedBody = JSON.parse(body);
            } catch (error) {
                this.renderError('Invalid JSON body');
                return;
            }
        }

        this.renderMeta('pending');
        this.renderResponse('Fetching...');
        const started = performance.now();
        const result = await apiClient.request(method, endpoint, { cache: false, body: parsedBody });
        const duration = Math.round(performance.now() - started);

        if (!result.ok) {
            this.renderError(result.error || 'Request failed', duration);
            return;
        }
        this.renderMeta('ok', duration, method, endpoint);
        this.renderResponse(result.data);
    }

    renderResponse(data) {
        if (!this.responseNode) return;
        if (typeof data === 'string') {
            this.responseNode.textContent = data;
            return;
        }
        this.responseNode.textContent = JSON.stringify(data, null, 2);
    }

    renderMeta(status, duration = 0, method = '', path = '') {
        if (!this.metaNode) return;
        if (status === 'pending') {
            this.metaNode.textContent = 'Sending request...';
            return;
        }
        this.metaNode.textContent = `${method} ${path} • ${duration}ms`;
    }

    renderError(message, duration = 0) {
        this.renderMeta('error', duration);
        this.renderResponse({ error: message });
    }
}

export default ApiExplorerView;
