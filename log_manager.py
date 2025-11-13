#!/usr/bin/env python3
"""
Log Management System - مدیریت کامل لاگ‌ها با قابلیت Export/Import/Filter
"""

import json
import csv
from datetime import datetime
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, asdict
from enum import Enum
from pathlib import Path
import gzip


class LogLevel(Enum):
    """سطوح لاگ"""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class LogCategory(Enum):
    """دسته‌بندی لاگ‌ها"""
    PROVIDER = "provider"
    POOL = "pool"
    API = "api"
    SYSTEM = "system"
    HEALTH_CHECK = "health_check"
    ROTATION = "rotation"
    REQUEST = "request"
    ERROR = "error"


@dataclass
class LogEntry:
    """ورودی لاگ"""
    timestamp: str
    level: str
    category: str
    message: str
    provider_id: Optional[str] = None
    pool_id: Optional[str] = None
    status_code: Optional[int] = None
    response_time: Optional[float] = None
    error: Optional[str] = None
    extra_data: Optional[Dict[str, Any]] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """تبدیل به dictionary"""
        return {k: v for k, v in asdict(self).items() if v is not None}
    
    @staticmethod
    def from_dict(data: Dict[str, Any]) -> 'LogEntry':
        """ساخت از dictionary"""
        return LogEntry(**data)


