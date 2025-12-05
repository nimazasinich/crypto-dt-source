/**
 * 🔥 Enhanced Trading Assistant with Real-Time Data & AI Agent
 * Features: Live data, TradingView charts, Smart agent, Beautiful animations
 * @version 4.0.0 - PRODUCTION READY
 */

import HTSEngine from './hts-engine.js';

// Configuration
const CONFIG = {
    updateInterval: 5000, // 5 seconds
    agentInterval: 60000, // 1 minute
    binanceWS: 'wss://stream.binance.com:9443/ws',
    binanceAPI: 'https://api.binance.com/api/v3',
    soundEnabled: true
};

// Crypto pairs
const CRYPTOS = [
    { symbol: 'BTC', name: 'Bitcoin', binance: 'BTCUSDT', icon: '₿' },
    { symbol: 'ETH', name: 'Ethereum', binance: 'ETHUSDT', icon: 'Ξ' },
    { symbol: 'BNB', name: 'Binance Coin', binance: 'BNBUSDT', icon: '🔸' },
    { symbol: 'SOL', name: 'Solana', binance: 'SOLUSDT', icon: '◎' },
    { symbol: 'XRP', name: 'Ripple', binance: 'XRPUSDT', icon: '✕' },
    { symbol: 'ADA', name: 'Cardano', binance: 'ADAUSDT', icon: '₳' }
];

// Strategies
const STRATEGIES = {
    'hts-hybrid': {
        name: '🔥 HTS Hybrid System',
        description: 'RSI+MACD (40%) + SMC (25%) + Patterns + AI',
        badge: 'PREMIUM',
        type: 'hybrid'
    },
    'trend-rsi-macd': {
        name: 'Trend + RSI + MACD',
        description: 'Classic momentum strategy',
        badge: 'STANDARD'
    },
    'scalping': {
        name: '⚡ Scalping',
        description: 'Quick trades, high frequency',
        badge: 'FAST'
    },
    'swing': {
        name: '📈 Swing Trading',
        description: 'Medium-term positions',
        badge: 'STABLE'
    }
};

/**
 * Main Trading System Class
 */
class EnhancedTradingSystem {
    constructor() {
        this.selectedCrypto = 'BTC';
        this.selectedStrategy = 'hts-hybrid';
        this.isAgentRunning = false;
        this.signals = [];
        this.prices = {};
        this.ws = null;
        this.chart = null;
        this.htsEngine = new HTSEngine();
        this.agentInterval = null;
        this.priceInterval = null;
        this.stats = {
            totalSignals: 0,
            winRate: 0
        };
    }

    /**
     * Initialize the system
     */
    async init() {
        console.log('[EnhancedTrading] 🚀 Initializing...');
        
        this.renderCryptoGrid();
        this.renderStrategyGrid();
        this.bindEvents();
        await this.initTradingViewChart();
        await this.loadInitialPrices();
        this.startPriceUpdates();
        
        this.showToast('🎉 System Ready!', 'success');
        this.updateLastUpdate();
        
        console.log('[EnhancedTrading] ✅ Ready!');
    }

    /**
     * Render crypto selection grid
     */
    renderCryptoGrid() {
        const container = document.getElementById('crypto-grid');
        if (!container) return;

        container.innerHTML = CRYPTOS.map(crypto => `
            <div class="crypto-btn ${crypto.symbol === this.selectedCrypto ? 'active' : ''}" 
                 data-symbol="${crypto.symbol}">
                <div class="crypto-symbol">${crypto.icon} ${crypto.symbol}</div>
                <div class="crypto-price" id="price-${crypto.symbol}">Loading...</div>
            </div>
        `).join('');

        // Add click handlers
        container.querySelectorAll('.crypto-btn').forEach(btn => {
            btn.addEventListener('click', () => {
                this.selectCrypto(btn.dataset.symbol);
            });
        });
    }

