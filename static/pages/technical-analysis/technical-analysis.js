/**
 * Advanced Technical Analysis Page
 * TradingView-like features with harmonic patterns, Elliott Wave, etc.
 */

import { apiClient } from '/static/shared/js/core/api-client.js';
import { logger } from '../../shared/js/utils/logger.js';
import { escapeHtml, safeFormatNumber, safeFormatCurrency } from '../../shared/js/utils/sanitizer.js';

class TechnicalAnalysisPage {
  constructor() {
    this.symbol = 'BTC';
    this.timeframe = '4h'; // Default for TA_QUICK
    this.currentMode = 'TA_QUICK';
    this.chart = null;
    this.candlestickSeries = null;
    this.volumeSeries = null;
    this.rsiSeries = null;
    this.macdSeries = null;
    this.trendLineSeries = null;
    this.supportLineSeries = null;
    this.resistanceLineSeries = null;
    this.fibonacciLevels = [];
    this.indicators = {
      rsi: true,
      macd: true,
      volume: false,
      ichimoku: false,
      elliott: false
    };
    this.patterns = {
      gartley: true,
      butterfly: true,
      bat: true,
      crab: true,
      candlestick: true
    };
    this.ohlcvData = [];
    this.analysisData = null;
    this.fundamentalData = null;
    this.onchainData = null;
    this.riskData = null;
    this.retryConfig = {
      maxRetries: 3,
      baseDelay: 1000,
      maxDelay: 5000
    };
  }

  async init() {
    try {
      console.log('[TechnicalAnalysis] Initializing...');
      this.bindEvents();
      await this.loadChart();
      await this.analyze();
      console.log('[TechnicalAnalysis] Ready');
    } catch (error) {
      logger.error('TechnicalAnalysis', 'Init error:', error);
    }
  }

  bindEvents() {
    // Mode tabs
    document.querySelectorAll('.mode-tab').forEach(tab => {
      tab.addEventListener('click', (e) => {
        const mode = e.currentTarget.dataset.mode;
        this.switchMode(mode);
      });
    });

    // Symbol input
    document.getElementById('symbol-input')?.addEventListener('change', (e) => {
      this.symbol = e.target.value.toUpperCase();
      this.runCurrentModeAnalysis();
    });

    // Timeframe select
    document.getElementById('timeframe-select')?.addEventListener('change', (e) => {
      this.timeframe = e.target.value;
      this.runCurrentModeAnalysis();
    });

    // Indicator checkboxes
    Object.keys(this.indicators).forEach(key => {
      const checkbox = document.getElementById(`indicator-${key}`);
      if (checkbox) {
        checkbox.addEventListener('change', (e) => {
          this.indicators[key] = e.target.checked;
          this.updateChart();
        });
      }
    });

    // Pattern checkboxes
    Object.keys(this.patterns).forEach(key => {
      const checkbox = document.getElementById(`pattern-${key}`);
      if (checkbox) {
        checkbox.addEventListener('change', (e) => {
          this.patterns[key] = e.target.checked;
          this.analyze();
        });
      }
    });

    // Analyze button
    document.getElementById('analyze-btn')?.addEventListener('click', () => {
      this.analyze();
    });

    // Chart controls
    document.getElementById('zoom-in')?.addEventListener('click', () => {
      this.chart?.timeScale().zoomIn();
    });
    document.getElementById('zoom-out')?.addEventListener('click', () => {
      this.chart?.timeScale().zoomOut();
    });
    document.getElementById('reset-chart')?.addEventListener('click', () => {
      this.chart?.timeScale().fitContent();
    });
  }

  async loadChart() {
    const container = document.getElementById('tradingview-chart');
    if (!container) return;

    // Create chart
    if (!window.LightweightCharts) {
      throw new Error('LightweightCharts library not loaded');
    }
    this.chart = window.LightweightCharts.createChart(container, {
      width: container.clientWidth,
      height: 600,
      layout: {
        background: { color: '#0f172a' },
        textColor: '#94a3b8',
      },
      grid: {
        vertLines: { color: '#1e293b' },
        horzLines: { color: '#1e293b' },
      },
      timeScale: {
        timeVisible: true,
        secondsVisible: false,
      },
    });

    // Create candlestick series with fallback for different library versions
    const seriesOptions = {
      upColor: '#22c55e',
      downColor: '#ef4444',
      borderVisible: false,
      wickUpColor: '#22c55e',
      wickDownColor: '#ef4444',
    };

    // Try multiple methods for compatibility
    if (typeof this.chart.addCandlestickSeries === 'function') {
      this.candlestickSeries = this.chart.addCandlestickSeries(seriesOptions);
    } else if (typeof this.chart.addSeries === 'function' && window.LightweightCharts && window.LightweightCharts.SeriesType && window.LightweightCharts.SeriesType.Candlestick) {
      this.candlestickSeries = this.chart.addSeries(window.LightweightCharts.SeriesType.Candlestick, seriesOptions);
    } else if (typeof this.chart.addSeries === 'function') {
      try {
        this.candlestickSeries = this.chart.addSeries('Candlestick', seriesOptions);
      } catch (e) {
        console.error('Failed to create candlestick series:', e);
        throw new Error('Could not create candlestick series');
      }
    } else {
      throw new Error('No compatible method to create candlestick series found');
    }

    if (!this.candlestickSeries) {
      throw new Error('Failed to create candlestick series');
    }

    // Create volume series (if enabled)
    if (this.indicators.volume) {
      this.volumeSeries = this.chart.addHistogramSeries({
        color: '#3b82f6',
        priceFormat: {
          type: 'volume',
        },
        priceScaleId: '',
        scaleMargins: {
          top: 0.8,
          bottom: 0,
        },
      });
    }
  }

