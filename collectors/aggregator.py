"""Async collectors that power the FastAPI endpoints."""

from __future__ import annotations

import asyncio
import json
import logging
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx

from config import CACHE_TTL, COIN_SYMBOL_MAPPING, USER_AGENT, get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class CollectorError(RuntimeError):
    """Raised when a provider fails to return data."""

    def __init__(self, message: str, provider: Optional[str] = None, status_code: Optional[int] = None):
        super().__init__(message)
        self.provider = provider
        self.status_code = status_code


@dataclass
class CacheEntry:
    value: Any
    expires_at: float


class TTLCache:
    """Simple in-memory TTL cache safe for async usage."""

    def __init__(self, ttl: int = CACHE_TTL) -> None:
        self.ttl = ttl or CACHE_TTL
        self._store: Dict[str, CacheEntry] = {}
        self._lock = asyncio.Lock()

    async def get(self, key: str) -> Any:
        async with self._lock:
            entry = self._store.get(key)
            if not entry:
                return None
            if entry.expires_at < time.time():
                self._store.pop(key, None)
                return None
            return entry.value

    async def set(self, key: str, value: Any) -> None:
        async with self._lock:
            self._store[key] = CacheEntry(value=value, expires_at=time.time() + self.ttl)


class ProvidersRegistry:
    """Utility that loads provider definitions from disk."""

    def __init__(self, path: Optional[Path] = None) -> None:
        self.path = Path(path or settings.providers_config_path)
        self._providers: Dict[str, Any] = {}
        self._load()

    def _load(self) -> None:
        if not self.path.exists():
            logger.warning("Providers config not found at %s", self.path)
            self._providers = {}
            return
        with self.path.open("r", encoding="utf-8") as handle:
            data = json.load(handle)
        self._providers = data.get("providers", {})

    @property
    def providers(self) -> Dict[str, Any]:
        return self._providers


