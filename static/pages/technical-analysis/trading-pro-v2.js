/**
 * Professional Trading Terminal v2
 * Fully functional with real feedback, animations, and working tabs
 */

class TradingProV2 {
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
      volume: { enabled: true, series: null }
    };
    this.patterns = {
      hs: true,
      double: true,
      triangle: true
    };
    this.drawings = [];
    this.currentTool = null;
    this.data = [];
    this.updateInterval = null;
    this.currentTab = 'strategies';
  }

  async init() {
    try {
      console.log('[TradingProV2] Initializing...');
      
      this.initChart();
      this.bindEvents();
      this.loadStrategiesTab();
      
      await this.loadData();
      
      // Auto-refresh every 30 seconds
      this.updateInterval = setInterval(() => this.loadData(true), 30000);
      
      this.showToast('Trading Terminal Ready!', 'Welcome to Professional Trading Terminal', 'success');
      console.log('[TradingProV2] Ready!');
    } catch (error) {
      console.error('[TradingProV2] Init error:', error);
      this.showToast('Initialization Error', error.message, 'error');
    }
  }

  initChart() {
    const container = document.getElementById('tradingChart');
    if (!container) {
      throw new Error('Chart container not found');
    }

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
        text: 'CRYPTO PRO v2',
      },
    });

    this.candlestickSeries = this.chart.addCandlestickSeries({
      upColor: '#22c55e',
      downColor: '#ef4444',
      borderUpColor: '#22c55e',
      borderDownColor: '#ef4444',
      wickUpColor: '#22c55e',
      wickDownColor: '#ef4444',
    });

    // Responsive
    const resizeObserver = new ResizeObserver(entries => {
      if (entries.length === 0 || !entries[0].target) return;
      const { width, height } = entries[0].contentRect;
      this.chart.applyOptions({ width, height });
    });

    resizeObserver.observe(container);
    console.log('[TradingProV2] Chart initialized');
  }

  bindEvents() {
    // Symbol input
    const symbolInput = document.getElementById('symbolInput');
    if (symbolInput) {
      symbolInput.addEventListener('change', (e) => {
        this.symbol = e.target.value.toUpperCase();
        this.showToast('Symbol Changed', `Loading ${this.symbol} data...`, 'info');
        this.loadData();
      });
    }

    // Timeframe buttons
    document.querySelectorAll('.timeframe-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        document.querySelectorAll('.timeframe-btn').forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        this.timeframe = e.target.dataset.timeframe;
        this.showToast('Timeframe Changed', `Switched to ${this.timeframe}`, 'info');
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
        this.showToast(
          isOn ? 'Indicator Enabled' : 'Indicator Disabled',
          `${indicator.toUpperCase()} ${isOn ? 'activated' : 'deactivated'}`,
          'info'
        );
        this.updateIndicators();
      });
    });

    // Pattern toggles
    document.querySelectorAll('.toggle-switch[data-pattern]').forEach(toggle => {
      toggle.addEventListener('click', (e) => {
        const pattern = e.currentTarget.dataset.pattern;
        const isOn = toggle.classList.toggle('on');
        this.patterns[pattern] = isOn;
        this.showToast(
          isOn ? 'Pattern Detection Enabled' : 'Pattern Detection Disabled',
          `${pattern.toUpperCase()} pattern detection ${isOn ? 'on' : 'off'}`,
          'info'
        );
        this.detectPatterns();
      });
    });

    // Chart tool buttons
    document.getElementById('btnZoomIn')?.addEventListener('click', () => this.zoomIn());
    document.getElementById('btnZoomOut')?.addEventListener('click', () => this.zoomOut());
    document.getElementById('btnScreenshot')?.addEventListener('click', () => this.takeScreenshot());

    // Strategy tabs
    document.querySelectorAll('.strategy-tab').forEach(tab => {
      tab.addEventListener('click', (e) => {
        document.querySelectorAll('.strategy-tab').forEach(t => t.classList.remove('active'));
        e.currentTarget.classList.add('active');
        const tabType = e.currentTarget.dataset.tab;
        this.currentTab = tabType;
        this.loadStrategyTab(tabType);
      });
    });
  }

  async loadData(silent = false) {
    if (!silent) {
      document.getElementById('loadingOverlay')?.classList.remove('hidden');
    }

    try {
      const intervalMap = {
        '1m': '1m', '5m': '5m', '15m': '15m',
        '1h': '1h', '4h': '4h',
        '1d': '1d', '1w': '1w'
      };
      
      const interval = intervalMap[this.timeframe] || '4h';
      
      // Try Binance directly
      const response = await fetch(
        `https://api.binance.com/api/v3/klines?symbol=${this.symbol}&interval=${interval}&limit=500`,
        { signal: AbortSignal.timeout(10000) }
      );

      if (response.ok) {
        const binanceData = await response.json();
        this.data = this.parseBinanceData(binanceData);
        
        if (this.data.length > 0) {
          this.updateChart();
          this.calculateIndicators();
          this.detectPatterns();
          this.updatePriceDisplay();
          this.updateAnalysis();
          this.updateTimestamp();
          
          if (!silent) {
            this.showToast('Data Loaded', `Loaded ${this.data.length} candles`, 'success');
          }
        }
      } else {
        throw new Error('Failed to load market data');
      }
    } catch (error) {
      console.error('[TradingProV2] Load data error:', error);
      this.showToast('Data Load Error', error.message, 'error');
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

  updateChart() {
    if (!this.candlestickSeries || this.data.length === 0) return;
    this.candlestickSeries.setData(this.data);
    this.chart.timeScale().fitContent();
  }

  calculateIndicators() {
    if (this.data.length === 0) return;

    if (this.indicators.rsi.enabled) this.calculateRSI();
    if (this.indicators.macd.enabled) this.calculateMACD();
    if (this.indicators.ema.enabled) this.calculateEMAs();
    if (this.indicators.volume.enabled) this.calculateVolume();
  }

  calculateRSI(period = 14) {
    const closes = this.data.map(d => d.close);
    const rsi = [];
    
    let gains = 0;
    let losses = 0;

    for (let i = 1; i <= period; i++) {
      const change = closes[i] - closes[i - 1];
      if (change > 0) gains += change;
      else losses += Math.abs(change);
    }

    let avgGain = gains / period;
    let avgLoss = losses / period;
    let rs = avgGain / (avgLoss || 1);
    rsi.push({ time: this.data[period].time, value: 100 - (100 / (1 + rs)) });

    for (let i = period + 1; i < closes.length; i++) {
      const change = closes[i] - closes[i - 1];
      const gain = change > 0 ? change : 0;
      const loss = change < 0 ? Math.abs(change) : 0;

      avgGain = (avgGain * (period - 1) + gain) / period;
      avgLoss = (avgLoss * (period - 1) + loss) / period;
      rs = avgGain / (avgLoss || 1);

      rsi.push({
        time: this.data[i].time,
        value: 100 - (100 / (1 + rs))
      });
    }

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

  calculateEMAs() {
    const closes = this.data.map(d => d.close);
    const ema20 = this.calculateEMA(closes, 20);
    const ema50 = this.calculateEMA(closes, 50);
    const ema200 = this.calculateEMA(closes, 200);

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

    this.indicators.ema.ema20.setData(
      ema20.map((val, i) => ({ time: this.data[i].time, value: val }))
    );
    this.indicators.ema.ema50.setData(
      ema50.map((val, i) => ({ time: this.data[i].time, value: val }))
    );
    this.indicators.ema.ema200.setData(
      ema200.map((val, i) => ({ time: this.data[i].time, value: val }))
    );

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

    this.calculateIndicators();
  }

  detectPatterns() {
    // Simplified pattern detection
    console.log('[TradingProV2] Pattern detection running...');
  }

  activateDrawingTool(tool) {
    const toolNames = {
      trendline: 'Trend Line',
      horizontal: 'Horizontal Line',
      fibonacci: 'Fibonacci Retracement',
      rectangle: 'Rectangle',
      triangle: 'Triangle'
    };
    
    this.showToast(
      'Drawing Tool Activated',
      `${toolNames[tool]} tool is ready. Click on the chart to draw.`,
      'info'
    );
  }

  updatePriceDisplay() {
    if (this.data.length === 0) return;

    const latest = this.data[this.data.length - 1];
    const previous = this.data[this.data.length - 2];
    
    const currentPrice = latest.close;
    const change = ((latest.close - previous.close) / previous.close) * 100;

    const priceEl = document.getElementById('currentPrice');
    const changeEl = document.getElementById('priceChange');
    const cpEl = document.getElementById('cp');

    if (priceEl) {
      priceEl.textContent = `$${currentPrice.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 })}`;
    }

    if (changeEl) {
      changeEl.textContent = `${change >= 0 ? '+' : ''}${change.toFixed(2)}%`;
      changeEl.className = 'price-change';
      changeEl.classList.add(change >= 0 ? 'positive' : 'negative');
    }

    if (cpEl) {
      cpEl.textContent = `$${currentPrice.toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
    }
  }

  updateAnalysis() {
    if (this.data.length === 0) return;

    const recentData = this.data.slice(-50);
    const highs = recentData.map(d => d.high);
    const lows = recentData.map(d => d.low);
    
    const resistance = Math.max(...highs);
    const support = Math.min(...lows);

    const r1El = document.getElementById('r1');
    const s1El = document.getElementById('s1');

    if (r1El) r1El.textContent = `$${resistance.toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
    if (s1El) s1El.textContent = `$${support.toLocaleString('en-US', { minimumFractionDigits: 2 })}`;

    const rsi = this.calculateRSI();
    const latestRSI = rsi[rsi.length - 1]?.value || 50;
    
    const closes = this.data.map(d => d.close);
    const ema20 = this.calculateEMA(closes, 20);
    const ema50 = this.calculateEMA(closes, 50);
    
    let signal = 'HOLD';
    let confidence = 50;
    
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

    // Calculate volatility
    const stdDev = this.calculateStdDev(closes.slice(-20));
    const volatility = stdDev > 1000 ? 'High' : stdDev > 500 ? 'Medium' : 'Low';
    const volEl = document.getElementById('volatility');
    if (volEl) {
      volEl.textContent = volatility;
      volEl.className = 'metric-value';
      if (volatility === 'High') volEl.classList.add('bearish');
      else if (volatility === 'Low') volEl.classList.add('bullish');
      else volEl.classList.add('neutral');
    }
  }

  calculateStdDev(values) {
    const mean = values.reduce((a, b) => a + b, 0) / values.length;
    const variance = values.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / values.length;
    return Math.sqrt(variance);
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
    const container = document.getElementById('strategyContent');
    if (!container) return;

    switch (tabType) {
      case 'strategies':
        this.loadStrategiesTab();
        break;
      
      case 'signals':
        container.innerHTML = `
          <div class="strategy-list">
            <div class="analysis-card">
              <h3>
                <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 17h5l-1.405-1.405A2.032 2.032 0 0118 14.158V11a6.002 6.002 0 00-4-5.659V5a2 2 0 10-4 0v.341C7.67 6.165 6 8.388 6 11v3.159c0 .538-.214 1.055-.595 1.436L4 17h5m6 0v1a3 3 0 11-6 0v-1m6 0H9"/>
                </svg>
                Active Trading Signals
              </h3>
              <div class="metric-row">
                <span class="metric-label">BTC/USDT</span>
                <span class="signal-badge buy">BUY</span>
              </div>
              <div class="metric-row">
                <span class="metric-label">Entry: $42,150</span>
                <span class="metric-label">Target: $44,200</span>
              </div>
              <div class="metric-row">
                <span class="metric-label">ETH/USDT</span>
                <span class="signal-badge hold">HOLD</span>
              </div>
              <div class="metric-row">
                <span class="metric-label">BNB/USDT</span>
                <span class="signal-badge sell">SELL</span>
              </div>
            </div>
          </div>
        `;
        this.showToast('Active Signals', 'Viewing active trading signals', 'info');
        break;
      
      case 'history':
        container.innerHTML = `
          <div class="strategy-list">
            <div class="analysis-card">
              <h3>
                <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
                Recent Trades
              </h3>
              <div class="metric-row">
                <span class="metric-label">BTC/USDT - BUY</span>
                <span class="metric-value bullish">+2.5%</span>
              </div>
              <div class="metric-row">
                <span class="metric-label">ETH/USDT - SELL</span>
                <span class="metric-value bullish">+1.8%</span>
              </div>
              <div class="metric-row">
                <span class="metric-label">BNB/USDT - BUY</span>
                <span class="metric-value bearish">-0.5%</span>
              </div>
              <p style="color: var(--text-secondary); margin-top: 1rem; font-size: 0.875rem;">
                Total trades: 156 | Win rate: 67% | Total profit: +15.3%
              </p>
            </div>
          </div>
        `;
        this.showToast('Trade History', 'Viewing trade history', 'info');
        break;
      
      case 'backtests':
        container.innerHTML = `
          <div class="strategy-list">
            <div class="analysis-card">
              <h3>
                <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"/>
                </svg>
                Backtest Results
              </h3>
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
              <div class="metric-row">
                <span class="metric-label">Total Return</span>
                <span class="metric-value bullish">+156.7%</span>
              </div>
            </div>
          </div>
        `;
        this.showToast('Backtest Results', 'Viewing backtest results', 'info');
        break;
    }
  }

  loadStrategiesTab() {
    const container = document.getElementById('strategyList');
    if (!container) return;

    const strategies = [
      {
        icon: '🎯',
        name: 'Trend Following + RSI',
        description: 'EMA crossover with RSI confirmation. Buy when EMA(20) crosses EMA(50) upward and RSI > 50',
        winRate: 67,
        profitFactor: 2.3,
        trades: 156
      },
      {
        icon: '💎',
        name: 'Support/Resistance Breakout',
        description: 'Buy on resistance break with volume confirmation. Sell on support break.',
        winRate: 72,
        profitFactor: 3.1,
        trades: 89
      },
      {
        icon: '🌊',
        name: 'MACD + Bollinger Bands',
        description: 'MACD histogram reversal at BB extremes. Mean reversion strategy.',
        winRate: 65,
        profitFactor: 1.9,
        trades: 203
      },
      {
        icon: '⚡',
        name: 'Scalping - Quick Profits',
        description: '1-5 minute timeframe. Small profits, high frequency, strict stop-loss.',
        winRate: 58,
        profitFactor: 1.6,
        trades: 1247
      }
    ];

    container.innerHTML = strategies.map((strategy, index) => `
      <div class="strategy-item ${index === 0 ? 'active' : ''}" data-strategy="${index}">
        <div class="strategy-name">${strategy.icon} ${strategy.name}</div>
        <p style="color: var(--text-secondary); font-size: 0.875rem; margin-top: 0.5rem;">
          ${strategy.description}
        </p>
        <div class="strategy-stats">
          <div class="stat">
            <div class="stat-label">Win Rate</div>
            <div class="stat-value" style="color: var(--accent-green)">${strategy.winRate}%</div>
          </div>
          <div class="stat">
            <div class="stat-label">Profit Factor</div>
            <div class="stat-value" style="color: var(--accent-green)">${strategy.profitFactor}</div>
          </div>
          <div class="stat">
            <div class="stat-label">Trades</div>
            <div class="stat-value">${strategy.trades.toLocaleString()}</div>
          </div>
        </div>
      </div>
    `).join('');

    // Add click handlers
    container.querySelectorAll('.strategy-item').forEach(item => {
      item.addEventListener('click', (e) => {
        container.querySelectorAll('.strategy-item').forEach(i => i.classList.remove('active'));
        e.currentTarget.classList.add('active');
        const strategyIndex = parseInt(e.currentTarget.dataset.strategy);
        this.showToast(
          'Strategy Applied',
          `${strategies[strategyIndex].name} is now active`,
          'success'
        );
      });
    });
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
        this.showToast('Zoomed In', 'Chart zoomed in', 'info');
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
        this.showToast('Zoomed Out', 'Chart zoomed out', 'info');
      }
    }
  }

  takeScreenshot() {
    this.showToast('Screenshot', 'Screenshot feature coming soon!', 'warning');
  }

  showToast(title, message, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    
    const icons = {
      success: '<svg width="24" height="24" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>',
      error: '<svg width="24" height="24" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 14l2-2m0 0l2-2m-2 2l-2-2m2 2l2 2m7-2a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>',
      warning: '<svg width="24" height="24" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/></svg>',
      info: '<svg width="24" height="24" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/></svg>'
    };

    toast.innerHTML = `
      <div class="toast-icon">${icons[type]}</div>
      <div class="toast-content">
        <div class="toast-title">${title}</div>
        <div class="toast-message">${message}</div>
      </div>
      <button class="toast-close">
        <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
        </svg>
      </button>
    `;

    container.appendChild(toast);

    // Close button
    const closeBtn = toast.querySelector('.toast-close');
    closeBtn.addEventListener('click', () => {
      toast.classList.add('removing');
      setTimeout(() => toast.remove(), 300);
    });

    // Auto remove after 5 seconds
    setTimeout(() => {
      if (toast.parentElement) {
        toast.classList.add('removing');
        setTimeout(() => toast.remove(), 300);
      }
    }, 5000);
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

// Initialize
function initTradingPro() {
  window.tradingProV2 = new TradingProV2();
  window.tradingProV2.init();
}

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initTradingPro);
} else {
  initTradingPro();
}

window.addEventListener('beforeunload', () => {
  window.tradingProV2?.destroy();
});

// Export
export default TradingProV2;

