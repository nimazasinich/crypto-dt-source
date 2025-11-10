"""
Configuration Module for Crypto API Monitor
Loads and manages API registry from JSON files
"""

import json
import os
from typing import Dict, List, Any
from pathlib import Path

class Config:
    """Configuration manager for API resources"""

    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.resources = []
        self.categories = {}
        self.api_keys = {}
        self.cors_proxies = [
            'https://api.allorigins.win/get?url=',
            'https://proxy.cors.sh/',
            'https://proxy.corsfix.com/?url=',
            'https://api.codetabs.com/v1/proxy?quest=',
            'https://thingproxy.freeboard.io/fetch/'
        ]

        # Load environment variables for API keys
        self._load_env_keys()

        # Load API resources
        self._load_resources()

    def _load_env_keys(self):
        """Load API keys from environment variables"""
        self.api_keys = {
            'etherscan': os.getenv('ETHERSCAN_KEY', 'SZHYFZK2RR8H9TIMJBVW54V4H81K2Z2KR2'),
            'etherscan_backup': os.getenv('ETHERSCAN_BACKUP_KEY', 'T6IR8VJHX2NE6ZJW2S3FDVN1TYG4PYYI45'),
            'bscscan': os.getenv('BSCSCAN_KEY', 'K62RKHGXTDCG53RU4MCG6XABIMJKTN19IT'),
            'tronscan': os.getenv('TRONSCAN_KEY', '7ae72726-bffe-4e74-9c33-97b761eeea21'),
            'coinmarketcap': os.getenv('CMC_KEY', '04cf4b5b-9868-465c-8ba0-9f2e78c92eb1'),
            'coinmarketcap_backup': os.getenv('CMC_BACKUP_KEY', 'b54bcf4d-1bca-4e8e-9a24-22ff2c3d462c'),
            'cryptocompare': os.getenv('CRYPTOCOMPARE_KEY', 'e79c8e6d4c5b4a3f2e1d0c9b8a7f6e5d4c3b2a1f'),
            'newsapi': os.getenv('NEWSAPI_KEY', 'pub_346789abc123def456789ghi012345jkl'),
        }

    def _load_resources(self):
        """Load API resources from JSON files"""
        try:
            # Load from ultimate_crypto_pipeline_2025_NZasinich.json
            ultimate_path = self.base_dir / 'ultimate_crypto_pipeline_2025_NZasinich.json'
            if ultimate_path.exists():
                with open(ultimate_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Extract resources from the first file content
                    if 'files' in data and len(data['files']) > 0:
                        resources_data = data['files'][0].get('content', {}).get('resources', [])
                        self.resources.extend(resources_data)

            # Load from all_apis_merged_2025.json
            merged_path = self.base_dir / 'all_apis_merged_2025.json'
            if merged_path.exists():
                with open(merged_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    # Extract discovered keys
                    if 'discovered_keys' in data:
                        self._merge_discovered_keys(data['discovered_keys'])

            # Organize by category
            self._organize_by_category()

            # Add tier information
            self._add_tier_info()

        except Exception as e:
            print(f"Error loading resources: {e}")
            # Fallback to hardcoded minimal set
            self._load_fallback_resources()

    def _merge_discovered_keys(self, discovered_keys: Dict):
        """Merge discovered keys into resources"""
        for key, value in discovered_keys.items():
            if isinstance(value, str) and len(value) > 10:
                # Update API keys if not already set
                key_lower = key.lower()
                if 'etherscan' in key_lower and 'etherscan' not in self.api_keys:
                    self.api_keys['etherscan'] = value
                elif 'bscscan' in key_lower and 'bscscan' not in self.api_keys:
                    self.api_keys['bscscan'] = value
                elif 'tronscan' in key_lower and 'tronscan' not in self.api_keys:
                    self.api_keys['tronscan'] = value

    def _organize_by_category(self):
        """Organize resources by category"""
        for resource in self.resources:
            category = resource.get('category', 'Other')
            if category not in self.categories:
                self.categories[category] = []
            self.categories[category].append(resource)

    def _add_tier_info(self):
        """Add tier classification to resources"""
        # Tier 1: Critical, high-reliability APIs
        tier1_names = ['CoinGecko', 'Etherscan', 'BscScan', 'CoinPaprika', 'Blockscout']
        # Tier 2: Important, good reliability
        tier2_names = ['CryptoCompare', 'Coinpaprika', 'CoinMarketCap', 'TronScan']
        # Tier 3: Nice to have

        for resource in self.resources:
            name = resource.get('name', '')
            if any(t in name for t in tier1_names):
                resource['tier'] = 1
            elif any(t in name for t in tier2_names):
                resource['tier'] = 2
            else:
                resource['tier'] = 3

    def _load_fallback_resources(self):
        """Load minimal fallback resources if JSON loading fails"""
        self.resources = [
            {
                "category": "Market Data",
                "name": "CoinGecko (Free)",
                "url": "https://api.coingecko.com/api/v3",
                "key": "",
                "free": True,
                "rateLimit": "10-30/min",
                "desc": "Comprehensive crypto data",
                "endpoint": "/simple/price",
                "tier": 1
            },
            {
                "category": "Block Explorer",
                "name": "Blockscout (Free)",
                "url": "https://eth.blockscout.com/api",
                "key": "",
                "free": True,
                "rateLimit": "Unlimited",
                "desc": "Open-source explorer",
                "endpoint": "/v2/addresses/",
                "tier": 1
            }
        ]
        self._organize_by_category()

    def get_all_resources(self) -> List[Dict]:
        """Get all API resources"""
        return self.resources

    def get_by_category(self, category: str) -> List[Dict]:
        """Get resources by category"""
        return self.categories.get(category, [])

    def get_categories(self) -> List[str]:
        """Get all unique categories"""
        return list(self.categories.keys())

    def get_free_resources(self) -> List[Dict]:
        """Get only free resources"""
        return [r for r in self.resources if r.get('free', False)]

    def get_by_tier(self, tier: int) -> List[Dict]:
        """Get resources by tier"""
        return [r for r in self.resources if r.get('tier', 3) == tier]

    def get_cors_proxy(self, index: int = 0) -> str:
        """Get CORS proxy by index"""
        if 0 <= index < len(self.cors_proxies):
            return self.cors_proxies[index]
        return self.cors_proxies[0]

    def get_api_key(self, provider: str) -> str:
        """Get API key for a provider"""
        return self.api_keys.get(provider.lower(), '')

    def stats(self) -> Dict[str, Any]:
        """Get configuration statistics"""
        return {
            'total_resources': len(self.resources),
            'total_categories': len(self.categories),
            'free_resources': len(self.get_free_resources()),
            'tier1_count': len(self.get_by_tier(1)),
            'tier2_count': len(self.get_by_tier(2)),
            'tier3_count': len(self.get_by_tier(3)),
            'api_keys_count': len([k for k in self.api_keys.values() if k]),
            'cors_proxies_count': len(self.cors_proxies),
            'categories': list(self.categories.keys())
        }


# Global config instance
config = Config()
