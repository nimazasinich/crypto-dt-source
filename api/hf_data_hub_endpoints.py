#!/usr/bin/env python3
"""
HuggingFace Data Hub API Endpoints
Serve data FROM HuggingFace Datasets to clients

This API ensures all data comes from HuggingFace Datasets:
    External APIs → Workers → HuggingFace Datasets → THIS API → Clients
"""

import logging
import os
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field

# Import authentication
from api.hf_auth import verify_hf_token

try:
    from datasets import load_dataset

    DATASETS_AVAILABLE = True
except ImportError:
    DATASETS_AVAILABLE = False

from utils.logger import setup_logger

logger = setup_logger("hf_data_hub_api")

# Create router
router = APIRouter(prefix="/api/hub", tags=["data-hub"])


# Response models
class MarketDataResponse(BaseModel):
    """Market data response model"""

    symbol: str
    price: float
    market_cap: Optional[float] = None
    volume_24h: Optional[float] = None
    change_24h: Optional[float] = None
    high_24h: Optional[float] = None
    low_24h: Optional[float] = None
    provider: str
    timestamp: str
    fetched_at: str


class OHLCDataResponse(BaseModel):
    """OHLC data response model"""

    symbol: str
    interval: str
    timestamp: str
    open: float
    high: float
    low: float
    close: float
    volume: float
    provider: str
    fetched_at: str


class DataHubStatus(BaseModel):
    """Data hub status response"""

    status: str
    message: str
    market_dataset: Dict[str, Any]
    ohlc_dataset: Dict[str, Any]
    timestamp: str


# Configuration
HF_TOKEN = os.getenv("HF_TOKEN") or os.getenv("HF_API_TOKEN")
HF_USERNAME = os.getenv("HF_USERNAME", "crypto-data-hub")
MARKET_DATASET = f"{HF_USERNAME}/crypto-market-data"
OHLC_DATASET = f"{HF_USERNAME}/crypto-ohlc-data"


def _load_market_dataset():
    """Load market data dataset from HuggingFace"""
    try:
        if not DATASETS_AVAILABLE:
            raise ImportError("datasets library not available")

        logger.info(f"Loading market dataset from HuggingFace: {MARKET_DATASET}")
        dataset = load_dataset(MARKET_DATASET, split="train", token=HF_TOKEN)
        return dataset

    except Exception as e:
        logger.error(f"Error loading market dataset: {e}")
        return None


def _load_ohlc_dataset():
    """Load OHLC dataset from HuggingFace"""
    try:
        if not DATASETS_AVAILABLE:
            raise ImportError("datasets library not available")

        logger.info(f"Loading OHLC dataset from HuggingFace: {OHLC_DATASET}")
        dataset = load_dataset(OHLC_DATASET, split="train", token=HF_TOKEN)
        return dataset

    except Exception as e:
        logger.error(f"Error loading OHLC dataset: {e}")
        return None


@router.get(
    "/status",
    response_model=DataHubStatus,
    summary="Data Hub Status",
    description="Get status of HuggingFace Data Hub and available datasets",
)
async def get_hub_status():
    """
    Get Data Hub status and dataset information

    Returns information about available HuggingFace Datasets:
    - Market data dataset (prices, volumes, market caps)
    - OHLC dataset (candlestick data)
    - Dataset sizes and last update times

    This endpoint does NOT require authentication.
    """
    try:
        market_info = {"available": False, "records": 0, "error": None}
        ohlc_info = {"available": False, "records": 0, "error": None}

        # Check market dataset
        try:
            market_dataset = _load_market_dataset()
            if market_dataset:
                market_info = {
                    "available": True,
                    "records": len(market_dataset),
                    "columns": market_dataset.column_names,
                    "url": f"https://huggingface.co/datasets/{MARKET_DATASET}",
                }
        except Exception as e:
            market_info["error"] = str(e)

        # Check OHLC dataset
        try:
            ohlc_dataset = _load_ohlc_dataset()
            if ohlc_dataset:
                ohlc_info = {
                    "available": True,
                    "records": len(ohlc_dataset),
                    "columns": ohlc_dataset.column_names,
                    "url": f"https://huggingface.co/datasets/{OHLC_DATASET}",
                }
        except Exception as e:
            ohlc_info["error"] = str(e)

        return DataHubStatus(
            status=(
                "healthy" if (market_info["available"] or ohlc_info["available"]) else "degraded"
            ),
            message=(
                "Data Hub operational"
                if (market_info["available"] or ohlc_info["available"])
                else "No datasets available"
            ),
            market_dataset=market_info,
            ohlc_dataset=ohlc_info,
            timestamp=datetime.utcnow().isoformat() + "Z",
        )

    except Exception as e:
        logger.error(f"Error getting hub status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error getting hub status: {str(e)}")


