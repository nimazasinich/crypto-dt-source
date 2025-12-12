#!/usr/bin/env python3
"""
Data Sources Database Model
مدل دیتابیس برای مدیریت منابع داده

این مدل برای ذخیره و مدیریت منابع داده استفاده می‌شود.
شامل اطلاعات منبع، وضعیت فعال/غیرفعال، و آمار استفاده.
"""

from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, Text, Enum, Index
from sqlalchemy.orm import relationship
from datetime import datetime
import enum
from typing import Dict, Any, List, Optional
import json

# Use the existing Base from models.py
try:
    from database.models import Base
except ImportError:
    from sqlalchemy.ext.declarative import declarative_base
    Base = declarative_base()


class DataSourceType(enum.Enum):
    """نوع منبع داده"""
    MARKET = "market"
    NEWS = "news"
    SENTIMENT = "sentiment"
    SOCIAL = "social"
    ONCHAIN = "onchain"
    DEFI = "defi"
    HISTORICAL = "historical"
    TECHNICAL = "technical"
    AGGREGATED = "aggregated"


class DataSourceStatus(enum.Enum):
    """وضعیت منبع داده"""
    ACTIVE = "active"
    INACTIVE = "inactive"
    RATE_LIMITED = "rate_limited"
    ERROR = "error"
    MAINTENANCE = "maintenance"


class CollectionInterval(enum.Enum):
    """بازه جمع‌آوری داده"""
    REALTIME = "realtime"  # On-demand from client
    MINUTES_1 = "1m"
    MINUTES_5 = "5m"
    MINUTES_15 = "15m"
    MINUTES_30 = "30m"
    HOURLY = "1h"
    HOURS_4 = "4h"
    DAILY = "1d"


class DataSource(Base):
    """
    Data Source Model - منبع داده
    ذخیره اطلاعات و وضعیت منابع داده در دیتابیس
    """
    __tablename__ = 'data_sources'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    
    # Basic Info
    source_id = Column(String(100), nullable=False, unique=True, index=True)
    name = Column(String(255), nullable=False)
    source_type = Column(String(50), nullable=False, index=True)
    description = Column(Text, nullable=True)
    
    # Connection Info
    base_url = Column(String(500), nullable=False)
    api_version = Column(String(20), nullable=True)
    
    # Authentication
    requires_api_key = Column(Boolean, default=False)
    api_key_env_var = Column(String(100), nullable=True)
    has_api_key_configured = Column(Boolean, default=False)
    
    # Rate Limiting
    rate_limit_description = Column(String(100), nullable=True)
    rate_limit_per_minute = Column(Integer, nullable=True)
    rate_limit_per_hour = Column(Integer, nullable=True)
    rate_limit_per_day = Column(Integer, nullable=True)
    
    # Collection Settings
    collection_interval = Column(String(20), default="30m")  # Default: 30 minutes for bulk
    supports_realtime = Column(Boolean, default=False)  # Can fetch on-demand
    
    # Supported Features
    supported_timeframes = Column(Text, nullable=True)  # JSON array
    categories = Column(Text, nullable=True)  # JSON array
    features = Column(Text, nullable=True)  # JSON array
    
    # Status
    is_active = Column(Boolean, default=True, index=True)
    status = Column(String(50), default="active", index=True)
    status_message = Column(Text, nullable=True)
    
    # Priority & Weight
    priority = Column(Integer, default=5)  # 1-10, lower is higher priority
    weight = Column(Integer, default=1)  # For load balancing
    
    # Verification
    is_verified = Column(Boolean, default=False)
    is_free_tier = Column(Boolean, default=True)
    
    # Statistics
    total_requests = Column(Integer, default=0)
    successful_requests = Column(Integer, default=0)
    failed_requests = Column(Integer, default=0)
    avg_response_time_ms = Column(Float, default=0.0)
    last_success_at = Column(DateTime, nullable=True)
    last_failure_at = Column(DateTime, nullable=True)
    last_error_message = Column(Text, nullable=True)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    last_checked_at = Column(DateTime, nullable=True)
    
    # Indexes for common queries
    __table_args__ = (
        Index('idx_source_type_active', 'source_type', 'is_active'),
        Index('idx_status_priority', 'status', 'priority'),
    )
    
    def __repr__(self):
        return f"<DataSource(id={self.source_id}, name={self.name}, active={self.is_active})>"
    
    def to_dict(self) -> Dict[str, Any]:
        """تبدیل به دیکشنری"""
        return {
            "id": self.id,
            "source_id": self.source_id,
            "name": self.name,
            "source_type": self.source_type,
            "description": self.description,
            "base_url": self.base_url,
            "api_version": self.api_version,
            "requires_api_key": self.requires_api_key,
            "api_key_env_var": self.api_key_env_var,
            "has_api_key_configured": self.has_api_key_configured,
            "rate_limit_description": self.rate_limit_description,
            "collection_interval": self.collection_interval,
            "supports_realtime": self.supports_realtime,
            "supported_timeframes": json.loads(self.supported_timeframes) if self.supported_timeframes else [],
            "categories": json.loads(self.categories) if self.categories else [],
            "features": json.loads(self.features) if self.features else [],
            "is_active": self.is_active,
            "status": self.status,
            "status_message": self.status_message,
            "priority": self.priority,
            "weight": self.weight,
            "is_verified": self.is_verified,
            "is_free_tier": self.is_free_tier,
            "total_requests": self.total_requests,
            "successful_requests": self.successful_requests,
            "failed_requests": self.failed_requests,
            "success_rate": (self.successful_requests / self.total_requests * 100) if self.total_requests > 0 else 0,
            "avg_response_time_ms": self.avg_response_time_ms,
            "last_success_at": self.last_success_at.isoformat() if self.last_success_at else None,
            "last_failure_at": self.last_failure_at.isoformat() if self.last_failure_at else None,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
            "last_checked_at": self.last_checked_at.isoformat() if self.last_checked_at else None
        }


