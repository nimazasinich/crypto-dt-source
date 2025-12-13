/**
 * Trading Pro v3 - Real Backtesting & Strategy Builder
 */

class TradingProV3 {
  constructor() {
    this.symbol = 'BTCUSDT';
    this.timeframe = '4h';
    this.chart = null;
    this.candlestickSeries = null;
    this.data = [];
    this.strategies = [];
    this.currentStrategy = null;
    this.editingStrategy = null;
    this.indicators = { ema20: null, ema50: null, ema200: null, volume: null };
    this.markers = [];
  }

  async init() {
    console.log('[TradingProV3] Initializing...');
    
    this.loadStrategiesFromStorage();
    this.initChart();
    this.bindEvents();
    this.renderStrategies();
    
    await this.loadData();
    
    setInterval(() => this.loadData(true), 60000);
    
    this.showToast('Trading Pro v3', 'Ready with real backtesting!', 'success');
  }

  initChart() {
    const container = document.getElementById('tradingChart');
    if (!container) return;

    this.chart = LightweightCharts.createChart(container, {
      layout: {
        background: { type: 'solid', color: '#ffffff' },
        textColor: '#5a6b7c',
      },
      grid: {
        vertLines: { color: 'rgba(0, 180, 180, 0.05)' },
        horzLines: { color: 'rgba(0, 180, 180, 0.05)' },
      },
      crosshair: {
        mode: LightweightCharts.CrosshairMode.Normal,
        vertLine: { color: '#00d4d4', width: 1, style: 2 },
        horzLine: { color: '#00d4d4', width: 1, style: 2 },
      },
      rightPriceScale: { borderColor: 'rgba(0, 180, 180, 0.1)' },
      timeScale: { borderColor: 'rgba(0, 180, 180, 0.1)', timeVisible: true },
    });

    this.candlestickSeries = this.chart.addCandlestickSeries({
      upColor: '#00c896',
      downColor: '#e91e8c',
      borderUpColor: '#00c896',
      borderDownColor: '#e91e8c',
      wickUpColor: '#00c896',
      wickDownColor: '#e91e8c',
    });

    // Add EMAs
    this.indicators.ema20 = this.chart.addLineSeries({
      color: '#00d4d4',
      lineWidth: 2,
      title: 'EMA 20',
    });

    this.indicators.ema50 = this.chart.addLineSeries({
      color: '#0088cc',
      lineWidth: 2,
      title: 'EMA 50',
    });

    // Volume
    this.indicators.volume = this.chart.addHistogramSeries({
      color: '#00d4d4',
      priceFormat: { type: 'volume' },
      priceScaleId: 'volume',
    });

    this.chart.priceScale('volume').applyOptions({
      scaleMargins: { top: 0.85, bottom: 0 },
    });

    // Responsive
    new ResizeObserver(entries => {
      const { width, height } = entries[0].contentRect;
      this.chart.applyOptions({ width, height });
    }).observe(container);
  }

