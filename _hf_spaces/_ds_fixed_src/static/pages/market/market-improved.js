/**
 * Market Page - Real-time Market Data (IMPROVED)
 * - Added SVG coin icons with fallback
 * - Added Chart button next to View button
 * - Improved metric cards visibility
 */

import { APIHelper } from '../../shared/js/utils/api-helper.js';

class MarketPage {
  constructor() {
    this.marketData = [];
    this.allMarketData = [];
    this.sortColumn = 'market_cap';
    this.sortDirection = 'desc';
    this.currentLimit = 50;
  }
  
  /**
   * Get coin image with SVG fallback
   * @param {Object} coin - Coin data
   * @returns {string} Image HTML with fallback
   */
  getCoinImage(coin) {
    const imageUrl = coin.image || `https://assets.coingecko.com/coins/images/1/small/${coin.id}.png`;
    const symbol = (coin.symbol || '?').charAt(0).toUpperCase();
    const colors = {
      'B': '#F7931A', // Bitcoin orange
      'E': '#627EEA', // Ethereum blue
      'S': '#14F195', // Solana green
      'C': '#3C3C3D', // Generic crypto
      'default': '#94a3b8'
    };
    const color = colors[symbol] || colors['default'];
    
    const fallbackSvg = `data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='32' height='32'%3E%3Ccircle cx='16' cy='16' r='15' fill='${encodeURIComponent(color)}'/%3E%3Ctext x='16' y='21' text-anchor='middle' fill='white' font-size='14' font-weight='bold' font-family='Arial'%3E${symbol}%3C/text%3E%3C/svg%3E`;
    
    return `<img src="${imageUrl}" 
                 alt="${coin.name || 'Coin'}" 
                 width="32" 
                 height="32"
                 onerror="this.onerror=null; this.src='${fallbackSvg}';"
                 loading="lazy"
                 class="coin-icon"
                 style="border-radius: 50%; object-fit: cover; box-shadow: 0 2px 4px rgba(0,0,0,0.1);">`;
  }

  async init() {
    try {
      console.log('[Market] Initializing...');
      
      // Show loading state
      const tbody = document.querySelector('#market-table tbody');
      if (tbody) {
        tbody.innerHTML = '<tr><td colspan="8" class="text-center"><div class="loading-container"><div class="spinner"></div><p style="margin-top: 12px; color: var(--text-muted);">Loading market data...</p></div></td></tr>';
      }
      
      this.bindEvents();
      await this.loadMarketData();
      
      // Auto-refresh every 30 seconds (only when tab is visible)
      setInterval(() => {
        if (!document.hidden) {
          this.loadMarketData(this.currentLimit);
        }
      }, 30000);
      
      this.showToast('Market data loaded', 'success');
    } catch (error) {
      console.error('[Market] Init error:', error);
      this.showToast('Failed to initialize market page', 'error');
    }
  }

  bindEvents() {
    // Refresh button
    document.getElementById('refresh-btn')?.addEventListener('click', () => {
      this.loadMarketData(this.currentLimit);
    });
    
    // Search functionality
    document.getElementById('search-input')?.addEventListener('input', (e) => {
      this.filterMarketData(e.target.value);
    });

    // Category filter buttons
    document.querySelectorAll('.category-filter-btn').forEach(btn => {
      btn.addEventListener('click', (e) => {
        document.querySelectorAll('.category-filter-btn').forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        this.filterByCategory(e.target.dataset.category);
      });
    });

    // Timeframe buttons (Top 10, Top 25, Top 50, All)
    document.querySelectorAll('[data-timeframe]').forEach(btn => {
      btn.addEventListener('click', (e) => {
        document.querySelectorAll('[data-timeframe]').forEach(b => b.classList.remove('active'));
        e.target.classList.add('active');
        const timeframe = e.target.dataset.timeframe;
        this.applyLimitFilter(timeframe);
      });
    });

    // Sort dropdown
    document.getElementById('sort-select')?.addEventListener('change', (e) => {
      this.sortMarketData(e.target.value);
    });

    // Export button
    document.getElementById('export-btn')?.addEventListener('click', () => {
      this.exportData();
    });

    // Table header sorting
    document.querySelectorAll('.sortable-header').forEach(header => {
      header.addEventListener('click', () => {
        const column = header.dataset.column;
        this.toggleSort(column);
      });
    });
  }

