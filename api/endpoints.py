"""
REST API Endpoints for Crypto API Monitoring System
Implements comprehensive monitoring, status tracking, and management endpoints
"""

from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Body
from pydantic import BaseModel, Field

# Import core modules
from database.db_manager import db_manager
from config import config
from monitoring.health_checker import HealthChecker
from monitoring.rate_limiter import rate_limiter
from utils.logger import setup_logger

# Setup logger
logger = setup_logger("api_endpoints")

# Create APIRouter instance
router = APIRouter(prefix="/api", tags=["monitoring"])


# ============================================================================
# Pydantic Models for Request/Response Validation
# ============================================================================

class TriggerCheckRequest(BaseModel):
    """Request model for triggering immediate health check"""
    provider: str = Field(..., description="Provider name to check")


class TestKeyRequest(BaseModel):
    """Request model for testing API key"""
    provider: str = Field(..., description="Provider name to test")


# ============================================================================
# GET /api/status - System Overview
# ============================================================================

@router.get("/status")
async def get_system_status():
    """
    Get comprehensive system status overview

    Returns:
        System overview with provider counts, health metrics, and last update
    """
    try:
        # Get latest system metrics from database
        latest_metrics = db_manager.get_latest_system_metrics()

        if latest_metrics:
            return {
                "total_apis": latest_metrics.total_providers,
                "online": latest_metrics.online_count,
                "degraded": latest_metrics.degraded_count,
                "offline": latest_metrics.offline_count,
                "avg_response_time_ms": round(latest_metrics.avg_response_time_ms, 2),
                "last_update": latest_metrics.timestamp.isoformat(),
                "system_health": latest_metrics.system_health
            }

        # Fallback: Calculate from providers if no metrics available
        providers = db_manager.get_all_providers()

        # Get recent connection attempts for each provider
        status_counts = {"online": 0, "degraded": 0, "offline": 0}
        response_times = []

        for provider in providers:
            attempts = db_manager.get_connection_attempts(
                provider_id=provider.id,
                hours=1,
                limit=10
            )

            if attempts:
                recent = attempts[0]
                if recent.status == "success" and recent.response_time_ms and recent.response_time_ms < 2000:
                    status_counts["online"] += 1
                    response_times.append(recent.response_time_ms)
                elif recent.status == "success":
                    status_counts["degraded"] += 1
                    if recent.response_time_ms:
                        response_times.append(recent.response_time_ms)
                else:
                    status_counts["offline"] += 1
            else:
                status_counts["offline"] += 1

        avg_response_time = sum(response_times) / len(response_times) if response_times else 0

        # Determine system health
        total = len(providers)
        online_pct = (status_counts["online"] / total * 100) if total > 0 else 0

        if online_pct >= 90:
            system_health = "healthy"
        elif online_pct >= 70:
            system_health = "degraded"
        else:
            system_health = "unhealthy"

        return {
            "total_apis": total,
            "online": status_counts["online"],
            "degraded": status_counts["degraded"],
            "offline": status_counts["offline"],
            "avg_response_time_ms": round(avg_response_time, 2),
            "last_update": datetime.utcnow().isoformat(),
            "system_health": system_health
        }

    except Exception as e:
        logger.error(f"Error getting system status: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get system status: {str(e)}")


# ============================================================================
# GET /api/categories - Category Statistics
# ============================================================================

