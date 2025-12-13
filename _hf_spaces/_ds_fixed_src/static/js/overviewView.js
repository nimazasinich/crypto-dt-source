import apiClient from './apiClient.js';
import { formatCurrency, formatPercent, renderMessage, createSkeletonRows } from './uiUtils.js';

class OverviewView {
    constructor(section) {
        this.section = section;
        this.statsContainer = section.querySelector('[data-overview-stats]');
        this.topCoinsBody = section.querySelector('[data-top-coins-body]');
        this.sentimentCanvas = section.querySelector('#sentiment-chart');
        this.sentimentChart = null;
    }

    async init() {
        this.renderStatSkeletons();
        this.topCoinsBody.innerHTML = createSkeletonRows(6, 6);
        await Promise.all([this.loadStats(), this.loadTopCoins(), this.loadSentiment()]);
    }

    renderStatSkeletons() {
        if (!this.statsContainer) return;
        this.statsContainer.innerHTML = Array.from({ length: 4 })
            .map(() => '<div class="glass-card stat-card skeleton" style="height: 140px;"></div>')
            .join('');
    }

    async loadStats() {
        if (!this.statsContainer) return;
        const result = await apiClient.getMarketStats();
        if (!result.ok) {
            renderMessage(this.statsContainer, {
                state: 'error',
                title: 'Unable to load market stats',
                body: result.error || 'Unknown error',
            });
            return;
        }
        const stats = result.data || {};
        const cards = [
            { label: 'Total Market Cap', value: formatCurrency(stats.total_market_cap) },
            { label: '24h Volume', value: formatCurrency(stats.total_volume_24h) },
            { label: 'BTC Dominance', value: formatPercent(stats.btc_dominance) },
            { label: 'ETH Dominance', value: formatPercent(stats.eth_dominance) },
        ];
        this.statsContainer.innerHTML = cards
            .map(
                (card) => `
                <div class="glass-card stat-card">
                    <h3>${card.label}</h3>
                    <div class="stat-value">${card.value}</div>
                    <div class="stat-trend">Updated ${new Date().toLocaleTimeString()}</div>
                </div>
            `,
            )
            .join('');
    }

    async loadTopCoins() {
        const result = await apiClient.getTopCoins(10);
        if (!result.ok) {
            this.topCoinsBody.innerHTML = `
                <tr><td colspan="7">
                    <div class="inline-message inline-error">
                        <strong>Failed to load coins</strong>
                        <p>${result.error}</p>
                    </div>
                </td></tr>`;
            return;
        }
        const rows = (result.data || []).map(
            (coin, index) => `
            <tr>
                <td>${index + 1}</td>
                <td>${coin.symbol || coin.ticker || '—'}</td>
                <td>${coin.name || 'Unknown'}</td>
                <td>${formatCurrency(coin.price)}</td>
                <td class="${coin.change_24h >= 0 ? 'text-success' : 'text-danger'}">
                    ${formatPercent(coin.change_24h)}
                </td>
                <td>${formatCurrency(coin.volume_24h)}</td>
                <td>${formatCurrency(coin.market_cap)}</td>
            </tr>
        `);
        this.topCoinsBody.innerHTML = rows.join('');
    }

    async loadSentiment() {
        if (!this.sentimentCanvas) return;
        const result = await apiClient.runQuery({ query: 'global crypto sentiment breakdown' });
        if (!result.ok) {
            this.sentimentCanvas.replaceWith(this.buildSentimentFallback(result.error));
            return;
        }
        const payload = result.data || {};
        const sentiment = payload.sentiment || payload.data || {};
        const data = {
            bullish: sentiment.bullish ?? 40,
            neutral: sentiment.neutral ?? 35,
            bearish: sentiment.bearish ?? 25,
        };
        if (this.sentimentChart) {
            this.sentimentChart.destroy();
        }
        this.sentimentChart = new Chart(this.sentimentCanvas, {
            type: 'doughnut',
            data: {
                labels: ['Bullish', 'Neutral', 'Bearish'],
                datasets: [
                    {
                        data: [data.bullish, data.neutral, data.bearish],
                        backgroundColor: ['#22c55e', '#38bdf8', '#ef4444'],
                        borderWidth: 0,
                    },
                ],
            },
            options: {
                cutout: '65%',
                plugins: {
                    legend: {
                        labels: { color: 'var(--text-primary)', usePointStyle: true },
                    },
                },
            },
        });
    }

    buildSentimentFallback(message) {
        const wrapper = document.createElement('div');
        wrapper.className = 'inline-message inline-info';
        wrapper.innerHTML = `
            <strong>Sentiment insight unavailable</strong>
            <p>${message || 'AI sentiment endpoint did not respond in time.'}</p>
        `;
        return wrapper;
    }
}

export default OverviewView;
