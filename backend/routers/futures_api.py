#!/usr/bin/env python3
"""
Futures Trading API Router
===========================
API endpoints for futures trading operations
"""

from fastapi import APIRouter, HTTPException, Depends, Body, Path, Query
from fastapi.responses import JSONResponse
from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
import logging

from backend.services.futures_trading_service import FuturesTradingService
from database.db_manager import db_manager

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/futures",
    tags=["Futures Trading"]
)


# ============================================================================
# Pydantic Models
# ============================================================================

class OrderRequest(BaseModel):
    """Request model for creating an order."""
    symbol: str = Field(..., description="Trading pair (e.g., BTC/USDT)")
    side: str = Field(..., description="Order side: 'buy' or 'sell'")
    order_type: str = Field(..., description="Order type: 'market', 'limit', 'stop', 'stop_limit'")
    quantity: float = Field(..., gt=0, description="Order quantity")
    price: Optional[float] = Field(None, gt=0, description="Limit price (required for limit orders)")
    stop_price: Optional[float] = Field(None, gt=0, description="Stop price (required for stop orders)")
    exchange: str = Field("demo", description="Exchange name (default: 'demo')")


# ============================================================================
# Dependency Injection
# ============================================================================

def get_db() -> Session:
    """Get database session."""
    db = db_manager.SessionLocal()
    try:
        yield db
    finally:
        db.close()


def get_futures_service(db: Session = Depends(get_db)) -> FuturesTradingService:
    """Get futures trading service instance."""
    return FuturesTradingService(db)


# ============================================================================
# API Endpoints
# ============================================================================

@router.post("/order")
async def execute_order(
    order_request: OrderRequest,
    service: FuturesTradingService = Depends(get_futures_service)
) -> JSONResponse:
    """
    Execute a futures trading order.
    
    Creates and processes a new futures order. For market orders, execution is immediate.
    For limit and stop orders, the order is placed in the order book.
    
    Args:
        order_request: Order details
        service: Futures trading service instance
    
    Returns:
        JSON response with order details
    """
    try:
        order = service.create_order(
            symbol=order_request.symbol,
            side=order_request.side,
            order_type=order_request.order_type,
            quantity=order_request.quantity,
            price=order_request.price,
            stop_price=order_request.stop_price,
            exchange=order_request.exchange
        )
        
        return JSONResponse(
            status_code=201,
            content={
                "success": True,
                "message": "Order created successfully",
                "data": order
            }
        )
    
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error executing order: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/positions")
async def get_positions(
    symbol: Optional[str] = Query(None, description="Filter by trading pair"),
    is_open: Optional[bool] = Query(True, description="Filter by open status"),
    service: FuturesTradingService = Depends(get_futures_service)
) -> JSONResponse:
    """
    Retrieve open futures positions.
    
    Returns all open positions, optionally filtered by symbol.
    
    Args:
        symbol: Optional trading pair filter
        is_open: Filter by open status (default: True)
        service: Futures trading service instance
    
    Returns:
        JSON response with list of positions
    """
    try:
        positions = service.get_positions(symbol=symbol, is_open=is_open)
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "count": len(positions),
                "data": positions
            }
        )
    
    except Exception as e:
        logger.error(f"Error retrieving positions: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.get("/orders")
async def list_orders(
    symbol: Optional[str] = Query(None, description="Filter by trading pair"),
    status: Optional[str] = Query(None, description="Filter by order status"),
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of orders to return"),
    service: FuturesTradingService = Depends(get_futures_service)
) -> JSONResponse:
    """
    List all trading orders.
    
    Returns all orders, optionally filtered by symbol and status.
    
    Args:
        symbol: Optional trading pair filter
        status: Optional order status filter
        limit: Maximum number of orders to return
        service: Futures trading service instance
    
    Returns:
        JSON response with list of orders
    """
    try:
        orders = service.get_orders(symbol=symbol, status=status, limit=limit)
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "count": len(orders),
                "data": orders
            }
        )
    
    except Exception as e:
        logger.error(f"Error retrieving orders: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")


@router.delete("/order/{order_id}")
async def cancel_order(
    order_id: str = Path(..., description="Order ID to cancel"),
    service: FuturesTradingService = Depends(get_futures_service)
) -> JSONResponse:
    """
    Cancel a specific order.
    
    Cancels an open or pending order by ID.
    
    Args:
        order_id: The order ID to cancel
        service: Futures trading service instance
    
    Returns:
        JSON response with cancelled order details
    """
    try:
        order = service.cancel_order(order_id)
        
        return JSONResponse(
            status_code=200,
            content={
                "success": True,
                "message": "Order cancelled successfully",
                "data": order
            }
        )
    
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error(f"Error cancelling order: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")