@router.get(
    "/market",
    response_model=List[MarketDataResponse],
    summary="Get Market Data from HuggingFace",
    description="Fetch real-time cryptocurrency market data FROM HuggingFace Datasets",
)
async def get_market_data_from_hub(
    symbols: Optional[str] = Query(
        None, description="Comma-separated list of symbols (e.g., 'BTC,ETH')"
    ),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of records to return"),
    _: dict = Depends(verify_hf_token),
):
    """
    Get market data FROM HuggingFace Dataset

    Data Flow:
        HuggingFace Dataset → THIS API → Client

    Authentication: Required (HF_TOKEN)

    Query Parameters:
        - symbols: Filter by specific symbols (comma-separated)
        - limit: Maximum records to return (1-1000)

    Returns:
        List of market data records with prices, volumes, market caps, etc.

    This endpoint ensures data is served FROM HuggingFace Datasets,
    NOT from local cache or external APIs.
    """
    try:
        # Load dataset from HuggingFace
        logger.info(f"Fetching market data FROM HuggingFace Dataset: {MARKET_DATASET}")
        dataset = _load_market_dataset()

        if not dataset:
            raise HTTPException(
                status_code=503, detail="Market dataset not available on HuggingFace"
            )

        # Convert to pandas for filtering
        df = dataset.to_pandas()

        if df.empty:
            raise HTTPException(
                status_code=404, detail="No market data available in HuggingFace Dataset"
            )

        # Filter by symbols if provided
        if symbols:
            symbol_list = [s.strip().upper() for s in symbols.split(",")]
            df = df[df["symbol"].isin(symbol_list)]

        # Sort by timestamp descending (most recent first)
        if "timestamp" in df.columns:
            df = df.sort_values("timestamp", ascending=False)
        elif "fetched_at" in df.columns:
            df = df.sort_values("fetched_at", ascending=False)

        # Apply limit
        df = df.head(limit)

        # Convert to response model
        results = df.to_dict("records")

        logger.info(f"✅ Serving {len(results)} market records FROM HuggingFace Dataset")

        return results

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching market data from HuggingFace: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Error fetching market data from HuggingFace: {str(e)}"
        )


@router.get(
    "/ohlc",
    response_model=List[OHLCDataResponse],
    summary="Get OHLC Data from HuggingFace",
    description="Fetch cryptocurrency candlestick data FROM HuggingFace Datasets",
)
async def get_ohlc_data_from_hub(
    symbol: str = Query(..., description="Trading pair symbol (e.g., 'BTCUSDT')"),
    interval: str = Query("1h", description="Candle interval (e.g., '1h', '4h', '1d')"),
    limit: int = Query(500, ge=1, le=5000, description="Maximum number of candles to return"),
    _: dict = Depends(verify_hf_token),
):
    """
    Get OHLC/candlestick data FROM HuggingFace Dataset

    Data Flow:
        HuggingFace Dataset → THIS API → Client

    Authentication: Required (HF_TOKEN)

    Query Parameters:
        - symbol: Trading pair (e.g., 'BTCUSDT')
        - interval: Candle interval ('1h', '4h', '1d')
        - limit: Maximum candles to return (1-5000)

    Returns:
        List of OHLC candles with open, high, low, close, volume data

    This endpoint ensures data is served FROM HuggingFace Datasets,
    NOT from local cache or external APIs.
    """
    try:
        # Load dataset from HuggingFace
        logger.info(f"Fetching OHLC data FROM HuggingFace Dataset: {OHLC_DATASET}")
        dataset = _load_ohlc_dataset()

        if not dataset:
            raise HTTPException(status_code=503, detail="OHLC dataset not available on HuggingFace")

        # Convert to pandas for filtering
        df = dataset.to_pandas()

        if df.empty:
            raise HTTPException(
                status_code=404, detail="No OHLC data available in HuggingFace Dataset"
            )

        # Filter by symbol and interval
        symbol_upper = symbol.upper()
        df = df[(df["symbol"] == symbol_upper) & (df["interval"] == interval)]

        if df.empty:
            raise HTTPException(
                status_code=404,
                detail=f"No OHLC data for {symbol_upper} {interval} in HuggingFace Dataset",
            )

        # Sort by timestamp descending (most recent first)
        if "timestamp" in df.columns:
            df = df.sort_values("timestamp", ascending=False)

        # Apply limit
        df = df.head(limit)

        # Convert to response model
        results = df.to_dict("records")

        logger.info(f"✅ Serving {len(results)} OHLC candles FROM HuggingFace Dataset")

        return results

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching OHLC data from HuggingFace: {e}", exc_info=True)
        raise HTTPException(
            status_code=500, detail=f"Error fetching OHLC data from HuggingFace: {str(e)}"
        )


