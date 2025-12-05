/**
 * Dashboard 2 - Pro Trading Terminal
 */

class Dashboard2 {
  constructor() {
    this.symbol = 'BTCUSDT';
    this.timeframe = '4h';
    this.chart = null;
    this.candlestickSeries = null;
    this.data = [];
    this.indicators = { ema20: null, ema50: null, volume: null };
    this.activeTool = 'crosshair';
    this.isDrawing = false;
    this.drawingStart = null;
    this.drawings = [];
  }

  async init() {
    console.log('[Dashboard2] Initializing...');
    
    this.initChart();
    this.bindEvents();
    this.initBattleAccordion();
    
    await Promise.all([
      this.loadMarketData(),
      this.loadFearGreed(),
      this.loadNews()
    ]);
    
    setTimeout(() => this.setupDrawing(), 500);
    
    setInterval(() => this.loadMarketData(true), 30000);
    setInterval(() => this.loadFearGreed(), 60000);
    
    this.showToast('Dashboard 2', 'Ready!', 'success');
  }

  initChart() {
    const container = document.getElementById('tradingChart');
    if (!container) return;

    this.chart = LightweightCharts.createChart(container, {
      layout: { background: { type: 'solid', color: '#ffffff' }, textColor: '#5a6b7c' },
      grid: { vertLines: { color: 'rgba(0,180,180,0.04)' }, horzLines: { color: 'rgba(0,180,180,0.04)' } },
      crosshair: { mode: LightweightCharts.CrosshairMode.Normal },
      rightPriceScale: { borderColor: 'rgba(0,180,180,0.1)' },
      timeScale: { borderColor: 'rgba(0,180,180,0.1)', timeVisible: true },
    });

    this.candlestickSeries = this.chart.addCandlestickSeries({
      upColor: '#00c896', downColor: '#e91e8c',
      borderUpColor: '#00c896', borderDownColor: '#e91e8c',
      wickUpColor: '#00c896', wickDownColor: '#e91e8c',
    });

    this.indicators.ema20 = this.chart.addLineSeries({ color: '#00d4d4', lineWidth: 2 });
    this.indicators.ema50 = this.chart.addLineSeries({ color: '#0088cc', lineWidth: 2 });
    this.indicators.volume = this.chart.addHistogramSeries({ priceFormat: { type: 'volume' }, priceScaleId: 'vol' });
    this.chart.priceScale('vol').applyOptions({ scaleMargins: { top: 0.85, bottom: 0 } });

    new ResizeObserver(e => {
      const { width, height } = e[0].contentRect;
      this.chart.applyOptions({ width, height });
    }).observe(container);
  }

  bindEvents() {
    document.getElementById('symbolInput')?.addEventListener('change', e => {
      this.symbol = e.target.value.toUpperCase();
      this.loadMarketData();
      this.loadNews();
    });

    document.querySelectorAll('.tf-btn').forEach(btn => {
      btn.addEventListener('click', e => {
        document.querySelectorAll('.tf-btn').forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        this.timeframe = e.target.dataset.tf;
        this.loadMarketData();
      });
    });

    document.querySelectorAll('.tool-btn').forEach(btn => {
      btn.addEventListener('click', () => this.selectTool(btn.dataset.tool));
    });
  }

  selectTool(tool) {
    if (tool === 'clear') {
      this.clearDrawings();
      return;
    }
    this.activeTool = tool;
    this.isDrawing = false;
    document.querySelectorAll('.tool-btn').forEach(btn => {
      if (btn.dataset.tool !== 'clear') btn.classList.toggle('active', btn.dataset.tool === tool);
    });
  }

  setupDrawing() {
    const container = document.getElementById('tradingChart');
    if (!container || !this.chart) return;

    container.addEventListener('click', e => {
      if (this.activeTool === 'crosshair') return;
      const rect = container.getBoundingClientRect();
      const x = e.clientX - rect.left;
      const y = e.clientY - rect.top;
      const time = this.chart.timeScale().coordinateToTime(x);
      const price = this.candlestickSeries.coordinateToPrice(y);
      if (!time || !price) return;

      if (this.activeTool === 'horizontal') {
        this.addHorizontalLine(price);
        return;
      }

      if (!this.isDrawing) {
        this.isDrawing = true;
        this.drawingStart = { time, price };
        this.showToast('📍', 'Click end point', 'info');
      } else {
        this.finishDrawing(time, price);
      }
    });
  }

