"""
Configuration Module for Crypto API Monitor
Loads and manages API registry from all_apis_merged_2025.json
"""

import json
import os
from typing import Dict, List, Any, Optional
from pathlib import Path
from utils.logger import setup_logger

logger = setup_logger("config")


class ProviderConfig:
    """Provider configuration data class"""

    def __init__(
        self,
        name: str,
        category: str,
        endpoint_url: str,
        requires_key: bool = False,
        api_key: Optional[str] = None,
        rate_limit_type: Optional[str] = None,
        rate_limit_value: Optional[int] = None,
        timeout_ms: int = 10000,
        priority_tier: int = 3,
        health_check_endpoint: Optional[str] = None
    ):
        self.name = name
        self.category = category
        self.endpoint_url = endpoint_url
        self.requires_key = requires_key
        self.api_key = api_key
        self.rate_limit_type = rate_limit_type
        self.rate_limit_value = rate_limit_value
        self.timeout_ms = timeout_ms
        self.priority_tier = priority_tier
        self.health_check_endpoint = health_check_endpoint or endpoint_url

    def to_dict(self) -> Dict:
        """Convert to dictionary"""
        return {
            "name": self.name,
            "category": self.category,
            "endpoint_url": self.endpoint_url,
            "requires_key": self.requires_key,
            "api_key_masked": self._mask_key() if self.api_key else None,
            "rate_limit_type": self.rate_limit_type,
            "rate_limit_value": self.rate_limit_value,
            "timeout_ms": self.timeout_ms,
            "priority_tier": self.priority_tier,
            "health_check_endpoint": self.health_check_endpoint
        }

    def _mask_key(self) -> str:
        """Mask API key for security"""
        if not self.api_key:
            return None
        if len(self.api_key) < 10:
            return "***"
        return f"{self.api_key[:8]}...{self.api_key[-4:]}"


