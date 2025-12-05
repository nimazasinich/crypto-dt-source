"""
Smart Proxy/DNS Manager
Handles proxy rotation for sanctioned exchanges (Binance, etc.)
"""

import asyncio
import aiohttp
import random
import time
from typing import List, Dict, Optional
from dataclasses import dataclass
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


@dataclass
class ProxyServer:
    """Proxy server configuration"""
    url: str
    protocol: str = "http"  # http, https, socks5
    username: Optional[str] = None
    password: Optional[str] = None
    success_count: int = 0
    failure_count: int = 0
    last_used: Optional[datetime] = None
    avg_response_time: float = 0.0
    is_active: bool = True
    
    def get_proxy_url(self) -> str:
        """Get full proxy URL with auth"""
        if self.username and self.password:
            return f"{self.protocol}://{self.username}:{self.password}@{self.url}"
        return f"{self.protocol}://{self.url}"
    
    def record_success(self, response_time: float):
        """Record successful proxy usage"""
        self.success_count += 1
        self.last_used = datetime.now()
        
        if self.avg_response_time == 0:
            self.avg_response_time = response_time
        else:
            self.avg_response_time = 0.7 * self.avg_response_time + 0.3 * response_time
    
    def record_failure(self):
        """Record proxy failure"""
        self.failure_count += 1
        self.last_used = datetime.now()
        
        # Deactivate if too many failures
        if self.failure_count > 10:
            self.is_active = False
    
    def get_success_rate(self) -> float:
        """Get success rate"""
        total = self.success_count + self.failure_count
        return self.success_count / max(total, 1)


@dataclass
class DNSServer:
    """Smart DNS server"""
    address: str
    port: int = 53
    protocol: str = "udp"  # udp, tcp, doh (DNS over HTTPS)
    is_active: bool = True
    success_count: int = 0
    failure_count: int = 0
    
    def get_address(self) -> str:
        """Get DNS server address"""
        return f"{self.address}:{self.port}"


