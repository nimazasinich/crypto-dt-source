#!/usr/bin/env python3
"""
Sentiment Aggregator - Uses ALL Free Sentiment Resources
Maximizes usage of all available free sentiment sources
"""

import httpx
import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import HTTPException

logger = logging.getLogger(__name__)


class SentimentAggregator:
    """
    Aggregates sentiment from ALL free sources:
    - Alternative.me Fear & Greed Index
    - CFGI API v1
    - CFGI Legacy
    - CoinGecko Community Data
    - Messari Social Metrics
    - Reddit r/cryptocurrency
    """
    
    def __init__(self):
        self.timeout = 10.0
        self.providers = {
            "alternative_me": {
                "base_url": "https://api.alternative.me",
                "priority": 1,
                "free": True
            },
            "cfgi_v1": {
                "base_url": "https://api.cfgi.io",
                "priority": 2,
                "free": True
            },
            "cfgi_legacy": {
                "base_url": "https://cfgi.io",
                "priority": 3,
                "free": True
            },
            "coingecko": {
                "base_url": "https://api.coingecko.com/api/v3",
                "priority": 4,
                "free": True
            },
            "messari": {
                "base_url": "https://data.messari.io/api/v1",
                "priority": 5,
                "free": True
            },
            "reddit": {
                "base_url": "https://www.reddit.com/r/CryptoCurrency",
                "priority": 6,
                "free": True
            }
        }
        
        # Cache for Fear & Greed data (updates once per day)
        self._fng_cache = None
        self._fng_cache_time = 0
        self._cache_duration = 3600  # 1 hour
    
    async def get_fear_greed_index(self) -> Dict[str, Any]:
        """
        Get Fear & Greed Index from ALL available providers with fallback
        """
        # Check cache first
        current_time = datetime.utcnow().timestamp()
        if self._fng_cache and (current_time - self._fng_cache_time) < self._cache_duration:
            logger.info("✅ Returning cached Fear & Greed Index")
            return self._fng_cache
        
        # Try all providers
        providers_to_try = sorted(
            self.providers.items(),
            key=lambda x: x[1]["priority"]
        )
        
        for provider_name, provider_info in providers_to_try:
            try:
                if provider_name == "alternative_me":
                    fng_data = await self._get_fng_alternative_me()
                elif provider_name == "cfgi_v1":
                    fng_data = await self._get_fng_cfgi_v1()
                elif provider_name == "cfgi_legacy":
                    fng_data = await self._get_fng_cfgi_legacy()
                else:
                    continue
                
                if fng_data:
                    # Cache the result
                    self._fng_cache = fng_data
                    self._fng_cache_time = current_time
                    
                    logger.info(f"✅ {provider_name.upper()}: Successfully fetched Fear & Greed Index")
                    return fng_data
                    
            except Exception as e:
                logger.warning(f"⚠️ {provider_name.upper()} failed: {e}")
                continue
        
        raise HTTPException(
            status_code=503,
            detail="All sentiment providers failed"
        )
    
    async def get_global_sentiment(self) -> Dict[str, Any]:
        """
        Get global market sentiment from multiple sources
        """
        # Get Fear & Greed Index
        try:
            fng_data = await self.get_fear_greed_index()
        except:
            fng_data = None
        
        # Get social sentiment from Reddit
        try:
            reddit_sentiment = await self._get_reddit_sentiment()
        except:
            reddit_sentiment = None
        
        # Combine all sentiment data
        result = {
            "fear_greed_index": fng_data,
            "social_sentiment": reddit_sentiment,
            "timestamp": int(datetime.utcnow().timestamp() * 1000)
        }
        
        # Calculate overall sentiment
        if fng_data:
            value = fng_data.get("value", 50)
            if value >= 75:
                overall = "Extreme Greed"
            elif value >= 55:
                overall = "Greed"
            elif value >= 45:
                overall = "Neutral"
            elif value >= 25:
                overall = "Fear"
            else:
                overall = "Extreme Fear"
            
            result["overall_sentiment"] = overall
            result["sentiment_score"] = value
        
        return result
    
    async def get_coin_sentiment(self, symbol: str) -> Dict[str, Any]:
        """
        Get sentiment for a specific cryptocurrency
        """
        # Try CoinGecko community data
        try:
            coingecko_sentiment = await self._get_coingecko_sentiment(symbol)
        except:
            coingecko_sentiment = None
        
        # Try Messari social metrics
        try:
            messari_sentiment = await self._get_messari_sentiment(symbol)
        except:
            messari_sentiment = None
        
        result = {
            "symbol": symbol.upper(),
            "coingecko": coingecko_sentiment,
            "messari": messari_sentiment,
            "timestamp": int(datetime.utcnow().timestamp() * 1000)
        }
        
        return result
    
    # Alternative.me implementation
    async def _get_fng_alternative_me(self) -> Dict[str, Any]:
        """Get Fear & Greed Index from Alternative.me"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.providers['alternative_me']['base_url']}/fng/",
                params={"limit": 1, "format": "json"}
            )
            response.raise_for_status()
            data = response.json()
            
            if data.get("data"):
                fng = data["data"][0]
                return {
                    "value": int(fng.get("value", 50)),
                    "value_classification": fng.get("value_classification", "Neutral"),
                    "timestamp": int(fng.get("timestamp", 0)) * 1000,
                    "time_until_update": fng.get("time_until_update", ""),
                    "source": "alternative.me"
                }
            
            raise Exception("No data returned from Alternative.me")
    
    # CFGI v1 implementation
    async def _get_fng_cfgi_v1(self) -> Dict[str, Any]:
        """Get Fear & Greed Index from CFGI API v1"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.providers['cfgi_v1']['base_url']}/v1/fear-greed"
            )
            response.raise_for_status()
            data = response.json()
            
            if data:
                value = data.get("value", 50)
                
                # Classify value
                if value >= 75:
                    classification = "Extreme Greed"
                elif value >= 55:
                    classification = "Greed"
                elif value >= 45:
                    classification = "Neutral"
                elif value >= 25:
                    classification = "Fear"
                else:
                    classification = "Extreme Fear"
                
                return {
                    "value": int(value),
                    "value_classification": classification,
                    "timestamp": int(datetime.utcnow().timestamp() * 1000),
                    "source": "cfgi.io"
                }
            
            raise Exception("No data returned from CFGI v1")
    
    # CFGI Legacy implementation
    async def _get_fng_cfgi_legacy(self) -> Dict[str, Any]:
        """Get Fear & Greed Index from CFGI Legacy API"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.providers['cfgi_legacy']['base_url']}/api"
            )
            response.raise_for_status()
            data = response.json()
            
            if data:
                value = data.get("value", 50)
                
                # Classify value
                if value >= 75:
                    classification = "Extreme Greed"
                elif value >= 55:
                    classification = "Greed"
                elif value >= 45:
                    classification = "Neutral"
                elif value >= 25:
                    classification = "Fear"
                else:
                    classification = "Extreme Fear"
                
                return {
                    "value": int(value),
                    "value_classification": classification,
                    "timestamp": int(datetime.utcnow().timestamp() * 1000),
                    "source": "cfgi.io (legacy)"
                }
            
            raise Exception("No data returned from CFGI Legacy")
    
    # CoinGecko sentiment implementation
    async def _get_coingecko_sentiment(self, symbol: str) -> Dict[str, Any]:
        """Get community sentiment from CoinGecko"""
        # Map symbol to CoinGecko ID
        symbol_to_id = {
            "BTC": "bitcoin", "ETH": "ethereum", "BNB": "binancecoin",
            "XRP": "ripple", "ADA": "cardano", "DOGE": "dogecoin",
            "SOL": "solana", "TRX": "tron", "DOT": "polkadot",
            "MATIC": "matic-network", "LTC": "litecoin", "SHIB": "shiba-inu",
            "AVAX": "avalanche-2", "UNI": "uniswap", "LINK": "chainlink"
        }
        
        coin_id = symbol_to_id.get(symbol.upper(), symbol.lower())
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.providers['coingecko']['base_url']}/coins/{coin_id}",
                params={
                    "localization": "false",
                    "tickers": "false",
                    "market_data": "false",
                    "community_data": "true",
                    "developer_data": "false",
                    "sparkline": "false"
                }
            )
            response.raise_for_status()
            data = response.json()
            
            community_data = data.get("community_data", {})
            sentiment_data = data.get("sentiment_votes_up_percentage", 0)
            
            return {
                "twitter_followers": community_data.get("twitter_followers", 0),
                "reddit_subscribers": community_data.get("reddit_subscribers", 0),
                "reddit_active_users": community_data.get("reddit_accounts_active_48h", 0),
                "sentiment_up_percentage": sentiment_data,
                "sentiment_down_percentage": 100 - sentiment_data,
                "source": "coingecko"
            }
    
    # Messari sentiment implementation
    async def _get_messari_sentiment(self, symbol: str) -> Dict[str, Any]:
        """Get social metrics from Messari"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.providers['messari']['base_url']}/assets/{symbol.lower()}/metrics"
            )
            response.raise_for_status()
            data = response.json()
            
            metrics = data.get("data", {})
            
            return {
                "name": metrics.get("name", ""),
                "symbol": metrics.get("symbol", "").upper(),
                "source": "messari"
            }
    
    # Reddit sentiment implementation
    async def _get_reddit_sentiment(self) -> Dict[str, Any]:
        """Get sentiment from Reddit r/cryptocurrency"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            # Get top posts
            headers = {"User-Agent": "Crypto Market Data Aggregator"}
            response = await client.get(
                f"{self.providers['reddit']['base_url']}/top.json",
                params={"limit": 25, "t": "day"},
                headers=headers
            )
            response.raise_for_status()
            data = response.json()
            
            posts = data.get("data", {}).get("children", [])
            
            # Analyze sentiment based on upvotes and comments
            total_upvotes = 0
            total_comments = 0
            bullish_keywords = ["bullish", "moon", "buy", "pump", "green", "up", "gain", "profit"]
            bearish_keywords = ["bearish", "dump", "sell", "crash", "red", "down", "loss", "bear"]
            
            bullish_count = 0
            bearish_count = 0
            
            for post in posts:
                post_data = post.get("data", {})
                title = post_data.get("title", "").lower()
                total_upvotes += post_data.get("ups", 0)
                total_comments += post_data.get("num_comments", 0)
                
                # Count bullish/bearish keywords
                for keyword in bullish_keywords:
                    if keyword in title:
                        bullish_count += 1
                
                for keyword in bearish_keywords:
                    if keyword in title:
                        bearish_count += 1
            
            # Calculate sentiment score (0-100)
            if bullish_count + bearish_count > 0:
                sentiment_score = (bullish_count / (bullish_count + bearish_count)) * 100
            else:
                sentiment_score = 50  # Neutral
            
            return {
                "platform": "reddit",
                "subreddit": "CryptoCurrency",
                "total_posts": len(posts),
                "total_upvotes": total_upvotes,
                "total_comments": total_comments,
                "bullish_mentions": bullish_count,
                "bearish_mentions": bearish_count,
                "sentiment_score": round(sentiment_score, 2),
                "source": "reddit"
            }


# Global instance
sentiment_aggregator = SentimentAggregator()

__all__ = ["SentimentAggregator", "sentiment_aggregator"]