  addHorizontalLine(price) {
    const line = this.candlestickSeries.createPriceLine({
      price, color: '#00d4d4', lineWidth: 2, axisLabelVisible: true
    });
    this.drawings.push({ type: 'priceline', line });
    this.showToast('✓', `Line at $${price.toFixed(0)}`, 'success');
  }

  finishDrawing(endTime, endPrice) {
    if (!this.drawingStart) return;

    if (this.activeTool === 'trendline') {
      const line = this.chart.addLineSeries({ color: '#00d4d4', lineWidth: 2, lastValueVisible: false, priceLineVisible: false });
      line.setData([
        { time: this.drawingStart.time, value: this.drawingStart.price },
        { time: endTime, value: endPrice }
      ]);
      this.drawings.push({ type: 'series', series: line });
    } else if (this.activeTool === 'fib') {
      const diff = endPrice - this.drawingStart.price;
      [0, 0.236, 0.382, 0.5, 0.618, 0.786, 1].forEach((lvl, i) => {
        const p = this.drawingStart.price + diff * lvl;
        const colors = ['#e91e8c', '#ff6b35', '#ffc107', '#00d4d4', '#00c896', '#0088cc', '#9c27b0'];
        const line = this.candlestickSeries.createPriceLine({ price: p, color: colors[i], lineWidth: 1, lineStyle: 2 });
        this.drawings.push({ type: 'priceline', line });
      });
    }

    this.isDrawing = false;
    this.drawingStart = null;
    this.showToast('✓', `${this.activeTool} added`, 'success');
  }

  clearDrawings() {
    this.drawings.forEach(d => {
      try {
        if (d.type === 'priceline') this.candlestickSeries.removePriceLine(d.line);
        else if (d.type === 'series') this.chart.removeSeries(d.series);
      } catch (e) {}
    });
    this.drawings = [];
    this.showToast('✓', 'Cleared', 'info');
  }

  async loadMarketData(silent = false) {
    if (!silent) document.getElementById('chartLoading')?.classList.remove('hidden');

    try {
      const res = await fetch(`https://api.binance.com/api/v3/klines?symbol=${this.symbol}&interval=${this.timeframe}&limit=500`);
      const raw = await res.json();
      this.data = raw.map(c => ({
        time: Math.floor(c[0] / 1000),
        open: +c[1], high: +c[2], low: +c[3], close: +c[4], volume: +c[5]
      }));
      this.updateChart();
      this.calcIndicators();
      this.updatePrice();
      this.updateLevels();
    } catch (e) {
      console.error(e);
    } finally {
      document.getElementById('chartLoading')?.classList.add('hidden');
    }
  }

  updateChart() {
    if (!this.candlestickSeries || !this.data.length) return;
    this.candlestickSeries.setData(this.data);
    this.indicators.volume?.setData(this.data.map(d => ({
      time: d.time, value: d.volume,
      color: d.close > d.open ? 'rgba(0,200,150,0.4)' : 'rgba(233,30,140,0.4)'
    })));
    this.chart.timeScale().fitContent();
  }

