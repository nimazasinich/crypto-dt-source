/**
 * Professional Technical Analysis Page
 * Real-time data, advanced indicators, professional UI
 * @version 3.0.0 - Production Ready for HF Spaces
 */

import { Toast } from '../../shared/js/components/toast.js';
import { escapeHtml, safeFormatNumber, safeFormatCurrency } from '../../shared/js/utils/sanitizer.js';

/**
 * API Configuration - HF Spaces Compatible
 */
const API_CONFIG = {
    backend: window.location.origin + '/api',
    timeout: 8000, // Reduced for faster fallback
    retries: 1, // Reduced retries for faster fallback
    fallbacks: {
        coingecko: 'https://api.coingecko.com/api/v3',
        binance: 'https://api.binance.com/api/v3',
        cryptocompare: 'https://min-api.cryptocompare.com/data'
    }
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
 * Symbol Mapping for different exchanges
 */
const SYMBOL_MAPPING = {
    'BTC': { coingecko: 'bitcoin', binance: 'BTCUSDT', cc: 'BTC' },
    'ETH': { coingecko: 'ethereum', binance: 'ETHUSDT', cc: 'ETH' },
    'BNB': { coingecko: 'binancecoin', binance: 'BNBUSDT', cc: 'BNB' },
    'SOL': { coingecko: 'solana', binance: 'SOLUSDT', cc: 'SOL' },
    'ADA': { coingecko: 'cardano', binance: 'ADAUSDT', cc: 'ADA' },
    'XRP': { coingecko: 'ripple', binance: 'XRPUSDT', cc: 'XRP' },
    'DOT': { coingecko: 'polkadot', binance: 'DOTUSDT', cc: 'DOT' },
    'DOGE': { coingecko: 'dogecoin', binance: 'DOGEUSDT', cc: 'DOGE' },
    'AVAX': { coingecko: 'avalanche-2', binance: 'AVAXUSDT', cc: 'AVAX' },
    'MATIC': { coingecko: 'matic-network', binance: 'MATICUSDT', cc: 'MATIC' }
};

/**
 * Timeframe conversion for different APIs
 */
const TIMEFRAME_MAP = {
    '1m': { binance: '1m', cc: 1 },
    '5m': { binance: '5m', cc: 5 },
    '15m': { binance: '15m', cc: 15 },
    '1h': { binance: '1h', cc: 60 },
    '4h': { binance: '4h', cc: 240 },
    '1d': { binance: '1d', cc: 1440 },
    '1w': { binance: '1w', cc: 10080 }
};

/**
 * Main Technical Analysis Class
 */
class TechnicalAnalysisProfessional {
    constructor() {
        this.chart = null;
        this.candlestickSeries = null;
        this.volumeSeries = null;
        this.currentSymbol = 'BTC';
        this.currentTimeframe = '4h';
        this.currentMode = 'quick';
        this.ohlcvData = [];
        this.indicators = {
            rsi: null,
            macd: null,
            ema: null,
            volume: null
        };
        this.dataSource = 'none';
        this.lastUpdate = null;
        this.autoRefreshInterval = null;
        this.isLoading = false;
    }

    /**
     * Initialize the page
     */
    async init() {
        try {
            console.log('[TechnicalAnalysis] Initializing Professional Edition...');
            
            this.bindEvents();
            this.initializeChart();
            await this.loadMarketData();
            this.setupAutoRefresh();
            
            this.showToast('✅ Technical Analysis Ready', 'success');
            console.log('[TechnicalAnalysis] Initialization complete');
        } catch (error) {
            console.error('[TechnicalAnalysis] Initialization error:', error);
            this.showToast('⚠️ Initialization error - using fallback mode', 'warning');
        }
    }

    /**
     * Bind UI events
     */
    bindEvents() {
        // Symbol selection
        const symbolSelect = document.getElementById('symbol-select');
        if (symbolSelect) {
            symbolSelect.addEventListener('change', (e) => {
                this.currentSymbol = e.target.value;
                this.loadMarketData();
            });
        }

        // Timeframe selection
        const timeframeButtons = document.querySelectorAll('[data-timeframe]');
        timeframeButtons.forEach(btn => {
            btn.addEventListener('click', (e) => {
                timeframeButtons.forEach(b => b.classList.remove('active'));
                e.currentTarget.classList.add('active');
                this.currentTimeframe = e.currentTarget.dataset.timeframe;
                this.loadMarketData();
            });
        });

        // Mode tabs
        const modeTabs = document.querySelectorAll('[data-mode]');
        modeTabs.forEach(tab => {
            tab.addEventListener('click', (e) => {
                modeTabs.forEach(t => t.classList.remove('active'));
                e.currentTarget.classList.add('active');
                this.currentMode = e.currentTarget.dataset.mode;
                this.performAnalysis();
            });
        });

        // Analyze button
        const analyzeBtn = document.getElementById('analyze-btn');
        if (analyzeBtn) {
            analyzeBtn.addEventListener('click', () => this.performAnalysis());
        }

        // Refresh button
        const refreshBtn = document.getElementById('refresh-data');
        if (refreshBtn) {
            refreshBtn.addEventListener('click', () => this.loadMarketData(true));
        }

        // Export button
        const exportBtn = document.getElementById('export-analysis');
        if (exportBtn) {
            exportBtn.addEventListener('click', () => this.exportAnalysis());
        }
    }

    /**
     * Initialize Lightweight Charts
     */
    initializeChart() {
        const chartContainer = document.getElementById('tradingview-chart');
        if (!chartContainer) {
            console.warn('Chart container not found');
            return;
        }

        try {
            // Check if LightweightCharts is loaded
            if (typeof LightweightCharts === 'undefined') {
                console.warn('LightweightCharts not loaded, showing fallback');
                this.showChartFallback();
                return;
            }

            // Create chart
            this.chart = LightweightCharts.createChart(chartContainer, {
                width: chartContainer.clientWidth,
                height: 500,
                layout: {
                    background: { color: 'transparent' },
                    textColor: '#d1d5db',
                },
                grid: {
                    vertLines: { color: 'rgba(255, 255, 255, 0.05)' },
                    horzLines: { color: 'rgba(255, 255, 255, 0.05)' },
                },
                crosshair: {
                    mode: LightweightCharts.CrosshairMode.Normal,
                },
                rightPriceScale: {
                    borderColor: 'rgba(255, 255, 255, 0.1)',
                },
                timeScale: {
                    borderColor: 'rgba(255, 255, 255, 0.1)',
                    timeVisible: true,
                    secondsVisible: false,
                },
            });

            // Add candlestick series
            this.candlestickSeries = this.chart.addCandlestickSeries({
                upColor: '#22c55e',
                downColor: '#ef4444',
                borderVisible: false,
                wickUpColor: '#22c55e',
                wickDownColor: '#ef4444',
            });

            // Add volume series
            this.volumeSeries = this.chart.addHistogramSeries({
                color: '#26a69a',
                priceFormat: {
                    type: 'volume',
                },
                priceScaleId: '',
                scaleMargins: {
                    top: 0.8,
                    bottom: 0,
                },
            });

            // Handle resize
            window.addEventListener('resize', () => {
                if (this.chart && chartContainer) {
                    this.chart.applyOptions({
                        width: chartContainer.clientWidth
                    });
                }
            });

            console.log('✅ Chart initialized successfully');
        } catch (error) {
            console.error('❌ Chart initialization error:', error);
            this.showChartFallback();
        }
    }

    /**
     * Show fallback when chart fails
     */
    showChartFallback() {
        const chartContainer = document.getElementById('tradingview-chart');
        if (chartContainer) {
            chartContainer.innerHTML = `
                <div style="display: flex; align-items: center; justify-content: center; height: 500px; background: rgba(0,0,0,0.2); border-radius: 12px;">
                    <div style="text-align: center; color: #9ca3af;">
                        <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="margin: 0 auto 1rem;">
                            <path d="M3 3v18h18"></path>
                            <path d="M19 9l-5 5-4-4-3 3"></path>
                        </svg>
                        <p style="font-size: 1.1rem; margin-bottom: 0.5rem;">Chart Loading...</p>
                        <p style="font-size: 0.875rem; opacity: 0.7;">Analysis data will still be available</p>
                    </div>
                </div>
            `;
        }
    }

    /**
     * Load market data from backend + fallbacks
     */
    async loadMarketData(forceRefresh = false) {
        if (this.isLoading) {
            console.log('Already loading data, skipping...');
            return;
        }

        this.isLoading = true;
        this.showLoadingState(true);

        try {
            console.log(`[TechnicalAnalysis] Loading data for ${this.currentSymbol} (${this.currentTimeframe})...`);

            // Check cache first
            const cacheKey = `ohlcv_${this.currentSymbol}_${this.currentTimeframe}`;
            const cached = API_CACHE.get(cacheKey);
            if (cached) {
                console.log('✅ Using cached data');
                this.ohlcvData = cached;
                this.dataSource = 'cache';
                this.lastUpdate = new Date();
                
                this.updateChart(cached);
                this.updatePriceInfo(cached[cached.length - 1]);
                this.calculateIndicators(cached);
                this.performAnalysis();
                
                this.showToast(`✅ Data loaded from cache`, 'success');
                return;
            }

            // Try backend first
            let ohlcvData = null;
            try {
                ohlcvData = await this.fetchFromBackend(this.currentSymbol, this.currentTimeframe);
                this.dataSource = 'backend';
                console.log('✅ Data loaded from backend');
            } catch (backendError) {
                console.warn('Backend API failed, trying fallbacks...', backendError.message || backendError);
            }

            // Fallback to Binance
            if (!ohlcvData || ohlcvData.length === 0) {
                try {
                    ohlcvData = await this.fetchFromBinance(this.currentSymbol, this.currentTimeframe);
                    this.dataSource = 'binance';
                    console.log('✅ Data loaded from Binance');
                } catch (binanceError) {
                    console.warn('Binance API failed, trying CryptoCompare...', binanceError);
                }
            }

            // Fallback to CryptoCompare
            if (!ohlcvData || ohlcvData.length === 0) {
                try {
                    ohlcvData = await this.fetchFromCryptoCompare(this.currentSymbol, this.currentTimeframe);
                    this.dataSource = 'cryptocompare';
                    console.log('✅ Data loaded from CryptoCompare');
                } catch (ccError) {
                    console.warn('CryptoCompare API failed', ccError);
                }
            }

            // Validate data - NO DEMO DATA, show error if all sources fail
            if (!ohlcvData || ohlcvData.length === 0) {
                console.error('❌ All data sources failed - no real data available');
                this.showErrorState('Unable to fetch real market data. Please check your connection and try again.');
                this.showToast('❌ Failed to load real data from all sources', 'error');
                return;
            } else {
                // Save to cache
                API_CACHE.set(cacheKey, ohlcvData);
            }

            this.ohlcvData = ohlcvData;
            this.lastUpdate = new Date();
            
            this.updateChart(ohlcvData);
            this.updatePriceInfo(ohlcvData[ohlcvData.length - 1]);
            this.calculateIndicators(ohlcvData);
            this.performAnalysis();

            this.showToast(`✅ Data loaded from ${this.dataSource}`, 'success');
        } catch (error) {
            console.error('❌ Failed to load market data:', error);
            this.showToast('❌ Failed to load data - please try again', 'error');
            this.showErrorState(error.message);
        } finally {
            this.isLoading = false;
            this.showLoadingState(false);
        }
    }

    /**
     * Fetch OHLCV from backend unified API
     */
    async fetchFromBackend(symbol, timeframe) {
        // Try unified OHLC API first
        try {
            const unifiedUrl = `${API_CONFIG.backend}/market/ohlc?symbol=${symbol}&interval=${timeframe}&limit=100`;
            const unifiedResponse = await this.fetchWithTimeout(unifiedUrl, API_CONFIG.timeout);
            
            if (unifiedResponse.ok) {
                const unifiedData = await unifiedResponse.json();
                const items = unifiedData.data || unifiedData.ohlcv || unifiedData.items || (Array.isArray(unifiedData) ? unifiedData : []);
                
                if (Array.isArray(items) && items.length > 0) {
                    return this.normalizeOHLCV(items);
                }
            }
        } catch (e) {
            console.warn('[TechnicalAnalysis] Unified OHLC API failed, trying legacy endpoint:', e.message);
        }
        
        // Fallback to legacy endpoint
        const url = `${API_CONFIG.backend}/ohlcv/${symbol}?interval=${timeframe}&limit=100`;
        const response = await this.fetchWithTimeout(url, API_CONFIG.timeout);
        
        if (!response.ok) {
            throw new Error(`Backend API error: ${response.status}`);
        }

        const data = await response.json();
        
        // Handle different response formats
        const items = data.data || data.ohlcv || data.items || (Array.isArray(data) ? data : []);
        
        if (!Array.isArray(items) || items.length === 0) {
            throw new Error('Invalid or empty data from backend');
        }

        // Normalize and validate data
        return this.normalizeOHLCV(items);
    }

    /**
     * Fetch OHLCV from Binance
     */
    async fetchFromBinance(symbol, timeframe) {
        const mapping = SYMBOL_MAPPING[symbol];
        if (!mapping) {
            throw new Error(`Symbol ${symbol} not supported`);
        }

        const binanceSymbol = mapping.binance;
        const interval = TIMEFRAME_MAP[timeframe]?.binance || '4h';
        
        const url = `${API_CONFIG.fallbacks.binance}/klines?symbol=${binanceSymbol}&interval=${interval}&limit=100`;
        
        const response = await this.fetchWithTimeout(url, API_CONFIG.timeout);
        
        if (!response.ok) {
            throw new Error(`Binance API error: ${response.status}`);
        }

        const data = await response.json();
        
        if (!Array.isArray(data) || data.length === 0) {
            throw new Error('Invalid data from Binance');
        }

        // Convert Binance format to standard OHLCV
        return data.map(item => ({
            time: Math.floor(item[0] / 1000), // Convert ms to seconds
            open: parseFloat(item[1]),
            high: parseFloat(item[2]),
            low: parseFloat(item[3]),
            close: parseFloat(item[4]),
            volume: parseFloat(item[5])
        }));
    }

    /**
     * Fetch OHLCV from CryptoCompare
     */
    async fetchFromCryptoCompare(symbol, timeframe) {
        const mapping = SYMBOL_MAPPING[symbol];
        if (!mapping) {
            throw new Error(`Symbol ${symbol} not supported`);
        }

        const ccSymbol = mapping.cc;
        const limit = 100;
        
        // Determine endpoint based on timeframe
        let endpoint;
        if (['1m', '5m', '15m'].includes(timeframe)) {
            endpoint = 'histominute';
        } else if (['1h', '4h'].includes(timeframe)) {
            endpoint = 'histohour';
        } else {
            endpoint = 'histoday';
        }
        
        const url = `${API_CONFIG.fallbacks.cryptocompare}/${endpoint}?fsym=${ccSymbol}&tsym=USD&limit=${limit}`;
        
        const response = await this.fetchWithTimeout(url, API_CONFIG.timeout);
        
        if (!response.ok) {
            throw new Error(`CryptoCompare API error: ${response.status}`);
        }

        const data = await response.json();
        
        if (data.Response === 'Error' || !data.Data || !Array.isArray(data.Data)) {
            throw new Error('Invalid data from CryptoCompare');
        }

        // Convert CryptoCompare format to standard OHLCV
        return data.Data.map(item => ({
            time: item.time,
            open: item.open,
            high: item.high,
            low: item.low,
            close: item.close,
            volume: item.volumefrom
        }));
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
                headers: {
                    'Accept': 'application/json'
                }
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
     * Normalize OHLCV data to standard format
     */
    normalizeOHLCV(items) {
        return items.map(item => {
            const normalized = {
                time: this.parseTime(item.timestamp || item.time || item.t || item.date),
                open: parseFloat(item.open || item.o),
                high: parseFloat(item.high || item.h),
                low: parseFloat(item.low || item.l),
                close: parseFloat(item.close || item.c),
                volume: parseFloat(item.volume || item.v || 0)
            };

            // Validate
            if (!normalized.time || isNaN(normalized.time)) {
                throw new Error('Invalid timestamp in OHLCV data');
            }
            if (isNaN(normalized.open) || isNaN(normalized.high) || 
                isNaN(normalized.low) || isNaN(normalized.close)) {
                throw new Error('Invalid OHLCV values');
            }
            if (normalized.high < normalized.low) {
                throw new Error('Invalid OHLCV: high < low');
            }

            return normalized;
        }).filter(item => item.close > 0); // Remove invalid entries
    }

    /**
     * Parse time to unix timestamp
     */
    parseTime(time) {
        if (typeof time === 'number') {
            // If it's already a timestamp, ensure it's in seconds
            return time > 10000000000 ? Math.floor(time / 1000) : time;
        }
        if (typeof time === 'string') {
            return Math.floor(new Date(time).getTime() / 1000);
        }
        throw new Error('Invalid time format');
    }

    /**
     * Update chart with new data
     */
    updateChart(ohlcvData) {
        if (!this.chart || !this.candlestickSeries) {
            console.warn('Chart not initialized, skipping update');
            return;
        }

        try {
            // Prepare candlestick data
            const candleData = ohlcvData.map(item => ({
                time: item.time,
                open: item.open,
                high: item.high,
                low: item.low,
                close: item.close
            }));

            // Prepare volume data
            const volumeData = ohlcvData.map(item => ({
                time: item.time,
                value: item.volume,
                color: item.close >= item.open ? 'rgba(34, 197, 94, 0.5)' : 'rgba(239, 68, 68, 0.5)'
            }));

            this.candlestickSeries.setData(candleData);
            this.volumeSeries.setData(volumeData);

            // Fit content
            this.chart.timeScale().fitContent();

            console.log('✅ Chart updated with', candleData.length, 'candles');
        } catch (error) {
            console.error('❌ Chart update error:', error);
        }
    }

    /**
     * Update price information display
     */
    updatePriceInfo(latestCandle) {
        if (!latestCandle) return;

        const priceElement = document.getElementById('current-price');
        const changeElement = document.getElementById('price-change');
        const highElement = document.getElementById('24h-high');
        const lowElement = document.getElementById('24h-low');
        const volumeElement = document.getElementById('24h-volume');

        if (priceElement) {
            priceElement.textContent = safeFormatCurrency(latestCandle.close);
        }

        // Calculate 24h change
        if (this.ohlcvData.length > 1) {
            const oldPrice = this.ohlcvData[0].close;
            const newPrice = latestCandle.close;
            const change = ((newPrice - oldPrice) / oldPrice) * 100;
            
            if (changeElement) {
                const arrow = change >= 0 ? '↑' : '↓';
                const color = change >= 0 ? '#22c55e' : '#ef4444';
                changeElement.textContent = `${arrow} ${Math.abs(change).toFixed(2)}%`;
                changeElement.style.color = color;
            }
        }

        // Calculate 24h high/low
        if (highElement && lowElement) {
            const prices = this.ohlcvData.map(c => [c.high, c.low]).flat();
            highElement.textContent = safeFormatCurrency(Math.max(...prices));
            lowElement.textContent = safeFormatCurrency(Math.min(...prices));
        }

        // Calculate total volume
        if (volumeElement) {
            const totalVolume = this.ohlcvData.reduce((sum, c) => sum + c.volume, 0);
            volumeElement.textContent = safeFormatNumber(totalVolume);
        }

        // Update last update time
        const lastUpdateEl = document.getElementById('last-update');
        if (lastUpdateEl) {
            lastUpdateEl.textContent = `Last update: ${new Date().toLocaleTimeString()}`;
        }

        // Update data source
        const dataSourceEl = document.getElementById('data-source');
        if (dataSourceEl) {
            dataSourceEl.textContent = `Source: ${this.dataSource}`;
        }
    }

    /**
     * Calculate technical indicators
     */
    calculateIndicators(ohlcvData) {
        if (!ohlcvData || ohlcvData.length < 14) {
            console.warn('Not enough data for indicators');
            return;
        }

        // Calculate RSI
        this.indicators.rsi = this.calculateRSI(ohlcvData);

        // Calculate MACD
        this.indicators.macd = this.calculateMACD(ohlcvData);

        // Calculate EMA
        this.indicators.ema = this.calculateEMA(ohlcvData, 20);
        
        // Calculate Bollinger Bands
        this.indicators.bollingerBands = this.calculateBollingerBands(ohlcvData);
        
        // Calculate SMA
        this.indicators.sma20 = this.calculateSMA(ohlcvData, 20);
        this.indicators.sma50 = this.calculateSMA(ohlcvData, 50);
        
        // Calculate Stochastic RSI
        this.indicators.stochRsi = this.calculateStochRSI(ohlcvData);
        
        // Calculate ATR (Average True Range)
        this.indicators.atr = this.calculateATR(ohlcvData);

        // Update indicator displays
        this.updateIndicatorDisplays();
    }
    
    /**
     * Calculate Bollinger Bands
     */
    calculateBollingerBands(data, period = 20, stdDev = 2) {
        if (data.length < period) return null;
        
        const closes = data.map(d => d.close);
        const sma = this.calculateSMA(data, period);
        
        // Calculate standard deviation
        const slice = closes.slice(-period);
        const mean = slice.reduce((a, b) => a + b, 0) / period;
        const variance = slice.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / period;
        const std = Math.sqrt(variance);
        
        return {
            upper: sma + (stdDev * std),
            middle: sma,
            lower: sma - (stdDev * std),
            bandwidth: ((sma + (stdDev * std)) - (sma - (stdDev * std))) / sma * 100
        };
    }
    
    /**
     * Calculate Simple Moving Average
     */
    calculateSMA(data, period) {
        if (data.length < period) return null;
        const closes = data.slice(-period).map(d => d.close);
        return closes.reduce((a, b) => a + b, 0) / period;
    }
    
    /**
     * Calculate Stochastic RSI
     */
    calculateStochRSI(data, rsiPeriod = 14, stochPeriod = 14) {
        if (data.length < rsiPeriod + stochPeriod) return null;
        
        // First calculate RSI values for last stochPeriod+1 candles
        const rsiValues = [];
        for (let i = data.length - stochPeriod - 1; i < data.length; i++) {
            const slice = data.slice(Math.max(0, i - rsiPeriod), i + 1);
            if (slice.length >= rsiPeriod) {
                const rsi = this.calculateRSI(slice, rsiPeriod);
                if (rsi !== null) rsiValues.push(rsi);
            }
        }
        
        if (rsiValues.length < 2) return null;
        
        const minRsi = Math.min(...rsiValues);
        const maxRsi = Math.max(...rsiValues);
        const currentRsi = rsiValues[rsiValues.length - 1];
        
        if (maxRsi === minRsi) return 50;
        
        return ((currentRsi - minRsi) / (maxRsi - minRsi)) * 100;
    }
    
    /**
     * Calculate Average True Range (ATR)
     */
    calculateATR(data, period = 14) {
        if (data.length < period + 1) return null;
        
        const trueRanges = [];
        for (let i = 1; i < data.length; i++) {
            const high = data[i].high;
            const low = data[i].low;
            const prevClose = data[i - 1].close;
            
            const tr = Math.max(
                high - low,
                Math.abs(high - prevClose),
                Math.abs(low - prevClose)
            );
            trueRanges.push(tr);
        }
        
        // Calculate ATR as SMA of true ranges
        const recentTR = trueRanges.slice(-period);
        return recentTR.reduce((a, b) => a + b, 0) / period;
    }

    /**
     * Calculate RSI (Relative Strength Index)
     */
    calculateRSI(data, period = 14) {
        if (data.length < period + 1) return null;

        let gains = 0;
        let losses = 0;

        // Calculate initial average gain/loss
        for (let i = 1; i <= period; i++) {
            const change = data[i].close - data[i - 1].close;
            if (change > 0) gains += change;
            else losses += Math.abs(change);
        }

        let avgGain = gains / period;
        let avgLoss = losses / period;

        // Calculate RSI for remaining periods
        const rsiValues = [];
        
        for (let i = period + 1; i < data.length; i++) {
            const change = data[i].close - data[i - 1].close;
            const gain = change > 0 ? change : 0;
            const loss = change < 0 ? Math.abs(change) : 0;

            avgGain = (avgGain * (period - 1) + gain) / period;
            avgLoss = (avgLoss * (period - 1) + loss) / period;

            const rs = avgGain / avgLoss;
            const rsi = 100 - (100 / (1 + rs));
            rsiValues.push(rsi);
        }

        return rsiValues.length > 0 ? rsiValues[rsiValues.length - 1] : null;
    }

    /**
     * Calculate MACD (Moving Average Convergence Divergence)
     */
    calculateMACD(data) {
        if (data.length < 26) return null;

        const ema12 = this.calculateEMA(data, 12);
        const ema26 = this.calculateEMA(data, 26);
        
        if (!ema12 || !ema26) return null;

        const macdLine = ema12 - ema26;
        
        return {
            value: macdLine,
            signal: macdLine > 0 ? 'bullish' : 'bearish'
        };
    }

    /**
     * Calculate EMA (Exponential Moving Average)
     */
    calculateEMA(data, period) {
        if (data.length < period) return null;

        const k = 2 / (period + 1);
        let ema = data[0].close;

        for (let i = 1; i < data.length; i++) {
            ema = data[i].close * k + ema * (1 - k);
        }

        return ema;
    }

    /**
     * Update indicator displays
     */
    updateIndicatorDisplays() {
        // RSI
        const rsiElement = document.getElementById('rsi-value');
        if (rsiElement && this.indicators.rsi !== null) {
            rsiElement.textContent = this.indicators.rsi.toFixed(2);
            
            // Color based on overbought/oversold
            if (this.indicators.rsi > 70) {
                rsiElement.style.color = '#ef4444'; // Overbought
            } else if (this.indicators.rsi < 30) {
                rsiElement.style.color = '#22c55e'; // Oversold
            } else {
                rsiElement.style.color = '#fbbf24'; // Neutral
            }
        }

        // MACD
        const macdElement = document.getElementById('macd-value');
        if (macdElement && this.indicators.macd) {
            macdElement.textContent = this.indicators.macd.value.toFixed(4);
            macdElement.style.color = this.indicators.macd.signal === 'bullish' ? '#22c55e' : '#ef4444';
        }

        // EMA
        const emaElement = document.getElementById('ema-value');
        if (emaElement && this.indicators.ema !== null) {
            emaElement.textContent = safeFormatCurrency(this.indicators.ema);
        }
        
        // Create or update extended indicators panel
        this.renderExtendedIndicators();
    }
    
    /**
     * Render extended indicators panel
     */
    renderExtendedIndicators() {
        // Find or create extended indicators container
        let container = document.getElementById('extended-indicators');
        if (!container) {
            const indicatorsSection = document.querySelector('.page-content');
            if (indicatorsSection) {
                const analysisResults = document.getElementById('analysis-results');
                if (analysisResults) {
                    container = document.createElement('div');
                    container.id = 'extended-indicators';
                    container.style.cssText = 'background: rgba(0,0,0,0.2); border-radius: 16px; padding: 1.5rem; margin-bottom: 1.5rem;';
                    analysisResults.parentNode.insertBefore(container, analysisResults);
                }
            }
        }
        
        if (!container) return;
        
        const bb = this.indicators.bollingerBands;
        const stochRsi = this.indicators.stochRsi;
        const atr = this.indicators.atr;
        const sma20 = this.indicators.sma20;
        const sma50 = this.indicators.sma50;
        const latestPrice = this.ohlcvData.length > 0 ? this.ohlcvData[this.ohlcvData.length - 1].close : 0;
        
        // Determine BB position
        let bbPosition = 'neutral';
        let bbColor = '#fbbf24';
        if (bb && latestPrice) {
            if (latestPrice >= bb.upper) {
                bbPosition = 'Upper Band';
                bbColor = '#ef4444';
            } else if (latestPrice <= bb.lower) {
                bbPosition = 'Lower Band';
                bbColor = '#22c55e';
            } else {
                const midDistance = (latestPrice - bb.lower) / (bb.upper - bb.lower);
                if (midDistance > 0.7) {
                    bbPosition = 'Near Upper';
                    bbColor = '#f59e0b';
                } else if (midDistance < 0.3) {
                    bbPosition = 'Near Lower';
                    bbColor = '#10b981';
                } else {
                    bbPosition = 'Middle Band';
                    bbColor = '#3b82f6';
                }
            }
        }
        
        // Determine trend from SMAs
        let smaTrend = 'neutral';
        let smaColor = '#fbbf24';
        if (sma20 && sma50) {
            if (sma20 > sma50) {
                smaTrend = 'Bullish (20 > 50)';
                smaColor = '#22c55e';
            } else {
                smaTrend = 'Bearish (20 < 50)';
                smaColor = '#ef4444';
            }
        }
        
        container.innerHTML = `
            <h3 style="margin: 0 0 1rem 0; font-size: 1.125rem; display: flex; align-items: center; gap: 0.5rem;">
                <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                    <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
                </svg>
                Advanced Indicators
            </h3>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 1rem;">
                <!-- Bollinger Bands -->
                <div style="background: rgba(0,0,0,0.2); border-radius: 8px; padding: 1rem; border-left: 4px solid ${bbColor};">
                    <div style="font-size: 0.75rem; text-transform: uppercase; color: var(--text-muted); margin-bottom: 0.5rem;">Bollinger Bands (20,2)</div>
                    <div style="font-size: 1.25rem; font-weight: 700; color: ${bbColor};">${bbPosition}</div>
                    ${bb ? `
                    <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.5rem;">
                        Upper: ${safeFormatCurrency(bb.upper)}<br>
                        Middle: ${safeFormatCurrency(bb.middle)}<br>
                        Lower: ${safeFormatCurrency(bb.lower)}<br>
                        Bandwidth: ${bb.bandwidth.toFixed(2)}%
                    </div>` : ''}
                </div>
                
                <!-- Stochastic RSI -->
                <div style="background: rgba(0,0,0,0.2); border-radius: 8px; padding: 1rem; border-left: 4px solid ${stochRsi > 80 ? '#ef4444' : stochRsi < 20 ? '#22c55e' : '#fbbf24'};">
                    <div style="font-size: 0.75rem; text-transform: uppercase; color: var(--text-muted); margin-bottom: 0.5rem;">Stochastic RSI</div>
                    <div style="font-size: 1.5rem; font-weight: 700; color: ${stochRsi > 80 ? '#ef4444' : stochRsi < 20 ? '#22c55e' : '#fbbf24'};">
                        ${stochRsi !== null ? stochRsi.toFixed(1) : '--'}
                    </div>
                    <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.25rem;">
                        ${stochRsi > 80 ? 'Overbought' : stochRsi < 20 ? 'Oversold' : 'Neutral'}
                    </div>
                </div>
                
                <!-- ATR -->
                <div style="background: rgba(0,0,0,0.2); border-radius: 8px; padding: 1rem; border-left: 4px solid #3b82f6;">
                    <div style="font-size: 0.75rem; text-transform: uppercase; color: var(--text-muted); margin-bottom: 0.5rem;">ATR (14)</div>
                    <div style="font-size: 1.5rem; font-weight: 700;">${atr !== null ? safeFormatCurrency(atr) : '--'}</div>
                    <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.25rem;">
                        Volatility: ${atr && latestPrice ? (atr / latestPrice * 100).toFixed(2) + '%' : '--'}
                    </div>
                </div>
                
                <!-- SMA Crossover -->
                <div style="background: rgba(0,0,0,0.2); border-radius: 8px; padding: 1rem; border-left: 4px solid ${smaColor};">
                    <div style="font-size: 0.75rem; text-transform: uppercase; color: var(--text-muted); margin-bottom: 0.5rem;">SMA Crossover</div>
                    <div style="font-size: 1.25rem; font-weight: 700; color: ${smaColor};">${smaTrend}</div>
                    <div style="font-size: 0.75rem; color: var(--text-muted); margin-top: 0.5rem;">
                        SMA20: ${sma20 ? safeFormatCurrency(sma20) : '--'}<br>
                        SMA50: ${sma50 ? safeFormatCurrency(sma50) : '--'}
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Perform technical analysis
     */
    performAnalysis() {
        if (!this.ohlcvData || this.ohlcvData.length === 0) {
            console.warn('No data available for analysis');
            return;
        }

        const resultsContainer = document.getElementById('analysis-results');
        if (!resultsContainer) return;

        const analysis = this.generateAnalysis();

        resultsContainer.innerHTML = `
            <div class="analysis-card">
                <div class="analysis-header">
                    <h3>Technical Analysis - ${this.currentSymbol} (${this.currentTimeframe})</h3>
                    <span class="badge badge-${analysis.signal}">${analysis.signal.toUpperCase()}</span>
                </div>
                <div class="analysis-body">
                    <div class="analysis-section">
                        <h4>Market Trend</h4>
                        <p class="trend-${analysis.trend.toLowerCase()}">${analysis.trendDescription}</p>
                    </div>
                    <div class="analysis-section">
                        <h4>Key Indicators</h4>
                        <ul class="indicator-list">
                            ${analysis.indicators.map(ind => `
                                <li>
                                    <span class="indicator-name">${ind.name}:</span>
                                    <span class="indicator-value ${ind.status}">${ind.value}</span>
                                    <span class="indicator-signal">(${ind.interpretation})</span>
                                </li>
                            `).join('')}
                        </ul>
                    </div>
                    <div class="analysis-section">
                        <h4>Trading Recommendation</h4>
                        <p class="recommendation">${analysis.recommendation}</p>
                    </div>
                    <div class="analysis-section">
                        <h4>Risk Assessment</h4>
                        <div class="risk-bar">
                            <div class="risk-fill risk-${analysis.risk}" style="width: ${analysis.riskScore}%"></div>
                        </div>
                        <p class="risk-text">Risk Level: ${analysis.risk.toUpperCase()} (${analysis.riskScore}%)</p>
                    </div>
                </div>
            </div>
        `;
    }

    /**
     * Generate analysis based on indicators and price action
     */
    generateAnalysis() {
        const latestCandle = this.ohlcvData[this.ohlcvData.length - 1];
        const rsi = this.indicators.rsi;
        const macd = this.indicators.macd;
        const ema = this.indicators.ema;
        const bb = this.indicators.bollingerBands;
        const stochRsi = this.indicators.stochRsi;
        const atr = this.indicators.atr;
        const sma20 = this.indicators.sma20;
        const sma50 = this.indicators.sma50;

        // Determine trend - use multiple indicators
        let trend = 'neutral';
        let trendDescription = 'Market is consolidating';
        let trendSignals = { bullish: 0, bearish: 0 };
        
        // EMA trend
        if (latestCandle.close > ema) {
            trendSignals.bullish++;
        } else if (latestCandle.close < ema) {
            trendSignals.bearish++;
        }
        
        // SMA crossover trend
        if (sma20 && sma50) {
            if (sma20 > sma50) {
                trendSignals.bullish++;
            } else {
                trendSignals.bearish++;
            }
        }
        
        // Bollinger Bands position
        if (bb) {
            if (latestCandle.close > bb.middle) {
                trendSignals.bullish++;
            } else {
                trendSignals.bearish++;
            }
        }
        
        if (trendSignals.bullish > trendSignals.bearish) {
            trend = 'bullish';
            trendDescription = `Uptrend detected: Price above EMA${sma20 > sma50 ? ', SMA20 > SMA50' : ''}${bb && latestCandle.close > bb.middle ? ', Above BB middle' : ''}`;
        } else if (trendSignals.bearish > trendSignals.bullish) {
            trend = 'bearish';
            trendDescription = `Downtrend detected: Price below EMA${sma20 < sma50 ? ', SMA20 < SMA50' : ''}${bb && latestCandle.close < bb.middle ? ', Below BB middle' : ''}`;
        }

        // Generate indicator analysis
        const indicators = [];

        if (rsi !== null) {
            let rsiStatus, rsiInterpretation;
            if (rsi > 70) {
                rsiStatus = 'overbought';
                rsiInterpretation = 'Overbought - potential reversal';
            } else if (rsi < 30) {
                rsiStatus = 'oversold';
                rsiInterpretation = 'Oversold - potential bounce';
            } else {
                rsiStatus = 'neutral';
                rsiInterpretation = 'Neutral momentum';
            }
            indicators.push({
                name: 'RSI (14)',
                value: rsi.toFixed(2),
                status: rsiStatus,
                interpretation: rsiInterpretation
            });
        }

        if (macd) {
            indicators.push({
                name: 'MACD',
                value: macd.value.toFixed(4),
                status: macd.signal,
                interpretation: macd.signal === 'bullish' ? 'Bullish crossover' : 'Bearish crossover'
            });
        }

        if (ema !== null) {
            const emaStatus = latestCandle.close > ema ? 'bullish' : 'bearish';
            indicators.push({
                name: 'EMA (20)',
                value: safeFormatCurrency(ema),
                status: emaStatus,
                interpretation: emaStatus === 'bullish' ? 'Price above EMA' : 'Price below EMA'
            });
        }
        
        // Add Bollinger Bands analysis
        if (bb) {
            let bbStatus, bbInterpretation;
            const bbPosition = (latestCandle.close - bb.lower) / (bb.upper - bb.lower);
            
            if (latestCandle.close >= bb.upper) {
                bbStatus = 'overbought';
                bbInterpretation = 'At upper band - possible reversal';
            } else if (latestCandle.close <= bb.lower) {
                bbStatus = 'oversold';
                bbInterpretation = 'At lower band - possible bounce';
            } else if (bbPosition > 0.7) {
                bbStatus = 'bearish';
                bbInterpretation = 'Near upper band - caution';
            } else if (bbPosition < 0.3) {
                bbStatus = 'bullish';
                bbInterpretation = 'Near lower band - potential buy';
            } else {
                bbStatus = 'neutral';
                bbInterpretation = 'Within bands - no signal';
            }
            
            indicators.push({
                name: 'Bollinger Bands',
                value: `${(bbPosition * 100).toFixed(0)}%`,
                status: bbStatus,
                interpretation: bbInterpretation
            });
        }
        
        // Add Stochastic RSI
        if (stochRsi !== null) {
            let stochStatus, stochInterpretation;
            if (stochRsi > 80) {
                stochStatus = 'overbought';
                stochInterpretation = 'Extreme overbought';
            } else if (stochRsi < 20) {
                stochStatus = 'oversold';
                stochInterpretation = 'Extreme oversold';
            } else {
                stochStatus = 'neutral';
                stochInterpretation = 'Normal range';
            }
            
            indicators.push({
                name: 'Stoch RSI',
                value: stochRsi.toFixed(1),
                status: stochStatus,
                interpretation: stochInterpretation
            });
        }
        
        // Add SMA crossover
        if (sma20 && sma50) {
            const smaStatus = sma20 > sma50 ? 'bullish' : 'bearish';
            indicators.push({
                name: 'SMA Cross',
                value: sma20 > sma50 ? 'Golden' : 'Death',
                status: smaStatus,
                interpretation: sma20 > sma50 ? 'Bullish crossover' : 'Bearish crossover'
            });
        }
        
        // Add ATR for volatility
        if (atr !== null) {
            const atrPercent = (atr / latestCandle.close) * 100;
            let atrStatus, atrInterpretation;
            
            if (atrPercent > 5) {
                atrStatus = 'high';
                atrInterpretation = 'High volatility - increase stop loss';
            } else if (atrPercent < 1) {
                atrStatus = 'low';
                atrInterpretation = 'Low volatility - breakout expected';
            } else {
                atrStatus = 'neutral';
                atrInterpretation = 'Normal volatility';
            }
            
            indicators.push({
                name: 'ATR (14)',
                value: `${atrPercent.toFixed(2)}%`,
                status: atrStatus,
                interpretation: atrInterpretation
            });
        }

        // Generate signal - count all indicator signals
        let signal = 'hold';
        let recommendation = 'Wait for clearer signals';
        
        const bullishSignals = indicators.filter(i => i.status === 'bullish' || i.status === 'oversold').length;
        const bearishSignals = indicators.filter(i => i.status === 'bearish' || i.status === 'overbought').length;
        const totalSignals = indicators.length;

        if (bullishSignals >= totalSignals * 0.5 && bullishSignals > bearishSignals) {
            signal = 'buy';
            recommendation = `Strong buy signals detected (${bullishSignals}/${totalSignals} indicators bullish). Consider entering a long position with proper risk management. Use ATR for stop loss placement.`;
        } else if (bearishSignals >= totalSignals * 0.5 && bearishSignals > bullishSignals) {
            signal = 'sell';
            recommendation = `Strong sell signals detected (${bearishSignals}/${totalSignals} indicators bearish). Consider taking profits or shorting with proper risk management.`;
        } else {
            recommendation = `Mixed signals (${bullishSignals} bullish, ${bearishSignals} bearish). Wait for clearer direction or trade cautiously.`;
        }

        // Calculate risk based on all indicators
        let riskScore = 50;
        let risk = 'medium';
        
        // RSI extreme adds risk
        if (rsi !== null) {
            if (rsi > 80 || rsi < 20) riskScore += 15;
            else if (rsi > 70 || rsi < 30) riskScore += 10;
        }
        
        // Stoch RSI extreme adds risk
        if (stochRsi !== null) {
            if (stochRsi > 90 || stochRsi < 10) riskScore += 15;
            else if (stochRsi > 80 || stochRsi < 20) riskScore += 10;
        }
        
        // High volatility adds risk
        if (atr !== null) {
            const atrPercent = (atr / latestCandle.close) * 100;
            if (atrPercent > 5) riskScore += 15;
            else if (atrPercent > 3) riskScore += 10;
        }
        
        // At Bollinger Band extremes adds risk
        if (bb) {
            if (latestCandle.close >= bb.upper || latestCandle.close <= bb.lower) {
                riskScore += 10;
            }
        }
        
        // Aligned signals reduce risk
        if (trend === 'bullish' && signal === 'buy') {
            riskScore -= 15;
        } else if (trend === 'bearish' && signal === 'sell') {
            riskScore -= 15;
        }

        riskScore = Math.max(10, Math.min(90, riskScore));

        if (riskScore < 35) risk = 'low';
        else if (riskScore > 65) risk = 'high';

        return {
            trend,
            trendDescription,
            indicators,
            signal,
            recommendation,
            risk,
            riskScore
        };
    }

    /**
     * Setup auto-refresh
     */
    setupAutoRefresh() {
        // Refresh every 30 seconds
        this.autoRefreshInterval = setInterval(() => {
            if (!this.isLoading && !document.hidden) {
                this.loadMarketData();
            }
        }, 30000);
    }

    /**
     * Export analysis
     */
    exportAnalysis() {
        const analysis = this.generateAnalysis();
        const exportData = {
            symbol: this.currentSymbol,
            timeframe: this.currentTimeframe,
            timestamp: new Date().toISOString(),
            dataSource: this.dataSource,
            price: this.ohlcvData[this.ohlcvData.length - 1],
            indicators: this.indicators,
            analysis: analysis
        };

        const blob = new Blob([JSON.stringify(exportData, null, 2)], { type: 'application/json' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${this.currentSymbol}_analysis_${Date.now()}.json`;
        a.click();
        URL.revokeObjectURL(url);

        this.showToast('✅ Analysis exported', 'success');
    }

    /**
     * Show loading state
     */
    showLoadingState(show) {
        const spinner = document.getElementById('loading-spinner');
        const analyzeBtn = document.getElementById('analyze-btn');
        
        if (spinner) {
            spinner.style.display = show ? 'block' : 'none';
        }
        if (analyzeBtn) {
            analyzeBtn.disabled = show;
            analyzeBtn.textContent = show ? 'Loading...' : 'Analyze';
        }
    }

    /**
     * Show error state
     */
    showErrorState(message) {
        const resultsContainer = document.getElementById('analysis-results');
        if (resultsContainer) {
            resultsContainer.innerHTML = `
                <div class="error-state">
                    <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <circle cx="12" cy="12" r="10"></circle>
                        <line x1="12" y1="8" x2="12" y2="12"></line>
                        <line x1="12" y1="16" x2="12.01" y2="16"></line>
                    </svg>
                    <h3>Unable to Load Data</h3>
                    <p>${escapeHtml(message)}</p>
                    <button onclick="location.reload()" class="btn btn-primary">Retry</button>
                </div>
            `;
        }
    }

    /**
     * Show toast notification
     */
    showToast(message, type = 'info') {
        if (typeof Toast !== 'undefined' && Toast.show) {
            Toast.show(message, type);
        } else {
            console.log(`[Toast ${type}]`, message);
        }
    }

    /**
     * REMOVED: generateDemoOHLCV - No mock data allowed
     * All data must come from real API sources
     */

    /**
     * Cleanup on page unload
     */
    destroy() {
        if (this.autoRefreshInterval) {
            clearInterval(this.autoRefreshInterval);
        }
        if (this.chart) {
            this.chart.remove();
        }
    }
}

// Initialize on page load
let technicalAnalysisInstance = null;

document.addEventListener('DOMContentLoaded', async () => {
    try {
        technicalAnalysisInstance = new TechnicalAnalysisProfessional();
        await technicalAnalysisInstance.init();
    } catch (error) {
        console.error('[TechnicalAnalysis] Fatal error:', error);
    }
});

// Cleanup on unload
window.addEventListener('beforeunload', () => {
    if (technicalAnalysisInstance) {
        technicalAnalysisInstance.destroy();
    }
});

export { TechnicalAnalysisProfessional };
export default TechnicalAnalysisProfessional;

