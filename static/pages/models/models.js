/**
 * AI Models Page - Hugging Face Integration
 * Fixed version with proper error handling
 */

import { APIHelper } from '../../shared/js/utils/api-helper.js';
import { modelsClient } from '../../shared/js/core/models-client.js';
import { api } from '../../shared/js/core/api-client.js';
import logger from '../../shared/js/utils/logger.js';

class ModelsPage {
  constructor() {
    this.models = [];
    this.allModels = [];
    this.activeFilters = { category: 'all', status: 'all' };
    this.refreshInterval = null;
  }

  async init() {
    try {
      console.log('[Models] Initializing...');
      
      this.bindEvents();
      await this.loadModels();
      await this.loadHealth();
      
      this.refreshInterval = setInterval(() => this.loadModels(), 60000);
      
      this.showToast('Models page ready', 'success');
    } catch (error) {
      console.error('[Models] Init error:', error);
      this.showToast('Failed to load models', 'error');
    }
  }

  createTimeoutSignal(ms = 10000) {
    // Prefer AbortSignal.timeout when available, fallback to AbortController.
    if (typeof AbortSignal !== 'undefined' && typeof AbortSignal.timeout === 'function') {
      return AbortSignal.timeout(ms);
    }
    const controller = new AbortController();
    setTimeout(() => controller.abort(), ms);
    return controller.signal;
  }

