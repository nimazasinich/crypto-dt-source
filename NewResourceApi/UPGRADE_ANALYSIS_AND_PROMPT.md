# 🚀 تحلیل جامع و پرامپت ارتقای پروژه Crypto Intelligence Hub

## 📊 تحلیل وضع فعلی

### ✅ نقاط قوت پروژه
1. **معماری قوی**: استفاده از FastAPI + Flask با Docker
2. **منابع متنوع**: 50+ provider مختلف برای داده‌های کریپتو
3. **پشتیبانی از Proxy**: سیستم Smart Proxy Manager برای دور زدن محدودیت‌ها
4. **WebSocket**: پشتیبانی از real-time data
5. **Database**: استفاده از SQLAlchemy برای persistence
6. **AI/ML**: ادغام با Hugging Face models

### ⚠️ نقاط ضعف و مشکلات

#### 1. **مدیریت Proxy و DNS**
```python
# مشکل فعلی:
- Proxy های نمونه (example.com) که کار نمی‌کنند
- عدم پیاده‌سازی واقعی smart DNS
- نداشتن fallback strategy مناسب برای Binance و CoinGecko
```

#### 2. **رابط کاربری**
```
- رابط کاربری استاتیک (HTML/CSS/JS)
- عدم استفاده از فریمورک مدرن (React/Vue)
- تجربه کاربری محدود
- عدم پشتیبانی موبایل مناسب
```

#### 3. **Performance و Scalability**
```
- نبود load balancing
- عدم استفاده کامل از caching
- نداشتن CDN برای static assets
```

#### 4. **Security و Rate Limiting**
```python
# نیازهای امنیتی:
- نبود API authentication مناسب
- Rate limiting محدود
- نداشتن CORS policy دقیق
```

#### 5. **Monitoring و Logging**
```
- لاگینگ ساده و غیرمتمرکز
- نبود metrics و analytics
- عدم monitoring سلامت providers
```

---

## 🎯 پرامپت جامع برای ارتقای پروژه

### مرحله 1: ارتقای Smart Proxy Manager

```
من یک سیستم جمع‌آوری داده کریپتو دارم که باید از proxy و DNS هوشمند برای دسترسی به Binance و CoinGecko استفاده کنه (این APIها در برخی کشورها فیلتر هستند).

**نیازمندی‌ها:**

1. **Smart Proxy System** با قابلیت‌های زیر:
   - ادغام با free proxy providers مثل ProxyScrape، Free-Proxy-List
   - Auto-refresh و validation پروکسی‌ها هر 5 دقیقه
   - Health check برای همه proxies
   - Load balancing هوشمند بین proxies
   - Fallback به direct connection در صورت عدم دسترسی proxy

2. **Dynamic DNS Resolution**:
   - استفاده از DoH (DNS over HTTPS) با Cloudflare/Google
   - DNS caching برای بهینه‌سازی
   - Fallback DNS servers
   - Automatic retry با DNS مختلف

3. **Provider-Specific Routing**:
   - تشخیص اتوماتیک نیاز به proxy (برای Binance و CoinGecko)
   - مسیریابی مستقیم برای provider های دیگر
   - Configurable routing rules

**کدی که باید بهبود داده بشه:**
- `/core/smart_proxy_manager.py` - سیستم فعلی ناقص است
- نیاز به ادغام واقعی با proxy providers
- پیاده‌سازی DNS over HTTPS
- افزودن retry logic و circuit breaker pattern

**خروجی مورد نیاز:**
کد کامل و عملیاتی برای `smart_proxy_manager.py` که:
- از API های رایگان proxy استفاده کند
- Health check اتوماتیک داشته باشد
- Load balancing هوشمند انجام دهد
- Logging و metrics کامل داشته باشد
```

---

### مرحله 2: ارتقای رابط کاربری به React/Next.js

