/**
 * Free Resources - Comprehensive Collection of Crypto Data Sources
 * Based on NewResourceApi documentation and additional verified sources
 * 
 * این فایل شامل تمام منابع رایگان داده کریپتو است
 */

// ============ Types & Enums ============

export enum ResourceType {
  MARKET_DATA = "market_data",
  NEWS = "news",
  SENTIMENT = "sentiment",
  BLOCKCHAIN = "blockchain",
  ONCHAIN = "onchain",
  DEFI = "defi",
  WHALE_TRACKING = "whale_tracking",
  TECHNICAL = "technical",
  AI_MODEL = "ai_model",
  SOCIAL = "social",
  HISTORICAL = "historical"
}

export enum TimeFrame {
  REALTIME = "realtime",
  MINUTE_1 = "1m",
  MINUTE_5 = "5m",
  MINUTE_15 = "15m",
  MINUTE_30 = "30m",
  HOUR_1 = "1h",
  HOUR_4 = "4h",
  DAY_1 = "1d",
  WEEK_1 = "1w",
  MONTH_1 = "1M"
}

export interface APIEndpoint {
  name: string;
  path: string;
  method?: "GET" | "POST" | "PUT" | "DELETE";
  params?: Record<string, string>;
}

export interface APIResource {
  id: string;
  name: string;
  resourceType: ResourceType;
  baseUrl: string;
  apiKeyEnv?: string;
  apiKey?: string;
  rateLimit: string;
  isFree: boolean;
  requiresAuth: boolean;
  isActive: boolean;
  priority: number;
  description: string;
  endpoints: Record<string, string>;
  supportedTimeframes: string[];
  features: string[];
  headers?: Record<string, string>;
  documentationUrl?: string;
}

// ============ API Keys Configuration ============

export const API_KEYS = {
  // Block Explorers
  etherscan: {
    key: "",
    backupKey: ""
  },
  bscscan: {
    key: ""
  },
  tronscan: {
    key: ""
  },
  
  // Market Data
  coinmarketcap: {
    keys: [
      "",
      ""
    ]
  },
  
  // News
  newsapi: {
    key: ""
  },
  
  // Sentiment
  sentimentApi: {
    key: ""
  },
  
  // AI Models
  huggingface: {
    key: ""
  },
  
  // Notifications
  telegram: {
    enabled: false,
    botToken: "",
    chatId: ""
  }
};

// ============ Block Explorers ============