class LogManager:
    """مدیریت لاگ‌ها"""
    
    def __init__(self, log_file: str = "logs/app.log", max_size_mb: int = 50):
        self.log_file = Path(log_file)
        self.max_size_bytes = max_size_mb * 1024 * 1024
        self.logs: List[LogEntry] = []
        
        # ساخت دایرکتوری logs
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
        # بارگذاری لاگ‌های موجود
        self.load_logs()
    
    def add_log(
        self,
        level: LogLevel,
        category: LogCategory,
        message: str,
        provider_id: Optional[str] = None,
        pool_id: Optional[str] = None,
        status_code: Optional[int] = None,
        response_time: Optional[float] = None,
        error: Optional[str] = None,
        extra_data: Optional[Dict[str, Any]] = None
    ):
        """افزودن لاگ جدید"""
        log_entry = LogEntry(
            timestamp=datetime.now().isoformat(),
            level=level.value,
            category=category.value,
            message=message,
            provider_id=provider_id,
            pool_id=pool_id,
            status_code=status_code,
            response_time=response_time,
            error=error,
            extra_data=extra_data
        )
        
        self.logs.append(log_entry)
        self._write_to_file(log_entry)
        
        # بررسی حجم و rotation
        self._check_rotation()
    
    def _write_to_file(self, log_entry: LogEntry):
        """نوشتن لاگ در فایل"""
        with open(self.log_file, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry.to_dict(), ensure_ascii=False) + '\n')
    
    def _check_rotation(self):
        """بررسی و rotation لاگ‌ها"""
        if self.log_file.exists() and self.log_file.stat().st_size > self.max_size_bytes:
            # فشرده‌سازی فایل قبلی
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            archive_file = self.log_file.parent / f"{self.log_file.stem}_{timestamp}.log.gz"
            
            with open(self.log_file, 'rb') as f_in:
                with gzip.open(archive_file, 'wb') as f_out:
                    f_out.writelines(f_in)
            
            # پاک کردن فایل فعلی
            self.log_file.unlink()
            
            print(f"✅ Log rotated to: {archive_file}")
    
    def load_logs(self, limit: Optional[int] = None):
        """بارگذاری لاگ‌ها از فایل"""
        if not self.log_file.exists():
            return
        
        self.logs.clear()
        
        try:
            with open(self.log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    if line.strip():
                        try:
                            data = json.loads(line)
                            self.logs.append(LogEntry.from_dict(data))
                        except json.JSONDecodeError:
                            continue
            
            # محدود کردن به تعداد مشخص
            if limit:
                self.logs = self.logs[-limit:]
            
            print(f"✅ Loaded {len(self.logs)} logs")
        except Exception as e:
            print(f"❌ Error loading logs: {e}")
    
    def filter_logs(
        self,
        level: Optional[LogLevel] = None,
        category: Optional[LogCategory] = None,
        provider_id: Optional[str] = None,
        pool_id: Optional[str] = None,
        start_time: Optional[datetime] = None,
        end_time: Optional[datetime] = None,
        search_text: Optional[str] = None
    ) -> List[LogEntry]:
        """فیلتر لاگ‌ها"""
        filtered = self.logs.copy()
        
        if level:
            filtered = [log for log in filtered if log.level == level.value]
        
        if category:
            filtered = [log for log in filtered if log.category == category.value]
        
        if provider_id:
            filtered = [log for log in filtered if log.provider_id == provider_id]
        
        if pool_id:
            filtered = [log for log in filtered if log.pool_id == pool_id]
        
        if start_time:
            filtered = [log for log in filtered if datetime.fromisoformat(log.timestamp) >= start_time]
        
        if end_time:
            filtered = [log for log in filtered if datetime.fromisoformat(log.timestamp) <= end_time]
        
        if search_text:
            filtered = [log for log in filtered if search_text.lower() in log.message.lower()]
        
        return filtered
    
    def get_recent_logs(self, limit: int = 100) -> List[LogEntry]:
        """دریافت آخرین لاگ‌ها"""
        return self.logs[-limit:]
    
    def get_error_logs(self, limit: Optional[int] = None) -> List[LogEntry]:
        """دریافت لاگ‌های خطا"""
        errors = [log for log in self.logs if log.level in ['error', 'critical']]
        if limit:
            return errors[-limit:]
        return errors
    
    def export_to_json(self, filepath: str, filtered: Optional[List[LogEntry]] = None):
        """صادرکردن لاگ‌ها به JSON"""
        logs_to_export = filtered if filtered else self.logs
        
        data = {
            "exported_at": datetime.now().isoformat(),
            "total_logs": len(logs_to_export),
            "logs": [log.to_dict() for log in logs_to_export]
        }
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        print(f"✅ Exported {len(logs_to_export)} logs to {filepath}")
    
    def export_to_csv(self, filepath: str, filtered: Optional[List[LogEntry]] = None):
        """صادرکردن لاگ‌ها به CSV"""
        logs_to_export = filtered if filtered else self.logs
        
        if not logs_to_export:
            print("⚠️  No logs to export")
            return
        
        # فیلدهای CSV
        fieldnames = ['timestamp', 'level', 'category', 'message', 'provider_id', 
                      'pool_id', 'status_code', 'response_time', 'error']
        
        with open(filepath, 'w', newline='', encoding='utf-8') as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            
            for log in logs_to_export:
                row = {k: v for k, v in log.to_dict().items() if k in fieldnames}
                writer.writerow(row)
        
        print(f"✅ Exported {len(logs_to_export)} logs to {filepath}")
    
    def import_from_json(self, filepath: str):
        """وارد کردن لاگ‌ها از JSON"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            logs_data = data.get('logs', [])
            
            for log_data in logs_data:
                log_entry = LogEntry.from_dict(log_data)
                self.logs.append(log_entry)
                self._write_to_file(log_entry)
            
            print(f"✅ Imported {len(logs_data)} logs from {filepath}")
        except Exception as e:
            print(f"❌ Error importing logs: {e}")
    
    def clear_logs(self):
        """پاک کردن همه لاگ‌ها"""
        self.logs.clear()
        if self.log_file.exists():
            self.log_file.unlink()
        print("✅ All logs cleared")
    
    def get_statistics(self) -> Dict[str, Any]:
        """آمار لاگ‌ها"""
        if not self.logs:
            return {"total": 0}
        
        stats = {
            "total": len(self.logs),
            "by_level": {},
            "by_category": {},
            "by_provider": {},
            "by_pool": {},
            "errors": len([log for log in self.logs if log.level in ['error', 'critical']]),
            "date_range": {
                "start": self.logs[0].timestamp if self.logs else None,
                "end": self.logs[-1].timestamp if self.logs else None
            }
        }
        
        # آمار بر اساس سطح
        for log in self.logs:
            stats["by_level"][log.level] = stats["by_level"].get(log.level, 0) + 1
            stats["by_category"][log.category] = stats["by_category"].get(log.category, 0) + 1
            
            if log.provider_id:
                stats["by_provider"][log.provider_id] = stats["by_provider"].get(log.provider_id, 0) + 1
            
            if log.pool_id:
                stats["by_pool"][log.pool_id] = stats["by_pool"].get(log.pool_id, 0) + 1
        
        return stats
    
    def search_logs(self, query: str, limit: int = 100) -> List[LogEntry]:
        """جستجوی لاگ‌ها"""
        results = []
        query_lower = query.lower()
        
        for log in reversed(self.logs):
            if (query_lower in log.message.lower() or
                (log.provider_id and query_lower in log.provider_id.lower()) or
                (log.error and query_lower in log.error.lower())):
                results.append(log)
                
                if len(results) >= limit:
                    break
        
        return results
    
    def get_provider_logs(self, provider_id: str, limit: Optional[int] = None) -> List[LogEntry]:
        """لاگ‌های یک provider"""
        provider_logs = [log for log in self.logs if log.provider_id == provider_id]
        if limit:
            return provider_logs[-limit:]
        return provider_logs
    
    def get_pool_logs(self, pool_id: str, limit: Optional[int] = None) -> List[LogEntry]:
        """لاگ‌های یک pool"""
        pool_logs = [log for log in self.logs if log.pool_id == pool_id]
        if limit:
            return pool_logs[-limit:]
        return pool_logs


# Global instance
_log_manager = None


def get_log_manager() -> LogManager:
    """دریافت instance مدیر لاگ"""
    global _log_manager
    if _log_manager is None:
        _log_manager = LogManager()
    return _log_manager


# Convenience functions
def log_info(category: LogCategory, message: str, **kwargs):
    """لاگ سطح INFO"""
    get_log_manager().add_log(LogLevel.INFO, category, message, **kwargs)


def log_error(category: LogCategory, message: str, **kwargs):
    """لاگ سطح ERROR"""
    get_log_manager().add_log(LogLevel.ERROR, category, message, **kwargs)


def log_warning(category: LogCategory, message: str, **kwargs):
    """لاگ سطح WARNING"""
    get_log_manager().add_log(LogLevel.WARNING, category, message, **kwargs)


def log_debug(category: LogCategory, message: str, **kwargs):
    """لاگ سطح DEBUG"""
    get_log_manager().add_log(LogLevel.DEBUG, category, message, **kwargs)


def log_critical(category: LogCategory, message: str, **kwargs):
    """لاگ سطح CRITICAL"""
    get_log_manager().add_log(LogLevel.CRITICAL, category, message, **kwargs)


# تست
if __name__ == "__main__":
    print("🧪 Testing Log Manager...\n")
    
    manager = LogManager()
    
    # تست افزودن لاگ
    log_info(LogCategory.SYSTEM, "System started")
    log_info(LogCategory.PROVIDER, "Provider health check", provider_id="coingecko", response_time=234.5)
    log_error(LogCategory.PROVIDER, "Provider failed", provider_id="etherscan", error="Timeout")
    log_warning(LogCategory.POOL, "Pool rotation", pool_id="market_pool")
    
    # آمار
    stats = manager.get_statistics()
    print("📊 Statistics:")
    print(json.dumps(stats, indent=2))
    
    # فیلتر
    errors = manager.get_error_logs()
    print(f"\n❌ Error logs: {len(errors)}")
    
    # Export
    manager.export_to_json("test_logs.json")
    manager.export_to_csv("test_logs.csv")
    
    print("\n✅ Log Manager test completed")