  calcIndicators() {
    if (!this.data.length) return;
    const closes = this.data.map(d => d.close);

    const ema20 = this.ema(closes, 20);
    const ema50 = this.ema(closes, 50);
    this.indicators.ema20?.setData(ema20.map((v, i) => ({ time: this.data[i].time, value: v })));
    this.indicators.ema50?.setData(ema50.map((v, i) => ({ time: this.data[i].time, value: v })));

    const rsi = this.rsi(closes, 14);
    const macd = this.macd(closes);
    const latestRsi = rsi[rsi.length - 1];
    const latestMacd = macd[macd.length - 1];
    
    // === همزبان کردن همه کارت‌ها ===
    // RSI: > 50 = Bullish, < 50 = Bearish
    const rsiBullish = latestRsi > 50;
    // MACD: > 0 = Bullish, < 0 = Bearish
    const macdBullish = latestMacd > 0;
    // EMA: 20 > 50 = Bullish
    const emaBullish = ema20[ema20.length - 1] > ema50[ema50.length - 1];
    // Price Action
    const pa = this.analyzePriceAction();

    // === کارت‌ها با زبان یکسان: Bullish / Bearish / Neutral ===
    // RSI: > 55 = Bullish, < 45 = Bearish, else Neutral
    const rsiStatus = latestRsi > 55 ? 'bullish' : latestRsi < 45 ? 'bearish' : 'neutral';
    const rsiStrong = latestRsi > 70 || latestRsi < 30;
    this.setVerdictWidget('rsi', rsiStatus, rsiStrong);
    
    // MACD
    const macdStatus = macdBullish ? 'bullish' : 'bearish';
    this.setVerdictWidget('macd', macdStatus, false);
    
    // EMA Trend
    const emaStatus = emaBullish ? 'bullish' : 'bearish';
    this.setVerdictWidget('trend', emaStatus, false);
    
    // Price Action - فقط از candle استفاده کن
    const isBullCandle = pa.candle.includes('Bull');
    const isBearCandle = pa.candle.includes('Bear');
    const paStatus = isBullCandle ? 'bullish' : isBearCandle ? 'bearish' : 'neutral';
    const paStrong = pa.candle.includes('Strong');
    this.setVerdictWidget('pa', paStatus, paStrong);
    
    // Update consensus
    this.updateConsensus([rsiStatus, macdStatus, emaStatus, paStatus]);

    // === پنل‌های سمت راست ===
    document.getElementById('panelRsi').textContent = latestRsi.toFixed(1);
    document.getElementById('panelRsi').className = 'metric-value ' + (rsiBullish ? 'bullish' : 'bearish');
    document.getElementById('panelMacd').textContent = macdBullish ? 'Bullish' : 'Bearish';
    document.getElementById('panelMacd').className = 'metric-value ' + (macdBullish ? 'bullish' : 'bearish');
    document.getElementById('panelTrend').textContent = emaBullish ? 'Bullish' : 'Bearish';
    document.getElementById('panelTrend').className = 'metric-value ' + (emaBullish ? 'bullish' : 'bearish');

    const vol = this.data.slice(-24).reduce((s, d) => s + d.volume, 0);
    document.getElementById('panelVolume').textContent = (vol / 1e9).toFixed(2) + 'B';

    // Price Action Panel
    document.getElementById('paPattern').textContent = pa.pattern;
    document.getElementById('paPattern').className = 'metric-value ' + (pa.bullish ? 'bullish' : 'bearish');
    document.getElementById('paCandle').textContent = pa.candle;
    document.getElementById('paCandle').className = 'metric-value ' + (pa.candleBullish ? 'bullish' : 'bearish');
    document.getElementById('paStructure').textContent = pa.structure;
    document.getElementById('paStructure').className = 'metric-value ' + (pa.structureBullish ? 'bullish' : 'bearish');
    document.getElementById('paVerdict').textContent = pa.bullish ? 'Bullish' : 'Bearish';
    document.getElementById('paVerdict').className = 'metric-value ' + (pa.bullish ? 'bullish' : 'bearish');

  }

  setVerdictWidget(id, status, isStrong = false) {
    const verdictEl = document.getElementById(id + 'Verdict');
    
    const labels = { bullish: 'Bullish', bearish: 'Bearish', neutral: 'Neutral' };
    const icons = { bullish: '↑', bearish: '↓', neutral: '—' };
    
    if (verdictEl) {
      // اگر پترن خالی است
      if (id === 'pa' && status === 'neutral') {
        verdictEl.textContent = '—';
        verdictEl.className = 'widget-verdict neutral';
      } else {
        verdictEl.textContent = `${icons[status]} ${labels[status]}`;
        // رنگ قوی‌تر برای Strong
        const strongClass = isStrong ? '-strong' : '';
        verdictEl.className = 'widget-verdict ' + status + strongClass;
      }
    }
  }