export const BLOCK_EXPLORERS: Record<string, APIResource> = {
  etherscan: {
    id: "etherscan",
    name: "Etherscan",
    resourceType: ResourceType.BLOCKCHAIN,
    baseUrl: "https://api.etherscan.io/api",
    apiKeyEnv: "ETHERSCAN_KEY",
    apiKey: API_KEYS.etherscan.key,
    rateLimit: "5 req/sec",
    isFree: true,
    requiresAuth: true,
    isActive: true,
    priority: 1,
    description: "Ethereum blockchain explorer API",
    endpoints: {
      account_balance: "?module=account&action=balance",
      account_txlist: "?module=account&action=txlist",
      token_balance: "?module=account&action=tokenbalance",
      gas_price: "?module=gastracker&action=gasoracle",
      eth_price: "?module=stats&action=ethprice",
      block_by_time: "?module=block&action=getblocknobytime",
      contract_abi: "?module=contract&action=getabi",
      token_transfers: "?module=account&action=tokentx"
    },
    supportedTimeframes: [],
    features: ["transactions", "tokens", "gas", "prices", "contracts"],
    documentationUrl: "https://docs.etherscan.io/"
  },
  
  bscscan: {
    id: "bscscan",
    name: "BscScan",
    resourceType: ResourceType.BLOCKCHAIN,
    baseUrl: "https://api.bscscan.com/api",
    apiKeyEnv: "BSCSCAN_KEY",
    apiKey: API_KEYS.bscscan.key,
    rateLimit: "5 req/sec",
    isFree: true,
    requiresAuth: true,
    isActive: true,
    priority: 1,
    description: "BSC blockchain explorer API",
    endpoints: {
      account_balance: "?module=account&action=balance",
      account_txlist: "?module=account&action=txlist",
      token_balance: "?module=account&action=tokenbalance",
      gas_price: "?module=gastracker&action=gasoracle",
      bnb_price: "?module=stats&action=bnbprice",
      token_transfers: "?module=account&action=tokentx"
    },
    supportedTimeframes: [],
    features: ["transactions", "tokens", "gas", "prices", "contracts"],
    documentationUrl: "https://docs.bscscan.com/"
  },
  
  tronscan: {
    id: "tronscan",
    name: "TronScan",
    resourceType: ResourceType.BLOCKCHAIN,
    baseUrl: "https://apilist.tronscanapi.com/api",
    apiKeyEnv: "TRONSCAN_KEY",
    apiKey: API_KEYS.tronscan.key,
    rateLimit: "varies",
    isFree: true,
    requiresAuth: true,
    isActive: true,
    priority: 1,
    description: "Tron blockchain explorer API",
    endpoints: {
      account: "/account",
      account_list: "/accountv2",
      transaction: "/transaction",
      transaction_info: "/transaction-info",
      token: "/token",
      token_trc10: "/token_trc10",
      token_trc20: "/token_trc20",
      contract: "/contract",
      node: "/node"
    },
    supportedTimeframes: [],
    features: ["transactions", "tokens", "contracts", "trc10", "trc20"],
    headers: { "TRON-PRO-API-KEY": API_KEYS.tronscan.key },
    documentationUrl: "https://tronscan.org/#/doc"
  },
  
  polygonscan: {
    id: "polygonscan",
    name: "Polygonscan",
    resourceType: ResourceType.BLOCKCHAIN,
    baseUrl: "https://api.polygonscan.com/api",
    apiKeyEnv: "POLYGONSCAN_KEY",
    rateLimit: "5 req/sec",
    isFree: true,
    requiresAuth: true,
    isActive: true,
    priority: 2,
    description: "Polygon blockchain explorer API",
    endpoints: {
      account_balance: "?module=account&action=balance",
      account_txlist: "?module=account&action=txlist",
      token_balance: "?module=account&action=tokenbalance",
      gas_price: "?module=gastracker&action=gasoracle",
      matic_price: "?module=stats&action=maticprice"
    },
    supportedTimeframes: [],
    features: ["transactions", "tokens", "gas", "prices"],
    documentationUrl: "https://docs.polygonscan.com/"
  },
  
  blockchair: {
    id: "blockchair",
    name: "Blockchair",
    resourceType: ResourceType.BLOCKCHAIN,
    baseUrl: "https://api.blockchair.com",
    rateLimit: "30 req/min free",
    isFree: true,
    requiresAuth: false,
    isActive: true,
    priority: 2,
    description: "Multi-chain blockchain explorer API",
    endpoints: {
      bitcoin_stats: "/bitcoin/stats",
      ethereum_stats: "/ethereum/stats",
      bitcoin_blocks: "/bitcoin/blocks",
      ethereum_blocks: "/ethereum/blocks",
      bitcoin_transactions: "/bitcoin/transactions",
      ethereum_transactions: "/ethereum/transactions"
    },
    supportedTimeframes: [],
    features: ["multi-chain", "transactions", "blocks", "stats"],
    documentationUrl: "https://blockchair.com/api/docs"
  }
};

// ============ Market Data Sources ============

