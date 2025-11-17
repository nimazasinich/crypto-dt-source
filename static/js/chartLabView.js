import apiClient from './apiClient.js';

class ChartLabView {
    constructor(section) {
        this.section = section;
        this.symbolSelect = section.querySelector('[data-chart-symbol]');
        this.timeframeButtons = section.querySelectorAll('[data-chart-timeframe]');
        this.indicatorInputs = section.querySelectorAll('[data-indicator]');
        this.analyzeButton = section.querySelector('[data-run-analysis]');
        this.canvas = section.querySelector('#chart-lab-canvas');
        this.insightsContainer = section.querySelector('[data-ai-insights]');
        this.chart = null;
        this.symbol = 'BTC';
        this.timeframe = '7d';
    }

    async init() {
        await this.loadChart();
        this.bindEvents();
    }

    bindEvents() {
        if (this.symbolSelect) {
            this.symbolSelect.addEventListener('change', async () => {
                this.symbol = this.symbolSelect.value;
                await this.loadChart();
            });
        }
        this.timeframeButtons.forEach((btn) => {
            btn.addEventListener('click', async () => {
                this.timeframeButtons.forEach((b) => b.classList.remove('active'));
                btn.classList.add('active');
                this.timeframe = btn.dataset.chartTimeframe;
                await this.loadChart();
            });
        });
        if (this.analyzeButton) {
            this.analyzeButton.addEventListener('click', () => this.runAnalysis());
        }
    }

    async loadChart() {
        if (!this.canvas) return;
        const result = await apiClient.getPriceChart(this.symbol, this.timeframe);
        const container = this.canvas.parentElement;
        if (!result.ok) {
            if (container) {
                let errorNode = container.querySelector('.chart-error');
                if (!errorNode) {
                    errorNode = document.createElement('div');
                    errorNode.className = 'inline-message inline-error chart-error';
                    container.appendChild(errorNode);
                }
                errorNode.textContent = result.error;
            }
            return;
        }
        if (container) {
            const errorNode = container.querySelector('.chart-error');
            if (errorNode) errorNode.remove();
        }
        const points = result.data || [];
        const labels = points.map((point) => point.time || point.timestamp || '');
        const prices = points.map((point) => point.price || point.close || point.value);
        if (this.chart) {
            this.chart.destroy();
        }
        this.chart = new Chart(this.canvas, {
            type: 'line',
            data: {
                labels,
                datasets: [
                    {
                        label: `${this.symbol} (${this.timeframe})`,
                        data: prices,
                        borderColor: '#f472b6',
                        backgroundColor: 'rgba(244, 114, 182, 0.2)',
                        fill: true,
                        tension: 0.4,
                    },
                ],
            },
            options: {
                scales: {
                    x: { ticks: { color: 'var(--text-muted)' } },
                    y: { ticks: { color: 'var(--text-muted)' } },
                },
                plugins: {
                    legend: { display: false },
                },
            },
        });
    }

    async runAnalysis() {
        if (!this.insightsContainer) return;
        const enabledIndicators = Array.from(this.indicatorInputs)
            .filter((input) => input.checked)
            .map((input) => input.value);
        this.insightsContainer.innerHTML = '<p>Running AI analysis...</p>';
        const payload = {
            query: `Analyze ${this.symbol} on ${this.timeframe} timeframe with indicators: ${enabledIndicators.join(', ')}`,
        };
        const result = await apiClient.runQuery(payload);
        if (!result.ok) {
            this.insightsContainer.innerHTML = `<div class="inline-message inline-error">${result.error}</div>`;
            return;
        }
        const data = result.data || {};
        const bullets = (data.insights || data.points || []).map((point) => `<li>${point}</li>`).join('');
        this.insightsContainer.innerHTML = `
            <h4>AI Insights</h4>
            <p><strong>Trend:</strong> ${data.trend || data.summary || 'N/A'}</p>
            <p><strong>Support:</strong> ${data.support || 'N/A'} • <strong>Resistance:</strong> ${data.resistance || 'N/A'}</p>
            <ul>${bullets || '<li>No specific insights returned.</li>'}</ul>
        `;
    }
}

export default ChartLabView;
