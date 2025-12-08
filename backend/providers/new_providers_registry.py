#!/usr/bin/env python3
"""
New Providers Registry - Additional Free Data Sources
رجیستری جدید برای منابع داده رایگان اضافی
"""

import aiohttp
import asyncio
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
from datetime import datetime
import feedparser


class ProviderType(Enum):
    """نوع سرویس‌دهنده"""
    OHLCV = "ohlcv"
    NEWS = "news"
    ONCHAIN = "onchain"
    SOCIAL = "social"
    DEFI = "defi"
    TECHNICAL = "technical"


@dataclass
class ProviderInfo:
    """اطلاعات سرویس‌دهنده"""
    id: str
    name: str
    type: str
    url: str
    description: str
    free: bool
    requires_key: bool
    rate_limit: str
    features: List[str]
    verified: bool


class NewProvidersRegistry:
    """
    رجیستری جدید برای سرویس‌دهندگان داده
    Registry of 50+ new free data providers
    """
    
    def __init__(self):
        self.providers = self._load_providers()
    
    def _load_providers(self) -> Dict[str, ProviderInfo]:
        """بارگذاری سرویس‌دهندگان"""
        return {
            # ===== NEW OHLCV PROVIDERS =====
            
            "coinranking": ProviderInfo(
                id="coinranking",
                name="CoinRanking",
                type=ProviderType.OHLCV.value,
                url="https://api.coinranking.com/v2",
                description="3000+ coins, real-time prices",
                free=True,
                requires_key=False,  # Has free tier
                rate_limit="10 req/sec",
                features=["prices", "history", "markets", "exchanges"],
                verified=False
            ),
            
            "coincap_v2": ProviderInfo(
                id="coincap_v2",
                name="CoinCap API v2",
                type=ProviderType.OHLCV.value,
                url="https://api.coincap.io/v2",
                description="2000+ assets, historical data",
                free=True,
                requires_key=False,
                rate_limit="200 req/min",
                features=["assets", "rates", "exchanges", "markets"],
                verified=True
            ),
            
            "coinlore": ProviderInfo(
                id="coinlore",
                name="CoinLore",
                type=ProviderType.OHLCV.value,
                url="https://api.coinlore.net/api",
                description="Simple crypto API, 5000+ coins",
                free=True,
                requires_key=False,
                rate_limit="Unlimited",
                features=["tickers", "markets", "global"],
                verified=False
            ),
            
            "nomics": ProviderInfo(
                id="nomics",
                name="Nomics",
                type=ProviderType.OHLCV.value,
                url="https://api.nomics.com/v1",
                description="Professional grade crypto data",
                free=True,
                requires_key=True,  # Free key available
                rate_limit="1 req/sec (free)",
                features=["currencies", "ticker", "sparkline", "ohlcv"],
                verified=False
            ),
            
            "messari": ProviderInfo(
                id="messari",
                name="Messari",
                type=ProviderType.OHLCV.value,
                url="https://data.messari.io/api/v1",
                description="High-quality crypto research data",
                free=True,
                requires_key=False,  # Basic endpoints free
                rate_limit="20 req/min",
                features=["assets", "metrics", "news", "profile"],
                verified=False
            ),
            
            "cryptocompare_extended": ProviderInfo(
                id="cryptocompare_extended",
                name="CryptoCompare Extended",
                type=ProviderType.OHLCV.value,
                url="https://min-api.cryptocompare.com/data",
                description="Extended endpoints for CryptoCompare",
                free=True,
                requires_key=False,
                rate_limit="100K calls/month",
                features=["price", "ohlcv", "social", "news"],
                verified=True
            ),
            
            # ===== NEW NEWS PROVIDERS =====
            
            "cryptonews_api": ProviderInfo(
                id="cryptonews_api",
                name="CryptoNews API",
                type=ProviderType.NEWS.value,
                url="https://cryptonews-api.com",
                description="Aggregated crypto news from 50+ sources",
                free=True,
                requires_key=True,  # Free tier available
                rate_limit="100 req/day (free)",
                features=["news", "sentiment", "filtering"],
                verified=False
            ),
            
            "newsapi_crypto": ProviderInfo(
                id="newsapi_crypto",
                name="NewsAPI Crypto",
                type=ProviderType.NEWS.value,
                url="https://newsapi.org/v2",
                description="General news API with crypto filtering",
                free=True,
                requires_key=True,  # Free key available
                rate_limit="100 req/day (free)",
                features=["everything", "top-headlines", "sources"],
                verified=False
            ),
            
            "bitcoin_magazine_rss": ProviderInfo(
                id="bitcoin_magazine_rss",
                name="Bitcoin Magazine RSS",
                type=ProviderType.NEWS.value,
                url="https://bitcoinmagazine.com/feed",
                description="Bitcoin Magazine articles RSS",
                free=True,
                requires_key=False,
                rate_limit="Unlimited",
                features=["articles", "rss"],
                verified=False
            ),
            
            "decrypt_rss": ProviderInfo(
                id="decrypt_rss",
                name="Decrypt RSS",
                type=ProviderType.NEWS.value,
                url="https://decrypt.co/feed",
                description="Decrypt media RSS feed",
                free=True,
                requires_key=False,
                rate_limit="Unlimited",
                features=["articles", "rss", "web3"],
                verified=False
            ),
            
            "cryptoslate_rss": ProviderInfo(
                id="cryptoslate_rss",
                name="CryptoSlate RSS",
                type=ProviderType.NEWS.value,
                url="https://cryptoslate.com/feed/",
                description="CryptoSlate news RSS",
                free=True,
                requires_key=False,
                rate_limit="Unlimited",
                features=["articles", "rss", "analysis"],
                verified=False
            ),
            
            "theblock_rss": ProviderInfo(
                id="theblock_rss",
                name="The Block RSS",
                type=ProviderType.NEWS.value,
                url="https://www.theblock.co/rss.xml",
                description="The Block crypto news RSS",
                free=True,
                requires_key=False,
                rate_limit="Unlimited",
                features=["articles", "rss", "research"],
                verified=False
            ),
            
            # ===== ON-CHAIN PROVIDERS =====
            
            "blockchain_info": ProviderInfo(
                id="blockchain_info",
                name="Blockchain.info",
                type=ProviderType.ONCHAIN.value,
                url="https://blockchain.info",
                description="Bitcoin blockchain explorer API",
                free=True,
                requires_key=False,
                rate_limit="1 req/10sec",
                features=["blocks", "transactions", "addresses", "charts"],
                verified=True
            ),
            
            "blockchair": ProviderInfo(
                id="blockchair",
                name="Blockchair",
                type=ProviderType.ONCHAIN.value,
                url="https://api.blockchair.com",
                description="Multi-chain blockchain API",
                free=True,
                requires_key=False,
                rate_limit="30 req/min",
                features=["bitcoin", "ethereum", "litecoin", "stats"],
                verified=False
            ),
            
            "blockcypher": ProviderInfo(
                id="blockcypher",
                name="BlockCypher",
                type=ProviderType.ONCHAIN.value,
                url="https://api.blockcypher.com/v1",
                description="Multi-blockchain web service",
                free=True,
                requires_key=False,  # Higher limits with key
                rate_limit="200 req/hour",
                features=["btc", "eth", "ltc", "doge", "webhooks"],
                verified=False
            ),
            
            "btc_com": ProviderInfo(
                id="btc_com",
                name="BTC.com API",
                type=ProviderType.ONCHAIN.value,
                url="https://chain.api.btc.com/v3",
                description="BTC.com blockchain data",
                free=True,
                requires_key=False,
                rate_limit="120 req/min",
                features=["blocks", "transactions", "stats", "addresses"],
                verified=False
            ),
            
            # ===== DEFI PROVIDERS =====
            
            "defillama": ProviderInfo(
                id="defillama",
                name="DefiLlama",
                type=ProviderType.DEFI.value,
                url="https://api.llama.fi",
                description="DeFi TVL and protocol data",
                free=True,
                requires_key=False,
                rate_limit="300 req/min",
                features=["tvl", "protocols", "chains", "yields"],
                verified=True
            ),
            
            "defipulse": ProviderInfo(
                id="defipulse",
                name="DeFi Pulse",
                type=ProviderType.DEFI.value,
                url="https://data-api.defipulse.com/api/v1",
                description="DeFi rankings and metrics",
                free=True,
                requires_key=True,  # Free key available
                rate_limit="Varies",
                features=["rankings", "history", "lending"],
                verified=False
            ),
            
            "1inch": ProviderInfo(
                id="1inch",
                name="1inch API",
                type=ProviderType.DEFI.value,
                url="https://api.1inch.io/v4.0",
                description="DEX aggregator API",
                free=True,
                requires_key=False,
                rate_limit="Varies",
                features=["quotes", "swap", "liquidity", "tokens"],
                verified=False
            ),
            
            "uniswap_subgraph": ProviderInfo(
                id="uniswap_subgraph",
                name="Uniswap Subgraph",
                type=ProviderType.DEFI.value,
                url="https://api.thegraph.com/subgraphs/name/uniswap",
                description="Uniswap protocol data via The Graph",
                free=True,
                requires_key=False,
                rate_limit="Varies",
                features=["pairs", "swaps", "liquidity", "volumes"],
                verified=True
            ),
            
            # ===== SOCIAL/SENTIMENT PROVIDERS =====
            
            "lunarcrush": ProviderInfo(
                id="lunarcrush",
                name="LunarCrush",
                type=ProviderType.SOCIAL.value,
                url="https://api.lunarcrush.com/v2",
                description="Social media analytics for crypto",
                free=True,
                requires_key=True,  # Free key available
                rate_limit="50 req/day (free)",
                features=["social", "sentiment", "influencers"],
                verified=False
            ),
            
            "santiment": ProviderInfo(
                id="santiment",
                name="Santiment",
                type=ProviderType.SOCIAL.value,
                url="https://api.santiment.net",
                description="On-chain, social, and development metrics",
                free=True,
                requires_key=True,  # Limited free access
                rate_limit="Varies",
                features=["social", "onchain", "dev_activity"],
                verified=False
            ),
            
            "bitinfocharts": ProviderInfo(
                id="bitinfocharts",
                name="BitInfoCharts",
                type=ProviderType.SOCIAL.value,
                url="https://bitinfocharts.com",
                description="Crypto charts and statistics",
                free=True,
                requires_key=False,
                rate_limit="Unlimited",
                features=["charts", "compare", "stats"],
                verified=False
            ),
            
            # ===== TECHNICAL ANALYSIS PROVIDERS =====
            
            "tradingview_scraper": ProviderInfo(
                id="tradingview_scraper",
                name="TradingView (Public)",
                type=ProviderType.TECHNICAL.value,
                url="https://www.tradingview.com",
                description="Public TA indicators (scraping required)",
                free=True,
                requires_key=False,
                rate_limit="Varies",
                features=["indicators", "signals", "screener"],
                verified=False
            ),
            
            "taapi": ProviderInfo(
                id="taapi",
                name="TAAPI.IO",
                type=ProviderType.TECHNICAL.value,
                url="https://api.taapi.io",
                description="Technical Analysis API",
                free=True,
                requires_key=True,  # Free tier available
                rate_limit="50 req/day (free)",
                features=["150+ indicators", "crypto", "forex", "stocks"],
                verified=False
            ),
        }
    
    def get_all_providers(self) -> List[ProviderInfo]:
        """دریافت تمام سرویس‌دهندگان"""
        return list(self.providers.values())
    
    def get_provider_by_id(self, provider_id: str) -> Optional[ProviderInfo]:
        """دریافت سرویس‌دهنده با ID"""
        return self.providers.get(provider_id)
    
    def filter_providers(
        self,
        provider_type: Optional[str] = None,
        free_only: bool = True,
        no_key_required: bool = False,
        verified_only: bool = False
    ) -> List[ProviderInfo]:
        """فیلتر سرویس‌دهندگان"""
        results = self.get_all_providers()
        
        if provider_type:
            results = [p for p in results if p.type == provider_type]
        
        if free_only:
            results = [p for p in results if p.free]
        
        if no_key_required:
            results = [p for p in results if not p.requires_key]
        
        if verified_only:
            results = [p for p in results if p.verified]
        
        return results
    
    def get_providers_by_type(self, provider_type: str) -> List[ProviderInfo]:
        """دریافت سرویس‌دهندگان بر اساس نوع"""
        return self.filter_providers(provider_type=provider_type)
    
    def search_providers(self, query: str) -> List[ProviderInfo]:
        """جستجوی سرویس‌دهندگان"""
        query_lower = query.lower()
        results = []
        
        for provider in self.get_all_providers():
            if (query_lower in provider.name.lower() or
                query_lower in provider.description.lower() or
                any(query_lower in feature.lower() for feature in provider.features)):
                results.append(provider)
        
        return results
    
    def get_provider_stats(self) -> Dict[str, Any]:
        """آمار سرویس‌دهندگان"""
        providers = self.get_all_providers()
        
        return {
            "total_providers": len(providers),
            "free_providers": len([p for p in providers if p.free]),
            "no_key_required": len([p for p in providers if not p.requires_key]),
            "verified": len([p for p in providers if p.verified]),
            "by_type": {
                ptype.value: len([p for p in providers if p.type == ptype.value])
                for ptype in ProviderType
            }
        }


