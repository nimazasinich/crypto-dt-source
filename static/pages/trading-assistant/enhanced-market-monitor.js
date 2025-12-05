/**
 * Enhanced Market Monitor Agent V2
 * Real-time market monitoring with WebSocket support
 * Features: Multi-exchange, error recovery, notification system
 */

/**
 * Enhanced Market Monitor Agent
 */
export class EnhancedMarketMonitor {
    constructor(config = {}) {
        this.symbol = config.symbol || 'BTC';
        this.strategy = config.strategy || 'ict-market-structure';
        this.interval = config.interval || 60000;
        this.useWebSocket = config.useWebSocket !== false;
        this.isRunning = false;
        this.intervalId = null;
        this.wsConnection = null;
        this.reconnectAttempts = 0;
        this.maxReconnectAttempts = 10;
        this.lastSignal = null;
        this.lastPrice = null;
        this.priceHistory = [];
        this.maxHistoryLength = 200;
        this.callbacks = {
            onSignal: null,
            onError: null,
            onPriceUpdate: null,
            onConnectionChange: null
        };
        this.errorCount = 0;
        this.maxErrors = 5;
        this.circuitBreakerOpen = false;
        this.lastAnalysisTime = 0;
        this.minAnalysisInterval = 10000;
        this.exchanges = ['binance', 'coinbase', 'kraken'];
        this.currentExchange = 'binance';
        this.failedExchanges = new Set();
    }

    /**
     * Start monitoring with automatic fallback
     */
    async start() {
        if (this.isRunning) {
            console.warn('[EnhancedMonitor] Already running');
            return { success: false, message: 'Already running' };
        }

        console.log(`[EnhancedMonitor] Starting for ${this.symbol} with ${this.strategy}`);
        this.isRunning = true;
        this.circuitBreakerOpen = false;
        this.errorCount = 0;

        try {
            // Try WebSocket first
            if (this.useWebSocket) {
                await this.connectWebSocket();
            }

            // Start polling as fallback/supplement
            await this.startPolling();

            // Emit connection status
            this.emitConnectionChange('connected');

            return { success: true, message: 'Monitor started successfully' };
        } catch (error) {
            console.error('[EnhancedMonitor] Start error:', error);
            this.emitError(error);
            return { success: false, message: error.message };
        }
    }

    /**
     * Stop monitoring
     */
    stop() {
        if (!this.isRunning) return;

        console.log('[EnhancedMonitor] Stopping...');
        this.isRunning = false;

        // Stop polling
        if (this.intervalId) {
            clearInterval(this.intervalId);
            this.intervalId = null;
        }

        // Close WebSocket
        if (this.wsConnection) {
            this.wsConnection.close();
            this.wsConnection = null;
        }

        this.emitConnectionChange('disconnected');
    }

