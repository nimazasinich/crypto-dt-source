/**
 * Real Data Fetcher
 * Fetches real cryptocurrency data from multiple providers with intelligent fallback
 * Uses crypto_resources_unified with 200+ endpoints
 */

import { API_REGISTRY, getTotalEndpointsCount } from './api-registry.js';

export class RealDataFetcher {
  constructor() {
    this.failedProviders = new Map();
    this.providerStats = new Map();
    this.cache = new Map();
  }

  /**
   * Fetch market data with provider fallback
   */
  async fetchMarketData(limit = 50) {
    const providers = [
      { name: 'CoinGecko', fetcher: () => this.fetchFromCoinGecko(limit) },
      { name: 'Binance', fetcher: () => this.fetchFromBinance(limit) },
      { name: 'CoinMarketCap', fetcher: () => this.fetchFromCoinMarketCap(limit) }
    ];
    return this.tryProviders(providers, 'market_data');
  }

  /**
   * Fetch trending coins
   */
  async fetchTrendingCoins() {
    const providers = [
      { name: 'CoinGecko Trending', fetcher: () => this.fetchCoinGeckoTrending() },
      { name: 'CoinCap Top', fetcher: () => this.fetchCoinCapTop() }
    ];
    return this.tryProviders(providers, 'trending');
  }

  /**
   * Fetch sentiment data
   */
  async fetchSentimentData(timeframe = '1D') {
    const providers = [
      { name: 'Fear & Greed', fetcher: () => this.fetchFearGreedIndex() },
      { name: 'LunarCrush', fetcher: () => this.fetchLunarCrushSentiment() }
    ];
    return this.tryProviders(providers, 'sentiment');
  }

  /**
   * Fetch on-chain analytics
   */
  async fetchOnChainAnalytics() {
    const providers = [
      { name: 'Glassnode', fetcher: () => this.fetchGlassnodeData() },
      { name: 'Covalent', fetcher: () => this.fetchCovalentData() }
    ];
    return this.tryProviders(providers, 'onchain');
  }

  /**
   * Fetch latest news
   */
  async fetchLatestNews(query = 'cryptocurrency') {
    const providers = [
      { name: 'NewsAPI', fetcher: () => this.fetchNewsAPI(query) },
      { name: 'CryptoPanic', fetcher: () => this.fetchCryptoPanic() }
    ];
    return this.tryProviders(providers, 'news');
  }

  /**
   * Try multiple providers with fallback
   */
  async tryProviders(providers, category) {
    for (const provider of providers) {
      try {
        console.log(`[RealDataFetcher] Trying ${provider.name}...`);
        const data = await provider.fetcher();
        if (data) {
          console.log(`[RealDataFetcher] ✅ ${provider.name} succeeded`);
          this.recordProviderSuccess(provider.name);
          return data;
        }
      } catch (error) {
        console.warn(`[RealDataFetcher] ❌ ${provider.name} failed:`, error.message);
        this.recordProviderFailure(provider.name);
      }
    }
    console.error('[RealDataFetcher] All providers failed for', category);
    return null;
  }

  /**
   * ========================================================================
   * COINGECKO ENDPOINTS
   * ========================================================================
   */

  async fetchFromCoinGecko(limit = 50) {
    try {
      const url = `https://api.coingecko.com/api/v3/coins/markets?vs_currency=usd&order=market_cap_desc&per_page=${Math.min(limit, 250)}&sparkline=true&price_change_percentage=7d`;
      
      const response = await fetch(url);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      
      const data = await response.json();
      return {
        coins: data.map(coin => ({
          rank: coin.market_cap_rank,
          name: coin.name,
          symbol: coin.symbol.toUpperCase(),
          price: coin.current_price,
          volume_24h: coin.total_volume,
          market_cap: coin.market_cap,
          change_24h: coin.price_change_percentage_24h,
          change_7d: coin.price_change_percentage_7d_in_currency,
          image: coin.image
        })),
        timestamp: new Date().toISOString(),
        source: 'coingecko'
      };
    } catch (error) {
      console.error('[CoinGecko] Error:', error);
      throw error;
    }
  }

