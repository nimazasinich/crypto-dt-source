"""Data models for the HuggingFace Crypto Data Engine"""

from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class OHLCV(BaseModel):
    """OHLCV candlestick data model"""

    timestamp: int = Field(..., description="Unix timestamp in milliseconds")
    open: float = Field(..., description="Opening price")
    high: float = Field(..., description="Highest price")
    low: float = Field(..., description="Lowest price")
    close: float = Field(..., description="Closing price")
    volume: float = Field(..., description="Trading volume")


class OHLCVResponse(BaseModel):
    """Response model for OHLCV endpoint"""

    success: bool = True
    data: List[OHLCV]
    symbol: str
    interval: str
    count: int
    source: str
    timestamp: Optional[int] = None


class Price(BaseModel):
    """Price data model"""

    symbol: str
    name: str
    price: float
    priceUsd: float
    change1h: Optional[float] = None
    change24h: Optional[float] = None
    change7d: Optional[float] = None
    volume24h: Optional[float] = None
    marketCap: Optional[float] = None
    rank: Optional[int] = None
    lastUpdate: str


class PricesResponse(BaseModel):
    """Response model for prices endpoint"""

    success: bool = True
    data: List[Price]
    timestamp: int
    source: str


class FearGreedIndex(BaseModel):
    """Fear & Greed Index model"""

    value: int = Field(..., ge=0, le=100)
    classification: str
    timestamp: str


class NewsSentiment(BaseModel):
    """News sentiment aggregation"""

    bullish: int = 0
    bearish: int = 0
    neutral: int = 0
    total: int = 0


class OverallSentiment(BaseModel):
    """Overall sentiment score"""

    sentiment: str  # "bullish", "bearish", "neutral"
    score: int = Field(..., ge=0, le=100)
    confidence: float = Field(..., ge=0, le=1)


class SentimentData(BaseModel):
    """Sentiment data model"""

    fearGreed: FearGreedIndex
    news: NewsSentiment
    overall: OverallSentiment


class SentimentResponse(BaseModel):
    """Response model for sentiment endpoint"""

    success: bool = True
    data: SentimentData
    timestamp: int


class MarketOverview(BaseModel):
    """Market overview data model"""

    totalMarketCap: float
    totalVolume24h: float
    btcDominance: float
    ethDominance: float
    activeCoins: int
    topGainers: List[Price] = []
    topLosers: List[Price] = []
    trending: List[Price] = []


class MarketOverviewResponse(BaseModel):
    """Response model for market overview endpoint"""

    success: bool = True
    data: MarketOverview
    timestamp: int


class ProviderHealth(BaseModel):
    """Provider health status"""

    name: str
    status: str  # "online", "offline", "degraded"
    latency: Optional[int] = None  # milliseconds
    lastCheck: str
    errorMessage: Optional[str] = None


class CacheInfo(BaseModel):
    """Cache statistics"""

    size: int
    hitRate: float


class HealthResponse(BaseModel):
    """Response model for health endpoint"""

    status: str  # "healthy", "degraded", "unhealthy"
    uptime: int  # seconds
    version: str
    providers: List[ProviderHealth]
    cache: CacheInfo


class ErrorResponse(BaseModel):
    """Error response model"""

    success: bool = False
    error: ErrorDetail
    timestamp: int


class ErrorDetail(BaseModel):
    """Error detail"""

    code: str
    message: str
    details: Optional[dict] = None
    retryAfter: Optional[int] = None
