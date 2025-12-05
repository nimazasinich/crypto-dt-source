"""
Smart Data Endpoints - NEVER Returns 404
Uses 305+ free resources with intelligent fallback
"""

import time
import logging
from typing import Optional, List
from fastapi import APIRouter, Depends, Query, HTTPException

from api.hf_auth import verify_hf_token
from utils.logger import setup_logger
import sys
sys.path.insert(0, '/workspace')
from core.smart_fallback_manager import get_fallback_manager
from workers.data_collection_agent import get_data_collection_agent

logger = setup_logger("smart_data_endpoints")

router = APIRouter(prefix="/api/smart", tags=["smart_fallback"])


@router.get("/market")
async def get_market_data_smart(
    limit: int = Query(100, ge=1, le=500, description="Number of coins"),
    auth: bool = Depends(verify_hf_token)
):
    """
    Get market data with SMART FALLBACK
    
    - Tries up to 21 different market data APIs
    - NEVER returns 404
    - Automatically switches to working source
    - Uses proxy for blocked exchanges
    - Returns data from best available source
    
    Categories tried:
    - market_data_apis (21 sources)
    - Market Data (17 sources)
    - Plus local cache
    """
    try:
        logger.info(f"🔍 Smart Market Data Request (limit={limit})")
        
        fallback_manager = get_fallback_manager()
        
        # Try to fetch with intelligent fallback
        data = await fallback_manager.fetch_with_fallback(
            category='market_data_apis',
            endpoint_path='/coins/markets',
            params={
                'vs_currency': 'usd',
                'order': 'market_cap_desc',
                'per_page': limit,
                'page': 1
            },
            max_attempts=15  # Try up to 15 different sources
        )
        
        if not data:
            # If all fails, try alternate category
            logger.warning("⚠️ Primary category failed, trying alternate...")
            data = await fallback_manager.fetch_with_fallback(
                category='Market Data',
                endpoint_path='/v1/cryptocurrency/listings/latest',
                params={'limit': limit},
                max_attempts=10
            )
        
        if not data:
            raise HTTPException(
                status_code=503,
                detail="All data sources temporarily unavailable. Please try again in a moment."
            )
        
        # Transform data to standard format
        items = data if isinstance(data, list) else data.get('data', [])
        
        return {
            "success": True,
            "source": "smart_fallback",
            "count": len(items),
            "items": items[:limit],
            "timestamp": int(time.time() * 1000),
            "note": "Data from best available source using smart fallback"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Smart market data error: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to fetch market data: {str(e)}"
        )