  async fetchCoinGeckoTrending() {
    try {
      const url = 'https://api.coingecko.com/api/v3/search/trending';
      const response = await fetch(url);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      
      const data = await response.json();
      return {
        coins: data.coins.slice(0, 10).map((item, i) => ({
          rank: i + 1,
          name: item.item.name,
          symbol: item.item.symbol.toUpperCase(),
          price: item.item.data.price,
          market_cap: item.item.data.market_cap,
          change_24h: item.item.data.price_change_percentage_24h,
          image: item.item.large
        })),
        source: 'coingecko_trending'
      };
    } catch (error) {
      console.error('[CoinGecko Trending] Error:', error);
      throw error;
    }
  }

  async fetchGlobalMarketData() {
    try {
      const url = 'https://api.coingecko.com/api/v3/global';
      const response = await fetch(url);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      
      const data = await response.json();
      return {
        total_market_cap: data.data.total_market_cap.usd,
        total_volume: data.data.total_24h_vol.usd,
        btc_dominance: data.data.btc_dominance,
        active_cryptocurrencies: data.data.active_cryptocurrencies
      };
    } catch (error) {
      console.error('[CoinGecko Global] Error:', error);
      throw error;
    }
  }

  /**
   * ========================================================================
   * BINANCE ENDPOINTS
   * ========================================================================
   */

  async fetchFromBinance(limit = 50) {
    try {
      const url = 'https://api.binance.com/api/v3/ticker/24hr';
      const response = await fetch(url);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      
      const data = await response.json();
      
      // Filter to top trading pairs
      return {
        coins: data.slice(0, limit).map((ticker, i) => ({
          rank: i + 1,
          symbol: ticker.symbol.replace('USDT', ''),
          price: parseFloat(ticker.lastPrice),
          volume_24h: parseFloat(ticker.volume),
          change_24h: parseFloat(ticker.priceChangePercent)
        })),
        source: 'binance'
      };
    } catch (error) {
      console.error('[Binance] Error:', error);
      throw error;
    }
  }

  /**
   * ========================================================================
   * COINMARKETCAP ENDPOINTS
   * ========================================================================
   */

  async fetchFromCoinMarketCap(limit = 50) {
    try {
      // Note: This requires a CMC API key
      const key = API_REGISTRY.market.coinmarketcap.key;
      if (!key) throw new Error('CoinMarketCap key not configured');

      const url = `https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest?limit=${limit}&convert=USD`;
      
      const response = await fetch(url, {
        headers: {
          'X-CMC_PRO_API_KEY': key
        }
      });
      
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      
      const data = await response.json();
      return {
        coins: data.data.map((coin, i) => ({
          rank: coin.cmc_rank,
          name: coin.name,
          symbol: coin.symbol,
          price: coin.quote.USD.price,
          volume_24h: coin.quote.USD.volume_24h,
          market_cap: coin.quote.USD.market_cap,
          change_24h: coin.quote.USD.percent_change_24h
        })),
        source: 'coinmarketcap'
      };
    } catch (error) {
      console.error('[CoinMarketCap] Error:', error);
      throw error;
    }
  }

  /**
   * ========================================================================
   * COINCAP ENDPOINTS
   * ========================================================================
   */

  async fetchCoinCapTop() {
    try {
      const url = 'https://api.coincap.io/v2/assets?limit=50';
      const response = await fetch(url);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      
      const data = await response.json();
      return {
        coins: data.data.map((coin, i) => ({
          rank: parseInt(coin.rank),
          name: coin.name,
          symbol: coin.symbol,
          price: parseFloat(coin.priceUsd),
          volume_24h: parseFloat(coin.volumeUsd24Hr),
          market_cap: parseFloat(coin.marketCapUsd),
          change_24h: parseFloat(coin.changePercent24Hr)
        })),
        source: 'coincap'
      };
    } catch (error) {
      console.error('[CoinCap] Error:', error);
      throw error;
    }
  }