@router.get("/categories")
async def get_categories():
    """
    Get statistics for all provider categories

    Returns:
        List of category statistics with provider counts and health metrics
    """
    try:
        categories = config.get_categories()
        category_stats = []

        for category in categories:
            providers = db_manager.get_all_providers(category=category)

            if not providers:
                continue

            total_sources = len(providers)
            online_sources = 0
            response_times = []
            rate_limited_count = 0
            last_updated = None

            for provider in providers:
                # Get recent attempts
                attempts = db_manager.get_connection_attempts(
                    provider_id=provider.id,
                    hours=1,
                    limit=5
                )

                if attempts:
                    recent = attempts[0]

                    # Update last_updated
                    if not last_updated or recent.timestamp > last_updated:
                        last_updated = recent.timestamp

                    # Count online sources
                    if recent.status == "success" and recent.response_time_ms and recent.response_time_ms < 2000:
                        online_sources += 1
                        response_times.append(recent.response_time_ms)

                    # Count rate limited
                    if recent.status == "rate_limited":
                        rate_limited_count += 1

            # Calculate metrics
            online_ratio = round(online_sources / total_sources, 2) if total_sources > 0 else 0
            avg_response_time = round(sum(response_times) / len(response_times), 2) if response_times else 0

            # Determine status
            if online_ratio >= 0.9:
                status = "healthy"
            elif online_ratio >= 0.7:
                status = "degraded"
            else:
                status = "critical"

            category_stats.append({
                "name": category,
                "total_sources": total_sources,
                "online_sources": online_sources,
                "online_ratio": online_ratio,
                "avg_response_time_ms": avg_response_time,
                "rate_limited_count": rate_limited_count,
                "last_updated": last_updated.isoformat() if last_updated else None,
                "status": status
            })

        return category_stats

    except Exception as e:
        logger.error(f"Error getting categories: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get categories: {str(e)}")


# ============================================================================
# GET /api/providers - Provider List with Filters
# ============================================================================

@router.get("/providers")
async def get_providers(
    category: Optional[str] = Query(None, description="Filter by category"),
    status: Optional[str] = Query(None, description="Filter by status (online/degraded/offline)"),
    search: Optional[str] = Query(None, description="Search by provider name")
):
    """
    Get list of providers with optional filtering

    Args:
        category: Filter by provider category
        status: Filter by provider status
        search: Search by provider name

    Returns:
        List of providers with detailed information
    """
    try:
        # Get providers from database
        providers = db_manager.get_all_providers(category=category)

        result = []

        for provider in providers:
            # Apply search filter
            if search and search.lower() not in provider.name.lower():
                continue

            # Get recent connection attempts
            attempts = db_manager.get_connection_attempts(
                provider_id=provider.id,
                hours=1,
                limit=10
            )

            # Determine provider status
            provider_status = "offline"
            response_time_ms = 0
            last_fetch = None

            if attempts:
                recent = attempts[0]
                last_fetch = recent.timestamp

                if recent.status == "success":
                    if recent.response_time_ms and recent.response_time_ms < 2000:
                        provider_status = "online"
                    else:
                        provider_status = "degraded"
                    response_time_ms = recent.response_time_ms or 0
                elif recent.status == "rate_limited":
                    provider_status = "degraded"
                else:
                    provider_status = "offline"

            # Apply status filter
            if status and provider_status != status:
                continue

            # Get rate limit info
            rate_limit_status = rate_limiter.get_status(provider.name)
            rate_limit = None
            if rate_limit_status:
                rate_limit = f"{rate_limit_status['current_usage']}/{rate_limit_status['limit_value']} {rate_limit_status['limit_type']}"
            elif provider.rate_limit_type and provider.rate_limit_value:
                rate_limit = f"0/{provider.rate_limit_value} {provider.rate_limit_type}"

            # Get schedule config
            schedule_config = db_manager.get_schedule_config(provider.id)

            result.append({
                "id": provider.id,
                "name": provider.name,
                "category": provider.category,
                "status": provider_status,
                "response_time_ms": response_time_ms,
                "rate_limit": rate_limit,
                "last_fetch": last_fetch.isoformat() if last_fetch else None,
                "has_key": provider.requires_key,
                "endpoints": provider.endpoint_url
            })

        return result

    except Exception as e:
        logger.error(f"Error getting providers: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get providers: {str(e)}")


# ============================================================================
# GET /api/logs - Query Logs with Pagination
# ============================================================================