export const MARKET_DATA_SOURCES: Record<string, APIResource> = {
  coinmarketcap: {
    id: "coinmarketcap",
    name: "CoinMarketCap",
    resourceType: ResourceType.MARKET_DATA,
    baseUrl: "https://pro-api.coinmarketcap.com/v1",
    apiKeyEnv: "COINMARKETCAP_KEY",
    apiKey: API_KEYS.coinmarketcap.keys[0],
    rateLimit: "333 req/day free",
    isFree: true,
    requiresAuth: true,
    isActive: true,
    priority: 1,
    description: "Leading cryptocurrency market data API",
    endpoints: {
      listings_latest: "/cryptocurrency/listings/latest",
      quotes_latest: "/cryptocurrency/quotes/latest",
      info: "/cryptocurrency/info",
      map: "/cryptocurrency/map",
      categories: "/cryptocurrency/categories",
      global_metrics: "/global-metrics/quotes/latest",
      exchange_listings: "/exchange/listings/latest"
    },
    supportedTimeframes: ["1h", "24h", "7d", "30d", "60d", "90d"],
    features: ["prices", "market_cap", "volume", "rankings", "historical"],
    headers: { "X-CMC_PRO_API_KEY": API_KEYS.coinmarketcap.keys[0] },
    documentationUrl: "https://coinmarketcap.com/api/documentation/v1/"
  },
  
  coingecko: {
    id: "coingecko",
    name: "CoinGecko",
    resourceType: ResourceType.MARKET_DATA,
    baseUrl: "https://api.coingecko.com/api/v3",
    rateLimit: "10-50 req/min free",
    isFree: true,
    requiresAuth: false,
    isActive: true,
    priority: 1,
    description: "Comprehensive cryptocurrency data API",
    endpoints: {
      ping: "/ping",
      simple_price: "/simple/price",
      coins_list: "/coins/list",
      coins_markets: "/coins/markets",
      coin_detail: "/coins/{id}",
      coin_history: "/coins/{id}/history",
      coin_market_chart: "/coins/{id}/market_chart",
      coin_ohlc: "/coins/{id}/ohlc",
      trending: "/search/trending",
      global: "/global",
      exchanges: "/exchanges"
    },
    supportedTimeframes: ["1d", "7d", "14d", "30d", "90d", "180d", "365d", "max"],
    features: ["prices", "market_cap", "volume", "historical", "trending", "defi"],
    documentationUrl: "https://www.coingecko.com/en/api/documentation"
  },
  
  coincap: {
    id: "coincap",
    name: "CoinCap",
    resourceType: ResourceType.MARKET_DATA,
    baseUrl: "https://api.coincap.io/v2",
    rateLimit: "200 req/min free",
    isFree: true,
    requiresAuth: false,
    isActive: true,
    priority: 1,
    description: "Real-time cryptocurrency market data",
    endpoints: {
      assets: "/assets",
      asset_detail: "/assets/{id}",
      asset_history: "/assets/{id}/history",
      markets: "/assets/{id}/markets",
      rates: "/rates",
      exchanges: "/exchanges",
      candles: "/candles"
    },
    supportedTimeframes: ["m1", "m5", "m15", "m30", "h1", "h2", "h6", "h12", "d1"],
    features: ["real-time", "prices", "volume", "market_cap", "historical"],
    documentationUrl: "https://docs.coincap.io/"
  },
  
  binance: {
    id: "binance",
    name: "Binance",
    resourceType: ResourceType.MARKET_DATA,
    baseUrl: "https://api.binance.com/api/v3",
    rateLimit: "1200 req/min",
    isFree: true,
    requiresAuth: false,
    isActive: true,
    priority: 1,
    description: "Binance exchange public API",
    endpoints: {
      ping: "/ping",
      time: "/time",
      ticker_price: "/ticker/price",
      ticker_24hr: "/ticker/24hr",
      klines: "/klines",
      depth: "/depth",
      trades: "/trades",
      avg_price: "/avgPrice",
      exchange_info: "/exchangeInfo"
    },
    supportedTimeframes: ["1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d", "3d", "1w", "1M"],
    features: ["real-time", "prices", "ohlcv", "order_book", "trades"],
    documentationUrl: "https://binance-docs.github.io/apidocs/spot/en/"
  },
  
  kucoin: {
    id: "kucoin",
    name: "KuCoin",
    resourceType: ResourceType.MARKET_DATA,
    baseUrl: "https://api.kucoin.com/api/v1",
    rateLimit: "varies",
    isFree: true,
    requiresAuth: false,
    isActive: true,
    priority: 2,
    description: "KuCoin exchange public API",
    endpoints: {
      market_list: "/market/allTickers",
      ticker: "/market/orderbook/level1",
      market_stats: "/market/stats",
      currencies: "/currencies",
      symbols: "/symbols",
      klines: "/market/candles"
    },
    supportedTimeframes: ["1min", "3min", "5min", "15min", "30min", "1hour", "2hour", "4hour", "6hour", "8hour", "12hour", "1day", "1week"],
    features: ["prices", "ohlcv", "order_book", "trades"],
    documentationUrl: "https://docs.kucoin.com/"
  },
  
  kraken: {
    id: "kraken",
    name: "Kraken",
    resourceType: ResourceType.MARKET_DATA,
    baseUrl: "https://api.kraken.com/0/public",
    rateLimit: "1 req/sec",
    isFree: true,
    requiresAuth: false,
    isActive: true,
    priority: 2,
    description: "Kraken exchange public API",
    endpoints: {
      time: "/Time",
      assets: "/Assets",
      asset_pairs: "/AssetPairs",
      ticker: "/Ticker",
      ohlc: "/OHLC",
      depth: "/Depth",
      trades: "/Trades",
      spread: "/Spread"
    },
    supportedTimeframes: ["1", "5", "15", "30", "60", "240", "1440", "10080", "21600"],
    features: ["prices", "ohlcv", "order_book", "trades"],
    documentationUrl: "https://docs.kraken.com/rest/"
  }
};

