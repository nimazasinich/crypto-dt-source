/**
 * Hybrid Trading System (HTS) Page
 * Complete implementation with real-time data, WebSocket, and full functionality
 */

import HTSEngine from './hts-engine.js';
import { TradingIcons } from './icons.js';
import { escapeHtml, safeFormatNumber, safeFormatCurrency } from '../../shared/js/utils/sanitizer.js';

class HTSPage {
    constructor() {
        this.engine = new HTSEngine();
        this.symbol = 'BTCUSDT';
        this.timeframe = '1h';
        this.chart = null;
        this.candlestickSeries = null;
        this.rsiSeries = null;
        this.macdSeries = null;
        this.volumeSeries = null;
        this.ohlcvData = [];
        this.analysisResult = null;
        this.autoAnalysisInterval = null;
        this.dataUpdateInterval = null;
    }

    async init() {
        try {
            console.log('[HTS] Initializing Hybrid Trading System...');
            this.bindEvents();
            await this.initChart();
            await this.loadInitialData();
            await this.runAnalysis();
            this.startDataUpdates();
            this.startAutoAnalysis();
            console.log('[HTS] Ready');
        } catch (error) {
            console.error('[HTS] Init error:', error);
            this.showError('Failed to initialize HTS. Please refresh the page.');
        }
    }

    /**
     * Bind event listeners
     */
    bindEvents() {
        // Tab switching
        document.querySelectorAll('.trading-tab').forEach(tab => {
            tab.addEventListener('click', (e) => {
                const view = e.currentTarget.dataset.view;
                this.switchView(view);
            });
        });
        // Symbol change
        document.getElementById('hts-symbol')?.addEventListener('change', (e) => {
            this.symbol = e.target.value;
            this.loadInitialData();
        });

        // Timeframe change
        document.getElementById('hts-timeframe')?.addEventListener('change', (e) => {
            this.timeframe = e.target.value;
            this.loadInitialData();
        });

        // Auto-analysis toggle
        document.getElementById('hts-auto-trade')?.addEventListener('change', (e) => {
            if (e.target.checked) {
                this.startAutoAnalysis();
            } else {
                this.stopAutoAnalysis();
            }
        });

        // Manual analyze button
        document.getElementById('hts-analyze-btn')?.addEventListener('click', () => {
            this.runAnalysis();
        });

        // Indicator toggles
        document.getElementById('show-rsi')?.addEventListener('change', () => this.updateChart());
        document.getElementById('show-macd')?.addEventListener('change', () => this.updateChart());
        document.getElementById('show-volume')?.addEventListener('change', () => this.updateChart());
    }

    /**
     * Switch between standard and HTS views
     */
    switchView(view) {
        document.querySelectorAll('.trading-tab').forEach(tab => {
            tab.classList.remove('active');
        });
        document.querySelector(`[data-view="${view}"]`)?.classList.add('active');

        const standardView = document.getElementById('standard-trading-view');
        const htsView = document.getElementById('hts-trading-view');

        if (view === 'hts') {
            standardView.style.display = 'none';
            htsView.style.display = 'block';
            if (!this.chart) {
                this.init();
            }
        } else {
            standardView.style.display = 'block';
            htsView.style.display = 'none';
        }
    }

