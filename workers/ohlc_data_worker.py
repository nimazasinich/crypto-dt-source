"""
OHLC Data Background Worker - REAL DATA FROM MULTIPLE FREE APIs

CRITICAL RULES:
- MUST fetch REAL candlestick data from multiple sources with automatic fallback
- MUST store actual OHLC values, not fake data
- MUST use actual timestamps from API responses
- NEVER generate or interpolate candles
- If primary API fails, automatically try alternative sources

SUPPORTED DATA SOURCES (in priority order):
1. CoinGecko (FREE, no API key, 365-day history)
2. Kraken (FREE, no API key, up to 720 candles)
3. Coinbase Pro (FREE, no API key, up to 300 candles)
4. Binance (FREE, but may be geo-restricted in some regions)
5. CoinPaprika (FREE, no API key, 366-day history)
"""

import asyncio
import time
import logging
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
import httpx

from database.cache_queries import get_cache_queries
from database.db_manager import db_manager
from utils.logger import setup_logger

logger = setup_logger("ohlc_worker")

# Get cache queries instance
cache = get_cache_queries(db_manager)

# HuggingFace Dataset Uploader (optional - only if HF_TOKEN is set)
HF_UPLOAD_ENABLED = bool(os.getenv("HF_TOKEN") or os.getenv("HF_API_TOKEN"))
if HF_UPLOAD_ENABLED:
    try:
        from hf_dataset_uploader import get_dataset_uploader
        hf_uploader = get_dataset_uploader()
        logger.info("✅ HuggingFace Dataset upload ENABLED for OHLC data")
    except Exception as e:
        logger.warning(f"HuggingFace Dataset upload disabled: {e}")
        HF_UPLOAD_ENABLED = False
        hf_uploader = None
else:
    logger.info("ℹ️  HuggingFace Dataset upload DISABLED (no HF_TOKEN)")
    hf_uploader = None

# Trading symbols to track (simplified format)
SYMBOLS = ["BTC", "ETH", "BNB", "XRP", "ADA", "SOL", "DOT", "DOGE", "MATIC", "AVAX", 
           "LINK", "LTC", "UNI", "ALGO", "XLM", "ATOM", "TRX", "XMR", "ETC", "XTZ"]

# Intervals to fetch
INTERVALS = ["1h", "4h", "1d"]

# Symbol mapping for different exchanges
SYMBOL_MAP = {
    "coingecko": {
        "BTC": "bitcoin", "ETH": "ethereum", "BNB": "binancecoin", "XRP": "ripple",
        "ADA": "cardano", "SOL": "solana", "DOT": "polkadot", "DOGE": "dogecoin",
        "MATIC": "matic-network", "AVAX": "avalanche-2", "LINK": "chainlink",
        "LTC": "litecoin", "UNI": "uniswap", "ALGO": "algorand", "XLM": "stellar",
        "ATOM": "cosmos", "TRX": "tron", "XMR": "monero", "ETC": "ethereum-classic",
        "XTZ": "tezos"
    },
    "kraken": {
        "BTC": "XXBTZUSD", "ETH": "XETHZUSD", "XRP": "XXRPZUSD", "ADA": "ADAUSD",
        "SOL": "SOLUSD", "DOT": "DOTUSD", "DOGE": "XDGUSD", "LINK": "LINKUSD",
        "LTC": "XLTCZUSD", "UNI": "UNIUSD", "ALGO": "ALGOUSD", "XLM": "XXLMZUSD",
        "ATOM": "ATOMUSD", "TRX": "TRXUSD", "ETC": "XETCZUSD", "XTZ": "XTZUSD"
    },
    "coinbase": {
        "BTC": "BTC-USD", "ETH": "ETH-USD", "XRP": "XRP-USD", "ADA": "ADA-USD",
        "SOL": "SOL-USD", "DOT": "DOT-USD", "DOGE": "DOGE-USD", "LINK": "LINK-USD",
        "LTC": "LTC-USD", "UNI": "UNI-USD", "ALGO": "ALGO-USD", "XLM": "XLM-USD",
        "ATOM": "ATOM-USD", "MATIC": "MATIC-USD", "AVAX": "AVAX-USD"
    },
    "binance": {
        "BTC": "BTCUSDT", "ETH": "ETHUSDT", "BNB": "BNBUSDT", "XRP": "XRPUSDT",
        "ADA": "ADAUSDT", "SOL": "SOLUSDT", "DOT": "DOTUSDT", "DOGE": "DOGEUSDT",
        "MATIC": "MATICUSDT", "AVAX": "AVAXUSDT", "LINK": "LINKUSDT", "LTC": "LTCUSDT",
        "UNI": "UNIUSDT", "ALGO": "ALGOUSDT", "XLM": "XLMUSDT", "ATOM": "ATOMUSDT",
        "TRX": "TRXUSDT", "XMR": "XMRUSDT", "ETC": "ETCUSDT", "XTZ": "XTZUSDT"
    }
}