  updateConsensus(statuses) {
    const bullishCount = statuses.filter(s => s === 'bullish').length;
    const bearishCount = statuses.filter(s => s === 'bearish').length;
    
    // Update scores
    const bullScore = document.getElementById('bullScore');
    const bearScore = document.getElementById('bearScore');
    if (bullScore) bullScore.textContent = bullishCount;
    if (bearScore) bearScore.textContent = bearishCount;
    
    // Update power bars
    const bullPower = document.getElementById('bullPower');
    const bearPower = document.getElementById('bearPower');
    if (bullPower) bullPower.style.width = (bullishCount * 25) + '%';
    if (bearPower) bearPower.style.width = (bearishCount * 25) + '%';
    
    // Update label and push indicator
    const labelEl = document.getElementById('battleLabel');
    const pushEl = document.getElementById('pushIndicator');
    const bullFighter = document.getElementById('bullFighter');
    const bearFighter = document.getElementById('bearFighter');
    
    // Remove winner classes
    if (bullFighter) bullFighter.classList.remove('winner');
    if (bearFighter) bearFighter.classList.remove('winner');
    if (pushEl) pushEl.classList.remove('bull-winning', 'bear-winning');
    
    if (bullishCount > bearishCount) {
      if (labelEl) {
        labelEl.textContent = 'Bulls Win!';
        labelEl.className = 'battle-label bullish';
      }
      if (pushEl) pushEl.classList.add('bull-winning');
      if (bullFighter) bullFighter.classList.add('winner');
    } else if (bearishCount > bullishCount) {
      if (labelEl) {
        labelEl.textContent = 'Bears Win!';
        labelEl.className = 'battle-label bearish';
      }
      if (pushEl) pushEl.classList.add('bear-winning');
      if (bearFighter) bearFighter.classList.add('winner');
    } else {
      if (labelEl) {
        labelEl.textContent = 'Draw';
        labelEl.className = 'battle-label neutral';
      }
    }
    
    this.updateSignalFromConsensus(bullishCount, bearishCount, 0);
  }

  initBattleAccordion() {
    const header = document.getElementById('battleHeader');
    const panel = header?.closest('.battle-panel');
    
    if (header && panel) {
      header.addEventListener('click', () => {
        panel.classList.toggle('open');
      });
    }
  }

  updateSignalFromConsensus(bullish, bearish, neutral) {
    let sig = 'HOLD', conf = 50;
    
    if (bullish === 4) { sig = 'STRONG BUY'; conf = 95; }
    else if (bullish === 3) { sig = 'BUY'; conf = 80; }
    else if (bearish === 4) { sig = 'STRONG SELL'; conf = 95; }
    else if (bearish === 3) { sig = 'SELL'; conf = 80; }
    else { sig = 'HOLD'; conf = 50; }
    
    const badge = document.getElementById('signalBadge');
    if (badge) {
      badge.textContent = sig;
      badge.className = 'signal-badge ' + (sig.includes('BUY') ? 'buy' : sig.includes('SELL') ? 'sell' : 'hold');
    }
    
    const confEl = document.getElementById('panelConfidence');
    if (confEl) {
      confEl.textContent = conf + '%';
      confEl.className = 'metric-value ' + (sig.includes('BUY') ? 'bullish' : sig.includes('SELL') ? 'bearish' : '');
    }
  }

