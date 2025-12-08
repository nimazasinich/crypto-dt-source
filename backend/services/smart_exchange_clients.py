#!/usr/bin/env python3
"""
Smart Exchange Clients - Binance & KuCoin
Ultra-intelligent clients with:
- DNS over HTTPS (DoH)
- Multi-layer proxies (HTTP, SOCKS4, SOCKS5)
- Geo-block bypass
- Smart routing
- Auto-recovery
- NO API KEY required for public endpoints
"""

import httpx
import asyncio
import time
import random
import logging
from typing import Optional, Dict, List, Tuple
from urllib.parse import urlparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import dns.resolver

logger = logging.getLogger(__name__)


class SmartDNSResolver:
    """Smart DNS resolver with DoH (DNS over HTTPS)"""
    
    def __init__(self):
        # Free DNS over HTTPS services
        self.doh_providers = [
            {"name": "Cloudflare", "url": "https://cloudflare-dns.com/dns-query"},
            {"name": "Google", "url": "https://dns.google/resolve"},
            {"name": "Quad9", "url": "https://dns.quad9.net/dns-query"},
            {"name": "AdGuard", "url": "https://dns.adguard.com/dns-query"},
        ]
        self.dns_cache = {}
        
        # Public DNS servers
        self.public_dns = [
            "1.1.1.1",  # Cloudflare
            "8.8.8.8",  # Google
            "9.9.9.9",  # Quad9
            "208.67.222.222",  # OpenDNS
        ]
    
    async def resolve_with_doh(self, domain: str) -> Optional[str]:
        """Resolve DNS using DNS over HTTPS"""
        if domain in self.dns_cache:
            logger.debug(f"🎯 DNS Cache: {domain} -> {self.dns_cache[domain]}")
            return self.dns_cache[domain]
        
        for provider in self.doh_providers:
            try:
                params = {"name": domain, "type": "A"}
                headers = {"Accept": "application/dns-json"}
                
                async with httpx.AsyncClient(timeout=5.0) as client:
                    response = await client.get(
                        provider["url"],
                        params=params,
                        headers=headers
                    )
                    
                    if response.status_code == 200:
                        data = response.json()
                        if "Answer" in data and len(data["Answer"]) > 0:
                            ip = data["Answer"][0]["data"]
                            self.dns_cache[domain] = ip
                            logger.info(f"✅ DoH ({provider['name']}): {domain} -> {ip}")
                            return ip
            except Exception as e:
                logger.debug(f"DoH {provider['name']} failed: {e}")
        
        return await self._fallback_dns(domain)
    
    async def _fallback_dns(self, domain: str) -> Optional[str]:
        """DNS fallback with public servers"""
        # Use asyncio for DNS resolution
        try:
            loop = asyncio.get_event_loop()
            ip = await loop.run_in_executor(None, self._resolve_sync, domain)
            if ip:
                self.dns_cache[domain] = ip
                return ip
        except:
            pass
        
        logger.error(f"❌ Failed to resolve {domain}")
        return None
    
    def _resolve_sync(self, domain: str) -> Optional[str]:
        """Synchronous DNS resolution"""
        import socket
        try:
            return socket.gethostbyname(domain)
        except:
            return None


