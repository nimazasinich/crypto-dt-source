"""
Data Access API Endpoints
Provides user-facing endpoints to access collected cryptocurrency data
"""

from datetime import datetime, timedelta
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel

from database.db_manager import db_manager
from utils.logger import setup_logger

logger = setup_logger("data_endpoints")

router = APIRouter(prefix="/api/crypto", tags=["data"])


# ============================================================================
# Pydantic Models
# ============================================================================

class PriceData(BaseModel):
    """Price data model"""
    symbol: str
    price_usd: float
    market_cap: Optional[float] = None
    volume_24h: Optional[float] = None
    price_change_24h: Optional[float] = None
    timestamp: datetime
    source: str


class NewsArticle(BaseModel):
    """News article model"""
    id: int
    title: str
    content: Optional[str] = None
    source: str
    url: Optional[str] = None
    published_at: datetime
    sentiment: Optional[str] = None
    tags: Optional[List[str]] = None


class WhaleTransaction(BaseModel):
    """Whale transaction model"""
    id: int
    blockchain: str
    transaction_hash: str
    from_address: str
    to_address: str
    amount: float
    amount_usd: float
    timestamp: datetime
    source: str


class SentimentMetric(BaseModel):
    """Sentiment metric model"""
    metric_name: str
    value: float
    classification: str
    timestamp: datetime
    source: str


# ============================================================================
# Market Data Endpoints
# ============================================================================

@router.get("/prices", response_model=List[PriceData])
async def get_all_prices(
    limit: int = Query(default=100, ge=1, le=1000, description="Number of records to return")
):
    """
    Get latest prices for all cryptocurrencies
    
    Returns the most recent price data for all tracked cryptocurrencies
    """
    try:
        prices = db_manager.get_latest_prices(limit=limit)
        
        if not prices:
            return []
        
        return [
            PriceData(
                symbol=p.symbol,
                price_usd=p.price_usd,
                market_cap=p.market_cap,
                volume_24h=p.volume_24h,
                price_change_24h=p.price_change_24h,
                timestamp=p.timestamp,
                source=p.source
            )
            for p in prices
        ]
    
    except Exception as e:
        logger.error(f"Error getting prices: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get prices: {str(e)}")