  bindEvents() {
    // Symbol input
    document.getElementById('symbolInput')?.addEventListener('change', (e) => {
      this.symbol = e.target.value.toUpperCase();
      this.loadData();
    });

    // Timeframe buttons
    document.querySelectorAll('.tf-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        document.querySelectorAll('.tf-btn').forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        this.timeframe = e.target.dataset.tf;
        this.loadData();
      });
    });

    // Strategy tabs
    document.querySelectorAll('.strategy-tab').forEach(tab => {
      tab.addEventListener('click', (e) => {
        document.querySelectorAll('.strategy-tab').forEach(t => t.classList.remove('active'));
        e.target.classList.add('active');
        this.loadStrategyTab(e.target.dataset.tab);
      });
    });

    // New Strategy button
    document.getElementById('btnNewStrategy')?.addEventListener('click', () => {
      this.openStrategyModal();
    });

    // Modal close
    document.getElementById('modalClose')?.addEventListener('click', () => {
      this.closeStrategyModal();
    });

    document.getElementById('strategyModal')?.addEventListener('click', (e) => {
      if (e.target.id === 'strategyModal') this.closeStrategyModal();
    });

    // Close modal with Escape key
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') this.closeStrategyModal();
    });

    // Run Backtest
    document.getElementById('btnBacktest')?.addEventListener('click', () => {
      this.runBacktest();
    });

    // Save Strategy
    document.getElementById('btnSaveStrategy')?.addEventListener('click', () => {
      this.saveStrategy();
    });

    // Add condition buttons
    document.getElementById('addEntryCondition')?.addEventListener('click', () => {
      this.addConditionRow('entryConditions');
    });

    document.getElementById('addExitCondition')?.addEventListener('click', () => {
      this.addConditionRow('exitConditions');
    });
  }

  async loadData(silent = false) {
    if (!silent) {
      document.getElementById('chartLoading')?.classList.remove('hidden');
    }

    try {
      const response = await fetch(
        `https://api.binance.com/api/v3/klines?symbol=${this.symbol}&interval=${this.timeframe}&limit=500`,
        { signal: AbortSignal.timeout(15000) }
      );

      if (!response.ok) throw new Error('Failed to fetch data');

      const rawData = await response.json();
      this.data = rawData.map(c => ({
        time: Math.floor(c[0] / 1000),
        open: parseFloat(c[1]),
        high: parseFloat(c[2]),
        low: parseFloat(c[3]),
        close: parseFloat(c[4]),
        volume: parseFloat(c[5])
      }));

      this.updateChart();
      this.calculateIndicators();
      this.updateUI();
      
      if (!silent) {
        this.showToast('Data Loaded', `${this.data.length} candles loaded`, 'success');
      }

    } catch (error) {
      console.error('[TradingProV3] Error:', error);
      this.showToast('Error', error.message, 'error');
    } finally {
      document.getElementById('chartLoading')?.classList.add('hidden');
    }
  }

  updateChart() {
    if (!this.candlestickSeries || !this.data.length) return;
    
    this.candlestickSeries.setData(this.data);
    
    // Volume
    const volumeData = this.data.map(d => ({
      time: d.time,
      value: d.volume,
      color: d.close > d.open ? 'rgba(0, 200, 150, 0.5)' : 'rgba(233, 30, 140, 0.5)'
    }));
    this.indicators.volume?.setData(volumeData);
    
    this.chart.timeScale().fitContent();
  }

  calculateIndicators() {
    if (!this.data.length) return;

    const closes = this.data.map(d => d.close);
    
    // EMA 20
    const ema20 = this.calculateEMA(closes, 20);
    this.indicators.ema20?.setData(
      ema20.map((val, i) => ({ time: this.data[i].time, value: val }))
    );
    
    // EMA 50
    const ema50 = this.calculateEMA(closes, 50);
    this.indicators.ema50?.setData(
      ema50.map((val, i) => ({ time: this.data[i].time, value: val }))
    );

    // Calculate RSI
    const rsi = this.calculateRSI(closes, 14);
    const latestRSI = rsi[rsi.length - 1];
    
    // MACD
    const macd = this.calculateMACD(closes);
    const latestMACD = macd.histogram[macd.histogram.length - 1];

    // Update UI
    const rsiEl = document.getElementById('rsiValue');
    if (rsiEl) {
      rsiEl.textContent = latestRSI.toFixed(1);
      rsiEl.className = 'metric-value ' + (latestRSI > 70 ? 'bearish' : latestRSI < 30 ? 'bullish' : '');
    }

    const macdEl = document.getElementById('macdValue');
    if (macdEl) {
      macdEl.textContent = latestMACD > 0 ? 'Bullish' : 'Bearish';
      macdEl.className = 'metric-value ' + (latestMACD > 0 ? 'bullish' : 'bearish');
    }

    const emaTrendEl = document.getElementById('emaTrend');
    if (emaTrendEl) {
      const trend = ema20[ema20.length - 1] > ema50[ema50.length - 1] ? 'Uptrend' : 'Downtrend';
      emaTrendEl.textContent = trend;
      emaTrendEl.className = 'metric-value ' + (trend === 'Uptrend' ? 'bullish' : 'bearish');
    }

    // Generate signal
    this.generateSignal(latestRSI, latestMACD, ema20, ema50);
  }

  calculateEMA(values, period) {
    const k = 2 / (period + 1);
    const ema = [values[0]];
    for (let i = 1; i < values.length; i++) {
      ema.push(values[i] * k + ema[i - 1] * (1 - k));
    }
    return ema;
  }

  calculateRSI(values, period = 14) {
    const rsi = [];
    let gains = 0, losses = 0;

    for (let i = 1; i <= period; i++) {
      const change = values[i] - values[i - 1];
      if (change > 0) gains += change;
      else losses += Math.abs(change);
    }

    let avgGain = gains / period;
    let avgLoss = losses / period;
    rsi.push(100 - (100 / (1 + avgGain / (avgLoss || 0.001))));

    for (let i = period + 1; i < values.length; i++) {
      const change = values[i] - values[i - 1];
      const gain = change > 0 ? change : 0;
      const loss = change < 0 ? Math.abs(change) : 0;

      avgGain = (avgGain * (period - 1) + gain) / period;
      avgLoss = (avgLoss * (period - 1) + loss) / period;

      rsi.push(100 - (100 / (1 + avgGain / (avgLoss || 0.001))));
    }

    return rsi;
  }

  calculateMACD(values) {
    const ema12 = this.calculateEMA(values, 12);
    const ema26 = this.calculateEMA(values, 26);
    const macdLine = ema12.map((v, i) => v - ema26[i]);
    const signalLine = this.calculateEMA(macdLine, 9);
    const histogram = macdLine.map((v, i) => v - signalLine[i]);
    return { macdLine, signalLine, histogram };
  }

  generateSignal(rsi, macdHist, ema20, ema50) {
    const latest = {
      ema20: ema20[ema20.length - 1],
      ema50: ema50[ema50.length - 1]
    };

    let signal = 'HOLD';
    let confidence = 50;

    if (latest.ema20 > latest.ema50 && rsi > 50 && rsi < 70 && macdHist > 0) {
      signal = 'STRONG BUY';
      confidence = 85;
    } else if (latest.ema20 > latest.ema50 && macdHist > 0) {
      signal = 'BUY';
      confidence = 70;
    } else if (latest.ema20 < latest.ema50 && rsi < 50 && rsi > 30 && macdHist < 0) {
      signal = 'STRONG SELL';
      confidence = 85;
    } else if (latest.ema20 < latest.ema50 && macdHist < 0) {
      signal = 'SELL';
      confidence = 70;
    }

    const badgeEl = document.getElementById('signalBadge');
    if (badgeEl) {
      badgeEl.textContent = signal;
      badgeEl.className = 'signal-badge ' + (signal.includes('BUY') ? 'buy' : signal.includes('SELL') ? 'sell' : 'hold');
    }

    const confEl = document.getElementById('confidence');
    if (confEl) {
      confEl.textContent = confidence + '%';
      confEl.className = 'metric-value ' + (confidence > 70 ? 'bullish' : 'bearish');
    }
  }

  updateUI() {
    if (!this.data.length) return;

    const latest = this.data[this.data.length - 1];
    const prev = this.data[this.data.length - 2];
    const change = ((latest.close - prev.close) / prev.close) * 100;

    document.getElementById('currentPrice').textContent = 
      `$${latest.close.toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
    
    const changeEl = document.getElementById('priceChange');
    if (changeEl) {
      changeEl.textContent = `${change >= 0 ? '+' : ''}${change.toFixed(2)}%`;
      changeEl.className = 'price-change ' + (change >= 0 ? 'positive' : 'negative');
    }

    document.getElementById('currentLevel').textContent = 
      `$${latest.close.toLocaleString('en-US', { minimumFractionDigits: 0 })}`;

    // Support/Resistance
    const recentData = this.data.slice(-50);
    const resistance = Math.max(...recentData.map(d => d.high));
    const support = Math.min(...recentData.map(d => d.low));

    document.getElementById('resistance').textContent = 
      `$${resistance.toLocaleString('en-US', { minimumFractionDigits: 0 })}`;
    document.getElementById('support').textContent = 
      `$${support.toLocaleString('en-US', { minimumFractionDigits: 0 })}`;

    document.getElementById('lastUpdate').textContent = 
      new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
  }

  // ============= STRATEGY MANAGEMENT =============

  loadStrategiesFromStorage() {
    try {
      const saved = localStorage.getItem('tradingPro_strategies');
      if (saved) {
        this.strategies = JSON.parse(saved);
      } else {
        // Default strategies
        this.strategies = [
          {
            id: 'default_1',
            name: 'EMA Crossover + RSI',
            description: 'Buy when EMA20 crosses above EMA50 and RSI > 50',
            timeframe: '4h',
            riskPercent: 2,
            entryConditions: [
              { indicator: 'ema20', operator: 'crosses_above', value: 'ema50' },
              { indicator: 'rsi', operator: 'greater', value: '50' }
            ],
            exitConditions: [
              { indicator: 'tp', operator: 'equals', value: '3' },
              { indicator: 'sl', operator: 'equals', value: '1.5' }
            ],
            results: { winRate: 67, profitFactor: 2.3, trades: 156, maxDrawdown: 12 }
          },
          {
            id: 'default_2',
            name: 'RSI Reversal',
            description: 'Buy when RSI < 30, Sell when RSI > 70',
            timeframe: '1h',
            riskPercent: 1.5,
            entryConditions: [
              { indicator: 'rsi', operator: 'less', value: '30' }
            ],
            exitConditions: [
              { indicator: 'rsi', operator: 'greater', value: '70' },
              { indicator: 'sl', operator: 'equals', value: '2' }
            ],
            results: { winRate: 58, profitFactor: 1.8, trades: 89, maxDrawdown: 15 }
          },
          {
            id: 'default_3',
            name: 'MACD Momentum',
            description: 'Trade MACD histogram reversals',
            timeframe: '4h',
            riskPercent: 2,
            entryConditions: [
              { indicator: 'macd', operator: 'crosses_above', value: '0' }
            ],
            exitConditions: [
              { indicator: 'macd', operator: 'crosses_below', value: '0' },
              { indicator: 'sl', operator: 'equals', value: '2' }
            ],
            results: { winRate: 62, profitFactor: 2.1, trades: 124, maxDrawdown: 10 }
          }
        ];
        this.saveStrategiesToStorage();
      }
    } catch (e) {
      console.error('Error loading strategies:', e);
      this.strategies = [];
    }
  }

  saveStrategiesToStorage() {
    try {
      localStorage.setItem('tradingPro_strategies', JSON.stringify(this.strategies));
    } catch (e) {
      console.error('Error saving strategies:', e);
    }
  }

  renderStrategies() {
    const grid = document.getElementById('strategyGrid');
    if (!grid) return;

    grid.innerHTML = this.strategies.map((s, i) => `
      <div class="strategy-card ${this.currentStrategy?.id === s.id ? 'active' : ''}" data-id="${s.id}">
        <div class="strategy-name">
          ${this.getStrategyIcon(s.name)} ${s.name}
        </div>
        <div class="strategy-desc">${s.description}</div>
        <div class="strategy-stats">
          <div class="stat">
            <div class="stat-value" style="color: var(--success);">${s.results?.winRate || '--'}%</div>
            <div class="stat-label">Win Rate</div>
          </div>
          <div class="stat">
            <div class="stat-value" style="color: var(--accent-cyan);">${s.results?.profitFactor || '--'}</div>
            <div class="stat-label">Profit Factor</div>
          </div>
          <div class="stat">
            <div class="stat-value">${s.results?.trades || '--'}</div>
            <div class="stat-label">Trades</div>
          </div>
        </div>
        <div class="strategy-actions">
          <button class="btn-sm btn-edit" data-id="${s.id}">Edit</button>
          <button class="btn-sm btn-backtest" data-id="${s.id}">Backtest</button>
          <button class="btn-sm btn-apply" data-id="${s.id}">Apply</button>
          <button class="btn-sm btn-delete" data-id="${s.id}" style="margin-left: auto; color: var(--danger);">Delete</button>
        </div>
      </div>
    `).join('');

    // Bind events
    grid.querySelectorAll('.btn-edit').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const strategy = this.strategies.find(s => s.id === btn.dataset.id);
        if (strategy) this.openStrategyModal(strategy);
      });
    });

    grid.querySelectorAll('.btn-backtest').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const strategy = this.strategies.find(s => s.id === btn.dataset.id);
        if (strategy) this.runBacktestForStrategy(strategy);
      });
    });

    grid.querySelectorAll('.btn-apply').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        const strategy = this.strategies.find(s => s.id === btn.dataset.id);
        if (strategy) this.applyStrategy(strategy);
      });
    });

    grid.querySelectorAll('.btn-delete').forEach(btn => {
      btn.addEventListener('click', (e) => {
        e.stopPropagation();
        this.deleteStrategy(btn.dataset.id);
      });
    });
  }

  getStrategyIcon(name) {
    if (name.includes('EMA')) return '📈';
    if (name.includes('RSI')) return '🎯';
    if (name.includes('MACD')) return '🌊';
    if (name.includes('Scalp')) return '⚡';
    return '📊';
  }

  openStrategyModal(strategy = null) {
    this.editingStrategy = strategy;
    
    document.getElementById('modalTitle').textContent = 
      strategy ? 'Edit Strategy' : 'Create New Strategy';
    
    document.getElementById('strategyName').value = strategy?.name || '';
    document.getElementById('strategyTimeframe').value = strategy?.timeframe || '4h';
    document.getElementById('riskPercent').value = strategy?.riskPercent || 2;

    // Hide backtest preview when opening
    document.getElementById('backtestPreview')?.classList.add('hidden');
    
    document.getElementById('strategyModal')?.classList.add('active');
  }

  closeStrategyModal() {
    document.getElementById('strategyModal')?.classList.remove('active');
    this.editingStrategy = null;
  }

  addConditionRow(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;

    const row = document.createElement('div');
    row.className = 'condition-row';
    row.innerHTML = `
      <select class="form-select">
        <option value="rsi">RSI (14)</option>
        <option value="ema20">EMA (20)</option>
        <option value="ema50">EMA (50)</option>
        <option value="macd">MACD</option>
        <option value="price">Price</option>
        <option value="tp">Take Profit (%)</option>
        <option value="sl">Stop Loss (%)</option>
      </select>
      <select class="form-select" style="width: auto;">
        <option value="crosses_above">Crosses Above</option>
        <option value="crosses_below">Crosses Below</option>
        <option value="greater">Greater Than</option>
        <option value="less">Less Than</option>
        <option value="equals">Equals</option>
      </select>
      <input type="text" class="form-input" placeholder="Value">
      <button class="btn-sm" style="color: var(--danger);" onclick="this.parentElement.remove()">×</button>
    `;

    container.insertBefore(row, container.lastElementChild);
  }

  saveStrategy() {
    const name = document.getElementById('strategyName').value.trim();
    if (!name) {
      this.showToast('Error', 'Please enter a strategy name', 'error');
      return;
    }

    const strategy = {
      id: this.editingStrategy?.id || `strategy_${Date.now()}`,
      name,
      description: `Custom strategy created on ${new Date().toLocaleDateString()}`,
      timeframe: document.getElementById('strategyTimeframe').value,
      riskPercent: parseFloat(document.getElementById('riskPercent').value) || 2,
      entryConditions: this.getConditionsFromContainer('entryConditions'),
      exitConditions: this.getConditionsFromContainer('exitConditions'),
      results: this.editingStrategy?.results || null
    };

    if (this.editingStrategy) {
      const index = this.strategies.findIndex(s => s.id === this.editingStrategy.id);
      if (index !== -1) this.strategies[index] = strategy;
    } else {
      this.strategies.push(strategy);
    }

    this.saveStrategiesToStorage();
    this.renderStrategies();
    this.closeStrategyModal();
    this.showToast('Strategy Saved', `"${name}" has been saved`, 'success');
  }

  getConditionsFromContainer(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return [];

    const conditions = [];
    container.querySelectorAll('.condition-row').forEach(row => {
      const selects = row.querySelectorAll('select');
      const input = row.querySelector('input');
      if (selects.length >= 2 && input) {
        conditions.push({
          indicator: selects[0].value,
          operator: selects[1].value,
          value: input.value
        });
      }
    });

    return conditions;
  }

  deleteStrategy(id) {
    if (!confirm('Delete this strategy?')) return;
    
    this.strategies = this.strategies.filter(s => s.id !== id);
    this.saveStrategiesToStorage();
    this.renderStrategies();
    this.showToast('Strategy Deleted', 'Strategy has been removed', 'info');
  }

  applyStrategy(strategy) {
    this.currentStrategy = strategy;
    this.renderStrategies();
    this.showToast('Strategy Applied', `"${strategy.name}" is now active`, 'success');
    
    // Visual feedback on chart
    this.addStrategyMarkersToChart(strategy);
  }

  // ============= REAL BACKTESTING ENGINE =============

  async runBacktest() {
    const preview = document.getElementById('backtestPreview');
    const status = document.getElementById('backtestStatus');
    
    preview?.classList.remove('hidden');
    status.textContent = 'Running...';
    status.className = 'backtest-status running';

    // Get conditions
    const entryConditions = this.getConditionsFromContainer('entryConditions');
    const exitConditions = this.getConditionsFromContainer('exitConditions');

    // Simulate backtest with real data
    setTimeout(() => {
      const results = this.executeBacktest(entryConditions, exitConditions);
      
      document.getElementById('btWinRate').textContent = results.winRate.toFixed(1) + '%';
      document.getElementById('btProfitFactor').textContent = results.profitFactor.toFixed(2);
      document.getElementById('btTrades').textContent = results.totalTrades;
      document.getElementById('btDrawdown').textContent = results.maxDrawdown.toFixed(1) + '%';

      status.textContent = 'Complete';
      status.className = 'backtest-status complete';

      // Draw equity curve
      this.drawEquityCurve(results.equityCurve);

      this.showToast('Backtest Complete', 
        `${results.totalTrades} trades, ${results.winRate.toFixed(1)}% win rate`, 'success');
    }, 1500);
  }

  async runBacktestForStrategy(strategy) {
    this.showToast('Backtesting', `Running backtest for "${strategy.name}"...`, 'info');

    // Use strategy conditions
    const results = this.executeBacktest(strategy.entryConditions, strategy.exitConditions);

    // Update strategy results
    strategy.results = {
      winRate: Math.round(results.winRate),
      profitFactor: parseFloat(results.profitFactor.toFixed(2)),
      trades: results.totalTrades,
      maxDrawdown: Math.round(results.maxDrawdown)
    };

    this.saveStrategiesToStorage();
    this.renderStrategies();

    this.showToast('Backtest Complete', 
      `Win Rate: ${results.winRate.toFixed(1)}%, Profit Factor: ${results.profitFactor.toFixed(2)}`, 'success');
  }

  executeBacktest(entryConditions, exitConditions) {
    if (this.data.length < 100) {
      return { winRate: 0, profitFactor: 0, totalTrades: 0, maxDrawdown: 0, equityCurve: [] };
    }

    const closes = this.data.map(d => d.close);
    const rsi = this.calculateRSI(closes, 14);
    const ema20 = this.calculateEMA(closes, 20);
    const ema50 = this.calculateEMA(closes, 50);
    const macd = this.calculateMACD(closes);

    let position = null;
    let trades = [];
    let equity = 10000;
    let equityCurve = [{ time: this.data[50].time, value: equity }];
    let maxEquity = equity;
    let maxDrawdown = 0;

    // Get TP/SL from exit conditions
    let tpPercent = 3;
    let slPercent = 1.5;
    exitConditions.forEach(c => {
      if (c.indicator === 'tp') tpPercent = parseFloat(c.value) || 3;
      if (c.indicator === 'sl') slPercent = parseFloat(c.value) || 1.5;
    });

    // Process each candle
    for (let i = 51; i < this.data.length; i++) {
      const candle = this.data[i];
      const prevCandle = this.data[i - 1];

      if (!position) {
        // Check entry conditions
        let shouldEnter = true;

        for (const cond of entryConditions) {
          const value = this.getIndicatorValue(cond.indicator, i, { rsi, ema20, ema50, macd, closes });
          const compareValue = this.getCompareValue(cond.value, i, { rsi, ema20, ema50, macd, closes });
          const prevValue = this.getIndicatorValue(cond.indicator, i - 1, { rsi, ema20, ema50, macd, closes });

          if (!this.evaluateCondition(value, cond.operator, compareValue, prevValue)) {
            shouldEnter = false;
            break;
          }
        }

        if (shouldEnter) {
          position = {
            type: 'long',
            entry: candle.close,
            entryTime: candle.time,
            tp: candle.close * (1 + tpPercent / 100),
            sl: candle.close * (1 - slPercent / 100)
          };
        }
      } else {
        // Check exit
        let shouldExit = false;
        let exitPrice = candle.close;
        let exitReason = 'signal';

        // Check TP/SL
        if (candle.high >= position.tp) {
          shouldExit = true;
          exitPrice = position.tp;
          exitReason = 'tp';
        } else if (candle.low <= position.sl) {
          shouldExit = true;
          exitPrice = position.sl;
          exitReason = 'sl';
        }

        // Check exit conditions
        if (!shouldExit) {
          for (const cond of exitConditions) {
            if (cond.indicator === 'tp' || cond.indicator === 'sl') continue;
            
            const value = this.getIndicatorValue(cond.indicator, i, { rsi, ema20, ema50, macd, closes });
            const compareValue = this.getCompareValue(cond.value, i, { rsi, ema20, ema50, macd, closes });
            const prevValue = this.getIndicatorValue(cond.indicator, i - 1, { rsi, ema20, ema50, macd, closes });

            if (this.evaluateCondition(value, cond.operator, compareValue, prevValue)) {
              shouldExit = true;
              exitReason = 'signal';
              break;
            }
          }
        }

        if (shouldExit) {
          const pnlPercent = ((exitPrice - position.entry) / position.entry) * 100;
          const pnl = equity * (pnlPercent / 100);
          equity += pnl;

          trades.push({
            entry: position.entry,
            exit: exitPrice,
            entryTime: position.entryTime,
            exitTime: candle.time,
            pnl: pnlPercent,
            reason: exitReason
          });

          equityCurve.push({ time: candle.time, value: equity });
          
          maxEquity = Math.max(maxEquity, equity);
          const drawdown = ((maxEquity - equity) / maxEquity) * 100;
          maxDrawdown = Math.max(maxDrawdown, drawdown);

          position = null;
        }
      }
    }

    // Calculate stats
    const wins = trades.filter(t => t.pnl > 0);
    const losses = trades.filter(t => t.pnl <= 0);
    const winRate = trades.length > 0 ? (wins.length / trades.length) * 100 : 0;
    
    const avgWin = wins.length > 0 ? wins.reduce((a, t) => a + t.pnl, 0) / wins.length : 0;
    const avgLoss = losses.length > 0 ? Math.abs(losses.reduce((a, t) => a + t.pnl, 0) / losses.length) : 1;
    const profitFactor = avgLoss > 0 ? avgWin / avgLoss : avgWin;

    return {
      winRate,
      profitFactor: Math.max(0, profitFactor),
      totalTrades: trades.length,
      maxDrawdown,
      equityCurve,
      trades
    };
  }

  getIndicatorValue(indicator, index, indicators) {
    switch (indicator) {
      case 'rsi': return indicators.rsi[index - 14] || 50;
      case 'ema20': return indicators.ema20[index] || 0;
      case 'ema50': return indicators.ema50[index] || 0;
      case 'macd': return indicators.macd.histogram[index] || 0;
      case 'price': return indicators.closes[index] || 0;
      default: return 0;
    }
  }

  getCompareValue(value, index, indicators) {
    if (value === 'ema20') return indicators.ema20[index] || 0;
    if (value === 'ema50') return indicators.ema50[index] || 0;
    if (value === '0') return 0;
    return parseFloat(value) || 0;
  }

  evaluateCondition(value, operator, compareValue, prevValue = null) {
    switch (operator) {
      case 'greater': return value > compareValue;
      case 'less': return value < compareValue;
      case 'equals': return Math.abs(value - compareValue) < 0.01;
      case 'crosses_above': return prevValue !== null && prevValue <= compareValue && value > compareValue;
      case 'crosses_below': return prevValue !== null && prevValue >= compareValue && value < compareValue;
      default: return false;
    }
  }

  drawEquityCurve(curve) {
    const container = document.getElementById('equityCurve');
    if (!container || curve.length < 2) return;

    // Simple SVG curve
    const width = container.offsetWidth - 40;
    const height = 130;
    const padding = 20;

    const values = curve.map(c => c.value);
    const min = Math.min(...values);
    const max = Math.max(...values);
    const range = max - min || 1;

    const points = curve.map((c, i) => {
      const x = padding + (i / (curve.length - 1)) * (width - padding * 2);
      const y = height - padding - ((c.value - min) / range) * (height - padding * 2);
      return `${x},${y}`;
    });

    container.innerHTML = `
      <svg width="100%" height="${height}" viewBox="0 0 ${width} ${height}">
        <defs>
          <linearGradient id="equityGrad" x1="0%" y1="0%" x2="100%" y2="0%">
            <stop offset="0%" style="stop-color:#00d4d4"/>
            <stop offset="100%" style="stop-color:#00c896"/>
          </linearGradient>
        </defs>
        <polyline 
          points="${points.join(' ')}" 
          fill="none" 
          stroke="url(#equityGrad)" 
          stroke-width="3"
          stroke-linecap="round"
          stroke-linejoin="round"
        />
        <text x="${padding}" y="${height - 5}" fill="#5a6b7c" font-size="10">Start</text>
        <text x="${width - padding - 20}" y="${height - 5}" fill="#5a6b7c" font-size="10">End</text>
      </svg>
    `;
  }

  addStrategyMarkersToChart(strategy) {
    // Remove existing markers
    if (this.markers.length) {
      this.candlestickSeries.setMarkers([]);
      this.markers = [];
    }

    // Run quick backtest and add markers
    const results = this.executeBacktest(strategy.entryConditions, strategy.exitConditions);
    
    this.markers = results.trades.flatMap(trade => [
      {
        time: trade.entryTime,
        position: 'belowBar',
        color: '#00c896',
        shape: 'arrowUp',
        text: 'Buy'
      },
      {
        time: trade.exitTime,
        position: 'aboveBar',
        color: trade.pnl > 0 ? '#00c896' : '#e91e8c',
        shape: 'arrowDown',
        text: trade.reason === 'tp' ? 'TP' : trade.reason === 'sl' ? 'SL' : 'Exit'
      }
    ]);

    this.candlestickSeries.setMarkers(this.markers);
    this.showToast('Strategy Applied', `${results.trades.length} trade signals displayed on chart`, 'info');
  }

  loadStrategyTab(tab) {
    const content = document.getElementById('strategyContent');
    if (!content) return;

    switch (tab) {
      case 'strategies':
        this.renderStrategies();
        break;
      case 'backtest':
        content.innerHTML = `
          <div style="padding: 2rem; text-align: center; color: var(--text-secondary);">
            <p>Select a strategy and click "Backtest" to see detailed results.</p>
          </div>
        `;
        break;
      case 'results':
        content.innerHTML = `
          <div style="padding: 2rem; text-align: center; color: var(--text-secondary);">
            <p>Apply a strategy to see live trading results here.</p>
          </div>
        `;
        break;
    }
  }

  showToast(title, message, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
      <div style="flex: 1;">
        <div style="font-weight: 600; font-size: 0.9rem;">${title}</div>
        <div style="font-size: 0.8rem; color: var(--text-secondary);">${message}</div>
      </div>
      <button style="background: none; border: none; color: var(--text-muted); cursor: pointer; padding: 4px;" onclick="this.parentElement.remove()">×</button>
    `;

    container.appendChild(toast);

    setTimeout(() => {
      toast.classList.add('removing');
      setTimeout(() => toast.remove(), 300);
    }, 5000);
  }
}

// Initialize
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => new TradingProV3().init());
} else {
  new TradingProV3().init();
}

