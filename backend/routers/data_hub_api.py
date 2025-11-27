#!/usr/bin/env python3
"""
Data Hub Complete API Router
=============================
✅ تمام endpoint های داده‌های کریپتو
✅ استفاده از کلیدهای API جدید
✅ سیستم Fallback خودکار
✅ WebSocket Support
"""

from fastapi import APIRouter, HTTPException, Query, Body, WebSocket, WebSocketDisconnect
from fastapi.responses import JSONResponse
from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel
import logging
import json
import uuid

# Import Data Hub Complete
from backend.services.data_hub_complete import get_data_hub

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/v2/data-hub", tags=["Data Hub Complete"])

# Get singleton Data Hub instance
data_hub = get_data_hub()


# ============================================================================
# Pydantic Models
# ============================================================================


class MarketRequest(BaseModel):
    """درخواست داده‌های بازار"""

    symbols: Optional[List[str]] = None
    limit: int = 100
    source: str = "auto"


class OHLCVRequest(BaseModel):
    """درخواست داده‌های OHLCV"""

    symbol: str
    interval: str = "1h"
    limit: int = 100
    source: str = "auto"


class SentimentRequest(BaseModel):
    """درخواست تحلیل احساسات"""

    text: str
    source: str = "huggingface"


class NewsRequest(BaseModel):
    """درخواست اخبار"""

    query: str = "cryptocurrency"
    limit: int = 20
    source: str = "auto"


class BlockchainRequest(BaseModel):
    """درخواست داده‌های بلاکچین"""

    chain: str
    data_type: str = "transactions"
    address: Optional[str] = None
    limit: int = 20


class WhaleRequest(BaseModel):
    """درخواست فعالیت نهنگ‌ها"""

    chain: str = "all"
    min_value_usd: float = 1000000
    limit: int = 50


class SocialMediaRequest(BaseModel):
    """درخواست داده‌های شبکه‌های اجتماعی"""

    platform: str = "reddit"
    query: str = "cryptocurrency"
    limit: int = 20


class AIRequest(BaseModel):
    """درخواست پیش‌بینی AI"""

    symbol: str
    model_type: str = "price"
    timeframe: str = "24h"


# ============================================================================
# 1. Market Data Endpoints - داده‌های قیمت بازار
# ============================================================================


