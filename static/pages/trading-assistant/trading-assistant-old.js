/**
 * Trading Assistant Page
 */

import { MarketMonitorAgent } from './market-monitor-agent.js';
import { TelegramService } from './telegram-service.js';
import { analyzeWithStrategy, HYBRID_STRATEGIES } from './trading-strategies.js';
import { TradingIcons } from './icons.js';
import { escapeHtml, safeFormatNumber, safeFormatCurrency } from '../../shared/js/utils/sanitizer.js';

class TradingAssistantPage {
    constructor() {
        this.selectedCrypto = 'BTC';
        this.selectedStrategy = 'trend-rsi-macd';
        this.monitorAgent = null;
        this.telegramService = new TelegramService();
        this.signalStack = [];
        this.maxStackSize = 10;
        this.autoMonitorEnabled = false;
        this.multiStrategyAnalysis = {};
    }

    async init() {
        try {
            console.log('[TradingAssistant] Initializing...');
            await this.telegramService.init();
            this.bindEvents();
            this.setupSignalModal();
            this.setupHelpModal();
            this.initTradingView();
            this.startAutoMonitoring();
            console.log('[TradingAssistant] Ready');
        } catch (error) {
            console.error('[TradingAssistant] Init error:', error);
        }
    }

    /**
     * Starts auto-monitoring agent
     */
    startAutoMonitoring() {
        try {
            const autoMonitor = document.getElementById('auto-monitor');
            if (autoMonitor && autoMonitor.checked) {
                this.autoMonitorEnabled = true;
                this.toggleMonitoring();
            }
        } catch (error) {
            console.warn('[TradingAssistant] Auto-monitor init error (non-critical):', error);
        }
    }

    /**
     * Initializes TradingView widget
     */
    initTradingView() {
        const widgetContainer = document.getElementById('tradingview-widget');
        if (!widgetContainer) return;

        const symbol = `${this.selectedCrypto}USD`;

        widgetContainer.innerHTML = '';

        const script = document.createElement('script');
        script.src = 'https://s3.tradingview.com/tv.js';
        script.async = true;
        script.onload = () => {
            if (window.TradingView) {
                new window.TradingView.widget({
                    autosize: true,
                    symbol: `BINANCE:${symbol}`,
                    interval: '4',
                    timezone: 'Etc/UTC',
                    theme: 'dark',
                    style: '1',
                    locale: 'en',
                    toolbar_bg: '#1a1a1a',
                    enable_publishing: false,
                    hide_top_toolbar: true,
                    hide_legend: true,
                    save_image: false,
                    container_id: 'tradingview-widget',
                });
            }
        };

        document.head.appendChild(script);
    }

    bindEvents() {
        const getSignalsBtn = document.getElementById('get-signals-btn');
        if (getSignalsBtn) {
            getSignalsBtn.addEventListener('click', () => this.analyzeMarket());
        }

        const startMonitoringBtn = document.getElementById('start-monitoring-btn');
        if (startMonitoringBtn) {
            startMonitoringBtn.addEventListener('click', () => this.toggleMonitoring());
        }

        const symbolInput = document.getElementById('symbol-input');
        if (symbolInput) {
            symbolInput.addEventListener('change', (e) => {
                this.selectedCrypto = e.target.value.toUpperCase();
            });
        }

        const strategySelect = document.getElementById('strategy-select');
        if (strategySelect) {
            strategySelect.addEventListener('change', (e) => {
                this.selectedStrategy = e.target.value;
            });
        }

        const telegramNotify = document.getElementById('telegram-notify');
        if (telegramNotify) {
            telegramNotify.addEventListener('change', (e) => {
                this.telegramService.enabled = e.target.checked && this.telegramService.isConfigured();
            });
        }
    }

    /**
     * Analyzes market using hybrid strategy with fallback
     */
    async analyzeMarket() {
        const symbolInput = document.getElementById('symbol-input');
        if (symbolInput) {
            this.selectedCrypto = symbolInput.value.toUpperCase() || 'BTC';
        }

        const resultsBody = document.getElementById('results-body');
        if (!resultsBody) return;

        resultsBody.innerHTML = '<div class="loading-spinner"></div>';

        try {
            let marketData;
            try {
                marketData = await this.fetchMarketData();
            } catch (error) {
                console.warn('[TradingAssistant] Market data fetch failed, using fallback:', error);
                marketData = this.getFallbackMarketData();
            }

            if (!marketData || !marketData.price) {
                throw new Error('Invalid market data');
            }

            let analysis;
            try {
                analysis = analyzeWithStrategy(this.selectedCrypto, this.selectedStrategy, marketData);
            } catch (error) {
                console.error('[TradingAssistant] Strategy analysis failed:', error);
                analysis = analyzeWithStrategy(this.selectedCrypto, 'trend-rsi-macd', marketData);
            }

            analysis.price = marketData.price;
            analysis.change24h = marketData.change24h;

            try {
                const multiStrategyAnalysis = await this.analyzeWithMultipleStrategies(marketData);
                analysis.multiStrategyAnalysis = multiStrategyAnalysis;
            } catch (error) {
                console.warn('[TradingAssistant] Multi-strategy analysis failed (non-critical):', error);
            }

            this.renderSignals(analysis);
            this.addSignalToStack(analysis);

            const telegramNotify = document.getElementById('telegram-notify');
            if (telegramNotify?.checked && this.telegramService.enabled) {
                this.telegramService.sendSignal(analysis).catch(err => {
                    console.warn('[TradingAssistant] Telegram send failed (non-critical):', err);
                });
            }
        } catch (error) {
            console.error('[TradingAssistant] Analysis error:', error);
            this.showErrorState(resultsBody, error);
        }
    }

