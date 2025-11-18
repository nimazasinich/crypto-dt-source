import apiClient from './apiClient.js';

class NewsView {
    constructor(section) {
        this.section = section;
        this.tableBody = section.querySelector('[data-news-body]');
        this.filterInput = section.querySelector('[data-news-search]');
        this.rangeSelect = section.querySelector('[data-news-range]');
        this.symbolFilter = section.querySelector('[data-news-symbol]');
        this.modalBackdrop = section.querySelector('[data-news-modal]');
        this.modalContent = section.querySelector('[data-news-modal-content]');
        this.closeModalBtn = section.querySelector('[data-close-news-modal]');
        this.dataset = [];
        this.datasetMap = new Map();
    }

    async init() {
        this.tableBody.innerHTML = '<tr><td colspan="6">Loading news...</td></tr>';
        await this.loadNews();
        this.bindEvents();
    }

    bindEvents() {
        if (this.filterInput) {
            this.filterInput.addEventListener('input', () => this.renderRows());
        }
        if (this.rangeSelect) {
            this.rangeSelect.addEventListener('change', () => this.renderRows());
        }
        if (this.symbolFilter) {
            this.symbolFilter.addEventListener('input', () => this.renderRows());
        }
        if (this.closeModalBtn) {
            this.closeModalBtn.addEventListener('click', () => this.hideModal());
        }
        if (this.modalBackdrop) {
            this.modalBackdrop.addEventListener('click', (event) => {
                if (event.target === this.modalBackdrop) {
                    this.hideModal();
                }
            });
        }
    }

    async loadNews() {
        const result = await apiClient.getLatestNews(40);
        if (!result.ok) {
            this.tableBody.innerHTML = `<tr><td colspan="6"><div class="inline-message inline-error">${result.error}</div></td></tr>`;
            return;
        }
        this.dataset = result.data || [];
        this.datasetMap.clear();
        this.dataset.forEach((item, index) => {
            const rowId = item.id || `${item.title}-${index}`;
            this.datasetMap.set(rowId, item);
        });
        this.renderRows();
    }

    renderRows() {
        const searchTerm = (this.filterInput?.value || '').toLowerCase();
        const symbolFilter = (this.symbolFilter?.value || '').toLowerCase();
        const range = this.rangeSelect?.value || '24h';
        const rangeMap = { '24h': 86_400_000, '7d': 604_800_000, '30d': 2_592_000_000 };
        const limit = rangeMap[range] || rangeMap['24h'];
        const filtered = this.dataset.filter((item) => {
            const matchesText = `${item.title} ${item.summary}`.toLowerCase().includes(searchTerm);
            const matchesSymbol = symbolFilter
                ? (item.symbols || []).some((symbol) => symbol.toLowerCase().includes(symbolFilter))
                : true;
            const published = new Date(item.published_at || item.date || Date.now()).getTime();
            const withinRange = Date.now() - published <= limit;
            return matchesText && matchesSymbol && withinRange;
        });
        if (!filtered.length) {
            this.tableBody.innerHTML = '<tr><td colspan="6">No news for selected filters.</td></tr>';
            return;
        }
        this.tableBody.innerHTML = filtered
            .map((news, index) => {
                const rowId = news.id || `${news.title}-${index}`;
                this.datasetMap.set(rowId, news);
                return `
                <tr data-news-id="${rowId}">
                    <td>${new Date(news.published_at || news.date).toLocaleString()}</td>
                    <td>${news.source || 'N/A'}</td>
                    <td>${news.title}</td>
                    <td>${(news.symbols || []).map((s) => `<span class="chip">${s}</span>`).join(' ')}</td>
                    <td><span class="badge ${this.getSentimentClass(news.sentiment)}">${news.sentiment || 'Unknown'}</span></td>
                    <td>
                        <button class="ghost" data-news-summarize="${rowId}">Summarize</button>
                    </td>
                </tr>
            `;
            })
            .join('');
        this.section.querySelectorAll('tr[data-news-id]').forEach((row) => {
            row.addEventListener('click', () => {
                const id = row.dataset.newsId;
                const item = this.datasetMap.get(id);
                if (item) {
                    this.showModal(item);
                }
            });
        });
        this.section.querySelectorAll('[data-news-summarize]').forEach((button) => {
            button.addEventListener('click', (event) => {
                event.stopPropagation();
                const { newsSummarize } = button.dataset;
                this.summarizeArticle(newsSummarize, button);
            });
        });
    }

    getSentimentClass(sentiment) {
        switch ((sentiment || '').toLowerCase()) {
            case 'bullish':
                return 'badge-success';
            case 'bearish':
                return 'badge-danger';
            default:
                return 'badge-neutral';
        }
    }

    async summarizeArticle(rowId, button) {
        const item = this.datasetMap.get(rowId);
        if (!item || !button) return;
        button.disabled = true;
        const original = button.textContent;
        button.textContent = 'Summarizing…';
        const payload = {
            title: item.title,
            body: item.body || item.summary || item.description || '',
            source: item.source || '',
        };
        const result = await apiClient.summarizeNews(payload);
        button.disabled = false;
        button.textContent = original;
        if (!result.ok) {
            this.showModal(item, null, result.error);
            return;
        }
        this.showModal(item, result.data?.analysis || result.data);
    }

    async showModal(item, analysis = null, errorMessage = null) {
        if (!this.modalContent) return;
        this.modalBackdrop.classList.add('active');
        this.modalContent.innerHTML = `
            <h3>${item.title}</h3>
            <p class="text-muted">${new Date(item.published_at || item.date).toLocaleString()} • ${item.source || ''}</p>
            <p>${item.summary || item.description || ''}</p>
            <div class="chip-row">${(item.symbols || []).map((s) => `<span class="chip">${s}</span>`).join('')}</div>
            <div class="ai-block">${analysis ? '' : errorMessage ? '' : 'Click Summarize to run AI insights.'}</div>
        `;
        const aiBlock = this.modalContent.querySelector('.ai-block');
        if (!aiBlock) return;
        if (errorMessage) {
            aiBlock.innerHTML = `<div class="inline-message inline-error">${errorMessage}</div>`;
            return;
        }
        if (!analysis) {
            aiBlock.innerHTML = '<div class="inline-message inline-info">Use the Summarize button to request AI analysis.</div>';
            return;
        }
        const sentiment = analysis.sentiment || analysis.analysis?.sentiment;
        aiBlock.innerHTML = `
            <h4>AI Summary</h4>
            <p>${analysis.summary || analysis.analysis?.summary || 'Model returned no summary.'}</p>
            <p><strong>Sentiment:</strong> ${sentiment?.label || sentiment || 'Unknown'} (${sentiment?.score ?? ''})</p>
        `;
    }

    hideModal() {
        if (this.modalBackdrop) {
            this.modalBackdrop.classList.remove('active');
        }
    }
}

export default NewsView;