@router.get(
    "/dataset-info",
    summary="Get Dataset Information",
    description="Get detailed information about HuggingFace Datasets",
)
async def get_dataset_info(
    dataset_type: str = Query("market", description="Dataset type: 'market' or 'ohlc'")
):
    """
    Get detailed information about a specific HuggingFace Dataset

    Query Parameters:
        - dataset_type: 'market' or 'ohlc'

    Returns:
        Detailed dataset information including:
        - Dataset name and URL
        - Number of records
        - Column names and types
        - Last update time
        - Dataset size

    This endpoint does NOT require authentication.
    """
    try:
        if dataset_type == "market":
            dataset_name = MARKET_DATASET
            dataset = _load_market_dataset()
        elif dataset_type == "ohlc":
            dataset_name = OHLC_DATASET
            dataset = _load_ohlc_dataset()
        else:
            raise HTTPException(
                status_code=400, detail="Invalid dataset_type. Must be 'market' or 'ohlc'"
            )

        if not dataset:
            raise HTTPException(status_code=404, detail=f"Dataset not found: {dataset_name}")

        # Get dataset info
        df = dataset.to_pandas()

        info = {
            "name": dataset_name,
            "url": f"https://huggingface.co/datasets/{dataset_name}",
            "records": len(dataset),
            "columns": dataset.column_names,
            "features": str(dataset.features),
            "size_mb": df.memory_usage(deep=True).sum() / 1024 / 1024,
            "sample_records": df.head(3).to_dict("records") if not df.empty else [],
        }

        # Add timestamp info if available
        if "timestamp" in df.columns:
            info["latest_timestamp"] = str(df["timestamp"].max())
            info["oldest_timestamp"] = str(df["timestamp"].min())
        elif "fetched_at" in df.columns:
            info["latest_timestamp"] = str(df["fetched_at"].max())
            info["oldest_timestamp"] = str(df["fetched_at"].min())

        return info

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting dataset info: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Error getting dataset info: {str(e)}")


# Health check for Data Hub
@router.get(
    "/health",
    summary="Data Hub Health Check",
    description="Check if Data Hub is operational and datasets are accessible",
)
async def data_hub_health():
    """
    Health check for Data Hub

    Returns:
        - Status of HuggingFace connection
        - Dataset availability
        - Number of records in each dataset
        - Last update times

    This endpoint does NOT require authentication.
    """
    try:
        health = {
            "status": "healthy",
            "timestamp": datetime.utcnow().isoformat() + "Z",
            "datasets": {},
        }

        # Check market dataset
        try:
            market_dataset = _load_market_dataset()
            if market_dataset:
                df = market_dataset.to_pandas()
                health["datasets"]["market"] = {
                    "available": True,
                    "records": len(market_dataset),
                    "latest_update": (
                        str(df["fetched_at"].max()) if "fetched_at" in df.columns else None
                    ),
                }
            else:
                health["datasets"]["market"] = {
                    "available": False,
                    "error": "Could not load dataset",
                }
                health["status"] = "degraded"
        except Exception as e:
            health["datasets"]["market"] = {"available": False, "error": str(e)}
            health["status"] = "degraded"

        # Check OHLC dataset
        try:
            ohlc_dataset = _load_ohlc_dataset()
            if ohlc_dataset:
                df = ohlc_dataset.to_pandas()
                health["datasets"]["ohlc"] = {
                    "available": True,
                    "records": len(ohlc_dataset),
                    "latest_update": (
                        str(df["fetched_at"].max()) if "fetched_at" in df.columns else None
                    ),
                }
            else:
                health["datasets"]["ohlc"] = {"available": False, "error": "Could not load dataset"}
                health["status"] = "degraded"
        except Exception as e:
            health["datasets"]["ohlc"] = {"available": False, "error": str(e)}
            health["status"] = "degraded"

        return health

    except Exception as e:
        logger.error(f"Error in health check: {e}", exc_info=True)
        return {
            "status": "unhealthy",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat() + "Z",
        }
