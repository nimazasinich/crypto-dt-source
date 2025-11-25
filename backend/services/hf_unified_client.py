#!/usr/bin/env python3
"""
Hugging Face Unified Client
==================================
تمام درخواست‌ها از طریق این کلاینت به Hugging Face Space ارسال می‌شوند.
هیچ درخواست مستقیمی به API های خارجی ارسال نمی‌شود.

✅ تمام داده‌ها از Hugging Face
✅ بدون WebSocket (فقط HTTP)
✅ Cache و Retry مکانیزم
✅ Error Handling

References: crypto_resources_unified_2025-11-11.json
"""

import httpx
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import os
import hashlib
import json

logger = logging.getLogger(__name__)


class HuggingFaceUnifiedClient:
    """
    کلاینت یکپارچه برای تمام درخواست‌های به Hugging Face Space

    این کلاینت **تنها** منبع دریافت داده است و به جای API های دیگر،
    تمام داده‌ها را از Hugging Face Space دریافت می‌کند.
    """

    def __init__(self):
        """Initialize HuggingFace client with config"""
        self.base_url = os.getenv(
            "HF_SPACE_BASE_URL",
            "https://really-amin-datasourceforcryptocurrency.hf.space"
        )
        self.api_token = os.getenv("HF_API_TOKEN", "")
        self.timeout = httpx.Timeout(30.0, connect=10.0)

        # Request headers
        self.headers = {
            "Content-Type": "application/json",
            "User-Agent": "CryptoDataHub/1.0"
        }

        # Add auth token if available
        if self.api_token:
            self.headers["Authorization"] = f"Bearer {self.api_token}"

        # Cache configuration
        self.cache = {}
        self.cache_ttl = {
            "market": 30,      # 30 seconds
            "ohlcv": 60,       # 1 minute
            "news": 300,       # 5 minutes
            "sentiment": 0,    # No cache for sentiment
            "blockchain": 60,  # 1 minute
        }

        logger.info(f"🚀 HuggingFace Unified Client initialized")
        logger.info(f"   Base URL: {self.base_url}")
        logger.info(f"   Auth: {'✅ Token configured' if self.api_token else '❌ No token'}")

    def _get_cache_key(self, endpoint: str, params: Dict = None) -> str:
        """Generate cache key from endpoint and params"""
        cache_str = f"{endpoint}:{json.dumps(params or {}, sort_keys=True)}"
        return hashlib.md5(cache_str.encode()).hexdigest()

    def _get_cached(self, cache_key: str, cache_type: str) -> Optional[Dict]:
        """Get data from cache if available and not expired"""
        if cache_key not in self.cache:
            return None

        cached_data, cached_time = self.cache[cache_key]
        ttl = self.cache_ttl.get(cache_type, 0)

        if ttl == 0:
            # No caching
            return None

        age = (datetime.now() - cached_time).total_seconds()
        if age < ttl:
            logger.info(f"📦 Cache HIT: {cache_key} (age: {age:.1f}s)")
            return cached_data
        else:
            # Expired
            logger.info(f"⏰ Cache EXPIRED: {cache_key} (age: {age:.1f}s, ttl: {ttl}s)")
            del self.cache[cache_key]
            return None

    def _set_cache(self, cache_key: str, data: Dict, cache_type: str):
        """Store data in cache"""
        ttl = self.cache_ttl.get(cache_type, 0)
        if ttl > 0:
            self.cache[cache_key] = (data, datetime.now())
            logger.info(f"💾 Cache SET: {cache_key} (ttl: {ttl}s)")

    async def _request(
        self,
        method: str,
        endpoint: str,
        params: Optional[Dict] = None,
        json_body: Optional[Dict] = None,
        cache_type: Optional[str] = None,
        retry: int = 3
    ) -> Dict[str, Any]:
        """
        Make HTTP request to HuggingFace Space

        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint (e.g., "/api/market")
            params: Query parameters
            json_body: JSON body for POST requests
            cache_type: Type of cache ("market", "ohlcv", etc.)
            retry: Number of retry attempts

        Returns:
            Response data as dict
        """
        # Check cache first (only for GET requests)
        if method.upper() == "GET" and cache_type:
            cache_key = self._get_cache_key(endpoint, params)
            cached = self._get_cached(cache_key, cache_type)
            if cached:
                return cached

        # Build full URL
        url = f"{self.base_url}{endpoint}"

        # Make request with retry
        last_error = None
        for attempt in range(retry):
            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    if method.upper() == "GET":
                        response = await client.get(url, headers=self.headers, params=params)
                    elif method.upper() == "POST":
                        response = await client.post(url, headers=self.headers, json=json_body)
                    else:
                        raise ValueError(f"Unsupported HTTP method: {method}")

                    # Check status
                    response.raise_for_status()

                    # Parse JSON
                    data = response.json()

                    # Cache if applicable
                    if method.upper() == "GET" and cache_type:
                        cache_key = self._get_cache_key(endpoint, params)
                        self._set_cache(cache_key, data, cache_type)

                    logger.info(f"✅ HF Request: {method} {endpoint} (attempt {attempt + 1}/{retry})")
                    return data

            except httpx.HTTPStatusError as e:
                last_error = e
                logger.warning(f"❌ HF Request failed (attempt {attempt + 1}/{retry}): {e.response.status_code} - {e.response.text}")
                if attempt < retry - 1:
                    await asyncio.sleep(1 * (attempt + 1))  # Exponential backoff
            except Exception as e:
                last_error = e
                logger.error(f"❌ HF Request error (attempt {attempt + 1}/{retry}): {e}")
                if attempt < retry - 1:
                    await asyncio.sleep(1 * (attempt + 1))

        # All retries failed
        raise Exception(f"HuggingFace API request failed after {retry} attempts: {last_error}")

    # =========================================================================
    # Market Data Methods
    # =========================================================================

    async def get_market_prices(
        self,
        symbols: Optional[List[str]] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        دریافت قیمت‌های بازار از HuggingFace

        Endpoint: GET /api/market

        Args:
            symbols: لیست سمبل‌ها (مثلاً ['BTC', 'ETH'])
            limit: تعداد نتایج

        Returns:
            {
                "success": True,
                "data": [
                    {
                        "symbol": "BTC",
                        "price": 50000.0,
                        "market_cap": 1000000000.0,
                        "volume_24h": 50000000.0,
                        "change_24h": 2.5,
                        "last_updated": 1234567890000
                    },
                    ...
                ],
                "source": "hf_engine",
                "timestamp": 1234567890000,
                "cached": False
            }
        """
        params = {"limit": limit}
        if symbols:
            params["symbols"] = ",".join(symbols)

        return await self._request(
            "GET",
            "/api/market",
            params=params,
            cache_type="market"
        )

    async def get_market_history(
        self,
        symbol: str,
        timeframe: str = "1h",
        limit: int = 1000
    ) -> Dict[str, Any]:
        """
        دریافت داده‌های تاریخی OHLCV از HuggingFace

        Endpoint: GET /api/market/history

        Args:
            symbol: سمبل (مثلاً "BTCUSDT")
            timeframe: بازه زمانی ("1m", "5m", "15m", "1h", "4h", "1d")
            limit: تعداد کندل‌ها

        Returns:
            {
                "success": True,
                "data": [
                    {
                        "timestamp": 1234567890000,
                        "open": 50000.0,
                        "high": 51000.0,
                        "low": 49500.0,
                        "close": 50500.0,
                        "volume": 1000000.0
                    },
                    ...
                ],
                "source": "hf_engine",
                "timestamp": 1234567890000
            }
        """
        params = {
            "symbol": symbol,
            "timeframe": timeframe,
            "limit": limit
        }

        return await self._request(
            "GET",
            "/api/market/history",
            params=params,
            cache_type="ohlcv"
        )

    # =========================================================================
    # Sentiment Analysis Methods
    # =========================================================================

    async def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        تحلیل احساسات متن با مدل‌های AI در HuggingFace

        Endpoint: POST /api/sentiment/analyze

        Args:
            text: متن برای تحلیل

        Returns:
            {
                "success": True,
                "data": {
                    "label": "positive",
                    "score": 0.95,
                    "sentiment": "positive",
                    "confidence": 0.95,
                    "text": "Bitcoin is...",
                    "timestamp": 1234567890000
                },
                "source": "hf_engine",
                "timestamp": 1234567890000
            }
        """
        json_body = {"text": text}

        return await self._request(
            "POST",
            "/api/sentiment/analyze",
            json_body=json_body,
            cache_type=None  # No cache for sentiment
        )

    # =========================================================================
    # News Methods (از HuggingFace Space)
    # =========================================================================

    async def get_news(
        self,
        limit: int = 20,
        source: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        دریافت اخبار رمز ارز از HuggingFace

        Endpoint: GET /api/news

        Args:
            limit: تعداد خبر
            source: منبع خبر (اختیاری)

        Returns:
            {
                "articles": [
                    {
                        "id": "123",
                        "title": "Bitcoin reaches new high",
                        "url": "https://...",
                        "source": "CoinDesk",
                        "published_at": "2025-01-01T00:00:00"
                    },
                    ...
                ],
                "meta": {
                    "cache_ttl_seconds": 300,
                    "source": "hf"
                }
            }
        """
        params = {"limit": limit}
        if source:
            params["source"] = source

        return await self._request(
            "GET",
            "/api/news",
            params=params,
            cache_type="news"
        )

    # =========================================================================
    # Blockchain Explorer Methods (از HuggingFace Space)
    # =========================================================================

    async def get_blockchain_gas_prices(self, chain: str = "ethereum") -> Dict[str, Any]:
        """
        دریافت قیمت گس از HuggingFace

        Endpoint: GET /api/crypto/blockchain/gas

        Args:
            chain: نام بلاکچین (ethereum, bsc, polygon, etc.)

        Returns:
            {
                "chain": "ethereum",
                "gas_prices": {
                    "fast": 50.0,
                    "standard": 30.0,
                    "slow": 20.0,
                    "unit": "gwei"
                },
                "timestamp": "2025-01-01T00:00:00",
                "meta": {...}
            }
        """
        params = {"chain": chain}

        return await self._request(
            "GET",
            "/api/crypto/blockchain/gas",
            params=params,
            cache_type="blockchain"
        )

    async def get_blockchain_stats(
        self,
        chain: str = "ethereum",
        hours: int = 24
    ) -> Dict[str, Any]:
        """
        دریافت آمار بلاکچین از HuggingFace

        Endpoint: GET /api/crypto/blockchain/stats

        Args:
            chain: نام بلاکچین
            hours: بازه زمانی (ساعت)

        Returns:
            {
                "chain": "ethereum",
                "blocks_24h": 7000,
                "transactions_24h": 1200000,
                "avg_gas_price": 25.0,
                "mempool_size": 100000,
                "meta": {...}
            }
        """
        params = {"chain": chain, "hours": hours}

        return await self._request(
            "GET",
            "/api/crypto/blockchain/stats",
            params=params,
            cache_type="blockchain"
        )

    # =========================================================================
    # Whale Tracking Methods
    # =========================================================================

    async def get_whale_transactions(
        self,
        limit: int = 50,
        chain: Optional[str] = None,
        min_amount_usd: float = 100000
    ) -> Dict[str, Any]:
        """
        دریافت تراکنش‌های نهنگ‌ها از HuggingFace

        Endpoint: GET /api/crypto/whales/transactions
        """
        params = {
            "limit": limit,
            "min_amount_usd": min_amount_usd
        }
        if chain:
            params["chain"] = chain

        return await self._request(
            "GET",
            "/api/crypto/whales/transactions",
            params=params,
            cache_type="market"
        )

    async def get_whale_stats(self, hours: int = 24) -> Dict[str, Any]:
        """
        دریافت آمار نهنگ‌ها از HuggingFace

        Endpoint: GET /api/crypto/whales/stats
        """
        params = {"hours": hours}

        return await self._request(
            "GET",
            "/api/crypto/whales/stats",
            params=params,
            cache_type="market"
        )

    # =========================================================================
    # Health & Status Methods
    # =========================================================================

    async def health_check(self) -> Dict[str, Any]:
        """
        بررسی سلامت HuggingFace Space

        Endpoint: GET /api/health

        Returns:
            {
                "success": True,
                "status": "healthy",
                "timestamp": 1234567890000,
                "version": "1.0.0",
                "database": "connected",
                "cache": {
                    "market_data_count": 100,
                    "ohlc_count": 5000
                },
                "ai_models": {
                    "loaded": 3,
                    "failed": 0,
                    "total": 3
                },
                "source": "hf_engine"
            }
        """
        return await self._request(
            "GET",
            "/api/health",
            cache_type=None
        )

    async def get_system_status(self) -> Dict[str, Any]:
        """
        دریافت وضعیت کل سیستم

        Endpoint: GET /api/status
        """
        return await self._request(
            "GET",
            "/api/status",
            cache_type=None
        )


# Global singleton instance
_hf_client_instance = None


def get_hf_client() -> HuggingFaceUnifiedClient:
    """Get singleton instance of HuggingFace Unified Client"""
    global _hf_client_instance
    if _hf_client_instance is None:
        _hf_client_instance = HuggingFaceUnifiedClient()
    return _hf_client_instance
