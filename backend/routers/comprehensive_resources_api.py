#!/usr/bin/env python3
"""
Comprehensive Resources API Router
Exposes ALL free resources through dedicated endpoints
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any, List
from datetime import datetime
import logging

# Import all aggregators
from backend.services.market_data_aggregator import market_data_aggregator
from backend.services.news_aggregator import news_aggregator
from backend.services.sentiment_aggregator import sentiment_aggregator
from backend.services.onchain_aggregator import onchain_aggregator
from backend.services.hf_dataset_aggregator import hf_dataset_aggregator

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Comprehensive Resources"])


# ============================================================================
# Market Data Endpoints - Uses ALL Free Market Data APIs
# ============================================================================

@router.get("/api/resources/market/price/{symbol}")
async def get_resource_price(symbol: str):
    """
    Get price from ALL free market data providers with automatic fallback.
    Providers: CoinGecko, CoinPaprika, CoinCap, Binance, CoinLore, Messari, CoinStats
    """
    try:
        price_data = await market_data_aggregator.get_price(symbol)
        return JSONResponse(content=price_data)
    except Exception as e:
        logger.error(f"Error fetching price from all providers: {e}")
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/api/resources/market/prices")
async def get_resource_prices(
    symbols: Optional[str] = Query(None, description="Comma-separated symbols (e.g., BTC,ETH,BNB)"),
    limit: int = Query(100, description="Number of top coins to fetch if symbols not provided")
):
    """
    Get prices for multiple symbols from ALL free market data providers.
    If symbols not provided, returns top coins by market cap.
    """
    try:
        symbols_list = symbols.split(",") if symbols else None
        prices = await market_data_aggregator.get_multiple_prices(symbols_list, limit)
        return JSONResponse(content={"success": True, "count": len(prices), "data": prices})
    except Exception as e:
        logger.error(f"Error fetching prices from all providers: {e}")
        raise HTTPException(status_code=503, detail=str(e))


# ============================================================================
# News Endpoints - Uses ALL Free News Sources
# ============================================================================

@router.get("/api/resources/news/latest")
async def get_resource_news(
    symbol: Optional[str] = Query(None, description="Filter by cryptocurrency symbol"),
    limit: int = Query(20, description="Number of articles to fetch")
):
    """
    Get news from ALL free news sources with automatic aggregation.
    Sources: CryptoPanic, CoinStats, CoinTelegraph RSS, CoinDesk RSS, Decrypt RSS, Bitcoin Magazine RSS, CryptoSlate
    """
    try:
        news = await news_aggregator.get_news(symbol=symbol, limit=limit)
        return JSONResponse(content={"success": True, "count": len(news), "news": news})
    except Exception as e:
        logger.error(f"Error fetching news from all sources: {e}")
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/api/resources/news/symbol/{symbol}")
async def get_resource_symbol_news(
    symbol: str,
    limit: int = Query(10, description="Number of articles to fetch")
):
    """
    Get news for a specific cryptocurrency symbol from all sources.
    """
    try:
        news = await news_aggregator.get_symbol_news(symbol=symbol, limit=limit)
        return JSONResponse(content={"success": True, "symbol": symbol.upper(), "count": len(news), "news": news})
    except Exception as e:
        logger.error(f"Error fetching symbol news: {e}")
        raise HTTPException(status_code=503, detail=str(e))


# ============================================================================
# Sentiment Endpoints - Uses ALL Free Sentiment Sources
# ============================================================================

@router.get("/api/resources/sentiment/fear-greed")
async def get_resource_fear_greed():
    """
    Get Fear & Greed Index from ALL free sentiment providers with fallback.
    Providers: Alternative.me, CFGI API v1, CFGI Legacy
    """
    try:
        fng_data = await sentiment_aggregator.get_fear_greed_index()
        return JSONResponse(content=fng_data)
    except Exception as e:
        logger.error(f"Error fetching Fear & Greed Index: {e}")
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/api/resources/sentiment/global")
async def get_resource_global_sentiment():
    """
    Get global market sentiment from multiple free sources.
    Includes: Fear & Greed Index, Reddit sentiment, overall market mood
    """
    try:
        sentiment = await sentiment_aggregator.get_global_sentiment()
        return JSONResponse(content=sentiment)
    except Exception as e:
        logger.error(f"Error fetching global sentiment: {e}")
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/api/resources/sentiment/coin/{symbol}")
async def get_resource_coin_sentiment(symbol: str):
    """
    Get sentiment for a specific cryptocurrency from all sources.
    Sources: CoinGecko community data, Messari social metrics
    """
    try:
        sentiment = await sentiment_aggregator.get_coin_sentiment(symbol)
        return JSONResponse(content=sentiment)
    except Exception as e:
        logger.error(f"Error fetching coin sentiment: {e}")
        raise HTTPException(status_code=503, detail=str(e))


# ============================================================================
# On-Chain Data Endpoints - Uses ALL Free Block Explorers & RPC Nodes
# ============================================================================

@router.get("/api/resources/onchain/balance")
async def get_resource_balance(
    address: str = Query(..., description="Blockchain address"),
    chain: str = Query("ethereum", description="Blockchain (ethereum, bsc, tron, polygon)")
):
    """
    Get address balance from ALL free block explorers with fallback.
    Ethereum: Etherscan (2 keys), Blockchair, Blockscout
    BSC: BscScan, Blockchair
    Tron: TronScan, Blockchair
    """
    try:
        balance = await onchain_aggregator.get_address_balance(address, chain)
        return JSONResponse(content=balance)
    except Exception as e:
        logger.error(f"Error fetching balance: {e}")
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/api/resources/onchain/gas")
async def get_resource_gas_price(
    chain: str = Query("ethereum", description="Blockchain (ethereum, bsc, polygon)")
):
    """
    Get current gas prices from explorers or RPC nodes.
    Uses: Etherscan/BscScan APIs, Free RPC nodes (Ankr, PublicNode, Cloudflare, etc.)
    """
    try:
        gas_data = await onchain_aggregator.get_gas_price(chain)
        return JSONResponse(content=gas_data)
    except Exception as e:
        logger.error(f"Error fetching gas price: {e}")
        raise HTTPException(status_code=503, detail=str(e))


@router.get("/api/resources/onchain/transactions")
async def get_resource_transactions(
    address: str = Query(..., description="Blockchain address"),
    chain: str = Query("ethereum", description="Blockchain (ethereum, bsc, tron)"),
    limit: int = Query(20, description="Number of transactions to fetch")
):
    """
    Get transaction history for an address from all available explorers.
    """
    try:
        transactions = await onchain_aggregator.get_transactions(address, chain, limit)
        return JSONResponse(content={"success": True, "count": len(transactions), "transactions": transactions})
    except Exception as e:
        logger.error(f"Error fetching transactions: {e}")
        raise HTTPException(status_code=503, detail=str(e))


# ============================================================================
# HuggingFace Dataset Endpoints - FREE Historical OHLCV Data
# ============================================================================

@router.get("/api/resources/hf/ohlcv")
async def get_resource_hf_ohlcv(
    symbol: str = Query(..., description="Cryptocurrency symbol"),
    timeframe: str = Query("1h", description="Timeframe"),
    limit: int = Query(1000, description="Number of candles to fetch")
):
    """
    Get historical OHLCV data from FREE HuggingFace datasets.
    Sources:
    - linxy/CryptoCoin (26 symbols, 7 timeframes)
    - WinkingFace/CryptoLM (BTC, ETH, SOL, XRP)
    """
    try:
        ohlcv = await hf_dataset_aggregator.get_ohlcv(symbol, timeframe, limit)
        return JSONResponse(content={"success": True, "count": len(ohlcv), "data": ohlcv})
    except Exception as e:
        logger.error(f"Error fetching HF dataset OHLCV: {e}")
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/api/resources/hf/symbols")
async def get_resource_hf_symbols():
    """
    Get list of available symbols from all HuggingFace datasets.
    """
    try:
        symbols = await hf_dataset_aggregator.get_available_symbols()
        return JSONResponse(content=symbols)
    except Exception as e:
        logger.error(f"Error fetching HF symbols: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/api/resources/hf/timeframes/{symbol}")
async def get_resource_hf_timeframes(symbol: str):
    """
    Get available timeframes for a specific symbol from HuggingFace datasets.
    """
    try:
        timeframes = await hf_dataset_aggregator.get_available_timeframes(symbol)
        return JSONResponse(content={"symbol": symbol.upper(), "timeframes": timeframes})
    except Exception as e:
        logger.error(f"Error fetching HF timeframes: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# Resource Status & Info
# ============================================================================

@router.get("/api/resources/status")
async def get_resources_status():
    """
    Get status of all free resources.
    """
    return JSONResponse(content={
        "success": True,
        "timestamp": int(datetime.utcnow().timestamp() * 1000),
        "resources": {
            "market_data": {
                "providers": [
                    "CoinGecko", "CoinPaprika", "CoinCap", "Binance",
                    "CoinLore", "Messari", "DefiLlama", "DIA Data", "CoinStats"
                ],
                "total": 9,
                "all_free": True
            },
            "news": {
                "providers": [
                    "CryptoPanic", "CoinStats", "CoinTelegraph RSS", "CoinDesk RSS",
                    "Decrypt RSS", "Bitcoin Magazine RSS", "CryptoSlate"
                ],
                "total": 7,
                "all_free": True
            },
            "sentiment": {
                "providers": [
                    "Alternative.me", "CFGI v1", "CFGI Legacy",
                    "CoinGecko Community", "Messari Social", "Reddit"
                ],
                "total": 6,
                "all_free": True
            },
            "onchain": {
                "explorers": {
                    "ethereum": ["Etherscan (2 keys)", "Blockchair", "Blockscout"],
                    "bsc": ["BscScan", "Blockchair"],
                    "tron": ["TronScan", "Blockchair"],
                    "polygon": ["RPC nodes"]
                },
                "rpc_nodes": {
                    "ethereum": 7,
                    "bsc": 5,
                    "polygon": 3,
                    "tron": 2
                },
                "total_explorers": 10,
                "total_rpc_nodes": 17,
                "mostly_free": True
            },
            "datasets": {
                "huggingface": {
                    "linxy_cryptocoin": {"symbols": 26, "timeframes": 7, "total_files": 182},
                    "winkingface": {"symbols": ["BTC", "ETH", "SOL", "XRP"]}
                },
                "all_free": True
            }
        },
        "total_free_resources": {
            "market_data_apis": 9,
            "news_sources": 7,
            "sentiment_apis": 6,
            "block_explorers": 10,
            "rpc_nodes": 17,
            "hf_datasets": 2,
            "total": 51
        },
        "message": "ALL resources are FREE with automatic fallback and intelligent load balancing"
    })


# Export router
__all__ = ["router"]

