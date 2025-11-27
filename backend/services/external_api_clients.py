#!/usr/bin/env python3
"""
External API Clients - Complete Collection
Direct HTTP clients for all external cryptocurrency data sources
NO WEBSOCKET - Only HTTP REST requests
"""

import json
import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

import feedparser
import httpx

logger = logging.getLogger(__name__)


class AlternativeMeClient:
    """
    Alternative.me API Client
    Fetches Fear & Greed Index for crypto markets
    """

    def __init__(self):
        self.base_url = "https://api.alternative.me"
        self.timeout = 10.0

    async def get_fear_greed_index(self, limit: int = 1) -> Dict[str, Any]:
        """
        Get Fear & Greed Index

        Args:
            limit: Number of historical data points (default: 1 for current)

        Returns:
            Fear & Greed Index data
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(f"{self.base_url}/fng/", params={"limit": limit})
                response.raise_for_status()
                data = response.json()

                # Transform to standard format
                results = []
                for item in data.get("data", []):
                    results.append(
                        {
                            "value": int(item.get("value", 0)),
                            "value_classification": item.get("value_classification", "neutral"),
                            "timestamp": int(item.get("timestamp", 0)),
                            "time_until_update": item.get("time_until_update"),
                            "source": "alternative.me",
                        }
                    )

                logger.info(f"✅ Alternative.me: Fetched Fear & Greed Index")

                return {
                    "success": True,
                    "data": results,
                    "metadata": data.get("metadata", {}),
                    "source": "alternative.me",
                    "timestamp": datetime.utcnow().isoformat(),
                }

        except Exception as e:
            logger.error(f"❌ Alternative.me API failed: {e}")
            raise Exception(f"Failed to fetch Fear & Greed Index: {str(e)}")


class RedditClient:
    """
    Reddit API Client
    Fetches cryptocurrency posts from Reddit
    """

    def __init__(self):
        self.base_url = "https://www.reddit.com"
        self.timeout = 15.0
        self.user_agent = "CryptoDataHub/1.0"

    async def get_top_posts(
        self, subreddit: str = "cryptocurrency", time_filter: str = "day", limit: int = 25
    ) -> Dict[str, Any]:
        """
        Get top posts from a subreddit

        Args:
            subreddit: Subreddit name (default: cryptocurrency)
            time_filter: Time filter (hour, day, week, month, year, all)
            limit: Number of posts

        Returns:
            Top Reddit posts
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/r/{subreddit}/top.json",
                    params={"t": time_filter, "limit": limit},
                    headers={"User-Agent": self.user_agent},
                )
                response.raise_for_status()
                data = response.json()

                # Transform to standard format
                posts = []
                for child in data.get("data", {}).get("children", []):
                    post_data = child.get("data", {})
                    posts.append(
                        {
                            "id": post_data.get("id"),
                            "title": post_data.get("title"),
                            "author": post_data.get("author"),
                            "score": post_data.get("score", 0),
                            "upvote_ratio": post_data.get("upvote_ratio", 0),
                            "num_comments": post_data.get("num_comments", 0),
                            "url": post_data.get("url"),
                            "permalink": f"{self.base_url}{post_data.get('permalink', '')}",
                            "created_utc": int(post_data.get("created_utc", 0)),
                            "selftext": post_data.get("selftext", "")[:500],  # Limit text
                            "subreddit": subreddit,
                            "source": "reddit",
                        }
                    )

                logger.info(f"✅ Reddit: Fetched {len(posts)} posts from r/{subreddit}")

                return {
                    "success": True,
                    "data": posts,
                    "subreddit": subreddit,
                    "time_filter": time_filter,
                    "count": len(posts),
                    "source": "reddit",
                    "timestamp": datetime.utcnow().isoformat(),
                }

        except Exception as e:
            logger.error(f"❌ Reddit API failed: {e}")
            raise Exception(f"Failed to fetch Reddit posts: {str(e)}")

    async def get_new_posts(
        self, subreddit: str = "cryptocurrency", limit: int = 25
    ) -> Dict[str, Any]:
        """
        Get new posts from a subreddit

        Args:
            subreddit: Subreddit name
            limit: Number of posts

        Returns:
            New Reddit posts
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/r/{subreddit}/new.json",
                    params={"limit": limit},
                    headers={"User-Agent": self.user_agent},
                )
                response.raise_for_status()
                data = response.json()

                # Transform to standard format
                posts = []
                for child in data.get("data", {}).get("children", []):
                    post_data = child.get("data", {})
                    posts.append(
                        {
                            "id": post_data.get("id"),
                            "title": post_data.get("title"),
                            "author": post_data.get("author"),
                            "score": post_data.get("score", 0),
                            "num_comments": post_data.get("num_comments", 0),
                            "url": post_data.get("url"),
                            "created_utc": int(post_data.get("created_utc", 0)),
                            "source": "reddit",
                        }
                    )

                logger.info(f"✅ Reddit: Fetched {len(posts)} new posts from r/{subreddit}")

                return {
                    "success": True,
                    "data": posts,
                    "subreddit": subreddit,
                    "count": len(posts),
                    "source": "reddit",
                    "timestamp": datetime.utcnow().isoformat(),
                }

        except Exception as e:
            logger.error(f"❌ Reddit API failed: {e}")
            raise Exception(f"Failed to fetch Reddit posts: {str(e)}")


class RSSFeedClient:
    """
    RSS Feed Client
    Fetches news from cryptocurrency RSS feeds
    """

    def __init__(self):
        self.feeds = {
            "coindesk": "https://www.coindesk.com/arc/outboundfeeds/rss/",
            "cointelegraph": "https://cointelegraph.com/rss",
            "bitcoinmagazine": "https://bitcoinmagazine.com/.rss/full/",
            "decrypt": "https://decrypt.co/feed",
            "theblock": "https://www.theblock.co/rss.xml",
        }

    async def fetch_feed(self, feed_name: str, limit: int = 20) -> Dict[str, Any]:
        """
        Fetch articles from a specific RSS feed

        Args:
            feed_name: Name of the feed (coindesk, cointelegraph, etc.)
            limit: Maximum number of articles

        Returns:
            RSS feed articles
        """
        if feed_name not in self.feeds:
            raise ValueError(f"Unknown feed: {feed_name}. Available: {list(self.feeds.keys())}")

        try:
            feed_url = self.feeds[feed_name]

            # Parse RSS feed
            feed = feedparser.parse(feed_url)

            # Transform to standard format
            articles = []
            for entry in feed.entries[:limit]:
                # Parse timestamp
                try:
                    if hasattr(entry, "published_parsed"):
                        dt = datetime(*entry.published_parsed[:6])
                    elif hasattr(entry, "updated_parsed"):
                        dt = datetime(*entry.updated_parsed[:6])
                    else:
                        dt = datetime.utcnow()

                    timestamp = int(dt.timestamp())
                except:
                    timestamp = int(datetime.utcnow().timestamp())

                articles.append(
                    {
                        "title": entry.get("title", ""),
                        "link": entry.get("link", ""),
                        "summary": entry.get("summary", "")[:500],  # Limit summary
                        "author": entry.get("author", ""),
                        "published": timestamp,
                        "source": feed_name,
                        "feed_url": feed_url,
                    }
                )

            logger.info(f"✅ RSS: Fetched {len(articles)} articles from {feed_name}")

            return {
                "success": True,
                "data": articles,
                "feed_name": feed_name,
                "feed_url": feed_url,
                "count": len(articles),
                "source": "rss",
                "timestamp": datetime.utcnow().isoformat(),
            }

        except Exception as e:
            logger.error(f"❌ RSS feed {feed_name} failed: {e}")
            raise Exception(f"Failed to fetch RSS feed: {str(e)}")

    async def fetch_all_feeds(self, limit_per_feed: int = 10) -> Dict[str, Any]:
        """
        Fetch articles from all RSS feeds

        Args:
            limit_per_feed: Maximum number of articles per feed

        Returns:
            All RSS feed articles
        """
        all_articles = []
        feed_results = {}

        for feed_name in self.feeds.keys():
            try:
                result = await self.fetch_feed(feed_name, limit_per_feed)
                feed_results[feed_name] = {"success": True, "count": result["count"]}
                all_articles.extend(result["data"])
            except Exception as e:
                logger.error(f"❌ Failed to fetch {feed_name}: {e}")
                feed_results[feed_name] = {"success": False, "error": str(e)}

        # Sort by published date
        all_articles.sort(key=lambda x: x.get("published", 0), reverse=True)

        logger.info(
            f"✅ RSS: Fetched {len(all_articles)} total articles from {len(self.feeds)} feeds"
        )

        return {
            "success": True,
            "data": all_articles,
            "total_articles": len(all_articles),
            "feeds": feed_results,
            "source": "rss",
            "timestamp": datetime.utcnow().isoformat(),
        }


# Global instances
alternative_me_client = AlternativeMeClient()
reddit_client = RedditClient()
rss_feed_client = RSSFeedClient()


# Export
__all__ = [
    "AlternativeMeClient",
    "RedditClient",
    "RSSFeedClient",
    "alternative_me_client",
    "reddit_client",
    "rss_feed_client",
]