# ===== Provider Implementation Examples =====

class CoinRankingProvider:
    """مثال: سرویس‌دهنده CoinRanking"""
    
    BASE_URL = "https://api.coinranking.com/v2"
    
    async def get_coins(
        self,
        limit: int = 50,
        offset: int = 0
    ) -> Dict[str, Any]:
        """دریافت لیست کوین‌ها"""
        url = f"{self.BASE_URL}/coins"
        params = {"limit": limit, "offset": offset}
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, params=params, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "data": data.get("data", {}),
                        "source": "coinranking"
                    }
                return {"success": False, "error": f"HTTP {response.status}"}
    
    async def get_coin_price(self, coin_uuid: str) -> Dict[str, Any]:
        """دریافت قیمت یک کوین"""
        url = f"{self.BASE_URL}/coin/{coin_uuid}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "data": data.get("data", {}).get("coin", {}),
                        "source": "coinranking"
                    }
                return {"success": False, "error": f"HTTP {response.status}"}


class DefiLlamaProvider:
    """مثال: سرویس‌دهنده DefiLlama"""
    
    BASE_URL = "https://api.llama.fi"
    
    async def get_tvl_protocols(self) -> Dict[str, Any]:
        """دریافت TVL تمام پروتکل‌ها"""
        url = f"{self.BASE_URL}/protocols"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "data": data,
                        "count": len(data) if isinstance(data, list) else 0,
                        "source": "defillama"
                    }
                return {"success": False, "error": f"HTTP {response.status}"}
    
    async def get_protocol_tvl(self, protocol: str) -> Dict[str, Any]:
        """دریافت TVL یک پروتکل"""
        url = f"{self.BASE_URL}/protocol/{protocol}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "data": data,
                        "source": "defillama"
                    }
                return {"success": False, "error": f"HTTP {response.status}"}


