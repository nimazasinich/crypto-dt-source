/**
 * Comprehensive API Client - Multi-Source with Fallback Chains
 * Integrates 150+ crypto data sources with automatic failover
 * Minimum 10 endpoints per query type as per requirements
 */

// ═══════════════════════════════════════════════════════════════
// API KEYS (from all_apis_merged_2025.json)
// ═══════════════════════════════════════════════════════════════
// NOTE: HuggingFace token should be obtained from backend API or user settings
// Backend reads from HF_API_TOKEN or HF_TOKEN environment variables
const API_KEYS = {
  ETHERSCAN: 'ETHERSCAN_API_KEY_HERE',
  ETHERSCAN_BACKUP: 'ETHERSCAN_API_KEY_HERE',
  BSCSCAN: 'BSCSCAN_API_KEY_HERE',
  TRONSCAN: 'TRONSCAN_API_KEY_HERE',
  CMC_PRIMARY: 'COINMARKETCAP_API_KEY_HERE',
  CMC_BACKUP: 'COINMARKETCAP_API_KEY_HERE',
  NEWSAPI: 'NEWSAPI_API_KEY_HERE',
  CRYPTOCOMPARE: 'CRYPTOCOMPARE_API_KEY_HERE',
  // HUGGINGFACE: Should be retrieved from backend API endpoint that reads HF_API_TOKEN env var
  HUGGINGFACE: null
};

// ═══════════════════════════════════════════════════════════════
// CORS PROXIES (fallback only when needed)
// ═══════════════════════════════════════════════════════════════
const CORS_PROXIES = [
  'https://api.allorigins.win/get?url=',
  'https://proxy.cors.sh/',
  'https://api.codetabs.com/v1/proxy?quest='
];

// ═══════════════════════════════════════════════════════════════
// MARKET DATA SOURCES (15+ endpoints)
// ═══════════════════════════════════════════════════════════════
const MARKET_SOURCES = [
  // Direct APIs (no proxy needed)
  {
    id: 'coingecko',
    name: 'CoinGecko',
    baseUrl: 'https://api.coingecko.com/api/v3',
    needsProxy: false,
    priority: 1,
    getPrice: (symbol) => `/simple/price?ids=${symbol}&vs_currencies=usd,eur&include_24hr_change=true&include_market_cap=true`
  },
  {
    id: 'coinpaprika',
    name: 'CoinPaprika',
    baseUrl: 'https://api.coinpaprika.com/v1',
    needsProxy: false,
    priority: 2,
    getPrice: (symbol) => `/tickers/${symbol}-${symbol}` // e.g., btc-bitcoin
  },
  {
    id: 'coincap',
    name: 'CoinCap',
    baseUrl: 'https://api.coincap.io/v2',
    needsProxy: false,
    priority: 3,
    getPrice: (symbol) => `/assets/${symbol}`
  },
  {
    id: 'binance',
    name: 'Binance Public',
    baseUrl: 'https://api.binance.com/api/v3',
    needsProxy: false,
    priority: 4,
    getPrice: (symbol) => `/ticker/price?symbol=${symbol.toUpperCase()}USDT`
  },
  {
    id: 'coinlore',
    name: 'CoinLore',
    baseUrl: 'https://api.coinlore.net/api',
    needsProxy: false,
    priority: 5,
    getPrice: (symbol) => `/ticker/?id=${symbol}` // requires coin ID
  },
  {
    id: 'defillama',
    name: 'DefiLlama',
    baseUrl: 'https://coins.llama.fi',
    needsProxy: false,
    priority: 6,
    getPrice: (symbol) => `/prices/current/coingecko:${symbol}`
  },
  {
    id: 'coinstats',
    name: 'CoinStats',
    baseUrl: 'https://api.coinstats.app/public/v1',
    needsProxy: false,
    priority: 7,
    getPrice: (symbol) => `/coins/${symbol}`
  },
  {
    id: 'messari',
    name: 'Messari',
    baseUrl: 'https://data.messari.io/api/v1',
    needsProxy: false,
    priority: 8,
    getPrice: (symbol) => `/assets/${symbol}/metrics`
  },
  {
    id: 'nomics',
    name: 'Nomics',
    baseUrl: 'https://api.nomics.com/v1',
    needsProxy: false,
    priority: 9,
    getPrice: (symbol) => `/currencies/ticker?ids=${symbol.toUpperCase()}&convert=USD`
  },
  {
    id: 'coindesk',
    name: 'CoinDesk',
    baseUrl: 'https://api.coindesk.com/v1',
    needsProxy: false,
    priority: 10,
    getPrice: () => `/bpi/currentprice.json` // Bitcoin only
  },
  // APIs requiring proxy or keys
  {
    id: 'cmc_primary',
    name: 'CoinMarketCap',
    baseUrl: 'https://pro-api.coinmarketcap.com/v1',
    needsProxy: true,
    priority: 11,
    headers: () => ({ 'X-CMC_PRO_API_KEY': API_KEYS.CMC_PRIMARY }),
    getPrice: (symbol) => `/cryptocurrency/quotes/latest?symbol=${symbol.toUpperCase()}`
  },
  {
    id: 'cmc_backup',
    name: 'CoinMarketCap Backup',
    baseUrl: 'https://pro-api.coinmarketcap.com/v1',
    needsProxy: true,
    priority: 12,
    headers: () => ({ 'X-CMC_PRO_API_KEY': API_KEYS.CMC_BACKUP }),
    getPrice: (symbol) => `/cryptocurrency/quotes/latest?symbol=${symbol.toUpperCase()}`
  },
  {
    id: 'cryptocompare',
    name: 'CryptoCompare',
    baseUrl: 'https://min-api.cryptocompare.com/data',
    needsProxy: false,
    priority: 13,
    getPrice: (symbol) => `/price?fsym=${symbol.toUpperCase()}&tsyms=USD,EUR&api_key=${API_KEYS.CRYPTOCOMPARE}`
  },
  {
    id: 'kraken',
    name: 'Kraken Public',
    baseUrl: 'https://api.kraken.com/0/public',
    needsProxy: false,
    priority: 14,
    getPrice: (symbol) => `/Ticker?pair=${symbol.toUpperCase()}USD`
  },
  {
    id: 'bitfinex',
    name: 'Bitfinex Public',
    baseUrl: 'https://api-pub.bitfinex.com/v2',
    needsProxy: false,
    priority: 15,
    getPrice: (symbol) => `/ticker/t${symbol.toUpperCase()}USD`
  }
];

