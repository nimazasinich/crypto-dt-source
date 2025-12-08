/**
 * Model Status Widget
 * Displays AI model status with health indicators
 */

import { modelsClient } from '../core/models-client.js';

/**
 * Get models page path (works from any location)
 */
function getModelsPagePath() {
  const basePath = window.location.pathname.includes('/static/') 
    ? window.location.pathname.split('/static/')[0] + '/static'
    : '/static';
  return `${basePath}/pages/models/index.html`;
}

/**
 * Render model status widget
 */
export async function renderModelStatusWidget(containerId) {
  const container = document.getElementById(containerId);
  if (!container) {
    console.error(`Container ${containerId} not found`);
    return;
  }

  // Show loading state
  container.innerHTML = `
    <div class="model-status-widget loading">
      <div class="spinner"></div>
      <p>Loading AI models status...</p>
    </div>
  `;

  try {
    // Fetch models summary
    const summary = await modelsClient.getModelsSummary();
    
    if (!summary.ok) {
      container.innerHTML = `
        <div class="model-status-widget error">
          <h3>⚠️ Models Status</h3>
          <p class="error-message">${summary.error || 'Failed to load models'}</p>
          <p class="fallback-note">Using fallback sentiment analysis</p>
        </div>
      `;
      return;
    }

    const stats = summary.summary;
    
    // Render widget
    container.innerHTML = `
      <div class="model-status-widget">
        <div class="widget-header">
          <h3>🤖 AI Models</h3>
          <span class="hf-mode-badge">${stats.hf_mode}</span>
        </div>

        <div class="stats-grid">
          <div class="stat-card">
            <div class="stat-value">${stats.total_models}</div>
            <div class="stat-label">Total</div>
          </div>
          <div class="stat-card loaded">
            <div class="stat-value">${stats.loaded_models}</div>
            <div class="stat-label">Loaded</div>
          </div>
          <div class="stat-card ${stats.failed_models > 0 ? 'warning' : ''}">
            <div class="stat-value">${stats.failed_models}</div>
            <div class="stat-label">Failed</div>
          </div>
        </div>

        <div class="categories-section">
          <h4>Models by Category</h4>
          <div id="${containerId}-categories" class="categories-list"></div>
        </div>

        <div class="widget-footer">
          <button onclick="window.location.href=getModelsPagePath()" class="btn-view-all">
            View All Models →
          </button>
        </div>
      </div>
    `;

    // Render categories
    renderCategories(`${containerId}-categories`, summary.categories);

  } catch (error) {
    console.error('Error rendering model status widget:', error);
    container.innerHTML = `
      <div class="model-status-widget error">
        <h3>⚠️ Models Status</h3>
        <p class="error-message">Failed to load: ${error.message}</p>
      </div>
    `;
  }
}

/**
 * Render categories
 */
function renderCategories(containerId, categories) {
  const container = document.getElementById(containerId);
  if (!container || !categories) return;

  let html = '';
  
  for (const [category, models] of Object.entries(categories)) {
    const loaded = models.filter(m => m.loaded).length;
    const healthy = models.filter(m => m.status === 'healthy').length;
    
    html += `
      <div class="category-item">
        <div class="category-header">
          <span class="category-name">${formatCategoryName(category)}</span>
          <span class="category-count">${loaded}/${models.length}</span>
        </div>
        <div class="category-progress">
          <div class="progress-fill" style="width: ${(loaded / models.length * 100)}%"></div>
        </div>
      </div>
    `;
  }

  container.innerHTML = html;
}

/**
 * Format category name
 */
function formatCategoryName(category) {
  const names = {
    'sentiment_crypto': 'Crypto Sentiment',
    'sentiment_social': 'Social Sentiment',
    'sentiment_financial': 'Financial Sentiment',
    'sentiment_news': 'News Sentiment',
    'analysis_generation': 'AI Analysis',
    'trading_signal': 'Trading Signals',
    'summarization': 'Summarization',
    'legacy': 'Legacy'
  };
  
  return names[category] || category;
}

/**
 * CSS for model status widget (to be injected)
 */
export const modelStatusWidgetCSS = `
  .model-status-widget {
    background: rgba(255, 255, 255, 0.03);
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-radius: 16px;
    padding: 1.5rem;
  }

  .model-status-widget.loading {
    text-align: center;
    padding: 2rem;
  }

  .model-status-widget.error {
    border-color: rgba(239, 68, 68, 0.3);
    background: rgba(239, 68, 68, 0.1);
  }

  .widget-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 1.5rem;
  }

  .widget-header h3 {
    margin: 0;
    font-size: 1.25rem;
    font-weight: 600;
  }

  .hf-mode-badge {
    padding: 0.25rem 0.75rem;
    background: rgba(45, 212, 191, 0.2);
    border: 1px solid rgba(45, 212, 191, 0.3);
    border-radius: 999px;
    font-size: 0.75rem;
    font-weight: 600;
    text-transform: uppercase;
  }

  .stats-grid {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 1rem;
    margin-bottom: 1.5rem;
  }

  .stat-card {
    text-align: center;
    padding: 1rem;
    background: rgba(0, 0, 0, 0.3);
    border-radius: 12px;
  }

  .stat-card.loaded {
    background: rgba(34, 197, 94, 0.1);
    border: 1px solid rgba(34, 197, 94, 0.2);
  }

  .stat-card.warning {
    background: rgba(239, 68, 68, 0.1);
    border: 1px solid rgba(239, 68, 68, 0.2);
  }

  .stat-value {
    font-size: 2rem;
    font-weight: 700;
    color: #2dd4bf;
  }

  .stat-label {
    font-size: 0.875rem;
    color: rgba(255, 255, 255, 0.6);
    margin-top: 0.25rem;
  }

  .categories-section h4 {
    font-size: 1rem;
    font-weight: 600;
    margin-bottom: 1rem;
    color: rgba(255, 255, 255, 0.8);
  }

  .categories-list {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }

  .category-item {
    padding: 0.75rem;
    background: rgba(0, 0, 0, 0.2);
    border-radius: 8px;
  }

  .category-header {
    display: flex;
    justify-content: space-between;
    margin-bottom: 0.5rem;
  }

  .category-name {
    font-weight: 500;
  }

  .category-count {
    color: rgba(255, 255, 255, 0.6);
    font-size: 0.875rem;
  }

  .category-progress {
    height: 4px;
    background: rgba(255, 255, 255, 0.1);
    border-radius: 999px;
    overflow: hidden;
  }

  .progress-fill {
    height: 100%;
    background: linear-gradient(90deg, #2dd4bf, #818cf8);
    transition: width 0.3s;
  }

  .widget-footer {
    margin-top: 1.5rem;
    text-align: center;
  }

  .btn-view-all {
    padding: 0.75rem 1.5rem;
    background: linear-gradient(135deg, #2dd4bf, #818cf8);
    border: none;
    border-radius: 8px;
    color: white;
    font-weight: 600;
    cursor: pointer;
    transition: transform 0.2s;
  }

  .btn-view-all:hover {
    transform: translateY(-2px);
  }

  .error-message {
    color: #fca5a5;
    margin: 0.5rem 0;
  }

  .fallback-note {
    color: rgba(255, 255, 255, 0.6);
    font-size: 0.875rem;
    margin-top: 0.5rem;
  }
`;

