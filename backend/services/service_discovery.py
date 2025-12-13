#!/usr/bin/env python3
"""
Service Discovery System
Auto-discovers ALL services used in the project by scanning files
"""

import os
import re
import json
import logging
from typing import Dict, List, Any, Optional, Set
from pathlib import Path
from dataclasses import dataclass, asdict
from enum import Enum

logger = logging.getLogger(__name__)


class ServiceCategory(str, Enum):
    """Service categories"""
    MARKET_DATA = "market_data"
    BLOCKCHAIN = "blockchain"
    NEWS_SENTIMENT = "news_sentiment"
    AI_SERVICES = "ai_services"
    INFRASTRUCTURE = "infrastructure"
    DEFI = "defi"
    SOCIAL = "social"
    EXCHANGES = "exchanges"
    TECHNICAL_ANALYSIS = "technical_analysis"
    INTERNAL_API = "internal_api"


@dataclass
class DiscoveredService:
    """Discovered service information"""
    id: str
    name: str
    category: ServiceCategory
    base_url: str
    endpoints: List[str]
    requires_auth: bool
    api_key_env: Optional[str]
    discovered_in: List[str]  # Files where this service was found
    features: List[str]
    priority: int = 2
    timeout: float = 10.0
    rate_limit: Optional[str] = None
    documentation_url: Optional[str] = None


