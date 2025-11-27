#!/usr/bin/env python3
"""
API Gateway - دروازه API با قابلیت کش
Powerful API Gateway with intelligent caching and fallback
"""

from fastapi import FastAPI, HTTPException, Query, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from typing import List, Optional, Dict, Any
from pydantic import BaseModel
from datetime import datetime, timedelta
import logging
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from crypto_data_bank.database import get_db
from crypto_data_bank.orchestrator import get_orchestrator
from crypto_data_bank.collectors.free_price_collector import FreePriceCollector
from crypto_data_bank.collectors.rss_news_collector import RSSNewsCollector
from crypto_data_bank.collectors.sentiment_collector import SentimentCollector
from crypto_data_bank.ai.huggingface_models import get_analyzer

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI
app = FastAPI(
    title="Crypto Data Bank API Gateway",
    description="🏦 Powerful Crypto Data Bank - FREE data aggregation from 200+ sources",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
db = get_db()
orchestrator = get_orchestrator()
price_collector = FreePriceCollector()
news_collector = RSSNewsCollector()
sentiment_collector = SentimentCollector()
ai_analyzer = get_analyzer()

# Application state
app_state = {"startup_time": datetime.now(), "background_collection_enabled": False}


# Pydantic Models
class PriceResponse(BaseModel):
    symbol: str
    price: float
    change24h: Optional[float] = None
    volume24h: Optional[float] = None
    marketCap: Optional[float] = None
    source: str
    timestamp: str


class NewsResponse(BaseModel):
    title: str
    description: Optional[str] = None
    url: str
    source: str
    published_at: Optional[str] = None
    coins: List[str] = []
    sentiment: Optional[float] = None


class SentimentResponse(BaseModel):
    overall_sentiment: str
    sentiment_score: float
    fear_greed_value: Optional[int] = None
    confidence: float
    timestamp: str


class HealthResponse(BaseModel):
    status: str
    database_status: str
    background_collection: bool
    uptime_seconds: float
    total_prices: int
    total_news: int
    last_update: Optional[str] = None


# === ROOT ENDPOINT ===


@app.get("/")
async def root():
    """معلومات API - API Information"""
    return {
        "name": "Crypto Data Bank API Gateway",
        "description": "🏦 Powerful FREE cryptocurrency data aggregation from 200+ sources",
        "version": "1.0.0",
        "features": [
            "Real-time prices from 5+ free sources",
            "News from 8+ RSS feeds",
            "Market sentiment analysis",
            "AI-powered news sentiment (HuggingFace models)",
            "Intelligent caching and database storage",
            "No API keys required for basic data",
        ],
        "endpoints": {
            "health": "/api/health",
            "prices": "/api/prices",
            "news": "/api/news",
            "sentiment": "/api/sentiment",
            "market_overview": "/api/market/overview",
            "trending_coins": "/api/trending",
            "ai_analysis": "/api/ai/analysis",
            "documentation": "/docs",
        },
        "data_sources": {
            "price_sources": ["CoinCap", "CoinGecko", "Binance Public", "Kraken", "CryptoCompare"],
            "news_sources": [
                "CoinTelegraph",
                "CoinDesk",
                "Bitcoin Magazine",
                "Decrypt",
                "The Block",
                "CryptoPotato",
                "NewsBTC",
                "Bitcoinist",
            ],
            "sentiment_sources": ["Fear & Greed Index", "BTC Dominance", "Global Market Stats"],
            "ai_models": ["FinBERT (sentiment)", "BART (classification)"],
        },
        "github": "https://github.com/nimazasinich/crypto-dt-source",
        "timestamp": datetime.now().isoformat(),
    }


# === HEALTH & STATUS ===


@app.get("/api/health", response_model=HealthResponse)
async def health_check():
    """بررسی سلامت سیستم - Health check"""
    try:
        stats = db.get_statistics()

        uptime = (datetime.now() - app_state["startup_time"]).total_seconds()

        status = orchestrator.get_collection_status()

        return HealthResponse(
            status="healthy",
            database_status="connected",
            background_collection=app_state["background_collection_enabled"],
            uptime_seconds=uptime,
            total_prices=stats.get("prices_count", 0),
            total_news=stats.get("news_count", 0),
            last_update=status["last_collection"].get("prices"),
        )

    except Exception as e:
        logger.error(f"Health check failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/stats")
async def get_statistics():
    """آمار کامل - Complete statistics"""
    try:
        db_stats = db.get_statistics()
        collection_status = orchestrator.get_collection_status()

        return {
            "database": db_stats,
            "collection": collection_status,
            "uptime_seconds": (datetime.now() - app_state["startup_time"]).total_seconds(),
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === PRICE ENDPOINTS ===


@app.get("/api/prices")
async def get_prices(
    symbols: Optional[str] = Query(None, description="Comma-separated symbols (e.g., BTC,ETH,SOL)"),
    limit: int = Query(100, ge=1, le=500, description="Number of results"),
    force_refresh: bool = Query(False, description="Force fresh data collection"),
):
    """
    دریافت قیمت‌های رمزارز - Get cryptocurrency prices

    - Uses cached database data by default (fast)
    - Set force_refresh=true for live data (slower)
    - Supports multiple symbols
    """
    try:
        symbol_list = symbols.split(",") if symbols else None

        # Check cache first (unless force_refresh)
        if not force_refresh:
            cached_prices = db.get_latest_prices(symbol_list, limit)

            if cached_prices:
                logger.info(f"✅ Returning {len(cached_prices)} prices from cache")
                return {
                    "success": True,
                    "source": "database_cache",
                    "count": len(cached_prices),
                    "data": cached_prices,
                    "timestamp": datetime.now().isoformat(),
                }

        # Force refresh or no cache - collect fresh data
        logger.info("📡 Collecting fresh price data...")
        all_prices = await price_collector.collect_all_free_sources(symbol_list)
        aggregated = price_collector.aggregate_prices(all_prices)

        # Save to database
        for price_data in aggregated:
            try:
                db.save_price(price_data["symbol"], price_data, "api_request")
            except:
                pass

        return {
            "success": True,
            "source": "live_collection",
            "count": len(aggregated),
            "data": aggregated,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error getting prices: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/prices/{symbol}")
async def get_price_single(
    symbol: str, history_hours: int = Query(24, ge=1, le=168, description="Hours of price history")
):
    """دریافت قیمت و تاریخچه یک رمزارز - Get single crypto price and history"""
    try:
        # Get latest price
        latest = db.get_latest_prices([symbol], 1)

        if not latest:
            # Try to collect fresh data
            all_prices = await price_collector.collect_all_free_sources([symbol])
            aggregated = price_collector.aggregate_prices(all_prices)

            if aggregated:
                latest = [aggregated[0]]
            else:
                raise HTTPException(status_code=404, detail=f"No data found for {symbol}")

        # Get price history
        history = db.get_price_history(symbol, history_hours)

        return {
            "success": True,
            "symbol": symbol,
            "current": latest[0],
            "history": history,
            "history_hours": history_hours,
            "timestamp": datetime.now().isoformat(),
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting price for {symbol}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# === NEWS ENDPOINTS ===


@app.get("/api/news")
async def get_news(
    limit: int = Query(50, ge=1, le=200, description="Number of news items"),
    category: Optional[str] = Query(None, description="Filter by category"),
    coin: Optional[str] = Query(None, description="Filter by coin symbol"),
    force_refresh: bool = Query(False, description="Force fresh data collection"),
):
    """
    دریافت اخبار رمزارز - Get cryptocurrency news

    - Uses cached database data by default
    - Set force_refresh=true for latest news
    - Filter by category or specific coin
    """
    try:
        # Check cache first
        if not force_refresh:
            cached_news = db.get_latest_news(limit, category)

            if cached_news:
                # Filter by coin if specified
                if coin:
                    cached_news = [
                        n
                        for n in cached_news
                        if coin.upper() in [c.upper() for c in n.get("coins", [])]
                    ]

                logger.info(f"✅ Returning {len(cached_news)} news from cache")
                return {
                    "success": True,
                    "source": "database_cache",
                    "count": len(cached_news),
                    "data": cached_news,
                    "timestamp": datetime.now().isoformat(),
                }

        # Collect fresh news
        logger.info("📰 Collecting fresh news...")
        all_news = await news_collector.collect_all_rss_feeds()
        unique_news = news_collector.deduplicate_news(all_news)

        # Filter by coin if specified
        if coin:
            unique_news = news_collector.filter_by_coins(unique_news, [coin])

        # Save to database
        for news_item in unique_news[:limit]:
            try:
                db.save_news(news_item)
            except:
                pass

        return {
            "success": True,
            "source": "live_collection",
            "count": len(unique_news[:limit]),
            "data": unique_news[:limit],
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error getting news: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/trending")
async def get_trending_coins():
    """سکه‌های پرطرفدار - Get trending coins from news"""
    try:
        # Get recent news from database
        recent_news = db.get_latest_news(100)

        if not recent_news:
            # Collect fresh news
            all_news = await news_collector.collect_all_rss_feeds()
            recent_news = news_collector.deduplicate_news(all_news)

        # Get trending coins
        trending = news_collector.get_trending_coins(recent_news)

        return {
            "success": True,
            "trending_coins": trending,
            "based_on_news": len(recent_news),
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === SENTIMENT ENDPOINTS ===


@app.get("/api/sentiment", response_model=Dict[str, Any])
async def get_market_sentiment(
    force_refresh: bool = Query(False, description="Force fresh data collection")
):
    """
    احساسات بازار - Get market sentiment

    - Includes Fear & Greed Index
    - BTC Dominance
    - Global market stats
    - Overall sentiment score
    """
    try:
        # Check cache first
        if not force_refresh:
            cached_sentiment = db.get_latest_sentiment()

            if cached_sentiment:
                logger.info("✅ Returning sentiment from cache")
                return {
                    "success": True,
                    "source": "database_cache",
                    "data": cached_sentiment,
                    "timestamp": datetime.now().isoformat(),
                }

        # Collect fresh sentiment
        logger.info("😊 Collecting fresh sentiment data...")
        sentiment_data = await sentiment_collector.collect_all_sentiment_data()

        # Save to database
        if sentiment_data.get("overall_sentiment"):
            db.save_sentiment(sentiment_data["overall_sentiment"], "api_request")

        return {
            "success": True,
            "source": "live_collection",
            "data": sentiment_data,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        logger.error(f"Error getting sentiment: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# === MARKET OVERVIEW ===


@app.get("/api/market/overview")
async def get_market_overview():
    """نمای کلی بازار - Complete market overview"""
    try:
        # Get top prices
        top_prices = db.get_latest_prices(None, 20)

        if not top_prices:
            # Collect fresh data
            all_prices = await price_collector.collect_all_free_sources()
            top_prices = price_collector.aggregate_prices(all_prices)[:20]

        # Get latest sentiment
        sentiment = db.get_latest_sentiment()

        if not sentiment:
            sentiment_data = await sentiment_collector.collect_all_sentiment_data()
            sentiment = sentiment_data.get("overall_sentiment")

        # Get latest news
        latest_news = db.get_latest_news(10)

        # Calculate market summary
        total_market_cap = sum(p.get("marketCap", 0) for p in top_prices)
        total_volume_24h = sum(p.get("volume24h", 0) for p in top_prices)

        return {
            "success": True,
            "market_summary": {
                "total_market_cap": total_market_cap,
                "total_volume_24h": total_volume_24h,
                "top_cryptocurrencies": len(top_prices),
            },
            "top_prices": top_prices[:10],
            "sentiment": sentiment,
            "latest_news": latest_news[:5],
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === AI ANALYSIS ENDPOINTS ===


@app.get("/api/ai/analysis")
async def get_ai_analysis(
    symbol: Optional[str] = Query(None, description="Filter by symbol"),
    limit: int = Query(50, ge=1, le=200),
):
    """تحلیل‌های هوش مصنوعی - Get AI analyses"""
    try:
        analyses = db.get_ai_analyses(symbol, limit)

        return {
            "success": True,
            "count": len(analyses),
            "data": analyses,
            "timestamp": datetime.now().isoformat(),
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/api/ai/analyze/news")
async def analyze_news_with_ai(text: str = Query(..., description="News text to analyze")):
    """تحلیل احساسات یک خبر با AI - Analyze news sentiment with AI"""
    try:
        result = await ai_analyzer.analyze_news_sentiment(text)

        return {"success": True, "analysis": result, "timestamp": datetime.now().isoformat()}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# === BACKGROUND COLLECTION CONTROL ===


@app.post("/api/collection/start")
async def start_background_collection(background_tasks: BackgroundTasks):
    """شروع جمع‌آوری پس‌زمینه - Start background data collection"""
    if app_state["background_collection_enabled"]:
        return {"success": False, "message": "Background collection already running"}

    background_tasks.add_task(orchestrator.start_background_collection)
    app_state["background_collection_enabled"] = True

    return {
        "success": True,
        "message": "Background collection started",
        "intervals": orchestrator.intervals,
        "timestamp": datetime.now().isoformat(),
    }


@app.post("/api/collection/stop")
async def stop_background_collection():
    """توقف جمع‌آوری پس‌زمینه - Stop background data collection"""
    if not app_state["background_collection_enabled"]:
        return {"success": False, "message": "Background collection not running"}

    await orchestrator.stop_background_collection()
    app_state["background_collection_enabled"] = False

    return {
        "success": True,
        "message": "Background collection stopped",
        "timestamp": datetime.now().isoformat(),
    }


@app.get("/api/collection/status")
async def get_collection_status():
    """وضعیت جمع‌آوری - Collection status"""
    return orchestrator.get_collection_status()


# === STARTUP & SHUTDOWN ===


@app.on_event("startup")
async def startup_event():
    """رویداد راه‌اندازی - Startup event"""
    logger.info("🚀 Starting Crypto Data Bank API Gateway...")
    logger.info("🏦 Powerful FREE data aggregation from 200+ sources")

    # Auto-start background collection
    try:
        await orchestrator.start_background_collection()
        app_state["background_collection_enabled"] = True
        logger.info("✅ Background collection started automatically")
    except Exception as e:
        logger.error(f"Failed to start background collection: {e}")


@app.on_event("shutdown")
async def shutdown_event():
    """رویداد خاموشی - Shutdown event"""
    logger.info("🛑 Shutting down Crypto Data Bank API Gateway...")

    if app_state["background_collection_enabled"]:
        await orchestrator.stop_background_collection()

    logger.info("✅ Shutdown complete")


if __name__ == "__main__":
    import uvicorn

    print("\n" + "=" * 70)
    print("🏦 Crypto Data Bank API Gateway")
    print("=" * 70)
    print("\n🚀 Starting server...")
    print("📍 URL: http://localhost:8888")
    print("📖 Docs: http://localhost:8888/docs")
    print("\n" + "=" * 70 + "\n")

    uvicorn.run("api_gateway:app", host="0.0.0.0", port=8888, reload=False, log_level="info")