@router.get("/logs")
async def get_logs(
    from_time: Optional[str] = Query(None, alias="from", description="Start time (ISO format)"),
    to_time: Optional[str] = Query(None, alias="to", description="End time (ISO format)"),
    provider: Optional[str] = Query(None, description="Filter by provider name"),
    status: Optional[str] = Query(None, description="Filter by status"),
    page: int = Query(1, ge=1, description="Page number"),
    per_page: int = Query(50, ge=1, le=500, description="Items per page")
):
    """
    Get connection attempt logs with filtering and pagination

    Args:
        from_time: Start time filter
        to_time: End time filter
        provider: Provider name filter
        status: Status filter
        page: Page number
        per_page: Items per page

    Returns:
        Paginated log entries with metadata
    """
    try:
        # Calculate time range
        if from_time:
            from_dt = datetime.fromisoformat(from_time.replace('Z', '+00:00'))
        else:
            from_dt = datetime.utcnow() - timedelta(hours=24)

        if to_time:
            to_dt = datetime.fromisoformat(to_time.replace('Z', '+00:00'))
        else:
            to_dt = datetime.utcnow()

        hours = (to_dt - from_dt).total_seconds() / 3600

        # Get provider ID if filter specified
        provider_id = None
        if provider:
            prov = db_manager.get_provider(name=provider)
            if prov:
                provider_id = prov.id

        # Get all matching logs (no limit for now)
        all_logs = db_manager.get_connection_attempts(
            provider_id=provider_id,
            status=status,
            hours=int(hours) + 1,
            limit=10000  # Large limit to get all
        )

        # Filter by time range
        filtered_logs = [
            log for log in all_logs
            if from_dt <= log.timestamp <= to_dt
        ]

        # Calculate pagination
        total = len(filtered_logs)
        total_pages = (total + per_page - 1) // per_page
        start_idx = (page - 1) * per_page
        end_idx = start_idx + per_page

        # Get page of logs
        page_logs = filtered_logs[start_idx:end_idx]

        # Format logs for response
        logs = []
        for log in page_logs:
            # Get provider name
            prov = db_manager.get_provider(provider_id=log.provider_id)
            provider_name = prov.name if prov else "Unknown"

            logs.append({
                "id": log.id,
                "timestamp": log.timestamp.isoformat(),
                "provider": provider_name,
                "endpoint": log.endpoint,
                "status": log.status,
                "response_time_ms": log.response_time_ms,
                "http_status_code": log.http_status_code,
                "error_type": log.error_type,
                "error_message": log.error_message,
                "retry_count": log.retry_count,
                "retry_result": log.retry_result
            })

        return {
            "logs": logs,
            "pagination": {
                "page": page,
                "per_page": per_page,
                "total": total,
                "total_pages": total_pages,
                "has_next": page < total_pages,
                "has_prev": page > 1
            }
        }

    except Exception as e:
        logger.error(f"Error getting logs: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get logs: {str(e)}")


# ============================================================================
# GET /api/schedule - Schedule Status
# ============================================================================

@router.get("/schedule")
async def get_schedule():
    """
    Get schedule status for all providers

    Returns:
        List of schedule information for each provider
    """
    try:
        configs = db_manager.get_all_schedule_configs(enabled_only=False)

        schedule_list = []

        for config in configs:
            # Get provider info
            provider = db_manager.get_provider(provider_id=config.provider_id)
            if not provider:
                continue

            # Calculate on-time percentage
            total_runs = config.on_time_count + config.late_count
            on_time_percentage = round((config.on_time_count / total_runs * 100), 1) if total_runs > 0 else 100.0

            # Get today's runs
            compliance_today = db_manager.get_schedule_compliance(
                provider_id=config.provider_id,
                hours=24
            )

            total_runs_today = len(compliance_today)
            successful_runs = sum(1 for c in compliance_today if c.on_time)
            skipped_runs = config.skip_count

            # Determine status
            if not config.enabled:
                status = "disabled"
            elif on_time_percentage >= 95:
                status = "on_schedule"
            elif on_time_percentage >= 80:
                status = "acceptable"
            else:
                status = "behind_schedule"

            schedule_list.append({
                "provider": provider.name,
                "category": provider.category,
                "schedule": config.schedule_interval,
                "last_run": config.last_run.isoformat() if config.last_run else None,
                "next_run": config.next_run.isoformat() if config.next_run else None,
                "on_time_percentage": on_time_percentage,
                "status": status,
                "total_runs_today": total_runs_today,
                "successful_runs": successful_runs,
                "skipped_runs": skipped_runs
            })

        return schedule_list

    except Exception as e:
        logger.error(f"Error getting schedule: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get schedule: {str(e)}")


# ============================================================================
# POST /api/schedule/trigger - Trigger Immediate Check
# ============================================================================

