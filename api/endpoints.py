"""
REST API Endpoints for Crypto API Monitor
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from database.db import get_db
from database.models import Provider, ConnectionAttempt, DataCollection, RateLimitUsage, ScheduleConfig, StatusEnum
from typing import List, Optional
from datetime import datetime, timedelta
from pydantic import BaseModel

router = APIRouter()


# Response Models
class StatusResponse(BaseModel):
    total_apis: int
    online: int
    degraded: int
    offline: int
    avg_response_time_ms: int
    last_update: datetime
    system_health: str


class CategoryResponse(BaseModel):
    name: str
    total_sources: int
    online_sources: int
    online_ratio: float
    avg_response_time_ms: int
    rate_limited_count: int
    last_updated: datetime
    status: str


# Endpoints
@router.get("/api/status", response_model=StatusResponse)
async def get_status(db: Session = Depends(get_db)):
    """Get overall system status"""
    providers = db.query(Provider).all()
    total = len(providers)
    online = sum(1 for p in providers if p.status.value == "online")
    degraded = sum(1 for p in providers if p.status.value == "degraded")
    offline = sum(1 for p in providers if p.status.value == "offline")

    avg_response = db.query(func.avg(Provider.last_response_time_ms)).scalar() or 0

    return StatusResponse(
        total_apis=total,
        online=online,
        degraded=degraded,
        offline=offline,
        avg_response_time_ms=int(avg_response),
        last_update=datetime.utcnow(),
        system_health="healthy" if (online / total > 0.8 if total > 0 else True) else "degraded"
    )


@router.get("/api/categories", response_model=List[CategoryResponse])
async def get_categories(db: Session = Depends(get_db)):
    """Get category statistics"""
    categories = db.query(Provider.category).distinct().all()
    result = []

    for (category,) in categories:
        providers = db.query(Provider).filter(Provider.category == category).all()
        total = len(providers)
        online = sum(1 for p in providers if p.status.value == "online")
        avg_response = sum(p.last_response_time_ms or 0 for p in providers) / total if total > 0 else 0
        rate_limited = sum(1 for p in providers if p.last_response_time_ms and p.last_response_time_ms > 5000)

        result.append(CategoryResponse(
            name=category.replace("_", " ").title(),
            total_sources=total,
            online_sources=online,
            online_ratio=online / total if total > 0 else 0,
            avg_response_time_ms=int(avg_response),
            rate_limited_count=rate_limited,
            last_updated=datetime.utcnow(),
            status="online" if (online / total > 0.8 if total > 0 else True) else "degraded"
        ))

    return result


@router.get("/api/providers")
async def get_providers(
    category: Optional[str] = None,
    status: Optional[str] = None,
    search: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """Get all providers with optional filters"""
    query = db.query(Provider)

    if category:
        query = query.filter(Provider.category == category)
    if status:
        query = query.filter(Provider.status == status)
    if search:
        query = query.filter(Provider.name.ilike(f"%{search}%"))

    providers = query.all()

    return [
        {
            "id": p.id,
            "name": p.name,
            "category": p.category,
            "status": p.status.value,
            "response_time_ms": p.last_response_time_ms,
            "rate_limit": {
                "used": 0,  # TODO: Calculate from rate_limit_usage
                "total": p.rate_limit_value,
                "period": p.rate_limit_type,
                "percentage": 0
            },
            "last_fetch": p.last_check_at.isoformat() if p.last_check_at else None,
            "has_key": p.requires_key
        }
        for p in providers
    ]


@router.get("/api/logs")
async def get_logs(
    from_date: Optional[datetime] = None,
    to_date: Optional[datetime] = None,
    provider: Optional[str] = None,
    status: Optional[str] = None,
    page: int = Query(1, ge=1),
    per_page: int = Query(50, ge=1, le=100),
    db: Session = Depends(get_db)
):
    """Get connection logs with pagination"""
    query = db.query(ConnectionAttempt).join(Provider)

    if from_date:
        query = query.filter(ConnectionAttempt.timestamp >= from_date)
    if to_date:
        query = query.filter(ConnectionAttempt.timestamp <= to_date)
    if provider:
        query = query.filter(Provider.name == provider)
    if status:
        query = query.filter(ConnectionAttempt.status == status)

    total = query.count()
    logs = query.order_by(desc(ConnectionAttempt.timestamp)).offset((page - 1) * per_page).limit(per_page).all()

    return {
        "total": total,
        "page": page,
        "per_page": per_page,
        "logs": [
            {
                "timestamp": log.timestamp.isoformat(),
                "provider": log.provider.name,
                "endpoint": log.endpoint,
                "status": log.status.value,
                "response_time_ms": log.response_time_ms,
                "http_code": log.http_status_code,
                "error_message": log.error_message
            }
            for log in logs
        ]
    }


@router.get("/api/schedule")
async def get_schedule(db: Session = Depends(get_db)):
    """Get schedule configuration"""
    schedules = db.query(ScheduleConfig).join(Provider).all()

    return [
        {
            "provider": s.provider.name,
            "category": s.provider.category,
            "schedule": s.schedule_interval,
            "last_run": s.last_run.isoformat() if s.last_run else None,
            "next_run": s.next_run.isoformat() if s.next_run else None,
            "on_time_percentage": (s.successful_runs / s.total_runs * 100) if s.total_runs > 0 else 100,
            "status": "active" if s.enabled else "paused"
        }
        for s in schedules
    ]


@router.post("/api/schedule/trigger")
async def trigger_schedule(provider: str, db: Session = Depends(get_db)):
    """Manually trigger a scheduled task"""
    # TODO: Implement manual trigger
    return {"status": "triggered", "provider": provider}


@router.get("/api/freshness")
async def get_freshness(db: Session = Depends(get_db)):
    """Get data freshness status"""
    collections = db.query(DataCollection).join(Provider).order_by(desc(DataCollection.actual_fetch_time)).limit(100).all()

    return [
        {
            "provider": c.provider.name,
            "category": c.category,
            "fetch_time": c.actual_fetch_time.isoformat(),
            "data_timestamp": c.data_timestamp.isoformat() if c.data_timestamp else None,
            "staleness_minutes": c.staleness_minutes,
            "ttl_minutes": 5,  # TODO: Get from provider config
            "status": "fresh" if (c.staleness_minutes and c.staleness_minutes < 5) else "stale"
        }
        for c in collections
    ]


@router.get("/api/failures")
async def get_failures(days: int = Query(7, ge=1, le=30), db: Session = Depends(get_db)):
    """Get failure analysis"""
    since = datetime.utcnow() - timedelta(days=days)

    failures = db.query(ConnectionAttempt).filter(
        ConnectionAttempt.timestamp >= since,
        ConnectionAttempt.status != StatusEnum.SUCCESS
    ).all()

    # Error type distribution
    error_types = {}
    for f in failures:
        error_types[f.error_type or "unknown"] = error_types.get(f.error_type or "unknown", 0) + 1

    # Top failing providers
    provider_failures = {}
    for f in failures:
        provider_failures[f.provider.name] = provider_failures.get(f.provider.name, 0) + 1

    top_failing = sorted(provider_failures.items(), key=lambda x: x[1], reverse=True)[:10]

    return {
        "error_type_distribution": error_types,
        "top_failing_providers": [{"provider": p, "failure_count": c} for p, c in top_failing],
        "recent_failures": [
            {
                "timestamp": f.timestamp.isoformat(),
                "provider": f.provider.name,
                "error_type": f.error_type,
                "error_message": f.error_message,
                "retry_attempted": f.retry_count > 0,
                "retry_result": f.retry_result
            }
            for f in failures[:20]
        ],
        "remediation_suggestions": []  # TODO: Generate suggestions
    }


@router.get("/api/rate-limits")
async def get_rate_limits(db: Session = Depends(get_db)):
    """Get rate limit status"""
    providers = db.query(Provider).all()

    return [
        {
            "provider": p.name,
            "limit_type": p.rate_limit_type,
            "limit_value": p.rate_limit_value,
            "current_usage": 0,  # TODO: Implement rate limit tracking
            "percentage": 0,
            "status": "normal"
        }
        for p in providers
    ]


@router.get("/api/config/keys")
async def get_api_keys(db: Session = Depends(get_db)):
    """Get API key configuration"""
    providers = db.query(Provider).filter(Provider.requires_key == True).all()

    return [
        {
            "provider": p.name,
            "key_masked": p.api_key_masked,
            "expires_at": None,  # TODO: Add expiration tracking
            "status": "active" if p.status.value == "online" else "inactive"
        }
        for p in providers
    ]


@router.get("/api/charts/health-history")
async def get_health_history(hours: int = Query(24, ge=1, le=168), db: Session = Depends(get_db)):
    """Get health history for charts"""
    since = datetime.utcnow() - timedelta(hours=hours)

    attempts = db.query(ConnectionAttempt).filter(
        ConnectionAttempt.timestamp >= since
    ).order_by(ConnectionAttempt.timestamp).all()

    # Group by hour
    hourly_data = {}
    for attempt in attempts:
        hour_key = attempt.timestamp.replace(minute=0, second=0, microsecond=0)
        if hour_key not in hourly_data:
            hourly_data[hour_key] = {"total": 0, "success": 0}

        hourly_data[hour_key]["total"] += 1
        if attempt.status == StatusEnum.SUCCESS:
            hourly_data[hour_key]["success"] += 1

    timestamps = sorted(hourly_data.keys())
    success_rates = [
        (hourly_data[ts]["success"] / hourly_data[ts]["total"] * 100) if hourly_data[ts]["total"] > 0 else 0
        for ts in timestamps
    ]

    return {
        "timestamps": [ts.isoformat() for ts in timestamps],
        "success_rate": success_rates
    }


@router.get("/api/charts/compliance")
async def get_compliance_chart(days: int = Query(7, ge=1, le=30), db: Session = Depends(get_db)):
    """Get compliance chart data"""
    since = datetime.utcnow() - timedelta(days=days)

    attempts = db.query(ConnectionAttempt).filter(
        ConnectionAttempt.timestamp >= since
    ).all()

    # Group by day
    daily_data = {}
    for attempt in attempts:
        day_key = attempt.timestamp.date()
        if day_key not in daily_data:
            daily_data[day_key] = {"total": 0, "success": 0}

        daily_data[day_key]["total"] += 1
        if attempt.status == StatusEnum.SUCCESS:
            daily_data[day_key]["success"] += 1

    dates = sorted(daily_data.keys())
    compliance_percentages = [
        (daily_data[date]["success"] / daily_data[date]["total"] * 100) if daily_data[date]["total"] > 0 else 0
        for date in dates
    ]

    return {
        "dates": [date.isoformat() for date in dates],
        "compliance_percentage": compliance_percentages
    }
