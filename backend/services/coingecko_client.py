#!/usr/bin/env python3
"""
CoinGecko API Client - REAL DATA ONLY
Fetches real cryptocurrency market data from CoinGecko
NO MOCK DATA - All data from live CoinGecko API
"""

import httpx
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import HTTPException

logger = logging.getLogger(__name__)


class CoinGeckoClient:
    """
    Real CoinGecko API Client
    Primary source for real-time cryptocurrency market prices
    """
    
    def __init__(self):
        self.base_url = "https://api.coingecko.com/api/v3"
        self.timeout = 15.0
        
        # Symbol to CoinGecko ID mapping
        self.symbol_to_id = {
            "BTC": "bitcoin",
            "ETH": "ethereum",
            "BNB": "binancecoin",
            "XRP": "ripple",
            "ADA": "cardano",
            "DOGE": "dogecoin",
            "SOL": "solana",
            "TRX": "tron",
            "DOT": "polkadot",
            "MATIC": "matic-network",
            "LTC": "litecoin",
            "SHIB": "shiba-inu",
            "AVAX": "avalanche-2",
            "UNI": "uniswap",
            "LINK": "chainlink",
            "ATOM": "cosmos",
            "XLM": "stellar",
            "ETC": "ethereum-classic",
            "XMR": "monero",
            "BCH": "bitcoin-cash"
        }
        
        # Reverse mapping
        self.id_to_symbol = {v: k for k, v in self.symbol_to_id.items()}
    
    def _symbol_to_coingecko_id(self, symbol: str) -> str:
        """Convert crypto symbol to CoinGecko coin ID"""
        symbol = symbol.upper().replace("USDT", "").replace("USD", "")
        return self.symbol_to_id.get(symbol, symbol.lower())
    
    def _coingecko_id_to_symbol(self, coin_id: str) -> str:
        """Convert CoinGecko coin ID to symbol"""
        return self.id_to_symbol.get(coin_id, coin_id.upper())
    
    async def get_market_prices(
        self,
        symbols: Optional[List[str]] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Fetch REAL market prices from CoinGecko
        
        Args:
            symbols: List of crypto symbols (e.g., ["BTC", "ETH"])
            limit: Maximum number of results
        
        Returns:
            List of real market data
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                if symbols:
                    # Get specific symbols using /simple/price endpoint
                    coin_ids = [self._symbol_to_coingecko_id(s) for s in symbols]
                    
                    response = await client.get(
                        f"{self.base_url}/simple/price",
                        params={
                            "ids": ",".join(coin_ids),
                            "vs_currencies": "usd",
                            "include_24hr_change": "true",
                            "include_24hr_vol": "true",
                            "include_market_cap": "true"
                        }
                    )
                    response.raise_for_status()
                    data = response.json()
                    
                    # Transform to standard format
                    prices = []
                    for coin_id, coin_data in data.items():
                        symbol = self._coingecko_id_to_symbol(coin_id)
                        prices.append({
                            "symbol": symbol,
                            "name": symbol,  # CoinGecko simple/price doesn't include name
                            "price": coin_data.get("usd", 0),
                            "change24h": coin_data.get("usd_24h_change", 0),
                            "changePercent24h": coin_data.get("usd_24h_change", 0),
                            "volume24h": coin_data.get("usd_24h_vol", 0),
                            "marketCap": coin_data.get("usd_market_cap", 0),
                            "source": "coingecko",
                            "timestamp": int(datetime.utcnow().timestamp() * 1000)
                        })
                    
                    logger.info(f"✅ CoinGecko: Fetched {len(prices)} real prices for specific symbols")
                    return prices
                
                else:
                    # Get top coins by market cap using /coins/markets endpoint
                    response = await client.get(
                        f"{self.base_url}/coins/markets",
                        params={
                            "vs_currency": "usd",
                            "order": "market_cap_desc",
                            "per_page": min(limit, 250),
                            "page": 1,
                            "sparkline": "false",
                            "price_change_percentage": "24h"
                        }
                    )
                    response.raise_for_status()
                    data = response.json()
                    
                    # Transform to standard format
                    prices = []
                    for coin in data:
                        prices.append({
                            "symbol": coin.get("symbol", "").upper(),
                            "name": coin.get("name", ""),
                            "price": coin.get("current_price", 0),
                            "change24h": coin.get("price_change_24h", 0),
                            "changePercent24h": coin.get("price_change_percentage_24h", 0),
                            "volume24h": coin.get("total_volume", 0),
                            "marketCap": coin.get("market_cap", 0),
                            "source": "coingecko",
                            "timestamp": int(datetime.utcnow().timestamp() * 1000)
                        })
                    
                    logger.info(f"✅ CoinGecko: Fetched {len(prices)} real market prices")
                    return prices
        
        except httpx.HTTPError as e:
            logger.error(f"❌ CoinGecko API HTTP error: {e}")
            raise HTTPException(
                status_code=503,
                detail=f"CoinGecko API temporarily unavailable: {str(e)}"
            )
        except Exception as e:
            logger.error(f"❌ CoinGecko API failed: {e}")
            raise HTTPException(
                status_code=503,
                detail=f"Failed to fetch real market data from CoinGecko: {str(e)}"
            )
    
    async def get_ohlcv(self, symbol: str, days: int = 7) -> Dict[str, Any]:
        """
        Fetch REAL OHLCV (price history) data from CoinGecko
        
        Args:
            symbol: Cryptocurrency symbol (e.g., "BTC", "ETH")
            days: Number of days of historical data (1, 7, 14, 30, 90, 180, 365, max)
        
        Returns:
            Dict with OHLCV data
        """
        try:
            coin_id = self._symbol_to_coingecko_id(symbol)
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Get market chart (OHLC) data
                response = await client.get(
                    f"{self.base_url}/coins/{coin_id}/market_chart",
                    params={
                        "vs_currency": "usd",
                        "days": str(days),
                        "interval": "daily" if days > 1 else "hourly"
                    }
                )
                response.raise_for_status()
                data = response.json()
                
                logger.info(f"✅ CoinGecko: Fetched {days} days of OHLCV data for {symbol}")
                return data
        
        except httpx.HTTPError as e:
            logger.error(f"❌ CoinGecko OHLCV API HTTP error: {e}")
            raise HTTPException(
                status_code=503,
                detail=f"CoinGecko OHLCV API unavailable: {str(e)}"
            )
        except Exception as e:
            logger.error(f"❌ CoinGecko OHLCV API failed: {e}")
            raise HTTPException(
                status_code=503,
                detail=f"Failed to fetch OHLCV data from CoinGecko: {str(e)}"
            )
    
    async def get_trending_coins(self, limit: int = 10) -> List[Dict[str, Any]]:
        """
        Fetch REAL trending coins from CoinGecko
        
        Returns:
            List of real trending coins
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                # Get trending coins
                response = await client.get(f"{self.base_url}/search/trending")
                response.raise_for_status()
                data = response.json()
                
                trending = []
                coins = data.get("coins", [])[:limit]
                
                # Get price data for trending coins
                if coins:
                    coin_ids = [coin["item"]["id"] for coin in coins]
                    
                    # Fetch current prices
                    price_response = await client.get(
                        f"{self.base_url}/simple/price",
                        params={
                            "ids": ",".join(coin_ids),
                            "vs_currencies": "usd",
                            "include_24hr_change": "true"
                        }
                    )
                    price_response.raise_for_status()
                    price_data = price_response.json()
                    
                    for idx, coin_obj in enumerate(coins):
                        coin = coin_obj["item"]
                        coin_id = coin["id"]
                        prices = price_data.get(coin_id, {})
                        
                        trending.append({
                            "symbol": coin.get("symbol", "").upper(),
                            "name": coin.get("name", ""),
                            "rank": idx + 1,
                            "price": prices.get("usd", 0),
                            "change24h": prices.get("usd_24h_change", 0),
                            "marketCapRank": coin.get("market_cap_rank", 0),
                            "source": "coingecko",
                            "timestamp": int(datetime.utcnow().timestamp() * 1000)
                        })
                
                logger.info(f"✅ CoinGecko: Fetched {len(trending)} real trending coins")
                return trending
        
        except httpx.HTTPError as e:
            logger.error(f"❌ CoinGecko trending API HTTP error: {e}")
            raise HTTPException(
                status_code=503,
                detail=f"CoinGecko trending API unavailable: {str(e)}"
            )
        except Exception as e:
            logger.error(f"❌ CoinGecko trending API failed: {e}")
            raise HTTPException(
                status_code=503,
                detail=f"Failed to fetch trending coins: {str(e)}"
            )


# Global instance
coingecko_client = CoinGeckoClient()


__all__ = ["CoinGeckoClient", "coingecko_client"]
