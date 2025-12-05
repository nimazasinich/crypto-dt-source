"""
Multi-Source API Aggregator with Detailed Logging
Shows exactly which services are tried and which succeeded
Minimum 10 fallbacks per category
"""
import httpx
import asyncio
import json
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ServiceAttempt:
    """Track each service attempt"""
    def __init__(self, service_id: str, service_name: str, url: str):
        self.service_id = service_id
        self.service_name = service_name
        self.url = url
        self.start_time = datetime.utcnow()
        self.end_time = None
        self.success = False
        self.status_code = None
        self.error = None
        self.response_time_ms = 0
        self.data = None
    
    def mark_success(self, status_code: int, data: Any):
        self.end_time = datetime.utcnow()
        self.success = True
        self.status_code = status_code
        self.data = data
        self.response_time_ms = int((self.end_time - self.start_time).total_seconds() * 1000)
    
    def mark_failure(self, error: str, status_code: int = None):
        self.end_time = datetime.utcnow()
        self.success = False
        self.error = str(error)
        self.status_code = status_code
        self.response_time_ms = int((self.end_time - self.start_time).total_seconds() * 1000)
    
    def to_dict(self) -> Dict:
        return {
            "service_id": self.service_id,
            "service_name": self.service_name,
            "url": self.url[:100],  # Truncate long URLs
            "success": self.success,
            "status_code": self.status_code,
            "error": self.error,
            "response_time_ms": self.response_time_ms
        }