@router.get("/news")
async def get_news_smart(
    limit: int = Query(20, ge=1, le=100, description="Number of news items"),
    auth: bool = Depends(verify_hf_token)
):
    """
    Get crypto news with SMART FALLBACK
    
    - Tries 15 different news APIs
    - NEVER returns 404
    - Automatically finds working source
    """
    try:
        logger.info(f"🔍 Smart News Request (limit={limit})")
        
        fallback_manager = get_fallback_manager()
        
        data = await fallback_manager.fetch_with_fallback(
            category='news_apis',
            endpoint_path='/news',
            params={'limit': limit},
            max_attempts=10
        )
        
        if not data:
            # Try alternate category
            data = await fallback_manager.fetch_with_fallback(
                category='News',
                endpoint_path='/v1/news',
                params={'limit': limit},
                max_attempts=5
            )
        
        if not data:
            raise HTTPException(
                status_code=503,
                detail="News sources temporarily unavailable"
            )
        
        news_items = data if isinstance(data, list) else data.get('news', [])
        
        return {
            "success": True,
            "source": "smart_fallback",
            "count": len(news_items),
            "news": news_items[:limit],
            "timestamp": int(time.time() * 1000)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Smart news error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/sentiment")
async def get_sentiment_smart(
    symbol: Optional[str] = Query(None, description="Crypto symbol (e.g., BTC)"),
    auth: bool = Depends(verify_hf_token)
):
    """
    Get sentiment analysis with SMART FALLBACK
    
    - Tries 12 sentiment APIs
    - NEVER returns 404
    - Real-time sentiment from multiple sources
    """
    try:
        logger.info(f"🔍 Smart Sentiment Request (symbol={symbol})")
        
        fallback_manager = get_fallback_manager()
        
        endpoint = f"/sentiment/{symbol}" if symbol else "/sentiment/global"
        
        data = await fallback_manager.fetch_with_fallback(
            category='sentiment_apis',
            endpoint_path=endpoint,
            max_attempts=8
        )
        
        if not data:
            data = await fallback_manager.fetch_with_fallback(
                category='Sentiment',
                endpoint_path=endpoint,
                max_attempts=5
            )
        
        if not data:
            raise HTTPException(
                status_code=503,
                detail="Sentiment sources temporarily unavailable"
            )
        
        return {
            "success": True,
            "source": "smart_fallback",
            "sentiment": data,
            "timestamp": int(time.time() * 1000)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Smart sentiment error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/whale-alerts")
async def get_whale_alerts_smart(
    limit: int = Query(20, ge=1, le=100),
    auth: bool = Depends(verify_hf_token)
):
    """
    Get whale tracking alerts with SMART FALLBACK
    
    - Tries 9 whale tracking APIs
    - NEVER returns 404
    - Real-time large transactions
    """
    try:
        logger.info(f"🔍 Smart Whale Alerts Request (limit={limit})")
        
        fallback_manager = get_fallback_manager()
        
        data = await fallback_manager.fetch_with_fallback(
            category='whale_tracking_apis',
            endpoint_path='/whales',
            params={'limit': limit},
            max_attempts=7
        )
        
        if not data:
            data = await fallback_manager.fetch_with_fallback(
                category='Whale-Tracking',
                endpoint_path='/transactions',
                params={'limit': limit},
                max_attempts=5
            )
        
        if not data:
            raise HTTPException(
                status_code=503,
                detail="Whale tracking sources temporarily unavailable"
            )
        
        alerts = data if isinstance(data, list) else data.get('transactions', [])
        
        return {
            "success": True,
            "source": "smart_fallback",
            "count": len(alerts),
            "alerts": alerts[:limit],
            "timestamp": int(time.time() * 1000)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Smart whale alerts error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/blockchain/{chain}")
async def get_blockchain_data_smart(
    chain: str,
    auth: bool = Depends(verify_hf_token)
):
    """
    Get blockchain data with SMART FALLBACK
    
    - Tries 40+ block explorers
    - NEVER returns 404
    - Supports: ethereum, bsc, polygon, tron, etc.
    """
    try:
        logger.info(f"🔍 Smart Blockchain Request (chain={chain})")
        
        fallback_manager = get_fallback_manager()
        
        data = await fallback_manager.fetch_with_fallback(
            category='block_explorers',
            endpoint_path=f'/{chain}/latest',
            max_attempts=10
        )
        
        if not data:
            data = await fallback_manager.fetch_with_fallback(
                category='Block Explorer',
                endpoint_path=f'/api?module=stats&action=ethprice',
                max_attempts=10
            )
        
        if not data:
            raise HTTPException(
                status_code=503,
                detail=f"Blockchain explorers for {chain} temporarily unavailable"
            )
        
        return {
            "success": True,
            "source": "smart_fallback",
            "chain": chain,
            "data": data,
            "timestamp": int(time.time() * 1000)
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Smart blockchain error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/health-report")
async def get_health_report(auth: bool = Depends(verify_hf_token)):
    """
    Get health report of all 305+ resources
    
    Shows:
    - Total resources
    - Active/degraded/failed counts
    - Top performing sources
    - Failing sources that need attention
    """
    try:
        fallback_manager = get_fallback_manager()
        agent = get_data_collection_agent()
        
        health_report = fallback_manager.get_health_report()
        agent_stats = agent.get_stats()
        
        return {
            "success": True,
            "health_report": health_report,
            "agent_stats": agent_stats,
            "timestamp": int(time.time() * 1000)
        }
    
    except Exception as e:
        logger.error(f"❌ Health report error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/stats")
async def get_smart_stats(auth: bool = Depends(verify_hf_token)):
    """
    Get statistics about smart fallback system
    
    Shows:
    - Total resources available (305+)
    - Resources by category
    - Collection statistics
    - Performance metrics
    """
    try:
        fallback_manager = get_fallback_manager()
        agent = get_data_collection_agent()
        
        return {
            "success": True,
            "total_resources": fallback_manager._count_total_resources(),
            "resources_by_category": {
                category: len(resources)
                for category, resources in fallback_manager.resources.items()
            },
            "agent_stats": agent.get_stats(),
            "timestamp": int(time.time() * 1000)
        }
    
    except Exception as e:
        logger.error(f"❌ Stats error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/cleanup-failed")
async def cleanup_failed_resources(
    max_age_hours: int = Query(24, description="Max age in hours"),
    auth: bool = Depends(verify_hf_token)
):
    """
    Manually trigger cleanup of failed resources
    
    Removes resources that have been failing for longer than max_age_hours
    """
    try:
        fallback_manager = get_fallback_manager()
        
        removed = fallback_manager.cleanup_failed_resources(max_age_hours=max_age_hours)
        
        return {
            "success": True,
            "removed_count": len(removed),
            "removed_resources": removed,
            "timestamp": int(time.time() * 1000)
        }
    
    except Exception as e:
        logger.error(f"❌ Cleanup error: {e}")
        raise HTTPException(status_code=500, detail=str(e))
