#!/usr/bin/env python3
"""
Unified Multi-Source Service
High-level service combining fallback engine with specialized fetchers
Implements validation, cross-checking, and aggregation
"""

import asyncio
import logging
import statistics
from typing import Dict, Any, List, Optional
from datetime import datetime

from .multi_source_fallback_engine import (
    MultiSourceFallbackEngine,
    DataType,
    get_fallback_engine
)
from .multi_source_data_fetchers import (
    MarketPriceFetcher,
    OHLCFetcher,
    NewsFetcher,
    SentimentFetcher
)

logger = logging.getLogger(__name__)


class DataValidator:
    """Validate and cross-check data from multiple sources"""
    
    @staticmethod
    def validate_price_data(prices: List[Dict[str, Any]]) -> bool:
        """Validate price data"""
        if not prices or len(prices) == 0:
            return False
        
        for price in prices:
            # Check required fields
            if "symbol" not in price or "price" not in price:
                return False
            
            # Check price is positive
            if price["price"] <= 0:
                return False
        
        return True
    
    @staticmethod
    def validate_ohlc_data(candles: List[Dict[str, Any]]) -> bool:
        """Validate OHLC data"""
        if not candles or len(candles) == 0:
            return False
        
        for candle in candles:
            # Check required fields
            required = ["timestamp", "open", "high", "low", "close", "volume"]
            if not all(field in candle for field in required):
                return False
            
            # Validate OHLC relationship
            if not (candle["low"] <= candle["open"] <= candle["high"] and
                    candle["low"] <= candle["close"] <= candle["high"]):
                logger.warning(f"⚠️ Invalid OHLC relationship in candle: {candle}")
                return False
        
        return True
    
    @staticmethod
    def cross_check_prices(results: List[Dict[str, Any]], variance_threshold: float = 0.05) -> Dict[str, Any]:
        """
        Cross-check prices from multiple sources
        
        Args:
            results: List of price results from different sources
            variance_threshold: Maximum acceptable variance (default 5%)
        
        Returns:
            Aggregated and validated result
        """
        if len(results) < 2:
            # Not enough sources to cross-check
            return results[0] if results else None
        
        # Group prices by symbol
        symbol_prices = {}
        for result in results:
            for price_data in result.get("prices", []):
                symbol = price_data["symbol"]
                if symbol not in symbol_prices:
                    symbol_prices[symbol] = []
                symbol_prices[symbol].append(price_data["price"])
        
        # Calculate statistics for each symbol
        aggregated_prices = []
        anomalies = []
        
        for symbol, prices in symbol_prices.items():
            if len(prices) < 2:
                aggregated_prices.append({
                    "symbol": symbol,
                    "price": prices[0],
                    "sources": 1,
                    "confidence": 0.5
                })
                continue
            
            # Calculate statistics
            mean_price = statistics.mean(prices)
            median_price = statistics.median(prices)
            stdev = statistics.stdev(prices) if len(prices) > 1 else 0
            variance = stdev / mean_price if mean_price > 0 else 0
            
            # Check if variance is acceptable
            if variance > variance_threshold:
                anomalies.append({
                    "symbol": symbol,
                    "prices": prices,
                    "mean": mean_price,
                    "variance": variance,
                    "threshold": variance_threshold
                })
                logger.warning(
                    f"⚠️ High variance for {symbol}: {variance:.2%} "
                    f"(threshold: {variance_threshold:.2%})"
                )
            
            # Use median as more robust measure
            aggregated_prices.append({
                "symbol": symbol,
                "price": median_price,
                "mean": mean_price,
                "median": median_price,
                "min": min(prices),
                "max": max(prices),
                "stdev": stdev,
                "variance": variance,
                "sources": len(prices),
                "confidence": 1.0 - min(variance, 1.0),  # Lower variance = higher confidence
                "all_prices": prices
            })
        
        return {
            "prices": aggregated_prices,
            "count": len(aggregated_prices),
            "sources_used": len(results),
            "anomalies": anomalies,
            "cross_checked": True
        }
    
    @staticmethod
    def aggregate_news(results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Aggregate news from multiple sources and deduplicate"""
        all_articles = []
        seen_urls = set()
        
        for result in results:
            for article in result.get("articles", []):
                url = article.get("url", "")
                if url and url not in seen_urls:
                    seen_urls.add(url)
                    all_articles.append(article)
        
        # Sort by published date (newest first)
        all_articles.sort(
            key=lambda x: x.get("publishedAt", ""),
            reverse=True
        )
        
        return {
            "articles": all_articles,
            "count": len(all_articles),
            "sources_used": len(results),
            "deduplicated": True
        }


class UnifiedMultiSourceService:
    """
    Unified service for fetching data from multiple sources with automatic fallback
    """
    
    def __init__(self):
        """Initialize the unified service"""
        self.engine = get_fallback_engine()
        self.validator = DataValidator()
        logger.info("✅ Unified Multi-Source Service initialized")
    
    async def get_market_prices(
        self,
        symbols: Optional[List[str]] = None,
        limit: int = 100,
        cross_check: bool = True,
        use_parallel: bool = False
    ) -> Dict[str, Any]:
        """
        Get market prices with automatic fallback through 23+ sources
        
        Args:
            symbols: List of symbols to fetch (None = top coins)
            limit: Maximum number of results
            cross_check: Whether to cross-check prices from multiple sources
            use_parallel: Whether to fetch from multiple sources in parallel
        
        Returns:
            Market price data with metadata
        """
        cache_key = f"market_prices:{','.join(symbols) if symbols else 'top'}:{limit}"
        
        async def fetch_dispatcher(source: Dict[str, Any], **kwargs) -> Dict[str, Any]:
            """Dispatch to appropriate fetcher based on source"""
            source_name = source["name"]
            
            # Special handlers
            if "coingecko" in source_name:
                return await MarketPriceFetcher.fetch_coingecko_special(source, symbols, limit=limit)
            elif "binance" in source_name:
                return await MarketPriceFetcher.fetch_binance_special(source, symbols, limit=limit)
            else:
                return await MarketPriceFetcher.fetch_generic(source, symbols=symbols, limit=limit)
        
        if cross_check and not use_parallel:
            # Fetch from multiple sources sequentially for cross-checking
            sources = self.engine._get_sources_for_data_type(DataType.MARKET_PRICES)[:3]
            results = []
            
            for source in sources:
                try:
                    result = await self.engine._fetch_from_source(source, fetch_dispatcher)
                    if result:
                        results.append(result)
                except Exception as e:
                    logger.warning(f"⚠️ Failed to fetch from {source['name']}: {e}")
            
            if results:
                # Cross-check and aggregate
                aggregated = self.validator.cross_check_prices(results)
                
                # Cache the result
                cache_ttl = self.engine.config["caching"]["market_prices"]["ttl_seconds"]
                self.engine.cache.set(cache_key, aggregated, cache_ttl)
                
                return {
                    "success": True,
                    "data": aggregated,
                    "method": "cross_checked",
                    "timestamp": datetime.utcnow().isoformat()
                }
        
        # Standard fallback or parallel fetch
        if use_parallel:
            result = await self.engine.fetch_parallel(
                DataType.MARKET_PRICES,
                fetch_dispatcher,
                cache_key,
                max_parallel=3,
                symbols=symbols,
                limit=limit
            )
        else:
            result = await self.engine.fetch_with_fallback(
                DataType.MARKET_PRICES,
                fetch_dispatcher,
                cache_key,
                symbols=symbols,
                limit=limit
            )
        
        return result
    
    async def get_ohlc_data(
        self,
        symbol: str,
        timeframe: str = "1h",
        limit: int = 1000,
        validate: bool = True
    ) -> Dict[str, Any]:
        """
        Get OHLC/candlestick data with automatic fallback through 18+ sources
        
        Args:
            symbol: Cryptocurrency symbol
            timeframe: Time interval (1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w)
            limit: Maximum number of candles
            validate: Whether to validate OHLC data
        
        Returns:
            OHLC data with metadata
        """
        cache_key = f"ohlc:{symbol}:{timeframe}:{limit}"
        
        async def fetch_dispatcher(source: Dict[str, Any], **kwargs) -> Dict[str, Any]:
            """Dispatch to appropriate OHLC fetcher"""
            source_name = source["name"]
            
            # Special handlers
            if "binance" in source_name:
                return await OHLCFetcher.fetch_binance_ohlc_special(
                    source, symbol, timeframe, limit
                )
            elif "coingecko" in source_name:
                # Map timeframe to days
                days_map = {"1h": 1, "4h": 7, "1d": 30, "1w": 90}
                days = days_map.get(timeframe, 7)
                return await OHLCFetcher.fetch_coingecko_ohlc(source, symbol, days)
            else:
                return await OHLCFetcher.fetch_generic_exchange(
                    source, symbol, timeframe, limit
                )
        
        result = await self.engine.fetch_with_fallback(
            DataType.OHLC_CANDLESTICK,
            fetch_dispatcher,
            cache_key,
            symbol=symbol,
            timeframe=timeframe,
            limit=limit
        )
        
        # Validate if requested
        if validate and result.get("success") and result.get("data"):
            candles = result["data"].get("candles", [])
            if not self.validator.validate_ohlc_data(candles):
                logger.warning(f"⚠️ OHLC validation failed for {symbol}")
                result["validation_warning"] = "Some candles failed validation"
        
        return result
    
    async def get_news(
        self,
        query: str = "cryptocurrency",
        limit: int = 50,
        aggregate: bool = True
    ) -> Dict[str, Any]:
        """
        Get news from 15+ sources with automatic fallback
        
        Args:
            query: Search query
            limit: Maximum number of articles
            aggregate: Whether to aggregate from multiple sources
        
        Returns:
            News articles with metadata
        """
        cache_key = f"news:{query}:{limit}"
        
        async def fetch_dispatcher(source: Dict[str, Any], **kwargs) -> Dict[str, Any]:
            """Dispatch to appropriate news fetcher"""
            if "rss" in source["name"]:
                return await NewsFetcher.fetch_rss_feed(source, limit=limit)
            else:
                return await NewsFetcher.fetch_news_api(source, query, limit)
        
        if aggregate:
            # Fetch from multiple sources
            sources = self.engine._get_sources_for_data_type(DataType.NEWS_FEEDS)[:5]
            results = []
            
            for source in sources:
                try:
                    result = await self.engine._fetch_from_source(source, fetch_dispatcher)
                    if result:
                        results.append(result)
                except Exception as e:
                    logger.warning(f"⚠️ News source {source['name']} failed: {e}")
            
            if results:
                # Aggregate and deduplicate
                aggregated = self.validator.aggregate_news(results)
                
                # Cache
                cache_ttl = self.engine.config["caching"]["news_feeds"]["ttl_seconds"]
                self.engine.cache.set(cache_key, aggregated, cache_ttl)
                
                return {
                    "success": True,
                    "data": aggregated,
                    "method": "aggregated",
                    "timestamp": datetime.utcnow().isoformat()
                }
        
        # Standard fallback
        result = await self.engine.fetch_with_fallback(
            DataType.NEWS_FEEDS,
            fetch_dispatcher,
            cache_key,
            query=query,
            limit=limit
        )
        
        return result
    
    async def get_sentiment(self) -> Dict[str, Any]:
        """
        Get sentiment data (Fear & Greed Index) with automatic fallback through 12+ sources
        
        Returns:
            Sentiment data with metadata
        """
        cache_key = "sentiment:fear_greed"
        
        async def fetch_dispatcher(source: Dict[str, Any], **kwargs) -> Dict[str, Any]:
            """Dispatch to sentiment fetcher"""
            return await SentimentFetcher.fetch_fear_greed(source)
        
        result = await self.engine.fetch_with_fallback(
            DataType.SENTIMENT_DATA,
            fetch_dispatcher,
            cache_key
        )
        
        return result
    
    def get_monitoring_stats(self) -> Dict[str, Any]:
        """Get monitoring statistics for all sources"""
        return self.engine.get_monitoring_stats()
    
    def clear_cache(self):
        """Clear all cached data"""
        self.engine.clear_cache()


# Global instance
_service_instance: Optional[UnifiedMultiSourceService] = None


def get_unified_service() -> UnifiedMultiSourceService:
    """Get or create global unified service instance"""
    global _service_instance
    if _service_instance is None:
        _service_instance = UnifiedMultiSourceService()
    return _service_instance


__all__ = [
    "UnifiedMultiSourceService",
    "DataValidator",
    "get_unified_service"
]
