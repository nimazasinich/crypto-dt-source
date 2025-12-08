import apiClient from './apiClient.js';

class AdminDashboard {
    constructor() {
        this.providersContainer = document.querySelector('[data-admin-providers]');
        this.tableBody = document.querySelector('[data-admin-table]');
        this.refreshBtn = document.querySelector('[data-admin-refresh]');
        this.healthBadge = document.querySelector('[data-admin-health]');
        this.latencyChartCanvas = document.querySelector('#provider-latency-chart');
        this.statusChartCanvas = document.querySelector('#provider-status-chart');
        this.latencyChart = null;
        this.statusChart = null;
    }

    init() {
        this.loadProviders();
        if (this.refreshBtn) {
            this.refreshBtn.addEventListener('click', () => this.loadProviders());
        }
    }

    async loadProviders() {
        if (this.tableBody) {
            this.tableBody.innerHTML = '<tr><td colspan="5">Loading providers...</td></tr>';
        }
        const result = await apiClient.getProviders();
        if (!result.ok) {
            this.providersContainer.innerHTML = `<div class="inline-message inline-error">${result.error}</div>`;
            this.tableBody.innerHTML = '';
            return;
        }
        const providers = result.data || [];
        this.renderCards(providers);
        this.renderTable(providers);
        this.renderCharts(providers);
    }

    renderCards(providers) {
        if (!this.providersContainer) return;
        const healthy = providers.filter((p) => p.status === 'healthy').length;
        const failing = providers.length - healthy;
        const avgLatency = (
            providers.reduce((sum, provider) => sum + Number(provider.latency || 0), 0) / (providers.length || 1)
        ).toFixed(0);
        this.providersContainer.innerHTML = `
            <div class="glass-card stat-card">
                <h3>Total Providers</h3>
                <div class="stat-value">${providers.length}</div>
            </div>
            <div class="glass-card stat-card">
                <h3>Healthy</h3>
                <div class="stat-value text-success">${healthy}</div>
            </div>
            <div class="glass-card stat-card">
                <h3>Issues</h3>
                <div class="stat-value text-danger">${failing}</div>
            </div>
            <div class="glass-card stat-card">
                <h3>Avg Latency</h3>
                <div class="stat-value">${avgLatency} ms</div>
            </div>
        `;
        if (this.healthBadge) {
            this.healthBadge.dataset.state = failing ? 'warn' : 'ok';
            this.healthBadge.querySelector('span').textContent = failing ? 'degraded' : 'optimal';
        }
    }

    renderTable(providers) {
        if (!this.tableBody) return;
        this.tableBody.innerHTML = providers
            .map(
                (provider) => `
                <tr>
                    <td>${provider.name}</td>
                    <td>${provider.category || '—'}</td>
                    <td>${provider.latency || '—'} ms</td>
                    <td>
                        <span class="badge ${provider.status === 'healthy' ? 'badge-success' : 'badge-danger'}">
                            ${provider.status}
                        </span>
                    </td>
                    <td>${provider.endpoint || provider.url || ''}</td>
                </tr>
            `,
            )
            .join('');
    }

    renderCharts(providers) {
        if (this.latencyChartCanvas) {
            const labels = providers.map((p) => p.name);
            const data = providers.map((p) => p.latency || 0);
            if (this.latencyChart) this.latencyChart.destroy();
            this.latencyChart = new Chart(this.latencyChartCanvas, {
                type: 'bar',
                data: {
                    labels,
                    datasets: [
                        {
                            label: 'Latency (ms)',
                            data,
                            backgroundColor: '#38bdf8',
                        },
                    ],
                },
                options: {
                    plugins: { legend: { display: false } },
                    scales: {
                        x: { ticks: { color: 'var(--text-muted)' } },
                        y: { ticks: { color: 'var(--text-muted)' } },
                    },
                },
            });
        }
        if (this.statusChartCanvas) {
            const healthy = providers.filter((p) => p.status === 'healthy').length;
            const degraded = providers.length - healthy;
            if (this.statusChart) this.statusChart.destroy();
            this.statusChart = new Chart(this.statusChartCanvas, {
                type: 'doughnut',
                data: {
                    labels: ['Healthy', 'Degraded'],
                    datasets: [
                        {
                            data: [healthy, degraded],
                            backgroundColor: ['#22c55e', '#f59e0b'],
                        },
                    ],
                },
                options: {
                    plugins: { legend: { labels: { color: 'var(--text-primary)' } } },
                },
            });
        }
    }
}

window.addEventListener('DOMContentLoaded', () => {
    const dashboard = new AdminDashboard();
    dashboard.init();
});
