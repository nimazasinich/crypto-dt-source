"""
Data Collection Background Worker - CONFIGURABLE INTERVALS

This worker manages data collection from all sources with:
- Bulk data collection: 15-30 minute intervals
- Real-time data: On-demand when client requests
- Smart scheduling based on source type

COLLECTION INTERVALS:
- Market data: 15 minutes
- News: 15 minutes  
- Sentiment: 15 minutes
- On-chain: 30 minutes
- Historical: 30 minutes
- DeFi: 15 minutes

REAL-TIME DATA:
- When client requests data, fetch immediately from source
- Cache results for configured TTL
"""

import asyncio
import time
import logging
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import httpx

from utils.logger import setup_logger

logger = setup_logger("data_collection_worker")

# ===== COLLECTION CONFIGURATION =====

# Bulk collection intervals (in minutes)
COLLECTION_INTERVALS = {
    "market": 15,      # Market data every 15 minutes
    "news": 15,        # News every 15 minutes
    "sentiment": 15,   # Sentiment every 15 minutes
    "social": 30,      # Social data every 30 minutes
    "onchain": 30,     # On-chain every 30 minutes
    "historical": 30,  # Historical every 30 minutes
    "defi": 15,        # DeFi data every 15 minutes
    "technical": 15,   # Technical indicators every 15 minutes
}

# Cache TTL for different data types (in seconds)
CACHE_TTL = {
    "market": 60,           # 1 minute cache for prices
    "news": 300,            # 5 minutes cache for news
    "sentiment": 300,       # 5 minutes cache for sentiment
    "ohlcv": 60,            # 1 minute cache for OHLCV
    "fear_greed": 3600,     # 1 hour cache for Fear & Greed
    "whale": 300,           # 5 minutes cache for whale alerts
}

# Sources that support real-time fetching (on-demand)
REALTIME_SOURCES = {
    "binance": ["price", "ohlcv", "trades"],
    "coingecko": ["price", "market"],
    "coincap": ["price", "assets"],
    "cryptocompare": ["price", "ohlcv"],
    "fear_greed": ["index"],
}


# ===== DATA COLLECTORS =====

class BaseDataCollector:
    """Base class for data collectors"""
    
    def __init__(self, name: str, interval_minutes: int):
        self.name = name
        self.interval_minutes = interval_minutes
        self.last_run = None
        self.is_running = False
        self.error_count = 0
        self.success_count = 0
        self.timeout = httpx.Timeout(15.0)
    
    async def collect(self) -> Dict[str, Any]:
        """Override in subclass"""
        raise NotImplementedError
    
    async def should_run(self) -> bool:
        """Check if collector should run based on interval"""
        if self.is_running:
            return False
        if self.last_run is None:
            return True
        elapsed = datetime.utcnow() - self.last_run
        return elapsed >= timedelta(minutes=self.interval_minutes)
    
    async def run(self) -> Optional[Dict[str, Any]]:
        """Run collection with error handling"""
        if not await self.should_run():
            return None
        
        self.is_running = True
        start_time = time.time()
        
        try:
            logger.info(f"[{self.name}] Starting collection...")
            result = await self.collect()
            
            elapsed = time.time() - start_time
            self.last_run = datetime.utcnow()
            self.success_count += 1
            self.error_count = 0  # Reset error count on success
            
            logger.info(f"[{self.name}] Collection completed in {elapsed:.2f}s")
            return result
            
        except Exception as e:
            self.error_count += 1
            logger.error(f"[{self.name}] Collection error: {e}")
            return {"success": False, "error": str(e)}
        
        finally:
            self.is_running = False