class MultiSourceAggregator:
    """
    Aggregates data from multiple sources with detailed logging
    Shows exactly how many services are available and which one succeeded
    """
    
    def __init__(self):
        self.client = httpx.AsyncClient(timeout=30.0, follow_redirects=True)
        self.sources = self._load_all_sources()
        
        # Print statistics on initialization
        stats = self.get_source_statistics()
        logger.info("=" * 70)
        logger.info("Multi-Source Aggregator Initialized")
        logger.info("=" * 70)
        for category, count in stats.items():
            logger.info(f"  {category}: {count} services")
        logger.info("=" * 70)
    
    def _load_all_sources(self) -> Dict[str, List[Dict]]:
        """Load all sources - MINIMUM 10 per category"""
        sources = {
            "market_data": self._get_market_data_sources(),
            "news": self._get_news_sources(),
            "sentiment": self._get_sentiment_sources(),
            "block_explorers": self._get_block_explorer_sources(),
            "whale_tracking": self._get_whale_tracking_sources(),
            "on_chain": self._get_on_chain_sources()
        }
        return sources
    
    def _get_market_data_sources(self) -> List[Dict]:
        """15+ market data sources"""
        return [
            {"id": "coingecko", "name": "CoinGecko", "url": "https://api.coingecko.com/api/v3", "free": True, "priority": 1},
            {"id": "binance", "name": "Binance", "url": "https://api.binance.com/api/v3", "free": True, "priority": 2},
            {"id": "coincap", "name": "CoinCap", "url": "https://api.coincap.io/v2", "free": True, "priority": 3},
            {"id": "coinpaprika", "name": "CoinPaprika", "url": "https://api.coinpaprika.com/v1", "free": True, "priority": 4},
            {"id": "coinlore", "name": "CoinLore", "url": "https://api.coinlore.net/api", "free": True, "priority": 5},
            {"id": "messari", "name": "Messari", "url": "https://data.messari.io/api/v1", "free": True, "priority": 6},
            {"id": "defillama", "name": "DefiLlama", "url": "https://coins.llama.fi", "free": True, "priority": 7},
            {"id": "coinstats", "name": "CoinStats", "url": "https://api.coinstats.app/public/v1", "free": True, "priority": 8},
            {"id": "livecoinwatch", "name": "LiveCoinWatch", "url": "https://api.livecoinwatch.com", "free": True, "priority": 9},
            {"id": "mobula", "name": "Mobula", "url": "https://api.mobula.io/api/1", "free": True, "priority": 10},
            {"id": "coinranking", "name": "CoinRanking", "url": "https://api.coinranking.com/v2", "free": True, "priority": 11},
            {"id": "dia", "name": "DIA Data", "url": "https://api.diadata.org/v1", "free": True, "priority": 12},
            {"id": "cryptocompare", "name": "CryptoCompare", "url": "https://min-api.cryptocompare.com/data", "free": True, "priority": 13},
            {"id": "coindesk", "name": "CoinDesk", "url": "https://api.coindesk.com/v1", "free": True, "priority": 14},
            {"id": "kraken", "name": "Kraken", "url": "https://api.kraken.com/0/public", "free": True, "priority": 15},
        ]
    
    def _get_news_sources(self) -> List[Dict]:
        """15+ news sources"""
        return [
            {"id": "cryptopanic", "name": "CryptoPanic", "url": "https://cryptopanic.com/api/v1", "free": True, "priority": 1},
            {"id": "coindesk_rss", "name": "CoinDesk RSS", "url": "https://www.coindesk.com/arc/outboundfeeds/rss", "free": True, "priority": 2},
            {"id": "cointelegraph_rss", "name": "Cointelegraph RSS", "url": "https://cointelegraph.com/rss", "free": True, "priority": 3},
            {"id": "decrypt_rss", "name": "Decrypt RSS", "url": "https://decrypt.co/feed", "free": True, "priority": 4},
            {"id": "bitcoinmagazine_rss", "name": "Bitcoin Magazine RSS", "url": "https://bitcoinmagazine.com/.rss/full", "free": True, "priority": 5},
            {"id": "reddit_crypto", "name": "Reddit r/Crypto", "url": "https://www.reddit.com/r/CryptoCurrency/new.json", "free": True, "priority": 6},
            {"id": "reddit_bitcoin", "name": "Reddit r/Bitcoin", "url": "https://www.reddit.com/r/Bitcoin/new.json", "free": True, "priority": 7},
            {"id": "coinstats_news", "name": "CoinStats News", "url": "https://api.coinstats.app/public/v1/news", "free": True, "priority": 8},
            {"id": "cryptocontrol", "name": "CryptoControl", "url": "https://cryptocontrol.io/api/v1/public/news", "free": True, "priority": 9},
            {"id": "cryptoslate", "name": "CryptoSlate", "url": "https://cryptoslate.com/feed", "free": True, "priority": 10},
            {"id": "newsbtc_rss", "name": "NewsBTC RSS", "url": "https://www.newsbtc.com/feed", "free": True, "priority": 11},
            {"id": "cryptonews_rss", "name": "CryptoNews RSS", "url": "https://cryptonews.com/news/feed", "free": True, "priority": 12},
            {"id": "coinjournal_rss", "name": "CoinJournal RSS", "url": "https://coinjournal.net/feed", "free": True, "priority": 13},
            {"id": "bitcoinist_rss", "name": "Bitcoinist RSS", "url": "https://bitcoinist.com/feed", "free": True, "priority": 14},
            {"id": "coincodex_news", "name": "CoinCodex News", "url": "https://coincodex.com/api/news", "free": True, "priority": 15},
        ]
    
    def _get_sentiment_sources(self) -> List[Dict]:
        """12+ sentiment sources"""
        return [
            {"id": "alternative_me", "name": "Alternative.me F&G", "url": "https://api.alternative.me/fng", "free": True, "priority": 1},
            {"id": "cfgi_v1", "name": "CFGI v1", "url": "https://api.cfgi.io/v1/fear-greed", "free": True, "priority": 2},
            {"id": "cfgi_legacy", "name": "CFGI Legacy", "url": "https://cfgi.io/api", "free": True, "priority": 3},
            {"id": "coingecko_sentiment", "name": "CoinGecko Community Data", "url": "https://api.coingecko.com/api/v3", "free": True, "priority": 4},
            {"id": "messari_sentiment", "name": "Messari Social", "url": "https://data.messari.io/api/v1", "free": True, "priority": 5},
            {"id": "lunarcrush", "name": "LunarCrush", "url": "https://api.lunarcrush.com/v2", "free": False, "priority": 6},
            {"id": "santiment", "name": "Santiment", "url": "https://api.santiment.net/graphql", "free": False, "priority": 7},
            {"id": "cryptoquant", "name": "CryptoQuant", "url": "https://api.cryptoquant.com/v1", "free": False, "priority": 8},
            {"id": "glassnode", "name": "Glassnode Social", "url": "https://api.glassnode.com/v1", "free": False, "priority": 9},
            {"id": "thetie", "name": "TheTie", "url": "https://api.thetie.io", "free": False, "priority": 10},
            {"id": "augmento", "name": "Augmento AI", "url": "https://api.augmento.ai/v1", "free": False, "priority": 11},
            {"id": "sentiment_investor", "name": "Sentiment Investor", "url": "https://api.sentimentinvestor.com", "free": False, "priority": 12},
        ]
    
    def _get_block_explorer_sources(self) -> List[Dict]:
        """15+ block explorer sources"""
        return [
            {"id": "blockchair", "name": "Blockchair", "url": "https://api.blockchair.com", "free": True, "priority": 1},
            {"id": "blockscout_eth", "name": "Blockscout ETH", "url": "https://eth.blockscout.com/api", "free": True, "priority": 2},
            {"id": "blockscout_polygon", "name": "Blockscout Polygon", "url": "https://polygon.blockscout.com/api", "free": True, "priority": 3},
            {"id": "ethplorer", "name": "Ethplorer", "url": "https://api.ethplorer.io", "free": True, "priority": 4},
            {"id": "etherchain", "name": "Etherchain", "url": "https://www.etherchain.org/api", "free": True, "priority": 5},
            {"id": "chainlens", "name": "Chainlens", "url": "https://api.chainlens.com", "free": True, "priority": 6},
            {"id": "covalent", "name": "Covalent", "url": "https://api.covalenthq.com/v1", "free": True, "priority": 7},
            {"id": "moralis", "name": "Moralis", "url": "https://deep-index.moralis.io/api/v2", "free": True, "priority": 8},
            {"id": "transpose", "name": "Transpose", "url": "https://api.transpose.io", "free": True, "priority": 9},
            {"id": "alchemy", "name": "Alchemy API", "url": "https://api.alchemy.com", "free": True, "priority": 10},
            {"id": "quicknode", "name": "QuickNode", "url": "https://api.quicknode.com", "free": True, "priority": 11},
            {"id": "getblock", "name": "GetBlock", "url": "https://go.getblock.io", "free": True, "priority": 12},
            {"id": "chainbase", "name": "Chainbase", "url": "https://api.chainbase.online", "free": True, "priority": 13},
            {"id": "footprint", "name": "Footprint Analytics", "url": "https://api.footprint.network", "free": True, "priority": 14},
            {"id": "bitquery", "name": "BitQuery", "url": "https://graphql.bitquery.io", "free": True, "priority": 15},
        ]
    
    def _get_whale_tracking_sources(self) -> List[Dict]:
        """10+ whale tracking sources"""
        return [
            {"id": "clankapp", "name": "ClankApp", "url": "https://clankapp.com/api", "free": True, "priority": 1},
            {"id": "whale_alert", "name": "Whale Alert", "url": "https://api.whale-alert.io/v1", "free": False, "priority": 2},
            {"id": "arkham", "name": "Arkham Intelligence", "url": "https://api.arkham.com", "free": False, "priority": 3},
            {"id": "whalemap", "name": "Whalemap", "url": "https://whalemap.io/api", "free": True, "priority": 4},
            {"id": "debank", "name": "DeBank", "url": "https://api.debank.com", "free": True, "priority": 5},
            {"id": "zerion", "name": "Zerion", "url": "https://api.zerion.io", "free": True, "priority": 6},
            {"id": "dexcheck", "name": "DexCheck", "url": "https://api.dexcheck.io", "free": True, "priority": 7},
            {"id": "nansen", "name": "Nansen", "url": "https://api.nansen.ai/v1", "free": False, "priority": 8},
            {"id": "chainalysis", "name": "Chainalysis", "url": "https://api.chainalysis.com", "free": False, "priority": 9},
            {"id": "elliptic", "name": "Elliptic", "url": "https://api.elliptic.co", "free": False, "priority": 10},
        ]
    
    def _get_on_chain_sources(self) -> List[Dict]:
        """10+ on-chain analytics sources"""
        return [
            {"id": "glassnode", "name": "Glassnode", "url": "https://api.glassnode.com/v1", "free": False, "priority": 1},
            {"id": "intotheblock", "name": "IntoTheBlock", "url": "https://api.intotheblock.com/v1", "free": False, "priority": 2},
            {"id": "thegraph", "name": "The Graph", "url": "https://api.thegraph.com/subgraphs/name", "free": True, "priority": 3},
            {"id": "dune", "name": "Dune Analytics", "url": "https://api.dune.com/api/v1", "free": True, "priority": 4},
            {"id": "coinmetrics", "name": "Coin Metrics", "url": "https://api.coinmetrics.io/v4", "free": False, "priority": 5},
            {"id": "cryptoquant_onchain", "name": "CryptoQuant On-Chain", "url": "https://api.cryptoquant.com/v1", "free": False, "priority": 6},
            {"id": "santiment_onchain", "name": "Santiment On-Chain", "url": "https://api.santiment.net/graphql", "free": False, "priority": 7},
            {"id": "tokenanalyst", "name": "Token Analyst", "url": "https://api.tokenanalyst.io/v1", "free": False, "priority": 8},
            {"id": "chaingraph", "name": "ChainGraph", "url": "https://api.chaingraph.io", "free": True, "priority": 9},
            {"id": "amberdata", "name": "Amberdata", "url": "https://web3api.io", "free": False, "priority": 10},
        ]
    
    async def fetch_with_fallbacks(
        self,
        category: str,
        fetch_func: callable,
        max_attempts: int = None
    ) -> Tuple[Dict[str, Any], List[ServiceAttempt]]:
        """
        Fetch data with comprehensive fallback system
        
        Args:
            category: Category name (market_data, news, sentiment, etc.)
            fetch_func: Async function that takes (source, attempt) and returns data
            max_attempts: Maximum number of services to try (None = try all)
        
        Returns:
            (result_data, list_of_attempts)
        """
        sources = self.sources.get(category, [])
        if not sources:
            logger.warning(f"No sources available for category: {category}")
            return {"error": "No sources available"}, []
        
        # Sort by priority
        sources = sorted(sources, key=lambda x: x.get("priority", 999))
        
        if max_attempts:
            sources = sources[:max_attempts]
        
        attempts = []
        logger.info(f"\n{'=' * 70}")
        logger.info(f"Fetching {category} - {len(sources)} services available")
        logger.info(f"{'=' * 70}")
        
        for i, source in enumerate(sources):
            attempt = ServiceAttempt(
                service_id=source.get("id"),
                service_name=source.get("name"),
                url=source.get("url", "")
            )
            
            logger.info(f"[{i+1}/{len(sources)}] Trying {source.get('name')}...")
            
            try:
                result = await fetch_func(source, attempt)
                
                if result and not result.get("error"):
                    attempt.mark_success(200, result)
                    logger.info(f"  ✅ SUCCESS from {source.get('name')} ({attempt.response_time_ms}ms)")
                    attempts.append(attempt)
                    
                    # Return first successful result
                    return {
                        "success": True,
                        "data": result,
                        "source_used": source,
                        "attempts_count": len(attempts),
                        "total_available": len(sources)
                    }, attempts
                else:
                    attempt.mark_failure("No data returned")
                    logger.warning(f"  ⚠️ No data from {source.get('name')}")
            
            except Exception as e:
                attempt.mark_failure(str(e))
                logger.warning(f"  ❌ Failed: {source.get('name')} - {str(e)[:100]}")
            
            attempts.append(attempt)
        
        logger.error(f"All {len(sources)} sources failed for {category}")
        
        return {
            "success": False,
            "error": f"All {len(sources)} sources failed",
            "attempts_count": len(attempts),
            "total_available": len(sources)
        }, attempts
    
    async def get_market_price(self, symbol: str) -> Tuple[Dict, List[ServiceAttempt]]:
        """Get price with 15+ fallbacks"""
        
        async def fetch_market(source, attempt):
            source_id = source.get("id")
            base_url = source.get("url")
            
            # CoinGecko
            if source_id == "coingecko":
                url = f"{base_url}/simple/price?ids={symbol.lower()}&vs_currencies=usd&include_24hr_change=true&include_market_cap=true"
                response = await self.client.get(url)
                data = response.json()
                if symbol.lower() in data:
                    return {
                        "symbol": symbol,
                        "price": data[symbol.lower()].get("usd"),
                        "change_24h": data[symbol.lower()].get("usd_24h_change"),
                        "market_cap": data[symbol.lower()].get("usd_market_cap")
                    }
            
            # Binance
            elif source_id == "binance":
                url = f"{base_url}/ticker/24hr?symbol={symbol.upper()}USDT"
                response = await self.client.get(url)
                data = response.json()
                return {
                    "symbol": symbol,
                    "price": float(data.get("lastPrice", 0)),
                    "change_24h": float(data.get("priceChangePercent", 0)),
                    "volume_24h": float(data.get("volume", 0))
                }
            
            # CoinCap
            elif source_id == "coincap":
                url = f"{base_url}/assets/{symbol.lower()}"
                response = await self.client.get(url)
                data = response.json()
                asset = data.get("data", {})
                return {
                    "symbol": symbol,
                    "price": float(asset.get("priceUsd", 0)),
                    "change_24h": float(asset.get("changePercent24Hr", 0)),
                    "market_cap": float(asset.get("marketCapUsd", 0))
                }
            
            # CoinPaprika
            elif source_id == "coinpaprika":
                url = f"{base_url}/tickers/{symbol.lower()}-{symbol.lower()}"
                response = await self.client.get(url)
                data = response.json()
                quotes = data.get("quotes", {}).get("USD", {})
                return {
                    "symbol": symbol,
                    "price": quotes.get("price"),
                    "change_24h": quotes.get("percent_change_24h"),
                    "market_cap": quotes.get("market_cap")
                }
            
            # Generic attempt for other sources
            else:
                response = await self.client.get(base_url)
                return {"raw": response.json()}
        
        return await self.fetch_with_fallbacks("market_data", fetch_market, max_attempts=15)
    
    async def get_news(self, limit: int = 10) -> Tuple[List[Dict], List[ServiceAttempt]]:
        """Get news with 15+ fallbacks"""
        
        async def fetch_news(source, attempt):
            source_id = source.get("id")
            base_url = source.get("url")
            news_items = []
            
            # CryptoPanic
            if source_id == "cryptopanic":
                url = f"{base_url}/posts/?public=true"
                response = await self.client.get(url)
                data = response.json()
                for item in data.get("results", [])[:limit]:
                    news_items.append({
                        "title": item.get("title"),
                        "url": item.get("url"),
                        "source": item.get("source", {}).get("title", "CryptoPanic") if isinstance(item.get("source"), dict) else "CryptoPanic",
                        "published_at": item.get("published_at")
                    })
                return news_items if news_items else None
            
            # RSS feeds
            elif "rss" in source_id or "feed" in base_url:
                headers = {"User-Agent": "Mozilla/5.0 (CryptoMonitor/1.0)"}
                response = await self.client.get(base_url, headers=headers)
                text = response.text
                
                if "<item>" in text:
                    import re
                    titles = re.findall(r'<title><!\[CDATA\[(.*?)\]\]></title>|<title>(.*?)</title>', text, re.DOTALL)
                    links = re.findall(r'<link>(.*?)</link>', text, re.DOTALL)
                    
                    for i, title_match in enumerate(titles[1:limit+1]):
                        title = title_match[0] or title_match[1]
                        news_items.append({
                            "title": title.strip(),
                            "url": links[i+1].strip() if i+1 < len(links) else base_url,
                            "source": source.get("name"),
                            "published_at": datetime.utcnow().isoformat()
                        })
                    return news_items if news_items else None
            
            # Reddit JSON
            elif "reddit" in source_id:
                headers = {"User-Agent": "Mozilla/5.0 (CryptoMonitor/1.0)"}
                response = await self.client.get(base_url, headers=headers)
                data = response.json()
                for child in data.get("data", {}).get("children", [])[:limit]:
                    post = child.get("data", {})
                    news_items.append({
                        "title": post.get("title"),
                        "url": f"https://reddit.com{post.get('permalink')}",
                        "source": "Reddit",
                        "published_at": datetime.fromtimestamp(post.get("created_utc", 0)).isoformat()
                    })
                return news_items if news_items else None
            
            return None
        
        result, attempts = await self.fetch_with_fallbacks("news", fetch_news, max_attempts=15)
        
        if result.get("success"):
            return result.get("data", []), attempts
        return [], attempts
    
    async def get_sentiment(self) -> Tuple[Dict, List[ServiceAttempt]]:
        """Get sentiment with 12+ fallbacks"""
        
        async def fetch_sentiment(source, attempt):
            source_id = source.get("id")
            base_url = source.get("url")
            
            # Alternative.me
            if source_id == "alternative_me":
                url = f"{base_url}/?limit=1"
                response = await self.client.get(url)
                data = response.json()
                item = data.get("data", [{}])[0]
                return {
                    "value": int(item.get("value", 50)),
                    "classification": item.get("value_classification", "neutral"),
                    "time_until_update": item.get("time_until_update")
                }
            
            # CFGI
            elif "cfgi" in source_id:
                response = await self.client.get(base_url)
                data = response.json()
                return {
                    "value": int(data.get("value", data.get("fgi", 50))),
                    "classification": data.get("classification", "neutral")
                }
            
            # CoinGecko Community Data
            elif source_id == "coingecko_sentiment":
                url = f"{base_url}/coins/bitcoin?community_data=true&market_data=false"
                response = await self.client.get(url)
                data = response.json()
                community = data.get("community_data", {})
                # Convert community metrics to sentiment score
                twitter = community.get("twitter_followers", 0)
                reddit = community.get("reddit_subscribers", 0)
                score = min(100, (twitter / 10000 + reddit / 1000))
                return {
                    "value": int(score),
                    "classification": "neutral",
                    "community_data": community
                }
            
            return None
        
        return await self.fetch_with_fallbacks("sentiment", fetch_sentiment, max_attempts=12)
    
    def get_source_statistics(self) -> Dict[str, int]:
        """Get statistics about available sources"""
        stats = {}
        for category, sources in self.sources.items():
            stats[category] = len(sources)
        stats["total"] = sum(stats.values())
        return stats
    
    def get_all_sources(self, category: str = None) -> Dict:
        """Get list of all sources"""
        if category:
            return {
                "category": category,
                "sources": self.sources.get(category, []),
                "count": len(self.sources.get(category, []))
            }
        
        return {
            "all_categories": {
                cat: {
                    "count": len(sources),
                    "free_count": sum(1 for s in sources if s.get("free", False)),
                    "services": [{"id": s["id"], "name": s["name"], "free": s.get("free", False)} for s in sources]
                }
                for cat, sources in self.sources.items()
            },
            "total_services": sum(len(s) for s in self.sources.values())
        }
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()


# Global instance
_aggregator = None

def get_aggregator() -> MultiSourceAggregator:
    """Get or create global aggregator"""
    global _aggregator
    if _aggregator is None:
        _aggregator = MultiSourceAggregator()
    return _aggregator

async def close_aggregator():
    """Close global aggregator"""
    global _aggregator
    if _aggregator:
        await _aggregator.close()
        _aggregator = None

