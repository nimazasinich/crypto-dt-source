import apiClient from './apiClient.js';
import { formatCurrency, formatPercent, createSkeletonRows } from './uiUtils.js';

class MarketView {
    constructor(section, wsClient) {
        this.section = section;
        this.wsClient = wsClient;
        this.tableBody = section.querySelector('[data-market-body]');
        this.searchInput = section.querySelector('[data-market-search]');
        this.timeframeButtons = section.querySelectorAll('[data-timeframe]');
        this.liveToggle = section.querySelector('[data-live-toggle]');
        this.drawer = section.querySelector('[data-market-drawer]');
        this.drawerClose = section.querySelector('[data-close-drawer]');
        this.drawerSymbol = section.querySelector('[data-drawer-symbol]');
        this.drawerStats = section.querySelector('[data-drawer-stats]');
        this.drawerNews = section.querySelector('[data-drawer-news]');
        this.chartWrapper = section.querySelector('[data-chart-wrapper]');
        this.chartCanvas = this.chartWrapper?.querySelector('#market-detail-chart');
        this.chart = null;
        this.coins = [];
        this.filtered = [];
        this.currentTimeframe = '7d';
        this.liveUpdates = false;
    }

    async init() {
        this.tableBody.innerHTML = createSkeletonRows(10, 7);
        await this.loadCoins();
        this.bindEvents();
    }

    bindEvents() {
        if (this.searchInput) {
            this.searchInput.addEventListener('input', () => this.filterCoins());
        }
        this.timeframeButtons.forEach((btn) => {
            btn.addEventListener('click', () => {
                this.timeframeButtons.forEach((b) => b.classList.remove('active'));
                btn.classList.add('active');
                this.currentTimeframe = btn.dataset.timeframe;
                if (this.drawer?.classList.contains('active') && this.drawerSymbol?.dataset.symbol) {
                    this.openDrawer(this.drawerSymbol.dataset.symbol);
                }
            });
        });
        if (this.liveToggle) {
            this.liveToggle.addEventListener('change', (event) => {
                this.liveUpdates = event.target.checked;
                if (this.liveUpdates) {
                    this.wsSubscription = this.wsClient.subscribe('price_update', (payload) => this.applyLiveUpdate(payload));
                } else if (this.wsSubscription) {
                    this.wsSubscription();
                }
            });
        }
        if (this.drawerClose) {
            this.drawerClose.addEventListener('click', () => this.drawer.classList.remove('active'));
        }
    }

    async loadCoins() {
        const result = await apiClient.getTopCoins(50);
        if (!result.ok) {
            this.tableBody.innerHTML = `
                <tr><td colspan="8">
                    <div class="inline-message inline-error">
                        <strong>Unable to load coins</strong>
                        <p>${result.error}</p>
                    </div>
                </td></tr>`;
            return;
        }
        this.coins = result.data || [];
        this.filtered = [...this.coins];
        this.renderTable();
    }

    filterCoins() {
        const term = this.searchInput.value.toLowerCase();
        this.filtered = this.coins.filter((coin) => {
            const name = `${coin.name} ${coin.symbol}`.toLowerCase();
            return name.includes(term);
        });
        this.renderTable();
    }

    renderTable() {
        this.tableBody.innerHTML = this.filtered
            .map(
                (coin, index) => `
                <tr data-symbol="${coin.symbol}" class="market-row">
                    <td>${index + 1}</td>
                    <td>
                        <div class="chip">${coin.symbol || '—'}</div>
                    </td>
                    <td>${coin.name || 'Unknown'}</td>
                    <td>${formatCurrency(coin.price)}</td>
                    <td class="${coin.change_24h >= 0 ? 'text-success' : 'text-danger'}">${formatPercent(coin.change_24h)}</td>
                    <td>${formatCurrency(coin.volume_24h)}</td>
                    <td>${formatCurrency(coin.market_cap)}</td>
                </tr>
            `,
            )
            .join('');
        this.section.querySelectorAll('.market-row').forEach((row) => {
            row.addEventListener('click', () => this.openDrawer(row.dataset.symbol));
        });
    }

