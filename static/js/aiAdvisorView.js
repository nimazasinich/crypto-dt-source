import apiClient from './apiClient.js';

class AIAdvisorView {
    constructor(section) {
        this.section = section;
        this.form = section.querySelector('[data-ai-form]');
        this.resultContainer = section.querySelector('[data-ai-result]');
        this.disclaimer = section.querySelector('[data-ai-disclaimer]');
    }

    init() {
        if (!this.form) return;
        this.form.addEventListener('submit', async (event) => {
            event.preventDefault();
            const formData = new FormData(this.form);
            const payload = {
                query: 'trade_advice',
                symbol: formData.get('symbol'),
                horizon: formData.get('horizon'),
                risk: formData.get('risk'),
                context: formData.get('context') || '',
            };
            this.resultContainer.innerHTML = '<p>Generating AI guidance...</p>';
            const result = await apiClient.runQuery(payload);
            if (!result.ok) {
                this.resultContainer.innerHTML = `<div class="inline-message inline-error">${result.error}</div>`;
                return;
            }
            const data = result.data || {};
            this.renderResult(data);
        });
    }

    renderResult(data) {
        const action = (data.action || 'HOLD').toUpperCase();
        this.resultContainer.innerHTML = `
            <div class="ai-result">
                <div class="action-badge action-${action.toLowerCase()}">${action}</div>
                <p><strong>Confidence:</strong> ${data.confidence ? `${(data.confidence * 100).toFixed(1)}%` : 'N/A'}</p>
                <p><strong>Suggested Horizon:</strong> ${data.horizon || 'N/A'}</p>
                <p><strong>Risk Profile:</strong> ${data.risk || 'N/A'}</p>
                <ul>${(data.reasons || []).map((reason) => `<li>${reason}</li>`).join('') || '<li>No reasoning provided.</li>'}</ul>
                <p>${data.summary || data.analysis || ''}</p>
            </div>
        `;
        if (this.disclaimer) {
            this.disclaimer.textContent = data.disclaimer || 'This is experimental AI research, not financial advice.';
        }
    }
}

export default AIAdvisorView;