  async loadMarketData(limit = 50) {
    try {
      let data = [];

      // Try backend API first
      try {
        const json = await APIHelper.fetchAPI(`/api/coins/top?limit=${limit}`);
        // Handle various response formats
        data = APIHelper.extractArray(json, ['markets', 'coins', 'data']);
        if (Array.isArray(data) && data.length > 0) {
          console.log('[Market] Data loaded from backend API:', data.length, 'coins');
        }
      } catch (e) {
        console.warn('[Market] Primary API unavailable, trying CoinGecko', e);
      }

      // Fallback to CoinGecko if no data
      if (!Array.isArray(data) || data.length === 0) {
        try {
          const response = await fetch(`https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&per_page=${limit}&price_change_percentage=7d&sparkline=true`);
          if (response.ok) {
            data = await response.json();
            console.log('[Market] Data loaded from CoinGecko:', data.length, 'coins');
          }
        } catch (e) {
          console.warn('[Market] Fallback API also unavailable', e);
        }
      }

      // If all APIs fail, show error - NO DEMO DATA
      if (!Array.isArray(data) || data.length === 0) {
        console.error('[Market] All APIs failed - no data available');
        this.marketData = [];
        this.allMarketData = [];
        this.renderMarketTable();
        this.showToast('Unable to load market data. Please check your connection.', 'error');
        return;
      }
      
      this.marketData = Array.isArray(data) ? data : [];
      this.allMarketData = [...this.marketData]; // Keep a copy for filtering
      this.renderMarketTable();
      this.updateMarketStats();
      this.updateTimestamp();
    } catch (error) {
      console.error('[Market] Load error:', error);
      this.marketData = [];
      this.allMarketData = [];
      this.renderMarketTable();
      this.showToast('Error loading market data. Please try again later.', 'error');
    }
  }

  renderMarketTable() {
    const tbody = document.querySelector('#market-table tbody');
    if (!tbody) return;
    
    // Update market stats
    this.updateMarketStats();
    
    if (this.marketData.length === 0) {
      tbody.innerHTML = '<tr><td colspan="8" class="text-center"><div class="loading-container"><div class="spinner"></div><p style="margin-top: 12px; color: var(--text-muted);">Loading market data...</p></div></td></tr>';
      return;
    }
    
    tbody.innerHTML = this.marketData.map((coin, index) => {
      const change = coin.price_change_percentage_24h || 0;
      const change7d = coin.price_change_percentage_7d_in_currency || 0;
      const changeClass = change >= 0 ? 'positive' : 'negative';
      const change7dClass = change7d >= 0 ? 'positive' : 'negative';
      const arrow = change >= 0 ? '↑' : '↓';
      const arrow7d = change7d >= 0 ? '↑' : '↓';
      
      return `
        <tr class="market-row">
          <td class="rank-cell">${index + 1}</td>
          <td class="coin-cell">
            ${this.getCoinImage(coin)}
            <div class="coin-info">
              <strong>${coin.name || 'Unknown'}</strong>
              <span class="coin-symbol">${(coin.symbol || 'N/A').toUpperCase()}</span>
            </div>
          </td>
          <td class="text-right price-cell">$${coin.current_price?.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 6})}</td>
          <td class="text-right ${changeClass}">
            <span class="change-badge">${arrow} ${Math.abs(change).toFixed(2)}%</span>
          </td>
          <td class="text-right ${change7dClass}">
            <span class="change-badge">${arrow7d} ${Math.abs(change7d).toFixed(2)}%</span>
          </td>
          <td class="text-right mcap-cell">$${(coin.market_cap / 1e9).toFixed(2)}B</td>
          <td class="text-right volume-cell">$${(coin.total_volume / 1e6).toFixed(2)}M</td>
          <td class="action-cell">
            <button class="btn-chart" onclick="marketPage.viewChart('${coin.id}')" title="View Chart">
              <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                <polyline points="22 7 13.5 15.5 8.5 10.5 2 17"></polyline>
                <polyline points="16 7 22 7 22 13"></polyline>
              </svg>
              Chart
            </button>
            <button class="btn-view" onclick="marketPage.viewDetails('${coin.id}')">
              View
            </button>
          </td>
        </tr>
      `;
    }).join('');
  }

