"""
Comprehensive Data Collector Service
Collects data from all free API resources and saves to database
"""

import asyncio
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime
import httpx
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
        self.client = httpx.AsyncClient(timeout=10.0)
        
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
                    'url': 'https://cryptopanic.com/api/v1/posts/',
                    'params': {'auth_token': 'free', 'public': 'true'}
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
                        'apikey': 'SZHYFZK2RR8H9TIMJBVW54V4H81K2Z2KR2'
                    }
                }
            ]
        }
    
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
                response = await self.client.get(
                    api_config['url'],
                    params=api_config['params']
                )
                response.raise_for_status()
                data = response.json()
                
                results['sources'][api_config['name']] = data
                
                # Save to database
                saved = await self._save_market_data(api_config['name'], data)
                results['saved_count'] += saved
                
                logger.info(f"✓ Collected market data from {api_config['name']}")
                
            except Exception as e:
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
                result = data.get('result', {})
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