// ============ News Sources ============

export const NEWS_SOURCES: Record<string, APIResource> = {
  newsapi: {
    id: "newsapi",
    name: "NewsAPI",
    resourceType: ResourceType.NEWS,
    baseUrl: "https://newsapi.org/v2",
    apiKeyEnv: "NEWSAPI_KEY",
    apiKey: API_KEYS.newsapi.key,
    rateLimit: "100 req/day free",
    isFree: true,
    requiresAuth: true,
    isActive: true,
    priority: 1,
    description: "News articles from thousands of sources",
    endpoints: {
      everything: "/everything",
      top_headlines: "/top-headlines",
      sources: "/sources"
    },
    supportedTimeframes: [],
    features: ["articles", "headlines", "sources", "search"],
    documentationUrl: "https://newsapi.org/docs"
  },
  
  cryptopanic: {
    id: "cryptopanic",
    name: "CryptoPanic",
    resourceType: ResourceType.NEWS,
    baseUrl: "https://cryptopanic.com/api/v1",
    apiKeyEnv: "CRYPTOPANIC_KEY",
    rateLimit: "5 req/sec",
    isFree: true,
    requiresAuth: true,
    isActive: true,
    priority: 1,
    description: "Cryptocurrency news aggregator",
    endpoints: {
      posts: "/posts/",
      currencies: "/currencies/"
    },
    supportedTimeframes: [],
    features: ["news", "sentiment", "trending"],
    documentationUrl: "https://cryptopanic.com/developers/api/"
  },
  
  coindesk_rss: {
    id: "coindesk_rss",
    name: "CoinDesk RSS",
    resourceType: ResourceType.NEWS,
    baseUrl: "https://www.coindesk.com",
    rateLimit: "unlimited",
    isFree: true,
    requiresAuth: false,
    isActive: true,
    priority: 2,
    description: "CoinDesk crypto news RSS feed",
    endpoints: {
      rss: "/arc/outboundfeeds/rss/"
    },
    supportedTimeframes: [],
    features: ["news", "rss"],
    documentationUrl: "https://www.coindesk.com/arc/outboundfeeds/rss/"
  },
  
  cointelegraph_rss: {
    id: "cointelegraph_rss",
    name: "Cointelegraph RSS",
    resourceType: ResourceType.NEWS,
    baseUrl: "https://cointelegraph.com",
    rateLimit: "unlimited",
    isFree: true,
    requiresAuth: false,
    isActive: true,
    priority: 2,
    description: "Cointelegraph crypto news RSS feed",
    endpoints: {
      rss: "/rss"
    },
    supportedTimeframes: [],
    features: ["news", "rss"],
    documentationUrl: "https://cointelegraph.com/rss"
  },
  
  cryptocompare_news: {
    id: "cryptocompare_news",
    name: "CryptoCompare News",
    resourceType: ResourceType.NEWS,
    baseUrl: "https://min-api.cryptocompare.com/data",
    rateLimit: "100,000 req/month free",
    isFree: true,
    requiresAuth: false,
    isActive: true,
    priority: 2,
    description: "CryptoCompare news API",
    endpoints: {
      news_latest: "/v2/news/?lang=EN",
      news_feeds: "/news/feeds",
      news_categories: "/news/categories"
    },
    supportedTimeframes: [],
    features: ["news", "categories", "feeds"],
    documentationUrl: "https://min-api.cryptocompare.com/documentation"
  }
};