class MarketDataCollector(BaseDataCollector):
    """Collect market data (prices, market cap, volume)"""
    
    COINGECKO_URL = "https://api.coingecko.com/api/v3"
    COINCAP_URL = "https://api.coincap.io/v2"
    
    def __init__(self):
        super().__init__("market_data", COLLECTION_INTERVALS["market"])
        self.top_coins = [
            "bitcoin", "ethereum", "binancecoin", "ripple", "cardano",
            "solana", "polkadot", "dogecoin", "polygon", "avalanche"
        ]
    
    async def collect(self) -> Dict[str, Any]:
        """Collect market data from multiple sources"""
        results = {"success": True, "data": [], "source": "multi"}
        
        # Try CoinGecko first
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                ids = ",".join(self.top_coins)
                url = f"{self.COINGECKO_URL}/coins/markets"
                params = {
                    "vs_currency": "usd",
                    "ids": ids,
                    "order": "market_cap_desc",
                    "per_page": 50,
                    "sparkline": False
                }
                
                response = await client.get(url, params=params)
                if response.status_code == 200:
                    coins = response.json()
                    for coin in coins:
                        results["data"].append({
                            "symbol": coin.get("symbol", "").upper(),
                            "name": coin.get("name"),
                            "price": coin.get("current_price"),
                            "market_cap": coin.get("market_cap"),
                            "volume_24h": coin.get("total_volume"),
                            "change_24h": coin.get("price_change_percentage_24h"),
                            "high_24h": coin.get("high_24h"),
                            "low_24h": coin.get("low_24h"),
                            "source": "coingecko",
                            "timestamp": datetime.utcnow().isoformat()
                        })
                    results["source"] = "coingecko"
                    return results
        except Exception as e:
            logger.warning(f"CoinGecko failed, trying CoinCap: {e}")
        
        # Fallback to CoinCap
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.COINCAP_URL}/assets?limit=50")
                if response.status_code == 200:
                    data = response.json()
                    for asset in data.get("data", []):
                        results["data"].append({
                            "symbol": asset.get("symbol", "").upper(),
                            "name": asset.get("name"),
                            "price": float(asset.get("priceUsd", 0)),
                            "market_cap": float(asset.get("marketCapUsd", 0)) if asset.get("marketCapUsd") else None,
                            "volume_24h": float(asset.get("volumeUsd24Hr", 0)) if asset.get("volumeUsd24Hr") else None,
                            "change_24h": float(asset.get("changePercent24Hr", 0)) if asset.get("changePercent24Hr") else None,
                            "source": "coincap",
                            "timestamp": datetime.utcnow().isoformat()
                        })
                    results["source"] = "coincap"
        except Exception as e:
            logger.error(f"CoinCap also failed: {e}")
            results["success"] = False
            results["error"] = str(e)
        
        return results


class NewsDataCollector(BaseDataCollector):
    """Collect news from multiple sources"""
    
    RSS_FEEDS = {
        "decrypt": "https://decrypt.co/feed",
        "cryptoslate": "https://cryptoslate.com/feed/",
        "bitcoinmagazine": "https://bitcoinmagazine.com/feed",
        "coindesk": "https://www.coindesk.com/arc/outboundfeeds/rss/",
    }
    
    CRYPTOCOMPARE_URL = "https://min-api.cryptocompare.com/data/v2/news/"
    
    def __init__(self):
        super().__init__("news_data", COLLECTION_INTERVALS["news"])
    
    async def collect(self) -> Dict[str, Any]:
        """Collect news from multiple sources"""
        import feedparser
        
        results = {"success": True, "data": [], "sources": []}
        
        # Collect from RSS feeds
        for source_name, feed_url in self.RSS_FEEDS.items():
            try:
                loop = asyncio.get_event_loop()
                feed = await loop.run_in_executor(None, feedparser.parse, feed_url)
                
                for entry in feed.entries[:10]:
                    results["data"].append({
                        "title": entry.get("title", ""),
                        "link": entry.get("link", ""),
                        "published": entry.get("published", ""),
                        "summary": entry.get("summary", "")[:300] if entry.get("summary") else "",
                        "source": source_name,
                        "fetched_at": datetime.utcnow().isoformat()
                    })
                results["sources"].append(source_name)
            except Exception as e:
                logger.warning(f"RSS feed {source_name} failed: {e}")
        
        # Collect from CryptoCompare
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(self.CRYPTOCOMPARE_URL, params={"lang": "EN"})
                if response.status_code == 200:
                    data = response.json()
                    for article in data.get("Data", [])[:20]:
                        results["data"].append({
                            "title": article.get("title", ""),
                            "link": article.get("url", ""),
                            "published": datetime.fromtimestamp(article.get("published_on", 0)).isoformat(),
                            "summary": article.get("body", "")[:300] if article.get("body") else "",
                            "source": "cryptocompare",
                            "fetched_at": datetime.utcnow().isoformat()
                        })
                    results["sources"].append("cryptocompare")
        except Exception as e:
            logger.warning(f"CryptoCompare news failed: {e}")
        
        return results


