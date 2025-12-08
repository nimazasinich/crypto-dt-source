#!/usr/bin/env python3
"""
Real API Clients - ZERO MOCK DATA
All clients fetch REAL data from external APIs
"""

import httpx
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import hashlib
from fastapi import HTTPException

logger = logging.getLogger(__name__)


class RealAPIConfiguration:
    """Real API keys - Loaded from environment variables"""
    
    import os
    
    # Blockchain Explorers
    TRONSCAN_API_KEY = os.getenv("TRONSCAN_API_KEY", "7ae72726-bffe-4e74-9c33-97b761eeea21")
    TRONSCAN_BASE_URL = "https://apilist.tronscan.org/api"
    
    BSCSCAN_API_KEY = os.getenv("BSCSCAN_API_KEY", "K62RKHGXTDCG53RU4MCG6XABIMJKTN19IT")
    BSCSCAN_BASE_URL = "https://api.bscscan.com/api"
    
    # کلید دوم Etherscan (جدید)
    ETHERSCAN_API_KEY = os.getenv("ETHERSCAN_API_KEY", "T6IR8VJHX2NE6ZJW2S3FDVN1TYG4PYYI45")
    ETHERSCAN_BASE_URL = "https://api.etherscan.io/api"
    
    # Market Data - کلیدهای جدید
    COINMARKETCAP_API_KEY = os.getenv("COINMARKETCAP_API_KEY", "a35ffaec-c66c-4f16-81e3-41a717e4822f")
    COINMARKETCAP_BASE_URL = "https://pro-api.coinmarketcap.com/v1"
    
    # News - کلید جدید
    NEWSAPI_API_KEY = os.getenv("NEWSAPI_API_KEY", "968a5e25552b4cb5ba3280361d8444ab")
    NEWSAPI_BASE_URL = "https://newsapi.org/v2"
    
    # HuggingFace Space - کلید جدید
    # IMPORTANT: Strip whitespace to avoid "Illegal header value" errors
    HF_API_TOKEN = os.getenv("HF_API_TOKEN", "").strip()
    HF_SPACE_BASE_URL = os.getenv("HF_SPACE_BASE_URL", "https://really-amin-datasourceforcryptocurrency.hf.space").strip()
    HF_SPACE_WS_URL = os.getenv("HF_SPACE_WS_URL", "wss://really-amin-datasourceforcryptocurrency.hf.space/ws").strip()
    
    # منابع اضافی جدید
    # TronGrid (منبع دوم برای Tron)
    TRONGRID_API_KEY = os.getenv("TRONGRID_API_KEY", "7ae72726-bffe-4e74-9c33-97b761eeea21")  # همان کلید TronScan
    TRONGRID_BASE_URL = "https://api.trongrid.io/v1"
    
    # Blockchair (برای چندین بلاکچین)
    BLOCKCHAIR_API_KEY = os.getenv("BLOCKCHAIR_API_KEY", "YOUR_BLOCKCHAIR_KEY")
    BLOCKCHAIR_BASE_URL = "https://api.blockchair.com"
    
    # Alternative.me برای Fear & Greed Index
    ALTERNATIVE_ME_BASE_URL = "https://api.alternative.me"
    
    # CoinGecko (بدون نیاز به کلید)
    COINGECKO_BASE_URL = "https://api.coingecko.com/api/v3"
    
    # Binance Public API (بدون نیاز به کلید)
    BINANCE_BASE_URL = "https://api.binance.com/api/v3"
    
    # CryptoCompare 
    CRYPTOCOMPARE_API_KEY = os.getenv("CRYPTOCOMPARE_API_KEY", "YOUR_CRYPTOCOMPARE_KEY")
    CRYPTOCOMPARE_BASE_URL = "https://min-api.cryptocompare.com/data"
    
    # Reddit API (برای احساسات اجتماعی)
    REDDIT_BASE_URL = "https://www.reddit.com/r"


