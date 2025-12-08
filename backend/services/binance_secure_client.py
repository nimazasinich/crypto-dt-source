#!/usr/bin/env python3
"""
Binance Secure Client with Rotating DNS/Proxy
کلاینت امن Binance با DNS و Proxy چرخشی
"""

import httpx
import logging
from typing import Optional, Dict, List
from datetime import datetime

from backend.services.rotating_access_manager import rotating_access_manager

logger = logging.getLogger(__name__)


class BinanceSecureClient:
    """
    Binance API Client با امنیت بالا
    
    همیشه از Rotating DNS/Proxy استفاده می‌کنه
    هیچ وقت مشکل دسترسی نداریم!
    """
    
    def __init__(self):
        self.base_url = "https://api.binance.com"
        self.api_urls = [
            "https://api.binance.com",
            "https://api1.binance.com",
            "https://api2.binance.com",
            "https://api3.binance.com"
        ]
        self.current_api_index = 0
    
    def get_next_api_url(self) -> str:
        """چرخش بین URLهای مختلف Binance"""
        url = self.api_urls[self.current_api_index]
        self.current_api_index = (self.current_api_index + 1) % len(self.api_urls)
        return url
    
    async def get_24h_ticker(self, symbol: str = "BTCUSDT") -> Optional[Dict]:
        """
        دریافت قیمت 24 ساعته با Rotating Access
        
        Args:
            symbol: نماد ارز (مثلاً BTCUSDT)
        
        Returns:
            {
                "symbol": "BTCUSDT",
                "lastPrice": "50000.00",
                "priceChange": "500.00",
                "priceChangePercent": "1.01",
                ...
            }
        """
        # استفاده از API URL چرخشی
        base_url = self.get_next_api_url()
        url = f"{base_url}/api/v3/ticker/24hr"
        
        logger.info(f"📊 Getting Binance ticker for {symbol} (Secure)")
        
        response = await rotating_access_manager.secure_fetch(
            url,
            params={"symbol": symbol},
            use_rotating_dns=True,
            use_rotating_proxy=True
        )
        
        if response and response.status_code == 200:
            data = response.json()
            logger.info(f"✅ Binance ticker retrieved: ${data.get('lastPrice')}")
            return data
        
        return None
    
    async def get_price(self, symbol: str = "BTCUSDT") -> Optional[float]:
        """
        دریافت قیمت فعلی (ساده)
        
        Returns:
            float: قیمت (مثلاً 50000.5)
        """
        base_url = self.get_next_api_url()
        url = f"{base_url}/api/v3/ticker/price"
        
        response = await rotating_access_manager.secure_fetch(
            url,
            params={"symbol": symbol},
            use_rotating_dns=True,
            use_rotating_proxy=True
        )
        
        if response and response.status_code == 200:
            data = response.json()
            price = float(data.get("price", 0))
            logger.info(f"✅ Binance price: {symbol} = ${price}")
            return price
        
        return None
    
    async def get_ohlcv(
        self,
        symbol: str = "BTCUSDT",
        interval: str = "1h",
        limit: int = 100
    ) -> Optional[List[Dict]]:
        """
        دریافت کندل‌ها (OHLCV)
        
        Args:
            symbol: نماد ارز
            interval: بازه زمانی (1m, 5m, 15m, 1h, 4h, 1d)
            limit: تعداد کندل
        
        Returns:
            [
                {
                    "timestamp": 1234567890,
                    "open": 50000,
                    "high": 51000,
                    "low": 49000,
                    "close": 50500,
                    "volume": 12345
                },
                ...
            ]
        """
        base_url = self.get_next_api_url()
        url = f"{base_url}/api/v3/klines"
        
        logger.info(f"📈 Getting Binance OHLCV for {symbol} ({interval})")
        
        response = await rotating_access_manager.secure_fetch(
            url,
            params={
                "symbol": symbol,
                "interval": interval,
                "limit": limit
            },
            use_rotating_dns=True,
            use_rotating_proxy=True
        )
        
        if response and response.status_code == 200:
            data = response.json()
            
            # تبدیل به فرمت خوانا
            ohlcv = []
            for candle in data:
                ohlcv.append({
                    "timestamp": candle[0],
                    "open": float(candle[1]),
                    "high": float(candle[2]),
                    "low": float(candle[3]),
                    "close": float(candle[4]),
                    "volume": float(candle[5])
                })
            
            logger.info(f"✅ Got {len(ohlcv)} candles")
            return ohlcv
        
        return None
    
    async def get_orderbook(self, symbol: str = "BTCUSDT", limit: int = 20) -> Optional[Dict]:
        """
        دریافت Order Book
        
        Returns:
            {
                "bids": [[price, quantity], ...],
                "asks": [[price, quantity], ...],
                ...
            }
        """
        base_url = self.get_next_api_url()
        url = f"{base_url}/api/v3/depth"
        
        response = await rotating_access_manager.secure_fetch(
            url,
            params={"symbol": symbol, "limit": limit},
            use_rotating_dns=True,
            use_rotating_proxy=True
        )
        
        if response and response.status_code == 200:
            data = response.json()
            logger.info(f"✅ Binance orderbook retrieved")
            return data
        
        return None
    
    async def get_exchange_info(self, symbol: Optional[str] = None) -> Optional[Dict]:
        """
        دریافت اطلاعات صرافی
        
        Args:
            symbol: نماد ارز (اختیاری)
        """
        base_url = self.get_next_api_url()
        url = f"{base_url}/api/v3/exchangeInfo"
        
        params = {}
        if symbol:
            params["symbol"] = symbol
        
        response = await rotating_access_manager.secure_fetch(
            url,
            params=params if params else None,
            use_rotating_dns=True,
            use_rotating_proxy=True
        )
        
        if response and response.status_code == 200:
            data = response.json()
            logger.info(f"✅ Binance exchange info retrieved")
            return data
        
        return None
    
    async def health_check(self) -> bool:
        """
        بررسی سلامت API
        
        Returns:
            True اگر Binance در دسترس باشه
        """
        base_url = self.get_next_api_url()
        url = f"{base_url}/api/v3/ping"
        
        try:
            response = await rotating_access_manager.secure_fetch(
                url,
                use_rotating_dns=True,
                use_rotating_proxy=True
            )
            
            if response and response.status_code == 200:
                logger.info(f"💚 Binance health check: OK")
                return True
            
            return False
        
        except:
            return False


# Global instance
binance_secure_client = BinanceSecureClient()


__all__ = ["BinanceSecureClient", "binance_secure_client"]