  bindEvents() {
    // Refresh button
    const refreshBtn = document.getElementById('refresh-btn');
    if (refreshBtn) {
      refreshBtn.addEventListener('click', () => {
        this.loadModels();
      });
    }

    // Tab switching
    document.querySelectorAll('.tab-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const tabId = e.currentTarget.dataset.tab;
        this.switchTab(tabId);
      });
    });

    // Test model button
    const runTestBtn = document.getElementById('run-test-btn');
    if (runTestBtn) {
      runTestBtn.addEventListener('click', () => {
        this.runTest();
      });
    }

    // Clear test button
    const clearTestBtn = document.getElementById('clear-test-btn');
    if (clearTestBtn) {
      clearTestBtn.addEventListener('click', () => {
        this.clearTest();
      });
    }

    // Example buttons
    document.querySelectorAll('.example-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const text = e.currentTarget.dataset.text;
        const testInput = document.getElementById('test-input');
        if (testInput) {
          testInput.value = text;
        }
      });
    });

    // Re-initialize all button
    const reinitBtn = document.getElementById('reinit-all-btn');
    if (reinitBtn) {
      reinitBtn.addEventListener('click', () => {
        this.reinitializeAll();
      });
    }

    // Filters
    const categoryFilter = document.getElementById('category-filter');
    if (categoryFilter) {
      categoryFilter.addEventListener('change', (e) => {
        this.activeFilters.category = e.target.value || 'all';
        this.applyFilters();
      });
    }

    const statusFilter = document.getElementById('status-filter');
    if (statusFilter) {
      statusFilter.addEventListener('change', (e) => {
        this.activeFilters.status = e.target.value || 'all';
        this.applyFilters();
      });
    }
  }

  switchTab(tabId) {
    // Remove active class from all tabs and contents
    document.querySelectorAll('.tab-btn').forEach(btn => {
      btn.classList.remove('active');
    });
    document.querySelectorAll('.tab-content').forEach(content => {
      content.classList.remove('active');
    });

    // Add active class to selected tab and content
    const selectedBtn = document.querySelector(`[data-tab="${tabId}"]`);
    const selectedContent = document.getElementById(`tab-${tabId}`);

    if (selectedBtn) {
      selectedBtn.classList.add('active');
    }

    if (selectedContent) {
      selectedContent.classList.add('active');
    }

    console.log(`[Models] Switched to tab: ${tabId}`);
  }

  async loadModels() {
    const container = document.getElementById('models-grid') || document.getElementById('models-container') || document.querySelector('.models-list');
    
    // Show loading state
    if (container) {
      container.innerHTML = `
        <div class="loading-state">
          <div class="loading-spinner"></div>
          <p class="loading-text">Loading AI models...</p>
        </div>
      `;
    }
    
    try {
      logger.info('Models', 'Loading models data...');
      let payload = null;
      let rawModels = [];
      
      // Strategy 1: Try /api/models/list endpoint
      try {
        logger.debug('Models', 'Attempting to load via /api/models/list...');
        const response = await fetch('/api/models/list', {
          method: 'GET',
          headers: { 'Content-Type': 'application/json' },
          signal: this.createTimeoutSignal(10000)
        });
        
        if (response.ok) {
          payload = await response.json();
          
          // Extract models array
          if (Array.isArray(payload.models)) {
            rawModels = payload.models;
            logger.info('Models', `Loaded ${rawModels.length} models via /api/models/list`);
          }
        }
      } catch (e) {
        logger.warn('Models', '/api/models/list failed:', e?.message || 'Unknown error');
      }

      // Strategy 2: Try /api/models/status if first failed
      if (!payload || rawModels.length === 0) {
        try {
          logger.debug('Models', 'Attempting to load via /api/models/status...');
          const response = await fetch('/api/models/status', {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' },
            signal: this.createTimeoutSignal(10000)
          });
          
          if (response.ok) {
            const statusData = await response.json();
            payload = statusData;
            
            // Try to get models from model_info
            if (statusData.model_info?.models) {
              rawModels = Object.values(statusData.model_info.models);
              logger.info('Models', `Loaded ${rawModels.length} models via /api/models/status`);
            }
          }
        } catch (e) {
          logger.warn('Models', '/api/models/status failed:', e?.message || 'Unknown error');
        }
      }

      // Strategy 3: Try /api/models/summary endpoint
      if (!payload || rawModels.length === 0) {
        try {
          logger.debug('Models', 'Attempting to load via /api/models/summary...');
          const response = await fetch('/api/models/summary', {
            method: 'GET',
            headers: { 'Content-Type': 'application/json' },
            signal: this.createTimeoutSignal(10000)
          });
          
          if (response.ok) {
            const summaryData = await response.json();
            payload = summaryData;
            
            // Extract from categories
            if (summaryData.categories) {
              for (const [category, categoryModels] of Object.entries(summaryData.categories)) {
                if (Array.isArray(categoryModels)) {
                  rawModels.push(...categoryModels);
                }
              }
              logger.info('Models', `Loaded ${rawModels.length} models via /api/models/summary`);
            }
          }
        } catch (e) {
          logger.warn('Models', '/api/models/summary failed:', e?.message || 'Unknown error');
        }
      }

      // Process models if we got any data
      if (Array.isArray(rawModels) && rawModels.length > 0) {
        this.models = rawModels.map((m, idx) => {
          // تشخیص status با دقت بیشتر
          const isLoaded = m.loaded === true || m.status === 'ready' || m.status === 'healthy' || m.status === 'loaded';
          const isFailed = m.failed === true || m.error || m.status === 'failed' || m.status === 'unavailable' || m.status === 'error';
          
          return {
            key: m.key || m.id || m.model_id || `model_${idx}`,
            name: m.name || m.model_name || m.model_id?.split('/').pop() || 'AI Model',
            model_id: m.model_id || m.id || m.name || 'unknown/model',
            category: m.category || m.provider || 'Hugging Face',
            task: m.task || m.type || 'Sentiment Analysis',
            loaded: isLoaded,
            failed: isFailed,
            requires_auth: Boolean(m.requires_auth || m.authentication || m.needs_token),
            status: isLoaded ? 'loaded' : isFailed ? 'failed' : 'available',
            error_count: Number(m.error_count || m.errors || 0),
            description: m.description || m.desc || `${m.name || m.model_id || 'Model'} - ${m.task || 'AI Model'}`,
            // فیلدهای اضافی برای debug
            success_rate: m.success_rate || (isLoaded ? 100 : isFailed ? 0 : null),
            last_used: m.last_used || m.last_access || null
          };
        });
        logger.info('Models', `Successfully processed ${this.models.length} models`);
        logger.debug('Models', 'Sample model:', this.models[0]);
      } else {
        logger.warn('Models', 'No models found in any endpoint, using fallback data');
        this.models = this.getFallbackModels();
      }

      this.allModels = [...this.models];
      this.applyFilters(false);
      this.renderCatalog();

      // Update stats from payload or calculate from models
      const stats = {
        total_models: payload?.total || payload?.total_models || this.models.length,
        models_loaded: payload?.models_loaded || payload?.loaded_models || this.models.filter(m => m.loaded).length,
        models_failed: payload?.models_failed || payload?.failed_models || this.models.filter(m => m.failed).length,
        hf_mode: payload?.hf_mode || (payload ? 'API' : 'Fallback'),
        hf_status: payload ? 'Connected' : 'Using fallback data',
        transformers_available: payload?.transformers_available || false
      };

      this.renderStats(stats);
      this.updateTimestamp();
      
      // Populate test model select
      this.populateTestModelSelect();
      
    } catch (error) {
      logger.error('Models', 'Load error:', error?.message || 'Unknown error');
      
      // Show error message
      this.showToast(`Failed to load models: ${error?.message || 'Unknown error'}`, 'error');
      
      // Fallback to demo data
      this.models = this.getFallbackModels();
      this.allModels = [...this.models];
      this.applyFilters(false);
      this.renderCatalog();
      this.renderStats({ 
        total_models: this.models.length, 
        models_loaded: 0, 
        models_failed: 0, 
        hf_mode: 'Fallback', 
        hf_status: 'API unavailable - using fallback data',
        transformers_available: false
      });
      this.updateTimestamp();
    }
  }
  
  populateTestModelSelect() {
    const testModelSelect = document.getElementById('test-model-select');
    if (testModelSelect && this.models.length > 0) {
      // Allow testing any model key via backend (auto-fallback if unavailable)
      testModelSelect.innerHTML = '<option value="">Auto (best available)</option>';
      
      const sorted = [...this.models].sort((a, b) => (a.category || '').localeCompare(b.category || '') || (a.name || '').localeCompare(b.name || ''));
      sorted.forEach(model => {
        const option = document.createElement('option');
        option.value = model.key;
        option.textContent = `${model.name} (${model.category})`;
        testModelSelect.appendChild(option);
      });
    }
  }

  applyFilters(shouldRerender = true) {
    const category = this.activeFilters.category;
    const status = this.activeFilters.status;

    const filtered = (this.allModels || []).filter((m) => {
      const catOk = category === 'all' ? true : (m.category === category || (m.category || '').toLowerCase() === category.toLowerCase());
      const statusOk = status === 'all' ? true : (m.status === status || (status === 'available' && !m.loaded && !m.failed));
      return catOk && statusOk;
    });

    this.models = filtered;
    if (shouldRerender) {
      this.renderModels();
    } else {
      // For initial load path we still need to render once.
      this.renderModels();
    }
  }

  /**
   * Extract models array from various payload structures
   */
  extractModelsArray(payload) {
    if (!payload) return [];
    
    // Try different paths
    const paths = [
      payload.models,
      payload.model_info,
      payload.data,
      payload.categories ? Object.values(payload.categories).flat() : null
    ];
    
    for (const path of paths) {
      if (Array.isArray(path) && path.length > 0) {
        return path;
      }
    }
    
    return [];
  }

  getFallbackModels() {
    return [
      {
        key: 'sentiment_model',
        name: 'Sentiment Analysis',
        model_id: 'cardiffnlp/twitter-roberta-base-sentiment-latest',
        category: 'Hugging Face',
        task: 'Text Classification',
        loaded: false,
        failed: false,
        requires_auth: false,
        status: 'unknown',
        description: 'Advanced sentiment analysis for crypto market text. (Fallback - API unavailable)'
      },
      {
        key: 'market_analysis',
        name: 'Market Analysis',
        model_id: 'internal/coingecko-api',
        category: 'Market Data',
        task: 'Price Analysis',
        loaded: false,
        failed: false,
        requires_auth: false,
        status: 'unknown',
        description: 'Real-time market data analysis using CoinGecko API. (Fallback - API unavailable)'
      }
    ];
  }

  renderStats(data) {
    try {
      const stats = {
        'total-models': data.total_models ?? this.models.length,
        'active-models': data.models_loaded ?? this.models.filter(m => m.loaded).length,
        'failed-models': data.models_failed ?? this.models.filter(m => m.failed).length,
        'hf-mode': data.hf_mode ?? 'unknown',
        'hf-status': data.hf_status
      };

      for (const [id, value] of Object.entries(stats)) {
        const el = document.getElementById(id);
        if (el && value !== undefined) {
          el.textContent = value;
        }
      }
    } catch (err) {
      console.warn('[Models] renderStats skipped:', err?.message || 'Unknown error');
    }
  }

  renderModels() {
    const container = document.getElementById('models-grid') || document.getElementById('models-list');
    if (!container) {
      console.warn('[Models] Container not found');
      return;
    }

    if (!this.models || this.models.length === 0) {
      container.innerHTML = `
        <div class="empty-state glass-card" style="grid-column: 1 / -1;">
          <div class="empty-icon">🤖</div>
          <h3>No models loaded</h3>
          <p>Models will be loaded on demand when needed for AI features.</p>
          <button class="btn-gradient" onclick="window.modelsPage?.loadModels()">
            <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 4 23 10 17 10"></polyline><polyline points="1 20 1 14 7 14"></polyline><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path></svg>
            Retry
          </button>
        </div>
      `;
      return;
    }

    container.innerHTML = this.models.map(model => {
      const statusClass = model.loaded ? 'loaded' : model.failed ? 'failed' : 'available';
      const statusText = model.loaded ? 'Loaded' : model.failed ? 'Failed' : 'Available';
      const statusBadgeClass = model.loaded ? 'loaded' : model.failed ? 'failed' : 'available';

      return `
        <div class="model-card ${statusClass}">
          <div class="model-header">
            <div class="model-icon">
              <svg xmlns="http://www.w3.org/2000/svg" width="32" height="32" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 4.44-2z"></path><path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-4.44-2z"></path></svg>
            </div>
            <div class="model-info">
              <h3 class="model-name">${model.name}</h3>
              <p class="model-type">${model.category}</p>
            </div>
            <div class="model-status ${statusBadgeClass}">
              ${statusText}
            </div>
          </div>
          
          <div class="model-body">
            <div class="model-id">${model.model_id}</div>
            
            <div class="model-meta">
              <span class="meta-badge">
                <svg xmlns="http://www.w3.org/2000/svg" width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><path d="M12 2v20M2 12h20"></path></svg>
                ${model.task}
              </span>
              <span class="meta-badge">
                ${model.requires_auth ? '🔒 Auth Required' : '🔓 Public'}
              </span>
              ${model.error_count > 0 ? `<span class="meta-badge">⚠️ ${model.error_count} errors</span>` : ''}
            </div>
          </div>
          
          <div class="model-footer">
            <button class="btn" onclick="window.modelsPage?.testModel('${model.key}')" ${!model.loaded ? 'disabled' : ''} title="${model.loaded ? 'Test this model' : 'Model not loaded'}">
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
              Test
            </button>
            <button class="btn" onclick="window.modelsPage?.viewModelDetails('${model.key}')" title="View model details">
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>
              Info
            </button>
            ${model.failed ? `<button class="btn reinit" onclick="window.modelsPage?.reinitModel('${model.key}')" title="Retry loading this model">
              <svg xmlns="http://www.w3.org/2000/svg" width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="23 4 23 10 17 10"></polyline><path d="M21 14a9 9 0 0 1-18 0 9 9 0 0 1 18 0"></path></svg>
              Retry
            </button>` : ''}
          </div>
        </div>
      `;
    }).join('');
  }
  
  reinitModel(modelKey) {
    this.showToast(`Reinitializing model: ${modelKey}...`, 'info');
    // TODO: Implement model reinitialization
    setTimeout(() => {
      this.showToast('Model reinitialization not yet implemented', 'warning');
    }, 1000);
  }

  viewModelDetails(modelKey) {
    const model = this.models.find(m => m.key === modelKey);
    if (!model) return;
    this.showToast(`Model: ${model.name} - ${model.model_id}`, 'info');
  }

  async testModel(modelId) {
    this.showToast('Testing model...', 'info');
    
    try {
      const response = await fetch('/api/sentiment/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ 
          text: 'Bitcoin is going to the moon! 🚀',
          mode: 'crypto',
          model_key: modelId,
          use_ensemble: false
        }),
        signal: this.createTimeoutSignal(10000)
      });
      
      if (response.ok) {
        const result = await response.json();
        
        if (result && result.sentiment) {
          this.showToast(
            `Test successful: ${result.sentiment} (${(result.score * 100).toFixed(0)}%)`,
            'success'
          );
        } else {
          this.showToast('Test completed but no sentiment data returned', 'warning');
        }
      } else {
        this.showToast('Test failed: API error', 'error');
      }
    } catch (error) {
      console.error('[Models] Test failed:', error);
      this.showToast(`Test failed: ${error?.message || 'Unknown error'}`, 'error');
    }
  }

  updateTimestamp() {
    const el = document.getElementById('last-update');
    if (el) {
      el.textContent = `Updated: ${new Date().toLocaleTimeString()}`;
    }
  }

  async runTest() {
    const input = document.getElementById('test-input');
    const resultDiv = document.getElementById('test-result');
    const modelSelect = document.getElementById('test-model-select');

    if (!input || !input.value.trim()) {
      this.showToast('Please enter text to analyze', 'warning');
      return;
    }

    const text = input.value.trim();
    const modelKey = modelSelect?.value || '';

    this.showToast('Analyzing...', 'info');

    try {
      const response = await fetch('/api/sentiment/analyze', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          text,
          mode: 'crypto',
          model_key: modelKey || undefined,
          use_ensemble: !modelKey
        }),
        signal: this.createTimeoutSignal(10000)
      });

      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`);
      }

      const result = await response.json();

      // Show result
      if (resultDiv) {
        resultDiv.classList.remove('hidden');
      }

      // Update sentiment display
      const emoji = this.getSentimentEmoji(result.sentiment);
      const emojiEl = document.getElementById('sentiment-emoji');
      const labelEl = document.getElementById('sentiment-label');
      const confidenceEl = document.getElementById('sentiment-confidence');
      const displayEl = document.getElementById('sentiment-display');
      const timeEl = document.getElementById('result-time');
      const jsonPre = document.querySelector('.result-json');

      if (emojiEl) emojiEl.textContent = emoji;
      const sentimentKey = (result.sentiment || 'unknown').toString().toLowerCase();
      if (displayEl) {
        displayEl.setAttribute('data-sentiment', sentimentKey);
        const pct = (typeof result.score === 'number' ? result.score : 0) * 100;
        displayEl.style.setProperty('--confidence', `${Math.max(0, Math.min(100, pct)).toFixed(1)}%`);
      }
      if (labelEl) {
        labelEl.textContent = result.sentiment || 'Unknown';
        // Ensure CSS sentiment variants can apply reliably
        labelEl.classList.remove('bullish', 'bearish', 'neutral', 'positive', 'negative', 'buy', 'sell', 'hold', 'unknown');
        labelEl.classList.add(sentimentKey);
      }
      if (confidenceEl) {
        const pct = (typeof result.score === 'number' ? result.score : 0) * 100;
        confidenceEl.textContent = `Confidence: ${Math.max(0, Math.min(100, pct)).toFixed(1)}%`;
      }
      if (timeEl) timeEl.textContent = new Date().toLocaleTimeString();
      if (jsonPre) jsonPre.textContent = JSON.stringify(result, null, 2);

      this.showToast('Analysis complete!', 'success');
    } catch (error) {
      console.error('[Models] Test error:', error);
      this.showToast(`Analysis failed: ${error?.message || 'Unknown error'}`, 'error');
    }
  }

  async loadHealth() {
    const container = document.getElementById('health-grid');
    if (!container) return;

    container.innerHTML = `
      <div class="loading-state">
        <div class="loading-spinner"></div>
        <p class="loading-text">Loading health data...</p>
      </div>
    `;

    try {
      const res = await fetch('/api/models/health', {
        method: 'GET',
        headers: { 'Content-Type': 'application/json' },
        signal: this.createTimeoutSignal(10000)
      });
      if (!res.ok) throw new Error(`HTTP ${res.status}`);
      const data = await res.json();

      const health = Array.isArray(data.health) ? data.health : (data.health ? Object.values(data.health) : []);
      if (!health.length) {
        container.innerHTML = `
          <div class="empty-state glass-card" style="grid-column: 1 / -1;">
            <div class="empty-icon">🏥</div>
            <h3>No health data</h3>
            <p>Health registry is empty (models may be running in fallback mode).</p>
          </div>
        `;
        return;
      }

      container.innerHTML = health.map((h) => {
        const status = h.status || 'unknown';
        const statusClass = status === 'healthy' ? 'loaded' : status === 'unavailable' ? 'failed' : 'available';
        const name = h.name || h.key || 'model';
        return `
          <div class="model-card ${statusClass}">
            <div class="model-header">
              <div class="model-info">
                <h3 class="model-name">${name}</h3>
                <p class="model-type">Health: ${status}</p>
              </div>
              <div class="model-status ${statusClass}">${status}</div>
            </div>
            <div class="model-body">
              <div class="model-meta">
                <span class="meta-badge">✅ ${Number(h.success_count || 0)} success</span>
                <span class="meta-badge">⚠️ ${Number(h.error_count || 0)} errors</span>
              </div>
            </div>
          </div>
        `;
      }).join('');
    } catch (e) {
      container.innerHTML = `
        <div class="empty-state glass-card" style="grid-column: 1 / -1;">
          <div class="empty-icon">⚠️</div>
          <h3>Health data unavailable</h3>
          <p>${e?.message || 'Unable to fetch /api/models/health'}</p>
        </div>
      `;
    }
  }

  renderCatalog() {
    // Best-effort catalog fill; only runs if the catalog containers exist on this page.
    const buckets = {
      crypto: document.getElementById('catalog-crypto'),
      financial: document.getElementById('catalog-financial'),
      social: document.getElementById('catalog-social'),
      trading: document.getElementById('catalog-trading'),
      generation: document.getElementById('catalog-generation'),
      summarization: document.getElementById('catalog-summarization')
    };

    const hasAny = Object.values(buckets).some(Boolean);
    if (!hasAny) return;

    const byBucket = { crypto: [], financial: [], social: [], trading: [], generation: [], summarization: [] };
    (this.allModels || []).forEach((m) => {
      const cat = (m.category || '').toLowerCase();
      if (cat.includes('crypto')) byBucket.crypto.push(m);
      else if (cat.includes('financial')) byBucket.financial.push(m);
      else if (cat.includes('social')) byBucket.social.push(m);
      else if (cat.includes('trading')) byBucket.trading.push(m);
      else if (cat.includes('generation') || cat.includes('gen')) byBucket.generation.push(m);
      else if (cat.includes('summar')) byBucket.summarization.push(m);
    });

    const renderList = (list) => list.map((m) => `
      <div class="catalog-model-item">
        <div class="catalog-model-name">${m.name}</div>
        <div class="catalog-model-id">${m.model_id}</div>
      </div>
    `).join('') || '<div class="empty-state"><p>No models in this category.</p></div>';

    if (buckets.crypto) buckets.crypto.innerHTML = renderList(byBucket.crypto);
    if (buckets.financial) buckets.financial.innerHTML = renderList(byBucket.financial);
    if (buckets.social) buckets.social.innerHTML = renderList(byBucket.social);
    if (buckets.trading) buckets.trading.innerHTML = renderList(byBucket.trading);
    if (buckets.generation) buckets.generation.innerHTML = renderList(byBucket.generation);
    if (buckets.summarization) buckets.summarization.innerHTML = renderList(byBucket.summarization);
  }

  getSentimentEmoji(sentiment) {
    const emojiMap = {
      'positive': '😊',
      'bullish': '📈',
      'negative': '😟',
      'bearish': '📉',
      'neutral': '😐',
      'buy': '🟢',
      'sell': '🔴',
      'hold': '🟡'
    };
    return emojiMap[sentiment?.toLowerCase()] || '📊';
  }

  clearTest() {
    const input = document.getElementById('test-input');
    const resultDiv = document.getElementById('test-result');

    if (input) {
      input.value = '';
    }

    if (resultDiv) {
      resultDiv.classList.add('hidden');
    }
  }

  async reinitializeAll() {
    this.showToast('Re-initializing all models...', 'info');

    try {
      const response = await fetch('/api/models/reinitialize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        signal: this.createTimeoutSignal(30000)
      });

      if (response.ok) {
        this.showToast('Models re-initialized successfully!', 'success');
        await this.loadModels();
      } else {
        throw new Error(`HTTP ${response.status}`);
      }
    } catch (error) {
      console.error('[Models] Re-initialize error:', error);
      this.showToast(`Re-initialization failed: ${error?.message || 'Unknown error'}`, 'error');
    }
  }

  showToast(message, type = 'info') {
    if (typeof APIHelper !== 'undefined' && APIHelper.showToast) {
      APIHelper.showToast(message, type);
    } else {
      console.log(`[Toast ${type}]`, message);
    }
  }
}

// Initialize
const modelsPage = new ModelsPage();
modelsPage.init();

// Expose globally for onclick handlers
window.modelsPage = modelsPage;