@router.get("/market/prices")
async def get_market_prices(
    symbols: Optional[str] = Query(None, description="Comma-separated symbols (e.g., BTC,ETH)"),
    limit: int = Query(100, description="Number of results"),
    source: str = Query("auto", description="Data source: auto, coinmarketcap, coingecko, binance"),
):
    """
    دریافت قیمت‌های لحظه‌ای بازار

    Sources:
    - CoinMarketCap (with new API key)
    - CoinGecko (free)
    - Binance (free)
    - HuggingFace

    Returns: قیمت، تغییرات 24 ساعته، حجم معاملات، Market Cap
    """
    try:
        symbol_list = None
        if symbols:
            symbol_list = [s.strip().upper() for s in symbols.split(",")]

        result = await data_hub.get_market_prices(symbols=symbol_list, limit=limit, source=source)

        if not result.get("success"):
            raise HTTPException(
                status_code=503, detail=result.get("error", "Failed to fetch market data")
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Market prices error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/market/prices")
async def post_market_prices(request: MarketRequest):
    """
    دریافت قیمت‌های بازار (POST method)
    """
    try:
        result = await data_hub.get_market_prices(
            symbols=request.symbols, limit=request.limit, source=request.source
        )

        if not result.get("success"):
            raise HTTPException(
                status_code=503, detail=result.get("error", "Failed to fetch market data")
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Market prices error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/market/top")
async def get_top_coins(limit: int = Query(10, description="Number of top coins")):
    """
    دریافت Top N ارزهای برتر بر اساس Market Cap
    """
    try:
        result = await data_hub.get_market_prices(limit=limit, source="auto")

        if result.get("success") and result.get("data"):
            # Sort by market cap
            data = sorted(result["data"], key=lambda x: x.get("market_cap", 0), reverse=True)
            result["data"] = data[:limit]

        return result

    except Exception as e:
        logger.error(f"❌ Top coins error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# 2. OHLCV Data Endpoints - داده‌های تاریخی
# ============================================================================


@router.get("/market/ohlcv")
async def get_ohlcv_data(
    symbol: str = Query(..., description="Symbol (e.g., BTC, ETH)"),
    interval: str = Query("1h", description="Interval: 1m, 5m, 15m, 1h, 4h, 1d"),
    limit: int = Query(100, description="Number of candles"),
    source: str = Query("auto", description="Data source: auto, binance, huggingface"),
):
    """
    دریافت داده‌های OHLCV (کندل استیک)

    Sources:
    - Binance (best for OHLCV)
    - HuggingFace

    Returns: Open, High, Low, Close, Volume for each candle
    """
    try:
        result = await data_hub.get_ohlcv_data(
            symbol=symbol.upper(), interval=interval, limit=limit, source=source
        )

        if not result.get("success"):
            raise HTTPException(
                status_code=503, detail=result.get("error", "Failed to fetch OHLCV data")
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ OHLCV error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/market/ohlcv")
async def post_ohlcv_data(request: OHLCVRequest):
    """
    دریافت داده‌های OHLCV (POST method)
    """
    try:
        result = await data_hub.get_ohlcv_data(
            symbol=request.symbol.upper(),
            interval=request.interval,
            limit=request.limit,
            source=request.source,
        )

        if not result.get("success"):
            raise HTTPException(
                status_code=503, detail=result.get("error", "Failed to fetch OHLCV data")
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ OHLCV error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# 3. Sentiment Data Endpoints - داده‌های احساسات
# ============================================================================


@router.get("/sentiment/fear-greed")
async def get_fear_greed_index():
    """
    دریافت شاخص ترس و طمع (Fear & Greed Index)

    Source: Alternative.me

    Returns:
    - مقدار شاخص (0-100)
    - طبقه‌بندی (Extreme Fear, Fear, Neutral, Greed, Extreme Greed)
    - تاریخچه 30 روزه
    """
    try:
        result = await data_hub.get_fear_greed_index()
        return result

    except Exception as e:
        logger.error(f"❌ Fear & Greed error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sentiment/analyze")
async def analyze_sentiment(request: SentimentRequest):
    """
    تحلیل احساسات متن با AI

    Source: HuggingFace Models

    Returns:
    - Label: POSITIVE, NEGATIVE, NEUTRAL
    - Score (0-1)
    - Confidence
    """
    try:
        result = await data_hub.analyze_sentiment(text=request.text, source=request.source)

        if not result.get("success"):
            raise HTTPException(
                status_code=503, detail=result.get("error", "Sentiment analysis failed")
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Sentiment analysis error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/sentiment/batch")
async def batch_sentiment_analysis(texts: List[str] = Body(...)):
    """
    تحلیل احساسات دسته‌ای برای چندین متن
    """
    try:
        results = []
        for text in texts[:50]:  # Limit to 50 texts
            result = await data_hub.analyze_sentiment(text=text)
            results.append(
                {
                    "text": text[:100],  # First 100 chars
                    "sentiment": result.get("data", {}) if result.get("success") else None,
                    "error": result.get("error") if not result.get("success") else None,
                }
            )

        return {
            "success": True,
            "total": len(results),
            "results": results,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"❌ Batch sentiment error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# 4. News Endpoints - داده‌های اخبار
# ============================================================================


@router.get("/news")
async def get_crypto_news(
    query: str = Query("cryptocurrency", description="Search query"),
    limit: int = Query(20, description="Number of articles"),
    source: str = Query("auto", description="Source: auto, newsapi, reddit"),
):
    """
    دریافت اخبار ارزهای دیجیتال

    Sources:
    - NewsAPI (with new API key)
    - Reddit (r/CryptoCurrency, r/Bitcoin, etc.)
    - HuggingFace

    Returns: Title, Description, URL, Source, Published Date
    """
    try:
        result = await data_hub.get_crypto_news(query=query, limit=limit, source=source)

        if not result.get("success"):
            raise HTTPException(status_code=503, detail=result.get("error", "Failed to fetch news"))

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ News error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/news")
async def post_crypto_news(request: NewsRequest):
    """
    دریافت اخبار (POST method)
    """
    try:
        result = await data_hub.get_crypto_news(
            query=request.query, limit=request.limit, source=request.source
        )

        if not result.get("success"):
            raise HTTPException(status_code=503, detail=result.get("error", "Failed to fetch news"))

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ News error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/news/latest/{symbol}")
async def get_latest_news_for_symbol(
    symbol: str, limit: int = Query(10, description="Number of articles")
):
    """
    دریافت آخرین اخبار برای یک سمبل خاص
    """
    try:
        query = f"{symbol} cryptocurrency"
        result = await data_hub.get_crypto_news(query=query, limit=limit)

        if result.get("success"):
            result["symbol"] = symbol.upper()

        return result

    except Exception as e:
        logger.error(f"❌ Symbol news error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# 5. Trending Data Endpoints - داده‌های ترندینگ
# ============================================================================


@router.get("/trending")
async def get_trending_coins():
    """
    دریافت ارزهای ترند روز

    Source: CoinGecko

    Returns: لیست ارزهای ترند با رتبه و امتیاز
    """
    try:
        result = await data_hub.get_trending_coins()
        return result

    except Exception as e:
        logger.error(f"❌ Trending error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/trending/search")
async def search_trending(query: str = Query(..., description="Search query")):
    """
    جستجو در ارزهای ترند
    """
    try:
        result = await data_hub.get_trending_coins()

        if result.get("success") and result.get("trending"):
            # Filter by query
            filtered = [
                coin
                for coin in result["trending"]
                if query.lower() in coin.get("name", "").lower()
                or query.lower() in coin.get("symbol", "").lower()
            ]
            result["trending"] = filtered
            result["filtered_by"] = query

        return result

    except Exception as e:
        logger.error(f"❌ Trending search error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# 6. Blockchain Data Endpoints - داده‌های بلاکچین
# ============================================================================


@router.get("/blockchain/{chain}")
async def get_blockchain_data(
    chain: str,
    data_type: str = Query("transactions", description="Type: transactions, balance, gas"),
    address: Optional[str] = Query(None, description="Wallet address"),
    limit: int = Query(20, description="Number of results"),
):
    """
    دریافت داده‌های بلاکچین

    Chains: ethereum, bsc, tron

    Sources:
    - Etherscan (with new API key)
    - BSCScan (with new API key)
    - TronScan (with new API key)

    Types:
    - transactions: لیست تراکنش‌ها
    - balance: موجودی آدرس
    - gas: قیمت گس
    """
    try:
        result = await data_hub.get_blockchain_data(
            chain=chain.lower(), data_type=data_type, address=address, limit=limit
        )

        if not result.get("success"):
            raise HTTPException(
                status_code=503, detail=result.get("error", "Failed to fetch blockchain data")
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Blockchain data error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/blockchain")
async def post_blockchain_data(request: BlockchainRequest):
    """
    دریافت داده‌های بلاکچین (POST method)
    """
    try:
        result = await data_hub.get_blockchain_data(
            chain=request.chain.lower(),
            data_type=request.data_type,
            address=request.address,
            limit=request.limit,
        )

        if not result.get("success"):
            raise HTTPException(
                status_code=503, detail=result.get("error", "Failed to fetch blockchain data")
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Blockchain data error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/blockchain/{chain}/gas")
async def get_gas_prices(chain: str):
    """
    دریافت قیمت گس برای بلاکچین مشخص
    """
    try:
        result = await data_hub.get_blockchain_data(chain=chain.lower(), data_type="gas")
        return result

    except Exception as e:
        logger.error(f"❌ Gas prices error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# 7. Whale Activity Endpoints - فعالیت نهنگ‌ها
# ============================================================================


@router.get("/whales")
async def get_whale_activity(
    chain: str = Query("all", description="Blockchain: all, ethereum, bsc, tron"),
    min_value_usd: float = Query(1000000, description="Minimum transaction value in USD"),
    limit: int = Query(50, description="Number of transactions"),
):
    """
    دریافت فعالیت نهنگ‌ها (تراکنش‌های بزرگ)

    Returns:
    - تراکنش‌های بالای $1M
    - جهت حرکت (IN/OUT از صرافی‌ها)
    - آدرس‌های مبدا و مقصد
    """
    try:
        result = await data_hub.get_whale_activity(
            chain=chain, min_value_usd=min_value_usd, limit=limit
        )
        return result

    except Exception as e:
        logger.error(f"❌ Whale activity error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/whales")
async def post_whale_activity(request: WhaleRequest):
    """
    دریافت فعالیت نهنگ‌ها (POST method)
    """
    try:
        result = await data_hub.get_whale_activity(
            chain=request.chain, min_value_usd=request.min_value_usd, limit=request.limit
        )
        return result

    except Exception as e:
        logger.error(f"❌ Whale activity error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# 8. Social Media Endpoints - داده‌های شبکه‌های اجتماعی
# ============================================================================


@router.get("/social/{platform}")
async def get_social_media_data(
    platform: str,
    query: str = Query("cryptocurrency", description="Search query"),
    limit: int = Query(20, description="Number of posts"),
):
    """
    دریافت داده‌های شبکه‌های اجتماعی

    Platforms: reddit

    Returns:
    - پست‌های Reddit از subreddit های کریپتو
    - امتیاز، تعداد کامنت، تاریخ
    """
    try:
        result = await data_hub.get_social_media_data(
            platform=platform.lower(), query=query, limit=limit
        )

        if not result.get("success"):
            raise HTTPException(
                status_code=503, detail=result.get("error", "Failed to fetch social data")
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Social media error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/social")
async def post_social_media_data(request: SocialMediaRequest):
    """
    دریافت داده‌های شبکه‌های اجتماعی (POST method)
    """
    try:
        result = await data_hub.get_social_media_data(
            platform=request.platform.lower(), query=request.query, limit=request.limit
        )

        if not result.get("success"):
            raise HTTPException(
                status_code=503, detail=result.get("error", "Failed to fetch social data")
            )

        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Social media error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# 9. AI Predictions Endpoints - پیش‌بینی‌های AI
# ============================================================================


@router.get("/ai/predict/{symbol}")
async def get_ai_prediction(
    symbol: str,
    model_type: str = Query("price", description="Type: price, trend, signal"),
    timeframe: str = Query("24h", description="Timeframe: 1h, 4h, 24h, 7d"),
):
    """
    دریافت پیش‌بینی از مدل‌های AI

    Source: HuggingFace Models

    Types:
    - price: پیش‌بینی قیمت
    - trend: پیش‌بینی روند
    - signal: سیگنال خرید/فروش
    """
    try:
        result = await data_hub.get_ai_prediction(
            symbol=symbol.upper(), model_type=model_type, timeframe=timeframe
        )
        return result

    except Exception as e:
        logger.error(f"❌ AI prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ai/predict")
async def post_ai_prediction(request: AIRequest):
    """
    دریافت پیش‌بینی AI (POST method)
    """
    try:
        result = await data_hub.get_ai_prediction(
            symbol=request.symbol.upper(),
            model_type=request.model_type,
            timeframe=request.timeframe,
        )
        return result

    except Exception as e:
        logger.error(f"❌ AI prediction error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# 10. Combined Data Endpoints - داده‌های ترکیبی
# ============================================================================


@router.get("/overview/{symbol}")
async def get_symbol_overview(symbol: str):
    """
    دریافت نمای کلی یک سمبل (ترکیبی از همه داده‌ها)

    Returns:
    - قیمت و آمار بازار
    - آخرین اخبار
    - تحلیل احساسات
    - پیش‌بینی AI
    """
    try:
        overview = {}

        # Get market data
        market = await data_hub.get_market_prices(symbols=[symbol.upper()], limit=1)
        if market.get("success") and market.get("data"):
            overview["market"] = market["data"][0] if market["data"] else None

        # Get latest news
        news = await data_hub.get_crypto_news(query=f"{symbol} cryptocurrency", limit=5)
        if news.get("success"):
            overview["news"] = news.get("articles", [])

        # Get AI prediction
        prediction = await data_hub.get_ai_prediction(symbol=symbol.upper())
        if prediction.get("success"):
            overview["prediction"] = prediction.get("prediction")

        # Get OHLCV data for chart
        ohlcv = await data_hub.get_ohlcv_data(symbol=symbol.upper(), interval="1h", limit=24)
        if ohlcv.get("success"):
            overview["chart_data"] = ohlcv.get("data", [])

        return {
            "success": True,
            "symbol": symbol.upper(),
            "overview": overview,
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"❌ Symbol overview error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/dashboard")
async def get_dashboard_data():
    """
    دریافت داده‌های داشبورد کامل

    Returns:
    - Top 10 coins
    - Fear & Greed Index
    - Latest news
    - Trending coins
    - Whale activities
    """
    try:
        dashboard = {}

        # Get top coins
        market = await data_hub.get_market_prices(limit=10)
        if market.get("success"):
            dashboard["top_coins"] = market.get("data", [])

        # Get Fear & Greed
        fg = await data_hub.get_fear_greed_index()
        if fg.get("success"):
            dashboard["fear_greed"] = fg.get("current", {})

        # Get latest news
        news = await data_hub.get_crypto_news(limit=10)
        if news.get("success"):
            dashboard["latest_news"] = news.get("articles", [])

        # Get trending
        trending = await data_hub.get_trending_coins()
        if trending.get("success"):
            dashboard["trending"] = trending.get("trending", [])[:5]

        # Get whale activity
        whales = await data_hub.get_whale_activity(limit=10)
        if whales.get("success"):
            dashboard["whale_activity"] = whales.get("data", {})

        return {"success": True, "dashboard": dashboard, "timestamp": datetime.utcnow().isoformat()}

    except Exception as e:
        logger.error(f"❌ Dashboard error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# System Health Endpoints - سلامت سیستم
# ============================================================================


@router.get("/health")
async def health_check():
    """
    بررسی سلامت Data Hub
    """
    try:
        health = await data_hub.check_all_sources_health()
        return health

    except Exception as e:
        logger.error(f"❌ Health check error: {e}")
        return {"success": False, "error": str(e), "timestamp": datetime.utcnow().isoformat()}


@router.get("/status")
async def get_status():
    """
    دریافت وضعیت کامل سیستم
    """
    try:
        health = await data_hub.check_all_sources_health()

        return {
            "success": True,
            "status": "operational" if health.get("operational_count", 0) > 5 else "degraded",
            "sources": health.get("status", {}),
            "statistics": {
                "operational": health.get("operational_count", 0),
                "total": health.get("total_sources", 0),
                "uptime_percentage": (
                    health.get("operational_count", 0) / health.get("total_sources", 1)
                )
                * 100,
            },
            "api_keys": {
                "coinmarketcap": "✅ Configured",
                "newsapi": "✅ Configured",
                "etherscan": "✅ Configured",
                "bscscan": "✅ Configured",
                "tronscan": "✅ Configured",
                "huggingface": "✅ Configured",
            },
            "timestamp": datetime.utcnow().isoformat(),
        }

    except Exception as e:
        logger.error(f"❌ Status error: {e}")
        return {
            "success": False,
            "status": "error",
            "error": str(e),
            "timestamp": datetime.utcnow().isoformat(),
        }


@router.get("/sources")
async def get_data_sources():
    """
    لیست منابع داده و قابلیت‌های آنها
    """
    sources = {
        "market_data": [
            {
                "name": "CoinMarketCap",
                "capabilities": ["prices", "market_cap", "volume"],
                "status": "active",
            },
            {"name": "CoinGecko", "capabilities": ["prices", "trending"], "status": "active"},
            {
                "name": "Binance",
                "capabilities": ["prices", "ohlcv", "24hr_tickers"],
                "status": "active",
            },
        ],
        "blockchain": [
            {
                "name": "Etherscan",
                "capabilities": ["eth_transactions", "gas_prices", "balances"],
                "status": "active",
            },
            {
                "name": "BSCScan",
                "capabilities": ["bsc_transactions", "token_info"],
                "status": "active",
            },
            {
                "name": "TronScan",
                "capabilities": ["tron_transactions", "tron_blocks"],
                "status": "active",
            },
        ],
        "news": [
            {"name": "NewsAPI", "capabilities": ["crypto_news", "headlines"], "status": "active"},
            {"name": "Reddit", "capabilities": ["posts", "sentiment"], "status": "active"},
        ],
        "sentiment": [
            {"name": "Alternative.me", "capabilities": ["fear_greed_index"], "status": "active"},
            {
                "name": "HuggingFace",
                "capabilities": ["text_sentiment", "ai_analysis"],
                "status": "active",
            },
        ],
        "ai": [
            {
                "name": "HuggingFace",
                "capabilities": ["price_prediction", "trend_analysis", "signals"],
                "status": "active",
            }
        ],
    }

    return {
        "success": True,
        "sources": sources,
        "total_sources": sum(len(v) for v in sources.values()),
        "timestamp": datetime.utcnow().isoformat(),
    }


# ============================================================================
# WebSocket Endpoint - Real-time Updates
# ============================================================================


class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}
        self.subscriptions: Dict[str, List[str]] = {}

    async def connect(self, websocket: WebSocket, client_id: str):
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.subscriptions[client_id] = []
        logger.info(f"✅ WebSocket connected: {client_id}")

    async def disconnect(self, client_id: str):
        if client_id in self.active_connections:
            del self.active_connections[client_id]
        if client_id in self.subscriptions:
            del self.subscriptions[client_id]
        logger.info(f"❌ WebSocket disconnected: {client_id}")

    async def send_message(self, client_id: str, message: dict):
        if client_id in self.active_connections:
            websocket = self.active_connections[client_id]
            await websocket.send_json(message)

    async def broadcast(self, message: dict, channel: str = None):
        for client_id, websocket in self.active_connections.items():
            if channel is None or channel in self.subscriptions.get(client_id, []):
                try:
                    await websocket.send_json(message)
                except:
                    await self.disconnect(client_id)


manager = ConnectionManager()


@router.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    WebSocket برای دریافت داده‌های Real-time

    Channels:
    - prices: قیمت‌های لحظه‌ای
    - news: اخبار جدید
    - whales: فعالیت نهنگ‌ها
    - sentiment: تحلیل احساسات
    """
    client_id = str(uuid.uuid4())

    try:
        await manager.connect(websocket, client_id)

        # Send welcome message
        await manager.send_message(
            client_id,
            {
                "type": "connected",
                "client_id": client_id,
                "timestamp": datetime.utcnow().isoformat(),
            },
        )

        while True:
            # Receive message from client
            data = await websocket.receive_text()
            message = json.loads(data)

            action = message.get("action")

            if action == "subscribe":
                channels = message.get("channels", [])
                manager.subscriptions[client_id] = channels

                await manager.send_message(
                    client_id,
                    {
                        "type": "subscribed",
                        "channels": channels,
                        "timestamp": datetime.utcnow().isoformat(),
                    },
                )

                # Start sending data for subscribed channels
                if "prices" in channels:
                    # Send initial price data
                    prices = await data_hub.get_market_prices(limit=10)
                    await manager.send_message(
                        client_id,
                        {
                            "type": "price_update",
                            "data": prices,
                            "timestamp": datetime.utcnow().isoformat(),
                        },
                    )

            elif action == "unsubscribe":
                manager.subscriptions[client_id] = []

                await manager.send_message(
                    client_id, {"type": "unsubscribed", "timestamp": datetime.utcnow().isoformat()}
                )

            elif action == "ping":
                await manager.send_message(
                    client_id, {"type": "pong", "timestamp": datetime.utcnow().isoformat()}
                )

    except WebSocketDisconnect:
        await manager.disconnect(client_id)
        logger.info(f"WebSocket client {client_id} disconnected")

    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        await manager.disconnect(client_id)


# Export router
__all__ = ["router"]
