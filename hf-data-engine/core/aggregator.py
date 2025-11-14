"""Data aggregator with multi-provider fallback"""
from __future__ import annotations
from typing import List, Optional
from datetime import datetime
import time
import logging
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from providers import BinanceProvider, CoinGeckoProvider, KrakenProvider, CoinCapProvider
from core.models import (
    OHLCV, Price, SentimentData, FearGreedIndex, NewsSentiment,
    OverallSentiment, MarketOverview, ProviderHealth
)
from core.config import settings
from core.cache import cache, cache_key, get_or_set
import httpx

logger = logging.getLogger(__name__)


class DataAggregator:
    """Aggregates data from multiple providers with fallback"""

    def __init__(self):
        # Initialize providers
        self.ohlcv_providers = [
            BinanceProvider(),
            KrakenProvider(),
        ]

        self.price_providers = [
            CoinGeckoProvider(api_key=settings.COINGECKO_API_KEY),
            CoinCapProvider(),
            BinanceProvider(),
        ]

        self.market_provider = CoinGeckoProvider(api_key=settings.COINGECKO_API_KEY)

        self.start_time = time.time()

    async def close(self):
        """Close all provider connections"""
        for provider in self.ohlcv_providers + self.price_providers:
            await provider.close()

    async def fetch_ohlcv(
        self,
        symbol: str,
        interval: str = "1h",
        limit: int = 100
    ) -> tuple[List[OHLCV], str]:
        """Fetch OHLCV data with provider fallback"""

        # Try each provider in order
        for provider in self.ohlcv_providers:
            try:
                logger.info(f"Trying {provider.name} for OHLCV data: {symbol} {interval}")
                data = await provider.fetch_ohlcv(symbol, interval, limit)

                if data and len(data) > 0:
                    logger.info(f"Successfully fetched {len(data)} candles from {provider.name}")
                    return data, provider.name

            except Exception as e:
                logger.warning(f"Provider {provider.name} failed: {e}")
                continue

        raise Exception("All OHLCV providers failed")

    async def fetch_prices(self, symbols: List[str]) -> tuple[List[Price], str]:
        """Fetch prices with aggregation from multiple providers"""

        all_prices = {}
        sources_used = []

        # Collect prices from all available providers
        for provider in self.price_providers:
            try:
                logger.info(f"Fetching prices from {provider.name}")
                prices = await provider.fetch_prices(symbols)

                for price in prices:
                    if price.symbol not in all_prices:
                        all_prices[price.symbol] = []
                    all_prices[price.symbol].append((provider.name, price))

                sources_used.append(provider.name)

            except Exception as e:
                logger.warning(f"Provider {provider.name} failed for prices: {e}")
                continue

        if not all_prices:
            raise Exception("All price providers failed")

        # Aggregate prices (use median or first available)
        aggregated = []
        for symbol, price_list in all_prices.items():
            if price_list:
                # Use first available price
                # Could implement median calculation for better accuracy
                _, price = price_list[0]
                aggregated.append(price)

        source_str = "+".join(sources_used) if sources_used else "multi-provider"

        return aggregated, source_str

    async def fetch_fear_greed_index(self) -> FearGreedIndex:
        """Fetch Fear & Greed Index from Alternative.me"""
        try:
            async with httpx.AsyncClient(timeout=10) as client:
                response = await client.get("https://api.alternative.me/fng/")
                data = response.json()

                if "data" in data and len(data["data"]) > 0:
                    fng_data = data["data"][0]
                    return FearGreedIndex(
                        value=int(fng_data["value"]),
                        classification=fng_data["value_classification"],
                        timestamp=datetime.now().isoformat()
                    )

        except Exception as e:
            logger.error(f"Failed to fetch Fear & Greed Index: {e}")

        # Return neutral value on failure
        return FearGreedIndex(
            value=50,
            classification="Neutral",
            timestamp=datetime.now().isoformat()
        )

    async def fetch_sentiment(self) -> SentimentData:
        """Fetch sentiment data"""
        fear_greed = await self.fetch_fear_greed_index()

        # Create overall sentiment based on Fear & Greed
        if fear_greed.value >= 75:
            sentiment = "extreme_greed"
            score = fear_greed.value
        elif fear_greed.value >= 55:
            sentiment = "bullish"
            score = fear_greed.value
        elif fear_greed.value >= 45:
            sentiment = "neutral"
            score = fear_greed.value
        elif fear_greed.value >= 25:
            sentiment = "bearish"
            score = fear_greed.value
        else:
            sentiment = "extreme_fear"
            score = fear_greed.value

        return SentimentData(
            fearGreed=fear_greed,
            news=NewsSentiment(total=0),
            overall=OverallSentiment(
                sentiment=sentiment,
                score=score,
                confidence=0.8
            )
        )

    async def fetch_market_overview(self) -> MarketOverview:
        """Fetch market overview data"""
        try:
            market_data = await self.market_provider.fetch_market_data()

            return MarketOverview(
                totalMarketCap=market_data.get("total_market_cap", {}).get("usd", 0),
                totalVolume24h=market_data.get("total_volume", {}).get("usd", 0),
                btcDominance=market_data.get("market_cap_percentage", {}).get("btc", 0),
                ethDominance=market_data.get("market_cap_percentage", {}).get("eth", 0),
                activeCoins=market_data.get("active_cryptocurrencies", 0)
            )

        except Exception as e:
            logger.error(f"Failed to fetch market overview: {e}")
            # Return empty data on failure
            return MarketOverview(
                totalMarketCap=0,
                totalVolume24h=0,
                btcDominance=0,
                ethDominance=0,
                activeCoins=0
            )

    async def get_all_provider_health(self) -> List[ProviderHealth]:
        """Get health status of all providers"""
        all_providers = set(self.ohlcv_providers + self.price_providers + [self.market_provider])
        health_list = []

        for provider in all_providers:
            health = await provider.get_health()
            health_list.append(health)

        return health_list

    def get_uptime(self) -> int:
        """Get service uptime in seconds"""
        return int(time.time() - self.start_time)


# Global aggregator instance
aggregator: Optional[DataAggregator] = None


def get_aggregator() -> DataAggregator:
    """Get global aggregator instance"""
    global aggregator
    if aggregator is None:
        aggregator = DataAggregator()
    return aggregator
