/**
 * Enhanced Crypto API Hub - Seamless Backend Integration
 * Features:
 * - Real backend data fetching with self-healing
 * - Automatic retry and fallback mechanisms
 * - Smooth error handling
 * - Live API testing with CORS proxy
 * - Export functionality
 */

import { showToast } from '../shared/js/components/toast-helper.js';
import { showLoading, hideLoading } from '../shared/js/components/loading-helper.js';

class CryptoAPIHub {
  constructor() {
    this.services = null;
    this.currentFilter = 'all';
    this.searchQuery = '';
    this.retryCount = 0;
    this.maxRetries = 3;
    this.fallbackData = this.getFallbackData();
    this.corsProxyEnabled = true;
  }

  /**
   * Initialize the hub
   */
  async init() {
    console.log('[CryptoAPIHub] Initializing...');
    
    // Show loading state
    this.renderLoadingState();
    
    // Fetch services data with self-healing
    await this.fetchServicesWithHealing();
    
    // Render services
    this.renderServices();
    
    // Setup event listeners
    this.setupEventListeners();
    
    // Update statistics
    this.updateStats();
    
    console.log('[CryptoAPIHub] Initialized successfully');
  }

  /**
   * Fetch services with self-healing mechanism
   */
  async fetchServicesWithHealing() {
    try {
      console.log('[CryptoAPIHub] Fetching services from backend...');
      
      // Try to fetch from backend
      const response = await this.fetchFromBackend();
      
      if (response && response.categories) {
        this.services = response;
        this.retryCount = 0;
        showToast('✅', 'Services loaded successfully', 'success');
        return;
      }
    } catch (error) {
      console.warn('[CryptoAPIHub] Backend fetch failed:', error);
    }

    // Self-healing: Try fallback
    await this.healWithFallback();
  }

  /**
   * Fetch from backend
   */
  async fetchFromBackend() {
    try {
      // Try the crypto-hub API endpoint
      const response = await fetch('/api/crypto-hub/services', {
        method: 'GET',
        headers: {
          'Content-Type': 'application/json',
        },
      });

      if (response.ok) {
        return await response.json();
      }

      throw new Error(`HTTP ${response.status}`);
    } catch (error) {
      console.error('[CryptoAPIHub] Backend error:', error);
      throw error;
    }
  }

  /**
   * Self-healing with fallback data
   */
  async healWithFallback() {
    console.log('[CryptoAPIHub] Activating self-healing mechanism...');

    if (this.retryCount < this.maxRetries) {
      this.retryCount++;
      showToast('🔄', `Retrying... (${this.retryCount}/${this.maxRetries})`, 'info');
      
      // Wait before retry
      await this.sleep(2000 * this.retryCount);
      
      // Try again
      await this.fetchServicesWithHealing();
      return;
    }

    // All retries failed, use fallback data
    console.log('[CryptoAPIHub] Using fallback data...');
    this.services = this.fallbackData;
    showToast('⚠️', 'Using cached data (backend unavailable)', 'warning');
  }