  filterMarketData(query) {
    if (!query || query.trim() === '') {
      // Reset to all data
      this.marketData = [...this.allMarketData];
      this.renderMarketTable();
      return;
    }
    
    if (!Array.isArray(this.allMarketData)) {
      this.marketData = [];
      return;
    }
    
    const searchTerm = query.toLowerCase().trim();
    const filtered = this.allMarketData.filter(coin =>
      (coin.name && coin.name.toLowerCase().includes(searchTerm)) ||
      (coin.symbol && coin.symbol.toLowerCase().includes(searchTerm)) ||
      (coin.id && coin.id.toLowerCase().includes(searchTerm))
    );
    
    this.marketData = filtered;
    this.renderMarketTable();
    
    // Show result count
    if (filtered.length === 0) {
      this.showToast('No coins found matching your search', 'info');
    }
  }

  viewChart(coinId) {
    const coin = this.marketData.find(c => c.id === coinId);
    if (!coin) return;

    // Redirect to chart page or open chart modal
    window.location.href = `/static/pages/chart/index.html?symbol=${coin.symbol.toUpperCase()}`;
  }

  viewDetails(coinId) {
    const coin = this.marketData.find(c => c.id === coinId) || this.allMarketData.find(c => c.id === coinId);
    if (!coin) {
      this.showToast('Coin not found', 'error');
      return;
    }

    const modal = document.getElementById('coin-modal');
    if (!modal) {
      // Create modal if it doesn't exist
      const newModal = document.createElement('div');
      newModal.id = 'coin-modal';
      newModal.className = 'modal';
      newModal.setAttribute('aria-hidden', 'true');
      newModal.innerHTML = `
        <div class="modal-backdrop"></div>
        <div class="modal-content modal-lg">
          <div class="modal-header">
            <h3 class="modal-title" id="modal-title">Coin Details</h3>
            <button class="btn-icon modal-close" aria-label="Close">
              <svg xmlns="http://www.w3.org/2000/svg" width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"></line><line x1="6" y1="6" x2="18" y2="18"></line></svg>
            </button>
          </div>
          <div class="modal-body" id="modal-body">
            <div class="loading-container"><div class="spinner"></div></div>
          </div>
        </div>
      `;
      document.body.appendChild(newModal);
      return this.viewDetails(coinId); // Retry with new modal
    }

    const change = coin.price_change_percentage_24h || 0;
    const change7d = coin.price_change_percentage_7d_in_currency || 0;
    const changeClass = change >= 0 ? 'positive' : 'negative';
    
    // Update modal
    document.getElementById('modal-title').textContent = `${coin.name || 'Unknown'} (${(coin.symbol || 'N/A').toUpperCase()})`;
    
    const modalBody = document.getElementById('modal-body');
    modalBody.innerHTML = `
      <div class="coin-detail">
        <div class="detail-header">
          ${this.getCoinImage(coin)}
          <div class="detail-price">
            <span class="price">$${coin.current_price?.toLocaleString('en-US', {minimumFractionDigits: 2, maximumFractionDigits: 8}) || '0.00'}</span>
            <span class="change ${changeClass}">
              ${change >= 0 ? '↑' : '↓'} ${Math.abs(change).toFixed(2)}% (24h)
            </span>
            <span class="change ${change7d >= 0 ? 'positive' : 'negative'}" style="font-size: 0.9em; margin-left: 8px;">
              ${change7d >= 0 ? '↑' : '↓'} ${Math.abs(change7d).toFixed(2)}% (7d)
            </span>
          </div>
        </div>
        <div class="detail-stats">
          <div class="stat">
            <span class="label">Market Cap</span>
            <span class="value">$${(coin.market_cap / 1e9).toFixed(2)}B</span>
          </div>
          <div class="stat">
            <span class="label">24h Volume</span>
            <span class="value">$${(coin.total_volume / 1e6).toFixed(2)}M</span>
          </div>
          <div class="stat">
            <span class="label">Market Cap Rank</span>
            <span class="value">#${coin.market_cap_rank || 'N/A'}</span>
          </div>
          <div class="stat">
            <span class="label">Circulating Supply</span>
            <span class="value">${coin.circulating_supply ? (coin.circulating_supply / 1e6).toFixed(2) + 'M' : 'N/A'}</span>
          </div>
          ${coin.total_supply ? `
          <div class="stat">
            <span class="label">Total Supply</span>
            <span class="value">${(coin.total_supply / 1e6).toFixed(2)}M</span>
          </div>
          ` : ''}
          ${coin.ath ? `
          <div class="stat">
            <span class="label">All-Time High</span>
            <span class="value">$${coin.ath.toLocaleString()}</span>
          </div>
          ` : ''}
        </div>
        <div class="chart-placeholder">
          <p style="text-align: center; color: var(--text-muted); padding: 40px;">Price chart coming soon</p>
        </div>
      </div>
    `;

    // Show modal
    modal.classList.add('active');
    modal.setAttribute('aria-hidden', 'false');

    // Close handlers
    const closeBtn = modal.querySelector('.modal-close');
    const backdrop = modal.querySelector('.modal-backdrop');
    
    const closeModal = () => {
      modal.classList.remove('active');
      modal.setAttribute('aria-hidden', 'true');
    };

    closeBtn?.addEventListener('click', closeModal);
    backdrop?.addEventListener('click', closeModal);
  }

