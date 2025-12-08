#!/usr/bin/env python3
"""
🔌 Fallback Integrator - اتصال سیستم fallback نهایی به پروژه موجود
Integration of Ultimate Fallback System with existing project
"""

import logging
from typing import Optional, Dict, Any, List
from datetime import datetime

try:
    import httpx
    HTTPX_AVAILABLE = True
except ImportError:
    HTTPX_AVAILABLE = False
    
try:
    import aiohttp
    AIOHTTP_AVAILABLE = True
except ImportError:
    AIOHTTP_AVAILABLE = False

from backend.services.ultimate_fallback_system import (
    ultimate_fallback,
    fetch_with_fallback,
    Resource
)

logger = logging.getLogger(__name__)


class FallbackIntegrator:
    """
    کلاس ادغام‌کننده سیستم fallback با collectors موجود
    Integrator class for fallback system with existing collectors
    """
    
    def __init__(self):
        self.http_client = None
        if HTTPX_AVAILABLE:
            import httpx
            self.http_client = httpx.AsyncClient(timeout=30.0)
        elif AIOHTTP_AVAILABLE:
            import aiohttp
            self.session = None  # will be created on first use
        
        self.stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'sources_used': {}
        }
        
        logger.info(f"🔌 FallbackIntegrator initialized (httpx={HTTPX_AVAILABLE}, aiohttp={AIOHTTP_AVAILABLE})")
    
    async def fetch_market_data(
        self,
        symbol: str,
        vs_currency: str = 'usd',
        max_attempts: int = 10
    ) -> Optional[Dict]:
        """
        دریافت داده‌های بازار با fallback خودکار
        
        Args:
            symbol: نماد ارز (bitcoin, ethereum, etc.)
            vs_currency: ارز مبنا
            max_attempts: حداکثر تلاش
        
        Returns:
            داده‌های بازار یا None
        """
        self.stats['total_requests'] += 1
        
        # دریافت زنجیره fallback
        resources = ultimate_fallback.get_fallback_chain('market_data', count=max_attempts)
        
        for resource in resources:
            if not resource.is_available():
                continue
            
            try:
                logger.info(f"🔄 Trying {resource.name} for {symbol}")
                
                # ساخت URL براساس منبع
                if 'coingecko' in resource.base_url:
                    url = f"{resource.base_url}/simple/price"
                    params = {'ids': symbol, 'vs_currencies': vs_currency}
                elif 'binance' in resource.base_url:
                    # تبدیل symbol به format Binance (BTC → BTCUSDT)
                    symbol_upper = symbol.upper()
                    if symbol_upper == 'BITCOIN':
                        symbol_upper = 'BTC'
                    elif symbol_upper == 'ETHEREUM':
                        symbol_upper = 'ETH'
                    
                    url = f"{resource.base_url}/ticker/price"
                    params = {'symbol': f"{symbol_upper}USDT"}
                elif 'coinpaprika' in resource.base_url:
                    url = f"{resource.base_url}/tickers/{symbol}-{symbol}"
                    params = {}
                elif 'coincap' in resource.base_url:
                    url = f"{resource.base_url}/assets/{symbol}"
                    params = {}
                else:
                    # Default endpoint
                    url = f"{resource.base_url}/price"
                    params = {'symbol': symbol, 'currency': vs_currency}
                
                # افزودن کلید API اگر نیاز باشد
                headers = {}
                if resource.auth_type == "apiKeyHeader":
                    api_key = resource.get_api_key()
                    if api_key and resource.header_name:
                        headers[resource.header_name] = api_key
                elif resource.auth_type == "apiKeyQuery":
                    api_key = resource.get_api_key()
                    if api_key and resource.param_name:
                        params[resource.param_name] = api_key
                
                # ارسال درخواست
                response = await self.http_client.get(url, params=params, headers=headers)
                response.raise_for_status()
                
                data = response.json()
                
                # Normalize data format
                normalized = self._normalize_market_data(data, symbol, resource)
                
                # ثبت موفقیت
                ultimate_fallback.mark_result(resource.id, 'market_data', True)
                self.stats['successful_requests'] += 1
                self.stats['sources_used'][resource.name] = \
                    self.stats['sources_used'].get(resource.name, 0) + 1
                
                logger.info(f"✅ Success from {resource.name}: ${normalized.get('price', 'N/A')}")
                return normalized
                
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 429:
                    logger.warning(f"⏳ {resource.name} rate limited")
                    ultimate_fallback.mark_result(resource.id, 'market_data', False, 'rate_limit')
                else:
                    logger.warning(f"❌ {resource.name} HTTP error: {e.response.status_code}")
                    ultimate_fallback.mark_result(resource.id, 'market_data', False)
            
            except Exception as e:
                logger.warning(f"❌ {resource.name} failed: {e}")
                ultimate_fallback.mark_result(resource.id, 'market_data', False)
                continue
        
        # همه منابع شکست خوردند
        self.stats['failed_requests'] += 1
        logger.error(f"❌ All {max_attempts} sources failed for {symbol}")
        return None
    
    async def fetch_news(
        self,
        query: str = 'cryptocurrency',
        limit: int = 10,
        max_attempts: int = 10
    ) -> List[Dict]:
        """
        دریافت اخبار با fallback خودکار
        
        Args:
            query: کلمه کلیدی جستجو
            limit: تعداد اخبار
            max_attempts: حداکثر تلاش
        
        Returns:
            لیست اخبار
        """
        self.stats['total_requests'] += 1
        
        resources = ultimate_fallback.get_fallback_chain('news', count=max_attempts)
        
        for resource in resources:
            if not resource.is_available():
                continue
            
            try:
                logger.info(f"🔄 Trying {resource.name} for news")
                
                # ساخت URL براساس منبع
                if 'cryptopanic' in resource.base_url:
                    url = f"{resource.base_url}/posts"
                    params = {'filter': 'hot'}
                elif 'newsapi' in resource.base_url:
                    url = f"{resource.base_url}/everything"
                    params = {'q': query, 'pageSize': limit}
                elif 'rss' in resource.name.lower():
                    # RSS feed
                    url = resource.base_url
                    params = {}
                else:
                    url = f"{resource.base_url}/news"
                    params = {'limit': limit}
                
                # کلید API
                headers = {}
                if resource.auth_type in ["apiKeyHeader", "apiKeyHeaderOptional"]:
                    api_key = resource.get_api_key()
                    if api_key and resource.header_name:
                        headers[resource.header_name] = api_key
                elif resource.auth_type in ["apiKeyQuery", "apiKeyQueryOptional"]:
                    api_key = resource.get_api_key()
                    if api_key and resource.param_name:
                        params[resource.param_name] = api_key
                
                response = await self.http_client.get(url, params=params, headers=headers)
                response.raise_for_status()
                
                # Parse response
                if 'rss' in resource.name.lower() or 'xml' in response.headers.get('content-type', ''):
                    news_items = self._parse_rss_feed(response.text)
                else:
                    data = response.json()
                    news_items = self._normalize_news_data(data, resource)
                
                # ثبت موفقیت
                ultimate_fallback.mark_result(resource.id, 'news', True)
                self.stats['successful_requests'] += 1
                self.stats['sources_used'][resource.name] = \
                    self.stats['sources_used'].get(resource.name, 0) + 1
                
                logger.info(f"✅ Got {len(news_items)} news from {resource.name}")
                return news_items[:limit]
                
            except Exception as e:
                logger.warning(f"❌ {resource.name} failed: {e}")
                ultimate_fallback.mark_result(resource.id, 'news', False)
                continue
        
        self.stats['failed_requests'] += 1
        logger.error(f"❌ All news sources failed")
        return []
    
    async def fetch_sentiment(
        self,
        max_attempts: int = 10
    ) -> Optional[Dict]:
        """
        دریافت شاخص احساسات با fallback خودکار
        
        Args:
            max_attempts: حداکثر تلاش
        
        Returns:
            داده‌های احساسات یا None
        """
        self.stats['total_requests'] += 1
        
        resources = ultimate_fallback.get_fallback_chain('sentiment', count=max_attempts)
        
        for resource in resources:
            if not resource.is_available():
                continue
            
            try:
                logger.info(f"🔄 Trying {resource.name} for sentiment")
                
                # ساخت URL
                if 'alternative.me' in resource.base_url:
                    url = f"{resource.base_url}/fng/"
                    params = {'limit': 1, 'format': 'json'}
                elif 'cfgi' in resource.base_url:
                    url = f"{resource.base_url}/v1/fear-greed"
                    params = {}
                else:
                    url = resource.base_url
                    params = {}
                
                response = await self.http_client.get(url, params=params)
                response.raise_for_status()
                
                data = response.json()
                normalized = self._normalize_sentiment_data(data, resource)
                
                ultimate_fallback.mark_result(resource.id, 'sentiment', True)
                self.stats['successful_requests'] += 1
                
                logger.info(f"✅ Sentiment from {resource.name}: {normalized.get('value', 'N/A')}")
                return normalized
                
            except Exception as e:
                logger.warning(f"❌ {resource.name} failed: {e}")
                ultimate_fallback.mark_result(resource.id, 'sentiment', False)
                continue
        
        self.stats['failed_requests'] += 1
        return None
    
    async def analyze_with_hf_models(
        self,
        text: str,
        task: str = 'sentiment',
        max_models: int = 5
    ) -> Dict:
        """
        آنالیز متن با چند مدل HuggingFace
        
        Args:
            text: متن برای آنالیز
            task: نوع task (sentiment, generation, summarization)
            max_models: حداکثر تعداد مدل
        
        Returns:
            نتیجه آنالیز
        """
        models = ultimate_fallback.get_fallback_chain('hf_models', count=max_models)
        results = []
        
        for model in models:
            if not model.is_available():
                continue
            
            # فیلتر براساس task
            if task == 'sentiment' and 'sentiment' not in model.name.lower():
                continue
            if task == 'generation' and 'gpt' not in model.name.lower():
                continue
            if task == 'summarization' and 'summar' not in model.name.lower():
                continue
            
            try:
                logger.info(f"🔄 Analyzing with {model.name}")
                
                headers = {}
                api_key = model.get_api_key()
                if api_key:
                    headers['Authorization'] = f'Bearer {api_key}'
                
                payload = {'inputs': text}
                
                response = await self.http_client.post(
                    model.base_url,
                    json=payload,
                    headers=headers,
                    timeout=60.0
                )
                response.raise_for_status()
                
                result = response.json()
                results.append({
                    'model': model.name,
                    'result': result
                })
                
                ultimate_fallback.mark_result(model.id, 'hf_models', True)
                
                # اگر 3 مدل موفق شدند، کافی است
                if len(results) >= 3:
                    break
                    
            except Exception as e:
                logger.warning(f"❌ {model.name} failed: {e}")
                ultimate_fallback.mark_result(model.id, 'hf_models', False)
                continue
        
        # Ensemble results
        if results:
            return self._ensemble_results(results, task)
        else:
            return {'status': 'error', 'message': 'All models failed'}
    
    def _normalize_market_data(self, data: Dict, symbol: str, resource: Resource) -> Dict:
        """Normalize market data format"""
        try:
            # CoinGecko format
            if symbol in data:
                return {
                    'symbol': symbol,
                    'price': data[symbol].get('usd', 0),
                    'source': resource.name,
                    'timestamp': datetime.now().isoformat()
                }
            
            # Binance format
            if 'price' in data:
                return {
                    'symbol': symbol,
                    'price': float(data['price']),
                    'source': resource.name,
                    'timestamp': datetime.now().isoformat()
                }
            
            # CoinPaprika format
            if 'quotes' in data:
                return {
                    'symbol': symbol,
                    'price': data['quotes'].get('USD', {}).get('price', 0),
                    'source': resource.name,
                    'timestamp': datetime.now().isoformat()
                }
            
            # Generic format
            return {
                'symbol': symbol,
                'price': data.get('price', data.get('last', 0)),
                'source': resource.name,
                'timestamp': datetime.now().isoformat(),
                'raw_data': data
            }
        except Exception as e:
            logger.error(f"Error normalizing market data: {e}")
            return {'symbol': symbol, 'price': 0, 'error': str(e)}
    
    def _normalize_news_data(self, data: Dict, resource: Resource) -> List[Dict]:
        """Normalize news data format"""
        try:
            news_items = []
            
            # CryptoPanic format
            if 'results' in data:
                for item in data['results'][:10]:
                    news_items.append({
                        'title': item.get('title'),
                        'url': item.get('url'),
                        'source': item.get('source', {}).get('title', resource.name),
                        'published': item.get('published_at')
                    })
            
            # NewsAPI format
            elif 'articles' in data:
                for item in data['articles'][:10]:
                    news_items.append({
                        'title': item.get('title'),
                        'url': item.get('url'),
                        'source': item.get('source', {}).get('name', resource.name),
                        'published': item.get('publishedAt')
                    })
            
            # Generic format
            elif isinstance(data, list):
                for item in data[:10]:
                    news_items.append({
                        'title': item.get('title', item.get('headline')),
                        'url': item.get('url', item.get('link')),
                        'source': resource.name,
                        'published': item.get('published', item.get('date'))
                    })
            
            return news_items
        except Exception as e:
            logger.error(f"Error normalizing news data: {e}")
            return []
    
    def _normalize_sentiment_data(self, data: Dict, resource: Resource) -> Dict:
        """Normalize sentiment data format"""
        try:
            # Alternative.me format
            if 'data' in data and isinstance(data['data'], list):
                item = data['data'][0]
                return {
                    'value': int(item.get('value', 50)),
                    'classification': item.get('value_classification', 'neutral'),
                    'source': resource.name,
                    'timestamp': item.get('timestamp')
                }
            
            # Generic format
            return {
                'value': data.get('value', data.get('score', 50)),
                'classification': data.get('classification', 'neutral'),
                'source': resource.name,
                'timestamp': datetime.now().isoformat()
            }
        except Exception as e:
            logger.error(f"Error normalizing sentiment data: {e}")
            return {'value': 50, 'classification': 'neutral', 'error': str(e)}
    
    def _parse_rss_feed(self, xml_content: str) -> List[Dict]:
        """Parse RSS feed (basic implementation)"""
        # TODO: استفاده از feedparser برای parse کامل
        return []
    
    def _ensemble_results(self, results: List[Dict], task: str) -> Dict:
        """Combine results from multiple models"""
        if not results:
            return {'status': 'error', 'message': 'No results'}
        
        if task == 'sentiment':
            # میانگین‌گیری
            sentiments = []
            for r in results:
                model_result = r['result']
                if isinstance(model_result, list) and len(model_result) > 0:
                    # استخراج label
                    label = model_result[0].get('label', 'neutral')
                    sentiments.append(label)
            
            # اکثریت vote
            if sentiments:
                most_common = max(set(sentiments), key=sentiments.count)
                return {
                    'sentiment': most_common,
                    'models_used': len(results),
                    'confidence': sentiments.count(most_common) / len(sentiments),
                    'details': results
                }
        
        return {
            'status': 'success',
            'models_used': len(results),
            'results': results
        }
    
    def get_stats(self) -> Dict:
        """دریافت آمار استفاده"""
        success_rate = 0
        if self.stats['total_requests'] > 0:
            success_rate = (self.stats['successful_requests'] / self.stats['total_requests']) * 100
        
        return {
            'total_requests': self.stats['total_requests'],
            'successful_requests': self.stats['successful_requests'],
            'failed_requests': self.stats['failed_requests'],
            'success_rate': round(success_rate, 2),
            'sources_used': self.stats['sources_used']
        }
    
    async def close(self):
        """بستن http client"""
        if self.http_client and HTTPX_AVAILABLE:
            await self.http_client.aclose()
        elif AIOHTTP_AVAILABLE and hasattr(self, 'session') and self.session:
            await self.session.close()


