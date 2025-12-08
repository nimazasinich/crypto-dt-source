// Chart Page - Real-time cryptocurrency price chart
class ChartPage {
  constructor() {
    this.currentSymbol = 'BTC';
    this.currentTimeframe = '1d';
    this.chartData = null;
    this.init();
  }

  init() {
    // Parse URL parameters
    const params = new URLSearchParams(window.location.search);
    const urlSymbol = params.get('symbol');
    if (urlSymbol) {
      this.currentSymbol = urlSymbol;
    }

    // Setup event listeners
    this.setupEventListeners();
    
    // Load initial data
    this.loadChartData();
  }

  setupEventListeners() {
    const symbolSelect = document.getElementById('symbol-select');
    const timeframeSelect = document.getElementById('timeframe-select');
    const refreshBtn = document.getElementById('refresh-btn');

    if (symbolSelect) {
      symbolSelect.value = this.currentSymbol;
      symbolSelect.addEventListener('change', (e) => {
        this.currentSymbol = e.target.value;
        this.loadChartData();
      });
    }

    if (timeframeSelect) {
      timeframeSelect.addEventListener('change', (e) => {
        this.currentTimeframe = e.target.value;
        this.loadChartData();
      });
    }

    if (refreshBtn) {
      refreshBtn.addEventListener('click', () => {
        this.loadChartData();
      });
    }
  }

  async loadChartData() {
    try {
      const chartCanvas = document.getElementById('price-chart');
      if (chartCanvas) {
        chartCanvas.innerHTML = '<div class="loading">⏳ در حال بارگذاری داده‌ها...</div>';
      }

      // Fetch market data
      const response = await fetch(`/api/market?limit=10`);
      if (!response.ok) {
        throw new Error('Failed to fetch market data');
      }

      const data = await response.json();
      
      // Find current symbol data
      const symbolData = data.data?.find(coin => 
        coin.symbol?.toUpperCase() === this.currentSymbol ||
        coin.name?.toUpperCase().includes(this.currentSymbol)
      );

      if (symbolData) {
        this.updateChartInfo(symbolData);
        this.renderChart(symbolData);
      } else {
        throw new Error('Symbol not found');
      }

    } catch (error) {
      console.error('Error loading chart data:', error);
      const chartCanvas = document.getElementById('price-chart');
      if (chartCanvas) {
        chartCanvas.innerHTML = `
          <div style="text-align: center; color: #ef4444;">
            ❌ خطا در بارگذاری داده‌ها<br>
            <small>${error.message}</small>
          </div>
        `;
      }
    }
  }

  updateChartInfo(data) {
    // Update title
    const title = document.getElementById('chart-title');
    if (title) {
      title.textContent = `نمودار ${data.name || this.currentSymbol}`;
    }

    // Update price info
    const currentPrice = document.getElementById('current-price');
    if (currentPrice && data.current_price) {
      currentPrice.textContent = `$${this.formatNumber(data.current_price)}`;
    }

    const change24h = document.getElementById('change-24h');
    if (change24h && data.price_change_percentage_24h !== undefined) {
      const changeValue = data.price_change_percentage_24h;
      change24h.textContent = `${changeValue > 0 ? '+' : ''}${changeValue.toFixed(2)}%`;
      change24h.className = 'info-value ' + (changeValue >= 0 ? 'positive' : 'negative');
    }

    const volume24h = document.getElementById('volume-24h');
    if (volume24h && data.total_volume) {
      volume24h.textContent = `$${this.formatLargeNumber(data.total_volume)}`;
    }

    const high24h = document.getElementById('high-24h');
    if (high24h && data.high_24h) {
      high24h.textContent = `$${this.formatNumber(data.high_24h)}`;
    }

    const low24h = document.getElementById('low-24h');
    if (low24h && data.low_24h) {
      low24h.textContent = `$${this.formatNumber(data.low_24h)}`;
    }
  }

  renderChart(data) {
    const chartCanvas = document.getElementById('price-chart');
    if (!chartCanvas) return;

    // Create a simple visualization
    const price = data.current_price || 0;
    const change = data.price_change_percentage_24h || 0;
    const high = data.high_24h || price * 1.1;
    const low = data.low_24h || price * 0.9;

    chartCanvas.innerHTML = `
      <div style="width: 100%; height: 100%; display: flex; flex-direction: column; justify-content: space-between;">
        <div style="text-align: center; padding: 2rem;">
          <div style="font-size: 3rem; font-weight: 700; margin-bottom: 1rem;">
            ${change >= 0 ? '📈' : '📉'}
          </div>
          <div style="font-size: 2.5rem; font-weight: 700; color: ${change >= 0 ? '#10b981' : '#ef4444'};">
            $${this.formatNumber(price)}
          </div>
          <div style="font-size: 1.2rem; color: ${change >= 0 ? '#10b981' : '#ef4444'}; margin-top: 0.5rem;">
            ${change >= 0 ? '+' : ''}${change.toFixed(2)}%
          </div>
        </div>
        
        <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 1rem; padding: 1rem; background: rgba(0,0,0,0.2); border-radius: 10px;">
          <div style="text-align: center;">
            <div style="color: #94a3b8; font-size: 0.9rem;">بالاترین</div>
            <div style="color: #10b981; font-size: 1.2rem; font-weight: 600;">$${this.formatNumber(high)}</div>
          </div>
          <div style="text-align: center;">
            <div style="color: #94a3b8; font-size: 0.9rem;">میانگین</div>
            <div style="color: #e2e8f0; font-size: 1.2rem; font-weight: 600;">$${this.formatNumber((high + low) / 2)}</div>
          </div>
          <div style="text-align: center;">
            <div style="color: #94a3b8; font-size: 0.9rem;">پایین‌ترین</div>
            <div style="color: #ef4444; font-size: 1.2rem; font-weight: 600;">$${this.formatNumber(low)}</div>
          </div>
        </div>

        <div style="text-align: center; color: #64748b; font-size: 0.9rem; padding: 1rem;">
          💡 برای نمایش نمودار تکنیکال پیشرفته، از صفحه تحلیل تکنیکال استفاده کنید
        </div>
      </div>
    `;
  }

  formatNumber(num) {
    if (num >= 1) {
      return num.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 2 });
    }
    return num.toLocaleString('en-US', { minimumFractionDigits: 2, maximumFractionDigits: 8 });
  }

  formatLargeNumber(num) {
    if (num >= 1e9) {
      return (num / 1e9).toFixed(2) + 'B';
    } else if (num >= 1e6) {
      return (num / 1e6).toFixed(2) + 'M';
    } else if (num >= 1e3) {
      return (num / 1e3).toFixed(2) + 'K';
    }
    return num.toFixed(2);
  }
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
  new ChartPage();
});
