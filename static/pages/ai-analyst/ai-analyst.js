/**
 * AI Analyst Page
 * AI-powered trading analysis and decision support
 */

import { api } from '../../shared/js/core/api-client.js';
import { LayoutManager } from '../../shared/js/core/layout-manager.js';
import { Toast } from '../../shared/js/components/toast.js';

class AIAnalystPage {
  constructor() {
    this.isLoading = false;
  }

  async init() {
    try {
      await LayoutManager.injectLayouts();
      LayoutManager.setActiveNav('ai-analyst');
      
      this.bindEvents();
    } catch (error) {
      console.error('[AIAnalyst] Init error:', error);
      Toast.error('Failed to initialize AI Analyst');
    }
  }

  bindEvents() {
    document.getElementById('analyze-btn')?.addEventListener('click', () => this.analyze());
    
    // Enter key on symbol input
    document.getElementById('symbol-input')?.addEventListener('keypress', (e) => {
      if (e.key === 'Enter') this.analyze();
    });
  }

  async analyze() {
    if (this.isLoading) return;

    const symbol = document.getElementById('symbol-input').value.trim().toUpperCase();
    const horizon = document.getElementById('horizon-select').value;
    const riskTolerance = document.getElementById('risk-select').value;
    const model = document.getElementById('model-select').value;
    const context = document.getElementById('context-input').value.trim();

    if (!symbol) {
      Toast.error('Please enter a cryptocurrency symbol');
      return;
    }

    this.isLoading = true;
    this.showLoading();

    try {
      const result = await api.getAIDecision(symbol, horizon, riskTolerance, context, model);
      this.renderResults(result, symbol);
      Toast.success('Analysis complete');
    } catch (error) {
      console.error('[AIAnalyst] Analysis error:', error);
      Toast.error('Analysis failed. Please try again.');
      this.showError(error.message);
    } finally {
      this.isLoading = false;
    }
  }

  async quickAnalyze(symbol) {
    document.getElementById('symbol-input').value = symbol;
    await this.analyze();
  }

  showLoading() {
    const body = document.getElementById('results-body');
    body.innerHTML = `
      <div class="loading-container">
        <div class="spinner"></div>
        <p>AI is analyzing market data...</p>
        <p class="loading-subtitle">This may take a few seconds</p>
      </div>
    `;
  }

  showError(message) {
    const body = document.getElementById('results-body');
    body.innerHTML = `
      <div class="error-state">
        <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="15" y1="9" x2="9" y2="15"></line><line x1="9" y1="9" x2="15" y2="15"></line></svg>
        <p>Failed to complete analysis</p>
        <p class="error-message">${message}</p>
        <button class="btn btn-primary" onclick="window.analystPage.analyze()">Try Again</button>
      </div>
    `;
  }

  renderResults(result, symbol) {
    const body = document.getElementById('results-body');
    
    const decision = result.decision || result.recommendation || 'HOLD';
    const confidence = result.confidence || result.confidence_score || 0.5;
    const decisionClass = this.getDecisionClass(decision);

    body.innerHTML = `
      <div class="analysis-results">
        <!-- Main Decision -->
        <div class="decision-card ${decisionClass}">
          <div class="decision-header">
            <span class="symbol">${symbol}</span>
            <span class="decision-badge">${decision}</span>
          </div>
          <div class="confidence-meter">
            <div class="meter-label">Confidence</div>
            <div class="meter-bar">
              <div class="meter-fill" style="width: ${confidence * 100}%"></div>
            </div>
            <div class="meter-value">${(confidence * 100).toFixed(0)}%</div>
          </div>
        </div>

        <!-- Analysis Summary -->
        ${result.summary || result.analysis ? `
          <div class="analysis-section">
            <h4>
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M14.5 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V7.5L14.5 2z"></path><polyline points="14 2 14 8 20 8"></polyline></svg>
              Analysis Summary
            </h4>
            <p>${result.summary || result.analysis}</p>
          </div>
        ` : ''}

        <!-- Key Signals -->
        ${result.signals && result.signals.length > 0 ? `
          <div class="analysis-section">
            <h4>
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline></svg>
              Key Signals
            </h4>
            <ul class="signals-list">
              ${result.signals.map(signal => `
                <li class="signal-item ${signal.type || 'neutral'}">
                  <span class="signal-icon">${this.getSignalIcon(signal.type)}</span>
                  <span class="signal-text">${signal.text || signal}</span>
                </li>
              `).join('')}
            </ul>
          </div>
        ` : ''}

        <!-- Risk Factors -->
        ${result.risks && result.risks.length > 0 ? `
          <div class="analysis-section">
            <h4>
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z"></path><line x1="12" y1="9" x2="12" y2="13"></line><line x1="12" y1="17" x2="12.01" y2="17"></line></svg>
              Risk Factors
            </h4>
            <ul class="risks-list">
              ${result.risks.map(risk => `<li>${risk}</li>`).join('')}
            </ul>
          </div>
        ` : ''}

        <!-- Price Targets -->
        ${result.targets ? `
          <div class="analysis-section">
            <h4>
              <svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><circle cx="12" cy="12" r="6"></circle><circle cx="12" cy="12" r="2"></circle></svg>
              Price Targets
            </h4>
            <div class="price-targets">
              ${result.targets.support ? `<div class="target support"><span>Support</span><strong>$${result.targets.support.toLocaleString()}</strong></div>` : ''}
              ${result.targets.resistance ? `<div class="target resistance"><span>Resistance</span><strong>$${result.targets.resistance.toLocaleString()}</strong></div>` : ''}
              ${result.targets.target ? `<div class="target primary"><span>Target</span><strong>$${result.targets.target.toLocaleString()}</strong></div>` : ''}
            </div>
          </div>
        ` : ''}

        <!-- Disclaimer -->
        <div class="disclaimer">
          <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>
          <span>This analysis is for informational purposes only and should not be considered financial advice. Always do your own research.</span>
        </div>
      </div>
    `;
  }

  getDecisionClass(decision) {
    const d = decision.toUpperCase();
    if (d.includes('BUY') || d.includes('BULLISH')) return 'bullish';
    if (d.includes('SELL') || d.includes('BEARISH')) return 'bearish';
    return 'neutral';
  }

  getSignalIcon(type) {
    if (type === 'bullish' || type === 'positive') {
      return '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 6 13.5 15.5 8.5 10.5 1 18"></polyline><polyline points="17 6 23 6 23 12"></polyline></svg>';
    }
    if (type === 'bearish' || type === 'negative') {
      return '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><polyline points="23 18 13.5 8.5 8.5 13.5 1 6"></polyline><polyline points="17 18 23 18 23 12"></polyline></svg>';
    }
    return '<svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="5" y1="12" x2="19" y2="12"></line></svg>';
  }
}

// Initialize page
const page = new AIAnalystPage();
window.analystPage = page;

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => page.init());
} else {
  page.init();
}
