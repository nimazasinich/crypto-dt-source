#!/usr/bin/env python3
"""
Sentiment & News Providers Registry - Extended Sources
منابع احساسات بازار و اخبار رمزارزها

این ماژول شامل منابع زیر است:
- Sentiment Analysis APIs
- News Aggregation APIs
- Social Media Sentiment
- Market Sentiment Indices
- Historical Data Sources
"""

import aiohttp
import asyncio
import feedparser
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


class SourceType(Enum):
    """نوع منبع داده"""
    SENTIMENT = "sentiment"
    NEWS = "news"
    SOCIAL = "social"
    MARKET_MOOD = "market_mood"
    HISTORICAL = "historical"
    AGGREGATED = "aggregated"


class TimeFrame(Enum):
    """بازه‌های زمانی پشتیبانی شده"""
    REALTIME = "realtime"
    MINUTES_1 = "1m"
    MINUTES_5 = "5m"
    MINUTES_15 = "15m"
    MINUTES_30 = "30m"
    HOURLY = "1h"
    HOURS_4 = "4h"
    DAILY = "1d"
    WEEKLY = "1w"
    MONTHLY = "1M"


@dataclass
class SentimentNewsSource:
    """تعریف یک منبع سنتیمنت یا اخبار"""
    id: str
    name: str
    source_type: str
    url: str
    description: str
    requires_api_key: bool = False
    api_key_env: str = ""
    rate_limit: str = "unlimited"
    supported_timeframes: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    is_active: bool = True
    priority: int = 1  # 1-10, lower is higher priority
    verified: bool = False
    free_tier: bool = True
    features: List[str] = field(default_factory=list)


