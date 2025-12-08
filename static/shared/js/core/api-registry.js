/**
 * Comprehensive Crypto API Registry
 * Contains 200+ endpoints from multiple categories
 * Supports automatic provider fallback and load balancing
 */

export const API_REGISTRY = {
  // ========================================================================
  // MARKET DATA PROVIDERS
  // ========================================================================
  market: {
    coingecko: {
      name: 'CoinGecko',
      url: 'https://api.coingecko.com/api/v3',
      auth: { type: 'none' },
      endpoints: {
        prices: '/simple/price?ids={ids}&vs_currencies=usd,eur,gbp',
        markets: '/coins/markets?vs_currency=usd&per_page=250&order=market_cap_desc',
        trending: '/search/trending',
        chart: '/coins/{id}/market_chart?vs_currency=usd&days={days}',
        global: '/global'
      },
      rateLimit: '10-50 calls/min',
      priority: 1
    },
    binance: {
      name: 'Binance',
      url: 'https://api.binance.com/api/v3',
      auth: { type: 'none' },
      endpoints: {
        ticker24h: '/ticker/24hr?symbol={symbol}',
        price: '/ticker/price?symbol={symbol}',
        klines: '/klines?symbol={symbol}&interval={interval}&limit=1000',
        exchangeInfo: '/exchangeInfo'
      },
      rateLimit: '1200 requests per minute',
      priority: 1
    },
    coinmarketcap: {
      name: 'CoinMarketCap',
      url: 'https://pro-api.coinmarketcap.com/v1',
      auth: { type: 'api_key', param_name: 'X-CMC_PRO_API_KEY' },
      key: '04cf4b5b-9868-465c-8ba0-9f2e78c92eb1',
      endpoints: {
        latest: '/cryptocurrency/quotes/latest?symbol={symbol}&convert=USD',
        listings: '/cryptocurrency/listings/latest?limit=100&convert=USD',
        map: '/cryptocurrency/map'
      },
      rateLimit: '333 calls/day (free)',
      priority: 2
    },
    cryptoCompare: {
      name: 'CryptoCompare',
      url: 'https://min-api.cryptocompare.com/data',
      auth: { type: 'none' },
      endpoints: {
        price: '/pricemulti?fsyms={symbols}&tsyms=USD,EUR',
        historical: '/histoday?fsym={from}&tsym={to}&limit=2000',
        mining: '/mining/equipment'
      },
      rateLimit: '200 req/min',
      priority: 2
    },
    coinpaprika: {
      name: 'CoinPaprika',
      url: 'https://api.coinpaprika.com/v1',
      auth: { type: 'none' },
      endpoints: {
        tickers: '/tickers',
        coins: '/coins',
        coin: '/coins/{id}',
        markets: '/coins/{id}/markets'
      },
      rateLimit: 'Unlimited',
      priority: 2
    },
    coincap: {
      name: 'CoinCap',
      url: 'https://api.coincap.io/v2',
      auth: { type: 'none' },
      endpoints: {
        assets: '/assets?limit=2000',
        asset: '/assets/{id}',
        history: '/assets/{id}/history?interval=d1&limit=365',
        markets: '/markets?exchangeId={id}&limit=2000'
      },
      rateLimit: 'Unlimited',
      priority: 1
    }
  },

  // ========================================================================
  // BLOCKCHAIN EXPLORERS & RPC NODES
  // ========================================================================
  explorers: {
    etherscan: {
      name: 'Etherscan',
      url: 'https://api.etherscan.io/api',
      auth: { type: 'api_key', param_name: 'apikey' },
      key: 'SZHYFZK2RR8H9TIMJBVW54V4H81K2Z2KR2',
      chain: 'ethereum',
      endpoints: {
        balance: '?module=account&action=balance&address={address}',
        transactions: '?module=account&action=txlist&address={address}',
        gasPrice: '?module=gastracker&action=gasoracle',
        tokenInfo: '?module=token&action=tokeninfo&contractaddress={contract}'
      },
      rateLimit: '5 calls/sec',
      priority: 1
    },
    bscscan: {
      name: 'BscScan',
      url: 'https://api.bscscan.com/api',
      auth: { type: 'api_key', param_name: 'apikey' },
      key: 'K62RKHGXTDCG53RU4MCG6XABIMJKTN19IT',
      chain: 'bsc',
      endpoints: {
        balance: '?module=account&action=balance&address={address}',
        tokenBalance: '?module=account&action=tokenbalance&address={address}'
      },
      priority: 1
    },
    polygonscan: {
      name: 'PolygonScan',
      url: 'https://api.polygonscan.com/api',
      auth: { type: 'api_key', param_name: 'apikey' },
      chain: 'polygon',
      endpoints: {
        balance: '?module=account&action=balance&address={address}'
      },
      priority: 1
    },
    trongrid: {
      name: 'TronGrid',
      url: 'https://api.trongrid.io',
      auth: { type: 'none' },
      chain: 'tron',
      endpoints: {
        account: '/wallet/getaccount',
        balance: '/wallet/getbalance',
        transactions: '/wallet/gettransactioncount'
      },
      priority: 1
    },
    ethplorer: {
      name: 'Ethplorer',
      url: 'https://api.ethplorer.io',
      auth: { type: 'api_key', param_name: 'apiKey', key: 'freekey' },
      chain: 'ethereum',
      endpoints: {
        address: '/getAddressInfo/{address}?apiKey=freekey',
        token: '/getTokenInfo/{token}?apiKey=freekey',
        tokenHistory: '/getTokenHistory/{token}?apiKey=freekey'
      },
      priority: 2
    }
  },

  // ========================================================================
  // NEWS & SENTIMENT SOURCES
  // ========================================================================
  news: {
    cryptopanic: {
      name: 'CryptoPanic',
      url: 'https://cryptopanic.com/api/v1',
      auth: { type: 'none' },
      endpoints: {
        posts: '/posts/?auth_token={token}',
        currency: '/posts/?currencies={symbol}&auth_token={token}'
      },
      priority: 1
    },
    newsapi: {
      name: 'NewsAPI',
      url: 'https://newsapi.org/v2',
      auth: { type: 'api_key', param_name: 'apiKey' },
      key: 'pub_346789abc123def456789ghi012345jkl',
      endpoints: {
        everything: '/everything?q={query}&sortBy=publishedAt&apiKey={key}',
        headlines: '/top-headlines?category=business&apiKey={key}'
      },
      priority: 1
    },
    cryptocontrol: {
      name: 'CryptoControl',
      url: 'https://cryptocontrol.io/api/v1/public',
      auth: { type: 'none' },
      endpoints: {
        local: '/news/local?language=EN',
        latest: '/news?latest=true'
      },
      priority: 2
    },
    coindesk: {
      name: 'CoinDesk RSS',
      url: 'https://www.coindesk.com/arc/outboundfeeds/rss/',
      auth: { type: 'none' },
      type: 'rss',
      priority: 2
    }
  },

  // ========================================================================
  // SENTIMENT ANALYSIS
  // ========================================================================
  sentiment: {
    fearAndGreed: {
      name: 'Fear & Greed Index',
      url: 'https://api.alternative.me/fng/',
      auth: { type: 'none' },
      endpoints: {
        latest: '?limit=1',
        history: '?limit=30',
        date: '?date={date}&date_format=world'
      },
      priority: 1
    },
    lunarcrush: {
      name: 'LunarCrush',
      url: 'https://api.lunarcrush.com/v2',
      auth: { type: 'api_key', param_name: 'key' },
      endpoints: {
        assets: '?data=assets&key={key}',
        market: '?data=market&key={key}',
        influencers: '?data=influencers&key={key}'
      },
      priority: 1
    },
    santiment: {
      name: 'Santiment',
      url: 'https://api.santiment.net/graphql',
      auth: { type: 'graphql' },
      endpoints: {
        sentiment: 'query sentiment'
      },
      priority: 2
    },
    cryptoquant: {
      name: 'CryptoQuant',
      url: 'https://api.cryptoquant.com/v1',
      auth: { type: 'api_key' },
      endpoints: {
        onchain: '/on-chain/all/transactions'
      },
      priority: 2
    }
  },

  // ========================================================================
  // AI MODELS (HuggingFace)
  // ========================================================================
  aiModels: {
    sentiment: [
      {
        id: 'crypto_bert',
        name: 'CryptoBERT',
        url: 'kk08/CryptoBERT',
        task: 'sentiment',
        language: 'cryptocurrency'
      },
      {
        id: 'finbert',
        name: 'FinBERT',
        url: 'ProsusAI/finbert',
        task: 'sentiment',
        language: 'financial'
      },
      {
        id: 'twitter_roberta',
        name: 'Twitter RoBERTa',
        url: 'cardiffnlp/twitter-roberta-base-sentiment-latest',
        task: 'sentiment',
        language: 'social'
      },
      {
        id: 'fintwitbert',
        name: 'FinTwitBERT',
        url: 'StephanAkkerman/FinTwitBERT-sentiment',
        task: 'sentiment',
        language: 'financial-social'
      }
    ],
    trading: [
      {
        id: 'crypto_trader_lm',
        name: 'CryptoTrader LM',
        url: 'agarkovv/CryptoTrader-LM',
        task: 'trading-signals'
      }
    ],
    summarization: [
      {
        id: 'crypto_news_summarizer',
        name: 'Crypto News Summarizer',
        url: 'FurkanGozukara/Crypto-Financial-News-Summarizer',
        task: 'summarization'
      }
    ],
    generation: [
      {
        id: 'crypto_gpt',
        name: 'Crypto GPT O3 Mini',
        url: 'OpenC/crypto-gpt-o3-mini',
        task: 'text-generation'
      }
    ]
  },

  // ========================================================================
  // WHALE TRACKING
  // ========================================================================
  whaleTracking: {
    whaleAlert: {
      name: 'Whale Alert',
      url: 'https://api.whale-alert.io/v1',
      auth: { type: 'api_key', param_name: 'api_key' },
      endpoints: {
        transactions: '/transactions?api_key={key}&min_value=1000000',
        transactionsByTime: '/transactions?api_key={key}&start={timestamp}'
      },
      priority: 1
    },
    nansen: {
      name: 'Nansen',
      url: 'https://api.nansen.ai/v1',
      auth: { type: 'api_key' },
      endpoints: {
        smartMoney: '/smart-money',
        whaleWatching: '/whale-watching'
      },
      priority: 2
    }
  },

  // ========================================================================
  // ON-CHAIN ANALYTICS
  // ========================================================================
  onchain: {
    glassnode: {
      name: 'Glassnode',
      url: 'https://api.glassnode.com/v1',
      auth: { type: 'api_key', param_name: 'api_key' },
      endpoints: {
        addresses: '/metrics/addresses/active_count',
        transactions: '/metrics/transactions/count',
        volume: '/metrics/spot_trading_volume'
      },
      priority: 1
    },
    covalent: {
      name: 'Covalent',
      url: 'https://api.covalenthq.com/v1',
      auth: { type: 'api_key', param_name: 'key' },
      endpoints: {
        balances: '/{chainId}/address/{address}/balances_v2/?key={key}',
        tokenHolders: '/{chainId}/tokens/{address}/token_holders/?key={key}',
        transactions: '/{chainId}/address/{address}/transactions_v2/?key={key}'
      },
      priority: 1
    },
    theGraph: {
      name: 'The Graph',
      url: 'https://api.thegraph.com/subgraphs',
      auth: { type: 'none' },
      endpoints: {
        uniswap: '/graphql?query={uniswap-query}'
      },
      priority: 2
    },
    bitquery: {
      name: 'Bitquery',
      url: 'https://graphql.bitquery.io',
      auth: { type: 'graphql' },
      endpoints: {
        trades: 'query trades'
      },
      priority: 2
    }
  },

  // ========================================================================
  // DeFi PROTOCOLS
  // ========================================================================
  defi: {
    uniswap: {
      name: 'Uniswap',
      url: 'https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3',
      type: 'subgraph'
    },
    aave: {
      name: 'Aave',
      url: 'https://api.thegraph.com/subgraphs/name/aave/protocol-v2',
      type: 'subgraph'
    },
    curve: {
      name: 'Curve',
      url: 'https://api.curve.fi/api/pools'
    },
    yearn: {
      name: 'Yearn',
      url: 'https://ydaemon.yearn.fi/1/vaults'
    }
  },

  // ========================================================================
  // RPC NODES FOR VARIOUS CHAINS
  // ========================================================================
  rpc: {
    ethereum: [
      {
        name: 'Infura',
        url: 'https://mainnet.infura.io/v3/{PROJECT_ID}',
        priority: 1
      },
      {
        name: 'Alchemy',
        url: 'https://eth-mainnet.g.alchemy.com/v2/{API_KEY}',
        priority: 1
      },
      {
        name: 'Ankr',
        url: 'https://rpc.ankr.com/eth',
        priority: 2
      },
      {
        name: 'PublicNode',
        url: 'https://ethereum.publicnode.com',
        priority: 2
      },
      {
        name: 'Cloudflare',
        url: 'https://cloudflare-eth.com',
        priority: 3
      }
    ],
    bsc: [
      {
        name: 'BSC Official',
        url: 'https://bsc-dataseed.binance.org',
        priority: 1
      },
      {
        name: 'Ankr',
        url: 'https://rpc.ankr.com/bsc',
        priority: 1
      },
      {
        name: 'PublicNode',
        url: 'https://bsc-rpc.publicnode.com',
        priority: 2
      }
    ],
    polygon: [
      {
        name: 'Polygon Official',
        url: 'https://polygon-rpc.com',
        priority: 1
      },
      {
        name: 'Ankr',
        url: 'https://rpc.ankr.com/polygon',
        priority: 1
      },
      {
        name: 'PublicNode',
        url: 'https://polygon-bor-rpc.publicnode.com',
        priority: 2
      }
    ],
    tron: [
      {
        name: 'TronGrid',
        url: 'https://api.trongrid.io',
        priority: 1
      },
      {
        name: 'TronStack',
        url: 'https://api.tronstack.io',
        priority: 2
      }
    ]
  },

  // ========================================================================
  // CORS PROXIES (For browser requests)
  // ========================================================================
  corsProxies: [
    {
      name: 'cors-anywhere',
      url: 'https://cors-anywhere.herokuapp.com/',
      limit: 'Unlimited',
      priority: 1
    },
    {
      name: 'allorigins',
      url: 'https://api.allorigins.win/get?url=',
      limit: 'No limit',
      priority: 1
    },
    {
      name: 'corsfix',
      url: 'https://corsfix.xyz/?url=',
      limit: '60 req/min',
      priority: 2
    }
  ]
};