    async openDrawer(symbol) {
        if (!symbol) return;
        this.drawerSymbol.textContent = symbol;
        this.drawerSymbol.dataset.symbol = symbol;
        this.drawer.classList.add('active');
        this.drawerStats.innerHTML = '<p>Loading...</p>';
        this.drawerNews.innerHTML = '<p>Loading news...</p>';
        await Promise.all([this.loadCoinDetails(symbol), this.loadCoinNews(symbol)]);
    }

    async loadCoinDetails(symbol) {
        const [details, chart] = await Promise.all([
            apiClient.getCoinDetails(symbol),
            apiClient.getPriceChart(symbol, this.currentTimeframe),
        ]);

        if (!details.ok) {
            this.drawerStats.innerHTML = `<div class="inline-message inline-error">${details.error}</div>`;
        } else {
            const coin = details.data || {};
            this.drawerStats.innerHTML = `
                <div class="grid-two">
                    <div>
                        <h4>Price</h4>
                        <p class="stat-value">${formatCurrency(coin.price)}</p>
                    </div>
                    <div>
                        <h4>24h Change</h4>
                        <p class="stat-value ${coin.change_24h >= 0 ? 'text-success' : 'text-danger'}">${formatPercent(coin.change_24h)}</p>
                    </div>
                    <div>
                        <h4>High / Low</h4>
                        <p>${formatCurrency(coin.high_24h)} / ${formatCurrency(coin.low_24h)}</p>
                    </div>
                    <div>
                        <h4>Market Cap</h4>
                        <p>${formatCurrency(coin.market_cap)}</p>
                    </div>
                </div>
            `;
        }

        if (!chart.ok) {
            if (this.chartWrapper) {
                this.chartWrapper.innerHTML = `<div class="inline-message inline-error">${chart.error}</div>`;
            }
        } else {
            this.renderChart(chart.data || []);
        }
    }

    renderChart(points) {
        if (!this.chartWrapper) return;
        if (!this.chartCanvas || !this.chartWrapper.contains(this.chartCanvas)) {
            this.chartWrapper.innerHTML = '<canvas id="market-detail-chart" height="180"></canvas>';
            this.chartCanvas = this.chartWrapper.querySelector('#market-detail-chart');
        }
        const labels = points.map((point) => point.time || point.timestamp);
        const data = points.map((point) => point.price || point.value);
        if (this.chart) {
            this.chart.destroy();
        }
        this.chart = new Chart(this.chartCanvas, {
            type: 'line',
            data: {
                labels,
                datasets: [
                    {
                        label: `${this.drawerSymbol.textContent} Price`,
                        data,
                        fill: false,
                        borderColor: '#38bdf8',
                        tension: 0.3,
                    },
                ],
            },
            options: {
                animation: false,
                scales: {
                    x: { ticks: { color: 'var(--text-muted)' } },
                    y: { ticks: { color: 'var(--text-muted)' } },
                },
                plugins: { legend: { display: false } },
            },
        });
    }

    async loadCoinNews(symbol) {
        const result = await apiClient.getLatestNews(5);
        if (!result.ok) {
            this.drawerNews.innerHTML = `<div class="inline-message inline-error">${result.error}</div>`;
            return;
        }
        const related = (result.data || []).filter((item) => (item.symbols || []).includes(symbol));
        if (!related.length) {
            this.drawerNews.innerHTML = '<p>No related headlines available.</p>';
            return;
        }
        this.drawerNews.innerHTML = related
            .map(
                (news) => `
                <article class="news-item">
                    <h4>${news.title}</h4>
                    <p>${news.summary || ''}</p>
                    <small>${new Date(news.published_at || news.date).toLocaleString()}</small>
                </article>
            `,
            )
            .join('');
    }

    applyLiveUpdate(payload) {
        if (!this.liveUpdates) return;
        const symbol = payload.symbol || payload.ticker;
        if (!symbol) return;
        const row = this.section.querySelector(`tr[data-symbol="${symbol}"]`);
        if (!row) return;
        const priceCell = row.children[3];
        const changeCell = row.children[4];
        if (payload.price) {
            priceCell.textContent = formatCurrency(payload.price);
        }
        if (payload.change_24h) {
            changeCell.textContent = formatPercent(payload.change_24h);
            changeCell.classList.toggle('text-success', payload.change_24h >= 0);
            changeCell.classList.toggle('text-danger', payload.change_24h < 0);
        }
        row.classList.add('flash');
        setTimeout(() => row.classList.remove('flash'), 600);
    }
}

export default MarketView;