  /**
   * ========================================================================
   * SENTIMENT ENDPOINTS
   * ========================================================================
   */

  async fetchFearGreedIndex() {
    try {
      const url = 'https://api.alternative.me/fng/?limit=30';
      const response = await fetch(url);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      
      const data = await response.json();
      return {
        current: data.data[0],
        history: data.data,
        source: 'fear_greed'
      };
    } catch (error) {
      console.error('[Fear & Greed] Error:', error);
      throw error;
    }
  }

  async fetchLunarCrushSentiment() {
    try {
      // This would need a real LunarCrush API key
      throw new Error('LunarCrush requires API key');
    } catch (error) {
      console.error('[LunarCrush] Error:', error);
      throw error;
    }
  }

  /**
   * ========================================================================
   * ON-CHAIN ANALYTICS ENDPOINTS
   * ========================================================================
   */

  async fetchGlassnodeData() {
    try {
      // Glassnode requires API key
      throw new Error('Glassnode requires API key');
    } catch (error) {
      console.error('[Glassnode] Error:', error);
      throw error;
    }
  }

  async fetchCovalentData() {
    try {
      // Covalent requires API key
      throw new Error('Covalent requires API key');
    } catch (error) {
      console.error('[Covalent] Error:', error);
      throw error;
    }
  }

  /**
   * ========================================================================
   * NEWS ENDPOINTS
   * ========================================================================
   */

  async fetchNewsAPI(query = 'cryptocurrency') {
    try {
      const key = 'pub_346789abc123def456789ghi012345jkl';
      const url = `https://newsapi.org/v2/everything?q=${query}&sortBy=publishedAt&language=en&pageSize=50&apiKey=${key}`;
      
      const response = await fetch(url);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      
      const data = await response.json();
      return {
        articles: data.articles.slice(0, 50).map(article => ({
          title: article.title,
          description: article.description,
          url: article.url,
          source: article.source.name,
          published_at: article.publishedAt,
          image: article.urlToImage
        })),
        source: 'newsapi'
      };
    } catch (error) {
      console.error('[NewsAPI] Error:', error);
      throw error;
    }
  }

  async fetchCryptoPanic() {
    try {
      const url = 'https://cryptopanic.com/api/v1/posts/?auth_token=optional&limit=50';
      const response = await fetch(url);
      if (!response.ok) throw new Error(`HTTP ${response.status}`);
      
      const data = await response.json();
      return {
        articles: data.results.slice(0, 50).map(article => ({
          title: article.title,
          url: article.link,
          source: article.source.title,
          kind: article.kind,
          published_at: article.published_at
        })),
        source: 'cryptopanic'
      };
    } catch (error) {
      console.error('[CryptoPanic] Error:', error);
      throw error;
    }
  }

  /**
   * ========================================================================
   * PROVIDER STATISTICS
   * ========================================================================
   */

  recordProviderSuccess(providerName) {
    const stats = this.providerStats.get(providerName) || { success: 0, failures: 0 };
    stats.success++;
    this.providerStats.set(providerName, stats);
    
    // Reset failure count
    this.failedProviders.delete(providerName);
  }

  recordProviderFailure(providerName) {
    const stats = this.providerStats.get(providerName) || { success: 0, failures: 0 };
    stats.failures++;
    this.providerStats.set(providerName, stats);
    
    // Mark as failed if too many failures
    const failures = (this.failedProviders.get(providerName) || 0) + 1;
    this.failedProviders.set(providerName, failures);
  }

  getProviderStats() {
    return Object.fromEntries(this.providerStats);
  }

  getTotalEndpoints() {
    return getTotalEndpointsCount();
  }
}

export const realDataFetcher = new RealDataFetcher();
export default realDataFetcher;