class SentimentNewsRegistry:
    """
    رجیستری جامع منابع سنتیمنت و اخبار
    Comprehensive Sentiment & News Sources Registry
    """
    
    def __init__(self):
        self.sources: Dict[str, SentimentNewsSource] = {}
        self._load_all_sources()
    
    def _load_all_sources(self):
        """بارگذاری تمام منابع"""
        
        # ===== SENTIMENT APIS =====
        self.sources["fear_greed_index"] = SentimentNewsSource(
            id="fear_greed_index",
            name="Fear & Greed Index",
            source_type=SourceType.SENTIMENT.value,
            url="https://api.alternative.me/fng/",
            description="Crypto Fear & Greed Index - measure market sentiment",
            requires_api_key=False,
            rate_limit="unlimited",
            supported_timeframes=["1d", "1w", "1M"],
            categories=["sentiment", "market_mood"],
            is_active=True,
            priority=1,
            verified=True,
            free_tier=True,
            features=["fear_index", "greed_index", "historical"]
        )
        
        self.sources["lunarcrush"] = SentimentNewsSource(
            id="lunarcrush",
            name="LunarCrush",
            source_type=SourceType.SOCIAL.value,
            url="https://lunarcrush.com/api",
            description="Social metrics and sentiment for cryptocurrencies",
            requires_api_key=True,
            api_key_env="LUNARCRUSH_KEY",
            rate_limit="50 req/day (free)",
            supported_timeframes=["realtime", "1h", "1d", "1w"],
            categories=["social", "sentiment", "influencers"],
            is_active=True,
            priority=2,
            verified=False,
            free_tier=True,
            features=["social_volume", "sentiment_score", "influencers", "galaxy_score"]
        )
        
        self.sources["santiment"] = SentimentNewsSource(
            id="santiment",
            name="Santiment",
            source_type=SourceType.SENTIMENT.value,
            url="https://api.santiment.net/graphql",
            description="On-chain, social, and development metrics",
            requires_api_key=True,
            api_key_env="SANTIMENT_KEY",
            rate_limit="varies",
            supported_timeframes=["1h", "1d", "1w"],
            categories=["onchain", "social", "development"],
            is_active=True,
            priority=3,
            verified=False,
            free_tier=True,
            features=["dev_activity", "social_volume", "whale_movements", "network_growth"]
        )
        
        self.sources["augmento"] = SentimentNewsSource(
            id="augmento",
            name="Augmento",
            source_type=SourceType.SOCIAL.value,
            url="https://api.augmento.ai/v0.1",
            description="Social media sentiment analysis",
            requires_api_key=False,
            rate_limit="100 req/day",
            supported_timeframes=["1h", "1d"],
            categories=["social", "sentiment"],
            is_active=True,
            priority=4,
            verified=False,
            free_tier=True,
            features=["sentiment_topics", "social_trends", "coin_sentiment"]
        )
        
        self.sources["the_tie"] = SentimentNewsSource(
            id="the_tie",
            name="The TIE",
            source_type=SourceType.SENTIMENT.value,
            url="https://api.thetie.io/v1",
            description="Enterprise-grade sentiment data",
            requires_api_key=True,
            api_key_env="THE_TIE_KEY",
            rate_limit="varies",
            supported_timeframes=["realtime", "1h", "1d"],
            categories=["sentiment", "analytics"],
            is_active=True,
            priority=5,
            verified=False,
            free_tier=False,
            features=["sentiment_score", "volume_buzz", "tweet_sentiment"]
        )
        
        self.sources["cryptoquant_sentiment"] = SentimentNewsSource(
            id="cryptoquant_sentiment",
            name="CryptoQuant Sentiment",
            source_type=SourceType.SENTIMENT.value,
            url="https://api.cryptoquant.com/v1",
            description="On-chain sentiment indicators",
            requires_api_key=True,
            api_key_env="CRYPTOQUANT_KEY",
            rate_limit="100 req/day",
            supported_timeframes=["1h", "1d"],
            categories=["onchain", "sentiment"],
            is_active=True,
            priority=3,
            verified=False,
            free_tier=True,
            features=["exchange_flows", "miner_flows", "market_indicators"]
        )
        
        self.sources["glassnode_sentiment"] = SentimentNewsSource(
            id="glassnode_sentiment",
            name="Glassnode Sentiment",
            source_type=SourceType.SENTIMENT.value,
            url="https://api.glassnode.com/v1/metrics",
            description="Glassnode on-chain sentiment metrics",
            requires_api_key=True,
            api_key_env="GLASSNODE_KEY",
            rate_limit="varies",
            supported_timeframes=["1h", "1d", "1w"],
            categories=["onchain", "sentiment"],
            is_active=True,
            priority=2,
            verified=True,
            free_tier=True,
            features=["sopr", "nupl", "hodl_waves", "reserve_risk"]
        )
        
        # ===== NEWS APIS =====
        self.sources["cryptopanic"] = SentimentNewsSource(
            id="cryptopanic",
            name="CryptoPanic",
            source_type=SourceType.NEWS.value,
            url="https://cryptopanic.com/api/v1/posts/",
            description="Crypto news aggregator with sentiment",
            requires_api_key=True,
            api_key_env="CRYPTOPANIC_KEY",
            rate_limit="500 req/day",
            supported_timeframes=["realtime", "1h", "1d"],
            categories=["news", "sentiment"],
            is_active=True,
            priority=1,
            verified=True,
            free_tier=True,
            features=["news_feed", "sentiment_votes", "trending_news", "filter_by_coin"]
        )
        
        self.sources["newsapi"] = SentimentNewsSource(
            id="newsapi",
            name="NewsAPI",
            source_type=SourceType.NEWS.value,
            url="https://newsapi.org/v2/everything",
            description="General news API with crypto filtering",
            requires_api_key=True,
            api_key_env="NEWSAPI_KEY",
            rate_limit="100 req/day (free)",
            supported_timeframes=["realtime", "1d"],
            categories=["news"],
            is_active=True,
            priority=2,
            verified=True,
            free_tier=True,
            features=["everything", "headlines", "sources"]
        )
        
        self.sources["cryptocompare_news"] = SentimentNewsSource(
            id="cryptocompare_news",
            name="CryptoCompare News",
            source_type=SourceType.NEWS.value,
            url="https://min-api.cryptocompare.com/data/v2/news/",
            description="CryptoCompare news feed",
            requires_api_key=False,
            rate_limit="100K/month",
            supported_timeframes=["realtime", "1h", "1d"],
            categories=["news"],
            is_active=True,
            priority=1,
            verified=True,
            free_tier=True,
            features=["latest_news", "news_by_categories", "news_by_coin"]
        )
        
        self.sources["messari_news"] = SentimentNewsSource(
            id="messari_news",
            name="Messari News",
            source_type=SourceType.NEWS.value,
            url="https://data.messari.io/api/v1/news",
            description="Messari research and news",
            requires_api_key=False,
            rate_limit="20 req/min",
            supported_timeframes=["realtime", "1d"],
            categories=["news", "research"],
            is_active=True,
            priority=2,
            verified=True,
            free_tier=True,
            features=["news", "research", "profiles"]
        )
        
        # ===== RSS NEWS FEEDS =====
        self.sources["bitcoin_magazine_rss"] = SentimentNewsSource(
            id="bitcoin_magazine_rss",
            name="Bitcoin Magazine RSS",
            source_type=SourceType.NEWS.value,
            url="https://bitcoinmagazine.com/feed",
            description="Bitcoin Magazine articles via RSS",
            requires_api_key=False,
            rate_limit="unlimited",
            supported_timeframes=["realtime"],
            categories=["news", "bitcoin"],
            is_active=True,
            priority=3,
            verified=True,
            free_tier=True,
            features=["articles", "analysis"]
        )
        
        self.sources["decrypt_rss"] = SentimentNewsSource(
            id="decrypt_rss",
            name="Decrypt RSS",
            source_type=SourceType.NEWS.value,
            url="https://decrypt.co/feed",
            description="Decrypt media RSS feed",
            requires_api_key=False,
            rate_limit="unlimited",
            supported_timeframes=["realtime"],
            categories=["news", "web3"],
            is_active=True,
            priority=3,
            verified=True,
            free_tier=True,
            features=["articles", "web3_news"]
        )
        
        self.sources["cryptoslate_rss"] = SentimentNewsSource(
            id="cryptoslate_rss",
            name="CryptoSlate RSS",
            source_type=SourceType.NEWS.value,
            url="https://cryptoslate.com/feed/",
            description="CryptoSlate news RSS",
            requires_api_key=False,
            rate_limit="unlimited",
            supported_timeframes=["realtime"],
            categories=["news", "analysis"],
            is_active=True,
            priority=3,
            verified=True,
            free_tier=True,
            features=["articles", "analysis"]
        )
        
        self.sources["theblock_rss"] = SentimentNewsSource(
            id="theblock_rss",
            name="The Block RSS",
            source_type=SourceType.NEWS.value,
            url="https://www.theblock.co/rss.xml",
            description="The Block crypto news RSS",
            requires_api_key=False,
            rate_limit="unlimited",
            supported_timeframes=["realtime"],
            categories=["news", "research"],
            is_active=True,
            priority=3,
            verified=True,
            free_tier=True,
            features=["articles", "research"]
        )
        
        self.sources["cointelegraph_rss"] = SentimentNewsSource(
            id="cointelegraph_rss",
            name="CoinTelegraph RSS",
            source_type=SourceType.NEWS.value,
            url="https://cointelegraph.com/rss",
            description="CoinTelegraph news feed",
            requires_api_key=False,
            rate_limit="unlimited",
            supported_timeframes=["realtime"],
            categories=["news"],
            is_active=True,
            priority=3,
            verified=True,
            free_tier=True,
            features=["articles", "breaking_news"]
        )
        
        self.sources["coindesk_rss"] = SentimentNewsSource(
            id="coindesk_rss",
            name="CoinDesk RSS",
            source_type=SourceType.NEWS.value,
            url="https://www.coindesk.com/arc/outboundfeeds/rss/",
            description="CoinDesk news feed",
            requires_api_key=False,
            rate_limit="unlimited",
            supported_timeframes=["realtime"],
            categories=["news"],
            is_active=True,
            priority=2,
            verified=True,
            free_tier=True,
            features=["articles", "analysis"]
        )
        
        # ===== SOCIAL SENTIMENT =====
        self.sources["reddit_crypto"] = SentimentNewsSource(
            id="reddit_crypto",
            name="Reddit r/CryptoCurrency",
            source_type=SourceType.SOCIAL.value,
            url="https://www.reddit.com/r/CryptoCurrency/new.json",
            description="Reddit cryptocurrency subreddit",
            requires_api_key=False,
            rate_limit="60 req/min",
            supported_timeframes=["realtime", "1h", "1d"],
            categories=["social", "community"],
            is_active=True,
            priority=2,
            verified=True,
            free_tier=True,
            features=["posts", "comments", "trending"]
        )
        
        self.sources["reddit_bitcoin"] = SentimentNewsSource(
            id="reddit_bitcoin",
            name="Reddit r/Bitcoin",
            source_type=SourceType.SOCIAL.value,
            url="https://www.reddit.com/r/Bitcoin/new.json",
            description="Reddit Bitcoin subreddit",
            requires_api_key=False,
            rate_limit="60 req/min",
            supported_timeframes=["realtime", "1h", "1d"],
            categories=["social", "bitcoin"],
            is_active=True,
            priority=2,
            verified=True,
            free_tier=True,
            features=["posts", "comments"]
        )
        
        # ===== HISTORICAL DATA =====
        self.sources["coingecko_historical"] = SentimentNewsSource(
            id="coingecko_historical",
            name="CoinGecko Historical",
            source_type=SourceType.HISTORICAL.value,
            url="https://api.coingecko.com/api/v3",
            description="Historical price and market data",
            requires_api_key=False,
            rate_limit="10-50 req/min",
            supported_timeframes=["1m", "5m", "15m", "30m", "1h", "4h", "1d", "1w"],
            categories=["market", "historical"],
            is_active=True,
            priority=1,
            verified=True,
            free_tier=True,
            features=["ohlcv", "market_chart", "price_history"]
        )
        
        self.sources["binance_historical"] = SentimentNewsSource(
            id="binance_historical",
            name="Binance Historical",
            source_type=SourceType.HISTORICAL.value,
            url="https://api.binance.com/api/v3",
            description="Binance historical OHLCV data",
            requires_api_key=False,
            rate_limit="1200 req/min",
            supported_timeframes=["1m", "5m", "15m", "30m", "1h", "4h", "1d", "1w", "1M"],
            categories=["market", "historical", "ohlcv"],
            is_active=True,
            priority=1,
            verified=True,
            free_tier=True,
            features=["klines", "historical_trades", "agg_trades"]
        )
        
        self.sources["cryptocompare_historical"] = SentimentNewsSource(
            id="cryptocompare_historical",
            name="CryptoCompare Historical",
            source_type=SourceType.HISTORICAL.value,
            url="https://min-api.cryptocompare.com/data/v2",
            description="Historical price data",
            requires_api_key=False,
            rate_limit="100K/month",
            supported_timeframes=["1m", "1h", "1d"],
            categories=["market", "historical"],
            is_active=True,
            priority=2,
            verified=True,
            free_tier=True,
            features=["histominute", "histohour", "histoday"]
        )
        
        # ===== AGGREGATED SOURCES =====
        self.sources["coincap_realtime"] = SentimentNewsSource(
            id="coincap_realtime",
            name="CoinCap Real-time",
            source_type=SourceType.AGGREGATED.value,
            url="https://api.coincap.io/v2",
            description="Real-time aggregated market data",
            requires_api_key=False,
            rate_limit="200 req/min",
            supported_timeframes=["realtime", "1m", "5m", "15m", "30m", "1h", "1d"],
            categories=["market", "realtime"],
            is_active=True,
            priority=1,
            verified=True,
            free_tier=True,
            features=["assets", "rates", "exchanges", "markets", "candles"]
        )
        
        self.sources["coinpaprika"] = SentimentNewsSource(
            id="coinpaprika",
            name="CoinPaprika",
            source_type=SourceType.AGGREGATED.value,
            url="https://api.coinpaprika.com/v1",
            description="Crypto market data with OHLCV",
            requires_api_key=False,
            rate_limit="unlimited",
            supported_timeframes=["5m", "15m", "30m", "1h", "4h", "1d"],
            categories=["market", "ohlcv"],
            is_active=True,
            priority=2,
            verified=True,
            free_tier=True,
            features=["tickers", "coins", "exchanges", "ohlcv"]
        )
        
        self.sources["defillama"] = SentimentNewsSource(
            id="defillama",
            name="DefiLlama",
            source_type=SourceType.AGGREGATED.value,
            url="https://api.llama.fi",
            description="DeFi TVL and protocol data",
            requires_api_key=False,
            rate_limit="300 req/min",
            supported_timeframes=["1h", "1d"],
            categories=["defi", "tvl"],
            is_active=True,
            priority=1,
            verified=True,
            free_tier=True,
            features=["protocols", "tvl", "chains", "yields", "stablecoins"]
        )
        
        # ===== MARKET INDICES =====
        self.sources["tradingview_public"] = SentimentNewsSource(
            id="tradingview_public",
            name="TradingView Public",
            source_type=SourceType.MARKET_MOOD.value,
            url="https://www.tradingview.com",
            description="Public technical indicators (scraping)",
            requires_api_key=False,
            rate_limit="varies",
            supported_timeframes=["realtime", "1h", "1d"],
            categories=["technical", "indicators"],
            is_active=True,
            priority=4,
            verified=False,
            free_tier=True,
            features=["indicators", "signals", "screener"]
        )
        
        self.sources["taapi"] = SentimentNewsSource(
            id="taapi",
            name="TAAPI.IO",
            source_type=SourceType.MARKET_MOOD.value,
            url="https://api.taapi.io",
            description="Technical Analysis API",
            requires_api_key=True,
            api_key_env="TAAPI_KEY",
            rate_limit="50 req/day (free)",
            supported_timeframes=["1m", "5m", "15m", "30m", "1h", "4h", "1d"],
            categories=["technical", "indicators"],
            is_active=True,
            priority=3,
            verified=False,
            free_tier=True,
            features=["rsi", "macd", "bollinger", "ema", "sma"]
        )
    
    # ===== QUERY METHODS =====
    
    def get_all_sources(self) -> List[SentimentNewsSource]:
        """دریافت همه منابع"""
        return list(self.sources.values())
    
    def get_active_sources(self) -> List[SentimentNewsSource]:
        """دریافت منابع فعال"""
        return [s for s in self.sources.values() if s.is_active]
    
    def get_source_by_id(self, source_id: str) -> Optional[SentimentNewsSource]:
        """دریافت منبع با شناسه"""
        return self.sources.get(source_id)
    
    def get_sources_by_type(self, source_type: str) -> List[SentimentNewsSource]:
        """دریافت منابع بر اساس نوع"""
        return [s for s in self.sources.values() if s.source_type == source_type]
    
    def get_free_sources(self) -> List[SentimentNewsSource]:
        """دریافت منابع رایگان"""
        return [s for s in self.sources.values() if s.free_tier and not s.requires_api_key]
    
    def get_sources_by_timeframe(self, timeframe: str) -> List[SentimentNewsSource]:
        """دریافت منابع بر اساس بازه زمانی"""
        return [s for s in self.sources.values() if timeframe in s.supported_timeframes]
    
    def get_sources_by_category(self, category: str) -> List[SentimentNewsSource]:
        """دریافت منابع بر اساس دسته‌بندی"""
        return [s for s in self.sources.values() if category in s.categories]
    
    def search_sources(self, query: str) -> List[SentimentNewsSource]:
        """جستجوی منابع"""
        query_lower = query.lower()
        results = []
        for source in self.sources.values():
            if (query_lower in source.name.lower() or
                query_lower in source.description.lower() or
                any(query_lower in cat.lower() for cat in source.categories) or
                any(query_lower in f.lower() for f in source.features)):
                results.append(source)
        return results
    
    def get_statistics(self) -> Dict[str, Any]:
        """آمار منابع"""
        all_sources = self.get_all_sources()
        return {
            "total_sources": len(all_sources),
            "active_sources": len([s for s in all_sources if s.is_active]),
            "free_sources": len([s for s in all_sources if s.free_tier]),
            "no_key_required": len([s for s in all_sources if not s.requires_api_key]),
            "verified_sources": len([s for s in all_sources if s.verified]),
            "by_type": {
                st.value: len([s for s in all_sources if s.source_type == st.value])
                for st in SourceType
            },
            "categories": list(set(cat for s in all_sources for cat in s.categories))
        }
    
    def set_source_active(self, source_id: str, is_active: bool) -> bool:
        """تنظیم فعال/غیرفعال بودن منبع"""
        if source_id in self.sources:
            self.sources[source_id].is_active = is_active
            return True
        return False
    
    def to_dict(self) -> Dict[str, Any]:
        """تبدیل به دیکشنری"""
        return {
            source_id: {
                "id": source.id,
                "name": source.name,
                "source_type": source.source_type,
                "url": source.url,
                "description": source.description,
                "requires_api_key": source.requires_api_key,
                "api_key_env": source.api_key_env,
                "rate_limit": source.rate_limit,
                "supported_timeframes": source.supported_timeframes,
                "categories": source.categories,
                "is_active": source.is_active,
                "priority": source.priority,
                "verified": source.verified,
                "free_tier": source.free_tier,
                "features": source.features
            }
            for source_id, source in self.sources.items()
        }


