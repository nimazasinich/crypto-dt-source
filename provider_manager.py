#!/usr/bin/env python3
"""
Provider Manager - مدیریت ارائه‌دهندگان API و استراتژی‌های Rotation
"""

import json
import asyncio
import aiohttp
import time
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
import random


class ProviderStatus(Enum):
    """وضعیت ارائه‌دهنده"""
    ONLINE = "online"
    OFFLINE = "offline"
    DEGRADED = "degraded"
    RATE_LIMITED = "rate_limited"


class RotationStrategy(Enum):
    """استراتژی‌های چرخش"""
    ROUND_ROBIN = "round_robin"
    PRIORITY = "priority"
    WEIGHTED = "weighted"
    LEAST_USED = "least_used"
    FASTEST_RESPONSE = "fastest_response"


@dataclass(init=False)
class RateLimitInfo:
    """اطلاعات محدودیت نرخ"""
    requests_per_second: Optional[int] = None
    requests_per_minute: Optional[int] = None
    requests_per_hour: Optional[int] = None
    requests_per_day: Optional[int] = None
    requests_per_week: Optional[int] = None
    requests_per_month: Optional[int] = None
    weight_per_minute: Optional[int] = None
    current_usage: int = 0
    reset_time: Optional[float] = None
    extra_limits: Dict[str, Any] = field(default_factory=dict)

    def __init__(
        self,
        requests_per_second: Optional[int] = None,
        requests_per_minute: Optional[int] = None,
        requests_per_hour: Optional[int] = None,
        requests_per_day: Optional[int] = None,
        requests_per_week: Optional[int] = None,
        requests_per_month: Optional[int] = None,
        weight_per_minute: Optional[int] = None,
        current_usage: int = 0,
        reset_time: Optional[float] = None,
        **extra: Any,
    ):
        self.requests_per_second = requests_per_second
        self.requests_per_minute = requests_per_minute
        self.requests_per_hour = requests_per_hour
        self.requests_per_day = requests_per_day
        self.requests_per_week = requests_per_week
        self.requests_per_month = requests_per_month
        self.weight_per_minute = weight_per_minute
        self.current_usage = current_usage
        self.reset_time = reset_time
        self.extra_limits = extra

    @classmethod
    def from_dict(cls, data: Optional[Dict[str, Any]]) -> "RateLimitInfo":
        """ساخت نمونه از دیکشنری و مدیریت کلیدهای ناشناخته."""
        if isinstance(data, cls):
            return data

        if not data:
            return cls()

        return cls(**data)
    
    def is_limited(self) -> bool:
        """بررسی محدودیت نرخ"""
        now = time.time()
        if self.reset_time and now < self.reset_time:
            if self.requests_per_second and self.current_usage >= self.requests_per_second:
                return True
            if self.requests_per_minute and self.current_usage >= self.requests_per_minute:
                return True
            if self.requests_per_hour and self.current_usage >= self.requests_per_hour:
                return True
            if self.requests_per_day and self.current_usage >= self.requests_per_day:
                return True
        return False
    
    def increment(self):
        """افزایش شمارنده استفاده"""
        self.current_usage += 1


