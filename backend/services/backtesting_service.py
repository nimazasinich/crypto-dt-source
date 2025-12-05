#!/usr/bin/env python3
"""
Backtesting Service
===================
سرویس بک‌تست برای ارزیابی استراتژی‌های معاملاتی با داده‌های تاریخی
"""

from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
import uuid
import logging
import json
import math

from database.models import (
    Base, BacktestJob, TrainingStatus, CachedOHLC
)

logger = logging.getLogger(__name__)


class BacktestingService:
    """سرویس اصلی بک‌تست"""

    def __init__(self, db_session: Session):
        """
        Initialize the backtesting service.
        
        Args:
            db_session: SQLAlchemy database session
        """
        self.db = db_session

    def start_backtest(
        self,
        strategy: str,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        initial_capital: float
    ) -> Dict[str, Any]:
        """
        Start a backtest for a specific strategy.
        
        Args:
            strategy: Name of the strategy to backtest
            symbol: Trading pair (e.g., "BTC/USDT")
            start_date: Backtest start date
            end_date: Backtest end date
            initial_capital: Starting capital
        
        Returns:
            Dict containing backtest job details
        """
        try:
            # Generate job ID
            job_id = f"BT-{uuid.uuid4().hex[:12].upper()}"

            # Create backtest job
            job = BacktestJob(
                job_id=job_id,
                strategy=strategy,
                symbol=symbol.upper(),
                start_date=start_date,
                end_date=end_date,
                initial_capital=initial_capital,
                status=TrainingStatus.PENDING
            )

            self.db.add(job)
            self.db.commit()
            self.db.refresh(job)

            # Run backtest in background (for now, run synchronously)
            results = self._run_backtest(job)

            # Update job with results
            job.status = TrainingStatus.COMPLETED
            job.total_return = results["total_return"]
            job.sharpe_ratio = results["sharpe_ratio"]
            job.max_drawdown = results["max_drawdown"]
            job.win_rate = results["win_rate"]
            job.total_trades = results["total_trades"]
            job.results = json.dumps(results)
            job.completed_at = datetime.utcnow()

            self.db.commit()
            self.db.refresh(job)

            logger.info(f"Backtest {job_id} completed successfully")

            return self._job_to_dict(job)

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error starting backtest: {e}", exc_info=True)
            raise

    def _run_backtest(self, job: BacktestJob) -> Dict[str, Any]:
        """
        Execute the backtest logic.
        
        Args:
            job: Backtest job
        
        Returns:
            Dict containing backtest results
        """
        try:
            # Fetch historical data
            historical_data = self._fetch_historical_data(
                job.symbol,
                job.start_date,
                job.end_date
            )

            if not historical_data:
                raise ValueError(f"No historical data found for {job.symbol}")

            # Get strategy function
            strategy_func = self._get_strategy_function(job.strategy)

            # Initialize backtest state
            capital = job.initial_capital
            position = 0.0  # Position size
            entry_price = 0.0
            trades = []
            equity_curve = [capital]
            high_water_mark = capital
            max_drawdown = 0.0

            # Run strategy on historical data
            for i, candle in enumerate(historical_data):
                close_price = candle["close"]
                signal = strategy_func(historical_data[:i+1], close_price)

                # Execute trades based on signal
                if signal == "BUY" and position == 0:
                    # Open long position
                    position = capital / close_price
                    entry_price = close_price
                    capital = 0
                
                elif signal == "SELL" and position > 0:
                    # Close long position
                    capital = position * close_price
                    pnl = capital - (position * entry_price)
                    trades.append({
                        "entry_price": entry_price,
                        "exit_price": close_price,
                        "pnl": pnl,
                        "return_pct": (pnl / (position * entry_price)) * 100,
                        "timestamp": candle["timestamp"]
                    })
                    position = 0
                    entry_price = 0.0

                # Calculate current equity
                current_equity = capital + (position * close_price if position > 0 else 0)
                equity_curve.append(current_equity)

                # Update drawdown
                if current_equity > high_water_mark:
                    high_water_mark = current_equity
                
                drawdown = ((high_water_mark - current_equity) / high_water_mark) * 100
                if drawdown > max_drawdown:
                    max_drawdown = drawdown

            # Close final position if open
            if position > 0:
                final_price = historical_data[-1]["close"]
                capital = position * final_price
                pnl = capital - (position * entry_price)
                trades.append({
                    "entry_price": entry_price,
                    "exit_price": final_price,
                    "pnl": pnl,
                    "return_pct": (pnl / (position * entry_price)) * 100,
                    "timestamp": historical_data[-1]["timestamp"]
                })

            # Calculate metrics
            total_return = ((capital - job.initial_capital) / job.initial_capital) * 100
            win_rate = self._calculate_win_rate(trades)
            sharpe_ratio = self._calculate_sharpe_ratio(equity_curve)

            return {
                "total_return": total_return,
                "sharpe_ratio": sharpe_ratio,
                "max_drawdown": max_drawdown,
                "win_rate": win_rate,
                "total_trades": len(trades),
                "trades": trades,
                "equity_curve": equity_curve[-100:]  # Last 100 points
            }

        except Exception as e:
            logger.error(f"Error running backtest: {e}", exc_info=True)
            raise

    def _fetch_historical_data(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[Dict[str, Any]]:
        """
        Fetch historical OHLC data.
        
        Args:
            symbol: Trading pair
            start_date: Start date
            end_date: End date
        
        Returns:
            List of candle dictionaries
        """
        try:
            # Convert symbol to database format (BTC/USDT -> BTCUSDT)
            db_symbol = symbol.replace("/", "").upper()

            candles = self.db.query(CachedOHLC).filter(
                and_(
                    CachedOHLC.symbol == db_symbol,
                    CachedOHLC.timestamp >= start_date,
                    CachedOHLC.timestamp <= end_date,
                    CachedOHLC.interval == "1h"  # Use 1h candles
                )
            ).order_by(CachedOHLC.timestamp.asc()).all()

            return [
                {
                    "timestamp": c.timestamp.isoformat() if c.timestamp else None,
                    "open": c.open,
                    "high": c.high,
                    "low": c.low,
                    "close": c.close,
                    "volume": c.volume
                }
                for c in candles
            ]

        except Exception as e:
            logger.error(f"Error fetching historical data: {e}", exc_info=True)
            return []

    def _get_strategy_function(self, strategy_name: str):
        """
        Get strategy function by name.
        
        Args:
            strategy_name: Strategy name
        
        Returns:
            Strategy function
        """
        strategies = {
            "simple_moving_average": self._sma_strategy,
            "rsi_strategy": self._rsi_strategy,
            "macd_strategy": self._macd_strategy
        }

        return strategies.get(strategy_name, self._sma_strategy)

    def _sma_strategy(self, data: List[Dict], current_price: float) -> str:
        """Simple Moving Average strategy."""
        if len(data) < 50:
            return "HOLD"
        
        # Calculate SMAs
        closes = [d["close"] for d in data[-50:]]
        sma_short = sum(closes[-10:]) / 10
        sma_long = sum(closes) / 50

        if sma_short > sma_long:
            return "BUY"
        elif sma_short < sma_long:
            return "SELL"
        return "HOLD"

    def _rsi_strategy(self, data: List[Dict], current_price: float) -> str:
        """RSI strategy."""
        if len(data) < 14:
            return "HOLD"
        
        # Calculate RSI (simplified)
        closes = [d["close"] for d in data[-14:]]
        gains = [max(0, closes[i] - closes[i-1]) for i in range(1, len(closes))]
        losses = [max(0, closes[i-1] - closes[i]) for i in range(1, len(closes))]
        
        avg_gain = sum(gains) / len(gains) if gains else 0
        avg_loss = sum(losses) / len(losses) if losses else 0
        
        if avg_loss == 0:
            rsi = 100
        else:
            rs = avg_gain / avg_loss
            rsi = 100 - (100 / (1 + rs))

        if rsi < 30:
            return "BUY"
        elif rsi > 70:
            return "SELL"
        return "HOLD"

    def _macd_strategy(self, data: List[Dict], current_price: float) -> str:
        """MACD strategy."""
        if len(data) < 26:
            return "HOLD"
        
        # Simplified MACD
        closes = [d["close"] for d in data[-26:]]
        ema_12 = sum(closes[-12:]) / 12
        ema_26 = sum(closes) / 26
        
        macd = ema_12 - ema_26

        if macd > 0:
            return "BUY"
        elif macd < 0:
            return "SELL"
        return "HOLD"

    def _calculate_win_rate(self, trades: List[Dict]) -> float:
        """Calculate win rate from trades."""
        if not trades:
            return 0.0
        
        winning_trades = sum(1 for t in trades if t["pnl"] > 0)
        return (winning_trades / len(trades)) * 100

    def _calculate_sharpe_ratio(self, equity_curve: List[float]) -> float:
        """Calculate Sharpe ratio from equity curve."""
        if len(equity_curve) < 2:
            return 0.0
        
        returns = []
        for i in range(1, len(equity_curve)):
            if equity_curve[i-1] > 0:
                ret = (equity_curve[i] - equity_curve[i-1]) / equity_curve[i-1]
                returns.append(ret)
        
        if not returns:
            return 0.0
        
        mean_return = sum(returns) / len(returns)
        variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
        std_dev = math.sqrt(variance) if variance > 0 else 0.0001

        # Annualized Sharpe (assuming daily returns)
        sharpe = (mean_return / std_dev) * math.sqrt(365) if std_dev > 0 else 0.0

        return sharpe

    def _job_to_dict(self, job: BacktestJob) -> Dict[str, Any]:
        """Convert job model to dictionary."""
        results = json.loads(job.results) if job.results else {}
        
        return {
            "job_id": job.job_id,
            "strategy": job.strategy,
            "symbol": job.symbol,
            "start_date": job.start_date.isoformat() if job.start_date else None,
            "end_date": job.end_date.isoformat() if job.end_date else None,
            "initial_capital": job.initial_capital,
            "status": job.status.value if job.status else None,
            "total_return": job.total_return,
            "sharpe_ratio": job.sharpe_ratio,
            "max_drawdown": job.max_drawdown,
            "win_rate": job.win_rate,
            "total_trades": job.total_trades,
            "results": results,
            "created_at": job.created_at.isoformat() if job.created_at else None,
            "completed_at": job.completed_at.isoformat() if job.completed_at else None
        }

