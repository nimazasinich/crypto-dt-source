"""
OHLCV Service with Multi-Provider Fallback
Automatically switches between Binance, CoinGecko, and other providers
"""

import logging
from typing import Dict, List, Any, Optional
from .api_fallback_manager import get_fallback_manager

logger = logging.getLogger(__name__)


class OHLCVService:
    """Service for fetching OHLCV data with automatic fallback"""
    
    def __init__(self):
        self.manager = get_fallback_manager("OHLCV")
        self._setup_providers()
    
    def _setup_providers(self):
        """Setup OHLCV providers in priority order"""
        # Priority 1: Binance (fastest, most reliable)
        self.manager.add_provider(
            name="Binance",
            priority=1,
            fetch_function=self._fetch_binance,
            cooldown_seconds=180,
            max_failures=3
        )
        
        # Priority 2: HuggingFace Space (fallback)
        self.manager.add_provider(
            name="HuggingFace",
            priority=2,
            fetch_function=self._fetch_huggingface,
            cooldown_seconds=300,
            max_failures=5
        )
        
        # Priority 3: Mock/Demo data (always available)
        self.manager.add_provider(
            name="Demo",
            priority=999,
            fetch_function=self._fetch_demo,
            cooldown_seconds=0,
            max_failures=999  # Never fails
        )
        
        logger.info("✅ OHLCV Service initialized with 3 providers")
    
    async def _fetch_binance(self, symbol: str, timeframe: str, limit: int = 100) -> Dict:
        """Fetch from Binance API"""
        try:
            from backend.services.binance_client import BinanceClient
            client = BinanceClient()
            candles = await client.get_ohlcv(symbol, timeframe=timeframe, limit=limit)
            
            return {
                "symbol": symbol.upper(),
                "timeframe": timeframe,
                "interval": timeframe,
                "limit": limit,
                "count": len(candles),
                "ohlcv": candles,
                "source": "binance"
            }
        except Exception as e:
            logger.error(f"Binance fetch failed: {e}")
            raise
    
    async def _fetch_huggingface(self, symbol: str, timeframe: str, limit: int = 100) -> Dict:
        """Fetch from HuggingFace Space"""
        import httpx
        import os
        
        base_url = os.getenv("HF_SPACE_BASE_URL", "https://really-amin-datasourceforcryptocurrency.hf.space")
        token = os.getenv("HF_API_TOKEN", "").strip()
        
        headers = {"Authorization": f"Bearer {token}"} if token else {}
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{base_url}/api/ohlcv/{symbol}",
                params={"interval": timeframe, "limit": limit},
                headers=headers,
                timeout=15.0
            )
            response.raise_for_status()
            return response.json()
    
    async def _fetch_demo(self, symbol: str, timeframe: str, limit: int = 100) -> Dict:
        """Fetch demo/fallback data"""
        import time
        import random
        
        # Generate realistic demo candles
        base_price = 50000 if symbol.upper() == "BTC" else 3000
        candles = []
        
        for i in range(limit):
            timestamp = int(time.time()) - (i * 3600)  # 1 hour intervals
            open_price = base_price + random.uniform(-1000, 1000)
            close_price = open_price + random.uniform(-500, 500)
            high_price = max(open_price, close_price) + random.uniform(0, 300)
            low_price = min(open_price, close_price) - random.uniform(0, 300)
            volume = random.uniform(1000, 10000)
            
            candles.append({
                "t": timestamp * 1000,
                "o": round(open_price, 2),
                "h": round(high_price, 2),
                "l": round(low_price, 2),
                "c": round(close_price, 2),
                "v": round(volume, 2)
            })
        
        return {
            "symbol": symbol.upper(),
            "timeframe": timeframe,
            "interval": timeframe,
            "limit": limit,
            "count": len(candles),
            "ohlcv": candles[::-1],  # Reverse to oldest first
            "source": "demo",
            "warning": "Using demo data - live data unavailable"
        }
    
    async def get_ohlcv(
        self,
        symbol: str,
        timeframe: str = "1h",
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Get OHLCV data with automatic fallback
        
        Args:
            symbol: Trading symbol (e.g., "BTC", "ETH")
            timeframe: Timeframe (e.g., "1h", "4h", "1d")
            limit: Number of candles
        
        Returns:
            Dict with OHLCV data and metadata
        """
        result = await self.manager.fetch_with_fallback(
            symbol=symbol,
            timeframe=timeframe,
            limit=limit
        )
        
        if not result["success"]:
            logger.error(f"All OHLCV providers failed for {symbol}")
        
        return result
    
    def get_status(self) -> Dict[str, Any]:
        """Get status of all OHLCV providers"""
        return self.manager.get_status()


# Global singleton
_ohlcv_service: Optional[OHLCVService] = None


def get_ohlcv_service() -> OHLCVService:
    """Get or create the OHLCV service singleton"""
    global _ohlcv_service
    if _ohlcv_service is None:
        _ohlcv_service = OHLCVService()
    return _ohlcv_service