class AdvancedProxyManager:
    """Advanced proxy manager with multiple sources and protocols"""
    
    def __init__(self):
        self.working_proxies = {
            'http': [],
            'socks4': [],
            'socks5': []
        }
        self.failed_proxies = set()
        self.last_fetch_time = 0
        self.fetch_interval = 300  # 5 minutes
        
        # Free proxy sources
        self.proxy_sources = [
            {
                "url": "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=5000&country=all&ssl=all&anonymity=elite",
                "type": "http"
            },
            {
                "url": "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks4&timeout=5000&country=all",
                "type": "socks4"
            },
            {
                "url": "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=socks5&timeout=5000&country=all",
                "type": "socks5"
            },
            {
                "url": "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/http.txt",
                "type": "http"
            },
            {
                "url": "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks4.txt",
                "type": "socks4"
            },
            {
                "url": "https://raw.githubusercontent.com/TheSpeedX/PROXY-List/master/socks5.txt",
                "type": "socks5"
            },
        ]
    
    async def fetch_proxies(self, force: bool = False) -> None:
        """Fetch proxies from multiple sources"""
        current_time = time.time()
        if not force and (current_time - self.last_fetch_time) < self.fetch_interval:
            return
        
        logger.info("🔄 Fetching fresh proxies...")
        
        async def fetch_from_source(source):
            try:
                async with httpx.AsyncClient(timeout=10.0) as client:
                    response = await client.get(source["url"])
                    if response.status_code == 200:
                        proxies = response.text.strip().split('\n')
                        return [(proxy.strip(), source["type"]) for proxy in proxies if proxy.strip()]
            except Exception as e:
                logger.debug(f"Failed to fetch from {source['url']}: {e}")
            return []
        
        # Parallel fetch from all sources
        tasks = [fetch_from_source(source) for source in self.proxy_sources]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        all_proxies = []
        for result in results:
            if isinstance(result, list):
                all_proxies.extend(result)
        
        # Remove duplicates
        unique_proxies = list(set(all_proxies))
        logger.info(f"📦 Fetched {len(unique_proxies)} unique proxies")
        
        # Test proxies (async)
        await self._test_proxies_async(unique_proxies[:30])  # Test first 30
        self.last_fetch_time = current_time
    
    async def _test_proxies_async(self, proxies: List[Tuple[str, str]]) -> None:
        """Test proxies asynchronously"""
        logger.info("🧪 Testing proxies...")
        
        async def test_proxy(proxy_info):
            proxy, proxy_type = proxy_info
            if proxy in self.failed_proxies:
                return None
            
            try:
                proxy_dict = self._format_proxy(proxy, proxy_type)
                
                # Use httpx with proxy
                timeout = httpx.Timeout(5.0)
                async with httpx.AsyncClient(proxies=proxy_dict, timeout=timeout) as client:
                    response = await client.get("https://api.binance.com/api/v3/ping")
                    
                    if response.status_code == 200:
                        return (proxy, proxy_type)
            except:
                self.failed_proxies.add(proxy)
            return None
        
        tasks = [test_proxy(p) for p in proxies]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        for result in results:
            if result and not isinstance(result, Exception):
                proxy, proxy_type = result
                if proxy not in [p[0] for p in self.working_proxies[proxy_type]]:
                    self.working_proxies[proxy_type].append((proxy, proxy_type))
                    logger.info(f"✅ Working proxy: {proxy} ({proxy_type})")
        
        total_working = sum(len(v) for v in self.working_proxies.values())
        logger.info(f"✅ Total working proxies: {total_working}")
    
    def _format_proxy(self, proxy: str, proxy_type: str) -> Dict:
        """Format proxy for use"""
        if proxy_type == 'http':
            return {
                "http://": f"http://{proxy}",
                "https://": f"http://{proxy}"
            }
        elif proxy_type in ['socks4', 'socks5']:
            return {
                "http://": f"{proxy_type}://{proxy}",
                "https://": f"{proxy_type}://{proxy}"
            }
        return {}
    
    def get_random_proxy(self) -> Optional[Dict]:
        """Get random working proxy"""
        # Select from all proxy types
        available_types = [k for k, v in self.working_proxies.items() if v]
        if not available_types:
            return None
        
        proxy_type = random.choice(available_types)
        proxy, _ = random.choice(self.working_proxies[proxy_type])
        return self._format_proxy(proxy, proxy_type)