class MarketDataCollector:
    """Fetch market data from public providers with caching and fallbacks."""

    def __init__(self, registry: Optional[ProvidersRegistry] = None) -> None:
        self.registry = registry or ProvidersRegistry()
        self.cache = TTLCache(settings.cache_ttl)
        self._symbol_map = {symbol.lower(): coin_id for coin_id, symbol in COIN_SYMBOL_MAPPING.items()}
        self.headers = {"User-Agent": settings.user_agent or USER_AGENT}
        self.timeout = 15.0

    async def _request(self, provider_key: str, path: str, params: Optional[Dict[str, Any]] = None) -> Any:
        provider = self.registry.providers.get(provider_key)
        if not provider:
            raise CollectorError(f"Provider {provider_key} not configured", provider=provider_key)

        url = provider["base_url"].rstrip("/") + path
        async with httpx.AsyncClient(timeout=self.timeout, headers=self.headers) as client:
            response = await client.get(url, params=params)
        if response.status_code != 200:
            raise CollectorError(
                f"{provider_key} request failed with HTTP {response.status_code}",
                provider=provider_key,
                status_code=response.status_code,
            )
        return response.json()

    async def get_top_coins(self, limit: int = 10) -> List[Dict[str, Any]]:
        cache_key = f"top_coins:{limit}"
        cached = await self.cache.get(cache_key)
        if cached:
            return cached

        providers = ["coingecko", "coincap"]
        last_error: Optional[Exception] = None
        for provider in providers:
            try:
                if provider == "coingecko":
                    data = await self._request(
                        "coingecko",
                        "/coins/markets",
                        {
                            "vs_currency": "usd",
                            "order": "market_cap_desc",
                            "per_page": limit,
                            "page": 1,
                            "sparkline": "false",
                            "price_change_percentage": "24h",
                        },
                    )
                    coins = [
                        {
                            "name": item.get("name"),
                            "symbol": item.get("symbol", "").upper(),
                            "price": item.get("current_price"),
                            "change_24h": item.get("price_change_percentage_24h"),
                            "market_cap": item.get("market_cap"),
                            "volume_24h": item.get("total_volume"),
                            "rank": item.get("market_cap_rank"),
                            "last_updated": item.get("last_updated"),
                        }
                        for item in data
                    ]
                    await self.cache.set(cache_key, coins)
                    return coins

                if provider == "coincap":
                    data = await self._request("coincap", "/assets", {"limit": limit})
                    coins = [
                        {
                            "name": item.get("name"),
                            "symbol": item.get("symbol", "").upper(),
                            "price": float(item.get("priceUsd", 0)),
                            "change_24h": float(item.get("changePercent24Hr", 0)),
                            "market_cap": float(item.get("marketCapUsd", 0)),
                            "volume_24h": float(item.get("volumeUsd24Hr", 0)),
                            "rank": int(item.get("rank", 0)),
                        }
                        for item in data.get("data", [])
                    ]
                    await self.cache.set(cache_key, coins)
                    return coins
            except Exception as exc:  # pragma: no cover - network heavy
                last_error = exc
                logger.warning("Provider %s failed: %s", provider, exc)

        raise CollectorError("Unable to fetch top coins", provider=str(last_error))

    async def _coin_id(self, symbol: str) -> str:
        symbol_lower = symbol.lower()
        if symbol_lower in self._symbol_map:
            return self._symbol_map[symbol_lower]

        cache_key = "coingecko:symbols"
        cached = await self.cache.get(cache_key)
        if cached:
            mapping = cached
        else:
            data = await self._request("coingecko", "/coins/list")
            mapping = {item["symbol"].lower(): item["id"] for item in data}
            await self.cache.set(cache_key, mapping)

        if symbol_lower not in mapping:
            raise CollectorError(f"Unknown symbol: {symbol}")

        return mapping[symbol_lower]

    async def get_coin_details(self, symbol: str) -> Dict[str, Any]:
        coin_id = await self._coin_id(symbol)
        cache_key = f"coin:{coin_id}"
        cached = await self.cache.get(cache_key)
        if cached:
            return cached

        data = await self._request(
            "coingecko",
            f"/coins/{coin_id}",
            {"localization": "false", "tickers": "false", "market_data": "true"},
        )
        market_data = data.get("market_data", {})
        coin = {
            "id": coin_id,
            "name": data.get("name"),
            "symbol": data.get("symbol", "").upper(),
            "description": data.get("description", {}).get("en"),
            "homepage": data.get("links", {}).get("homepage", [None])[0],
            "price": market_data.get("current_price", {}).get("usd"),
            "market_cap": market_data.get("market_cap", {}).get("usd"),
            "volume_24h": market_data.get("total_volume", {}).get("usd"),
            "change_24h": market_data.get("price_change_percentage_24h"),
            "circulating_supply": market_data.get("circulating_supply"),
            "total_supply": market_data.get("total_supply"),
            "ath": market_data.get("ath", {}).get("usd"),
            "atl": market_data.get("atl", {}).get("usd"),
            "last_updated": data.get("last_updated"),
        }
        await self.cache.set(cache_key, coin)
        return coin

    async def get_market_stats(self) -> Dict[str, Any]:
        cache_key = "market:stats"
        cached = await self.cache.get(cache_key)
        if cached:
            return cached

        global_data = await self._request("coingecko", "/global")
        stats = global_data.get("data", {})
        market = {
            "total_market_cap": stats.get("total_market_cap", {}).get("usd"),
            "total_volume_24h": stats.get("total_volume", {}).get("usd"),
            "market_cap_change_percentage_24h": stats.get("market_cap_change_percentage_24h_usd"),
            "btc_dominance": stats.get("market_cap_percentage", {}).get("btc"),
            "eth_dominance": stats.get("market_cap_percentage", {}).get("eth"),
            "active_cryptocurrencies": stats.get("active_cryptocurrencies"),
            "markets": stats.get("markets"),
            "updated_at": stats.get("updated_at"),
        }
        await self.cache.set(cache_key, market)
        return market

    async def get_price_history(self, symbol: str, timeframe: str = "7d") -> List[Dict[str, Any]]:
        coin_id = await self._coin_id(symbol)
        mapping = {"1d": 1, "7d": 7, "30d": 30, "90d": 90}
        days = mapping.get(timeframe, 7)
        cache_key = f"history:{coin_id}:{days}"
        cached = await self.cache.get(cache_key)
        if cached:
            return cached

        data = await self._request(
            "coingecko",
            f"/coins/{coin_id}/market_chart",
            {"vs_currency": "usd", "days": days},
        )
        prices = [
            {
                "timestamp": datetime.fromtimestamp(point[0] / 1000, tz=timezone.utc).isoformat(),
                "price": round(point[1], 4),
            }
            for point in data.get("prices", [])
        ]
        await self.cache.set(cache_key, prices)
        return prices


