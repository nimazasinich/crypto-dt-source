#!/usr/bin/env python3
"""
Hugging Face Dataset Loader Service
دسترسی به Dataset‌های رایگان HuggingFace
"""

import pandas as pd
from typing import Dict, List, Optional, Any, Union
import logging
import asyncio
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

# بررسی وجود کتابخانه datasets
try:
    from datasets import load_dataset
    DATASETS_AVAILABLE = True
except ImportError:
    DATASETS_AVAILABLE = False
    logger.warning("datasets library not available. Install with: pip install datasets")


class HFDatasetService:
    """
    سرویس برای بارگذاری و استفاده از Dataset‌های رایگان HF
    
    مزایا:
    - دسترسی رایگان به 100,000+ dataset
    - داده تاریخی کریپتو
    - داده اخبار و sentiment
    - بدون نیاز به API key (برای dataset‌های public)
    """
    
    # Dataset‌های معتبر کریپتو که تأیید شده‌اند
    CRYPTO_DATASETS = {
        "linxy/CryptoCoin": {
            "description": "182 فایل CSV با OHLCV برای 26 کریپتو",
            "symbols": ["BTC", "ETH", "BNB", "SOL", "ADA", "XRP", "DOT", "DOGE", 
                       "AVAX", "MATIC", "LINK", "UNI", "ATOM", "LTC", "XMR"],
            "timeframes": ["1m", "5m", "15m", "30m", "1h", "4h", "1d"],
            "columns": ["timestamp", "open", "high", "low", "close", "volume"],
            "date_range": "2017-present"
        },
        "WinkingFace/CryptoLM-Bitcoin-BTC-USDT": {
            "description": "داده تاریخی Bitcoin با indicators",
            "symbols": ["BTC"],
            "timeframes": ["1h"],
            "columns": ["timestamp", "open", "high", "low", "close", "volume", "rsi", "macd"],
            "date_range": "2019-2023"
        },
        "sebdg/crypto_data": {
            "description": "OHLCV + indicators برای 10 کریپتو",
            "symbols": ["BTC", "ETH", "BNB", "ADA", "DOT", "LINK", "UNI", "AVAX", "MATIC", "SOL"],
            "indicators": ["RSI", "MACD", "Bollinger Bands", "EMA", "SMA"],
            "timeframes": ["1h", "4h", "1d"],
            "date_range": "2020-present"
        }
    }
    
    NEWS_DATASETS = {
        "Kwaai/crypto-news": {
            "description": "اخبار کریپتو با sentiment labels",
            "size": "10,000+ news articles",
            "languages": ["en"],
            "date_range": "2020-2023"
        },
        "jacopoteneggi/crypto-news": {
            "description": "اخبار روزانه کریپتو",
            "size": "50,000+ articles",
            "sources": ["CoinDesk", "CoinTelegraph", "Bitcoin Magazine"],
            "date_range": "2018-2023"
        }
    }
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 3600  # 1 ساعت
    
    def is_available(self) -> bool:
        """بررسی در دسترس بودن کتابخانه datasets"""
        return DATASETS_AVAILABLE
    
    async def load_crypto_ohlcv(
        self, 
        symbol: str = "BTC", 
        timeframe: str = "1h",
        limit: int = 1000,
        dataset_name: str = "linxy/CryptoCoin"
    ) -> pd.DataFrame:
        """
        بارگذاری OHLCV از Dataset
        
        Args:
            symbol: نماد کریپتو (BTC, ETH, ...)
            timeframe: بازه زمانی (1m, 5m, 1h, 1d, ...)
            limit: تعداد رکورد
            dataset_name: نام dataset
        
        Returns:
            DataFrame شامل OHLCV
        """
        if not DATASETS_AVAILABLE:
            logger.error("datasets library not available")
            return pd.DataFrame()
        
        try:
            # کلید cache
            cache_key = f"{dataset_name}:{symbol}:{timeframe}:{limit}"
            
            # بررسی cache
            if cache_key in self.cache:
                cached_data, cached_time = self.cache[cache_key]
                if (datetime.now() - cached_time).total_seconds() < self.cache_ttl:
                    logger.info(f"Returning cached data for {cache_key}")
                    return cached_data
            
            logger.info(f"Loading dataset {dataset_name} for {symbol}...")
            
            # بارگذاری Dataset
            # استفاده از streaming برای صرفه‌جویی در RAM
            dataset = load_dataset(
                dataset_name,
                split="train",
                streaming=True
            )
            
            # تبدیل به DataFrame (محدود به limit رکورد)
            records = []
            count = 0
            
            for record in dataset:
                # فیلتر بر اساس symbol (اگر فیلد symbol موجود باشد)
                if "symbol" in record:
                    if record["symbol"].upper() != symbol.upper():
                        continue
                
                records.append(record)
                count += 1
                
                if count >= limit:
                    break
            
            df = pd.DataFrame(records)
            
            # استانداردسازی ستون‌ها
            if not df.empty:
                # تبدیل timestamp اگر رشته است
                if "timestamp" in df.columns:
                    if df["timestamp"].dtype == "object":
                        df["timestamp"] = pd.to_datetime(df["timestamp"])
                
                # مرتب‌سازی بر اساس timestamp
                if "timestamp" in df.columns:
                    df = df.sort_values("timestamp", ascending=False)
                
                # ذخیره در cache
                self.cache[cache_key] = (df, datetime.now())
            
            logger.info(f"Loaded {len(df)} records for {symbol}")
            return df
            
        except Exception as e:
            logger.error(f"Error loading dataset: {e}")
            return pd.DataFrame()
    
    async def load_crypto_news(
        self,
        limit: int = 100,
        dataset_name: str = "Kwaai/crypto-news"
    ) -> List[Dict[str, Any]]:
        """
        بارگذاری اخبار کریپتو از Dataset
        
        Args:
            limit: تعداد خبر
            dataset_name: نام dataset
        
        Returns:
            لیست اخبار
        """
        if not DATASETS_AVAILABLE:
            logger.error("datasets library not available")
            return []
        
        try:
            logger.info(f"Loading news from {dataset_name}...")
            
            # بارگذاری Dataset
            dataset = load_dataset(
                dataset_name,
                split="train",
                streaming=True
            )
            
            # استخراج اخبار
            news_items = []
            count = 0
            
            for record in dataset:
                news_item = {
                    "title": record.get("title", ""),
                    "content": record.get("text", record.get("content", "")),
                    "url": record.get("url", ""),
                    "source": record.get("source", "HuggingFace Dataset"),
                    "published_at": record.get("date", record.get("published_at", "")),
                    "sentiment": record.get("sentiment", "neutral")
                }
                
                news_items.append(news_item)
                count += 1
                
                if count >= limit:
                    break
            
            logger.info(f"Loaded {len(news_items)} news articles")
            return news_items
            
        except Exception as e:
            logger.error(f"Error loading news: {e}")
            return []
    
    async def get_historical_prices(
        self,
        symbol: str,
        days: int = 30,
        timeframe: str = "1h"
    ) -> Dict[str, Any]:
        """
        دریافت قیمت‌های تاریخی
        
        Args:
            symbol: نماد کریپتو
            days: تعداد روز گذشته
            timeframe: بازه زمانی
        
        Returns:
            Dict شامل داده قیمت و آمار
        """
        # محاسبه تعداد رکورد مورد نیاز
        records_per_day = {
            "1m": 1440,
            "5m": 288,
            "15m": 96,
            "30m": 48,
            "1h": 24,
            "4h": 6,
            "1d": 1
        }
        
        limit = records_per_day.get(timeframe, 24) * days
        
        # بارگذاری داده
        df = await self.load_crypto_ohlcv(symbol, timeframe, limit)
        
        if df.empty:
            return {
                "status": "error",
                "error": "No data available",
                "symbol": symbol
            }
        
        # محاسبه آمار
        latest_close = float(df.iloc[0]["close"]) if "close" in df.columns else 0
        earliest_close = float(df.iloc[-1]["close"]) if "close" in df.columns else 0
        
        price_change = latest_close - earliest_close
        price_change_pct = (price_change / earliest_close * 100) if earliest_close > 0 else 0
        
        high_price = float(df["high"].max()) if "high" in df.columns else 0
        low_price = float(df["low"].min()) if "low" in df.columns else 0
        avg_volume = float(df["volume"].mean()) if "volume" in df.columns else 0
        
        return {
            "status": "success",
            "symbol": symbol,
            "timeframe": timeframe,
            "days": days,
            "records": len(df),
            "latest_price": latest_close,
            "price_change": price_change,
            "price_change_pct": price_change_pct,
            "high": high_price,
            "low": low_price,
            "avg_volume": avg_volume,
            "data": df.to_dict(orient="records")[:100],  # محدود به 100 رکورد اول
            "source": "HuggingFace Dataset",
            "is_free": True
        }
    
    def get_available_datasets(self) -> Dict[str, Any]:
        """
        لیست Dataset‌های موجود
        """
        return {
            "crypto_data": {
                "total": len(self.CRYPTO_DATASETS),
                "datasets": self.CRYPTO_DATASETS
            },
            "news_data": {
                "total": len(self.NEWS_DATASETS),
                "datasets": self.NEWS_DATASETS
            },
            "library_available": DATASETS_AVAILABLE,
            "installation": "pip install datasets" if not DATASETS_AVAILABLE else "✅ Installed"
        }
    
    def get_supported_symbols(self) -> List[str]:
        """
        لیست نمادهای پشتیبانی شده
        """
        symbols = set()
        for dataset_info in self.CRYPTO_DATASETS.values():
            symbols.update(dataset_info.get("symbols", []))
        return sorted(list(symbols))
    
    def get_supported_timeframes(self) -> List[str]:
        """
        لیست بازه‌های زمانی پشتیبانی شده
        """
        timeframes = set()
        for dataset_info in self.CRYPTO_DATASETS.values():
            timeframes.update(dataset_info.get("timeframes", []))
        return sorted(list(timeframes))