    /**
     * Initialize TradingView Lightweight Chart
     */
    async initChart() {
        const container = document.getElementById('hts-chart-container');
        if (!container) {
            console.warn('[HTS] Chart container not found');
            return;
        }

        // Wait for LightweightCharts library to load (max 5 seconds)
        let retries = 0;
        const maxRetries = 10;
        while (typeof LightweightCharts === 'undefined' && retries < maxRetries) {
            await new Promise(resolve => setTimeout(resolve, 500));
            retries++;
        }

        if (typeof LightweightCharts === 'undefined') {
            console.error('[HTS] TradingView Lightweight Charts library not loaded after timeout');
            this.showError('Charting library not available. Please refresh the page.');
            return;
        }

        try {
            this.chart = LightweightCharts.createChart(container, {
                width: container.clientWidth,
                height: 500,
                layout: {
                    background: { color: '#1a1a1a' },
                    textColor: '#d1d5db',
                },
                grid: {
                    vertLines: { color: '#2a2a2a' },
                    horzLines: { color: '#2a2a2a' },
                },
                timeScale: {
                    timeVisible: true,
                    secondsVisible: false,
                },
            });

            if (!this.chart) {
                throw new Error('Failed to create chart instance');
            }

            // Try multiple methods to create candlestick series (compatibility with different library versions)
            const seriesOptions = {
                upColor: '#26a69a',
                downColor: '#ef5350',
                borderVisible: false,
                wickUpColor: '#26a69a',
                wickDownColor: '#ef5350',
            };

            // Method 1: Try addCandlestickSeries (older API)
            if (typeof this.chart.addCandlestickSeries === 'function') {
                this.candlestickSeries = this.chart.addCandlestickSeries(seriesOptions);
            }
            // Method 2: Try addSeries with CandlestickSeries type (newer API)
            else if (typeof this.chart.addSeries === 'function' && LightweightCharts.SeriesType && LightweightCharts.SeriesType.Candlestick) {
                this.candlestickSeries = this.chart.addSeries(LightweightCharts.SeriesType.Candlestick, seriesOptions);
            }
            // Method 3: Try addSeries with string type
            else if (typeof this.chart.addSeries === 'function') {
                try {
                    this.candlestickSeries = this.chart.addSeries('Candlestick', seriesOptions);
                } catch (e) {
                    console.warn('[HTS] Failed to create series with string type:', e);
                }
            }

            if (!this.candlestickSeries) {
                console.error('[HTS] Available chart methods:', Object.getOwnPropertyNames(Object.getPrototypeOf(this.chart)));
                throw new Error('Failed to create candlestick series - no compatible method found');
            }

            if (typeof this.chart.addHistogramSeries === 'function') {
                this.volumeSeries = this.chart.addHistogramSeries({
                    color: '#26a69a',
                    priceFormat: {
                        type: 'volume',
                    },
                    priceScaleId: 'volume',
                    scaleMargins: {
                        top: 0.8,
                        bottom: 0,
                    },
                });
            }

            if (typeof this.chart.addLineSeries === 'function') {
                this.rsiSeries = this.chart.addLineSeries({
                    color: '#ff9800',
                    lineWidth: 2,
                    priceScaleId: 'rsi',
                    scaleMargins: {
                        top: 0.7,
                        bottom: 0,
                    },
                });

                this.macdSeries = this.chart.addLineSeries({
                    color: '#2196f3',
                    lineWidth: 2,
                    priceScaleId: 'macd',
                    scaleMargins: {
                        top: 0.5,
                        bottom: 0.3,
                    },
                });
            }

            // Handle resize
            window.addEventListener('resize', () => {
                if (this.chart && container) {
                    this.chart.applyOptions({ width: container.clientWidth });
                }
            });

            console.log('[HTS] Chart initialized successfully');
        } catch (error) {
            console.error('[HTS] Chart initialization error:', error);
            this.showError(`Failed to initialize chart: ${error.message}`);
            this.chart = null;
            this.candlestickSeries = null;
            this.volumeSeries = null;
            this.rsiSeries = null;
            this.macdSeries = null;
        }
    }

    /**
     * Start periodic data updates from API
     */
    startDataUpdates() {
        this.stopDataUpdates();
        // Update data every 30 seconds
        this.dataUpdateInterval = setInterval(async () => {
            try {
                await this.loadInitialData();
                if (document.getElementById('hts-auto-trade')?.checked) {
                    await this.runAnalysis();
                }
            } catch (error) {
                console.warn('[HTS] Data update error:', error);
            }
        }, 30000);
    }

    /**
     * Stop data updates
     */
    stopDataUpdates() {
        if (this.dataUpdateInterval) {
            clearInterval(this.dataUpdateInterval);
            this.dataUpdateInterval = null;
        }
    }