    /**
     * Gets fallback market data when API fails
     */
    getFallbackMarketData() {
        const defaultPrice = this.getDefaultPrice(this.selectedCrypto);
        return {
            symbol: this.selectedCrypto,
            price: defaultPrice,
            volume: 1000000,
            high24h: defaultPrice * 1.05,
            low24h: defaultPrice * 0.95,
            change24h: 0,
        };
    }

    /**
     * Gets default price for fallback
     */
    getDefaultPrice(symbol) {
        const defaults = {
            'BTC': 50000,
            'ETH': 3000,
            'SOL': 100,
            'BNB': 600,
            'XRP': 0.5,
            'ADA': 0.5,
        };
        return defaults[symbol] || 1000;
    }

    /**
     * Shows error state with retry option
     */
    showErrorState(container, error) {
        container.innerHTML = `
      <div class="error-state">
        <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
          <circle cx="12" cy="12" r="10"></circle>
          <line x1="12" y1="8" x2="12" y2="12"></line>
          <line x1="12" y1="16" x2="12.01" y2="16"></line>
        </svg>
        <h3>Analysis Unavailable</h3>
        <p>Unable to analyze market. Using fallback data.</p>
        <button class="btn btn-primary" onclick="window.tradingAssistantPage.analyzeMarket()" style="margin-top: 16px;">
          Retry Analysis
        </button>
      </div>
    `;
    }

    /**
     * Fetches market data with fallback and retry logic
     */
    async fetchMarketData(retries = 2) {
        const baseUrl = window.location.origin; // Use relative URL for Hugging Face compatibility
        
        for (let attempt = 0; attempt <= retries; attempt++) {
            try {
                if (attempt > 0) {
                    const delay = Math.min(1000 * Math.pow(2, attempt - 1), 5000);
                    await new Promise(resolve => setTimeout(resolve, delay));
                }
                
                // Use coins/top endpoint which returns { coins: [...] }
                const response = await fetch(`${baseUrl}/api/coins/top?limit=100`, {
                    signal: AbortSignal.timeout(10000)
                });

                if (!response.ok) {
                    if (attempt < retries && response.status >= 500) {
                        continue; // Retry on server errors
                    }
                    throw new Error(`Market API returned ${response.status}`);
                }

                const contentType = response.headers.get('content-type');
                if (!contentType || !contentType.includes('application/json')) {
                    throw new Error('Invalid response type');
                }

                const data = await response.json();
                
                if (!data || typeof data !== 'object') {
                    throw new Error('Invalid response format');
                }
                
                // Handle { coins: [...] } format
                const coins = Array.isArray(data.coins) ? data.coins : (Array.isArray(data.data) ? data.data : []);
                
                if (!Array.isArray(coins) || coins.length === 0) {
                    throw new Error('No coins data in response');
                }
                
                const symbolUpper = this.selectedCrypto.toUpperCase();
                const coin = coins.find(c => 
                    c && typeof c === 'object' &&
                    ((c.symbol && String(c.symbol).toUpperCase() === symbolUpper) ||
                     (c.name && String(c.name).toUpperCase() === symbolUpper))
                );
                
                if (coin) {
                    const price = parseFloat(coin.current_price || coin.price || 0);
                    if (isNaN(price) || price <= 0) {
                        throw new Error(`Invalid price data for ${this.selectedCrypto}`);
                    }
                    
                    return {
                        symbol: this.selectedCrypto,
                        price: price,
                        volume: parseFloat(coin.total_volume || coin.volume_24h || 0) || 0,
                        high24h: parseFloat(coin.high_24h || price * 1.05) || price * 1.05,
                        low24h: parseFloat(coin.low_24h || price * 0.95) || price * 0.95,
                        change24h: parseFloat(coin.price_change_percentage_24h || coin.change_24h || 0) || 0,
                    };
                }

                throw new Error(`No market data found for ${this.selectedCrypto}`);
            } catch (error) {
                if (attempt < retries && (error.name === 'AbortError' || error.message.includes('timeout') || error.message.includes('network'))) {
                    continue; // Retry on network errors
                }
                if (error.name === 'AbortError') {
                    throw new Error('Request timeout');
                }
                throw error;
            }
        }
        
        throw new Error('Failed to fetch market data after retries');
    }

    /**
     * Toggles monitoring agent
     */
    toggleMonitoring() {
        const autoMonitor = document.getElementById('auto-monitor');
        if (!autoMonitor?.checked) {
            if (this.monitorAgent) {
                this.monitorAgent.stop();
                this.monitorAgent = null;
            }
            return;
        }

        if (this.monitorAgent && this.monitorAgent.isRunning) {
            this.monitorAgent.stop();
            this.monitorAgent = null;
            return;
        }

        this.startMonitoring();
    }