  analyzePriceAction() {
    if (this.data.length < 5) return { pattern: '--', candle: '--', structure: '--', bullish: true, candleBullish: true, structureBullish: true };

    const recent = this.data.slice(-5);
    const last = recent[recent.length - 1];
    const prev = recent[recent.length - 2];

    // Candle Analysis
    const body = Math.abs(last.close - last.open);
    const upperWick = last.high - Math.max(last.open, last.close);
    const lowerWick = Math.min(last.open, last.close) - last.low;
    const candleBullish = last.close > last.open;

    let candle = 'Neutral';
    if (body > (upperWick + lowerWick) * 2) {
      candle = candleBullish ? 'Strong Bull' : 'Strong Bear';
    } else if (lowerWick > body * 2 && upperWick < body) {
      candle = 'Hammer';
    } else if (upperWick > body * 2 && lowerWick < body) {
      candle = 'Shooting Star';
    } else if (body < (last.high - last.low) * 0.1) {
      candle = 'Doji';
    } else {
      candle = candleBullish ? 'Bullish' : 'Bearish';
    }

    // Structure - Higher Highs/Lower Lows
    const highs = recent.map(d => d.high);
    const lows = recent.map(d => d.low);
    const hh = highs[4] > highs[3] && highs[3] > highs[2];
    const ll = lows[4] < lows[3] && lows[3] < lows[2];
    const hl = lows[4] > lows[3];
    const lh = highs[4] < highs[3];

    let structure = 'Consolidation';
    let structureBullish = true;
    if (hh && hl) { structure = 'HH + HL'; structureBullish = true; }
    else if (ll && lh) { structure = 'LL + LH'; structureBullish = false; }
    else if (hh) { structure = 'Higher Highs'; structureBullish = true; }
    else if (ll) { structure = 'Lower Lows'; structureBullish = false; }

    // Pattern Detection
    let pattern = 'No Pattern';
    let patternBullish = candleBullish;

    // Engulfing
    if (last.close > last.open && prev.close < prev.open && 
        last.open < prev.close && last.close > prev.open) {
      pattern = 'Engulfing';
      patternBullish = true;
    } else if (last.close < last.open && prev.close > prev.open &&
        last.open > prev.close && last.close < prev.open) {
      pattern = 'Engulfing';
      patternBullish = false;
    }

    // Morning/Evening Star
    const mid = recent[recent.length - 3];
    if (mid && Math.abs(mid.close - mid.open) < (mid.high - mid.low) * 0.1) {
      if (recent[recent.length - 4].close < recent[recent.length - 4].open && candleBullish) {
        pattern = 'Morning Star';
        patternBullish = true;
      } else if (recent[recent.length - 4].close > recent[recent.length - 4].open && !candleBullish) {
        pattern = 'Evening Star';
        patternBullish = false;
      }
    }

    // Overall verdict
    const bullishScore = (candleBullish ? 1 : 0) + (structureBullish ? 1 : 0) + (patternBullish ? 1 : 0);
    const overallBullish = bullishScore >= 2;

    return {
      pattern: pattern,
      candle: candle,
      structure: structure,
      bullish: overallBullish,
      candleBullish: candleBullish,
      structureBullish: structureBullish
    };
  }


  updatePrice() {
    if (!this.data.length) return;
    const l = this.data[this.data.length - 1];
    const p = this.data[this.data.length - 2];
    const chg = ((l.close - p.close) / p.close) * 100;

    document.getElementById('currentPrice').textContent = `$${l.close.toLocaleString('en-US', { minimumFractionDigits: 2 })}`;
    const chgEl = document.getElementById('priceChange');
    chgEl.textContent = `${chg >= 0 ? '+' : ''}${chg.toFixed(2)}%`;
    chgEl.className = 'price-change ' + (chg >= 0 ? 'positive' : 'negative');
    document.getElementById('lastUpdate').textContent = new Date().toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
    document.getElementById('currentLevel').textContent = `$${l.close.toLocaleString('en-US', { maximumFractionDigits: 0 })}`;
  }

  updateLevels() {
    const recent = this.data.slice(-50);
    const high = Math.max(...recent.map(d => d.high));
    const low = Math.min(...recent.map(d => d.low));
    document.getElementById('resistance').textContent = `$${high.toLocaleString('en-US', { maximumFractionDigits: 0 })}`;
    document.getElementById('support').textContent = `$${low.toLocaleString('en-US', { maximumFractionDigits: 0 })}`;
  }

  async loadFearGreed() {
    try {
      const res = await fetch('https://api.alternative.me/fng/?limit=1');
      const data = await res.json();
      const val = +data.data[0].value;
      const lbl = data.data[0].value_classification;
      this.updateFG(val, lbl);
    } catch (e) {
      this.updateFG(23, 'Extreme Fear');
    }
  }

  updateFG(val, lbl) {
    const scoreEl = document.getElementById('fgScore');
    const lblEl = document.getElementById('fgLabel');
    const indEl = document.getElementById('fgIndicator');
    
    const cls = val <= 40 ? 'fear' : val >= 60 ? 'greed' : 'neutral';
    
    if (scoreEl) { 
      scoreEl.textContent = val; 
      scoreEl.className = 'fg-score ' + cls; 
    }
    if (lblEl) lblEl.textContent = lbl;
    if (indEl) indEl.style.left = val + '%';
  }