class ServiceDiscovery:
    """Auto-discover all services used in the project"""
    
    def __init__(self, workspace_root: str = "/workspace"):
        self.workspace_root = Path(workspace_root)
        self.discovered_services: Dict[str, DiscoveredService] = {}
        self.url_patterns: Set[str] = set()
        
        # URL patterns to extract services
        self.url_regex = re.compile(r'https?://[^\s\'"<>]+')
        self.api_key_regex = re.compile(r'([A-Z_]+(?:_KEY|_TOKEN|_API_KEY))')
        
    def discover_all_services(self) -> Dict[str, DiscoveredService]:
        """
        Discover all services by scanning the project
        
        Returns:
            Dictionary of discovered services
        """
        logger.info("🔍 Starting comprehensive service discovery...")
        
        # Scan different file types
        self._scan_python_files()
        self._scan_javascript_files()
        self._scan_config_files()
        self._load_known_services()
        self._categorize_services()
        
        logger.info(f"✅ Discovered {len(self.discovered_services)} unique services")
        return self.discovered_services
    
    def _scan_python_files(self):
        """Scan Python files for API endpoints"""
        python_files = list(self.workspace_root.rglob("*.py"))
        logger.info(f"📂 Scanning {len(python_files)} Python files...")
        
        for py_file in python_files:
            # Skip virtual environments and cache
            if any(skip in str(py_file) for skip in ['.venv', 'venv', '__pycache__', '.git']):
                continue
                
            try:
                with open(py_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    self._extract_services_from_content(content, str(py_file.relative_to(self.workspace_root)))
            except Exception as e:
                logger.debug(f"Could not read {py_file}: {e}")
    
    def _scan_javascript_files(self):
        """Scan JavaScript files for API endpoints"""
        js_files = list(self.workspace_root.rglob("*.js"))
        logger.info(f"📂 Scanning {len(js_files)} JavaScript files...")
        
        for js_file in js_files:
            if any(skip in str(js_file) for skip in ['node_modules', '.git', 'dist', 'build']):
                continue
                
            try:
                with open(js_file, 'r', encoding='utf-8', errors='ignore') as f:
                    content = f.read()
                    self._extract_services_from_content(content, str(js_file.relative_to(self.workspace_root)))
            except Exception as e:
                logger.debug(f"Could not read {js_file}: {e}")
    
    def _scan_config_files(self):
        """Scan configuration files"""
        config_files = [
            self.workspace_root / "config.py",
            self.workspace_root / "config" / "api_keys.json",
            self.workspace_root / "config" / "service_registry.json",
        ]
        
        for config_file in config_files:
            if config_file.exists():
                try:
                    content = config_file.read_text(encoding='utf-8')
                    self._extract_services_from_content(content, str(config_file.relative_to(self.workspace_root)))
                except Exception as e:
                    logger.debug(f"Could not read {config_file}: {e}")
    
    def _extract_services_from_content(self, content: str, file_path: str):
        """Extract service URLs and API keys from file content"""
        # Find all URLs
        urls = self.url_regex.findall(content)
        
        for url in urls:
            # Clean URL
            url = url.rstrip('",\'>;)]')
            
            # Skip internal/local URLs
            if any(skip in url for skip in ['localhost', '127.0.0.1', '0.0.0.0', 'example.com']):
                continue
            
            # Skip documentation and repository URLs (unless they're APIs)
            if any(skip in url for skip in ['github.com', 'docs.', '/doc/', 'readme']) and '/api' not in url.lower():
                continue
            
            self.url_patterns.add(url)
            self._create_service_from_url(url, file_path)
    
    def _create_service_from_url(self, url: str, found_in: str):
        """Create a service entry from a URL"""
        # Extract base URL
        base_url_match = re.match(r'(https?://[^/]+)', url)
        if not base_url_match:
            return
        
        base_url = base_url_match.group(1)
        
        # Generate service ID from base URL
        service_id = base_url.replace('https://', '').replace('http://', '').replace('www.', '').replace('.', '_').replace('-', '_').split('/')[0]
        
        # Get or create service
        if service_id not in self.discovered_services:
            # Extract service name
            domain = base_url.replace('https://', '').replace('http://', '').replace('www.', '').split('/')[0]
            name = domain.split('.')[0].title()
            
            self.discovered_services[service_id] = DiscoveredService(
                id=service_id,
                name=name,
                category=ServiceCategory.INTERNAL_API,  # Will be categorized later
                base_url=base_url,
                endpoints=[],
                requires_auth=False,
                api_key_env=None,
                discovered_in=[],
                features=[]
            )
        
        # Add endpoint if different from base
        if url != base_url:
            endpoint = url.replace(base_url, '')
            if endpoint and endpoint not in self.discovered_services[service_id].endpoints:
                self.discovered_services[service_id].endpoints.append(endpoint)
        
        # Add file where it was found
        if found_in not in self.discovered_services[service_id].discovered_in:
            self.discovered_services[service_id].discovered_in.append(found_in)
    
    def _load_known_services(self):
        """Load and enhance with known service configurations"""
        known_services = {
            # Market Data
            "api_coingecko_com": {
                "name": "CoinGecko",
                "category": ServiceCategory.MARKET_DATA,
                "requires_auth": False,
                "features": ["prices", "market_data", "trending", "ohlcv"],
                "rate_limit": "10-50 req/min",
                "documentation_url": "https://www.coingecko.com/en/api/documentation"
            },
            "pro_api_coinmarketcap_com": {
                "name": "CoinMarketCap",
                "category": ServiceCategory.MARKET_DATA,
                "requires_auth": True,
                "api_key_env": "COINMARKETCAP_KEY",
                "features": ["prices", "rankings", "historical"],
                "rate_limit": "333 req/day free",
                "documentation_url": "https://coinmarketcap.com/api/documentation/v1/"
            },
            "api_coincap_io": {
                "name": "CoinCap",
                "category": ServiceCategory.MARKET_DATA,
                "requires_auth": False,
                "features": ["real-time", "prices", "historical"],
                "rate_limit": "200 req/min"
            },
            "api_binance_com": {
                "name": "Binance",
                "category": ServiceCategory.EXCHANGES,
                "requires_auth": False,
                "features": ["prices", "ohlcv", "orderbook", "trades"],
                "rate_limit": "1200 req/min"
            },
            "api_kucoin_com": {
                "name": "KuCoin",
                "category": ServiceCategory.EXCHANGES,
                "requires_auth": False,
                "features": ["prices", "ohlcv", "orderbook"],
                "rate_limit": "varies"
            },
            
            # Blockchain Explorers
            "api_etherscan_io": {
                "name": "Etherscan",
                "category": ServiceCategory.BLOCKCHAIN,
                "requires_auth": True,
                "api_key_env": "ETHERSCAN_KEY",
                "features": ["transactions", "tokens", "gas", "contracts"],
                "rate_limit": "5 req/sec"
            },
            "api_bscscan_com": {
                "name": "BscScan",
                "category": ServiceCategory.BLOCKCHAIN,
                "requires_auth": True,
                "api_key_env": "BSCSCAN_KEY",
                "features": ["transactions", "tokens", "gas"],
                "rate_limit": "5 req/sec"
            },
            "apilist_tronscanapi_com": {
                "name": "TronScan",
                "category": ServiceCategory.BLOCKCHAIN,
                "requires_auth": True,
                "api_key_env": "TRONSCAN_KEY",
                "features": ["transactions", "tokens", "trc20"],
                "rate_limit": "varies"
            },
            "api_blockchair_com": {
                "name": "Blockchair",
                "category": ServiceCategory.BLOCKCHAIN,
                "requires_auth": False,
                "features": ["multi-chain", "transactions", "blocks"],
                "rate_limit": "30 req/min"
            },
            
            # News & Sentiment
            "api_alternative_me": {
                "name": "Fear & Greed Index",
                "category": ServiceCategory.NEWS_SENTIMENT,
                "requires_auth": False,
                "features": ["sentiment", "fear_greed"],
                "rate_limit": "unlimited"
            },
            "newsapi_org": {
                "name": "NewsAPI",
                "category": ServiceCategory.NEWS_SENTIMENT,
                "requires_auth": True,
                "api_key_env": "NEWSAPI_KEY",
                "features": ["news", "headlines"],
                "rate_limit": "100 req/day free"
            },
            "cryptopanic_com": {
                "name": "CryptoPanic",
                "category": ServiceCategory.NEWS_SENTIMENT,
                "requires_auth": True,
                "api_key_env": "CRYPTOPANIC_KEY",
                "features": ["news", "sentiment"],
                "rate_limit": "5 req/sec"
            },
            "min_api_cryptocompare_com": {
                "name": "CryptoCompare",
                "category": ServiceCategory.MARKET_DATA,
                "requires_auth": False,
                "features": ["news", "prices", "historical"],
                "rate_limit": "100,000 req/month"
            },
            
            # Social
            "www_reddit_com": {
                "name": "Reddit",
                "category": ServiceCategory.SOCIAL,
                "requires_auth": False,
                "features": ["discussions", "sentiment"],
                "rate_limit": "60 req/min"
            },
            
            # DeFi
            "api_llama_fi": {
                "name": "DefiLlama",
                "category": ServiceCategory.DEFI,
                "requires_auth": False,
                "features": ["tvl", "protocols", "yields"],
                "rate_limit": "unlimited"
            },
            
            # RSS Feeds
            "www_coindesk_com": {
                "name": "CoinDesk RSS",
                "category": ServiceCategory.NEWS_SENTIMENT,
                "requires_auth": False,
                "features": ["news", "rss"],
                "rate_limit": "unlimited"
            },
            "cointelegraph_com": {
                "name": "Cointelegraph RSS",
                "category": ServiceCategory.NEWS_SENTIMENT,
                "requires_auth": False,
                "features": ["news", "rss"],
                "rate_limit": "unlimited"
            },
            "decrypt_co": {
                "name": "Decrypt RSS",
                "category": ServiceCategory.NEWS_SENTIMENT,
                "requires_auth": False,
                "features": ["news", "rss"],
                "rate_limit": "unlimited"
            },
            
            # Technical Analysis
            "api_taapi_io": {
                "name": "TAAPI",
                "category": ServiceCategory.TECHNICAL_ANALYSIS,
                "requires_auth": True,
                "api_key_env": "TAAPI_KEY",
                "features": ["indicators", "rsi", "macd"],
                "rate_limit": "varies"
            },
            
            # AI Services
            "api_inference_huggingface_co": {
                "name": "HuggingFace Inference",
                "category": ServiceCategory.AI_SERVICES,
                "requires_auth": True,
                "api_key_env": "HF_TOKEN",
                "features": ["ml_models", "inference"],
                "rate_limit": "varies"
            },
            "huggingface_co": {
                "name": "HuggingFace",
                "category": ServiceCategory.AI_SERVICES,
                "requires_auth": True,
                "api_key_env": "HF_TOKEN",
                "features": ["ml_models", "datasets"],
                "rate_limit": "varies"
            },
        }
        
        # Enhance discovered services with known information
        for service_id, known_info in known_services.items():
            if service_id in self.discovered_services:
                service = self.discovered_services[service_id]
                service.name = known_info.get("name", service.name)
                service.category = known_info.get("category", service.category)
                service.requires_auth = known_info.get("requires_auth", service.requires_auth)
                service.api_key_env = known_info.get("api_key_env", service.api_key_env)
                service.features = known_info.get("features", service.features)
                service.rate_limit = known_info.get("rate_limit", service.rate_limit)
                service.documentation_url = known_info.get("documentation_url", service.documentation_url)
    
    def _categorize_services(self):
        """Categorize services that weren't already categorized"""
        for service in self.discovered_services.values():
            if service.category == ServiceCategory.INTERNAL_API:
                # Try to categorize based on name or URL
                name_lower = service.name.lower()
                url_lower = service.base_url.lower()
                
                if any(kw in name_lower or kw in url_lower for kw in ['coin', 'market', 'price', 'crypto', 'ticker']):
                    service.category = ServiceCategory.MARKET_DATA
                elif any(kw in name_lower or kw in url_lower for kw in ['scan', 'explorer', 'blockchain', 'etherscan', 'bscscan']):
                    service.category = ServiceCategory.BLOCKCHAIN
                elif any(kw in name_lower or kw in url_lower for kw in ['news', 'rss', 'feed', 'sentiment', 'panic']):
                    service.category = ServiceCategory.NEWS_SENTIMENT
                elif any(kw in name_lower or kw in url_lower for kw in ['defi', 'llama', 'dex', 'swap']):
                    service.category = ServiceCategory.DEFI
                elif any(kw in name_lower or kw in url_lower for kw in ['reddit', 'twitter', 'social']):
                    service.category = ServiceCategory.SOCIAL
                elif any(kw in name_lower or kw in url_lower for kw in ['binance', 'kucoin', 'kraken', 'exchange']):
                    service.category = ServiceCategory.EXCHANGES
                elif any(kw in name_lower or kw in url_lower for kw in ['huggingface', 'model', 'inference']):
                    service.category = ServiceCategory.AI_SERVICES
    
    def get_services_by_category(self, category: ServiceCategory) -> List[DiscoveredService]:
        """Get services filtered by category"""
        return [s for s in self.discovered_services.values() if s.category == category]
    
    def get_all_services(self) -> List[DiscoveredService]:
        """Get all discovered services"""
        return list(self.discovered_services.values())
    
    def export_to_dict(self) -> Dict[str, Any]:
        """Export discovered services to dictionary"""
        return {
            "total_services": len(self.discovered_services),
            "categories": {
                category.value: len(self.get_services_by_category(category))
                for category in ServiceCategory
            },
            "services": [asdict(service) for service in self.discovered_services.values()]
        }
    
    def export_to_json(self, output_file: Optional[str] = None) -> str:
        """Export to JSON file or string"""
        data = self.export_to_dict()
        json_str = json.dumps(data, indent=2, default=str)
        
        if output_file:
            Path(output_file).write_text(json_str)
            logger.info(f"✅ Exported service discovery to {output_file}")
        
        return json_str


# Singleton instance
_discovery_instance: Optional[ServiceDiscovery] = None


def get_service_discovery() -> ServiceDiscovery:
    """Get or create singleton service discovery instance"""
    global _discovery_instance
    if _discovery_instance is None:
        _discovery_instance = ServiceDiscovery()
        _discovery_instance.discover_all_services()
    return _discovery_instance


# Internal API Services (local endpoints)
INTERNAL_SERVICES = [
    {
        "id": "local_api",
        "name": "Local API Server",
        "category": ServiceCategory.INFRASTRUCTURE,
        "base_url": "http://localhost:7860",
        "endpoints": [
            "/api/health",
            "/api/market",
            "/api/sentiment/global",
            "/api/news",
            "/api/providers",
            "/api/resources/stats",
            "/api/ohlcv",
            "/api/indicators/services",
            "/api/ai/decision",
            "/api/defi/protocols",
            "/docs",
            "/openapi.json"
        ],
        "requires_auth": False,
        "priority": 1,
        "features": ["rest_api", "websocket", "real-time"]
    },
    {
        "id": "database",
        "name": "SQLite Database",
        "category": ServiceCategory.INFRASTRUCTURE,
        "base_url": "sqlite:///./crypto_hub.db",
        "endpoints": [],
        "requires_auth": False,
        "priority": 1,
        "features": ["persistence", "cache", "state_management"]
    },
    {
        "id": "websocket",
        "name": "WebSocket Server",
        "category": ServiceCategory.INFRASTRUCTURE,
        "base_url": "ws://localhost:7860/ws",
        "endpoints": ["/ws"],
        "requires_auth": False,
        "priority": 1,
        "features": ["real-time", "push_notifications", "live_updates"]
    }
]


if __name__ == "__main__":
    # Test service discovery
    logging.basicConfig(level=logging.INFO)
    
    discovery = ServiceDiscovery()
    services = discovery.discover_all_services()
    
    print("\n" + "=" * 70)
    print("SERVICE DISCOVERY RESULTS")
    print("=" * 70)
    
    # Export to JSON
    json_output = discovery.export_to_json("/workspace/discovered_services.json")
    
    # Print summary
    print(f"\n✅ Total Services Discovered: {len(services)}")
    print("\nBy Category:")
    for category in ServiceCategory:
        count = len(discovery.get_services_by_category(category))
        if count > 0:
            print(f"  • {category.value}: {count}")
    
    print("\n" + "=" * 70)
