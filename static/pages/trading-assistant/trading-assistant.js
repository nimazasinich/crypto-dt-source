/**
 * Trading Assistant Page
 * Real-time trading signals and recommendations
 */

import { api } from '../../shared/js/core/api-client.js';
import { LayoutManager } from '../../shared/js/core/layout-manager.js';
import { Toast } from '../../shared/js/components/toast.js';

class TradingAssistantPage {
  constructor() {
    this.isLoading = false;
    this.currentSignals = null;
  }

  async init() {
    try {
      await LayoutManager.injectLayouts();
      LayoutManager.setActiveNav('trading-assistant');
      
      this.bindEvents();
    } catch (error) {
      console.error('[Trading] Init error:', error);
      Toast.error('Failed to initialize Trading Assistant');
    }
  }

  bindEvents() {
    document.getElementById('get-signals-btn')?.addEventListener('click', () => this.getSignalsFromForm());
    document.getElementById('refresh-btn')?.addEventListener('click', () => this.refresh());
    
    document.getElementById('symbol-input')?.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') this.getSignalsFromForm();
    });
  }

  async getSignalsFromForm() {
    const symbol = document.getElementById('symbol-input').value.trim().toUpperCase();
    if (!symbol) {
      Toast.error('Please enter a symbol');
      return;
    }
    await this.getSignals(symbol);
  }

  async getSignals(symbol) {
    if (this.isLoading) return;

    document.getElementById('symbol-input').value = symbol;
    this.isLoading = true;
    this.showLoading(symbol);

    try {
      const result = await api.getAISignals(symbol);
      this.currentSignals = { symbol, ...result };
      this.renderSignals(result, symbol);
      this.updateLastUpdate();
      Toast.success(`Signals loaded for ${symbol}`);
    } catch (error) {
      console.error('[Trading] Signals error:', error);
      Toast.error('Failed to get trading signals');
      this.showError(error.message);
    } finally {
      this.isLoading = false;
    }
  }

  async refresh() {
    if (this.currentSignals?.symbol) {
      await this.getSignals(this.currentSignals.symbol);
    } else {
      Toast.info('Select a cryptocurrency first');
    }
  }

  showLoading(symbol) {
    const body = document.getElementById('results-body');
    body.innerHTML = `
      <div class="loading-container">
        <div class="spinner"></div>
        <p>Analyzing ${symbol} market data...</p>
      </div>
    `;
  }

  showError(message) {
    const body = document.getElementById('results-body');
    body.innerHTML = `
      <div class="error-state">
        <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>
        <p>Failed to get signals</p>
        <p class="error-message">${message}</p>
      </div>
    `;
  }

  renderSignals(result, symbol) {
    const body = document.getElementById('results-body');
    const signals = result.signals || [];
    const overall = result.overall || result.recommendation || 'NEUTRAL';
    const overallClass = this.getSignalClass(overall);

    body.innerHTML = `
      <div class="signals-content">
        <!-- Overall Signal -->
        <div class="overall-signal ${overallClass}">
          <div class="signal-symbol">${symbol}</div>
          <div class="signal-direction">
            ${this.getDirectionIcon(overall)}
            <span>${overall}</span>
          </div>
          ${result.strength ? `<div class="signal-strength">Strength: ${(result.strength * 100).toFixed(0)}%</div>` : ''}
        </div>

        <!-- Individual Signals -->
        ${signals.length > 0 ? `
          <div class="signals-grid">
            ${signals.map(signal => `
              <div class="signal-card ${this.getSignalClass(signal.direction || signal.type)}">
                <div class="signal-header">
                  <span class="signal-name">${signal.name || signal.indicator}</span>
                  <span class="signal-value">${signal.direction || signal.type || signal.value}</span>
                </div>
                ${signal.description ? `<div class="signal-desc">${signal.description}</div>` : ''}
                ${signal.weight ? `<div class="signal-weight">Weight: ${(signal.weight * 100).toFixed(0)}%</div>` : ''}
              </div>
            `).join('')}
          </div>
        ` : ''}

        <!-- Key Levels -->
        ${result.levels ? `
          <div class="key-levels">
            <h4>
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="12" y1="20" x2="12" y2="10"></line><line x1="18" y1="20" x2="18" y2="4"></line><line x1="6" y1="20" x2="6" y2="16"></line></svg>
              Key Levels
            </h4>
            <div class="levels-grid">
              ${result.levels.resistance ? `
                <div class="level resistance">
                  <span class="level-label">Resistance</span>
                  <span class="level-value">$${this.formatPrice(result.levels.resistance)}</span>
                </div>
              ` : ''}
              ${result.levels.current ? `
                <div class="level current">
                  <span class="level-label">Current</span>
                  <span class="level-value">$${this.formatPrice(result.levels.current)}</span>
                </div>
              ` : ''}
              ${result.levels.support ? `
                <div class="level support">
                  <span class="level-label">Support</span>
                  <span class="level-value">$${this.formatPrice(result.levels.support)}</span>
                </div>
              ` : ''}
            </div>
          </div>
        ` : ''}

        <!-- Trade Setup -->
        ${result.setup ? `
          <div class="trade-setup">
            <h4>
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><circle cx="12" cy="12" r="6"></circle><circle cx="12" cy="12" r="2"></circle></svg>
              Suggested Setup
            </h4>
            <div class="setup-grid">
              ${result.setup.entry ? `<div class="setup-item"><span>Entry</span><strong>$${this.formatPrice(result.setup.entry)}</strong></div>` : ''}
              ${result.setup.stopLoss ? `<div class="setup-item stop"><span>Stop Loss</span><strong>$${this.formatPrice(result.setup.stopLoss)}</strong></div>` : ''}
              ${result.setup.takeProfit ? `<div class="setup-item take"><span>Take Profit</span><strong>$${this.formatPrice(result.setup.takeProfit)}</strong></div>` : ''}
              ${result.setup.riskReward ? `<div class="setup-item"><span>R:R Ratio</span><strong>${result.setup.riskReward.toFixed(2)}</strong></div>` : ''}
            </div>
          </div>
        ` : ''}

        <!-- Risk Warning -->
        <div class="risk-warning">
          <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
          <span>Trading involves risk. These signals are for informational purposes only. Always use proper risk management.</span>
        </div>
      </div>
    `;
  }

  getSignalClass(direction) {
    if (!direction) return 'neutral';
    const d = direction.toUpperCase();
    if (d.includes('BUY') || d.includes('LONG') || d.includes('BULLISH') || d === 'UP') return 'bullish';
    if (d.includes('SELL') || d.includes('SHORT') || d.includes('BEARISH') || d === 'DOWN') return 'bearish';
    return 'neutral';
  }

  getDirectionIcon(direction) {
    const cls = this.getSignalClass(direction);
    if (cls === 'bullish') {
      return '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline><polyline points="17 6 23 6 23 12"></polyline></svg>';
    }
    if (cls === 'bearish') {
      return '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 18 13.5 8.5 8.5 13.5 1 6"></polyline><polyline points="17 18 23 18 23 12"></polyline></svg>';
    }
    return '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"></line></svg>';
  }

  formatPrice(price) {
    if (typeof price !== 'number') return price;
    if (price >= 1000) return price.toLocaleString(undefined, { maximumFractionDigits: 0 });
    if (price >= 1) return price.toFixed(2);
    return price.toFixed(6);
  }

  updateLastUpdate() {
    const el = document.getElementById('last-update');
    if (el) {
      el.textContent = `Updated: ${new Date().toLocaleTimeString()}`;
    }
  }
}

// Initialize page
const page = new TradingAssistantPage();
window.tradingPage = page;

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => page.init());
} else {
  page.init();
}
