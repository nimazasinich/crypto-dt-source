#!/usr/bin/env python3
"""
Configuration constants for Crypto Data Aggregator
All configuration in one place - no hardcoded values
"""

import os
import json
import base64
import logging
from functools import lru_cache
from pathlib import Path
from typing import Dict, Any, List, Optional
from dataclasses import dataclass

# ==================== DIRECTORIES ====================
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR / "data"
LOG_DIR = BASE_DIR / "logs"
DB_DIR = DATA_DIR / "database"

# Create directories if they don't exist
for directory in [DATA_DIR, LOG_DIR, DB_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

logger = logging.getLogger(__name__)


# ==================== PROVIDER CONFIGURATION ====================


@dataclass
class ProviderConfig:
    """Configuration for an API provider"""

    name: str
    endpoint_url: str
    category: str = "market_data"
    requires_key: bool = False
    api_key: Optional[str] = None
    timeout_ms: int = 10000
    rate_limit_type: Optional[str] = None
    rate_limit_value: Optional[int] = None
    health_check_endpoint: Optional[str] = None

    def __post_init__(self):
        if self.health_check_endpoint is None:
            self.health_check_endpoint = self.endpoint_url


@dataclass
class Settings:
    """Runtime configuration loaded from environment variables."""

    hf_token: Optional[str] = None
    hf_token_encoded: Optional[str] = None
    cmc_api_key: Optional[str] = None
    etherscan_key: Optional[str] = None
    newsapi_key: Optional[str] = None
    log_level: str = "INFO"
    database_path: Path = DB_DIR / "crypto_aggregator.db"
    redis_url: Optional[str] = None
    cache_ttl: int = 300
    user_agent: str = "CryptoDashboard/1.0"
    providers_config_path: Path = BASE_DIR / "providers_config_extended.json"


def _decode_token(value: Optional[str]) -> Optional[str]:
    """Decode a base64 encoded Hugging Face token."""

    if not value:
        return None

    try:
        decoded = base64.b64decode(value).decode("utf-8").strip()
        return decoded or None
    except Exception as exc:  # pragma: no cover - defensive logging
        logger.warning("Failed to decode HF token: %s", exc)
        return None


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return cached runtime settings."""

    raw_token = os.environ.get("HF_TOKEN")
    encoded_token = os.environ.get("HF_TOKEN_ENCODED")
    decoded_token = raw_token or _decode_token(encoded_token)

    database_path = Path(os.environ.get("DATABASE_PATH", str(DB_DIR / "crypto_aggregator.db")))

    settings = Settings(
        hf_token=decoded_token,
        hf_token_encoded=encoded_token,
        cmc_api_key=os.environ.get("CMC_API_KEY"),
        etherscan_key=os.environ.get("ETHERSCAN_KEY"),
        newsapi_key=os.environ.get("NEWSAPI_KEY"),
        log_level=os.environ.get("LOG_LEVEL", "INFO").upper(),
        database_path=database_path,
        redis_url=os.environ.get("REDIS_URL"),
        cache_ttl=int(os.environ.get("CACHE_TTL", "300")),
        user_agent=os.environ.get("USER_AGENT", "CryptoDashboard/1.0"),
        providers_config_path=Path(
            os.environ.get("PROVIDERS_CONFIG_PATH", str(BASE_DIR / "providers_config_extended.json"))
        ),
    )

    return settings


class ConfigManager:
    """Configuration manager for API providers"""
    
    def __init__(self):
        self.providers: Dict[str, ProviderConfig] = {}
        self._load_default_providers()
        self._load_env_keys()
    
    def _load_default_providers(self):
        """Load default provider configurations"""
        # CoinGecko (Free, no key)
        self.providers["CoinGecko"] = ProviderConfig(
            name="CoinGecko",
            endpoint_url="https://api.coingecko.com/api/v3",
            category="market_data",
            requires_key=False,
            timeout_ms=10000
        )
        
        # CoinMarketCap (Requires API key)
        self.providers["CoinMarketCap"] = ProviderConfig(
            name="CoinMarketCap",
            endpoint_url="https://pro-api.coinmarketcap.com/v1",
            category="market_data",
            requires_key=True,
            timeout_ms=10000
        )
        
        # Binance (Free, no key)
        self.providers["Binance"] = ProviderConfig(
            name="Binance",
            endpoint_url="https://api.binance.com/api/v3",
            category="market_data",
            requires_key=False,
            timeout_ms=10000
        )
        
        # Etherscan (Requires API key)
        self.providers["Etherscan"] = ProviderConfig(
            name="Etherscan",
            endpoint_url="https://api.etherscan.io/api",
            category="blockchain_explorers",
            requires_key=True,
            timeout_ms=10000
        )
        
        # BscScan (Requires API key)
        self.providers["BscScan"] = ProviderConfig(
            name="BscScan",
            endpoint_url="https://api.bscscan.com/api",
            category="blockchain_explorers",
            requires_key=True,
            timeout_ms=10000
        )
        
        # TronScan (Requires API key)
        self.providers["TronScan"] = ProviderConfig(
            name="TronScan",
            endpoint_url="https://apilist.tronscan.org/api",
            category="blockchain_explorers",
            requires_key=True,
            timeout_ms=10000
        )
        
        # CryptoPanic (Requires API key)
        self.providers["CryptoPanic"] = ProviderConfig(
            name="CryptoPanic",
            endpoint_url="https://cryptopanic.com/api/v1",
            category="news",
            requires_key=True,
            timeout_ms=10000
        )
        
        # NewsAPI (Requires API key)
        self.providers["NewsAPI"] = ProviderConfig(
            name="NewsAPI",
            endpoint_url="https://newsapi.org/v2",
            category="news",
            requires_key=True,
            timeout_ms=10000
        )
        
        # Alternative.me Fear & Greed Index (Free, no key)
        self.providers["Alternative.me"] = ProviderConfig(
            name="Alternative.me",
            endpoint_url="https://api.alternative.me",
            category="sentiment",
            requires_key=False,
            timeout_ms=10000
        )
    
    def _load_env_keys(self):
        """Load API keys from environment variables"""
        key_mapping = {
            "CoinMarketCap": "CMC_API_KEY",
            "Etherscan": "ETHERSCAN_KEY",
            "BscScan": "BSCSCAN_KEY",
            "TronScan": "TRONSCAN_KEY",
            "CryptoPanic": "CRYPTOPANIC_KEY",
            "NewsAPI": "NEWSAPI_KEY",
        }
        
        for provider_name, env_var in key_mapping.items():
            if provider_name in self.providers:
                api_key = os.environ.get(env_var)
                if api_key:
                    self.providers[provider_name].api_key = api_key
    
    def get_provider(self, provider_name: str) -> Optional[ProviderConfig]:
        """Get provider configuration by name"""
        return self.providers.get(provider_name)
    
    def get_all_providers(self) -> List[ProviderConfig]:
        """Get all provider configurations"""
        return list(self.providers.values())
    
    def get_providers_by_category(self, category: str) -> List[ProviderConfig]:
        """Get providers filtered by category"""
        return [p for p in self.providers.values() if p.category == category]
    
    def get_categories(self) -> List[str]:
        """Get all unique categories"""
        return list(set(p.category for p in self.providers.values()))
    
    def add_provider(self, provider: ProviderConfig):
        """Add a new provider configuration"""
        self.providers[provider.name] = provider
    
    def stats(self) -> Dict[str, Any]:
        """Get configuration statistics"""
        providers_list = list(self.providers.values())
        return {
            'total_resources': len(providers_list),
            'total_categories': len(self.get_categories()),
            'free_resources': sum(1 for p in providers_list if not p.requires_key),
            'tier1_count': 0,  # Placeholder for tier support
            'tier2_count': 0,
            'tier3_count': len(providers_list),
            'api_keys_count': sum(1 for p in providers_list if p.api_key),
            'cors_proxies_count': 0,
            'categories': self.get_categories()
        }
    
    def get_by_tier(self, tier: int) -> List[Dict[str, Any]]:
        """Get resources by tier (placeholder for compatibility)"""
        # Return all providers for now
        return [{'name': p.name} for p in self.providers.values()]
    
    def get_all_resources(self) -> List[Dict[str, Any]]:
        """Get all resources in dictionary format (for compatibility)"""
        return [
            {
                'name': p.name,
                'endpoint': p.endpoint_url,
                'url': p.endpoint_url,
                'category': p.category,
                'requires_key': p.requires_key,
                'api_key': p.api_key,
                'timeout': p.timeout_ms,
            }
            for p in self.providers.values()
        ]


# Create global config instance
config = ConfigManager()

# Runtime settings loaded from environment
settings = get_settings()

# ==================== DATABASE ====================
DATABASE_PATH = Path(settings.database_path)
DATABASE_BACKUP_DIR = DATA_DIR / "backups"
DATABASE_BACKUP_DIR.mkdir(parents=True, exist_ok=True)

# ==================== API ENDPOINTS (NO KEYS REQUIRED) ====================

# CoinGecko API (Free, no key)
COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"
COINGECKO_ENDPOINTS = {
    "ping": "/ping",
    "price": "/simple/price",
    "coins_list": "/coins/list",
    "coins_markets": "/coins/markets",
    "coin_data": "/coins/{id}",
    "trending": "/search/trending",
    "global": "/global",
}

# CoinCap API (Free, no key)
COINCAP_BASE_URL = "https://api.coincap.io/v2"
COINCAP_ENDPOINTS = {
    "assets": "/assets",
    "asset_detail": "/assets/{id}",
    "asset_history": "/assets/{id}/history",
    "markets": "/markets",
    "rates": "/rates",
}

# Binance Public API (Free, no key)
BINANCE_BASE_URL = "https://api.binance.com/api/v3"
BINANCE_ENDPOINTS = {
    "ping": "/ping",
    "ticker_24h": "/ticker/24hr",
    "ticker_price": "/ticker/price",
    "klines": "/klines",
    "trades": "/trades",
}

# Alternative.me Fear & Greed Index (Free, no key)
ALTERNATIVE_ME_URL = "https://api.alternative.me/fng/"

# ==================== RSS FEEDS ====================
RSS_FEEDS = {
    "coindesk": "https://www.coindesk.com/arc/outboundfeeds/rss/",
    "cointelegraph": "https://cointelegraph.com/rss",
    "bitcoin_magazine": "https://bitcoinmagazine.com/.rss/full/",
    "decrypt": "https://decrypt.co/feed",
    "bitcoinist": "https://bitcoinist.com/feed/",
}

# ==================== REDDIT ENDPOINTS (NO AUTH) ====================
REDDIT_ENDPOINTS = {
    "cryptocurrency": "https://www.reddit.com/r/cryptocurrency/.json",
    "bitcoin": "https://www.reddit.com/r/bitcoin/.json",
    "ethtrader": "https://www.reddit.com/r/ethtrader/.json",
    "cryptomarkets": "https://www.reddit.com/r/CryptoMarkets/.json",
}

# ==================== HUGGING FACE MODELS ====================
HUGGINGFACE_MODELS = {
    "sentiment_twitter": "cardiffnlp/twitter-roberta-base-sentiment-latest",
    "sentiment_financial": "ProsusAI/finbert",
    "summarization": "facebook/bart-large-cnn",
    "crypto_sentiment": "ElKulako/CryptoBERT",  # Requires authentication
}

# Hugging Face Authentication
HF_TOKEN = settings.hf_token or ""
HF_USE_AUTH_TOKEN = bool(HF_TOKEN)

# ==================== DATA COLLECTION SETTINGS ====================
COLLECTION_INTERVALS = {
    "price_data": 300,  # 5 minutes in seconds
    "news_data": 1800,  # 30 minutes in seconds
    "sentiment_data": 1800,  # 30 minutes in seconds
}

# Number of top cryptocurrencies to track
TOP_COINS_LIMIT = 100

# Request timeout in seconds
REQUEST_TIMEOUT = 10

# Max retries for failed requests
MAX_RETRIES = 3

# ==================== CACHE SETTINGS ====================
CACHE_TTL = settings.cache_ttl or 300  # 5 minutes in seconds
CACHE_MAX_SIZE = 1000  # Maximum number of cached items

# ==================== LOGGING SETTINGS ====================
LOG_FILE = LOG_DIR / "crypto_aggregator.log"
LOG_LEVEL = settings.log_level
LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
LOG_MAX_BYTES = 10 * 1024 * 1024  # 10 MB
LOG_BACKUP_COUNT = 5

# ==================== GRADIO SETTINGS ====================
GRADIO_SHARE = False
GRADIO_SERVER_NAME = "0.0.0.0"
GRADIO_SERVER_PORT = 7860
GRADIO_THEME = "default"
AUTO_REFRESH_INTERVAL = 30  # seconds

# ==================== DATA VALIDATION ====================
MIN_PRICE = 0.0
MAX_PRICE = 1000000000.0  # 1 billion
MIN_VOLUME = 0.0
MIN_MARKET_CAP = 0.0

# ==================== CHART SETTINGS ====================
CHART_TIMEFRAMES = {
    "1d": {"days": 1, "interval": "1h"},
    "7d": {"days": 7, "interval": "4h"},
    "30d": {"days": 30, "interval": "1d"},
    "90d": {"days": 90, "interval": "1d"},
    "1y": {"days": 365, "interval": "1w"},
}

# Technical indicators
MA_PERIODS = [7, 30]  # Moving Average periods
RSI_PERIOD = 14  # RSI period

# ==================== SENTIMENT THRESHOLDS ====================
SENTIMENT_LABELS = {
    "very_negative": (-1.0, -0.6),
    "negative": (-0.6, -0.2),
    "neutral": (-0.2, 0.2),
    "positive": (0.2, 0.6),
    "very_positive": (0.6, 1.0),
}

# ==================== AI ANALYSIS SETTINGS ====================
AI_CONFIDENCE_THRESHOLD = 0.6
PREDICTION_HORIZON_HOURS = 72

# ==================== USER AGENT ====================
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"

# ==================== RATE LIMITING ====================
RATE_LIMIT_CALLS = 50
RATE_LIMIT_PERIOD = 60  # seconds

# ==================== COIN SYMBOLS ====================
# Top cryptocurrencies to focus on
FOCUS_COINS = [
    "bitcoin", "ethereum", "binancecoin", "ripple", "cardano",
    "solana", "polkadot", "dogecoin", "avalanche-2", "polygon",
    "chainlink", "uniswap", "litecoin", "cosmos", "algorand"
]

COIN_SYMBOL_MAPPING = {
    "bitcoin": "BTC",
    "ethereum": "ETH",
    "binancecoin": "BNB",
    "ripple": "XRP",
    "cardano": "ADA",
    "solana": "SOL",
    "polkadot": "DOT",
    "dogecoin": "DOGE",
    "avalanche-2": "AVAX",
    "polygon": "MATIC",
}

# ==================== ERROR MESSAGES ====================
ERROR_MESSAGES = {
    "api_unavailable": "API service is currently unavailable. Using cached data.",
    "no_data": "No data available at the moment.",
    "database_error": "Database operation failed.",
    "network_error": "Network connection error.",
    "invalid_input": "Invalid input provided.",
}

# ==================== SUCCESS MESSAGES ====================
SUCCESS_MESSAGES = {
    "data_collected": "Data successfully collected and saved.",
    "cache_cleared": "Cache cleared successfully.",
    "database_initialized": "Database initialized successfully.",
}
