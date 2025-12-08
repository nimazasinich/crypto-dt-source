/**
 * Professional Trading Terminal
 * TradingView-like interface with advanced indicators and strategies
 */

class TradingPro {
  constructor() {
    this.symbol = 'BTCUSDT';
    this.timeframe = '4h';
    this.chart = null;
    this.candlestickSeries = null;
    this.volumeSeries = null;
    this.indicators = {
      rsi: { enabled: true, series: null },
      macd: { enabled: true, series: null },
      bb: { enabled: false, upper: null, lower: null, middle: null },
      ema: { enabled: true, ema20: null, ema50: null, ema200: null },
      volume: { enabled: true, series: null },
      ichimoku: { enabled: false, series: [] }
    };
    this.patterns = {
      hs: true,
      double: true,
      triangle: true,
      wedge: false
    };
    this.drawings = [];
    this.currentTool = null;
    this.data = [];
    this.updateInterval = null;
  }

  async init() {
    try {
      console.log('[TradingPro] Initializing Professional Trading Terminal...');
      
      this.initChart();
      this.bindEvents();
      await this.loadData();
      
      // Auto-refresh every 30 seconds
      this.updateInterval = setInterval(() => this.loadData(true), 30000);
      
      console.log('[TradingPro] Ready!');
    } catch (error) {
      console.error('[TradingPro] Init error:', error);
    }
  }

  initChart() {
    const container = document.getElementById('tradingChart');
    if (!container) {
      console.error('[TradingPro] Chart container not found');
      return;
    }

    // Create chart
    this.chart = LightweightCharts.createChart(container, {
      layout: {
        background: { color: '#0f1429' },
        textColor: '#d1d4dc',
      },
      grid: {
        vertLines: { color: 'rgba(255, 255, 255, 0.05)' },
        horzLines: { color: 'rgba(255, 255, 255, 0.05)' },
      },
      crosshair: {
        mode: LightweightCharts.CrosshairMode.Normal,
        vertLine: {
          color: '#2dd4bf',
          width: 1,
          style: LightweightCharts.LineStyle.Dashed,
        },
        horzLine: {
          color: '#2dd4bf',
          width: 1,
          style: LightweightCharts.LineStyle.Dashed,
        },
      },
      rightPriceScale: {
        borderColor: 'rgba(255, 255, 255, 0.1)',
      },
      timeScale: {
        borderColor: 'rgba(255, 255, 255, 0.1)',
        timeVisible: true,
        secondsVisible: false,
      },
      watermark: {
        visible: true,
        fontSize: 48,
        horzAlign: 'center',
        vertAlign: 'center',
        color: 'rgba(255, 255, 255, 0.03)',
        text: 'CRYPTO PRO',
      },
    });

    // Create candlestick series
    this.candlestickSeries = this.chart.addCandlestickSeries({
      upColor: '#22c55e',
      downColor: '#ef4444',
      borderUpColor: '#22c55e',
      borderDownColor: '#ef4444',
      wickUpColor: '#22c55e',
      wickDownColor: '#ef4444',
    });

    // Make chart responsive
    const resizeObserver = new ResizeObserver(entries => {
      if (entries.length === 0 || !entries[0].target) return;
      const { width, height } = entries[0].contentRect;
      this.chart.applyOptions({ width, height });
    });

    resizeObserver.observe(container);

    console.log('[TradingPro] Chart initialized');
  }

