/**
 * AI Models Client for Frontend Integration
 * Handles model status, health tracking, and sentiment analysis
 */

import { api } from './api-client.js';

/**
 * Models Client with status tracking and health monitoring
 */
export class ModelsClient {
  constructor() {
    this.models = [];
    this.healthRegistry = [];
    this.lastUpdate = null;
    this.statusCache = null;
  }

  /**
   * Get models summary with categories
   * Enhanced error handling and logging
   */
  async getModelsSummary() {
    try {
      console.log('[ModelsClient] Fetching models summary from /api/models/summary');
      const response = await api.get('/models/summary');
      
      // Validate response structure
      if (!response) {
        throw new Error('Empty response from /api/models/summary');
      }
      
      // Check if response indicates failure
      if (response.fallback === true || (response.ok === false && !response.summary)) {
        console.warn('[ModelsClient] Received fallback or error response:', response);
        // Still try to extract any available data
      }
      
      this.models = [];
      this.healthRegistry = response.health_registry || [];
      this.lastUpdate = new Date();
      this.statusCache = response;

      // Flatten categories into models array
      if (response.categories && typeof response.categories === 'object') {
        for (const [category, categoryModels] of Object.entries(response.categories)) {
          if (Array.isArray(categoryModels)) {
            categoryModels.forEach(model => {
              if (model && typeof model === 'object') {
                this.models.push({
                  ...model,
                  category
                });
              }
            });
          }
        }
      }

      // Log successful fetch
      const summary = response.summary || {};
      console.log('[ModelsClient] Models summary loaded:', {
        total: summary.total_models || 0,
        loaded: summary.loaded_models || 0,
        failed: summary.failed_models || 0,
        categories: Object.keys(response.categories || {}).length,
        healthEntries: this.healthRegistry.length
      });

      return response;
    } catch (error) {
      const safeError = error || new Error('Unknown error');
      console.error('[ModelsClient] Failed to get models summary:', safeError);
      console.error('[ModelsClient] Error details:', {
        message: safeError?.message || 'Unknown error',
        stack: safeError?.stack || 'No stack trace',
        name: safeError?.name || 'Error'
      });
      
      // Return structured fallback that matches expected format
      return {
        ok: false,
        error: safeError?.message || 'Unknown error',
        fallback: true,
        summary: {
          total_models: 0,
          loaded_models: 0,
          failed_models: 0,
          hf_mode: 'error',
          transformers_available: false
        },
        categories: {},
        health_registry: [],
        timestamp: new Date().toISOString()
      };
    }
  }

  /**
   * Get model status
   * Enhanced error handling and logging
   */
  async getModelsStatus() {
    try {
      console.log('[ModelsClient] Fetching models status from /api/models/status');
      const response = await api.getModelsStatus();
      
      // Validate response
      if (!response) {
        throw new Error('Empty response from /api/models/status');
      }
      
      // Log status
      console.log('[ModelsClient] Models status loaded:', {
        success: response.success,
        loaded: response.models_loaded || 0,
        failed: response.models_failed || 0,
        hf_mode: response.hf_mode || 'unknown'
      });
      
      return response;
    } catch (error) {
      const safeError = error || new Error('Unknown error');
      console.error('[ModelsClient] Failed to get models status:', safeError);
      console.error('[ModelsClient] Error details:', {
        message: safeError?.message || 'Unknown error',
        stack: safeError?.stack || 'No stack trace',
        name: safeError?.name || 'Error'
      });
      
      // Return fallback instead of throwing
      return {
        success: false,
        status: 'error',
        status_message: `Error retrieving model status: ${safeError?.message || 'Unknown error'}`,
        error: safeError?.message || 'Unknown error',
        models_loaded: 0,
        models_failed: 0,
        hf_mode: 'unknown',
        transformers_available: false,
        fallback: true,
        timestamp: new Date().toISOString()
      };
    }
  }

  /**
   * Get health registry
   * Enhanced with error handling
   */
  async getHealthRegistry() {
    try {
      const summary = await this.getModelsSummary();
      const registry = summary?.health_registry || [];
      console.log(`[ModelsClient] Health registry loaded: ${registry.length} entries`);
      return registry;
    } catch (error) {
      const safeError = error || new Error('Unknown error');
      console.error('[ModelsClient] Failed to get health registry:', safeError?.message || 'Unknown error');
      return [];
    }
  }