class UltraSmartBinanceClient:
    """
    Ultra-smart Binance client with:
    - DNS over HTTPS
    - Multi-layer proxies (HTTP, SOCKS4, SOCKS5)
    - Smart routing
    - Auto-recovery
    - NO API KEY required (Public APIs only)
    """
    
    def __init__(self, enable_proxy: bool = False, enable_doh: bool = True):
        self.enable_proxy = enable_proxy
        self.enable_doh = enable_doh
        self.exchange_name = "Binance"
        
        # DNS and Proxy management
        self.dns_resolver = SmartDNSResolver()
        self.proxy_manager = AdvancedProxyManager()
        
        # Public Binance endpoints (NO API KEY needed)
        self.endpoints = [
            "https://api.binance.com",
            "https://api1.binance.com",
            "https://api2.binance.com",
            "https://api3.binance.com",
            "https://data-api.binance.vision",  # Public data
        ]
        
        self.current_endpoint_index = 0
        
        # User agents
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        ]
    
    async def _make_request(self, endpoint: str, params: Optional[Dict] = None,
                           retry_count: int = 0, max_retries: int = 5) -> Dict:
        """Smart request with all protection layers"""
        
        if retry_count >= max_retries:
            raise Exception(f"❌ Max retries reached for {self.exchange_name}")
        
        url = f"{self.endpoints[self.current_endpoint_index]}{endpoint}"
        
        # Prepare request settings
        headers = {
            "User-Agent": random.choice(self.user_agents),
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept-Encoding": "gzip, deflate, br",
            "Connection": "keep-alive",
        }
        
        # Prepare client kwargs
        client_kwargs = {
            "timeout": httpx.Timeout(15.0),
            "headers": headers,
            "follow_redirects": True
        }
        
        # Add proxy if enabled
        current_proxy = None
        if self.enable_proxy:
            current_proxy = self.proxy_manager.get_random_proxy()
            if current_proxy:
                client_kwargs["proxies"] = current_proxy
                logger.info(f"🔒 Using proxy for Binance")
        
        try:
            async with httpx.AsyncClient(**client_kwargs) as client:
                response = await client.get(url, params=params)
                
                if response.status_code == 200:
                    logger.info(f"✅ Binance success: {endpoint}")
                    return response.json()
                
                elif response.status_code == 451:
                    logger.warning(f"🚫 Geo-block (attempt {retry_count + 1}/{max_retries})")
                    return await self._handle_geo_block(endpoint, params, retry_count)
                
                elif response.status_code == 429:
                    wait_time = int(response.headers.get('Retry-After', 60))
                    logger.warning(f"⏱️ Rate limit, waiting {wait_time}s...")
                    await asyncio.sleep(wait_time)
                    return await self._make_request(endpoint, params, retry_count + 1, max_retries)
                
                elif response.status_code == 418:
                    logger.warning("🚫 IP banned, switching...")
                    if current_proxy:
                        proxy_str = list(current_proxy.values())[0]
                        self.proxy_manager.failed_proxies.add(proxy_str)
                    return await self._make_request(endpoint, params, retry_count + 1, max_retries)
                
                else:
                    logger.error(f"❌ HTTP {response.status_code}")
                    raise Exception(f"HTTP Error: {response.status_code}")
        
        except httpx.ProxyError:
            logger.warning("⚠️ Proxy failed, trying new one...")
            if current_proxy:
                proxy_str = list(current_proxy.values())[0]
                self.proxy_manager.failed_proxies.add(proxy_str)
            return await self._make_request(endpoint, params, retry_count + 1, max_retries)
        
        except httpx.TimeoutException:
            logger.warning("⏱️ Timeout, retrying...")
            return await self._make_request(endpoint, params, retry_count + 1, max_retries)
        
        except Exception as e:
            logger.error(f"❌ Request error: {str(e)}")
            if retry_count < max_retries - 1:
                await asyncio.sleep(2)
                return await self._make_request(endpoint, params, retry_count + 1, max_retries)
            raise
    
    async def _handle_geo_block(self, endpoint: str, params: Optional[Dict], retry_count: int) -> Dict:
        """Smart geo-blocking handling"""
        
        strategies = [
            ("🔄 Switching endpoint", self._switch_endpoint),
            ("🔄 Enabling proxy", self._enable_proxy_fallback),
        ]
        
        for strategy_name, strategy_func in strategies:
            try:
                logger.info(strategy_name)
                await strategy_func()
                await asyncio.sleep(2)
                return await self._make_request(endpoint, params, retry_count + 1)
            except:
                continue
        
        raise Exception(
            f"❌ Unable to bypass geo-block for {self.exchange_name}\n"
            "💡 Try enabling VPN or proxy"
        )
    
    async def _switch_endpoint(self):
        """Switch endpoint"""
        self.current_endpoint_index = (self.current_endpoint_index + 1) % len(self.endpoints)
        logger.info(f"🔄 Switched to: {self.endpoints[self.current_endpoint_index]}")
    
    async def _enable_proxy_fallback(self):
        """Enable proxy as fallback"""
        if not self.enable_proxy:
            self.enable_proxy = True
            await self.proxy_manager.fetch_proxies(force=True)
    
    # ===== Public Binance API Methods =====
    
    async def ping(self) -> Dict:
        """Test connection"""
        return await self._make_request("/api/v3/ping")
    
    async def get_server_time(self) -> Dict:
        """Get server time"""
        return await self._make_request("/api/v3/time")
    
    async def get_ticker_price(self, symbol: str = "BTCUSDT") -> Dict:
        """Get current price"""
        return await self._make_request("/api/v3/ticker/price", {"symbol": symbol})
    
    async def get_all_prices(self) -> List[Dict]:
        """Get all prices"""
        return await self._make_request("/api/v3/ticker/price")
    
    async def get_ticker_24h(self, symbol: str = "BTCUSDT") -> Dict:
        """Get 24h statistics"""
        return await self._make_request("/api/v3/ticker/24hr", {"symbol": symbol})
    
    async def get_klines(self, symbol: str = "BTCUSDT", interval: str = "1h",
                        limit: int = 1000, start_time: Optional[int] = None,
                        end_time: Optional[int] = None) -> List:
        """
        Get candlestick data
        
        Intervals: 1m, 3m, 5m, 15m, 30m, 1h, 2h, 4h, 6h, 8h, 12h, 1d, 3d, 1w, 1M
        """
        params = {
            "symbol": symbol,
            "interval": interval,
            "limit": min(limit, 1000)
        }
        if start_time:
            params["startTime"] = start_time
        if end_time:
            params["endTime"] = end_time
        
        return await self._make_request("/api/v3/klines", params)
    
    async def get_orderbook(self, symbol: str = "BTCUSDT", limit: int = 100) -> Dict:
        """Get order book"""
        return await self._make_request("/api/v3/depth", {
            "symbol": symbol,
            "limit": min(limit, 5000)
        })