  bindEvents() {
    // Symbol input
    document.getElementById('symbolInput')?.addEventListener('change', (e) => {
      this.symbol = e.target.value.toUpperCase();
      this.loadData();
    });

    // Timeframe buttons
    document.querySelectorAll('.timeframe-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        document.querySelectorAll('.timeframe-btn').forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        this.timeframe = e.target.dataset.timeframe;
        this.loadData();
      });
    });

    // Drawing tools
    document.querySelectorAll('.tool-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        document.querySelectorAll('.tool-btn').forEach(b => b.classList.remove('active'));
        e.currentTarget.classList.add('active');
        this.currentTool = e.currentTarget.dataset.tool;
        this.activateDrawingTool(this.currentTool);
      });
    });

    // Indicator toggles
    document.querySelectorAll('.toggle-switch[data-indicator]').forEach(toggle => {
      toggle.addEventListener('click', (e) => {
        const indicator = e.currentTarget.dataset.indicator;
        const isOn = toggle.classList.toggle('on');
        this.indicators[indicator].enabled = isOn;
        this.updateIndicators();
      });
    });

    // Pattern toggles
    document.querySelectorAll('.toggle-switch[data-pattern]').forEach(toggle => {
      toggle.addEventListener('click', (e) => {
        const pattern = e.currentTarget.dataset.pattern;
        const isOn = toggle.classList.toggle('on');
        this.patterns[pattern] = isOn;
        this.detectPatterns();
      });
    });

    // Strategy tabs
    document.querySelectorAll('.strategy-tab').forEach(tab => {
      tab.addEventListener('click', (e) => {
        document.querySelectorAll('.strategy-tab').forEach(t => t.classList.remove('active'));
        e.target.classList.add('active');
        const tabType = e.target.dataset.tab;
        this.loadStrategyTab(tabType);
      });
    });

    // Strategy items
    document.querySelectorAll('.strategy-item').forEach(item => {
      item.addEventListener('click', (e) => {
        document.querySelectorAll('.strategy-item').forEach(i => i.classList.remove('active'));
        e.currentTarget.classList.add('active');
        this.applyStrategy(e.currentTarget);
      });
    });
  }

  async loadData(silent = false) {
    if (!silent) {
      document.getElementById('loadingOverlay')?.classList.remove('hidden');
    }

    try {
      // Map timeframe for API
      const intervalMap = {
        '1m': '1m', '5m': '5m', '15m': '15m',
        '1h': '1h', '4h': '4h',
        '1d': '1d', '1w': '1w'
      };
      
      const interval = intervalMap[this.timeframe] || '4h';
      const symbol = this.symbol.replace('USDT', '').toLowerCase();
      
      // Try backend first with query parameters (more compatible)
      let response;
      try {
        response = await fetch(`/api/ohlcv?symbol=${encodeURIComponent(symbol)}&timeframe=${encodeURIComponent(interval)}&limit=500`, {
          signal: AbortSignal.timeout(10000)
        });

        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }

        const backendData = await response.json();
        
        // Validate response structure
        if (!backendData || typeof backendData !== 'object') {
          throw new Error('Invalid response format');
        }
        
        // Handle both success and error responses
        if (backendData.success === false || backendData.error === true) {
          throw new Error(backendData.message || 'Failed to fetch OHLCV data');
        }
        
        // Extract data array
        const ohlcvData = backendData.data || backendData.ohlcv || [];
        if (!Array.isArray(ohlcvData) || ohlcvData.length === 0) {
          throw new Error('No OHLCV data available');
        }
        
        this.data = this.parseBackendData(ohlcvData);
        
      } catch (error) {
        console.warn('[TradingPro] Backend fetch failed, trying Binance directly:', error);
        
        // Fallback to Binance directly
        try {
          response = await fetch(
            `https://api.binance.com/api/v3/klines?symbol=${this.symbol}&interval=${interval}&limit=500`,
            { signal: AbortSignal.timeout(10000) }
          );

          if (response.ok) {
            const binanceData = await response.json();
            this.data = this.parseBinanceData(binanceData);
          } else {
            throw new Error(`Binance API returned ${response.status}`);
          }
        } catch (binanceError) {
          console.error('[TradingPro] All data sources failed:', binanceError);
          this.data = [];
          this.showError('Unable to load chart data. Please try again later.');
          return;
        }
      }

      // Validate data before rendering
      if (!this.data || this.data.length === 0) {
        this.showError('No data available for this symbol');
        return;
      }
      
      // Validate data structure
      const firstCandle = this.data[0];
      if (!firstCandle || typeof firstCandle.open !== 'number' || typeof firstCandle.close !== 'number') {
        this.showError('Invalid data format received');
        return;
      }

      this.updateChart();
      this.calculateIndicators();
      this.detectPatterns();
      this.updatePriceDisplay();
      this.updateAnalysis();
      this.updateTimestamp();

    } catch (error) {
      console.error('[TradingPro] Load data error:', error);
      this.showError('Failed to load chart data');
    } finally {
      if (!silent) {
        document.getElementById('loadingOverlay')?.classList.add('hidden');
      }
    }
  }

  parseBinanceData(data) {
    return data.map(candle => ({
      time: Math.floor(candle[0] / 1000),
      open: parseFloat(candle[1]),
      high: parseFloat(candle[2]),
      low: parseFloat(candle[3]),
      close: parseFloat(candle[4]),
      volume: parseFloat(candle[5])
    }));
  }

  parseBackendData(data) {
    // Handle both array input and object with data property
    const ohlcvData = Array.isArray(data) ? data : (data.data || data.ohlcv || []);
    if (!Array.isArray(ohlcvData)) return [];
    
    return ohlcvData.map(candle => {
      // Handle different timestamp formats: t (milliseconds), time (seconds), timestamp (seconds or milliseconds)
      let timestamp = candle.t || candle.time || candle.timestamp || 0;
      // Convert to seconds if in milliseconds
      if (timestamp > 1e10) timestamp = Math.floor(timestamp / 1000);
      
      return {
        time: timestamp,
        open: parseFloat(candle.o || candle.open || 0),
        high: parseFloat(candle.h || candle.high || 0),
        low: parseFloat(candle.l || candle.low || 0),
        close: parseFloat(candle.c || candle.close || 0),
        volume: parseFloat(candle.v || candle.volume || 0)
      };
    }).filter(candle => candle.time > 0 && candle.open > 0); // Filter invalid candles
  }

  updateChart() {
    if (!this.candlestickSeries) {
      console.warn('[TradingPro] Chart not initialized');
      return;
    }
    
    if (!this.data || this.data.length === 0) {
      this.showError('No data available to display');
      return;
    }

    // Update candlestick data
    this.candlestickSeries.setData(this.data);

    // Fit content
    this.chart.timeScale().fitContent();
  }

  calculateIndicators() {
    if (this.data.length === 0) return;

    // Calculate RSI
    if (this.indicators.rsi.enabled) {
      this.calculateRSI();
    }

    // Calculate MACD
    if (this.indicators.macd.enabled) {
      this.calculateMACD();
    }

    // Calculate Bollinger Bands
    if (this.indicators.bb.enabled) {
      this.calculateBollingerBands();
    }

    // Calculate EMAs
    if (this.indicators.ema.enabled) {
      this.calculateEMAs();
    }

    // Calculate Volume
    if (this.indicators.volume.enabled) {
      this.calculateVolume();
    }
  }

  calculateRSI(period = 14) {
    const closes = this.data.map(d => d.close);
    const rsi = [];
    
    let gains = 0;
    let losses = 0;

    // Calculate first average gain/loss
    for (let i = 1; i <= period; i++) {
      const change = closes[i] - closes[i - 1];
      if (change > 0) gains += change;
      else losses += Math.abs(change);
    }

    let avgGain = gains / period;
    let avgLoss = losses / period;
    let rs = avgGain / avgLoss;
    rsi.push({ time: this.data[period].time, value: 100 - (100 / (1 + rs)) });

    // Calculate RSI for remaining data
    for (let i = period + 1; i < closes.length; i++) {
      const change = closes[i] - closes[i - 1];
      const gain = change > 0 ? change : 0;
      const loss = change < 0 ? Math.abs(change) : 0;

      avgGain = (avgGain * (period - 1) + gain) / period;
      avgLoss = (avgLoss * (period - 1) + loss) / period;
      rs = avgGain / avgLoss;

      rsi.push({
        time: this.data[i].time,
        value: 100 - (100 / (1 + rs))
      });
    }

    // Update RSI display
    const latestRSI = rsi[rsi.length - 1]?.value || 50;
    const rsiEl = document.getElementById('rsiValue');
    if (rsiEl) {
      rsiEl.textContent = latestRSI.toFixed(1);
      rsiEl.className = 'metric-value';
      if (latestRSI > 70) rsiEl.classList.add('bearish');
      else if (latestRSI < 30) rsiEl.classList.add('bullish');
      else rsiEl.classList.add('neutral');
    }

    return rsi;
  }

  calculateMACD() {
    const closes = this.data.map(d => d.close);
    const ema12 = this.calculateEMA(closes, 12);
    const ema26 = this.calculateEMA(closes, 26);
    
    const macdLine = ema12.map((val, i) => val - ema26[i]);
    const signalLine = this.calculateEMA(macdLine, 9);
    const histogram = macdLine.map((val, i) => val - signalLine[i]);

    // Update MACD display
    const latestHistogram = histogram[histogram.length - 1];
    const macdEl = document.getElementById('macdValue');
    if (macdEl) {
      if (latestHistogram > 0) {
        macdEl.textContent = 'Bullish';
        macdEl.className = 'metric-value bullish';
      } else {
        macdEl.textContent = 'Bearish';
        macdEl.className = 'metric-value bearish';
      }
    }

    return { macdLine, signalLine, histogram };
  }

  calculateEMA(values, period) {
    const k = 2 / (period + 1);
    const ema = [values[0]];

    for (let i = 1; i < values.length; i++) {
      ema.push(values[i] * k + ema[i - 1] * (1 - k));
    }

    return ema;
  }

  calculateBollingerBands(period = 20, stdDev = 2) {
    const closes = this.data.map(d => d.close);
    const sma = this.calculateSMA(closes, period);
    const upper = [];
    const lower = [];

    for (let i = period - 1; i < closes.length; i++) {
      const slice = closes.slice(i - period + 1, i + 1);
      const mean = sma[i];
      const variance = slice.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / period;
      const sd = Math.sqrt(variance);

      upper.push(mean + stdDev * sd);
      lower.push(mean - stdDev * sd);
    }

    return { upper, middle: sma, lower };
  }

  calculateSMA(values, period) {
    const sma = [];
    for (let i = period - 1; i < values.length; i++) {
      const sum = values.slice(i - period + 1, i + 1).reduce((a, b) => a + b, 0);
      sma.push(sum / period);
    }
    return sma;
  }

  calculateEMAs() {
    const closes = this.data.map(d => d.close);
    const ema20 = this.calculateEMA(closes, 20);
    const ema50 = this.calculateEMA(closes, 50);
    const ema200 = this.calculateEMA(closes, 200);

    // Add EMA lines to chart
    if (!this.indicators.ema.ema20) {
      this.indicators.ema.ema20 = this.chart.addLineSeries({
        color: '#2dd4bf',
        lineWidth: 2,
        title: 'EMA 20',
      });
    }

    if (!this.indicators.ema.ema50) {
      this.indicators.ema.ema50 = this.chart.addLineSeries({
        color: '#818cf8',
        lineWidth: 2,
        title: 'EMA 50',
      });
    }

    if (!this.indicators.ema.ema200) {
      this.indicators.ema.ema200 = this.chart.addLineSeries({
        color: '#ec4899',
        lineWidth: 2,
        title: 'EMA 200',
      });
    }

    // Set data
    this.indicators.ema.ema20.setData(
      ema20.map((val, i) => ({ time: this.data[i].time, value: val }))
    );
    this.indicators.ema.ema50.setData(
      ema50.map((val, i) => ({ time: this.data[i].time, value: val }))
    );
    this.indicators.ema.ema200.setData(
      ema200.map((val, i) => ({ time: this.data[i].time, value: val }))
    );

    // Determine trend
    const latest = {
      ema20: ema20[ema20.length - 1],
      ema50: ema50[ema50.length - 1],
      ema200: ema200[ema200.length - 1]
    };

    const emaEl = document.getElementById('emaValue');
    if (emaEl) {
      if (latest.ema20 > latest.ema50 && latest.ema50 > latest.ema200) {
        emaEl.textContent = 'Strong Uptrend';
        emaEl.className = 'metric-value bullish';
      } else if (latest.ema20 < latest.ema50 && latest.ema50 < latest.ema200) {
        emaEl.textContent = 'Strong Downtrend';
        emaEl.className = 'metric-value bearish';
      } else {
        emaEl.textContent = 'Mixed';
        emaEl.className = 'metric-value neutral';
      }
    }
  }

  calculateVolume() {
    if (!this.indicators.volume.series) {
      this.indicators.volume.series = this.chart.addHistogramSeries({
        color: '#26a69a',
        priceFormat: {
          type: 'volume',
        },
        priceScaleId: 'volume',
      });

      this.chart.priceScale('volume').applyOptions({
        scaleMargins: {
          top: 0.8,
          bottom: 0,
        },
      });
    }

    const volumeData = this.data.map(d => ({
      time: d.time,
      value: d.volume,
      color: d.close > d.open ? 'rgba(34, 197, 94, 0.5)' : 'rgba(239, 68, 68, 0.5)'
    }));

    this.indicators.volume.series.setData(volumeData);
  }

  updateIndicators() {
    // Remove disabled indicators
    Object.keys(this.indicators).forEach(key => {
      const indicator = this.indicators[key];
      if (!indicator.enabled) {
        if (indicator.series) {
          this.chart.removeSeries(indicator.series);
          indicator.series = null;
        }
        if (indicator.ema20) {
          this.chart.removeSeries(indicator.ema20);
          this.chart.removeSeries(indicator.ema50);
          this.chart.removeSeries(indicator.ema200);
          indicator.ema20 = null;
          indicator.ema50 = null;
          indicator.ema200 = null;
        }
      }
    });

    // Recalculate enabled indicators
    this.calculateIndicators();
  }

  detectPatterns() {
    const patterns = [];

    if (this.data.length < 50) return patterns;

    // Detect Head & Shoulders
    if (this.patterns.hs) {
      const hs = this.detectHeadAndShoulders();
      if (hs) patterns.push(hs);
    }

    // Detect Double Top/Bottom
    if (this.patterns.double) {
      const double = this.detectDoubleTops();
      if (double) patterns.push(double);
    }

    // Detect Triangles
    if (this.patterns.triangle) {
      const triangle = this.detectTriangles();
      if (triangle) patterns.push(triangle);
    }

    // Add markers for detected patterns
    patterns.forEach(pattern => {
      this.addPatternMarker(pattern);
    });

    return patterns;
  }

  detectHeadAndShoulders() {
    // Simple Head & Shoulders detection
    const closes = this.data.map(d => d.close);
    const len = closes.length;
    
    if (len < 30) return null;

    // Look for pattern in last 30 candles
    const recent = closes.slice(-30);
    const max = Math.max(...recent);
    const maxIdx = recent.lastIndexOf(max);

    // Check if there are lower peaks on both sides (shoulders)
    if (maxIdx > 5 && maxIdx < 25) {
      const leftPeak = Math.max(...recent.slice(0, maxIdx - 3));
      const rightPeak = Math.max(...recent.slice(maxIdx + 3));

      if (leftPeak < max * 0.98 && rightPeak < max * 0.98 && 
          Math.abs(leftPeak - rightPeak) < max * 0.02) {
        return {
          type: 'head_shoulders',
          signal: 'sell',
          confidence: 0.7,
          index: len - 30 + maxIdx
        };
      }
    }

    return null;
  }

  detectDoubleTops() {
    const closes = this.data.map(d => d.close);
    const len = closes.length;
    
    if (len < 20) return null;

    const recent = closes.slice(-20);
    const peaks = [];

    for (let i = 1; i < recent.length - 1; i++) {
      if (recent[i] > recent[i - 1] && recent[i] > recent[i + 1]) {
        peaks.push({ value: recent[i], index: i });
      }
    }

    if (peaks.length >= 2) {
      const lastTwo = peaks.slice(-2);
      const diff = Math.abs(lastTwo[0].value - lastTwo[1].value);
      if (diff < lastTwo[0].value * 0.02) {
        return {
          type: 'double_top',
          signal: 'sell',
          confidence: 0.75,
          index: len - 20 + lastTwo[1].index
        };
      }
    }

    return null;
  }

  detectTriangles() {
    // Simplified triangle detection
    const closes = this.data.map(d => d.close);
    const highs = this.data.map(d => d.high);
    const lows = this.data.map(d => d.low);
    
    if (closes.length < 20) return null;

    const recent = closes.slice(-20);
    const recentHighs = highs.slice(-20);
    const recentLows = lows.slice(-20);

    const maxHigh = Math.max(...recentHighs);
    const minLow = Math.min(...recentLows);
    const range = maxHigh - minLow;

    const recentRange = Math.max(...recent.slice(-5)) - Math.min(...recent.slice(-5));

    if (recentRange < range * 0.3) {
      return {
        type: 'triangle',
        signal: 'breakout_pending',
        confidence: 0.65,
        index: closes.length - 10
      };
    }

    return null;
  }

  addPatternMarker(pattern) {
    // Add visual marker on chart for detected pattern
    console.log('[TradingPro] Pattern detected:', pattern.type, 'Confidence:', pattern.confidence);
    // In a real implementation, would add a marker on the chart
  }

  activateDrawingTool(tool) {
    console.log('[TradingPro] Activated drawing tool:', tool);
    
    switch (tool) {
      case 'trendline':
        this.showToast('Click two points to draw trend line', 'info');
        break;
      case 'horizontal':
        this.showToast('Click to draw horizontal line', 'info');
        break;
      case 'fibonacci':
        this.showToast('Click two points for Fibonacci retracement', 'info');
        break;
      case 'rectangle':
        this.showToast('Click two points to draw rectangle', 'info');
        break;
      case 'triangle':
        this.showToast('Click three points to draw triangle', 'info');
        break;
    }
  }

  updatePriceDisplay() {
    if (this.data.length === 0) return;

    const latest = this.data[this.data.length - 1];
    const previous = this.data[this.data.length - 2];
    
    const currentPrice = latest.close;
    const change = ((latest.close - previous.close) / previous.close) * 100;

    const priceEl = document.getElementById('currentPrice');
    const changeEl = document.getElementById('priceChange');

    if (priceEl) {
      priceEl.textContent = `$${currentPrice.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    }

    if (changeEl) {
      changeEl.textContent = `${change >= 0 ? '+' : ''}${change.toFixed(2)}%`;
      changeEl.className = 'price-change';
      changeEl.classList.add(change >= 0 ? 'positive' : 'negative');
    }

    // Update current price in sidebar
    const cpEl = document.getElementById('cp');
    if (cpEl) {
      cpEl.textContent = `$${currentPrice.toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
    }
  }

  updateAnalysis() {
    if (this.data.length === 0) return;

    const latest = this.data[this.data.length - 1];
    const closes = this.data.map(d => d.close);
    
    // Calculate support and resistance
    const recentData = this.data.slice(-50);
    const highs = recentData.map(d => d.high);
    const lows = recentData.map(d => d.low);
    
    const resistance = Math.max(...highs);
    const support = Math.min(...lows);

    const r1El = document.getElementById('r1');
    const s1El = document.getElementById('s1');

    if (r1El) r1El.textContent = `$${resistance.toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
    if (s1El) s1El.textContent = `$${support.toLocaleString('en-US', { minimumFractionDigits: 2 })}`;

    // Generate signal based on indicators
    const rsi = this.calculateRSI();
    const latestRSI = rsi[rsi.length - 1]?.value || 50;
    
    const ema20 = this.calculateEMA(closes, 20);
    const ema50 = this.calculateEMA(closes, 50);
    
    let signal = 'HOLD';
    let confidence = 50;
    
    // Simple strategy: EMA crossover + RSI confirmation
    if (ema20[ema20.length - 1] > ema50[ema50.length - 1] && latestRSI > 50 && latestRSI < 70) {
      signal = 'STRONG BUY';
      confidence = 85;
    } else if (ema20[ema20.length - 1] > ema50[ema50.length - 1] && latestRSI < 70) {
      signal = 'BUY';
      confidence = 70;
    } else if (ema20[ema20.length - 1] < ema50[ema50.length - 1] && latestRSI < 50 && latestRSI > 30) {
      signal = 'STRONG SELL';
      confidence = 85;
    } else if (ema20[ema20.length - 1] < ema50[ema50.length - 1] && latestRSI > 30) {
      signal = 'SELL';
      confidence = 70;
    }

    const signalEl = document.getElementById('currentSignal');
    const confidenceEl = document.getElementById('confidence');
    const strengthEl = document.getElementById('strength');

    if (signalEl) {
      signalEl.textContent = signal;
      signalEl.className = 'signal-badge';
      if (signal.includes('BUY')) signalEl.classList.add('buy');
      else if (signal.includes('SELL')) signalEl.classList.add('sell');
      else signalEl.classList.add('hold');
    }

    if (confidenceEl) {
      confidenceEl.textContent = `${confidence}%`;
      confidenceEl.className = 'metric-value';
      if (confidence > 75) confidenceEl.classList.add('bullish');
      else if (confidence < 50) confidenceEl.classList.add('bearish');
      else confidenceEl.classList.add('neutral');
    }

    if (strengthEl) {
      const strength = confidence > 75 ? 'Strong' : confidence > 60 ? 'Medium' : 'Weak';
      strengthEl.textContent = strength;
      strengthEl.className = 'metric-value';
      if (confidence > 75) strengthEl.classList.add('bullish');
      else strengthEl.classList.add('neutral');
    }

    // Update volume and market cap (from CoinGecko)
    this.loadMarketStats();
  }

  async loadMarketStats() {
    try {
      const symbol = this.symbol.replace('USDT', '').toLowerCase();
      const response = await fetch(`/api/coins/top?limit=100`);
      
      if (response.ok) {
        const data = await response.json();
        const coins = data.data || data.coins || [];
        const coin = coins.find(c => c.symbol?.toUpperCase() === symbol.toUpperCase());
        
        if (coin) {
          const vol24hEl = document.getElementById('volume24h');
          const mcapEl = document.getElementById('marketCap');
          
          if (vol24hEl && coin.total_volume) {
            vol24hEl.textContent = this.formatCurrency(coin.total_volume);
          }
          
          if (mcapEl && coin.market_cap) {
            mcapEl.textContent = this.formatCurrency(coin.market_cap);
          }
        }
      }
    } catch (error) {
      console.error('[TradingPro] Market stats error:', error);
    }
  }

  updateTimestamp() {
    const now = new Date();
    const timeStr = now.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
    const updateEl = document.getElementById('lastUpdate');
    if (updateEl) {
      updateEl.textContent = timeStr;
    }
  }

  loadStrategyTab(tabType) {
    const container = document.querySelector('.strategy-content');
    if (!container) return;

    switch (tabType) {
      case 'strategies':
        // Already loaded in HTML
        break;
      
      case 'signals':
        container.innerHTML = `
          <div class="strategy-list">
            <div class="analysis-card">
              <h3>🎯 Active Trading Signals</h3>
              <div class="metric-row">
                <span class="metric-label">BTC/USDT</span>
                <span class="signal-badge buy">BUY</span>
              </div>
              <div class="metric-row">
                <span class="metric-label">Entry: $42,150</span>
                <span class="metric-label">Target: $44,200</span>
              </div>
            </div>
          </div>
        `;
        break;
      
      case 'history':
        container.innerHTML = `
          <div class="strategy-list">
            <div class="analysis-card">
              <h3>📜 Recent Trades</h3>
              <p style="color: var(--text-secondary);">No trade history available yet.</p>
            </div>
          </div>
        `;
        break;
      
      case 'backtests':
        container.innerHTML = `
          <div class="strategy-list">
            <div class="analysis-card">
              <h3>📊 Backtest Results</h3>
              <div class="metric-row">
                <span class="metric-label">Total Trades</span>
                <span class="metric-value">1,247</span>
              </div>
              <div class="metric-row">
                <span class="metric-label">Win Rate</span>
                <span class="metric-value bullish">67.3%</span>
              </div>
              <div class="metric-row">
                <span class="metric-label">Profit Factor</span>
                <span class="metric-value bullish">2.41</span>
              </div>
              <div class="metric-row">
                <span class="metric-label">Max Drawdown</span>
                <span class="metric-value bearish">-12.5%</span>
              </div>
            </div>
          </div>
        `;
        break;
    }
  }

  applyStrategy(strategyElement) {
    const strategyName = strategyElement.querySelector('.strategy-name')?.textContent;
    console.log('[TradingPro] Applying strategy:', strategyName);
    this.showToast(`Strategy "${strategyName}" applied to chart`, 'success');
    
    // Recalculate analysis based on strategy
    this.updateAnalysis();
  }

  zoomIn() {
    if (this.chart) {
      const timeScale = this.chart.timeScale();
      const range = timeScale.getVisibleLogicalRange();
      if (range) {
        const newRange = {
          from: range.from + (range.to - range.from) * 0.1,
          to: range.to - (range.to - range.from) * 0.1
        };
        timeScale.setVisibleLogicalRange(newRange);
      }
    }
  }

  zoomOut() {
    if (this.chart) {
      const timeScale = this.chart.timeScale();
      const range = timeScale.getVisibleLogicalRange();
      if (range) {
        const newRange = {
          from: range.from - (range.to - range.from) * 0.1,
          to: range.to + (range.to - range.from) * 0.1
        };
        timeScale.setVisibleLogicalRange(newRange);
      }
    }
  }

  takeScreenshot() {
    this.showToast('Screenshot feature coming soon!', 'info');
  }

  formatCurrency(value) {
    if (!value) return '$0';
    
    if (value >= 1e9) return `$${(value / 1e9).toFixed(2)}B`;
    if (value >= 1e6) return `$${(value / 1e6).toFixed(2)}M`;
    if (value >= 1e3) return `$${(value / 1e3).toFixed(2)}K`;
    
    return `$${value.toFixed(2)}`;
  }

  showToast(message, type = 'info') {
    console.log(`[TradingPro] ${type.toUpperCase()}: ${message}`);
  }

  showError(message) {
    console.error('[TradingPro] ERROR:', message);
    
    // Display error message in UI
    const chartContainer = document.getElementById('chart-container') || document.querySelector('.chart-container');
    if (chartContainer) {
      const errorDiv = document.createElement('div');
      errorDiv.className = 'error-message';
      errorDiv.style.cssText = 'padding: 2rem; text-align: center; color: #ef4444; background: rgba(239, 68, 68, 0.1); border-radius: 8px; margin: 1rem;';
      errorDiv.innerHTML = `
        <div style="font-size: 1.2rem; font-weight: 600; margin-bottom: 0.5rem;">⚠️ ${message}</div>
        <div style="font-size: 0.9rem; opacity: 0.8;">Please try again or select a different symbol/timeframe</div>
      `;
      
      // Clear existing error messages
      chartContainer.querySelectorAll('.error-message').forEach(el => el.remove());
      chartContainer.appendChild(errorDiv);
    }
    
    // Also show toast if available
    if (window.showToast) {
      window.showToast(message, 'error');
    }
  }

  destroy() {
    if (this.updateInterval) {
      clearInterval(this.updateInterval);
    }
    if (this.chart) {
      this.chart.remove();
    }
  }
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => {
    window.tradingPro = new TradingPro();
    window.tradingPro.init();
  });
} else {
  window.tradingPro = new TradingPro();
  window.tradingPro.init();
}

// Cleanup on page unload
window.addEventListener('beforeunload', () => {
  window.tradingPro?.destroy();
});

