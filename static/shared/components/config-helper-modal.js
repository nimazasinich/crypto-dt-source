/**
 * Configuration Helper Modal
 * Shows users how to configure and use all backend services
 */

export class ConfigHelperModal {
  constructor() {
    this.modal = null;
    this.services = this.getServicesConfig();
  }

  getServicesConfig() {
    const baseUrl = window.location.origin;
    
    return [
      {
        name: 'Market Data API',
        category: 'Core Services',
        description: 'Real-time cryptocurrency market data',
        endpoints: [
          { method: 'GET', path: '/api/market/top', desc: 'Top cryptocurrencies' },
          { method: 'GET', path: '/api/market/trending', desc: 'Trending coins' },
          { method: 'GET', path: '/api/coins/top?limit=50', desc: 'Top coins with limit' }
        ],
        example: `fetch('${baseUrl}/api/market/top')
  .then(res => res.json())
  .then(data => console.log(data));`
      },
      {
        name: 'Sentiment Analysis API',
        category: 'AI Services',
        description: 'AI-powered sentiment analysis',
        endpoints: [
          { method: 'GET', path: '/api/sentiment/global', desc: 'Global market sentiment' },
          { method: 'GET', path: '/api/sentiment/asset/{symbol}', desc: 'Asset sentiment' },
          { method: 'POST', path: '/api/sentiment/analyze', desc: 'Analyze custom text' }
        ],
        example: `fetch('${baseUrl}/api/sentiment/global')
  .then(res => res.json())
  .then(data => console.log(data));`
      },
      {
        name: 'News Aggregator API',
        category: 'Data Services',
        description: 'Crypto news from multiple sources',
        endpoints: [
          { method: 'GET', path: '/api/news', desc: 'Latest crypto news' },
          { method: 'GET', path: '/api/news/latest?limit=10', desc: 'News with limit' },
          { method: 'GET', path: '/api/news?source=CoinDesk', desc: 'Filter by source' }
        ],
        example: `fetch('${baseUrl}/api/news?limit=10')
  .then(res => res.json())
  .then(data => console.log(data));`
      },
      {
        name: 'OHLCV Data API',
        category: 'Trading Data',
        description: 'Historical price data (OHLCV)',
        endpoints: [
          { method: 'GET', path: '/api/ohlcv/{symbol}', desc: 'OHLCV for symbol' },
          { method: 'GET', path: '/api/ohlcv/multi', desc: 'Multiple symbols' },
          { method: 'GET', path: '/api/market/ohlc?symbol=BTC', desc: 'OHLC data' }
        ],
        example: `fetch('${baseUrl}/api/ohlcv/bitcoin')
  .then(res => res.json())
  .then(data => console.log(data));`
      },
      {
        name: 'AI Models API',
        category: 'AI Services',
        description: 'AI model management and status',
        endpoints: [
          { method: 'GET', path: '/api/models/status', desc: 'Models status' },
          { method: 'GET', path: '/api/models/list', desc: 'List all models' },
          { method: 'GET', path: '/api/ai/signals', desc: 'AI trading signals' }
        ],
        example: `fetch('${baseUrl}/api/models/status')
  .then(res => res.json())
  .then(data => console.log(data));`
      },
      {
        name: 'Trading & Backtesting API',
        category: 'Trading Services',
        description: 'Smart trading and backtesting',
        endpoints: [
          { method: 'GET', path: '/api/trading/backtest', desc: 'Backtest strategy' },
          { method: 'GET', path: '/api/futures/positions', desc: 'Futures positions' },
          { method: 'POST', path: '/api/ai/decision', desc: 'AI trading decision' }
        ],
        example: `fetch('${baseUrl}/api/trading/backtest?symbol=BTC')
  .then(res => res.json())
  .then(data => console.log(data));`
      },
      {
        name: 'Multi-Source Fallback API',
        category: 'Advanced Services',
        description: '137+ data sources with fallback',
        endpoints: [
          { method: 'GET', path: '/api/multi-source/data/{symbol}', desc: 'Multi-source data' },
          { method: 'GET', path: '/api/sources/all', desc: 'All sources' },
          { method: 'GET', path: '/api/test-source/{source_id}', desc: 'Test source' }
        ],
        example: `fetch('${baseUrl}/api/sources/all')
  .then(res => res.json())
  .then(data => console.log(data));`
      },
      {
        name: 'Technical Analysis API',
        category: 'Analysis Services',
        description: 'Technical indicators and analysis',
        endpoints: [
          { method: 'GET', path: '/api/technical/quick/{symbol}', desc: 'Quick TA' },
          { method: 'GET', path: '/api/technical/comprehensive/{symbol}', desc: 'Full analysis' },
          { method: 'GET', path: '/api/technical/risk/{symbol}', desc: 'Risk assessment' }
        ],
        example: `fetch('${baseUrl}/api/technical/quick/bitcoin')
  .then(res => res.json())
  .then(data => console.log(data));`
      },
      {
        name: 'Resources API',
        category: 'System Services',
        description: 'API resources and statistics',
        endpoints: [
          { method: 'GET', path: '/api/resources/summary', desc: 'Resources summary' },
          { method: 'GET', path: '/api/resources/stats', desc: 'Detailed stats' },
          { method: 'GET', path: '/api/resources/apis', desc: 'All APIs list' }
        ],
        example: `fetch('${baseUrl}/api/resources/summary')
  .then(res => res.json())
  .then(data => console.log(data));`
      },
      {
        name: 'Real-Time Monitoring API',
        category: 'System Services',
        description: 'System monitoring and health',
        endpoints: [
          { method: 'GET', path: '/api/health', desc: 'Health check' },
          { method: 'GET', path: '/api/status', desc: 'System status' },
          { method: 'GET', path: '/api/monitoring/status', desc: 'Monitoring data' }
        ],
        example: `fetch('${baseUrl}/api/health')
  .then(res => res.json())
  .then(data => console.log(data));`
      }
    ];
  }