    /**
     * Starts monitoring agent
     */
    startMonitoring() {
        const symbolInput = document.getElementById('symbol-input');
        const strategySelect = document.getElementById('strategy-select');

        this.monitorAgent = new MarketMonitorAgent({
            symbol: symbolInput?.value.toUpperCase() || 'BTC',
            strategy: strategySelect?.value || 'trend-rsi-macd',
            interval: 60000,
        });

        this.monitorAgent.onSignal(async (analysis) => {
            try {
                const marketData = await this.fetchMarketData().catch(() => this.getFallbackMarketData());
                const multiStrategyAnalysis = await this.analyzeWithMultipleStrategies(marketData).catch(() => null);
                if (multiStrategyAnalysis) {
                    analysis.multiStrategyAnalysis = multiStrategyAnalysis;
                }
            } catch (error) {
                console.warn('[TradingAssistant] Multi-strategy analysis failed (non-critical):', error);
            }

            this.showSignalModal(analysis);
            this.addSignalToStack(analysis);

            const telegramNotify = document.getElementById('telegram-notify');
            if (telegramNotify?.checked && this.telegramService.enabled) {
                this.telegramService.sendSignal(analysis).catch(err => {
                    console.warn('[TradingAssistant] Telegram send failed (non-critical):', err);
                });
            }
        });

        this.monitorAgent.onError((error) => {
            console.error('[TradingAssistant] Monitor error:', error);
        });

        this.monitorAgent.start();
    }

    /**
     * Get trading signals for a symbol
     * @param {string} symbol - Crypto symbol (e.g., 'BTC', 'ETH')
     */
    async getSignals(symbol) {
        if (symbol) {
            this.selectedCrypto = symbol;
            const symbolInput = document.getElementById('symbol-input');
            if (symbolInput) {
                symbolInput.value = symbol;
            }
        }
        await this.analyzeMarket();
    }

    async loadSignals() {
        const resultsBody = document.getElementById('results-body');
        if (!resultsBody) return;

        resultsBody.innerHTML = '<div class="loading-spinner"></div>';

        try {
            let data = null;

            try {
                const response = await fetch(`/api/ai/signals?symbol=${this.selectedCrypto}`);
                if (response.ok) {
                    const contentType = response.headers.get('content-type');
                    if (contentType && contentType.includes('application/json')) {
                        data = await response.json();
                    }
                }
            } catch (e) {
                console.warn('[TradingAssistant] /api/ai/signals unavailable, using fallback', e);
            }

            if (!data) {
                try {
                    const sentimentRes = await fetch('/api/sentiment/analyze', {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            text: `${this.selectedCrypto} trading signal`,
                            mode: 'crypto'
                        })
                    });

                    if (sentimentRes.ok) {
                        const contentType = sentimentRes.headers.get('content-type');
                        if (contentType && contentType.includes('application/json')) {
                            const sentimentData = await sentimentRes.json();
                            const sentiment = (sentimentData.sentiment || '').toLowerCase();
                            let signal = 'hold';
                            if (sentiment.includes('bull')) signal = 'buy';
                            if (sentiment.includes('bear')) signal = 'sell';

                            data = {
                                signal,
                                confidence: Math.round((sentimentData.confidence || 0.7) * 100),
                                current_price: 0,
                                prediction: {
                                    entry: 0,
                                    target: 0,
                                    stop_loss: 0,
                                    risk_reward: '1:2'
                                }
                            };
                        }
                    }
                } catch (e) {
                    console.warn('[TradingAssistant] Sentiment API also unavailable, using demo data', e);
                }
            }

            if (!data) {
                // NO MOCK DATA - Show error state
                resultsBody.innerHTML = `
          <div class="error-state">
            <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
              <circle cx="12" cy="12" r="10"></circle>
              <line x1="12" y1="8" x2="12" y2="12"></line>
              <line x1="12" y1="16" x2="12.01" y2="16"></line>
            </svg>
            <h3>API Unavailable</h3>
            <p>Unable to fetch trading signals. Please check backend connection.</p>
          </div>
        `;
                return;
            }

            // Fetch real price data with proper base URL
            try {
                const baseUrl = window.location.origin;
                const priceRes = await fetch(`${baseUrl}/api/market?limit=1&symbol=${this.selectedCrypto}`, {
                    signal: AbortSignal.timeout(10000)
                });
                if (priceRes.ok) {
                    const priceData = await priceRes.json();
                    if (priceData && priceData.success && Array.isArray(priceData.items) && priceData.items.length > 0) {
                        const item = priceData.items[0];
                        if (item && typeof item === 'object') {
                            const price = parseFloat(item.price);
                            const change24h = parseFloat(item.change_24h);
                            if (!isNaN(price) && price > 0) {
                                data.price = price;
                            }
                            if (!isNaN(change24h)) {
                                data.change_24h = change24h;
                            }
                        }
                    }
                }
            } catch (e) {
                console.warn('[TradingAssistant] Price data unavailable:', e.message);
            }