// ============ Sentiment Sources ============

export const SENTIMENT_SOURCES: Record<string, APIResource> = {
  fear_greed_index: {
    id: "fear_greed_index",
    name: "Fear & Greed Index",
    resourceType: ResourceType.SENTIMENT,
    baseUrl: "https://api.alternative.me",
    rateLimit: "unlimited",
    isFree: true,
    requiresAuth: false,
    isActive: true,
    priority: 1,
    description: "Crypto Fear & Greed Index",
    endpoints: {
      fng: "/fng/",
      fng_history: "/fng/?limit=30"
    },
    supportedTimeframes: ["daily"],
    features: ["sentiment", "fear_greed", "historical"],
    documentationUrl: "https://alternative.me/crypto/fear-and-greed-index/"
  },
  
  custom_sentiment: {
    id: "custom_sentiment",
    name: "Custom Sentiment API",
    resourceType: ResourceType.SENTIMENT,
    baseUrl: "https://sentiment-api.example.com",
    apiKeyEnv: "SENTIMENT_API_KEY",
    apiKey: API_KEYS.sentimentApi.key,
    rateLimit: "varies",
    isFree: true,
    requiresAuth: true,
    isActive: true,
    priority: 2,
    description: "Custom sentiment analysis API",
    endpoints: {
      analyze: "/analyze",
      market_sentiment: "/market-sentiment",
      social_sentiment: "/social-sentiment"
    },
    supportedTimeframes: [],
    features: ["sentiment", "social", "market"]
  },
  
  lunarcrush: {
    id: "lunarcrush",
    name: "LunarCrush",
    resourceType: ResourceType.SENTIMENT,
    baseUrl: "https://lunarcrush.com/api/v2",
    apiKeyEnv: "LUNARCRUSH_KEY",
    rateLimit: "varies",
    isFree: true,
    requiresAuth: true,
    isActive: true,
    priority: 2,
    description: "Social sentiment analytics",
    endpoints: {
      assets: "/assets",
      market: "/market",
      global: "/global",
      influencers: "/influencers"
    },
    supportedTimeframes: [],
    features: ["social_sentiment", "influencers", "trending"],
    documentationUrl: "https://lunarcrush.com/developers"
  }
};

// ============ On-Chain Analytics ============

