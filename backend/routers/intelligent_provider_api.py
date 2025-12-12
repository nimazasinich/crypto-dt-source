"""
Intelligent Provider API Router
Exposes intelligent load-balanced provider service
TRUE ROUND-ROBIN with health-based selection - No fake data!
"""

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from typing import List, Optional
import logging

from backend.services.intelligent_provider_service import get_intelligent_provider_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/providers", tags=["Intelligent Providers"])


@router.get("/market-prices")
async def get_market_prices(
    symbols: Optional[str] = Query(None, description="Comma-separated list of symbols (e.g., BTC,ETH,BNB)"),
    limit: int = Query(100, ge=1, le=250, description="Number of results to return")
):
    """
    Get market prices with intelligent load balancing
    
    Features:
    - TRUE round-robin distribution across ALL providers
    - Each provider goes to back of queue after use
    - Health-based selection (avoids failed providers)
    - Automatic exponential backoff on failures
    - Provider-specific caching
    
    **NO FAKE DATA - All data from real APIs only!**
    """
    try:
        service = get_intelligent_provider_service()
        
        # Parse symbols
        symbol_list = None
        if symbols:
            symbol_list = [s.strip().upper() for s in symbols.split(',')]
        
        # Get prices with intelligent load balancing
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


@router.get("/stats")
async def get_provider_stats():
    """
    Get statistics for all providers
    
    Returns:
    - Current queue order
    - Provider health and load scores
    - Success/failure rates
    - Backoff status
    - Cache statistics
    """
    try:
        service = get_intelligent_provider_service()
        stats = service.get_provider_stats()
        
        return JSONResponse(content={
            "success": True,
            "stats": stats
        })
    
    except Exception as e:
        logger.error(f"Error fetching provider stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health")
async def health_check():
    """
    Check health of intelligent provider service
    """
    try:
        service = get_intelligent_provider_service()
        stats = service.get_provider_stats()
        
        # Count available providers
        available_count = sum(
            1 for p in stats['providers'].values() 
            if p.get('is_available', False)
        )
        
        total_count = len(stats['providers'])
        
        # Calculate total requests
        total_requests = sum(
            p.get('total_requests', 0) 
            for p in stats['providers'].values()
        )
        
        # Calculate average success rate
        success_rates = [
            p.get('success_rate', 0) 
            for p in stats['providers'].values()
        ]
        avg_success_rate = sum(success_rates) / len(success_rates) if success_rates else 0
        
        return JSONResponse(content={
            "success": True,
            "status": "healthy" if available_count > 0 else "degraded",
            "available_providers": available_count,
            "total_providers": total_count,
            "cache_entries": stats['cache']['valid_entries'],
            "total_requests": total_requests,
            "avg_success_rate": round(avg_success_rate, 2),
            "queue_order": stats['queue_order']
        })
    
    except Exception as e:
        logger.error(f"Error checking health: {e}")
        raise HTTPException(status_code=500, detail=str(e))


__all__ = ["router"]
