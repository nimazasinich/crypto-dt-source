/**
 * Dynamic Model Loader - Frontend Logic
 * سیستم هوشمند بارگذاری مدل - منطق فرانت‌اند
 */

const dynamicLoader = {
  apiBase: window.location.origin,
  registeredModels: [],
  
  /**
   * مقداردهی اولیه
   */
  async init() {
    console.log('🚀 Initializing Dynamic Model Loader...');
    
    // Load registered models
    await this.refreshModelsList();
    
    // Setup event listeners
    this.setupEventListeners();
    
    console.log('✅ Dynamic Model Loader initialized');
  },
  
  setupEventListeners() {
    // Manual form submission
    const manualForm = document.getElementById('manual-form');
    if (manualForm) {
      manualForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        await this.submitManualConfig();
      });
    }
  },
  
  /**
   * نمایش حالت‌های مختلف
   */
  showPasteMode() {
    this.closeAllModes();
    document.getElementById('paste-mode').style.display = 'block';
    document.getElementById('paste-input').focus();
  },
  
  showManualMode() {
    this.closeAllModes();
    document.getElementById('manual-mode').style.display = 'block';
    document.getElementById('manual-model-id').focus();
  },
  
  showAutoMode() {
    this.closeAllModes();
    document.getElementById('auto-mode').style.display = 'block';
    document.getElementById('auto-url').focus();
  },
  
  closeAllModes() {
    document.getElementById('paste-mode').style.display = 'none';
    document.getElementById('manual-mode').style.display = 'none';
    document.getElementById('auto-mode').style.display = 'none';
  },
  
  closeTestPanel() {
    document.getElementById('test-panel').style.display = 'none';
  },
  
  /**
   * پردازش کپی/پیست
   */
  async processPastedConfig() {
    const configText = document.getElementById('paste-input').value.trim();
    const autoDetect = document.getElementById('auto-detect-paste').checked;
    
    if (!configText) {
      this.showError('Please paste a configuration');
      return;
    }
    
    this.showInfo('Processing pasted configuration...');
    
    try {
      const response = await fetch(`${this.apiBase}/api/dynamic-models/paste-config`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          config_text: configText,
          auto_detect: autoDetect
        })
      });
      
      const data = await response.json();
      
      if (data.success) {
        this.showSuccess(`Model "${data.data.model_id}" registered successfully!`);
        await this.refreshModelsList();
        this.closeAllModes();
        document.getElementById('paste-input').value = '';
      } else {
        this.showError(data.error || 'Failed to process configuration');
      }
    } catch (error) {
      this.showError(`Error: ${error.message}`);
      console.error('Paste config error:', error);
    }
  },
  
  async testPastedConfig() {
    const configText = document.getElementById('paste-input').value.trim();
    
    if (!configText) {
      this.showError('Please paste a configuration');
      return;
    }
    
    this.showInfo('Testing configuration...');
    
    try {
      // Parse the config
      let parsedConfig;
      try {
        parsedConfig = JSON.parse(configText);
      } catch {
        this.showError('Invalid JSON. Please provide valid JSON configuration for testing.');
        return;
      }
      
      const response = await fetch(`${this.apiBase}/api/dynamic-models/test-connection`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(parsedConfig)
      });
      
      const data = await response.json();
      
      if (data.success && data.test_result.success) {
        this.showSuccess(`✅ Connection successful! (${Math.round(data.test_result.response_time_ms)}ms)`);
      } else {
        this.showError(`❌ Connection failed: ${data.test_result.error || 'Unknown error'}`);
      }
    } catch (error) {
      this.showError(`Test failed: ${error.message}`);
      console.error('Test error:', error);
    }
  },
  
  /**
   * ارسال فرم دستی
   */
  async submitManualConfig() {
    const config = {
      model_id: document.getElementById('manual-model-id').value.trim(),
      model_name: document.getElementById('manual-model-name').value.trim(),
      base_url: document.getElementById('manual-base-url').value.trim(),
      api_key: document.getElementById('manual-api-key').value.trim() || null,
      api_type: document.getElementById('manual-api-type').value === 'auto' 
        ? null 
        : document.getElementById('manual-api-type').value,
      endpoints: document.getElementById('manual-endpoint').value.trim() || null
    };
    
    const testFirst = document.getElementById('test-before-register').checked;
    
    if (testFirst) {
      this.showInfo('Testing connection first...');
      
      try {
        const testResponse = await fetch(`${this.apiBase}/api/dynamic-models/test-connection`, {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(config)
        });
        
        const testData = await testResponse.json();
        
        if (!testData.success || !testData.test_result.success) {
          const proceed = confirm(
            `Connection test failed: ${testData.test_result.error}\n\nDo you want to register anyway?`
          );
          if (!proceed) return;
        }
      } catch (error) {
        const proceed = confirm(
          `Test failed: ${error.message}\n\nDo you want to register anyway?`
        );
        if (!proceed) return;
      }
    }
    
    this.showInfo('Registering model...');
    
    try {
      const response = await fetch(`${this.apiBase}/api/dynamic-models/register`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config)
      });
      
      const data = await response.json();
      
      if (data.success) {
        this.showSuccess(`Model "${config.model_id}" registered successfully!`);
        await this.refreshModelsList();
        this.closeAllModes();
        document.getElementById('manual-form').reset();
      } else {
        this.showError(data.message || 'Registration failed');
      }
    } catch (error) {
      this.showError(`Error: ${error.message}`);
      console.error('Registration error:', error);
    }
  },
  
  async testManualConfig() {
    const config = {
      model_id: document.getElementById('manual-model-id').value.trim(),
      model_name: document.getElementById('manual-model-name').value.trim(),
      base_url: document.getElementById('manual-base-url').value.trim(),
      api_key: document.getElementById('manual-api-key').value.trim() || null,
      api_type: document.getElementById('manual-api-type').value === 'auto' 
        ? null 
        : document.getElementById('manual-api-type').value
    };
    
    if (!config.base_url) {
      this.showError('Please enter a base URL');
      return;
    }
    
    this.showInfo('Testing connection...');
    
    try {
      const response = await fetch(`${this.apiBase}/api/dynamic-models/test-connection`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(config)
      });
      
      const data = await response.json();
      
      if (data.success && data.test_result.success) {
        this.showSuccess(
          `✅ Connection successful!\n` +
          `API Type: ${data.test_result.api_type}\n` +
          `Response Time: ${Math.round(data.test_result.response_time_ms)}ms\n` +
          `Capabilities: ${data.test_result.detected_capabilities.join(', ')}`
        );
      } else {
        this.showError(
          `❌ Connection failed:\n${data.test_result.error || 'Unknown error'}`
        );
      }
    } catch (error) {
      this.showError(`Test failed: ${error.message}`);
      console.error('Test error:', error);
    }
  },
  
  /**
   * تنظیم خودکار از URL
   */
  async autoConfigureFromURL() {
    const url = document.getElementById('auto-url').value.trim();
    
    if (!url) {
      this.showError('Please enter a URL');
      return;
    }
    
    this.showInfo('Auto-configuring model...');
    
    try {
      const response = await fetch(`${this.apiBase}/api/dynamic-models/auto-configure`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ url })
      });
      
      const data = await response.json();
      
      if (data.success) {
        this.showSuccess(
          `✅ Model auto-configured and registered!\n` +
          `Model ID: ${data.config.model_id}\n` +
          `API Type: ${data.config.api_type}\n` +
          `Endpoints discovered: ${Object.keys(data.config.endpoints?.endpoints || {}).length}`
        );
        await this.refreshModelsList();
        this.closeAllModes();
        document.getElementById('auto-url').value = '';
      } else {
        this.showError(data.error || 'Auto-configuration failed');
      }
    } catch (error) {
      this.showError(`Error: ${error.message}`);
      console.error('Auto-configure error:', error);
    }
  },
  
  /**
   * بازخوانی لیست مدل‌ها
   */
  async refreshModelsList() {
    const container = document.getElementById('models-list');
    
    try {
      const response = await fetch(`${this.apiBase}/api/dynamic-models/models`);
      const data = await response.json();
      
      if (data.success) {
        this.registeredModels = data.models;
        this.renderModelsList(data.models);
      } else {
        container.innerHTML = '<p class="error-text">Failed to load models</p>';
      }
    } catch (error) {
      console.error('Failed to load models:', error);
      container.innerHTML = '<p class="error-text">Error loading models</p>';
    }
  },
  
  renderModelsList(models) {
    const container = document.getElementById('models-list');
    
    if (models.length === 0) {
      container.innerHTML = `
        <div class="empty-state">
          <p>No models registered yet</p>
          <p class="text-secondary">Click one of the quick action buttons above to register your first model</p>
        </div>
      `;
      return;
    }
    
    container.innerHTML = models.map(model => `
      <div class="model-card" data-model-id="${model.model_id}">
        <div class="model-header">
          <div class="model-info">
            <h4>${this.escapeHtml(model.model_name)}</h4>
            <span class="model-type">${model.api_type || 'unknown'}</span>
          </div>
          <div class="model-actions">
            <button 
              class="btn-icon" 
              title="Test model"
              onclick="dynamicLoader.openTestModel('${model.model_id}')"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polygon points="5 3 19 12 5 21 5 3"></polygon></svg>
            </button>
            <button 
              class="btn-icon" 
              title="View details"
              onclick="dynamicLoader.viewModelDetails('${model.model_id}')"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><circle cx="12" cy="12" r="10"></circle><line x1="12" y1="16" x2="12" y2="12"></line><line x1="12" y1="8" x2="12.01" y2="8"></line></svg>
            </button>
            <button 
              class="btn-icon btn-danger" 
              title="Delete model"
              onclick="dynamicLoader.deleteModel('${model.model_id}')"
            >
              <svg xmlns="http://www.w3.org/2000/svg" width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2"><polyline points="3 6 5 6 21 6"></polyline><path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path></svg>
            </button>
          </div>
        </div>
        <div class="model-details">
          <div><strong>ID:</strong> ${this.escapeHtml(model.model_id)}</div>
          <div><strong>URL:</strong> ${this.escapeHtml(model.base_url)}</div>
          ${model.api_key ? '<div><strong>Auth:</strong> Yes (API key set)</div>' : ''}
        </div>
        <div class="model-meta">
          <span>Created: ${new Date(model.created_at).toLocaleString()}</span>
          ${model.last_used_at ? `<span>Last used: ${new Date(model.last_used_at).toLocaleString()}</span>` : ''}
          <span>Uses: ${model.use_count || 0}</span>
        </div>
      </div>
    `).join('');
  },
  
  /**
   * عملیات روی مدل‌ها
   */
  openTestModel(modelId) {
    // Populate test panel
    const select = document.getElementById('test-model-select');
    select.innerHTML = this.registeredModels.map(m => 
      `<option value="${m.model_id}" ${m.model_id === modelId ? 'selected' : ''}>${m.model_name}</option>`
    ).join('');
    
    // Show test panel
    document.getElementById('test-panel').style.display = 'block';
    document.getElementById('test-panel').scrollIntoView({ behavior: 'smooth' });
  },
  
  async executeTest() {
    const modelId = document.getElementById('test-model-select').value;
    const endpoint = document.getElementById('test-endpoint').value.trim();
    const payloadText = document.getElementById('test-payload').value.trim();
    
    if (!modelId) {
      this.showError('Please select a model');
      return;
    }
    
    let payload;
    try {
      payload = JSON.parse(payloadText || '{}');
    } catch {
      this.showError('Invalid JSON payload');
      return;
    }
    
    this.showInfo('Testing model...');
    
    const resultDiv = document.getElementById('test-result');
    resultDiv.innerHTML = '<div class="spinner"></div><p>Running test...</p>';
    
    try {
      const response = await fetch(
        `${this.apiBase}/api/dynamic-models/models/${modelId}/use`,
        {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ endpoint, payload })
        }
      );
      
      const data = await response.json();
      
      if (data.success) {
        this.showSuccess(`Test completed in ${Math.round(data.data.response_time_ms)}ms`);
        resultDiv.innerHTML = `
          <div class="success-banner">✅ Test Successful</div>
          <div><strong>Response Time:</strong> ${Math.round(data.data.response_time_ms)}ms</div>
          <div><strong>Response Data:</strong></div>
          <pre>${JSON.stringify(data.data.data, null, 2)}</pre>
        `;
      } else {
        this.showError('Test failed');
        resultDiv.innerHTML = `
          <div class="error-banner">❌ Test Failed</div>
          <div><strong>Error:</strong> ${data.error}</div>
        `;
      }
    } catch (error) {
      this.showError(`Test error: ${error.message}`);
      resultDiv.innerHTML = `
        <div class="error-banner">❌ Error</div>
        <div>${error.message}</div>
      `;
    }
  },
  
  viewModelDetails(modelId) {
    const model = this.registeredModels.find(m => m.model_id === modelId);
    if (!model) return;
    
    alert(`
Model Details:
--------------
ID: ${model.model_id}
Name: ${model.model_name}
API Type: ${model.api_type}
Base URL: ${model.base_url}
Created: ${new Date(model.created_at).toLocaleString()}
Use Count: ${model.use_count || 0}
Auto-detected: ${model.auto_detected ? 'Yes' : 'No'}

Config:
${JSON.stringify(model.config, null, 2)}

Endpoints:
${JSON.stringify(model.endpoints, null, 2)}
    `.trim());
  },
  
  async deleteModel(modelId) {
    if (!confirm(`Are you sure you want to delete model "${modelId}"?`)) {
      return;
    }
    
    try {
      const response = await fetch(
        `${this.apiBase}/api/dynamic-models/models/${modelId}`,
        { method: 'DELETE' }
      );
      
      const data = await response.json();
      
      if (data.success) {
        this.showSuccess(`Model "${modelId}" deleted`);
        await this.refreshModelsList();
      } else {
        this.showError('Failed to delete model');
      }
    } catch (error) {
      this.showError(`Error: ${error.message}`);
    }
  },
  
  /**
   * پیغام‌های وضعیت
   */
  showSuccess(message) {
    this.showMessage(message, 'success');
  },
  
  showError(message) {
    this.showMessage(message, 'error');
  },
  
  showInfo(message) {
    this.showMessage(message, 'info');
  },
  
  showMessage(message, type = 'info') {
    const container = document.getElementById('status-messages');
    const messageDiv = document.createElement('div');
    messageDiv.className = `status-message ${type}`;
    messageDiv.textContent = message;
    
    container.appendChild(messageDiv);
    
    setTimeout(() => {
      messageDiv.remove();
    }, 5000);
  },
  
  /**
   * ابزارها
   */
  escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
  }
};

// Auto-initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => dynamicLoader.init());
} else {
  dynamicLoader.init();
}

// Export for global access
window.dynamicLoader = dynamicLoader;

