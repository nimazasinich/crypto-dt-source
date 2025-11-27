/**
 * Market Page
 * Real-time cryptocurrency market data with charts
 */

import { api } from '../../shared/js/core/api-client.js';
import { pollingManager } from '../../shared/js/core/polling-manager.js';
import { LayoutManager } from '../../shared/js/core/layout-manager.js';
import { Toast } from '../../shared/js/components/toast.js';

class MarketPage {
  constructor() {
    this.coins = [];
    this.filteredCoins = [];
    this.timeframe = '7D';
    this.sortBy = 'rank';
  }

  async init() {
    try {
      await LayoutManager.injectLayouts();
      LayoutManager.setActiveNav('market');
      
      this.bindEvents();
      await this.loadData();
      this.setupPolling();
    } catch (error) {
      console.error('[Market] Init error:', error);
      Toast.error('Failed to initialize market page');
    }
  }

  bindEvents() {
    document.getElementById('refresh-btn')?.addEventListener('click', () => this.loadData());
    document.getElementById('search-input')?.addEventListener('input', () => this.filterCoins());
    document.getElementById('sort-select')?.addEventListener('change', (e) => {
      this.sortBy = e.target.value;
      this.sortAndRender();
    });

    // Timeframe buttons
    document.getElementById('timeframe-btns')?.addEventListener('click', (e) => {
      if (e.target.dataset.timeframe) {
        this.timeframe = e.target.dataset.timeframe;
        document.querySelectorAll('#timeframe-btns .btn').forEach(btn => btn.classList.remove('active'));
        e.target.classList.add('active');
        this.loadData();
      }
    });

    // Modal close
    document.querySelector('.modal-close')?.addEventListener('click', () => this.closeModal());
    document.querySelector('.modal-backdrop')?.addEventListener('click', () => this.closeModal());
    document.addEventListener('keydown', (e) => {
      if (e.key === 'Escape') this.closeModal();
    });
  }

  async loadData() {
    try {
      const tbody = document.getElementById('market-tbody');
      tbody.innerHTML = '<tr><td colspan="8" class="text-center"><div class="spinner"></div> Loading...</td></tr>';
      
      const [marketData, topCoins] = await Promise.all([
        api.getMarket().catch(() => null),
        api.getTopCoins(50).catch(() => ({ coins: [] }))
      ]);

      // Update global stats
      if (marketData) {
        this.updateStats(marketData);
      }

      this.coins = topCoins.coins || topCoins.data || [];
      this.filterCoins();
      this.updateLastUpdate();
      
    } catch (error) {
      console.error('[Market] Load error:', error);
      Toast.error('Failed to load market data');
    }
  }

  updateStats(data) {
    document.getElementById('total-mcap').textContent = this.formatLargeNumber(data.total_market_cap || data.totalMarketCap);
    document.getElementById('total-volume').textContent = this.formatLargeNumber(data.total_volume || data.totalVolume);
    document.getElementById('btc-dominance').textContent = data.btc_dominance ? `${data.btc_dominance.toFixed(1)}%` : '--';
    document.getElementById('active-coins').textContent = data.active_coins || data.activeCoins || '--';
  }

  filterCoins() {
    const search = document.getElementById('search-input').value.toLowerCase();
    
    this.filteredCoins = this.coins.filter(coin => {
      const name = (coin.name || '').toLowerCase();
      const symbol = (coin.symbol || '').toLowerCase();
      return name.includes(search) || symbol.includes(search);
    });

    this.sortAndRender();
  }

  sortAndRender() {
    // Sort
    this.filteredCoins.sort((a, b) => {
      switch (this.sortBy) {
        case 'price_desc': return (b.price || b.current_price || 0) - (a.price || a.current_price || 0);
        case 'price_asc': return (a.price || a.current_price || 0) - (b.price || b.current_price || 0);
        case 'change_desc': return (b.change_24h || b.price_change_percentage_24h || 0) - (a.change_24h || a.price_change_percentage_24h || 0);
        case 'change_asc': return (a.change_24h || a.price_change_percentage_24h || 0) - (b.change_24h || b.price_change_percentage_24h || 0);
        case 'volume': return (b.volume || b.total_volume || 0) - (a.volume || a.total_volume || 0);
        default: return (a.rank || a.market_cap_rank || 0) - (b.rank || b.market_cap_rank || 0);
      }
    });

    this.renderTable();
  }

