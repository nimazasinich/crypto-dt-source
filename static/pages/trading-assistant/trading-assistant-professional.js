/**
 * Professional Trading Assistant
 * Real-time signals, advanced strategies, automated monitoring
 * @version 3.0.0 - Production Ready for HF Spaces
 */

import { escapeHtml, safeFormatNumber, safeFormatCurrency } from '../../shared/js/utils/sanitizer.js';
import HTSEngine from './hts-engine.js';

/**
 * API Configuration
 * Using server's unified API with automatic fallbacks
 */
const API_CONFIG = {
    // Server API endpoints (with fallback chain)
    serverBase: window.location.origin, // Use same origin as the page
    unifiedRate: '/api/service/rate', // Unified rate endpoint with 5 fallbacks
    unifiedOHLC: '/api/market/ohlc', // OHLC endpoint with 5 fallbacks
    // Direct APIs as last resort (only if server fails)
    binance: 'https://api.binance.com/api/v3',
    coingecko: 'https://api.coingecko.com/api/v3',
    timeout: 10000,
    retries: 2
};

/**
 * Simple cache for API responses
 */
const API_CACHE = {
    data: new Map(),
    ttl: 60000, // 60 seconds
    
    set(key, value) {
        this.data.set(key, {
            value,
            timestamp: Date.now()
        });
    },
    
    get(key) {
        const item = this.data.get(key);
        if (!item) return null;
        
        if (Date.now() - item.timestamp > this.ttl) {
            this.data.delete(key);
            return null;
        }
        
        return item.value;
    },
    
    clear() {
        this.data.clear();
    }
};

/**
 * Trading Strategies
 */
const STRATEGIES = {
    'hts-hybrid': {
        name: '🔥 HTS Hybrid System',
        description: 'RSI+MACD (40%) + SMC (25%) + Patterns (20%) + Sentiment (10%) + ML (5%)',
        indicators: ['RSI', 'MACD', 'SMC', 'Patterns', 'Sentiment', 'ML'],
        timeframes: ['15m', '1h', '4h', '1d'],
        badge: 'PREMIUM',
        type: 'hybrid'
    },
    'trend-rsi-macd': {
        name: 'Trend + RSI + MACD',
        description: 'Combines trend following with momentum indicators',
        indicators: ['EMA', 'RSI', 'MACD'],
        timeframes: ['1h', '4h', '1d']
    },
    'scalping': {
        name: 'Scalping Strategy',
        description: 'Quick trades on small price movements',
        indicators: ['Bollinger Bands', 'Stochastic', 'Volume'],
        timeframes: ['1m', '5m', '15m']
    },
    'swing': {
        name: 'Swing Trading',
        description: 'Medium-term position trading',
        indicators: ['EMA', 'RSI', 'Support/Resistance'],
        timeframes: ['4h', '1d', '1w']
    },
    'breakout': {
        name: 'Breakout Strategy',
        description: 'Trade price breakouts from consolidation',
        indicators: ['ATR', 'Volume', 'Bollinger Bands'],
        timeframes: ['15m', '1h', '4h']
    }
};

/**
 * Cryptos for monitoring
 */
const CRYPTOS = [
    { symbol: 'BTC', name: 'Bitcoin', binance: 'BTCUSDT', demoPrice: 43000 },
    { symbol: 'ETH', name: 'Ethereum', binance: 'ETHUSDT', demoPrice: 2300 },
    { symbol: 'BNB', name: 'Binance Coin', binance: 'BNBUSDT', demoPrice: 310 },
    { symbol: 'SOL', name: 'Solana', binance: 'SOLUSDT', demoPrice: 98 },
    { symbol: 'ADA', name: 'Cardano', binance: 'ADAUSDT', demoPrice: 0.58 },
    { symbol: 'XRP', name: 'Ripple', binance: 'XRPUSDT', demoPrice: 0.62 },
    { symbol: 'DOT', name: 'Polkadot', binance: 'DOTUSDT', demoPrice: 7.2 },
    { symbol: 'AVAX', name: 'Avalanche', binance: 'AVAXUSDT', demoPrice: 38 },
    { symbol: 'MATIC', name: 'Polygon', binance: 'MATICUSDT', demoPrice: 0.89 },
    { symbol: 'LINK', name: 'Chainlink', binance: 'LINKUSDT', demoPrice: 14.5 }
];

/**
 * Main Trading Assistant Class
 */