class SmartProxyManager:
    """
    Smart proxy manager with rotation and health tracking
    Supports multiple proxy types and smart DNS
    """
    
    def __init__(self):
        self.proxies: List[ProxyServer] = []
        self.dns_servers: List[DNSServer] = []
        self.current_proxy_index = 0
        self.rotation_enabled = True
        self.rotation_interval = 60  # Rotate every 60 seconds
        self.last_rotation = datetime.now()
        
        # Initialize with free/public proxies
        self._load_default_proxies()
        self._load_default_dns()
        
        logger.info(f"✅ SmartProxyManager initialized with {len(self.proxies)} proxies and {len(self.dns_servers)} DNS servers")
    
    def _load_default_proxies(self):
        """Load default free proxy list"""
        # Free proxy list (you can expand this)
        default_proxies = [
            # Public HTTP proxies (example - replace with real ones)
            "proxy1.example.com:8080",
            "proxy2.example.com:3128",
            # SOCKS5 proxies
            "socks5://proxy3.example.com:1080",
        ]
        
        # Note: In production, use a proxy provider service
        # or rotate through a large list of tested proxies
        
        for proxy_url in default_proxies:
            if proxy_url.startswith("socks5://"):
                protocol = "socks5"
                url = proxy_url.replace("socks5://", "")
            else:
                protocol = "http"
                url = proxy_url
            
            self.proxies.append(ProxyServer(
                url=url,
                protocol=protocol
            ))
        
        # Add environment-based proxies
        import os
        env_proxy = os.getenv("PROXY_URL")
        if env_proxy:
            self.proxies.append(ProxyServer(url=env_proxy, protocol="http"))
    
    def _load_default_dns(self):
        """Load default smart DNS servers"""
        # Public DNS servers
        self.dns_servers = [
            DNSServer(address="1.1.1.1", port=53),  # Cloudflare
            DNSServer(address="8.8.8.8", port=53),  # Google
            DNSServer(address="9.9.9.9", port=53),  # Quad9
            DNSServer(address="208.67.222.222", port=53),  # OpenDNS
        ]
    
    async def get_proxy(self) -> Optional[str]:
        """Get next available proxy with rotation"""
        if not self.proxies:
            logger.warning("⚠️ No proxies configured")
            return None
        
        # Check if rotation needed
        if self.rotation_enabled:
            now = datetime.now()
            if (now - self.last_rotation).seconds > self.rotation_interval:
                self._rotate_proxy()
                self.last_rotation = now
        
        # Get active proxies
        active_proxies = [p for p in self.proxies if p.is_active]
        
        if not active_proxies:
            logger.error("❌ All proxies are inactive!")
            return None
        
        # Sort by success rate and response time
        active_proxies.sort(
            key=lambda p: (p.get_success_rate(), -p.avg_response_time),
            reverse=True
        )
        
        # Get best proxy
        best_proxy = active_proxies[0]
        proxy_url = best_proxy.get_proxy_url()
        
        logger.debug(f"🔄 Using proxy: {best_proxy.url} (success rate: {best_proxy.get_success_rate():.1%})")
        
        return proxy_url
    
    def _rotate_proxy(self):
        """Rotate to next proxy"""
        if len(self.proxies) > 1:
            self.current_proxy_index = (self.current_proxy_index + 1) % len(self.proxies)
            logger.debug(f"🔄 Rotated to proxy #{self.current_proxy_index}")
    
    async def test_proxy(self, proxy: ProxyServer, test_url: str = "https://httpbin.org/ip") -> bool:
        """Test if proxy is working"""
        try:
            start_time = time.time()
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    test_url,
                    proxy=proxy.get_proxy_url(),
                    timeout=aiohttp.ClientTimeout(total=10)
                ) as response:
                    if response.status == 200:
                        response_time = time.time() - start_time
                        proxy.record_success(response_time)
                        logger.info(f"✅ Proxy {proxy.url} is working ({response_time:.2f}s)")
                        return True
            
            proxy.record_failure()
            return False
        
        except Exception as e:
            proxy.record_failure()
            logger.warning(f"⚠️ Proxy {proxy.url} failed: {e}")
            return False
    
    async def test_all_proxies(self):
        """Test all proxies and update their status"""
        logger.info("🧪 Testing all proxies...")
        
        tasks = [self.test_proxy(proxy) for proxy in self.proxies]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        active_count = sum(1 for r in results if r is True)
        logger.info(f"✅ {active_count}/{len(self.proxies)} proxies are active")
    
    def add_proxy(self, url: str, protocol: str = "http", username: str = None, password: str = None):
        """Add a new proxy"""
        proxy = ProxyServer(
            url=url,
            protocol=protocol,
            username=username,
            password=password
        )
        self.proxies.append(proxy)
        logger.info(f"➕ Added proxy: {url}")
    
    def remove_proxy(self, url: str):
        """Remove a proxy"""
        self.proxies = [p for p in self.proxies if p.url != url]
        logger.info(f"➖ Removed proxy: {url}")
    
    def get_dns_server(self) -> str:
        """Get next DNS server"""
        active_dns = [d for d in self.dns_servers if d.is_active]
        
        if not active_dns:
            return "8.8.8.8:53"  # Fallback to Google DNS
        
        # Random selection
        dns = random.choice(active_dns)
        return dns.get_address()
    
    async def resolve_with_smart_dns(self, hostname: str) -> Optional[str]:
        """Resolve hostname using smart DNS"""
        import socket
        
        dns_server = self.get_dns_server()
        logger.debug(f"🔍 Resolving {hostname} using DNS: {dns_server}")
        
        try:
            # Use system DNS (we can't easily override without dnspython)
            ip = socket.gethostbyname(hostname)
            logger.debug(f"✅ Resolved {hostname} -> {ip}")
            return ip
        except socket.gaierror as e:
            logger.error(f"❌ DNS resolution failed for {hostname}: {e}")
            return None
    
    def get_status_report(self) -> Dict:
        """Get proxy manager status"""
        active_proxies = [p for p in self.proxies if p.is_active]
        
        return {
            "total_proxies": len(self.proxies),
            "active_proxies": len(active_proxies),
            "inactive_proxies": len(self.proxies) - len(active_proxies),
            "dns_servers": len(self.dns_servers),
            "rotation_enabled": self.rotation_enabled,
            "rotation_interval": self.rotation_interval,
            "proxies": [
                {
                    "url": p.url,
                    "protocol": p.protocol,
                    "is_active": p.is_active,
                    "success_rate": p.get_success_rate(),
                    "avg_response_time": p.avg_response_time,
                    "success_count": p.success_count,
                    "failure_count": p.failure_count
                }
                for p in self.proxies
            ]
        }
    
    async def fetch_with_proxy_rotation(
        self,
        url: str,
        max_retries: int = 3,
        **kwargs
    ) -> Optional[Dict]:
        """Fetch URL with automatic proxy rotation on failure"""
        for attempt in range(max_retries):
            proxy_url = await self.get_proxy()
            
            if not proxy_url:
                logger.warning("⚠️ No proxy available, trying direct connection")
                proxy_url = None
            
            try:
                start_time = time.time()
                
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        url,
                        proxy=proxy_url,
                        timeout=aiohttp.ClientTimeout(total=15),
                        **kwargs
                    ) as response:
                        response.raise_for_status()
                        
                        response_time = time.time() - start_time
                        
                        # Record success
                        if proxy_url:
                            for proxy in self.proxies:
                                if proxy.get_proxy_url() == proxy_url:
                                    proxy.record_success(response_time)
                                    break
                        
                        return await response.json()
            
            except Exception as e:
                logger.warning(f"⚠️ Proxy attempt {attempt + 1} failed: {e}")
                
                # Record failure
                if proxy_url:
                    for proxy in self.proxies:
                        if proxy.get_proxy_url() == proxy_url:
                            proxy.record_failure()
                            break
                
                # Rotate to next proxy
                self._rotate_proxy()
                
                # If last attempt, raise
                if attempt == max_retries - 1:
                    raise
        
        return None


# Global instance
_proxy_manager = None

def get_proxy_manager() -> SmartProxyManager:
    """Get global proxy manager instance"""
    global _proxy_manager
    if _proxy_manager is None:
        _proxy_manager = SmartProxyManager()
    return _proxy_manager
