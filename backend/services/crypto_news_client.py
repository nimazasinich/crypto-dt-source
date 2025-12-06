#!/usr/bin/env python3
"""
Cryptocurrency News API Client - REAL DATA ONLY
Fetches real news from NewsAPI, CryptoPanic, and RSS feeds
NO MOCK DATA - All news from real sources
"""

import httpx
import logging
import os
import hashlib
import feedparser
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import HTTPException

logger = logging.getLogger(__name__)


class CryptoNewsClient:
    """
    Real Cryptocurrency News API Client
    Aggregates news from multiple real sources
    """
    
    def __init__(self):
        # NewsAPI
        self.newsapi_key = os.getenv("NEWSAPI_KEY", "")
        self.newsapi_url = "https://newsapi.org/v2"
        
        # CryptoPanic
        self.cryptopanic_token = os.getenv("CRYPTOPANIC_TOKEN", "")
        self.cryptopanic_url = "https://cryptopanic.com/api/v1"
        
        # RSS Feeds - Updated URLs for reliability
        self.rss_feeds = {
            "coindesk": "https://www.coindesk.com/arc/outboundfeeds/rss/",
            "cointelegraph": "https://cointelegraph.com/rss",
            "decrypt": "https://decrypt.co/feed",
            "bitcoinist": "https://bitcoinist.com/feed/",
            "cryptoslate": "https://cryptoslate.com/feed/"
        }
        
        self.timeout = 15.0
    
    async def get_latest_news(self, limit: int = 20) -> List[Dict[str, Any]]:
        """
        Get REAL latest cryptocurrency news
        Tries multiple sources with fallback
        
        Returns:
            List of real news articles
        """
        articles = []
        
        # Try NewsAPI first (if API key available)
        if self.newsapi_key:
            try:
                newsapi_articles = await self._fetch_from_newsapi(limit=limit)
                articles.extend(newsapi_articles)
                
                if len(articles) >= limit:
                    logger.info(f"✅ NewsAPI: Fetched {len(articles)} real articles")
                    return articles[:limit]
            except Exception as e:
                logger.warning(f"⚠️ NewsAPI failed: {e}")
        
        # Try CryptoPanic (if token available)
        if self.cryptopanic_token and len(articles) < limit:
            try:
                cryptopanic_articles = await self._fetch_from_cryptopanic(
                    limit=limit - len(articles)
                )
                articles.extend(cryptopanic_articles)
                
                if len(articles) >= limit:
                    logger.info(
                        f"✅ CryptoPanic: Fetched {len(articles)} real articles"
                    )
                    return articles[:limit]
            except Exception as e:
                logger.warning(f"⚠️ CryptoPanic failed: {e}")
        
        # Fallback to RSS feeds
        if len(articles) < limit:
            try:
                rss_articles = await self._fetch_from_rss_feeds(
                    limit=limit - len(articles)
                )
                articles.extend(rss_articles)
                
                logger.info(f"✅ RSS Feeds: Fetched {len(articles)} real articles")
            except Exception as e:
                logger.warning(f"⚠️ RSS feeds failed: {e}")
        
        # If still no articles, raise error
        if len(articles) == 0:
            raise HTTPException(
                status_code=503,
                detail="All news sources temporarily unavailable"
            )
        
        logger.info(
            f"✅ Successfully fetched {len(articles)} real news articles "
            f"from multiple sources"
        )
        return articles[:limit]
    
    async def _fetch_from_newsapi(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Fetch REAL news from NewsAPI"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.newsapi_url}/everything",
                    params={
                        "q": "cryptocurrency OR bitcoin OR ethereum OR crypto",
                        "apiKey": self.newsapi_key,
                        "language": "en",
                        "sortBy": "publishedAt",
                        "pageSize": min(limit, 100)
                    }
                )
                response.raise_for_status()
                data = response.json()
                
                articles = []
                for article in data.get("articles", []):
                    # Parse timestamp
                    published_at = article.get("publishedAt", "")
                    try:
                        dt = datetime.fromisoformat(
                            published_at.replace("Z", "+00:00")
                        )
                        timestamp = int(dt.timestamp() * 1000)
                    except:
                        timestamp = int(datetime.utcnow().timestamp() * 1000)
                    
                    articles.append({
                        "title": article.get("title", ""),
                        "description": article.get("description", ""),
                        "url": article.get("url", ""),
                        "source": article.get("source", {}).get("name", "NewsAPI"),
                        "timestamp": timestamp,
                        "author": article.get("author"),
                        "imageUrl": article.get("urlToImage")
                    })
                
                logger.info(f"✅ NewsAPI: Fetched {len(articles)} articles")
                return articles
        
        except Exception as e:
            logger.error(f"❌ NewsAPI failed: {e}")
            raise
    
    async def _fetch_from_cryptopanic(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Fetch REAL news from CryptoPanic"""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.cryptopanic_url}/posts/",
                    params={
                        "auth_token": self.cryptopanic_token,
                        "public": "true",
                        "filter": "hot"
                    }
                )
                response.raise_for_status()
                data = response.json()
                
                articles = []
                for post in data.get("results", [])[:limit]:
                    # Parse timestamp
                    created_at = post.get("created_at", "")
                    try:
                        dt = datetime.fromisoformat(
                            created_at.replace("Z", "+00:00")
                        )
                        timestamp = int(dt.timestamp() * 1000)
                    except:
                        timestamp = int(datetime.utcnow().timestamp() * 1000)
                    
                    articles.append({
                        "title": post.get("title", ""),
                        "description": post.get("title", ""),  # CryptoPanic doesn't have description
                        "url": post.get("url", ""),
                        "source": post.get("source", {}).get("title", "CryptoPanic"),
                        "timestamp": timestamp
                    })
                
                logger.info(f"✅ CryptoPanic: Fetched {len(articles)} articles")
                return articles
        
        except Exception as e:
            logger.error(f"❌ CryptoPanic failed: {e}")
            raise
    
    async def _fetch_from_rss_feeds(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Fetch REAL news from RSS feeds"""
        articles = []
        successful_sources = 0
        
        for source_name, feed_url in self.rss_feeds.items():
            try:
                # Parse RSS feed with timeout handling
                async with httpx.AsyncClient(timeout=self.timeout, follow_redirects=True) as client:
                    response = await client.get(feed_url)
                    response.raise_for_status()
                    
                # Parse RSS feed
                feed = feedparser.parse(response.text)
                
                if feed.bozo and feed.bozo_exception:
                    logger.warning(f"⚠️ RSS ({source_name}): Feed parsing warning: {feed.bozo_exception}")
                
                if not feed.entries:
                    logger.warning(f"⚠️ RSS ({source_name}): No entries found")
                    continue
                
                for entry in feed.entries[:limit]:
                    # Parse timestamp
                    try:
                        if hasattr(entry, "published_parsed") and entry.published_parsed:
                            dt = datetime(*entry.published_parsed[:6])
                        elif hasattr(entry, "updated_parsed") and entry.updated_parsed:
                            dt = datetime(*entry.updated_parsed[:6])
                        else:
                            dt = datetime.utcnow()
                        
                        timestamp = int(dt.timestamp() * 1000)
                    except Exception as ts_error:
                        logger.debug(f"Timestamp parsing failed for {source_name}: {ts_error}")
                        timestamp = int(datetime.utcnow().timestamp() * 1000)
                    
                    # Extract description
                    description = ""
                    if hasattr(entry, "summary"):
                        description = entry.summary[:300]
                    elif hasattr(entry, "description"):
                        description = entry.description[:300]
                    
                    articles.append({
                        "title": entry.get("title", "Untitled"),
                        "description": description,
                        "url": entry.get("link", ""),
                        "source": source_name.title(),
                        "timestamp": timestamp
                    })
                
                successful_sources += 1
                logger.info(
                    f"✅ RSS ({source_name}): Fetched {len(feed.entries)} articles"
                )
                
                if len(articles) >= limit:
                    break
            
            except httpx.HTTPError as e:
                logger.warning(f"⚠️ RSS feed {source_name} HTTP error: {e}")
                continue
            except Exception as e:
                logger.warning(f"⚠️ RSS feed {source_name} failed: {e}")
                continue
        
        if successful_sources > 0:
            logger.info(f"✅ Successfully fetched from {successful_sources}/{len(self.rss_feeds)} RSS sources")
        else:
            logger.error(f"❌ All RSS feeds failed")
        
        return articles[:limit]


# Global instance
crypto_news_client = CryptoNewsClient()


__all__ = ["CryptoNewsClient", "crypto_news_client"]