  async analyze() {
    try {
      // Fetch OHLCV data with retry logic
      let response;
      let retries = 0;
      const maxRetries = 2;
      
      while (retries <= maxRetries) {
        try {
          // Use relative URL
          const url = `/api/ohlcv?symbol=${encodeURIComponent(this.symbol)}&timeframe=${encodeURIComponent(this.timeframe)}&limit=500`;
          response = await fetch(url, {
            signal: AbortSignal.timeout(15000)
          });

          if (response.ok) {
            break;
          }
          
          if (retries < maxRetries && response.status >= 500) {
            const delay = Math.min(1000 * Math.pow(2, retries), 5000);
            await this.delay(delay);
            retries++;
            continue;
          }
          
          throw new Error(`Failed to fetch OHLCV data: HTTP ${response.status}`);
        } catch (error) {
          if (retries < maxRetries && (error.message.includes('timeout') || error.message.includes('network'))) {
            const delay = Math.min(1000 * Math.pow(2, retries), 5000);
            await this.delay(delay);
            retries++;
            continue;
          }
          throw error;
        }
      }

      if (!response || !response.ok) {
        throw new Error('Failed to fetch OHLCV data after retries');
      }

      const data = await response.json();
      if (!data || typeof data !== 'object') {
        throw new Error('Invalid response format');
      }
      
      // Handle error responses
      if (data.success === false || data.error === true) {
        throw new Error(data.message || 'Failed to fetch OHLCV data');
      }
      
      // Validate data structure
      const ohlcvData = data.data || data.ohlcv || [];
      if (!Array.isArray(ohlcvData) || ohlcvData.length === 0) {
        throw new Error('No OHLCV data available');
      }
      
      // Validate first candle has required fields
      const firstCandle = ohlcvData[0];
      if (!firstCandle || (typeof firstCandle.open === 'undefined' && typeof firstCandle.o === 'undefined')) {
        throw new Error('Invalid OHLCV data structure - missing required fields');
      }

      this.ohlcvData = ohlcvData;

      // Fetch technical analysis with error handling
      let analysisResponse;
      try {
        analysisResponse = await apiClient.fetch(
          '/api/technical/analyze',
          {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              symbol: this.symbol,
              timeframe: this.timeframe,
              ohlcv: this.ohlcvData,
              indicators: this.indicators,
              patterns: this.patterns
            })
          },
          20000
        );

        if (analysisResponse.ok) {
          const analysisJson = await analysisResponse.json();
          if (analysisJson && typeof analysisJson === 'object') {
            this.analysisData = analysisJson;
          } else {
            throw new Error('Invalid analysis response format');
          }
        } else {
          // Fallback: calculate locally
          logger.warn('TechnicalAnalysis', `Analysis API returned ${analysisResponse.status}, using local calculation`);
          this.analysisData = this.calculateTechnicalAnalysis();
        }
      } catch (error) {
        logger.warn('TechnicalAnalysis', 'Analysis API error, using local calculation:', error);
        // Fallback: calculate locally
        this.analysisData = this.calculateTechnicalAnalysis();
      }