    /**
     * Render strategy selection grid
     */
    renderStrategyGrid() {
        const container = document.getElementById('strategy-grid');
        if (!container) return;

        container.innerHTML = Object.entries(STRATEGIES).map(([key, strategy]) => `
            <div class="strategy-card ${strategy.type === 'hybrid' ? 'hts-strategy' : ''} ${key === this.selectedStrategy ? 'active' : ''}" 
                 data-strategy="${key}">
                <div class="strategy-badge">${strategy.badge}</div>
                <div style="font-weight: 700; margin-bottom: 10px;">${strategy.name}</div>
                <div style="font-size: 0.85rem; color: rgba(255,255,255,0.7);">${strategy.description}</div>
            </div>
        `).join('');

        // Add click handlers
        container.querySelectorAll('.strategy-card').forEach(card => {
            card.addEventListener('click', () => {
                this.selectStrategy(card.dataset.strategy);
            });
        });
    }

    /**
     * Select crypto
     */
    selectCrypto(symbol) {
        this.selectedCrypto = symbol;
        
        // Update UI
        document.querySelectorAll('.crypto-btn').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.symbol === symbol);
        });

        // Update chart
        if (this.chart) {
            const crypto = CRYPTOS.find(c => c.symbol === symbol);
            this.chart.setSymbol(`BINANCE:${crypto.binance}`, '60');
        }

        this.showToast(`Selected ${symbol}`, 'info');
    }

    /**
     * Select strategy
     */
    selectStrategy(strategy) {
        this.selectedStrategy = strategy;
        
        // Update UI
        document.querySelectorAll('.strategy-card').forEach(card => {
            card.classList.toggle('active', card.dataset.strategy === strategy);
        });

        this.showToast(`Strategy: ${STRATEGIES[strategy].name}`, 'info');
    }

    /**
     * Bind event listeners
     */
    bindEvents() {
        // Start agent
        document.getElementById('start-agent-btn')?.addEventListener('click', () => {
            this.startAgent();
        });

        // Stop agent
        document.getElementById('stop-agent-btn')?.addEventListener('click', () => {
            this.stopAgent();
        });

        // Analyze button
        document.getElementById('analyze-btn')?.addEventListener('click', () => {
            this.analyzeMarket();
        });

        // Refresh button
        document.getElementById('refresh-btn')?.addEventListener('click', () => {
            this.refreshData();
        });
    }

    /**
     * Initialize TradingView chart
     */
    async initTradingViewChart() {
        const crypto = CRYPTOS.find(c => c.symbol === this.selectedCrypto);
        
        try {
            this.chart = new TradingView.widget({
                autosize: true,
                symbol: `BINANCE:${crypto.binance}`,
                interval: '60',
                timezone: 'Etc/UTC',
                theme: 'dark',
                style: '1',
                locale: 'en',
                toolbar_bg: '#0a0a0a',
                enable_publishing: false,
                hide_side_toolbar: false,
                allow_symbol_change: true,
                container_id: 'tradingview-chart',
                studies: [
                    'RSI@tv-basicstudies',
                    'MACD@tv-basicstudies',
                    'Volume@tv-basicstudies'
                ],
                disabled_features: ['use_localstorage_for_settings'],
                enabled_features: ['study_templates'],
                overrides: {
                    'mainSeriesProperties.candleStyle.upColor': '#00ff00',
                    'mainSeriesProperties.candleStyle.downColor': '#ff0000',
                    'mainSeriesProperties.candleStyle.borderUpColor': '#00ff00',
                    'mainSeriesProperties.candleStyle.borderDownColor': '#ff0000',
                    'mainSeriesProperties.candleStyle.wickUpColor': '#00ff00',
                    'mainSeriesProperties.candleStyle.wickDownColor': '#ff0000'
                }
            });
            
            console.log('[TradingView] Chart initialized');
        } catch (error) {
            console.error('[TradingView] Error:', error);
            this.showToast('Chart initialization failed', 'error');
        }
    }

    /**
     * Load initial prices
     */
    async loadInitialPrices() {
        console.log('[Prices] Loading initial prices...');
        
        for (const crypto of CRYPTOS) {
            try {
                const price = await this.fetchPrice(crypto.binance);
                this.prices[crypto.symbol] = price;
                this.updatePriceDisplay(crypto.symbol, price);
            } catch (error) {
                console.error(`[Prices] Error loading ${crypto.symbol}:`, error);
            }
        }

        // Update current price display
        const currentPrice = this.prices[this.selectedCrypto];
        if (currentPrice) {
            document.getElementById('current-price').textContent = `$${currentPrice.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
        }
    }

    /**
     * Fetch price from Binance
     */
    async fetchPrice(symbol) {
        try {
            const response = await fetch(`${CONFIG.binanceAPI}/ticker/price?symbol=${symbol}`, {
                signal: AbortSignal.timeout(5000)
            });
            
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const data = await response.json();
            return parseFloat(data.price);
        } catch (error) {
            console.error(`[Binance] Error fetching ${symbol}:`, error);
            throw error;
        }
    }

    /**
     * Fetch OHLCV data
     */
    async fetchOHLCV(symbol, interval = '1h', limit = 100) {
        try {
            const url = `${CONFIG.binanceAPI}/klines?symbol=${symbol}&interval=${interval}&limit=${limit}`;
            const response = await fetch(url, {
                signal: AbortSignal.timeout(10000)
            });
            
            if (!response.ok) throw new Error(`HTTP ${response.status}`);
            
            const data = await response.json();
            
            return data.map(candle => ({
                timestamp: candle[0],
                open: parseFloat(candle[1]),
                high: parseFloat(candle[2]),
                low: parseFloat(candle[3]),
                close: parseFloat(candle[4]),
                volume: parseFloat(candle[5])
            }));
        } catch (error) {
            console.error(`[Binance] OHLCV error:`, error);
            throw error;
        }
    }

    /**
     * Update price display
     */
    updatePriceDisplay(symbol, price) {
        const priceEl = document.getElementById(`price-${symbol}`);
        if (priceEl) {
            const formatted = price < 1 
                ? `$${price.toFixed(4)}`
                : `$${price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
            priceEl.textContent = formatted;
        }

        // Update current price if selected
        if (symbol === this.selectedCrypto) {
            const currentPriceEl = document.getElementById('current-price');
            if (currentPriceEl) {
                const formatted = price < 1 
                    ? `$${price.toFixed(4)}`
                    : `$${price.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
                currentPriceEl.textContent = formatted;
            }
        }
    }

    /**
     * Start price updates
     */
    startPriceUpdates() {
        if (this.priceInterval) return;

        this.priceInterval = setInterval(async () => {
            for (const crypto of CRYPTOS) {
                try {
                    const price = await this.fetchPrice(crypto.binance);
                    this.prices[crypto.symbol] = price;
                    this.updatePriceDisplay(crypto.symbol, price);
                } catch (error) {
                    // Silent fail
                }
            }
            this.updateLastUpdate();
        }, CONFIG.updateInterval);

        console.log('[Prices] Auto-update started');
    }

    /**
     * Start AI agent
     */
    async startAgent() {
        if (this.isAgentRunning) return;

        this.isAgentRunning = true;
        document.getElementById('start-agent-btn').style.display = 'none';
        document.getElementById('stop-agent-btn').style.display = 'block';
        document.getElementById('agent-status').textContent = 'Active 🟢';
        document.getElementById('agent-pairs').textContent = CRYPTOS.length;

        this.showToast('🤖 AI Agent Started!', 'success');
        this.playSound('start');

        // Run immediately
        await this.agentScan();

        // Then run periodically
        this.agentInterval = setInterval(() => {
            this.agentScan();
        }, CONFIG.agentInterval);

        console.log('[Agent] Started');
    }

    /**
     * Stop AI agent
     */
    stopAgent() {
        if (!this.isAgentRunning) return;

        this.isAgentRunning = false;
        document.getElementById('start-agent-btn').style.display = 'block';
        document.getElementById('stop-agent-btn').style.display = 'none';
        document.getElementById('agent-status').textContent = 'Stopped 🔴';

        if (this.agentInterval) {
            clearInterval(this.agentInterval);
            this.agentInterval = null;
        }

        this.showToast('🤖 AI Agent Stopped', 'info');
        console.log('[Agent] Stopped');
    }

    /**
     * Agent scan all pairs
     */
    async agentScan() {
        console.log('[Agent] 🔍 Scanning markets...');

        for (const crypto of CRYPTOS) {
            try {
                // Fetch OHLCV data
                const ohlcv = await this.fetchOHLCV(crypto.binance, '1h', 100);
                
                // Analyze with HTS
                const analysis = await this.htsEngine.analyze(ohlcv, crypto.symbol);
                
                // Generate signal if strong enough
                if (analysis.confidence >= 70 && analysis.finalSignal !== 'hold') {
                    this.addSignal({
                        symbol: crypto.symbol,
                        signal: analysis.finalSignal,
                        confidence: analysis.confidence,
                        price: analysis.currentPrice,
                        stopLoss: analysis.stopLoss,
                        takeProfits: analysis.takeProfitLevels,
                        strategy: 'HTS Hybrid',
                        timestamp: new Date(),
                        analysis: analysis
                    });
                }
            } catch (error) {
                console.error(`[Agent] Error scanning ${crypto.symbol}:`, error);
            }
        }
    }

    /**
     * Analyze current market
     */
    async analyzeMarket() {
        const btn = document.getElementById('analyze-btn');
        if (!btn) return;

        btn.disabled = true;
        btn.innerHTML = '<span style="position: relative; z-index: 1;">⏳ ANALYZING...</span>';

        try {
            const crypto = CRYPTOS.find(c => c.symbol === this.selectedCrypto);
            
            this.showToast(`Analyzing ${this.selectedCrypto}...`, 'info');

            // Fetch OHLCV data
            const ohlcv = await this.fetchOHLCV(crypto.binance, '1h', 100);

            // Analyze based on strategy
            let analysis;
            if (this.selectedStrategy === 'hts-hybrid') {
                analysis = await this.htsEngine.analyze(ohlcv, this.selectedCrypto);
            } else {
                // Use basic analysis for other strategies
                analysis = this.basicAnalysis(ohlcv);
            }

            // Add signal
            this.addSignal({
                symbol: this.selectedCrypto,
                signal: analysis.finalSignal || analysis.signal,
                confidence: analysis.confidence,
                price: analysis.currentPrice || ohlcv[ohlcv.length - 1].close,
                stopLoss: analysis.stopLoss,
                takeProfits: analysis.takeProfitLevels || [],
                strategy: STRATEGIES[this.selectedStrategy].name,
                timestamp: new Date(),
                analysis: analysis
            });

            this.showToast(`✅ Analysis Complete!`, 'success');
            this.playSound('signal');

        } catch (error) {
            console.error('[Analysis] Error:', error);
            this.showToast(`❌ Analysis failed: ${error.message}`, 'error');
        } finally {
            btn.disabled = false;
            btn.innerHTML = '<span style="position: relative; z-index: 1;">⚡ ANALYZE NOW</span>';
        }
    }

    /**
     * Basic analysis for non-HTS strategies
     */
    basicAnalysis(ohlcv) {
        const closes = ohlcv.map(c => c.close);
        const currentPrice = closes[closes.length - 1];
        
        // Simple RSI calculation
        const rsi = this.calculateRSI(closes, 14);
        
        let signal = 'hold';
        let confidence = 50;
        
        if (rsi < 30) {
            signal = 'buy';
            confidence = 70;
        } else if (rsi > 70) {
            signal = 'sell';
            confidence = 70;
        }

        const atr = (ohlcv[ohlcv.length - 1].high - ohlcv[ohlcv.length - 1].low);
        
        return {
            signal,
            confidence,
            currentPrice,
            stopLoss: signal === 'buy' ? currentPrice - (atr * 2) : currentPrice + (atr * 2),
            takeProfitLevels: [
                { level: signal === 'buy' ? currentPrice + (atr * 3) : currentPrice - (atr * 3), type: 'TP1' }
            ]
        };
    }

    /**
     * Calculate RSI
     */
    calculateRSI(prices, period = 14) {
        if (prices.length < period + 1) return 50;

        let gains = 0;
        let losses = 0;

        for (let i = 1; i <= period; i++) {
            const change = prices[i] - prices[i - 1];
            if (change > 0) gains += change;
            else losses += Math.abs(change);
        }

        const avgGain = gains / period;
        const avgLoss = losses / period;
        const rs = avgGain / (avgLoss || 1);
        return 100 - (100 / (1 + rs));
    }

    /**
     * Add signal to list
     */
    addSignal(signal) {
        this.signals.unshift(signal);
        if (this.signals.length > 50) {
            this.signals = this.signals.slice(0, 50);
        }

        this.renderSignals();
        this.updateStats();
    }

    /**
     * Render signals
     */
    renderSignals() {
        const container = document.getElementById('signals-container');
        if (!container) return;

        if (this.signals.length === 0) {
            container.innerHTML = `
                <div style="text-align: center; padding: 40px; color: rgba(255,255,255,0.5);">
                    <div style="font-size: 3rem; margin-bottom: 15px;">📡</div>
                    <div>No signals yet</div>
                </div>
            `;
            return;
        }

        container.innerHTML = this.signals.map(signal => `
            <div class="signal-item ${signal.signal}">
                <div class="signal-header">
                    <div>
                        <span class="signal-badge ${signal.signal}">${signal.signal.toUpperCase()}</span>
                        <strong style="margin-left: 10px;">${signal.symbol}</strong>
                    </div>
                    <div style="font-size: 0.85rem; color: rgba(255,255,255,0.7);">
                        ${signal.timestamp.toLocaleTimeString()}
                    </div>
                </div>
                <div style="margin-top: 15px;">
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px; margin-bottom: 10px;">
                        <div>
                            <div style="font-size: 0.8rem; color: rgba(255,255,255,0.6);">Entry Price</div>
                            <div style="font-weight: 700; color: var(--neon-cyan);">$${signal.price.toFixed(2)}</div>
                        </div>
                        <div>
                            <div style="font-size: 0.8rem; color: rgba(255,255,255,0.6);">Confidence</div>
                            <div style="font-weight: 700; color: var(--neon-green);">${signal.confidence.toFixed(0)}%</div>
                        </div>
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                        <div>
                            <div style="font-size: 0.8rem; color: rgba(255,255,255,0.6);">Stop Loss</div>
                            <div style="font-weight: 700; color: #ff0000;">$${signal.stopLoss.toFixed(2)}</div>
                        </div>
                        <div>
                            <div style="font-size: 0.8rem; color: rgba(255,255,255,0.6);">Take Profit</div>
                            <div style="font-weight: 700; color: var(--neon-green);">$${(signal.takeProfits[0]?.level || 0).toFixed(2)}</div>
                        </div>
                    </div>
                    <div style="margin-top: 10px; padding-top: 10px; border-top: 1px solid rgba(255,255,255,0.1);">
                        <div style="font-size: 0.75rem; color: rgba(255,255,255,0.5);">Strategy: ${signal.strategy}</div>
                    </div>
                </div>
            </div>
        `).join('');
    }

    /**
     * Update statistics
     */
    updateStats() {
        this.stats.totalSignals = this.signals.length;
        
        document.getElementById('total-signals').textContent = this.stats.totalSignals;
        document.getElementById('win-rate').textContent = `${this.stats.winRate}%`;
    }

    /**
     * Refresh all data
     */
    async refreshData() {
        this.showToast('🔄 Refreshing...', 'info');
        await this.loadInitialPrices();
        this.showToast('✅ Data refreshed!', 'success');
    }

    /**
     * Update last update time
     */
    updateLastUpdate() {
        const now = new Date();
        const timeStr = now.toLocaleTimeString();
        document.getElementById('last-update').textContent = timeStr;
    }

    /**
     * Show toast notification
     */
    showToast(message, type = 'info') {
        const container = document.getElementById('toast-container');
        if (!container) return;

        const colors = {
            success: 'var(--neon-green)',
            error: '#ff0000',
            info: 'var(--neon-cyan)',
            warning: 'var(--neon-orange)'
        };

        const toast = document.createElement('div');
        toast.className = 'toast';
        toast.style.borderColor = colors[type];
        toast.innerHTML = `
            <div style="display: flex; align-items: center; gap: 10px;">
                <div style="font-size: 1.5rem;">
                    ${type === 'success' ? '✅' : type === 'error' ? '❌' : type === 'warning' ? '⚠️' : 'ℹ️'}
                </div>
                <div style="flex: 1;">${message}</div>
            </div>
        `;

        container.appendChild(toast);

        setTimeout(() => {
            toast.style.animation = 'slideInRight 0.5s ease-out reverse';
            setTimeout(() => toast.remove(), 500);
        }, 3000);
    }

    /**
     * Play sound
     */
    playSound(type) {
        if (!CONFIG.soundEnabled) return;

        const audio = new Audio();
        
        if (type === 'signal') {
            audio.src = 'data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBTGH0fPTgjMGHm7A7+OZSA0PVKzn77BdGAg+ltryxnMpBSuAzvLaizsIGGS56+mjUBELTKXh8bllHAU2jdXzzn0vBSh+zPDckj4KE1y06+ytWxYKQ5zg8sFuJAU0iM/z1YU1Bx1qvO7mnEoPDlOq5O+zYBoGPJPY8sp0KwYpfsrw3ZI+ChNctOvrrVsWCkOc4PLBbiQFNIjP89WFNQcdarzv5pxKDw5TquTvs2AaBjyT2PLKdCsGKX7K8N2SPgoTXLTr661bFgpDnODywW4kBTSIz/PVhTUHHWq87+acSg8OU6rk77NgGgY8k9jyynQrBil+yvDdkj4KE1y06+utWxYKQ5zg8sFuJAU0iM/z1YU1Bx1qvO/mnEoPDlOq5O+zYBoGPJPY8sp0KwYpfsrw3ZI+ChNctOvrrVsWCkOc4PLBbiQFNIjP89WFNQcdarzv5pxKDw5TquTvs2AaBjyT2PLKdCsGKX7K8N2SPgoTXLTr661bFgpDnODywW4kBTSIz/PVhTUHHWq87+acSg8OU6rk77NgGgY8k9jyynQrBil+yvDdkj4KE1y06+utWxYKQ5zg8sFuJAU0iM/z1YU1Bx1qvO/mnEoPDlOq5O+zYBoGPJPY8sp0KwYpfsrw3ZI+ChNctOvrrVsWCkOc4PLBbiQFNIjP89WFNQcdarzv5pxKDw5TquTvs2AaBjyT2PLKdCsGKX7K8N2SPgoTXLTr661bFgpDnODywW4kBTSIz/PVhTUHHWq87+acSg8OU6rk77NgGgY8k9jyynQrBil+yvDdkj4KE1y06+utWxYKQ5zg8sFuJAU0iM/z1YU1Bx1qvO/mnEoPDlOq5O+zYBoGPJPY8sp0KwYpfsrw3ZI+ChNctOvrrVsWCkOc4PLBbiQFNIjP89WFNQcdarzv5pxKDw5TquTvs2AaBjyT2PLKdCsGKX7K8N2SPgoTXLTr661bFgpDnODywW4kBTSIz/PVhTUHHWq87+acSg8OU6rk77NgGgY8k9jyynQrBil+yvDdkj4KE1y06+utWxYKQ5zg8sFuJAU0iM/z1YU1Bx1qvO/mnEoPDlOq5O+zYBoGPJPY8sp0KwYpfsrw3ZI+ChNctOvrrVsWCkOc4PLBbiQFNIjP89WFNQcdarzv5pxKDw5TquTvs2AaBjyT2PLKdCsGKX7K8N2SPgoTXLTr661bFgpDnODywW4kBTSIz/PVhTUHHWq87+acSg8OU6rk77NgGgY8k9jyynQrBil+yvDdkj4=';
        } else if (type === 'start') {
            audio.src = 'data:audio/wav;base64,UklGRnoGAABXQVZFZm10IBAAAAABAAEAQB8AAEAfAAABAAgAZGF0YQoGAACBhYqFbF1fdJivrJBhNjVgodDbq2EcBj+a2/LDciUFLIHO8tiJNwgZaLvt559NEAxQp+PwtmMcBjiR1/LMeSwFJHfH8N2QQAoUXrTp66hVFApGn+DyvmwhBTGH0fPTgjMGHm7A7+OZSA0PVKzn77BdGAg+ltryxnMpBSuAzvLaizsIGGS56+mjUBELTKXh8bllHAU2jdXzzn0vBSh+zPDckj4KE1y06+ytWxYKQ5zg8sFuJAU0iM/z1YU1Bx1qvO7mnEoPDlOq5O+zYBoGPJPY8sp0KwYpfsrw3ZI+ChNctOvrrVsWCkOc4PLBbiQFNIjP89WFNQcdarzv5pxKDw5TquTvs2AaBjyT2PLKdCsGKX7K8N2SPgoTXLTr661bFgpDnODywW4kBTSIz/PVhTUHHWq87+acSg8OU6rk77NgGgY8k9jyynQrBil+yvDdkj4KE1y06+utWxYKQ5zg8sFuJAU0iM/z1YU1Bx1qvO/mnEoPDlOq5O+zYBoGPJPY8sp0KwYpfsrw3ZI+ChNctOvrrVsWCkOc4PLBbiQFNIjP89WFNQcdarzv5pxKDw5TquTvs2AaBjyT2PLKdCsGKX7K8N2SPgoTXLTr661bFgpDnODywW4kBTSIz/PVhTUHHWq87+acSg8OU6rk77NgGgY8k9jyynQrBil+yvDdkj4KE1y06+utWxYKQ5zg8sFuJAU0iM/z1YU1Bx1qvO/mnEoPDlOq5O+zYBoGPJPY8sp0KwYpfsrw3ZI+ChNctOvrrVsWCkOc4PLBbiQFNIjP89WFNQcdarzv5pxKDw5TquTvs2AaBjyT2PLKdCsGKX7K8N2SPgoTXLTr661bFgpDnODywW4kBTSIz/PVhTUHHWq87+acSg8OU6rk77NgGgY8k9jyynQrBil+yvDdkj4KE1y06+utWxYKQ5zg8sFuJAU0iM/z1YU1Bx1qvO/mnEoPDlOq5O+zYBoGPJPY8sp0KwYpfsrw3ZI+ChNctOvrrVsWCkOc4PLBbiQFNIjP89WFNQcdarzv5pxKDw5TquTvs2AaBjyT2PLKdCsGKX7K8N2SPgoTXLTr661bFgpDnODywW4kBTSIz/PVhTUHHWq87+acSg8OU6rk77NgGgY8k9jyynQrBil+yvDdkj4KE1y06+utWxYKQ5zg8sFuJAU0iM/z1YU1Bx1qvO/mnEoPDlOq5O+zYBoGPJPY8sp0KwYpfsrw3ZI+ChNctOvrrVsWCkOc4PLBbiQFNIjP89WFNQcdarzv5pxKDw5TquTvs2AaBjyT2PLKdCsGKX7K8N2SPgoTXLTr661bFgpDnODywW4kBTSIz/PVhTUHHWq87+acSg8OU6rk77NgGgY8k9jyynQrBil+yvDdkj4=';
        }
        
        audio.play().catch(() => {});
    }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    const system = new EnhancedTradingSystem();
    system.init();
    
    // Make it globally accessible for debugging
    window.tradingSystem = system;
});