  renderTable() {
    const tbody = document.getElementById('market-tbody');
    
    if (this.filteredCoins.length === 0) {
      tbody.innerHTML = '<tr><td colspan="8" class="text-center">No coins found</td></tr>';
      return;
    }

    tbody.innerHTML = this.filteredCoins.map((coin, index) => {
      const price = coin.price || coin.current_price || 0;
      const change24h = coin.change_24h || coin.price_change_percentage_24h || 0;
      const change7d = coin.change_7d || coin.price_change_percentage_7d || 0;
      const mcap = coin.market_cap || 0;
      const volume = coin.volume || coin.total_volume || 0;

      return `
        <tr class="clickable" onclick="window.marketPage.showCoinDetail('${coin.id || coin.symbol}')">
          <td>${coin.rank || coin.market_cap_rank || index + 1}</td>
          <td>
            <div class="coin-info">
              ${coin.image ? `<img src="${coin.image}" alt="${coin.name}" class="coin-icon">` : ''}
              <div>
                <span class="coin-name">${coin.name}</span>
                <span class="coin-symbol">${(coin.symbol || '').toUpperCase()}</span>
              </div>
            </div>
          </td>
          <td class="text-right">$${this.formatPrice(price)}</td>
          <td class="text-right ${change24h >= 0 ? 'positive' : 'negative'}">${change24h >= 0 ? '+' : ''}${change24h.toFixed(2)}%</td>
          <td class="text-right ${change7d >= 0 ? 'positive' : 'negative'}">${change7d >= 0 ? '+' : ''}${change7d.toFixed(2)}%</td>
          <td class="text-right">$${this.formatLargeNumber(mcap)}</td>
          <td class="text-right">$${this.formatLargeNumber(volume)}</td>
          <td>
            <div class="mini-chart ${change7d >= 0 ? 'up' : 'down'}">
              ${this.renderMiniChart(coin.sparkline)}
            </div>
          </td>
        </tr>
      `;
    }).join('');
  }

  renderMiniChart(sparkline) {
    if (!sparkline || !sparkline.length) return '---';
    
    // Simple SVG sparkline
    const width = 80;
    const height = 24;
    const data = sparkline.slice(-20);
    const min = Math.min(...data);
    const max = Math.max(...data);
    const range = max - min || 1;
    
    const points = data.map((val, i) => {
      const x = (i / (data.length - 1)) * width;
      const y = height - ((val - min) / range) * height;
      return `${x},${y}`;
    }).join(' ');

    return `<svg width="${width}" height="${height}" viewBox="0 0 ${width} ${height}"><polyline points="${points}" fill="none" stroke="currentColor" stroke-width="1.5"/></svg>`;
  }

