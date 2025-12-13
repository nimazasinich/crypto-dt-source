"""
Crypto API Hub Self-Healing Backend Router

This module provides backend support for the self-healing crypto API hub,
including health monitoring, diagnostics, and automatic recovery mechanisms.
"""

from fastapi import APIRouter, HTTPException, Request, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import httpx
import asyncio
from datetime import datetime, timedelta
import logging
from pathlib import Path

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/crypto-hub",
    tags=["Crypto API Hub Self-Healing"]
)

# Health monitoring storage
health_status: Dict[str, Dict[str, Any]] = {}
failed_endpoints: Dict[str, Dict[str, Any]] = {}
recovery_log: List[Dict[str, Any]] = []


class HealthCheckRequest(BaseModel):
    """Model for health check request"""
    endpoints: List[str]


class RecoveryRequest(BaseModel):
    """Model for manual recovery trigger"""
    endpoint: str


@router.get("/", response_class=HTMLResponse)
async def serve_crypto_hub():
    """
    Serve the crypto API hub HTML page
    """
    try:
        html_path = Path(__file__).parent.parent.parent / "static" / "crypto-api-hub-stunning.html"
        
        if not html_path.exists():
            raise HTTPException(status_code=404, detail="Crypto API Hub page not found")
        
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Inject self-healing script (NO backend proxying of arbitrary URLs)
        injection = '''
    <script src="/static/js/crypto-api-hub-self-healing.js"></script>
    <script>
        // Initialize self-healing system
        const selfHealing = new SelfHealingAPIHub({
            backendUrl: '/api/crypto-hub',
            enableAutoRecovery: true,
            enableCaching: true,
            retryAttempts: 3,
            healthCheckInterval: 60000
        });

        // Add health status indicator to UI
        function addHealthIndicator() {
            const header = document.querySelector('.header-actions');
            if (header) {
                const healthBtn = document.createElement('button');
                healthBtn.className = 'btn-gradient';
                healthBtn.innerHTML = `
                    <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2">
                        <path d="M22 12h-4l-3 9L9 3l-3 9H2"></path>
                    </svg>
                    <span id="health-status">Health</span>
                `;
                healthBtn.onclick = showHealthStatus;
                header.insertBefore(healthBtn, header.firstChild);

                // Update health status periodically
                setInterval(updateHealthIndicator, 30000);
                updateHealthIndicator();
            }
        }

        async function updateHealthIndicator() {
            const health = selfHealing.getHealthStatus();
            const statusElement = document.getElementById('health-status');
            if (statusElement) {
                statusElement.textContent = `Health: ${health.healthPercentage}%`;
            }
        }

        async function showHealthStatus() {
            const diagnostics = selfHealing.getDiagnostics();
            alert(`System Health Status\\n\\n` +
                  `Healthy: ${diagnostics.health.healthy}/${diagnostics.health.total}\\n` +
                  `Failed Endpoints: ${diagnostics.health.failedEndpoints}\\n` +
                  `Cache Entries: ${diagnostics.cache.size}\\n` +
                  `Health: ${diagnostics.health.healthPercentage}%`);
        }

        // Initialize on page load
        if (document.readyState === 'loading') {
            document.addEventListener('DOMContentLoaded', addHealthIndicator);
        } else {
            addHealthIndicator();
        }
    </script>
</body>'''
        
        html_content = html_content.replace('</body>', injection)
        
        return HTMLResponse(content=html_content)
    
    except Exception as e:
        logger.error(f"Error serving crypto hub: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/health-check")
