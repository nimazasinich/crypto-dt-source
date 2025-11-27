#!/usr/bin/env python3
"""
Direct API Router - Complete REST Endpoints
All external API integrations exposed through REST endpoints
NO PIPELINES - Direct model loading and inference
"""

import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Body, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel

from backend.services.binance_client import binance_client
from backend.services.coingecko_client import coingecko_client
from backend.services.crypto_news_client import crypto_news_client
from backend.services.dataset_loader import crypto_dataset_loader

# Import all clients and services
from backend.services.direct_model_loader import direct_model_loader
from backend.services.external_api_clients import (
    alternative_me_client,
    reddit_client,
    rss_feed_client,
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v1", tags=["Direct API - External Services"])


# ============================================================================
# Pydantic Models
# ============================================================================


class SentimentRequest(BaseModel):
    """Sentiment analysis request"""

    text: str
    model_key: Optional[str] = "cryptobert_elkulako"


class BatchSentimentRequest(BaseModel):
    """Batch sentiment analysis request"""

    texts: List[str]
    model_key: Optional[str] = "cryptobert_elkulako"


class DatasetQueryRequest(BaseModel):
    """Dataset query request"""

    dataset_key: str
    filters: Optional[Dict[str, Any]] = None
    limit: int = 100


# ============================================================================
# CoinGecko Endpoints
# ============================================================================


@router.get("/coingecko/price")
async def get_coingecko_prices(
    symbols: Optional[str] = Query(None, description="Comma-separated symbols (e.g., BTC,ETH)"),
    limit: int = Query(100, description="Maximum number of coins"),
):
    """
    Get real-time cryptocurrency prices from CoinGecko

    Examples:
    - `/api/v1/coingecko/price?symbols=BTC,ETH`
    - `/api/v1/coingecko/price?limit=50`
    """
    try:
        symbol_list = symbols.split(",") if symbols else None
        result = await coingecko_client.get_market_prices(symbols=symbol_list, limit=limit)

        return {
            "success": True,
            "data": result,
            "source": "coingecko",
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"❌ CoinGecko price endpoint failed: {e}")
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/coingecko/trending")
async def get_coingecko_trending(limit: int = Query(10, description="Number of trending coins")):
    """
    Get trending cryptocurrencies from CoinGecko
    """
    try:
        result = await coingecko_client.get_trending_coins(limit=limit)

        return {
            "success": True,
            "data": result,
            "source": "coingecko",
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"❌ CoinGecko trending endpoint failed: {e}")
        raise HTTPException(status_code=503, detail=str(e))


# ============================================================================
# Binance Endpoints
# ============================================================================


@router.get("/binance/klines")
async def get_binance_klines(
    symbol: str = Query(..., description="Symbol (e.g., BTC, BTCUSDT)"),
    timeframe: str = Query("1h", description="Timeframe (1m, 5m, 15m, 1h, 4h, 1d)"),
    limit: int = Query(1000, description="Number of candles (max 1000)"),
):
    """
    Get OHLCV candlestick data from Binance

    Examples:
    - `/api/v1/binance/klines?symbol=BTC&timeframe=1h&limit=100`
    - `/api/v1/binance/klines?symbol=ETHUSDT&timeframe=4h&limit=500`
    """
    try:
        result = await binance_client.get_ohlcv(symbol=symbol, timeframe=timeframe, limit=limit)

        return {
            "success": True,
            "data": result,
            "source": "binance",
            "symbol": symbol,
            "timeframe": timeframe,
            "count": len(result),
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"❌ Binance klines endpoint failed: {e}")
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/binance/ticker")
async def get_binance_ticker(symbol: str = Query(..., description="Symbol (e.g., BTC)")):
    """
    Get 24-hour ticker data from Binance
    """
    try:
        result = await binance_client.get_24h_ticker(symbol=symbol)

        return {
            "success": True,
            "data": result,
            "source": "binance",
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"❌ Binance ticker endpoint failed: {e}")
        raise HTTPException(status_code=503, detail=str(e))


# ============================================================================
# Alternative.me Endpoints
# ============================================================================


@router.get("/alternative/fng")
async def get_fear_greed_index(
    limit: int = Query(1, description="Number of historical data points")
):
    """
    Get Fear & Greed Index from Alternative.me

    Examples:
    - `/api/v1/alternative/fng` - Current index
    - `/api/v1/alternative/fng?limit=30` - Last 30 days
    """
    try:
        result = await alternative_me_client.get_fear_greed_index(limit=limit)

        return result

    except Exception as e:
        logger.error(f"❌ Alternative.me endpoint failed: {e}")
        raise HTTPException(status_code=503, detail=str(e))


# ============================================================================
# Reddit Endpoints
# ============================================================================


@router.get("/reddit/top")
async def get_reddit_top_posts(
    subreddit: str = Query("cryptocurrency", description="Subreddit name"),
    time_filter: str = Query("day", description="Time filter (hour, day, week, month)"),
    limit: int = Query(25, description="Number of posts"),
):
    """
    Get top posts from Reddit cryptocurrency subreddits

    Examples:
    - `/api/v1/reddit/top?subreddit=cryptocurrency&time_filter=day&limit=25`
    - `/api/v1/reddit/top?subreddit=bitcoin&time_filter=week&limit=50`
    """
    try:
        result = await reddit_client.get_top_posts(
            subreddit=subreddit, time_filter=time_filter, limit=limit
        )

        return result

    except Exception as e:
        logger.error(f"❌ Reddit endpoint failed: {e}")
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/reddit/new")
async def get_reddit_new_posts(
    subreddit: str = Query("cryptocurrency", description="Subreddit name"),
    limit: int = Query(25, description="Number of posts"),
):
    """
    Get new posts from Reddit cryptocurrency subreddits
    """
    try:
        result = await reddit_client.get_new_posts(subreddit=subreddit, limit=limit)

        return result

    except Exception as e:
        logger.error(f"❌ Reddit endpoint failed: {e}")
        raise HTTPException(status_code=503, detail=str(e))


# ============================================================================
# RSS Feed Endpoints
# ============================================================================


@router.get("/rss/feed")
async def get_rss_feed(
    feed_name: str = Query(
        ..., description="Feed name (coindesk, cointelegraph, bitcoinmagazine, decrypt, theblock)"
    ),
    limit: int = Query(20, description="Number of articles"),
):
    """
    Get news articles from RSS feeds

    Available feeds: coindesk, cointelegraph, bitcoinmagazine, decrypt, theblock

    Examples:
    - `/api/v1/rss/feed?feed_name=coindesk&limit=20`
    - `/api/v1/rss/feed?feed_name=cointelegraph&limit=10`
    """
    try:
        result = await rss_feed_client.fetch_feed(feed_name=feed_name, limit=limit)

        return result

    except Exception as e:
        logger.error(f"❌ RSS feed endpoint failed: {e}")
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/rss/all")
async def get_all_rss_feeds(limit_per_feed: int = Query(10, description="Articles per feed")):
    """
    Get news articles from all RSS feeds
    """
    try:
        result = await rss_feed_client.fetch_all_feeds(limit_per_feed=limit_per_feed)

        return result

    except Exception as e:
        logger.error(f"❌ RSS all feeds endpoint failed: {e}")
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/coindesk/rss")
async def get_coindesk_rss(limit: int = Query(20, description="Number of articles")):
    """
    Get CoinDesk RSS feed

    Direct endpoint: https://www.coindesk.com/arc/outboundfeeds/rss/
    """
    try:
        result = await rss_feed_client.fetch_feed("coindesk", limit)
        return result
    except Exception as e:
        logger.error(f"❌ CoinDesk RSS failed: {e}")
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/cointelegraph/rss")
async def get_cointelegraph_rss(limit: int = Query(20, description="Number of articles")):
    """
    Get CoinTelegraph RSS feed

    Direct endpoint: https://cointelegraph.com/rss
    """
    try:
        result = await rss_feed_client.fetch_feed("cointelegraph", limit)
        return result
    except Exception as e:
        logger.error(f"❌ CoinTelegraph RSS failed: {e}")
        raise HTTPException(status_code=503, detail=str(e))


# ============================================================================
# Crypto News Endpoints (Aggregated)
# ============================================================================


@router.get("/news/latest")
async def get_latest_crypto_news(limit: int = Query(20, description="Number of articles")):
    """
    Get latest cryptocurrency news from multiple sources
    (Aggregates NewsAPI, CryptoPanic, and RSS feeds)
    """
    try:
        result = await crypto_news_client.get_latest_news(limit=limit)

        return {
            "success": True,
            "data": result,
            "count": len(result),
            "source": "aggregated",
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"❌ Crypto news endpoint failed: {e}")
        raise HTTPException(status_code=503, detail=str(e))


# ============================================================================
# Hugging Face Model Endpoints (Direct Loading - NO PIPELINES)
# ============================================================================


@router.post("/hf/sentiment")
async def analyze_sentiment(request: SentimentRequest):
    """
    Analyze sentiment using HuggingFace models (NO PIPELINE)

    Available models:
    - cryptobert_elkulako (default): ElKulako/cryptobert
    - cryptobert_kk08: kk08/CryptoBERT
    - finbert: ProsusAI/finbert
    - twitter_sentiment: cardiffnlp/twitter-roberta-base-sentiment

    Example:
    ```json
    {
        "text": "Bitcoin price is surging to new heights!",
        "model_key": "cryptobert_elkulako"
    }
    ```
    """
    try:
        result = await direct_model_loader.predict_sentiment(
            text=request.text, model_key=request.model_key
        )

        return result

    except Exception as e:
        logger.error(f"❌ Sentiment analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/hf/sentiment/batch")
async def analyze_sentiment_batch(request: BatchSentimentRequest):
    """
    Batch sentiment analysis (NO PIPELINE)

    Example:
    ```json
    {
        "texts": [
            "Bitcoin is mooning!",
            "Ethereum looks bearish today",
            "Market is neutral"
        ],
        "model_key": "cryptobert_elkulako"
    }
    ```
    """
    try:
        result = await direct_model_loader.batch_predict_sentiment(
            texts=request.texts, model_key=request.model_key
        )

        return result

    except Exception as e:
        logger.error(f"❌ Batch sentiment analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/hf/models")
async def get_loaded_models():
    """
    Get list of loaded HuggingFace models
    """
    try:
        result = direct_model_loader.get_loaded_models()
        return result

    except Exception as e:
        logger.error(f"❌ Get models failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/hf/models/load")
async def load_model(model_key: str = Query(..., description="Model key to load")):
    """
    Load a specific HuggingFace model

    Available models:
    - cryptobert_elkulako
    - cryptobert_kk08
    - finbert
    - twitter_sentiment
    """
    try:
        result = await direct_model_loader.load_model(model_key)
        return result

    except Exception as e:
        logger.error(f"❌ Load model failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/hf/models/load-all")
async def load_all_models():
    """
    Load all configured HuggingFace models
    """
    try:
        result = await direct_model_loader.load_all_models()
        return result

    except Exception as e:
        logger.error(f"❌ Load all models failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Hugging Face Dataset Endpoints
# ============================================================================


@router.get("/hf/datasets")
async def get_loaded_datasets():
    """
    Get list of loaded HuggingFace datasets
    """
    try:
        result = crypto_dataset_loader.get_loaded_datasets()
        return result

    except Exception as e:
        logger.error(f"❌ Get datasets failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/hf/datasets/load")
async def load_dataset(
    dataset_key: str = Query(..., description="Dataset key to load"),
    split: Optional[str] = Query(None, description="Dataset split"),
    streaming: bool = Query(False, description="Enable streaming"),
):
    """
    Load a specific HuggingFace dataset

    Available datasets:
    - cryptocoin: linxy/CryptoCoin
    - bitcoin_btc_usdt: WinkingFace/CryptoLM-Bitcoin-BTC-USDT
    - ethereum_eth_usdt: WinkingFace/CryptoLM-Ethereum-ETH-USDT
    - solana_sol_usdt: WinkingFace/CryptoLM-Solana-SOL-USDT
    - ripple_xrp_usdt: WinkingFace/CryptoLM-Ripple-XRP-USDT
    """
    try:
        result = await crypto_dataset_loader.load_dataset(
            dataset_key=dataset_key, split=split, streaming=streaming
        )
        return result

    except Exception as e:
        logger.error(f"❌ Load dataset failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/hf/datasets/load-all")
async def load_all_datasets(streaming: bool = Query(False, description="Enable streaming")):
    """
    Load all configured HuggingFace datasets
    """
    try:
        result = await crypto_dataset_loader.load_all_datasets(streaming=streaming)
        return result

    except Exception as e:
        logger.error(f"❌ Load all datasets failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/hf/datasets/sample")
async def get_dataset_sample(
    dataset_key: str = Query(..., description="Dataset key"),
    num_samples: int = Query(10, description="Number of samples"),
    split: Optional[str] = Query(None, description="Dataset split"),
):
    """
    Get sample rows from a dataset
    """
    try:
        result = await crypto_dataset_loader.get_dataset_sample(
            dataset_key=dataset_key, num_samples=num_samples, split=split
        )
        return result

    except Exception as e:
        logger.error(f"❌ Get dataset sample failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/hf/datasets/query")
async def query_dataset(request: DatasetQueryRequest):
    """
    Query dataset with filters

    Example:
    ```json
    {
        "dataset_key": "bitcoin_btc_usdt",
        "filters": {"price": 50000},
        "limit": 100
    }
    ```
    """
    try:
        result = await crypto_dataset_loader.query_dataset(
            dataset_key=request.dataset_key, filters=request.filters, limit=request.limit
        )
        return result

    except Exception as e:
        logger.error(f"❌ Query dataset failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/hf/datasets/stats")
async def get_dataset_stats(dataset_key: str = Query(..., description="Dataset key")):
    """
    Get statistics about a dataset
    """
    try:
        result = await crypto_dataset_loader.get_dataset_stats(dataset_key=dataset_key)
        return result

    except Exception as e:
        logger.error(f"❌ Get dataset stats failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# System Status Endpoint
# ============================================================================


@router.get("/status")
async def get_system_status():
    """
    Get overall system status
    """
    try:
        models_info = direct_model_loader.get_loaded_models()
        datasets_info = crypto_dataset_loader.get_loaded_datasets()

        return {
            "success": True,
            "status": "operational",
            "models": {
                "total_configured": models_info["total_configured"],
                "total_loaded": models_info["total_loaded"],
                "device": models_info["device"],
            },
            "datasets": {
                "total_configured": datasets_info["total_configured"],
                "total_loaded": datasets_info["total_loaded"],
            },
            "external_apis": {
                "coingecko": "available",
                "binance": "available",
                "alternative_me": "available",
                "reddit": "available",
                "rss_feeds": "available",
            },
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"❌ System status failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# Export router
__all__ = ["router"]
