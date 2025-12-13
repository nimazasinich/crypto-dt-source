#!/usr/bin/env python3
"""
Service Health Monitor API
Real-time monitoring of all API services and data providers
Shows status, response times, success rates, and health metrics
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
from datetime import datetime
import logging
import asyncio
import httpx
import time

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/health", tags=["Health Monitor"])


class ServiceStatus(BaseModel):
    """Service status model"""
    name: str
    status: str  # "online", "offline", "rate_limited", "degraded"
    response_time_ms: Optional[float] = None
    last_check: str
    last_error: Optional[str] = None
    success_rate: Optional[float] = None
    details: Optional[Dict[str, Any]] = None


class HealthMonitorResponse(BaseModel):
    """Health monitor response"""
    timestamp: str
    total_services: int
    online: int
    offline: int
    rate_limited: int
    degraded: int
    services: List[ServiceStatus]
    overall_health: str  # "healthy", "degraded", "critical"


# Service configuration for health checks
SERVICES_CONFIG = {
    "crypto_api_clean": {
        "name": "Crypto API Clean",
        "category": "Resource Database",
        "endpoint": "https://really-amin-crypto-api-clean-fixed.hf.space/api/resources/stats",
        "timeout": 10,
        "sub_services": ["rpc_nodes (24)", "block_explorers (33)", "market_data_apis (33)", "news_apis (17)", "sentiment_apis (14)"],
        "description": "281+ cryptocurrency resources across 12 categories",
        "priority": 2
    },
    "crypto_dt_source": {
        "name": "Crypto DT Source",
        "category": "Unified Data API",
        "endpoint": "https://crypto-dt-source.onrender.com/api/v1/status",
        "timeout": 15,
        "sub_services": ["prices", "klines", "sentiment", "models", "datasets"],
        "description": "Unified API v2.0.0 with 4 AI models and 5 datasets",
        "priority": 2
    },
    "coingecko": {
        "name": "CoinGecko",
        "category": "Data Provider",
        "endpoint": "https://api.coingecko.com/api/v3/ping",
        "timeout": 5,
        "sub_services": ["prices", "market_data", "ohlcv"]
    },
    "binance": {
        "name": "Binance",
        "category": "Exchange",
        "endpoint": "https://api.binance.com/api/v3/ping",
        "timeout": 5,
        "sub_services": ["spot", "futures", "websocket"]
    },
    "coincap": {
        "name": "CoinCap",
        "category": "Data Provider",
        "endpoint": "https://api.coincap.io/v2/assets/bitcoin",
        "timeout": 5,
        "sub_services": ["assets", "markets", "rates"]
    },
    "cryptocompare": {
        "name": "CryptoCompare",
        "category": "Data Provider",
        "endpoint": "https://min-api.cryptocompare.com/data/price?fsym=BTC&tsyms=USD",
        "timeout": 5,
        "sub_services": ["price", "historical", "social"]
    },
    "huggingface": {
        "name": "HuggingFace Space",
        "category": "Internal",
        "endpoint": "/api/health/self",
        "timeout": 3,
        "sub_services": ["api", "websocket", "database"],
        "internal": True
    },
    "backend_indicators": {
        "name": "Technical Indicators",
        "category": "Internal",
        "endpoint": "/api/indicators/services",
        "timeout": 3,
        "sub_services": ["rsi", "macd", "bollinger_bands", "comprehensive"],
        "internal": True
    },
    "backend_market": {
        "name": "Market Data API",
        "category": "Internal",
        "endpoint": "/api/market/crypto/list",
        "timeout": 3,
        "sub_services": ["prices", "ohlcv", "tickers"],
        "internal": True
    }
}


def get_base_url() -> str:
    """Get the base URL for internal services"""
    import os
    # For HF Spaces
    if os.getenv("SPACE_ID"):
        return f"https://{os.getenv('SPACE_ID')}.hf.space"
    # For local development
    return "http://localhost:7860"


async def check_service_health(service_id: str, config: Dict[str, Any]) -> ServiceStatus:
    """
    Check the health of a single service
    """
    start_time = time.time()
    
    try:
        # Build URL for internal services
        endpoint = config["endpoint"]
        if config.get("internal", False):
            base_url = get_base_url()
            endpoint = f"{base_url}{endpoint}" if not endpoint.startswith("http") else endpoint
        
        async with httpx.AsyncClient() as client:
            response = await client.get(
                endpoint,
                timeout=config.get("timeout", 5),
                follow_redirects=True
            )
            
            response_time = (time.time() - start_time) * 1000  # Convert to ms
            
            # Determine status
            if response.status_code == 200:
                status = "online"
            elif response.status_code == 429:
                status = "rate_limited"
            elif 500 <= response.status_code < 600:
                status = "degraded"
            else:
                status = "offline"
            
            # Calculate success rate (simplified - in production, use historical data)
            success_rate = 100.0 if status == "online" else 50.0 if status == "degraded" else 0.0
            
            return ServiceStatus(
                name=config["name"],
                status=status,
                response_time_ms=round(response_time, 2),
                last_check=datetime.utcnow().isoformat() + "Z",
                last_error=None if status == "online" else f"HTTP {response.status_code}",
                success_rate=success_rate,
                details={
                    "category": config.get("category", "Unknown"),
                    "sub_services": config.get("sub_services", []),
                    "http_status": response.status_code
                }
            )
            
    except asyncio.TimeoutError:
        return ServiceStatus(
            name=config["name"],
            status="offline",
            response_time_ms=config.get("timeout", 5) * 1000,
            last_check=datetime.utcnow().isoformat() + "Z",
            last_error="Request timeout",
            success_rate=0.0,
            details={
                "category": config.get("category", "Unknown"),
                "sub_services": config.get("sub_services", []),
                "error_type": "timeout"
            }
        )
    except httpx.ConnectError as e:
        return ServiceStatus(
            name=config["name"],
            status="offline",
            response_time_ms=None,
            last_check=datetime.utcnow().isoformat() + "Z",
            last_error=f"Connection failed: {str(e)[:100]}",
            success_rate=0.0,
            details={
                "category": config.get("category", "Unknown"),
                "sub_services": config.get("sub_services", []),
                "error_type": "connection_error"
            }
        )
    except Exception as e:
        logger.error(f"Error checking {service_id}: {e}")
        return ServiceStatus(
            name=config["name"],
            status="offline",
            response_time_ms=None,
            last_check=datetime.utcnow().isoformat() + "Z",
            last_error=str(e)[:100],
            success_rate=0.0,
            details={
                "category": config.get("category", "Unknown"),
                "sub_services": config.get("sub_services", []),
                "error_type": "unknown_error"
            }
        )


@router.get("/monitor", response_model=HealthMonitorResponse)
async def get_service_health():
    """
    Get health status of all services
    Returns real-time status of all API providers and internal services
    """
    try:
        # Check all services concurrently
        tasks = [
            check_service_health(service_id, config)
            for service_id, config in SERVICES_CONFIG.items()
        ]
        
        services = await asyncio.gather(*tasks)
        
        # Calculate statistics
        online = sum(1 for s in services if s.status == "online")
        offline = sum(1 for s in services if s.status == "offline")
        rate_limited = sum(1 for s in services if s.status == "rate_limited")
        degraded = sum(1 for s in services if s.status == "degraded")
        
        # Determine overall health
        total = len(services)
        if online == total:
            overall_health = "healthy"
        elif online >= total * 0.7:
            overall_health = "degraded"
        else:
            overall_health = "critical"
        
        return HealthMonitorResponse(
            timestamp=datetime.utcnow().isoformat() + "Z",
            total_services=total,
            online=online,
            offline=offline,
            rate_limited=rate_limited,
            degraded=degraded,
            services=services,
            overall_health=overall_health
        )
        
    except Exception as e:
        logger.error(f"Health monitor error: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to check service health: {str(e)}")


@router.get("/self")
async def health_check():
    """
    Simple health check endpoint for this service
    """
    return {
        "status": "healthy",
        "service": "crypto-intelligence-hub",
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "version": "1.0.0"
    }


@router.get("/services")
async def list_monitored_services():
    """
    List all monitored services with their configuration
    """
    return {
        "success": True,
        "total_services": len(SERVICES_CONFIG),
        "services": [
            {
                "id": service_id,
                "name": config["name"],
                "category": config.get("category", "Unknown"),
                "sub_services": config.get("sub_services", [])
            }
            for service_id, config in SERVICES_CONFIG.items()
        ],
        "timestamp": datetime.utcnow().isoformat() + "Z"
    }
