#!/usr/bin/env python3
"""
CoinDesk API Client - Real cryptocurrency data and news
Uses CoinDesk API with authentication key for enhanced data access
"""

import httpx
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# CoinDesk API Key
COINDESK_API_KEY = "313f415173eb92928568d91eee6fd91d0c7569a56a9c7579181b7a083a740318"


class CoinDeskClient:
    """
    CoinDesk API Client for cryptocurrency prices and news
    """
    
    def __init__(self, api_key: str = COINDESK_API_KEY):
        self.base_url = "https://api.coindesk.com/v2"
        self.bpi_url = "https://api.coindesk.com/v1/bpi"  # Bitcoin Price Index
        # Fallback to alternate domain if main is unreachable
        self.fallback_bpi_url = "https://www.coindesk.com/api/v1/bpi"
        self.api_key = api_key
        self.timeout = 15.0
    
    async def get_bitcoin_price(self, currency: str = "USD") -> Dict[str, Any]:
        """
        Get current Bitcoin price from CoinDesk BPI (Bitcoin Price Index)
        With fallback to alternate endpoints
        
        Args:
            currency: Currency code (USD, EUR, GBP)
        
        Returns:
            Bitcoin price data from CoinDesk
        """
        # Try multiple endpoints
        urls = [
            f"{self.bpi_url}/currentprice/{currency}.json",
            f"{self.fallback_bpi_url}/currentprice/{currency}.json"
        ]
        
        last_error = None
        for url in urls:
            try:
                async with httpx.AsyncClient(
                    timeout=self.timeout,
                    follow_redirects=True
                ) as client:
                    headers = {}
                    if self.api_key:
                        headers["Authorization"] = f"Bearer {self.api_key}"
                    
                    response = await client.get(url, headers=headers)
                    response.raise_for_status()
                    data = response.json()
                
                    # Extract BPI data
                    bpi = data.get("bpi", {})
                    usd_data = bpi.get(currency, {})
                    
                    price = float(usd_data.get("rate_float", 0))
                    if price > 0:
                        result = {
                            "symbol": "BTC",
                            "price": price,
                            "currency": currency,
                            "rate": usd_data.get("rate", "0"),
                            "description": usd_data.get("description", ""),
                            "timestamp": data.get("time", {}).get("updatedISO", datetime.utcnow().isoformat()),
                            "source": "CoinDesk BPI"
                        }
                        
                        logger.info(f"✅ CoinDesk: Fetched BTC price: ${result['price']}")
                        return result
            
            except httpx.HTTPStatusError as e:
                last_error = f"HTTP {e.response.status_code}"
                logger.warning(f"⚠️ CoinDesk endpoint failed ({url}): {last_error}")
                continue
            except httpx.ConnectError as e:
                last_error = f"Connection error: {e}"
                logger.warning(f"⚠️ CoinDesk unreachable ({url}): {last_error}")
                continue
            except Exception as e:
                last_error = str(e)
                logger.warning(f"⚠️ CoinDesk endpoint failed ({url}): {last_error}")
                continue
        
        # All endpoints failed
        logger.error(f"❌ CoinDesk API failed (all endpoints): {last_error}")
        raise Exception(f"CoinDesk API unavailable: {last_error}")
    
    async def get_historical_prices(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get historical Bitcoin prices from CoinDesk
        
        Args:
            start_date: Start date (YYYY-MM-DD format)
            end_date: End date (YYYY-MM-DD format)
        
        Returns:
            Historical price data
        """
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                headers = {}
                if self.api_key:
                    headers["Authorization"] = f"Bearer {self.api_key}"
                
                params = {}
                if start_date:
                    params["start"] = start_date
                if end_date:
                    params["end"] = end_date
                
                response = await client.get(
                    f"{self.bpi_url}/historical/close.json",
                    params=params,
                    headers=headers
                )
                response.raise_for_status()
                data = response.json()
                
                logger.info(f"✅ CoinDesk: Fetched historical data")
                return data
        
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ CoinDesk historical API HTTP error: {e.response.status_code}")
            raise
        except Exception as e:
            logger.error(f"❌ CoinDesk historical API failed: {e}")
            raise
    
    async def get_market_data(self, symbols: List[str] = None) -> List[Dict[str, Any]]:
        """
        Get market data for cryptocurrencies
        Currently focuses on Bitcoin (CoinDesk's primary asset)
        
        Args:
            symbols: List of symbols (currently supports ["BTC"])
        
        Returns:
            List of market data
        """
        if not symbols:
            symbols = ["BTC"]
        
        results = []
        
        # CoinDesk primarily provides BTC data
        if "BTC" in [s.upper() for s in symbols]:
            try:
                btc_data = await self.get_bitcoin_price("USD")
                results.append({
                    "symbol": "BTC",
                    "name": "Bitcoin",
                    "price": btc_data.get("price", 0),
                    "currency": "USD",
                    "source": "CoinDesk",
                    "timestamp": btc_data.get("timestamp", ""),
                    "provider": "CoinDesk BPI"
                })
            except Exception as e:
                logger.warning(f"⚠️ CoinDesk BTC data failed: {e}")
        
        return results


# Global instance
coindesk_client = CoinDeskClient()


# Standalone functions for compatibility
async def fetch_coindesk_btc_price() -> float:
    """Get Bitcoin price from CoinDesk"""
    try:
        data = await coindesk_client.get_bitcoin_price("USD")
        return data.get("price", 0)
    except:
        return 0


async def fetch_coindesk_market_data(symbols: List[str] = None) -> List[Dict[str, Any]]:
    """Get market data from CoinDesk"""
    return await coindesk_client.get_market_data(symbols)


__all__ = ["CoinDeskClient", "coindesk_client", "fetch_coindesk_btc_price", "fetch_coindesk_market_data"]