      this.updateChart();
      this.renderAnalysis();
    } catch (error) {
      logger.error('TechnicalAnalysis', 'Analysis error:', error);
      this.showError('Failed to load analysis. Using fallback calculations.');
      this.analysisData = this.calculateTechnicalAnalysis();
      this.updateChart();
      this.renderAnalysis();
    }
  }

  calculateTechnicalAnalysis() {
    // Fallback local calculations
    return {
      support_resistance: this.calculateSupportResistance(),
      harmonic_patterns: this.detectHarmonicPatterns(),
      elliott_wave: this.analyzeElliottWave(),
      candlestick_patterns: this.detectCandlestickPatterns(),
      indicators: this.calculateIndicators(),
      signals: this.generateSignals()
    };
  }

  calculateSupportResistance() {
    const closes = this.ohlcvData.map(c => parseFloat(c.c || c.close));
    const highs = this.ohlcvData.map(c => parseFloat(c.h || c.high));
    const lows = this.ohlcvData.map(c => parseFloat(c.l || c.low));

    // Pivot-based calculation
    const pivots = this.findPivotPoints(highs, lows, closes);
    
    return {
      support: pivots.support,
      resistance: pivots.resistance,
      levels: pivots.levels
    };
  }

  findPivotPoints(highs, lows, closes, period = 5) {
    const pivotHighs = [];
    const pivotLows = [];
    const levels = [];

    for (let i = period; i < highs.length - period; i++) {
      // Pivot High
      let isPivotHigh = true;
      for (let j = i - period; j <= i + period; j++) {
        if (j !== i && highs[j] >= highs[i]) {
          isPivotHigh = false;
          break;
        }
      }
      if (isPivotHigh) {
        pivotHighs.push({ index: i, value: highs[i] });
        levels.push({ type: 'resistance', value: highs[i], strength: this.calculateLevelStrength(highs[i], highs) });
      }

      // Pivot Low
      let isPivotLow = true;
      for (let j = i - period; j <= i + period; j++) {
        if (j !== i && lows[j] <= lows[i]) {
          isPivotLow = false;
          break;
        }
      }
      if (isPivotLow) {
        pivotLows.push({ index: i, value: lows[i] });
        levels.push({ type: 'support', value: lows[i], strength: this.calculateLevelStrength(lows[i], lows) });
      }
    }

    // Get strongest levels
    const support = pivotLows.length > 0 
      ? pivotLows.sort((a, b) => a.value - b.value)[0].value 
      : Math.min(...lows.slice(-50));
    
    const resistance = pivotHighs.length > 0
      ? pivotHighs.sort((a, b) => b.value - a.value)[0].value
      : Math.max(...highs.slice(-50));

    return { support, resistance, levels: levels.slice(-10) };
  }

  calculateLevelStrength(level, prices) {
    const touches = prices.filter(p => Math.abs(p - level) / level < 0.01).length;
    return Math.min(touches / 3, 1);
  }

  detectHarmonicPatterns() {
    const patterns = [];
    const closes = this.ohlcvData.map(c => parseFloat(c.c || c.close));
    
    // Gartley Pattern
    const gartley = this.detectGartley(closes);
    if (gartley) patterns.push(gartley);

    // Butterfly Pattern
    const butterfly = this.detectButterfly(closes);
    if (butterfly) patterns.push(butterfly);

    // Bat Pattern
    const bat = this.detectBat(closes);
    if (bat) patterns.push(bat);

    // Crab Pattern
    const crab = this.detectCrab(closes);
    if (crab) patterns.push(crab);

    return patterns;
  }

  detectGartley(prices) {
    // Simplified Gartley detection
    if (prices.length < 5) return null;
    
    const X = prices[prices.length - 5];
    const A = prices[prices.length - 4];
    const B = prices[prices.length - 3];
    const C = prices[prices.length - 2];
    const D = prices[prices.length - 1];

    const AB = Math.abs((B - A) / (A - X));
    const BC = Math.abs((C - B) / (B - A));
    const CD = Math.abs((D - C) / (C - B));

    // Gartley ratios: AB ~ 0.618, BC ~ 0.382-0.886, CD ~ 0.786
    if (Math.abs(AB - 0.618) < 0.1 && 
        BC > 0.3 && BC < 0.9 && 
        Math.abs(CD - 0.786) < 0.1) {
      return {
        type: 'Gartley',
        pattern: 'Bullish',
        confidence: 0.75,
        points: { X, A, B, C, D }
      };
    }
    return null;
  }

  detectButterfly(prices) {
    if (prices.length < 5) return null;
    
    const X = prices[prices.length - 5];
    const A = prices[prices.length - 4];
    const B = prices[prices.length - 3];
    const C = prices[prices.length - 2];
    const D = prices[prices.length - 1];

    const AB = Math.abs((B - A) / (A - X));
    const BC = Math.abs((C - B) / (B - A));
    const CD = Math.abs((D - C) / (C - B));

    // Butterfly ratios: AB ~ 0.786, BC ~ 0.382-0.886, CD ~ 1.27-1.618
    if (Math.abs(AB - 0.786) < 0.1 && 
        BC > 0.3 && BC < 0.9 && 
        CD > 1.2 && CD < 1.7) {
      return {
        type: 'Butterfly',
        pattern: 'Bearish',
        confidence: 0.70,
        points: { X, A, B, C, D }
      };
    }
    return null;
  }

  detectBat(prices) {
    if (prices.length < 5) return null;
    
    const X = prices[prices.length - 5];
    const A = prices[prices.length - 4];
    const B = prices[prices.length - 3];
    const C = prices[prices.length - 2];
    const D = prices[prices.length - 1];

    const AB = Math.abs((B - A) / (A - X));
    const BC = Math.abs((C - B) / (B - A));
    const CD = Math.abs((D - C) / (C - B));

    // Bat ratios: AB ~ 0.382-0.5, BC ~ 0.382-0.886, CD ~ 0.886
    if (AB > 0.3 && AB < 0.55 && 
        BC > 0.3 && BC < 0.9 && 
        Math.abs(CD - 0.886) < 0.1) {
      return {
        type: 'Bat',
        pattern: 'Bullish',
        confidence: 0.72,
        points: { X, A, B, C, D }
      };
    }
    return null;
  }

  detectCrab(prices) {
    if (prices.length < 5) return null;
    
    const X = prices[prices.length - 5];
    const A = prices[prices.length - 4];
    const B = prices[prices.length - 3];
    const C = prices[prices.length - 2];
    const D = prices[prices.length - 1];

    const AB = Math.abs((B - A) / (A - X));
    const BC = Math.abs((C - B) / (B - A));
    const CD = Math.abs((D - C) / (C - B));

    // Crab ratios: AB ~ 0.382-0.618, BC ~ 0.382-0.886, CD ~ 1.618
    if (AB > 0.3 && AB < 0.65 && 
        BC > 0.3 && BC < 0.9 && 
        Math.abs(CD - 1.618) < 0.15) {
      return {
        type: 'Crab',
        pattern: 'Bearish',
        confidence: 0.68,
        points: { X, A, B, C, D }
      };
    }
    return null;
  }

  analyzeElliottWave() {
    const closes = this.ohlcvData.map(c => parseFloat(c.c || c.close));
    if (closes.length < 34) return null;

    // Simplified Elliott Wave analysis
    const waves = this.identifyWaves(closes);
    return {
      wave_count: waves.length,
      current_wave: waves[waves.length - 1],
      pattern: this.determineElliottPattern(waves),
      target: this.calculateElliottTarget(waves)
    };
  }

  identifyWaves(prices) {
    const waves = [];
    let direction = null;
    let startIdx = 0;

    for (let i = 1; i < prices.length; i++) {
      const change = prices[i] - prices[i - 1];
      const currentDir = change > 0 ? 'up' : 'down';

      if (direction === null) {
        direction = currentDir;
      } else if (direction !== currentDir) {
        waves.push({
          direction,
          start: startIdx,
          end: i - 1,
          magnitude: Math.abs(prices[i - 1] - prices[startIdx])
        });
        startIdx = i - 1;
        direction = currentDir;
      }
    }

    return waves;
  }

  determineElliottPattern(waves) {
    if (waves.length < 5) return 'Incomplete';
    
    // Check for 5-wave impulse pattern
    const impulse = waves.slice(-5);
    if (impulse.length === 5) {
      const wave3 = impulse[2];
      const wave1 = impulse[0];
      
      // Wave 3 should be the longest
      if (wave3.magnitude > wave1.magnitude * 1.618) {
        return 'Impulse Wave (5-3-5-3-5)';
      }
    }
    
    return 'Corrective Wave';
  }

  calculateElliottTarget(waves) {
    if (waves.length < 3) return null;
    
    const lastWave = waves[waves.length - 1];
    const prevWave = waves[waves.length - 2];
    
    // Fibonacci extension target
    const target = lastWave.magnitude * 1.618;
    return {
      price: target,
      type: lastWave.direction === 'up' ? 'resistance' : 'support'
    };
  }

  detectCandlestickPatterns() {
    const patterns = [];
    
    for (let i = 4; i < this.ohlcvData.length; i++) {
      const candles = this.ohlcvData.slice(i - 4, i + 1);
      
      // Doji
      if (this.isDoji(candles[candles.length - 1])) {
        patterns.push({ type: 'Doji', index: i, signal: 'Reversal' });
      }
      
      // Hammer
      if (this.isHammer(candles[candles.length - 1])) {
        patterns.push({ type: 'Hammer', index: i, signal: 'Bullish' });
      }
      
      // Engulfing
      const engulfing = this.isEngulfing(candles[candles.length - 2], candles[candles.length - 1]);
      if (engulfing) {
        patterns.push({ type: engulfing, index: i, signal: engulfing.includes('Bullish') ? 'Bullish' : 'Bearish' });
      }
    }

    return patterns.slice(-10);
  }

  isDoji(candle) {
    const body = Math.abs(parseFloat(candle.c || candle.close) - parseFloat(candle.o || candle.open));
    const range = parseFloat(candle.h || candle.high) - parseFloat(candle.l || candle.low);
    return body / range < 0.1 && range > 0;
  }

  isHammer(candle) {
    const body = Math.abs(parseFloat(candle.c || candle.close) - parseFloat(candle.o || candle.open));
    const lowerShadow = Math.min(parseFloat(candle.c || candle.close), parseFloat(candle.o || candle.open)) - parseFloat(candle.l || candle.low);
    const upperShadow = parseFloat(candle.h || candle.high) - Math.max(parseFloat(candle.c || candle.close), parseFloat(candle.o || candle.open));
    return lowerShadow > body * 2 && upperShadow < body * 0.5;
  }

  isEngulfing(prevCandle, currentCandle) {
    const prevBody = Math.abs(parseFloat(prevCandle.c || prevCandle.close) - parseFloat(prevCandle.o || prevCandle.open));
    const currBody = Math.abs(parseFloat(currentCandle.c || currentCandle.close) - parseFloat(currentCandle.o || currentCandle.open));
    
    const prevBullish = parseFloat(prevCandle.c || prevCandle.close) > parseFloat(prevCandle.o || prevCandle.open);
    const currBullish = parseFloat(currentCandle.c || currentCandle.close) > parseFloat(currentCandle.o || currentCandle.open);
    
    if (currBody > prevBody * 1.5) {
      if (!prevBullish && currBullish) {
        return 'Bullish Engulfing';
      } else if (prevBullish && !currBullish) {
        return 'Bearish Engulfing';
      }
    }
    return null;
  }

  calculateIndicators() {
    const closes = this.ohlcvData.map(c => parseFloat(c.c || c.close));
    const volumes = this.ohlcvData.map(c => parseFloat(c.v || c.volume || 0));

    return {
      rsi: this.calculateRSI(closes),
      macd: this.calculateMACD(closes),
      ichimoku: this.calculateIchimoku(this.ohlcvData),
      sma20: this.calculateSMA(closes, 20),
      sma50: this.calculateSMA(closes, 50),
      volume_avg: volumes.length > 0 ? volumes.reduce((a, b) => a + b, 0) / volumes.length : 0
    };
  }

  calculateRSI(prices, period = 14) {
    if (prices.length < period + 1) return null;
    
    const deltas = [];
    for (let i = 1; i < prices.length; i++) {
      deltas.push(prices[i] - prices[i - 1]);
    }
    
    const gains = deltas.slice(-period).filter(d => d > 0);
    const losses = deltas.slice(-period).filter(d => d < 0).map(d => Math.abs(d));
    
    const avgGain = gains.length > 0 ? gains.reduce((a, b) => a + b, 0) / period : 0;
    const avgLoss = losses.length > 0 ? losses.reduce((a, b) => a + b, 0) / period : 0;
    
    if (avgLoss === 0) return avgGain > 0 ? 100 : 50;
    
    const rs = avgGain / avgLoss;
    return 100 - (100 / (1 + rs));
  }

  calculateMACD(prices, fast = 12, slow = 26, signal = 9) {
    if (prices.length < slow + signal) return null;
    
    const emaFast = this.calculateEMA(prices, fast);
    const emaSlow = this.calculateEMA(prices, slow);
    
    if (!emaFast || !emaSlow) return null;
    
    const macdLine = emaFast - emaSlow;
    const signalLine = this.calculateEMA([macdLine], signal);
    
    return {
      macd: macdLine,
      signal: signalLine,
      histogram: macdLine - signalLine
    };
  }

  calculateEMA(prices, period) {
    if (prices.length < period) return null;
    
    const multiplier = 2 / (period + 1);
    let ema = prices.slice(0, period).reduce((a, b) => a + b, 0) / period;
    
    for (let i = period; i < prices.length; i++) {
      ema = (prices[i] - ema) * multiplier + ema;
    }
    
    return ema;
  }

  calculateSMA(prices, period) {
    if (prices.length < period) return null;
    return prices.slice(-period).reduce((a, b) => a + b, 0) / period;
  }

  calculateIchimoku(ohlcv) {
    if (ohlcv.length < 52) return null;
    
    const closes = ohlcv.map(c => parseFloat(c.c || c.close));
    const highs = ohlcv.map(c => parseFloat(c.h || c.high));
    const lows = ohlcv.map(c => parseFloat(c.l || c.low));
    
    const tenkan = (Math.max(...highs.slice(-9)) + Math.min(...lows.slice(-9))) / 2;
    const kijun = (Math.max(...highs.slice(-26)) + Math.min(...lows.slice(-26))) / 2;
    const senkouA = (tenkan + kijun) / 2;
    const senkouB = (Math.max(...highs.slice(-52)) + Math.min(...lows.slice(-52))) / 2;
    const chikou = closes[closes.length - 26];
    
    return {
      tenkan,
      kijun,
      senkouA,
      senkouB,
      chikou,
      cloud: senkouA > senkouB ? 'bullish' : 'bearish'
    };
  }

  generateSignals() {
    const indicators = this.calculateIndicators();
    const signals = [];
    
    // RSI signals
    if (indicators.rsi) {
      if (indicators.rsi < 30) {
        signals.push({ type: 'BUY', source: 'RSI Oversold', strength: 'Strong' });
      } else if (indicators.rsi > 70) {
        signals.push({ type: 'SELL', source: 'RSI Overbought', strength: 'Strong' });
      }
    }
    
    // MACD signals
    if (indicators.macd) {
      if (indicators.macd.histogram > 0 && indicators.macd.macd > indicators.macd.signal) {
        signals.push({ type: 'BUY', source: 'MACD Bullish Crossover', strength: 'Medium' });
      } else if (indicators.macd.histogram < 0 && indicators.macd.macd < indicators.macd.signal) {
        signals.push({ type: 'SELL', source: 'MACD Bearish Crossover', strength: 'Medium' });
      }
    }
    
    // Support/Resistance signals
    const sr = this.calculateSupportResistance();
    const lastClose = parseFloat(this.ohlcvData[this.ohlcvData.length - 1].c || this.ohlcvData[this.ohlcvData.length - 1].close);
    
    if (sr.support && lastClose <= sr.support * 1.02) {
      signals.push({ type: 'BUY', source: 'Near Support Level', strength: 'Medium' });
    }
    
    if (sr.resistance && lastClose >= sr.resistance * 0.98) {
      signals.push({ type: 'SELL', source: 'Near Resistance Level', strength: 'Medium' });
    }
    
    return signals;
  }

  updateChart() {
    if (!this.chart || !this.candlestickSeries) {
      // Try to reload chart if not initialized
      this.loadChart();
      return;
    }

    if (!this.ohlcvData || this.ohlcvData.length === 0) {
      logger.warn('TechnicalAnalysis', 'No OHLCV data to display');
      return;
    }

    try {
      // Format data for TradingView
      const chartData = this.ohlcvData
        .filter(candle => {
          const close = parseFloat(candle.c || candle.close || 0);
          const open = parseFloat(candle.o || candle.open || 0);
          const high = parseFloat(candle.h || candle.high || 0);
          const low = parseFloat(candle.l || candle.low || 0);
          return close > 0 && open > 0 && high > 0 && low > 0 && high >= low;
        })
        .map(candle => ({
          time: Math.floor(parseInt(candle.t || candle.openTime || Date.now()) / 1000),
          open: parseFloat(candle.o || candle.open),
          high: parseFloat(candle.h || candle.high),
          low: parseFloat(candle.l || candle.low),
          close: parseFloat(candle.c || candle.close)
        }))
        .sort((a, b) => a.time - b.time); // Ensure chronological order

      if (chartData.length === 0) {
        throw new Error('No valid chart data after filtering');
      }

      this.candlestickSeries.setData(chartData);
      this.chart.timeScale().fitContent();
      
      // Draw trend lines with animation
      this.drawTrendLines();
      
      // Draw support/resistance levels
      this.drawSupportResistance();

      // Update volume if enabled
      if (this.indicators.volume && this.volumeSeries) {
        const volumeData = this.ohlcvData.map(candle => ({
          time: Math.floor(parseInt(candle.t || candle.openTime) / 1000),
          value: parseFloat(candle.v || candle.volume || 0),
          color: parseFloat(candle.c || candle.close) >= parseFloat(candle.o || candle.open) 
            ? 'rgba(34, 197, 94, 0.5)' 
            : 'rgba(239, 68, 68, 0.5)'
        }));
        this.volumeSeries.setData(volumeData);
      }

      // Update price display with validation
      const lastCandle = this.ohlcvData[this.ohlcvData.length - 1];
      if (!lastCandle) {
        logger.warn('TechnicalAnalysis', 'No last candle available for price display');
        return;
      }
      
      const lastClose = parseFloat(lastCandle.c || lastCandle.close);
      if (isNaN(lastClose) || lastClose <= 0) {
        logger.warn('TechnicalAnalysis', 'Invalid last close price');
        return;
      }
      
      const prevClose = this.ohlcvData.length > 1 
        ? parseFloat(this.ohlcvData[this.ohlcvData.length - 2].c || this.ohlcvData[this.ohlcvData.length - 2].close)
        : lastClose;
      
      if (isNaN(prevClose) || prevClose <= 0) {
        logger.warn('TechnicalAnalysis', 'Invalid previous close price');
        return;
      }
      
      const change = prevClose !== 0 ? ((lastClose - prevClose) / prevClose) * 100 : 0;
      
      const priceEl = document.getElementById('chart-price');
      if (priceEl) {
        priceEl.textContent = safeFormatNumber(lastClose);
      }
      
      const changeEl = document.getElementById('chart-change');
      if (changeEl) {
        changeEl.textContent = `${change >= 0 ? '+' : ''}${safeFormatNumber(change, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}%`;
        changeEl.className = `change-display ${change >= 0 ? 'positive' : 'negative'}`;
      }
    } catch (error) {
      logger.error('TechnicalAnalysis', 'Chart update error:', error);
      this.showError('Failed to update chart. Please try again.');
    }
  }
  
  drawTrendLines() {
    if (!this.analysisData || !this.chart) return;
    
    try {
      // Draw trend line based on SMA
      const closes = this.ohlcvData.map(c => parseFloat(c.c || c.close)).filter(v => v > 0);
      if (closes.length < 20) return;
      
      const sma20 = this.calculateSMA(closes, 20);
      if (!sma20) return;
      
      // Create trend line series
      if (!this.trendLineSeries) {
        this.trendLineSeries = this.chart.addLineSeries({
          color: '#2dd4bf',
          lineWidth: 2,
          lineStyle: 2, // Dashed
          title: 'SMA 20'
        });
      }
      
      // Calculate SMA20 data points
      const trendData = [];
      for (let i = 19; i < this.ohlcvData.length; i++) {
        const periodCloses = closes.slice(i - 19, i + 1);
        const sma = periodCloses.reduce((a, b) => a + b, 0) / 20;
        trendData.push({
          time: Math.floor(parseInt(this.ohlcvData[i].t || this.ohlcvData[i].openTime) / 1000),
          value: sma
        });
      }
      
      this.trendLineSeries.setData(trendData);
    } catch (error) {
      logger.warn('TechnicalAnalysis', 'Failed to draw trend lines:', error);
    }
  }
  
  drawSupportResistance() {
    if (!this.analysisData || !this.analysisData.support_resistance || !this.chart) return;
    
    try {
      const { support, resistance } = this.analysisData.support_resistance;
      if (!support && !resistance) return;
      
      const lastTime = Math.floor(parseInt(this.ohlcvData[this.ohlcvData.length - 1].t || this.ohlcvData[this.ohlcvData.length - 1].openTime) / 1000);
      const firstTime = Math.floor(parseInt(this.ohlcvData[0].t || this.ohlcvData[0].openTime) / 1000);
      
      // Draw support line
      if (support && !this.supportLineSeries) {
        this.supportLineSeries = this.chart.addLineSeries({
          color: '#ef4444',
          lineWidth: 2,
          lineStyle: 2,
          title: 'Support'
        });
        this.supportLineSeries.setData([
          { time: firstTime, value: support },
          { time: lastTime, value: support }
        ]);
      }
      
      // Draw resistance line
      if (resistance && !this.resistanceLineSeries) {
        this.resistanceLineSeries = this.chart.addLineSeries({
          color: '#22c55e',
          lineWidth: 2,
          lineStyle: 2,
          title: 'Resistance'
        });
        this.resistanceLineSeries.setData([
          { time: firstTime, value: resistance },
          { time: lastTime, value: resistance }
        ]);
      }
    } catch (error) {
      logger.warn('TechnicalAnalysis', 'Failed to draw support/resistance:', error);
    }
  }
  
  renderAnalysis() {
    if (!this.analysisData) return;

    this.renderSupportResistance();
    this.renderSignals();
    this.renderHarmonicPatterns();
    this.renderElliottWave();
    this.renderTradeRecommendations();
  }

  renderSupportResistance() {
    const container = document.getElementById('support-resistance-levels');
    if (!container || !this.analysisData || !this.analysisData.support_resistance) return;

    const { support, resistance, levels } = this.analysisData.support_resistance;
    
    // Validate levels array
    const validLevels = Array.isArray(levels) ? levels.filter(level => 
      level && typeof level === 'object' && 
      typeof level.value === 'number' && !isNaN(level.value) &&
      typeof level.strength === 'number' && !isNaN(level.strength)
    ) : [];
    
    const supportValue = (support && typeof support === 'number' && !isNaN(support)) 
      ? safeFormatNumber(support) 
      : '—';
    const resistanceValue = (resistance && typeof resistance === 'number' && !isNaN(resistance)) 
      ? safeFormatNumber(resistance) 
      : '—';
    
    container.innerHTML = `
      <div class="level-item support">
        <div class="level-icon">↓</div>
        <div class="level-details">
          <span class="level-type">Support</span>
          <strong class="level-price">${escapeHtml(supportValue)}</strong>
        </div>
      </div>
      <div class="level-item resistance">
        <div class="level-icon">↑</div>
        <div class="level-details">
          <span class="level-type">Resistance</span>
          <strong class="level-price">${escapeHtml(resistanceValue)}</strong>
        </div>
      </div>
      ${validLevels.map(level => {
        const levelType = escapeHtml(String(level.type || 'support'));
        const levelValue = safeFormatNumber(level.value);
        const strengthPercent = safeFormatNumber(level.strength * 100, { minimumFractionDigits: 0, maximumFractionDigits: 0 });
        return `
        <div class="level-item ${levelType}" style="opacity: ${Math.max(0, Math.min(1, level.strength))}">
          <div class="level-icon">${levelType === 'support' ? '↓' : '↑'}</div>
          <div class="level-details">
            <span class="level-type">${levelType === 'support' ? 'Support' : 'Resistance'}</span>
            <strong class="level-price">${escapeHtml(levelValue)}</strong>
            <span class="level-strength">Strength: ${escapeHtml(strengthPercent)}%</span>
          </div>
        </div>
      `;
      }).join('')}
    `;
  }

  renderSignals() {
    const container = document.getElementById('trading-signals');
    if (!container || !this.analysisData || !this.analysisData.signals) {
      if (container) {
        container.innerHTML = '<div class="no-signals">No signals detected</div>';
      }
      return;
    }

    const signals = Array.isArray(this.analysisData.signals) ? this.analysisData.signals : [];
    
    if (signals.length === 0) {
      container.innerHTML = '<div class="no-signals">No signals detected</div>';
      return;
    }
    
    container.innerHTML = signals.map(signal => {
      if (!signal || typeof signal !== 'object') return '';
      
      const signalType = String(signal.type || 'HOLD').toUpperCase();
      const signalSource = escapeHtml(String(signal.source || 'Unknown'));
      const signalStrength = escapeHtml(String(signal.strength || 'Medium'));
      const signalClass = escapeHtml(String(signalType).toLowerCase());
      const signalIcon = signalType === 'BUY' ? '🟢' : signalType === 'SELL' ? '🔴' : '🟡';
      
      return `
      <div class="signal-item ${signalClass}">
        <div class="signal-icon">${signalIcon}</div>
        <div class="signal-details">
          <span class="signal-type">${escapeHtml(signalType)}</span>
          <span class="signal-source">${signalSource}</span>
          <span class="signal-strength">${signalStrength}</span>
        </div>
      </div>
    `;
    }).filter(html => html.length > 0).join('') || '<div class="no-signals">No signals detected</div>';
  }

  renderHarmonicPatterns() {
    const container = document.getElementById('harmonic-patterns');
    if (!container || !this.analysisData || !this.analysisData.harmonic_patterns) {
      if (container) {
        container.innerHTML = '<div class="no-patterns">No harmonic patterns detected</div>';
      }
      return;
    }

    const patterns = Array.isArray(this.analysisData.harmonic_patterns) 
      ? this.analysisData.harmonic_patterns.filter(p => p && typeof p === 'object')
      : [];
    
    if (patterns.length === 0) {
      container.innerHTML = '<div class="no-patterns">No harmonic patterns detected</div>';
      return;
    }
    
    container.innerHTML = patterns.map(pattern => {
      const patternType = escapeHtml(String(pattern.type || 'Unknown'));
      const patternPattern = escapeHtml(String(pattern.pattern || 'Neutral').toLowerCase());
      const confidence = typeof pattern.confidence === 'number' && !isNaN(pattern.confidence)
        ? safeFormatNumber(pattern.confidence * 100, { minimumFractionDigits: 0, maximumFractionDigits: 0 })
        : '0';
      
      return `
      <div class="pattern-item ${patternPattern}">
        <div class="pattern-header">
          <span class="pattern-type">${patternType}</span>
          <span class="pattern-confidence">${escapeHtml(confidence)}%</span>
        </div>
        <div class="pattern-details">
          <span class="pattern-direction">${escapeHtml(String(pattern.pattern || 'Neutral'))}</span>
        </div>
      </div>
    `;
    }).filter(html => html.length > 0).join('') || '<div class="no-patterns">No harmonic patterns detected</div>';
  }

  renderElliottWave() {
    const container = document.getElementById('elliott-wave');
    if (!container || !this.analysisData || !this.analysisData.elliott_wave) {
      if (container) {
        container.innerHTML = '<div class="no-wave">Elliott Wave analysis not available</div>';
      }
      return;
    }

    const wave = this.analysisData.elliott_wave;
    if (!wave || typeof wave !== 'object') {
      if (container) {
        container.innerHTML = '<div class="no-wave">Elliott Wave analysis not available</div>';
      }
      return;
    }
    
    const pattern = escapeHtml(String(wave.pattern || 'Incomplete'));
    const waveCount = typeof wave.wave_count === 'number' ? wave.wave_count : 0;
    const targetHtml = (wave.target && typeof wave.target === 'object' && 
                       typeof wave.target.price === 'number' && !isNaN(wave.target.price))
      ? `
          <div class="wave-info">
            <span class="wave-label">Target:</span>
            <span class="wave-value">${escapeHtml(safeFormatNumber(wave.target.price))} (${escapeHtml(String(wave.target.type || 'unknown'))})</span>
          </div>
        `
      : '';
    
    container.innerHTML = `
      <div class="wave-analysis-card">
        <div class="wave-info">
          <span class="wave-label">Pattern:</span>
          <span class="wave-value">${pattern}</span>
        </div>
        <div class="wave-info">
          <span class="wave-label">Wave Count:</span>
          <span class="wave-value">${escapeHtml(String(waveCount))}</span>
        </div>
        ${targetHtml}
      </div>
    `;
  }

  renderTradeRecommendations() {
    const container = document.getElementById('trade-recommendations');
    if (!container) return;

    if (!this.analysisData || !this.ohlcvData || this.ohlcvData.length === 0) {
      container.innerHTML = '<div class="no-recommendations">Insufficient data for recommendations</div>';
      return;
    }

    const signals = Array.isArray(this.analysisData.signals) ? this.analysisData.signals : [];
    const sr = (this.analysisData.support_resistance && typeof this.analysisData.support_resistance === 'object') 
      ? this.analysisData.support_resistance 
      : {};
    
    const lastCandle = this.ohlcvData[this.ohlcvData.length - 1];
    const lastClose = (lastCandle && (typeof lastCandle.c === 'number' || typeof lastCandle.close === 'number'))
      ? parseFloat(lastCandle.c || lastCandle.close)
      : 0;
    
    if (lastClose <= 0 || isNaN(lastClose)) {
      container.innerHTML = '<div class="no-recommendations">Invalid price data</div>';
      return;
    }
    
    const buySignals = signals.filter(s => s && s.type === 'BUY');
    const sellSignals = signals.filter(s => s && s.type === 'SELL');
    
    let recommendation = 'HOLD';
    let tp = null;
    let sl = null;
    
    if (buySignals.length > sellSignals.length) {
      recommendation = 'BUY';
      tp = (sr.resistance && typeof sr.resistance === 'number' && !isNaN(sr.resistance))
        ? sr.resistance 
        : lastClose * 1.05;
      sl = (sr.support && typeof sr.support === 'number' && !isNaN(sr.support))
        ? sr.support 
        : lastClose * 0.95;
    } else if (sellSignals.length > buySignals.length) {
      recommendation = 'SELL';
      tp = (sr.support && typeof sr.support === 'number' && !isNaN(sr.support))
        ? sr.support 
        : lastClose * 0.95;
      sl = (sr.resistance && typeof sr.resistance === 'number' && !isNaN(sr.resistance))
        ? sr.resistance 
        : lastClose * 1.05;
    }
    
    const recommendationClass = escapeHtml(recommendation.toLowerCase());
    const confidenceText = signals.length > 0 ? 'High' : 'Low';
    const tpValue = tp && typeof tp === 'number' && !isNaN(tp) ? safeFormatNumber(tp) : '—';
    const slValue = sl && typeof sl === 'number' && !isNaN(sl) ? safeFormatNumber(sl) : '—';
    
    container.innerHTML = `
      <div class="recommendation-card ${recommendationClass}">
        <div class="recommendation-header">
          <span class="recommendation-type">${escapeHtml(recommendation)}</span>
          <span class="recommendation-confidence">${escapeHtml(confidenceText)}</span>
        </div>
        ${recommendation !== 'HOLD' ? `
          <div class="recommendation-levels">
            <div class="level-item">
              <span class="level-label">Take Profit:</span>
              <strong class="level-value">${escapeHtml(tpValue)}</strong>
            </div>
            <div class="level-item">
              <span class="level-label">Stop Loss:</span>
              <strong class="level-value">${escapeHtml(slValue)}</strong>
            </div>
          </div>
        ` : ''}
        <div class="recommendation-signals">
          <span>${escapeHtml(String(buySignals.length))} Buy Signals</span>
          <span>${escapeHtml(String(sellSignals.length))} Sell Signals</span>
        </div>
      </div>
    `;
  }

  showError(message) {
    this.showNotification(message, 'error');
    logger.error('TechnicalAnalysis', message);
  }
  
  showSuccess(message) {
    this.showNotification(message, 'success');
  }
  
  showWarning(message) {
    this.showNotification(message, 'warning');
  }
  
  showInfo(message) {
    this.showNotification(message, 'info');
  }
  
  showNotification(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `notification ${type}`;
    toast.textContent = message;
    toast.style.cssText = `
      position: fixed;
      top: 20px;
      right: 20px;
      padding: 16px 24px;
      background: linear-gradient(135deg, rgba(15, 23, 42, 0.95), rgba(30, 41, 59, 0.95));
      backdrop-filter: blur(10px);
      border-radius: 8px;
      border-left: 4px solid;
      color: var(--text-strong);
      z-index: 10000;
      box-shadow: 0 8px 32px rgba(0, 0, 0, 0.4);
      min-width: 300px;
      max-width: 500px;
      animation: slideInRight 0.4s cubic-bezier(0.34, 1.56, 0.64, 1);
    `;
    
    if (type === 'success') toast.style.borderLeftColor = '#22c55e';
    else if (type === 'error') toast.style.borderLeftColor = '#ef4444';
    else if (type === 'warning') toast.style.borderLeftColor = '#eab308';
    else toast.style.borderLeftColor = '#3b82f6';
    
    document.body.appendChild(toast);
    
    setTimeout(() => {
      toast.style.animation = 'slideInRight 0.4s ease-out reverse';
      setTimeout(() => toast.remove(), 400);
    }, 5000);
  }
  
  showLoading(message = 'Loading...') {
    const container = document.getElementById(`mode-${this.currentMode}`);
    if (container) {
      container.innerHTML = `
        <div class="loading-state">
          <div class="loading-spinner"></div>
          <p class="loading-message">${message}</p>
        </div>
      `;
    }
  }
  
  hideLoading() {
    // Loading will be replaced by actual content
  }
  
  renderErrorState(mode, error) {
    const container = document.getElementById(`mode-${mode}`);
    if (container) {
      const errorMessage = error && error.message ? escapeHtml(error.message) : 'An unexpected error occurred';
      container.innerHTML = `
        <div class="error-state">
          <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
            <circle cx="12" cy="12" r="10"></circle>
            <line x1="12" y1="8" x2="12" y2="12"></line>
            <line x1="12" y1="16" x2="12.01" y2="16"></line>
          </svg>
          <h3>Analysis Failed</h3>
          <p>${errorMessage}</p>
          <button class="btn btn-primary" onclick="if(window.technicalAnalysisPage){window.technicalAnalysisPage.runCurrentModeAnalysis();}">
            Retry Analysis
          </button>
        </div>
      `;
    }
  }
  
  runCurrentModeAnalysis() {
    this.analyze();
  }
  
  delay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
  
  async fetchWithRetry(url, options = {}, timeout = 15000, retries = 3) {
    for (let i = 0; i < retries; i++) {
      try {
        const response = await apiClient.fetch(url, options, timeout);
        if (response.ok) {
          return response;
        }
        
        if (i < retries - 1 && response.status >= 500) {
          const delayMs = Math.min(this.retryConfig.baseDelay * Math.pow(2, i), this.retryConfig.maxDelay);
          await this.delay(delayMs);
          continue;
        }
        
        return response;
      } catch (error) {
        if (i < retries - 1) {
          const delayMs = Math.min(this.retryConfig.baseDelay * Math.pow(2, i), this.retryConfig.maxDelay);
          await this.delay(delayMs);
          continue;
        }
        throw error;
      }
    }
    throw new Error('Max retries exceeded');
  }
}

export default TechnicalAnalysisPage;