    /**
     * Load initial OHLCV data from API
     */
    async loadInitialData() {
        try {
            this.updateConnectionStatus('Loading data...', 'info');
            
            const symbol = this.symbol.replace('USDT', '');
            
            // Get base API URL - use relative URLs for HuggingFace compatibility
            const baseUrl = window.location.origin;
            const apiUrl = `${baseUrl}/api/market?symbol=${symbol}&limit=100`;
            
            // Try multiple API endpoints with retry logic
            let data = null;
            let response = null;
            let retries = 0;
            const maxRetries = 2;
            
            // Try /api/market endpoint first
            while (retries <= maxRetries) {
                try {
                    if (retries > 0) {
                        const delay = Math.min(1000 * Math.pow(2, retries - 1), 5000);
                        await new Promise(resolve => setTimeout(resolve, delay));
                    }
                    
                    response = await fetch(apiUrl, {
                        method: 'GET',
                        headers: {
                            'Content-Type': 'application/json',
                        },
                        signal: AbortSignal.timeout(10000)
                    });
                    
                    if (response.ok) {
                        break;
                    }
                    
                    if (retries < maxRetries && response.status >= 500) {
                        retries++;
                        continue;
                    }
                    
                    throw new Error(`HTTP ${response.status}: ${response.statusText}`);
                } catch (error) {
                    if (retries < maxRetries && (error.name === 'AbortError' || error.message.includes('timeout') || error.message.includes('network'))) {
                        retries++;
                        continue;
                    }
                    throw error;
                }
            }
            
            if (!response || !response.ok) {
                throw new Error('Failed to fetch data after retries');
            }
                
            data = await response.json();
            
            if (!data || typeof data !== 'object') {
                throw new Error('Invalid response format');
            }
            
            // Try to get real OHLCV data from API
            const ohlcvUrl = `${baseUrl}/api/market/ohlc?symbol=${symbol}&interval=1h&limit=100`;
            try {
                const ohlcvResponse = await fetch(ohlcvUrl, {
                    method: 'GET',
                    headers: { 'Content-Type': 'application/json' },
                    signal: AbortSignal.timeout(10000)
                });
                
                if (ohlcvResponse.ok) {
                    const ohlcvData = await ohlcvResponse.json();
                    const ohlc = ohlcvData.data || ohlcvData.ohlc || ohlcvData;
                    
                    if (Array.isArray(ohlc) && ohlc.length > 0) {
                        // Transform to chart format
                        this.ohlcvData = ohlc.map(candle => ({
                            time: candle.timestamp || candle.time || candle[0],
                            open: candle.open || candle.o || candle[1],
                            high: candle.high || candle.h || candle[2],
                            low: candle.low || candle.l || candle[3],
                            close: candle.close || candle.c || candle[4],
                            volume: candle.volume || candle.v || candle[5]
                        })).filter(c => c.time && c.open && c.high && c.low && c.close);
                        
                        if (this.ohlcvData.length > 0) {
                            this.updateChart();
                            this.updateConnectionStatus('Real OHLCV data loaded', 'success');
                            return;
                        }
                    }
                }
            } catch (ohlcvError) {
                console.warn('[HTS] OHLCV API failed:', ohlcvError);
            }
            
            // If OHLCV API fails, try to use price data from market endpoint
            if (data && data.success && Array.isArray(data.items) && data.items.length > 0) {
                const item = data.items.find(i => i && i.symbol === symbol) || data.items[0];
                if (item && typeof item === 'object') {
                    const price = parseFloat(item.price || item.current_price);
                    if (!isNaN(price) && price > 0) {
                        // Try to fetch historical OHLCV from another endpoint
                        const historyUrl = `${baseUrl}/api/service/history?symbol=${symbol}&interval=1h&limit=100`;
                        try {
                            const historyResponse = await fetch(historyUrl, {
                                method: 'GET',
                                headers: { 'Content-Type': 'application/json' },
                                signal: AbortSignal.timeout(10000)
                            });
                            
                            if (historyResponse.ok) {
                                const historyData = await historyResponse.json();
                                const history = historyData.data || historyData.history || historyData;
                                
                                if (Array.isArray(history) && history.length > 0) {
                                    this.ohlcvData = history.map(candle => ({
                                        time: candle.timestamp || candle.time || candle[0],
                                        open: candle.open || candle.o || candle[1],
                                        high: candle.high || candle.h || candle[2],
                                        low: candle.low || candle.l || candle[3],
                                        close: candle.close || candle.c || candle[4],
                                        volume: candle.volume || candle.v || candle[5]
                                    })).filter(c => c.time && c.open && c.high && c.low && c.close);
                                    
                                    if (this.ohlcvData.length > 0) {
                                        this.updateChart();
                                        this.updateConnectionStatus('Historical OHLCV data loaded', 'success');
                                        return;
                                    }
                                }
                            }
                        } catch (historyError) {
                            console.warn('[HTS] History API failed:', historyError);
                        }
                    }
                }
            }
        } catch (e) {
            console.error('[HTS] All APIs failed:', e);
            if (e.message && e.message.includes('ERR_CONNECTION_REFUSED')) {
                console.warn('[HTS] Connection refused - ensure backend is running or use correct API URL');
            }
        }
        
        // NO FALLBACK - Show error if all APIs fail
        this.ohlcvData = [];
        this.updateChart();
        this.updateConnectionStatus('No data available - all APIs failed', 'error');
    }

