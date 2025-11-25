"""
OHLC Data Background Worker - REAL DATA FROM FREE APIs ONLY

CRITICAL RULES:
- MUST fetch REAL candlestick data from Binance API (FREE, no API key)
- MUST store actual OHLC values, not fake data
- MUST use actual timestamps from API responses
- NEVER generate or interpolate candles
- If API fails, log error and retry (don't fake it)
"""

import asyncio
import time
import logging
import os
from datetime import datetime
from typing import List, Dict, Any
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

# Binance API (FREE - no API key required)
BINANCE_BASE_URL = "https://api.binance.com/api/v3"

# Trading pairs to track
TRADING_PAIRS = [
    "BTCUSDT", "ETHUSDT", "BNBUSDT", "XRPUSDT", "ADAUSDT",
    "SOLUSDT", "DOTUSDT", "DOGEUSDT", "MATICUSDT", "AVAXUSDT",
    "LINKUSDT", "LTCUSDT", "UNIUSDT", "ALGOUSDT", "XLMUSDT",
    "ATOMUSDT", "TRXUSDT", "XMRUSDT", "ETCUSDT", "XTZUSDT"
]

# Intervals to fetch (Binance format)
INTERVALS = ["1h", "4h", "1d"]


async def fetch_binance_klines(
    symbol: str,
    interval: str = "1h",
    limit: int = 500
) -> List[Dict[str, Any]]:
    """
    Fetch REAL candlestick data from Binance API (FREE)
    
    CRITICAL RULES:
    1. MUST call actual Binance API
    2. MUST return actual candlestick data from API
    3. NEVER generate fake candles
    4. If API fails, return empty list (not fake data)
    
    Args:
        symbol: Trading pair symbol (e.g., 'BTCUSDT')
        interval: Candle interval (e.g., '1h', '4h', '1d')
        limit: Number of candles to fetch (max 1000)
        
    Returns:
        List of dictionaries with REAL OHLC data
    """
    try:
        # Build API request - REAL API call
        url = f"{BINANCE_BASE_URL}/klines"
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": limit
        }
        
        logger.debug(f"Fetching REAL OHLC data from Binance: {symbol} {interval}")
        
        # Make REAL HTTP request to Binance
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(url, params=params)
            response.raise_for_status()
            
            # Parse REAL response data
            klines = response.json()
            
            if not klines or not isinstance(klines, list):
                logger.error(f"Invalid response from Binance for {symbol}: {klines}")
                return []
            
            logger.debug(f"Successfully fetched {len(klines)} candles for {symbol} {interval}")
            
            # Extract REAL candle data from API response
            ohlc_data = []
            for kline in klines:
                try:
                    # Binance kline format:
                    # [
                    #   0: Open time,
                    #   1: Open,
                    #   2: High,
                    #   3: Low,
                    #   4: Close,
                    #   5: Volume,
                    #   6: Close time,
                    #   ...
                    # ]
                    
                    # REAL data from API - NOT fake
                    data = {
                        "symbol": symbol,
                        "interval": interval,
                        "timestamp": datetime.fromtimestamp(kline[0] / 1000),  # REAL timestamp
                        "open": float(kline[1]),  # REAL open price
                        "high": float(kline[2]),  # REAL high price
                        "low": float(kline[3]),  # REAL low price
                        "close": float(kline[4]),  # REAL close price
                        "volume": float(kline[5]),  # REAL volume
                        "provider": "binance"
                    }
                    
                    ohlc_data.append(data)
                    
                except Exception as e:
                    logger.error(f"Error parsing kline data for {symbol}: {e}")
                    continue
            
            return ohlc_data
            
    except httpx.HTTPError as e:
        logger.error(f"HTTP error fetching from Binance ({symbol}): {e}")
        return []
    except Exception as e:
        logger.error(f"Error fetching from Binance ({symbol}): {e}", exc_info=True)
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