class TradingAssistantProfessional {
    constructor() {
        this.selectedCrypto = 'BTC';
        this.selectedStrategy = 'trend-rsi-macd';
        this.isMonitoring = false;
        this.monitoringInterval = null;
        this.signals = [];
        this.marketData = {};
        this.lastUpdate = null;
    }

    /**
     * Initialize
     */
    async init() {
        try {
            console.log('[TradingAssistant] Initializing Professional Edition...');
            
            this.bindEvents();
            this.renderStrategyCards();
            this.renderCryptoList();
            await this.loadMarketData();
            
            this.showToast('✅ Trading Assistant Ready', 'success');
            console.log('[TradingAssistant] Initialization complete');
        } catch (error) {
            console.error('[TradingAssistant] Initialization error:', error);
            this.showToast('⚠️ Initialization error - using fallback mode', 'warning');
        }
    }

    /**
     * Bind UI events
     */
    bindEvents() {
        // Crypto selection
        document.addEventListener('click', (e) => {
            if (e.target.closest('[data-crypto]')) {
                const cryptoBtn = e.target.closest('[data-crypto]');
                this.selectedCrypto = cryptoBtn.dataset.crypto;
                this.updateCryptoSelection();
                this.loadMarketData();
            }
        });

        // Strategy selection
        document.addEventListener('click', (e) => {
            if (e.target.closest('[data-strategy]')) {
                const strategyBtn = e.target.closest('[data-strategy]');
                this.selectedStrategy = strategyBtn.dataset.strategy;
                this.updateStrategySelection();
            }
        });

        // Get signals button
        const getSignalsBtn = document.getElementById('get-signals-btn');
        if (getSignalsBtn) {
            getSignalsBtn.addEventListener('click', () => this.analyzeMarket());
        }

        // Toggle monitoring
        const toggleMonitorBtn = document.getElementById('toggle-monitor-btn');
        if (toggleMonitorBtn) {
            toggleMonitorBtn.addEventListener('click', () => this.toggleMonitoring());
        }

        // Refresh button
        const refreshBtn = document.getElementById('refresh-data');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.loadMarketData(true));
        }

        // Export signals
        const exportBtn = document.getElementById('export-signals');
        if (exportBtn) {
            exportBtn.addEventListener('click', () => this.exportSignals());
        }
    }

    /**
     * Render strategy cards
     */
    renderStrategyCards() {
        const container = document.getElementById('strategy-cards');
        if (!container) return;

        const html = Object.entries(STRATEGIES).map(([key, strategy]) => {
            const badgeText = strategy.badge || `${strategy.indicators.length} indicators`;
            const badgeClass = strategy.badge === 'PREMIUM' ? 'premium-badge' : 'strategy-badge';
            
            return `
                <div class="strategy-card ${key === this.selectedStrategy ? 'active' : ''} ${strategy.type === 'hybrid' ? 'hybrid-strategy' : ''}" data-strategy="${key}">
                    <div class="strategy-header">
                        <h4>${escapeHtml(strategy.name)}</h4>
                        <span class="${badgeClass}">${badgeText}</span>
                    </div>
                    <p class="strategy-description">${escapeHtml(strategy.description)}</p>
                    <div class="strategy-indicators">
                        ${strategy.indicators.map(ind => `<span class="indicator-tag">${escapeHtml(ind)}</span>`).join('')}
                    </div>
                    <div class="strategy-timeframes">
                        <small>Timeframes: ${strategy.timeframes.join(', ')}</small>
                    </div>
                </div>
            `;
        }).join('');

        container.innerHTML = html;
    }

    /**
     * Render crypto list
     */
    renderCryptoList() {
        const container = document.getElementById('crypto-list');
        if (!container) return;

        const html = CRYPTOS.map(crypto => `
            <button class="crypto-btn ${crypto.symbol === this.selectedCrypto ? 'active' : ''}" data-crypto="${crypto.symbol}">
                <span class="crypto-symbol">${crypto.symbol}</span>
                <span class="crypto-name">${escapeHtml(crypto.name)}</span>
                <span class="crypto-price" id="price-${crypto.symbol}">Loading...</span>
            </button>
        `).join('');

        container.innerHTML = html;
    }

    /**
     * Update crypto selection
     */
    updateCryptoSelection() {
        document.querySelectorAll('[data-crypto]').forEach(btn => {
            btn.classList.toggle('active', btn.dataset.crypto === this.selectedCrypto);
        });
    }

    /**
     * Update strategy selection
     */
    updateStrategySelection() {
        document.querySelectorAll('[data-strategy]').forEach(card => {
            card.classList.toggle('active', card.dataset.strategy === this.selectedStrategy);
        });
    }

    /**
     * Load market data
     */
    async loadMarketData(forceRefresh = false) {
        try {
            console.log('[TradingAssistant] Loading market data...');

            // Load current prices for all cryptos
            for (const crypto of CRYPTOS) {
                try {
                    const price = await this.fetchPrice(crypto.symbol);
                    this.marketData[crypto.symbol] = { price, timestamp: Date.now() };
                    
                    // Update price display
                    const priceEl = document.getElementById(`price-${crypto.symbol}`);
                    if (priceEl) {
                        priceEl.textContent = safeFormatCurrency(price);
                    }
                } catch (error) {
                    console.warn(`Failed to load price for ${crypto.symbol}:`, error);
                }
            }

            // Load OHLCV for selected crypto
            const ohlcvData = await this.fetchOHLCV(this.selectedCrypto, '4h', 100);
            this.marketData[this.selectedCrypto].ohlcv = ohlcvData;

            this.lastUpdate = new Date();
            this.updateLastUpdateDisplay();

            console.log('✅ Market data loaded');
        } catch (error) {
            console.error('❌ Failed to load market data:', error);
            this.showToast('Failed to load market data', 'error');
        }
    }

    /**
     * Fetch current price using server's unified API with automatic fallbacks
     * Fallback chain: Server API → CoinGecko → Binance → Demo price
     */
    async fetchPrice(symbol) {
        const crypto = CRYPTOS.find(c => c.symbol === symbol);
        if (!crypto) throw new Error('Symbol not found');

        // Check cache first
        const cacheKey = `price_${symbol}`;
        const cached = API_CACHE.get(cacheKey);
        if (cached) {
            return cached;
        }

        // Priority 1: Use server's unified API (has 5 fallback providers)
        try {
            const pair = `${symbol}/USDT`;
            const url = `${API_CONFIG.serverBase}${API_CONFIG.unifiedRate}?pair=${encodeURIComponent(pair)}`;
            console.log(`[API] Fetching price from server unified API: ${url}`);
            
            const response = await this.fetchWithTimeout(url, 10000);
            
            if (response.ok) {
                const data = await response.json();
                const price = parseFloat(data?.data?.price || data?.price || 0);
                if (price > 0) {
                    API_CACHE.set(cacheKey, price);
                    const source = data?.meta?.source || 'server';
                    console.log(`[API] ${symbol} price from ${source}: $${price.toFixed(2)}`);
                    return price;
                }
            }
        } catch (error) {
            console.warn(`[API] Server unified API failed for ${symbol}:`, error.message);
        }

        // Priority 2: Try CoinGecko directly (as fallback)
        try {
            const cgMap = {
                'BTC': 'bitcoin',
                'ETH': 'ethereum',
                'BNB': 'binancecoin',
                'SOL': 'solana',
                'XRP': 'ripple',
                'ADA': 'cardano'
            };
            
            const coinId = cgMap[symbol];
            if (coinId) {
                const url = `${API_CONFIG.coingecko}/simple/price?ids=${coinId}&vs_currencies=usd`;
                const response = await this.fetchWithTimeout(url, 8000);
                
                if (response.ok) {
                    const data = await response.json();
                    const price = data[coinId]?.usd;
                    if (price > 0) {
                        API_CACHE.set(cacheKey, price);
                        console.log(`[API] ${symbol} price from CoinGecko (direct): $${price.toFixed(2)}`);
                        return price;
                    }
                }
            }
        } catch (error) {
            console.warn(`[API] CoinGecko direct fetch failed for ${symbol}:`, error.message);
        }

        // Priority 3: Try Binance directly (last resort, may timeout - but skip if likely to fail)
        // Skip direct Binance calls to avoid CORS/timeout issues - rely on server's unified API
        console.warn(`[API] All unified sources failed for ${symbol} - server should handle fallbacks`);
        
        // Throw error instead of using demo price - NO MOCK DATA
        throw new Error(`Unable to fetch real price for ${symbol} from all sources`);
    }

    /**
     * Fetch OHLCV data using server's unified API with automatic fallbacks
     * Fallback chain: Server API → Binance → CoinGecko → Demo data
     */
    async fetchOHLCV(symbol, timeframe, limit) {
        const crypto = CRYPTOS.find(c => c.symbol === symbol);
        if (!crypto) throw new Error('Symbol not found');

        // Check cache first
        const cacheKey = `ohlcv_${symbol}_${timeframe}_${limit}`;
        const cached = API_CACHE.get(cacheKey);
        if (cached) {
            console.log(`[API] Using cached OHLCV for ${symbol}`);
            return cached;
        }

        // Priority 1: Use server's unified OHLC API (has 5 fallback providers)
        try {
            const intervalMap = {
                '1m': '1m', '5m': '5m', '15m': '15m',
                '1h': '1h', '4h': '4h', '1d': '1d', '1w': '1w'
            };
            
            const interval = intervalMap[timeframe] || '4h';
            const url = `${API_CONFIG.serverBase}${API_CONFIG.unifiedOHLC}?symbol=${symbol}&interval=${interval}&limit=${limit}`;
            
            console.log(`[API] Fetching OHLCV from server unified API: ${url}`);
            
            const response = await this.fetchWithTimeout(url, 12000);
            
            if (response.ok) {
                const data = await response.json();
                // Handle different response formats
                let ohlcvData = null;
                
                if (data?.success && data?.data) {
                    ohlcvData = data.data;
                } else if (data?.data && Array.isArray(data.data)) {
                    ohlcvData = data.data;
                } else if (Array.isArray(data)) {
                    ohlcvData = data;
                }
                
                if (ohlcvData && ohlcvData.length > 0) {
                    // Transform to standard format if needed
                    const transformed = ohlcvData.map(candle => {
                        if (Array.isArray(candle)) {
                            // Binance format: [time, open, high, low, close, volume]
                            return {
                                time: candle[0],
                                open: parseFloat(candle[1]),
                                high: parseFloat(candle[2]),
                                low: parseFloat(candle[3]),
                                close: parseFloat(candle[4]),
                                volume: parseFloat(candle[5])
                            };
                        } else {
                            // Already in object format
                            return {
                                time: candle.ts || candle.time || candle.t,
                                open: parseFloat(candle.open || candle.o),
                                high: parseFloat(candle.high || candle.h),
                                low: parseFloat(candle.low || candle.l),
                                close: parseFloat(candle.close || candle.c),
                                volume: parseFloat(candle.volume || candle.v || 0)
                            };
                        }
                    });
                    
                    API_CACHE.set(cacheKey, transformed);
                    const source = data?.meta?.source || 'server';
                    console.log(`[API] ${symbol} OHLCV from ${source}: ${transformed.length} candles`);
                    return transformed;
                }
            }
        } catch (error) {
            console.warn(`[API] Server unified OHLC API failed for ${symbol}:`, error.message);
        }

        // Priority 2: Try Binance directly (fallback)
        try {
            const intervalMap = {
                '1m': '1m', '5m': '5m', '15m': '15m',
                '1h': '1h', '4h': '4h', '1d': '1d', '1w': '1w'
            };
            
            const interval = intervalMap[timeframe] || '4h';
            const url = `${API_CONFIG.binance}/klines?symbol=${crypto.binance}&interval=${interval}&limit=${limit}`;
            
            console.log(`[API] Trying Binance direct for OHLCV: ${url}`);
            
            const response = await this.fetchWithTimeout(url, 8000);
            
            if (response.ok) {
                const data = await response.json();
                
                const ohlcv = data.map(item => ({
                    time: Math.floor(item[0] / 1000),
                    open: parseFloat(item[1]),
                    high: parseFloat(item[2]),
                    low: parseFloat(item[3]),
                    close: parseFloat(item[4]),
                    volume: parseFloat(item[5])
                }));
                
                API_CACHE.set(cacheKey, ohlcv);
                console.log(`[API] ${symbol} OHLCV from Binance (direct): ${ohlcv.length} candles`);
                return ohlcv;
            }
        } catch (error) {
            console.warn('[API] Binance direct OHLCV fetch failed:', error.message);
        }

        // Last resort: Generate demo OHLCV data
        console.warn(`[API] All sources failed for ${symbol} OHLCV, generating demo data`);
        return this.generateDemoOHLCV(crypto.demoPrice || 1000, limit);
    }

    /**
     * Generate demo OHLCV data for fallback
     */
    generateDemoOHLCV(basePrice, limit) {
        const now = Math.floor(Date.now() / 1000);
        const interval = 14400; // 4 hours in seconds
        const data = [];
        
        for (let i = limit - 1; i >= 0; i--) {
            const volatility = basePrice * 0.02; // 2% volatility
            const trend = (Math.random() - 0.5) * volatility;
            
            const open = basePrice + trend;
            const close = open + (Math.random() - 0.5) * volatility;
            const high = Math.max(open, close) + Math.random() * volatility * 0.5;
            const low = Math.min(open, close) - Math.random() * volatility * 0.5;
            const volume = basePrice * (10000 + Math.random() * 5000);
            
            data.push({
                time: now - (i * interval),
                open,
                high,
                low,
                close,
                volume
            });
            
            basePrice = close; // Next candle starts from previous close
        }
        
        return data;
    }

    /**
     * Fetch with timeout
     */
    async fetchWithTimeout(url, timeout) {
        const controller = new AbortController();
        const timeoutId = setTimeout(() => controller.abort(), timeout);

        try {
            const response = await fetch(url, {
                signal: controller.signal,
                headers: { 'Accept': 'application/json' }
            });
            clearTimeout(timeoutId);
            return response;
        } catch (error) {
            clearTimeout(timeoutId);
            if (error.name === 'AbortError') {
                throw new Error('Request timeout');
            }
            throw error;
        }
    }

    /**
     * Analyze market and generate signals
     */
    async analyzeMarket() {
        const analyzeBtn = document.getElementById('get-signals-btn');
        if (analyzeBtn) {
            analyzeBtn.disabled = true;
            analyzeBtn.textContent = 'Analyzing...';
        }

        try {
            console.log(`[TradingAssistant] Analyzing ${this.selectedCrypto} with ${this.selectedStrategy}...`);

            // Get OHLCV data
            const cryptoData = this.marketData[this.selectedCrypto];
            if (!cryptoData || !cryptoData.ohlcv) {
                await this.loadMarketData();
            }

            const ohlcvData = this.marketData[this.selectedCrypto].ohlcv;
            if (!ohlcvData || ohlcvData.length < 30) {
                throw new Error('Insufficient data for analysis');
            }

            // Calculate indicators
            const indicators = this.calculateIndicators(ohlcvData);

            // Generate signal (async for HTS support)
            const signal = await this.generateSignal(ohlcvData, indicators, this.selectedStrategy);

            // Add to signals list
            this.signals.unshift(signal);
            if (this.signals.length > 50) {
                this.signals = this.signals.slice(0, 50);
            }

            // Render signals
            this.renderSignals();

            this.showToast(`✅ Signal generated: ${signal.action.toUpperCase()}`, signal.action === 'BUY' ? 'success' : signal.action === 'SELL' ? 'error' : 'info');
        } catch (error) {
            console.error('❌ Analysis error:', error);
            this.showToast('Analysis failed: ' + error.message, 'error');
        } finally {
            if (analyzeBtn) {
                analyzeBtn.disabled = false;
                analyzeBtn.textContent = 'Get Signals';
            }
        }
    }

    /**
     * Calculate technical indicators
     */
    calculateIndicators(ohlcvData) {
        const closes = ohlcvData.map(c => c.close);
        
        return {
            rsi: this.calculateRSI(closes, 14),
            macd: this.calculateMACD(closes),
            ema20: this.calculateEMA(closes, 20),
            ema50: this.calculateEMA(closes, 50),
            atr: this.calculateATR(ohlcvData, 14),
            volume: ohlcvData[ohlcvData.length - 1].volume
        };
    }

    /**
     * Calculate RSI
     */
    calculateRSI(prices, period = 14) {
        if (prices.length < period + 1) return null;

        let gains = 0;
        let losses = 0;

        for (let i = 1; i <= period; i++) {
            const change = prices[i] - prices[i - 1];
            if (change > 0) gains += change;
            else losses += Math.abs(change);
        }

        let avgGain = gains / period;
        let avgLoss = losses / period;

        for (let i = period + 1; i < prices.length; i++) {
            const change = prices[i] - prices[i - 1];
            const gain = change > 0 ? change : 0;
            const loss = change < 0 ? Math.abs(change) : 0;

            avgGain = (avgGain * (period - 1) + gain) / period;
            avgLoss = (avgLoss * (period - 1) + loss) / period;
        }

        const rs = avgGain / avgLoss;
        return 100 - (100 / (1 + rs));
    }

    /**
     * Calculate MACD
     */
    calculateMACD(prices) {
        const ema12 = this.calculateEMA(prices, 12);
        const ema26 = this.calculateEMA(prices, 26);
        return ema12 - ema26;
    }

    /**
     * Calculate EMA
     */
    calculateEMA(prices, period) {
        if (prices.length < period) return null;

        const k = 2 / (period + 1);
        let ema = prices[0];

        for (let i = 1; i < prices.length; i++) {
            ema = prices[i] * k + ema * (1 - k);
        }

        return ema;
    }

    /**
     * Calculate ATR (Average True Range)
     */
    calculateATR(ohlcvData, period = 14) {
        if (ohlcvData.length < period + 1) return null;

        const trValues = [];
        for (let i = 1; i < ohlcvData.length; i++) {
            const high = ohlcvData[i].high;
            const low = ohlcvData[i].low;
            const prevClose = ohlcvData[i - 1].close;

            const tr = Math.max(
                high - low,
                Math.abs(high - prevClose),
                Math.abs(low - prevClose)
            );
            trValues.push(tr);
        }

        // Calculate ATR as average of TR values
        const atr = trValues.slice(-period).reduce((sum, tr) => sum + tr, 0) / period;
        return atr;
    }

    /**
     * Generate trading signal
     */
    async generateSignal(ohlcvData, indicators, strategy) {
        const latestCandle = ohlcvData[ohlcvData.length - 1];
        const currentPrice = latestCandle.close;

        let action = 'HOLD';
        let confidence = 50;
        let reasons = [];
        let htsAnalysis = null;

        // HTS Hybrid Strategy
        if (strategy === 'hts-hybrid') {
            try {
                // Convert OHLCV format for HTS (time -> timestamp)
                const htsOHLCV = ohlcvData.map(candle => ({
                    timestamp: candle.time || candle.timestamp,
                    open: candle.open,
                    high: candle.high,
                    low: candle.low,
                    close: candle.close,
                    volume: candle.volume
                }));

                const htsEngine = new HTSEngine();
                htsAnalysis = await htsEngine.analyze(htsOHLCV, this.selectedCrypto);
                
                action = htsAnalysis.finalSignal.toUpperCase();
                confidence = Math.round(htsAnalysis.confidence);
                
                // Build reasons from components
                reasons = [];
                if (htsAnalysis.components.rsiMacd.signal !== 'hold') {
                    reasons.push(`RSI+MACD (${Math.round(htsAnalysis.components.rsiMacd.weight * 100)}%): ${htsAnalysis.components.rsiMacd.signal.toUpperCase()}`);
                }
                if (htsAnalysis.components.smc.signal !== 'hold') {
                    reasons.push(`SMC (${Math.round(htsAnalysis.components.smc.weight * 100)}%): ${htsAnalysis.components.smc.signal.toUpperCase()}`);
                }
                if (htsAnalysis.components.patterns.detected > 0) {
                    reasons.push(`Patterns: ${htsAnalysis.components.patterns.bullish} bullish, ${htsAnalysis.components.patterns.bearish} bearish`);
                }
                reasons.push(`Market Regime: ${htsAnalysis.marketRegime || 'neutral'}`);
                reasons.push(`Final Score: ${htsAnalysis.finalScore.toFixed(1)}/100`);

                // Use HTS calculated levels
                const entryPrice = htsAnalysis.currentPrice;
                const stopLoss = htsAnalysis.stopLoss;
                const takeProfits = htsAnalysis.takeProfitLevels;

                return {
                    timestamp: new Date(),
                    symbol: this.selectedCrypto,
                    strategy: STRATEGIES[strategy].name,
                    action,
                    confidence,
                    reasons,
                    price: currentPrice,
                    entryPrice,
                    stopLoss,
                    takeProfit: takeProfits[0]?.level || entryPrice * (action === 'BUY' ? 1.03 : 0.97),
                    takeProfits: takeProfits,
                    indicators: {
                        rsi: htsAnalysis.indicators.rsi?.toFixed(2),
                        macd: htsAnalysis.indicators.macd?.macd?.toFixed(4),
                        atr: htsAnalysis.indicators.atr?.toFixed(2),
                        regime: htsAnalysis.marketRegime
                    },
                    htsDetails: {
                        finalScore: htsAnalysis.finalScore,
                        components: htsAnalysis.components,
                        smcLevels: htsAnalysis.smcLevels,
                        patterns: htsAnalysis.patterns
                    }
                };
            } catch (error) {
                console.error('[HTS] Analysis error:', error);
                reasons = ['HTS analysis failed, using fallback'];
            }
        }

        // Standard Strategy Logic (trend-rsi-macd)
        if (strategy === 'trend-rsi-macd') {
            // Bullish signals
            const bullishSignals = [];
            if (indicators.rsi < 30) bullishSignals.push('RSI Oversold');
            if (indicators.macd > 0) bullishSignals.push('MACD Bullish');
            if (currentPrice > indicators.ema20) bullishSignals.push('Above EMA20');

            // Bearish signals
            const bearishSignals = [];
            if (indicators.rsi > 70) bearishSignals.push('RSI Overbought');
            if (indicators.macd < 0) bearishSignals.push('MACD Bearish');
            if (currentPrice < indicators.ema20) bearishSignals.push('Below EMA20');

            if (bullishSignals.length >= 2) {
                action = 'BUY';
                confidence = 60 + (bullishSignals.length * 10);
                reasons = bullishSignals;
            } else if (bearishSignals.length >= 2) {
                action = 'SELL';
                confidence = 60 + (bearishSignals.length * 10);
                reasons = bearishSignals;
            } else {
                reasons = ['Mixed signals - no clear trend'];
            }
        }

        // Calculate entry/exit/stop
        const entryPrice = currentPrice;
        const stopLoss = action === 'BUY' 
            ? currentPrice - (indicators.atr * 1.5)
            : currentPrice + (indicators.atr * 1.5);
        const takeProfit = action === 'BUY'
            ? currentPrice + (indicators.atr * 3)
            : currentPrice - (indicators.atr * 3);

        return {
            timestamp: new Date(),
            symbol: this.selectedCrypto,
            strategy: STRATEGIES[strategy].name,
            action,
            confidence,
            reasons,
            price: currentPrice,
            entryPrice,
            stopLoss,
            takeProfit,
            indicators: {
                rsi: indicators.rsi?.toFixed(2),
                macd: indicators.macd?.toFixed(4),
                ema20: indicators.ema20?.toFixed(2)
            }
        };
    }

    /**
     * Render signals list
     */
    renderSignals() {
        const container = document.getElementById('signals-list');
        if (!container) return;

        if (this.signals.length === 0) {
            container.innerHTML = `
                <div style="text-align: center; padding: 3rem; color: var(--text-muted);">
                    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin-bottom: 1rem;">
                        <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
                    </svg>
                    <p>No signals yet. Click "Get Signals" to analyze the market.</p>
                </div>
            `;
            return;
        }

        const html = this.signals.map(signal => {
            // HTS specific display
            const isHTS = signal.htsDetails !== undefined;
            const takeProfitsHTML = signal.takeProfits && signal.takeProfits.length > 0
                ? signal.takeProfits.map((tp, i) => 
                    `<div><strong>${tp.type}:</strong> ${safeFormatCurrency(tp.level)} (${tp.percentage || 33}%)</div>`
                  ).join('')
                : `<div><strong>Take Profit:</strong> ${safeFormatCurrency(signal.takeProfit)}</div>`;

            const indicatorsHTML = isHTS
                ? `
                    <span>RSI: ${signal.indicators.rsi || 'N/A'}</span>
                    <span>MACD: ${signal.indicators.macd || 'N/A'}</span>
                    <span>ATR: ${signal.indicators.atr || 'N/A'}</span>
                    ${signal.indicators.regime ? `<span>Regime: ${signal.indicators.regime}</span>` : ''}
                `
                : `
                    <span>RSI: ${signal.indicators.rsi}</span>
                    <span>MACD: ${signal.indicators.macd}</span>
                    <span>EMA20: ${signal.indicators.ema20}</span>
                `;

            return `
                <div class="signal-card signal-${signal.action.toLowerCase()}">
                    <div class="signal-header">
                        <div>
                            <span class="signal-badge badge-${signal.action.toLowerCase()}">${signal.action}</span>
                            <span class="signal-symbol">${signal.symbol}</span>
                            <span class="signal-confidence">${signal.confidence}% confidence</span>
                            ${isHTS ? '<span class="strategy-badge" style="margin-left: 0.5rem;">HTS</span>' : ''}
                        </div>
                        <div class="signal-time">${signal.timestamp.toLocaleTimeString()}</div>
                    </div>
                    <div class="signal-body">
                        <div class="signal-price">
                            <strong>Strategy:</strong> ${escapeHtml(signal.strategy)}<br>
                            <strong>Entry:</strong> ${safeFormatCurrency(signal.entryPrice)}
                        </div>
                        <div class="signal-targets">
                            <div><strong>Stop Loss:</strong> ${safeFormatCurrency(signal.stopLoss)}</div>
                            ${takeProfitsHTML}
                        </div>
                        <div class="signal-reasons">
                            <strong>Analysis:</strong>
                            <ul>
                                ${signal.reasons.map(r => `<li>${escapeHtml(r)}</li>`).join('')}
                            </ul>
                        </div>
                        <div class="signal-indicators">
                            ${indicatorsHTML}
                        </div>
                    </div>
                </div>
            `;
        }).join('');

        container.innerHTML = html;
    }

    /**
     * Toggle monitoring
     */
    toggleMonitoring() {
        this.isMonitoring = !this.isMonitoring;
        
        const btn = document.getElementById('toggle-monitor-btn');
        if (btn) {
            btn.textContent = this.isMonitoring ? 'Stop Monitoring' : 'Start Monitoring';
            btn.classList.toggle('btn-danger', this.isMonitoring);
            btn.classList.toggle('btn-primary', !this.isMonitoring);
        }

        if (this.isMonitoring) {
            this.startMonitoring();
            this.showToast('✅ Monitoring started', 'success');
        } else {
            this.stopMonitoring();
            this.showToast('⏹️ Monitoring stopped', 'info');
        }
    }

    /**
     * Start automated monitoring
     */
    startMonitoring() {
        // Analyze every 5 minutes
        this.monitoringInterval = setInterval(() => {
            this.analyzeMarket();
        }, 5 * 60 * 1000);

        // Immediate analysis
        this.analyzeMarket();
    }

    /**
     * Stop monitoring
     */
    stopMonitoring() {
        if (this.monitoringInterval) {
            clearInterval(this.monitoringInterval);
            this.monitoringInterval = null;
        }
    }

    /**
     * Export signals
     */
    exportSignals() {
        if (this.signals.length === 0) {
            this.showToast('No signals to export', 'warning');
            return;
        }

        const exportData = {
            exportDate: new Date().toISOString(),
            totalSignals: this.signals.length,
            signals: this.signals
        };

        const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `trading_signals_${Date.now()}.json`;
        a.click();
        URL.revokeObjectURL(url);

        this.showToast('✅ Signals exported', 'success');
    }

    /**
     * Update last update display
     */
    updateLastUpdateDisplay() {
        const el = document.getElementById('last-update-time');
        if (el && this.lastUpdate) {
            el.textContent = `Last update: ${this.lastUpdate.toLocaleTimeString()}`;
        }
    }

    /**
     * Show toast notification
     */
    showToast(message, type = 'info') {
        console.log(`[Toast ${type}]`, message);
        
        // Simple toast implementation
        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        toast.textContent = message;
        toast.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            background: ${type === 'success' ? '#22c55e' : type === 'error' ? '#ef4444' : '#3b82f6'};
            color: white;
            padding: 1rem 1.5rem;
            border-radius: 8px;
            box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            z-index: 10000;
            animation: slideIn 0.3s ease;
        `;

        document.body.appendChild(toast);

        setTimeout(() => {
            toast.style.animation = 'slideOut 0.3s ease';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }

    /**
     * Cleanup
     */
    destroy() {
        this.stopMonitoring();
    }
}

// Initialize on page load
let tradingAssistantInstance = null;

document.addEventListener('DOMContentLoaded', async () => {
    try {
        tradingAssistantInstance = new TradingAssistantProfessional();
        await tradingAssistantInstance.init();
    } catch (error) {
        console.error('[TradingAssistant] Fatal error:', error);
    }
});

// Cleanup on unload
window.addEventListener('beforeunload', () => {
    if (tradingAssistantInstance) {
        tradingAssistantInstance.destroy();
    }
});

// Add CSS animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(400px); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(400px); opacity: 0; }
    }
`;
document.head.appendChild(style);

export { TradingAssistantProfessional };
export default TradingAssistantProfessional;