class NewsCollector:
    """Fetch latest crypto news."""

    def __init__(self, registry: Optional[ProvidersRegistry] = None) -> None:
        self.registry = registry or ProvidersRegistry()
        self.cache = TTLCache(settings.cache_ttl)
        self.headers = {"User-Agent": settings.user_agent or USER_AGENT}
        self.timeout = 15.0

    async def get_latest_news(self, limit: int = 10) -> List[Dict[str, Any]]:
        cache_key = f"news:{limit}"
        cached = await self.cache.get(cache_key)
        if cached:
            return cached

        url = "https://min-api.cryptocompare.com/data/v2/news/"
        params = {"lang": "EN"}
        async with httpx.AsyncClient(timeout=self.timeout, headers=self.headers) as client:
            response = await client.get(url, params=params)
        if response.status_code != 200:
            raise CollectorError(f"News provider error: HTTP {response.status_code}")

        payload = response.json()
        items = []
        for entry in payload.get("Data", [])[:limit]:
            published = datetime.fromtimestamp(entry.get("published_on", 0), tz=timezone.utc)
            items.append(
                {
                    "id": entry.get("id"),
                    "title": entry.get("title"),
                    "body": entry.get("body"),
                    "url": entry.get("url"),
                    "source": entry.get("source"),
                    "categories": entry.get("categories"),
                    "published_at": published.isoformat(),
                }
            )

        await self.cache.set(cache_key, items)
        return items


class ProviderStatusCollector:
    """Perform lightweight health checks against configured providers."""

    def __init__(self, registry: Optional[ProvidersRegistry] = None) -> None:
        self.registry = registry or ProvidersRegistry()
        self.cache = TTLCache(max(settings.cache_ttl, 600))
        self.headers = {"User-Agent": settings.user_agent or USER_AGENT}
        self.timeout = 8.0

    async def _check_provider(self, client: httpx.AsyncClient, provider_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        url = data.get("health_check") or data.get("base_url")
        start = time.perf_counter()
        try:
            response = await client.get(url, timeout=self.timeout)
            latency = round((time.perf_counter() - start) * 1000, 2)
            status = "online" if response.status_code < 400 else "degraded"
            return {
                "provider_id": provider_id,
                "name": data.get("name", provider_id),
                "category": data.get("category"),
                "status": status,
                "status_code": response.status_code,
                "latency_ms": latency,
            }
        except Exception as exc:  # pragma: no cover - network heavy
            logger.warning("Provider %s health check failed: %s", provider_id, exc)
            return {
                "provider_id": provider_id,
                "name": data.get("name", provider_id),
                "category": data.get("category"),
                "status": "offline",
                "status_code": None,
                "latency_ms": None,
                "error": str(exc),
            }

    async def get_providers_status(self) -> List[Dict[str, Any]]:
        cached = await self.cache.get("providers_status")
        if cached:
            return cached

        providers = self.registry.providers
        if not providers:
            return []

        results: List[Dict[str, Any]] = []
        async with httpx.AsyncClient(timeout=self.timeout, headers=self.headers) as client:
            tasks = [self._check_provider(client, pid, data) for pid, data in providers.items()]
            for chunk in asyncio.as_completed(tasks):
                results.append(await chunk)

        await self.cache.set("providers_status", results)
        return results


__all__ = [
    "CollectorError",
    "MarketDataCollector",
    "NewsCollector",
    "ProviderStatusCollector",
]