    // REMOVED: generateOHLCVFromPrice() - No synthetic data generation allowed, only real data from APIs
    // REMOVED: generateFallbackData() - No fallback data generation allowed, only real data from APIs

    /**
     * Update chart with current data
     */
    updateChart() {
        if (!this.chart || !this.candlestickSeries || this.ohlcvData.length === 0) {
            if (!this.chart) {
                console.warn('[HTS] Chart not initialized, skipping update');
            }
            return;
        }

        try {
            // Update candlestick data
            const candlestickData = this.ohlcvData.map(d => ({
                time: d.time,
                open: d.open,
                high: d.high,
                low: d.low,
                close: d.close
            }));
            
            if (typeof this.candlestickSeries.setData === 'function') {
                this.candlestickSeries.setData(candlestickData);
            }

            // Update volume
            if (this.volumeSeries && document.getElementById('show-volume')?.checked) {
                if (typeof this.volumeSeries.setData === 'function') {
                    const volumeData = this.ohlcvData.map(d => ({
                        time: d.time,
                        value: d.volume,
                        color: d.close >= d.open ? '#26a69a80' : '#ef535080'
                    }));
                    this.volumeSeries.setData(volumeData);
                }
            }

            // Calculate and update RSI
            if (this.rsiSeries && document.getElementById('show-rsi')?.checked) {
                if (typeof this.rsiSeries.setData === 'function') {
                    const rsiValues = this.calculateRSIForChart();
                    if (rsiValues.length > 0) {
                        this.rsiSeries.setData(rsiValues);
                    }
                }
            }

            // Calculate and update MACD
            if (this.macdSeries && document.getElementById('show-macd')?.checked) {
                if (typeof this.macdSeries.setData === 'function') {
                    const macdValues = this.calculateMACDForChart();
                    if (macdValues.length > 0) {
                        this.macdSeries.setData(macdValues);
                    }
                }
            }

            // Fit content to view
            if (typeof this.chart.timeScale === 'function') {
                const timeScale = this.chart.timeScale();
                if (timeScale && typeof timeScale.fitContent === 'function') {
                    timeScale.fitContent();
                }
            }
        } catch (error) {
            console.error('[HTS] Chart update error:', error);
        }
    }

    /**
     * Calculate RSI for chart display
     */
    calculateRSIForChart() {
        if (this.ohlcvData.length < 15) return [];
        
        const closes = this.ohlcvData.map(d => d.close);
        const rsiValues = [];
        
        for (let i = 14; i < closes.length; i++) {
            const rsi = this.engine.calculateRSI(closes.slice(0, i + 1), 14);
            if (rsi !== null) {
                rsiValues.push({
                    time: this.ohlcvData[i].time,
                    value: rsi
                });
            }
        }
        
        return rsiValues;
    }

    /**
     * Calculate MACD for chart display
     */
    calculateMACDForChart() {
        if (this.ohlcvData.length < 26) return [];
        
        const closes = this.ohlcvData.map(d => d.close);
        const macdValues = [];
        
        for (let i = 26; i < closes.length; i++) {
            const macd = this.engine.calculateMACD(closes.slice(0, i + 1));
            if (macd && macd.macd !== null) {
                macdValues.push({
                    time: this.ohlcvData[i].time,
                    value: macd.macd
                });
            }
        }
        
        return macdValues;
    }


