"""
Market Data REST API Router

Endpoints:
- GET /api/v1/market/latest - Latest cryptocurrency listings
- GET /api/v1/market/quotes - Price quotes for specific symbols
- GET /api/v1/market/global - Global market metrics
- GET /api/v1/market/ohlcv - Historical OHLCV data

Data source: CoinMarketCap API
All endpoints return standardized JSON with {success, source, data} format.
"""

from __future__ import annotations

import logging
from typing import Optional

from fastapi import APIRouter, HTTPException, Query
from providers.coinmarketcap_provider import CoinMarketCapProvider

# Configure logging
logger = logging.getLogger("routers.market")

# Create router
router = APIRouter(prefix="/api/v1/market", tags=["Market Data"])

# Provider instance (singleton)
_cmc_provider: Optional[CoinMarketCapProvider] = None


def get_cmc_provider() -> CoinMarketCapProvider:
    """Get or create CoinMarketCap provider instance"""
    global _cmc_provider
    if _cmc_provider is None:
        _cmc_provider = CoinMarketCapProvider()
    return _cmc_provider


# ============================================================================
# MARKET DATA ENDPOINTS
# ============================================================================


@router.get("/latest")
async def get_latest_listings(
    limit: int = Query(50, ge=1, le=100, description="Number of cryptocurrencies (max 100)"),
    start: int = Query(1, ge=1, description="Starting rank"),
    convert: str = Query("USD", description="Currency to convert prices to"),
    sort: str = Query("market_cap", description="Sort field (market_cap, volume_24h, price)"),
    sort_dir: str = Query("desc", description="Sort direction (asc, desc)"),
):
    """
    Get latest cryptocurrency listings with market data.

    Returns top cryptocurrencies ranked by market cap including:
    - Price, volume, market cap
    - 1h, 24h, 7d, 30d price changes
    - Supply information
    - CMC ranking

    Example: /api/v1/market/latest?limit=50
    """
    provider = get_cmc_provider()

    try:
        result = await provider.get_latest_listings(
            start=start, limit=limit, convert=convert.upper(), sort=sort, sort_dir=sort_dir
        )
        return result
    except Exception as e:
        logger.error(f"Latest listings error: {e}")
        return {
            "success": False,
            "source": "coinmarketcap",
            "error": "Failed to fetch market listings",
            "details": str(e),
        }


@router.get("/quotes")
async def get_price_quotes(
    symbols: Optional[str] = Query(None, description="Comma-separated symbols (e.g., BTC,ETH,SOL)"),
    ids: Optional[str] = Query(None, description="Comma-separated CMC IDs"),
    convert: str = Query("USD", description="Currency to convert to"),
):
    """
    Get price quotes for specific cryptocurrencies.

    Use either symbols or ids parameter.

    Examples:
    - /api/v1/market/quotes?symbols=BTC,ETH,SOL
    - /api/v1/market/quotes?ids=1,1027,5426
    """
    if not symbols and not ids:
        return {
            "success": False,
            "source": "coinmarketcap",
            "error": "Missing parameter",
            "details": "Either 'symbols' or 'ids' query parameter is required",
        }

    provider = get_cmc_provider()

    try:
        result = await provider.get_quotes(symbols=symbols, ids=ids, convert=convert.upper())
        return result
    except Exception as e:
        logger.error(f"Quotes error: {e}")
        return {
            "success": False,
            "source": "coinmarketcap",
            "error": "Failed to fetch price quotes",
            "details": str(e),
        }


@router.get("/global")
async def get_global_metrics(convert: str = Query("USD", description="Currency to convert to")):
    """
    Get global cryptocurrency market metrics.

    Returns:
    - Total market cap and 24h volume
    - Active cryptocurrencies and exchanges
    - BTC and ETH dominance
    - DeFi and stablecoin metrics
    """
    provider = get_cmc_provider()

    try:
        result = await provider.get_global_metrics(convert=convert.upper())
        return result
    except Exception as e:
        logger.error(f"Global metrics error: {e}")
        return {
            "success": False,
            "source": "coinmarketcap",
            "error": "Failed to fetch global metrics",
            "details": str(e),
        }


