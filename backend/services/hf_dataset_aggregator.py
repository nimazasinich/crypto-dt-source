#!/usr/bin/env python3
"""
HuggingFace Dataset Aggregator - Uses ALL Free HF Datasets
Maximizes usage of all available free HuggingFace datasets for historical OHLCV data
"""

import httpx
import logging
import io
import csv
from typing import Dict, Any, List, Optional
from datetime import datetime
from fastapi import HTTPException

logger = logging.getLogger(__name__)


class HFDatasetAggregator:
    """
    Aggregates historical OHLCV data from ALL free HuggingFace datasets:
    - linxy/CryptoCoin (26 symbols x 7 timeframes = 182 CSVs)
    - WinkingFace/CryptoLM-Bitcoin-BTC-USDT
    - WinkingFace/CryptoLM-Ethereum-ETH-USDT
    - WinkingFace/CryptoLM-Solana-SOL-USDT
    - WinkingFace/CryptoLM-Ripple-XRP-USDT
    """
    
    def __init__(self):
        self.timeout = 30.0
        
        # linxy/CryptoCoin dataset configuration
        self.linxy_base_url = "https://huggingface.co/datasets/linxy/CryptoCoin/resolve/main"
        self.linxy_symbols = [
            "BTC", "ETH", "BNB", "XRP", "ADA", "DOGE", "SOL", "TRX", "DOT", "MATIC",
            "LTC", "SHIB", "AVAX", "UNI", "LINK", "ATOM", "XLM", "ETC", "XMR", "BCH",
            "NEAR", "APT", "ARB", "OP", "FTM", "ALGO"
        ]
        self.linxy_timeframes = ["1m", "5m", "15m", "30m", "1h", "4h", "1d"]
        
        # WinkingFace datasets configuration
        self.winkingface_datasets = {
            "BTC": "https://huggingface.co/datasets/WinkingFace/CryptoLM-Bitcoin-BTC-USDT/resolve/main",
            "ETH": "https://huggingface.co/datasets/WinkingFace/CryptoLM-Ethereum-ETH-USDT/resolve/main",
            "SOL": "https://huggingface.co/datasets/WinkingFace/CryptoLM-Solana-SOL-USDT/resolve/main",
            "XRP": "https://huggingface.co/datasets/WinkingFace/CryptoLM-Ripple-XRP-USDT/resolve/main"
        }
        
        # Cache for dataset data
        self._cache = {}
        self._cache_duration = 3600  # 1 hour
    
    async def get_ohlcv(
        self,
        symbol: str,
        timeframe: str = "1h",
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        Get OHLCV data from HuggingFace datasets with fallback
        """
        symbol = symbol.upper().replace("USDT", "").replace("USD", "")
        
        # Try linxy/CryptoCoin first
        if symbol in self.linxy_symbols and timeframe in self.linxy_timeframes:
            try:
                data = await self._get_linxy_ohlcv(symbol, timeframe, limit)
                if data:
                    logger.info(f"✅ linxy/CryptoCoin: Fetched {len(data)} candles for {symbol}/{timeframe}")
                    return data
            except Exception as e:
                logger.warning(f"⚠️ linxy/CryptoCoin failed for {symbol}/{timeframe}: {e}")
        
        # Try WinkingFace datasets
        if symbol in self.winkingface_datasets:
            try:
                data = await self._get_winkingface_ohlcv(symbol, timeframe, limit)
                if data:
                    logger.info(f"✅ WinkingFace: Fetched {len(data)} candles for {symbol}")
                    return data
            except Exception as e:
                logger.warning(f"⚠️ WinkingFace failed for {symbol}: {e}")
        
        raise HTTPException(
            status_code=404,
            detail=f"No HuggingFace dataset found for {symbol}/{timeframe}"
        )
    
    async def _get_linxy_ohlcv(
        self,
        symbol: str,
        timeframe: str,
        limit: int
    ) -> List[Dict[str, Any]]:
        """Get OHLCV data from linxy/CryptoCoin dataset"""
        cache_key = f"linxy_{symbol}_{timeframe}"
        
        # Check cache
        if cache_key in self._cache:
            cached_data, cached_time = self._cache[cache_key]
            if (datetime.utcnow().timestamp() - cached_time) < self._cache_duration:
                logger.info(f"✅ Returning cached data for {symbol}/{timeframe}")
                return cached_data[:limit]
        
        # Download CSV from HuggingFace
        csv_filename = f"{symbol}_{timeframe}.csv"
        csv_url = f"{self.linxy_base_url}/{csv_filename}"
        
        async with httpx.AsyncClient(timeout=self.timeout) as client:
            response = await client.get(csv_url)
            response.raise_for_status()
            
            # Parse CSV
            csv_content = response.text
            csv_reader = csv.DictReader(io.StringIO(csv_content))
            
            ohlcv_data = []
            for row in csv_reader:
                try:
                    # linxy/CryptoCoin CSV format:
                    # timestamp, open, high, low, close, volume
                    ohlcv_data.append({
                        "timestamp": int(row.get("timestamp", 0)),
                        "open": float(row.get("open", 0)),
                        "high": float(row.get("high", 0)),
                        "low": float(row.get("low", 0)),
                        "close": float(row.get("close", 0)),
                        "volume": float(row.get("volume", 0))
                    })
                except (ValueError, KeyError) as e:
                    logger.warning(f"⚠️ Failed to parse row: {e}")
                    continue
            
            # Sort by timestamp (newest first)
            ohlcv_data.sort(key=lambda x: x["timestamp"], reverse=True)
            
            # Cache the result
            self._cache[cache_key] = (ohlcv_data, datetime.utcnow().timestamp())
            
            return ohlcv_data[:limit]
    
    async def _get_winkingface_ohlcv(
        self,
        symbol: str,
        timeframe: str,
        limit: int
    ) -> List[Dict[str, Any]]:
        """Get OHLCV data from WinkingFace datasets"""
        cache_key = f"winkingface_{symbol}_{timeframe}"
        
        # Check cache
        if cache_key in self._cache:
            cached_data, cached_time = self._cache[cache_key]
            if (datetime.utcnow().timestamp() - cached_time) < self._cache_duration:
                logger.info(f"✅ Returning cached data for {symbol} (WinkingFace)")
                return cached_data[:limit]
        
        # WinkingFace datasets have different CSV filenames
        base_url = self.winkingface_datasets[symbol]
        
        # Try different possible filenames
        possible_files = [
            f"{symbol}USDT_{timeframe}.csv",
            f"data.csv",
            f"{symbol}USDT_1h.csv"  # Fallback to 1h if specific timeframe not found
        ]
        
        for csv_filename in possible_files:
            try:
                csv_url = f"{base_url}/{csv_filename}"
                
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.get(csv_url)
                    response.raise_for_status()
                    
                    # Parse CSV
                    csv_content = response.text
                    csv_reader = csv.DictReader(io.StringIO(csv_content))
                    
                    ohlcv_data = []
                    for row in csv_reader:
                        try:
                            # WinkingFace CSV format may vary
                            # Try to detect and parse correctly
                            timestamp_key = None
                            for key in ["timestamp", "time", "date", "unix"]:
                                if key in row:
                                    timestamp_key = key
                                    break
                            
                            if not timestamp_key:
                                continue
                            
                            ohlcv_data.append({
                                "timestamp": int(float(row.get(timestamp_key, 0))),
                                "open": float(row.get("open", 0)),
                                "high": float(row.get("high", 0)),
                                "low": float(row.get("low", 0)),
                                "close": float(row.get("close", 0)),
                                "volume": float(row.get("volume", 0))
                            })
                        except (ValueError, KeyError) as e:
                            logger.warning(f"⚠️ Failed to parse row: {e}")
                            continue
                    
                    if ohlcv_data:
                        # Sort by timestamp (newest first)
                        ohlcv_data.sort(key=lambda x: x["timestamp"], reverse=True)
                        
                        # Cache the result
                        self._cache[cache_key] = (ohlcv_data, datetime.utcnow().timestamp())
                        
                        return ohlcv_data[:limit]
                
            except Exception as e:
                logger.warning(f"⚠️ Failed to fetch {csv_filename}: {e}")
                continue
        
        raise Exception(f"No data found for {symbol} in WinkingFace datasets")
    
    async def get_available_symbols(self) -> Dict[str, List[str]]:
        """
        Get list of available symbols from all datasets
        """
        return {
            "linxy_cryptocoin": self.linxy_symbols,
            "winkingface": list(self.winkingface_datasets.keys())
        }
    
    async def get_available_timeframes(self, symbol: str) -> List[str]:
        """
        Get available timeframes for a specific symbol
        """
        symbol = symbol.upper().replace("USDT", "").replace("USD", "")
        
        timeframes = []
        
        # Check linxy/CryptoCoin
        if symbol in self.linxy_symbols:
            timeframes.extend(self.linxy_timeframes)
        
        # WinkingFace datasets typically have 1h data
        if symbol in self.winkingface_datasets:
            timeframes.append("1h")
        
        return list(set(timeframes))  # Remove duplicates


# Global instance
hf_dataset_aggregator = HFDatasetAggregator()

__all__ = ["HFDatasetAggregator", "hf_dataset_aggregator"]