  /**
   * Test a specific model
   */
  async testModel(modelKey, text) {
    try {
      return await api.testModel(modelKey, text);
    } catch (error) {
      const safeError = error || new Error('Unknown error');
      console.error(`Failed to test model ${modelKey}:`, safeError);
      // Return fallback instead of throwing
      return {
        success: false,
        error: safeError?.message || 'Unknown error',
        model: modelKey,
        result: {
          sentiment: 'neutral',
          score: 0.5,
          confidence: 0.5
        },
        fallback: true
      };
    }
  }

  /**
   * Analyze sentiment using available models
   */
  async analyzeSentiment(text, mode = 'crypto', modelKey = null) {
    try {
      return await api.analyzeSentiment(text, mode, modelKey);
    } catch (error) {
      const safeError = error || new Error('Unknown error');
      console.error('Failed to analyze sentiment:', safeError);
      // Return fallback instead of throwing
      return {
        success: false,
        error: safeError?.message || 'Unknown error',
        sentiment: 'neutral',
        score: 0.5,
        confidence: 0.5,
        model: modelKey || 'fallback',
        fallback: true
      };
    }
  }

  /**
   * Get model by key
   */
  getModel(key) {
    return this.models.find(m => m.key === key);
  }

  /**
   * Get models by category
   */
  getModelsByCategory(category) {
    return this.models.filter(m => m.category === category);
  }

  /**
   * Get loaded models
   */
  getLoadedModels() {
    return this.models.filter(m => m.loaded);
  }

  /**
   * Get failed models
   */
  getFailedModels() {
    return this.models.filter(m => m.status === 'unavailable' || m.error_count > 0);
  }

  /**
   * Get healthy models
   */
  getHealthyModels() {
    return this.models.filter(m => m.status === 'healthy');
  }

  /**
   * Format model status for display
   */
  formatModelStatus(model) {
    const statusIcons = {
      'healthy': '✓',
      'degraded': '⚠',
      'unavailable': '✗',
      'unknown': '?'
    };

    const statusColors = {
      'healthy': '#22c55e',
      'degraded': '#f59e0b',
      'unavailable': '#ef4444',
      'unknown': '#64748b'
    };

    return {
      icon: statusIcons[model.status] || '?',
      color: statusColors[model.status] || '#64748b',
      text: model.status || 'unknown'
    };
  }

  /**
   * Get category statistics
   */
  getCategoryStats() {
    const stats = {};
    
    this.models.forEach(model => {
      const cat = model.category || 'other';
      if (!stats[cat]) {
        stats[cat] = {
          total: 0,
          loaded: 0,
          healthy: 0,
          degraded: 0,
          unavailable: 0
        };
      }
      
      stats[cat].total++;
      if (model.loaded) stats[cat].loaded++;
      if (model.status === 'healthy') stats[cat].healthy++;
      if (model.status === 'degraded') stats[cat].degraded++;
      if (model.status === 'unavailable') stats[cat].unavailable++;
    });

    return stats;
  }

  /**
   * Get summary statistics
   */
  getSummaryStats() {
    if (this.statusCache && this.statusCache.summary) {
      return this.statusCache.summary;
    }

    return {
      total_models: this.models.length,
      loaded_models: this.getLoadedModels().length,
      failed_models: this.getFailedModels().length,
      hf_mode: 'unknown',
      transformers_available: false
    };
  }

  /**
   * Force refresh models data (clears cache and fetches fresh data)
   */
  async refresh() {
    console.log('[ModelsClient] Force refreshing models data...');
    
    // Clear API client cache for models endpoints
    try {
      if (api && typeof api.clearCacheEntry === 'function') {
        api.clearCacheEntry('/models/summary');
        api.clearCacheEntry('/models/status');
        console.log('[ModelsClient] Cleared API cache for models endpoints');
      } else if (api && typeof api.clearCache === 'function') {
        // If clearCacheEntry doesn't exist, clear all cache
        api.clearCache();
        console.log('[ModelsClient] Cleared all API cache');
      }
    } catch (e) {
      console.warn('[ModelsClient] Failed to clear cache:', e);
    }
    
    // Clear local cache
    this.statusCache = null;
    this.models = [];
    this.healthRegistry = [];
    this.lastUpdate = null;
    
    // Fetch fresh data (skip cache)
    return await this.getModelsSummary();
  }

  /**
   * Check if models data is stale (older than specified milliseconds)
   */
  isStale(maxAge = 60000) {
    if (!this.lastUpdate) return true;
    return (Date.now() - this.lastUpdate.getTime()) > maxAge;
  }
}

/**
 * Export singleton instance
 */
export const modelsClient = new ModelsClient();
export default modelsClient;

console.log('[ModelsClient] Initialized');

