#!/usr/bin/env python3
"""
Smart Access Manager
سیستم دسترسی هوشمند به Binance و CoinGecko با همه روش‌های ممکن

Features:
- Direct Connection (اتصال مستقیم)
- DNS over HTTPS (تغییر DNS)
- Free Proxy (استفاده از پروکسی رایگان)
- DNS + Proxy (ترکیبی)
- Automatic Fallback (فالبک خودکار)
"""

import httpx
import asyncio
import logging
from typing import Optional, Dict, List, Tuple
from datetime import datetime, timedelta
from enum import Enum

logger = logging.getLogger(__name__)


class AccessMethod(Enum):
    """روش‌های دسترسی"""
    DIRECT = "direct"
    DNS_CLOUDFLARE = "dns_cloudflare"
    DNS_GOOGLE = "dns_google"
    PROXY = "proxy"
    DNS_PROXY = "dns_proxy"


class SmartAccessManager:
    """
    مدیریت هوشمند دسترسی به APIهای فیلترشده
    
    Priority Order (ترتیب اولویت):
    1. Direct Connection (سریع‌ترین)
    2. DNS over HTTPS - Cloudflare (تغییر DNS)
    3. DNS over HTTPS - Google (DNS جایگزین)
    4. Free Proxy (پروکسی رایگان)
    5. DNS + Proxy (ترکیبی - قوی‌ترین)
    """
    
    def __init__(self):
        self.cloudflare_doh = "https://cloudflare-dns.com/dns-query"
        self.google_doh = "https://dns.google/resolve"
        self.proxyscrape_api = "https://api.proxyscrape.com/v2/"
        
        # Cache for proxies and DNS resolutions
        self.proxy_cache: List[str] = []
        self.proxy_cache_time: Optional[datetime] = None
        self.proxy_refresh_interval = timedelta(minutes=5)
        
        self.dns_cache: Dict[str, str] = {}
        self.dns_cache_time: Dict[str, datetime] = {}
        self.dns_cache_duration = timedelta(hours=1)
        
        # Success statistics
        self.success_stats = {
            AccessMethod.DIRECT: {"success": 0, "fail": 0},
            AccessMethod.DNS_CLOUDFLARE: {"success": 0, "fail": 0},
            AccessMethod.DNS_GOOGLE: {"success": 0, "fail": 0},
            AccessMethod.PROXY: {"success": 0, "fail": 0},
            AccessMethod.DNS_PROXY: {"success": 0, "fail": 0},
        }
        
        # Blocked domains that need special handling
        self.restricted_domains = [
            "api.binance.com",
            "api.coingecko.com",
            "www.binance.com",
            "pro-api.coingecko.com"
        ]
    
    async def resolve_dns_cloudflare(self, hostname: str) -> Optional[str]:
        """
        Resolve DNS using Cloudflare DoH
        حل DNS با استفاده از Cloudflare
        """
        # Check cache
        if hostname in self.dns_cache:
            cached_time = self.dns_cache_time.get(hostname)
            if cached_time and (datetime.now() - cached_time) < self.dns_cache_duration:
                logger.info(f"🔍 DNS Cache Hit: {hostname} -> {self.dns_cache[hostname]}")
                return self.dns_cache[hostname]
        
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    self.cloudflare_doh,
                    params={"name": hostname, "type": "A"},
                    headers={"accept": "application/dns-json"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if "Answer" in data and len(data["Answer"]) > 0:
                        ip = data["Answer"][0]["data"]
                        
                        # Update cache
                        self.dns_cache[hostname] = ip
                        self.dns_cache_time[hostname] = datetime.now()
                        
                        logger.info(f"🔍 Cloudflare DNS: {hostname} -> {ip}")
                        return ip
        
        except Exception as e:
            logger.warning(f"⚠️ Cloudflare DNS failed for {hostname}: {e}")
        
        return None
    
    async def resolve_dns_google(self, hostname: str) -> Optional[str]:
        """
        Resolve DNS using Google DoH
        حل DNS با استفاده از Google
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    self.google_doh,
                    params={"name": hostname, "type": "A"}
                )
                
                if response.status_code == 200:
                    data = response.json()
                    if "Answer" in data and len(data["Answer"]) > 0:
                        ip = data["Answer"][0]["data"]
                        
                        # Update cache
                        self.dns_cache[hostname] = ip
                        self.dns_cache_time[hostname] = datetime.now()
                        
                        logger.info(f"🔍 Google DNS: {hostname} -> {ip}")
                        return ip
        
        except Exception as e:
            logger.warning(f"⚠️ Google DNS failed for {hostname}: {e}")
        
        return None
    
    async def get_free_proxies(self, limit: int = 10) -> List[str]:
        """
        Get fresh free proxies from ProxyScrape
        دریافت پروکسی‌های رایگان تازه
        """
        # Check cache
        if self.proxy_cache and self.proxy_cache_time:
            if (datetime.now() - self.proxy_cache_time) < self.proxy_refresh_interval:
                logger.info(f"📦 Proxy Cache Hit: {len(self.proxy_cache)} proxies")
                return self.proxy_cache[:limit]
        
        try:
            logger.info("🔄 Fetching fresh proxies from ProxyScrape...")
            
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
                    
                    # Update cache
                    self.proxy_cache = proxies
                    self.proxy_cache_time = datetime.now()
                    
                    logger.info(f"✅ Fetched {len(proxies)} proxies from ProxyScrape")
                    return proxies[:limit]
        
        except Exception as e:
            logger.error(f"❌ Failed to fetch proxies: {e}")
        
        return []
    
    async def test_proxy(self, proxy: str, test_url: str = "https://httpbin.org/ip") -> bool:
        """
        Test if a proxy is working
        تست عملکرد پروکسی
        """
        try:
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(
                    test_url,
                    proxy=f"http://{proxy}"
                )
                return response.status_code == 200
        except:
            return False
    
    async def fetch_with_method(
        self,
        url: str,
        method: AccessMethod,
        **kwargs
    ) -> Tuple[Optional[httpx.Response], AccessMethod]:
        """
        Fetch URL using specific access method
        دریافت URL با روش خاص
        """
        try:
            if method == AccessMethod.DIRECT:
                # Method 1: Direct connection
                logger.info(f"🔗 Trying DIRECT connection to {url}")
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.get(url, **kwargs)
                    if response.status_code == 200:
                        self.success_stats[method]["success"] += 1
                        logger.info(f"✅ DIRECT connection successful!")
                        return response, method
            
            elif method == AccessMethod.DNS_CLOUDFLARE:
                # Method 2: DNS over HTTPS (Cloudflare)
                hostname = url.split("//")[1].split("/")[0]
                ip = await self.resolve_dns_cloudflare(hostname)
                
                if ip:
                    # Replace hostname with IP
                    url_with_ip = url.replace(hostname, ip)
                    logger.info(f"🔗 Trying Cloudflare DNS: {hostname} -> {ip}")
                    
                    async with httpx.AsyncClient(timeout=10.0) as client:
                        # Add Host header to preserve virtual host
                        headers = kwargs.get("headers", {})
                        headers["Host"] = hostname
                        kwargs["headers"] = headers
                        
                        response = await client.get(url_with_ip, **kwargs)
                        if response.status_code == 200:
                            self.success_stats[method]["success"] += 1
                            logger.info(f"✅ Cloudflare DNS successful!")
                            return response, method
            
            elif method == AccessMethod.DNS_GOOGLE:
                # Method 3: DNS over HTTPS (Google)
                hostname = url.split("//")[1].split("/")[0]
                ip = await self.resolve_dns_google(hostname)
                
                if ip:
                    url_with_ip = url.replace(hostname, ip)
                    logger.info(f"🔗 Trying Google DNS: {hostname} -> {ip}")
                    
                    async with httpx.AsyncClient(timeout=10.0) as client:
                        headers = kwargs.get("headers", {})
                        headers["Host"] = hostname
                        kwargs["headers"] = headers
                        
                        response = await client.get(url_with_ip, **kwargs)
                        if response.status_code == 200:
                            self.success_stats[method]["success"] += 1
                            logger.info(f"✅ Google DNS successful!")
                            return response, method
            
            elif method == AccessMethod.PROXY:
                # Method 4: Free Proxy
                proxies = await self.get_free_proxies(limit=5)
                
                for proxy in proxies:
                    try:
                        logger.info(f"🔗 Trying PROXY: {proxy}")
                        async with httpx.AsyncClient(timeout=10.0) as client:
                            response = await client.get(
                                url,
                                proxy=f"http://{proxy}",
                                **kwargs
                            )
                            if response.status_code == 200:
                                self.success_stats[method]["success"] += 1
                                logger.info(f"✅ PROXY {proxy} successful!")
                                return response, method
                    except:
                        continue
            
            elif method == AccessMethod.DNS_PROXY:
                # Method 5: DNS + Proxy (Most Powerful!)
                hostname = url.split("//")[1].split("/")[0]
                ip = await self.resolve_dns_cloudflare(hostname)
                
                if not ip:
                    ip = await self.resolve_dns_google(hostname)
                
                if ip:
                    url_with_ip = url.replace(hostname, ip)
                    proxies = await self.get_free_proxies(limit=3)
                    
                    for proxy in proxies:
                        try:
                            logger.info(f"🔗 Trying DNS+PROXY: {hostname}->{ip} via {proxy}")
                            async with httpx.AsyncClient(timeout=10.0) as client:
                                headers = kwargs.get("headers", {})
                                headers["Host"] = hostname
                                kwargs["headers"] = headers
                                
                                response = await client.get(
                                    url_with_ip,
                                    proxy=f"http://{proxy}",
                                    **kwargs
                                )
                                if response.status_code == 200:
                                    self.success_stats[method]["success"] += 1
                                    logger.info(f"✅ DNS+PROXY successful!")
                                    return response, method
                        except:
                            continue
        
        except Exception as e:
            logger.warning(f"⚠️ Method {method.value} failed: {e}")
        
        self.success_stats[method]["fail"] += 1
        return None, method
    
    async def smart_fetch(self, url: str, force_smart: bool = False, **kwargs) -> Optional[httpx.Response]:
        """
        Smart fetch with automatic fallback through all methods
        دریافت هوشمند با فالبک خودکار از همه روش‌ها
        
        اولویت‌ها:
        1. بررسی می‌کنه که آیا این API نیاز به Proxy/DNS داره یا نه
        2. اگر نیاز نداره، فقط DIRECT استفاده می‌کنه (سریع‌تر)
        3. اگر نیاز داره، از همه روش‌ها استفاده می‌کنه
        
        Args:
            url: آدرس API
            force_smart: اجبار به استفاده از Smart Access (حتی اگر لازم نباشه)
        """
        logger.info(f"\n{'='*60}")
        logger.info(f"🚀 SMART FETCH: {url}")
        
        # بررسی آیا این URL نیاز به Smart Access داره؟
        from backend.config.restricted_apis import get_access_config
        
        # استخراج domain
        if "://" in url:
            domain = url.split("://")[1].split("/")[0]
        else:
            domain = url.split("/")[0]
        
        config = get_access_config(domain)
        use_smart = config["use_smart_access"] or force_smart
        
        logger.info(f"📋 API: {config['api_name']}")
        logger.info(f"🔐 Access Level: {config['access_level'].value}")
        logger.info(f"🎯 Use Smart Access: {use_smart}")
        logger.info(f"{'='*60}")
        
        if not use_smart:
            # این API نیاز به Proxy/DNS نداره - فقط Direct
            logger.info(f"✅ Using DIRECT connection (no proxy/DNS needed)")
            
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.get(url, **kwargs)
                    
                    if response.status_code == 200:
                        self.success_stats[AccessMethod.DIRECT]["success"] += 1
                        logger.info(f"\n✅ SUCCESS with DIRECT connection")
                        logger.info(f"{'='*60}\n")
                        return response
            except Exception as e:
                logger.warning(f"⚠️ Direct connection failed: {e}")
        
        # استفاده از Fallback Order از config
        fallback_order = config.get("fallback_order", [
            "direct",
            "dns_cloudflare",
            "dns_google",
            "proxy",
            "dns_proxy"
        ])
        
        # تبدیل به AccessMethod
        method_map = {
            "direct": AccessMethod.DIRECT,
            "dns_cloudflare": AccessMethod.DNS_CLOUDFLARE,
            "dns_google": AccessMethod.DNS_GOOGLE,
            "proxy": AccessMethod.PROXY,
            "dns_proxy": AccessMethod.DNS_PROXY,
        }
        
        methods = [method_map.get(m, AccessMethod.DIRECT) for m in fallback_order]
        
        logger.info(f"🔄 Trying fallback methods: {fallback_order}")
        
        for method in methods:
            response, used_method = await self.fetch_with_method(url, method, **kwargs)
            
            if response and response.status_code == 200:
                logger.info(f"\n✅ SUCCESS with method: {used_method.value}")
                logger.info(f"{'='*60}\n")
                return response
            
            logger.warning(f"❌ Method {method.value} failed, trying next...")
        
        # All methods failed
        logger.error(f"\n❌ ALL METHODS FAILED for {url}")
        logger.error(f"{'='*60}\n")
        return None
    
    def get_statistics(self) -> Dict:
        """
        Get access statistics
        آمار دسترسی
        """
        total_success = sum(s["success"] for s in self.success_stats.values())
        total_fail = sum(s["fail"] for s in self.success_stats.values())
        total = total_success + total_fail
        
        stats = {
            "total_requests": total,
            "total_success": total_success,
            "total_failed": total_fail,
            "success_rate": f"{(total_success/total*100) if total > 0 else 0:.1f}%",
            "methods": {}
        }
        
        for method, counts in self.success_stats.items():
            method_total = counts["success"] + counts["fail"]
            stats["methods"][method.value] = {
                "success": counts["success"],
                "failed": counts["fail"],
                "success_rate": f"{(counts['success']/method_total*100) if method_total > 0 else 0:.1f}%"
            }
        
        return stats


# Global instance
smart_access_manager = SmartAccessManager()


__all__ = ["SmartAccessManager", "smart_access_manager", "AccessMethod"]