    /**
     * Run HTS analysis
     */
    async runAnalysis() {
        try {
            if (this.ohlcvData.length < 30) {
                this.showError('Insufficient data for analysis. Please wait...');
                return;
            }

            const symbol = this.symbol.replace('USDT', '');
            this.analysisResult = await this.engine.analyze(this.ohlcvData, symbol);
            
            this.renderAnalysisResult();
            this.renderComponents();
            this.renderSMCLevels();
            this.renderPatterns();
        } catch (error) {
            console.error('[HTS] Analysis error:', error);
            this.showError('Analysis failed: ' + error.message);
        }
    }

    /**
     * Render analysis result
     */
    renderAnalysisResult() {
        if (!this.analysisResult) return;

        const container = document.getElementById('hts-signal-content');
        if (!container) return;

        if (!this.analysisResult || typeof this.analysisResult !== 'object') {
            container.innerHTML = '<div class="error-message">Invalid analysis result</div>';
            return;
        }
        
        const { finalScore, finalSignal, confidence, currentPrice, stopLoss, takeProfitLevels, riskReward, marketRegime } = this.analysisResult;
        
        const signal = String(finalSignal || 'hold').toLowerCase();
        const signalColor = signal === 'buy' ? '#22c55e' : signal === 'sell' ? '#ef4444' : '#eab308';
        const signalIcon = signal === 'buy' ? TradingIcons.buy : signal === 'sell' ? TradingIcons.sell : TradingIcons.hold;
        
        const validScore = typeof finalScore === 'number' && !isNaN(finalScore) ? finalScore : 0;
        const validConfidence = typeof confidence === 'number' && !isNaN(confidence) ? Math.max(0, Math.min(100, confidence)) : 0;
        const validPrice = typeof currentPrice === 'number' && !isNaN(currentPrice) && currentPrice > 0 ? currentPrice : 0;
        const validStopLoss = typeof stopLoss === 'number' && !isNaN(stopLoss) && stopLoss > 0 ? stopLoss : 0;
        const validTakeProfits = Array.isArray(takeProfitLevels) ? takeProfitLevels.filter(tp => tp && typeof tp === 'object' && typeof tp.level === 'number' && !isNaN(tp.level)) : [];
        const validRiskReward = typeof riskReward === 'number' && !isNaN(riskReward) ? riskReward : 0;
        
        const regimeColors = {
            'trending': '#3b82f6',
            'ranging': '#8b5cf6',
            'volatile': '#f59e0b',
            'volatile-trending': '#ef4444',
            'neutral': '#6b7280'
        };
        
        const regimeLabels = {
            'trending': 'Trending Market',
            'ranging': 'Ranging Market',
            'volatile': 'Volatile Market',
            'volatile-trending': 'Volatile Trending',
            'neutral': 'Neutral Market'
        };

        container.innerHTML = `
            <div class="signal-main">
                ${marketRegime ? `
                    <div class="market-regime-badge" style="background: ${regimeColors[marketRegime.regime || 'neutral']}20; border-color: ${regimeColors[marketRegime.regime || 'neutral']}40;">
                        <span class="regime-label">Market Regime:</span>
                        <span class="regime-value">${regimeLabels[marketRegime.regime || 'neutral']}</span>
                        <span class="regime-stats">
                            Volatility: ${(marketRegime.volatility || 0).toFixed(2)}% | 
                            Trend: ${(marketRegime.trendStrength || 0).toFixed(0)}%
                        </span>
                    </div>
                ` : ''}
                <div class="signal-score">
                    <div class="score-value" style="color: ${signalColor}">${escapeHtml(safeFormatNumber(validScore, { minimumFractionDigits: 1, maximumFractionDigits: 1 }))}</div>
                    <div class="score-label">Final Score</div>
                </div>
                <div class="signal-details">
                    <div class="detail-item">
                        <span class="detail-label">Signal:</span>
                        <span class="detail-value signal-${escapeHtml(signal)}" style="color: ${signalColor}">
                            ${signalIcon} ${escapeHtml(signal.toUpperCase())}
                        </span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Confidence:</span>
                        <span class="detail-value">${escapeHtml(safeFormatNumber(validConfidence, { minimumFractionDigits: 1, maximumFractionDigits: 1 }))}%</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Current Price:</span>
                        <span class="detail-value">${validPrice > 0 ? safeFormatCurrency(validPrice) : '—'}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Stop Loss:</span>
                        <span class="detail-value text-danger">${validStopLoss > 0 ? safeFormatCurrency(validStopLoss) : '—'}</span>
                    </div>
                    <div class="detail-item">
                        <span class="detail-label">Risk/Reward:</span>
                        <span class="detail-value">1:${escapeHtml(safeFormatNumber(validRiskReward, { minimumFractionDigits: 2, maximumFractionDigits: 2 }))}</span>
                    </div>
                </div>
                <div class="take-profit-levels">
                    <h4>Take Profit Levels</h4>
                    ${validTakeProfits.length > 0 ? validTakeProfits.map(tp => {
                        const tpType = escapeHtml(String(tp.type || 'TP'));
                        const tpLevel = safeFormatCurrency(tp.level);
                        const tpRR = typeof tp.riskReward === 'number' && !isNaN(tp.riskReward) 
                            ? escapeHtml(safeFormatNumber(tp.riskReward, { minimumFractionDigits: 2, maximumFractionDigits: 2 }))
                            : '—';
                        return `
                        <div class="tp-level">
                            <span class="tp-label">${tpType}:</span>
                            <span class="tp-value">${tpLevel}</span>
                            <span class="tp-rr">R:R ${tpRR}</span>
                        </div>
                    `;
                    }).join('') : '<div class="no-tp-levels">No take profit levels available</div>'}
                </div>
            </div>
        `;

        // Update signal badge
        const badge = document.getElementById('hts-signal-badge');
        if (badge) {
            badge.textContent = finalSignal.toUpperCase();
            badge.className = `signal-badge signal-${finalSignal}`;
        }
    }

