#!/usr/bin/env python3
"""
Market Data Aggregator - Uses ALL Free Resources
Maximizes usage of all available free market data APIs with intelligent fallback
"""

import httpx
import logging
import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import HTTPException

logger = logging.getLogger(__name__)


class MarketDataAggregator:
    """
    Aggregates market data from ALL free sources:
    - CoinGecko (primary)
    - CoinPaprika
    - CoinCap
    - Binance Public
    - CoinLore
    - Messari
    - DefiLlama
    - DIA Data
    - CoinStats
    - FreeCryptoAPI
    """
    
    def __init__(self):
        self.timeout = 10.0
        self.providers = {
            "coingecko": {
                "base_url": "https://api.coingecko.com/api/v3",
                "priority": 1,
                "free": True
            },
            "coinpaprika": {
                "base_url": "https://api.coinpaprika.com/v1",
                "priority": 2,
                "free": True
            },
            "coincap": {
                "base_url": "https://api.coincap.io/v2",
                "priority": 3,
                "free": True
            },
            "binance": {
                "base_url": "https://api.binance.com/api/v3",
                "priority": 4,
                "free": True
            },
            "coinlore": {
                "base_url": "https://api.coinlore.net/api",
                "priority": 5,
                "free": True
            },
            "messari": {
                "base_url": "https://data.messari.io/api/v1",
                "priority": 6,
                "free": True
            },
            "defillama": {
                "base_url": "https://coins.llama.fi",
                "priority": 7,
                "free": True
            },
            "diadata": {
                "base_url": "https://api.diadata.org/v1",
                "priority": 8,
                "free": True
            },
            "coinstats": {
                "base_url": "https://api.coinstats.app/public/v1",
                "priority": 9,
                "free": True
            }
        }
        
        # Symbol mappings for different providers
        self.symbol_to_coingecko_id = {
            "BTC": "bitcoin", "ETH": "ethereum", "BNB": "binancecoin",
            "XRP": "ripple", "ADA": "cardano", "DOGE": "dogecoin",
            "SOL": "solana", "TRX": "tron", "DOT": "polkadot",
            "MATIC": "matic-network", "LTC": "litecoin", "SHIB": "shiba-inu",
            "AVAX": "avalanche-2", "UNI": "uniswap", "LINK": "chainlink",
            "ATOM": "cosmos", "XLM": "stellar", "ETC": "ethereum-classic",
            "XMR": "monero", "BCH": "bitcoin-cash", "NEAR": "near",
            "APT": "aptos", "ARB": "arbitrum", "OP": "optimism"
        }
    
    async def get_price(self, symbol: str) -> Dict[str, Any]:
        """
        Get price using ALL available free providers with fallback
        """
        symbol = symbol.upper().replace("USDT", "").replace("USD", "")
        
        # Try all providers in priority order
        providers_to_try = sorted(
            self.providers.items(),
            key=lambda x: x[1]["priority"]
        )
        
        for provider_name, provider_info in providers_to_try:
            try:
                if provider_name == "coingecko":
                    price_data = await self._get_price_coingecko(symbol)
                elif provider_name == "coinpaprika":
                    price_data = await self._get_price_coinpaprika(symbol)
                elif provider_name == "coincap":
                    price_data = await self._get_price_coincap(symbol)
                elif provider_name == "binance":
                    price_data = await self._get_price_binance(symbol)
                elif provider_name == "coinlore":
                    price_data = await self._get_price_coinlore(symbol)
                elif provider_name == "messari":
                    price_data = await self._get_price_messari(symbol)
                elif provider_name == "coinstats":
                    price_data = await self._get_price_coinstats(symbol)
                else:
                    continue
                
                if price_data and price_data.get("price", 0) > 0:
                    logger.info(f"✅ {provider_name.upper()}: Successfully fetched price for {symbol}")
                    return price_data
                    
            except Exception as e:
                logger.warning(f"⚠️ {provider_name.upper()} failed for {symbol}: {e}")
                continue
        
        raise HTTPException(
            status_code=503,
            detail=f"All market data providers failed for {symbol}"
        )
    
    async def get_multiple_prices(self, symbols: List[str], limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get prices for multiple symbols using batch APIs where possible
        """
        # Try CoinGecko batch first
        try:
            return await self._get_batch_coingecko(symbols or None, limit)
        except Exception as e:
            logger.warning(f"⚠️ CoinGecko batch failed: {e}")
        
        # Try CoinCap batch
        try:
            return await self._get_batch_coincap(symbols, limit)
        except Exception as e:
            logger.warning(f"⚠️ CoinCap batch failed: {e}")
        
        # Try CoinPaprika batch
        try:
            return await self._get_batch_coinpaprika(limit)
        except Exception as e:
            logger.warning(f"⚠️ CoinPaprika batch failed: {e}")
        
        # Fallback: Get individual prices
        if symbols:
            results = []
            for symbol in symbols[:limit]:
                try:
                    price_data = await self.get_price(symbol)
                    results.append(price_data)
                except:
                    continue
            
            if results:
                return results
        
        raise HTTPException(
            status_code=503,
            detail="All market data providers failed"
        )
    
    # CoinGecko implementation
    async def _get_price_coingecko(self, symbol: str) -> Dict[str, Any]:
        """Get price from CoinGecko"""
        coin_id = self.symbol_to_coingecko_id.get(symbol, symbol.lower())
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.providers['coingecko']['base_url']}/simple/price",
                params={
                    "ids": coin_id,
                    "vs_currencies": "usd",
                    "include_24hr_change": "true",
                    "include_24hr_vol": "true",
                    "include_market_cap": "true"
                }
            )
            response.raise_for_status()
            data = response.json()
            
            if coin_id in data:
                coin_data = data[coin_id]
                return {
                    "symbol": symbol,
                    "price": coin_data.get("usd", 0),
                    "change24h": coin_data.get("usd_24h_change", 0),
                    "volume24h": coin_data.get("usd_24h_vol", 0),
                    "marketCap": coin_data.get("usd_market_cap", 0),
                    "source": "coingecko",
                    "timestamp": int(datetime.utcnow().timestamp() * 1000)
                }
            
            raise Exception("Coin not found in CoinGecko")
    
    async def _get_batch_coingecko(self, symbols: Optional[List[str]], limit: int) -> List[Dict[str, Any]]:
        """Get batch prices from CoinGecko"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            if symbols:
                coin_ids = [self.symbol_to_coingecko_id.get(s.upper(), s.lower()) for s in symbols]
                response = await client.get(
                    f"{self.providers['coingecko']['base_url']}/simple/price",
                    params={
                        "ids": ",".join(coin_ids),
                        "vs_currencies": "usd",
                        "include_24hr_change": "true",
                        "include_24hr_vol": "true",
                        "include_market_cap": "true"
                    }
                )
            else:
                response = await client.get(
                    f"{self.providers['coingecko']['base_url']}/coins/markets",
                    params={
                        "vs_currency": "usd",
                        "order": "market_cap_desc",
                        "per_page": min(limit, 250),
                        "page": 1,
                        "sparkline": "false"
                    }
                )
            
            response.raise_for_status()
            data = response.json()
            
            results = []
            if isinstance(data, list):
                for coin in data:
                    results.append({
                        "symbol": coin.get("symbol", "").upper(),
                        "name": coin.get("name", ""),
                        "price": coin.get("current_price", 0),
                        "change24h": coin.get("price_change_24h", 0),
                        "volume24h": coin.get("total_volume", 0),
                        "marketCap": coin.get("market_cap", 0),
                        "source": "coingecko",
                        "timestamp": int(datetime.utcnow().timestamp() * 1000)
                    })
            else:
                for coin_id, coin_data in data.items():
                    symbol = next((k for k, v in self.symbol_to_coingecko_id.items() if v == coin_id), coin_id.upper())
                    results.append({
                        "symbol": symbol,
                        "price": coin_data.get("usd", 0),
                        "change24h": coin_data.get("usd_24h_change", 0),
                        "volume24h": coin_data.get("usd_24h_vol", 0),
                        "marketCap": coin_data.get("usd_market_cap", 0),
                        "source": "coingecko",
                        "timestamp": int(datetime.utcnow().timestamp() * 1000)
                    })
            
            logger.info(f"✅ CoinGecko: Fetched {len(results)} prices")
            return results
    
    # CoinPaprika implementation
    async def _get_price_coinpaprika(self, symbol: str) -> Dict[str, Any]:
        """Get price from CoinPaprika"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            # Search for coin
            search_response = await client.get(
                f"{self.providers['coinpaprika']['base_url']}/search",
                params={"q": symbol, "c": "currencies", "limit": 1}
            )
            search_response.raise_for_status()
            search_data = search_response.json()
            
            if search_data.get("currencies"):
                coin_id = search_data["currencies"][0]["id"]
                
                # Get ticker data
                ticker_response = await client.get(
                    f"{self.providers['coinpaprika']['base_url']}/tickers/{coin_id}"
                )
                ticker_response.raise_for_status()
                ticker_data = ticker_response.json()
                
                quotes = ticker_data.get("quotes", {}).get("USD", {})
                return {
                    "symbol": symbol,
                    "name": ticker_data.get("name", ""),
                    "price": quotes.get("price", 0),
                    "change24h": quotes.get("percent_change_24h", 0),
                    "volume24h": quotes.get("volume_24h", 0),
                    "marketCap": quotes.get("market_cap", 0),
                    "source": "coinpaprika",
                    "timestamp": int(datetime.utcnow().timestamp() * 1000)
                }
            
            raise Exception("Coin not found in CoinPaprika")
    
    async def _get_batch_coinpaprika(self, limit: int) -> List[Dict[str, Any]]:
        """Get batch prices from CoinPaprika"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.providers['coinpaprika']['base_url']}/tickers",
                params={"limit": limit}
            )
            response.raise_for_status()
            data = response.json()
            
            results = []
            for coin in data:
                quotes = coin.get("quotes", {}).get("USD", {})
                results.append({
                    "symbol": coin.get("symbol", "").upper(),
                    "name": coin.get("name", ""),
                    "price": quotes.get("price", 0),
                    "change24h": quotes.get("percent_change_24h", 0),
                    "volume24h": quotes.get("volume_24h", 0),
                    "marketCap": quotes.get("market_cap", 0),
                    "source": "coinpaprika",
                    "timestamp": int(datetime.utcnow().timestamp() * 1000)
                })
            
            logger.info(f"✅ CoinPaprika: Fetched {len(results)} prices")
            return results
    
    # CoinCap implementation
    async def _get_price_coincap(self, symbol: str) -> Dict[str, Any]:
        """Get price from CoinCap"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            # Search for asset
            search_response = await client.get(
                f"{self.providers['coincap']['base_url']}/assets",
                params={"search": symbol, "limit": 1}
            )
            search_response.raise_for_status()
            search_data = search_response.json()
            
            if search_data.get("data"):
                asset_id = search_data["data"][0]["id"]
                
                # Get asset details
                asset_response = await client.get(
                    f"{self.providers['coincap']['base_url']}/assets/{asset_id}"
                )
                asset_response.raise_for_status()
                asset_data = asset_response.json()
                
                asset = asset_data.get("data", {})
                return {
                    "symbol": symbol,
                    "name": asset.get("name", ""),
                    "price": float(asset.get("priceUsd", 0)),
                    "change24h": float(asset.get("changePercent24Hr", 0)),
                    "volume24h": float(asset.get("volumeUsd24Hr", 0)),
                    "marketCap": float(asset.get("marketCapUsd", 0)),
                    "source": "coincap",
                    "timestamp": int(datetime.utcnow().timestamp() * 1000)
                }
            
            raise Exception("Asset not found in CoinCap")
    
    async def _get_batch_coincap(self, symbols: Optional[List[str]], limit: int) -> List[Dict[str, Any]]:
        """Get batch prices from CoinCap"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.providers['coincap']['base_url']}/assets",
                params={"limit": limit}
            )
            response.raise_for_status()
            data = response.json()
            
            results = []
            for asset in data.get("data", []):
                results.append({
                    "symbol": asset.get("symbol", "").upper(),
                    "name": asset.get("name", ""),
                    "price": float(asset.get("priceUsd", 0)),
                    "change24h": float(asset.get("changePercent24Hr", 0)),
                    "volume24h": float(asset.get("volumeUsd24Hr", 0)),
                    "marketCap": float(asset.get("marketCapUsd", 0)),
                    "source": "coincap",
                    "timestamp": int(datetime.utcnow().timestamp() * 1000)
                })
            
            logger.info(f"✅ CoinCap: Fetched {len(results)} prices")
            return results
    
    # Binance implementation
    async def _get_price_binance(self, symbol: str) -> Dict[str, Any]:
        """Get price from Binance"""
        binance_symbol = f"{symbol}USDT"
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.providers['binance']['base_url']}/ticker/24hr",
                params={"symbol": binance_symbol}
            )
            response.raise_for_status()
            data = response.json()
            
            return {
                "symbol": symbol,
                "price": float(data.get("lastPrice", 0)),
                "change24h": float(data.get("priceChangePercent", 0)),
                "volume24h": float(data.get("volume", 0)),
                "high24h": float(data.get("highPrice", 0)),
                "low24h": float(data.get("lowPrice", 0)),
                "source": "binance",
                "timestamp": int(datetime.utcnow().timestamp() * 1000)
            }
    
    # CoinLore implementation
    async def _get_price_coinlore(self, symbol: str) -> Dict[str, Any]:
        """Get price from CoinLore"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.providers['coinlore']['base_url']}/tickers/"
            )
            response.raise_for_status()
            data = response.json()
            
            for coin in data.get("data", []):
                if coin.get("symbol", "").upper() == symbol:
                    return {
                        "symbol": symbol,
                        "name": coin.get("name", ""),
                        "price": float(coin.get("price_usd", 0)),
                        "change24h": float(coin.get("percent_change_24h", 0)),
                        "marketCap": float(coin.get("market_cap_usd", 0)),
                        "source": "coinlore",
                        "timestamp": int(datetime.utcnow().timestamp() * 1000)
                    }
            
            raise Exception("Coin not found in CoinLore")
    
    # Messari implementation
    async def _get_price_messari(self, symbol: str) -> Dict[str, Any]:
        """Get price from Messari"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.providers['messari']['base_url']}/assets/{symbol.lower()}/metrics"
            )
            response.raise_for_status()
            data = response.json()
            
            metrics = data.get("data", {}).get("market_data", {})
            return {
                "symbol": symbol,
                "name": data.get("data", {}).get("name", ""),
                "price": float(metrics.get("price_usd", 0)),
                "change24h": float(metrics.get("percent_change_usd_last_24_hours", 0)),
                "volume24h": float(metrics.get("real_volume_last_24_hours", 0)),
                "marketCap": float(metrics.get("marketcap", {}).get("current_marketcap_usd", 0)),
                "source": "messari",
                "timestamp": int(datetime.utcnow().timestamp() * 1000)
            }
    
    # CoinStats implementation
    async def _get_price_coinstats(self, symbol: str) -> Dict[str, Any]:
        """Get price from CoinStats"""
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(
                f"{self.providers['coinstats']['base_url']}/coins",
                params={"currency": "USD"}
            )
            response.raise_for_status()
            data = response.json()
            
            for coin in data.get("coins", []):
                if coin.get("symbol", "").upper() == symbol:
                    return {
                        "symbol": symbol,
                        "name": coin.get("name", ""),
                        "price": float(coin.get("price", 0)),
                        "change24h": float(coin.get("priceChange1d", 0)),
                        "volume24h": float(coin.get("volume", 0)),
                        "marketCap": float(coin.get("marketCap", 0)),
                        "source": "coinstats",
                        "timestamp": int(datetime.utcnow().timestamp() * 1000)
                    }
            
            raise Exception("Coin not found in CoinStats")


# Global instance
market_data_aggregator = MarketDataAggregator()

__all__ = ["MarketDataAggregator", "market_data_aggregator"]

