"""
Comprehensive Data Collector Service
Collects data from all free API resources and saves to database
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import httpx
import os
import time
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import insert

from database.models import (
    MarketPrice, NewsArticle, SentimentMetric,
    WhaleTransaction, GasPrice, BlockchainStat,
    CachedMarketData, CachedOHLC
)

logger = logging.getLogger(__name__)


class DataCollectorService:
    """Service for collecting data from all free API resources"""
    
    def __init__(self, db_session: AsyncSession):
        self.db_session = db_session
        # Follow redirects (CryptoPanic moved endpoints) and keep timeouts conservative
        self.client = httpx.AsyncClient(timeout=10.0, follow_redirects=True)

        # Simple in-memory cache to reduce upstream rate-limit pressure
        # key -> (value, expiry_epoch)
        self._cache: Dict[str, Any] = {}
        self._cache_expiry: Dict[str, float] = {}
        self._last_call: Dict[str, float] = {}

        # Feature toggles (keep noisy/fragile sources opt-in)
        self.enable_coincap = os.getenv("ENABLE_COINCAP", "false").lower() == "true"

        # Secrets via env (never hardcode)
        self.coingecko_pro_key = os.getenv("COINGECKO_PRO_API_KEY", "").strip()
        self.cryptopanic_key = (
            os.getenv("CRYPTOPANIC_API_KEY", "").strip()
            or os.getenv("CRYPTOPANIC_TOKEN", "").strip()
        )
        self.etherscan_key = os.getenv("ETHERSCAN_API_KEY", "").strip()
        
        # API endpoints configuration
        self.apis = {
            'market_data': [
                {
                    'name': 'CoinGecko',
                    'url': 'https://api.coingecko.com/api/v3/simple/price',
                    'params': {
                        'ids': 'bitcoin,ethereum,binancecoin,solana,ripple',
                        'vs_currencies': 'usd',
                        'include_market_cap': 'true',
                        'include_24hr_vol': 'true',
                        'include_24hr_change': 'true'
                    }
                },
                {
                    'name': 'Binance',
                    'url': 'https://api.binance.com/api/v3/ticker/24hr',
                    'params': {'symbols': '["BTCUSDT","ETHUSDT","BNBUSDT","SOLUSDT"]'}
                },
                {
                    'name': 'CoinCap',
                    'url': 'https://api.coincap.io/v2/assets',
                    'params': {'limit': '10'}
                }
            ],
            'news': [
                {
                    'name': 'CryptoPanic',
                    # CryptoPanic moved to developer v2 endpoints; use new stable path
                    'url': 'https://cryptopanic.com/api/developer/v2/posts/',
                    'params': {'auth_token': '', 'public': 'true'}
                }
            ],
            'sentiment': [
                {
                    'name': 'Alternative.me Fear & Greed',
                    'url': 'https://api.alternative.me/fng/',
                    'params': {'limit': '1'}
                }
            ],
            'gas': [
                {
                    'name': 'Etherscan Gas',
                    'url': 'https://api.etherscan.io/api',
                    'params': {
                        'module': 'gastracker',
                        'action': 'gasoracle',
                        'apikey': ''
                    }
                }
            ]
        }

        # Inject optional auth at runtime
        if self.coingecko_pro_key:
            # CoinGecko Pro uses this param name even on free endpoints for higher tiers
            self.apis["market_data"][0]["params"]["x_cg_pro_api_key"] = self.coingecko_pro_key
        if self.cryptopanic_key:
            self.apis["news"][0]["params"]["auth_token"] = self.cryptopanic_key
        if self.etherscan_key:
            self.apis["gas"][0]["params"]["apikey"] = self.etherscan_key

    def _cache_key(self, url: str, params: Dict[str, Any]) -> str:
        items = "&".join(f"{k}={params[k]}" for k in sorted(params.keys()))
        return f"{url}?{items}"

    async def _get_json_with_backoff(
        self,
        source_name: str,
        url: str,
        params: Dict[str, Any],
        *,
        cache_ttl_s: int = 60,
        min_interval_s: int = 10,
        max_retries: int = 3,
    ) -> Any:
        """
        Fetch JSON with:
        - basic per-source throttling (min_interval_s)
        - short in-memory caching (cache_ttl_s)
        - exponential backoff on 429/503
        """
        now = time.time()

        ck = self._cache_key(url, params)
        exp = self._cache_expiry.get(ck, 0)
        if exp > now and ck in self._cache:
            return self._cache[ck]

        last = self._last_call.get(source_name, 0)
        if now - last < min_interval_s:
            # Within throttle window: return cached if available, else skip call
            if ck in self._cache:
                return self._cache[ck]
            raise RuntimeError(f"Throttled {source_name} (min_interval_s={min_interval_s})")

        self._last_call[source_name] = now

        attempt = 0
        backoff = 1.5
        while True:
            attempt += 1
            try:
                resp = await self.client.get(url, params=params)
                # Some providers (e.g., Binance) can be geo-blocked in certain environments
                if resp.status_code == 451:
                    raise httpx.HTTPStatusError(
                        "Geo-blocked (451)",
                        request=resp.request,
                        response=resp,
                    )
                # Explicitly treat 429 as retryable with backoff
                if resp.status_code == 429:
                    retry_after = resp.headers.get("Retry-After")
                    sleep_s = float(retry_after) if retry_after and retry_after.isdigit() else backoff
                    if attempt <= max_retries:
                        await asyncio.sleep(sleep_s)
                        backoff *= 2
                        continue
                resp.raise_for_status()
                data = resp.json()
                # Cache
                self._cache[ck] = data
                self._cache_expiry[ck] = time.time() + max(1, cache_ttl_s)
                return data
            except httpx.HTTPStatusError as e:
                status = e.response.status_code if e.response is not None else None
                if status == 451:
                    # Not retryable; bubble up as-is for caller to downgrade to warning
                    raise
                if status in (429, 503, 502, 504) and attempt <= max_retries:
                    await asyncio.sleep(backoff)
                    backoff *= 2
                    continue
                raise
            except Exception:
                if attempt <= max_retries:
                    await asyncio.sleep(backoff)
                    backoff *= 2
                    continue
                raise
    
    async def collect_market_data(self) -> Dict[str, Any]:
        """Collect market data from all sources"""
        results = {
            'timestamp': datetime.utcnow(),
            'sources': {},
            'saved_count': 0,
            'errors': []
        }
        
        for api_config in self.apis['market_data']:
            try:
                # CoinCap is frequently blocked/unresolvable in some environments; keep it opt-in
                if api_config["name"] == "CoinCap" and not self.enable_coincap:
                    continue

                # Reduce rate-limit pressure:
                # - CoinGecko: cache longer and throttle
                # - Binance: short cache
                if api_config["name"] == "CoinGecko":
                    data = await self._get_json_with_backoff(
                        api_config["name"],
                        api_config["url"],
                        api_config["params"],
                        cache_ttl_s=60,
                        min_interval_s=20,
                        max_retries=4,
                    )
                elif api_config["name"] == "Binance":
                    data = await self._get_json_with_backoff(
                        api_config["name"],
                        api_config["url"],
                        api_config["params"],
                        cache_ttl_s=15,
                        min_interval_s=5,
                        max_retries=2,
                    )
                else:
                    data = await self._get_json_with_backoff(
                        api_config["name"],
                        api_config["url"],
                        api_config["params"],
                        cache_ttl_s=30,
                        min_interval_s=10,
                        max_retries=2,
                    )
                
                results['sources'][api_config['name']] = data
                
                # Save to database
                saved = await self._save_market_data(api_config['name'], data)
                results['saved_count'] += saved
                
                logger.info(f"✓ Collected market data from {api_config['name']}")
                
            except Exception as e:
                # Downgrade geo-blocked providers to warnings (expected in some regions/HF)
                if isinstance(e, httpx.HTTPStatusError) and getattr(e.response, "status_code", None) == 451:
                    logger.warning(f"⚠️ {api_config['name']} geo-blocked (451); skipping")
                    continue

                error_msg = f"Failed to collect from {api_config['name']}: {str(e)}"
                logger.error(error_msg)
                results['errors'].append(error_msg)
        
        return results
    
    async def _save_market_data(self, source: str, data: Dict) -> int:
        """Save market data to database"""
        saved_count = 0
        
        try:
            if source == 'CoinGecko':
                # CoinGecko format
                for coin_id, coin_data in data.items():
                    if isinstance(coin_data, dict) and 'usd' in coin_data:
                        market_price = MarketPrice(
                            symbol=coin_id.upper()[:20],
                            price_usd=coin_data.get('usd', 0),
                            market_cap=coin_data.get('usd_market_cap'),
                            volume_24h=coin_data.get('usd_24h_vol'),
                            price_change_24h=coin_data.get('usd_24h_change'),
                            timestamp=datetime.utcnow(),
                            source=source
                        )
                        self.db_session.add(market_price)
                        
                        # Also save to cached_market_data
                        cached = CachedMarketData(
                            symbol=coin_id.upper()[:20],
                            price=coin_data.get('usd', 0),
                            market_cap=coin_data.get('usd_market_cap'),
                            volume_24h=coin_data.get('usd_24h_vol'),
                            change_24h=coin_data.get('usd_24h_change'),
                            provider=source.lower(),
                            fetched_at=datetime.utcnow()
                        )
                        self.db_session.add(cached)
                        saved_count += 1
            
            elif source == 'Binance':
                # Binance format
                if isinstance(data, list):
                    for ticker in data:
                        symbol = ticker.get('symbol', '').replace('USDT', '')[:20]
                        market_price = MarketPrice(
                            symbol=symbol,
                            price_usd=float(ticker.get('lastPrice', 0)),
                            volume_24h=float(ticker.get('volume', 0)),
                            price_change_24h=float(ticker.get('priceChangePercent', 0)),
                            timestamp=datetime.utcnow(),
                            source=source
                        )
                        self.db_session.add(market_price)
                        saved_count += 1
            
            elif source == 'CoinCap':
                # CoinCap format
                assets = data.get('data', [])
                for asset in assets:
                    market_price = MarketPrice(
                        symbol=asset.get('symbol', '')[:20],
                        price_usd=float(asset.get('priceUsd', 0)),
                        market_cap=float(asset.get('marketCapUsd', 0)) if asset.get('marketCapUsd') else None,
                        volume_24h=float(asset.get('volumeUsd24Hr', 0)) if asset.get('volumeUsd24Hr') else None,
                        timestamp=datetime.utcnow(),
                        source=source
                    )
                    self.db_session.add(market_price)
                    saved_count += 1
            
            await self.db_session.commit()
            
        except Exception as e:
            logger.error(f"Error saving market data from {source}: {e}")
            await self.db_session.rollback()
        
        return saved_count
    
    async def collect_news(self) -> Dict[str, Any]:
        """Collect news from all sources"""
        results = {
            'timestamp': datetime.utcnow(),
            'sources': {},
            'saved_count': 0,
            'errors': []
        }
        
        for api_config in self.apis['news']:
            try:
                if api_config["name"] == "CryptoPanic" and not self.cryptopanic_key:
                    # Avoid calling with 'free' tokens which redirect/fail
                    continue

                response = await self.client.get(
                    api_config['url'],
                    params=api_config['params']
                )
                response.raise_for_status()
                data = response.json()
                
                results['sources'][api_config['name']] = data
                
                # Save to database
                saved = await self._save_news(api_config['name'], data)
                results['saved_count'] += saved
                
                logger.info(f"✓ Collected news from {api_config['name']}")
                
            except Exception as e:
                error_msg = f"Failed to collect news from {api_config['name']}: {str(e)}"
                logger.error(error_msg)
                results['errors'].append(error_msg)
        
        return results
    
    async def _save_news(self, source: str, data: Dict) -> int:
        """Save news to database"""
        saved_count = 0
        
        try:
            if source == 'CryptoPanic':
                results = data.get('results', [])
                for article in results:
                    news = NewsArticle(
                        title=article.get('title', '')[:500],
                        content=None,
                        source=source,
                        url=article.get('url'),
                        published_at=datetime.fromisoformat(article.get('published_at').replace('Z', '+00:00')) if article.get('published_at') else datetime.utcnow(),
                        sentiment=article.get('votes', {}).get('kind'),
                        tags=','.join([c['slug'] for c in article.get('currencies', [])]),
                        created_at=datetime.utcnow()
                    )
                    self.db_session.add(news)
                    saved_count += 1
            
            await self.db_session.commit()
            
        except Exception as e:
            logger.error(f"Error saving news from {source}: {e}")
            await self.db_session.rollback()
        
        return saved_count
    
    async def collect_sentiment(self) -> Dict[str, Any]:
        """Collect sentiment data"""
        results = {
            'timestamp': datetime.utcnow(),
            'sources': {},
            'saved_count': 0,
            'errors': []
        }
        
        for api_config in self.apis['sentiment']:
            try:
                response = await self.client.get(
                    api_config['url'],
                    params=api_config['params']
                )
                response.raise_for_status()
                data = response.json()
                
                results['sources'][api_config['name']] = data
                
                # Save to database
                saved = await self._save_sentiment(api_config['name'], data)
                results['saved_count'] += saved
                
                logger.info(f"✓ Collected sentiment from {api_config['name']}")
                
            except Exception as e:
                error_msg = f"Failed to collect sentiment from {api_config['name']}: {str(e)}"
                logger.error(error_msg)
                results['errors'].append(error_msg)
        
        return results
    
    async def _save_sentiment(self, source: str, data: Dict) -> int:
        """Save sentiment data to database"""
        saved_count = 0
        
        try:
            if source == 'Alternative.me Fear & Greed':
                fng_data = data.get('data', [])
                if fng_data:
                    fng = fng_data[0]
                    sentiment = SentimentMetric(
                        metric_name='fear_greed_index',
                        value=float(fng.get('value', 0)),
                        classification=fng.get('value_classification', 'neutral'),
                        timestamp=datetime.utcnow(),
                        source=source
                    )
                    self.db_session.add(sentiment)
                    saved_count += 1
            
            await self.db_session.commit()
            
        except Exception as e:
            logger.error(f"Error saving sentiment from {source}: {e}")
            await self.db_session.rollback()
        
        return saved_count
    
    async def collect_gas_prices(self) -> Dict[str, Any]:
        """Collect gas prices"""
        results = {
            'timestamp': datetime.utcnow(),
            'sources': {},
            'saved_count': 0,
            'errors': []
        }
        
        for api_config in self.apis['gas']:
            try:
                if api_config["name"] == "Etherscan Gas" and not self.etherscan_key:
                    continue

                response = await self.client.get(
                    api_config['url'],
                    params=api_config['params']
                )
                response.raise_for_status()
                data = response.json()
                
                results['sources'][api_config['name']] = data
                
                # Save to database
                saved = await self._save_gas_prices(api_config['name'], data)
                results['saved_count'] += saved
                
                logger.info(f"✓ Collected gas prices from {api_config['name']}")
                
            except Exception as e:
                error_msg = f"Failed to collect gas prices from {api_config['name']}: {str(e)}"
                logger.error(error_msg)
                results['errors'].append(error_msg)
        
        return results
    
    async def _save_gas_prices(self, source: str, data: Dict) -> int:
        """Save gas prices to database"""
        saved_count = 0
        
        try:
            if source == 'Etherscan Gas':
                # Etherscan returns:
                # {"status":"1","message":"OK","result":{...}}
                # or {"status":"0","message":"NOTOK","result":"Max rate limit reached"}
                if not isinstance(data, dict):
                    raise ValueError("Etherscan response is not a JSON object")

                status = data.get("status")
                message = data.get("message", "")
                result = data.get('result', {})

                if status != "1" or not isinstance(result, dict):
                    # Do not crash/save invalid data
                    logger.warning(f"Etherscan gas not available: status={status} message={message} result_type={type(result).__name__}")
                    return 0

                gas_price = GasPrice(
                    blockchain='ethereum',
                    gas_price_gwei=float(result.get('SafeGasPrice', 0)),
                    fast_gas_price=float(result.get('FastGasPrice', 0)),
                    standard_gas_price=float(result.get('ProposeGasPrice', 0)),
                    slow_gas_price=float(result.get('SafeGasPrice', 0)),
                    timestamp=datetime.utcnow(),
                    source=source
                )
                self.db_session.add(gas_price)
                saved_count += 1
            
            await self.db_session.commit()
            
        except Exception as e:
            logger.error(f"Error saving gas prices from {source}: {e}")
            await self.db_session.rollback()
        
        return saved_count
    
    async def collect_all(self) -> Dict[str, Any]:
        """Collect data from all sources"""
        logger.info("Starting comprehensive data collection...")
        
        results = {
            'timestamp': datetime.utcnow(),
            'market_data': await self.collect_market_data(),
            'news': await self.collect_news(),
            'sentiment': await self.collect_sentiment(),
            'gas_prices': await self.collect_gas_prices()
        }
        
        total_saved = (
            results['market_data']['saved_count'] +
            results['news']['saved_count'] +
            results['sentiment']['saved_count'] +
            results['gas_prices']['saved_count']
        )
        
        logger.info(f"✓ Comprehensive collection complete. Total saved: {total_saved} records")
        
        return results
    
    async def close(self):
        """Close HTTP client"""
        await self.client.aclose()
