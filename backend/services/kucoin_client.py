#!/usr/bin/env python3
"""
KuCoin API Client
کلاینت KuCoin با پشتیبانی Smart Access
"""

import httpx
import logging
from typing import Optional, Dict, List
from datetime import datetime

logger = logging.getLogger(__name__)


class KuCoinClient:
    """
    KuCoin Exchange API Client
    
    KuCoin یکی از صرافی‌های محبوب که ممکنه در بعضی مناطق فیلتر باشه
    از Smart Access برای دسترسی قابل اطمینان استفاده می‌کنه
    """
    
    def __init__(self):
        self.base_url = "https://api.kucoin.com"
        self.futures_url = "https://api-futures.kucoin.com"
        
    async def _make_request(
        self,
        url: str,
        params: Optional[Dict] = None,
        use_rotating_access: bool = True
    ) -> Optional[Dict]:
        """
        ارسال درخواست به KuCoin با Rotating DNS/Proxy
        
        Args:
            url: آدرس API
            params: پارامترهای درخواست
            use_rotating_access: استفاده از Rotating Access (DNS/Proxy چرخشی)
        """
        try:
            if use_rotating_access:
                # استفاده از Rotating Access برای امنیت و دسترسی همیشگی
                from backend.services.rotating_access_manager import rotating_access_manager
                
                logger.info(f"🔐 KuCoin request with ROTATING Access: {url}")
                response = await rotating_access_manager.secure_fetch(
                    url,
                    params=params,
                    use_rotating_dns=True,
                    use_rotating_proxy=True
                )
            else:
                # درخواست مستقیم (فقط برای تست)
                logger.info(f"🔗 KuCoin direct request: {url}")
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.get(url, params=params)
            
            if response and response.status_code == 200:
                data = response.json()
                
                # بررسی پاسخ KuCoin
                if data.get("code") == "200000":  # Success code
                    logger.info(f"✅ KuCoin request successful")
                    return data.get("data")
                else:
                    logger.error(f"❌ KuCoin API error: {data.get('msg')}")
                    return None
            else:
                logger.error(f"❌ KuCoin request failed: {response.status_code if response else 'No response'}")
                return None
        
        except Exception as e:
            logger.error(f"❌ KuCoin request exception: {e}")
            return None
    
    async def get_ticker(self, symbol: str = "BTC-USDT", use_rotating_access: bool = True) -> Optional[Dict]:
        """
        دریافت قیمت فعلی یک ارز
        
        Args:
            symbol: نماد ارز (مثلاً BTC-USDT)
        
        Returns:
            {
                "symbol": "BTC-USDT",
                "price": "50000.5",
                "changeRate": "0.0123",
                "high": "51000",
                "low": "49000",
                ...
            }
        """
        url = f"{self.base_url}/api/v1/market/stats"
        params = {"symbol": symbol}
        
        logger.info(f"📊 Getting KuCoin ticker for {symbol}")
        data = await self._make_request(url, params, use_rotating_access=use_rotating_access)
        
        if data:
            return {
                "symbol": data.get("symbol"),
                "price": float(data.get("last", 0)),
                "high_24h": float(data.get("high", 0)),
                "low_24h": float(data.get("low", 0)),
                "volume_24h": float(data.get("vol", 0)),
                "change_24h": float(data.get("changeRate", 0)) * 100,
                "timestamp": datetime.now().isoformat()
            }
        
        return None
    
    async def get_all_tickers(self) -> Optional[List[Dict]]:
        """
        دریافت قیمت همه ارزها
        
        Returns:
            [
                {"symbol": "BTC-USDT", "price": 50000, ...},
                {"symbol": "ETH-USDT", "price": 3000, ...},
                ...
            ]
        """
        url = f"{self.base_url}/api/v1/market/allTickers"
        
        logger.info(f"📊 Getting all KuCoin tickers")
        data = await self._make_request(url, use_smart_access=True)
        
        if data and "ticker" in data:
            tickers = []
            for ticker in data["ticker"][:50]:  # محدود به 50 تا
                tickers.append({
                    "symbol": ticker.get("symbol"),
                    "price": float(ticker.get("last", 0)),
                    "volume_24h": float(ticker.get("vol", 0)),
                    "change_24h": float(ticker.get("changeRate", 0)) * 100
                })
            
            return tickers
        
        return None
    
    async def get_orderbook(self, symbol: str = "BTC-USDT", depth: int = 20) -> Optional[Dict]:
        """
        دریافت Order Book (لیست سفارشات)
        
        Args:
            symbol: نماد ارز
            depth: عمق order book (20 یا 100)
        
        Returns:
            {
                "bids": [[price, size], ...],
                "asks": [[price, size], ...],
                "timestamp": ...
            }
        """
        url = f"{self.base_url}/api/v1/market/orderbook/level2_{depth}"
        params = {"symbol": symbol}
        
        logger.info(f"📖 Getting KuCoin orderbook for {symbol}")
        data = await self._make_request(url, params, use_smart_access=True)
        
        if data:
            return {
                "symbol": symbol,
                "bids": [[float(p), float(s)] for p, s in data.get("bids", [])[:10]],
                "asks": [[float(p), float(s)] for p, s in data.get("asks", [])[:10]],
                "timestamp": data.get("time")
            }
        
        return None
    
    async def get_24h_stats(self, symbol: str = "BTC-USDT", use_rotating_access: bool = True) -> Optional[Dict]:
        """
        دریافت آمار 24 ساعته
        
        Returns:
            {
                "symbol": "BTC-USDT",
                "high": 51000,
                "low": 49000,
                "vol": 12345,
                "last": 50000,
                "changeRate": 0.0123
            }
        """
        url = f"{self.base_url}/api/v1/market/stats"
        params = {"symbol": symbol}
        
        data = await self._make_request(url, params, use_rotating_access=use_rotating_access)
        
        if data:
            return {
                "symbol": data.get("symbol"),
                "high_24h": float(data.get("high", 0)),
                "low_24h": float(data.get("low", 0)),
                "volume_24h": float(data.get("vol", 0)),
                "price": float(data.get("last", 0)),
                "change_rate": float(data.get("changeRate", 0)),
                "change_price": float(data.get("changePrice", 0))
            }
        
        return None
    
    async def get_klines(
        self,
        symbol: str = "BTC-USDT",
        interval: str = "1hour",
        start_time: Optional[int] = None,
        end_time: Optional[int] = None
    ) -> Optional[List[Dict]]:
        """
        دریافت کندل‌ها (OHLCV)
        
        Args:
            symbol: نماد ارز
            interval: بازه زمانی (1min, 5min, 15min, 30min, 1hour, 4hour, 1day, 1week)
            start_time: زمان شروع (timestamp)
            end_time: زمان پایان (timestamp)
        
        Returns:
            [
                {
                    "time": timestamp,
                    "open": 50000,
                    "high": 51000,
                    "low": 49000,
                    "close": 50500,
                    "volume": 12345
                },
                ...
            ]
        """
        url = f"{self.base_url}/api/v1/market/candles"
        params = {
            "symbol": symbol,
            "type": interval
        }
        
        if start_time:
            params["startAt"] = start_time
        if end_time:
            params["endAt"] = end_time
        
        logger.info(f"📈 Getting KuCoin klines for {symbol} ({interval})")
        data = await self._make_request(url, params, use_smart_access=True)
        
        if data:
            klines = []
            for candle in data:
                # KuCoin format: [timestamp, open, close, high, low, volume, turnover]
                klines.append({
                    "timestamp": int(candle[0]),
                    "open": float(candle[1]),
                    "close": float(candle[2]),
                    "high": float(candle[3]),
                    "low": float(candle[4]),
                    "volume": float(candle[5])
                })
            
            return klines
        
        return None
    
    async def get_currencies(self) -> Optional[List[Dict]]:
        """
        دریافت لیست همه ارزها
        
        Returns:
            [
                {
                    "currency": "BTC",
                    "name": "Bitcoin",
                    "fullName": "Bitcoin",
                    "precision": 8
                },
                ...
            ]
        """
        url = f"{self.base_url}/api/v1/currencies"
        
        logger.info(f"💰 Getting KuCoin currencies list")
        data = await self._make_request(url, use_smart_access=True)
        
        if data:
            return [{
                "currency": curr.get("currency"),
                "name": curr.get("name"),
                "full_name": curr.get("fullName"),
                "precision": curr.get("precision")
            } for curr in data[:100]]  # محدود به 100 تا
        
        return None
    
    async def health_check(self, use_rotating_access: bool = True) -> bool:
        """
        بررسی سلامت API
        
        Returns:
            True اگر API در دسترس باشه
        """
        url = f"{self.base_url}/api/v1/status"
        
        try:
            data = await self._make_request(url, use_rotating_access=use_rotating_access)
            
            if data:
                status = data.get("status")
                logger.info(f"💚 KuCoin health check: {status}")
                return status == "open"
            
            return False
        
        except:
            return False


# Global instance
kucoin_client = KuCoinClient()


__all__ = ["KuCoinClient", "kucoin_client"]