export const ONCHAIN_SOURCES: Record<string, APIResource> = {
  blockchain_com: {
    id: "blockchain_com",
    name: "Blockchain.com",
    resourceType: ResourceType.ONCHAIN,
    baseUrl: "https://api.blockchain.info",
    rateLimit: "varies",
    isFree: true,
    requiresAuth: false,
    isActive: true,
    priority: 1,
    description: "Bitcoin blockchain data",
    endpoints: {
      stats: "/stats",
      ticker: "/ticker",
      rawblock: "/rawblock/{hash}",
      rawtx: "/rawtx/{hash}",
      balance: "/balance"
    },
    supportedTimeframes: [],
    features: ["bitcoin", "transactions", "blocks", "addresses"],
    documentationUrl: "https://www.blockchain.com/api"
  },
  
  mempool_space: {
    id: "mempool_space",
    name: "Mempool.space",
    resourceType: ResourceType.ONCHAIN,
    baseUrl: "https://mempool.space/api",
    rateLimit: "varies",
    isFree: true,
    requiresAuth: false,
    isActive: true,
    priority: 1,
    description: "Bitcoin mempool and blockchain explorer",
    endpoints: {
      mempool: "/mempool",
      fees_recommended: "/v1/fees/recommended",
      blocks: "/blocks",
      block_height: "/block-height/{height}",
      tx: "/tx/{txid}"
    },
    supportedTimeframes: [],
    features: ["mempool", "fees", "blocks", "transactions"],
    documentationUrl: "https://mempool.space/docs/api"
  }
};

// ============ DeFi Sources ============

export const DEFI_SOURCES: Record<string, APIResource> = {
  defillama: {
    id: "defillama",
    name: "DefiLlama",
    resourceType: ResourceType.DEFI,
    baseUrl: "https://api.llama.fi",
    rateLimit: "unlimited",
    isFree: true,
    requiresAuth: false,
    isActive: true,
    priority: 1,
    description: "DeFi TVL and protocol analytics",
    endpoints: {
      protocols: "/protocols",
      protocol_detail: "/protocol/{protocol}",
      tvl_all: "/tvl",
      chains: "/chains",
      stablecoins: "/stablecoins",
      yields: "/yields/pools",
      dexs: "/overview/dexs"
    },
    supportedTimeframes: [],
    features: ["tvl", "protocols", "chains", "yields", "dexs"],
    documentationUrl: "https://defillama.com/docs/api"
  },
  
  inch_1: {
    id: "1inch",
    name: "1inch",
    resourceType: ResourceType.DEFI,
    baseUrl: "https://api.1inch.io/v5.0/1",
    rateLimit: "varies",
    isFree: true,
    requiresAuth: false,
    isActive: true,
    priority: 2,
    description: "DEX aggregator API",
    endpoints: {
      tokens: "/tokens",
      quote: "/quote",
      swap: "/swap",
      liquidity_sources: "/liquidity-sources"
    },
    supportedTimeframes: [],
    features: ["dex", "swap", "quotes", "aggregator"],
    documentationUrl: "https://docs.1inch.io/"
  }
};

// ============ Whale Tracking ============

export const WHALE_SOURCES: Record<string, APIResource> = {
  whale_alert: {
    id: "whale_alert",
    name: "Whale Alert",
    resourceType: ResourceType.WHALE_TRACKING,
    baseUrl: "https://api.whale-alert.io/v1",
    apiKeyEnv: "WHALE_ALERT_KEY",
    rateLimit: "10 req/min free",
    isFree: true,
    requiresAuth: true,
    isActive: true,
    priority: 1,
    description: "Large crypto transaction tracking",
    endpoints: {
      status: "/status",
      transactions: "/transactions"
    },
    supportedTimeframes: [],
    features: ["whale_alerts", "large_transactions", "multi-chain"],
    documentationUrl: "https://docs.whale-alert.io/"
  }
};

// ============ Technical Analysis ============

export const TECHNICAL_SOURCES: Record<string, APIResource> = {
  taapi: {
    id: "taapi",
    name: "TAAPI.IO",
    resourceType: ResourceType.TECHNICAL,
    baseUrl: "https://api.taapi.io",
    apiKeyEnv: "TAAPI_KEY",
    rateLimit: "varies",
    isFree: true,
    requiresAuth: true,
    isActive: true,
    priority: 1,
    description: "Technical analysis indicators API",
    endpoints: {
      rsi: "/rsi",
      macd: "/macd",
      ema: "/ema",
      sma: "/sma",
      bbands: "/bbands",
      stoch: "/stoch",
      atr: "/atr",
      adx: "/adx",
      dmi: "/dmi",
      sar: "/sar",
      ichimoku: "/ichimoku"
    },
    supportedTimeframes: [],
    features: ["indicators", "rsi", "macd", "bollinger", "ema", "sma"],
    documentationUrl: "https://taapi.io/documentation/"
  }
};