# ===== DATA FETCHERS =====

class SentimentNewsFetcher:
    """دریافت داده از منابع سنتیمنت و اخبار"""
    
    def __init__(self):
        self.registry = SentimentNewsRegistry()
        self.timeout = aiohttp.ClientTimeout(total=15)
    
    async def fetch_fear_greed_index(self, limit: int = 30) -> Dict[str, Any]:
        """دریافت شاخص ترس و طمع"""
        source = self.registry.get_source_by_id("fear_greed_index")
        if not source or not source.is_active:
            return {"success": False, "error": "Source not available"}
        
        try:
            url = f"{source.url}?limit={limit}"
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return {
                            "success": True,
                            "data": data.get("data", []),
                            "source": "fear_greed_index"
                        }
                    return {"success": False, "error": f"HTTP {response.status}"}
        except Exception as e:
            logger.error(f"Fear & Greed fetch error: {e}")
            return {"success": False, "error": str(e)}
    
    async def fetch_rss_news(self, source_id: str, limit: int = 20) -> Dict[str, Any]:
        """دریافت اخبار از RSS"""
        source = self.registry.get_source_by_id(source_id)
        if not source or not source.is_active:
            return {"success": False, "error": "Source not available"}
        
        try:
            loop = asyncio.get_event_loop()
            feed = await loop.run_in_executor(None, feedparser.parse, source.url)
            
            articles = []
            for entry in feed.entries[:limit]:
                articles.append({
                    "title": entry.get("title", ""),
                    "link": entry.get("link", ""),
                    "published": entry.get("published", ""),
                    "summary": entry.get("summary", "")[:500] if entry.get("summary") else "",
                    "author": entry.get("author", ""),
                    "source": source.name
                })
            
            return {
                "success": True,
                "data": articles,
                "count": len(articles),
                "source": source_id
            }
        except Exception as e:
            logger.error(f"RSS fetch error for {source_id}: {e}")
            return {"success": False, "error": str(e)}
    
    async def fetch_all_rss_news(self, limit_per_source: int = 10) -> Dict[str, Any]:
        """دریافت اخبار از همه منابع RSS"""
        rss_sources = [s for s in self.registry.get_active_sources() 
                      if "_rss" in s.id or s.url.endswith("/feed")]
        
        all_news = []
        tasks = [self.fetch_rss_news(s.id, limit_per_source) for s in rss_sources]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, dict) and result.get("success"):
                all_news.extend(result.get("data", []))
        
        # Sort by published date if available
        all_news.sort(key=lambda x: x.get("published", ""), reverse=True)
        
        return {
            "success": True,
            "data": all_news,
            "count": len(all_news),
            "sources": [s.id for s in rss_sources]
        }
    
    async def fetch_reddit_posts(self, subreddit: str = "cryptocurrency", limit: int = 25) -> Dict[str, Any]:
        """دریافت پست‌های ردیت"""
        source_id = f"reddit_{subreddit.lower()}"
        source = self.registry.get_source_by_id(source_id)
        
        if not source:
            url = f"https://www.reddit.com/r/{subreddit}/new.json?limit={limit}"
        else:
            url = f"{source.url}?limit={limit}"
        
        try:
            headers = {"User-Agent": "CryptoMonitor/1.0"}
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(url, headers=headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        posts = []
                        for post in data.get("data", {}).get("children", []):
                            post_data = post.get("data", {})
                            posts.append({
                                "title": post_data.get("title", ""),
                                "url": f"https://reddit.com{post_data.get('permalink', '')}",
                                "score": post_data.get("score", 0),
                                "num_comments": post_data.get("num_comments", 0),
                                "created_utc": post_data.get("created_utc", 0),
                                "author": post_data.get("author", ""),
                                "subreddit": subreddit
                            })
                        return {
                            "success": True,
                            "data": posts,
                            "count": len(posts),
                            "source": f"reddit_{subreddit}"
                        }
                    return {"success": False, "error": f"HTTP {response.status}"}
        except Exception as e:
            logger.error(f"Reddit fetch error: {e}")
            return {"success": False, "error": str(e)}
    
    async def fetch_cryptocompare_news(self, categories: str = "", limit: int = 50) -> Dict[str, Any]:
        """دریافت اخبار از CryptoCompare"""
        source = self.registry.get_source_by_id("cryptocompare_news")
        if not source or not source.is_active:
            return {"success": False, "error": "Source not available"}
        
        try:
            params = {"lang": "EN"}
            if categories:
                params["categories"] = categories
            
            url = source.url
            async with aiohttp.ClientSession(timeout=self.timeout) as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        articles = []
                        for article in data.get("Data", [])[:limit]:
                            articles.append({
                                "id": article.get("id"),
                                "title": article.get("title", ""),
                                "body": article.get("body", "")[:500],
                                "url": article.get("url", ""),
                                "source": article.get("source", ""),
                                "published_on": article.get("published_on", 0),
                                "categories": article.get("categories", "")
                            })
                        return {
                            "success": True,
                            "data": articles,
                            "count": len(articles),
                            "source": "cryptocompare_news"
                        }
                    return {"success": False, "error": f"HTTP {response.status}"}
        except Exception as e:
            logger.error(f"CryptoCompare news fetch error: {e}")
            return {"success": False, "error": str(e)}


# ===== SINGLETON =====
_registry = None
_fetcher = None


def get_sentiment_news_registry() -> SentimentNewsRegistry:
    """دریافت instance سراسری registry"""
    global _registry
    if _registry is None:
        _registry = SentimentNewsRegistry()
    return _registry


def get_sentiment_news_fetcher() -> SentimentNewsFetcher:
    """دریافت instance سراسری fetcher"""
    global _fetcher
    if _fetcher is None:
        _fetcher = SentimentNewsFetcher()
    return _fetcher


# ===== TEST =====
if __name__ == "__main__":
    print("="*70)
    print("🧪 Testing Sentiment & News Providers Registry")
    print("="*70)
    
    registry = SentimentNewsRegistry()
    stats = registry.get_statistics()
    
    print(f"\n📊 Statistics:")
    print(f"   Total Sources: {stats['total_sources']}")
    print(f"   Active: {stats['active_sources']}")
    print(f"   Free: {stats['free_sources']}")
    print(f"   No Key Required: {stats['no_key_required']}")
    print(f"   Verified: {stats['verified_sources']}")
    
    print(f"\n   By Type:")
    for source_type, count in stats['by_type'].items():
        print(f"      • {source_type.upper()}: {count}")
    
    print(f"\n⭐ Free Sources (No API Key):")
    free_sources = registry.get_free_sources()
    for i, s in enumerate(free_sources[:10], 1):
        marker = "✅" if s.verified else "🟡"
        print(f"   {marker} {i}. {s.name} - {s.description[:50]}...")
    
    print("\n" + "="*70)
    
    # Test fetching
    async def test_fetching():
        fetcher = SentimentNewsFetcher()
        
        print("\n🧪 Testing Fear & Greed Index...")
        result = await fetcher.fetch_fear_greed_index(limit=5)
        if result["success"]:
            print(f"   ✅ Got {len(result['data'])} entries")
        else:
            print(f"   ❌ Error: {result.get('error')}")
        
        print("\n🧪 Testing RSS News (Decrypt)...")
        result = await fetcher.fetch_rss_news("decrypt_rss", limit=3)
        if result["success"]:
            print(f"   ✅ Got {result['count']} articles")
            for article in result['data'][:2]:
                print(f"      • {article['title'][:50]}...")
        else:
            print(f"   ❌ Error: {result.get('error')}")
        
        print("\n🧪 Testing Reddit Posts...")
        result = await fetcher.fetch_reddit_posts("cryptocurrency", limit=3)
        if result["success"]:
            print(f"   ✅ Got {result['count']} posts")
        else:
            print(f"   ❌ Error: {result.get('error')}")
    
    asyncio.run(test_fetching())
    
    print("\n" + "="*70)
    print("✅ Sentiment & News Providers Registry Complete!")
    print("="*70)