    /**
     * Render component scores
     */
    renderComponents() {
        if (!this.analysisResult || !this.analysisResult.components) return;

        const container = document.getElementById('hts-components-grid');
        if (!container) return;

        const components = this.analysisResult.components;
        
        if (!components || typeof components !== 'object') {
            container.innerHTML = '<div class="no-components">No component data available</div>';
            return;
        }

        container.innerHTML = Object.entries(components)
            .filter(([key, comp]) => comp && typeof comp === 'object')
            .map(([key, comp]) => {
                const validScore = typeof comp.score === 'number' && !isNaN(comp.score) 
                    ? Math.max(0, Math.min(100, comp.score)) 
                    : 50;
                const validWeight = typeof comp.weight === 'number' && !isNaN(comp.weight) 
                    ? Math.max(0, Math.min(1, comp.weight)) 
                    : 0;
                const validBaseWeight = (comp.baseWeight && typeof comp.baseWeight === 'number' && !isNaN(comp.baseWeight))
                    ? Math.max(0, Math.min(1, comp.baseWeight))
                    : validWeight;
                const validConfidence = typeof comp.confidence === 'number' && !isNaN(comp.confidence)
                    ? Math.max(0, Math.min(100, comp.confidence))
                    : 0;
                
                const scoreColor = validScore > 60 ? '#22c55e' : validScore < 40 ? '#ef4444' : '#eab308';
                const weightPercent = (validWeight * 100).toFixed(1);
                const baseWeightPercent = (validBaseWeight * 100).toFixed(1);
                const weightChange = validBaseWeight ? validWeight - validBaseWeight : 0;
                const weightChangePercent = (weightChange * 100).toFixed(1);
                const weightChangeColor = weightChange > 0.001 ? '#22c55e' : weightChange < -0.001 ? '#ef4444' : '#6b7280';
                
                const signal = escapeHtml(String(comp.signal || 'hold').toUpperCase());
                const signalClass = escapeHtml(String(comp.signal || 'hold'));
                const keyDisplay = escapeHtml(String(key).toUpperCase());
                
                const detailsHtml = (key === 'rsiMacd' && comp.details && typeof comp.details === 'object') ? `
                        <div class="component-details">
                            <div>RSI: ${escapeHtml(String(comp.details.rsi || '—'))}</div>
                            <div>MACD: ${escapeHtml(String(comp.details.macd || '—'))}</div>
                            <div>Histogram: ${escapeHtml(String(comp.details.histogram || '—'))}</div>
                        </div>
                    ` : '';
                
                return `
                <div class="component-card">
                    <div class="component-header">
                        <h4>${keyDisplay}</h4>
                        <div class="weight-info">
                            <span class="component-weight">${escapeHtml(weightPercent)}%</span>
                            ${Math.abs(weightChange) > 0.001 ? `
                                <span class="weight-change" style="color: ${weightChangeColor}">
                                    ${weightChange > 0 ? '↑' : '↓'} ${escapeHtml(String(Math.abs(weightChangePercent)))}%
                                </span>
                            ` : ''}
                        </div>
                    </div>
                    <div class="weight-bar-container">
                        <div class="weight-bar-base" style="width: ${escapeHtml(baseWeightPercent)}%"></div>
                        <div class="weight-bar-current" style="width: ${escapeHtml(weightPercent)}%; background: ${weightChangeColor}"></div>
                    </div>
                    <div class="component-score" style="color: ${scoreColor}">
                        ${escapeHtml(safeFormatNumber(validScore, { minimumFractionDigits: 1, maximumFractionDigits: 1 }))}
                    </div>
                    <div class="component-signal signal-${signalClass}">
                        ${signal}
                    </div>
                    <div class="component-confidence">
                        Confidence: ${escapeHtml(safeFormatNumber(validConfidence, { minimumFractionDigits: 1, maximumFractionDigits: 1 }))}%
                    </div>
                    ${detailsHtml}
                </div>
            `;
        }).filter(html => html.length > 0).join('') || '<div class="no-components">No component data available</div>';
    }