// ============ Social Sources ============

export const SOCIAL_SOURCES: Record<string, APIResource> = {
  reddit: {
    id: "reddit",
    name: "Reddit API",
    resourceType: ResourceType.SOCIAL,
    baseUrl: "https://www.reddit.com",
    rateLimit: "60 req/min",
    isFree: true,
    requiresAuth: false,
    isActive: true,
    priority: 1,
    description: "Reddit cryptocurrency communities",
    endpoints: {
      r_crypto: "/r/CryptoCurrency/hot.json",
      r_bitcoin: "/r/Bitcoin/hot.json",
      r_ethereum: "/r/ethereum/hot.json",
      r_altcoin: "/r/altcoin/hot.json",
      r_defi: "/r/defi/hot.json"
    },
    supportedTimeframes: [],
    features: ["discussions", "sentiment", "trending"],
    documentationUrl: "https://www.reddit.com/dev/api/"
  }
};

// ============ Historical Data Sources ============

export const HISTORICAL_SOURCES: Record<string, APIResource> = {
  cryptocompare_historical: {
    id: "cryptocompare_historical",
    name: "CryptoCompare Historical",
    resourceType: ResourceType.HISTORICAL,
    baseUrl: "https://min-api.cryptocompare.com/data",
    rateLimit: "100,000 req/month free",
    isFree: true,
    requiresAuth: false,
    isActive: true,
    priority: 1,
    description: "Historical crypto price data",
    endpoints: {
      histoday: "/v2/histoday",
      histohour: "/v2/histohour",
      histominute: "/histominute"
    },
    supportedTimeframes: ["1m", "1h", "1d"],
    features: ["ohlcv", "historical", "daily", "hourly", "minute"],
    documentationUrl: "https://min-api.cryptocompare.com/documentation"
  },
  
  messari: {
    id: "messari",
    name: "Messari",
    resourceType: ResourceType.HISTORICAL,
    baseUrl: "https://data.messari.io/api/v1",
    apiKeyEnv: "MESSARI_KEY",
    rateLimit: "20 req/min free",
    isFree: true,
    requiresAuth: false,
    isActive: true,
    priority: 2,
    description: "Crypto research and data",
    endpoints: {
      assets: "/assets",
      asset_detail: "/assets/{symbol}",
      asset_metrics: "/assets/{symbol}/metrics",
      asset_profile: "/assets/{symbol}/profile"
    },
    supportedTimeframes: [],
    features: ["metrics", "profiles", "research"],
    documentationUrl: "https://messari.io/api"
  }
};

// ============ ML Models Configuration ============

export interface MLModel {
  name: string;
  type: string;
  purpose: string;
  inputFeatures?: string[];
  timeframes?: string[];
  huggingfaceModel?: string;
}

export const ML_MODELS_CONFIG: Record<string, MLModel> = {
  price_prediction_lstm: {
    name: "PricePredictionLSTM",
    type: "LSTM",
    purpose: "Short-term price prediction",
    inputFeatures: ["open", "high", "low", "close", "volume"],
    timeframes: ["1m", "5m", "15m", "1h", "4h"]
  },
  sentiment_analysis_transformer: {
    name: "SentimentAnalysisTransformer",
    type: "Transformer",
    purpose: "News and social media sentiment analysis",
    huggingfaceModel: "ProsusAI/finbert"
  },
  anomaly_detection_isolation_forest: {
    name: "AnomalyDetectionIsolationForest",
    type: "Isolation Forest",
    purpose: "Detecting market anomalies"
  },
  trend_classification_random_forest: {
    name: "TrendClassificationRandomForest",
    type: "Random Forest",
    purpose: "Market trend classification"
  }
};

// ============ Analysis Endpoints Configuration ============