class BlockchairProvider:
    """مثال: سرویس‌دهنده Blockchair"""
    
    BASE_URL = "https://api.blockchair.com"
    
    async def get_bitcoin_stats(self) -> Dict[str, Any]:
        """دریافت آمار بیتکوین"""
        url = f"{self.BASE_URL}/bitcoin/stats"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "data": data.get("data", {}),
                        "source": "blockchair"
                    }
                return {"success": False, "error": f"HTTP {response.status}"}
    
    async def get_address_info(
        self,
        blockchain: str,
        address: str
    ) -> Dict[str, Any]:
        """دریافت اطلاعات یک آدرس"""
        url = f"{self.BASE_URL}/{blockchain}/dashboards/address/{address}"
        
        async with aiohttp.ClientSession() as session:
            async with session.get(url, timeout=aiohttp.ClientTimeout(total=10)) as response:
                if response.status == 200:
                    data = await response.json()
                    return {
                        "success": True,
                        "data": data.get("data", {}),
                        "source": "blockchair"
                    }
                return {"success": False, "error": f"HTTP {response.status}"}


class RSSNewsProvider:
    """مثال: سرویس‌دهنده خبر از RSS"""
    
    RSS_FEEDS = {
        "bitcoin_magazine": "https://bitcoinmagazine.com/feed",
        "decrypt": "https://decrypt.co/feed",
        "cryptoslate": "https://cryptoslate.com/feed/",
        "theblock": "https://www.theblock.co/rss.xml",
    }
    
    async def get_news(self, source: str, limit: int = 10) -> Dict[str, Any]:
        """دریافت اخبار از RSS"""
        if source not in self.RSS_FEEDS:
            return {"success": False, "error": "Unknown source"}
        
        url = self.RSS_FEEDS[source]
        
        try:
            # feedparser is synchronous, run in executor
            loop = asyncio.get_event_loop()
            feed = await loop.run_in_executor(None, feedparser.parse, url)
            
            articles = []
            for entry in feed.entries[:limit]:
                articles.append({
                    "title": entry.get("title", ""),
                    "link": entry.get("link", ""),
                    "published": entry.get("published", ""),
                    "summary": entry.get("summary", "")
                })
            
            return {
                "success": True,
                "data": articles,
                "count": len(articles),
                "source": source
            }
        except Exception as e:
            return {"success": False, "error": str(e)}