    /**
     * Render SMC levels
     */
    renderSMCLevels() {
        if (!this.analysisResult || !this.analysisResult.smcLevels) return;

        const container = document.getElementById('hts-smc-content');
        if (!container) return;

        const smcLevels = this.analysisResult.smcLevels;
        if (!smcLevels || typeof smcLevels !== 'object') {
            container.innerHTML = '<div class="no-smc">No SMC levels available</div>';
            return;
        }

        const orderBlocks = Array.isArray(smcLevels.orderBlocks) ? smcLevels.orderBlocks : [];
        const liquidityZones = Array.isArray(smcLevels.liquidityZones) ? smcLevels.liquidityZones : [];
        const breakerBlocks = Array.isArray(smcLevels.breakerBlocks) ? smcLevels.breakerBlocks : [];
        
        container.innerHTML = `
            <div class="smc-section">
                <h4>Order Blocks: ${escapeHtml(String(orderBlocks.length))}</h4>
                <div class="smc-items">
                    ${orderBlocks.slice(-3)
                        .filter(block => block && typeof block === 'object' && 
                                typeof block.high === 'number' && !isNaN(block.high) &&
                                typeof block.low === 'number' && !isNaN(block.low))
                        .map(block => {
                            const volume = typeof block.volume === 'number' && !isNaN(block.volume) 
                                ? (block.volume / 1000000).toFixed(2) 
                                : '0.00';
                            return `
                        <div class="smc-item">
                            <span>High: ${safeFormatCurrency(block.high)}</span>
                            <span>Low: ${safeFormatCurrency(block.low)}</span>
                            <span>Volume: ${escapeHtml(volume)}M</span>
                        </div>
                    `;
                        }).join('') || '<div class="no-items">No order blocks</div>'}
                </div>
            </div>
            <div class="smc-section">
                <h4>Liquidity Zones: ${escapeHtml(String(liquidityZones.length))}</h4>
                <div class="smc-items">
                    ${liquidityZones
                        .filter(zone => zone && typeof zone === 'object' && 
                                typeof zone.level === 'number' && !isNaN(zone.level))
                        .map(zone => {
                            const zoneType = escapeHtml(String(zone.type || 'unknown').toUpperCase());
                            const zoneTypeClass = escapeHtml(String(zone.type || 'unknown'));
                            const zoneStrength = escapeHtml(String(zone.strength || 'Medium'));
                            return `
                        <div class="smc-item smc-${zoneTypeClass}">
                            <span>${zoneType}: ${safeFormatCurrency(zone.level)}</span>
                            <span>Strength: ${zoneStrength}</span>
                        </div>
                    `;
                        }).join('') || '<div class="no-items">No liquidity zones</div>'}
                </div>
            </div>
            <div class="smc-section">
                <h4>Breaker Blocks: ${escapeHtml(String(breakerBlocks.length))}</h4>
                <div class="smc-items">
                    ${breakerBlocks
                        .filter(block => block && typeof block === 'object' && 
                                typeof block.level === 'number' && !isNaN(block.level))
                        .map(block => {
                            const blockType = escapeHtml(String(block.type || 'unknown').toUpperCase());
                            const blockTypeClass = escapeHtml(String(block.type || 'unknown'));
                            return `
                        <div class="smc-item smc-${blockTypeClass}">
                            <span>${blockType}</span>
                            <span>Level: ${safeFormatCurrency(block.level)}</span>
                        </div>
                    `;
                        }).join('') || '<div class="no-items">No breaker blocks</div>'}
                </div>
            </div>
        `;
    }