# ═══════════════════════════════════════════════════════════════
# Global Instance
# ═══════════════════════════════════════════════════════════════

fallback_integrator = FallbackIntegrator()


# ═══════════════════════════════════════════════════════════════
# Test
# ═══════════════════════════════════════════════════════════════

async def test_integrator():
    """تست integrator"""
    print("=" * 80)
    print("🧪 Testing Fallback Integrator")
    print("=" * 80)
    print()
    
    # Test 1: Market Data
    print("📊 Test 1: Market Data")
    data = await fallback_integrator.fetch_market_data('bitcoin')
    if data:
        print(f"✅ Price: ${data.get('price', 'N/A')} from {data.get('source')}")
    else:
        print("❌ Failed to fetch market data")
    print()
    
    # Test 2: News
    print("📰 Test 2: News")
    news = await fallback_integrator.fetch_news('bitcoin', limit=5)
    print(f"✅ Got {len(news)} news articles")
    if news:
        print(f"   First: {news[0].get('title', 'N/A')}")
    print()
    
    # Test 3: Sentiment
    print("💭 Test 3: Sentiment")
    sentiment = await fallback_integrator.fetch_sentiment()
    if sentiment:
        print(f"✅ Sentiment: {sentiment.get('classification', 'N/A')} ({sentiment.get('value', 'N/A')})")
    else:
        print("❌ Failed to fetch sentiment")
    print()
    
    # Stats
    print("=" * 80)
    print("📊 Statistics")
    print("=" * 80)
    stats = fallback_integrator.get_stats()
    print(f"Total Requests: {stats['total_requests']}")
    print(f"Successful: {stats['successful_requests']}")
    print(f"Failed: {stats['failed_requests']}")
    print(f"Success Rate: {stats['success_rate']}%")
    print()
    print("Sources Used:")
    for source, count in stats['sources_used'].items():
        print(f"  - {source}: {count}")
    
    await fallback_integrator.close()


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_integrator())