```
رابط کاربری فعلی من HTML/CSS/JS ساده است. می‌خواهم آن را به یک داشبورد مدرن React/Next.js ارتقا دهم.

**نیازمندی‌های UI/UX:**

1. **داشبورد اصلی** شامل:
   - Real-time price ticker برای top 20 coins
   - نمودارهای TradingView/Recharts برای نمایش OHLC
   - News feed با فیلتر sentiment
   - Provider health status
   - Search و filter پیشرفته

2. **صفحه تحلیل** با:
   - نمودارهای تکنیکال (RSI, MACD, BB)
   - On-chain metrics
   - Social sentiment analysis
   - AI-powered predictions

3. **صفحه Providers** برای:
   - نمایش وضعیت همه providers
   - Test connectivity
   - Enable/disable providers
   - نمایش rate limits و usage

4. **تم دارک/لایت** با طراحی مدرن Glassmorphism

**استک فنی پیشنهادی:**
```typescript
// Tech Stack
{
  "framework": "Next.js 14 (App Router)",
  "ui": "Shadcn/ui + Tailwind CSS",
  "charts": "Recharts + TradingView Lightweight Charts",
  "state": "Zustand",
  "api": "SWR for data fetching",
  "websocket": "Socket.io-client",
  "icons": "Lucide React"
}
```

**خروجی مورد نیاز:**
ساختار کامل پروژه Next.js شامل:
- Component structure
- API routes integration با FastAPI backend
- Real-time WebSocket integration
- Responsive design
- Dark/Light theme
- Persian RTL support (در صورت نیاز)
```

---

### مرحله 3: بهبود System Architecture

```
می‌خواهم معماری سیستم را بهینه کنم تا scalable و maintainable باشد.

**بهبودهای مورد نیاز:**

1. **Caching Strategy**:
```python
# Redis برای caching
cache_config = {
    "price_data": "60 seconds TTL",
    "ohlcv_data": "5 minutes TTL",
    "news": "10 minutes TTL",
    "provider_health": "30 seconds TTL"
}
```

2. **Rate Limiting** با استفاده از `slowapi`:
```python
# Per-endpoint rate limits
rate_limits = {
    "/api/prices": "100/minute",
    "/api/ohlcv": "50/minute",
    "/api/news": "30/minute",
    "/ws/*": "No limit (WebSocket)"
}
```

3. **Background Workers** برای:
- جمع‌آوری داده‌های OHLCV هر 1 دقیقه
- Scraping news هر 5 دقیقه
- Provider health checks هر 30 ثانیه
- Database cleanup هر 24 ساعت

4. **Error Handling & Resilience**:
```python
# Circuit breaker pattern
from circuitbreaker import circuit

@circuit(failure_threshold=5, recovery_timeout=60)
async def fetch_from_provider(provider_name: str):
    # Implementation with retry logic
    pass
```

**خروجی مورد نیاز:**
- کد کامل برای workers با APScheduler/Celery
- Redis integration برای caching
- Circuit breaker implementation
- Comprehensive error handling
```

---

### مرحله 4: Monitoring و Observability

```
نیاز به یک سیستم جامع monitoring دارم.

**نیازمندی‌ها:**

1. **Metrics Collection**:
```python
# Metrics to track
metrics = {
    "api_requests_total": "Counter",
    "api_response_time": "Histogram",
    "provider_requests": "Counter by provider",
    "provider_failures": "Counter",
    "cache_hits": "Counter",
    "active_websocket_connections": "Gauge"
}
```

2. **Logging با Structured Logs**:
```python
import structlog

logger = structlog.get_logger()
logger.info("provider_request", 
    provider="binance", 
    endpoint="/api/v3/ticker", 
    duration_ms=150,
    status="success"
)
```

3. **Health Checks**:
```python
@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "providers": {
            "binance": "ok",
            "coingecko": "ok",
            ...
        },
        "database": "connected",
        "cache": "connected",
        "uptime": "2d 5h 30m"
    }
