#!/usr/bin/env python3
"""
Trading & Backtesting Service
Integrates smart exchange clients with multi-source system
Specialized for trading and backtesting with Binance & KuCoin
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import pandas as pd
import numpy as np

from .smart_exchange_clients import UltraSmartBinanceClient, UltraSmartKuCoinClient
from .multi_source_fallback_engine import get_fallback_engine, DataType

logger = logging.getLogger(__name__)


class TradingDataService:
    """
    Service for fetching trading data with smart exchange clients
    Integrates with multi-source fallback system
    """
    
    def __init__(self, enable_proxy: bool = False, enable_doh: bool = True):
        """
        Initialize trading data service
        
        Args:
            enable_proxy: Enable proxy for geo-restricted access
            enable_doh: Enable DNS over HTTPS
        """
        # Smart exchange clients
        self.binance = UltraSmartBinanceClient(enable_proxy=enable_proxy, enable_doh=enable_doh)
        self.kucoin = UltraSmartKuCoinClient(enable_proxy=enable_proxy, enable_doh=enable_doh)
        
        # Multi-source fallback engine
        self.fallback_engine = get_fallback_engine()
        
        logger.info("✅ Trading Data Service initialized")
    
    async def get_trading_price(
        self,
        symbol: str,
        exchange: str = "binance",
        use_fallback: bool = True
    ) -> Dict[str, Any]:
        """
        Get trading price with smart routing
        
        Args:
            symbol: Trading pair (e.g., "BTCUSDT" for Binance, "BTC-USDT" for KuCoin)
            exchange: Exchange name ("binance" or "kucoin")
            use_fallback: Use multi-source fallback if primary fails
        
        Returns:
            Price data with metadata
        """
        try:
            if exchange.lower() == "binance":
                result = await self.binance.get_ticker_price(symbol)
                return {
                    "success": True,
                    "exchange": "binance",
                    "symbol": symbol,
                    "price": float(result["price"]),
                    "timestamp": datetime.utcnow().isoformat(),
                    "method": "smart_client"
                }
            
            elif exchange.lower() == "kucoin":
                result = await self.kucoin.get_ticker_price(symbol)
                return {
                    "success": True,
                    "exchange": "kucoin",
                    "symbol": symbol,
                    "price": float(result["price"]),
                    "timestamp": datetime.utcnow().isoformat(),
                    "method": "smart_client"
                }
            
            else:
                raise ValueError(f"Unsupported exchange: {exchange}")
        
        except Exception as e:
            logger.warning(f"Smart client failed for {exchange}: {e}")
            
            if use_fallback:
                logger.info(f"Falling back to multi-source system for {symbol}")
                return await self._fallback_to_multisource(symbol)
            else:
                raise
    
    async def _fallback_to_multisource(self, symbol: str) -> Dict[str, Any]:
        """Fallback to multi-source system"""
        from .multi_source_data_fetchers import MarketPriceFetcher
        
        # Try to get from multi-source system
        cache_key = f"trading_price:{symbol}"
        
        async def fetch_from_multisource(source: Dict[str, Any], **kwargs) -> Dict[str, Any]:
            """Fetch from multi-source"""
            if "binance" in source["name"]:
                return await MarketPriceFetcher.fetch_binance_special(source, [symbol])
            elif "coingecko" in source["name"]:
                return await MarketPriceFetcher.fetch_coingecko_special(source, [symbol])
            else:
                return await MarketPriceFetcher.fetch_generic(source, symbols=[symbol])
        
        result = await self.fallback_engine.fetch_with_fallback(
            DataType.MARKET_PRICES,
            fetch_from_multisource,
            cache_key,
            symbols=[symbol]
        )
        
        return result
    
    async def get_trading_ohlcv(
        self,
        symbol: str,
        timeframe: str = "1h",
        limit: int = 1000,
        exchange: str = "binance",
        start_time: Optional[int] = None,
        end_time: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get OHLCV data for trading/backtesting
        
        Args:
            symbol: Trading pair
            timeframe: Timeframe (1m, 5m, 15m, 1h, 4h, 1d, etc.)
            limit: Number of candles
            exchange: Exchange name
            start_time: Start timestamp (milliseconds)
            end_time: End timestamp (milliseconds)
        
        Returns:
            OHLCV data with metadata
        """
        try:
            if exchange.lower() == "binance":
                # Map timeframe to Binance format
                interval = self._map_timeframe_binance(timeframe)
                
                klines = await self.binance.get_klines(
                    symbol=symbol,
                    interval=interval,
                    limit=limit,
                    start_time=start_time,
                    end_time=end_time
                )
                
                # Transform Binance klines to standard format
                candles = []
                for kline in klines:
                    candles.append({
                        "timestamp": int(kline[0]),
                        "open": float(kline[1]),
                        "high": float(kline[2]),
                        "low": float(kline[3]),
                        "close": float(kline[4]),
                        "volume": float(kline[5]),
                        "close_time": int(kline[6]),
                        "quote_volume": float(kline[7]),
                        "trades": int(kline[8]),
                        "taker_buy_base": float(kline[9]),
                        "taker_buy_quote": float(kline[10])
                    })
                
                return {
                    "success": True,
                    "exchange": "binance",
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "candles": candles,
                    "count": len(candles),
                    "method": "smart_client",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            elif exchange.lower() == "kucoin":
                # Map timeframe to KuCoin format
                interval = self._map_timeframe_kucoin(timeframe)
                
                klines = await self.kucoin.get_klines(
                    symbol=symbol,
                    interval=interval,
                    start_time=start_time,
                    end_time=end_time
                )
                
                # Transform KuCoin klines to standard format
                candles = []
                for kline in klines:
                    # KuCoin format: [time, open, close, high, low, volume, amount]
                    candles.append({
                        "timestamp": int(kline[0]) * 1000,  # Convert to ms
                        "open": float(kline[1]),
                        "close": float(kline[2]),
                        "high": float(kline[3]),
                        "low": float(kline[4]),
                        "volume": float(kline[5]),
                        "quote_volume": float(kline[6])
                    })
                
                return {
                    "success": True,
                    "exchange": "kucoin",
                    "symbol": symbol,
                    "timeframe": timeframe,
                    "candles": candles,
                    "count": len(candles),
                    "method": "smart_client",
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            else:
                raise ValueError(f"Unsupported exchange: {exchange}")
        
        except Exception as e:
            logger.error(f"Failed to get OHLCV for {symbol} on {exchange}: {e}")
            raise
    
    def _map_timeframe_binance(self, timeframe: str) -> str:
        """Map generic timeframe to Binance format"""
        mapping = {
            "1m": "1m", "3m": "3m", "5m": "5m", "15m": "15m", "30m": "30m",
            "1h": "1h", "2h": "2h", "4h": "4h", "6h": "6h", "8h": "8h", "12h": "12h",
            "1d": "1d", "3d": "3d", "1w": "1w", "1M": "1M"
        }
        return mapping.get(timeframe, "1h")
    
    def _map_timeframe_kucoin(self, timeframe: str) -> str:
        """Map generic timeframe to KuCoin format"""
        mapping = {
            "1m": "1min", "3m": "3min", "5m": "5min", "15m": "15min", "30m": "30min",
            "1h": "1hour", "2h": "2hour", "4h": "4hour", "6h": "6hour",
            "8h": "8hour", "12h": "12hour",
            "1d": "1day", "1w": "1week"
        }
        return mapping.get(timeframe, "1hour")
    
    async def get_orderbook(
        self,
        symbol: str,
        exchange: str = "binance",
        limit: int = 100
    ) -> Dict[str, Any]:
        """
        Get order book for trading
        
        Args:
            symbol: Trading pair
            exchange: Exchange name
            limit: Depth limit
        
        Returns:
            Order book data
        """
        try:
            if exchange.lower() == "binance":
                result = await self.binance.get_orderbook(symbol, limit)
                
                return {
                    "success": True,
                    "exchange": "binance",
                    "symbol": symbol,
                    "bids": [[float(price), float(qty)] for price, qty in result["bids"]],
                    "asks": [[float(price), float(qty)] for price, qty in result["asks"]],
                    "timestamp": result.get("lastUpdateId", 0)
                }
            
            elif exchange.lower() == "kucoin":
                result = await self.kucoin.get_orderbook(symbol)
                
                return {
                    "success": True,
                    "exchange": "kucoin",
                    "symbol": symbol,
                    "bids": [[float(bid[0]), float(bid[1])] for bid in result.get("bids", [])],
                    "asks": [[float(ask[0]), float(ask[1])] for ask in result.get("asks", [])],
                    "timestamp": result.get("time", 0)
                }
            
            else:
                raise ValueError(f"Unsupported exchange: {exchange}")
        
        except Exception as e:
            logger.error(f"Failed to get orderbook for {symbol} on {exchange}: {e}")
            raise
    
    async def get_24h_stats(
        self,
        symbol: str,
        exchange: str = "binance"
    ) -> Dict[str, Any]:
        """
        Get 24h trading statistics
        
        Args:
            symbol: Trading pair
            exchange: Exchange name
        
        Returns:
            24h statistics
        """
        try:
            if exchange.lower() == "binance":
                result = await self.binance.get_ticker_24h(symbol)
                
                return {
                    "success": True,
                    "exchange": "binance",
                    "symbol": symbol,
                    "price": float(result["lastPrice"]),
                    "change": float(result["priceChange"]),
                    "change_percent": float(result["priceChangePercent"]),
                    "high": float(result["highPrice"]),
                    "low": float(result["lowPrice"]),
                    "volume": float(result["volume"]),
                    "quote_volume": float(result["quoteVolume"]),
                    "trades": int(result["count"]),
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            elif exchange.lower() == "kucoin":
                result = await self.kucoin.get_ticker_24h(symbol)
                
                return {
                    "success": True,
                    "exchange": "kucoin",
                    "symbol": symbol,
                    "price": float(result.get("last", 0)),
                    "change_percent": float(result.get("changeRate", 0)) * 100,
                    "high": float(result.get("high", 0)),
                    "low": float(result.get("low", 0)),
                    "volume": float(result.get("vol", 0)),
                    "quote_volume": float(result.get("volValue", 0)),
                    "timestamp": datetime.utcnow().isoformat()
                }
            
            else:
                raise ValueError(f"Unsupported exchange: {exchange}")
        
        except Exception as e:
            logger.error(f"Failed to get 24h stats for {symbol} on {exchange}: {e}")
            raise


class BacktestingService:
    """
    Backtesting service with historical data from smart clients
    """
    
    def __init__(self, trading_service: TradingDataService):
        """
        Initialize backtesting service
        
        Args:
            trading_service: Trading data service instance
        """
        self.trading_service = trading_service
        logger.info("✅ Backtesting Service initialized")
    
    async def fetch_historical_data(
        self,
        symbol: str,
        timeframe: str = "1h",
        days: int = 30,
        exchange: str = "binance"
    ) -> pd.DataFrame:
        """
        Fetch historical data for backtesting
        
        Args:
            symbol: Trading pair
            timeframe: Timeframe
            days: Number of days of historical data
            exchange: Exchange name
        
        Returns:
            DataFrame with OHLCV data
        """
        # Calculate timestamps
        end_time = int(datetime.utcnow().timestamp() * 1000)
        start_time = int((datetime.utcnow() - timedelta(days=days)).timestamp() * 1000)
        
        # Fetch data in chunks (max 1000 candles per request)
        all_candles = []
        current_start = start_time
        
        while current_start < end_time:
            try:
                result = await self.trading_service.get_trading_ohlcv(
                    symbol=symbol,
                    timeframe=timeframe,
                    limit=1000,
                    exchange=exchange,
                    start_time=current_start,
                    end_time=end_time
                )
                
                candles = result.get("candles", [])
                if not candles:
                    break
                
                all_candles.extend(candles)
                
                # Update start time for next chunk
                last_timestamp = candles[-1]["timestamp"]
                current_start = last_timestamp + 1
                
                # Avoid rate limiting
                await asyncio.sleep(0.5)
            
            except Exception as e:
                logger.error(f"Error fetching historical data: {e}")
                break
        
        # Convert to DataFrame
        if all_candles:
            df = pd.DataFrame(all_candles)
            df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
            df.set_index('timestamp', inplace=True)
            df = df.sort_index()
            
            logger.info(f"✅ Fetched {len(df)} candles for {symbol} ({days} days)")
            return df
        else:
            logger.warning(f"No historical data fetched for {symbol}")
            return pd.DataFrame()
    
    async def run_backtest(
        self,
        symbol: str,
        strategy: str,
        timeframe: str = "1h",
        days: int = 30,
        exchange: str = "binance",
        initial_capital: float = 10000.0
    ) -> Dict[str, Any]:
        """
        Run backtest with a trading strategy
        
        Args:
            symbol: Trading pair
            strategy: Strategy name (e.g., "sma_crossover", "rsi", "macd")
            timeframe: Timeframe
            days: Historical data period
            exchange: Exchange name
            initial_capital: Initial capital for backtesting
        
        Returns:
            Backtest results
        """
        # Fetch historical data
        df = await self.fetch_historical_data(symbol, timeframe, days, exchange)
        
        if df.empty:
            return {
                "success": False,
                "error": "No historical data available",
                "symbol": symbol,
                "exchange": exchange
            }
        
        # Apply strategy
        if strategy == "sma_crossover":
            results = self._backtest_sma_crossover(df, initial_capital)
        elif strategy == "rsi":
            results = self._backtest_rsi(df, initial_capital)
        elif strategy == "macd":
            results = self._backtest_macd(df, initial_capital)
        else:
            return {
                "success": False,
                "error": f"Unknown strategy: {strategy}",
                "symbol": symbol
            }
        
        results.update({
            "symbol": symbol,
            "exchange": exchange,
            "timeframe": timeframe,
            "days": days,
            "initial_capital": initial_capital
        })
        
        return results
    
    def _backtest_sma_crossover(self, df: pd.DataFrame, initial_capital: float) -> Dict[str, Any]:
        """Simple Moving Average Crossover strategy"""
        # Calculate SMAs
        df['sma_fast'] = df['close'].rolling(window=10).mean()
        df['sma_slow'] = df['close'].rolling(window=30).mean()
        
        # Generate signals
        df['signal'] = 0
        df.loc[df['sma_fast'] > df['sma_slow'], 'signal'] = 1  # Buy
        df.loc[df['sma_fast'] < df['sma_slow'], 'signal'] = -1  # Sell
        
        # Calculate returns
        df['position'] = df['signal'].shift(1)
        df['returns'] = df['close'].pct_change()
        df['strategy_returns'] = df['position'] * df['returns']
        
        # Calculate metrics
        total_return = (1 + df['strategy_returns']).prod() - 1
        final_capital = initial_capital * (1 + total_return)
        profit = final_capital - initial_capital
        
        # Count trades
        trades = (df['signal'].diff() != 0).sum()
        
        return {
            "success": True,
            "strategy": "sma_crossover",
            "total_return": total_return * 100,  # Percentage
            "final_capital": final_capital,
            "profit": profit,
            "trades": int(trades),
            "candles_analyzed": len(df)
        }
    
    def _backtest_rsi(self, df: pd.DataFrame, initial_capital: float) -> Dict[str, Any]:
        """RSI strategy"""
        # Calculate RSI
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['rsi'] = 100 - (100 / (1 + rs))
        
        # Generate signals
        df['signal'] = 0
        df.loc[df['rsi'] < 30, 'signal'] = 1  # Oversold - Buy
        df.loc[df['rsi'] > 70, 'signal'] = -1  # Overbought - Sell
        
        # Calculate returns
        df['position'] = df['signal'].shift(1)
        df['returns'] = df['close'].pct_change()
        df['strategy_returns'] = df['position'] * df['returns']
        
        # Calculate metrics
        total_return = (1 + df['strategy_returns']).prod() - 1
        final_capital = initial_capital * (1 + total_return)
        profit = final_capital - initial_capital
        trades = (df['signal'].diff() != 0).sum()
        
        return {
            "success": True,
            "strategy": "rsi",
            "total_return": total_return * 100,
            "final_capital": final_capital,
            "profit": profit,
            "trades": int(trades),
            "candles_analyzed": len(df)
        }
    
    def _backtest_macd(self, df: pd.DataFrame, initial_capital: float) -> Dict[str, Any]:
        """MACD strategy"""
        # Calculate MACD
        ema_fast = df['close'].ewm(span=12, adjust=False).mean()
        ema_slow = df['close'].ewm(span=26, adjust=False).mean()
        df['macd'] = ema_fast - ema_slow
        df['signal_line'] = df['macd'].ewm(span=9, adjust=False).mean()
        
        # Generate signals
        df['signal'] = 0
        df.loc[df['macd'] > df['signal_line'], 'signal'] = 1  # Buy
        df.loc[df['macd'] < df['signal_line'], 'signal'] = -1  # Sell
        
        # Calculate returns
        df['position'] = df['signal'].shift(1)
        df['returns'] = df['close'].pct_change()
        df['strategy_returns'] = df['position'] * df['returns']
        
        # Calculate metrics
        total_return = (1 + df['strategy_returns']).prod() - 1
        final_capital = initial_capital * (1 + total_return)
        profit = final_capital - initial_capital
        trades = (df['signal'].diff() != 0).sum()
        
        return {
            "success": True,
            "strategy": "macd",
            "total_return": total_return * 100,
            "final_capital": final_capital,
            "profit": profit,
            "trades": int(trades),
            "candles_analyzed": len(df)
        }


# Global instances
_trading_service_instance: Optional[TradingDataService] = None
_backtesting_service_instance: Optional[BacktestingService] = None


def get_trading_service(enable_proxy: bool = False, enable_doh: bool = True) -> TradingDataService:
    """Get or create trading service instance"""
    global _trading_service_instance
    if _trading_service_instance is None:
        _trading_service_instance = TradingDataService(enable_proxy=enable_proxy, enable_doh=enable_doh)
    return _trading_service_instance


def get_backtesting_service() -> BacktestingService:
    """Get or create backtesting service instance"""
    global _backtesting_service_instance
    if _backtesting_service_instance is None:
        trading_service = get_trading_service()
        _backtesting_service_instance = BacktestingService(trading_service)
    return _backtesting_service_instance


__all__ = [
    "TradingDataService",
    "BacktestingService",
    "get_trading_service",
    "get_backtesting_service"
]