@dataclass
class Provider:
    """کلاس ارائه‌دهنده API"""
    provider_id: str
    name: str
    category: str
    base_url: str
    endpoints: Dict[str, str]
    rate_limit: RateLimitInfo
    requires_auth: bool = False
    priority: int = 5
    weight: int = 50
    status: ProviderStatus = ProviderStatus.ONLINE
    
    # آمار
    total_requests: int = 0
    successful_requests: int = 0
    failed_requests: int = 0
    avg_response_time: float = 0.0
    last_check: Optional[datetime] = None
    last_error: Optional[str] = None
    
    # Circuit Breaker
    consecutive_failures: int = 0
    circuit_breaker_open: bool = False
    circuit_breaker_open_until: Optional[float] = None
    
    def __post_init__(self):
        """مقداردهی اولیه"""
        if isinstance(self.rate_limit, dict):
            self.rate_limit = RateLimitInfo.from_dict(self.rate_limit)
        elif not isinstance(self.rate_limit, RateLimitInfo):
            self.rate_limit = RateLimitInfo()
    
    @property
    def success_rate(self) -> float:
        """نرخ موفقیت"""
        if self.total_requests == 0:
            return 100.0
        return (self.successful_requests / self.total_requests) * 100
    
    @property
    def is_available(self) -> bool:
        """آیا ارائه‌دهنده در دسترس است؟"""
        # بررسی Circuit Breaker
        if self.circuit_breaker_open:
            if self.circuit_breaker_open_until and time.time() > self.circuit_breaker_open_until:
                self.circuit_breaker_open = False
                self.consecutive_failures = 0
            else:
                return False
        
        # بررسی محدودیت نرخ
        if self.rate_limit and self.rate_limit.is_limited():
            self.status = ProviderStatus.RATE_LIMITED
            return False
        
        # بررسی وضعیت
        return self.status in [ProviderStatus.ONLINE, ProviderStatus.DEGRADED]
    
    def record_success(self, response_time: float):
        """ثبت درخواست موفق"""
        self.total_requests += 1
        self.successful_requests += 1
        self.consecutive_failures = 0
        
        # محاسبه میانگین متحرک زمان پاسخ
        if self.avg_response_time == 0:
            self.avg_response_time = response_time
        else:
            self.avg_response_time = (self.avg_response_time * 0.8) + (response_time * 0.2)
        
        self.status = ProviderStatus.ONLINE
        self.last_check = datetime.now()
        
        if self.rate_limit:
            self.rate_limit.increment()
    
    def record_failure(self, error: str, circuit_breaker_threshold: int = 5):
        """ثبت درخواست ناموفق"""
        self.total_requests += 1
        self.failed_requests += 1
        self.consecutive_failures += 1
        self.last_error = error
        self.last_check = datetime.now()
        
        # فعال‌سازی Circuit Breaker
        if self.consecutive_failures >= circuit_breaker_threshold:
            self.circuit_breaker_open = True
            self.circuit_breaker_open_until = time.time() + 60  # ۶۰ ثانیه
            self.status = ProviderStatus.OFFLINE
        else:
            self.status = ProviderStatus.DEGRADED


@dataclass
class ProviderPool:
    """استخر ارائه‌دهندگان با استراتژی چرخش"""
    pool_id: str
    pool_name: str
    category: str
    rotation_strategy: RotationStrategy
    providers: List[Provider] = field(default_factory=list)
    current_index: int = 0
    enabled: bool = True
    total_rotations: int = 0
    
    def add_provider(self, provider: Provider):
        """افزودن ارائه‌دهنده به استخر"""
        if provider not in self.providers:
            self.providers.append(provider)
            # مرتب‌سازی بر اساس اولویت
            if self.rotation_strategy == RotationStrategy.PRIORITY:
                self.providers.sort(key=lambda p: p.priority, reverse=True)
    
    def remove_provider(self, provider_id: str):
        """حذف ارائه‌دهنده از استخر"""
        self.providers = [p for p in self.providers if p.provider_id != provider_id]
    
    def get_next_provider(self) -> Optional[Provider]:
        """دریافت ارائه‌دهنده بعدی بر اساس استراتژی"""
        if not self.providers or not self.enabled:
            return None
        
        # فیلتر ارائه‌دهندگان در دسترس
        available = [p for p in self.providers if p.is_available]
        if not available:
            return None
        
        provider = None
        
        if self.rotation_strategy == RotationStrategy.ROUND_ROBIN:
            provider = self._round_robin(available)
        elif self.rotation_strategy == RotationStrategy.PRIORITY:
            provider = self._priority_based(available)
        elif self.rotation_strategy == RotationStrategy.WEIGHTED:
            provider = self._weighted_random(available)
        elif self.rotation_strategy == RotationStrategy.LEAST_USED:
            provider = self._least_used(available)
        elif self.rotation_strategy == RotationStrategy.FASTEST_RESPONSE:
            provider = self._fastest_response(available)
        
        if provider:
            self.total_rotations += 1
        
        return provider
    
    def _round_robin(self, available: List[Provider]) -> Provider:
        """چرخش Round Robin"""
        provider = available[self.current_index % len(available)]
        self.current_index += 1
        return provider
    
    def _priority_based(self, available: List[Provider]) -> Provider:
        """بر اساس اولویت"""
        return max(available, key=lambda p: p.priority)
    
    def _weighted_random(self, available: List[Provider]) -> Provider:
        """انتخاب تصادفی وزن‌دار"""
        weights = [p.weight for p in available]
        return random.choices(available, weights=weights, k=1)[0]
    
    def _least_used(self, available: List[Provider]) -> Provider:
        """کمترین استفاده شده"""
        return min(available, key=lambda p: p.total_requests)
    
    def _fastest_response(self, available: List[Provider]) -> Provider:
        """سریع‌ترین پاسخ"""
        return min(available, key=lambda p: p.avg_response_time if p.avg_response_time > 0 else float('inf'))
    
    def get_stats(self) -> Dict[str, Any]:
        """آمار استخر"""
        total_providers = len(self.providers)
        available_providers = len([p for p in self.providers if p.is_available])
        
        return {
            "pool_id": self.pool_id,
            "pool_name": self.pool_name,
            "category": self.category,
            "rotation_strategy": self.rotation_strategy.value,
            "total_providers": total_providers,
            "available_providers": available_providers,
            "total_rotations": self.total_rotations,
            "enabled": self.enabled,
            "providers": [
                {
                    "provider_id": p.provider_id,
                    "name": p.name,
                    "status": p.status.value,
                    "success_rate": p.success_rate,
                    "total_requests": p.total_requests,
                    "avg_response_time": p.avg_response_time,
                    "is_available": p.is_available
                }
                for p in self.providers
            ]
        }