```

**خروجی مورد نیاز:**
- کد monitoring با Prometheus metrics
- Structured logging setup
- Health check endpoints
- Dashboard template برای Grafana (optional)
```

---

### مرحله 5: Testing و Documentation

```
نیاز به test coverage و documentation جامع دارم.

**Testing Requirements:**

1. **Unit Tests** برای:
```python
# Test examples
def test_proxy_manager():
    """Test proxy rotation and health checks"""
    pass

def test_data_collectors():
    """Test each provider's data collection"""
    pass

def test_api_endpoints():
    """Test all FastAPI endpoints"""
    pass
```

2. **Integration Tests**:
```python
async def test_end_to_end_flow():
    """Test complete data flow from provider to API"""
    pass
```

3. **Load Testing** با locust:
```python
from locust import HttpUser, task

class CryptoAPIUser(HttpUser):
    @task
    def get_prices(self):
        self.client.get("/api/prices")
```

**Documentation:**
- API documentation با OpenAPI/Swagger
- راهنمای استقرار در Hugging Face Spaces
- راهنمای توسعه‌دهنده
- نمونه کدهای استفاده از API

**خروجی مورد نیاز:**
- Test suite کامل با pytest
- Load testing scripts
- Comprehensive documentation
```

---

## 📋 Priority List برای پیاده‌سازی

### High Priority (حیاتی)
1. ✅ اصلاح Smart Proxy Manager برای Binance/CoinGecko
2. ✅ پیاده‌سازی DNS over HTTPS
3. ✅ افزودن Caching با Redis
4. ✅ بهبود Error Handling

### Medium Priority (مهم)
5. ⚡ ارتقای UI به React/Next.js
6. ⚡ پیاده‌سازی Background Workers
7. ⚡ افزودن Monitoring و Metrics
8. ⚡ Rate Limiting پیشرفته

### Low Priority (اختیاری اما مفید)
9. 📝 Testing Suite
10. 📝 Documentation
11. 📝 Load Testing
12. 📝 CI/CD Pipeline

---

## 🔧 کدهای نمونه برای شروع سریع

### نمونه Smart Proxy Manager بهبود یافته:

```python
"""
Smart Proxy Manager v2.0
با ادغام واقعی proxy providers و DNS over HTTPS
"""

import aiohttp
import asyncio
from typing import List, Optional
from datetime import datetime, timedelta
import logging

logger = logging.getLogger(__name__)


class ProxyProvider:
    """Base class for proxy providers"""
    
    async def fetch_proxies(self) -> List[str]:
        """Fetch proxy list from provider"""
        raise NotImplementedError


class ProxyScrapeProvider(ProxyProvider):
    """Free proxy provider: ProxyScrape.com"""
    
    BASE_URL = "https://api.proxyscrape.com/v2/"
    
    async def fetch_proxies(self) -> List[str]:
        params = {
            "request": "displayproxies",
            "protocol": "http",
            "timeout": "10000",
            "country": "all",
            "ssl": "all",
            "anonymity": "elite"
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.get(self.BASE_URL, params=params) as resp:
                text = await resp.text()
                proxies = [p.strip() for p in text.split('\n') if p.strip()]
                logger.info(f"✅ Fetched {len(proxies)} proxies from ProxyScrape")
                return proxies


class FreeProxyListProvider(ProxyProvider):
    """Scraper for free-proxy-list.net"""
    
    async def fetch_proxies(self) -> List[str]:
        # Implementation for scraping free-proxy-list.net
        # Use BeautifulSoup or similar
        pass


class DNSOverHTTPS:
    """DNS over HTTPS implementation"""
    
    CLOUDFLARE_DOH = "https://cloudflare-dns.com/dns-query"
    GOOGLE_DOH = "https://dns.google/resolve"
    
    async def resolve(self, hostname: str, use_provider: str = "cloudflare") -> Optional[str]:
        """Resolve hostname using DoH"""
        
        url = self.CLOUDFLARE_DOH if use_provider == "cloudflare" else self.GOOGLE_DOH
        
        params = {
            "name": hostname,
            "type": "A"
        }
        
        headers = {
            "accept": "application/dns-json"
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params, headers=headers) as resp:
                    data = await resp.json()
                    
                    if "Answer" in data and len(data["Answer"]) > 0:
                        ip = data["Answer"][0]["data"]
                        logger.info(f"🔍 Resolved {hostname} -> {ip} via {use_provider}")
                        return ip
                    
                    logger.warning(f"⚠️ No DNS answer for {hostname}")
                    return None
        
        except Exception as e:
            logger.error(f"❌ DoH resolution failed: {e}")
            return None


class SmartProxyManagerV2:
    """Enhanced Smart Proxy Manager"""
    
    def __init__(self):
        self.proxy_providers = [
            ProxyScrapeProvider(),
            # FreeProxyListProvider(),
        ]
        
        self.doh = DNSOverHTTPS()
        self.proxies: List[dict] = []
        self.last_refresh = None
        self.refresh_interval = timedelta(minutes=5)
        
        # Providers that need proxy/DNS
        self.restricted_providers = ["binance", "coingecko"]
    
    async def initialize(self):
        """Initialize and fetch initial proxy list"""
        await self.refresh_proxies()
    
    async def refresh_proxies(self):
        """Refresh proxy list from all providers"""
        logger.info("🔄 Refreshing proxy list...")
        
        all_proxies = []
        for provider in self.proxy_providers:
            try:
                proxies = await provider.fetch_proxies()
                all_proxies.extend(proxies)
            except Exception as e:
                logger.error(f"Failed to fetch from provider: {e}")
        
        # Test proxies and keep working ones
        working_proxies = await self._test_proxies(all_proxies[:20])  # Test first 20
        
        self.proxies = [
            {
                "url": proxy,
                "tested_at": datetime.now(),
                "success_count": 0,
                "fail_count": 0
            }
            for proxy in working_proxies
        ]
        
        self.last_refresh = datetime.now()
        logger.info(f"✅ Proxy list refreshed: {len(self.proxies)} working proxies")
    
    async def _test_proxies(self, proxy_list: List[str]) -> List[str]:
        """Test proxies and return working ones"""
        working = []
        
        async def test_proxy(proxy: str):
            try:
                async with aiohttp.ClientSession() as session:
                    async with session.get(
                        "https://httpbin.org/ip",
                        proxy=f"http://{proxy}",
                        timeout=aiohttp.ClientTimeout(total=5)
                    ) as resp:
                        if resp.status == 200:
                            working.append(proxy)
            except:
                pass
        
        await asyncio.gather(*[test_proxy(p) for p in proxy_list], return_exceptions=True)
        return working
    
    async def get_proxy_for_provider(self, provider_name: str) -> Optional[str]:
        """Get proxy if needed for provider"""
        
        # Check if provider needs proxy
        if provider_name.lower() not in self.restricted_providers:
            return None  # Direct connection
        
        # Refresh if needed
        if not self.proxies or (datetime.now() - self.last_refresh) > self.refresh_interval:
            await self.refresh_proxies()
        
        if not self.proxies:
            logger.warning("⚠️ No working proxies available!")
            return None
        
        # Get best proxy (least failures)
        best_proxy = min(self.proxies, key=lambda p: p['fail_count'])
        return f"http://{best_proxy['url']}"
    
    async def resolve_hostname(self, hostname: str) -> Optional[str]:
        """Resolve hostname using DoH"""
        return await self.doh.resolve(hostname)


# Global instance
proxy_manager = SmartProxyManagerV2()
```

### نمونه استفاده در Collectors:

```python
async def fetch_binance_data(symbol: str):
    """Fetch data from Binance with proxy support"""
    
    # Get proxy
    proxy = await proxy_manager.get_proxy_for_provider("binance")
    
    # Resolve hostname if needed
    # ip = await proxy_manager.resolve_hostname("api.binance.com")
    
    url = f"https://api.binance.com/api/v3/ticker/24hr"
    params = {"symbol": symbol}
    
    async with aiohttp.ClientSession() as session:
        try:
            async with session.get(
                url,
                params=params,
                proxy=proxy,  # Will be None for non-restricted providers
                timeout=aiohttp.ClientTimeout(total=10)
            ) as resp:
                return await resp.json()
        
        except Exception as e:
            logger.error(f"Binance fetch failed: {e}")
            # Fallback or retry logic
            return None
```

---

## 📦 فایل‌های کلیدی که باید بهبود داده شوند

1. **`/core/smart_proxy_manager.py`** - اولویت 1
2. **`/workers/market_data_worker.py`** - ادغام با proxy manager
3. **`/workers/ohlc_data_worker.py`** - ادغام با proxy manager
4. **`/static/*`** - جایگزینی با React/Next.js
5. **`/api/endpoints.py`** - افزودن rate limiting و caching
6. **`/monitoring/health_checker.py`** - بهبود health checks
7. **`requirements.txt`** - افزودن dependencies جدید

---

## 🎨 نمونه Component React برای Dashboard

```typescript
// components/PriceTicker.tsx
'use client'

import { useEffect, useState } from 'react'
import { Card } from '@/components/ui/card'

interface CoinPrice {
  symbol: string
  price: number
  change24h: number
}

export function PriceTicker() {
  const [prices, setPrices] = useState<CoinPrice[]>([])
  
  useEffect(() => {
    // WebSocket connection
    const ws = new WebSocket('ws://localhost:7860/ws/prices')
    
    ws.onmessage = (event) => {
      const data = JSON.parse(event.data)
      setPrices(data.prices)
    }
    
    return () => ws.close()
  }, [])
  
  return (
    <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
      {prices.map((coin) => (
        <Card key={coin.symbol} className="p-4">
          <div className="flex items-center justify-between">
            <span className="font-bold">{coin.symbol}</span>
            <span className={coin.change24h >= 0 ? 'text-green-500' : 'text-red-500'}>
              {coin.change24h.toFixed(2)}%
            </span>
          </div>
          <div className="text-2xl font-bold mt-2">
            ${coin.price.toLocaleString()}
          </div>
        </Card>
      ))}
    </div>
  )
}
```

---

## 🚀 دستور العمل استقرار در Hugging Face Spaces

```bash
# 1. Clone و setup
git clone <your-repo>
cd crypto-intelligence-hub

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set environment variables
export HF_API_TOKEN="your_token"
export REDIS_URL="redis://localhost:6379"

# 4. Run with Docker
docker-compose up -d

# 5. Access
# API: http://localhost:7860
# Docs: http://localhost:7860/docs
```

---

## 📞 سوالات متداول

### چطور Binance و CoinGecko رو بدون proxy تست کنم؟
```python
# در config.py یا .env
RESTRICTED_PROVIDERS = []  # Empty list = no proxy needed
```

### چطور provider جدید اضافه کنم؟
```python
# در backend/providers/new_providers_registry.py
"new_provider": ProviderInfo(
    id="new_provider",
    name="New Provider",
    type=ProviderType.OHLCV.value,
    url="https://api.newprovider.com",
    ...
)
```

---

## 🎯 نتیجه‌گیری

این پرامپت جامع شامل:
- ✅ تحلیل کامل وضع موجود
- ✅ شناسایی نقاط ضعف
- ✅ پرامپت‌های دقیق برای هر بخش
- ✅ کدهای نمونه آماده استفاده
- ✅ Priority list واضح
- ✅ راهنمای پیاده‌سازی

با استفاده از این پرامپت‌ها می‌توانید پروژه را به صورت گام‌به‌گام ارتقا دهید!