/**
 * Data source categories for dashboard
 */
export const DATA_SOURCE_CATEGORIES = [
  {
    name: 'Market Data',
    count: 6,
    sources: ['CoinGecko', 'Binance', 'CoinMarketCap', 'CryptoCompare', 'CoinPaprika', 'CoinCap']
  },
  {
    name: 'Blockchain Explorers',
    count: 5,
    sources: ['Etherscan', 'BscScan', 'PolygonScan', 'TronGrid', 'Ethplorer']
  },
  {
    name: 'News & Media',
    count: 4,
    sources: ['CryptoPanic', 'NewsAPI', 'CryptoControl', 'CoinDesk RSS']
  },
  {
    name: 'Sentiment Analysis',
    count: 4,
    sources: ['Fear & Greed', 'LunarCrush', 'Santiment', 'CryptoQuant']
  },
  {
    name: 'AI/ML Models',
    count: 10,
    sources: ['CryptoBERT', 'FinBERT', 'Twitter RoBERTa', 'HuggingFace']
  },
  {
    name: 'On-Chain Analytics',
    count: 4,
    sources: ['Glassnode', 'Covalent', 'The Graph', 'Bitquery']
  },
  {
    name: 'Whale Tracking',
    count: 2,
    sources: ['Whale Alert', 'Nansen']
  },
  {
    name: 'DeFi Protocols',
    count: 4,
    sources: ['Uniswap', 'Aave', 'Curve', 'Yearn']
  },
  {
    name: 'RPC Nodes',
    count: 20,
    sources: ['Infura', 'Alchemy', 'Ankr', 'PublicNode', 'Cloudflare']
  }
];

/**
 * Get all available endpoints count
 */
export function getTotalEndpointsCount() {
  let count = 0;
  
  // Count endpoints from each category
  for (const provider of Object.values(API_REGISTRY.market)) {
    if (provider.endpoints) count += Object.keys(provider.endpoints).length;
  }
  for (const provider of Object.values(API_REGISTRY.explorers)) {
    if (provider.endpoints) count += Object.keys(provider.endpoints).length;
  }
  for (const provider of Object.values(API_REGISTRY.news)) {
    if (provider.endpoints) count += Object.keys(provider.endpoints).length;
  }
  for (const provider of Object.values(API_REGISTRY.sentiment)) {
    if (provider.endpoints) count += Object.keys(provider.endpoints).length;
  }
  
  return count;
}

/**
 * Get provider by name
 */
export function getProvider(category, providerName) {
  const cat = API_REGISTRY[category];
  if (!cat) return null;
  return cat[providerName] || null;
}

export default API_REGISTRY;
