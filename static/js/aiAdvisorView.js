import apiClient from './apiClient.js';
import { formatCurrency, formatPercent } from './uiUtils.js';

class AIAdvisorView {
    constructor(section) {
        this.section = section;
        this.form = section?.querySelector('[data-ai-form]');
        this.decisionContainer = section?.querySelector('[data-ai-result]');
        this.sentimentContainer = section?.querySelector('[data-sentiment-result]');
        this.disclaimer = section?.querySelector('[data-ai-disclaimer]');
        this.contextInput = section?.querySelector('textarea[name="context"]');
        this.modelSelect = section?.querySelector('select[name="model"]');
    }

    init() {
        if (!this.form) return;
        this.form.addEventListener('submit', async (event) => {
            event.preventDefault();
            const formData = new FormData(this.form);
            await this.handleSubmit(formData);
        });
    }

    async handleSubmit(formData) {
        const symbol = formData.get('symbol') || 'BTC';
        const horizon = formData.get('horizon') || 'swing';
        const risk = formData.get('risk') || 'moderate';
        const context = (formData.get('context') || '').trim();
        const mode = formData.get('model') || 'auto';

        if (this.decisionContainer) {
            this.decisionContainer.innerHTML = '<p>Generating AI strategy...</p>';
        }
        if (this.sentimentContainer && context) {
            this.sentimentContainer.innerHTML = '<p>Running sentiment model...</p>';
        }

        const decisionPayload = {
            query: `Provide ${horizon} outlook for ${symbol} with ${risk} risk. ${context}`,
            symbol,
            task: 'decision',
            options: { horizon, risk },
        };

        const jobs = [apiClient.runQuery(decisionPayload)];
        if (context) {
            jobs.push(apiClient.analyzeSentiment({ text: context, mode }));
        }

        const [decisionResult, sentimentResult] = await Promise.all(jobs);

        if (!decisionResult.ok) {
            this.decisionContainer.innerHTML = `<div class="inline-message inline-error">${decisionResult.error}</div>`;
        } else {
            this.renderDecisionResult(decisionResult.data || {});
        }

        if (context && this.sentimentContainer) {
            if (!sentimentResult?.ok) {
                this.sentimentContainer.innerHTML = `<div class="inline-message inline-error">${sentimentResult?.error || 'AI sentiment endpoint unavailable'}</div>`;
            } else {
                this.renderSentimentResult(sentimentResult.data || sentimentResult);
            }
        }
    }

    renderDecisionResult(response) {
        if (!this.decisionContainer) return;
        const payload = response.data || {};
        const analysis = payload.analysis || payload;
        const summary = analysis.summary?.summary || analysis.summary || 'No summary provided.';
        const signals = analysis.signals || {};
        const topCoins = (payload.top_coins || []).slice(0, 3);

        this.decisionContainer.innerHTML = `
            <div class="ai-result">
                <p class="text-muted">${response.message || 'Decision support summary'}</p>
                <p>${summary}</p>
                <div class="grid-two">
                    <div>
                        <h4>Market Signals</h4>
                        <ul>
                            ${Object.entries(signals)
                                .map(([, value]) => `<li>${value?.label || 'neutral'} (${value?.score ?? '—'})</li>`)
                                .join('') || '<li>No model signals.</li>'}
                        </ul>
                    </div>
                    <div>
                        <h4>Watchlist</h4>
                        <ul>
                            ${topCoins
                                .map(
                                    (coin) =>
                                        `<li>${coin.symbol || coin.ticker}: ${formatCurrency(coin.price)} (${formatPercent(coin.change_24h)})</li>`,
                                )
                                .join('') || '<li>No coin highlights.</li>'}
                        </ul>
                    </div>
                </div>
            </div>
        `;
        if (this.disclaimer) {
            this.disclaimer.textContent =
                response.data?.disclaimer || 'This AI output is experimental research and not financial advice.';
        }
    }

    renderSentimentResult(result) {
        const container = this.sentimentContainer;
        if (!container) return;
        const payload = result.result || result;
        const signals = result.signals || payload.signals || {};
        container.innerHTML = `
            <div class="glass-card">
                <h4>Sentiment (${result.mode || 'auto'})</h4>
                <p><strong>Label:</strong> ${payload.label || payload.classification || 'neutral'}</p>
                <p><strong>Score:</strong> ${payload.score ?? payload.sentiment?.score ?? '—'}</p>
                <div class="chip-row">
                    ${Object.entries(signals)
                        .map(([key, value]) => `<span class="chip">${key}: ${value?.label || 'n/a'}</span>`)
                        .join('') || ''}
                </div>
                <p>${payload.summary?.summary || payload.summary?.summary_text || payload.summary || ''}</p>
            </div>
        `;
    }
}

export default AIAdvisorView;
