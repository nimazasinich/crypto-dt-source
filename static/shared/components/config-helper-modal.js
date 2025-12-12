/**
 * Configuration Helper Modal - Updated with All Services
 * Shows users how to configure and use all backend services
 * 
 * Services Include:
 * - Market Data (8+ providers)
 * - News (9+ sources)
 * - Sentiment Analysis (4+ providers)
 * - On-Chain Analytics (4+ providers)
 * - DeFi Data (3+ providers)
 * - Technical Analysis
 * - AI Models
 * - Block Explorers
 */

export class ConfigHelperModal {
  constructor() {
    this.modal = null;
    this.services = this.getServicesConfig();
  }

  getServicesConfig() {
    const baseUrl = window.location.origin;
    
    return [
      // ===== UNIFIED SERVICE API =====
      {
        name: 'Unified Service API',
        category: 'Core Services',
        description: 'Single entry point for all cryptocurrency data needs',
        endpoints: [
          { method: 'GET', path: '/api/service/rate?pair=BTC/USDT', desc: 'Get exchange rate' },
          { method: 'GET', path: '/api/service/rate/batch?pairs=BTC/USDT,ETH/USDT', desc: 'Multiple rates' },
          { method: 'GET', path: '/api/service/market-status', desc: 'Market overview' },
          { method: 'GET', path: '/api/service/top?n=10', desc: 'Top cryptocurrencies' },
          { method: 'GET', path: '/api/service/sentiment?symbol=BTC', desc: 'Get sentiment' },
          { method: 'GET', path: '/api/service/whales?chain=ethereum&min_amount_usd=1000000', desc: 'Whale transactions' },
          { method: 'GET', path: '/api/service/onchain?address=0x...&chain=ethereum', desc: 'On-chain data' },
          { method: 'POST', path: '/api/service/query', desc: 'Universal query endpoint' }
        ],
        example: `// Get BTC price
fetch('${baseUrl}/api/service/rate?pair=BTC/USDT')
  .then(res => res.json())
  .then(data => console.log('BTC Price:', data.data.price));

// Get multiple prices
fetch('${baseUrl}/api/service/rate/batch?pairs=BTC/USDT,ETH/USDT,BNB/USDT')
  .then(res => res.json())
  .then(data => data.data.forEach(r => console.log(r.pair + ': $' + r.price)));`
      },
      
      // ===== MARKET DATA =====
      {
        name: 'Market Data API',
        category: 'Market Data',
        description: 'Real-time prices, OHLCV, and market statistics from 8+ providers',
        endpoints: [
          { method: 'GET', path: '/api/market?limit=100', desc: 'Market data with prices' },
          { method: 'GET', path: '/api/ohlcv?symbol=BTC&timeframe=1h&limit=500', desc: 'OHLCV candlestick data' },
          { method: 'GET', path: '/api/klines?symbol=BTCUSDT&interval=1h', desc: 'Klines (alias for OHLCV)' },
          { method: 'GET', path: '/api/historical?symbol=BTC&days=30', desc: 'Historical price data' },
          { method: 'GET', path: '/api/coins/top?limit=50', desc: 'Top coins by market cap' },
          { method: 'GET', path: '/api/trending', desc: 'Trending cryptocurrencies' }
        ],
        example: `// Get OHLCV data for charting
fetch('${baseUrl}/api/ohlcv?symbol=BTC&timeframe=1h&limit=100')
  .then(res => res.json())
  .then(data => {
    console.log('OHLCV data:', data.data);
    // Each candle: { t, o, h, l, c, v }
  });`
      },
      
      // ===== NEWS =====
      {
        name: 'News Aggregator API',
        category: 'News & Media',
        description: 'Crypto news from 9+ sources including RSS feeds',
        endpoints: [
          { method: 'GET', path: '/api/news?limit=20', desc: 'Latest crypto news' },
          { method: 'GET', path: '/api/news/latest?symbol=BTC&limit=10', desc: 'News filtered by symbol' },
          { method: 'GET', path: '/api/news?source=decrypt', desc: 'News from specific source' }
        ],
        example: `// Get latest news
fetch('${baseUrl}/api/news?limit=10')
  .then(res => res.json())
  .then(data => {
    data.articles.forEach(article => {
      console.log(article.title, '-', article.source);
    });
  });`
      },
      
      // ===== SENTIMENT =====
      {
        name: 'Sentiment Analysis API',
        category: 'Sentiment',
        description: 'Fear & Greed Index, social sentiment, and AI-powered analysis',
        endpoints: [
          { method: 'GET', path: '/api/sentiment/global', desc: 'Global market sentiment' },
          { method: 'GET', path: '/api/fear-greed', desc: 'Fear & Greed Index' },
          { method: 'GET', path: '/api/sentiment/asset/{symbol}', desc: 'Asset-specific sentiment' },
          { method: 'POST', path: '/api/sentiment/analyze', desc: 'Analyze custom text' }
        ],
        example: `// Get Fear & Greed Index
fetch('${baseUrl}/api/fear-greed')
  .then(res => res.json())
  .then(data => {
    console.log('Fear & Greed:', data.value, '-', data.classification);
  });

// Analyze text sentiment
fetch('${baseUrl}/api/sentiment/analyze', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ text: 'Bitcoin is going to the moon!' })
})
  .then(res => res.json())
  .then(data => console.log('Sentiment:', data.label, data.score));`
      },
      
      // ===== ON-CHAIN ANALYTICS =====
      {
        name: 'On-Chain Analytics API',
        category: 'Analytics',
        description: 'Blockchain data, whale tracking, and network statistics',
        endpoints: [
          { method: 'GET', path: '/api/whale', desc: 'Whale transactions' },
          { method: 'GET', path: '/api/whales/transactions?limit=50', desc: 'Recent whale moves' },
          { method: 'GET', path: '/api/whales/stats?hours=24', desc: 'Whale activity statistics' },
          { method: 'GET', path: '/api/blockchain/gas?chain=ethereum', desc: 'Gas prices' }
        ],
        example: `// Get whale transactions
fetch('${baseUrl}/api/service/whales?chain=ethereum&min_amount_usd=1000000&limit=20')
  .then(res => res.json())
  .then(data => {
    data.data.forEach(tx => {
      console.log('Whale:', tx.amount_usd, 'USD', tx.chain);
    });
  });`
      },
      
      // ===== TECHNICAL ANALYSIS =====
      {
        name: 'Technical Analysis API',
        category: 'Analysis Services',
        description: '5 analysis modes: Quick TA, Fundamental, On-Chain, Risk, Comprehensive',
        endpoints: [
          { method: 'POST', path: '/api/technical/ta-quick', desc: 'Quick technical analysis' },
          { method: 'POST', path: '/api/technical/fa-eval', desc: 'Fundamental evaluation' },
          { method: 'POST', path: '/api/technical/onchain-health', desc: 'On-chain network health' },
          { method: 'POST', path: '/api/technical/risk-assessment', desc: 'Risk & volatility assessment' },
          { method: 'POST', path: '/api/technical/comprehensive', desc: 'Comprehensive analysis' }
        ],
        example: `// Quick Technical Analysis
const ohlcv = await fetch('${baseUrl}/api/ohlcv?symbol=BTC&timeframe=4h&limit=200')
  .then(r => r.json()).then(d => d.data);

fetch('${baseUrl}/api/technical/ta-quick', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({
    symbol: 'BTC',
    timeframe: '4h',
    ohlcv: ohlcv
  })
})
  .then(res => res.json())
  .then(data => {
    console.log('Trend:', data.trend);
    console.log('RSI:', data.rsi);
    console.log('Entry Range:', data.entry_range);
  });`
      },
      
      // ===== AI MODELS =====
      {
        name: 'AI Models API',
        category: 'AI Services',
        description: 'HuggingFace AI models for sentiment, analysis, and predictions',
        endpoints: [
          { method: 'GET', path: '/api/models/status', desc: 'Models status' },
          { method: 'GET', path: '/api/models/list', desc: 'List all models' },
          { method: 'GET', path: '/api/models/health', desc: 'Model health check' },
          { method: 'POST', path: '/api/models/reinit-all', desc: 'Reinitialize models' },
          { method: 'POST', path: '/api/ai/decision', desc: 'AI trading decision' }
        ],
        example: `// Get AI trading decision
fetch('${baseUrl}/api/ai/decision', {
  method: 'POST',
  headers: { 'Content-Type': 'application/json' },
  body: JSON.stringify({ symbol: 'BTC', timeframe: '1h' })
})
  .then(res => res.json())
  .then(data => {
    console.log('Decision:', data.decision);
    console.log('Confidence:', data.confidence);
    console.log('Signals:', data.signals);
  });`
      },
      
      // ===== DEFI DATA =====
      {
        name: 'DeFi Data API',
        category: 'DeFi Services',
        description: 'DefiLlama TVL, protocols, yields, and stablecoins',
        endpoints: [
          { method: 'GET', path: '/api/defi/tvl', desc: 'Total Value Locked' },
          { method: 'GET', path: '/api/defi/protocols?limit=20', desc: 'Top DeFi protocols' },
          { method: 'GET', path: '/api/defi/yields', desc: 'DeFi yields' }
        ],
        example: `// Get DeFi TVL data
fetch('${baseUrl}/api/defi/protocols?limit=10')
  .then(res => res.json())
  .then(data => {
    data.protocols.forEach(p => {
      console.log(p.name, '- TVL:', p.tvl);
    });
  });`
      },
      
      // ===== RESOURCES & MONITORING =====
      {
        name: 'Resources & Monitoring API',
        category: 'System Services',
        description: 'API resources, providers status, and system health',
        endpoints: [
          { method: 'GET', path: '/api/resources/stats', desc: 'Resources statistics' },
          { method: 'GET', path: '/api/resources/apis', desc: 'All APIs list' },
          { method: 'GET', path: '/api/resources/summary', desc: 'Resources summary' },
          { method: 'GET', path: '/api/providers', desc: 'Data providers list' },
          { method: 'GET', path: '/api/status', desc: 'System status' },
          { method: 'GET', path: '/api/health', desc: 'Health check' }
        ],
        example: `// Check system health
fetch('${baseUrl}/api/health')
  .then(res => res.json())
  .then(data => {
    console.log('Status:', data.status);
    console.log('Providers:', data.providers);
  });

// Get resources stats
fetch('${baseUrl}/api/resources/stats')
  .then(res => res.json())
  .then(data => {
    console.log('Total APIs:', data.total_functional);
    console.log('Success Rate:', data.success_rate + '%');
  });`
      },
      
      // ===== WEBSOCKET =====
      {
        name: 'WebSocket API (Optional)',
        category: 'Real-time Services',
        description: 'Optional real-time streaming via WebSocket (HTTP polling recommended)',
        endpoints: [
          { method: 'WS', path: '/ws/master', desc: 'Master endpoint (all services)' },
          { method: 'WS', path: '/ws/live', desc: 'Live market data' },
          { method: 'WS', path: '/ws/ai/data', desc: 'AI model updates' },
          { method: 'WS', path: '/ws/monitoring', desc: 'System monitoring' }
        ],
        example: `// WebSocket connection (optional - HTTP works fine)
const ws = new WebSocket('wss://${window.location.host}/ws/master');

ws.onopen = () => {
  ws.send(JSON.stringify({
    action: 'subscribe',
    service: 'market_data'
  }));
};

ws.onmessage = (event) => {
  const data = JSON.parse(event.data);
  console.log('Real-time update:', data);
};

// Alternative: HTTP polling (recommended)
setInterval(async () => {
  const data = await fetch('${baseUrl}/api/market?limit=100')
    .then(r => r.json());
  console.log('Market data:', data);
}, 30000);`
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
            <p>Access <strong>40+ data providers</strong> through our unified API. Copy and paste these examples to get started.</p>
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
            <div class="config-helper-stats">
              <span>📊 8+ Market Providers</span>
              <span>📰 9+ News Sources</span>
              <span>🎭 4+ Sentiment APIs</span>
              <span>🔗 4+ On-Chain APIs</span>
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
    margin-bottom: 12px;
  }

  .config-helper-base-url code {
    flex: 1;
    padding: 4px 8px;
    background: var(--bg-main, #ffffff);
    border-radius: 4px;
    font-family: 'Courier New', monospace;
    font-size: 13px;
  }

  .config-helper-stats {
    display: flex;
    flex-wrap: wrap;
    gap: 12px;
    padding: 12px;
    background: linear-gradient(135deg, #e0f2f1 0%, #b2dfdb 100%);
    border-radius: 8px;
    font-size: 13px;
    font-weight: 500;
  }

  .config-helper-stats span {
    padding: 4px 8px;
    background: rgba(255,255,255,0.7);
    border-radius: 4px;
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

  .method-badge.ws {
    background: #8b5cf6;
    color: white;
  }

  .endpoint-path {
    flex: 1;
    font-family: 'Courier New', monospace;
    font-size: 12px;
    color: var(--text-primary, #0f2926);
    word-break: break-all;
  }

  .endpoint-desc {
    color: var(--text-muted, #6b7280);
    font-size: 12px;
    white-space: nowrap;
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
      white-space: normal;
    }

    .config-helper-stats {
      flex-direction: column;
    }
  }
`;
document.head.appendChild(style);