class Config:
    """Configuration manager for API resources"""

    def __init__(self, config_file: str = "all_apis_merged_2025.json"):
        """
        Initialize configuration

        Args:
            config_file: Path to JSON configuration file
        """
        self.base_dir = Path(__file__).parent
        self.config_file = self.base_dir / config_file
        self.providers: Dict[str, ProviderConfig] = {}
        self.api_keys: Dict[str, List[str]] = {}
        self.cors_proxies: List[str] = [
            'https://api.allorigins.win/get?url=',
            'https://proxy.cors.sh/',
            'https://proxy.corsfix.com/?url=',
            'https://api.codetabs.com/v1/proxy?quest=',
            'https://thingproxy.freeboard.io/fetch/'
        ]

        # Load environment variables
        self._load_env_keys()

        # Load from JSON
        self._load_from_json()

        # Build provider registry
        self._build_provider_registry()

    def _load_env_keys(self):
        """Load API keys from environment variables"""
        env_keys = {
            'etherscan': [
                os.getenv('ETHERSCAN_KEY_1', ''),
                os.getenv('ETHERSCAN_KEY_2', '')
            ],
            'bscscan': [os.getenv('BSCSCAN_KEY', '')],
            'tronscan': [os.getenv('TRONSCAN_KEY', '')],
            'coinmarketcap': [
                os.getenv('COINMARKETCAP_KEY_1', ''),
                os.getenv('COINMARKETCAP_KEY_2', '')
            ],
            'newsapi': [os.getenv('NEWSAPI_KEY', '')],
            'cryptocompare': [os.getenv('CRYPTOCOMPARE_KEY', '')],
            'huggingface': [os.getenv('HUGGINGFACE_KEY', '')]
        }

        # Filter out empty keys
        for provider, keys in env_keys.items():
            self.api_keys[provider] = [k for k in keys if k]

    def _load_from_json(self):
        """Load configuration from JSON file"""
        try:
            if not self.config_file.exists():
                logger.warning(f"Config file not found: {self.config_file}")
                return

            with open(self.config_file, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Load discovered keys
            discovered_keys = data.get('discovered_keys', {})
            for provider, keys in discovered_keys.items():
                if isinstance(keys, list):
                    # Merge with env keys, preferring env keys
                    if provider not in self.api_keys or not self.api_keys[provider]:
                        self.api_keys[provider] = keys
                    else:
                        # Add discovered keys that aren't in env
                        for key in keys:
                            if key not in self.api_keys[provider]:
                                self.api_keys[provider].append(key)

            logger.info(f"Loaded {len(self.api_keys)} provider keys from config")

        except Exception as e:
            logger.error(f"Error loading config file: {e}")

    def _build_provider_registry(self):
        """Build provider registry from configuration"""

        # Market Data Providers
        self.providers['CoinGecko'] = ProviderConfig(
            name='CoinGecko',
            category='market_data',
            endpoint_url='https://api.coingecko.com/api/v3',
            requires_key=False,
            rate_limit_type='per_minute',
            rate_limit_value=50,
            timeout_ms=10000,
            priority_tier=1,
            health_check_endpoint='https://api.coingecko.com/api/v3/ping'
        )

        # CoinMarketCap
        cmc_keys = self.api_keys.get('coinmarketcap', [])
        self.providers['CoinMarketCap'] = ProviderConfig(
            name='CoinMarketCap',
            category='market_data',
            endpoint_url='https://pro-api.coinmarketcap.com/v1',
            requires_key=True,
            api_key=cmc_keys[0] if cmc_keys else None,
            rate_limit_type='per_hour',
            rate_limit_value=100,
            timeout_ms=10000,
            priority_tier=2,
            health_check_endpoint='https://pro-api.coinmarketcap.com/v1/cryptocurrency/map?limit=1'
        )

        # Blockchain Explorers
        etherscan_keys = self.api_keys.get('etherscan', [])
        self.providers['Etherscan'] = ProviderConfig(
            name='Etherscan',
            category='blockchain_explorers',
            endpoint_url='https://api.etherscan.io/api',
            requires_key=True,
            api_key=etherscan_keys[0] if etherscan_keys else None,
            rate_limit_type='per_second',
            rate_limit_value=5,
            timeout_ms=10000,
            priority_tier=1,
            health_check_endpoint='https://api.etherscan.io/api?module=stats&action=ethsupply'
        )

        bscscan_keys = self.api_keys.get('bscscan', [])
        self.providers['BscScan'] = ProviderConfig(
            name='BscScan',
            category='blockchain_explorers',
            endpoint_url='https://api.bscscan.com/api',
            requires_key=True,
            api_key=bscscan_keys[0] if bscscan_keys else None,
            rate_limit_type='per_second',
            rate_limit_value=5,
            timeout_ms=10000,
            priority_tier=1,
            health_check_endpoint='https://api.bscscan.com/api?module=stats&action=bnbsupply'
        )

        tronscan_keys = self.api_keys.get('tronscan', [])
        self.providers['TronScan'] = ProviderConfig(
            name='TronScan',
            category='blockchain_explorers',
            endpoint_url='https://apilist.tronscanapi.com/api',
            requires_key=True,
            api_key=tronscan_keys[0] if tronscan_keys else None,
            rate_limit_type='per_minute',
            rate_limit_value=60,
            timeout_ms=10000,
            priority_tier=2,
            health_check_endpoint='https://apilist.tronscanapi.com/api/system/status'
        )

        # News APIs
        self.providers['CryptoPanic'] = ProviderConfig(
            name='CryptoPanic',
            category='news',
            endpoint_url='https://cryptopanic.com/api/v1',
            requires_key=False,
            rate_limit_type='per_hour',
            rate_limit_value=100,
            timeout_ms=10000,
            priority_tier=2,
            health_check_endpoint='https://cryptopanic.com/api/v1/posts/?auth_token=free&public=true'
        )

        newsapi_keys = self.api_keys.get('newsapi', [])
        self.providers['NewsAPI'] = ProviderConfig(
            name='NewsAPI',
            category='news',
            endpoint_url='https://newsdata.io/api/1',
            requires_key=True,
            api_key=newsapi_keys[0] if newsapi_keys else None,
            rate_limit_type='per_day',
            rate_limit_value=200,
            timeout_ms=10000,
            priority_tier=3,
            health_check_endpoint='https://newsdata.io/api/1/news?category=business'
        )

        # Sentiment APIs
        self.providers['AlternativeMe'] = ProviderConfig(
            name='AlternativeMe',
            category='sentiment',
            endpoint_url='https://api.alternative.me',
            requires_key=False,
            rate_limit_type='per_minute',
            rate_limit_value=60,
            timeout_ms=10000,
            priority_tier=2,
            health_check_endpoint='https://api.alternative.me/fng/'
        )

        # CryptoCompare
        cryptocompare_keys = self.api_keys.get('cryptocompare', [])
        self.providers['CryptoCompare'] = ProviderConfig(
            name='CryptoCompare',
            category='market_data',
            endpoint_url='https://min-api.cryptocompare.com/data',
            requires_key=True,
            api_key=cryptocompare_keys[0] if cryptocompare_keys else None,
            rate_limit_type='per_hour',
            rate_limit_value=250,
            timeout_ms=10000,
            priority_tier=2,
            health_check_endpoint='https://min-api.cryptocompare.com/data/price?fsym=BTC&tsyms=USD'
        )

        logger.info(f"Built provider registry with {len(self.providers)} providers")

    def get_provider(self, name: str) -> Optional[ProviderConfig]:
        """Get provider configuration by name"""
        return self.providers.get(name)

    def get_all_providers(self) -> List[ProviderConfig]:
        """Get all provider configurations"""
        return list(self.providers.values())

    def get_providers_by_category(self, category: str) -> List[ProviderConfig]:
        """Get providers by category"""
        return [p for p in self.providers.values() if p.category == category]

    def get_providers_by_tier(self, tier: int) -> List[ProviderConfig]:
        """Get providers by priority tier"""
        return [p for p in self.providers.values() if p.priority_tier == tier]

    def get_api_key(self, provider: str, index: int = 0) -> Optional[str]:
        """Get API key for provider"""
        keys = self.api_keys.get(provider.lower(), [])
        if keys and 0 <= index < len(keys):
            return keys[index]
        return None

    def get_categories(self) -> List[str]:
        """Get all unique categories"""
        return list(set(p.category for p in self.providers.values()))

    def stats(self) -> Dict[str, Any]:
        """Get configuration statistics"""
        return {
            'total_providers': len(self.providers),
            'categories': len(self.get_categories()),
            'providers_with_keys': sum(1 for p in self.providers.values() if p.requires_key),
            'tier1_count': len(self.get_providers_by_tier(1)),
            'tier2_count': len(self.get_providers_by_tier(2)),
            'tier3_count': len(self.get_providers_by_tier(3)),
            'api_keys_loaded': len(self.api_keys),
            'categories_list': self.get_categories()
        }


# Global config instance
config = Config()
