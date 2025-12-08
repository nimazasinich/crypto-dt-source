/**
 * OHLCV Data Client - Comprehensive Multi-Source Integration
 * Provides candlestick/OHLCV data from 15+ sources with automatic fallback
 * Uses all resources from all_apis_merged_2025.json
 * 
 * Supports multiple timeframes: 1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w, 1M
 */

// ═══════════════════════════════════════════════════════════════
// API KEYS (from all_apis_merged_2025.json)
// ═══════════════════════════════════════════════════════════════
const API_KEYS = {
  CRYPTOCOMPARE: 'e79c8e6d4c5b4a3f2e1d0c9b8a7f6e5d4c3b2a1f',
  CMC: 'b54bcf4d-1bca-4e8e-9a24-22ff2c3d462c',
  CMC_BACKUP: '04cf4b5b-9868-465c-8ba0-9f2e78c92eb1',
  ETHERSCAN: 'SZHYFZK2RR8H9TIMJBVW54V4H81K2Z2KR2',
  BSCSCAN: 'K62RKHGXTDCG53RU4MCG6XABIMJKTN19IT',
  TRONSCAN: '7ae72726-bffe-4e74-9c33-97b761eeea21'
};

// ═══════════════════════════════════════════════════════════════
// OHLCV DATA SOURCES (15+ endpoints as required)
// ═══════════════════════════════════════════════════════════════
const OHLCV_SOURCES = [
  // ─────────────────────────────────────────────────────────────
  // TIER 1: Direct, No Auth Required (Highest Priority)
  // ─────────────────────────────────────────────────────────────
  {
    id: 'binance',
    name: 'Binance Public API',
    baseUrl: 'https://api.binance.com',
    needsProxy: false,
    needsAuth: false,
    priority: 1,
    maxLimit: 1000,
    
    timeframeMap: {
      '1m': '1m', '5m': '5m', '15m': '15m', '30m': '30m',
      '1h': '1h', '4h': '4h', '1d': '1d', '1w': '1w', '1M': '1M'
    },
    
    buildUrl: (symbol, timeframe, limit) => {
      const interval = OHLCV_SOURCES[0].timeframeMap[timeframe] || '1d';
      return `/api/v3/klines?symbol=${symbol.toUpperCase()}USDT&interval=${interval}&limit=${limit}`;
    },
    
    parseResponse: (data) => {
      return data.map(item => ({
        timestamp: item[0],
        open: parseFloat(item[1]),
        high: parseFloat(item[2]),
        low: parseFloat(item[3]),
        close: parseFloat(item[4]),
        volume: parseFloat(item[5])
      }));
    }
  },

  {
    id: 'coingecko_ohlc',
    name: 'CoinGecko OHLC',
    baseUrl: 'https://api.coingecko.com/api/v3',
    needsProxy: false,
    needsAuth: false,
    priority: 2,
    maxLimit: 365,
    
    buildUrl: (symbol, timeframe, limit) => {
      const days = limit > 90 ? 365 : limit > 30 ? 90 : limit > 7 ? 30 : 7;
      return `/coins/${symbol.toLowerCase()}/ohlc?vs_currency=usd&days=${days}`;
    },
    
    parseResponse: (data) => {
      return data.map(item => ({
        timestamp: item[0],
        open: item[1],
        high: item[2],
        low: item[3],
        close: item[4],
        volume: null // CoinGecko OHLC doesn't include volume
      }));
    }
  },

  {
    id: 'coinpaprika',
    name: 'CoinPaprika Historical',
    baseUrl: 'https://api.coinpaprika.com/v1',
    needsProxy: false,
    needsAuth: false,
    priority: 3,
    maxLimit: 366,
    
    buildUrl: (symbol, timeframe, limit) => {
      const now = new Date();
      const start = new Date(now.getTime() - (limit * 24 * 60 * 60 * 1000));
      return `/coins/${symbol.toLowerCase()}-${symbol.toLowerCase()}/ohlcv/historical?start=${start.toISOString().split('T')[0]}&end=${now.toISOString().split('T')[0]}`;
    },
    
    parseResponse: (data) => {
      return data.map(item => ({
        timestamp: new Date(item.time_open).getTime(),
        open: item.open,
        high: item.high,
        low: item.low,
        close: item.close,
        volume: item.volume
      }));
    }
  },

  {
    id: 'coincap_history',
    name: 'CoinCap History',
    baseUrl: 'https://api.coincap.io/v2',
    needsProxy: false,
    needsAuth: false,
    priority: 4,
    maxLimit: 2000,
    
    timeframeMap: {
      '1m': 'm1', '5m': 'm5', '15m': 'm15', '30m': 'm30',
      '1h': 'h1', '4h': 'h6', '1d': 'd1'
    },
    
    buildUrl: (symbol, timeframe, limit) => {
      const interval = OHLCV_SOURCES.find(s => s.id === 'coincap_history').timeframeMap[timeframe] || 'd1';
      const end = Date.now();
      const start = end - (limit * this.getIntervalMs(timeframe));
      return `/assets/${symbol.toLowerCase()}/history?interval=${interval}&start=${start}&end=${end}`;
    },
    
    parseResponse: (data) => {
      if (!data.data) return [];
      return data.data.map(item => ({
        timestamp: item.time,
        open: parseFloat(item.priceUsd),
        high: parseFloat(item.priceUsd),
        low: parseFloat(item.priceUsd),
        close: parseFloat(item.priceUsd),
        volume: null
      }));
    }
  },

  {
    id: 'kraken',
    name: 'Kraken Public OHLC',
    baseUrl: 'https://api.kraken.com/0/public',
    needsProxy: false,
    needsAuth: false,
    priority: 5,
    maxLimit: 720,
    
    timeframeMap: {
      '1m': '1', '5m': '5', '15m': '15', '30m': '30',
      '1h': '60', '4h': '240', '1d': '1440', '1w': '10080'
    },
    
    buildUrl: (symbol, timeframe, limit) => {
      const interval = OHLCV_SOURCES.find(s => s.id === 'kraken').timeframeMap[timeframe] || '1440';
      const pair = `${symbol.toUpperCase()}USD`;
      return `/OHLC?pair=${pair}&interval=${interval}`;
    },
    
    parseResponse: (data) => {
      if (!data.result) return [];
      const pair = Object.keys(data.result).find(k => k !== 'last');
      if (!pair) return [];
      
      return data.result[pair].map(item => ({
        timestamp: item[0] * 1000,
        open: parseFloat(item[1]),
        high: parseFloat(item[2]),
        low: parseFloat(item[3]),
        close: parseFloat(item[4]),
        volume: parseFloat(item[6])
      }));
    }
  },

  // ─────────────────────────────────────────────────────────────
  // TIER 2: Require API Key but Direct Access
  // ─────────────────────────────────────────────────────────────
  {
    id: 'cryptocompare_minute',
    name: 'CryptoCompare Minute',
    baseUrl: 'https://min-api.cryptocompare.com/data/v2',
    needsProxy: false,
    needsAuth: true,
    priority: 6,
    maxLimit: 2000,
    
    buildUrl: (symbol, timeframe, limit) => {
      const endpoint = timeframe.includes('m') ? 'histominute' :
                      timeframe.includes('h') ? 'histohour' : 'histoday';
      return `/${endpoint}?fsym=${symbol.toUpperCase()}&tsym=USD&limit=${limit}&api_key=${API_KEYS.CRYPTOCOMPARE}`;
    },
    
    parseResponse: (data) => {
      if (!data.Data || !data.Data.Data) return [];
      return data.Data.Data.map(item => ({
        timestamp: item.time * 1000,
        open: item.open,
        high: item.high,
        low: item.low,
        close: item.close,
        volume: item.volumefrom
      }));
    }
  },

  {
    id: 'cryptocompare_hour',
    name: 'CryptoCompare Hour',
    baseUrl: 'https://min-api.cryptocompare.com/data/v2',
    needsProxy: false,
    needsAuth: true,
    priority: 7,
    maxLimit: 2000,
    
    buildUrl: (symbol, timeframe, limit) => {
      return `/histohour?fsym=${symbol.toUpperCase()}&tsym=USD&limit=${limit}&api_key=${API_KEYS.CRYPTOCOMPARE}`;
    },
    
    parseResponse: (data) => {
      if (!data.Data || !data.Data.Data) return [];
      return data.Data.Data.map(item => ({
        timestamp: item.time * 1000,
        open: item.open,
        high: item.high,
        low: item.low,
        close: item.close,
        volume: item.volumefrom
      }));
    }
  },

  {
    id: 'cryptocompare_day',
    name: 'CryptoCompare Day',
    baseUrl: 'https://min-api.cryptocompare.com/data/v2',
    needsProxy: false,
    needsAuth: true,
    priority: 8,
    maxLimit: 2000,
    
    buildUrl: (symbol, timeframe, limit) => {
      return `/histoday?fsym=${symbol.toUpperCase()}&tsym=USD&limit=${limit}&api_key=${API_KEYS.CRYPTOCOMPARE}`;
    },
    
    parseResponse: (data) => {
      if (!data.Data || !data.Data.Data) return [];
      return data.Data.Data.map(item => ({
        timestamp: item.time * 1000,
        open: item.open,
        high: item.high,
        low: item.low,
        close: item.close,
        volume: item.volumefrom
      }));
    }
  },

  // ─────────────────────────────────────────────────────────────
  // TIER 3: Additional Sources (More Fallbacks)
  // ─────────────────────────────────────────────────────────────
  {
    id: 'bitfinex',
    name: 'Bitfinex Candles',
    baseUrl: 'https://api-pub.bitfinex.com/v2',
    needsProxy: false,
    needsAuth: false,
    priority: 9,
    maxLimit: 10000,
    
    timeframeMap: {
      '1m': '1m', '5m': '5m', '15m': '15m', '30m': '30m',
      '1h': '1h', '4h': '4h', '1d': '1D', '1w': '7D', '1M': '1M'
    },
    
    buildUrl: (symbol, timeframe, limit) => {
      const tf = OHLCV_SOURCES.find(s => s.id === 'bitfinex').timeframeMap[timeframe] || '1D';
      const now = Date.now();
      const start = now - (limit * this.getIntervalMs(timeframe));
      return `/candles/trade:${tf}:t${symbol.toUpperCase()}USD/hist?limit=${limit}&start=${start}&end=${now}`;
    },
    
    parseResponse: (data) => {
      return data.map(item => ({
        timestamp: item[0],
        open: item[1],
        high: item[3],
        low: item[4],
        close: item[2],
        volume: item[5]
      }));
    }
  },

  {
    id: 'coinbase',
    name: 'Coinbase Pro Candles',
    baseUrl: 'https://api.exchange.coinbase.com',
    needsProxy: false,
    needsAuth: false,
    priority: 10,
    maxLimit: 300,
    
    timeframeMap: {
      '1m': '60', '5m': '300', '15m': '900',
      '1h': '3600', '4h': '14400', '1d': '86400'
    },
    
    buildUrl: (symbol, timeframe, limit) => {
      const granularity = OHLCV_SOURCES.find(s => s.id === 'coinbase').timeframeMap[timeframe] || '86400';
      const end = Math.floor(Date.now() / 1000);
      const start = end - (limit * parseInt(granularity));
      return `/products/${symbol.toUpperCase()}-USD/candles?granularity=${granularity}&start=${start}&end=${end}`;
    },
    
    parseResponse: (data) => {
      return data.map(item => ({
        timestamp: item[0] * 1000,
        low: item[1],
        high: item[2],
        open: item[3],
        close: item[4],
        volume: item[5]
      }));
    }
  },

  {
    id: 'gemini',
    name: 'Gemini Candles',
    baseUrl: 'https://api.gemini.com/v2',
    needsProxy: false,
    needsAuth: false,
    priority: 11,
    maxLimit: 500,
    
    timeframeMap: {
      '1m': '1m', '5m': '5m', '15m': '15m', '30m': '30m',
      '1h': '1hr', '4h': '6hr', '1d': '1day'
    },
    
    buildUrl: (symbol, timeframe, limit) => {
      const tf = OHLCV_SOURCES.find(s => s.id === 'gemini').timeframeMap[timeframe] || '1day';
      return `/candles/${symbol.toLowerCase()}usd/${tf}`;
    },
    
    parseResponse: (data) => {
      return data.map(item => ({
        timestamp: item[0],
        open: item[1],
        high: item[2],
        low: item[3],
        close: item[4],
        volume: item[5]
      }));
    }
  },

  {
    id: 'okx',
    name: 'OKX Market Data',
    baseUrl: 'https://www.okx.com/api/v5/market',
    needsProxy: false,
    needsAuth: false,
    priority: 12,
    maxLimit: 300,
    
    timeframeMap: {
      '1m': '1m', '5m': '5m', '15m': '15m', '30m': '30m',
      '1h': '1H', '4h': '4H', '1d': '1D', '1w': '1W'
    },
    
    buildUrl: (symbol, timeframe, limit) => {
      const bar = OHLCV_SOURCES.find(s => s.id === 'okx').timeframeMap[timeframe] || '1D';
      return `/candles?instId=${symbol.toUpperCase()}-USDT&bar=${bar}&limit=${limit}`;
    },
    
    parseResponse: (data) => {
      if (!data.data) return [];
      return data.data.map(item => ({
        timestamp: parseInt(item[0]),
        open: parseFloat(item[1]),
        high: parseFloat(item[2]),
        low: parseFloat(item[3]),
        close: parseFloat(item[4]),
        volume: parseFloat(item[5])
      }));
    }
  },

  {
    id: 'kucoin',
    name: 'KuCoin Market Data',
    baseUrl: 'https://api.kucoin.com/api/v1',
    needsProxy: false,
    needsAuth: false,
    priority: 13,
    maxLimit: 1500,
    
    timeframeMap: {
      '1m': '1min', '5m': '5min', '15m': '15min', '30m': '30min',
      '1h': '1hour', '4h': '4hour', '1d': '1day', '1w': '1week'
    },
    
    buildUrl: (symbol, timeframe, limit) => {
      const type = OHLCV_SOURCES.find(s => s.id === 'kucoin').timeframeMap[timeframe] || '1day';
      const end = Math.floor(Date.now() / 1000);
      const start = end - (limit * this.getIntervalSeconds(timeframe));
      return `/market/candles?type=${type}&symbol=${symbol.toUpperCase()}-USDT&startAt=${start}&endAt=${end}`;
    },
    
    parseResponse: (data) => {
      if (!data.data) return [];
      return data.data.map(item => ({
        timestamp: parseInt(item[0]) * 1000,
        open: parseFloat(item[1]),
        close: parseFloat(item[2]),
        high: parseFloat(item[3]),
        low: parseFloat(item[4]),
        volume: parseFloat(item[5])
      }));
    }
  },

  {
    id: 'bybit',
    name: 'Bybit Market Data',
    baseUrl: 'https://api.bybit.com/v5/market',
    needsProxy: false,
    needsAuth: false,
    priority: 14,
    maxLimit: 200,
    
    timeframeMap: {
      '1m': '1', '5m': '5', '15m': '15', '30m': '30',
      '1h': '60', '4h': '240', '1d': 'D', '1w': 'W', '1M': 'M'
    },
    
    buildUrl: (symbol, timeframe, limit) => {
      const interval = OHLCV_SOURCES.find(s => s.id === 'bybit').timeframeMap[timeframe] || 'D';
      return `/kline?category=spot&symbol=${symbol.toUpperCase()}USDT&interval=${interval}&limit=${limit}`;
    },
    
    parseResponse: (data) => {
      if (!data.result || !data.result.list) return [];
      return data.result.list.map(item => ({
        timestamp: parseInt(item[0]),
        open: parseFloat(item[1]),
        high: parseFloat(item[2]),
        low: parseFloat(item[3]),
        close: parseFloat(item[4]),
        volume: parseFloat(item[5])
      }));
    }
  },

  {
    id: 'gate_io',
    name: 'Gate.io Market Data',
    baseUrl: 'https://api.gateio.ws/api/v4',
    needsProxy: false,
    needsAuth: false,
    priority: 15,
    maxLimit: 1000,
    
    timeframeMap: {
      '1m': '1m', '5m': '5m', '15m': '15m', '30m': '30m',
      '1h': '1h', '4h': '4h', '1d': '1d', '1w': '7d'
    },
    
    buildUrl: (symbol, timeframe, limit) => {
      const interval = OHLCV_SOURCES.find(s => s.id === 'gate_io').timeframeMap[timeframe] || '1d';
      return `/spot/candlesticks?currency_pair=${symbol.toUpperCase()}_USDT&interval=${interval}&limit=${limit}`;
    },
    
    parseResponse: (data) => {
      return data.map(item => ({
        timestamp: parseInt(item[0]) * 1000,
        open: parseFloat(item[5]),
        high: parseFloat(item[3]),
        low: parseFloat(item[4]),
        close: parseFloat(item[2]),
        volume: parseFloat(item[1])
      }));
    }
  },

  // ─────────────────────────────────────────────────────────────
  // TIER 4: Alternative/Backup Sources
  // ─────────────────────────────────────────────────────────────
  {
    id: 'bitstamp',
    name: 'Bitstamp OHLC',
    baseUrl: 'https://www.bitstamp.net/api/v2',
    needsProxy: false,
    needsAuth: false,
    priority: 16,
    maxLimit: 1000,
    
    timeframeMap: {
      '1m': '60', '5m': '300', '15m': '900', '30m': '1800',
      '1h': '3600', '4h': '14400', '1d': '86400'
    },
    
    buildUrl: (symbol, timeframe, limit) => {
      const step = OHLCV_SOURCES.find(s => s.id === 'bitstamp').timeframeMap[timeframe] || '86400';
      return `/ohlc/${symbol.toLowerCase()}usd/?step=${step}&limit=${limit}`;
    },
    
    parseResponse: (data) => {
      if (!data.data || !data.data.ohlc) return [];
      return data.data.ohlc.map(item => ({
        timestamp: parseInt(item.timestamp) * 1000,
        open: parseFloat(item.open),
        high: parseFloat(item.high),
        low: parseFloat(item.low),
        close: parseFloat(item.close),
        volume: parseFloat(item.volume)
      }));
    }
  },

  {
    id: 'mexc',
    name: 'MEXC Market Data',
    baseUrl: 'https://api.mexc.com/api/v3',
    needsProxy: false,
    needsAuth: false,
    priority: 17,
    maxLimit: 1000,
    
    timeframeMap: {
      '1m': '1m', '5m': '5m', '15m': '15m', '30m': '30m',
      '1h': '1h', '4h': '4h', '1d': '1d', '1w': '1w', '1M': '1M'
    },
    
    buildUrl: (symbol, timeframe, limit) => {
      const interval = OHLCV_SOURCES.find(s => s.id === 'mexc').timeframeMap[timeframe] || '1d';
      return `/klines?symbol=${symbol.toUpperCase()}USDT&interval=${interval}&limit=${limit}`;
    },
    
    parseResponse: (data) => {
      return data.map(item => ({
        timestamp: item[0],
        open: parseFloat(item[1]),
        high: parseFloat(item[2]),
        low: parseFloat(item[3]),
        close: parseFloat(item[4]),
        volume: parseFloat(item[5])
      }));
    }
  },

  {
    id: 'huobi',
    name: 'Huobi Market Data',
    baseUrl: 'https://api.huobi.pro/market',
    needsProxy: false,
    needsAuth: false,
    priority: 18,
    maxLimit: 2000,
    
    timeframeMap: {
      '1m': '1min', '5m': '5min', '15m': '15min', '30m': '30min',
      '1h': '60min', '4h': '4hour', '1d': '1day', '1w': '1week', '1M': '1mon'
    },
    
    buildUrl: (symbol, timeframe, limit) => {
      const period = OHLCV_SOURCES.find(s => s.id === 'huobi').timeframeMap[timeframe] || '1day';
      return `/history/kline?symbol=${symbol.toLowerCase()}usdt&period=${period}&size=${limit}`;
    },
    
    parseResponse: (data) => {
      if (!data.data) return [];
      return data.data.map(item => ({
        timestamp: item.id * 1000,
        open: item.open,
        high: item.high,
        low: item.low,
        close: item.close,
        volume: item.vol
      }));
    }
  },

  {
    id: 'defillama',
    name: 'DefiLlama Charts',
    baseUrl: 'https://coins.llama.fi',
    needsProxy: false,
    needsAuth: false,
    priority: 19,
    maxLimit: 365,
    
    buildUrl: (symbol, timeframe, limit) => {
      const span = limit * this.getIntervalSeconds(timeframe);
      const start = Math.floor(Date.now() / 1000) - span;
      return `/chart/coingecko:${symbol.toLowerCase()}?start=${start}&span=${limit}&period=1d`;
    },
    
    parseResponse: (data) => {
      if (!data.coins) return [];
      const coinKey = Object.keys(data.coins)[0];
      if (!coinKey || !data.coins[coinKey].prices) return [];
      
      return data.coins[coinKey].prices.map(item => ({
        timestamp: item.timestamp * 1000,
        open: item.price,
        high: item.price,
        low: item.price,
        close: item.price,
        volume: null
      }));
    }
  },

  {
    id: 'bitget',
    name: 'Bitget Market Data',
    baseUrl: 'https://api.bitget.com/api/spot/v1',
    needsProxy: false,
    needsAuth: false,
    priority: 20,
    maxLimit: 1000,
    
    timeframeMap: {
      '1m': '1m', '5m': '5m', '15m': '15m', '30m': '30m',
      '1h': '1h', '4h': '4h', '1d': '1day', '1w': '1week'
    },
    
    buildUrl: (symbol, timeframe, limit) => {
      const period = OHLCV_SOURCES.find(s => s.id === 'bitget').timeframeMap[timeframe] || '1day';
      const end = Date.now();
      const start = end - (limit * this.getIntervalMs(timeframe));
      return `/market/candles?symbol=${symbol.toUpperCase()}USDT_SPBL&period=${period}&after=${start}&before=${end}&limit=${limit}`;
    },
    
    parseResponse: (data) => {
      if (!data.data) return [];
      return data.data.map(item => ({
        timestamp: parseInt(item[0]),
        open: parseFloat(item[1]),
        high: parseFloat(item[2]),
        low: parseFloat(item[3]),
        close: parseFloat(item[4]),
        volume: parseFloat(item[5])
      }));
    }
  },

  {
    id: 'messari',
    name: 'Messari Timeseries',
    baseUrl: 'https://data.messari.io/api/v1',
    needsProxy: false,
    needsAuth: false,
    priority: 21,
    maxLimit: 2000,
    
    buildUrl: (symbol, timeframe, limit) => {
      const interval = timeframe.includes('h') ? '1h' : '1d';
      const start = new Date(Date.now() - (limit * this.getIntervalMs(timeframe))).toISOString();
      const end = new Date().toISOString();
      return `/assets/${symbol.toLowerCase()}/metrics/price/time-series?start=${start}&end=${end}&interval=${interval}`;
    },
    
    parseResponse: (data) => {
      if (!data.data || !data.data.values) return [];
      return data.data.values.map(item => ({
        timestamp: item[0],
        open: item[1],
        high: item[1],
        low: item[1],
        close: item[1],
        volume: null
      }));
    }
  }
];