  filterByCategory(category) {
    console.log('[Market] Filter by category:', category);
    // Can be extended with real category filtering
    this.renderMarketTable();
  }

  /**
   * Apply limit filter (Top 10, Top 25, Top 50, All)
   * @param {string} timeframe - Filter value from button
   */
  applyLimitFilter(timeframe) {
    let limit = 50;
    switch(timeframe) {
      case '1D':
        limit = 10;
        break;
      case '7D':
        limit = 25;
        break;
      case '30D':
        limit = 50;
        break;
      case '1Y':
        limit = 100;
        break;
      default:
        limit = 50;
    }
    
    this.currentLimit = limit;
    this.loadMarketData(limit);
    this.showToast(`Showing Top ${limit} coins`, 'info');
  }

  sortMarketData(sortBy) {
    if (!Array.isArray(this.marketData)) {
      this.marketData = [];
      return;
    }
    
    const sorted = [...this.marketData].sort((a, b) => {
      switch (sortBy) {
        case 'price_desc':
          return (b.current_price || 0) - (a.current_price || 0);
        case 'price_asc':
          return (a.current_price || 0) - (b.current_price || 0);
        case 'change_desc':
          return (b.price_change_percentage_24h || 0) - (a.price_change_percentage_24h || 0);
        case 'change_asc':
          return (a.price_change_percentage_24h || 0) - (b.price_change_percentage_24h || 0);
        case 'volume':
          return (b.total_volume || 0) - (a.total_volume || 0);
        case 'rank':
        default:
          return (a.market_cap_rank || 999) - (b.market_cap_rank || 999);
      }
    });

    this.marketData = sorted;
    this.renderMarketTable();
  }