    /**
     * Render detected patterns
     */
    renderPatterns() {
        if (!this.analysisResult || !this.analysisResult.patterns) return;

        const container = document.getElementById('hts-patterns-content');
        if (!container) return;

        const patterns = Array.isArray(this.analysisResult.patterns) ? this.analysisResult.patterns : [];
        
        if (patterns.length === 0) {
            container.innerHTML = '<p class="no-patterns">No patterns detected</p>';
            return;
        }

        container.innerHTML = `
            <div class="patterns-grid">
                ${patterns
                    .filter(pattern => pattern && typeof pattern === 'object')
                    .map(pattern => {
                        const patternName = escapeHtml(String(pattern.name || 'Unknown Pattern'));
                        const patternType = escapeHtml(String(pattern.type || 'neutral').toUpperCase());
                        const patternTypeClass = escapeHtml(String(pattern.type || 'neutral'));
                        const patternConfidence = typeof pattern.confidence === 'number' && !isNaN(pattern.confidence)
                            ? escapeHtml(safeFormatNumber(pattern.confidence, { minimumFractionDigits: 0, maximumFractionDigits: 0 }))
                            : '0';
                        
                        return `
                    <div class="pattern-card pattern-${patternTypeClass}">
                        <div class="pattern-name">${patternName}</div>
                        <div class="pattern-type">${patternType}</div>
                        <div class="pattern-confidence">Confidence: ${patternConfidence}%</div>
                    </div>
                `;
                    }).filter(html => html.length > 0).join('') || '<p class="no-patterns">No valid patterns detected</p>'}
            </div>
        `;
    }

    /**
     * Update connection status
     */
    updateConnectionStatus(status, type) {
        const statusEl = document.getElementById('hts-connection-status');
        if (statusEl) {
            statusEl.textContent = status;
            statusEl.className = `status-indicator status-${type}`;
        }
    }

    /**
     * Show error message
     */
    showError(message) {
        const container = document.getElementById('hts-signal-content');
        if (container) {
            container.innerHTML = `
                <div class="error-message">
                    ${TradingIcons.risk}
                    <p>${message}</p>
                </div>
            `;
        }
    }

    /**
     * Start auto-analysis
     */
    startAutoAnalysis() {
        this.stopAutoAnalysis();
        this.autoAnalysisInterval = setInterval(async () => {
            if (this.ohlcvData.length >= 30) {
                await this.runAnalysis();
            }
        }, 60000); // Every minute
    }

    /**
     * Stop auto-analysis
     */
    stopAutoAnalysis() {
        if (this.autoAnalysisInterval) {
            clearInterval(this.autoAnalysisInterval);
            this.autoAnalysisInterval = null;
        }
    }
}

// Initialize HTS Page when DOM is ready
let htsPageInstance = null;

document.addEventListener('DOMContentLoaded', () => {
    // Only initialize if we're on the trading assistant page
    if (document.getElementById('hts-trading-view')) {
        htsPageInstance = new HTSPage();
        window.htsPage = htsPageInstance;
    }
});

// Export for module use
export default HTSPage;