// ═══════════════════════════════════════════════════════════════
// HELPER FUNCTIONS
// ═══════════════════════════════════════════════════════════════

function getIntervalMs(timeframe) {
  const map = {
    '1m': 60 * 1000,
    '5m': 5 * 60 * 1000,
    '15m': 15 * 60 * 1000,
    '30m': 30 * 60 * 1000,
    '1h': 60 * 60 * 1000,
    '4h': 4 * 60 * 60 * 1000,
    '1d': 24 * 60 * 60 * 1000,
    '1w': 7 * 24 * 60 * 60 * 1000,
    '1M': 30 * 24 * 60 * 60 * 1000
  };
  return map[timeframe] || map['1d'];
}

function getIntervalSeconds(timeframe) {
  return Math.floor(getIntervalMs(timeframe) / 1000);
}

async function fetchWithTimeout(url, options = {}, timeout = 15000) {
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

// ═══════════════════════════════════════════════════════════════
// OHLCV CLIENT CLASS
// ═══════════════════════════════════════════════════════════════

class OHLCVClient {
  constructor() {
    this.cache = new Map();
    this.cacheTimeout = 60000; // 1 minute for OHLCV data
    this.requestLog = [];
    this.sources = OHLCV_SOURCES.sort((a, b) => a.priority - b.priority);
  }

  /**
   * Get OHLCV data with automatic fallback through all sources
   * @param {string} symbol - Symbol (e.g., 'bitcoin', 'BTC')
   * @param {string} timeframe - Timeframe ('1m', '5m', '15m', '30m', '1h', '4h', '1d', '1w', '1M')
   * @param {number} limit - Number of candles (default: 100)
   * @returns {Promise<Array>} Array of OHLCV objects
   */
  async getOHLCV(symbol, timeframe = '1d', limit = 100) {
    const cacheKey = `ohlcv_${symbol}_${timeframe}_${limit}`;
    
    // Check cache
    const cached = this.getCached(cacheKey);
    if (cached) {
      console.log(`📦 Using cached OHLCV data for ${symbol} ${timeframe}`);
      return cached;
    }

    console.log(`🔍 Fetching OHLCV: ${symbol} ${timeframe} (${limit} candles)`);
    console.log(`📊 Trying ${this.sources.length} sources...`);

    // Try each source in priority order
    for (const source of this.sources) {
      try {
        console.log(`🔄 [${source.priority}/${this.sources.length}] Trying ${source.name}...`);
        
        // Build URL
        const endpoint = source.buildUrl(symbol, timeframe, Math.min(limit, source.maxLimit));
        const url = `${source.baseUrl}${endpoint}`;
        
        // Fetch data
        const response = await fetchWithTimeout(url, {}, 15000);
        
        if (!response.ok) {
          throw new Error(`HTTP ${response.status}`);
        }
        
        const rawData = await response.json();
        
        // Parse response
        const ohlcv = source.parseResponse(rawData);
        
        // Validate data
        if (!ohlcv || ohlcv.length === 0) {
          throw new Error('Empty dataset');
        }

        // Sort by timestamp (ascending)
        ohlcv.sort((a, b) => a.timestamp - b.timestamp);
        
        // Limit to requested amount
        const result = ohlcv.slice(-limit);
        
        // Cache successful result
        this.setCache(cacheKey, result);
        this.logRequest(source.name, true, result.length);
        
        console.log(`✅ SUCCESS: ${source.name} returned ${result.length} candles`);
        console.log(`   Date Range: ${new Date(result[0].timestamp).toLocaleDateString()} → ${new Date(result[result.length - 1].timestamp).toLocaleDateString()}`);
        
        return result;
        
      } catch (error) {
        console.warn(`❌ ${source.name} failed:`, error.message);
        this.logRequest(source.name, false, error.message);
        continue;
      }
    }

    throw new Error(`All ${this.sources.length} OHLCV sources failed for ${symbol} ${timeframe}`);
  }

  /**
   * Get OHLCV from specific source (for testing)
   * @param {string} sourceId - Source ID
   * @param {string} symbol - Symbol
   * @param {string} timeframe - Timeframe
   * @param {number} limit - Limit
   */
  async getFromSource(sourceId, symbol, timeframe = '1d', limit = 100) {
    const source = this.sources.find(s => s.id === sourceId);
    if (!source) {
      throw new Error(`Source '${sourceId}' not found`);
    }

    console.log(`🎯 Direct request to ${source.name}...`);
    
    const endpoint = source.buildUrl(symbol, timeframe, Math.min(limit, source.maxLimit));
    const url = `${source.baseUrl}${endpoint}`;
    
    const response = await fetchWithTimeout(url);
    if (!response.ok) {
      throw new Error(`HTTP ${response.status}`);
    }
    
    const rawData = await response.json();
    const ohlcv = source.parseResponse(rawData);
    
    console.log(`✅ ${source.name}: ${ohlcv.length} candles`);
    return ohlcv;
  }

  /**
   * Get OHLCV from multiple sources in parallel (for aggregation/validation)
   * @param {string} symbol - Symbol
   * @param {string} timeframe - Timeframe
   * @param {number} limit - Limit
   * @param {number} sourceCount - Number of sources to try (default: 3)
   */
  async getMultiSource(symbol, timeframe = '1d', limit = 100, sourceCount = 3) {
    console.log(`🔄 Fetching from ${sourceCount} sources in parallel...`);
    
    const promises = this.sources.slice(0, sourceCount).map(async (source) => {
      try {
        const endpoint = source.buildUrl(symbol, timeframe, Math.min(limit, source.maxLimit));
        const url = `${source.baseUrl}${endpoint}`;
        const response = await fetchWithTimeout(url, {}, 10000);
        
        if (!response.ok) throw new Error(`HTTP ${response.status}`);
        
        const rawData = await response.json();
        const ohlcv = source.parseResponse(rawData);
        
        return {
          source: source.name,
          sourceId: source.id,
          data: ohlcv.slice(-limit),
          success: true
        };
      } catch (error) {
        return {
          source: source.name,
          sourceId: source.id,
          error: error.message,
          success: false
        };
      }
    });

    const results = await Promise.allSettled(promises);
    
    const successful = results
      .filter(r => r.status === 'fulfilled' && r.value.success)
      .map(r => r.value);
    
    const failed = results
      .filter(r => r.status === 'rejected' || (r.status === 'fulfilled' && !r.value.success))
      .map(r => r.status === 'fulfilled' ? r.value : { source: 'unknown', error: r.reason?.message });

    console.log(`✅ Successful: ${successful.length}/${sourceCount}`);
    console.log(`❌ Failed: ${failed.length}/${sourceCount}`);
    
    return {
      successful,
      failed,
      total: sourceCount
    };
  }

  // Cache management
  getCached(key) {
    const cached = this.cache.get(key);
    if (cached && Date.now() - cached.timestamp < this.cacheTimeout) {
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

  clearCache() {
    this.cache.clear();
    console.log('✅ OHLCV cache cleared');
  }

  // Request logging
  logRequest(source, success, detail) {
    this.requestLog.push({
      source,
      success,
      detail,
      timestamp: new Date().toISOString()
    });
    
    if (this.requestLog.length > 200) {
      this.requestLog.shift();
    }
  }

  /**
   * Get statistics about API usage
   */
  getStats() {
    const total = this.requestLog.length;
    const successful = this.requestLog.filter(r => r.success).length;
    const failed = total - successful;
    const successRate = total > 0 ? ((successful / total) * 100).toFixed(1) : 0;

    // Group by source
    const bySource = {};
    this.requestLog.forEach(req => {
      if (!bySource[req.source]) {
        bySource[req.source] = { success: 0, failed: 0 };
      }
      if (req.success) {
        bySource[req.source].success++;
      } else {
        bySource[req.source].failed++;
      }
    });

    return {
      total,
      successful,
      failed,
      successRate: `${successRate}%`,
      cacheSize: this.cache.size,
      sourceStats: bySource,
      recentRequests: this.requestLog.slice(-20),
      availableSources: this.sources.length
    };
  }

  /**
   * List all available sources
   */
  listSources() {
    return this.sources.map(s => ({
      id: s.id,
      name: s.name,
      priority: s.priority,
      maxLimit: s.maxLimit,
      needsAuth: s.needsAuth || false,
      needsProxy: s.needsProxy || false
    }));
  }

  /**
   * Test all sources for a symbol
   * @param {string} symbol - Symbol to test
   * @param {string} timeframe - Timeframe
   * @param {number} limit - Candle limit
   */
  async testAllSources(symbol, timeframe = '1d', limit = 10) {
    console.log(`🧪 Testing all ${this.sources.length} sources for ${symbol} ${timeframe}...`);
    console.log('─'.repeat(60));
    
    const results = [];
    
    for (const source of this.sources) {
      try {
        const startTime = Date.now();
        const data = await this.getFromSource(source.id, symbol, timeframe, limit);
        const duration = Date.now() - startTime;
        
        results.push({
          source: source.name,
          status: 'SUCCESS',
          candles: data.length,
          duration: `${duration}ms`,
          priority: source.priority
        });
        
        console.log(`✅ [${source.priority}] ${source.name}: ${data.length} candles (${duration}ms)`);
        
      } catch (error) {
        results.push({
          source: source.name,
          status: 'FAILED',
          error: error.message,
          priority: source.priority
        });
        
        console.log(`❌ [${source.priority}] ${source.name}: ${error.message}`);
      }
      
      // Small delay to avoid rate limits
      await new Promise(r => setTimeout(r, 200));
    }
    
    console.log('─'.repeat(60));
    const successCount = results.filter(r => r.status === 'SUCCESS').length;
    console.log(`📊 Results: ${successCount}/${results.length} sources working`);
    
    return results;
  }

  // Helper methods
  getIntervalMs(timeframe) {
    return getIntervalMs(timeframe);
  }

  getIntervalSeconds(timeframe) {
    return getIntervalSeconds(timeframe);
  }
}

// ═══════════════════════════════════════════════════════════════
// EXPORT
// ═══════════════════════════════════════════════════════════════
export const ohlcvClient = new OHLCVClient();
export default ohlcvClient;

// Make available globally for console debugging
if (typeof window !== 'undefined') {
  window.ohlcvClient = ohlcvClient;
}