# ===== توابع کمکی =====

async def quick_price_data(
    symbol: str = "BTC",
    days: int = 7
) -> Dict[str, Any]:
    """
    دریافت سریع داده قیمت
    
    Args:
        symbol: نماد کریپتو
        days: تعداد روز
    
    Returns:
        Dict شامل داده و آمار
    """
    service = HFDatasetService()
    return await service.get_historical_prices(symbol, days)


async def quick_crypto_news(limit: int = 10) -> List[Dict[str, Any]]:
    """
    دریافت سریع اخبار کریپتو
    
    Args:
        limit: تعداد خبر
    
    Returns:
        لیست اخبار
    """
    service = HFDatasetService()
    return await service.load_crypto_news(limit)


# ===== مثال استفاده =====
if __name__ == "__main__":
    async def test_service():
        """تست سرویس"""
        print("🧪 Testing HF Dataset Service...")
        
        service = HFDatasetService()
        
        # بررسی در دسترس بودن
        print(f"\n1️⃣ Library available: {service.is_available()}")
        
        if not service.is_available():
            print("   ⚠️  Install with: pip install datasets")
            return
        
        # لیست dataset‌ها
        print("\n2️⃣ Available Datasets:")
        datasets = service.get_available_datasets()
        print(f"   Crypto datasets: {datasets['crypto_data']['total']}")
        print(f"   News datasets: {datasets['news_data']['total']}")
        
        # نمادهای پشتیبانی شده
        print("\n3️⃣ Supported Symbols:")
        symbols = service.get_supported_symbols()
        print(f"   {', '.join(symbols[:10])}...")
        
        # تست بارگذاری قیمت
        print("\n4️⃣ Loading BTC price data...")
        try:
            result = await service.get_historical_prices("BTC", days=7, timeframe="1h")
            if result["status"] == "success":
                print(f"   ✅ Loaded {result['records']} records")
                print(f"   Latest price: ${result['latest_price']:,.2f}")
                print(f"   Change: {result['price_change_pct']:+.2f}%")
                print(f"   High: ${result['high']:,.2f}")
                print(f"   Low: ${result['low']:,.2f}")
            else:
                print(f"   ❌ Error: {result.get('error')}")
        except Exception as e:
            print(f"   ❌ Exception: {e}")
        
        # تست بارگذاری اخبار
        print("\n5️⃣ Loading crypto news...")
        try:
            news = await service.load_crypto_news(limit=5)
            print(f"   ✅ Loaded {len(news)} news articles")
            for i, article in enumerate(news[:3], 1):
                print(f"   {i}. {article['title'][:60]}...")
        except Exception as e:
            print(f"   ❌ Exception: {e}")
        
        print("\n✅ Testing complete!")
    
    import asyncio
    asyncio.run(test_service())
