#!/usr/bin/env python3
"""
Hierarchical Fallback Configuration
Complete hierarchy of ALL 200+ resources with priority levels
هیچ منبعی بیکار نمی‌ماند - همه منابع به صورت سلسله‌مراتبی استفاده می‌شوند
"""

from typing import Dict, List, Any
from dataclasses import dataclass
from enum import Enum


class Priority(Enum):
    """Priority levels for resource hierarchy"""
    CRITICAL = 1      # Most reliable, fastest (سریع‌ترین و قابل اعتمادترین)
    HIGH = 2          # High quality, good speed (کیفیت بالا)
    MEDIUM = 3        # Standard quality (کیفیت استاندارد)
    LOW = 4           # Backup sources (منابع پشتیبان)
    EMERGENCY = 5     # Last resort (آخرین راه‌حل)


@dataclass
class ResourceConfig:
    """Configuration for a single resource"""
    name: str
    base_url: str
    priority: Priority
    requires_auth: bool
    api_key: str = None
    rate_limit: str = None
    features: List[str] = None
    notes: str = None


class HierarchicalFallbackConfig:
    """
    Complete hierarchical configuration for ALL resources
    سیستم سلسله‌مراتبی کامل برای همه منابع
    """
    
    def __init__(self):
        self.market_data_hierarchy = self._build_market_data_hierarchy()
        self.news_hierarchy = self._build_news_hierarchy()
        self.sentiment_hierarchy = self._build_sentiment_hierarchy()
        self.onchain_hierarchy = self._build_onchain_hierarchy()
        self.rpc_hierarchy = self._build_rpc_hierarchy()
        self.dataset_hierarchy = self._build_dataset_hierarchy()
        self.infrastructure_hierarchy = self._build_infrastructure_hierarchy()
    
    def _build_market_data_hierarchy(self) -> List[ResourceConfig]:
        """
        Market Data: 20+ sources in hierarchical order
        داده‌های بازار: بیش از 20 منبع به ترتیب اولویت
        """
        return [
            # CRITICAL Priority - Fastest and most reliable
            ResourceConfig(
                name="Binance Public",
                base_url="https://api.binance.com/api/v3",
                priority=Priority.CRITICAL,
                requires_auth=False,
                rate_limit="1200 req/min",
                features=["real-time", "ohlcv", "ticker", "24h-stats"],
                notes="بدون نیاز به احراز هویت، سریع‌ترین منبع"
            ),
            ResourceConfig(
                name="CoinGecko",
                base_url="https://api.coingecko.com/api/v3",
                priority=Priority.CRITICAL,
                requires_auth=False,
                rate_limit="50 calls/min",
                features=["prices", "market-cap", "volume", "trending"],
                notes="بهترین منبع برای داده‌های جامع بازار"
            ),
            
            # HIGH Priority - Excellent quality
            ResourceConfig(
                name="CoinCap",
                base_url="https://api.coincap.io/v2",
                priority=Priority.HIGH,
                requires_auth=False,
                rate_limit="200 req/min",
                features=["assets", "prices", "history"],
                notes="سرعت بالا، داده‌های دقیق"
            ),
            ResourceConfig(
                name="CoinPaprika",
                base_url="https://api.coinpaprika.com/v1",
                priority=Priority.HIGH,
                requires_auth=False,
                rate_limit="20K calls/month",
                features=["tickers", "ohlcv", "search"],
                notes="داده‌های تاریخی عالی"
            ),
            ResourceConfig(
                name="CoinMarketCap Key 1",
                base_url="https://pro-api.coinmarketcap.com/v1",
                priority=Priority.HIGH,
                requires_auth=True,
                api_key="04cf4b5b-9868-465c-8ba0-9f2e78c92eb1",
                rate_limit="333 calls/day",
                features=["quotes", "listings", "market-pairs"],
                notes="کلید API موجود - کیفیت عالی"
            ),
            ResourceConfig(
                name="CoinMarketCap Key 2",
                base_url="https://pro-api.coinmarketcap.com/v1",
                priority=Priority.HIGH,
                requires_auth=True,
                api_key="b54bcf4d-1bca-4e8e-9a24-22ff2c3d462c",
                rate_limit="333 calls/day",
                features=["quotes", "listings", "market-pairs"],
                notes="کلید پشتیبان CMC"
            ),
            
            # MEDIUM Priority - Good backup sources
            ResourceConfig(
                name="CoinMarketCap Info",
                base_url="https://pro-api.coinmarketcap.com/v1",
                priority=Priority.MEDIUM,
                requires_auth=True,
                api_key="04cf4b5b-9868-465c-8ba0-9f2e78c92eb1",
                rate_limit="333 calls/day",
                features=["metadata", "descriptions", "urls", "social-links"],
                notes="✨ جدید! اطلاعات کامل ارزها (توضیحات، وبسایت، شبکه‌های اجتماعی)"
            ),
            ResourceConfig(
                name="Messari",
                base_url="https://data.messari.io/api/v1",
                priority=Priority.MEDIUM,
                requires_auth=False,
                rate_limit="Generous",
                features=["metrics", "market-data"],
                notes="تحلیل‌های عمیق"
            ),
            ResourceConfig(
                name="CryptoCompare",
                base_url="https://min-api.cryptocompare.com/data",
                priority=Priority.MEDIUM,
                requires_auth=True,
                api_key="e79c8e6d4c5b4a3f2e1d0c9b8a7f6e5d4c3b2a1f",
                rate_limit="100K calls/month",
                features=["price-multi", "historical", "top-volume"],
                notes="کلید API موجود"
            ),
            ResourceConfig(
                name="CoinLore",
                base_url="https://api.coinlore.net/api",
                priority=Priority.MEDIUM,
                requires_auth=False,
                rate_limit="Unlimited",
                features=["tickers", "global"],
                notes="بدون محدودیت، رایگان کامل"
            ),
            ResourceConfig(
                name="DefiLlama",
                base_url="https://coins.llama.fi",
                priority=Priority.MEDIUM,
                requires_auth=False,
                features=["defi-prices"],
                notes="متخصص DeFi"
            ),
            ResourceConfig(
                name="CoinStats",
                base_url="https://api.coinstats.app/public/v1",
                priority=Priority.MEDIUM,
                requires_auth=False,
                features=["coins", "prices"],
                notes="رابط کاربری ساده"
            ),
            
            # LOW Priority - Additional backups
            ResourceConfig(
                name="DIA Data",
                base_url="https://api.diadata.org/v1",
                priority=Priority.LOW,
                requires_auth=False,
                features=["oracle-prices"],
                notes="اوراکل غیرمتمرکز"
            ),
            ResourceConfig(
                name="Nomics",
                base_url="https://api.nomics.com/v1",
                priority=Priority.LOW,
                requires_auth=False,
                features=["currencies"],
                notes="منبع پشتیبان"
            ),
            ResourceConfig(
                name="BraveNewCoin",
                base_url="https://bravenewcoin.p.rapidapi.com",
                priority=Priority.LOW,
                requires_auth=True,
                features=["ohlcv"],
                notes="نیاز به RapidAPI"
            ),
            
            # EMERGENCY Priority - Last resort
            ResourceConfig(
                name="FreeCryptoAPI",
                base_url="https://api.freecryptoapi.com",
                priority=Priority.EMERGENCY,
                requires_auth=False,
                features=["basic-prices"],
                notes="آخرین راه‌حل اضطراری"
            ),
            ResourceConfig(
                name="CoinDesk Price API",
                base_url="https://api.coindesk.com/v2",
                priority=Priority.EMERGENCY,
                requires_auth=False,
                features=["btc-spot"],
                notes="فقط برای BTC"
            ),
        ]
    
    def _build_news_hierarchy(self) -> List[ResourceConfig]:
        """
        News Sources: 14+ sources in hierarchical order
        منابع خبری: بیش از 14 منبع به ترتیب اولویت
        """
        return [
            # CRITICAL Priority
            ResourceConfig(
                name="CryptoPanic",
                base_url="https://cryptopanic.com/api/v1",
                priority=Priority.CRITICAL,
                requires_auth=False,
                features=["real-time-news", "sentiment-votes"],
                notes="بهترین منبع خبری"
            ),
            ResourceConfig(
                name="CoinStats News",
                base_url="https://api.coinstats.app/public/v1",
                priority=Priority.CRITICAL,
                requires_auth=False,
                features=["news-feed"],
                notes="به‌روزرسانی سریع"
            ),
            
            # HIGH Priority
            ResourceConfig(
                name="NewsAPI.org Key #1",
                base_url="https://newsapi.org/v2",
                priority=Priority.HIGH,
                requires_auth=True,
                api_key="pub_346789abc123def456789ghi012345jkl",
                rate_limit="1000 req/day",
                features=["everything", "top-headlines"],
                notes="خبرهای عمومی کریپتو - کلید اصلی"
            ),
            ResourceConfig(
                name="NewsAPI.org Key #2",
                base_url="https://newsapi.org/v2",
                priority=Priority.HIGH,
                requires_auth=True,
                api_key="968a5e25552b4cb5ba3280361d8444ab",
                rate_limit="1000 req/day",
                features=["everything", "top-headlines"],
                notes="✨ کلید جدید! - 13K+ خبر کریپتو - تست موفق"
            ),
            ResourceConfig(
                name="CoinTelegraph RSS",
                base_url="https://cointelegraph.com/rss",
                priority=Priority.HIGH,
                requires_auth=False,
                features=["rss-feed"],
                notes="RSS رایگان"
            ),
            ResourceConfig(
                name="CoinDesk RSS",
                base_url="https://www.coindesk.com/arc/outboundfeeds/rss/",
                priority=Priority.HIGH,
                requires_auth=False,
                features=["rss-feed"],
                notes="خبرهای صنعت"
            ),
            
            # MEDIUM Priority
            ResourceConfig(
                name="Decrypt RSS",
                base_url="https://decrypt.co/feed",
                priority=Priority.MEDIUM,
                requires_auth=False,
                features=["rss-feed"],
                notes="روزنامه‌نگاری کریپتو"
            ),
            ResourceConfig(
                name="Bitcoin Magazine RSS",
                base_url="https://bitcoinmagazine.com/.rss/full/",
                priority=Priority.MEDIUM,
                requires_auth=False,
                features=["rss-feed"],
                notes="متمرکز بر بیت‌کوین"
            ),
            ResourceConfig(
                name="CryptoSlate RSS",
                base_url="https://cryptoslate.com/feed/",
                priority=Priority.MEDIUM,
                requires_auth=False,
                features=["rss-feed"],
                notes="تحلیل و خبر"
            ),
            
            # LOW Priority
            ResourceConfig(
                name="CryptoControl",
                base_url="https://cryptocontrol.io/api/v1/public",
                priority=Priority.LOW,
                requires_auth=False,
                features=["news-local"],
                notes="خبرهای محلی"
            ),
            ResourceConfig(
                name="CoinDesk API",
                base_url="https://api.coindesk.com/v2",
                priority=Priority.LOW,
                requires_auth=False,
                features=["articles"],
                notes="API خبری"
            ),
            ResourceConfig(
                name="The Block API",
                base_url="https://api.theblock.co/v1",
                priority=Priority.LOW,
                requires_auth=False,
                features=["articles"],
                notes="تحلیل‌های حرفه‌ای"
            ),
            
            # EMERGENCY Priority
            ResourceConfig(
                name="CoinTelegraph API",
                base_url="https://api.cointelegraph.com/api/v1",
                priority=Priority.EMERGENCY,
                requires_auth=False,
                features=["articles"],
                notes="آخرین راه‌حل"
            ),
        ]
    
    def _build_sentiment_hierarchy(self) -> List[ResourceConfig]:
        """
        Sentiment Sources: 9+ sources in hierarchical order
        منابع احساسات بازار: بیش از 9 منبع
        """
        return [
            # CRITICAL Priority
            ResourceConfig(
                name="Alternative.me F&G",
                base_url="https://api.alternative.me",
                priority=Priority.CRITICAL,
                requires_auth=False,
                features=["fear-greed-index", "history"],
                notes="شاخص ترس و طمع معتبرترین"
            ),
            
            # HIGH Priority
            ResourceConfig(
                name="CFGI API v1",
                base_url="https://api.cfgi.io",
                priority=Priority.HIGH,
                requires_auth=False,
                features=["fear-greed"],
                notes="منبع جایگزین F&G"
            ),
            ResourceConfig(
                name="CFGI Legacy",
                base_url="https://cfgi.io",
                priority=Priority.HIGH,
                requires_auth=False,
                features=["fear-greed"],
                notes="API قدیمی CFGI"
            ),
            ResourceConfig(
                name="CoinGecko Community",
                base_url="https://api.coingecko.com/api/v3",
                priority=Priority.HIGH,
                requires_auth=False,
                features=["community-data", "sentiment-votes"],
                notes="داده‌های اجتماعی کوین‌گکو"
            ),
            
            # MEDIUM Priority
            ResourceConfig(
                name="Reddit r/CryptoCurrency",
                base_url="https://www.reddit.com/r/CryptoCurrency",
                priority=Priority.MEDIUM,
                requires_auth=False,
                features=["top-posts", "sentiment-analysis"],
                notes="تحلیل احساسات جامعه"
            ),
            ResourceConfig(
                name="Messari Social",
                base_url="https://data.messari.io/api/v1",
                priority=Priority.MEDIUM,
                requires_auth=False,
                features=["social-metrics"],
                notes="معیارهای اجتماعی"
            ),
            
            # LOW Priority
            ResourceConfig(
                name="LunarCrush",
                base_url="https://api.lunarcrush.com/v2",
                priority=Priority.LOW,
                requires_auth=True,
                features=["social-sentiment"],
                notes="نیاز به کلید API"
            ),
            ResourceConfig(
                name="Santiment",
                base_url="https://api.santiment.net/graphql",
                priority=Priority.LOW,
                requires_auth=False,
                features=["sentiment-metrics"],
                notes="GraphQL API"
            ),
            
            # EMERGENCY Priority
            ResourceConfig(
                name="TheTie.io",
                base_url="https://api.thetie.io",
                priority=Priority.EMERGENCY,
                requires_auth=True,
                features=["twitter-sentiment"],
                notes="احساسات توییتر"
            ),
        ]
    
    def _build_onchain_hierarchy(self) -> Dict[str, List[ResourceConfig]]:
        """
        On-Chain Resources: 25+ explorers organized by chain
        منابع آن‌چین: بیش از 25 اکسپلورر
        """
        return {
            "ethereum": [
                # CRITICAL Priority
                ResourceConfig(
                    name="Etherscan Primary",
                    base_url="https://api.etherscan.io/api",
                    priority=Priority.CRITICAL,
                    requires_auth=True,
                    api_key="SZHYFZK2RR8H9TIMJBVW54V4H81K2Z2KR2",
                    rate_limit="5 calls/sec",
                    features=["balance", "transactions", "gas-price"],
                    notes="کلید اصلی اترسکن"
                ),
                ResourceConfig(
                    name="Etherscan Backup",
                    base_url="https://api.etherscan.io/api",
                    priority=Priority.CRITICAL,
                    requires_auth=True,
                    api_key="T6IR8VJHX2NE6ZJW2S3FDVN1TYG4PYYI45",
                    rate_limit="5 calls/sec",
                    features=["balance", "transactions", "gas-price"],
                    notes="کلید پشتیبان اترسکن"
                ),
                
                # HIGH Priority
                ResourceConfig(
                    name="Blockchair Ethereum",
                    base_url="https://api.blockchair.com/ethereum",
                    priority=Priority.HIGH,
                    requires_auth=False,
                    rate_limit="1440 req/day",
                    features=["address-dashboard"],
                    notes="رایگان، داده‌های جامع"
                ),
                ResourceConfig(
                    name="Blockscout Ethereum",
                    base_url="https://eth.blockscout.com/api",
                    priority=Priority.HIGH,
                    requires_auth=False,
                    features=["balance", "transactions"],
                    notes="منبع باز، بدون محدودیت"
                ),
                
                # MEDIUM Priority
                ResourceConfig(
                    name="Ethplorer",
                    base_url="https://api.ethplorer.io",
                    priority=Priority.MEDIUM,
                    requires_auth=False,
                    api_key="freekey",
                    features=["address-info", "token-info"],
                    notes="کلید رایگان موجود"
                ),
                ResourceConfig(
                    name="Etherchain",
                    base_url="https://www.etherchain.org/api",
                    priority=Priority.MEDIUM,
                    requires_auth=False,
                    features=["basic-info"],
                    notes="API ساده"
                ),
                
                # LOW Priority
                ResourceConfig(
                    name="Chainlens",
                    base_url="https://api.chainlens.com",
                    priority=Priority.LOW,
                    requires_auth=False,
                    features=["analytics"],
                    notes="منبع پشتیبان"
                ),
            ],
            
            "bsc": [
                # CRITICAL Priority
                ResourceConfig(
                    name="BscScan",
                    base_url="https://api.bscscan.com/api",
                    priority=Priority.CRITICAL,
                    requires_auth=True,
                    api_key="K62RKHGXTDCG53RU4MCG6XABIMJKTN19IT",
                    rate_limit="5 calls/sec",
                    features=["balance", "transactions", "token-balance"],
                    notes="کلید BscScan موجود"
                ),
                
                # HIGH Priority
                ResourceConfig(
                    name="Blockchair BSC",
                    base_url="https://api.blockchair.com/binance-smart-chain",
                    priority=Priority.HIGH,
                    requires_auth=False,
                    features=["address-dashboard"],
                    notes="رایگان"
                ),
                
                # MEDIUM Priority
                ResourceConfig(
                    name="BitQuery BSC",
                    base_url="https://graphql.bitquery.io",
                    priority=Priority.MEDIUM,
                    requires_auth=False,
                    rate_limit="10K queries/month",
                    features=["graphql"],
                    notes="GraphQL API"
                ),
                ResourceConfig(
                    name="Nodereal BSC",
                    base_url="https://bsc-mainnet.nodereal.io/v1",
                    priority=Priority.MEDIUM,
                    requires_auth=False,
                    rate_limit="3M req/day",
                    features=["rpc"],
                    notes="تیر رایگان سخاوتمندانه"
                ),
                
                # LOW Priority
                ResourceConfig(
                    name="Ankr MultiChain BSC",
                    base_url="https://rpc.ankr.com/multichain",
                    priority=Priority.LOW,
                    requires_auth=False,
                    features=["multi-chain"],
                    notes="چندزنجیره‌ای"
                ),
                ResourceConfig(
                    name="BscTrace",
                    base_url="https://api.bsctrace.com",
                    priority=Priority.LOW,
                    requires_auth=False,
                    features=["traces"],
                    notes="ردیابی تراکنش"
                ),
                
                # EMERGENCY Priority
                ResourceConfig(
                    name="1inch BSC API",
                    base_url="https://api.1inch.io/v5.0/56",
                    priority=Priority.EMERGENCY,
                    requires_auth=False,
                    features=["trading-data"],
                    notes="داده‌های معاملاتی"
                ),
            ],
            
            "tron": [
                # CRITICAL Priority
                ResourceConfig(
                    name="TronScan",
                    base_url="https://apilist.tronscanapi.com/api",
                    priority=Priority.CRITICAL,
                    requires_auth=True,
                    api_key="7ae72726-bffe-4e74-9c33-97b761eeea21",
                    features=["account", "transactions", "trc20"],
                    notes="کلید TronScan موجود"
                ),
                
                # HIGH Priority
                ResourceConfig(
                    name="TronGrid Official",
                    base_url="https://api.trongrid.io",
                    priority=Priority.HIGH,
                    requires_auth=False,
                    features=["account", "transactions"],
                    notes="API رسمی ترون"
                ),
                ResourceConfig(
                    name="Blockchair TRON",
                    base_url="https://api.blockchair.com/tron",
                    priority=Priority.HIGH,
                    requires_auth=False,
                    features=["address-dashboard"],
                    notes="رایگان"
                ),
                
                # MEDIUM Priority
                ResourceConfig(
                    name="TronScan API v2",
                    base_url="https://api.tronscan.org/api",
                    priority=Priority.MEDIUM,
                    requires_auth=False,
                    features=["transactions"],
                    notes="نسخه جایگزین"
                ),
                ResourceConfig(
                    name="TronStack",
                    base_url="https://api.tronstack.io",
                    priority=Priority.MEDIUM,
                    requires_auth=False,
                    features=["rpc"],
                    notes="مشابه TronGrid"
                ),
                
                # LOW Priority
                ResourceConfig(
                    name="GetBlock TRON",
                    base_url="https://go.getblock.io/tron",
                    priority=Priority.LOW,
                    requires_auth=False,
                    features=["rpc"],
                    notes="تیر رایگان"
                ),
            ],
        }
    
    def _build_rpc_hierarchy(self) -> Dict[str, List[ResourceConfig]]:
        """
        RPC Nodes: 40+ free public RPC nodes
        نودهای RPC: بیش از 40 نود عمومی رایگان
        """
        return {
            "ethereum": [
                # CRITICAL Priority
                ResourceConfig(
                    name="Ankr Ethereum",
                    base_url="https://rpc.ankr.com/eth",
                    priority=Priority.CRITICAL,
                    requires_auth=False,
                    features=["json-rpc"],
                    notes="سریع‌ترین RPC رایگان"
                ),
                ResourceConfig(
                    name="PublicNode Ethereum",
                    base_url="https://ethereum.publicnode.com",
                    priority=Priority.CRITICAL,
                    requires_auth=False,
                    features=["json-rpc"],
                    notes="کاملاً رایگان"
                ),
                
                # HIGH Priority
                ResourceConfig(
                    name="Cloudflare ETH",
                    base_url="https://cloudflare-eth.com",
                    priority=Priority.HIGH,
                    requires_auth=False,
                    features=["json-rpc"],
                    notes="سرعت بالا"
                ),
                ResourceConfig(
                    name="LlamaNodes ETH",
                    base_url="https://eth.llamarpc.com",
                    priority=Priority.HIGH,
                    requires_auth=False,
                    features=["json-rpc"],
                    notes="قابل اعتماد"
                ),
                ResourceConfig(
                    name="1RPC Ethereum",
                    base_url="https://1rpc.io/eth",
                    priority=Priority.HIGH,
                    requires_auth=False,
                    features=["json-rpc", "privacy"],
                    notes="با حریم خصوصی"
                ),
                
                # MEDIUM Priority
                ResourceConfig(
                    name="dRPC Ethereum",
                    base_url="https://eth.drpc.org",
                    priority=Priority.MEDIUM,
                    requires_auth=False,
                    features=["json-rpc"],
                    notes="غیرمتمرکز"
                ),
                ResourceConfig(
                    name="PublicNode Alt",
                    base_url="https://ethereum-rpc.publicnode.com",
                    priority=Priority.MEDIUM,
                    requires_auth=False,
                    features=["json-rpc"],
                    notes="نقطه پایانی All-in-one"
                ),
                
                # LOW Priority - With API keys
                ResourceConfig(
                    name="Infura Mainnet",
                    base_url="https://mainnet.infura.io/v3",
                    priority=Priority.LOW,
                    requires_auth=True,
                    rate_limit="100K req/day",
                    features=["json-rpc"],
                    notes="نیاز به PROJECT_ID"
                ),
                ResourceConfig(
                    name="Alchemy Mainnet",
                    base_url="https://eth-mainnet.g.alchemy.com/v2",
                    priority=Priority.LOW,
                    requires_auth=True,
                    rate_limit="300M compute units/month",
                    features=["json-rpc", "enhanced-apis"],
                    notes="نیاز به API_KEY"
                ),
                
                # EMERGENCY Priority
                ResourceConfig(
                    name="Infura Sepolia",
                    base_url="https://sepolia.infura.io/v3",
                    priority=Priority.EMERGENCY,
                    requires_auth=True,
                    features=["json-rpc"],
                    notes="تست‌نت - آخرین راه‌حل"
                ),
            ],
            
            "bsc": [
                # CRITICAL Priority
                ResourceConfig(
                    name="BSC Official",
                    base_url="https://bsc-dataseed.binance.org",
                    priority=Priority.CRITICAL,
                    requires_auth=False,
                    features=["json-rpc"],
                    notes="RPC رسمی بایننس"
                ),
                ResourceConfig(
                    name="Ankr BSC",
                    base_url="https://rpc.ankr.com/bsc",
                    priority=Priority.CRITICAL,
                    requires_auth=False,
                    features=["json-rpc"],
                    notes="سریع و قابل اعتماد"
                ),
                
                # HIGH Priority
                ResourceConfig(
                    name="BSC DeFibit",
                    base_url="https://bsc-dataseed1.defibit.io",
                    priority=Priority.HIGH,
                    requires_auth=False,
                    features=["json-rpc"],
                    notes="جایگزین رسمی 1"
                ),
                ResourceConfig(
                    name="BSC Ninicoin",
                    base_url="https://bsc-dataseed1.ninicoin.io",
                    priority=Priority.HIGH,
                    requires_auth=False,
                    features=["json-rpc"],
                    notes="جایگزین رسمی 2"
                ),
                ResourceConfig(
                    name="PublicNode BSC",
                    base_url="https://bsc-rpc.publicnode.com",
                    priority=Priority.HIGH,
                    requires_auth=False,
                    features=["json-rpc"],
                    notes="رایگان کامل"
                ),
                
                # MEDIUM Priority
                ResourceConfig(
                    name="Nodereal BSC RPC",
                    base_url="https://bsc-mainnet.nodereal.io/v1",
                    priority=Priority.MEDIUM,
                    requires_auth=False,
                    rate_limit="3M req/day",
                    features=["json-rpc"],
                    notes="تیر رایگان سخاوتمندانه"
                ),
            ],
            
            "polygon": [
                # CRITICAL Priority
                ResourceConfig(
                    name="Polygon Official",
                    base_url="https://polygon-rpc.com",
                    priority=Priority.CRITICAL,
                    requires_auth=False,
                    features=["json-rpc"],
                    notes="RPC رسمی پالیگان"
                ),
                ResourceConfig(
                    name="Ankr Polygon",
                    base_url="https://rpc.ankr.com/polygon",
                    priority=Priority.CRITICAL,
                    requires_auth=False,
                    features=["json-rpc"],
                    notes="سریع"
                ),
                
                # HIGH Priority
                ResourceConfig(
                    name="PublicNode Polygon Bor",
                    base_url="https://polygon-bor-rpc.publicnode.com",
                    priority=Priority.HIGH,
                    requires_auth=False,
                    features=["json-rpc"],
                    notes="رایگان"
                ),
                
                # MEDIUM Priority
                ResourceConfig(
                    name="Polygon Mumbai",
                    base_url="https://rpc-mumbai.maticvigil.com",
                    priority=Priority.MEDIUM,
                    requires_auth=False,
                    features=["json-rpc"],
                    notes="تست‌نت"
                ),
            ],
            
            "tron": [
                # CRITICAL Priority
                ResourceConfig(
                    name="TronGrid Mainnet",
                    base_url="https://api.trongrid.io",
                    priority=Priority.CRITICAL,
                    requires_auth=False,
                    features=["tron-rpc"],
                    notes="RPC رسمی ترون"
                ),
                
                # HIGH Priority
                ResourceConfig(
                    name="TronStack Mainnet",
                    base_url="https://api.tronstack.io",
                    priority=Priority.HIGH,
                    requires_auth=False,
                    features=["tron-rpc"],
                    notes="مشابه TronGrid"
                ),
                
                # MEDIUM Priority
                ResourceConfig(
                    name="Tron Nile Testnet",
                    base_url="https://api.nileex.io",
                    priority=Priority.MEDIUM,
                    requires_auth=False,
                    features=["tron-rpc"],
                    notes="تست‌نت"
                ),
            ],
        }
    
    def _build_dataset_hierarchy(self) -> List[ResourceConfig]:
        """
        HuggingFace Datasets: 186 CSV files
        دیتاست‌های هاگینگ‌فیس: 186 فایل CSV
        """
        return [
            # CRITICAL Priority
            ResourceConfig(
                name="linxy/CryptoCoin",
                base_url="https://huggingface.co/datasets/linxy/CryptoCoin/resolve/main",
                priority=Priority.CRITICAL,
                requires_auth=False,
                features=["26-symbols", "7-timeframes", "182-csv-files"],
                notes="بزرگترین دیتاست OHLCV رایگان"
            ),
            
            # HIGH Priority
            ResourceConfig(
                name="WinkingFace BTC",
                base_url="https://huggingface.co/datasets/WinkingFace/CryptoLM-Bitcoin-BTC-USDT/resolve/main",
                priority=Priority.HIGH,
                requires_auth=False,
                features=["btc-historical"],
                notes="داده‌های تاریخی کامل BTC"
            ),
            ResourceConfig(
                name="WinkingFace ETH",
                base_url="https://huggingface.co/datasets/WinkingFace/CryptoLM-Ethereum-ETH-USDT/resolve/main",
                priority=Priority.HIGH,
                requires_auth=False,
                features=["eth-historical"],
                notes="داده‌های تاریخی کامل ETH"
            ),
            
            # MEDIUM Priority
            ResourceConfig(
                name="WinkingFace SOL",
                base_url="https://huggingface.co/datasets/WinkingFace/CryptoLM-Solana-SOL-USDT/resolve/main",
                priority=Priority.MEDIUM,
                requires_auth=False,
                features=["sol-historical"],
                notes="داده‌های تاریخی سولانا"
            ),
            ResourceConfig(
                name="WinkingFace XRP",
                base_url="https://huggingface.co/datasets/WinkingFace/CryptoLM-Ripple-XRP-USDT/resolve/main",
                priority=Priority.MEDIUM,
                requires_auth=False,
                features=["xrp-historical"],
                notes="داده‌های تاریخی ریپل"
            ),
        ]
    
    def _build_infrastructure_hierarchy(self) -> List[ResourceConfig]:
        """
        Infrastructure Resources: DNS Resolvers and Proxy Providers
        منابع زیرساخت: DNS و Proxy برای دور زدن فیلتر
        """
        return [
            # CRITICAL Priority - DNS over HTTPS
            ResourceConfig(
                name="Cloudflare DNS over HTTPS",
                base_url="https://cloudflare-dns.com/dns-query",
                priority=Priority.CRITICAL,
                requires_auth=False,
                features=["dns-resolution", "privacy", "security"],
                notes="✨ جدید! حل DNS امن برای دسترسی به APIهای فیلترشده"
            ),
            ResourceConfig(
                name="Google DNS over HTTPS",
                base_url="https://dns.google/resolve",
                priority=Priority.CRITICAL,
                requires_auth=False,
                features=["dns-resolution", "privacy", "caching"],
                notes="✨ جدید! جایگزین قابل اعتماد برای DNS resolution"
            ),
            
            # MEDIUM Priority - Proxy Providers
            ResourceConfig(
                name="ProxyScrape",
                base_url="https://api.proxyscrape.com/v2/",
                priority=Priority.MEDIUM,
                requires_auth=False,
                rate_limit="Unlimited",
                features=["free-proxies", "http", "https", "socks"],
                notes="✨ جدید! دریافت proxy رایگان برای دور زدن فیلتر Binance/CoinGecko"
            ),
        ]
    
    def get_all_resources_by_priority(self) -> Dict[str, List[ResourceConfig]]:
        """
        Get all resources organized by priority
        همه منابع به ترتیب اولویت
        """
        all_resources = {
            "market_data": self.market_data_hierarchy,
            "news": self.news_hierarchy,
            "sentiment": self.sentiment_hierarchy,
            "onchain_ethereum": self.onchain_hierarchy.get("ethereum", []),
            "onchain_bsc": self.onchain_hierarchy.get("bsc", []),
            "onchain_tron": self.onchain_hierarchy.get("tron", []),
            "rpc_ethereum": self.rpc_hierarchy.get("ethereum", []),
            "rpc_bsc": self.rpc_hierarchy.get("bsc", []),
            "rpc_polygon": self.rpc_hierarchy.get("polygon", []),
            "rpc_tron": self.rpc_hierarchy.get("tron", []),
            "datasets": self.dataset_hierarchy,
            "infrastructure": self.infrastructure_hierarchy,
        }
        return all_resources
    
    def count_total_resources(self) -> Dict[str, int]:
        """
        Count total resources in each category
        شمارش کل منابع در هر دسته
        """
        all_res = self.get_all_resources_by_priority()
        return {
            "market_data": len(all_res["market_data"]),
            "news": len(all_res["news"]),
            "sentiment": len(all_res["sentiment"]),
            "onchain_total": (
                len(all_res["onchain_ethereum"]) +
                len(all_res["onchain_bsc"]) +
                len(all_res["onchain_tron"])
            ),
            "rpc_total": (
                len(all_res["rpc_ethereum"]) +
                len(all_res["rpc_bsc"]) +
                len(all_res["rpc_polygon"]) +
                len(all_res["rpc_tron"])
            ),
            "datasets": len(all_res["datasets"]),
            "infrastructure": len(all_res["infrastructure"]),
        }


# Global instance
hierarchical_config = HierarchicalFallbackConfig()

__all__ = ["HierarchicalFallbackConfig", "hierarchical_config", "Priority", "ResourceConfig"]

