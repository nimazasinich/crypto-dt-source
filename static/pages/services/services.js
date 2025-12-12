/**
 * Services Page - Technical Indicator Services
 */

class ServicesPage {
  constructor() {
    this.services = [];
    this.currentCategory = 'all';
    this.currentSymbol = 'BTC';
    this.currentTimeframe = '1h';
  }

  async init() {
    console.log('[Services] Initializing...');
    
    this.bindEvents();
    await this.loadServices();
    this.checkUrlParams();
    
    console.log('[Services] Ready');
  }

  bindEvents() {
    // Refresh button
    document.getElementById('refresh-btn')?.addEventListener('click', () => {
      this.loadServices();
    });

    // Symbol input
    document.getElementById('symbol-input')?.addEventListener('change', (e) => {
      this.currentSymbol = e.target.value.toUpperCase() || 'BTC';
    });

    // Timeframe select
    document.getElementById('timeframe-select')?.addEventListener('change', (e) => {
      this.currentTimeframe = e.target.value || '1h';
    });

    // Analyze all button
    document.getElementById('analyze-all-btn')?.addEventListener('click', () => {
      this.analyzeAll();
    });

    // Category buttons
    document.querySelectorAll('.category-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        document.querySelectorAll('.category-btn').forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        this.currentCategory = e.target.dataset.category;
        this.filterServices();
      });
    });
  }

  checkUrlParams() {
    const params = new URLSearchParams(window.location.search);
    const service = params.get('service');
    
    if (service) {
      // Auto-analyze the specific service
      setTimeout(() => {
        this.analyzeService(service);
      }, 500);
    }
  }

  async loadServices() {
    const grid = document.getElementById('services-grid');
    if (!grid) return;

    grid.innerHTML = `
      <div class="loading-state">
        <div class="loading-spinner"></div>
        <p>Loading indicator services...</p>
      </div>
    `;

    try {
      const response = await fetch('/api/indicators/services');
      
      if (response.ok) {
        const data = await response.json();
        this.services = data.services || [];
        console.log('[Services] Loaded', this.services.length, 'services');
      } else {
        // Use fallback data
        this.services = this.getFallbackServices();
      }
    } catch (error) {
      console.error('[Services] Load error:', error);
      this.services = this.getFallbackServices();
    }

    this.renderServices();
    this.updateTimestamp();
  }

  getFallbackServices() {
    return [
      {
        id: 'bollinger_bands',
        name: 'Bollinger Bands',
        description: 'Volatility bands placed above and below a moving average. Identifies overbought/oversold conditions and potential breakouts.',
        endpoint: '/api/indicators/bollinger-bands',
        parameters: ['symbol', 'timeframe', 'period', 'std_dev'],
        icon: '📊',
        category: 'volatility'
      },
      {
        id: 'stoch_rsi',
        name: 'Stochastic RSI',
        description: 'Combines Stochastic oscillator with RSI for enhanced momentum detection. Great for identifying extreme conditions.',
        endpoint: '/api/indicators/stoch-rsi',
        parameters: ['symbol', 'timeframe', 'rsi_period', 'stoch_period'],
        icon: '📈',
        category: 'momentum'
      },
      {
        id: 'atr',
        name: 'Average True Range (ATR)',
        description: 'Measures market volatility by analyzing the range of price movements. Useful for setting stop losses.',
        endpoint: '/api/indicators/atr',
        parameters: ['symbol', 'timeframe', 'period'],
        icon: '📉',
        category: 'volatility'
      },
      {
        id: 'sma',
        name: 'Simple Moving Average (SMA)',
        description: 'Average price over specified periods (20, 50, 200). Identifies trend direction and support/resistance levels.',
        endpoint: '/api/indicators/sma',
        parameters: ['symbol', 'timeframe'],
        icon: '〰️',
        category: 'trend'
      },
      {
        id: 'ema',
        name: 'Exponential Moving Average (EMA)',
        description: 'Weighted moving average giving more weight to recent prices. More responsive to current price action.',
        endpoint: '/api/indicators/ema',
        parameters: ['symbol', 'timeframe'],
        icon: '📐',
        category: 'trend'
      },
      {
        id: 'macd',
        name: 'MACD',
        description: 'Moving Average Convergence Divergence. Trend-following momentum indicator showing relationship between EMAs.',
        endpoint: '/api/indicators/macd',
        parameters: ['symbol', 'timeframe', 'fast', 'slow', 'signal'],
        icon: '🔀',
        category: 'momentum'
      },
      {
        id: 'rsi',
        name: 'RSI',
        description: 'Relative Strength Index. Momentum oscillator measuring speed and magnitude of price movements (0-100).',
        endpoint: '/api/indicators/rsi',
        parameters: ['symbol', 'timeframe', 'period'],
        icon: '💪',
        category: 'momentum'
      },
      {
        id: 'comprehensive',
        name: 'Comprehensive Analysis',
        description: 'All indicators combined with trading signals. Get a complete market overview with actionable recommendations.',
        endpoint: '/api/indicators/comprehensive',
        parameters: ['symbol', 'timeframe'],
        icon: '🎯',
        category: 'analysis'
      }
    ];
  }

  filterServices() {
    this.renderServices();
  }

  renderServices() {
    const grid = document.getElementById('services-grid');
    if (!grid) return;

    const filteredServices = this.currentCategory === 'all'
      ? this.services
      : this.services.filter(s => s.category === this.currentCategory);

    if (filteredServices.length === 0) {
      grid.innerHTML = `
        <div class="error-state">
          <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="8" x2="12" y2="12"></line>
            <line x1="12" y1="16" x2="12.01" y2="16"></line>
          </svg>
          <h3>No services found</h3>
          <p>No indicator services match the selected category.</p>
        </div>
      `;
      return;
    }

    grid.innerHTML = filteredServices.map(service => `
      <div class="service-card-large" data-service="${service.id}">
        <div class="service-card-header">
          <div class="service-card-icon">${service.icon}</div>
          <div class="service-card-title">
            <h3>${service.name}</h3>
            <span class="category-tag">${service.category}</span>
          </div>
        </div>
        <div class="service-card-body">
          <p class="service-card-desc">${service.description}</p>
          <div class="service-card-params">
            ${service.parameters.map(p => `<span class="param-tag">${p}</span>`).join('')}
          </div>
        </div>
        <div class="service-card-footer">
          <div class="service-status">
            <span class="status-dot"></span>
            <span>Available</span>
          </div>
          <button class="btn btn-primary" onclick="servicesPage.analyzeService('${service.id}')">
            <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
            </svg>
            Analyze
          </button>
        </div>
      </div>
    `).join('');
  }

  async analyzeService(serviceId) {
    const resultsSection = document.getElementById('results-section');
    const resultsContainer = document.getElementById('results-container');
    
    if (!resultsSection || !resultsContainer) return;

    // Get current values
    const symbolInput = document.getElementById('symbol-input');
    const timeframeSelect = document.getElementById('timeframe-select');
    
    this.currentSymbol = symbolInput?.value?.toUpperCase() || 'BTC';
    this.currentTimeframe = timeframeSelect?.value || '1h';

    // Show results section
    resultsSection.style.display = 'block';
    resultsContainer.innerHTML = `
      <div class="loading-state">
        <div class="loading-spinner"></div>
        <p>Analyzing ${this.currentSymbol} with ${serviceId}...</p>
      </div>
    `;

    // Scroll to results
    resultsSection.scrollIntoView({ behavior: 'smooth' });

    try {
      const service = this.services.find(s => s.id === serviceId);
      if (!service) throw new Error('Service not found');

      const url = `${service.endpoint}?symbol=${encodeURIComponent(this.currentSymbol)}&timeframe=${encodeURIComponent(this.currentTimeframe)}`;
      const response = await fetch(url);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const result = await response.json();
      this.renderResult(service, result);
    } catch (error) {
      console.error('[Services] Analysis error:', error);
      resultsContainer.innerHTML = `
        <div class="error-state">
          <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="15" y1="9" x2="9" y2="15"></line>
            <line x1="9" y1="9" x2="15" y2="15"></line>
          </svg>
          <h3>Analysis Failed</h3>
          <p>${error.message}</p>
          <button class="btn btn-primary" onclick="servicesPage.analyzeService('${serviceId}')">Retry</button>
        </div>
      `;
    }
  }

  async analyzeAll() {
    const resultsSection = document.getElementById('results-section');
    const resultsContainer = document.getElementById('results-container');
    
    if (!resultsSection || !resultsContainer) return;

    // Get current values
    const symbolInput = document.getElementById('symbol-input');
    const timeframeSelect = document.getElementById('timeframe-select');
    
    this.currentSymbol = symbolInput?.value?.toUpperCase() || 'BTC';
    this.currentTimeframe = timeframeSelect?.value || '1h';

    // Show loading
    resultsSection.style.display = 'block';
    resultsContainer.innerHTML = `
      <div class="loading-state">
        <div class="loading-spinner"></div>
        <p>Running comprehensive analysis on ${this.currentSymbol}...</p>
      </div>
    `;

    resultsSection.scrollIntoView({ behavior: 'smooth' });

    try {
      const url = `/api/indicators/comprehensive?symbol=${encodeURIComponent(this.currentSymbol)}&timeframe=${encodeURIComponent(this.currentTimeframe)}`;
      const response = await fetch(url);

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const result = await response.json();
      this.renderComprehensiveResult(result);
    } catch (error) {
      console.error('[Services] Comprehensive analysis error:', error);
      resultsContainer.innerHTML = `
        <div class="error-state">
          <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="15" y1="9" x2="9" y2="15"></line>
            <line x1="9" y1="9" x2="15" y2="15"></line>
          </svg>
          <h3>Analysis Failed</h3>
          <p>${error.message}</p>
          <button class="btn btn-primary" onclick="servicesPage.analyzeAll()">Retry</button>
        </div>
      `;
    }
  }

  renderResult(service, result) {
    const resultsContainer = document.getElementById('results-container');
    if (!resultsContainer) return;

    const signalClass = this.getSignalClass(result.signal);
    const data = result.data || {};

    let valuesHtml = '';
    for (const [key, value] of Object.entries(data)) {
      if (value !== null && value !== undefined) {
        valuesHtml += `
          <div class="result-value">
            <span class="label">${this.formatLabel(key)}</span>
            <span class="value">${this.formatValue(value)}</span>
          </div>
        `;
      }
    }

    resultsContainer.innerHTML = `
      <div class="result-card">
        <div class="result-card-header">
          <h4>
            <span class="indicator-icon">${service.icon}</span>
            ${service.name}
          </h4>
          <span class="signal-badge ${signalClass}">${result.signal || 'N/A'}</span>
        </div>
        <div class="result-card-body">
          <div class="result-values">
            ${valuesHtml}
          </div>
          <div class="result-description">
            <p>${result.description || 'No description available'}</p>
          </div>
        </div>
      </div>
    `;
  }

  renderComprehensiveResult(result) {
    const resultsContainer = document.getElementById('results-container');
    if (!resultsContainer) return;

    const indicators = result.indicators || {};
    const signals = result.signals || {};

    let cardsHtml = '';

    // Overall signal card
    const overallClass = this.getSignalClass(result.overall_signal?.toLowerCase());
    cardsHtml += `
      <div class="result-card" style="grid-column: 1 / -1;">
        <div class="result-card-header" style="background: linear-gradient(135deg, rgba(20, 184, 166, 0.2), rgba(6, 182, 212, 0.15));">
          <h4>
            <span class="indicator-icon">🎯</span>
            Overall Analysis - ${result.symbol || this.currentSymbol}
          </h4>
          <span class="signal-badge ${overallClass}">${result.overall_signal || 'N/A'}</span>
        </div>
        <div class="result-card-body">
          <div class="result-values">
            <div class="result-value">
              <span class="label">Current Price</span>
              <span class="value">${this.formatValue(result.current_price)}</span>
            </div>
            <div class="result-value">
              <span class="label">Confidence</span>
              <span class="value">${result.confidence || 0}%</span>
            </div>
          </div>
          <div class="result-description">
            <p><strong>Recommendation:</strong> ${result.recommendation || 'No recommendation available'}</p>
          </div>
        </div>
      </div>
    `;

    // Individual indicator cards
    const indicatorMeta = {
      bollinger_bands: { icon: '📊', name: 'Bollinger Bands' },
      stoch_rsi: { icon: '📈', name: 'Stochastic RSI' },
      atr: { icon: '📉', name: 'ATR' },
      sma: { icon: '〰️', name: 'SMA' },
      ema: { icon: '📐', name: 'EMA' },
      macd: { icon: '🔀', name: 'MACD' },
      rsi: { icon: '💪', name: 'RSI' }
    };

    for (const [key, data] of Object.entries(indicators)) {
      const meta = indicatorMeta[key] || { icon: '📊', name: key };
      const signal = signals[key] || 'neutral';
      const signalClass = this.getSignalClass(signal);

      let valuesHtml = '';
      if (typeof data === 'object') {
        for (const [k, v] of Object.entries(data)) {
          if (v !== null && v !== undefined) {
            valuesHtml += `
              <div class="result-value">
                <span class="label">${this.formatLabel(k)}</span>
                <span class="value">${this.formatValue(v)}</span>
              </div>
            `;
          }
        }
      }

      cardsHtml += `
        <div class="result-card">
          <div class="result-card-header">
            <h4>
              <span class="indicator-icon">${meta.icon}</span>
              ${meta.name}
            </h4>
            <span class="signal-badge ${signalClass}">${signal}</span>
          </div>
          <div class="result-card-body">
            <div class="result-values">
              ${valuesHtml || '<p style="grid-column: 1/-1; text-align: center; color: var(--text-muted);">No data</p>'}
            </div>
          </div>
        </div>
      `;
    }

    resultsContainer.innerHTML = cardsHtml;
  }

  getSignalClass(signal) {
    if (!signal) return 'neutral';
    const s = signal.toLowerCase();
    
    if (s.includes('buy') || s.includes('bullish') || s.includes('oversold') || s.includes('strong_buy')) {
      return 'bullish';
    }
    if (s.includes('sell') || s.includes('bearish') || s.includes('overbought') || s.includes('strong_sell')) {
      return 'bearish';
    }
    return 'neutral';
  }

  formatLabel(key) {
    return key
      .replace(/_/g, ' ')
      .replace(/([A-Z])/g, ' $1')
      .split(' ')
      .map(w => w.charAt(0).toUpperCase() + w.slice(1).toLowerCase())
      .join(' ');
  }

  formatValue(value) {
    if (value === null || value === undefined) return '—';
    if (typeof value === 'number') {
      if (value > 1000000) return (value / 1000000).toFixed(2) + 'M';
      if (value > 1000) return (value / 1000).toFixed(2) + 'K';
      if (value < 0.0001 && value > 0) return value.toExponential(2);
      if (Number.isInteger(value)) return value.toLocaleString();
      return value.toFixed(value < 1 ? 4 : 2);
    }
    return String(value);
  }

  updateTimestamp() {
    const el = document.getElementById('last-update');
    if (el) {
      el.textContent = `Updated: ${new Date().toLocaleTimeString()}`;
    }
  }

  showToast(message, type = 'info') {
    console.log(`[Toast ${type}]`, message);
    // Implement toast if needed
  }
}

// Initialize
const servicesPage = new ServicesPage();
servicesPage.init();

// Expose globally
window.servicesPage = servicesPage;

export default servicesPage;