  show() {
    if (this.modal) {
      this.modal.style.display = 'flex';
      return;
    }

    this.modal = this.createModal();
    document.body.appendChild(this.modal);
  }

  hide() {
    if (this.modal) {
      this.modal.style.display = 'none';
    }
  }

  createModal() {
    const modal = document.createElement('div');
    modal.className = 'config-helper-modal';
    modal.innerHTML = `
      <div class="config-helper-overlay"></div>
      <div class="config-helper-content">
        <div class="config-helper-header">
          <h2>
            <svg width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <path d="M12 2v20M17 5H9.5a3.5 3.5 0 0 0 0 7h5a3.5 3.5 0 0 1 0 7H6"/>
            </svg>
            API Configuration Guide
          </h2>
          <button class="config-helper-close" aria-label="Close">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <line x1="18" y1="6" x2="6" y2="18"/>
              <line x1="6" y1="6" x2="18" y2="18"/>
            </svg>
          </button>
        </div>
        
        <div class="config-helper-body">
          <div class="config-helper-intro">
            <p>Copy and paste these configurations to use our services in your application.</p>
            <div class="config-helper-base-url">
              <strong>Base URL:</strong> 
              <code>${window.location.origin}</code>
              <button class="copy-btn" data-copy="${window.location.origin}">
                <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                  <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
                </svg>
              </button>
            </div>
          </div>

          <div class="config-helper-services">
            ${this.renderServices()}
          </div>
        </div>
      </div>
    `;

    // Event listeners
    modal.querySelector('.config-helper-close').addEventListener('click', () => this.hide());
    modal.querySelector('.config-helper-overlay').addEventListener('click', () => this.hide());
    
    // Copy buttons
    modal.querySelectorAll('.copy-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const text = btn.getAttribute('data-copy');
        this.copyToClipboard(text, btn);
      });
    });

    // Collapsible sections
    modal.querySelectorAll('.service-header').forEach(header => {
      header.addEventListener('click', () => {
        const service = header.parentElement;
        service.classList.toggle('expanded');
      });
    });

    return modal;
  }

  renderServices() {
    const categories = {};
    
    // Group by category
    this.services.forEach(service => {
      if (!categories[service.category]) {
        categories[service.category] = [];
      }
      categories[service.category].push(service);
    });

    return Object.entries(categories).map(([category, services]) => `
      <div class="service-category">
        <h3 class="category-title">${category}</h3>
        ${services.map(service => this.renderService(service)).join('')}
      </div>
    `).join('');
  }

  renderService(service) {
    return `
      <div class="service-item">
        <div class="service-header">
          <div class="service-title">
            <span class="service-name">${service.name}</span>
            <svg class="expand-icon" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="6 9 12 15 18 9"/>
            </svg>
          </div>
          <p class="service-desc">${service.description}</p>
        </div>
        
        <div class="service-details">
          <div class="endpoints-list">
            <h4>Endpoints:</h4>
            ${service.endpoints.map(ep => `
              <div class="endpoint-item">
                <span class="method-badge ${ep.method.toLowerCase()}">${ep.method}</span>
                <code class="endpoint-path">${ep.path}</code>
                <span class="endpoint-desc">${ep.desc}</span>
                <button class="copy-btn" data-copy="${window.location.origin}${ep.path}">
                  <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                    <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
                  </svg>
                </button>
              </div>
            `).join('')}
          </div>
          
          <div class="code-example">
            <div class="code-header">
              <span>Example Usage:</span>
              <button class="copy-btn" data-copy="${service.example}">
                <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                  <rect x="9" y="9" width="13" height="13" rx="2" ry="2"/>
                  <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/>
                </svg>
                Copy
              </button>
            </div>
            <pre><code>${this.escapeHtml(service.example)}</code></pre>
          </div>
        </div>
      </div>
    `;
  }

  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }

  async copyToClipboard(text, button) {
    try {
      await navigator.clipboard.writeText(text);
      
      // Visual feedback
      const originalHTML = button.innerHTML;
      button.innerHTML = `
        <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <polyline points="20 6 9 17 4 12"/>
        </svg>
      `;
      button.classList.add('copied');
      
      setTimeout(() => {
        button.innerHTML = originalHTML;
        button.classList.remove('copied');
      }, 2000);
    } catch (err) {
      console.error('Failed to copy:', err);
    }
  }
}

