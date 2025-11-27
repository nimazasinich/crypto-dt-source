/**
 * Sentiment Analysis Page
 * AI-powered market sentiment analysis
 */

import { api } from '../../shared/js/core/api-client.js';
import { LayoutManager } from '../../shared/js/core/layout-manager.js';
import { Toast } from '../../shared/js/components/toast.js';

class SentimentPage {
  constructor() {
    this.activeTab = 'global';
  }

  async init() {
    try {
      await LayoutManager.injectLayouts();
      LayoutManager.setActiveNav('sentiment');
      
      this.bindEvents();
      await this.loadGlobalSentiment();
    } catch (error) {
      console.error('[Sentiment] Init error:', error);
      Toast.error('Failed to initialize sentiment page');
    }
  }

  bindEvents() {
    // Tab switching
    document.querySelectorAll('.tab').forEach(tab => {
      tab.addEventListener('click', (e) => this.switchTab(e.target.closest('.tab').dataset.tab));
    });

    // Global refresh
    document.getElementById('refresh-global')?.addEventListener('click', () => this.loadGlobalSentiment());

    // Asset analysis
    document.getElementById('analyze-asset')?.addEventListener('click', () => this.analyzeAsset());
    document.getElementById('asset-input')?.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') this.analyzeAsset();
    });

    // Text analysis
    document.getElementById('analyze-text')?.addEventListener('click', () => this.analyzeText());
  }

  switchTab(tabId) {
    this.activeTab = tabId;

    // Update tab buttons
    document.querySelectorAll('.tab').forEach(tab => {
      tab.classList.toggle('active', tab.dataset.tab === tabId);
    });

    // Update tab panes
    document.querySelectorAll('.tab-pane').forEach(pane => {
      pane.classList.toggle('active', pane.id === `tab-${tabId}`);
    });
  }

  async loadGlobalSentiment() {
    const container = document.getElementById('global-content');
    container.innerHTML = '<div class="loading-container"><div class="spinner"></div><p>Loading sentiment data...</p></div>';

    try {
      const data = await api.getGlobalSentiment();
      this.renderGlobalSentiment(data);
    } catch (error) {
      console.error('[Sentiment] Global error:', error);
      container.innerHTML = `
        <div class="error-state">
          <p>Failed to load global sentiment</p>
          <button class="btn btn-primary" onclick="window.sentimentPage.loadGlobalSentiment()">Retry</button>
        </div>
      `;
    }
  }

  renderGlobalSentiment(data) {
    const container = document.getElementById('global-content');
    const sentiment = data.sentiment || data.overall || 'neutral';
    const score = data.score || data.sentiment_score || 0.5;
    const fear_greed = data.fear_greed_index || data.fearGreedIndex || 50;

    container.innerHTML = `
      <div class="global-sentiment">
        <div class="sentiment-gauge ${this.getSentimentClass(sentiment)}">
          <div class="gauge-circle">
            <div class="gauge-fill" style="--percent: ${score * 100}%"></div>
            <div class="gauge-value">${(score * 100).toFixed(0)}</div>
          </div>
          <div class="gauge-label">${this.getSentimentLabel(sentiment)}</div>
        </div>

        <div class="sentiment-details">
          <div class="detail-item">
            <span class="detail-label">Fear & Greed Index</span>
            <div class="fear-greed-bar">
              <div class="bar-fill" style="width: ${fear_greed}%"></div>
              <span class="bar-value">${fear_greed}</span>
            </div>
            <span class="detail-desc">${this.getFearGreedLabel(fear_greed)}</span>
          </div>

          ${data.social_sentiment ? `
            <div class="detail-item">
              <span class="detail-label">Social Sentiment</span>
              <span class="detail-value ${data.social_sentiment.trend === 'up' ? 'positive' : data.social_sentiment.trend === 'down' ? 'negative' : ''}">${data.social_sentiment.score || '--'}</span>
            </div>
          ` : ''}

          ${data.market_trend ? `
            <div class="detail-item">
              <span class="detail-label">Market Trend</span>
              <span class="detail-value ${data.market_trend === 'bullish' ? 'positive' : data.market_trend === 'bearish' ? 'negative' : ''}">${data.market_trend}</span>
            </div>
          ` : ''}
        </div>

        ${data.top_mentions && data.top_mentions.length > 0 ? `
          <div class="top-mentions">
            <h4>Most Mentioned Assets</h4>
            <div class="mentions-list">
              ${data.top_mentions.slice(0, 5).map(m => `
                <div class="mention-item">
                  <span class="mention-symbol">${m.symbol}</span>
                  <span class="mention-count">${m.count} mentions</span>
                  <span class="mention-sentiment ${this.getSentimentClass(m.sentiment)}">${m.sentiment || 'neutral'}</span>
                </div>
              `).join('')}
            </div>
          </div>
        ` : ''}
      </div>
    `;
  }

  async analyzeAsset() {
    const symbol = document.getElementById('asset-input').value.trim().toUpperCase();
    if (!symbol) {
      Toast.error('Please enter a cryptocurrency symbol');
      return;
    }

    const container = document.getElementById('asset-results');
    container.innerHTML = '<div class="loading-container"><div class="spinner"></div><p>Analyzing sentiment...</p></div>';

    try {
      const result = await api.analyzeSentiment(symbol, 'crypto');
      this.renderSentimentResult(container, result, symbol);
      Toast.success(`Sentiment analysis complete for ${symbol}`);
    } catch (error) {
      console.error('[Sentiment] Asset analysis error:', error);
      container.innerHTML = `<div class="error-state"><p>Analysis failed: ${error.message}</p></div>`;
      Toast.error('Analysis failed');
    }
  }

  async analyzeText() {
    const text = document.getElementById('text-input').value.trim();
    const mode = document.getElementById('mode-select').value;

    if (!text) {
      Toast.error('Please enter text to analyze');
      return;
    }

    const container = document.getElementById('text-results');
    container.innerHTML = '<div class="loading-container"><div class="spinner"></div><p>Analyzing text...</p></div>';

    try {
      const result = await api.analyzeSentiment(text, mode);
      this.renderSentimentResult(container, result);
      Toast.success('Text analysis complete');
    } catch (error) {
      console.error('[Sentiment] Text analysis error:', error);
      container.innerHTML = `<div class="error-state"><p>Analysis failed: ${error.message}</p></div>`;
      Toast.error('Analysis failed');
    }
  }

  renderSentimentResult(container, result, symbol = null) {
    const sentiment = result.sentiment || result.label || 'neutral';
    const score = result.score || result.confidence || 0.5;

    container.innerHTML = `
      <div class="sentiment-result ${this.getSentimentClass(sentiment)}">
        ${symbol ? `<div class="result-symbol">${symbol}</div>` : ''}
        
        <div class="result-main">
          <div class="result-sentiment">${this.getSentimentLabel(sentiment)}</div>
          <div class="result-score">
            <span class="score-value">${(score * 100).toFixed(0)}%</span>
            <span class="score-label">Confidence</span>
          </div>
        </div>

        <div class="score-bar">
          <div class="bar negative" style="width: ${sentiment === 'negative' ? score * 100 : (1 - score) * 50}%"></div>
          <div class="bar neutral" style="width: ${sentiment === 'neutral' ? score * 100 : 10}%"></div>
          <div class="bar positive" style="width: ${sentiment === 'positive' ? score * 100 : (1 - score) * 50}%"></div>
        </div>

        ${result.details || result.breakdown ? `
          <div class="result-details">
            <h4>Breakdown</h4>
            ${Object.entries(result.details || result.breakdown).map(([key, value]) => `
              <div class="detail-row">
                <span class="detail-key">${key}</span>
                <span class="detail-value">${typeof value === 'number' ? (value * 100).toFixed(1) + '%' : value}</span>
              </div>
            `).join('')}
          </div>
        ` : ''}

        ${result.keywords && result.keywords.length > 0 ? `
          <div class="result-keywords">
            <h4>Key Terms</h4>
            <div class="keywords-list">
              ${result.keywords.map(k => `<span class="keyword">${k}</span>`).join('')}
            </div>
          </div>
        ` : ''}
      </div>
    `;
  }

  getSentimentClass(sentiment) {
    if (!sentiment) return 'neutral';
    const s = sentiment.toLowerCase();
    if (s.includes('positive') || s.includes('bullish')) return 'positive';
    if (s.includes('negative') || s.includes('bearish')) return 'negative';
    return 'neutral';
  }

  getSentimentLabel(sentiment) {
    if (!sentiment) return 'Neutral';
    return sentiment.charAt(0).toUpperCase() + sentiment.slice(1);
  }

  getFearGreedLabel(index) {
    if (index <= 20) return 'Extreme Fear';
    if (index <= 40) return 'Fear';
    if (index <= 60) return 'Neutral';
    if (index <= 80) return 'Greed';
    return 'Extreme Greed';
  }
}

// Initialize page
const page = new SentimentPage();
window.sentimentPage = page;

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => page.init());
} else {
  page.init();
}