  async showCoinDetail(coinId) {
    const modal = document.getElementById('coin-modal');
    const body = document.getElementById('modal-body');
    const title = document.getElementById('modal-title');
    
    modal.classList.add('active');
    modal.setAttribute('aria-hidden', 'false');
    body.innerHTML = '<div class="loading-container"><div class="spinner"></div><p>Loading details...</p></div>';

    try {
      const coin = this.coins.find(c => c.id === coinId || c.symbol === coinId);
      
      if (!coin) {
        throw new Error('Coin not found');
      }

      title.textContent = `${coin.name} (${(coin.symbol || '').toUpperCase()})`;
      
      const price = coin.price || coin.current_price || 0;
      const change24h = coin.change_24h || coin.price_change_percentage_24h || 0;
      const mcap = coin.market_cap || 0;
      const volume = coin.volume || coin.total_volume || 0;

      body.innerHTML = `
        <div class="coin-detail">
          <div class="detail-header">
            ${coin.image ? `<img src="${coin.image}" alt="${coin.name}" class="coin-logo">` : ''}
            <div class="detail-price">
              <span class="price">$${this.formatPrice(price)}</span>
              <span class="change ${change24h >= 0 ? 'positive' : 'negative'}">${change24h >= 0 ? '+' : ''}${change24h.toFixed(2)}%</span>
            </div>
          </div>
          
          <div class="detail-stats">
            <div class="stat">
              <span class="label">Market Cap</span>
              <span class="value">$${this.formatLargeNumber(mcap)}</span>
            </div>
            <div class="stat">
              <span class="label">24h Volume</span>
              <span class="value">$${this.formatLargeNumber(volume)}</span>
            </div>
            <div class="stat">
              <span class="label">Rank</span>
              <span class="value">#${coin.rank || coin.market_cap_rank || '-'}</span>
            </div>
            ${coin.circulating_supply ? `
              <div class="stat">
                <span class="label">Circulating Supply</span>
                <span class="value">${this.formatLargeNumber(coin.circulating_supply)} ${(coin.symbol || '').toUpperCase()}</span>
              </div>
            ` : ''}
          </div>

          <div class="chart-placeholder">
            <canvas id="detail-chart"></canvas>
          </div>
        </div>
      `;

      // Load chart if sparkline data available
      if (coin.sparkline && coin.sparkline.length > 0) {
        this.renderDetailChart(coin.sparkline);
      }

    } catch (error) {
      body.innerHTML = `<div class="error-state"><p>Failed to load coin details</p></div>`;
    }
  }

  async renderDetailChart(sparkline) {
    try {
      const { loadChartJS, getChartDefaults } = await import('../../shared/js/components/chart.js');
      await loadChartJS();
      
      const canvas = document.getElementById('detail-chart');
      if (!canvas) return;

      const ctx = canvas.getContext('2d');
      const defaults = getChartDefaults();
      
      const isUp = sparkline[sparkline.length - 1] >= sparkline[0];
      const color = isUp ? '#10b981' : '#ef4444';

      new Chart(ctx, {
        type: 'line',
        data: {
          labels: sparkline.map((_, i) => i),
          datasets: [{
            data: sparkline,
            borderColor: color,
            backgroundColor: color + '20',
            fill: true,
            tension: 0.4,
            pointRadius: 0,
          }]
        },
        options: {
          ...defaults,
          plugins: {
            legend: { display: false }
          },
          scales: {
            x: { display: false },
            y: { display: false }
          }
        }
      });
    } catch (error) {
      console.error('[Market] Chart error:', error);
    }
  }

  closeModal() {
    const modal = document.getElementById('coin-modal');
    modal.classList.remove('active');
    modal.setAttribute('aria-hidden', 'true');
  }

  formatPrice(price) {
    if (price >= 1000) return price.toLocaleString(undefined, { maximumFractionDigits: 0 });
    if (price >= 1) return price.toFixed(2);
    if (price >= 0.01) return price.toFixed(4);
    return price.toFixed(8);
  }

  formatLargeNumber(num) {
    if (!num) return '--';
    if (num >= 1e12) return `${(num / 1e12).toFixed(2)}T`;
    if (num >= 1e9) return `${(num / 1e9).toFixed(2)}B`;
    if (num >= 1e6) return `${(num / 1e6).toFixed(2)}M`;
    if (num >= 1e3) return `${(num / 1e3).toFixed(2)}K`;
    return num.toFixed(2);
  }

  setupPolling() {
    pollingManager.start(
      'market-data',
      () => api.getTopCoins(50),
      (data, error) => {
        if (data) {
          this.coins = data.coins || data.data || [];
          this.filterCoins();
          this.updateLastUpdate();
        }
      },
      30000 // 30 seconds
    );
  }

  updateLastUpdate() {
    const el = document.getElementById('last-update');
    if (el) {
      el.textContent = `Updated: ${new Date().toLocaleTimeString()}`;
    }
  }

  destroy() {
    pollingManager.stop('market-data');
  }
}

// Initialize page
const page = new MarketPage();
window.marketPage = page;

if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', () => page.init());
} else {
  page.init();
}

window.addEventListener('beforeunload', () => page.destroy());
