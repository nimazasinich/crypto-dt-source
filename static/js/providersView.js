import apiClient from './apiClient.js';

class ProvidersView {
    constructor(section) {
        this.section = section;
        this.tableBody = section?.querySelector('[data-providers-table]');
        this.searchInput = section?.querySelector('[data-provider-search]');
        this.categorySelect = section?.querySelector('[data-provider-category]');
        this.summaryNode = section?.querySelector('[data-provider-summary]');
        this.refreshButton = section?.querySelector('[data-provider-refresh]');
        this.providers = [];
        this.filtered = [];
    }

    init() {
        if (!this.section) return;
        this.bindEvents();
        this.loadProviders();
    }

    bindEvents() {
        this.searchInput?.addEventListener('input', () => this.applyFilters());
        this.categorySelect?.addEventListener('change', () => this.applyFilters());
        this.refreshButton?.addEventListener('click', () => this.loadProviders());
    }

    async loadProviders() {
        if (this.tableBody) {
            this.tableBody.innerHTML = '<tr><td colspan="5">Loading providers...</td></tr>';
        }
        const result = await apiClient.getProviders();
        if (!result.ok) {
            this.tableBody.innerHTML = `<tr><td colspan="5"><div class="inline-message inline-error">${result.error}</div></td></tr>`;
            return;
        }
        const data = result.data || {};
        this.providers = data.providers || data || [];
        this.applyFilters();
    }

    applyFilters() {
        const term = (this.searchInput?.value || '').toLowerCase();
        const category = this.categorySelect?.value || 'all';
        this.filtered = this.providers.filter((provider) => {
            const matchesTerm = `${provider.name} ${provider.provider_id}`.toLowerCase().includes(term);
            const matchesCategory = category === 'all' || (provider.category || 'uncategorized') === category;
            return matchesTerm && matchesCategory;
        });
        this.renderTable();
        this.renderSummary();
    }

    renderTable() {
        if (!this.tableBody) return;
        if (!this.filtered.length) {
            this.tableBody.innerHTML = '<tr><td colspan="5">No providers match the filters.</td></tr>';
            return;
        }
        this.tableBody.innerHTML = this.filtered
            .map(
                (provider) => `
                <tr>
                    <td>${provider.name || provider.provider_id}</td>
                    <td>${provider.category || 'general'}</td>
                    <td><span class="badge ${provider.status === 'healthy' ? 'badge-success' : 'badge-danger'}">${
                        provider.status || 'unknown'
                    }</span></td>
                    <td>${provider.latency_ms ? `${provider.latency_ms}ms` : '—'}</td>
                    <td>${provider.error || provider.status_code || 'OK'}</td>
                </tr>
            `,
            )
            .join('');
    }

    renderSummary() {
        if (!this.summaryNode) return;
        const total = this.providers.length;
        const healthy = this.providers.filter((provider) => provider.status === 'healthy').length;
        const degraded = total - healthy;
        this.summaryNode.innerHTML = `
            <div class="stat-card glass-card">
                <h3>Total Providers</h3>
                <p class="stat-value">${total}</p>
            </div>
            <div class="stat-card glass-card">
                <h3>Healthy</h3>
                <p class="stat-value text-success">${healthy}</p>
            </div>
            <div class="stat-card glass-card">
                <h3>Issues</h3>
                <p class="stat-value text-danger">${degraded}</p>
            </div>
        `;
    }
}

export default ProvidersView;
