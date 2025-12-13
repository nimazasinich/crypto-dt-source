"""
OHLCV Service with Multi-Provider Fallback
Automatically switches between Binance, CoinGecko, and other providers
"""

import logging
from typing import Dict, List, Any, Optional
from fastapi import HTTPException
from .api_fallback_manager import get_fallback_manager
import os

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
        
        # Priority 2: CoinGecko (reliable alternative)
        self.manager.add_provider(
            name="CoinGecko",
            priority=2,
            fetch_function=self._fetch_coingecko,
            cooldown_seconds=60,
            max_failures=3
        )
        
        # Priority 3: HuggingFace Space (proxy to other services)
        self.manager.add_provider(
            name="HuggingFace",
            priority=3,
            fetch_function=self._fetch_huggingface,
            cooldown_seconds=300,
            max_failures=5
        )
        
        logger.info("✅ OHLCV Service initialized with 3 providers (Binance, CoinGecko, HuggingFace)")
    
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
        except HTTPException as e:
            if e.status_code == 451:
                logger.warning(f"⚠️ Binance access restricted (HTTP 451). Falling back to CoinGecko.")
            else:
                logger.error(f"Binance fetch failed: {e.detail}")
            raise
        except Exception as e:
            logger.error(f"Binance fetch failed: {e}")
            raise
    
    async def _fetch_coingecko(self, symbol: str, timeframe: str, limit: int = 100) -> Dict:
        """Fetch from CoinGecko API"""
        try:
            from backend.services.coingecko_client import CoinGeckoClient
            client = CoinGeckoClient()
            
            # CoinGecko uses days, not limit
            days = self._timeframe_to_days(timeframe, limit)
            data = await client.get_ohlcv(symbol, days=days)
            
            return {
                "symbol": symbol.upper(),
                "timeframe": timeframe,
                "interval": timeframe,
                "limit": limit,
                "count": len(data.get("prices", [])),
                "ohlcv": self._format_coingecko_data(data),
                "source": "coingecko"
            }
        except Exception as e:
            logger.error(f"CoinGecko fetch failed: {e}")
            raise
    
    def _timeframe_to_days(self, timeframe: str, limit: int) -> int:
        """Convert timeframe and limit to days for CoinGecko"""
        # Map timeframes to approximate days
        timeframe_hours = {
            "1m": 1/60, "5m": 5/60, "15m": 15/60, "30m": 0.5,
            "1h": 1, "4h": 4, "1d": 24, "1w": 168
        }
        hours = timeframe_hours.get(timeframe, 1)
        days = max(1, int((hours * limit) / 24))
        return min(days, 365)  # CoinGecko max 365 days
    
    def _format_coingecko_data(self, data: Dict) -> List[Dict]:
        """Format CoinGecko data to standard OHLCV format"""
        candles = []
        prices = data.get("prices", [])
        
        for price_point in prices:
            timestamp, price = price_point
            candles.append({
                "timestamp": int(timestamp),
                "open": price,
                "high": price,  # Approximate
                "low": price,   # Approximate
                "close": price,
                "volume": 0
            })
        
        return candles
    
    async def _fetch_huggingface(self, symbol: str, timeframe: str, limit: int = 100) -> Dict:
        """Fetch from HuggingFace Space"""
        import httpx
        
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