  async loadNews() {
    const coin = this.symbol.replace('USDT', '');
    const news = [
      { title: `${coin} breaks key resistance, analysts bullish`, score: 78, src: 'CoinDesk', time: '1h' },
      { title: `Institutional buying pressure on ${coin}`, score: 72, src: 'Bloomberg', time: '2h' },
      { title: `${coin} network sees record transactions`, score: 65, src: 'Reuters', time: '3h' },
      { title: `Major exchange lists new ${coin} pairs`, score: 58, src: 'CoinTelegraph', time: '4h' },
      { title: `${coin} volatility rises amid uncertainty`, score: 42, src: 'Decrypt', time: '5h' },
    ];
    const feed = document.getElementById('newsFeed');
    if (feed) {
      feed.innerHTML = news.map(n => {
        const cls = n.score >= 60 ? 'positive' : n.score <= 45 ? 'negative' : 'neutral';
        const icon = this.getNewsIcon(cls);
        return `
        <div class="news-item">
          <div class="news-icon ${cls}">${icon}</div>
          <div class="news-content">
            <div class="news-title">${n.title}</div>
            <div class="news-meta">${n.src} • ${n.time}</div>
          </div>
          <div class="news-score ${cls}">${n.score}</div>
        </div>
      `}).join('');
    }
  }

  getNewsIcon(type) {
    const icons = {
      positive: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><path d="M8 14s1.5 2 4 2 4-2 4-2"/><line x1="9" y1="9" x2="9.01" y2="9"/><line x1="15" y1="9" x2="15.01" y2="9"/></svg>`,
      negative: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><path d="M16 16s-1.5-2-4-2-4 2-4 2"/><line x1="9" y1="9" x2="9.01" y2="9"/><line x1="15" y1="9" x2="15.01" y2="9"/></svg>`,
      neutral: `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><circle cx="12" cy="12" r="10"/><line x1="8" y1="15" x2="16" y2="15"/><line x1="9" y1="9" x2="9.01" y2="9"/><line x1="15" y1="9" x2="15.01" y2="9"/></svg>`
    };
    return icons[type] || icons.neutral;
  }

  ema(arr, p) {
    const k = 2 / (p + 1);
    const r = [arr[0]];
    for (let i = 1; i < arr.length; i++) r.push(arr[i] * k + r[i - 1] * (1 - k));
    return r;
  }

  rsi(arr, p = 14) {
    const r = [];
    let g = 0, l = 0;
    for (let i = 1; i <= p; i++) {
      const d = arr[i] - arr[i - 1];
      d > 0 ? g += d : l += Math.abs(d);
    }
    let ag = g / p, al = l / p;
    r.push(100 - 100 / (1 + ag / (al || 0.001)));
    for (let i = p + 1; i < arr.length; i++) {
      const d = arr[i] - arr[i - 1];
      ag = (ag * (p - 1) + (d > 0 ? d : 0)) / p;
      al = (al * (p - 1) + (d < 0 ? Math.abs(d) : 0)) / p;
      r.push(100 - 100 / (1 + ag / (al || 0.001)));
    }
    return r;
  }

  macd(arr) {
    const e12 = this.ema(arr, 12);
    const e26 = this.ema(arr, 26);
    const ml = e12.map((v, i) => v - e26[i]);
    const sl = this.ema(ml, 9);
    return ml.map((v, i) => v - sl[i]);
  }

  showToast(title, msg, type = 'info') {
    const c = document.getElementById('toastContainer');
    if (!c) return;
    const t = document.createElement('div');
    t.className = 'toast ' + type;
    t.innerHTML = `<div style="font-weight:600;font-size:0.75rem;">${title}</div><div style="font-size:0.65rem;color:var(--text-secondary);">${msg}</div>`;
    c.appendChild(t);
    setTimeout(() => t.remove(), 3000);
  }
}

document.readyState === 'loading'
  ? document.addEventListener('DOMContentLoaded', () => new Dashboard2().init())
  : new Dashboard2().init();