    /**
     * Connect to WebSocket for real-time updates
     */
    async connectWebSocket() {
        const wsUrl = this.getWebSocketUrl(this.currentExchange);
        
        if (!wsUrl) {
            console.warn('[EnhancedMonitor] WebSocket not available for current exchange');
            return;
        }

        try {
            this.wsConnection = new WebSocket(wsUrl);

            this.wsConnection.onopen = () => {
                console.log('[EnhancedMonitor] WebSocket connected');
                this.reconnectAttempts = 0;
                this.emitConnectionChange('websocket-connected');
                
                // Subscribe to symbol
                this.subscribeToSymbol();
            };

            this.wsConnection.onmessage = (event) => {
                try {
                    const data = JSON.parse(event.data);
                    this.handleWebSocketMessage(data);
                } catch (error) {
                    console.error('[EnhancedMonitor] WebSocket message error:', error);
                }
            };

            this.wsConnection.onerror = (error) => {
                console.error('[EnhancedMonitor] WebSocket error:', error);
                this.handleConnectionError(error);
            };

            this.wsConnection.onclose = () => {
                console.log('[EnhancedMonitor] WebSocket closed');
                if (this.isRunning && this.reconnectAttempts < this.maxReconnectAttempts) {
                    this.reconnectAttempts++;
                    setTimeout(() => {
                        console.log(`[EnhancedMonitor] Reconnecting... (${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
                        this.connectWebSocket();
                    }, Math.min(1000 * Math.pow(2, this.reconnectAttempts), 30000));
                }
            };
        } catch (error) {
            console.error('[EnhancedMonitor] WebSocket connection failed:', error);
            this.handleConnectionError(error);
        }
    }

    /**
     * Get WebSocket URL for exchange
     */
    getWebSocketUrl(exchange) {
        const symbol = this.symbol.toLowerCase();
        
        const urls = {
            binance: `wss://stream.binance.com:9443/ws/${symbol}usdt@kline_1m`,
            coinbase: `wss://ws-feed.exchange.coinbase.com`,
            kraken: `wss://ws.kraken.com`
        };

        return urls[exchange];
    }

    /**
     * Subscribe to symbol on WebSocket
     */
    subscribeToSymbol() {
        if (!this.wsConnection || this.wsConnection.readyState !== WebSocket.OPEN) {
            return;
        }

        const symbol = this.symbol.toUpperCase();
        
        // Exchange-specific subscription
        if (this.currentExchange === 'coinbase') {
            this.wsConnection.send(JSON.stringify({
                type: 'subscribe',
                channels: [{ name: 'ticker', product_ids: [`${symbol}-USD`] }]
            }));
        } else if (this.currentExchange === 'kraken') {
            this.wsConnection.send(JSON.stringify({
                event: 'subscribe',
                pair: [`${symbol}/USD`],
                subscription: { name: 'ticker' }
            }));
        }
        // Binance doesn't need explicit subscription in URL
    }

    /**
     * Handle WebSocket messages
     */
    handleWebSocketMessage(data) {
        try {
            const priceData = this.parseWebSocketData(data);
            
            if (priceData) {
                this.lastPrice = priceData.price;
                this.addToPriceHistory(priceData);
                this.emitPriceUpdate(priceData);

                // Throttled analysis
                const now = Date.now();
                if (now - this.lastAnalysisTime >= this.minAnalysisInterval) {
                    this.lastAnalysisTime = now;
                    this.performAnalysis();
                }
            }
        } catch (error) {
            console.error('[EnhancedMonitor] Message parsing error:', error);
        }
    }

    /**
     * Parse WebSocket data from different exchanges
     */
    parseWebSocketData(data) {
        try {
            // Binance format
            if (data.e === 'kline') {
                const kline = data.k;
                return {
                    timestamp: kline.t,
                    open: parseFloat(kline.o),
                    high: parseFloat(kline.h),
                    low: parseFloat(kline.l),
                    close: parseFloat(kline.c),
                    volume: parseFloat(kline.v),
                    price: parseFloat(kline.c),
                    exchange: 'binance'
                };
            }

            // Coinbase format
            if (data.type === 'ticker') {
                return {
                    timestamp: Date.now(),
                    price: parseFloat(data.price),
                    volume: parseFloat(data.volume_24h || 0),
                    exchange: 'coinbase'
                };
            }

            // Kraken format
            if (Array.isArray(data) && data[2] === 'ticker') {
                const ticker = data[1];
                return {
                    timestamp: Date.now(),
                    price: parseFloat(ticker.c[0]),
                    volume: parseFloat(ticker.v[1]),
                    exchange: 'kraken'
                };
            }

            return null;
        } catch (error) {
            console.error('[EnhancedMonitor] Data parsing error:', error);
            return null;
        }
    }

    /**
     * Add price to history
     */
    addToPriceHistory(priceData) {
        this.priceHistory.push(priceData);
        
        // Keep history at max length
        if (this.priceHistory.length > this.maxHistoryLength) {
            this.priceHistory.shift();
        }
    }

    /**
     * Start polling as fallback
     */
    async startPolling() {
        // Initial check
        await this.checkMarket();
        
        // Set up interval
        this.intervalId = setInterval(async () => {
            if (!this.circuitBreakerOpen) {
                await this.checkMarket();
            } else {
                this.attemptCircuitBreakerReset();
            }
        }, this.interval);
    }

    /**
     * Check market conditions
     */
    async checkMarket() {
        try {
            const marketData = await this.fetchMarketDataWithFallback();
            
            if (!marketData) {
                throw new Error('Failed to fetch market data from all sources');
            }

            this.resetErrorCount();
            
            // Perform analysis
            await this.performAnalysis(marketData);
        } catch (error) {
            console.error('[EnhancedMonitor] Market check error:', error);
            this.handleError(error);
        }
    }

    /**
     * Fetch market data with multi-exchange fallback
     */
    async fetchMarketDataWithFallback() {
        const availableExchanges = this.exchanges.filter(ex => !this.failedExchanges.has(ex));

        if (availableExchanges.length === 0) {
            console.warn('[EnhancedMonitor] All exchanges failed, resetting...');
            this.failedExchanges.clear();
            return this.getFallbackData();
        }

        for (const exchange of availableExchanges) {
            try {
                const data = await this.fetchFromExchange(exchange);
                this.currentExchange = exchange;
                return data;
            } catch (error) {
                console.warn(`[EnhancedMonitor] ${exchange} failed:`, error.message);
                this.failedExchanges.add(exchange);
            }
        }

        return this.getFallbackData();
    }

    /**
     * Fetch from specific exchange
     */
    async fetchFromExchange(exchange) {
        const controller = new AbortController();
        const timeout = setTimeout(() => controller.abort(), 10000);

        try {
            let url;
            const symbol = this.symbol.toUpperCase();

            switch (exchange) {
                case 'binance':
                    url = `https://api.binance.com/api/v3/klines?symbol=${symbol}USDT&interval=1h&limit=100`;
                    break;
                case 'coinbase':
                    url = `https://api.exchange.coinbase.com/products/${symbol}-USD/candles?granularity=3600`;
                    break;
                case 'kraken':
                    url = `https://api.kraken.com/0/public/OHLC?pair=${symbol}USD&interval=60`;
                    break;
                default:
                    throw new Error(`Unknown exchange: ${exchange}`);
            }

            const response = await fetch(url, { 
                signal: controller.signal,
                headers: { 'Accept': 'application/json' }
            });

            clearTimeout(timeout);

            if (!response.ok) {
                throw new Error(`HTTP ${response.status}`);
            }

            const data = await response.json();
            return this.normalizeExchangeData(data, exchange);
        } catch (error) {
            clearTimeout(timeout);
            throw error;
        }
    }

    /**
     * Normalize data from different exchanges
     */
    normalizeExchangeData(data, exchange) {
        try {
            if (!data || typeof data !== 'object') {
                throw new Error('Invalid data format');
            }
            
            let normalized = [];
            let rawData = [];

            // Extract data array based on exchange format
            switch (exchange) {
                case 'binance':
                    rawData = Array.isArray(data) ? data : [];
                    break;
                case 'coinbase':
                    rawData = Array.isArray(data) ? data : [];
                    break;
                case 'kraken':
                    rawData = (data.result && typeof data.result === 'object') 
                        ? Object.values(data.result)[0] || []
                        : [];
                    break;
                default:
                    throw new Error(`Unknown exchange: ${exchange}`);
            }

            if (!Array.isArray(rawData) || rawData.length === 0) {
                throw new Error('Empty or invalid data array');
            }

            switch (exchange) {
                case 'binance':
                    normalized = rawData
                        .filter(item => Array.isArray(item) && item.length >= 6)
                        .map(item => {
                            const open = parseFloat(item[1]);
                            const high = parseFloat(item[2]);
                            const low = parseFloat(item[3]);
                            const close = parseFloat(item[4]);
                            const volume = parseFloat(item[5]);
                            
                            // Validate OHLC
                            if (isNaN(open) || isNaN(high) || isNaN(low) || isNaN(close) ||
                                open <= 0 || high <= 0 || low <= 0 || close <= 0 ||
                                high < low || high < Math.max(open, close) || low > Math.min(open, close)) {
                                return null;
                            }
                            
                            return {
                                timestamp: parseInt(item[0]) || Date.now(),
                                open: open,
                                high: high,
                                low: low,
                                close: close,
                                volume: isNaN(volume) ? 0 : volume
                            };
                        })
                        .filter(item => item !== null);
                    break;

                case 'coinbase':
                    normalized = rawData
                        .filter(item => Array.isArray(item) && item.length >= 5)
                        .map(item => {
                            const timestamp = parseInt(item[0]) * 1000;
                            const low = parseFloat(item[1]);
                            const high = parseFloat(item[2]);
                            const open = parseFloat(item[3]);
                            const close = parseFloat(item[4]);
                            
                            // Validate OHLC
                            if (isNaN(open) || isNaN(high) || isNaN(low) || isNaN(close) ||
                                open <= 0 || high <= 0 || low <= 0 || close <= 0 ||
                                high < low || high < Math.max(open, close) || low > Math.min(open, close)) {
                                return null;
                            }
                            
                            return {
                                timestamp: timestamp || Date.now(),
                                low: low,
                                high: high,
                                open: open,
                                close: close,
                                volume: parseFloat(item[5]) || 0
                            };
                        })
                        .filter(item => item !== null);
                    break;

                case 'kraken':
                    normalized = rawData
                        .filter(item => Array.isArray(item) && item.length >= 7)
                        .map(item => {
                            const timestamp = parseInt(item[0]) * 1000;
                            const open = parseFloat(item[2]);
                            const high = parseFloat(item[3]);
                            const low = parseFloat(item[4]);
                            const close = parseFloat(item[5]);
                            const volume = parseFloat(item[6]);
                            
                            // Validate OHLC
                            if (isNaN(open) || isNaN(high) || isNaN(low) || isNaN(close) ||
                                open <= 0 || high <= 0 || low <= 0 || close <= 0 ||
                                high < low || high < Math.max(open, close) || low > Math.min(open, close)) {
                                return null;
                            }
                            
                            return {
                                timestamp: timestamp || Date.now(),
                                open: open,
                                high: high,
                                low: low,
                                close: close,
                                volume: isNaN(volume) ? 0 : volume
                            };
                        })
                        .filter(item => item !== null);
                    break;
            }

            if (normalized.length === 0) {
                throw new Error('No valid data after normalization');
            }

            return normalized.sort((a, b) => a.timestamp - b.timestamp);
        } catch (error) {
            console.error(`[EnhancedMonitor] Normalization error for ${exchange}:`, error);
            throw error;
        }
    }

    /**
     * Get fallback demo data
     */
    getFallbackData() {
        console.warn('[EnhancedMonitor] Using fallback demo data');
        
        const data = [];
        const now = Date.now();
        let basePrice = 50000;

        for (let i = 99; i >= 0; i--) {
            const timestamp = now - (i * 3600000);
            const volatility = basePrice * 0.02;
            
            const open = basePrice + (Math.random() - 0.5) * volatility;
            const close = open + (Math.random() - 0.5) * volatility;
            const high = Math.max(open, close) + Math.random() * volatility * 0.5;
            const low = Math.min(open, close) - Math.random() * volatility * 0.5;
            const volume = Math.random() * 1000000;

            data.push({ timestamp, open, high, low, close, volume });
            basePrice = close;
        }

        return data;
    }

    /**
     * Perform trading analysis
     */
    async performAnalysis(marketData = null) {
        try {
            // Use provided data or price history
            const ohlcvData = marketData || this.convertPriceHistoryToOHLCV();

            if (!ohlcvData || ohlcvData.length < 50) {
                console.warn('[EnhancedMonitor] Insufficient data for analysis');
                return;
            }

            // Import strategy module dynamically
            const { analyzeWithAdvancedStrategy } = await import('./advanced-strategies-v2.js');
            
            const analysis = await analyzeWithAdvancedStrategy(
                this.symbol,
                this.strategy,
                ohlcvData
            );

            if (this.shouldNotify(analysis)) {
                this.emitSignal(analysis);
            }
        } catch (error) {
            console.error('[EnhancedMonitor] Analysis error:', error);
            this.handleError(error);
        }
    }

    /**
     * Convert price history to OHLCV format
     */
    convertPriceHistoryToOHLCV() {
        if (this.priceHistory.length < 10) return null;

        // Group by minute intervals
        const grouped = new Map();
        
        this.priceHistory.forEach(item => {
            const minute = Math.floor(item.timestamp / 60000) * 60000;
            
            if (!grouped.has(minute)) {
                grouped.set(minute, {
                    timestamp: minute,
                    open: item.price,
                    high: item.price,
                    low: item.price,
                    close: item.price,
                    volume: item.volume || 0
                });
            } else {
                const candle = grouped.get(minute);
                candle.high = Math.max(candle.high, item.price);
                candle.low = Math.min(candle.low, item.price);
                candle.close = item.price;
                candle.volume += item.volume || 0;
            }
        });

        return Array.from(grouped.values()).sort((a, b) => a.timestamp - b.timestamp);
    }

    /**
     * Determine if notification should be sent
     */
    shouldNotify(analysis) {
        if (!analysis) return false;

        // Always notify on new signal type
        if (!this.lastSignal || this.lastSignal.signal !== analysis.signal) {
            this.lastSignal = analysis;
            return true;
        }

        // Notify on high confidence signals
        if (analysis.confidence >= 85 && analysis.signal !== 'hold') {
            return true;
        }

        // Notify on significant price moves
        if (this.lastPrice && analysis.entry) {
            const priceChange = Math.abs((analysis.entry - this.lastPrice) / this.lastPrice);
            if (priceChange > 0.03) { // 3% move
                return true;
            }
        }

        return false;
    }

    /**
     * Handle connection errors with fallback
     */
    handleConnectionError(error) {
        this.errorCount++;
        
        if (this.errorCount >= this.maxErrors) {
            console.error('[EnhancedMonitor] Circuit breaker opened due to repeated errors');
            this.circuitBreakerOpen = true;
            this.emitConnectionChange('circuit-breaker-open');
        }

        // Try switching exchange
        const currentIndex = this.exchanges.indexOf(this.currentExchange);
        const nextIndex = (currentIndex + 1) % this.exchanges.length;
        this.currentExchange = this.exchanges[nextIndex];
        
        console.log(`[EnhancedMonitor] Switching to ${this.currentExchange}`);
    }

    /**
     * Handle general errors
     */
    handleError(error) {
        this.errorCount++;
        
        if (this.errorCount >= this.maxErrors && !this.circuitBreakerOpen) {
            console.error('[EnhancedMonitor] Circuit breaker triggered');
            this.circuitBreakerOpen = true;
            this.emitConnectionChange('circuit-breaker-open');
        }

        this.emitError(error);
    }

    /**
     * Reset error count on successful operations
     */
    resetErrorCount() {
        if (this.errorCount > 0) {
            this.errorCount = Math.max(0, this.errorCount - 1);
        }
    }

    /**
     * Attempt to reset circuit breaker
     */
    attemptCircuitBreakerReset() {
        const resetTime = 60000; // 1 minute
        
        if (this.errorCount > 0) {
            this.errorCount--;
        }

        if (this.errorCount === 0) {
            console.log('[EnhancedMonitor] Circuit breaker reset, resuming...');
            this.circuitBreakerOpen = false;
            this.failedExchanges.clear();
            this.emitConnectionChange('circuit-breaker-reset');
        }
    }

    /**
     * Emit signal event
     */
    emitSignal(analysis) {
        console.log('[EnhancedMonitor] Signal:', analysis);
        
        if (this.callbacks.onSignal) {
            this.callbacks.onSignal(analysis);
        }
    }

    /**
     * Emit price update event
     */
    emitPriceUpdate(priceData) {
        if (this.callbacks.onPriceUpdate) {
            this.callbacks.onPriceUpdate(priceData);
        }
    }

    /**
     * Emit error event
     */
    emitError(error) {
        if (this.callbacks.onError) {
            this.callbacks.onError(error);
        }
    }

    /**
     * Emit connection change event
     */
    emitConnectionChange(status) {
        console.log('[EnhancedMonitor] Connection status:', status);
        
        if (this.callbacks.onConnectionChange) {
            this.callbacks.onConnectionChange({
                status,
                exchange: this.currentExchange,
                websocket: !!this.wsConnection,
                circuitBreaker: this.circuitBreakerOpen
            });
        }
    }

    /**
     * Set callback functions
     */
    on(event, callback) {
        if (this.callbacks.hasOwnProperty(`on${event.charAt(0).toUpperCase()}${event.slice(1)}`)) {
            this.callbacks[`on${event.charAt(0).toUpperCase()}${event.slice(1)}`] = callback;
        }
    }

    /**
     * Update configuration
     */
    updateConfig(config) {
        let needsRestart = false;

        if (config.symbol && config.symbol !== this.symbol) {
            this.symbol = config.symbol;
            needsRestart = true;
        }

        if (config.strategy) {
            this.strategy = config.strategy;
        }

        if (config.interval) {
            this.interval = config.interval;
            needsRestart = true;
        }

        if (needsRestart && this.isRunning) {
            this.stop();
            this.start();
        }
    }

    /**
     * Get current status
     */
    getStatus() {
        return {
            isRunning: this.isRunning,
            symbol: this.symbol,
            strategy: this.strategy,
            interval: this.interval,
            exchange: this.currentExchange,
            websocketConnected: !!(this.wsConnection && this.wsConnection.readyState === WebSocket.OPEN),
            circuitBreakerOpen: this.circuitBreakerOpen,
            errorCount: this.errorCount,
            lastSignal: this.lastSignal,
            lastPrice: this.lastPrice,
            historyLength: this.priceHistory.length,
            failedExchanges: Array.from(this.failedExchanges)
        };
    }
}

export default EnhancedMarketMonitor;