  toggleSort(column) {
    if (!Array.isArray(this.marketData)) {
      this.marketData = [];
      return;
    }
    
    if (this.sortColumn === column) {
      this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
    } else {
      this.sortColumn = column;
      this.sortDirection = 'desc';
    }

    const sorted = [...this.marketData].sort((a, b) => {
      const aVal = a[column] || 0;
      const bVal = b[column] || 0;
      return this.sortDirection === 'asc' ? aVal - bVal : bVal - aVal;
    });

    this.marketData = sorted;
    this.renderMarketTable();
  }

  updateMarketStats() {
    if (!Array.isArray(this.marketData) || this.marketData.length === 0) return;
    
    // Calculate totals
    const totalMcap = this.marketData.reduce((sum, coin) => sum + (coin.market_cap || 0), 0);
    const totalVolume = this.marketData.reduce((sum, coin) => sum + (coin.total_volume || 0), 0);
    
    // Get BTC data
    const btcCoin = this.marketData.find(c => c.symbol.toLowerCase() === 'btc');
    const btcMcap = btcCoin?.market_cap || 0;
    const btcDominance = totalMcap > 0 ? (btcMcap / totalMcap) * 100 : 0;
    
    // Update DOM with improved styling
    const totalMcapEl = document.getElementById('total-mcap');
    const totalVolumeEl = document.getElementById('total-volume');
    const btcDominanceEl = document.getElementById('btc-dominance');
    const activeCoinsEl = document.getElementById('active-coins');
    
    if (totalMcapEl) {
      totalMcapEl.textContent = `$${(totalMcap / 1e12).toFixed(2)}T`;
      totalMcapEl.style.fontWeight = '700';
      totalMcapEl.style.fontSize = '1.5rem';
    }
    if (totalVolumeEl) {
      totalVolumeEl.textContent = `$${(totalVolume / 1e9).toFixed(2)}B`;
      totalVolumeEl.style.fontWeight = '700';
      totalVolumeEl.style.fontSize = '1.5rem';
    }
    if (btcDominanceEl) {
      btcDominanceEl.textContent = `${btcDominance.toFixed(1)}%`;
      btcDominanceEl.style.fontWeight = '700';
      btcDominanceEl.style.fontSize = '1.5rem';
      btcDominanceEl.style.color = btcDominance > 50 ? '#10b981' : '#f59e0b';
    }
    if (activeCoinsEl) {
      activeCoinsEl.textContent = this.marketData.length.toString();
      activeCoinsEl.style.fontWeight = '700';
      activeCoinsEl.style.fontSize = '1.5rem';
    }
  }

  exportData() {
    const csv = [
      ['Rank', 'Name', 'Symbol', 'Price', '24h Change', 'Market Cap', 'Volume'],
      ...this.marketData.map((coin, idx) => [
        idx + 1,
        coin.name,
        coin.symbol.toUpperCase(),
        coin.current_price,
        coin.price_change_percentage_24h,
        coin.market_cap,
        coin.total_volume
      ])
    ].map(row => row.join(',')).join('\n');

    const blob = new Blob([csv], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `market_data_${Date.now()}.csv`;
    a.click();
    URL.revokeObjectURL(url);

    this.showToast('Market data exported', 'success');
  }

  updateTimestamp() {
    const el = document.getElementById('last-update');
    if (el) {
      el.textContent = `Updated: ${new Date().toLocaleTimeString()}`;
    }
  }

  showToast(message, type = 'info') {
    APIHelper.showToast(message, type);
  }
}

// Export for module import
export default MarketPage;

// Also create instance for direct access
if (typeof window !== 'undefined') {
  const marketPage = new MarketPage();
  window.marketPage = marketPage;
  // Auto-init if DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => marketPage.init());
  } else {
    marketPage.init();
  }
}
