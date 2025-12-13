#!/usr/bin/env python3
"""
Crypto DT Source Client - Integration with crypto-dt-source.onrender.com
https://crypto-dt-source.onrender.com

Unified Cryptocurrency Data API v2.0.0 providing:
- Direct HuggingFace model inference (4 models: CryptoBERT, FinBERT, etc.)
- External API integration (CoinGecko, Binance, Alternative.me, Reddit, RSS)
- Cryptocurrency datasets (5 datasets: CryptoCoin, WinkingFace crypto datasets)
- Real-time market data with rate limiting
- Multi-page frontend with HTTP polling
"""

import httpx
import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

# Base URL for the Crypto DT Source API
CRYPTO_DT_SOURCE_BASE_URL = "https://crypto-dt-source.onrender.com"


class CryptoDTSourceService:
    """
    Service for accessing Crypto DT Source API
    Provides unified cryptocurrency data and AI model access
    """
    
    def __init__(self, timeout: int = 20):
        self.base_url = CRYPTO_DT_SOURCE_BASE_URL
        self.timeout = timeout
        self._client: Optional[httpx.AsyncClient] = None
    
    async def _get_client(self) -> httpx.AsyncClient:
        """Get or create async HTTP client"""
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self._client
    
    async def close(self):
        """Close the HTTP client"""
        if self._client and not self._client.is_closed:
            await self._client.aclose()
    
    async def _request(self, endpoint: str, params: Dict = None) -> Dict[str, Any]:
        """
        Make async request to Crypto DT Source with proper error handling
        
        Returns standardized response format matching project patterns
        """
        provider = "CryptoDTSource"
        start_time = datetime.now(timezone.utc)
        
        try:
            client = await self._get_client()
            url = f"{self.base_url}{endpoint}"
            
            response = await client.get(url, params=params)
            response.raise_for_status()
            
            data = response.json()
            response_time_ms = (datetime.now(timezone.utc) - start_time).total_seconds() * 1000
            
            logger.info(f"✅ {provider} - {endpoint} - {response_time_ms:.0f}ms")
            
            return {
                "provider": provider,
                "endpoint": endpoint,
                "data": data,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "response_time_ms": response_time_ms,
                "success": True,
                "error": None
            }
            
        except httpx.HTTPStatusError as e:
            logger.error(f"❌ {provider} - {endpoint} - HTTP {e.response.status_code}")
            return {
                "provider": provider,
                "endpoint": endpoint,
                "data": None,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "success": False,
                "error": f"HTTP {e.response.status_code}",
                "error_type": "http_error"
            }
        except httpx.TimeoutException:
            logger.error(f"❌ {provider} - {endpoint} - Timeout")
            return {
                "provider": provider,
                "endpoint": endpoint,
                "data": None,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "success": False,
                "error": "Request timeout",
                "error_type": "timeout"
            }
        except Exception as e:
            logger.error(f"❌ {provider} - {endpoint} - {str(e)}")
            return {
                "provider": provider,
                "endpoint": endpoint,
                "data": None,
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "success": False,
                "error": str(e),
                "error_type": "exception"
            }
    
    # ===== MARKET DATA =====
    
    async def get_coingecko_price(
        self,
        ids: str = "bitcoin,ethereum",
        vs_currencies: str = "usd"
    ) -> Dict[str, Any]:
        """
        Get cryptocurrency prices from CoinGecko
        
        Args:
            ids: Comma-separated coin IDs (e.g., "bitcoin,ethereum,solana")
            vs_currencies: Comma-separated currencies (e.g., "usd,eur")
        """
        return await self._request(
            "/api/v1/coingecko/price",
            params={"ids": ids, "vs_currencies": vs_currencies}
        )
    
    async def get_binance_klines(
        self,
        symbol: str = "BTCUSDT",
        interval: str = "1h",
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Get candlestick data from Binance
        
        Args:
            symbol: Trading pair (e.g., "BTCUSDT", "ETHUSDT")
            interval: Time interval (1m, 5m, 15m, 1h, 4h, 1d)
            limit: Number of candles (max 1000)
        """
        return await self._request(
            "/api/v1/binance/klines",
            params={"symbol": symbol, "interval": interval, "limit": limit}
        )
    
    # ===== SENTIMENT DATA =====
    
    async def get_fear_greed_index(self, limit: int = 1) -> Dict[str, Any]:
        """
        Get Fear & Greed Index from Alternative.me
        
        Args:
            limit: Number of historical data points (1 for current only)
        """
        return await self._request(
            "/api/v1/alternative/fng",
            params={"limit": limit}
        )
    
    async def get_hf_sentiment(self, text: str, model_key: str = "cryptobert_kk08") -> Dict[str, Any]:
        """
        Run sentiment analysis using HuggingFace models
        
        Args:
            text: Text to analyze
            model_key: Model to use (cryptobert_kk08, finbert, twitter_sentiment, cryptobert_elkulako)
        """
        return await self._request(
            "/api/v1/hf/sentiment",
            params={"text": text, "model_key": model_key}
        )
    
    # ===== NEWS & SOCIAL =====
    
    async def get_reddit_top(
        self,
        subreddit: str = "cryptocurrency",
        time_filter: str = "day",
        limit: int = 25
    ) -> Dict[str, Any]:
        """
        Get top posts from Reddit
        
        Args:
            subreddit: Subreddit name (default: cryptocurrency)
            time_filter: Time filter (hour, day, week, month, year, all)
            limit: Number of posts
        """
        return await self._request(
            "/api/v1/reddit/top",
            params={"subreddit": subreddit, "time_filter": time_filter, "limit": limit}
        )
    
    async def get_rss_feed(
        self,
        feed_name: str = "coindesk",
        limit: int = 20
    ) -> Dict[str, Any]:
        """
        Get crypto news from RSS feeds
        
        Args:
            feed_name: Feed name (coindesk, cointelegraph, bitcoinmagazine, decrypt, theblock)
            limit: Number of articles
        """
        return await self._request(
            "/api/v1/rss/feed",
            params={"feed_name": feed_name, "limit": limit}
        )
    
    # ===== AI MODELS =====
    
    async def get_hf_models(self) -> Dict[str, Any]:
        """
        Get list of available HuggingFace models
        
        Returns:
            List of 4 sentiment analysis models:
            - kk08/CryptoBERT
            - cardiffnlp/twitter-roberta-base-sentiment-latest
            - ProsusAI/finbert
            - ElKulako/cryptobert
        """
        return await self._request("/api/v1/hf/models")
    
    async def get_hf_datasets(self) -> Dict[str, Any]:
        """
        Get list of available HuggingFace datasets
        
        Returns:
            List of 5 crypto datasets:
            - linxy/CryptoCoin
            - WinkingFace/CryptoLM-Bitcoin-BTC-USDT
            - WinkingFace/CryptoLM-Ethereum-ETH-USDT
            - WinkingFace/CryptoLM-Solana-SOL-USDT
            - WinkingFace/CryptoLM-Ripple-XRP-USDT
        """
        return await self._request("/api/v1/hf/datasets")
    
    # ===== SYSTEM STATUS =====
    
    async def get_status(self) -> Dict[str, Any]:
        """
        Get system status including models, datasets, and external APIs
        """
        return await self._request("/api/v1/status")
    
    async def health_check(self) -> Dict[str, Any]:
        """Check API health status"""
        return await self._request("/api")
    
    # ===== CONVENIENCE METHODS =====
    
    async def get_btc_price(self) -> float:
        """
        Get current Bitcoin price in USD
        
        Returns:
            float: BTC price in USD
        """
        result = await self.get_coingecko_price(ids="bitcoin", vs_currencies="usd")
        if result["success"] and result["data"]:
            data = result["data"].get("data", [])
            if data:
                return data[0].get("price", 0)
        return 0
    
    async def get_eth_price(self) -> float:
        """
        Get current Ethereum price in USD
        
        Returns:
            float: ETH price in USD
        """
        result = await self.get_coingecko_price(ids="ethereum", vs_currencies="usd")
        if result["success"] and result["data"]:
            data = result["data"].get("data", [])
            if data:
                return data[0].get("price", 0)
        return 0
    
    async def get_top_100_prices(self) -> List[Dict[str, Any]]:
        """
        Get top 100 cryptocurrency prices
        
        Returns:
            List of price data for top 100 coins
        """
        result = await self.get_coingecko_price(
            ids="bitcoin,ethereum,tether,ripple,binancecoin,usd-coin,solana,cardano,dogecoin,polkadot",
            vs_currencies="usd"
        )
        if result["success"] and result["data"]:
            return result["data"].get("data", [])
        return []
    
    async def analyze_crypto_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze crypto-related text sentiment using CryptoBERT
        
        Args:
            text: Text to analyze
            
        Returns:
            Sentiment analysis results
        """
        return await self.get_hf_sentiment(text, model_key="cryptobert_kk08")


# ===== SINGLETON INSTANCE =====

_service_instance: Optional[CryptoDTSourceService] = None


def get_crypto_dt_source_service() -> CryptoDTSourceService:
    """Get singleton instance of Crypto DT Source Service"""
    global _service_instance
    if _service_instance is None:
        _service_instance = CryptoDTSourceService()
    return _service_instance


# ===== STANDALONE FUNCTIONS (for collectors compatibility) =====

async def fetch_crypto_dt_prices(ids: str = "bitcoin,ethereum") -> Dict[str, Any]:
    """Fetch cryptocurrency prices from Crypto DT Source"""
    service = get_crypto_dt_source_service()
    return await service.get_coingecko_price(ids=ids)


async def fetch_crypto_dt_sentiment(text: str) -> Dict[str, Any]:
    """Analyze sentiment using Crypto DT Source"""
    service = get_crypto_dt_source_service()
    return await service.analyze_crypto_sentiment(text)


# ===== TEST =====

if __name__ == "__main__":
    async def main():
        service = get_crypto_dt_source_service()
        
        print("=" * 70)
        print("Testing Crypto DT Source Service")
        print("=" * 70)
        
        # Health check
        print("\n1. Health Check:")
        result = await service.health_check()
        print(f"   Success: {result['success']}")
        
        # System status
        print("\n2. System Status:")
        result = await service.get_status()
        if result['success']:
            data = result['data']
            print(f"   Version: {data.get('version')}")
            print(f"   Models: {data.get('models', {}).get('total_configured')}")
            print(f"   Datasets: {data.get('datasets', {}).get('total_configured')}")
        
        # Bitcoin price
        print("\n3. Bitcoin Price:")
        btc_price = await service.get_btc_price()
        print(f"   BTC: ${btc_price:,.2f}")
        
        # Fear & Greed Index
        print("\n4. Fear & Greed Index:")
        result = await service.get_fear_greed_index()
        if result['success']:
            print(f"   Success: {result['success']}")
        
        # Available models
        print("\n5. Available Models:")
        result = await service.get_hf_models()
        if result['success']:
            models = result['data'].get('models', [])
            print(f"   Total: {len(models)}")
            for model in models[:2]:
                print(f"     - {model.get('model_id')}")
        
        await service.close()
        print("\n" + "=" * 70)
        print("Tests completed!")
    
    asyncio.run(main())