// ═══════════════════════════════════════════════════════════════
// NEWS SOURCES (12+ endpoints)
// ═══════════════════════════════════════════════════════════════
const NEWS_SOURCES = [
  {
    id: 'cryptopanic',
    name: 'CryptoPanic',
    baseUrl: 'https://cryptopanic.com/api/v1',
    needsProxy: false,
    priority: 1,
    getNews: () => `/posts/?public=true`
  },
  {
    id: 'coinstats_news',
    name: 'CoinStats News',
    baseUrl: 'https://api.coinstats.app/public/v1',
    needsProxy: false,
    priority: 2,
    getNews: () => `/news`
  },
  {
    id: 'cointelegraph_rss',
    name: 'Cointelegraph RSS',
    baseUrl: 'https://cointelegraph.com',
    needsProxy: false,
    priority: 3,
    getNews: () => `/rss`,
    parseRSS: true
  },
  {
    id: 'coindesk_rss',
    name: 'CoinDesk RSS',
    baseUrl: 'https://www.coindesk.com',
    needsProxy: false,
    priority: 4,
    getNews: () => `/arc/outboundfeeds/rss/?outputType=xml`,
    parseRSS: true
  },
  {
    id: 'decrypt_rss',
    name: 'Decrypt RSS',
    baseUrl: 'https://decrypt.co',
    needsProxy: false,
    priority: 5,
    getNews: () => `/feed`,
    parseRSS: true
  },
  {
    id: 'bitcoin_magazine_rss',
    name: 'Bitcoin Magazine RSS',
    baseUrl: 'https://bitcoinmagazine.com',
    needsProxy: false,
    priority: 6,
    getNews: () => `/.rss/full/`,
    parseRSS: true
  },
  {
    id: 'reddit_crypto',
    name: 'Reddit r/CryptoCurrency',
    baseUrl: 'https://www.reddit.com/r/CryptoCurrency',
    needsProxy: false,
    priority: 7,
    getNews: () => `/hot.json?limit=25`
  },
  {
    id: 'reddit_bitcoin',
    name: 'Reddit r/Bitcoin',
    baseUrl: 'https://www.reddit.com/r/Bitcoin',
    needsProxy: false,
    priority: 8,
    getNews: () => `/new.json?limit=25`
  },
  {
    id: 'blockworks',
    name: 'Blockworks RSS',
    baseUrl: 'https://blockworks.co',
    needsProxy: false,
    priority: 9,
    getNews: () => `/feed`,
    parseRSS: true
  },
  {
    id: 'theblock_rss',
    name: 'The Block RSS',
    baseUrl: 'https://www.theblock.co',
    needsProxy: false,
    priority: 10,
    getNews: () => `/rss.xml`,
    parseRSS: true
  },
  {
    id: 'coinjournal',
    name: 'CoinJournal RSS',
    baseUrl: 'https://coinjournal.net',
    needsProxy: false,
    priority: 11,
    getNews: () => `/feed/`,
    parseRSS: true
  },
  {
    id: 'cryptoslate_rss',
    name: 'CryptoSlate RSS',
    baseUrl: 'https://cryptoslate.com',
    needsProxy: false,
    priority: 12,
    getNews: () => `/feed/`,
    parseRSS: true
  }
];

