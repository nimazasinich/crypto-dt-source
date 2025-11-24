"""
Database Query Functions for Cached Market Data
Provides REAL data access from cached_market_data and cached_ohlc tables

CRITICAL RULES:
- ONLY read from database - NEVER generate fake data
- Return empty list if no data found
- All queries must be REAL database operations
"""

import logging
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from sqlalchemy import desc, and_, func
from sqlalchemy.orm import Session

from database.models import CachedMarketData, CachedOHLC
from database.db_manager import DatabaseManager
from utils.logger import setup_logger

logger = setup_logger("cache_queries")


class CacheQueries:
    """
    Database query operations for cached market data
    
    CRITICAL: All methods return REAL data from database ONLY
    """
    
    def __init__(self, db_manager: DatabaseManager):
        self.db = db_manager
    
    def get_cached_market_data(
        self,
        symbols: Optional[List[str]] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        Get cached market data from database
        
        CRITICAL RULES:
        - ONLY read from cached_market_data table
        - NEVER generate or fake data
        - Return empty list if no data found
        - Use DISTINCT ON to get latest data per symbol
        
        Args:
            symbols: List of symbols to filter (e.g., ['BTC', 'ETH'])
            limit: Maximum number of records
            
        Returns:
            List of dictionaries with REAL market data from database
        """
        try:
            with self.db.get_session() as session:
                # Subquery to get latest fetched_at for each symbol
                subq = session.query(
                    CachedMarketData.symbol,
                    func.max(CachedMarketData.fetched_at).label('max_fetched_at')
                ).group_by(CachedMarketData.symbol)
                
                if symbols:
                    subq = subq.filter(CachedMarketData.symbol.in_(symbols))
                
                subq = subq.subquery()
                
                # Join to get full records for latest entries
                query = session.query(CachedMarketData).join(
                    subq,
                    and_(
                        CachedMarketData.symbol == subq.c.symbol,
                        CachedMarketData.fetched_at == subq.c.max_fetched_at
                    )
                ).order_by(desc(CachedMarketData.fetched_at)).limit(limit)
                
                results = query.all()
                
                if not results:
                    logger.info(f"No cached market data found for symbols={symbols}")
                    return []
                
                # Convert to dictionaries - REAL data from database
                data = []
                for row in results:
                    data.append({
                        "symbol": row.symbol,
                        "price": float(row.price),
                        "market_cap": float(row.market_cap) if row.market_cap else None,
                        "volume_24h": float(row.volume_24h) if row.volume_24h else None,
                        "change_24h": float(row.change_24h) if row.change_24h else None,
                        "high_24h": float(row.high_24h) if row.high_24h else None,
                        "low_24h": float(row.low_24h) if row.low_24h else None,
                        "provider": row.provider,
                        "fetched_at": row.fetched_at
                    })
                
                logger.info(f"Retrieved {len(data)} cached market records")
                return data
                
        except Exception as e:
            logger.error(f"Database error in get_cached_market_data: {e}", exc_info=True)
            # Return empty list on error - NEVER fake data
            return []
    
    def get_cached_ohlc(
        self,
        symbol: str,
        interval: str = "1h",
        limit: int = 1000
    ) -> List[Dict[str, Any]]:
        """
        Get cached OHLC data from database
        
        CRITICAL RULES:
        - ONLY read from cached_ohlc table
        - NEVER generate fake candles
        - Return empty list if no data found
        - Order by timestamp ASC for chart display
        
        Args:
            symbol: Trading pair symbol (e.g., 'BTCUSDT')
            interval: Candle interval (e.g., '1h', '4h', '1d')
            limit: Maximum number of candles
            
        Returns:
            List of dictionaries with REAL OHLC data from database
        """
        try:
            with self.db.get_session() as session:
                # Query for OHLC data
                query = session.query(CachedOHLC).filter(
                    and_(
                        CachedOHLC.symbol == symbol,
                        CachedOHLC.interval == interval
                    )
                ).order_by(desc(CachedOHLC.timestamp)).limit(limit)
                
                results = query.all()
                
                if not results:
                    logger.info(f"No cached OHLC data found for {symbol} {interval}")
                    return []
                
                # Convert to dictionaries - REAL candle data from database
                # Reverse order for chronological display
                data = []
                for row in reversed(results):
                    data.append({
                        "timestamp": row.timestamp,
                        "open": float(row.open),
                        "high": float(row.high),
                        "low": float(row.low),
                        "close": float(row.close),
                        "volume": float(row.volume),
                        "provider": row.provider,
                        "fetched_at": row.fetched_at
                    })
                
                logger.info(f"Retrieved {len(data)} OHLC candles for {symbol} {interval}")
                return data
                
        except Exception as e:
            logger.error(f"Database error in get_cached_ohlc: {e}", exc_info=True)
            # Return empty list on error - NEVER fake data
            return []
    
    def save_market_data(
        self,
        symbol: str,
        price: float,
        market_cap: Optional[float] = None,
        volume_24h: Optional[float] = None,
        change_24h: Optional[float] = None,
        high_24h: Optional[float] = None,
        low_24h: Optional[float] = None,
        provider: str = "unknown"
    ) -> bool:
        """
        Save market data to cache
        
        CRITICAL: Only used by background workers to store REAL API data
        
        Args:
            symbol: Crypto symbol
            price: Current price (REAL from API)
            market_cap: Market cap (REAL from API)
            volume_24h: 24h volume (REAL from API)
            change_24h: 24h change (REAL from API)
            high_24h: 24h high (REAL from API)
            low_24h: 24h low (REAL from API)
            provider: Data provider name
            
        Returns:
            bool: True if saved successfully
        """
        try:
            with self.db.get_session() as session:
                # Create new record with REAL data
                record = CachedMarketData(
                    symbol=symbol,
                    price=price,
                    market_cap=market_cap,
                    volume_24h=volume_24h,
                    change_24h=change_24h,
                    high_24h=high_24h,
                    low_24h=low_24h,
                    provider=provider,
                    fetched_at=datetime.utcnow()
                )
                
                session.add(record)
                session.commit()
                
                logger.info(f"Saved market data for {symbol} from {provider}")
                return True
                
        except Exception as e:
            logger.error(f"Error saving market data for {symbol}: {e}", exc_info=True)
            return False
    
    def save_ohlc_candle(
        self,
        symbol: str,
        interval: str,
        timestamp: datetime,
        open_price: float,
        high: float,
        low: float,
        close: float,
        volume: float,
        provider: str = "unknown"
    ) -> bool:
        """
        Save OHLC candle to cache
        
        CRITICAL: Only used by background workers to store REAL candle data
        
        Args:
            symbol: Trading pair symbol
            interval: Candle interval
            timestamp: Candle open time (REAL from API)
            open_price: Open price (REAL from API)
            high: High price (REAL from API)
            low: Low price (REAL from API)
            close: Close price (REAL from API)
            volume: Volume (REAL from API)
            provider: Data provider name
            
        Returns:
            bool: True if saved successfully
        """
        try:
            with self.db.get_session() as session:
                # Check if candle already exists
                existing = session.query(CachedOHLC).filter(
                    and_(
                        CachedOHLC.symbol == symbol,
                        CachedOHLC.interval == interval,
                        CachedOHLC.timestamp == timestamp
                    )
                ).first()
                
                if existing:
                    # Update existing candle
                    existing.open = open_price
                    existing.high = high
                    existing.low = low
                    existing.close = close
                    existing.volume = volume
                    existing.provider = provider
                    existing.fetched_at = datetime.utcnow()
                else:
                    # Create new candle with REAL data
                    record = CachedOHLC(
                        symbol=symbol,
                        interval=interval,
                        timestamp=timestamp,
                        open=open_price,
                        high=high,
                        low=low,
                        close=close,
                        volume=volume,
                        provider=provider,
                        fetched_at=datetime.utcnow()
                    )
                    session.add(record)
                
                session.commit()
                
                logger.debug(f"Saved OHLC candle for {symbol} {interval} at {timestamp}")
                return True
                
        except Exception as e:
            logger.error(f"Error saving OHLC candle for {symbol}: {e}", exc_info=True)
            return False
    
    def cleanup_old_data(self, days: int = 7) -> Dict[str, int]:
        """
        Remove old cached data to manage storage
        
        Args:
            days: Remove data older than N days
            
        Returns:
            Dictionary with counts of deleted records
        """
        try:
            with self.db.get_session() as session:
                cutoff_time = datetime.utcnow() - timedelta(days=days)
                deleted_counts = {}
                
                # Clean old market data
                deleted = session.query(CachedMarketData).filter(
                    CachedMarketData.fetched_at < cutoff_time
                ).delete()
                deleted_counts['market_data'] = deleted
                
                # Clean old OHLC data
                deleted = session.query(CachedOHLC).filter(
                    CachedOHLC.fetched_at < cutoff_time
                ).delete()
                deleted_counts['ohlc'] = deleted
                
                session.commit()
                
                total_deleted = sum(deleted_counts.values())
                logger.info(f"Cleaned up {total_deleted} old cache records (older than {days} days)")
                
                return deleted_counts
                
        except Exception as e:
            logger.error(f"Error cleaning up old data: {e}", exc_info=True)
            return {}


# Global instance
_cache_queries = None

def get_cache_queries(db_manager: Optional[DatabaseManager] = None) -> CacheQueries:
    """
    Get global CacheQueries instance
    
    Args:
        db_manager: DatabaseManager instance (optional, will use global if not provided)
        
    Returns:
        CacheQueries instance
    """
    global _cache_queries
    
    if _cache_queries is None:
        if db_manager is None:
            from database.db_manager import db_manager as global_db
            db_manager = global_db
        _cache_queries = CacheQueries(db_manager)
    
    return _cache_queries