class CoinMarketCapClient:
    """
    Real CoinMarketCap API Client
    Fetches REAL market data - NO MOCK DATA
    """
    
    def __init__(self):
        self.api_key = RealAPIConfiguration.COINMARKETCAP_API_KEY
        self.base_url = RealAPIConfiguration.COINMARKETCAP_BASE_URL
        self.headers = {
            "X-CMC_PRO_API_KEY": self.api_key,
            "Accept": "application/json"
        }
    
    async def get_latest_listings(self, limit: int = 100) -> Dict[str, Any]:
        """
        Fetch REAL latest cryptocurrency listings
        """
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(
                    f"{self.base_url}/cryptocurrency/listings/latest",
                    headers=self.headers,
                    params={
                        "limit": limit,
                        "convert": "USD"
                    }
                )
                response.raise_for_status()
                data = response.json()
                
                logger.info(f"✅ CoinMarketCap: Fetched {len(data.get('data', []))} real listings")
                return {
                    "success": True,
                    "data": data.get("data", []),
                    "meta": {
                        "source": "coinmarketcap",
                        "timestamp": datetime.utcnow().isoformat(),
                        "cached": False
                    }
                }
        except Exception as e:
            logger.error(f"❌ CoinMarketCap API failed: {e}")
            raise HTTPException(status_code=503, detail=f"Failed to fetch real market data: {str(e)}")
    
    async def get_quotes(self, symbols: List[str]) -> Dict[str, Any]:
        """
        Fetch REAL price quotes for specific symbols
        """
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(
                    f"{self.base_url}/cryptocurrency/quotes/latest",
                    headers=self.headers,
                    params={
                        "symbol": ",".join(symbols),
                        "convert": "USD"
                    }
                )
                response.raise_for_status()
                data = response.json()
                
                logger.info(f"✅ CoinMarketCap: Fetched real quotes for {len(symbols)} symbols")
                return {
                    "success": True,
                    "data": data.get("data", {}),
                    "meta": {
                        "source": "coinmarketcap",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                }
        except Exception as e:
            logger.error(f"❌ CoinMarketCap quotes failed: {e}")
            raise HTTPException(status_code=503, detail=f"Failed to fetch real quotes: {str(e)}")
    
    async def get_ohlc(self, symbol: str, interval: str = "1h", limit: int = 100) -> Dict[str, Any]:
        """
        Fetch REAL OHLC data from CoinMarketCap
        """
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(
                    f"{self.base_url}/cryptocurrency/quotes/historical",
                    headers=self.headers,
                    params={
                        "symbol": symbol,
                        "count": limit,
                        "interval": interval
                    }
                )
                response.raise_for_status()
                data = response.json()
                
                logger.info(f"✅ CoinMarketCap: Fetched real OHLC for {symbol}")
                return {
                    "success": True,
                    "data": data.get("data", {}),
                    "meta": {
                        "source": "coinmarketcap",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                }
        except Exception as e:
            logger.error(f"❌ CoinMarketCap OHLC failed: {e}")
            # Try alternative source if CMC fails
            return await self._get_ohlc_fallback(symbol, interval, limit)
    
    async def _get_ohlc_fallback(self, symbol: str, interval: str, limit: int) -> Dict[str, Any]:
        """
        Fallback chain for OHLC data with at least 3 providers
        Priority: Binance → CoinGecko → CoinPaprika → CoinCap → CryptoCompare
        """
        fallback_providers = [
            ("binance", self._fetch_binance_ohlc),
            ("coingecko", self._fetch_coingecko_ohlc),
            ("coinpaprika", self._fetch_coinpaprika_ohlc),
            ("coincap", self._fetch_coincap_ohlc),
            ("cryptocompare", self._fetch_cryptocompare_ohlc)
        ]
        
        last_error = None
        for provider_name, fetch_func in fallback_providers:
            try:
                logger.info(f"🔄 Trying OHLC fallback: {provider_name}")
                result = await fetch_func(symbol, interval, limit)
                if result and result.get("success"):
                    logger.info(f"✅ {provider_name} fallback succeeded: {len(result.get('data', []))} candles")
                    return result
            except Exception as e:
                logger.warning(f"⚠️ {provider_name} fallback failed: {e}")
                last_error = e
                continue
        
        logger.error(f"❌ All OHLC fallback providers failed. Last error: {last_error}")
        raise HTTPException(status_code=503, detail=f"All OHLC sources failed. Tried: {[p[0] for p in fallback_providers]}")
    
    async def _fetch_binance_ohlc(self, symbol: str, interval: str, limit: int) -> Dict[str, Any]:
        """Fallback 1: Binance"""
        interval_map = {"1m": "1m", "5m": "5m", "15m": "15m", "1h": "1h", "4h": "4h", "1d": "1d"}
        binance_interval = interval_map.get(interval, "1h")
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                "https://api.binance.com/api/v3/klines",
                params={
                    "symbol": f"{symbol}USDT",
                    "interval": binance_interval,
                    "limit": limit
                }
            )
            response.raise_for_status()
            klines = response.json()
            
            ohlc_data = []
            for kline in klines:
                ohlc_data.append({
                    "ts": int(kline[0]),
                    "open": float(kline[1]),
                    "high": float(kline[2]),
                    "low": float(kline[3]),
                    "close": float(kline[4]),
                    "volume": float(kline[5])
                })
            
            return {
                "success": True,
                "data": ohlc_data,
                "meta": {"source": "binance", "timestamp": datetime.utcnow().isoformat(), "fallback": True}
            }
    
    async def _fetch_coingecko_ohlc(self, symbol: str, interval: str, limit: int) -> Dict[str, Any]:
        """Fallback 2: CoinGecko"""
        # Map interval to CoinGecko format
        days_map = {"1h": 1, "4h": 7, "1d": 30}
        days = days_map.get(interval, 1)
        
        # Get coin ID from symbol
        coin_id_map = {"BTC": "bitcoin", "ETH": "ethereum", "BNB": "binancecoin", "USDT": "tether"}
        coin_id = coin_id_map.get(symbol.upper(), symbol.lower())
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                f"{RealAPIConfiguration.COINGECKO_BASE_URL}/coins/{coin_id}/ohlc",
                params={"vs_currency": "usd", "days": days}
            )
            response.raise_for_status()
            data = response.json()
            
            ohlc_data = []
            for item in data[:limit]:
                ohlc_data.append({
                    "ts": item[0],
                    "open": item[1],
                    "high": item[2],
                    "low": item[3],
                    "close": item[4],
                    "volume": 0  # CoinGecko doesn't provide volume in OHLC endpoint
                })
            
            return {
                "success": True,
                "data": ohlc_data,
                "meta": {"source": "coingecko", "timestamp": datetime.utcnow().isoformat(), "fallback": True}
            }
    
    async def _fetch_coinpaprika_ohlc(self, symbol: str, interval: str, limit: int) -> Dict[str, Any]:
        """Fallback 3: CoinPaprika"""
        # Get coin ID
        coin_id_map = {"BTC": "btc-bitcoin", "ETH": "eth-ethereum", "BNB": "bnb-binance-coin"}
        coin_id = coin_id_map.get(symbol.upper(), f"{symbol.lower()}-{symbol.lower()}")
        
        # Map interval
        quote_map = {"1h": "1h", "4h": "4h", "1d": "1d"}
        quote = quote_map.get(interval, "1h")
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                f"https://api.coinpaprika.com/v1/coins/{coin_id}/ohlcv/historical",
                params={"quote": "usd", "interval": quote}
            )
            response.raise_for_status()
            data = response.json()
            
            ohlc_data = []
            for item in data[-limit:]:  # Get last N items
                ohlc_data.append({
                    "ts": int(item["time_open"]),
                    "open": float(item["open"]),
                    "high": float(item["high"]),
                    "low": float(item["low"]),
                    "close": float(item["close"]),
                    "volume": float(item["volume"])
                })
            
            return {
                "success": True,
                "data": ohlc_data,
                "meta": {"source": "coinpaprika", "timestamp": datetime.utcnow().isoformat(), "fallback": True}
            }
    
    async def _fetch_coincap_ohlc(self, symbol: str, interval: str, limit: int) -> Dict[str, Any]:
        """Fallback 4: CoinCap"""
        coin_id_map = {"BTC": "bitcoin", "ETH": "ethereum", "BNB": "binance-coin"}
        coin_id = coin_id_map.get(symbol.upper(), symbol.lower())
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                f"https://api.coincap.io/v2/assets/{coin_id}/history",
                params={"interval": interval, "limit": limit}
            )
            response.raise_for_status()
            data = response.json()
            
            ohlc_data = []
            for item in data.get("data", []):
                price = float(item.get("priceUsd", 0))
                ohlc_data.append({
                    "ts": int(item["time"]),
                    "open": price,
                    "high": price,
                    "low": price,
                    "close": price,
                    "volume": float(item.get("volumeUsd", 0))
                })
            
            return {
                "success": True,
                "data": ohlc_data,
                "meta": {"source": "coincap", "timestamp": datetime.utcnow().isoformat(), "fallback": True}
            }
    
    async def _fetch_cryptocompare_ohlc(self, symbol: str, interval: str, limit: int) -> Dict[str, Any]:
        """Fallback 5: CryptoCompare"""
        interval_map = {"1h": "histohour", "4h": "histohour", "1d": "histoday"}
        endpoint = interval_map.get(interval, "histohour")
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                f"https://min-api.cryptocompare.com/data/v2/{endpoint}",
                params={
                    "fsym": symbol.upper(),
                    "tsym": "USD",
                    "limit": limit
                }
            )
            response.raise_for_status()
            data = response.json()
            
            ohlc_data = []
            for item in data.get("Data", {}).get("Data", []):
                ohlc_data.append({
                    "ts": item["time"] * 1000,
                    "open": float(item["open"]),
                    "high": float(item["high"]),
                    "low": float(item["low"]),
                    "close": float(item["close"]),
                    "volume": float(item["volumefrom"])
                })
            
            return {
                "success": True,
                "data": ohlc_data,
                "meta": {"source": "cryptocompare", "timestamp": datetime.utcnow().isoformat(), "fallback": True}
            }