@router.post("/schedule/trigger")
async def trigger_check(request: TriggerCheckRequest):
    """
    Trigger immediate health check for a provider

    Args:
        request: Request containing provider name

    Returns:
        Health check result
    """
    try:
        # Verify provider exists
        provider = db_manager.get_provider(name=request.provider)
        if not provider:
            raise HTTPException(status_code=404, detail=f"Provider not found: {request.provider}")

        # Create health checker and run check
        checker = HealthChecker()
        result = await checker.check_provider(request.provider)
        await checker.close()

        if not result:
            raise HTTPException(status_code=500, detail=f"Health check failed for {request.provider}")

        return {
            "provider": result.provider_name,
            "status": result.status.value,
            "response_time_ms": result.response_time,
            "timestamp": datetime.fromtimestamp(result.timestamp).isoformat(),
            "error_message": result.error_message,
            "triggered_at": datetime.utcnow().isoformat()
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error triggering check: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to trigger check: {str(e)}")


# ============================================================================
# GET /api/freshness - Data Freshness
# ============================================================================

@router.get("/freshness")
async def get_freshness():
    """
    Get data freshness information for all providers

    Returns:
        List of data freshness metrics
    """
    try:
        providers = db_manager.get_all_providers()
        freshness_list = []

        for provider in providers:
            # Get most recent data collection
            collections = db_manager.get_data_collections(
                provider_id=provider.id,
                hours=24,
                limit=1
            )

            if not collections:
                continue

            collection = collections[0]

            # Calculate staleness
            now = datetime.utcnow()
            fetch_age_minutes = (now - collection.actual_fetch_time).total_seconds() / 60

            # Determine TTL based on category
            ttl_minutes = 5  # Default
            if provider.category == "market_data":
                ttl_minutes = 1
            elif provider.category == "blockchain_explorers":
                ttl_minutes = 5
            elif provider.category == "news":
                ttl_minutes = 15

            # Determine status
            if fetch_age_minutes <= ttl_minutes:
                status = "fresh"
            elif fetch_age_minutes <= ttl_minutes * 2:
                status = "stale"
            else:
                status = "expired"

            freshness_list.append({
                "provider": provider.name,
                "category": provider.category,
                "fetch_time": collection.actual_fetch_time.isoformat(),
                "data_timestamp": collection.data_timestamp.isoformat() if collection.data_timestamp else None,
                "staleness_minutes": round(fetch_age_minutes, 2),
                "ttl_minutes": ttl_minutes,
                "status": status
            })

        return freshness_list

    except Exception as e:
        logger.error(f"Error getting freshness: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get freshness: {str(e)}")


# ============================================================================
# GET /api/failures - Failure Analysis
# ============================================================================

@router.get("/failures")
async def get_failures():
    """
    Get comprehensive failure analysis

    Returns:
        Failure analysis with error distribution and recommendations
    """
    try:
        # Get failure analysis from database
        analysis = db_manager.get_failure_analysis(hours=24)

        # Get recent failures
        recent_failures = db_manager.get_failure_logs(hours=1, limit=10)

        recent_list = []
        for failure in recent_failures:
            provider = db_manager.get_provider(provider_id=failure.provider_id)
            recent_list.append({
                "timestamp": failure.timestamp.isoformat(),
                "provider": provider.name if provider else "Unknown",
                "error_type": failure.error_type,
                "error_message": failure.error_message,
                "http_status": failure.http_status,
                "retry_attempted": failure.retry_attempted,
                "retry_result": failure.retry_result
            })

        # Generate remediation suggestions
        remediation_suggestions = []

        error_type_distribution = analysis.get('failures_by_error_type', [])
        for error_stat in error_type_distribution:
            error_type = error_stat['error_type']
            count = error_stat['count']

            if error_type == 'timeout' and count > 5:
                remediation_suggestions.append({
                    "issue": "High timeout rate",
                    "suggestion": "Increase timeout values or check network connectivity",
                    "priority": "high"
                })
            elif error_type == 'rate_limit' and count > 3:
                remediation_suggestions.append({
                    "issue": "Rate limit errors",
                    "suggestion": "Implement request throttling or add additional API keys",
                    "priority": "medium"
                })
            elif error_type == 'auth_error' and count > 0:
                remediation_suggestions.append({
                    "issue": "Authentication failures",
                    "suggestion": "Verify API keys are valid and not expired",
                    "priority": "critical"
                })

        return {
            "error_type_distribution": error_type_distribution,
            "top_failing_providers": analysis.get('top_failing_providers', []),
            "recent_failures": recent_list,
            "remediation_suggestions": remediation_suggestions
        }

    except Exception as e:
        logger.error(f"Error getting failures: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get failures: {str(e)}")


# ============================================================================
# GET /api/rate-limits - Rate Limit Status
# ============================================================================

@router.get("/rate-limits")
async def get_rate_limits():
    """
    Get rate limit status for all providers

    Returns:
        List of rate limit information
    """
    try:
        statuses = rate_limiter.get_all_statuses()

        rate_limit_list = []

        for provider_name, status_info in statuses.items():
            if status_info:
                rate_limit_list.append({
                    "provider": status_info['provider'],
                    "limit_type": status_info['limit_type'],
                    "limit_value": status_info['limit_value'],
                    "current_usage": status_info['current_usage'],
                    "percentage": status_info['percentage'],
                    "reset_time": status_info['reset_time'],
                    "reset_in_seconds": status_info['reset_in_seconds'],
                    "status": status_info['status']
                })

        # Add providers with configured limits but no tracking yet
        providers = db_manager.get_all_providers()
        tracked_providers = {rl['provider'] for rl in rate_limit_list}

        for provider in providers:
            if provider.name not in tracked_providers and provider.rate_limit_type and provider.rate_limit_value:
                rate_limit_list.append({
                    "provider": provider.name,
                    "limit_type": provider.rate_limit_type,
                    "limit_value": provider.rate_limit_value,
                    "current_usage": 0,
                    "percentage": 0.0,
                    "reset_time": (datetime.utcnow() + timedelta(hours=1)).isoformat(),
                    "reset_in_seconds": 3600,
                    "status": "ok"
                })

        return rate_limit_list

    except Exception as e:
        logger.error(f"Error getting rate limits: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get rate limits: {str(e)}")


# ============================================================================
# GET /api/config/keys - API Keys Status
# ============================================================================

@router.get("/config/keys")
async def get_api_keys():
    """
    Get API key status for all providers

    Returns:
        List of API key information (masked)
    """
    try:
        providers = db_manager.get_all_providers()

        keys_list = []

        for provider in providers:
            if not provider.requires_key:
                continue

            # Determine key status
            if provider.api_key_masked:
                key_status = "configured"
            else:
                key_status = "missing"

            # Get usage quota from rate limits if available
            rate_status = rate_limiter.get_status(provider.name)
            usage_quota_remaining = None
            if rate_status:
                percentage_used = rate_status['percentage']
                usage_quota_remaining = f"{100 - percentage_used:.1f}%"

            keys_list.append({
                "provider": provider.name,
                "key_masked": provider.api_key_masked or "***NOT_SET***",
                "created_at": provider.created_at.isoformat(),
                "expires_at": None,  # Not tracked in current schema
                "status": key_status,
                "usage_quota_remaining": usage_quota_remaining
            })

        return keys_list

    except Exception as e:
        logger.error(f"Error getting API keys: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get API keys: {str(e)}")


# ============================================================================
# POST /api/config/keys/test - Test API Key
# ============================================================================

@router.post("/config/keys/test")
async def test_api_key(request: TestKeyRequest):
    """
    Test an API key by performing a health check

    Args:
        request: Request containing provider name

    Returns:
        Test result
    """
    try:
        # Verify provider exists and requires key
        provider = db_manager.get_provider(name=request.provider)
        if not provider:
            raise HTTPException(status_code=404, detail=f"Provider not found: {request.provider}")

        if not provider.requires_key:
            raise HTTPException(status_code=400, detail=f"Provider {request.provider} does not require an API key")

        if not provider.api_key_masked:
            raise HTTPException(status_code=400, detail=f"No API key configured for {request.provider}")

        # Perform health check to test key
        checker = HealthChecker()
        result = await checker.check_provider(request.provider)
        await checker.close()

        if not result:
            raise HTTPException(status_code=500, detail=f"Failed to test API key for {request.provider}")

        # Determine if key is valid based on result
        key_valid = result.status.value == "online" or result.status.value == "degraded"

        # Check for auth-specific errors
        if result.error_message and ('auth' in result.error_message.lower() or 'key' in result.error_message.lower() or '401' in result.error_message or '403' in result.error_message):
            key_valid = False

        return {
            "provider": request.provider,
            "key_valid": key_valid,
            "test_timestamp": datetime.utcnow().isoformat(),
            "response_time_ms": result.response_time,
            "status_code": result.status_code,
            "error_message": result.error_message,
            "test_endpoint": result.endpoint_tested
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error testing API key: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to test API key: {str(e)}")


# ============================================================================
# GET /api/charts/health-history - Health History for Charts
# ============================================================================

@router.get("/charts/health-history")
async def get_health_history(
    hours: int = Query(24, ge=1, le=168, description="Hours of history to retrieve")
):
    """
    Get health history data for charts

    Args:
        hours: Number of hours of history to retrieve

    Returns:
        Time series data for health metrics
    """
    try:
        # Get system metrics history
        metrics = db_manager.get_system_metrics(hours=hours)

        if not metrics:
            return {
                "timestamps": [],
                "success_rate": [],
                "avg_response_time": []
            }

        # Sort by timestamp
        metrics.sort(key=lambda x: x.timestamp)

        timestamps = []
        success_rates = []
        avg_response_times = []

        for metric in metrics:
            timestamps.append(metric.timestamp.isoformat())

            # Calculate success rate
            total = metric.online_count + metric.degraded_count + metric.offline_count
            success_rate = round((metric.online_count / total * 100), 2) if total > 0 else 0
            success_rates.append(success_rate)

            avg_response_times.append(round(metric.avg_response_time_ms, 2))

        return {
            "timestamps": timestamps,
            "success_rate": success_rates,
            "avg_response_time": avg_response_times
        }

    except Exception as e:
        logger.error(f"Error getting health history: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get health history: {str(e)}")


# ============================================================================
# GET /api/charts/compliance - Compliance History for Charts
# ============================================================================

@router.get("/charts/compliance")
async def get_compliance_history(
    days: int = Query(7, ge=1, le=30, description="Days of history to retrieve")
):
    """
    Get schedule compliance history for charts

    Args:
        days: Number of days of history to retrieve

    Returns:
        Time series data for compliance metrics
    """
    try:
        # Get all providers with schedule configs
        configs = db_manager.get_all_schedule_configs(enabled_only=True)

        if not configs:
            return {
                "dates": [],
                "compliance_percentage": []
            }

        # Generate date range
        end_date = datetime.utcnow().date()
        dates = []
        compliance_percentages = []

        for day_offset in range(days - 1, -1, -1):
            current_date = end_date - timedelta(days=day_offset)
            dates.append(current_date.isoformat())

            # Calculate compliance for this day
            day_start = datetime.combine(current_date, datetime.min.time())
            day_end = datetime.combine(current_date, datetime.max.time())

            total_checks = 0
            on_time_checks = 0

            for config in configs:
                compliance_records = db_manager.get_schedule_compliance(
                    provider_id=config.provider_id,
                    hours=24
                )

                # Filter for current date
                day_records = [
                    r for r in compliance_records
                    if day_start <= r.timestamp <= day_end
                ]

                total_checks += len(day_records)
                on_time_checks += sum(1 for r in day_records if r.on_time)

            # Calculate percentage
            compliance_pct = round((on_time_checks / total_checks * 100), 2) if total_checks > 0 else 100.0
            compliance_percentages.append(compliance_pct)

        return {
            "dates": dates,
            "compliance_percentage": compliance_percentages
        }

    except Exception as e:
        logger.error(f"Error getting compliance history: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get compliance history: {str(e)}")


# ============================================================================
# GET /api/charts/rate-limit-history - Rate Limit History for Charts
# ============================================================================

@router.get("/charts/rate-limit-history")
async def get_rate_limit_history(
    hours: int = Query(24, ge=1, le=168, description="Hours of history (1-168)"),
    providers: Optional[str] = Query(None, description="Comma-separated provider names (max 5)")
):
    """
    Get rate limit usage history for chart visualization

    Args:
        hours: Number of hours of history to retrieve (1-168, default 24)
        providers: Comma-separated list of provider names (max 5, default: top 5 by limit)

    Returns:
        List of series objects with rate limit history per provider

    Response Schema:
        [
            {
                "provider": "coingecko",
                "hours": 24,
                "series": [
                    {"t": "2025-11-10T13:00:00Z", "pct": 42.5},
                    ...
                ],
                "meta": {
                    "limit_type": "per_minute",
                    "limit_value": 30
                }
            }
        ]
    """
    try:
        # Security: Cap hours to prevent abuse
        hours = min(max(hours, 1), 168)

        # Get all providers
        all_providers = db_manager.get_all_providers()

        # Security: Validate and filter provider names
        valid_provider_names = {p.name for p in all_providers}
        selected_providers = []

        if providers:
            # Parse and validate provider list
            provider_list = [p.strip() for p in providers.split(',') if p.strip()]

            # Security: Limit to max 5 providers
            provider_list = provider_list[:5]

            # Security: Enforce allow-list (only valid provider names)
            for prov_name in provider_list:
                if prov_name not in valid_provider_names:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid provider name: {prov_name}. Must be one of: {', '.join(sorted(valid_provider_names))}"
                    )
                selected_providers.append(prov_name)
        else:
            # Default: Select up to 5 providers with rate limits
            providers_with_limits = [
                p for p in all_providers
                if p.rate_limit_type and p.rate_limit_value
            ][:5]
            selected_providers = [p.name for p in providers_with_limits]

        if not selected_providers:
            return []

        # Build time series for each provider
        result = []
        now = datetime.utcnow()

        for provider_name in selected_providers:
            # Get provider object
            provider = db_manager.get_provider(name=provider_name)
            if not provider:
                continue

            # Get rate limit usage records
            usage_records = db_manager.get_rate_limit_usage(
                provider_id=provider.id,
                hours=hours
            )

            # Build hourly time series
            points = []
            hour_map = {}  # timestamp -> usage record

            # Map records to hourly buckets
            for record in usage_records:
                # Round to hour bucket
                hour_bucket = record.timestamp.replace(minute=0, second=0, microsecond=0)
                # Keep most recent record per hour
                if hour_bucket not in hour_map or record.timestamp > hour_map[hour_bucket].timestamp:
                    hour_map[hour_bucket] = record

            # Generate points for each hour (fill gaps with zeros)
            for hour_offset in range(hours):
                hour_time = now - timedelta(hours=hours - hour_offset - 1)
                hour_bucket = hour_time.replace(minute=0, second=0, microsecond=0)

                if hour_bucket in hour_map:
                    record = hour_map[hour_bucket]
                    pct = round(record.percentage, 2)
                else:
                    pct = 0.0

                points.append({
                    "t": hour_bucket.isoformat() + "Z",
                    "pct": pct
                })

            # Get rate limit metadata
            meta = {
                "limit_type": provider.rate_limit_type,
                "limit_value": provider.rate_limit_value
            }

            result.append({
                "provider": provider_name,
                "hours": hours,
                "series": points,
                "meta": meta
            })

        logger.info(f"Rate limit history: {len(result)} providers, {hours}h")
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting rate limit history: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get rate limit history: {str(e)}")


# ============================================================================
# GET /api/charts/freshness-history - Data Freshness History for Charts
# ============================================================================

@router.get("/charts/freshness-history")
async def get_freshness_history(
    hours: int = Query(24, ge=1, le=168, description="Hours of history (1-168)"),
    providers: Optional[str] = Query(None, description="Comma-separated provider names (max 5)")
):
    """
    Get data freshness/staleness history for chart visualization

    Args:
        hours: Number of hours of history to retrieve (1-168, default 24)
        providers: Comma-separated list of provider names (max 5, default: top 5 by activity)

    Returns:
        List of series objects with freshness history per provider

    Response Schema:
        [
            {
                "provider": "coingecko",
                "hours": 24,
                "series": [
                    {
                        "t": "2025-11-10T13:00:00Z",
                        "staleness_min": 7.2,
                        "ttl_min": 15,
                        "status": "fresh"
                    },
                    ...
                ],
                "meta": {
                    "category": "market_data",
                    "default_ttl": 1
                }
            }
        ]
    """
    try:
        # Security: Cap hours to prevent abuse
        hours = min(max(hours, 1), 168)

        # Get all providers
        all_providers = db_manager.get_all_providers()

        # Security: Validate and filter provider names
        valid_provider_names = {p.name for p in all_providers}
        selected_providers = []

        if providers:
            # Parse and validate provider list
            provider_list = [p.strip() for p in providers.split(',') if p.strip()]

            # Security: Limit to max 5 providers
            provider_list = provider_list[:5]

            # Security: Enforce allow-list (only valid provider names)
            for prov_name in provider_list:
                if prov_name not in valid_provider_names:
                    raise HTTPException(
                        status_code=400,
                        detail=f"Invalid provider name: {prov_name}. Must be one of: {', '.join(sorted(valid_provider_names))}"
                    )
                selected_providers.append(prov_name)
        else:
            # Default: Select up to 5 most active providers
            selected_providers = [p.name for p in all_providers[:5]]

        if not selected_providers:
            return []

        # Build time series for each provider
        result = []
        now = datetime.utcnow()

        for provider_name in selected_providers:
            # Get provider object
            provider = db_manager.get_provider(name=provider_name)
            if not provider:
                continue

            # Get data collections
            collections = db_manager.get_data_collections(
                provider_id=provider.id,
                hours=hours
            )

            # Determine TTL based on category
            ttl_minutes = 5  # Default
            if provider.category == "market_data":
                ttl_minutes = 1
            elif provider.category == "blockchain_explorers":
                ttl_minutes = 5
            elif provider.category == "news":
                ttl_minutes = 15
            elif provider.category == "defi":
                ttl_minutes = 10

            # Build hourly time series
            points = []
            hour_map = {}  # timestamp -> collection record

            # Map records to hourly buckets (keep most recent per hour)
            for collection in collections:
                hour_bucket = collection.actual_fetch_time.replace(minute=0, second=0, microsecond=0)
                if hour_bucket not in hour_map or collection.actual_fetch_time > hour_map[hour_bucket].actual_fetch_time:
                    hour_map[hour_bucket] = collection

            # Generate points for each hour
            for hour_offset in range(hours):
                hour_time = now - timedelta(hours=hours - hour_offset - 1)
                hour_bucket = hour_time.replace(minute=0, second=0, microsecond=0)

                if hour_bucket in hour_map:
                    collection = hour_map[hour_bucket]

                    # Calculate staleness (age of data at time of fetch)
                    staleness_min = collection.staleness_minutes or 0.0

                    # Determine status
                    if staleness_min <= ttl_minutes:
                        status = "fresh"
                    elif staleness_min <= ttl_minutes * 2:
                        status = "aging"
                    else:
                        status = "stale"

                    points.append({
                        "t": hour_bucket.isoformat() + "Z",
                        "staleness_min": round(staleness_min, 2),
                        "ttl_min": ttl_minutes,
                        "status": status
                    })
                else:
                    # No data for this hour - mark as stale
                    points.append({
                        "t": hour_bucket.isoformat() + "Z",
                        "staleness_min": 999.0,
                        "ttl_min": ttl_minutes,
                        "status": "stale"
                    })

            # Get metadata
            meta = {
                "category": provider.category,
                "default_ttl": ttl_minutes
            }

            result.append({
                "provider": provider_name,
                "hours": hours,
                "series": points,
                "meta": meta
            })

        logger.info(f"Freshness history: {len(result)} providers, {hours}h")
        return result

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting freshness history: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get freshness history: {str(e)}")


# ============================================================================
# Health Check Endpoint
# ============================================================================

@router.get("/health")
async def api_health():
    """
    API health check endpoint

    Returns:
        API health status
    """
    try:
        # Check database connection
        db_health = db_manager.health_check()

        return {
            "status": "healthy" if db_health['status'] == 'healthy' else "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "database": db_health['status'],
            "version": "1.0.0"
        }
    except Exception as e:
        logger.error(f"Health check failed: {e}", exc_info=True)
        return {
            "status": "unhealthy",
            "timestamp": datetime.utcnow().isoformat(),
            "error": str(e),
            "version": "1.0.0"
        }


# ============================================================================
# Initialize Logger
# ============================================================================

logger.info("API endpoints module loaded successfully")