class UltraSmartKuCoinClient:
    """
    Ultra-smart KuCoin client with same features as Binance
    - NO API KEY required (Public APIs only)
    - DNS over HTTPS
    - Multi-layer proxies
    """
    
    def __init__(self, enable_proxy: bool = False, enable_doh: bool = True):
        self.enable_proxy = enable_proxy
        self.enable_doh = enable_doh
        self.exchange_name = "KuCoin"
        
        # DNS and Proxy management
        self.dns_resolver = SmartDNSResolver()
        self.proxy_manager = AdvancedProxyManager()
        
        # Public KuCoin endpoints
        self.endpoints = [
            "https://api.kucoin.com",
            "https://api-futures.kucoin.com",
        ]
        
        self.current_endpoint_index = 0
        
        # User agents
        self.user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
        ]
    
    async def _make_request(self, endpoint: str, params: Optional[Dict] = None,
                           retry_count: int = 0, max_retries: int = 5) -> Dict:
        """Smart KuCoin request"""
        
        if retry_count >= max_retries:
            raise Exception(f"❌ Max retries reached for {self.exchange_name}")
        
        url = f"{self.endpoints[self.current_endpoint_index]}{endpoint}"
        
        headers = {
            "User-Agent": random.choice(self.user_agents),
            "Accept": "application/json",
        }
        
        client_kwargs = {
            "timeout": httpx.Timeout(15.0),
            "headers": headers,
            "follow_redirects": True
        }
        
        current_proxy = None
        if self.enable_proxy:
            current_proxy = self.proxy_manager.get_random_proxy()
            if current_proxy:
                client_kwargs["proxies"] = current_proxy
        
        try:
            async with httpx.AsyncClient(**client_kwargs) as client:
                response = await client.get(url, params=params)
                
                if response.status_code == 200:
                    data = response.json()
                    if data.get('code') == '200000':  # KuCoin success
                        logger.info(f"✅ KuCoin success: {endpoint}")
                        return data.get('data', data)
                    else:
                        raise Exception(f"KuCoin API Error: {data.get('msg')}")
                
                elif response.status_code == 429:
                    await asyncio.sleep(60)
                    return await self._make_request(endpoint, params, retry_count + 1, max_retries)
                
                else:
                    raise Exception(f"HTTP Error: {response.status_code}")
        
        except Exception as e:
            logger.error(f"❌ KuCoin error: {str(e)}")
            if retry_count < max_retries - 1:
                await asyncio.sleep(2)
                return await self._make_request(endpoint, params, retry_count + 1, max_retries)
            raise
    
    # ===== Public KuCoin API Methods =====
    
    async def get_ticker_price(self, symbol: str = "BTC-USDT") -> Dict:
        """Get current price"""
        result = await self._make_request("/api/v1/market/orderbook/level1", {"symbol": symbol})
        return {
            "symbol": symbol,
            "price": result.get('price', '0')
        }
    
    async def get_ticker_24h(self, symbol: str = "BTC-USDT") -> Dict:
        """Get 24h statistics"""
        return await self._make_request("/api/v1/market/stats", {"symbol": symbol})
    
    async def get_klines(self, symbol: str = "BTC-USDT", interval: str = "1hour",
                        start_time: Optional[int] = None, end_time: Optional[int] = None) -> List:
        """
        Get candlestick data
        
        Intervals: 1min, 3min, 5min, 15min, 30min, 1hour, 2hour, 4hour, 6hour, 8hour, 12hour, 1day, 1week
        """
        params = {
            "symbol": symbol,
            "type": interval
        }
        if start_time:
            params["startAt"] = start_time
        if end_time:
            params["endAt"] = end_time
        
        return await self._make_request("/api/v1/market/candles", params)
    
    async def get_orderbook(self, symbol: str = "BTC-USDT") -> Dict:
        """Get order book"""
        return await self._make_request("/api/v1/market/orderbook/level2_100", {"symbol": symbol})


__all__ = [
    "UltraSmartBinanceClient",
    "UltraSmartKuCoinClient",
    "SmartDNSResolver",
    "AdvancedProxyManager"
]
