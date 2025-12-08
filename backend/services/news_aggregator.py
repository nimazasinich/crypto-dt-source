#!/usr/bin/env python3
"""
News Aggregator - Uses ALL Free News Resources
Maximizes usage of all available free crypto news sources
"""

import httpx
import logging
import feedparser
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import HTTPException

logger = logging.getLogger(__name__)


class NewsAggregator:
    """
    Aggregates news from ALL free sources:
    - CryptoPanic
    - CoinStats
    - CoinTelegraph RSS
    - CoinDesk RSS
    - Decrypt RSS
    - Bitcoin Magazine RSS
    - CryptoSlate
    - The Block
    - CoinDesk API
    - CoinTelegraph API
    """
    
    def __init__(self):
        self.timeout = 10.0
        self.providers = {
            "cryptopanic": {
                "base_url": "https://cryptopanic.com/api/v1",
                "type": "api",
                "priority": 1,
                "free": True
            },
            "coinstats": {
                "base_url": "https://api.coinstats.app/public/v1",
                "type": "api",
                "priority": 2,
                "free": True
            },
            "cointelegraph_rss": {
                "base_url": "https://cointelegraph.com/rss",
                "type": "rss",
                "priority": 3,
                "free": True
            },
            "coindesk_rss": {
                "base_url": "https://www.coindesk.com/arc/outboundfeeds/rss/",
                "type": "rss",
                "priority": 4,
                "free": True
            },
            "decrypt_rss": {
                "base_url": "https://decrypt.co/feed",
                "type": "rss",
                "priority": 5,
                "free": True
            },
            "bitcoinmagazine_rss": {
                "base_url": "https://bitcoinmagazine.com/.rss/full/",
                "type": "rss",
                "priority": 6,
                "free": True
            },
            "cryptoslate": {
                "base_url": "https://cryptoslate.com/feed/",
                "type": "rss",
                "priority": 7,
                "free": True
            }
        }
    
    async def get_news(
        self,
        symbol: Optional[str] = None,
        limit: int = 20
    ) -> List[Dict[str, Any]]:
        """
        Get news from ALL available free providers with fallback
        """
        all_news = []
        
        # Try all providers in parallel
        tasks = []
        for provider_name, provider_info in self.providers.items():
            task = self._fetch_from_provider(provider_name, provider_info, symbol, limit)
            tasks.append(task)
        
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Collect all successful results
        for provider_name, result in zip(self.providers.keys(), results):
            if isinstance(result, Exception):
                logger.warning(f"⚠️ {provider_name.upper()} failed: {result}")
                continue
            
            if result:
                all_news.extend(result)
                logger.info(f"✅ {provider_name.upper()}: Fetched {len(result)} articles")
        
        if not all_news:
            raise HTTPException(
                status_code=503,
                detail="All news providers failed"
            )
        
        # Sort by timestamp (newest first) and deduplicate
        all_news.sort(key=lambda x: x.get("timestamp", 0), reverse=True)
        
        # Deduplicate by title
        seen_titles = set()
        unique_news = []
        for article in all_news:
            title_lower = article.get("title", "").lower()
            if title_lower not in seen_titles:
                seen_titles.add(title_lower)
                unique_news.append(article)
        
        return unique_news[:limit]
    
    async def _fetch_from_provider(
        self,
        provider_name: str,
        provider_info: Dict[str, Any],
        symbol: Optional[str],
        limit: int
    ) -> List[Dict[str, Any]]:
        """Fetch news from a specific provider"""
        try:
            if provider_info["type"] == "api":
                if provider_name == "cryptopanic":
                    return await self._get_news_cryptopanic(symbol, limit)
                elif provider_name == "coinstats":
                    return await self._get_news_coinstats(limit)
            
            elif provider_info["type"] == "rss":
                return await self._get_news_rss(
                    provider_name,
                    provider_info["base_url"],
                    limit
                )
            
            return []
        
        except Exception as e:
            logger.warning(f"⚠️ {provider_name} failed: {e}")
            return []
    
    async def _get_news_cryptopanic(self, symbol: Optional[str], limit: int) -> List[Dict[str, Any]]:
        """Get news from CryptoPanic (free, no API key required)"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            params = {"public": "true"}
            if symbol:
                params["currencies"] = symbol.upper()
            
            response = await client.get(
                f"{self.providers['cryptopanic']['base_url']}/posts/",
                params=params
            )
            response.raise_for_status()
            data = response.json()
            
            news = []
            for post in data.get("results", [])[:limit]:
                news.append({
                    "title": post.get("title", ""),
                    "summary": post.get("title", ""),  # CryptoPanic doesn't provide summaries
                    "url": post.get("url", ""),
                    "source": post.get("source", {}).get("title", "CryptoPanic"),
                    "published_at": post.get("published_at", ""),
                    "timestamp": self._parse_timestamp(post.get("published_at", "")),
                    "sentiment": post.get("votes", {}).get("positive", 0) - post.get("votes", {}).get("negative", 0),
                    "provider": "cryptopanic"
                })
            
            return news
    
    async def _get_news_coinstats(self, limit: int) -> List[Dict[str, Any]]:
        """Get news from CoinStats"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.providers['coinstats']['base_url']}/news"
            )
            response.raise_for_status()
            data = response.json()
            
            news = []
            for article in data.get("news", [])[:limit]:
                news.append({
                    "title": article.get("title", ""),
                    "summary": article.get("description", ""),
                    "url": article.get("link", ""),
                    "source": article.get("source", "CoinStats"),
                    "published_at": article.get("feedDate", ""),
                    "timestamp": article.get("feedDate", 0) * 1000 if article.get("feedDate") else 0,
                    "image_url": article.get("imgURL", ""),
                    "provider": "coinstats"
                })
            
            return news
    
    async def _get_news_rss(self, provider_name: str, rss_url: str, limit: int) -> List[Dict[str, Any]]:
        """Get news from RSS feed"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(rss_url)
            response.raise_for_status()
            
            # Parse RSS feed
            feed = feedparser.parse(response.text)
            
            news = []
            for entry in feed.entries[:limit]:
                news.append({
                    "title": entry.get("title", ""),
                    "summary": entry.get("summary", "") or entry.get("description", ""),
                    "url": entry.get("link", ""),
                    "source": provider_name.replace("_rss", "").title(),
                    "published_at": entry.get("published", ""),
                    "timestamp": self._parse_timestamp(entry.get("published", "")),
                    "provider": provider_name
                })
            
            return news
    
    def _parse_timestamp(self, date_str: str) -> int:
        """Parse various date formats to Unix timestamp (milliseconds)"""
        if not date_str:
            return int(datetime.utcnow().timestamp() * 1000)
        
        try:
            # Try ISO format first
            dt = datetime.fromisoformat(date_str.replace("Z", "+00:00"))
            return int(dt.timestamp() * 1000)
        except:
            pass
        
        try:
            # Try RFC 2822 format (RSS feeds)
            from email.utils import parsedate_to_datetime
            dt = parsedate_to_datetime(date_str)
            return int(dt.timestamp() * 1000)
        except:
            pass
        
        # Return current time if parsing fails
        return int(datetime.utcnow().timestamp() * 1000)
    
    async def get_latest_news(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get latest news from all sources"""
        return await self.get_news(symbol=None, limit=limit)
    
    async def get_symbol_news(self, symbol: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Get news for a specific symbol"""
        return await self.get_news(symbol=symbol, limit=limit)


# Global instance
news_aggregator = NewsAggregator()

__all__ = ["NewsAggregator", "news_aggregator"]