class SentimentDataCollector(BaseDataCollector):
    """Collect sentiment data"""
    
    FEAR_GREED_URL = "https://api.alternative.me/fng/"
    
    def __init__(self):
        super().__init__("sentiment_data", COLLECTION_INTERVALS["sentiment"])
    
    async def collect(self) -> Dict[str, Any]:
        """Collect Fear & Greed Index and other sentiment"""
        results = {"success": True, "data": {}, "source": "fear_greed"}
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.FEAR_GREED_URL}?limit=30")
                if response.status_code == 200:
                    data = response.json()
                    fng_data = data.get("data", [])
                    
                    if fng_data:
                        latest = fng_data[0]
                        results["data"] = {
                            "value": int(latest.get("value", 50)),
                            "classification": latest.get("value_classification", "Neutral"),
                            "timestamp": latest.get("timestamp"),
                            "history": [
                                {
                                    "value": int(d.get("value", 50)),
                                    "classification": d.get("value_classification"),
                                    "timestamp": d.get("timestamp")
                                }
                                for d in fng_data[:30]
                            ]
                        }
        except Exception as e:
            logger.error(f"Fear & Greed fetch failed: {e}")
            results["success"] = False
            results["error"] = str(e)
        
        return results


class OnChainDataCollector(BaseDataCollector):
    """Collect on-chain data"""
    
    BLOCKCHAIR_URL = "https://api.blockchair.com"
    
    def __init__(self):
        super().__init__("onchain_data", COLLECTION_INTERVALS["onchain"])
    
    async def collect(self) -> Dict[str, Any]:
        """Collect on-chain statistics"""
        results = {"success": True, "data": {}, "source": "blockchair"}
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Bitcoin stats
                response = await client.get(f"{self.BLOCKCHAIR_URL}/bitcoin/stats")
                if response.status_code == 200:
                    data = response.json()
                    results["data"]["bitcoin"] = data.get("data", {})
                
                # Ethereum stats
                response = await client.get(f"{self.BLOCKCHAIR_URL}/ethereum/stats")
                if response.status_code == 200:
                    data = response.json()
                    results["data"]["ethereum"] = data.get("data", {})
        except Exception as e:
            logger.error(f"On-chain data fetch failed: {e}")
            results["success"] = False
            results["error"] = str(e)
        
        return results


class DeFiDataCollector(BaseDataCollector):
    """Collect DeFi data from DefiLlama"""
    
    DEFILLAMA_URL = "https://api.llama.fi"
    
    def __init__(self):
        super().__init__("defi_data", COLLECTION_INTERVALS["defi"])
    
    async def collect(self) -> Dict[str, Any]:
        """Collect DeFi TVL and protocol data"""
        results = {"success": True, "data": {}, "source": "defillama"}
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Total TVL
                response = await client.get(f"{self.DEFILLAMA_URL}/tvl")
                if response.status_code == 200:
                    results["data"]["total_tvl"] = response.json()
                
                # Top protocols
                response = await client.get(f"{self.DEFILLAMA_URL}/protocols")
                if response.status_code == 200:
                    protocols = response.json()
                    results["data"]["top_protocols"] = protocols[:20] if isinstance(protocols, list) else []
        except Exception as e:
            logger.error(f"DeFi data fetch failed: {e}")
            results["success"] = False
            results["error"] = str(e)
        
        return results


# ===== REAL-TIME DATA FETCHER =====

