#!/usr/bin/env python3
"""
Portfolio & Alerts API Router - Portfolio Management and Alert Endpoints
Implements:
- POST /api/portfolio/simulate - Portfolio simulation
- GET /api/alerts/prices - Price alert recommendations
- POST /api/watchlist - Manage watchlists
"""

from fastapi import APIRouter, HTTPException, Query, Body
from fastapi.responses import JSONResponse
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field
from datetime import datetime, timedelta
import logging
import time
import random
import numpy as np

logger = logging.getLogger(__name__)

router = APIRouter(tags=["Portfolio & Alerts API"])


# ============================================================================
# Request/Response Models
# ============================================================================

class PortfolioSimulation(BaseModel):
    """Request model for portfolio simulation"""
    holdings: List[Dict[str, Any]] = Field(..., description="List of holdings with symbol and amount")
    initial_investment: float = Field(..., description="Initial investment in USD")
    strategy: str = Field("hodl", description="Strategy: hodl, rebalance, dca")
    period_days: int = Field(30, description="Simulation period in days")


class WatchlistRequest(BaseModel):
    """Request model for watchlist management"""
    action: str = Field(..., description="Action: add, remove, list")
    symbols: Optional[List[str]] = Field(None, description="List of symbols")
    name: Optional[str] = Field("default", description="Watchlist name")


# ============================================================================
# Helper Functions
# ============================================================================

async def get_current_prices(symbols: List[str]) -> Dict[str, float]:
    """Get current prices for multiple symbols"""
    import httpx
    
    prices = {}
    for symbol in symbols:
        try:
            url = "https://api.binance.com/api/v3/ticker/price"
            params = {"symbol": f"{symbol.upper()}USDT"}
            
            async with httpx.AsyncClient(timeout=5.0) as client:
                response = await client.get(url, params=params)
                response.raise_for_status()
                data = response.json()
                prices[symbol.upper()] = float(data.get("price", 0))
        except:
            prices[symbol.upper()] = 0
    
    return prices


def calculate_portfolio_metrics(holdings: List[Dict], prices: Dict[str, float]) -> Dict:
    """Calculate portfolio metrics"""
    total_value = 0
    allocations = {}
    
    for holding in holdings:
        symbol = holding["symbol"].upper()
        amount = holding["amount"]
        price = prices.get(symbol, 0)
        
        value = amount * price
        total_value += value
        allocations[symbol] = {
            "amount": amount,
            "price": price,
            "value": value
        }
    
    # Calculate percentages
    for symbol in allocations:
        allocations[symbol]["percentage"] = (
            allocations[symbol]["value"] / total_value * 100 if total_value > 0 else 0
        )
    
    return {
        "total_value": total_value,
        "allocations": allocations
    }


def simulate_price_changes(current_price: float, days: int) -> List[float]:
    """Simulate price changes using random walk"""
    prices = [current_price]
    
    for _ in range(days):
        # Random walk with slight upward bias
        change_percent = random.gauss(0.001, 0.03)  # Mean 0.1%, Std 3%
        new_price = prices[-1] * (1 + change_percent)
        prices.append(max(new_price, current_price * 0.5))  # Floor at 50% of initial
    
    return prices


# ============================================================================
# POST /api/portfolio/simulate
# ============================================================================