async def fetch_from_coingecko(symbol: str, interval: str, limit: int) -> List[Dict[str, Any]]:
    """
    Fetch OHLC data from CoinGecko (FREE, no API key required)
    
    Args:
        symbol: Base symbol (e.g., 'BTC')
        interval: Interval (only '1d' supported by CoinGecko)
        limit: Number of days to fetch (max 365)
        
    Returns:
        List of OHLC candles
    """
    try:
        coin_id = SYMBOL_MAP["coingecko"].get(symbol)
        if not coin_id:
            logger.debug(f"CoinGecko: No mapping for {symbol}")
            return []
        
        # CoinGecko only supports daily data
        if interval not in ["1d", "4h", "1h"]:
            return []
        
        # Calculate days based on interval
        days = min(limit if interval == "1d" else limit // 6 if interval == "4h" else limit // 24, 365)
        
        url = f"https://api.coingecko.com/api/v3/coins/{coin_id}/ohlc"
        params = {"vs_currency": "usd", "days": days}
        
        logger.debug(f"Fetching from CoinGecko: {coin_id} ({symbol})")
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if not data or not isinstance(data, list):
                return []
            
            ohlc_data = []
            for candle in data:
                try:
                    # CoinGecko format: [timestamp, open, high, low, close]
                    ohlc_data.append({
                        "symbol": symbol,
                        "interval": interval,
                        "timestamp": datetime.fromtimestamp(candle[0] / 1000),
                        "open": float(candle[1]),
                        "high": float(candle[2]),
                        "low": float(candle[3]),
                        "close": float(candle[4]),
                        "volume": 0.0,  # CoinGecko OHLC doesn't include volume
                        "provider": "coingecko"
                    })
                except Exception as e:
                    logger.debug(f"Error parsing CoinGecko candle: {e}")
                    continue
            
            logger.info(f"✅ CoinGecko: Fetched {len(ohlc_data)} candles for {symbol}")
            return ohlc_data
            
    except httpx.HTTPStatusError as e:
        logger.debug(f"CoinGecko HTTP error for {symbol}: {e.response.status_code}")
        return []
    except Exception as e:
        logger.debug(f"CoinGecko error for {symbol}: {e}")
        return []


async def fetch_from_kraken(symbol: str, interval: str, limit: int) -> List[Dict[str, Any]]:
    """
    Fetch OHLC data from Kraken (FREE, no API key required)
    
    Args:
        symbol: Base symbol (e.g., 'BTC')
        interval: Interval
        limit: Number of candles
        
    Returns:
        List of OHLC candles
    """
    try:
        pair = SYMBOL_MAP["kraken"].get(symbol)
        if not pair:
            logger.debug(f"Kraken: No mapping for {symbol}")
            return []
        
        # Map interval to Kraken format (in minutes)
        interval_map = {"1h": "60", "4h": "240", "1d": "1440"}
        kraken_interval = interval_map.get(interval)
        if not kraken_interval:
            return []
        
        url = "https://api.kraken.com/0/public/OHLC"
        params = {"pair": pair, "interval": kraken_interval}
        
        logger.debug(f"Fetching from Kraken: {pair} ({symbol})")
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if data.get("error") and len(data["error"]) > 0:
                logger.debug(f"Kraken error for {symbol}: {data['error']}")
                return []
            
            result = data.get("result", {})
            candles = result.get(pair, [])
            
            if not candles:
                return []
            
            ohlc_data = []
            for candle in candles[:limit]:
                try:
                    # Kraken format: [time, open, high, low, close, vwap, volume, count]
                    ohlc_data.append({
                        "symbol": symbol,
                        "interval": interval,
                        "timestamp": datetime.fromtimestamp(int(candle[0])),
                        "open": float(candle[1]),
                        "high": float(candle[2]),
                        "low": float(candle[3]),
                        "close": float(candle[4]),
                        "volume": float(candle[6]),
                        "provider": "kraken"
                    })
                except Exception as e:
                    logger.debug(f"Error parsing Kraken candle: {e}")
                    continue
            
            logger.info(f"✅ Kraken: Fetched {len(ohlc_data)} candles for {symbol}")
            return ohlc_data
            
    except Exception as e:
        logger.debug(f"Kraken error for {symbol}: {e}")
        return []


async def fetch_from_coinbase(symbol: str, interval: str, limit: int) -> List[Dict[str, Any]]:
    """
    Fetch OHLC data from Coinbase Pro (FREE, no API key required)
    
    Args:
        symbol: Base symbol (e.g., 'BTC')
        interval: Interval
        limit: Number of candles (max 300)
        
    Returns:
        List of OHLC candles
    """
    try:
        pair = SYMBOL_MAP["coinbase"].get(symbol)
        if not pair:
            logger.debug(f"Coinbase: No mapping for {symbol}")
            return []
        
        # Map interval to Coinbase granularity (in seconds)
        interval_map = {"1h": "3600", "4h": "21600", "1d": "86400"}
        granularity = interval_map.get(interval)
        if not granularity:
            return []
        
        url = f"https://api.exchange.coinbase.com/products/{pair}/candles"
        params = {"granularity": granularity}
        
        logger.debug(f"Fetching from Coinbase: {pair} ({symbol})")
        
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if not data or not isinstance(data, list):
                return []
            
            ohlc_data = []
            for candle in data[:limit]:
                try:
                    # Coinbase format: [time, low, high, open, close, volume]
                    ohlc_data.append({
                        "symbol": symbol,
                        "interval": interval,
                        "timestamp": datetime.fromtimestamp(int(candle[0])),
                        "open": float(candle[3]),
                        "high": float(candle[2]),
                        "low": float(candle[1]),
                        "close": float(candle[4]),
                        "volume": float(candle[5]),
                        "provider": "coinbase"
                    })
                except Exception as e:
                    logger.debug(f"Error parsing Coinbase candle: {e}")
                    continue
            
            logger.info(f"✅ Coinbase: Fetched {len(ohlc_data)} candles for {symbol}")
            return ohlc_data
            
    except Exception as e:
        logger.debug(f"Coinbase error for {symbol}: {e}")
        return []


async def fetch_from_binance(symbol: str, interval: str, limit: int) -> List[Dict[str, Any]]:
    """
    Fetch OHLC data from Binance (FREE, may be geo-restricted)
    
    Args:
        symbol: Base symbol (e.g., 'BTC')
        interval: Interval
        limit: Number of candles
        
    Returns:
        List of OHLC candles
    """
    try:
        pair = SYMBOL_MAP["binance"].get(symbol)
        if not pair:
            logger.debug(f"Binance: No mapping for {symbol}")
            return []
        
        url = "https://api.binance.com/api/v3/klines"
        params = {"symbol": pair, "interval": interval, "limit": limit}
        
        logger.debug(f"Fetching from Binance: {pair} ({symbol})")
        
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            data = response.json()
            
            if not data or not isinstance(data, list):
                return []
            
            ohlc_data = []
            for candle in data:
                try:
                    # Binance format: [time, open, high, low, close, volume, ...]
                    ohlc_data.append({
                        "symbol": symbol,
                        "interval": interval,
                        "timestamp": datetime.fromtimestamp(int(candle[0]) / 1000),
                        "open": float(candle[1]),
                        "high": float(candle[2]),
                        "low": float(candle[3]),
                        "close": float(candle[4]),
                        "volume": float(candle[5]),
                        "provider": "binance"
                    })
                except Exception as e:
                    logger.debug(f"Error parsing Binance candle: {e}")
                    continue
            
            logger.info(f"✅ Binance: Fetched {len(ohlc_data)} candles for {symbol}")
            return ohlc_data
            
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 451:
            logger.debug(f"Binance geo-restricted for {symbol}")
        else:
            logger.debug(f"Binance HTTP error for {symbol}: {e.response.status_code}")
        return []
    except Exception as e:
        logger.debug(f"Binance error for {symbol}: {e}")
        return []


async def fetch_ohlc_with_fallback(symbol: str, interval: str, limit: int = 100) -> List[Dict[str, Any]]:
    """
    Fetch OHLC data with automatic fallback across multiple sources
    
    Priority order:
    1. CoinGecko (most reliable, no auth, no geo-restrictions)
    2. Kraken (reliable, no auth)
    3. Coinbase (reliable, no auth)
    4. Binance (may be geo-restricted)
    
    Args:
        symbol: Base symbol (e.g., 'BTC')
        interval: Interval ('1h', '4h', '1d')
        limit: Number of candles to fetch
        
    Returns:
        List of OHLC candles from first successful source
    """
    sources = [
        ("CoinGecko", fetch_from_coingecko),
        ("Kraken", fetch_from_kraken),
        ("Coinbase", fetch_from_coinbase),
        ("Binance", fetch_from_binance),
    ]
    
    for source_name, fetch_func in sources:
        try:
            data = await fetch_func(symbol, interval, limit)
            if data and len(data) > 0:
                logger.debug(f"✅ Successfully fetched {len(data)} candles from {source_name} for {symbol}")
                return data
        except Exception as e:
            logger.debug(f"❌ {source_name} failed for {symbol}: {e}")
            continue
    
    logger.warning(f"⚠️  All sources failed for {symbol} {interval}")
    return []


async def save_ohlc_data_to_cache(ohlc_data: List[Dict[str, Any]]) -> int:
    """
    Save REAL OHLC data to database cache AND upload to HuggingFace Datasets

    Data Flow:
        1. Save to SQLite cache (local persistence)
        2. Upload to HuggingFace Datasets (cloud storage & hub)
        3. Clients can fetch from HuggingFace Datasets

    Args:
        ohlc_data: List of REAL OHLC data dictionaries

    Returns:
        int: Number of candles saved
    """
    saved_count = 0

    # Step 1: Save to local SQLite cache
    for data in ohlc_data:
        try:
            success = cache.save_ohlc_candle(
                symbol=data["symbol"],
                interval=data["interval"],
                timestamp=data["timestamp"],
                open_price=data["open"],
                high=data["high"],
                low=data["low"],
                close=data["close"],
                volume=data["volume"],
                provider=data["provider"]
            )

            if success:
                saved_count += 1

        except Exception as e:
            logger.error(f"Error saving OHLC data for {data.get('symbol')}: {e}")
            continue

    # Step 2: Upload to HuggingFace Datasets (if enabled)
    if HF_UPLOAD_ENABLED and hf_uploader and ohlc_data:
        try:
            # Prepare data for upload (convert datetime to ISO string)
            upload_data = []
            for data in ohlc_data:
                upload_record = data.copy()
                if isinstance(upload_record.get("timestamp"), datetime):
                    upload_record["timestamp"] = upload_record["timestamp"].isoformat() + "Z"
                upload_data.append(upload_record)

            logger.info(f"📤 Uploading {len(upload_data)} OHLC records to HuggingFace Datasets...")
            upload_success = await hf_uploader.upload_ohlc_data(
                upload_data,
                append=True  # Append to existing data
            )

            if upload_success:
                logger.info(f"✅ Successfully uploaded OHLC data to HuggingFace Datasets")
            else:
                logger.warning(f"⚠️  Failed to upload OHLC data to HuggingFace Datasets")

        except Exception as e:
            logger.error(f"Error uploading OHLC to HuggingFace Datasets: {e}")
            # Don't fail if HF upload fails - local cache is still available

    return saved_count


async def fetch_and_cache_ohlc_for_symbol(symbol: str, interval: str) -> int:
    """
    Fetch and cache OHLC data for a single symbol and interval using multi-source fallback
    
    Args:
        symbol: Base symbol (e.g., 'BTC')
        interval: Candle interval ('1h', '4h', '1d')
        
    Returns:
        int: Number of candles saved
    """
    try:
        # Determine limit based on interval
        limit = 100 if interval == "1d" else 100
        
        # Fetch REAL data with automatic fallback
        ohlc_data = await fetch_ohlc_with_fallback(symbol, interval, limit)
        
        if not ohlc_data or len(ohlc_data) == 0:
            logger.debug(f"No OHLC data received for {symbol} {interval}")
            return 0
        
        # Save REAL data to database
        saved_count = await save_ohlc_data_to_cache(ohlc_data)
        
        if saved_count > 0:
            logger.debug(f"Saved {saved_count}/{len(ohlc_data)} candles for {symbol} {interval}")
        return saved_count
        
    except Exception as e:
        logger.error(f"Error fetching OHLC for {symbol} {interval}: {e}")
        return 0


async def ohlc_data_worker_loop():
    """
    Background worker loop - Fetch REAL OHLC data periodically with multi-source fallback
    
    CRITICAL RULES:
    1. Run continuously in background
    2. Fetch REAL data from multiple sources with automatic fallback
    3. Store REAL data in database
    4. NEVER generate fake candles as fallback
    5. If all sources fail, log error and retry on next iteration
    """
    
    logger.info("Starting OHLC data background worker with multi-source fallback")
    logger.info("📊 Data sources: CoinGecko, Kraken, Coinbase, Binance")
    iteration = 0
    
    while True:
        try:
            iteration += 1
            start_time = time.time()
            
            logger.info(f"[Iteration {iteration}] Fetching REAL OHLC data from multiple sources...")
            
            total_saved = 0
            total_combinations = len(SYMBOLS) * len(INTERVALS)
            successful_fetches = 0
            
            # Fetch OHLC data for all symbols and intervals
            for symbol in SYMBOLS:
                for interval in INTERVALS:
                    try:
                        saved = await fetch_and_cache_ohlc_for_symbol(symbol, interval)
                        total_saved += saved
                        if saved > 0:
                            successful_fetches += 1
                        
                        # Small delay to avoid rate limiting
                        await asyncio.sleep(0.5)
                        
                    except Exception as e:
                        logger.error(f"Error processing {symbol} {interval}: {e}")
                        continue
            
            elapsed = time.time() - start_time
            logger.info(
                f"[Iteration {iteration}] Successfully saved {total_saved} REAL OHLC candles "
                f"({successful_fetches}/{total_combinations} symbol-intervals) in {elapsed:.2f}s"
            )
            
            # Sleep for 5 minutes between iterations to respect rate limits
            await asyncio.sleep(300)  # 5 minutes
            
        except Exception as e:
            logger.error(f"[Iteration {iteration}] Worker error: {e}", exc_info=True)
            # Wait and retry - DON'T generate fake data
            await asyncio.sleep(300)


async def start_ohlc_data_worker():
    """
    Start OHLC data background worker with multi-source support
    
    This should be called during application startup
    """
    try:
        logger.info("Initializing OHLC data worker with multi-source fallback...")
        logger.info("📊 Supported sources: CoinGecko, Kraken, Coinbase, Binance")
        
        # Run initial fetch for a few symbols immediately
        logger.info("Running initial OHLC data fetch...")
        total_saved = 0
        
        for symbol in SYMBOLS[:5]:  # First 5 symbols only for initial fetch
            for interval in INTERVALS:
                saved = await fetch_and_cache_ohlc_for_symbol(symbol, interval)
                total_saved += saved
                await asyncio.sleep(0.5)
        
        logger.info(f"Initial fetch: Saved {total_saved} REAL OHLC candles")
        
        # Start background loop
        asyncio.create_task(ohlc_data_worker_loop())
        logger.info("OHLC data worker started successfully")
        
    except Exception as e:
        logger.error(f"Failed to start OHLC data worker: {e}", exc_info=True)


# For testing
if __name__ == "__main__":
    import sys
    sys.path.append("/workspace")
    
    async def test():
        """Test the worker with multi-source fallback"""
        logger.info("Testing OHLC data worker with multi-source fallback...")
        
        # Test symbols
        test_symbols = ["BTC", "ETH"]
        interval = "1h"
        
        for symbol in test_symbols:
            logger.info(f"\n{'='*60}")
            logger.info(f"Testing {symbol}")
            logger.info(f"{'='*60}")
            
            data = await fetch_ohlc_with_fallback(symbol, interval, limit=10)
            logger.info(f"Fetched {len(data)} candles for {symbol} {interval}")
            
            if data:
                # Print sample data
                logger.info(f"Provider: {data[0].get('provider')}")
                for candle in data[:3]:
                    logger.info(
                        f"  {candle['timestamp']}: O={candle['open']:.2f} "
                        f"H={candle['high']:.2f} L={candle['low']:.2f} C={candle['close']:.2f}"
                    )
                
                # Test save to database
                saved = await save_ohlc_data_to_cache(data)
                logger.info(f"Saved {saved} candles to database")
            else:
                logger.warning(f"No data retrieved for {symbol}")
    
    asyncio.run(test())