class RealTimeDataFetcher:
    """
    Fetch data in real-time when client requests
    For instant data that shouldn't wait for scheduled collection
    """
    
    def __init__(self):
        self.cache = {}  # Simple in-memory cache
        self.timeout = httpx.Timeout(10.0)
    
    def _get_cache_key(self, source: str, data_type: str, params: Dict) -> str:
        """Generate cache key"""
        params_str = "_".join(f"{k}={v}" for k, v in sorted(params.items()))
        return f"{source}_{data_type}_{params_str}"
    
    def _is_cache_valid(self, cache_key: str, ttl_seconds: int) -> bool:
        """Check if cached data is still valid"""
        if cache_key not in self.cache:
            return False
        cached_at = self.cache[cache_key].get("cached_at")
        if not cached_at:
            return False
        return (datetime.utcnow() - cached_at).total_seconds() < ttl_seconds
    
    async def fetch_price(self, symbol: str, source: str = "binance") -> Dict[str, Any]:
        """Fetch real-time price"""
        cache_key = self._get_cache_key(source, "price", {"symbol": symbol})
        ttl = CACHE_TTL.get("market", 60)
        
        if self._is_cache_valid(cache_key, ttl):
            return self.cache[cache_key]["data"]
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                if source == "binance":
                    url = f"https://api.binance.com/api/v3/ticker/price?symbol={symbol}USDT"
                    response = await client.get(url)
                    if response.status_code == 200:
                        data = response.json()
                        result = {
                            "success": True,
                            "symbol": symbol,
                            "price": float(data.get("price", 0)),
                            "source": "binance",
                            "timestamp": datetime.utcnow().isoformat()
                        }
                        self.cache[cache_key] = {"data": result, "cached_at": datetime.utcnow()}
                        return result
                
                elif source == "coingecko":
                    url = f"https://api.coingecko.com/api/v3/simple/price?ids={symbol.lower()}&vs_currencies=usd"
                    response = await client.get(url)
                    if response.status_code == 200:
                        data = response.json()
                        price = data.get(symbol.lower(), {}).get("usd", 0)
                        result = {
                            "success": True,
                            "symbol": symbol,
                            "price": price,
                            "source": "coingecko",
                            "timestamp": datetime.utcnow().isoformat()
                        }
                        self.cache[cache_key] = {"data": result, "cached_at": datetime.utcnow()}
                        return result
        except Exception as e:
            logger.error(f"Real-time price fetch error: {e}")
        
        return {"success": False, "error": "Failed to fetch price"}
    
    async def fetch_ohlcv(self, symbol: str, interval: str = "1h", limit: int = 100) -> Dict[str, Any]:
        """Fetch real-time OHLCV data"""
        cache_key = self._get_cache_key("binance", "ohlcv", {"symbol": symbol, "interval": interval})
        ttl = CACHE_TTL.get("ohlcv", 60)
        
        if self._is_cache_valid(cache_key, ttl):
            return self.cache[cache_key]["data"]
        
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                url = "https://api.binance.com/api/v3/klines"
                params = {
                    "symbol": f"{symbol}USDT",
                    "interval": interval,
                    "limit": limit
                }
                response = await client.get(url, params=params)
                
                if response.status_code == 200:
                    klines = response.json()
                    ohlcv = []
                    for k in klines:
                        ohlcv.append({
                            "t": k[0],  # Open time
                            "o": float(k[1]),  # Open
                            "h": float(k[2]),  # High
                            "l": float(k[3]),  # Low
                            "c": float(k[4]),  # Close
                            "v": float(k[5]),  # Volume
                        })
                    
                    result = {
                        "success": True,
                        "symbol": symbol,
                        "interval": interval,
                        "data": ohlcv,
                        "source": "binance",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                    self.cache[cache_key] = {"data": result, "cached_at": datetime.utcnow()}
                    return result
        except Exception as e:
            logger.error(f"OHLCV fetch error: {e}")
        
        return {"success": False, "error": "Failed to fetch OHLCV"}


# ===== MAIN WORKER =====

class DataCollectionWorker:
    """Main data collection worker managing all collectors"""
    
    def __init__(self):
        self.collectors = {
            "market": MarketDataCollector(),
            "news": NewsDataCollector(),
            "sentiment": SentimentDataCollector(),
            "onchain": OnChainDataCollector(),
            "defi": DeFiDataCollector(),
        }
        self.realtime_fetcher = RealTimeDataFetcher()
        self.is_running = False
        self.last_results = {}
    
    async def run_all_collectors(self) -> Dict[str, Any]:
        """Run all collectors that are due"""
        results = {}
        for name, collector in self.collectors.items():
            result = await collector.run()
            if result:
                results[name] = result
                self.last_results[name] = {
                    "data": result,
                    "collected_at": datetime.utcnow().isoformat()
                }
        return results
    
    async def worker_loop(self):
        """Main worker loop"""
        self.is_running = True
        logger.info("Starting data collection worker...")
        logger.info(f"Collection intervals: {COLLECTION_INTERVALS}")
        
        while self.is_running:
            try:
                # Check and run each collector
                for name, collector in self.collectors.items():
                    if await collector.should_run():
                        result = await collector.run()
                        if result:
                            self.last_results[name] = {
                                "data": result,
                                "collected_at": datetime.utcnow().isoformat()
                            }
                
                # Sleep for 1 minute before checking again
                await asyncio.sleep(60)
                
            except Exception as e:
                logger.error(f"Worker loop error: {e}")
                await asyncio.sleep(60)
    
    def stop(self):
        """Stop the worker"""
        self.is_running = False
        logger.info("Stopping data collection worker...")
    
    def get_collector_status(self) -> Dict[str, Any]:
        """Get status of all collectors"""
        return {
            name: {
                "last_run": collector.last_run.isoformat() if collector.last_run else None,
                "interval_minutes": collector.interval_minutes,
                "is_running": collector.is_running,
                "success_count": collector.success_count,
                "error_count": collector.error_count,
                "next_run_in": max(0, collector.interval_minutes * 60 - 
                                   (datetime.utcnow() - collector.last_run).total_seconds()) 
                               if collector.last_run else 0
            }
            for name, collector in self.collectors.items()
        }


# ===== GLOBAL INSTANCES =====

_worker = None
_realtime_fetcher = None


def get_data_collection_worker() -> DataCollectionWorker:
    """Get global worker instance"""
    global _worker
    if _worker is None:
        _worker = DataCollectionWorker()
    return _worker


def get_realtime_fetcher() -> RealTimeDataFetcher:
    """Get global real-time fetcher instance"""
    global _realtime_fetcher
    if _realtime_fetcher is None:
        _realtime_fetcher = RealTimeDataFetcher()
    return _realtime_fetcher


async def start_data_collection_worker():
    """Start the data collection worker"""
    worker = get_data_collection_worker()
    
    # Run initial collection
    logger.info("Running initial data collection...")
    await worker.run_all_collectors()
    
    # Start background loop
    asyncio.create_task(worker.worker_loop())
    logger.info("Data collection worker started")


# ===== TEST =====
if __name__ == "__main__":
    async def test():
        print("="*70)
        print("🧪 Testing Data Collection Worker")
        print("="*70)
        
        worker = DataCollectionWorker()
        
        print("\n📊 Collection Intervals:")
        for data_type, interval in COLLECTION_INTERVALS.items():
            print(f"   • {data_type}: {interval} minutes")
        
        print("\n🔄 Running all collectors...")
        results = await worker.run_all_collectors()
        
        for name, result in results.items():
            if result.get("success"):
                data = result.get("data", {})
                count = len(data) if isinstance(data, list) else "object"
                print(f"   ✅ {name}: {count} items")
            else:
                print(f"   ❌ {name}: {result.get('error')}")
        
        print("\n⚡ Testing Real-time Fetcher...")
        fetcher = RealTimeDataFetcher()
        
        price = await fetcher.fetch_price("BTC")
        if price.get("success"):
            print(f"   ✅ BTC Price: ${price.get('price')}")
        else:
            print(f"   ❌ Price fetch failed: {price.get('error')}")
        
        ohlcv = await fetcher.fetch_ohlcv("BTC", "1h", 10)
        if ohlcv.get("success"):
            print(f"   ✅ OHLCV: {len(ohlcv.get('data', []))} candles")
        else:
            print(f"   ❌ OHLCV fetch failed: {ohlcv.get('error')}")
        
        print("\n" + "="*70)
        print("✅ Data Collection Worker Test Complete!")
        print("="*70)
    
    asyncio.run(test())