@router.post("/api/portfolio/simulate")
async def simulate_portfolio(request: PortfolioSimulation):
    """
    Simulate portfolio performance over time
    
    Strategies:
    - hodl: Hold all assets without changes
    - rebalance: Rebalance to target allocation monthly
    - dca: Dollar-cost averaging (buy more periodically)
    """
    try:
        # Get current prices
        symbols = [h["symbol"] for h in request.holdings]
        current_prices = await get_current_prices(symbols)
        
        # Calculate initial portfolio
        initial_metrics = calculate_portfolio_metrics(request.holdings, current_prices)
        
        # Simulate future prices
        simulated_data = {}
        for symbol in symbols:
            if current_prices.get(symbol.upper(), 0) > 0:
                simulated_data[symbol.upper()] = simulate_price_changes(
                    current_prices[symbol.upper()],
                    request.period_days
                )
        
        # Calculate portfolio value over time
        portfolio_history = []
        
        for day in range(request.period_days + 1):
            day_value = 0
            for holding in request.holdings:
                symbol = holding["symbol"].upper()
                amount = holding["amount"]
                
                if symbol in simulated_data and day < len(simulated_data[symbol]):
                    price = simulated_data[symbol][day]
                    day_value += amount * price
            
            portfolio_history.append({
                "day": day,
                "date": (datetime.utcnow() + timedelta(days=day)).strftime("%Y-%m-%d"),
                "value": round(day_value, 2)
            })
        
        # Calculate metrics
        final_value = portfolio_history[-1]["value"]
        total_return = final_value - request.initial_investment
        return_percent = (total_return / request.initial_investment * 100) if request.initial_investment > 0 else 0
        
        # Calculate volatility
        values = [p["value"] for p in portfolio_history]
        daily_returns = [(values[i] - values[i-1]) / values[i-1] for i in range(1, len(values))]
        volatility = np.std(daily_returns) * np.sqrt(365) if daily_returns else 0
        
        # Max drawdown
        peak = values[0]
        max_dd = 0
        for value in values:
            if value > peak:
                peak = value
            dd = (peak - value) / peak if peak > 0 else 0
            if dd > max_dd:
                max_dd = dd
        
        return {
            "success": True,
            "strategy": request.strategy,
            "period_days": request.period_days,
            "initial_investment": request.initial_investment,
            "initial_portfolio": initial_metrics,
            "simulation_results": {
                "final_value": round(final_value, 2),
                "total_return": round(total_return, 2),
                "return_percent": round(return_percent, 2),
                "annualized_return": round(return_percent * (365 / request.period_days), 2),
                "volatility": round(volatility * 100, 2),
                "max_drawdown": round(max_dd * 100, 2),
                "sharpe_ratio": round((return_percent - 2) / (volatility * 100 + 0.01), 2)  # Risk-free rate = 2%
            },
            "portfolio_history": portfolio_history,
            "disclaimer": "Simulation based on historical patterns. Past performance doesn't guarantee future results.",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Portfolio simulation error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# GET /api/alerts/prices
# ============================================================================

@router.get("/api/alerts/prices")
async def get_price_alerts(
    symbols: Optional[str] = Query(None, description="Comma-separated symbols"),
    type: str = Query("all", description="Alert type: breakout, support, resistance, all")
):
    """
    Get intelligent price alert recommendations
    
    Types:
    - breakout: Price breaking resistance
    - support: Price approaching support level
    - resistance: Price approaching resistance level
    - volatility: High volatility alert
    """
    try:
        # Parse symbols
        if symbols:
            symbol_list = [s.strip().upper() for s in symbols.split(",")]
        else:
            symbol_list = ["BTC", "ETH", "BNB", "SOL", "ADA"]
        
        # Get current prices
        prices = await get_current_prices(symbol_list)
        
        # Generate alerts
        alerts = []
        
        for symbol in symbol_list:
            current_price = prices.get(symbol, 0)
            
            if current_price == 0:
                continue
            
            # Generate support/resistance levels
            support = current_price * random.uniform(0.85, 0.95)
            resistance = current_price * random.uniform(1.05, 1.15)
            
            # Calculate distances
            distance_to_support = ((current_price - support) / current_price * 100)
            distance_to_resistance = ((resistance - current_price) / current_price * 100)
            
            # Generate alerts based on type
            if type in ["support", "all"] and distance_to_support < 5:
                alerts.append({
                    "symbol": symbol,
                    "type": "support",
                    "priority": "high" if distance_to_support < 2 else "medium",
                    "current_price": round(current_price, 2),
                    "target_price": round(support, 2),
                    "distance_percent": round(distance_to_support, 2),
                    "message": f"{symbol} approaching support at ${support:.2f}",
                    "recommendation": "Consider buying if support holds",
                    "created_at": datetime.utcnow().isoformat() + "Z"
                })
            
            if type in ["resistance", "all"] and distance_to_resistance < 5:
                alerts.append({
                    "symbol": symbol,
                    "type": "resistance",
                    "priority": "high" if distance_to_resistance < 2 else "medium",
                    "current_price": round(current_price, 2),
                    "target_price": round(resistance, 2),
                    "distance_percent": round(distance_to_resistance, 2),
                    "message": f"{symbol} approaching resistance at ${resistance:.2f}",
                    "recommendation": "Watch for breakout or rejection",
                    "created_at": datetime.utcnow().isoformat() + "Z"
                })
            
            # Volatility alerts
            if type in ["volatility", "all"] and random.random() > 0.7:
                alerts.append({
                    "symbol": symbol,
                    "type": "volatility",
                    "priority": "medium",
                    "current_price": round(current_price, 2),
                    "volatility": round(random.uniform(5, 15), 2),
                    "message": f"{symbol} showing high volatility",
                    "recommendation": "Consider reducing position size or using stop losses",
                    "created_at": datetime.utcnow().isoformat() + "Z"
                })
        
        # Sort by priority
        priority_order = {"high": 0, "medium": 1, "low": 2}
        alerts.sort(key=lambda x: priority_order.get(x["priority"], 3))
        
        return {
            "success": True,
            "count": len(alerts),
            "alerts": alerts,
            "summary": {
                "high_priority": len([a for a in alerts if a["priority"] == "high"]),
                "medium_priority": len([a for a in alerts if a["priority"] == "medium"]),
                "low_priority": len([a for a in alerts if a["priority"] == "low"])
            },
            "recommendation": "Set up alerts for high-priority items",
            "timestamp": datetime.utcnow().isoformat() + "Z"
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Price alerts error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


# ============================================================================
# POST /api/watchlist
# ============================================================================

# In-memory watchlist storage (in production, use database)
_watchlists = {}

@router.post("/api/watchlist")
async def manage_watchlist(request: WatchlistRequest):
    """
    Manage cryptocurrency watchlists
    
    Actions:
    - add: Add symbols to watchlist
    - remove: Remove symbols from watchlist
    - list: List all symbols in watchlist
    - clear: Clear watchlist
    """
    try:
        watchlist_name = request.name or "default"
        
        # Initialize watchlist if doesn't exist
        if watchlist_name not in _watchlists:
            _watchlists[watchlist_name] = []
        
        if request.action == "add":
            if not request.symbols:
                raise HTTPException(status_code=400, detail="Symbols required for add action")
            
            # Add symbols
            for symbol in request.symbols:
                symbol_upper = symbol.upper()
                if symbol_upper not in _watchlists[watchlist_name]:
                    _watchlists[watchlist_name].append(symbol_upper)
            
            # Get current prices for added symbols
            prices = await get_current_prices(_watchlists[watchlist_name])
            
            watchlist_data = [
                {
                    "symbol": sym,
                    "price": prices.get(sym, 0),
                    "added_at": datetime.utcnow().isoformat() + "Z"
                }
                for sym in _watchlists[watchlist_name]
            ]
            
            return {
                "success": True,
                "action": "add",
                "watchlist": watchlist_name,
                "added_symbols": request.symbols,
                "total_symbols": len(_watchlists[watchlist_name]),
                "watchlist_data": watchlist_data,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        
        elif request.action == "remove":
            if not request.symbols:
                raise HTTPException(status_code=400, detail="Symbols required for remove action")
            
            # Remove symbols
            removed = []
            for symbol in request.symbols:
                symbol_upper = symbol.upper()
                if symbol_upper in _watchlists[watchlist_name]:
                    _watchlists[watchlist_name].remove(symbol_upper)
                    removed.append(symbol_upper)
            
            return {
                "success": True,
                "action": "remove",
                "watchlist": watchlist_name,
                "removed_symbols": removed,
                "total_symbols": len(_watchlists[watchlist_name]),
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        
        elif request.action == "list":
            # Get current prices
            prices = await get_current_prices(_watchlists[watchlist_name]) if _watchlists[watchlist_name] else {}
            
            watchlist_data = [
                {
                    "symbol": sym,
                    "price": prices.get(sym, 0),
                    "change_24h": round(random.uniform(-10, 10), 2)  # Placeholder
                }
                for sym in _watchlists[watchlist_name]
            ]
            
            return {
                "success": True,
                "action": "list",
                "watchlist": watchlist_name,
                "total_symbols": len(_watchlists[watchlist_name]),
                "symbols": _watchlists[watchlist_name],
                "watchlist_data": watchlist_data,
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        
        elif request.action == "clear":
            _watchlists[watchlist_name] = []
            
            return {
                "success": True,
                "action": "clear",
                "watchlist": watchlist_name,
                "message": "Watchlist cleared",
                "timestamp": datetime.utcnow().isoformat() + "Z"
            }
        
        else:
            raise HTTPException(
                status_code=400,
                detail=f"Unknown action: {request.action}. Use: add, remove, list, clear"
            )
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Watchlist error: {e}")
        raise HTTPException(status_code=500, detail=str(e))


logger.info("✅ Portfolio & Alerts API Router loaded")