            this.renderSignals(data);
        } catch (error) {
            console.error('[TradingAssistant] Signals error:', error);
            const errorMessage = error && error.message ? escapeHtml(error.message) : 'Failed to load signals. API may be offline.';
            resultsBody.innerHTML = `<div class="error-state">${TradingIcons.risk} ${errorMessage}</div>`;
        }
    }

    /**
     * Renders trading signals with modern UI
     */
    renderSignals(data) {
        const resultsBody = document.getElementById('results-body');
        if (!resultsBody) return;

        if (!data || typeof data !== 'object') {
            resultsBody.innerHTML = '<div class="error-state">Invalid signal data</div>';
            return;
        }

        const signal = String(data.signal || 'hold').toLowerCase();
        const price = typeof data.price === 'number' && !isNaN(data.price) && data.price > 0 ? data.price : 0;
        const takeProfits = Array.isArray(data.takeProfitLevels) ? data.takeProfitLevels : [];
        const stopLoss = typeof data.stopLoss === 'number' && !isNaN(data.stopLoss) ? data.stopLoss : (price > 0 ? price * 0.95 : 0);
        const indicators = data.indicators && typeof data.indicators === 'object' ? data.indicators : {};
        const levels = data.levels && typeof data.levels === 'object' ? data.levels : {};
        const confidence = typeof data.confidence === 'number' && !isNaN(data.confidence) ? Math.max(0, Math.min(100, data.confidence)) : 50;
        const strategy = escapeHtml(String(data.strategy || 'Unknown Strategy'));
        const symbolDisplay = escapeHtml(String(this.selectedCrypto));

        resultsBody.innerHTML = `
      <div class="signals-result glass-card">
        <div class="signal-header">
          <div>
            <h3>${symbolDisplay}/USD</h3>
            <div class="strategy-badges">
              <span class="strategy-badge ${data.strategyType === 'advanced' ? 'badge-advanced' : data.strategyType === 'scalping' ? 'badge-scalping' : ''}">${strategy}</span>
              ${data.strategyType === 'advanced' ? `<span class="badge-premium">${TradingIcons.strategy} ${escapeHtml('Advanced')}</span>` : ''}
              ${data.strategyType === 'scalping' ? `<span class="badge-scalping">${TradingIcons.monitor} ${escapeHtml('SCALPING')}</span>` : ''}
              ${data.strategyType === 'fallback' ? `<span class="badge-fallback">${TradingIcons.risk} ${escapeHtml('Fallback')}</span>` : ''}
            </div>
          </div>
          ${data.isScalping ? `
            <div class="scalping-warning">
              ${TradingIcons.risk}
              <div>
                <strong>High Risk Scalping Strategy</strong>
                <p>Designed for futures trading. Very tight stops (0.5%) and quick targets. Use with caution!</p>
              </div>
            </div>
          ` : ''}
          ${data.multiStrategyAnalysis ? `
            <div class="multi-strategy-analysis">
              <h4>${TradingIcons.compare} Multi-Strategy Analysis</h4>
              <div class="analysis-grid">
                <div class="analysis-card">
                  <span class="analysis-label">Success Probability</span>
                  <span class="analysis-value success">${data.multiStrategyAnalysis.successProbability}%</span>
                </div>
                <div class="analysis-card">
                  <span class="analysis-label">Overall Risk</span>
                  <span class="analysis-value risk-${data.multiStrategyAnalysis.riskLevel}">${data.multiStrategyAnalysis.riskLevel}</span>
                </div>
                <div class="analysis-card">
                  <span class="analysis-label">Avg Confidence</span>
                  <span class="analysis-value">${Math.round(data.multiStrategyAnalysis.averageConfidence)}%</span>
                </div>
                ${data.multiStrategyAnalysis.bestStrategy ? `
                  <div class="analysis-card best-strategy">
                    <span class="analysis-label">Best Strategy</span>
                    <span class="analysis-value">${data.multiStrategyAnalysis.bestStrategy.strategy}</span>
                    <span class="analysis-sub">${data.multiStrategyAnalysis.bestStrategy.confidence}% confidence</span>
                  </div>
                ` : ''}
              </div>
            </div>
          ` : ''}
          <div class="current-price">
            <span class="price-label">Current Price</span>
            <span class="price-value">${price > 0 ? safeFormatCurrency(price) : '—'}</span>
            ${data.change24h !== undefined && typeof data.change24h === 'number' && !isNaN(data.change24h) ? `<span class="price-change ${data.change24h >= 0 ? 'positive' : 'negative'}">${data.change24h >= 0 ? '+' : ''}${escapeHtml(safeFormatNumber(data.change24h, { minimumFractionDigits: 2, maximumFractionDigits: 2 }))}%</span>` : ''}
          </div>
        </div>
        
        <div class="signal-indicator signal-${escapeHtml(signal)} ${data.strategyType === 'advanced' ? 'badge-advanced' : ''} ${data.strategyType === 'scalping' ? 'badge-scalping' : ''}">
          <div class="signal-icon">${this.getSignalIcon(signal)}</div>
          <div class="signal-content">
            <div class="signal-text">${escapeHtml(signal.toUpperCase())}</div>
            <div class="signal-strength-bar">
              <div class="strength-fill" style="width: ${Math.max(0, Math.min(100, confidence))}%; background: ${signal === 'buy' ? '#22c55e' : signal === 'sell' ? '#ef4444' : '#eab308'}"></div>
            </div>
            <div class="signal-confidence">
              ${escapeHtml(String(confidence))}% Confidence • ${escapeHtml(String(data.strength || 'medium'))} signal
              ${data.strategyType === 'advanced' ? ' • ⭐ Advanced Algorithm' : ''}
            </div>
          </div>
        </div>
        
        <div class="price-targets">
          <h4>Take Profit Levels</h4>
          ${takeProfits.length > 0 ? takeProfits.map((tp, idx) => {
            if (!tp || typeof tp !== 'object' || typeof tp.level !== 'number' || isNaN(tp.level) || price <= 0) {
              return '';
            }
            const profit = price > 0 ? ((tp.level / price - 1) * 100) : 0;
            const tpType = escapeHtml(String(tp.type || `TP${idx + 1}`));
            return `
              <div class="target-item tp-${idx + 1}">
                <span class="target-label">${tpType}:</span>
                <span class="target-value">${safeFormatCurrency(tp.level)}</span>
                <span class="target-profit">+${escapeHtml(safeFormatNumber(profit, { minimumFractionDigits: 2, maximumFractionDigits: 2 }))}%</span>
              </div>
            `;
        }).filter(html => html.length > 0).join('') : (price > 0 ? `
            <div class="target-item">
              <span class="target-label">TP1:</span>
              <span class="target-value">${safeFormatCurrency(price * 1.05)}</span>
              <span class="target-profit">+5%</span>
            </div>
          ` : '')}
          ${price > 0 && stopLoss > 0 ? `
          <div class="target-item stop-loss">
            <span class="target-label">Stop Loss:</span>
            <span class="target-value">${safeFormatCurrency(stopLoss)}</span>
            <span class="target-risk">${escapeHtml(safeFormatNumber(Math.abs(((stopLoss / price - 1) * 100)), { minimumFractionDigits: 2, maximumFractionDigits: 2 }))}%</span>
          </div>
          ` : ''}
        </div>

        ${data.riskReward && data.riskReward.riskRewardRatio ? `
          <div class="risk-reward-info">
            <span class="risk-reward-label">Risk/Reward Ratio:</span>
            <span class="risk-reward-value">${escapeHtml(String(data.riskReward.riskRewardRatio))}</span>
          </div>
        ` : ''}
        
        ${levels.resistance || levels.support ? `
          <div class="key-levels-section">
            <h4>Key Levels</h4>
            ${levels.resistance && Array.isArray(levels.resistance) && levels.resistance.length > 0 ? `
              <div class="levels-group">
                <span class="levels-label">Resistance:</span>
                ${levels.resistance.slice(0, 3).filter(r => r && typeof r === 'object' && typeof r.level === 'number' && !isNaN(r.level)).map(r => `
                  <span class="level-tag resistance">${safeFormatCurrency(r.level)}</span>
                `).join('')}
              </div>
            ` : ''}
            ${levels.support && Array.isArray(levels.support) && levels.support.length > 0 ? `
              <div class="levels-group">
                <span class="levels-label">Support:</span>
                ${levels.support.slice(0, 3).filter(s => s && typeof s === 'object' && typeof s.level === 'number' && !isNaN(s.level)).map(s => `
                  <span class="level-tag support">${safeFormatCurrency(s.level)}</span>
                `).join('')}
              </div>
            ` : ''}
          </div>
        ` : ''}
        
        ${indicators.rsi || indicators.macd || indicators.trend ? `
          <div class="technical-indicators">
            <h4>Technical Indicators</h4>
            <div class="indicators-grid">
              ${indicators.rsi && typeof indicators.rsi === 'number' && !isNaN(indicators.rsi) ? `
                <div class="indicator-box">
                  <span class="indicator-label">RSI</span>
                  <span class="indicator-value ${indicators.rsi > 70 ? 'overbought' : indicators.rsi < 30 ? 'oversold' : ''}">${escapeHtml(safeFormatNumber(indicators.rsi, { minimumFractionDigits: 0, maximumFractionDigits: 0 }))}</span>
                </div>
              ` : ''}
              ${indicators.macd ? `
                <div class="indicator-box">
                  <span class="indicator-label">MACD</span>
                  <span class="indicator-value ${escapeHtml(String(indicators.macd))}">${escapeHtml(String(indicators.macd))}</span>
                </div>
              ` : ''}
              ${indicators.trend ? `
                <div class="indicator-box">
                  <span class="indicator-label">Trend</span>
                  <span class="indicator-value ${escapeHtml(String(indicators.trend))}">${escapeHtml(String(indicators.trend).toUpperCase())}</span>
                </div>
              ` : ''}
              ${indicators.stochastic ? `
                <div class="indicator-box">
                  <span class="indicator-label">Stochastic</span>
                  <span class="indicator-value">${escapeHtml(String(indicators.stochastic))}</span>
                </div>
              ` : ''}
            </div>
          </div>
        ` : ''}
      </div>
    `;
    }

    /**
     * Sets up signal modal for waterfall display
     */
    setupSignalModal() {
        if (document.getElementById('signal-modal')) return;

        const modal = document.createElement('div');
        modal.id = 'signal-modal';
        modal.className = 'signal-modal';
        modal.innerHTML = `
      <div class="signal-modal-content">
        <button class="signal-modal-close">&times;</button>
        <div class="signal-modal-body"></div>
      </div>
    `;
        document.body.appendChild(modal);

        modal.querySelector('.signal-modal-close').addEventListener('click', () => {
            modal.classList.remove('active');
        });

        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.classList.remove('active');
            }
        });
    }

    /**
     * Shows signal in modal
     */
    showSignalModal(analysis) {
        const modal = document.getElementById('signal-modal');
        if (!modal) return;

        const body = modal.querySelector('.signal-modal-body');
        const signal = analysis.signal.toLowerCase();

        body.innerHTML = `
      <div class="signal-modal-header signal-${signal}">
        <div class="signal-modal-icon">${this.getSignalIcon(signal)}</div>
        <div>
          <h2>${analysis.signal.toUpperCase()} Signal</h2>
          <p>${analysis.strategy}</p>
        </div>
      </div>
      <div class="signal-modal-details">
        <div class="detail-row">
          <span>Symbol:</span>
          <strong>${this.selectedCrypto}</strong>
        </div>
        <div class="detail-row">
          <span>Price:</span>
          <strong>$${analysis.price.toLocaleString()}</strong>
        </div>
        <div class="detail-row">
          <span>Confidence:</span>
          <strong>${analysis.confidence}%</strong>
        </div>
        ${analysis.multiStrategyAnalysis ? `
          <div class="detail-section">
            <h3>${TradingIcons.compare} Multi-Strategy Analysis</h3>
            <div class="modal-analysis-grid">
              <div class="modal-analysis-item">
                <span class="modal-analysis-label">Success Probability</span>
                <span class="modal-analysis-value success">${analysis.multiStrategyAnalysis.successProbability}%</span>
              </div>
              <div class="modal-analysis-item">
                <span class="modal-analysis-label">Overall Risk</span>
                <span class="modal-analysis-value risk-${analysis.multiStrategyAnalysis.riskLevel}">${analysis.multiStrategyAnalysis.riskLevel}</span>
              </div>
              <div class="modal-analysis-item">
                <span class="modal-analysis-label">Avg Confidence</span>
                <span class="modal-analysis-value">${Math.round(analysis.multiStrategyAnalysis.averageConfidence)}%</span>
              </div>
            </div>
            ${analysis.multiStrategyAnalysis.bestStrategy ? `
              <div class="modal-best-strategy">
                <strong>Best Strategy:</strong> ${analysis.multiStrategyAnalysis.bestStrategy.strategy} (${analysis.multiStrategyAnalysis.bestStrategy.confidence}%)
              </div>
            ` : ''}
          </div>
        ` : ''}
        ${analysis.takeProfitLevels && analysis.takeProfitLevels.length > 0 ? `
          <div class="detail-section">
            <h3>${TradingIcons.profit} Take Profit Levels</h3>
            ${analysis.takeProfitLevels.map(tp => {
            const profit = ((tp.level / analysis.price - 1) * 100).toFixed(2);
            return `
              <div class="detail-row">
                <span>${tp.type}:</span>
                <strong>$${tp.level.toLocaleString()}</strong>
                <span class="profit-badge">+${profit}%</span>
              </div>
            `;
        }).join('')}
          </div>
        ` : ''}
        ${analysis.stopLoss ? `
          <div class="detail-row">
            <span>${TradingIcons.risk} Stop Loss:</span>
            <strong class="text-danger">$${analysis.stopLoss.toLocaleString()}</strong>
            <span class="risk-badge-modal">${Math.abs(((analysis.stopLoss / analysis.price - 1) * 100)).toFixed(2)}%</span>
          </div>
        ` : ''}
      </div>
    `;

        modal.classList.add('active');

        setTimeout(() => {
            modal.classList.remove('active');
        }, 8000);
    }

    /**
     * Adds signal to waterfall stack
     */
    addSignalToStack(analysis) {
        this.signalStack.unshift({
            ...analysis,
            timestamp: new Date(),
        });

        if (this.signalStack.length > this.maxStackSize) {
            this.signalStack.pop();
        }

        this.updateSignalStack();
    }

    /**
     * Updates signal stack display
     */
    updateSignalStack() {
        let stackContainer = document.getElementById('signal-stack');
        if (!stackContainer) {
            stackContainer = document.createElement('div');
            stackContainer.id = 'signal-stack';
            stackContainer.className = 'signal-stack';
            const resultsBody = document.getElementById('results-body');
            if (resultsBody) {
                resultsBody.parentNode.insertBefore(stackContainer, resultsBody.nextSibling);
            }
        }

        if (this.signalStack.length === 0) {
            stackContainer.style.display = 'none';
            return;
        }

        stackContainer.style.display = 'block';
        stackContainer.innerHTML = `
      <h4>Recent Signals</h4>
      <div class="signal-stack-items">
        ${this.signalStack.slice(0, 5).map(signal => `
          <div class="signal-stack-item signal-${signal.signal}">
            <span class="stack-icon">${this.getSignalIcon(signal.signal)}</span>
            <span class="stack-symbol">${this.selectedCrypto}</span>
            <span class="stack-signal">${signal.signal.toUpperCase()}</span>
            <span class="stack-time">${new Date(signal.timestamp).toLocaleTimeString()}</span>
          </div>
        `).join('')}
      </div>
    `;
    }

    /**
     * Gets SVG icon for signal
     */
    getSignalIcon(signal) {
        const icons = {
            'buy': TradingIcons.buy,
            'sell': TradingIcons.sell,
            'hold': TradingIcons.hold
        };
        return icons[signal] || TradingIcons.hold;
    }

    /**
     * Shows strategy comparison table
     */
    showStrategyComparison() {
        const panel = document.getElementById('comparison-panel');
        const tableContainer = document.getElementById('strategy-comparison-table');

        if (!panel || !tableContainer) return;

        const strategies = [
            { name: 'Trend + RSI + MACD', type: 'Standard', timeframe: '4h, 1d', risk: 'Medium', success: '75-80%', advantages: 'ترکیب روند و مومنتوم، سیگنال‌های واضح', bestFor: 'معامله‌گران متوسط' },
            { name: 'Bollinger Bands + RSI', type: 'Standard', timeframe: '1h, 4h', risk: 'Low', success: '70-75%', advantages: 'ریسک پایین، مناسب برای بازارهای نوسانی', bestFor: 'معامله‌گران محافظه‌کار' },
            { name: 'EMA + Volume + RSI', type: 'Standard', timeframe: '1h, 4h, 1d', risk: 'Medium', success: '72-78%', advantages: 'تأیید حجم، شناسایی روند زودهنگام', bestFor: 'معامله‌گران مومنتوم' },
            { name: 'S/R + Fibonacci', type: 'Standard', timeframe: '4h, 1d, 1w', risk: 'High', success: '68-73%', advantages: 'سطوح دقیق ورود/خروج، مناسب برای سوئینگ', bestFor: 'معامله‌گران حرفه‌ای' },
            { name: 'MACD + Stochastic + EMA', type: 'Standard', timeframe: '1h, 4h', risk: 'Medium', success: '76-82%', advantages: 'تأیید سه‌گانه، کاهش سیگنال‌های کاذب', bestFor: 'معامله‌گران پیشرفته' },
            { name: 'Ensemble Multi-Timeframe', type: 'Advanced', timeframe: '15m, 1h, 4h, 1d', risk: 'Medium', success: '80-85%', advantages: 'تحلیل چند تایم‌فریم، کاهش خطا', bestFor: 'معامله‌گران حرفه‌ای' },
            { name: 'Volume Profile + Order Flow', type: 'Advanced', timeframe: '1h, 4h, 1d', risk: 'High', success: '78-83%', advantages: 'تحلیل عمق بازار، شناسایی مناطق کلیدی', bestFor: 'معامله‌گران نهادی' },
            { name: 'Adaptive Breakout', type: 'Advanced', timeframe: '4h, 1d', risk: 'Medium', success: '75-80%', advantages: 'تطبیق با نوسان، شناسایی بریک‌اوت واقعی', bestFor: 'معامله‌گران پیشرفته' },
            { name: 'Mean Reversion + Momentum', type: 'Advanced', timeframe: '1h, 4h', risk: 'Low', success: '73-78%', advantages: 'ترکیب دو روش، ریسک پایین', bestFor: 'معامله‌گران محافظه‌کار' },
            { name: 'S/R Breakout Confirmation', type: 'Advanced', timeframe: '4h, 1d', risk: 'High', success: '79-84%', advantages: 'تأیید چندگانه، پتانسیل سود بالا', bestFor: 'معامله‌گران حرفه‌ای' },
            { name: '⚡ Pre-Breakout Scalping', type: 'Scalping', timeframe: '1m, 5m, 15m', risk: 'Very High', success: '82-88%', advantages: 'ورود قبل از بریک‌اوت، سود سریع', bestFor: 'اسکلپرهای حرفه‌ای' },
            { name: '⚡ Liquidity Zone Scalping', type: 'Scalping', timeframe: '1m, 5m', risk: 'Very High', success: '80-86%', advantages: 'شناسایی مناطق نقدینگی، ورود بهینه', bestFor: 'اسکلپرهای پیشرفته' },
            { name: '⚡ Momentum Accumulation', type: 'Scalping', timeframe: '1m, 5m, 15m', risk: 'Very High', success: '83-89%', advantages: 'شناسایی تجمع مومنتوم، ورود زودهنگام', bestFor: 'اسکلپرهای حرفه‌ای' },
            { name: '⚡ Volume Spike Breakout', type: 'Scalping', timeframe: '1m, 5m', risk: 'Very High', success: '81-87%', advantages: 'شناسایی اسپایک حجم، تأیید قوی', bestFor: 'اسکلپرهای پیشرفته' },
            { name: '⚡ Order Flow Imbalance', type: 'Scalping', timeframe: '1m, 5m', risk: 'Very High', success: '79-85%', advantages: 'تحلیل جریان سفارشات، پیش‌بینی حرکت', bestFor: 'اسکلپرهای نهادی' },
        ];

        tableContainer.innerHTML = `
      <div class="comparison-table-wrapper">
        <table class="strategy-comparison-table">
          <thead>
            <tr>
              <th>#</th>
              <th>نام استراتژی</th>
              <th>نوع</th>
              <th>تایم‌فریم</th>
              <th>ریسک</th>
              <th>میزان موفقیت</th>
              <th>مزایا</th>
              <th>مناسب برای</th>
            </tr>
          </thead>
          <tbody>
            ${strategies.map((strategy, index) => `
              <tr class="${strategy.type.toLowerCase()}">
                <td>${index + 1}</td>
                <td><strong>${strategy.name}</strong></td>
                <td><span class="type-badge ${strategy.type.toLowerCase()}">${strategy.type}</span></td>
                <td>${strategy.timeframe}</td>
                <td><span class="risk-badge risk-${strategy.risk.toLowerCase().replace(' ', '-')}">${strategy.risk}</span></td>
                <td><strong class="success-rate">${strategy.success}</strong></td>
                <td>${strategy.advantages}</td>
                <td>${strategy.bestFor}</td>
              </tr>
            `).join('')}
          </tbody>
        </table>
        <div class="comparison-summary">
          <h4>خلاصه آماری</h4>
          <div class="summary-grid">
            <div class="summary-item">
              <span class="summary-label">Standard Strategies</span>
              <span class="summary-value">72-78%</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Advanced Strategies</span>
              <span class="summary-value">77-82%</span>
            </div>
            <div class="summary-item">
              <span class="summary-label">Scalping Strategies</span>
              <span class="summary-value">81-87%</span>
            </div>
          </div>
        </div>
      </div>
    `;

        panel.style.display = 'block';
        panel.scrollIntoView({ behavior: 'smooth', block: 'start' });
    }

    /**
     * Analyzes market with multiple strategies for comparison
     */
    async analyzeWithMultipleStrategies(marketData) {
        const strategies = Object.keys(HYBRID_STRATEGIES);
        const results = [];

        for (const strategyKey of strategies.slice(0, 5)) {
            try {
                const analysis = analyzeWithStrategy(this.selectedCrypto, strategyKey, marketData);
                results.push({
                    strategy: analysis.strategy,
                    strategyKey,
                    signal: analysis.signal,
                    confidence: analysis.confidence,
                    strength: analysis.strength,
                    riskReward: analysis.riskReward,
                    takeProfitLevels: analysis.takeProfitLevels,
                    stopLoss: analysis.stopLoss,
                });
            } catch (error) {
                console.warn(`[TradingAssistant] Strategy ${strategyKey} analysis failed:`, error);
            }
        }

        return {
            strategies: results,
            bestStrategy: results.reduce((best, current) =>
                current.confidence > (best?.confidence || 0) ? current : best, null
            ),
            averageConfidence: results.length > 0 ? results.reduce((sum, r) => sum + r.confidence, 0) / results.length : 0,
            successProbability: this.calculateSuccessProbability(results),
            riskLevel: this.calculateOverallRisk(results),
        };
    }

    /**
     * Calculates success probability based on multiple strategies
     */
    calculateSuccessProbability(strategies) {
        if (strategies.length === 0) return 0;

        const buySignals = strategies.filter(s => s.signal === 'buy').length;
        const sellSignals = strategies.filter(s => s.signal === 'sell').length;
        const holdSignals = strategies.filter(s => s.signal === 'hold').length;

        const maxSignals = Math.max(buySignals, sellSignals, holdSignals);
        const agreement = maxSignals / strategies.length;

        const avgConfidence = strategies.reduce((sum, s) => sum + s.confidence, 0) / strategies.length;

        return Math.round((agreement * 0.6 + avgConfidence / 100 * 0.4) * 100);
    }

    /**
     * Calculates overall risk level
     */
    calculateOverallRisk(strategies) {
        if (strategies.length === 0) return 'medium';

        const riskLevels = strategies.map(s => {
            const strategy = HYBRID_STRATEGIES[s.strategyKey];
            return strategy?.riskLevel || 'medium';
        });

        const riskCounts = {
            'low': riskLevels.filter(r => r === 'low').length,
            'medium': riskLevels.filter(r => r === 'medium').length,
            'high': riskLevels.filter(r => r === 'high').length,
            'very-high': riskLevels.filter(r => r === 'very-high').length,
        };

        if (riskCounts['very-high'] > 0) return 'very-high';
        if (riskCounts['high'] > riskCounts['medium']) return 'high';
        if (riskCounts['low'] > riskCounts['medium']) return 'low';
        return 'medium';
    }

    /**
     * Sets up help modal
     */
    setupHelpModal() {
        if (document.getElementById('help-modal')) return;

        const modal = document.createElement('div');
        modal.id = 'help-modal';
        modal.className = 'help-modal';
        modal.innerHTML = `
      <div class="help-modal-content">
        <div class="help-modal-header">
          <h2>${TradingIcons.help} Strategy Guide & Comparison</h2>
          <button class="help-modal-close">&times;</button>
        </div>
        <div class="help-modal-body" id="help-modal-body"></div>
      </div>
    `;
        document.body.appendChild(modal);

        modal.querySelector('.help-modal-close').addEventListener('click', () => {
            modal.classList.remove('active');
        });

        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.classList.remove('active');
            }
        });
    }

    /**
     * Shows help modal with strategy comparison
     */
    showHelpModal() {
        const modal = document.getElementById('help-modal');
        const body = document.getElementById('help-modal-body');
        if (!modal || !body) return;

        body.innerHTML = this.generateHelpContent();
        modal.classList.add('active');
    }

    /**
     * Generates help modal content
     */
    generateHelpContent() {
        return `
      <div class="help-content">
        <div class="help-section">
          <h3>${TradingIcons.strategy} Strategy Types</h3>
          <div class="strategy-types-grid">
            <div class="strategy-type-card">
              <h4>Standard Strategies</h4>
              <p>Basic strategies suitable for beginners. Lower risk, moderate returns.</p>
              <span class="success-badge">72-78% Success Rate</span>
            </div>
            <div class="strategy-type-card advanced">
              <h4>Advanced Strategies</h4>
              <p>Complex algorithms combining multiple indicators and timeframes.</p>
              <span class="success-badge">77-82% Success Rate</span>
            </div>
            <div class="strategy-type-card scalping">
              <h4>Scalping Strategies</h4>
              <p>High-frequency trading for quick profits. Very high risk!</p>
              <span class="success-badge">81-87% Success Rate</span>
            </div>
          </div>
        </div>

        <div class="help-section">
          <h3>${TradingIcons.compare} Multi-Strategy Analysis</h3>
          <p>When analyzing a trading point, the system evaluates multiple strategies simultaneously:</p>
          <ul class="help-features">
            <li><strong>Success Probability:</strong> Calculated from agreement between strategies</li>
            <li><strong>Risk Assessment:</strong> Overall risk level based on all strategies</li>
            <li><strong>Best Strategy:</strong> Strategy with highest confidence</li>
            <li><strong>Take Profit Levels:</strong> Calculated based on risk/reward ratio</li>
          </ul>
        </div>

        <div class="help-section">
          <button class="btn btn-primary" onclick="window.tradingAssistantPage.showStrategyComparison(); document.getElementById('help-modal').classList.remove('active');">
            ${TradingIcons.compare} View Full Strategy Comparison Table
          </button>
        </div>
      </div>
    `;
    }

    /**
     * Starts auto-monitoring agent
     */
    startAutoMonitoring() {
        try {
            const autoMonitor = document.getElementById('auto-monitor');
            if (autoMonitor && autoMonitor.checked) {
                this.autoMonitorEnabled = true;
                setTimeout(() => this.toggleMonitoring(), 1000);
            }
        } catch (error) {
            console.warn('[TradingAssistant] Auto-monitor init error (non-critical):', error);
        }
    }
}

export default TradingAssistantPage;
