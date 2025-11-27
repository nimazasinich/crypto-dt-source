"""
CoinMarketCap Provider - Market data and cryptocurrency information

Provides:
- Latest cryptocurrency prices
- OHLCV historical data
- Market cap rankings
- Global market metrics

API Documentation: https://coinmarketcap.com/api/documentation/v1/
"""

from __future__ import annotations
from typing import Any, Dict, List, Optional

from .base import BaseProvider, create_success_response, create_error_response


class CoinMarketCapProvider(BaseProvider):
    """CoinMarketCap REST API provider for market data"""
    
    # API Key (temporary hardcoded - will be secured later)
    API_KEY = "a35ffaec-c66c-4f16-81e3-41a717e4822f"
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(
            name="coinmarketcap",
            base_url="https://pro-api.coinmarketcap.com/v1",
            api_key=api_key or self.API_KEY,
            timeout=10.0,
            cache_ttl=30.0
        )
    
    def _get_default_headers(self) -> Dict[str, str]:
        """Get headers with CMC API key"""
        return {
            "Accept": "application/json",
            "X-CMC_PRO_API_KEY": self.api_key
        }
    
    async def get_latest_listings(
        self,
        start: int = 1,
        limit: int = 50,
        convert: str = "USD",
        sort: str = "market_cap",
        sort_dir: str = "desc"
    ) -> Dict[str, Any]:
        """
        Get latest cryptocurrency listings with market data.
        
        Args:
            start: Starting rank (1-based)
            limit: Number of results (max 5000)
            convert: Currency to convert prices to
            sort: Sort field (market_cap, volume_24h, price, etc.)
            sort_dir: Sort direction (asc/desc)
        
        Returns:
            Standardized response with cryptocurrency list
        """
        params = {
            "start": start,
            "limit": min(limit, 100),  # Limit for performance
            "convert": convert.upper(),
            "sort": sort,
            "sort_dir": sort_dir
        }
        
        response = await self.get("cryptocurrency/listings/latest", params=params)
        
        if not response.get("success"):
            return response
        
        data = response.get("data", {})
        
        # CMC returns status + data structure
        if data.get("status", {}).get("error_code"):
            error_msg = data.get("status", {}).get("error_message", "Unknown error")
            return create_error_response(self.name, error_msg)
        
        cryptocurrencies = data.get("data", [])
        
        return create_success_response(
            self.name,
            {
                "cryptocurrencies": self._format_listings(cryptocurrencies, convert),
                "count": len(cryptocurrencies),
                "convert": convert
            }
        )
    
    def _format_listings(self, listings: List[Dict], convert: str = "USD") -> List[Dict]:
        """Format cryptocurrency listing data"""
        formatted = []
        for crypto in listings:
            quote = crypto.get("quote", {}).get(convert.upper(), {})
            formatted.append({
                "id": crypto.get("id"),
                "name": crypto.get("name"),
                "symbol": crypto.get("symbol"),
                "slug": crypto.get("slug"),
                "rank": crypto.get("cmc_rank"),
                "price": quote.get("price"),
                "volume24h": quote.get("volume_24h"),
                "volumeChange24h": quote.get("volume_change_24h"),
                "percentChange1h": quote.get("percent_change_1h"),
                "percentChange24h": quote.get("percent_change_24h"),
                "percentChange7d": quote.get("percent_change_7d"),
                "percentChange30d": quote.get("percent_change_30d"),
                "marketCap": quote.get("market_cap"),
                "marketCapDominance": quote.get("market_cap_dominance"),
                "fullyDilutedMarketCap": quote.get("fully_diluted_market_cap"),
                "circulatingSupply": crypto.get("circulating_supply"),
                "totalSupply": crypto.get("total_supply"),
                "maxSupply": crypto.get("max_supply"),
                "lastUpdated": quote.get("last_updated")
            })
        return formatted
    
    async def get_quotes(
        self,
        symbols: Optional[str] = None,
        ids: Optional[str] = None,
        convert: str = "USD"
    ) -> Dict[str, Any]:
        """
        Get price quotes for specific cryptocurrencies.
        
        Args:
            symbols: Comma-separated symbols (e.g., "BTC,ETH")
            ids: Comma-separated CMC IDs
            convert: Currency to convert prices to
        """
        if not symbols and not ids:
            return create_error_response(
                self.name,
                "Missing parameter",
                "Either 'symbols' or 'ids' is required"
            )
        
        params = {"convert": convert.upper()}
        if symbols:
            params["symbol"] = symbols.upper()
        if ids:
            params["id"] = ids
        
        response = await self.get("cryptocurrency/quotes/latest", params=params)
        
        if not response.get("success"):
            return response
        
        data = response.get("data", {})
        
        if data.get("status", {}).get("error_code"):
            error_msg = data.get("status", {}).get("error_message", "Unknown error")
            return create_error_response(self.name, error_msg)
        
        quotes_data = data.get("data", {})
        
        # Format quotes (can be dict keyed by symbol or id)
        quotes = []
        for key, crypto in quotes_data.items():
            if isinstance(crypto, list):
                crypto = crypto[0]  # Handle array response
            quote = crypto.get("quote", {}).get(convert.upper(), {})
            quotes.append({
                "id": crypto.get("id"),
                "name": crypto.get("name"),
                "symbol": crypto.get("symbol"),
                "price": quote.get("price"),
                "volume24h": quote.get("volume_24h"),
                "percentChange1h": quote.get("percent_change_1h"),
                "percentChange24h": quote.get("percent_change_24h"),
                "percentChange7d": quote.get("percent_change_7d"),
                "marketCap": quote.get("market_cap"),
                "lastUpdated": quote.get("last_updated")
            })
        
        return create_success_response(
            self.name,
            {
                "quotes": quotes,
                "count": len(quotes),
                "convert": convert
            }
        )
    
    async def get_global_metrics(self, convert: str = "USD") -> Dict[str, Any]:
        """Get global cryptocurrency market metrics"""
        params = {"convert": convert.upper()}
        
        response = await self.get("global-metrics/quotes/latest", params=params)
        
        if not response.get("success"):
            return response
        
        data = response.get("data", {})
        
        if data.get("status", {}).get("error_code"):
            error_msg = data.get("status", {}).get("error_message", "Unknown error")
            return create_error_response(self.name, error_msg)
        
        metrics = data.get("data", {})
        quote = metrics.get("quote", {}).get(convert.upper(), {})
        
        return create_success_response(
            self.name,
            {
                "activeCryptocurrencies": metrics.get("active_cryptocurrencies"),
                "totalCryptocurrencies": metrics.get("total_cryptocurrencies"),
                "activeExchanges": metrics.get("active_exchanges"),
                "totalExchanges": metrics.get("total_exchanges"),
                "activeMarketPairs": metrics.get("active_market_pairs"),
                "totalMarketCap": quote.get("total_market_cap"),
                "totalVolume24h": quote.get("total_volume_24h"),
                "totalVolume24hReported": quote.get("total_volume_24h_reported"),
                "altcoinMarketCap": quote.get("altcoin_market_cap"),
                "altcoinVolume24h": quote.get("altcoin_volume_24h"),
                "btcDominance": metrics.get("btc_dominance"),
                "ethDominance": metrics.get("eth_dominance"),
                "defiVolume24h": metrics.get("defi_volume_24h"),
                "defiMarketCap": metrics.get("defi_market_cap"),
                "stablecoinVolume24h": metrics.get("stablecoin_volume_24h"),
                "stablecoinMarketCap": metrics.get("stablecoin_market_cap"),
                "derivativesVolume24h": metrics.get("derivatives_volume_24h"),
                "lastUpdated": metrics.get("last_updated"),
                "convert": convert
            }
        )
    
    async def get_ohlcv_historical(
        self,
        symbol: str,
        time_period: str = "daily",
        count: int = 30,
        convert: str = "USD"
    ) -> Dict[str, Any]:
        """
        Get historical OHLCV data for a cryptocurrency.
        Note: This endpoint requires a paid plan on CMC.
        
        Args:
            symbol: Cryptocurrency symbol (e.g., "BTC")
            time_period: "daily", "hourly", "weekly", "monthly"
            count: Number of periods to return
            convert: Currency to convert values to
        """
        params = {
            "symbol": symbol.upper(),
            "time_period": time_period,
            "count": min(count, 100),
            "convert": convert.upper()
        }
        
        response = await self.get("cryptocurrency/ohlcv/historical", params=params)
        
        if not response.get("success"):
            # Return graceful fallback for free tier
            return create_error_response(
                self.name,
                "OHLCV historical data requires paid plan",
                "Consider using alternative providers for OHLCV data"
            )
        
        data = response.get("data", {})
        
        if data.get("status", {}).get("error_code"):
            error_msg = data.get("status", {}).get("error_message", "Unknown error")
            return create_error_response(self.name, error_msg)
        
        crypto_data = data.get("data", {})
        quotes = crypto_data.get("quotes", [])
        
        ohlcv = []
        for q in quotes:
            quote = q.get("quote", {}).get(convert.upper(), {})
            ohlcv.append({
                "timestamp": q.get("time_open"),
                "open": quote.get("open"),
                "high": quote.get("high"),
                "low": quote.get("low"),
                "close": quote.get("close"),
                "volume": quote.get("volume"),
                "marketCap": quote.get("market_cap")
            })
        
        return create_success_response(
            self.name,
            {
                "symbol": symbol.upper(),
                "timePeriod": time_period,
                "ohlcv": ohlcv,
                "count": len(ohlcv),
                "convert": convert
            }
        )
    
    async def get_map(self, limit: int = 100) -> Dict[str, Any]:
        """Get CMC ID map for cryptocurrencies"""
        params = {
            "listing_status": "active",
            "start": 1,
            "limit": min(limit, 5000),
            "sort": "cmc_rank"
        }
        
        response = await self.get("cryptocurrency/map", params=params)
        
        if not response.get("success"):
            return response
        
        data = response.get("data", {})
        
        if data.get("status", {}).get("error_code"):
            error_msg = data.get("status", {}).get("error_message", "Unknown error")
            return create_error_response(self.name, error_msg)
        
        crypto_map = data.get("data", [])
        
        formatted = []
        for crypto in crypto_map:
            formatted.append({
                "id": crypto.get("id"),
                "name": crypto.get("name"),
                "symbol": crypto.get("symbol"),
                "slug": crypto.get("slug"),
                "rank": crypto.get("rank"),
                "isActive": crypto.get("is_active"),
                "platform": crypto.get("platform")
            })
        
        return create_success_response(
            self.name,
            {
                "cryptocurrencies": formatted,
                "count": len(formatted)
            }
        )