class DataCollectionLog(Base):
    """
    Data Collection Log - لاگ جمع‌آوری داده
    ثبت تاریخچه جمع‌آوری داده از منابع
    """
    __tablename__ = 'data_collection_logs'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(String(100), nullable=False, index=True)
    
    # Collection Info
    collection_type = Column(String(50), nullable=False)  # scheduled, on_demand, bulk
    interval_used = Column(String(20), nullable=True)
    
    # Timing
    started_at = Column(DateTime, nullable=False, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    
    # Results
    success = Column(Boolean, default=False)
    records_fetched = Column(Integer, default=0)
    records_stored = Column(Integer, default=0)
    
    # Error Info
    error_type = Column(String(100), nullable=True)
    error_message = Column(Text, nullable=True)
    
    # HTTP Info
    http_status_code = Column(Integer, nullable=True)
    response_size_bytes = Column(Integer, nullable=True)
    
    # Indexes
    __table_args__ = (
        Index('idx_collection_source_time', 'source_id', 'started_at'),
        Index('idx_collection_success', 'success', 'started_at'),
    )
    
    def to_dict(self) -> Dict[str, Any]:
        """تبدیل به دیکشنری"""
        return {
            "id": self.id,
            "source_id": self.source_id,
            "collection_type": self.collection_type,
            "interval_used": self.interval_used,
            "started_at": self.started_at.isoformat() if self.started_at else None,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None,
            "duration_ms": self.duration_ms,
            "success": self.success,
            "records_fetched": self.records_fetched,
            "records_stored": self.records_stored,
            "error_type": self.error_type,
            "error_message": self.error_message,
            "http_status_code": self.http_status_code,
            "response_size_bytes": self.response_size_bytes
        }


class CollectionSchedule(Base):
    """
    Collection Schedule - زمان‌بندی جمع‌آوری
    تنظیم بازه‌های جمع‌آوری داده برای هر منبع
    """
    __tablename__ = 'collection_schedules'
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    source_id = Column(String(100), nullable=False, unique=True, index=True)
    
    # Schedule Settings
    collection_interval = Column(String(20), nullable=False, default="30m")
    is_enabled = Column(Boolean, default=True)
    
    # Execution Times
    last_run_at = Column(DateTime, nullable=True)
    next_run_at = Column(DateTime, nullable=True)
    
    # Statistics
    consecutive_failures = Column(Integer, default=0)
    total_runs = Column(Integer, default=0)
    successful_runs = Column(Integer, default=0)
    
    # Backoff Settings
    backoff_until = Column(DateTime, nullable=True)  # If in backoff state
    backoff_multiplier = Column(Float, default=1.0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self) -> Dict[str, Any]:
        """تبدیل به دیکشنری"""
        return {
            "id": self.id,
            "source_id": self.source_id,
            "collection_interval": self.collection_interval,
            "is_enabled": self.is_enabled,
            "last_run_at": self.last_run_at.isoformat() if self.last_run_at else None,
            "next_run_at": self.next_run_at.isoformat() if self.next_run_at else None,
            "consecutive_failures": self.consecutive_failures,
            "total_runs": self.total_runs,
            "successful_runs": self.successful_runs,
            "success_rate": (self.successful_runs / self.total_runs * 100) if self.total_runs > 0 else 0,
            "backoff_until": self.backoff_until.isoformat() if self.backoff_until else None,
            "backoff_multiplier": self.backoff_multiplier,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }


# ===== DATA SOURCE MANAGER =====

class DataSourceManager:
    """
    مدیریت منابع داده در دیتابیس
    Data Source Manager for database operations
    """
    
    def __init__(self, session):
        self.session = session
    
    def create_source(self, source_data: Dict[str, Any]) -> Optional[DataSource]:
        """ایجاد منبع جدید"""
        try:
            source = DataSource(
                source_id=source_data["source_id"],
                name=source_data["name"],
                source_type=source_data.get("source_type", "market"),
                description=source_data.get("description"),
                base_url=source_data["base_url"],
                api_version=source_data.get("api_version"),
                requires_api_key=source_data.get("requires_api_key", False),
                api_key_env_var=source_data.get("api_key_env_var"),
                rate_limit_description=source_data.get("rate_limit_description"),
                collection_interval=source_data.get("collection_interval", "30m"),
                supports_realtime=source_data.get("supports_realtime", False),
                supported_timeframes=json.dumps(source_data.get("supported_timeframes", [])),
                categories=json.dumps(source_data.get("categories", [])),
                features=json.dumps(source_data.get("features", [])),
                is_active=source_data.get("is_active", True),
                status=source_data.get("status", "active"),
                priority=source_data.get("priority", 5),
                weight=source_data.get("weight", 1),
                is_verified=source_data.get("is_verified", False),
                is_free_tier=source_data.get("is_free_tier", True)
            )
            self.session.add(source)
            self.session.commit()
            return source
        except Exception as e:
            self.session.rollback()
            print(f"Error creating source: {e}")
            return None
    
    def get_source(self, source_id: str) -> Optional[DataSource]:
        """دریافت منبع با شناسه"""
        return self.session.query(DataSource).filter_by(source_id=source_id).first()
    
    def get_all_sources(self) -> List[DataSource]:
        """دریافت همه منابع"""
        return self.session.query(DataSource).all()
    
    def get_active_sources(self) -> List[DataSource]:
        """دریافت منابع فعال"""
        return self.session.query(DataSource).filter_by(is_active=True).all()
    
    def get_sources_by_type(self, source_type: str) -> List[DataSource]:
        """دریافت منابع بر اساس نوع"""
        return self.session.query(DataSource).filter_by(source_type=source_type, is_active=True).all()
    
    def update_source_status(self, source_id: str, is_active: bool, status: str = None, status_message: str = None) -> bool:
        """به‌روزرسانی وضعیت منبع"""
        try:
            source = self.get_source(source_id)
            if source:
                source.is_active = is_active
                if status:
                    source.status = status
                if status_message:
                    source.status_message = status_message
                source.updated_at = datetime.utcnow()
                self.session.commit()
                return True
            return False
        except Exception as e:
            self.session.rollback()
            print(f"Error updating source status: {e}")
            return False
    
    def record_request(self, source_id: str, success: bool, response_time_ms: float, error_message: str = None) -> bool:
        """ثبت درخواست"""
        try:
            source = self.get_source(source_id)
            if source:
                source.total_requests += 1
                if success:
                    source.successful_requests += 1
                    source.last_success_at = datetime.utcnow()
                else:
                    source.failed_requests += 1
                    source.last_failure_at = datetime.utcnow()
                    if error_message:
                        source.last_error_message = error_message
                
                # Update average response time
                if source.avg_response_time_ms > 0:
                    source.avg_response_time_ms = (source.avg_response_time_ms + response_time_ms) / 2
                else:
                    source.avg_response_time_ms = response_time_ms
                
                source.last_checked_at = datetime.utcnow()
                self.session.commit()
                return True
            return False
        except Exception as e:
            self.session.rollback()
            print(f"Error recording request: {e}")
            return False
    
    def get_sources_for_collection(self, interval: str) -> List[DataSource]:
        """دریافت منابع برای جمع‌آوری بر اساس بازه"""
        return self.session.query(DataSource).filter(
            DataSource.is_active == True,
            DataSource.collection_interval == interval,
            DataSource.status != "error"
        ).order_by(DataSource.priority).all()
    
    def get_statistics(self) -> Dict[str, Any]:
        """آمار منابع"""
        all_sources = self.get_all_sources()
        active_sources = [s for s in all_sources if s.is_active]
        
        total_requests = sum(s.total_requests for s in all_sources)
        successful_requests = sum(s.successful_requests for s in all_sources)
        
        return {
            "total_sources": len(all_sources),
            "active_sources": len(active_sources),
            "by_type": {},  # Would need to count by type
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "success_rate": (successful_requests / total_requests * 100) if total_requests > 0 else 0,
            "sources_with_errors": len([s for s in all_sources if s.status == "error"])
        }


# ===== INITIALIZATION HELPER =====

def init_data_sources_from_registry(session, registry):
    """
    Initialize data sources in database from registry
    پر کردن جدول منابع از رجیستری
    """
    manager = DataSourceManager(session)
    
    for source_id, source_info in registry.to_dict().items():
        existing = manager.get_source(source_id)
        if not existing:
            source_data = {
                "source_id": source_id,
                "name": source_info["name"],
                "source_type": source_info["source_type"],
                "description": source_info.get("description"),
                "base_url": source_info["url"],
                "requires_api_key": source_info.get("requires_api_key", False),
                "api_key_env_var": source_info.get("api_key_env"),
                "rate_limit_description": source_info.get("rate_limit"),
                "collection_interval": "30m",  # Default to 30 minutes
                "supports_realtime": "realtime" in source_info.get("supported_timeframes", []),
                "supported_timeframes": source_info.get("supported_timeframes", []),
                "categories": source_info.get("categories", []),
                "features": source_info.get("features", []),
                "is_active": source_info.get("is_active", True),
                "priority": source_info.get("priority", 5),
                "is_verified": source_info.get("verified", False),
                "is_free_tier": source_info.get("free_tier", True)
            }
            manager.create_source(source_data)
            print(f"Created data source: {source_id}")
        else:
            print(f"Data source already exists: {source_id}")
    
    return manager


# ===== COLLECTION INTERVALS CONFIGURATION =====

# Recommended collection intervals for different data types
COLLECTION_INTERVALS = {
    # Bulk data - collect every 15-30 minutes
    "market": "15m",
    "historical": "30m",
    "onchain": "30m",
    "defi": "15m",
    
    # News - collect every 15-30 minutes
    "news": "15m",
    "social": "30m",
    
    # Sentiment - collect every 15 minutes
    "sentiment": "15m",
    
    # Technical - collect every 15 minutes
    "technical": "15m",
    
    # Aggregated - collect every 15 minutes
    "aggregated": "15m"
}

# Real-time sources - fetch on-demand from client
REALTIME_SOURCES = [
    "binance_historical",
    "coingecko_historical",
    "coincap_realtime",
    "fear_greed_index"
]