@router.get("/prices/{symbol}", response_model=PriceData)
async def get_price_by_symbol(symbol: str):
    """
    Get latest price for a specific cryptocurrency
    
    Args:
        symbol: Cryptocurrency symbol (e.g., BTC, ETH, BNB)
    """
    try:
        symbol = symbol.upper()
        price = db_manager.get_latest_price_by_symbol(symbol)
        
        if not price:
            raise HTTPException(status_code=404, detail=f"Price data not found for {symbol}")
        
        return PriceData(
            symbol=price.symbol,
            price_usd=price.price_usd,
            market_cap=price.market_cap,
            volume_24h=price.volume_24h,
            price_change_24h=price.price_change_24h,
            timestamp=price.timestamp,
            source=price.source
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting price for {symbol}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get price: {str(e)}")


@router.get("/history/{symbol}")
async def get_price_history(
    symbol: str,
    hours: int = Query(default=24, ge=1, le=720, description="Number of hours of history"),
    interval: int = Query(default=60, ge=1, le=1440, description="Interval in minutes")
):
    """
    Get price history for a cryptocurrency
    
    Args:
        symbol: Cryptocurrency symbol
        hours: Number of hours of history to return
        interval: Data point interval in minutes
    """
    try:
        symbol = symbol.upper()
        history = db_manager.get_price_history(symbol, hours=hours)
        
        if not history:
            raise HTTPException(status_code=404, detail=f"No history found for {symbol}")
        
        # Sample data based on interval
        sampled = []
        last_time = None
        
        for record in history:
            if last_time is None or (record.timestamp - last_time).total_seconds() >= interval * 60:
                sampled.append({
                    "timestamp": record.timestamp.isoformat(),
                    "price_usd": record.price_usd,
                    "volume_24h": record.volume_24h,
                    "market_cap": record.market_cap
                })
                last_time = record.timestamp
        
        return {
            "symbol": symbol,
            "data_points": len(sampled),
            "interval_minutes": interval,
            "history": sampled
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting history for {symbol}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get history: {str(e)}")


@router.get("/market-overview")
async def get_market_overview():
    """
    Get market overview with top cryptocurrencies
    """
    try:
        prices = db_manager.get_latest_prices(limit=20)
        
        if not prices:
            return {
                "total_market_cap": 0,
                "total_volume_24h": 0,
                "top_gainers": [],
                "top_losers": [],
                "top_by_market_cap": []
            }
        
        # Calculate totals
        total_market_cap = sum(p.market_cap for p in prices if p.market_cap)
        total_volume_24h = sum(p.volume_24h for p in prices if p.volume_24h)
        
        # Sort by price change
        sorted_by_change = sorted(
            [p for p in prices if p.price_change_24h is not None],
            key=lambda x: x.price_change_24h,
            reverse=True
        )
        
        # Sort by market cap
        sorted_by_mcap = sorted(
            [p for p in prices if p.market_cap is not None],
            key=lambda x: x.market_cap,
            reverse=True
        )
        
        return {
            "total_market_cap": total_market_cap,
            "total_volume_24h": total_volume_24h,
            "top_gainers": [
                {
                    "symbol": p.symbol,
                    "price_usd": p.price_usd,
                    "price_change_24h": p.price_change_24h
                }
                for p in sorted_by_change[:5]
            ],
            "top_losers": [
                {
                    "symbol": p.symbol,
                    "price_usd": p.price_usd,
                    "price_change_24h": p.price_change_24h
                }
                for p in sorted_by_change[-5:]
            ],
            "top_by_market_cap": [
                {
                    "symbol": p.symbol,
                    "price_usd": p.price_usd,
                    "market_cap": p.market_cap,
                    "volume_24h": p.volume_24h
                }
                for p in sorted_by_mcap[:10]
            ],
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error getting market overview: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get market overview: {str(e)}")


# ============================================================================
# News Endpoints
# ============================================================================

@router.get("/news", response_model=List[NewsArticle])
async def get_latest_news(
    limit: int = Query(default=50, ge=1, le=200, description="Number of articles"),
    source: Optional[str] = Query(default=None, description="Filter by source"),
    sentiment: Optional[str] = Query(default=None, description="Filter by sentiment")
):
    """
    Get latest cryptocurrency news
    
    Args:
        limit: Maximum number of articles to return
        source: Filter by news source
        sentiment: Filter by sentiment (positive, negative, neutral)
    """
    try:
        news = db_manager.get_latest_news(
            limit=limit,
            source=source,
            sentiment=sentiment
        )
        
        if not news:
            return []
        
        return [
            NewsArticle(
                id=article.id,
                title=article.title,
                content=article.content,
                source=article.source,
                url=article.url,
                published_at=article.published_at,
                sentiment=article.sentiment,
                tags=article.tags.split(',') if article.tags else None
            )
            for article in news
        ]
    
    except Exception as e:
        logger.error(f"Error getting news: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get news: {str(e)}")


@router.get("/news/{news_id}", response_model=NewsArticle)
async def get_news_by_id(news_id: int):
    """
    Get a specific news article by ID
    """
    try:
        article = db_manager.get_news_by_id(news_id)
        
        if not article:
            raise HTTPException(status_code=404, detail=f"News article {news_id} not found")
        
        return NewsArticle(
            id=article.id,
            title=article.title,
            content=article.content,
            source=article.source,
            url=article.url,
            published_at=article.published_at,
            sentiment=article.sentiment,
            tags=article.tags.split(',') if article.tags else None
        )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting news {news_id}: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get news: {str(e)}")


@router.get("/news/search")
async def search_news(
    q: str = Query(..., min_length=2, description="Search query"),
    limit: int = Query(default=50, ge=1, le=200)
):
    """
    Search news articles by keyword
    
    Args:
        q: Search query
        limit: Maximum number of results
    """
    try:
        results = db_manager.search_news(query=q, limit=limit)
        
        return {
            "query": q,
            "count": len(results),
            "results": [
                {
                    "id": article.id,
                    "title": article.title,
                    "source": article.source,
                    "url": article.url,
                    "published_at": article.published_at.isoformat(),
                    "sentiment": article.sentiment
                }
                for article in results
            ]
        }
    
    except Exception as e:
        logger.error(f"Error searching news: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to search news: {str(e)}")


# ============================================================================
# Sentiment Endpoints
# ============================================================================

@router.get("/sentiment/current")
async def get_current_sentiment():
    """
    Get current market sentiment metrics
    """
    try:
        sentiment = db_manager.get_latest_sentiment()
        
        if not sentiment:
            return {
                "fear_greed_index": None,
                "classification": "unknown",
                "timestamp": None,
                "message": "No sentiment data available"
            }
        
        return {
            "fear_greed_index": sentiment.value,
            "classification": sentiment.classification,
            "timestamp": sentiment.timestamp.isoformat(),
            "source": sentiment.source,
            "description": _get_sentiment_description(sentiment.classification)
        }
    
    except Exception as e:
        logger.error(f"Error getting sentiment: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get sentiment: {str(e)}")


@router.get("/sentiment/history")
async def get_sentiment_history(
    hours: int = Query(default=168, ge=1, le=720, description="Hours of history (default: 7 days)")
):
    """
    Get sentiment history
    """
    try:
        history = db_manager.get_sentiment_history(hours=hours)
        
        return {
            "data_points": len(history),
            "history": [
                {
                    "timestamp": record.timestamp.isoformat(),
                    "value": record.value,
                    "classification": record.classification
                }
                for record in history
            ]
        }
    
    except Exception as e:
        logger.error(f"Error getting sentiment history: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get sentiment history: {str(e)}")


# ============================================================================
# Whale Tracking Endpoints
# ============================================================================

@router.get("/whales/transactions", response_model=List[WhaleTransaction])
async def get_whale_transactions(
    limit: int = Query(default=50, ge=1, le=200),
    blockchain: Optional[str] = Query(default=None, description="Filter by blockchain"),
    min_amount_usd: Optional[float] = Query(default=None, ge=0, description="Minimum transaction amount in USD")
):
    """
    Get recent large cryptocurrency transactions (whale movements)
    
    Args:
        limit: Maximum number of transactions
        blockchain: Filter by blockchain (ethereum, bitcoin, etc.)
        min_amount_usd: Minimum transaction amount in USD
    """
    try:
        transactions = db_manager.get_whale_transactions(
            limit=limit,
            blockchain=blockchain,
            min_amount_usd=min_amount_usd
        )
        
        if not transactions:
            return []
        
        return [
            WhaleTransaction(
                id=tx.id,
                blockchain=tx.blockchain,
                transaction_hash=tx.transaction_hash,
                from_address=tx.from_address,
                to_address=tx.to_address,
                amount=tx.amount,
                amount_usd=tx.amount_usd,
                timestamp=tx.timestamp,
                source=tx.source
            )
            for tx in transactions
        ]
    
    except Exception as e:
        logger.error(f"Error getting whale transactions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get whale transactions: {str(e)}")


@router.get("/whales/stats")
async def get_whale_stats(
    hours: int = Query(default=24, ge=1, le=168, description="Time period in hours")
):
    """
    Get whale activity statistics
    """
    try:
        stats = db_manager.get_whale_stats(hours=hours)
        
        return {
            "period_hours": hours,
            "total_transactions": stats.get('total_transactions', 0),
            "total_volume_usd": stats.get('total_volume_usd', 0),
            "avg_transaction_usd": stats.get('avg_transaction_usd', 0),
            "largest_transaction_usd": stats.get('largest_transaction_usd', 0),
            "by_blockchain": stats.get('by_blockchain', {}),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error getting whale stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get whale stats: {str(e)}")


# ============================================================================
# Blockchain Data Endpoints
# ============================================================================

@router.get("/blockchain/gas")
async def get_gas_prices():
    """
    Get current gas prices for various blockchains
    """
    try:
        gas_prices = db_manager.get_latest_gas_prices()
        
        return {
            "ethereum": gas_prices.get('ethereum', {}),
            "bsc": gas_prices.get('bsc', {}),
            "polygon": gas_prices.get('polygon', {}),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error getting gas prices: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get gas prices: {str(e)}")


@router.get("/blockchain/stats")
async def get_blockchain_stats():
    """
    Get blockchain statistics
    """
    try:
        stats = db_manager.get_blockchain_stats()
        
        return {
            "ethereum": stats.get('ethereum', {}),
            "bitcoin": stats.get('bitcoin', {}),
            "bsc": stats.get('bsc', {}),
            "timestamp": datetime.utcnow().isoformat()
        }
    
    except Exception as e:
        logger.error(f"Error getting blockchain stats: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get blockchain stats: {str(e)}")


# ============================================================================
# Helper Functions
# ============================================================================

def _get_sentiment_description(classification: str) -> str:
    """Get human-readable description for sentiment classification"""
    descriptions = {
        "extreme_fear": "Extreme Fear - Investors are very worried",
        "fear": "Fear - Investors are concerned",
        "neutral": "Neutral - Market is balanced",
        "greed": "Greed - Investors are getting greedy",
        "extreme_greed": "Extreme Greed - Market may be overheated"
    }
    return descriptions.get(classification, "Unknown sentiment")

