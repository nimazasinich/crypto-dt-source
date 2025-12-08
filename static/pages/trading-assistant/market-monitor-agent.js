/**
 * Market Monitoring Agent
 * Continuously monitors market and generates signals
 */

export class MarketMonitorAgent {
  constructor(config = {}) {
    this.symbol = config.symbol || 'BTC';
    this.strategy = config.strategy || 'trend-rsi-macd';
    this.interval = config.interval || 60000; // 1 minute
    this.isRunning = false;
    this.intervalId = null;
    this.lastSignal = null;
    this.onSignalCallback = null;
    this.onErrorCallback = null;
  }

  /**
   * Starts the monitoring agent
   */
  start() {
    if (this.isRunning) {
      console.warn('[MonitorAgent] Already running');
      return;
    }

    console.log(`[MonitorAgent] Starting for ${this.symbol} with ${this.strategy}`);
    this.isRunning = true;
    
    this.checkMarket();
    
    this.intervalId = setInterval(() => {
      this.checkMarket();
    }, this.interval);
  }

  /**
   * Stops the monitoring agent
   */
  stop() {
    if (!this.isRunning) return;

    console.log('[MonitorAgent] Stopping...');
    this.isRunning = false;
    
    if (this.intervalId) {
      clearInterval(this.intervalId);
      this.intervalId = null;
    }
  }

  /**
   * Checks market conditions and generates signals
   */
  async checkMarket() {
    try {
      const marketData = await this.fetchMarketData();
      
      const analysis = await this.analyzeMarket(marketData);
      
      if (this.shouldNotify(analysis)) {
        this.emitSignal(analysis);
      }
    } catch (error) {
      console.error('[MonitorAgent] Error checking market:', error);
      if (this.onErrorCallback) {
        this.onErrorCallback(error);
      }
    }
  }

  /**
   * Fetches current market data with fallback and retry logic
   */
  async fetchMarketData(retries = 2) {
    const baseUrl = window.location.origin; // Use relative URL for Hugging Face compatibility
    const apiUrl = `${baseUrl}/api/market?limit=1&symbol=${this.symbol}`;

    for (let attempt = 0; attempt <= retries; attempt++) {
      try {
        if (attempt > 0) {
          const delay = Math.min(1000 * Math.pow(2, attempt - 1), 5000);
          await new Promise(resolve => setTimeout(resolve, delay));
        }

        const response = await fetch(apiUrl, {
          signal: AbortSignal.timeout(10000)
        });

        if (!response.ok) {
          if (attempt < retries && response.status >= 500) {
            continue; // Retry on server errors
          }
          throw new Error(`Market API returned ${response.status}`);
        }

        const contentType = response.headers.get('content-type');
        if (!contentType || !contentType.includes('application/json')) {
          throw new Error('Invalid response type');
        }

        const data = await response.json();
        
        if (!data || typeof data !== 'object') {
          throw new Error('Invalid response format');
        }
        
        if (data.success && Array.isArray(data.items) && data.items.length > 0) {
          const item = data.items[0];
          if (!item || typeof item !== 'object') {
            throw new Error('Invalid item data');
          }
          
          const price = parseFloat(item.price);
          if (isNaN(price) || price <= 0) {
            throw new Error('Invalid price data');
          }
          
          return {
            symbol: this.symbol,
            price: price,
            volume: parseFloat(item.volume_24h || 0) || 0,
            high24h: parseFloat(item.high_24h || price * 1.05) || price * 1.05,
            low24h: parseFloat(item.low_24h || price * 0.95) || price * 0.95,
            change24h: parseFloat(item.change_24h || 0) || 0,
          };
        }

        throw new Error('No market data available');
      } catch (error) {
        if (attempt < retries && (error.name === 'AbortError' || error.message.includes('timeout') || error.message.includes('network'))) {
          continue; // Retry on network errors
        }
        console.warn('[MonitorAgent] Fetch error, using fallback:', error.message);
        return this.getFallbackMarketData();
      }
    }
    
    // If all retries failed, return fallback
    return this.getFallbackMarketData();
  }

  /**
   * Gets fallback market data
   */
  getFallbackMarketData() {
    const defaultPrices = {
      'BTC': 50000,
      'ETH': 3000,
      'SOL': 100,
      'BNB': 600,
      'XRP': 0.5,
      'ADA': 0.5,
    };
    const price = defaultPrices[this.symbol] || 1000;
    
    return {
      symbol: this.symbol,
      price,
      volume: 1000000,
      high24h: price * 1.05,
      low24h: price * 0.95,
      change24h: 0,
    };
  }

  /**
   * Analyzes market using selected strategy
   */
  async analyzeMarket(marketData) {
    const { analyzeWithStrategy } = await import('./trading-strategies.js');
    return analyzeWithStrategy(this.symbol, this.strategy, marketData);
  }

  /**
   * Determines if a notification should be sent
   */
  shouldNotify(analysis) {
    if (!this.lastSignal) {
      this.lastSignal = analysis;
      return true;
    }

    if (this.lastSignal.signal !== analysis.signal) {
      this.lastSignal = analysis;
      return true;
    }

    if (analysis.strength === 'strong' && analysis.confidence >= 80) {
      return true;
    }

    return false;
  }

  /**
   * Emits signal to callback
   */
  emitSignal(analysis) {
    console.log('[MonitorAgent] New signal:', analysis);
    if (this.onSignalCallback) {
      this.onSignalCallback(analysis);
    }
  }

  /**
   * Sets the signal callback
   */
  onSignal(callback) {
    this.onSignalCallback = callback;
  }

  /**
   * Sets the error callback
   */
  onError(callback) {
    this.onErrorCallback = callback;
  }

  /**
   * Updates agent configuration
   */
  updateConfig(config) {
    if (config.symbol) this.symbol = config.symbol;
    if (config.strategy) this.strategy = config.strategy;
    if (config.interval) this.interval = config.interval;

    if (this.isRunning) {
      this.stop();
      this.start();
    }
  }

  /**
   * Gets agent status
   */
  getStatus() {
    return {
      isRunning: this.isRunning,
      symbol: this.symbol,
      strategy: this.strategy,
      interval: this.interval,
      lastSignal: this.lastSignal,
    };
  }
}