export const ANALYSIS_ENDPOINTS: Record<string, string> = {
  track_position: "/track_position",
  market_analysis: "/market_analysis",
  technical_analysis: "/technical_analysis",
  sentiment_analysis: "/sentiment_analysis",
  whale_activity: "/whale_activity",
  trading_strategies: "/trading_strategies",
  ai_prediction: "/ai_prediction",
  risk_management: "/risk_management",
  pdf_analysis: "/pdf_analysis",
  ai_enhanced_analysis: "/ai_enhanced_analysis",
  multi_source_data: "/multi_source_data",
  news_analysis: "/news_analysis",
  exchange_integration: "/exchange_integration",
  smart_alerts: "/smart_alerts",
  advanced_social_media_analysis: "/advanced_social_media_analysis",
  dynamic_modeling: "/dynamic_modeling",
  multi_currency_analysis: "/multi_currency_analysis",
  telegram_settings: "/telegram_settings",
  collect_data: "/collect-data",
  greed_fear_index: "/greed-fear-index",
  onchain_metrics: "/onchain-metrics",
  custom_alerts: "/custom-alerts",
  stakeholder_analysis: "/stakeholder-analysis"
};

// ============ Combined Registry ============

export const ALL_RESOURCES: Record<string, APIResource> = {
  ...BLOCK_EXPLORERS,
  ...MARKET_DATA_SOURCES,
  ...NEWS_SOURCES,
  ...SENTIMENT_SOURCES,
  ...ONCHAIN_SOURCES,
  ...DEFI_SOURCES,
  ...WHALE_SOURCES,
  ...TECHNICAL_SOURCES,
  ...SOCIAL_SOURCES,
  ...HISTORICAL_SOURCES
};

// ============ Utility Functions ============

export function getResourceById(id: string): APIResource | undefined {
  return ALL_RESOURCES[id];
}

export function getResourcesByType(type: ResourceType): APIResource[] {
  return Object.values(ALL_RESOURCES).filter(r => r.resourceType === type);
}

export function getFreeResources(): APIResource[] {
  return Object.values(ALL_RESOURCES).filter(r => r.isFree);
}

export function getActiveResources(): APIResource[] {
  return Object.values(ALL_RESOURCES).filter(r => r.isActive);
}

export function getNoAuthResources(): APIResource[] {
  return Object.values(ALL_RESOURCES).filter(r => !r.requiresAuth);
}

export function searchResources(query: string): APIResource[] {
  const q = query.toLowerCase();
  return Object.values(ALL_RESOURCES).filter(
    r => r.name.toLowerCase().includes(q) || 
         r.description.toLowerCase().includes(q) ||
         r.features.some(f => f.toLowerCase().includes(q))
  );
}

export function getStatistics(): {
  total: number;
  free: number;
  active: number;
  noAuth: number;
  byType: Record<string, number>;
} {
  const resources = Object.values(ALL_RESOURCES);
  const byType: Record<string, number> = {};
  
  for (const r of resources) {
    const type = r.resourceType;
    byType[type] = (byType[type] || 0) + 1;
  }
  
  return {
    total: resources.length,
    free: resources.filter(r => r.isFree).length,
    active: resources.filter(r => r.isActive).length,
    noAuth: resources.filter(r => !r.requiresAuth).length,
    byType
  };
}

// Export default
export default {
  API_KEYS,
  ALL_RESOURCES,
  BLOCK_EXPLORERS,
  MARKET_DATA_SOURCES,
  NEWS_SOURCES,
  SENTIMENT_SOURCES,
  ONCHAIN_SOURCES,
  DEFI_SOURCES,
  WHALE_SOURCES,
  TECHNICAL_SOURCES,
  SOCIAL_SOURCES,
  HISTORICAL_SOURCES,
  ML_MODELS_CONFIG,
  ANALYSIS_ENDPOINTS,
  getResourceById,
  getResourcesByType,
  getFreeResources,
  getActiveResources,
  getNoAuthResources,
  searchResources,
  getStatistics
};
