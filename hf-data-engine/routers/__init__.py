"""
REST API Routers for HuggingFace Space Backend

Provides endpoints for:
- /api/v1/blockchain - Blockchain transaction data (ETH, BSC, TRON)
- /api/v1/market - Cryptocurrency market data (CoinMarketCap)
- /api/v1/news - Crypto news aggregation
- /api/v1/hf - HuggingFace AI inference (sentiment, summarization)

All endpoints are REST-only (no WebSockets) and return standardized JSON responses.
"""

from .blockchain import router as blockchain_router
from .hf_inference import router as hf_inference_router
from .market import router as market_router
from .news import router as news_router

__all__ = [
    "blockchain_router",
    "market_router",
    "news_router",
    "hf_inference_router",
]
