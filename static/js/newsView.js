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
            .map(
                (news) => `
                <tr data-news-id="${news.id || news.title}">
                    <td>${new Date(news.published_at || news.date).toLocaleString()}</td>
                    <td>${news.source || 'N/A'}</td>
                    <td>${news.title}</td>
                    <td>${(news.symbols || []).map((s) => `<span class="chip">${s}</span>`).join(' ')}</td>
                    <td><span class="badge ${this.getSentimentClass(news.sentiment)}">${news.sentiment || 'Unknown'}</span></td>
                    <td>${news.impact || '—'}</td>
                </tr>
            `,
            )
            .join('');
        this.section.querySelectorAll('tr[data-news-id]').forEach((row) => {
            row.addEventListener('click', () => {
                const id = row.dataset.newsId;
                const item = filtered.find((news) => (news.id || news.title) === id);
                if (item) {
                    this.showModal(item);
                }
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

    async showModal(item) {
        if (!this.modalContent) return;
        this.modalBackdrop.classList.add('active');
        this.modalContent.innerHTML = `
            <h3>${item.title}</h3>
            <p class="text-muted">${new Date(item.published_at || item.date).toLocaleString()} • ${item.source || ''}</p>
            <p>${item.summary || item.description || ''}</p>
            <div class="chip-row">${(item.symbols || []).map((s) => `<span class="chip">${s}</span>`).join('')}</div>
            <div class="ai-block">Analyzing…</div>
        `;
        const result = await apiClient.runQuery({ query: `Summarize sentiment for: ${item.title}` });
        const aiBlock = this.modalContent.querySelector('.ai-block');
        if (!aiBlock) return;
        if (!result.ok) {
            aiBlock.innerHTML = `<div class="inline-message inline-warn">${result.error}</div>`;
        } else {
            const data = result.data || {};
            aiBlock.innerHTML = `
                <h4>AI Summary</h4>
                <p>${data.summary || data.result || 'Model returned no summary.'}</p>
                <p><strong>Sentiment:</strong> ${data.sentiment || 'Unknown'}</p>
            `;
        }
    }

    hideModal() {
        if (this.modalBackdrop) {
            this.modalBackdrop.classList.remove('active');
        }
    }
}

export default NewsView;