  /**
   * Get fallback data (embedded for self-healing)
   */
  getFallbackData() {
    return {
      metadata: {
        version: "1.0.0",
        total_services: 74,
        total_endpoints: 150,
        api_keys_count: 10,
        last_updated: new Date().toISOString()
      },
      categories: {
        explorer: {
          name: "Blockchain Explorers",
          description: "Track transactions and addresses",
          services: [
            {
              name: "Etherscan",
              url: "https://api.etherscan.io/api",
              key: "SZHYFZK2RR8H9TIMJBVW54V4H81K2Z2KR2",
              endpoints: [
                "?module=account&action=balance&address={address}&apikey={KEY}",
                "?module=gastracker&action=gasoracle&apikey={KEY}"
              ]
            },
            {
              name: "BscScan",
              url: "https://api.bscscan.com/api",
              key: "K62RKHGXTDCG53RU4MCG6XABIMJKTN19IT",
              endpoints: ["?module=account&action=balance&address={address}&apikey={KEY}"]
            },
            {
              name: "TronScan",
              url: "https://apilist.tronscanapi.com/api",
              key: "7ae72726-bffe-4e74-9c33-97b761eeea21",
              endpoints: ["/account?address={address}"]
            }
          ]
        },
        market: {
          name: "Market Data",
          description: "Real-time prices and market metrics",
          services: [
            {
              name: "CoinGecko",
              url: "https://api.coingecko.com/api/v3",
              key: "",
              endpoints: [
                "/simple/price?ids=bitcoin,ethereum&vs_currencies=usd",
                "/coins/markets?vs_currency=usd&per_page=100"
              ]
            },
            {
              name: "CoinMarketCap",
              url: "https://pro-api.coinmarketcap.com/v1",
              key: "04cf4b5b-9868-465c-8ba0-9f2e78c92eb1",
              endpoints: ["/cryptocurrency/quotes/latest?symbol=BTC&convert=USD"]
            },
            {
              name: "Binance",
              url: "https://api.binance.com/api/v3",
              key: "",
              endpoints: ["/ticker/price?symbol=BTCUSDT"]
            }
          ]
        },
        news: {
          name: "News & Media",
          description: "Crypto news and updates",
          services: [
            {
              name: "CryptoPanic",
              url: "https://cryptopanic.com/api/v1",
              key: "",
              endpoints: ["/posts/?auth_token={KEY}"]
            },
            {
              name: "NewsAPI",
              url: "https://newsapi.org/v2",
              key: "pub_346789abc123def456789ghi012345jkl",
              endpoints: ["/everything?q=crypto&apiKey={KEY}"]
            }
          ]
        },
        sentiment: {
          name: "Sentiment Analysis",
          description: "Market sentiment indicators",
          services: [
            {
              name: "Fear & Greed",
              url: "https://api.alternative.me/fng/",
              key: "",
              endpoints: ["?limit=1", "?limit=30"]
            },
            {
              name: "LunarCrush",
              url: "https://api.lunarcrush.com/v2",
              key: "",
              endpoints: ["?data=assets&key={KEY}"]
            }
          ]
        },
        analytics: {
          name: "Analytics & Tools",
          description: "Advanced analytics and whale tracking",
          services: [
            {
              name: "Whale Alert",
              url: "https://api.whale-alert.io/v1",
              key: "",
              endpoints: ["/transactions?api_key={KEY}&min_value=1000000"]
            },
            {
              name: "Glassnode",
              url: "https://api.glassnode.com/v1",
              key: "",
              endpoints: []
            },
            {
              name: "Hugging Face",
              url: "https://api-inference.huggingface.co/models",
              key: "",
              endpoints: ["/ElKulako/cryptobert"]
            }
          ]
        }
      }
    };
  }

  /**
   * Render services grid
   */
  renderServices() {
    const grid = document.getElementById('servicesGrid');
    if (!grid) return;

    let html = '';
    let count = 0;

    const categories = this.services?.categories || {};

    Object.entries(categories).forEach(([categoryKey, category]) => {
      const services = category.services || [];

      services.forEach((service, index) => {
        // Apply filter
        if (this.currentFilter !== 'all' && categoryKey !== this.currentFilter) {
          return;
        }

        // Apply search
        if (this.searchQuery) {
          const searchLower = this.searchQuery.toLowerCase();
          const matchesSearch = 
            service.name.toLowerCase().includes(searchLower) ||
            service.url.toLowerCase().includes(searchLower) ||
            categoryKey.toLowerCase().includes(searchLower);
          
          if (!matchesSearch) return;
        }

        count++;
        const hasKey = service.key ? `<span class="badge badge-key">🔑 Has Key</span>` : '';
        const endpoints = service.endpoints?.length || 0;

        html += `
          <div class="service-card" data-category="${categoryKey}" data-name="${service.name.toLowerCase()}" style="animation-delay: ${index * 0.05}s">
            <div class="service-header">
              <div class="service-icon">${this.getIcon(categoryKey)}</div>
              <div class="service-info">
                <div class="service-name">${service.name}</div>
                <div class="service-url">${service.url}</div>
              </div>
            </div>
            <div class="service-badges">
              <span class="badge badge-category">${categoryKey}</span>
              ${endpoints > 0 ? `<span class="badge badge-endpoints">${endpoints} endpoints</span>` : ''}
              ${hasKey}
            </div>
            ${this.renderEndpoints(service, categoryKey)}
          </div>
        `;
      });
    });

    if (html === '') {
      html = '<div class="empty-state"><div class="empty-icon">🔍</div><div class="empty-text">No services found</div></div>';
    }

    grid.innerHTML = html;
  }