class ProviderManager:
    """مدیر ارائه‌دهندگان"""
    
    def __init__(self, config_path: str = "providers_config_extended.json"):
        self.config_path = config_path
        self.providers: Dict[str, Provider] = {}
        self.pools: Dict[str, ProviderPool] = {}
        self.session: Optional[aiohttp.ClientSession] = None
        
        self.load_config()
    
    def load_config(self):
        """بارگذاری پیکربندی از فایل JSON"""
        try:
            with open(self.config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            # بارگذاری ارائه‌دهندگان
            for provider_id, provider_data in config.get('providers', {}).items():
                rate_limit_data = provider_data.get('rate_limit', {})
                rate_limit = RateLimitInfo.from_dict(rate_limit_data)
                
                provider = Provider(
                    provider_id=provider_id,
                    name=provider_data['name'],
                    category=provider_data['category'],
                    base_url=provider_data['base_url'],
                    endpoints=provider_data.get('endpoints', {}),
                    rate_limit=rate_limit,
                    requires_auth=provider_data.get('requires_auth', False),
                    priority=provider_data.get('priority', 5),
                    weight=provider_data.get('weight', 50)
                )
                self.providers[provider_id] = provider
            
            # بارگذاری Pool‌ها
            for pool_config in config.get('pool_configurations', []):
                pool_id = pool_config['pool_name'].lower().replace(' ', '_')
                pool = ProviderPool(
                    pool_id=pool_id,
                    pool_name=pool_config['pool_name'],
                    category=pool_config['category'],
                    rotation_strategy=RotationStrategy(pool_config['rotation_strategy'])
                )
                
                # افزودن ارائه‌دهندگان به Pool
                for provider_id in pool_config.get('providers', []):
                    if provider_id in self.providers:
                        pool.add_provider(self.providers[provider_id])
                
                self.pools[pool_id] = pool
            
            print(f"✅ بارگذاری موفق: {len(self.providers)} ارائه‌دهنده، {len(self.pools)} استخر")
        
        except FileNotFoundError:
            print(f"❌ خطا: فایل {self.config_path} یافت نشد")
        except Exception as e:
            print(f"❌ خطا در بارگذاری پیکربندی: {e}")
    
    async def init_session(self):
        """مقداردهی اولیه HTTP Session"""
        if not self.session:
            timeout = aiohttp.ClientTimeout(total=10)
            self.session = aiohttp.ClientSession(timeout=timeout)
    
    async def close_session(self):
        """بستن HTTP Session"""
        if self.session:
            await self.session.close()
            self.session = None
    
    async def health_check(self, provider: Provider) -> bool:
        """بررسی سلامت ارائه‌دهنده"""
        await self.init_session()
        
        # انتخاب اولین endpoint برای تست
        if not provider.endpoints:
            return False
        
        endpoint = list(provider.endpoints.values())[0]
        url = f"{provider.base_url}{endpoint}"
        
        start_time = time.time()
        
        try:
            async with self.session.get(url) as response:
                response_time = (time.time() - start_time) * 1000  # میلی‌ثانیه
                
                if response.status == 200:
                    provider.record_success(response_time)
                    return True
                else:
                    provider.record_failure(f"HTTP {response.status}")
                    return False
        
        except asyncio.TimeoutError:
            provider.record_failure("Timeout")
            return False
        except Exception as e:
            provider.record_failure(str(e))
            return False
    
    async def health_check_all(self, silent: bool = False):
        """بررسی سلامت همه ارائه‌دهندگان"""
        tasks = [self.health_check(provider) for provider in self.providers.values()]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        online = sum(1 for r in results if r is True)
        if not silent:
            print(f"✅ بررسی سلامت: {online}/{len(self.providers)} ارائه‌دهنده آنلاین")
        return online, len(self.providers)
    
    def get_provider(self, provider_id: str) -> Optional[Provider]:
        """دریافت ارائه‌دهنده با ID"""
        return self.providers.get(provider_id)
    
    def get_pool(self, pool_id: str) -> Optional[ProviderPool]:
        """دریافت Pool با ID"""
        return self.pools.get(pool_id)
    
    def get_next_from_pool(self, pool_id: str) -> Optional[Provider]:
        """دریافت ارائه‌دهنده بعدی از Pool"""
        pool = self.get_pool(pool_id)
        if pool:
            return pool.get_next_provider()
        return None
    
    def get_all_stats(self) -> Dict[str, Any]:
        """آمار کامل سیستم"""
        total_providers = len(self.providers)
        online_providers = len([p for p in self.providers.values() if p.status == ProviderStatus.ONLINE])
        offline_providers = len([p for p in self.providers.values() if p.status == ProviderStatus.OFFLINE])
        degraded_providers = len([p for p in self.providers.values() if p.status == ProviderStatus.DEGRADED])
        
        total_requests = sum(p.total_requests for p in self.providers.values())
        successful_requests = sum(p.successful_requests for p in self.providers.values())
        
        return {
            "summary": {
                "total_providers": total_providers,
                "online": online_providers,
                "offline": offline_providers,
                "degraded": degraded_providers,
                "total_requests": total_requests,
                "successful_requests": successful_requests,
                "overall_success_rate": (successful_requests / total_requests * 100) if total_requests > 0 else 0
            },
            "providers": {
                provider_id: {
                    "name": p.name,
                    "category": p.category,
                    "status": p.status.value,
                    "success_rate": p.success_rate,
                    "total_requests": p.total_requests,
                    "avg_response_time": p.avg_response_time,
                    "is_available": p.is_available,
                    "priority": p.priority,
                    "weight": p.weight
                }
                for provider_id, p in self.providers.items()
            },
            "pools": {
                pool_id: pool.get_stats()
                for pool_id, pool in self.pools.items()
            }
        }
    
    def export_stats(self, filepath: str = "provider_stats.json"):
        """صادرکردن آمار به فایل JSON"""
        stats = self.get_all_stats()
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2, ensure_ascii=False)
        print(f"✅ آمار در {filepath} ذخیره شد")


# تست و نمونه استفاده
async def main():
    """تابع اصلی برای تست"""
    manager = ProviderManager()
    
    print("\n📊 بررسی سلامت ارائه‌دهندگان...")
    await manager.health_check_all()
    
    print("\n🔄 تست Pool چرخشی...")
    pool = manager.get_pool("primary_market_data_pool")
    if pool:
        for i in range(5):
            provider = pool.get_next_provider()
            if provider:
                print(f"  Round {i+1}: {provider.name}")
    
    print("\n📈 آمار کلی:")
    stats = manager.get_all_stats()
    summary = stats['summary']
    print(f"  کل: {summary['total_providers']}")
    print(f"  آنلاین: {summary['online']}")
    print(f"  آفلاین: {summary['offline']}")
    print(f"  نرخ موفقیت: {summary['overall_success_rate']:.2f}%")
    
    # صادرکردن آمار
    manager.export_stats()
    
    await manager.close_session()
    print("\n✅ اتمام")


if __name__ == "__main__":
    asyncio.run(main())