class NewsAPIClient:
    """
    Real NewsAPI Client
    Fetches REAL crypto news - NO MOCK DATA
    """
    
    def __init__(self):
        self.api_key = RealAPIConfiguration.NEWSAPI_API_KEY
        self.base_url = RealAPIConfiguration.NEWSAPI_BASE_URL
    
    async def get_crypto_news(self, symbol: str = "BTC", limit: int = 20) -> Dict[str, Any]:
        """
        Fetch REAL crypto news from NewsAPI
        """
        try:
            search_query = f"{symbol} OR cryptocurrency OR crypto OR bitcoin"
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/everything",
                    params={
                        "q": search_query,
                        "apiKey": self.api_key,
                        "language": "en",
                        "sortBy": "publishedAt",
                        "pageSize": limit
                    }
                )
                response.raise_for_status()
                data = response.json()
            
            articles = []
            for article in data.get("articles", []):
                article_id = hashlib.md5(article["url"].encode()).hexdigest()
                articles.append({
                    "id": article_id,
                    "title": article["title"],
                    "summary": article.get("description", ""),
                    "url": article["url"],
                    "source": article["source"]["name"],
                    "published_at": article["publishedAt"],
                    "image_url": article.get("urlToImage"),
                    "author": article.get("author")
                })
            
            logger.info(f"✅ NewsAPI: Fetched {len(articles)} real articles")
            return {
                "success": True,
                "articles": articles,
                "meta": {
                    "total": len(articles),
                    "source": "newsapi",
                    "query": search_query,
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
        except Exception as e:
            logger.error(f"❌ NewsAPI failed: {e}")
            raise HTTPException(status_code=503, detail=f"Failed to fetch real news: {str(e)}")
    
    async def get_top_headlines(self, limit: int = 10) -> Dict[str, Any]:
        """
        Fetch REAL top crypto headlines
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/top-headlines",
                    params={
                        "q": "cryptocurrency OR bitcoin",
                        "apiKey": self.api_key,
                        "language": "en",
                        "pageSize": limit
                    }
                )
                response.raise_for_status()
                data = response.json()
            
            articles = []
            for article in data.get("articles", []):
                article_id = hashlib.md5(article["url"].encode()).hexdigest()
                articles.append({
                    "id": article_id,
                    "title": article["title"],
                    "summary": article.get("description", ""),
                    "url": article["url"],
                    "source": article["source"]["name"],
                    "published_at": article["publishedAt"]
                })
            
            logger.info(f"✅ NewsAPI: Fetched {len(articles)} real headlines")
            return {
                "success": True,
                "articles": articles,
                "meta": {
                    "source": "newsapi",
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
        except Exception as e:
            logger.error(f"❌ NewsAPI headlines failed: {e}")
            raise HTTPException(status_code=503, detail=f"Failed to fetch headlines: {str(e)}")


class BlockchainExplorerClient:
    """
    Real Blockchain Explorer Clients
    Fetches REAL blockchain data - NO MOCK DATA
    """
    
    def __init__(self):
        self.etherscan_key = RealAPIConfiguration.ETHERSCAN_API_KEY
        self.bscscan_key = RealAPIConfiguration.BSCSCAN_API_KEY
        self.tronscan_key = RealAPIConfiguration.TRONSCAN_API_KEY
    
    async def get_ethereum_transactions(self, address: Optional[str] = None, limit: int = 20) -> Dict[str, Any]:
        """
        Fetch REAL Ethereum transactions
        """
        try:
            # Use a known whale address if none provided
            if not address:
                address = "0x742d35Cc6634C0532925a3b844Bc9e7595f0bEb"  # Binance Hot Wallet
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    RealAPIConfiguration.ETHERSCAN_BASE_URL,
                    params={
                        "module": "account",
                        "action": "txlist",
                        "address": address,
                        "startblock": 0,
                        "endblock": 99999999,
                        "page": 1,
                        "offset": limit,
                        "sort": "desc",
                        "apikey": self.etherscan_key
                    }
                )
                response.raise_for_status()
                data = response.json()
            
            transactions = data.get("result", [])[:limit]
            
            logger.info(f"✅ Etherscan: Fetched {len(transactions)} real transactions")
            return {
                "success": True,
                "chain": "ethereum",
                "transactions": transactions,
                "meta": {
                    "total": len(transactions),
                    "source": "etherscan",
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
        except Exception as e:
            logger.error(f"❌ Etherscan failed: {e}")
            raise HTTPException(status_code=503, detail=f"Failed to fetch Ethereum data: {str(e)}")
    
    async def get_bsc_transactions(self, address: Optional[str] = None, limit: int = 20) -> Dict[str, Any]:
        """
        Fetch REAL BSC transactions
        """
        try:
            if not address:
                address = "0x8894E0a0c962CB723c1976a4421c95949bE2D4E3"  # Binance BSC Hot Wallet
            
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    RealAPIConfiguration.BSCSCAN_BASE_URL,
                    params={
                        "module": "account",
                        "action": "txlist",
                        "address": address,
                        "startblock": 0,
                        "endblock": 99999999,
                        "page": 1,
                        "offset": limit,
                        "sort": "desc",
                        "apikey": self.bscscan_key
                    }
                )
                response.raise_for_status()
                data = response.json()
            
            transactions = data.get("result", [])[:limit]
            
            logger.info(f"✅ BSCScan: Fetched {len(transactions)} real transactions")
            return {
                "success": True,
                "chain": "bsc",
                "transactions": transactions,
                "meta": {
                    "total": len(transactions),
                    "source": "bscscan",
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
        except Exception as e:
            logger.error(f"❌ BSCScan failed: {e}")
            raise HTTPException(status_code=503, detail=f"Failed to fetch BSC data: {str(e)}")
    
    async def get_tron_transactions(self, limit: int = 20) -> Dict[str, Any]:
        """
        Fetch REAL Tron transactions
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{RealAPIConfiguration.TRONSCAN_BASE_URL}/transaction",
                    params={
                        "sort": "-timestamp",
                        "limit": limit
                    },
                    headers={
                        "TRON-PRO-API-KEY": self.tronscan_key
                    }
                )
                response.raise_for_status()
                data = response.json()
            
            transactions = data.get("data", [])
            
            logger.info(f"✅ Tronscan: Fetched {len(transactions)} real transactions")
            return {
                "success": True,
                "chain": "tron",
                "transactions": transactions,
                "meta": {
                    "total": len(transactions),
                    "source": "tronscan",
                    "timestamp": datetime.utcnow().isoformat()
                }
            }
        except Exception as e:
            logger.error(f"❌ Tronscan failed: {e}")
            raise HTTPException(status_code=503, detail=f"Failed to fetch Tron data: {str(e)}")
    
    async def get_gas_prices(self, chain: str = "ethereum") -> Dict[str, Any]:
        """
        Fetch REAL gas prices
        """
        try:
            if chain.lower() == "ethereum":
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.get(
                        RealAPIConfiguration.ETHERSCAN_BASE_URL,
                        params={
                            "module": "gastracker",
                            "action": "gasoracle",
                            "apikey": self.etherscan_key
                        }
                    )
                    response.raise_for_status()
                    data = response.json()
                
                result = data.get("result", {})
                
                logger.info(f"✅ Etherscan: Fetched real gas prices")
                return {
                    "success": True,
                    "chain": "ethereum",
                    "gas_prices": {
                        "safe": float(result.get("SafeGasPrice", 0)),
                        "standard": float(result.get("ProposeGasPrice", 0)),
                        "fast": float(result.get("FastGasPrice", 0)),
                        "unit": "gwei"
                    },
                    "meta": {
                        "source": "etherscan",
                        "timestamp": datetime.utcnow().isoformat()
                    }
                }
            else:
                raise HTTPException(status_code=400, detail=f"Chain {chain} not supported")
        except Exception as e:
            logger.error(f"❌ Gas prices failed: {e}")
            raise HTTPException(status_code=503, detail=f"Failed to fetch gas prices: {str(e)}")


class HuggingFaceSpaceClient:
    """
    Real HuggingFace Space Client
    Connects to REAL HF Space - NO MOCK DATA
    """
    
    def __init__(self):
        # Ensure token is stripped to prevent "Illegal header value" errors
        self.api_token = (RealAPIConfiguration.HF_API_TOKEN or "").strip()
        self.base_url = RealAPIConfiguration.HF_SPACE_BASE_URL
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        } if self.api_token else {
            "Content-Type": "application/json"
        }
    
    async def check_connection(self) -> Dict[str, Any]:
        """
        Check REAL connection to HF Space
        """
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(
                    f"{self.base_url}/api/health",
                    headers=self.headers
                )
                response.raise_for_status()
                
                logger.info(f"✅ HuggingFace Space: Connected successfully")
                return {
                    "success": True,
                    "connected": True,
                    "space_url": self.base_url,
                    "timestamp": datetime.utcnow().isoformat()
                }
        except Exception as e:
            logger.error(f"❌ HuggingFace Space connection failed: {e}")
            return {
                "success": False,
                "connected": False,
                "error": str(e),
                "timestamp": datetime.utcnow().isoformat()
            }
    
    async def get_market_data(self) -> Dict[str, Any]:
        """
        Fetch REAL market data from HF Space
        """
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(
                    f"{self.base_url}/api/market",
                    headers=self.headers
                )
                response.raise_for_status()
                data = response.json()
                
                logger.info(f"✅ HF Space: Fetched real market data")
                return data
        except Exception as e:
            logger.error(f"❌ HF Space market data failed: {e}")
            # Return error instead of mock data
            raise HTTPException(status_code=503, detail=f"HF Space unavailable: {str(e)}")
    
    async def get_trading_pairs(self) -> Dict[str, Any]:
        """
        Fetch REAL trading pairs from HF Space
        """
        try:
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(
                    f"{self.base_url}/api/market/pairs",
                    headers=self.headers
                )
                response.raise_for_status()
                data = response.json()
                
                logger.info(f"✅ HF Space: Fetched real trading pairs")
                return data
        except Exception as e:
            logger.error(f"❌ HF Space trading pairs failed: {e}")
            raise HTTPException(status_code=503, detail=f"Failed to fetch trading pairs: {str(e)}")


# Global instances - Initialize once
cmc_client = CoinMarketCapClient()
news_client = NewsAPIClient()
blockchain_client = BlockchainExplorerClient()
hf_client = HuggingFaceSpaceClient()


# Export all clients
__all__ = [
    "RealAPIConfiguration",
    "CoinMarketCapClient",
    "NewsAPIClient",
    "BlockchainExplorerClient",
    "HuggingFaceSpaceClient",
    "cmc_client",
    "news_client",
    "blockchain_client",
    "hf_client"
]