  /**
   * Render endpoints for a service
   */
  renderEndpoints(service, category) {
    const endpoints = service.endpoints || [];

    if (endpoints.length === 0) {
      return '<div class="no-endpoints">Base endpoint available</div>';
    }

    let html = '<div class="endpoints-list">';

    endpoints.slice(0, 2).forEach(endpoint => {
      const fullUrl = service.url + endpoint;
      const encodedUrl = encodeURIComponent(fullUrl);

      html += `
        <div class="endpoint-item">
          <div class="endpoint-path">${endpoint}</div>
          <div class="endpoint-actions">
            <button class="btn-sm" onclick="window.cryptoAPIHub.copyText('${fullUrl.replace(/'/g, "\\'")}')">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <rect x="9" y="9" width="13" height="13" rx="2" ry="2"></rect>
                <path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"></path>
              </svg>
              Copy
            </button>
            <button class="btn-sm" onclick="window.cryptoAPIHub.testEndpoint('${fullUrl.replace(/'/g, "\\'")}', '${service.key || ''}')">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"></polyline>
              </svg>
              Test
            </button>
          </div>
        </div>
      `;
    });

    if (endpoints.length > 2) {
      html += `<div class="more-endpoints">+${endpoints.length - 2} more endpoints</div>`;
    }

    html += '</div>';
    return html;
  }

  /**
   * Get icon for category
   */
  getIcon(category) {
    const icons = {
      explorer: '<svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2"><path d="M10 13a5 5 0 0 0 7.54.54l3-3a5 5 0 0 0-7.07-7.07l-1.72 1.71"></path><path d="M14 11a5 5 0 0 0-7.54-.54l-3 3a5 5 0 0 0 7.07 7.07l1.71-1.71"></path></svg>',
      market: '<svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2"><line x1="12" y1="20" x2="12" y2="10"></line><line x1="18" y1="20" x2="18" y2="4"></line><line x1="6" y1="20" x2="6" y2="16"></line></svg>',
      news: '<svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2"><path d="M4 22h16a2 2 0 0 0 2-2V4a2 2 0 0 0-2-2H8a2 2 0 0 0-2 2v16a2 2 0 0 1-2 2Zm0 0a2 2 0 0 1-2-2v-9c0-1.1.9-2 2-2h2"></path><path d="M18 14h-8"></path><path d="M15 18h-5"></path><path d="M10 6h8v4h-8V6Z"></path></svg>',
      sentiment: '<svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2"><path d="M9.5 2A2.5 2.5 0 0 1 12 4.5v15a2.5 2.5 0 0 1-4.96.44 2.5 2.5 0 0 1-2.96-3.08 3 3 0 0 1-.34-5.58 2.5 2.5 0 0 1 1.32-4.24 2.5 2.5 0 0 1 1.98-3A2.5 2.5 0 0 1 9.5 2Z"></path><path d="M14.5 2A2.5 2.5 0 0 0 12 4.5v15a2.5 2.5 0 0 0 4.96.44 2.5 2.5 0 0 0 2.96-3.08 3 3 0 0 0 .34-5.58 2.5 2.5 0 0 0-1.32-4.24 2.5 2.5 0 0 0-1.98-3A2.5 2.5 0 0 0 14.5 2Z"></path></svg>',
      analytics: '<svg viewBox="0 0 24 24" fill="none" stroke="white" stroke-width="2"><path d="M3 3v18h18"></path><path d="m19 9-5 5-4-4-3 3"></path></svg>'
    };
    return icons[category] || icons.analytics;
  }

  /**
   * Render loading state
   */
  renderLoadingState() {
    const grid = document.getElementById('servicesGrid');
    if (!grid) return;

    grid.innerHTML = `
      <div class="loading-state">
        <div class="loading-spinner"></div>
        <div class="loading-text">Loading services...</div>
      </div>
    `;
  }

  /**
   * Update statistics
   */
  updateStats() {
    const metadata = this.services?.metadata || {};
    
    const statsData = {
      services: metadata.total_services || 74,
      endpoints: metadata.total_endpoints || 150,
      keys: metadata.api_keys_count || 10
    };

    // Update stat values
    document.querySelectorAll('.stat-value').forEach((el, index) => {
      const values = [statsData.services, statsData.endpoints + '+', statsData.keys];
      if (el && values[index]) {
        el.textContent = values[index];
      }
    });
  }

