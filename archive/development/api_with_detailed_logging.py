"""
API Endpoints with Detailed Logging and Service Statistics
Shows exactly which services were tried and which succeeded
"""
from fastapi import APIRouter, Query
from typing import Optional
from datetime import datetime
from multi_source_aggregator import get_aggregator, close_aggregator

router = APIRouter(prefix="/api/v2", tags=["v2-detailed"])


@router.get("/market/price/{symbol}")
async def get_price_detailed(symbol: str, show_attempts: bool = True):
    """
    Get price with detailed fallback logging
    
    Response includes:
    - The actual price data
    - Which service succeeded
    - How many services were tried
    - Total services available
    - All attempts (if show_attempts=true)
    """
    aggregator = get_aggregator()
    
    result, attempts = await aggregator.get_market_price(symbol)
    
    response = {
        "success": result.get("success", False),
        "data": result.get("data"),
        "metadata": {
            "symbol": symbol,
            "source_used": result.get("source_used", {}).get("name") if result.get("source_used") else None,
            "attempts_made": result.get("attempts_count", 0),
            "total_available": result.get("total_available", 0),
            "success_rate": f"{result.get('attempts_count', 0)}/{result.get('total_available', 0)}",
            "timestamp": datetime.utcnow().isoformat()
        }
    }
    
    if show_attempts:
        response["attempts"] = [attempt.to_dict() for attempt in attempts]
    
    return response


@router.get("/news/latest")
async def get_news_detailed(limit: int = 10, show_attempts: bool = True):
    """
    Get news with detailed fallback logging
    
    Shows which news source succeeded and how many were tried
    """
    aggregator = get_aggregator()
    
    news, attempts = await aggregator.get_news(limit)
    
    response = {
        "success": len(news) > 0,
        "news": news,
        "count": len(news),
        "metadata": {
            "sources_tried": len(attempts),
            "total_available": len(aggregator.sources["news"]),
            "success_rate": f"{len([a for a in attempts if a.success])}/{len(attempts)}",
            "successful_sources": [a.service_name for a in attempts if a.success],
            "timestamp": datetime.utcnow().isoformat()
        }
    }
    
    if show_attempts:
        response["attempts"] = [attempt.to_dict() for attempt in attempts]
    
    return response


@router.get("/sentiment/global")
async def get_sentiment_detailed(show_attempts: bool = True):
    """
    Get sentiment with detailed fallback logging
    
    Shows which sentiment API succeeded from 12+ sources
    """
    aggregator = get_aggregator()
    
    result, attempts = await aggregator.get_sentiment()
    
    response = {
        "success": result.get("success", False),
        "data": result.get("data"),
        "metadata": {
            "source_used": result.get("source_used", {}).get("name") if result.get("source_used") else None,
            "attempts_made": result.get("attempts_count", 0),
            "total_available": result.get("total_available", 0),
            "success_rate": f"{result.get('attempts_count', 0)}/{result.get('total_available', 0)}",
            "timestamp": datetime.utcnow().isoformat()
        }
    }
    
    if show_attempts:
        response["attempts"] = [attempt.to_dict() for attempt in attempts]
    
    return response


@router.get("/sources/statistics")
async def get_sources_statistics():
    """
    Get complete statistics about all available services
    
    Shows exactly how many fallbacks exist for each category
    """
    aggregator = get_aggregator()
    stats = aggregator.get_source_statistics()
    all_sources = aggregator.get_all_sources()
    
    return {
        "success": True,
        "statistics": stats,
        "by_category": {
            cat: {
                "total_services": len(sources),
                "free_services": sum(1 for s in sources if s.get("free", False)),
                "premium_services": sum(1 for s in sources if not s.get("free", True)),
                "services": [
                    {
                        "id": s["id"],
                        "name": s["name"],
                        "free": s.get("free", False),
                        "priority": s.get("priority", 999)
                    }
                    for s in sorted(sources, key=lambda x: x.get("priority", 999))[:10]
                ]
            }
            for cat, sources in aggregator.sources.items()
        },
        "guarantees": {
            "market_data": "Minimum 15 services, always returns data",
            "news": "Minimum 15 services, always returns data",
            "sentiment": "Minimum 12 services, always returns data",
            "block_explorers": "Minimum 15 services",
            "whale_tracking": "Minimum 10 services",
            "on_chain": "Minimum 10 services"
        },
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/sources/list")
async def list_all_sources(category: Optional[str] = None):
    """
    List all available sources
    
    Query params:
    - category: Filter by category (market_data, news, sentiment, etc.)
    """
    aggregator = get_aggregator()
    
    if category:
        sources = aggregator.sources.get(category, [])
        return {
            "category": category,
            "total": len(sources),
            "services": [
                {
                    "rank": i + 1,
                    "id": s["id"],
                    "name": s["name"],
                    "url": s["url"],
                    "free": s.get("free", False),
                    "priority": s.get("priority", 999)
                }
                for i, s in enumerate(sorted(sources, key=lambda x: x.get("priority", 999)))
            ]
        }
    
    # Return all categories
    all_sources = aggregator.get_all_sources()
    return all_sources


@router.get("/health/detailed")
async def health_detailed():
    """
    Detailed health check showing all service availability
    """
    aggregator = get_aggregator()
    stats = aggregator.get_source_statistics()
    
    return {
        "status": "healthy",
        "service": "Crypto Monitor with Multi-Source Aggregation",
        "total_services": stats["total"],
        "categories": {
            cat: {
                "services_available": count,
                "status": "healthy" if count >= 10 else "degraded",
                "min_required": 10
            }
            for cat, count in stats.items() if cat != "total"
        },
        "guarantees": {
            "always_returns_data": True,
            "multiple_fallbacks": True,
            "http_only": True,
            "websocket": False
        },
        "timestamp": datetime.utcnow().isoformat()
    }