async def health_check(request: HealthCheckRequest, background_tasks: BackgroundTasks):
    """
    Perform health checks on multiple endpoints
    """
    results = {}
    
    for endpoint in request.endpoints:
        background_tasks.add_task(check_endpoint_health, endpoint)
        
        # Return cached status if available
        if endpoint in health_status:
            results[endpoint] = health_status[endpoint]
        else:
            results[endpoint] = {
                "status": "checking",
                "message": "Health check in progress"
            }
    
    return {
        "success": True,
        "results": results,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/health-status")
async def get_health_status():
    """
    Get current health status of all monitored endpoints
    """
    total = len(health_status)
    healthy = sum(1 for s in health_status.values() if s.get("status") == "healthy")
    degraded = sum(1 for s in health_status.values() if s.get("status") == "degraded")
    unhealthy = sum(1 for s in health_status.values() if s.get("status") == "unhealthy")
    
    return {
        "total": total,
        "healthy": healthy,
        "degraded": degraded,
        "unhealthy": unhealthy,
        "health_percentage": round((healthy / total * 100)) if total > 0 else 0,
        "failed_endpoints": len(failed_endpoints),
        "endpoints": health_status,
        "timestamp": datetime.utcnow().isoformat()
    }


@router.post("/recover")
async def trigger_recovery(request: RecoveryRequest):
    """
    Manually trigger recovery for a specific endpoint
    """
    try:
        logger.info(f"Manual recovery triggered for: {request.endpoint}")
        
        # Check endpoint health
        is_healthy = await check_endpoint_health(request.endpoint)
        
        if is_healthy:
            # Remove from failed endpoints
            if request.endpoint in failed_endpoints:
                del failed_endpoints[request.endpoint]
            
            # Log recovery
            recovery_log.append({
                "endpoint": request.endpoint,
                "timestamp": datetime.utcnow().isoformat(),
                "type": "manual",
                "success": True
            })
            
            return {
                "success": True,
                "message": "Endpoint recovered successfully",
                "endpoint": request.endpoint
            }
        else:
            return {
                "success": False,
                "message": "Endpoint still unhealthy",
                "endpoint": request.endpoint
            }
    
    except Exception as e:
        logger.error(f"Recovery error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/diagnostics")
async def get_diagnostics():
    """
    Get comprehensive diagnostics information
    """
    return {
        "health": await get_health_status(),
        "failed_endpoints": [
            {
                "url": url,
                **details
            }
            for url, details in failed_endpoints.items()
        ],
        "recovery_log": recovery_log[-50:],  # Last 50 recovery attempts
        "timestamp": datetime.utcnow().isoformat()
    }


@router.get("/recovery-log")
async def get_recovery_log(limit: int = 50):
    """
    Get recovery log
    """
    return {
        "log": recovery_log[-limit:],
        "total": len(recovery_log),
        "timestamp": datetime.utcnow().isoformat()
    }


@router.delete("/clear-failures")
async def clear_failures():
    """
    Clear all failure records (admin function)
    """
    global failed_endpoints, recovery_log
    
    cleared = len(failed_endpoints)
    failed_endpoints.clear()
    recovery_log.clear()
    
    return {
        "success": True,
        "cleared": cleared,
        "message": f"Cleared {cleared} failure records"
    }


# Helper functions

async def check_endpoint_health(endpoint: str) -> bool:
    """
    Check health of a specific endpoint
    """
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            response = await client.head(endpoint)
            
            is_healthy = response.status_code < 400
            
            health_status[endpoint] = {
                "status": "healthy" if is_healthy else "degraded",
                "status_code": response.status_code,
                "last_check": datetime.utcnow().isoformat(),
                "response_time": response.elapsed.total_seconds()
            }
            
            return is_healthy
    
    except Exception as e:
        health_status[endpoint] = {
            "status": "unhealthy",
            "last_check": datetime.utcnow().isoformat(),
            "error": str(e)
        }
        
        record_failure(endpoint, str(e))
        return False


def record_failure(endpoint: str, error: str):
    """
    Record endpoint failure
    """
    if endpoint not in failed_endpoints:
        failed_endpoints[endpoint] = {
            "count": 0,
            "first_failure": datetime.utcnow().isoformat(),
            "errors": []
        }
    
    record = failed_endpoints[endpoint]
    record["count"] += 1
    record["last_failure"] = datetime.utcnow().isoformat()
    record["errors"].append({
        "timestamp": datetime.utcnow().isoformat(),
        "message": error
    })
    
    # Keep only last 10 errors
    if len(record["errors"]) > 10:
        record["errors"] = record["errors"][-10:]
    
    logger.error(f"Endpoint failure recorded: {endpoint} ({record['count']} failures)")


# Background task for continuous monitoring
async def continuous_monitoring():
    """
    Background task for continuous endpoint monitoring
    """
    while True:
        try:
            # Check all registered endpoints
            for endpoint in list(health_status.keys()):
                await check_endpoint_health(endpoint)
            
            # Clean up old failures (older than 1 hour)
            current_time = datetime.utcnow()
            to_remove = []
            
            for endpoint, record in failed_endpoints.items():
                last_failure = datetime.fromisoformat(record["last_failure"])
                if current_time - last_failure > timedelta(hours=1):
                    to_remove.append(endpoint)
            
            for endpoint in to_remove:
                del failed_endpoints[endpoint]
                logger.info(f"Cleaned up old failure record: {endpoint}")
            
            # Wait before next check
            await asyncio.sleep(60)  # Check every minute
        
        except Exception as e:
            logger.error(f"Monitoring error: {e}")
            await asyncio.sleep(60)
