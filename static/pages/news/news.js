/**
 * News Page
 * Displays cryptocurrency news with AI summarization
 */

import { api } from '../../shared/js/core/api-client.js';
import { pollingManager } from '../../shared/js/core/polling-manager.js';
import { LayoutManager } from '../../shared/js/core/layout-manager.js';
import { Toast } from '../../shared/js/components/toast.js';

class NewsPage {
  constructor() {
    this.news = [];
    this.filteredNews = [];
    this.sources = new Set();
  }

  async init() {
    try {
      await LayoutManager.injectLayouts();
      LayoutManager.setActiveNav('news');
      
      this.bindEvents();
      await this.loadData();
      this.setupPolling();
    } catch (error) {
      console.error('[News] Init error:', error);
      Toast.error('Failed to initialize news page');
    }
  }

  bindEvents() {
    document.getElementById('refresh-btn')?.addEventListener('click', () => this.loadData());
    document.getElementById('search-input')?.addEventListener('input', () => this.filterNews());
    document.getElementById('source-select')?.addEventListener('change', () => this.filterNews());
    document.getElementById('sentiment-select')?.addEventListener('change', () => this.filterNews());
    
    // Modal close
    document.querySelector('.modal-close')?.addEventListener('click', () => this.closeModal());
    document.querySelector('.modal-backdrop')?.addEventListener('click', () => this.closeModal());
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') this.closeModal();
    });
  }

  async loadData() {
    try {
      const list = document.getElementById('news-list');
      list.innerHTML = '<div class="loading-container"><div class="spinner"></div><p>Loading news...</p></div>';
      
      const data = await api.getLatestNews(50);
      this.news = data.articles || data.news || [];
      this.filteredNews = [...this.news];
      
      // Extract unique sources
      this.sources = new Set(this.news.map(n => n.source).filter(Boolean));
      this.populateSources();
      
      this.renderStats();
      this.renderNews();
      this.updateLastUpdate();
      
    } catch (error) {
      console.error('[News] Load error:', error);
      Toast.error('Failed to load news');
      document.getElementById('news-list').innerHTML = `
        <div class="empty-state">
          <p>Failed to load news. Please try again.</p>
        </div>
      `;
    }
  }

  populateSources() {
    const select = document.getElementById('source-select');
    select.innerHTML = '<option value="">All Sources</option>';
    this.sources.forEach(source => {
      select.innerHTML += `<option value="${source}">${source}</option>`;
    });
  }

  renderStats() {
    const total = this.news.length;
    const positive = this.news.filter(n => n.sentiment === 'positive' || n.sentiment_score > 0.3).length;
    const negative = this.news.filter(n => n.sentiment === 'negative' || n.sentiment_score < -0.3).length;
    const neutral = total - positive - negative;

    document.getElementById('total-articles').textContent = total;
    document.getElementById('positive-count').textContent = positive;
    document.getElementById('neutral-count').textContent = neutral;
    document.getElementById('negative-count').textContent = negative;
  }

  renderNews() {
    const list = document.getElementById('news-list');
    
    if (this.filteredNews.length === 0) {
      list.innerHTML = `
        <div class="empty-state">
          <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 22h16a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v16a2 2 0 0 1-2 2Zm0 0a2 2 0 0 1-2-2v-9c0-1.1.9-2 2-2h2"></path></svg>
          <p>No news articles found</p>
        </div>
      `;
      return;
    }

    list.innerHTML = this.filteredNews.map((article, index) => `
      <article class="news-card" data-index="${index}">
        <div class="news-header">
          <span class="news-source">${article.source || 'Unknown'}</span>
          <span class="news-date">${this.formatDate(article.published_at || article.date)}</span>
          ${article.sentiment ? `<span class="badge badge-${this.getSentimentClass(article)}">${article.sentiment}</span>` : ''}
        </div>
        <h3 class="news-title">${article.title}</h3>
        <p class="news-excerpt">${article.description || article.content?.substring(0, 150) || ''}</p>
        <div class="news-footer">
          <div class="news-tags">
            ${(article.tags || article.coins || []).slice(0, 3).map(tag => `<span class="tag">${tag}</span>`).join('')}
          </div>
          <div class="news-actions">
            <button class="btn btn-sm btn-secondary" onclick="window.newsPage.summarize(${index})">
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 4.44-2z"></path><path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-4.44-2z"></path></svg>
              Summarize
            </button>
            ${article.url ? `
              <a href="${article.url}" target="_blank" rel="noopener" class="btn btn-sm btn-primary">
                <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line></svg>
                Read
              </a>
            ` : ''}
          </div>
        </div>
      </article>
    `).join('');
  }

  filterNews() {
    const search = document.getElementById('search-input').value.toLowerCase();
    const source = document.getElementById('source-select').value;
    const sentiment = document.getElementById('sentiment-select').value;

    this.filteredNews = this.news.filter(article => {
      const matchesSearch = !search || 
        article.title?.toLowerCase().includes(search) ||
        article.description?.toLowerCase().includes(search);
      const matchesSource = !source || article.source === source;
      const matchesSentiment = !sentiment || article.sentiment === sentiment;
      
      return matchesSearch && matchesSource && matchesSentiment;
    });

    this.renderNews();
  }

  getSentimentClass(article) {
    if (article.sentiment === 'positive' || article.sentiment_score > 0.3) return 'success';
    if (article.sentiment === 'negative' || article.sentiment_score < -0.3) return 'error';
    return 'secondary';
  }

  formatDate(dateStr) {
    if (!dateStr) return '';
    const date = new Date(dateStr);
    const now = new Date();
    const diff = now - date;
    
    if (diff < 3600000) return `${Math.floor(diff / 60000)}m ago`;
    if (diff < 86400000) return `${Math.floor(diff / 3600000)}h ago`;
    return date.toLocaleDateString();
  }

  async summarize(index) {
    const article = this.filteredNews[index];
    if (!article) return;

    const modal = document.getElementById('summarize-modal');
    const body = document.getElementById('modal-body');
    
    modal.classList.add('active');
    modal.setAttribute('aria-hidden', 'false');
    body.innerHTML = '<div class="loading-container"><div class="spinner"></div><p>Generating AI summary...</p></div>';

    try {
      const result = await api.summarizeNews(article.title, article.content || article.description);
      
      body.innerHTML = `
        <div class="summary-content">
          <h4>${article.title}</h4>
          <div class="summary-text">${result.summary || result.text || 'No summary available'}</div>
          ${result.key_points ? `
            <div class="key-points">
              <h5>Key Points:</h5>
              <ul>
                ${result.key_points.map(p => `<li>${p}</li>`).join('')}
              </ul>
            </div>
          ` : ''}
          ${result.sentiment ? `
            <div class="sentiment-analysis">
              <span class="badge badge-${this.getSentimentClass(result)}">Sentiment: ${result.sentiment}</span>
            </div>
          ` : ''}
        </div>
      `;
    } catch (error) {
      body.innerHTML = `
        <div class="error-state">
          <p>Failed to generate summary. Please try again.</p>
        </div>
      `;
      Toast.error('Failed to generate summary');
    }
  }

  closeModal() {
    const modal = document.getElementById('summarize-modal');
    modal.classList.remove('active');
    modal.setAttribute('aria-hidden', 'true');
  }

  setupPolling() {
    pollingManager.start(
      'news-data',
      () => api.getLatestNews(50),
      (data, error) => {
        if (data) {
          this.news = data.articles || data.news || [];
          this.filterNews();
          this.renderStats();
          this.updateLastUpdate();
        }
      },
      120000 // 2 minutes
    );
  }

  updateLastUpdate() {
    const el = document.getElementById('last-update');
    if (el) {
      el.textContent = `Updated: ${new Date().toLocaleTimeString()}`;
    }
  }

  destroy() {
    pollingManager.stop('news-data');
  }
}

// Initialize page
const page = new NewsPage();
window.newsPage = page;

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => page.init());
} else {
  page.init();
}

window.addEventListener('beforeunload', () => page.destroy());
