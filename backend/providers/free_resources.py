"""
Free Resources Provider - Comprehensive Collection of Crypto Data Sources
Based on NewResourceApi documentation and additional verified sources
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from enum import Enum
import os


class ResourceType(Enum):
    MARKET_DATA = "market_data"
    NEWS = "news"
    SENTIMENT = "sentiment"
    BLOCKCHAIN = "blockchain"
    ONCHAIN = "onchain"
    DEFI = "defi"
    WHALE_TRACKING = "whale_tracking"
    TECHNICAL = "technical"
    AI_MODEL = "ai_model"
    SOCIAL = "social"
    HISTORICAL = "historical"


class TimeFrame(Enum):
    REALTIME = "realtime"
    MINUTE_1 = "1m"
    MINUTE_5 = "5m"
    MINUTE_15 = "15m"
    MINUTE_30 = "30m"
    HOUR_1 = "1h"
    HOUR_4 = "4h"
    DAY_1 = "1d"
    WEEK_1 = "1w"
    MONTH_1 = "1M"


@dataclass
class APIResource:
    """Data class for API Resource configuration"""
    id: str
    name: str
    resource_type: ResourceType
    base_url: str
    api_key_env: str = ""
    api_key: str = ""
    rate_limit: str = "unlimited"
    is_free: bool = True
    requires_auth: bool = False
    is_active: bool = True
    priority: int = 1
    description: str = ""
    endpoints: Dict[str, str] = field(default_factory=dict)
    supported_timeframes: List[str] = field(default_factory=list)
    features: List[str] = field(default_factory=list)
    headers: Dict[str, str] = field(default_factory=dict)
    documentation_url: str = ""


class FreeResourcesRegistry:
    """Registry of all available free and configured API resources"""
    
    def __init__(self):
        self.resources: Dict[str, APIResource] = {}
        self._load_all_resources()
    
    def _load_all_resources(self):
        """Load all available resources"""
        self._load_block_explorers()
        self._load_market_data_sources()
        self._load_news_sources()
        self._load_sentiment_sources()
        self._load_onchain_analytics()
        self._load_defi_sources()
        self._load_whale_tracking()
        self._load_technical_analysis()
        self._load_social_sources()
        self._load_historical_sources()
    
    def _load_block_explorers(self):
        """Block explorer APIs - Etherscan, BscScan, TronScan, etc."""
        
        # Etherscan - Ethereum
        self.resources["etherscan"] = APIResource(
            id="etherscan",
            name="Etherscan",
            resource_type=ResourceType.BLOCKCHAIN,
            base_url="https://api.etherscan.io/api",
            api_key_env="ETHERSCAN_KEY",
            api_key=os.getenv("ETHERSCAN_KEY", "SZHYFZK2RR8H9TIMJBVW54V4H81K2Z2KR2"),
            rate_limit="5 req/sec",
            is_free=True,
            requires_auth=True,
            description="Ethereum blockchain explorer API",
            endpoints={
                "account_balance": "?module=account&action=balance",
                "account_txlist": "?module=account&action=txlist",
                "token_balance": "?module=account&action=tokenbalance",
                "gas_price": "?module=gastracker&action=gasoracle",
                "eth_price": "?module=stats&action=ethprice",
                "block_by_time": "?module=block&action=getblocknobytime",
                "contract_abi": "?module=contract&action=getabi",
                "token_transfers": "?module=account&action=tokentx"
            },
            features=["transactions", "tokens", "gas", "prices", "contracts"],
            documentation_url="https://docs.etherscan.io/"
        )
        
        # BscScan - Binance Smart Chain
        self.resources["bscscan"] = APIResource(
            id="bscscan",
            name="BscScan",
            resource_type=ResourceType.BLOCKCHAIN,
            base_url="https://api.bscscan.com/api",
            api_key_env="BSCSCAN_KEY",
            api_key=os.getenv("BSCSCAN_KEY", "K62RKHGXTDCG53RU4MCG6XABIMJKTN19IT"),
            rate_limit="5 req/sec",
            is_free=True,
            requires_auth=True,
            description="BSC blockchain explorer API",
            endpoints={
                "account_balance": "?module=account&action=balance",
                "account_txlist": "?module=account&action=txlist",
                "token_balance": "?module=account&action=tokenbalance",
                "gas_price": "?module=gastracker&action=gasoracle",
                "bnb_price": "?module=stats&action=bnbprice",
                "token_transfers": "?module=account&action=tokentx"
            },
            features=["transactions", "tokens", "gas", "prices", "contracts"],
            documentation_url="https://docs.bscscan.com/"
        )
        
        # TronScan - Tron Network
        self.resources["tronscan"] = APIResource(
            id="tronscan",
            name="TronScan",
            resource_type=ResourceType.BLOCKCHAIN,
            base_url="https://apilist.tronscanapi.com/api",
            api_key_env="TRONSCAN_KEY",
            api_key=os.getenv("TRONSCAN_KEY", "7ae72726-bffe-4e74-9c33-97b761eeea21"),
            rate_limit="varies",
            is_free=True,
            requires_auth=True,
            description="Tron blockchain explorer API",
            endpoints={
                "account": "/account",
                "account_list": "/accountv2",
                "transaction": "/transaction",
                "transaction_info": "/transaction-info",
                "token": "/token",
                "token_trc10": "/token_trc10",
                "token_trc20": "/token_trc20",
                "contract": "/contract",
                "node": "/node"
            },
            headers={"TRON-PRO-API-KEY": os.getenv("TRONSCAN_KEY", "7ae72726-bffe-4e74-9c33-97b761eeea21")},
            features=["transactions", "tokens", "contracts", "trc10", "trc20"],
            documentation_url="https://tronscan.org/#/doc"
        )
        
        # Polygonscan - Polygon Network
        self.resources["polygonscan"] = APIResource(
            id="polygonscan",
            name="Polygonscan",
            resource_type=ResourceType.BLOCKCHAIN,
            base_url="https://api.polygonscan.com/api",
            api_key_env="POLYGONSCAN_KEY",
            rate_limit="5 req/sec",
            is_free=True,
            requires_auth=True,
            description="Polygon blockchain explorer API",
            endpoints={
                "account_balance": "?module=account&action=balance",
                "account_txlist": "?module=account&action=txlist",
                "token_balance": "?module=account&action=tokenbalance",
                "gas_price": "?module=gastracker&action=gasoracle",
                "matic_price": "?module=stats&action=maticprice"
            },
            features=["transactions", "tokens", "gas", "prices"],
            documentation_url="https://docs.polygonscan.com/"
        )
        
        # Blockchair - Multi-chain
        self.resources["blockchair"] = APIResource(
            id="blockchair",
            name="Blockchair",
            resource_type=ResourceType.BLOCKCHAIN,
            base_url="https://api.blockchair.com",
            rate_limit="30 req/min free",
            is_free=True,
            requires_auth=False,
            description="Multi-chain blockchain explorer API",
            endpoints={
                "bitcoin_stats": "/bitcoin/stats",
                "ethereum_stats": "/ethereum/stats",
                "bitcoin_blocks": "/bitcoin/blocks",
                "ethereum_blocks": "/ethereum/blocks",
                "bitcoin_transactions": "/bitcoin/transactions",
                "ethereum_transactions": "/ethereum/transactions"
            },
            features=["multi-chain", "transactions", "blocks", "stats"],
            documentation_url="https://blockchair.com/api/docs"
        )
    
    def _load_market_data_sources(self):
        """Market data sources - CoinMarketCap, CoinGecko, etc."""
        
        # CoinMarketCap
        self.resources["coinmarketcap"] = APIResource(
            id="coinmarketcap",
            name="CoinMarketCap",
            resource_type=ResourceType.MARKET_DATA,
            base_url="https://pro-api.coinmarketcap.com/v1",
            api_key_env="COINMARKETCAP_KEY",
            api_key=os.getenv("COINMARKETCAP_KEY", "a35ffaec-c66c-4f16-81e3-41a717e4822f"),
            rate_limit="333 req/day free",
            is_free=True,
            requires_auth=True,
            description="Leading cryptocurrency market data API",
            endpoints={
                "listings_latest": "/cryptocurrency/listings/latest",
                "quotes_latest": "/cryptocurrency/quotes/latest",
                "info": "/cryptocurrency/info",
                "map": "/cryptocurrency/map",
                "categories": "/cryptocurrency/categories",
                "global_metrics": "/global-metrics/quotes/latest",
                "exchange_listings": "/exchange/listings/latest"
            },
            headers={"X-CMC_PRO_API_KEY": os.getenv("COINMARKETCAP_KEY", "a35ffaec-c66c-4f16-81e3-41a717e4822f")},
            features=["prices", "market_cap", "volume", "rankings", "historical"],
            supported_timeframes=["1h", "24h", "7d", "30d", "60d", "90d"],
            documentation_url="https://coinmarketcap.com/api/documentation/v1/"
        )
        
        # CoinGecko
        self.resources["coingecko"] = APIResource(
            id="coingecko",
            name="CoinGecko",
            resource_type=ResourceType.MARKET_DATA,
            base_url="https://api.coingecko.com/api/v3",
            rate_limit="10-50 req/min free",
            is_free=True,
            requires_auth=False,
            description="Comprehensive cryptocurrency data API",
            endpoints={
                "ping": "/ping",
                "simple_price": "/simple/price",
                "coins_list": "/coins/list",
                "coins_markets": "/coins/markets",
                "coin_detail": "/coins/{id}",
                "coin_history": "/coins/{id}/history",
                "coin_market_chart": "/coins/{id}/market_chart",
                "coin_ohlc": "/coins/{id}/ohlc",
                "trending": "/search/trending",
                "global": "/global",
                "exchanges": "/exchanges"
            },
            features=["prices", "market_cap", "volume", "historical", "trending", "defi"],
            supported_timeframes=["1d", "7d", "14d", "30d", "90d", "180d", "365d", "max"],
            documentation_url="https://www.coingecko.com/en/api/documentation"
        )
        
        # CoinCap
        self.resources["coincap"] = APIResource(
            id="coincap",
            name="CoinCap",
            resource_type=ResourceType.MARKET_DATA,
            base_url="https://api.coincap.io/v2",
            rate_limit="200 req/min free",
            is_free=True,
            requires_auth=False,
            description="Real-time cryptocurrency market data",
            endpoints={
                "assets": "/assets",
                "asset_detail": "/assets/{id}",
                "asset_history": "/assets/{id}/history",
                "markets": "/assets/{id}/markets",
                "rates": "/rates",
                "exchanges": "/exchanges",
                "candles": "/candles"
            },
            features=["real-time", "prices", "volume", "market_cap", "historical"],
            supported_timeframes=["m1", "m5", "m15", "m30", "h1", "h2", "h6", "h12", "d1"],
            documentation_url="https://docs.coincap.io/"
        )
        
        # Binance
        self.resources["binance"] = APIResource(
            id="binance",
            name="Binance",
            resource_type=ResourceType.MARKET_DATA,
            base_url="https://api.binance.com/api/v3",
            rate_limit="1200 req/min",
            is_free=True,
            requires_auth=False,
            description="Binance exchange public API",
            endpoints={
                "ping": "/ping",
                "time": "/time",
                "ticker_price": "/ticker/price",
                "ticker_24hr": "/ticker/24hr",
                "klines": "/klines",
                "depth": "/depth",
                "trades": "/trades",
                "avg_price": "/avgPrice",
                "exchange_info": "/exchangeInfo"
            },
            features=["real-time", "prices", "ohlcv", "order_book", "trades"],
            supported_timeframes=["1m", "3m", "5m", "15m", "30m", "1h", "2h", "4h", "6h", "8h", "12h", "1d", "3d", "1w", "1M"],
            documentation_url="https://binance-docs.github.io/apidocs/spot/en/"
        )
        
        # KuCoin
        self.resources["kucoin"] = APIResource(
            id="kucoin",
            name="KuCoin",
            resource_type=ResourceType.MARKET_DATA,
            base_url="https://api.kucoin.com/api/v1",
            rate_limit="varies",
            is_free=True,
            requires_auth=False,
            description="KuCoin exchange public API",
            endpoints={
                "market_list": "/market/allTickers",
                "ticker": "/market/orderbook/level1",
                "market_stats": "/market/stats",
                "currencies": "/currencies",
                "symbols": "/symbols",
                "klines": "/market/candles"
            },
            features=["prices", "ohlcv", "order_book", "trades"],
            supported_timeframes=["1min", "3min", "5min", "15min", "30min", "1hour", "2hour", "4hour", "6hour", "8hour", "12hour", "1day", "1week"],
            documentation_url="https://docs.kucoin.com/"
        )
        
        # Kraken
        self.resources["kraken"] = APIResource(
            id="kraken",
            name="Kraken",
            resource_type=ResourceType.MARKET_DATA,
            base_url="https://api.kraken.com/0/public",
            rate_limit="1 req/sec",
            is_free=True,
            requires_auth=False,
            description="Kraken exchange public API",
            endpoints={
                "time": "/Time",
                "assets": "/Assets",
                "asset_pairs": "/AssetPairs",
                "ticker": "/Ticker",
                "ohlc": "/OHLC",
                "depth": "/Depth",
                "trades": "/Trades",
                "spread": "/Spread"
            },
            features=["prices", "ohlcv", "order_book", "trades"],
            supported_timeframes=["1", "5", "15", "30", "60", "240", "1440", "10080", "21600"],
            documentation_url="https://docs.kraken.com/rest/"
        )
    
    def _load_news_sources(self):
        """News sources - NewsAPI, CryptoPanic, RSS feeds"""
        
        # NewsAPI
        self.resources["newsapi"] = APIResource(
            id="newsapi",
            name="NewsAPI",
            resource_type=ResourceType.NEWS,
            base_url="https://newsapi.org/v2",
            api_key_env="NEWSAPI_KEY",
            api_key=os.getenv("NEWSAPI_KEY", "968a5e25552b4cb5ba3280361d8444ab"),
            rate_limit="100 req/day free",
            is_free=True,
            requires_auth=True,
            description="News articles from thousands of sources",
            endpoints={
                "everything": "/everything",
                "top_headlines": "/top-headlines",
                "sources": "/sources"
            },
            features=["articles", "headlines", "sources", "search"],
            documentation_url="https://newsapi.org/docs"
        )
        
        # CryptoPanic
        self.resources["cryptopanic"] = APIResource(
            id="cryptopanic",
            name="CryptoPanic",
            resource_type=ResourceType.NEWS,
            base_url="https://cryptopanic.com/api/v1",
            api_key_env="CRYPTOPANIC_KEY",
            rate_limit="5 req/sec",
            is_free=True,
            requires_auth=True,
            description="Cryptocurrency news aggregator",
            endpoints={
                "posts": "/posts/",
                "currencies": "/currencies/"
            },
            features=["news", "sentiment", "trending"],
            documentation_url="https://cryptopanic.com/developers/api/"
        )
        
        # CoinDesk RSS
        self.resources["coindesk_rss"] = APIResource(
            id="coindesk_rss",
            name="CoinDesk RSS",
            resource_type=ResourceType.NEWS,
            base_url="https://www.coindesk.com",
            rate_limit="unlimited",
            is_free=True,
            requires_auth=False,
            description="CoinDesk crypto news RSS feed",
            endpoints={
                "rss": "/arc/outboundfeeds/rss/"
            },
            features=["news", "rss"],
            documentation_url="https://www.coindesk.com/arc/outboundfeeds/rss/"
        )
        
        # Cointelegraph RSS
        self.resources["cointelegraph_rss"] = APIResource(
            id="cointelegraph_rss",
            name="Cointelegraph RSS",
            resource_type=ResourceType.NEWS,
            base_url="https://cointelegraph.com",
            rate_limit="unlimited",
            is_free=True,
            requires_auth=False,
            description="Cointelegraph crypto news RSS feed",
            endpoints={
                "rss": "/rss"
            },
            features=["news", "rss"],
            documentation_url="https://cointelegraph.com/rss"
        )
        
        # CryptoCompare News
        self.resources["cryptocompare_news"] = APIResource(
            id="cryptocompare_news",
            name="CryptoCompare News",
            resource_type=ResourceType.NEWS,
            base_url="https://min-api.cryptocompare.com/data",
            rate_limit="100,000 req/month free",
            is_free=True,
            requires_auth=False,
            description="CryptoCompare news API",
            endpoints={
                "news_latest": "/v2/news/?lang=EN",
                "news_feeds": "/news/feeds",
                "news_categories": "/news/categories"
            },
            features=["news", "categories", "feeds"],
            documentation_url="https://min-api.cryptocompare.com/documentation"
        )
    
    def _load_sentiment_sources(self):
        """Sentiment analysis sources"""
        
        # Alternative.me Fear & Greed
        self.resources["fear_greed_index"] = APIResource(
            id="fear_greed_index",
            name="Fear & Greed Index",
            resource_type=ResourceType.SENTIMENT,
            base_url="https://api.alternative.me",
            rate_limit="unlimited",
            is_free=True,
            requires_auth=False,
            description="Crypto Fear & Greed Index",
            endpoints={
                "fng": "/fng/",
                "fng_history": "/fng/?limit=30"
            },
            features=["sentiment", "fear_greed", "historical"],
            supported_timeframes=["daily"],
            documentation_url="https://alternative.me/crypto/fear-and-greed-index/"
        )
        
        # Custom Sentiment API
        self.resources["custom_sentiment"] = APIResource(
            id="custom_sentiment",
            name="Custom Sentiment API",
            resource_type=ResourceType.SENTIMENT,
            base_url="https://sentiment-api.example.com",
            api_key_env="SENTIMENT_API_KEY",
            api_key=os.getenv("SENTIMENT_API_KEY", "vltdvdho63uqnjgf_fq75qbks72e3wfmx"),
            rate_limit="varies",
            is_free=True,
            requires_auth=True,
            description="Custom sentiment analysis API",
            endpoints={
                "analyze": "/analyze",
                "market_sentiment": "/market-sentiment",
                "social_sentiment": "/social-sentiment"
            },
            features=["sentiment", "social", "market"]
        )
        
        # LunarCrush
        self.resources["lunarcrush"] = APIResource(
            id="lunarcrush",
            name="LunarCrush",
            resource_type=ResourceType.SENTIMENT,
            base_url="https://lunarcrush.com/api/v2",
            api_key_env="LUNARCRUSH_KEY",
            rate_limit="varies",
            is_free=True,
            requires_auth=True,
            description="Social sentiment analytics",
            endpoints={
                "assets": "/assets",
                "market": "/market",
                "global": "/global",
                "influencers": "/influencers"
            },
            features=["social_sentiment", "influencers", "trending"],
            documentation_url="https://lunarcrush.com/developers"
        )
        
        # Santiment
        self.resources["santiment"] = APIResource(
            id="santiment",
            name="Santiment",
            resource_type=ResourceType.SENTIMENT,
            base_url="https://api.santiment.net/graphql",
            api_key_env="SANTIMENT_KEY",
            rate_limit="varies",
            is_free=False,
            requires_auth=True,
            description="On-chain and social metrics",
            endpoints={
                "graphql": ""
            },
            features=["on-chain", "social", "development"],
            documentation_url="https://academy.santiment.net/for-developers/"
        )
    
    def _load_onchain_analytics(self):
        """On-chain analytics sources"""
        
        # Glassnode
        self.resources["glassnode"] = APIResource(
            id="glassnode",
            name="Glassnode",
            resource_type=ResourceType.ONCHAIN,
            base_url="https://api.glassnode.com/v1/metrics",
            api_key_env="GLASSNODE_KEY",
            rate_limit="varies",
            is_free=False,
            requires_auth=True,
            description="On-chain market intelligence",
            endpoints={
                "market": "/market",
                "addresses": "/addresses",
                "supply": "/supply",
                "indicators": "/indicators"
            },
            features=["on-chain", "market_intelligence", "addresses"],
            documentation_url="https://docs.glassnode.com/"
        )
        
        # Blockchain.com
        self.resources["blockchain_com"] = APIResource(
            id="blockchain_com",
            name="Blockchain.com",
            resource_type=ResourceType.ONCHAIN,
            base_url="https://api.blockchain.info",
            rate_limit="varies",
            is_free=True,
            requires_auth=False,
            description="Bitcoin blockchain data",
            endpoints={
                "stats": "/stats",
                "ticker": "/ticker",
                "rawblock": "/rawblock/{hash}",
                "rawtx": "/rawtx/{hash}",
                "balance": "/balance"
            },
            features=["bitcoin", "transactions", "blocks", "addresses"],
            documentation_url="https://www.blockchain.com/api"
        )
        
        # Mempool.space
        self.resources["mempool_space"] = APIResource(
            id="mempool_space",
            name="Mempool.space",
            resource_type=ResourceType.ONCHAIN,
            base_url="https://mempool.space/api",
            rate_limit="varies",
            is_free=True,
            requires_auth=False,
            description="Bitcoin mempool and blockchain explorer",
            endpoints={
                "mempool": "/mempool",
                "fees_recommended": "/v1/fees/recommended",
                "blocks": "/blocks",
                "block_height": "/block-height/{height}",
                "tx": "/tx/{txid}"
            },
            features=["mempool", "fees", "blocks", "transactions"],
            documentation_url="https://mempool.space/docs/api"
        )
    
    def _load_defi_sources(self):
        """DeFi data sources"""
        
        # DefiLlama
        self.resources["defillama"] = APIResource(
            id="defillama",
            name="DefiLlama",
            resource_type=ResourceType.DEFI,
            base_url="https://api.llama.fi",
            rate_limit="unlimited",
            is_free=True,
            requires_auth=False,
            description="DeFi TVL and protocol analytics",
            endpoints={
                "protocols": "/protocols",
                "protocol_detail": "/protocol/{protocol}",
                "tvl_all": "/tvl",
                "chains": "/chains",
                "stablecoins": "/stablecoins",
                "yields": "/yields/pools",
                "dexs": "/overview/dexs"
            },
            features=["tvl", "protocols", "chains", "yields", "dexs"],
            documentation_url="https://defillama.com/docs/api"
        )
        
        # 1inch
        self.resources["1inch"] = APIResource(
            id="1inch",
            name="1inch",
            resource_type=ResourceType.DEFI,
            base_url="https://api.1inch.io/v5.0/1",
            rate_limit="varies",
            is_free=True,
            requires_auth=False,
            description="DEX aggregator API",
            endpoints={
                "tokens": "/tokens",
                "quote": "/quote",
                "swap": "/swap",
                "liquidity_sources": "/liquidity-sources"
            },
            features=["dex", "swap", "quotes", "aggregator"],
            documentation_url="https://docs.1inch.io/"
        )
        
        # Uniswap Subgraph
        self.resources["uniswap_subgraph"] = APIResource(
            id="uniswap_subgraph",
            name="Uniswap Subgraph",
            resource_type=ResourceType.DEFI,
            base_url="https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v3",
            rate_limit="varies",
            is_free=True,
            requires_auth=False,
            description="Uniswap V3 subgraph data",
            endpoints={
                "graphql": ""
            },
            features=["liquidity", "pools", "swaps", "tokens"],
            documentation_url="https://docs.uniswap.org/api/subgraph/overview"
        )
    
    def _load_whale_tracking(self):
        """Whale tracking and large transaction monitoring"""
        
        # Whale Alert
        self.resources["whale_alert"] = APIResource(
            id="whale_alert",
            name="Whale Alert",
            resource_type=ResourceType.WHALE_TRACKING,
            base_url="https://api.whale-alert.io/v1",
            api_key_env="WHALE_ALERT_KEY",
            rate_limit="10 req/min free",
            is_free=True,
            requires_auth=True,
            description="Large crypto transaction tracking",
            endpoints={
                "status": "/status",
                "transactions": "/transactions"
            },
            features=["whale_alerts", "large_transactions", "multi-chain"],
            documentation_url="https://docs.whale-alert.io/"
        )
        
        # Etherscan Whale Tracker (using main Etherscan)
        self.resources["etherscan_whales"] = APIResource(
            id="etherscan_whales",
            name="Etherscan Whale Tracker",
            resource_type=ResourceType.WHALE_TRACKING,
            base_url="https://api.etherscan.io/api",
            api_key_env="ETHERSCAN_KEY",
            api_key=os.getenv("ETHERSCAN_KEY", "SZHYFZK2RR8H9TIMJBVW54V4H81K2Z2KR2"),
            rate_limit="5 req/sec",
            is_free=True,
            requires_auth=True,
            description="Track large ETH/ERC20 transactions",
            endpoints={
                "large_txs": "?module=account&action=txlist&sort=desc",
                "token_transfers": "?module=account&action=tokentx&sort=desc"
            },
            features=["large_transactions", "ethereum", "erc20"]
        )
    
    def _load_technical_analysis(self):
        """Technical analysis sources"""
        
        # TAAPI
        self.resources["taapi"] = APIResource(
            id="taapi",
            name="TAAPI.IO",
            resource_type=ResourceType.TECHNICAL,
            base_url="https://api.taapi.io",
            api_key_env="TAAPI_KEY",
            rate_limit="varies",
            is_free=True,
            requires_auth=True,
            description="Technical analysis indicators API",
            endpoints={
                "rsi": "/rsi",
                "macd": "/macd",
                "ema": "/ema",
                "sma": "/sma",
                "bbands": "/bbands",
                "stoch": "/stoch",
                "atr": "/atr",
                "adx": "/adx",
                "dmi": "/dmi",
                "sar": "/sar",
                "ichimoku": "/ichimoku"
            },
            features=["indicators", "rsi", "macd", "bollinger", "ema", "sma"],
            documentation_url="https://taapi.io/documentation/"
        )
        
        # TradingView (unofficial scraping - use with caution)
        self.resources["tradingview_ideas"] = APIResource(
            id="tradingview_ideas",
            name="TradingView Ideas",
            resource_type=ResourceType.TECHNICAL,
            base_url="https://www.tradingview.com",
            rate_limit="limited",
            is_free=True,
            requires_auth=False,
            description="TradingView trading ideas",
            endpoints={
                "ideas": "/ideas/"
            },
            features=["ideas", "analysis", "charts"],
            documentation_url="https://www.tradingview.com/"
        )
    
    def _load_social_sources(self):
        """Social media and community sources"""
        
        # Reddit
        self.resources["reddit"] = APIResource(
            id="reddit",
            name="Reddit API",
            resource_type=ResourceType.SOCIAL,
            base_url="https://www.reddit.com",
            rate_limit="60 req/min",
            is_free=True,
            requires_auth=False,
            description="Reddit cryptocurrency communities",
            endpoints={
                "r_crypto": "/r/CryptoCurrency/hot.json",
                "r_bitcoin": "/r/Bitcoin/hot.json",
                "r_ethereum": "/r/ethereum/hot.json",
                "r_altcoin": "/r/altcoin/hot.json",
                "r_defi": "/r/defi/hot.json"
            },
            features=["discussions", "sentiment", "trending"],
            documentation_url="https://www.reddit.com/dev/api/"
        )
        
        # Twitter/X (requires API key)
        self.resources["twitter"] = APIResource(
            id="twitter",
            name="Twitter/X API",
            resource_type=ResourceType.SOCIAL,
            base_url="https://api.twitter.com/2",
            api_key_env="TWITTER_BEARER_TOKEN",
            rate_limit="varies",
            is_free=False,
            requires_auth=True,
            description="Twitter/X crypto discussions",
            endpoints={
                "search": "/tweets/search/recent",
                "user": "/users/by/username/{username}",
                "tweets": "/tweets"
            },
            features=["tweets", "sentiment", "influencers"],
            documentation_url="https://developer.twitter.com/en/docs"
        )
    
    def _load_historical_sources(self):
        """Historical data sources"""
        
        # CryptoCompare Historical
        self.resources["cryptocompare_historical"] = APIResource(
            id="cryptocompare_historical",
            name="CryptoCompare Historical",
            resource_type=ResourceType.HISTORICAL,
            base_url="https://min-api.cryptocompare.com/data",
            rate_limit="100,000 req/month free",
            is_free=True,
            requires_auth=False,
            description="Historical crypto price data",
            endpoints={
                "histoday": "/v2/histoday",
                "histohour": "/v2/histohour",
                "histominute": "/histominute"
            },
            features=["ohlcv", "historical", "daily", "hourly", "minute"],
            supported_timeframes=["1m", "1h", "1d"],
            documentation_url="https://min-api.cryptocompare.com/documentation"
        )
        
        # Messari
        self.resources["messari"] = APIResource(
            id="messari",
            name="Messari",
            resource_type=ResourceType.HISTORICAL,
            base_url="https://data.messari.io/api/v1",
            api_key_env="MESSARI_KEY",
            rate_limit="20 req/min free",
            is_free=True,
            requires_auth=False,
            description="Crypto research and data",
            endpoints={
                "assets": "/assets",
                "asset_detail": "/assets/{symbol}",
                "asset_metrics": "/assets/{symbol}/metrics",
                "asset_profile": "/assets/{symbol}/profile"
            },
            features=["metrics", "profiles", "research"],
            documentation_url="https://messari.io/api"
        )
    
    # ============ Registry Access Methods ============
    
    def get_resource(self, resource_id: str) -> Optional[APIResource]:
        """Get a specific resource by ID"""
        return self.resources.get(resource_id)
    
    def get_by_type(self, resource_type: ResourceType) -> List[APIResource]:
        """Get all resources of a specific type"""
        return [r for r in self.resources.values() if r.resource_type == resource_type]
    
    def get_free_resources(self) -> List[APIResource]:
        """Get all free resources"""
        return [r for r in self.resources.values() if r.is_free]
    
    def get_active_resources(self) -> List[APIResource]:
        """Get all active resources"""
        return [r for r in self.resources.values() if r.is_active]
    
    def get_no_auth_resources(self) -> List[APIResource]:
        """Get all resources that don't require authentication"""
        return [r for r in self.resources.values() if not r.requires_auth]
    
    def search_resources(self, query: str) -> List[APIResource]:
        """Search resources by name or description"""
        query_lower = query.lower()
        return [
            r for r in self.resources.values()
            if query_lower in r.name.lower() or query_lower in r.description.lower()
        ]
    
    def get_all_resources(self) -> List[APIResource]:
        """Get all registered resources"""
        return list(self.resources.values())
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get registry statistics"""
        resources = list(self.resources.values())
        return {
            "total_resources": len(resources),
            "free_resources": len([r for r in resources if r.is_free]),
            "active_resources": len([r for r in resources if r.is_active]),
            "no_auth_required": len([r for r in resources if not r.requires_auth]),
            "by_type": {
                rt.value: len([r for r in resources if r.resource_type == rt])
                for rt in ResourceType
            }
        }
    
    def export_to_dict(self) -> Dict[str, Any]:
        """Export all resources as dictionary"""
        return {
            rid: {
                "id": r.id,
                "name": r.name,
                "type": r.resource_type.value,
                "base_url": r.base_url,
                "is_free": r.is_free,
                "requires_auth": r.requires_auth,
                "is_active": r.is_active,
                "rate_limit": r.rate_limit,
                "description": r.description,
                "endpoints": r.endpoints,
                "features": r.features
            }
            for rid, r in self.resources.items()
        }


# ============ ML Models Configuration ============

ML_MODELS_CONFIG = {
    "price_prediction_lstm": {
        "name": "PricePredictionLSTM",
        "type": "LSTM",
        "purpose": "Short-term price prediction",
        "input_features": ["open", "high", "low", "close", "volume"],
        "timeframes": ["1m", "5m", "15m", "1h", "4h"],
        "huggingface_model": None
    },
    "sentiment_analysis_transformer": {
        "name": "SentimentAnalysisTransformer",
        "type": "Transformer",
        "purpose": "News and social media sentiment analysis",
        "huggingface_model": "ProsusAI/finbert"
    },
    "anomaly_detection_isolation_forest": {
        "name": "AnomalyDetectionIsolationForest",
        "type": "Isolation Forest",
        "purpose": "Detecting market anomalies"
    },
    "trend_classification_random_forest": {
        "name": "TrendClassificationRandomForest",
        "type": "Random Forest",
        "purpose": "Market trend classification"
    }
}


# ============ Analysis Endpoints Configuration ============

ANALYSIS_ENDPOINTS = {
    "track_position": "/track_position",
    "market_analysis": "/market_analysis",
    "technical_analysis": "/technical_analysis",
    "sentiment_analysis": "/sentiment_analysis",
    "whale_activity": "/whale_activity",
    "trading_strategies": "/trading_strategies",
    "ai_prediction": "/ai_prediction",
    "risk_management": "/risk_management",
    "pdf_analysis": "/pdf_analysis",
    "ai_enhanced_analysis": "/ai_enhanced_analysis",
    "multi_source_data": "/multi_source_data",
    "news_analysis": "/news_analysis",
    "exchange_integration": "/exchange_integration",
    "smart_alerts": "/smart_alerts",
    "advanced_social_media_analysis": "/advanced_social_media_analysis",
    "dynamic_modeling": "/dynamic_modeling",
    "multi_currency_analysis": "/multi_currency_analysis",
    "telegram_settings": "/telegram_settings",
    "collect_data": "/collect-data",
    "greed_fear_index": "/greed-fear-index",
    "onchain_metrics": "/onchain-metrics",
    "custom_alerts": "/custom-alerts",
    "stakeholder_analysis": "/stakeholder-analysis"
}


# ============ Singleton Instance ============

_registry_instance: Optional[FreeResourcesRegistry] = None


def get_free_resources_registry() -> FreeResourcesRegistry:
    """Get or create the singleton registry instance"""
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = FreeResourcesRegistry()
    return _registry_instance


# ============ Test Function ============

if __name__ == "__main__":
    registry = get_free_resources_registry()
    stats = registry.get_statistics()
    
    print("=" * 60)
    print("FREE RESOURCES REGISTRY - STATISTICS")
    print("=" * 60)
    print(f"Total Resources: {stats['total_resources']}")
    print(f"Free Resources: {stats['free_resources']}")
    print(f"Active Resources: {stats['active_resources']}")
    print(f"No Auth Required: {stats['no_auth_required']}")
    print()
    print("By Type:")
    for rtype, count in stats['by_type'].items():
        print(f"  - {rtype}: {count}")
    
    print()
    print("=" * 60)
    print("BLOCK EXPLORERS (with API keys)")
    print("=" * 60)
    for r in registry.get_by_type(ResourceType.BLOCKCHAIN):
        print(f"  - {r.name}: {r.base_url}")
        if r.api_key:
            print(f"    API Key: {r.api_key[:10]}...")
    
    print()
    print("=" * 60)
    print("MARKET DATA SOURCES")
    print("=" * 60)
    for r in registry.get_by_type(ResourceType.MARKET_DATA):
        print(f"  - {r.name}: {r.base_url}")
        print(f"    Features: {', '.join(r.features[:5])}")
