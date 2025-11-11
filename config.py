"""
Configuration Module for Crypto API Monitor
Loads and manages API registry from all_apis_merged_2025.json
"""

import json
import os
from pathlib import Path
from typing import Dict, List, Optional
from pydantic import BaseModel


class APIKey(BaseModel):
    provider: str
    key: str
    masked_key: str


class ProviderConfig(BaseModel):
    name: str
    category: str
    endpoint_url: str
    requires_key: bool
    api_key: Optional[str] = None
    rate_limit_type: str = "per_minute"
    rate_limit_value: int = 60
    timeout_ms: int = 10000
    priority_tier: int = 2


class Config:
    # Load JSON registry
    REGISTRY_PATH = Path(__file__).parent / "all_apis_merged_2025.json"

    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./crypto_monitor.db")

    # Server
    HOST = "0.0.0.0"
    PORT = int(os.getenv("PORT", 7860))

    # Security
    API_TOKENS = [token for token in os.getenv("API_TOKENS", "").split(",") if token]
    ALLOWED_IPS = [ip for ip in os.getenv("ALLOWED_IPS", "").split(",") if ip]

    # WebSocket
    WS_HEARTBEAT_INTERVAL = 30

    # Monitoring
    HEALTH_CHECK_INTERVAL = 300  # 5 minutes
    AUTO_REFRESH_ENABLED = True

    # API Keys (loaded from JSON)
    API_KEYS: Dict[str, List[str]] = {}
    PROVIDERS: List[ProviderConfig] = []

    @classmethod
    def load_registry(cls):
        """Load API registry from JSON file"""
        if not cls.REGISTRY_PATH.exists():
            raise FileNotFoundError(f"Registry file not found: {cls.REGISTRY_PATH}")

        with open(cls.REGISTRY_PATH, 'r') as f:
            data = json.load(f)

        # Parse discovered_keys
        discovered_keys = data.get("discovered_keys", {})
        cls.API_KEYS = {
            "etherscan": discovered_keys.get("etherscan", []),
            "bscscan": discovered_keys.get("bscscan", []),
            "tronscan": discovered_keys.get("tronscan", []),
            "coinmarketcap": discovered_keys.get("coinmarketcap", []),
            "newsapi": discovered_keys.get("newsapi", []),
            "cryptocompare": discovered_keys.get("cryptocompare", []),
            "huggingface": discovered_keys.get("huggingface", [])
        }

        # Build provider configurations
        cls._build_providers()

        return cls

    @classmethod
    def _build_providers(cls):
        """Build provider configurations from API keys"""
        # Market Data Providers
        cls.PROVIDERS.extend([
            ProviderConfig(
                name="CoinGecko",
                category="market_data",
                endpoint_url="https://api.coingecko.com/api/v3",
                requires_key=False,
                rate_limit_type="per_minute",
                rate_limit_value=50,
                priority_tier=1
            ),
            ProviderConfig(
                name="CoinMarketCap",
                category="market_data",
                endpoint_url="https://pro-api.coinmarketcap.com/v1",
                requires_key=True,
                api_key=cls.API_KEYS["coinmarketcap"][0] if cls.API_KEYS["coinmarketcap"] else None,
                rate_limit_type="per_hour",
                rate_limit_value=100,
                priority_tier=1
            ),
            ProviderConfig(
                name="CryptoCompare",
                category="market_data",
                endpoint_url="https://min-api.cryptocompare.com/data",
                requires_key=True,
                api_key=cls.API_KEYS["cryptocompare"][0] if cls.API_KEYS["cryptocompare"] else None,
                rate_limit_type="per_hour",
                rate_limit_value=100,
                priority_tier=2
            ),
            ProviderConfig(
                name="Binance",
                category="market_data",
                endpoint_url="https://api.binance.com/api/v3",
                requires_key=False,
                rate_limit_type="per_minute",
                rate_limit_value=1200,
                priority_tier=1
            ),
        ])

        # Blockchain Explorers
        cls.PROVIDERS.extend([
            ProviderConfig(
                name="Etherscan",
                category="blockchain_explorers",
                endpoint_url="https://api.etherscan.io/api",
                requires_key=True,
                api_key=cls.API_KEYS["etherscan"][0] if cls.API_KEYS["etherscan"] else None,
                rate_limit_type="per_day",
                rate_limit_value=100000,
                priority_tier=1
            ),
            ProviderConfig(
                name="BscScan",
                category="blockchain_explorers",
                endpoint_url="https://api.bscscan.com/api",
                requires_key=True,
                api_key=cls.API_KEYS["bscscan"][0] if cls.API_KEYS["bscscan"] else None,
                rate_limit_type="per_day",
                rate_limit_value=100000,
                priority_tier=1
            ),
            ProviderConfig(
                name="TronScan",
                category="blockchain_explorers",
                endpoint_url="https://apilist.tronscanapi.com/api",
                requires_key=True,
                api_key=cls.API_KEYS["tronscan"][0] if cls.API_KEYS["tronscan"] else None,
                rate_limit_type="per_day",
                rate_limit_value=100000,
                priority_tier=2
            ),
        ])

        # News & Sentiment
        cls.PROVIDERS.extend([
            ProviderConfig(
                name="CryptoPanic",
                category="news",
                endpoint_url="https://cryptopanic.com/api/v1",
                requires_key=False,
                rate_limit_type="per_hour",
                rate_limit_value=50,
                priority_tier=2
            ),
            ProviderConfig(
                name="NewsAPI",
                category="news",
                endpoint_url="https://newsdata.io/api/1",
                requires_key=True,
                api_key=cls.API_KEYS["newsapi"][0] if cls.API_KEYS["newsapi"] else None,
                rate_limit_type="per_day",
                rate_limit_value=200,
                priority_tier=2
            ),
            ProviderConfig(
                name="Alternative.me",
                category="sentiment",
                endpoint_url="https://api.alternative.me",
                requires_key=False,
                rate_limit_type="per_hour",
                rate_limit_value=20,
                priority_tier=2
            ),
        ])

        # On-chain Analytics
        cls.PROVIDERS.extend([
            ProviderConfig(
                name="The Graph",
                category="onchain_analytics",
                endpoint_url="https://api.thegraph.com/subgraphs/name",
                requires_key=False,
                rate_limit_type="per_minute",
                rate_limit_value=100,
                priority_tier=3
            ),
            ProviderConfig(
                name="Blockchair",
                category="onchain_analytics",
                endpoint_url="https://api.blockchair.com",
                requires_key=False,
                rate_limit_type="per_hour",
                rate_limit_value=1000,
                priority_tier=3
            ),
        ])


# Initialize configuration
config = Config.load_registry()
