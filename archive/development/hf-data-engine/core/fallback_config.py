"""
Fallback Configuration Loader
Parses /mnt/data/api-config-complete.txt and extracts provider configurations
"""

import re
import logging
from typing import Dict, List, Any, Optional
from pathlib import Path
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


@dataclass
class ProviderConfig:
    """Provider configuration"""
    name: str
    base_url: str
    category: str
    key: Optional[str] = None
    header_key: Optional[str] = None
    needs_proxy: bool = False
    rate_limit: Optional[int] = None
    priority: int = 1
    capabilities: List[str] = field(default_factory=list)
    method: str = "GET"


@dataclass
class FallbackConfig:
    """Complete fallback configuration"""
    cors_proxies: List[str] = field(default_factory=list)
    market_data: List[ProviderConfig] = field(default_factory=list)
    explorers: Dict[str, List[ProviderConfig]] = field(default_factory=dict)
    news: List[ProviderConfig] = field(default_factory=list)
    sentiment: List[ProviderConfig] = field(default_factory=list)
    whale_tracking: List[ProviderConfig] = field(default_factory=list)
    rpc_nodes: Dict[str, List[str]] = field(default_factory=dict)
    
    
class FallbackConfigLoader:
    """Loads and parses fallback provider configuration"""
    
    def __init__(self, config_path: str = "/mnt/data/api-config-complete.txt"):
        self.config_path = config_path
        self.config = FallbackConfig()
        
    def load(self) -> FallbackConfig:
        """Load configuration from file"""
        try:
            path = Path(self.config_path)
            
            # Try multiple locations
            if not path.exists():
                # Try workspace location
                workspace_path = Path("/workspace/api-resources/api-config-complete__1_.txt")
                if workspace_path.exists():
                    path = workspace_path
                else:
                    logger.warning(f"Config file not found at {self.config_path}")
                    return self._get_default_config()
            
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self._parse_content(content)
            logger.info(f"Loaded fallback configuration from {path}")
            return self.config
            
        except Exception as e:
            logger.error(f"Error loading config: {e}")
            return self._get_default_config()
    
    def _parse_content(self, content: str):
        """Parse configuration file content"""
        # Parse CORS proxies
        cors_section = self._extract_section(content, "CORS PROXY SOLUTIONS")
        if cors_section:
            self.config.cors_proxies = self._parse_cors_proxies(cors_section)
        
        # Parse Market Data APIs
        market_section = self._extract_section(content, "MARKET DATA APIs")
        if market_section:
            self.config.market_data = self._parse_market_data(market_section)
        
        # Parse Block Explorer APIs
        explorer_section = self._extract_section(content, "BLOCK EXPLORER APIs")
        if explorer_section:
            self.config.explorers = self._parse_explorers(explorer_section)
        
        # Parse News APIs
        news_section = self._extract_section(content, "NEWS & SOCIAL APIs")
        if news_section:
            self.config.news = self._parse_news(news_section)
        
        # Parse Sentiment APIs
        sentiment_section = self._extract_section(content, "SENTIMENT & MOOD APIs")
        if sentiment_section:
            self.config.sentiment = self._parse_sentiment(sentiment_section)
        
        # Parse Whale Tracking APIs
        whale_section = self._extract_section(content, "WHALE TRACKING APIs")
        if whale_section:
            self.config.whale_tracking = self._parse_whale_tracking(whale_section)
        
        # Parse RPC Nodes
        rpc_section = self._extract_section(content, "RPC NODE PROVIDERS")
        if rpc_section:
            self.config.rpc_nodes = self._parse_rpc_nodes(rpc_section)
    
    def _extract_section(self, content: str, section_name: str) -> Optional[str]:
        """Extract a section from the config file"""
        pattern = rf"={{{3,}}\s*{re.escape(section_name)}.*?={{{3,}}"
        match = re.search(pattern, content, re.DOTALL | re.IGNORECASE)
        
        if match:
            start = match.end()
            # Find next major section
            next_section = re.search(r"={70,}", content[start:])
            if next_section:
                return content[start:start + next_section.start()]
            return content[start:]
        return None
    
    def _parse_cors_proxies(self, section: str) -> List[str]:
        """Parse CORS proxy URLs"""
        proxies = []
        
        # Look for URL patterns
        urls = [
            "https://api.allorigins.win/get?url=",
            "https://proxy.cors.sh/",
            "https://proxy.corsfix.com/?url=",
            "https://api.codetabs.com/v1/proxy?quest=",
            "https://thingproxy.freeboard.io/fetch/"
        ]
        
        for url in urls:
            if url in section:
                proxies.append(url)
        
        logger.info(f"Loaded {len(proxies)} CORS proxies")
        return proxies
    
    def _parse_market_data(self, section: str) -> List[ProviderConfig]:
        """Parse market data providers"""
        providers = []
        
        # CoinGecko (primary)
        if "coingecko" in section.lower():
            providers.append(ProviderConfig(
                name="coingecko",
                base_url="https://api.coingecko.com/api/v3",
                category="market_data",
                needs_proxy=False,
                rate_limit=50,
                priority=1,
                capabilities=["price", "market_cap", "volume", "trending"]
            ))
        
        # CoinMarketCap (with keys)
        cmc_keys = self._extract_api_keys(section, "CoinMarketCap")
        for i, key in enumerate(cmc_keys[:2]):
            providers.append(ProviderConfig(
                name=f"coinmarketcap_{i+1}",
                base_url="https://pro-api.coinmarketcap.com/v1",
                category="market_data",
                key=key,
                header_key="X-CMC_PRO_API_KEY",
                needs_proxy=True,
                rate_limit=333,
                priority=2 + i,
                capabilities=["price", "market_cap", "volume"]
            ))
        
        # CryptoCompare
        cc_key = self._extract_api_key(section, "CryptoCompare")
        if cc_key:
            providers.append(ProviderConfig(
                name="cryptocompare",
                base_url="https://min-api.cryptocompare.com/data",
                category="market_data",
                key=cc_key,
                needs_proxy=False,
                rate_limit=100000,
                priority=3,
                capabilities=["price", "historical"]
            ))
        
        # Free APIs
        free_providers = [
            ("coinpaprika", "https://api.coinpaprika.com/v1"),
            ("coincap", "https://api.coincap.io/v2"),
            ("binance", "https://api.binance.com/api/v3"),
            ("coinlore", "https://api.coinlore.net/api"),
        ]
        
        for i, (name, url) in enumerate(free_providers):
            if name in section.lower():
                providers.append(ProviderConfig(
                    name=name,
                    base_url=url,
                    category="market_data",
                    needs_proxy=False,
                    priority=4 + i,
                    capabilities=["price"]
                ))
        
        logger.info(f"Loaded {len(providers)} market data providers")
        return providers
    
    def _parse_explorers(self, section: str) -> Dict[str, List[ProviderConfig]]:
        """Parse blockchain explorer APIs"""
        explorers = {"ethereum": [], "bsc": [], "tron": []}
        
        # Ethereum - Etherscan
        eth_keys = self._extract_api_keys(section, "Etherscan")
        for i, key in enumerate(eth_keys[:2]):
            explorers["ethereum"].append(ProviderConfig(
                name=f"etherscan_{i+1}",
                base_url="https://api.etherscan.io/api",
                category="blockchain_explorer",
                key=key,
                needs_proxy=False,
                rate_limit=5,
                priority=1 + i,
                capabilities=["balance", "transactions", "gas"]
            ))
        
        # BSC - BscScan
        bsc_key = self._extract_api_key(section, "BscScan")
        if bsc_key:
            explorers["bsc"].append(ProviderConfig(
                name="bscscan",
                base_url="https://api.bscscan.com/api",
                category="blockchain_explorer",
                key=bsc_key,
                needs_proxy=False,
                rate_limit=5,
                priority=1,
                capabilities=["balance", "transactions"]
            ))
        
        # Tron - TronScan
        tron_key = self._extract_api_key(section, "TronScan")
        if tron_key:
            explorers["tron"].append(ProviderConfig(
                name="tronscan",
                base_url="https://apilist.tronscanapi.com/api",
                category="blockchain_explorer",
                key=tron_key,
                needs_proxy=False,
                priority=1,
                capabilities=["account", "transactions"]
            ))
        
        # Add free fallbacks
        explorers["ethereum"].append(ProviderConfig(
            name="blockchair_eth",
            base_url="https://api.blockchair.com/ethereum",
            category="blockchain_explorer",
            needs_proxy=False,
            priority=3,
            capabilities=["balance", "transactions"]
        ))
        
        logger.info(f"Loaded explorers: ETH={len(explorers['ethereum'])}, BSC={len(explorers['bsc'])}, TRON={len(explorers['tron'])}")
        return explorers
    
    def _parse_news(self, section: str) -> List[ProviderConfig]:
        """Parse news APIs"""
        providers = []
        
        # CryptoPanic (free)
        if "cryptopanic" in section.lower():
            providers.append(ProviderConfig(
                name="cryptopanic",
                base_url="https://cryptopanic.com/api/v1",
                category="news",
                needs_proxy=False,
                priority=1,
                capabilities=["news", "posts"]
            ))
        
        # Reddit
        if "reddit" in section.lower():
            providers.append(ProviderConfig(
                name="reddit_crypto",
                base_url="https://www.reddit.com/r/CryptoCurrency",
                category="news",
                needs_proxy=False,
                priority=2,
                capabilities=["posts"]
            ))
        
        logger.info(f"Loaded {len(providers)} news providers")
        return providers
    
    def _parse_sentiment(self, section: str) -> List[ProviderConfig]:
        """Parse sentiment APIs"""
        providers = []
        
        # Alternative.me (free)
        if "alternative.me" in section.lower():
            providers.append(ProviderConfig(
                name="alternative_me",
                base_url="https://api.alternative.me/fng",
                category="sentiment",
                needs_proxy=False,
                priority=1,
                capabilities=["fear_greed"]
            ))
        
        logger.info(f"Loaded {len(providers)} sentiment providers")
        return providers
    
    def _parse_whale_tracking(self, section: str) -> List[ProviderConfig]:
        """Parse whale tracking APIs"""
        providers = []
        
        # ClankApp (free)
        if "clankapp" in section.lower():
            providers.append(ProviderConfig(
                name="clankapp",
                base_url="https://clankapp.com/api",
                category="whale_tracking",
                needs_proxy=False,
                priority=1,
                capabilities=["whales", "transactions"]
            ))
        
        # BitQuery
        if "bitquery" in section.lower():
            providers.append(ProviderConfig(
                name="bitquery",
                base_url="https://graphql.bitquery.io",
                category="whale_tracking",
                needs_proxy=False,
                priority=2,
                method="POST",
                capabilities=["transfers", "large_transactions"]
            ))
        
        logger.info(f"Loaded {len(providers)} whale tracking providers")
        return providers
    
    def _parse_rpc_nodes(self, section: str) -> Dict[str, List[str]]:
        """Parse RPC node URLs"""
        nodes = {
            "ethereum": [],
            "bsc": [],
            "polygon": [],
            "tron": []
        }
        
        # Ethereum
        eth_rpcs = [
            "https://eth.llamarpc.com",
            "https://ethereum.publicnode.com",
            "https://cloudflare-eth.com",
            "https://rpc.ankr.com/eth"
        ]
        
        # BSC
        bsc_rpcs = [
            "https://bsc-dataseed.binance.org",
            "https://rpc.ankr.com/bsc",
            "https://bsc-rpc.publicnode.com"
        ]
        
        # Polygon
        polygon_rpcs = [
            "https://polygon-rpc.com",
            "https://rpc.ankr.com/polygon"
        ]
        
        # Tron
        tron_rpcs = [
            "https://api.trongrid.io",
            "https://api.tronstack.io"
        ]
        
        for url in eth_rpcs:
            if url in section:
                nodes["ethereum"].append(url)
        
        for url in bsc_rpcs:
            if url in section:
                nodes["bsc"].append(url)
        
        for url in polygon_rpcs:
            if url in section:
                nodes["polygon"].append(url)
        
        for url in tron_rpcs:
            if url in section:
                nodes["tron"].append(url)
        
        logger.info(f"Loaded RPC nodes: ETH={len(nodes['ethereum'])}, BSC={len(nodes['bsc'])}, POLYGON={len(nodes['polygon'])}")
        return nodes
    
    def _extract_api_keys(self, section: str, provider_name: str) -> List[str]:
        """Extract API keys for a provider"""
        keys = []
        
        # Pattern: provider_name: KEY
        # or provider_name_N: KEY
        pattern = rf"{re.escape(provider_name)}(?:_\d+)?:\s*([A-Za-z0-9\-]+)"
        matches = re.finditer(pattern, section, re.IGNORECASE)
        
        for match in matches:
            key = match.group(1).strip()
            if len(key) > 10:  # Valid key length
                keys.append(key)
        
        return keys
    
    def _extract_api_key(self, section: str, provider_name: str) -> Optional[str]:
        """Extract single API key"""
        keys = self._extract_api_keys(section, provider_name)
        return keys[0] if keys else None
    
    def _get_default_config(self) -> FallbackConfig:
        """Return default configuration if file is not available"""
        logger.info("Using default fallback configuration")
        
        config = FallbackConfig()
        
        # Default CORS proxies
        config.cors_proxies = [
            "https://api.allorigins.win/get?url=",
            "https://proxy.cors.sh/",
        ]
        
        # Default market data providers
        config.market_data = [
            ProviderConfig(
                name="coingecko",
                base_url="https://api.coingecko.com/api/v3",
                category="market_data",
                needs_proxy=False,
                priority=1,
                capabilities=["price", "market_cap"]
            ),
            ProviderConfig(
                name="binance",
                base_url="https://api.binance.com/api/v3",
                category="market_data",
                needs_proxy=False,
                priority=2,
                capabilities=["price"]
            ),
        ]
        
        # Default explorers
        config.explorers = {
            "ethereum": [
                ProviderConfig(
                    name="blockchair_eth",
                    base_url="https://api.blockchair.com/ethereum",
                    category="blockchain_explorer",
                    needs_proxy=False,
                    priority=1,
                    capabilities=["balance"]
                )
            ]
        }
        
        # Default news
        config.news = [
            ProviderConfig(
                name="cryptopanic",
                base_url="https://cryptopanic.com/api/v1",
                category="news",
                needs_proxy=False,
                priority=1
            )
        ]
        
        # Default sentiment
        config.sentiment = [
            ProviderConfig(
                name="alternative_me",
                base_url="https://api.alternative.me/fng",
                category="sentiment",
                needs_proxy=False,
                priority=1
            )
        ]
        
        return config


# Global loader instance
_loader = FallbackConfigLoader()
_config_cache: Optional[FallbackConfig] = None


def get_fallback_config() -> FallbackConfig:
    """Get cached fallback configuration"""
    global _config_cache
    
    if _config_cache is None:
        _config_cache = _loader.load()
    
    return _config_cache


def reload_fallback_config() -> FallbackConfig:
    """Reload fallback configuration from file"""
    global _config_cache
    _config_cache = _loader.load()
    return _config_cache