async def fetch_and_cache_ohlc_for_pair(symbol: str, interval: str) -> int:
    """
    Fetch and cache OHLC data for a single trading pair and interval
    
    Args:
        symbol: Trading pair symbol
        interval: Candle interval
        
    Returns:
        int: Number of candles saved
    """
    try:
        # Fetch REAL data from Binance
        ohlc_data = await fetch_binance_klines(symbol, interval, limit=500)
        
        if not ohlc_data or len(ohlc_data) == 0:
            logger.warning(f"No OHLC data received for {symbol} {interval}")
            return 0
        
        # Save REAL data to database
        saved_count = await save_ohlc_data_to_cache(ohlc_data)
        
        logger.debug(f"Saved {saved_count}/{len(ohlc_data)} candles for {symbol} {interval}")
        return saved_count
        
    except Exception as e:
        logger.error(f"Error fetching OHLC for {symbol} {interval}: {e}")
        return 0


async def ohlc_data_worker_loop():
    """
    Background worker loop - Fetch REAL OHLC data periodically
    
    CRITICAL RULES:
    1. Run continuously in background
    2. Fetch REAL data from Binance every 5 minutes
    3. Store REAL data in database
    4. NEVER generate fake candles as fallback
    5. If API fails, log error and retry on next iteration
    """
    
    logger.info("Starting OHLC data background worker")
    iteration = 0
    
    while True:
        try:
            iteration += 1
            start_time = time.time()
            
            logger.info(f"[Iteration {iteration}] Fetching REAL OHLC data from Binance...")
            
            total_saved = 0
            total_pairs = len(TRADING_PAIRS) * len(INTERVALS)
            
            # Fetch OHLC data for all pairs and intervals
            for symbol in TRADING_PAIRS:
                for interval in INTERVALS:
                    try:
                        saved = await fetch_and_cache_ohlc_for_pair(symbol, interval)
                        total_saved += saved
                        
                        # Small delay to avoid rate limiting
                        await asyncio.sleep(0.2)
                        
                    except Exception as e:
                        logger.error(f"Error processing {symbol} {interval}: {e}")
                        continue
            
            elapsed = time.time() - start_time
            logger.info(
                f"[Iteration {iteration}] Successfully saved {total_saved} "
                f"REAL OHLC candles from Binance ({total_pairs} pair-intervals) in {elapsed:.2f}s"
            )
            
            # Binance free tier: 1200 requests/minute weight limit
            # Sleep for 5 minutes between iterations
            await asyncio.sleep(300)  # 5 minutes
            
        except Exception as e:
            logger.error(f"[Iteration {iteration}] Worker error: {e}", exc_info=True)
            # Wait and retry - DON'T generate fake data
            await asyncio.sleep(300)


async def start_ohlc_data_worker():
    """
    Start OHLC data background worker
    
    This should be called during application startup
    """
    try:
        logger.info("Initializing OHLC data worker...")
        
        # Run initial fetch for a few pairs immediately
        logger.info("Running initial OHLC data fetch...")
        total_saved = 0
        
        for symbol in TRADING_PAIRS[:5]:  # First 5 pairs only for initial fetch
            for interval in INTERVALS:
                saved = await fetch_and_cache_ohlc_for_pair(symbol, interval)
                total_saved += saved
                await asyncio.sleep(0.2)
        
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
        """Test the worker"""
        logger.info("Testing OHLC data worker...")
        
        # Test API fetch
        symbol = "BTCUSDT"
        interval = "1h"
        
        data = await fetch_binance_klines(symbol, interval, limit=10)
        logger.info(f"Fetched {len(data)} candles for {symbol} {interval}")
        
        if data:
            # Print sample data
            for candle in data[:5]:
                logger.info(
                    f"  {candle['timestamp']}: O={candle['open']:.2f} "
                    f"H={candle['high']:.2f} L={candle['low']:.2f} C={candle['close']:.2f}"
                )
            
            # Test save to database
            saved = await save_ohlc_data_to_cache(data)
            logger.info(f"Saved {saved} candles to database")
    
    asyncio.run(test())
