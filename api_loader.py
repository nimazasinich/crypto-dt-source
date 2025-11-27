"""
API Configuration Loader
Loads all API sources from all_apis_merged_2025.json
"""

import json
import re
from typing import Dict, List, Any


class APILoader:
    def __init__(self, config_file="all_apis_merged_2025.json"):
        self.config_file = config_file
        self.apis = {}
        self.keys = {}
        self.cors_proxies = []
        self.load_config()

    def load_config(self):
        """Load and parse the comprehensive API configuration"""
        try:
            with open(self.config_file, "r", encoding="utf-8") as f:
                data = json.load(f)

            # Extract API keys from raw content
            self.extract_keys(data)

            # Extract CORS proxies
            self.extract_cors_proxies(data)

            # Build API registry
            self.build_api_registry(data)

            print(f"✓ Loaded {len(self.apis)} API sources")
            print(f"✓ Found {len(self.keys)} API keys")
            print(f"✓ Configured {len(self.cors_proxies)} CORS proxies")

        except Exception as e:
            print(f"✗ Error loading config: {e}")
            self.load_defaults()

    def extract_keys(self, data):
        """Extract API keys from configuration"""
        content = str(data)

        # Known key patterns
        key_patterns = {
            "TronScan": r"TronScan[:\s]+([a-f0-9-]{36})",
            "BscScan": r"BscScan[:\s]+([A-Z0-9]{34})",
            "Etherscan": r"Etherscan[:\s]+([A-Z0-9]{34})",
            "Etherscan_2": r"Etherscan_2[:\s]+([A-Z0-9]{34})",
            "CoinMarketCap": r"CoinMarketCap[:\s]+([a-f0-9-]{36})",
            "CoinMarketCap_2": r"CoinMarketCap_2[:\s]+([a-f0-9-]{36})",
            "CryptoCompare": r"CryptoCompare[:\s]+([a-f0-9]{40})",
        }

        for name, pattern in key_patterns.items():
            match = re.search(pattern, content)
            if match:
                self.keys[name] = match.group(1)

    def extract_cors_proxies(self, data):
        """Extract CORS proxy URLs"""
        self.cors_proxies = [
            "https://api.allorigins.win/get?url=",
            "https://proxy.cors.sh/",
            "https://proxy.corsfix.com/?url=",
            "https://api.codetabs.com/v1/proxy?quest=",
            "https://thingproxy.freeboard.io/fetch/",
        ]

    def build_api_registry(self, data):
        """Build comprehensive API registry"""

        # Market Data APIs
        self.apis["CoinGecko"] = {
            "name": "CoinGecko",
            "category": "market_data",
            "url": "https://api.coingecko.com/api/v3/ping",
            "test_field": "gecko_says",
            "key": None,
            "priority": 1,
        }

        self.apis["CoinGecko_Price"] = {
            "name": "CoinGecko Price",
            "category": "market_data",
            "url": "https://api.coingecko.com/api/v3/simple/price?ids=bitcoin&vs_currencies=usd",
            "test_field": "bitcoin",
            "key": None,
            "priority": 1,
        }

        self.apis["Binance"] = {
            "name": "Binance",
            "category": "market_data",
            "url": "https://api.binance.com/api/v3/ping",
            "test_field": None,
            "key": None,
            "priority": 1,
        }

        self.apis["Binance_Price"] = {
            "name": "Binance BTCUSDT",
            "category": "market_data",
            "url": "https://api.binance.com/api/v3/ticker/24hr?symbol=BTCUSDT",
            "test_field": "symbol",
            "key": None,
            "priority": 1,
        }

        self.apis["CoinCap"] = {
            "name": "CoinCap",
            "category": "market_data",
            "url": "https://api.coincap.io/v2/assets/bitcoin",
            "test_field": "data",
            "key": None,
            "priority": 2,
        }

        self.apis["Coinpaprika"] = {
            "name": "Coinpaprika",
            "category": "market_data",
            "url": "https://api.coinpaprika.com/v1/tickers/btc-bitcoin",
            "test_field": "id",
            "key": None,
            "priority": 2,
        }

        self.apis["CoinLore"] = {
            "name": "CoinLore",
            "category": "market_data",
            "url": "https://api.coinlore.net/api/ticker/?id=90",
            "test_field": None,
            "key": None,
            "priority": 2,
        }

        # Sentiment APIs
        self.apis["Alternative.me"] = {
            "name": "Alternative.me",
            "category": "sentiment",
            "url": "https://api.alternative.me/fng/",
            "test_field": "data",
            "key": None,
            "priority": 1,
        }

        # News APIs
        self.apis["CryptoPanic"] = {
            "name": "CryptoPanic",
            "category": "news",
            "url": "https://cryptopanic.com/api/v1/posts/?public=true",
            "test_field": "results",
            "key": None,
            "priority": 1,
        }

        self.apis["Reddit_Crypto"] = {
            "name": "Reddit Crypto",
            "category": "news",
            "url": "https://www.reddit.com/r/CryptoCurrency/hot.json?limit=5",
            "test_field": "data",
            "key": None,
            "priority": 2,
        }

        # Block Explorers (with keys)
        if "Etherscan" in self.keys:
            self.apis["Etherscan"] = {
                "name": "Etherscan",
                "category": "blockchain_explorers",
                "url": f'https://api.etherscan.io/api?module=stats&action=ethsupply&apikey={self.keys["Etherscan"]}',
                "test_field": "result",
                "key": self.keys["Etherscan"],
                "priority": 1,
            }

        if "BscScan" in self.keys:
            self.apis["BscScan"] = {
                "name": "BscScan",
                "category": "blockchain_explorers",
                "url": f'https://api.bscscan.com/api?module=stats&action=bnbsupply&apikey={self.keys["BscScan"]}',
                "test_field": "result",
                "key": self.keys["BscScan"],
                "priority": 1,
            }

        if "TronScan" in self.keys:
            self.apis["TronScan"] = {
                "name": "TronScan",
                "category": "blockchain_explorers",
                "url": "https://apilist.tronscanapi.com/api/system/status",
                "test_field": None,
                "key": self.keys["TronScan"],
                "priority": 1,
            }

        # Additional free APIs
        self.apis["Blockchair_BTC"] = {
            "name": "Blockchair Bitcoin",
            "category": "blockchain_explorers",
            "url": "https://api.blockchair.com/bitcoin/stats",
            "test_field": "data",
            "key": None,
            "priority": 2,
        }

        self.apis["Blockchain.info"] = {
            "name": "Blockchain.info",
            "category": "blockchain_explorers",
            "url": "https://blockchain.info/latestblock",
            "test_field": "height",
            "key": None,
            "priority": 2,
        }

        # RPC Nodes
        self.apis["Ankr_ETH"] = {
            "name": "Ankr Ethereum",
            "category": "rpc_nodes",
            "url": "https://rpc.ankr.com/eth",
            "test_field": None,
            "key": None,
            "priority": 2,
            "method": "POST",
        }

        self.apis["Cloudflare_ETH"] = {
            "name": "Cloudflare ETH",
            "category": "rpc_nodes",
            "url": "https://cloudflare-eth.com",
            "test_field": None,
            "key": None,
            "priority": 2,
            "method": "POST",
        }

        # DeFi APIs
        self.apis["1inch"] = {
            "name": "1inch",
            "category": "defi",
            "url": "https://api.1inch.io/v5.0/1/healthcheck",
            "test_field": None,
            "key": None,
            "priority": 2,
        }

        # Additional market data
        self.apis["Messari"] = {
            "name": "Messari",
            "category": "market_data",
            "url": "https://data.messari.io/api/v1/assets/bitcoin/metrics",
            "test_field": "data",
            "key": None,
            "priority": 2,
        }

        self.apis["CoinDesk"] = {
            "name": "CoinDesk",
            "category": "market_data",
            "url": "https://api.coindesk.com/v1/bpi/currentprice.json",
            "test_field": "bpi",
            "key": None,
            "priority": 2,
        }

    def load_defaults(self):
        """Load minimal default configuration if file loading fails"""
        self.apis = {
            "CoinGecko": {
                "name": "CoinGecko",
                "category": "market_data",
                "url": "https://api.coingecko.com/api/v3/ping",
                "test_field": "gecko_says",
                "key": None,
                "priority": 1,
            },
            "Binance": {
                "name": "Binance",
                "category": "market_data",
                "url": "https://api.binance.com/api/v3/ping",
                "test_field": None,
                "key": None,
                "priority": 1,
            },
        }

    def get_all_apis(self) -> Dict[str, Dict[str, Any]]:
        """Get all configured APIs"""
        return self.apis

    def get_apis_by_category(self, category: str) -> Dict[str, Dict[str, Any]]:
        """Get APIs filtered by category"""
        return {k: v for k, v in self.apis.items() if v["category"] == category}

    def get_categories(self) -> List[str]:
        """Get all unique categories"""
        return list(set(api["category"] for api in self.apis.values()))

    def add_custom_api(self, name: str, url: str, category: str, test_field: str = None):
        """Add a custom API source"""
        self.apis[name] = {
            "name": name,
            "category": category,
            "url": url,
            "test_field": test_field,
            "key": None,
            "priority": 3,
        }
        return True

    def remove_api(self, name: str):
        """Remove an API source"""
        if name in self.apis:
            del self.apis[name]
            return True
        return False


# Global instance
api_loader = APILoader()
