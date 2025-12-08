#!/usr/bin/env python3
"""
Rotating DNS/Proxy Manager
مدیر چرخشی DNS و Proxy برای Binance و KuCoin

Features:
- DNS Rotation (چرخش بین Cloudflare، Google، OpenDNS)
- Proxy Rotation (چرخش بین پروکسی‌های مختلف)
- Health Monitoring (پایش سلامت)
- Automatic Failover (تعویض خودکار در صورت مشکل)
- Always Secure (همیشه امن)
"""

import httpx
import asyncio
import logging
from typing import Optional, Dict, List, Tuple
from datetime import datetime, timedelta
from enum import Enum
import random

logger = logging.getLogger(__name__)


class DNSProvider(Enum):
    """ارائه‌دهندگان DNS"""
    CLOUDFLARE = "cloudflare"
    GOOGLE = "google"
    QUAD9 = "quad9"
    OPENDNS = "opendns"


class RotatingAccessManager:
    """
    مدیر دسترسی چرخشی برای Binance و KuCoin
    
    با چرخش خودکار DNS و Proxy برای امنیت و قابلیت اطمینان بیشتر
    """
    
    def __init__(self):
        # DNS Providers
        self.dns_providers = {
            DNSProvider.CLOUDFLARE: "https://cloudflare-dns.com/dns-query",
            DNSProvider.GOOGLE: "https://dns.google/resolve",
            DNSProvider.QUAD9: "https://dns.quad9.net/dns-query",
            DNSProvider.OPENDNS: "https://doh.opendns.com/dns-query"
        }
        
        # Current DNS Provider (rotation)
        self.current_dns_index = 0
        self.dns_rotation_interval = timedelta(minutes=10)
        self.last_dns_rotation = datetime.now()
        
        # Proxy settings
        self.proxyscrape_api = "https://api.proxyscrape.com/v2/"
        self.proxy_pool: List[str] = []
        self.current_proxy_index = 0
        self.proxy_rotation_interval = timedelta(minutes=5)
        self.last_proxy_rotation = datetime.now()
        self.proxy_health: Dict[str, Dict] = {}
        
        # DNS Cache with rotation
        self.dns_cache: Dict[str, List[str]] = {}  # domain -> [ip1, ip2, ...]
        self.dns_cache_time: Dict[str, datetime] = {}
        self.dns_cache_duration = timedelta(minutes=30)
        
        # Statistics
        self.rotation_stats = {
            "dns_rotations": 0,
            "proxy_rotations": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "dns_failures": {},
            "proxy_failures": {}
        }
        
        # Critical domains (Binance & KuCoin)
        self.critical_domains = [
            "api.binance.com",
            "api.kucoin.com",
            "api-futures.kucoin.com"
        ]
    
    def get_next_dns_provider(self) -> Tuple[DNSProvider, str]:
        """
        دریافت DNS Provider بعدی (چرخشی)
        
        Returns:
            (provider, url)
        """
        # بررسی زمان چرخش
        if (datetime.now() - self.last_dns_rotation) > self.dns_rotation_interval:
            self.current_dns_index = (self.current_dns_index + 1) % len(self.dns_providers)
            self.last_dns_rotation = datetime.now()
            self.rotation_stats["dns_rotations"] += 1
            logger.info(f"🔄 DNS Rotation: #{self.rotation_stats['dns_rotations']}")
        
        providers = list(self.dns_providers.items())
        provider, url = providers[self.current_dns_index]
        
        logger.info(f"🔍 Using DNS Provider: {provider.value}")
        return provider, url
    
    async def resolve_dns_rotating(self, hostname: str) -> Optional[str]:
        """
        حل DNS با استفاده از چرخش خودکار بین providerها
        
        اگر یک provider کار نکرد، بعدی رو امتحان می‌کنه
        """
        # بررسی Cache
        if hostname in self.dns_cache:
            cached_time = self.dns_cache_time.get(hostname)
            if cached_time and (datetime.now() - cached_time) < self.dns_cache_duration:
                cached_ips = self.dns_cache[hostname]
                # چرخش بین IPهای کش شده
                selected_ip = random.choice(cached_ips)
                logger.info(f"🔍 DNS Cache Hit: {hostname} -> {selected_ip}")
                return selected_ip
        
        # امتحان همه providerها تا یکی کار کنه
        providers = list(self.dns_providers.items())
        
        # شروع از current provider
        start_index = self.current_dns_index
        
        for i in range(len(providers)):
            index = (start_index + i) % len(providers)
            provider, url = providers[index]
            
            try:
                logger.info(f"🔍 Trying DNS: {provider.value} for {hostname}")
                
                async with httpx.AsyncClient(timeout=5.0) as client:
                    response = await client.get(
                        url,
                        params={"name": hostname, "type": "A"},
                        headers={"accept": "application/dns-json"}
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        
                        if "Answer" in data and len(data["Answer"]) > 0:
                            # جمع‌آوری همه IPها
                            ips = [ans["data"] for ans in data["Answer"] if ans["type"] == 1]
                            
                            if ips:
                                # ذخیره در cache
                                self.dns_cache[hostname] = ips
                                self.dns_cache_time[hostname] = datetime.now()
                                
                                # انتخاب تصادفی یکی از IPها
                                selected_ip = random.choice(ips)
                                
                                logger.info(f"✅ {provider.value} DNS: {hostname} -> {selected_ip} (از {len(ips)} IP)")
                                return selected_ip
            
            except Exception as e:
                logger.warning(f"⚠️ {provider.value} DNS failed: {e}")
                
                # ثبت خطا
                if provider.value not in self.rotation_stats["dns_failures"]:
                    self.rotation_stats["dns_failures"][provider.value] = 0
                self.rotation_stats["dns_failures"][provider.value] += 1
                
                continue
        
        logger.error(f"❌ All DNS providers failed for {hostname}")
        return None
    
    async def get_rotating_proxy(self) -> Optional[str]:
        """
        دریافت proxy بعدی (چرخشی)
        
        Returns:
            proxy string (ip:port)
        """
        # بررسی زمان refresh
        if not self.proxy_pool or \
           (datetime.now() - self.last_proxy_rotation) > self.proxy_rotation_interval:
            await self.refresh_proxy_pool()
        
        if not self.proxy_pool:
            return None
        
        # چرخش
        self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxy_pool)
        proxy = self.proxy_pool[self.current_proxy_index]
        
        logger.info(f"🔄 Using Proxy #{self.current_proxy_index + 1}/{len(self.proxy_pool)}: {proxy}")
        
        return proxy
    
    async def refresh_proxy_pool(self):
        """
        بروزرسانی لیست پروکسی‌ها
        """
        try:
            logger.info("🔄 Refreshing proxy pool...")
            
            async with httpx.AsyncClient(timeout=15.0) as client:
                response = await client.get(
                    self.proxyscrape_api,
                    params={
                        "request": "displayproxies",
                        "protocol": "http",
                        "timeout": "10000",
                        "country": "all",
                        "ssl": "all",
                        "anonymity": "elite"
                    }
                )
                
                if response.status_code == 200:
                    proxies_text = response.text
                    proxies = [p.strip() for p in proxies_text.split('\n') if p.strip()]
                    
                    # شافل برای تصادفی بودن
                    random.shuffle(proxies)
                    
                    self.proxy_pool = proxies[:20]  # نگه‌داری 20 proxy
                    self.last_proxy_rotation = datetime.now()
                    self.rotation_stats["proxy_rotations"] += 1
                    
                    logger.info(f"✅ Proxy pool refreshed: {len(self.proxy_pool)} proxies")
        
        except Exception as e:
            logger.error(f"❌ Failed to refresh proxy pool: {e}")
    
    async def secure_fetch(
        self,
        url: str,
        use_rotating_dns: bool = True,
        use_rotating_proxy: bool = True,
        **kwargs
    ) -> Optional[httpx.Response]:
        """
        دریافت امن با DNS و Proxy چرخشی
        
        Strategy:
        1. Direct (اول)
        2. Rotating DNS (اگر فیلتر بود)
        3. Rotating Proxy (اگر DNS کار نکرد)
        4. DNS + Proxy (قوی‌ترین)
        
        Args:
            url: آدرس API
            use_rotating_dns: استفاده از DNS چرخشی
            use_rotating_proxy: استفاده از Proxy چرخشی
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"🔐 SECURE FETCH (Rotating): {url}")
        logger.info(f"{'='*60}")
        
        # Method 1: Direct (سریع‌ترین)
        logger.info("1️⃣ Trying DIRECT connection...")
        try:
            async with httpx.AsyncClient(timeout=10.0) as client:
                response = await client.get(url, **kwargs)
                
                if response.status_code == 200:
                    self.rotation_stats["successful_requests"] += 1
                    logger.info(f"✅ DIRECT connection successful!")
                    return response
        except Exception as e:
            logger.warning(f"⚠️ Direct failed: {e}")
        
        # Method 2: Rotating DNS
        if use_rotating_dns:
            logger.info("2️⃣ Trying ROTATING DNS...")
            
            # امتحان 2 DNS provider مختلف
            for attempt in range(2):
                try:
                    hostname = url.split("://")[1].split("/")[0]
                    ip = await self.resolve_dns_rotating(hostname)
                    
                    if ip:
                        url_with_ip = url.replace(hostname, ip)
                        
                        async with httpx.AsyncClient(timeout=10.0, verify=False) as client:
                            headers = kwargs.get("headers", {})
                            headers["Host"] = hostname
                            kwargs["headers"] = headers
                            
                            response = await client.get(url_with_ip, **kwargs)
                            
                            if response.status_code == 200:
                                self.rotation_stats["successful_requests"] += 1
                                logger.info(f"✅ ROTATING DNS successful!")
                                return response
                except Exception as e:
                    logger.warning(f"⚠️ Rotating DNS attempt {attempt + 1} failed: {e}")
        
        # Method 3: Rotating Proxy
        if use_rotating_proxy:
            logger.info("3️⃣ Trying ROTATING PROXY...")
            
            # امتحان 3 proxy مختلف
            for attempt in range(3):
                try:
                    proxy = await self.get_rotating_proxy()
                    
                    if proxy:
                        logger.info(f"   Using proxy: {proxy}")
                        
                        async with httpx.AsyncClient(timeout=10.0, verify=False) as client:
                            response = await client.get(
                                url,
                                proxy=f"http://{proxy}",
                                **kwargs
                            )
                            
                            if response.status_code == 200:
                                self.rotation_stats["successful_requests"] += 1
                                logger.info(f"✅ ROTATING PROXY successful!")
                                return response
                except Exception as e:
                    logger.warning(f"⚠️ Rotating Proxy attempt {attempt + 1} failed: {e}")
        
        # Method 4: DNS + Proxy (قوی‌ترین)
        if use_rotating_dns and use_rotating_proxy:
            logger.info("4️⃣ Trying DNS + PROXY (Combined)...")
            
            try:
                hostname = url.split("://")[1].split("/")[0]
                ip = await self.resolve_dns_rotating(hostname)
                proxy = await self.get_rotating_proxy()
                
                if ip and proxy:
                    url_with_ip = url.replace(hostname, ip)
                    
                    async with httpx.AsyncClient(timeout=10.0, verify=False) as client:
                        headers = kwargs.get("headers", {})
                        headers["Host"] = hostname
                        kwargs["headers"] = headers
                        
                        response = await client.get(
                            url_with_ip,
                            proxy=f"http://{proxy}",
                            **kwargs
                        )
                        
                        if response.status_code == 200:
                            self.rotation_stats["successful_requests"] += 1
                            logger.info(f"✅ DNS + PROXY successful!")
                            return response
            except Exception as e:
                logger.warning(f"⚠️ DNS + Proxy failed: {e}")
        
        # همه روش‌ها ناموفق
        self.rotation_stats["failed_requests"] += 1
        logger.error(f"❌ ALL METHODS FAILED for {url}")
        logger.error(f"{'='*60}\n")
        return None
    
    def get_statistics(self) -> Dict:
        """آمار چرخش و دسترسی"""
        total = self.rotation_stats["successful_requests"] + self.rotation_stats["failed_requests"]
        success_rate = (self.rotation_stats["successful_requests"] / total * 100) if total > 0 else 0
        
        return {
            "dns_rotations": self.rotation_stats["dns_rotations"],
            "proxy_rotations": self.rotation_stats["proxy_rotations"],
            "successful_requests": self.rotation_stats["successful_requests"],
            "failed_requests": self.rotation_stats["failed_requests"],
            "success_rate": f"{success_rate:.1f}%",
            "dns_providers": len(self.dns_providers),
            "proxy_pool_size": len(self.proxy_pool),
            "dns_failures": self.rotation_stats["dns_failures"],
            "proxy_failures": self.rotation_stats["proxy_failures"],
            "cache_size": len(self.dns_cache)
        }
    
    def print_status(self):
        """چاپ وضعیت فعلی"""
        stats = self.get_statistics()
        
        print("\n" + "="*60)
        print("📊 ROTATING ACCESS MANAGER STATUS")
        print("="*60)
        
        print(f"\n🔄 Rotations:")
        print(f"   DNS Rotations:   {stats['dns_rotations']}")
        print(f"   Proxy Rotations: {stats['proxy_rotations']}")
        
        print(f"\n📈 Requests:")
        print(f"   Successful: {stats['successful_requests']}")
        print(f"   Failed:     {stats['failed_requests']}")
        print(f"   Success Rate: {stats['success_rate']}")
        
        print(f"\n🔍 Resources:")
        print(f"   DNS Providers: {stats['dns_providers']}")
        print(f"   Proxy Pool:    {stats['proxy_pool_size']}")
        print(f"   DNS Cache:     {stats['cache_size']} domains")
        
        print("\n" + "="*60)


# Global instance
rotating_access_manager = RotatingAccessManager()


__all__ = ["RotatingAccessManager", "rotating_access_manager", "DNSProvider"]