// Styles
const style = document.createElement('style');
style.textContent = `
  .config-helper-modal {
    position: fixed;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    z-index: 10000;
    display: flex;
    align-items: center;
    justify-content: center;
    padding: 20px;
  }

  .config-helper-overlay {
    position: absolute;
    top: 0;
    left: 0;
    right: 0;
    bottom: 0;
    background: rgba(0, 0, 0, 0.7);
    backdrop-filter: blur(4px);
  }

  .config-helper-content {
    position: relative;
    background: var(--bg-main, #ffffff);
    border-radius: 16px;
    max-width: 900px;
    width: 100%;
    max-height: 85vh;
    display: flex;
    flex-direction: column;
    box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
    animation: modalSlideIn 0.3s ease;
  }

  @keyframes modalSlideIn {
    from {
      opacity: 0;
      transform: translateY(-20px) scale(0.95);
    }
    to {
      opacity: 1;
      transform: translateY(0) scale(1);
    }
  }

  .config-helper-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    padding: 24px;
    border-bottom: 1px solid var(--border-light, #e5e7eb);
  }

  .config-helper-header h2 {
    display: flex;
    align-items: center;
    gap: 12px;
    margin: 0;
    font-size: 20px;
    font-weight: 600;
    color: var(--text-primary, #0f2926);
  }

  .config-helper-header svg {
    color: var(--teal, #14b8a6);
  }

  .config-helper-close {
    background: none;
    border: none;
    padding: 8px;
    cursor: pointer;
    border-radius: 8px;
    color: var(--text-muted, #6b7280);
    transition: all 0.2s;
  }

  .config-helper-close:hover {
    background: var(--bg-secondary, #f3f4f6);
    color: var(--text-primary, #0f2926);
  }

  .config-helper-body {
    overflow-y: auto;
    padding: 24px;
  }

  .config-helper-intro {
    margin-bottom: 24px;
  }

  .config-helper-intro p {
    color: var(--text-secondary, #6b7280);
    margin-bottom: 12px;
  }

  .config-helper-base-url {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 12px;
    background: var(--bg-secondary, #f3f4f6);
    border-radius: 8px;
    font-size: 14px;
  }

  .config-helper-base-url code {
    flex: 1;
    padding: 4px 8px;
    background: var(--bg-main, #ffffff);
    border-radius: 4px;
    font-family: 'Courier New', monospace;
    font-size: 13px;
  }

  .service-category {
    margin-bottom: 24px;
  }

  .category-title {
    font-size: 16px;
    font-weight: 600;
    color: var(--teal, #14b8a6);
    margin-bottom: 12px;
    padding-bottom: 8px;
    border-bottom: 2px solid var(--teal-light, #2dd4bf);
  }

  .service-item {
    background: var(--bg-secondary, #f8fdfc);
    border: 1px solid var(--border-light, #e5e7eb);
    border-radius: 12px;
    margin-bottom: 12px;
    overflow: hidden;
    transition: all 0.2s;
  }

  .service-item:hover {
    border-color: var(--teal-light, #2dd4bf);
  }

  .service-header {
    padding: 16px;
    cursor: pointer;
    user-select: none;
  }

  .service-title {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 4px;
  }

  .service-name {
    font-weight: 600;
    color: var(--text-primary, #0f2926);
    font-size: 15px;
  }

  .expand-icon {
    color: var(--text-muted, #6b7280);
    transition: transform 0.2s;
  }

  .service-item.expanded .expand-icon {
    transform: rotate(180deg);
  }

  .service-desc {
    color: var(--text-secondary, #6b7280);
    font-size: 13px;
    margin: 0;
  }

  .service-details {
    max-height: 0;
    overflow: hidden;
    transition: max-height 0.3s ease;
  }

  .service-item.expanded .service-details {
    max-height: 1000px;
  }

  .endpoints-list {
    padding: 0 16px 16px;
  }

  .endpoints-list h4 {
    font-size: 13px;
    font-weight: 600;
    color: var(--text-secondary, #6b7280);
    margin-bottom: 8px;
  }

  .endpoint-item {
    display: flex;
    align-items: center;
    gap: 8px;
    padding: 8px;
    background: var(--bg-main, #ffffff);
    border-radius: 6px;
    margin-bottom: 6px;
    font-size: 13px;
  }

  .method-badge {
    padding: 2px 8px;
    border-radius: 4px;
    font-weight: 600;
    font-size: 11px;
    text-transform: uppercase;
  }

  .method-badge.get {
    background: #10b981;
    color: white;
  }

  .method-badge.post {
    background: #3b82f6;
    color: white;
  }

  .endpoint-path {
    flex: 1;
    font-family: 'Courier New', monospace;
    font-size: 12px;
    color: var(--text-primary, #0f2926);
  }

  .endpoint-desc {
    color: var(--text-muted, #6b7280);
    font-size: 12px;
  }

  .code-example {
    padding: 0 16px 16px;
  }

  .code-header {
    display: flex;
    align-items: center;
    justify-content: space-between;
    margin-bottom: 8px;
    font-size: 13px;
    font-weight: 600;
    color: var(--text-secondary, #6b7280);
  }

  .code-example pre {
    background: #1e293b;
    color: #e2e8f0;
    padding: 12px;
    border-radius: 8px;
    overflow-x: auto;
    margin: 0;
    font-size: 12px;
    line-height: 1.6;
  }

  .copy-btn {
    background: var(--teal, #14b8a6);
    color: white;
    border: none;
    padding: 6px 12px;
    border-radius: 6px;
    cursor: pointer;
    display: inline-flex;
    align-items: center;
    gap: 4px;
    font-size: 12px;
    transition: all 0.2s;
  }

  .copy-btn:hover {
    background: var(--teal-dark, #0d7377);
    transform: translateY(-1px);
  }

  .copy-btn.copied {
    background: #10b981;
  }

  @media (max-width: 768px) {
    .config-helper-content {
      max-width: 100%;
      max-height: 95vh;
      margin: 10px;
    }

    .endpoint-item {
      flex-wrap: wrap;
    }

    .endpoint-desc {
      width: 100%;
      margin-top: 4px;
    }
  }
`;
document.head.appendChild(style);
