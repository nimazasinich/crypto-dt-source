#!/usr/bin/env python3
"""
Binance Public API Client - REAL DATA ONLY
Fetches real OHLCV historical data from Binance
NO MOCK DATA - All data from live Binance API
"""

import httpx
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import HTTPException

logger = logging.getLogger(__name__)


class BinanceClient:
    """
    Real Binance Public API Client
    Primary source for real historical OHLCV candlestick data
    """
    
    def __init__(self):
        self.base_url = "https://api.binance.com/api/v3"
        self.timeout = 15.0
        
        # Timeframe mapping
        self.timeframe_map = {
            "1m": "1m",
            "5m": "5m",
            "15m": "15m",
            "30m": "30m",
            "1h": "1h",
            "4h": "4h",
            "1d": "1d",
            "1w": "1w"
        }
    
    def _normalize_symbol(self, symbol: str) -> str:
        """Normalize symbol to Binance format (e.g., BTC -> BTCUSDT)"""
        symbol = symbol.upper().strip()
        
        # If already has USDT suffix, return as is
        if symbol.endswith("USDT"):
            return symbol
        
        # Add USDT suffix
        return f"{symbol}USDT"
    
    async def get_ohlcv(
        self,
        symbol: str,
        timeframe: str = "1h",
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        Fetch REAL OHLCV candlestick data from Binance
        
        Args:
            symbol: Cryptocurrency symbol (e.g., "BTC", "ETH", "BTCUSDT")
            timeframe: Time interval (1m, 5m, 15m, 30m, 1h, 4h, 1d, 1w)
            limit: Maximum number of candles (max 1000)
        
        Returns:
            List of real OHLCV candles
        """
        try:
            # Normalize symbol
            binance_symbol = self._normalize_symbol(symbol)
            
            # Map timeframe
            binance_interval = self.timeframe_map.get(timeframe, "1h")
            
            # Limit to max 1000
            limit = min(limit, 1000)
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/klines",
                    params={
                        "symbol": binance_symbol,
                        "interval": binance_interval,
                        "limit": limit
                    }
                )
                response.raise_for_status()
                klines = response.json()
                
                # Transform Binance format to standard OHLCV format
                ohlcv_data = []
                for kline in klines:
                    # Binance kline format:
                    # [timestamp, open, high, low, close, volume, ...]
                    timestamp = int(kline[0])
                    open_price = float(kline[1])
                    high_price = float(kline[2])
                    low_price = float(kline[3])
                    close_price = float(kline[4])
                    volume = float(kline[5])
                    
                    # Filter out invalid candles
                    if open_price > 0 and close_price > 0:
                        ohlcv_data.append({
                            "timestamp": timestamp,
                            "open": open_price,
                            "high": high_price,
                            "low": low_price,
                            "close": close_price,
                            "volume": volume
                        })
                
                logger.info(
                    f"✅ Binance: Fetched {len(ohlcv_data)} real candles "
                    f"for {binance_symbol} ({timeframe})"
                )
                return ohlcv_data
        
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 400:
                logger.error(f"❌ Binance: Invalid symbol or parameters: {symbol}")
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid symbol or parameters: {symbol}"
                )
            elif e.response.status_code == 404:
                logger.error(f"❌ Binance: Symbol not found: {binance_symbol}")
                raise HTTPException(
                    status_code=404,
                    detail=f"Symbol not found on Binance: {symbol}"
                )
            elif e.response.status_code == 451:
                logger.warning(
                    f"⚠️ Binance: HTTP 451 - Access restricted (geo-blocking or legal restrictions) for {binance_symbol}. "
                    f"Consider using alternative data sources or VPN."
                )
                raise HTTPException(
                    status_code=451,
                    detail=f"Binance API access restricted for your region. Please use alternative data sources (CoinGecko, CoinMarketCap)."
                )
            else:
                logger.error(f"❌ Binance API HTTP error: {e}")
                raise HTTPException(
                    status_code=503,
                    detail=f"Binance API temporarily unavailable: {str(e)}"
                )
        except httpx.HTTPError as e:
            logger.error(f"❌ Binance API HTTP error: {e}")
            raise HTTPException(
                status_code=503,
                detail=f"Binance API temporarily unavailable: {str(e)}"
            )
        except Exception as e:
            logger.error(f"❌ Binance API failed: {e}")
            raise HTTPException(
                status_code=503,
                detail=f"Failed to fetch real OHLCV data from Binance: {str(e)}"
            )
    
    async def get_24h_ticker(self, symbol: str) -> Dict[str, Any]:
        """
        Fetch REAL 24-hour ticker price change statistics
        
        Args:
            symbol: Cryptocurrency symbol (e.g., "BTC", "ETH")
        
        Returns:
            Real 24-hour ticker data
        """
        try:
            binance_symbol = self._normalize_symbol(symbol)
            
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(
                    f"{self.base_url}/ticker/24hr",
                    params={"symbol": binance_symbol}
                )
                response.raise_for_status()
                data = response.json()
                
                # Transform to standard format
                ticker = {
                    "symbol": symbol.upper().replace("USDT", ""),
                    "price": float(data.get("lastPrice", 0)),
                    "change24h": float(data.get("priceChange", 0)),
                    "changePercent24h": float(data.get("priceChangePercent", 0)),
                    "volume24h": float(data.get("volume", 0)),
                    "high24h": float(data.get("highPrice", 0)),
                    "low24h": float(data.get("lowPrice", 0)),
                    "source": "binance",
                    "timestamp": int(datetime.utcnow().timestamp() * 1000)
                }
                
                logger.info(f"✅ Binance: Fetched real 24h ticker for {binance_symbol}")
                return ticker
        
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 451:
                logger.warning(
                    f"⚠️ Binance: HTTP 451 - Access restricted (geo-blocking or legal restrictions). "
                    f"Consider using alternative data sources."
                )
                raise HTTPException(
                    status_code=451,
                    detail=f"Binance API access restricted for your region. Please use alternative data sources (CoinGecko, CoinMarketCap)."
                )
            logger.error(f"❌ Binance ticker error: {e}")
            raise HTTPException(
                status_code=503,
                detail=f"Failed to fetch ticker from Binance: {str(e)}"
            )
        except Exception as e:
            logger.error(f"❌ Binance ticker failed: {e}")
            raise HTTPException(
                status_code=503,
                detail=f"Failed to fetch real ticker data: {str(e)}"
            )


# Global instance
binance_client = BinanceClient()


__all__ = ["BinanceClient", "binance_client"]