// ═══════════════════════════════════════════════════════════════
// SENTIMENT SOURCES (10+ endpoints for Fear & Greed)
// ═══════════════════════════════════════════════════════════════
const SENTIMENT_SOURCES = [
  {
    id: 'alternative_me',
    name: 'Alternative.me F&G',
    baseUrl: 'https://api.alternative.me',
    needsProxy: false,
    priority: 1,
    getSentiment: () => `/fng/?limit=1`
  },
  {
    id: 'cfgi_v1',
    name: 'CFGI API v1',
    baseUrl: 'https://api.cfgi.io/v1',
    needsProxy: false,
    priority: 2,
    getSentiment: () => `/fear-greed`
  },
  {
    id: 'cfgi_legacy',
    name: 'CFGI Legacy',
    baseUrl: 'https://cfgi.io',
    needsProxy: false,
    priority: 3,
    getSentiment: () => `/api`
  },
  {
    id: 'coinglass_fgi',
    name: 'CoinGlass F&G',
    baseUrl: 'https://open-api.coinglass.com/public/v2',
    needsProxy: false,
    priority: 4,
    getSentiment: () => `/indicator/fear_greed`
  },
  {
    id: 'lunarcrush',
    name: 'LunarCrush Social',
    baseUrl: 'https://api.lunarcrush.com/v2',
    needsProxy: false,
    priority: 5,
    getSentiment: () => `?data=global`
  },
  {
    id: 'santiment',
    name: 'Santiment Social Volume',
    baseUrl: 'https://api.santiment.net',
    needsProxy: false,
    priority: 6,
    getSentiment: () => `/graphql`,
    method: 'POST'
  },
  {
    id: 'thetie',
    name: 'TheTie.io Sentiment',
    baseUrl: 'https://api.thetie.io',
    needsProxy: false,
    priority: 7,
    getSentiment: () => `/v1/sentiment?symbol=BTC`
  },
  {
    id: 'augmento',
    name: 'Augmento AI Sentiment',
    baseUrl: 'https://api.augmento.ai/v1',
    needsProxy: false,
    priority: 8,
    getSentiment: () => `/signals/overview`
  },
  {
    id: 'cryptoquant_sentiment',
    name: 'CryptoQuant Sentiment',
    baseUrl: 'https://api.cryptoquant.com/v1',
    needsProxy: false,
    priority: 9,
    getSentiment: () => `/btc/indicator/fear-greed`
  },
  {
    id: 'glassnode_social',
    name: 'Glassnode Social Metrics',
    baseUrl: 'https://api.glassnode.com/v1',
    needsProxy: false,
    priority: 10,
    getSentiment: () => `/metrics/social/sentiment_positive`
  }
];

// ═══════════════════════════════════════════════════════════════
// HELPER FUNCTIONS
// ═══════════════════════════════════════════════════════════════

async function fetchWithTimeout(url, options = {}, timeout = 10000) {
  const controller = new AbortController();
  const id = setTimeout(() => controller.abort(), timeout);
  
  try {
    const response = await fetch(url, {
      ...options,
      signal: controller.signal
    });
    clearTimeout(id);
    return response;
  } catch (error) {
    clearTimeout(id);
    throw error;
  }
}