  /**
   * Setup event listeners
   */
  setupEventListeners() {
    // Search input
    const searchInput = document.getElementById('searchInput');
    if (searchInput) {
      searchInput.addEventListener('input', (e) => {
        this.searchQuery = e.target.value;
        this.renderServices();
      });
    }

    // Filter tabs
    document.querySelectorAll('.filter-tab').forEach(tab => {
      tab.addEventListener('click', (e) => {
        this.setFilter(e.target.dataset.filter);
      });
    });

    // Method buttons
    document.querySelectorAll('.method-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        const method = e.target.dataset.method;
        this.setMethod(method);
      });
    });

    // Update last update time
    this.updateLastUpdateTime();
  }

  /**
   * Set HTTP method
   */
  setMethod(method) {
    this.currentMethod = method;
    
    // Update active button
    document.querySelectorAll('.method-btn').forEach(btn => {
      btn.classList.remove('active');
      if (btn.dataset.method === method) {
        btn.classList.add('active');
      }
    });

    // Show/hide body field
    const bodyGroup = document.getElementById('bodyGroup');
    if (bodyGroup) {
      bodyGroup.style.display = (method === 'POST' || method === 'PUT') ? 'block' : 'none';
    }
  }

  /**
   * Update last update time
   */
  updateLastUpdateTime() {
    const el = document.getElementById('lastUpdate');
    if (el) {
      el.textContent = `Last updated: ${new Date().toLocaleTimeString()}`;
    }
  }

  /**
   * Set filter
   */
  setFilter(filter) {
    this.currentFilter = filter;
    
    // Update active tab
    document.querySelectorAll('.filter-tab').forEach(t => t.classList.remove('active'));
    const activeTab = document.querySelector(`[data-filter="${filter}"]`);
    if (activeTab) activeTab.classList.add('active');
    
    // Re-render
    this.renderServices();
  }

  /**
   * Copy text to clipboard
   */
  async copyText(text) {
    try {
      await navigator.clipboard.writeText(text);
      showToast('✅', 'Copied to clipboard!', 'success');
    } catch (error) {
      showToast('❌', 'Failed to copy', 'error');
    }
  }

  /**
   * Test endpoint
   */
  async testEndpoint(url, key) {
    // Replace key placeholders
    let finalUrl = url;
    if (key) {
      finalUrl = url.replace('{KEY}', key).replace('{key}', key);
    }

    // Open tester modal with URL
    this.openTester(finalUrl);
  }

  /**
   * Open API tester modal
   */
  openTester(url = '') {
    const modal = document.getElementById('testerModal');
    const urlInput = document.getElementById('testUrl');
    
    if (modal) {
      modal.classList.add('active');
      if (urlInput && url) {
        urlInput.value = url;
      }
    }
  }

  /**
   * Close API tester modal
   */
  closeTester() {
    const modal = document.getElementById('testerModal');
    if (modal) {
      modal.classList.remove('active');
    }
  }

  /**
   * Send API test request
   */
  async sendTestRequest() {
    const url = document.getElementById('testUrl')?.value;
    const headersText = document.getElementById('testHeaders')?.value || '{}';
    const bodyText = document.getElementById('testBody')?.value;
    const responseBox = document.getElementById('responseBox');
    const responseJson = document.getElementById('responseJson');
    const method = this.currentMethod || 'GET';

    if (!url) {
      showToast('⚠️', 'Please enter a URL', 'warning');
      return;
    }

    if (responseBox) responseBox.style.display = 'block';
    if (responseJson) responseJson.textContent = '⏳ Sending request...';

    try {
      // Use CORS proxy if enabled
      const requestUrl = this.corsProxyEnabled 
        ? `/api/crypto-hub/test`
        : url;

      const requestOptions = this.corsProxyEnabled
        ? {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
              url: url,
              method: method,
              headers: JSON.parse(headersText),
              body: bodyText
            })
          }
        : {
            method: method,
            headers: JSON.parse(headersText),
            body: (method === 'POST' || method === 'PUT') ? bodyText : undefined
          };

      const response = await fetch(requestUrl, requestOptions);
      const data = await response.json();

      if (responseJson) {
        responseJson.textContent = JSON.stringify(data, null, 2);
      }
      
      showToast('✅', 'Request successful!', 'success');
    } catch (error) {
      if (responseJson) {
        responseJson.textContent = `❌ Error: ${error.message}\n\nThis might be due to CORS policy. Try using the CORS proxy.`;
      }
      showToast('❌', 'Request failed', 'error');
    }
  }

  /**
   * Export services as JSON
   */
  exportJSON() {
    const data = {
      metadata: {
        exported_at: new Date().toISOString(),
        ...this.services?.metadata
      },
      services: this.services
    };

    const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `crypto-api-hub-${Date.now()}.json`;
    a.click();
    URL.revokeObjectURL(url);

    showToast('✅', 'JSON exported successfully!', 'success');
  }

  /**
   * Sleep utility
   */
  sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
  }
}

// Initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
  window.cryptoAPIHub = new CryptoAPIHub();
  window.cryptoAPIHub.init();
});

// Export for module usage
export default CryptoAPIHub;