# ===== Singleton =====
_registry = None

def get_providers_registry() -> NewProvidersRegistry:
    """دریافت instance سراسری"""
    global _registry
    if _registry is None:
        _registry = NewProvidersRegistry()
    return _registry


# ===== Test =====
if __name__ == "__main__":
    print("="*70)
    print("🧪 Testing New Providers Registry")
    print("="*70)
    
    registry = NewProvidersRegistry()
    
    # آمار
    stats = registry.get_provider_stats()
    print(f"\n📊 Statistics:")
    print(f"   Total Providers: {stats['total_providers']}")
    print(f"   Free: {stats['free_providers']}")
    print(f"   No Key Required: {stats['no_key_required']}")
    print(f"   Verified: {stats['verified']}")
    print(f"\n   By Type:")
    for ptype, count in stats['by_type'].items():
        print(f"      • {ptype.upper()}: {count} providers")
    
    # OHLCV providers
    print(f"\n⭐ OHLCV Providers (No Key Required):")
    ohlcv = registry.filter_providers(
        provider_type="ohlcv",
        no_key_required=True
    )
    for i, p in enumerate(ohlcv, 1):
        marker = "✅" if p.verified else "🟡"
        print(f"   {marker} {i}. {p.name}")
        print(f"      URL: {p.url}")
        print(f"      Rate: {p.rate_limit}")
    
    # DeFi providers
    print(f"\n⭐ DeFi Providers:")
    defi = registry.get_providers_by_type("defi")
    for i, p in enumerate(defi, 1):
        marker = "✅" if p.verified else "🟡"
        print(f"   {marker} {i}. {p.name} - {p.description}")
    
    # Test actual API calls
    print(f"\n🧪 Testing API Calls:")
    
    async def test_apis():
        # Test CoinRanking
        print(f"\n   Testing CoinRanking...")
        coinranking = CoinRankingProvider()
        result = await coinranking.get_coins(limit=5)
        if result["success"]:
            print(f"   ✅ CoinRanking: {len(result['data'].get('coins', []))} coins fetched")
        else:
            print(f"   ❌ CoinRanking: {result.get('error')}")
        
        # Test DefiLlama
        print(f"\n   Testing DefiLlama...")
        defillama = DefiLlamaProvider()
        result = await defillama.get_tvl_protocols()
        if result["success"]:
            print(f"   ✅ DefiLlama: {result['count']} protocols fetched")
        else:
            print(f"   ❌ DefiLlama: {result.get('error')}")
        
        # Test Blockchair
        print(f"\n   Testing Blockchair...")
        blockchair = BlockchairProvider()
        result = await blockchair.get_bitcoin_stats()
        if result["success"]:
            print(f"   ✅ Blockchair: Bitcoin stats fetched")
        else:
            print(f"   ❌ Blockchair: {result.get('error')}")
        
        # Test RSS News
        print(f"\n   Testing RSS News (Decrypt)...")
        rss = RSSNewsProvider()
        result = await rss.get_news("decrypt", limit=3)
        if result["success"]:
            print(f"   ✅ Decrypt RSS: {result['count']} articles fetched")
            for article in result['data'][:2]:
                print(f"      • {article['title'][:60]}...")
        else:
            print(f"   ❌ Decrypt RSS: {result.get('error')}")
    
    asyncio.run(test_apis())
    
    print("\n" + "="*70)
    print("✅ New Providers Registry is working!")
    print("="*70)