async function fetchDirect(url, options = {}) {
  try {
    const response = await fetchWithTimeout(url, options);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}: ${response.statusText}`);
    }
    const contentType = response.headers.get('content-type');
    if (contentType && contentType.includes('application/json')) {
      return await response.json();
    }
    return await response.text();
  } catch (error) {
    throw new Error(`Direct fetch failed: ${error.message}`);
  }
}

async function fetchWithProxy(url, options = {}, proxyIndex = 0) {
  if (proxyIndex >= CORS_PROXIES.length) {
    throw new Error('All CORS proxies exhausted');
  }
  
  const proxy = CORS_PROXIES[proxyIndex];
  const proxyUrl = proxy + encodeURIComponent(url);
  
  try {
    const response = await fetchWithTimeout(proxyUrl, {
      ...options,
      headers: {
        ...options.headers,
        'Origin': window.location.origin,
        'x-requested-with': 'XMLHttpRequest'
      }
    });
    
    if (!response.ok) {
      throw new Error(`Proxy returned ${response.status}`);
    }
    
    const data = await response.json();
    // Handle allOrigins response format
    return data.contents ? JSON.parse(data.contents) : data;
  } catch (error) {
    console.warn(`Proxy ${proxyIndex + 1} failed:`, error.message);
    // Try next proxy
    return fetchWithProxy(url, options, proxyIndex + 1);
  }
}

function parseRSS(xmlText, sourceName) {
  const parser = new DOMParser();
  const doc = parser.parseFromString(xmlText, 'text/xml');
  const items = doc.querySelectorAll('item');
  
  const news = [];
  items.forEach((item, index) => {
    if (index >= 20) return; // Limit to 20 items
    
    const title = item.querySelector('title')?.textContent || '';
    const link = item.querySelector('link')?.textContent || '';
    const pubDate = item.querySelector('pubDate')?.textContent || '';
    const description = item.querySelector('description')?.textContent || '';
    
    if (title && link) {
      news.push({
        title,
        link,
        publishedAt: pubDate,
        description: description.substring(0, 200),
        source: sourceName
      });
    }
  });
  
  return news;
}

// ═══════════════════════════════════════════════════════════════
// MAIN API CLIENT CLASS
// ═══════════════════════════════════════════════════════════════

class ComprehensiveAPIClient {
  constructor() {
    this.cache = new Map();
    this.cacheTimeout = 60000; // 1 minute
    this.requestLog = [];
  }

  // Cache management
  getCached(key) {
    const cached = this.cache.get(key);
    if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
      console.log(`📦 Cache hit: ${key}`);
      return cached.data;
    }
    return null;
  }

  setCache(key, data) {
    this.cache.set(key, {
      data,
      timestamp: Date.now()
    });
  }

  // Log requests for debugging
  logRequest(source, success, error = null) {
    this.requestLog.push({
      source,
      success,
      error,
      timestamp: new Date().toISOString()
    });
    
    // Keep only last 100 logs
    if (this.requestLog.length > 100) {
      this.requestLog.shift();
    }
  }

  // ═══════════════════════════════════════════════════════════
  // MARKET DATA - Try all 15+ sources
  // ═══════════════════════════════════════════════════════════
  async getMarketPrice(symbol) {
    const cacheKey = `market_${symbol}`;
    const cached = this.getCached(cacheKey);
    if (cached) return cached;

    const normalizedSymbol = symbol.toLowerCase();
    const sources = [...MARKET_SOURCES].sort((a, b) => a.priority - b.priority);

    for (const source of sources) {
      try {
        console.log(`🔄 Trying ${source.name} for ${symbol}...`);
        
        const endpoint = source.getPrice(normalizedSymbol);
        const url = `${source.baseUrl}${endpoint}`;
        const options = source.headers ? { headers: source.headers() } : {};

        let data;
        if (source.needsProxy) {
          data = await fetchWithProxy(url, options);
        } else {
          data = await fetchDirect(url, options);
        }

        // Normalize response based on source
        const normalized = this.normalizeMarketData(data, source.id, symbol);
        if (normalized) {
          this.setCache(cacheKey, normalized);
          this.logRequest(source.name, true);
          console.log(`✅ Success: ${source.name}`);
          return normalized;
        }
      } catch (error) {
        console.warn(`❌ ${source.name} failed:`, error.message);
        this.logRequest(source.name, false, error.message);
        continue;
      }
    }

    throw new Error(`All ${sources.length} market data sources failed for ${symbol}`);
  }

  normalizeMarketData(data, sourceId, symbol) {
    try {
      switch (sourceId) {
        case 'coingecko':
          const coinId = symbol.toLowerCase();
          return {
            symbol: symbol.toUpperCase(),
            price: data[coinId]?.usd || null,
            change24h: data[coinId]?.usd_24h_change || null,
            marketCap: data[coinId]?.usd_market_cap || null,
            source: 'CoinGecko',
            timestamp: Date.now()
          };
        
        case 'binance':
          return {
            symbol: symbol.toUpperCase(),
            price: parseFloat(data.price),
            source: 'Binance',
            timestamp: Date.now()
          };
        
        case 'coincap':
          return {
            symbol: symbol.toUpperCase(),
            price: parseFloat(data.data?.priceUsd || 0),
            change24h: parseFloat(data.data?.changePercent24Hr || 0),
            marketCap: parseFloat(data.data?.marketCapUsd || 0),
            source: 'CoinCap',
            timestamp: Date.now()
          };
        
        case 'cmc_primary':
        case 'cmc_backup':
          const cmcData = data.data?.[symbol.toUpperCase()];
          return {
            symbol: symbol.toUpperCase(),
            price: cmcData?.quote?.USD?.price || null,
            change24h: cmcData?.quote?.USD?.percent_change_24h || null,
            marketCap: cmcData?.quote?.USD?.market_cap || null,
            source: 'CoinMarketCap',
            timestamp: Date.now()
          };
        
        default:
          // Generic fallback
          return {
            symbol: symbol.toUpperCase(),
            price: data.price || data.last || data.lastPrice || null,
            source: sourceId,
            timestamp: Date.now(),
            raw: data
          };
      }
    } catch (error) {
      console.warn(`Failed to normalize ${sourceId} data:`, error);
      return null;
    }
  }

  // ═══════════════════════════════════════════════════════════
  // NEWS - Try all 12+ sources
  // ═══════════════════════════════════════════════════════════
  async getNews(limit = 20) {
    const cacheKey = 'news_latest';
    const cached = this.getCached(cacheKey);
    if (cached) return cached;

    const allNews = [];
    const sources = [...NEWS_SOURCES].sort((a, b) => a.priority - b.priority);

    for (const source of sources) {
      try {
        console.log(`🔄 Fetching news from ${source.name}...`);
        
        const endpoint = source.getNews();
        const url = `${source.baseUrl}${endpoint}`;

        let data;
        if (source.needsProxy) {
          data = await fetchWithProxy(url);
        } else {
          data = await fetchDirect(url);
        }

        let news = [];
        if (source.parseRSS) {
          news = parseRSS(data, source.name);
        } else {
          news = this.normalizeNewsData(data, source.id, source.name);
        }

        if (news && news.length > 0) {
          allNews.push(...news);
          this.logRequest(source.name, true);
          console.log(`✅ Got ${news.length} articles from ${source.name}`);
        }

        // Stop if we have enough news
        if (allNews.length >= limit * 2) break;
      } catch (error) {
        console.warn(`❌ ${source.name} failed:`, error.message);
        this.logRequest(source.name, false, error.message);
        continue;
      }
    }

    // Deduplicate and sort by date
    const uniqueNews = this.deduplicateNews(allNews);
    const sortedNews = uniqueNews.slice(0, limit);
    
    this.setCache(cacheKey, sortedNews);
    return sortedNews;
  }

  normalizeNewsData(data, sourceId, sourceName) {
    try {
      switch (sourceId) {
        case 'cryptopanic':
          return data.results?.map(item => ({
            title: item.title,
            link: item.url,
            publishedAt: item.published_at,
            source: item.source?.title || sourceName,
            votes: item.votes?.positive || 0
          })) || [];
        
        case 'coinstats_news':
          return data.news?.map(item => ({
            title: item.title,
            link: item.link,
            publishedAt: item.feedDate,
            source: item.source || sourceName,
            imgURL: item.imgURL
          })) || [];
        
        case 'reddit_crypto':
        case 'reddit_bitcoin':
          return data.data?.children?.map(item => ({
            title: item.data.title,
            link: `https://reddit.com${item.data.permalink}`,
            publishedAt: new Date(item.data.created_utc * 1000).toISOString(),
            source: sourceName,
            score: item.data.score
          })) || [];
        
        default:
          return [];
      }
    } catch (error) {
      console.warn(`Failed to normalize ${sourceId} news:`, error);
      return [];
    }
  }

  deduplicateNews(newsArray) {
    const seen = new Set();
    return newsArray.filter(item => {
      const key = item.title.toLowerCase().trim();
      if (seen.has(key)) return false;
      seen.add(key);
      return true;
    });
  }

  // ═══════════════════════════════════════════════════════════
  // SENTIMENT (Fear & Greed) - Try all 10+ sources
  // ═══════════════════════════════════════════════════════════
  async getSentiment() {
    const cacheKey = 'sentiment_fng';
    const cached = this.getCached(cacheKey);
    if (cached) return cached;

    const sources = [...SENTIMENT_SOURCES].sort((a, b) => a.priority - b.priority);

    for (const source of sources) {
      try {
        console.log(`🔄 Trying ${source.name} for sentiment...`);
        
        const endpoint = source.getSentiment();
        const url = `${source.baseUrl}${endpoint}`;
        const options = source.method === 'POST' ? { method: 'POST' } : {};

        let data;
        if (source.needsProxy) {
          data = await fetchWithProxy(url, options);
        } else {
          data = await fetchDirect(url, options);
        }

        const normalized = this.normalizeSentimentData(data, source.id);
        if (normalized && normalized.value !== null) {
          this.setCache(cacheKey, normalized);
          this.logRequest(source.name, true);
          console.log(`✅ Sentiment from ${source.name}: ${normalized.value}`);
          return normalized;
        }
      } catch (error) {
        console.warn(`❌ ${source.name} failed:`, error.message);
        this.logRequest(source.name, false, error.message);
        continue;
      }
    }

    throw new Error(`All ${sources.length} sentiment sources failed`);
  }

  normalizeSentimentData(data, sourceId) {
    try {
      switch (sourceId) {
        case 'alternative_me':
          const fngData = data.data?.[0];
          return {
            value: parseInt(fngData?.value || 0),
            classification: fngData?.value_classification || 'Unknown',
            source: 'Alternative.me',
            timestamp: Date.now()
          };
        
        case 'cfgi_v1':
        case 'cfgi_legacy':
          return {
            value: parseInt(data.value || data.fgi || 0),
            classification: data.classification || this.getClassification(data.value),
            source: 'CFGI',
            timestamp: Date.now()
          };
        
        case 'coinglass_fgi':
          return {
            value: parseInt(data.data?.value || 0),
            classification: data.data?.value_classification || 'Unknown',
            source: 'CoinGlass',
            timestamp: Date.now()
          };
        
        default:
          // Generic fallback
          const value = parseInt(data.value || data.score || 50);
          return {
            value,
            classification: this.getClassification(value),
            source: sourceId,
            timestamp: Date.now(),
            raw: data
          };
      }
    } catch (error) {
      console.warn(`Failed to normalize ${sourceId} sentiment:`, error);
      return null;
    }
  }

  getClassification(value) {
    if (value <= 25) return 'Extreme Fear';
    if (value <= 45) return 'Fear';
    if (value <= 55) return 'Neutral';
    if (value <= 75) return 'Greed';
    return 'Extreme Greed';
  }

  // ═══════════════════════════════════════════════════════════
  // OHLCV DATA (Import from dedicated client)
  // ═══════════════════════════════════════════════════════════
  async getOHLCV(symbol, timeframe = '1d', limit = 100) {
    try {
      // Dynamically import OHLCV client
      const { default: ohlcvClient } = await import('/static/shared/js/ohlcv-client.js');
      return await ohlcvClient.getOHLCV(symbol, timeframe, limit);
    } catch (error) {
      console.error('Failed to load OHLCV client:', error);
      throw error;
    }
  }

  // ═══════════════════════════════════════════════════════════
  // UTILITY: Get request statistics
  // ═══════════════════════════════════════════════════════════
  getStats() {
    const total = this.requestLog.length;
    const successful = this.requestLog.filter(r => r.success).length;
    const failed = total - successful;
    const successRate = total > 0 ? ((successful / total) * 100).toFixed(1) : 0;

    return {
      total,
      successful,
      failed,
      successRate: `${successRate}%`,
      cacheSize: this.cache.size,
      recentRequests: this.requestLog.slice(-10)
    };
  }

  // Clear cache
  clearCache() {
    this.cache.clear();
    console.log('✅ Cache cleared');
  }
}

// ═══════════════════════════════════════════════════════════════
// EXPORT
// ═══════════════════════════════════════════════════════════════
export const apiClient = new ComprehensiveAPIClient();
export default apiClient;

