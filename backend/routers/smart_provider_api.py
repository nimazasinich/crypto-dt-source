"""
Smart Provider API Router
Exposes smart provider service with rate limiting, caching, and intelligent fallback
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import List, Optional
import logging

from backend.services.smart_provider_service import get_smart_provider_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/smart-providers", tags=["Smart Providers"])


@router.get("/market-prices")
async def get_market_prices(
    symbols: Optional[str] = Query(None, description="Comma-separated list of symbols (e.g., BTC,ETH,BNB)"),
    limit: int = Query(100, ge=1, le=250, description="Number of results to return")
):
    """
    Get market prices with smart provider fallback
    
    Features:
    - Smart provider rotation (Binance → CoinCap → CoinGecko)
    - Automatic rate limit handling with exponential backoff
    - Provider-specific caching (30s to 5min)
    - 429 error prevention for CoinGecko
    """
    try:
        service = get_smart_provider_service()
        
        # Parse symbols
        symbol_list = None
        if symbols:
            symbol_list = [s.strip().upper() for s in symbols.split(',')]
        
        # Get prices with smart fallback
        result = await service.get_market_prices(symbols=symbol_list, limit=limit)
        
        return JSONResponse(content={
            "success": True,
            "data": result['data'],
            "meta": {
                "source": result['source'],
                "cached": result.get('cached', False),
                "timestamp": result['timestamp'],
                "count": len(result['data']),
                "error": result.get('error')
            }
        })
    
    except Exception as e:
        logger.error(f"Error fetching market prices: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/provider-stats")
async def get_provider_stats():
    """
    Get statistics for all providers
    
    Returns:
    - Provider health status
    - Success/failure rates
    - Rate limit hits
    - Backoff status
    - Cache statistics
    """
    try:
        service = get_smart_provider_service()
        stats = service.get_provider_stats()
        
        return JSONResponse(content={
            "success": True,
            "stats": stats
        })
    
    except Exception as e:
        logger.error(f"Error fetching provider stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reset-provider/{provider_name}")
async def reset_provider(provider_name: str):
    """
    Reset a specific provider's backoff and stats
    
    Use this to manually reset a provider that's in backoff mode
    """
    try:
        service = get_smart_provider_service()
        service.reset_provider(provider_name)
        
        return JSONResponse(content={
            "success": True,
            "message": f"Provider {provider_name} reset successfully"
        })
    
    except Exception as e:
        logger.error(f"Error resetting provider: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/clear-cache")
async def clear_cache():
    """
    Clear all cached data
    
    Use this to force fresh data from providers
    """
    try:
        service = get_smart_provider_service()
        service.clear_cache()
        
        return JSONResponse(content={
            "success": True,
            "message": "Cache cleared successfully"
        })
    
    except Exception as e:
        logger.error(f"Error clearing cache: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """
    Check health of smart provider service
    """
    try:
        service = get_smart_provider_service()
        stats = service.get_provider_stats()
        
        # Count available providers
        available_count = sum(
            1 for p in stats['providers'].values() 
            if p.get('is_available', False)
        )
        
        total_count = len(stats['providers'])
        
        return JSONResponse(content={
            "success": True,
            "status": "healthy" if available_count > 0 else "degraded",
            "available_providers": available_count,
            "total_providers": total_count,
            "cache_entries": stats['cache']['valid_entries']
        })
    
    except Exception as e:
        logger.error(f"Error checking health: {e}")
        raise HTTPException(status_code=500, detail=str(e))


__all__ = ["router"]