@router.get("/ohlcv")
async def get_ohlcv_data(
    symbol: str = Query(..., description="Cryptocurrency symbol (e.g., BTC, BTCUSDT)"),
    interval: str = Query("1h", description="Time interval (NOTE: CMC OHLCV requires paid plan)"),
    count: int = Query(30, ge=1, le=100, description="Number of data points"),
):
    """
    Get historical OHLCV (candlestick) data for a cryptocurrency.

    NOTE: CoinMarketCap OHLCV historical endpoint requires a paid API plan.
    For free OHLCV data, consider using the /api/ohlcv endpoint which uses
    free providers like Binance or CoinGecko.

    Returns OHLCV data with:
    - Open, High, Low, Close prices
    - Volume
    - Market cap (CMC-specific)
    """
    provider = get_cmc_provider()

    # Normalize symbol
    symbol_clean = symbol.upper().replace("USDT", "").replace("/", "")

    # Map interval to CMC time_period
    interval_map = {
        "1h": "hourly",
        "4h": "hourly",
        "1d": "daily",
        "daily": "daily",
        "1w": "weekly",
        "weekly": "weekly",
    }
    time_period = interval_map.get(interval, "daily")

    try:
        result = await provider.get_ohlcv_historical(
            symbol=symbol_clean, time_period=time_period, count=count
        )
        return result
    except Exception as e:
        logger.error(f"OHLCV error: {e}")
        return {
            "success": False,
            "source": "coinmarketcap",
            "error": "Failed to fetch OHLCV data",
            "details": str(e),
        }


@router.get("/map")
async def get_cryptocurrency_map(
    limit: int = Query(100, ge=1, le=500, description="Number of cryptocurrencies")
):
    """
    Get cryptocurrency ID map.

    Returns mapping of symbols to CMC IDs, useful for other API calls.
    """
    provider = get_cmc_provider()

    try:
        result = await provider.get_map(limit=limit)
        return result
    except Exception as e:
        logger.error(f"Map error: {e}")
        return {
            "success": False,
            "source": "coinmarketcap",
            "error": "Failed to fetch cryptocurrency map",
            "details": str(e),
        }


# ============================================================================
# CONVENIENCE ENDPOINTS
# ============================================================================


@router.get("/top")
async def get_top_cryptocurrencies(
    count: int = Query(10, ge=1, le=50, description="Number of top cryptos")
):
    """
    Convenience endpoint: Get top cryptocurrencies by market cap.

    Simplified response with just the essentials.
    """
    provider = get_cmc_provider()

    try:
        result = await provider.get_latest_listings(limit=count)

        if not result.get("success"):
            return result

        # Simplify the response
        cryptos = result.get("data", {}).get("cryptocurrencies", [])
        simplified = []
        for c in cryptos:
            simplified.append(
                {
                    "rank": c.get("rank"),
                    "symbol": c.get("symbol"),
                    "name": c.get("name"),
                    "price": c.get("price"),
                    "change24h": c.get("percentChange24h"),
                    "marketCap": c.get("marketCap"),
                    "volume24h": c.get("volume24h"),
                }
            )

        return {
            "success": True,
            "source": "coinmarketcap",
            "data": {"cryptocurrencies": simplified, "count": len(simplified)},
        }
    except Exception as e:
        logger.error(f"Top cryptos error: {e}")
        return {
            "success": False,
            "source": "coinmarketcap",
            "error": "Failed to fetch top cryptocurrencies",
            "details": str(e),
        }


@router.get("/price/{symbol}")
async def get_single_price(symbol: str, convert: str = Query("USD", description="Currency")):
    """
    Get price for a single cryptocurrency.

    Example: /api/v1/market/price/BTC
    """
    provider = get_cmc_provider()

    try:
        result = await provider.get_quotes(symbols=symbol.upper(), convert=convert.upper())

        if not result.get("success"):
            return result

        quotes = result.get("data", {}).get("quotes", [])
        if quotes:
            quote = quotes[0]
            return {
                "success": True,
                "source": "coinmarketcap",
                "data": {
                    "symbol": quote.get("symbol"),
                    "name": quote.get("name"),
                    "price": quote.get("price"),
                    "change24h": quote.get("percentChange24h"),
                    "volume24h": quote.get("volume24h"),
                    "marketCap": quote.get("marketCap"),
                    "lastUpdated": quote.get("lastUpdated"),
                },
            }
        else:
            return {
                "success": False,
                "source": "coinmarketcap",
                "error": f"Symbol '{symbol}' not found",
            }
    except Exception as e:
        logger.error(f"Single price error: {e}")
        return {
            "success": False,
            "source": "coinmarketcap",
            "error": "Failed to fetch price",
            "details": str(e),
        }


# ============================================================================
# HEALTH CHECK
# ============================================================================


@router.get("/health")
async def market_health():
    """Check health status of market data provider"""
    provider = get_cmc_provider()

    return {
        "success": True,
        "provider": {
            "name": provider.name,
            "baseUrl": provider.base_url,
            "timeout": provider.timeout,
        },
        "endpoints": [
            "/api/v1/market/latest",
            "/api/v1/market/quotes",
            "/api/v1/market/global",
            "/api/v1/market/ohlcv",
            "/api/v1/market/map",
            "/api/v1/market/top",
            "/api/v1/market/price/{symbol}",
        ],
    }
