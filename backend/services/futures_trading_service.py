#!/usr/bin/env python3
"""
Futures Trading Service
========================
سرویس مدیریت معاملات Futures با قابلیت اجرای دستورات، مدیریت موقعیت‌ها و پیگیری سفارشات
"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from sqlalchemy import and_
import uuid
import logging

from database.models import (
    Base, FuturesOrder, FuturesPosition, OrderStatus, OrderSide, OrderType
)

logger = logging.getLogger(__name__)


class FuturesTradingService:
    """سرویس اصلی مدیریت معاملات Futures"""

    def __init__(self, db_session: Session):
        """
        Initialize the futures trading service.
        
        Args:
            db_session: SQLAlchemy database session
        """
        self.db = db_session

    def create_order(
        self,
        symbol: str,
        side: str,
        order_type: str,
        quantity: float,
        price: Optional[float] = None,
        stop_price: Optional[float] = None,
        exchange: str = "demo"
    ) -> Dict[str, Any]:
        """
        Create and execute a futures trading order.
        
        Args:
            symbol: Trading pair (e.g., "BTC/USDT")
            side: Order side ("buy" or "sell")
            order_type: Order type ("market", "limit", "stop", "stop_limit")
            quantity: Order quantity
            price: Limit price (required for limit orders)
            stop_price: Stop price (required for stop orders)
            exchange: Exchange name (default: "demo")
        
        Returns:
            Dict containing order details
        """
        try:
            # Validate inputs
            if order_type in ["limit", "stop_limit"] and not price:
                raise ValueError(f"Price is required for {order_type} orders")
            
            if order_type in ["stop", "stop_limit"] and not stop_price:
                raise ValueError(f"Stop price is required for {order_type} orders")

            # Generate order ID
            order_id = f"ORD-{uuid.uuid4().hex[:12].upper()}"

            # Create order record
            order = FuturesOrder(
                order_id=order_id,
                symbol=symbol.upper(),
                side=OrderSide.BUY if side.lower() == "buy" else OrderSide.SELL,
                order_type=OrderType[order_type.upper()],
                quantity=quantity,
                price=price,
                stop_price=stop_price,
                status=OrderStatus.OPEN if order_type == "market" else OrderStatus.PENDING,
                exchange=exchange
            )

            self.db.add(order)
            self.db.commit()
            self.db.refresh(order)

            # Execute market orders immediately (in demo mode)
            if order_type == "market":
                self._execute_market_order(order)

            logger.info(f"Created order {order_id} for {symbol} {side} {quantity} @ {price or 'MARKET'}")

            return self._order_to_dict(order)

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error creating order: {e}", exc_info=True)
            raise

    def _execute_market_order(self, order: FuturesOrder) -> None:
        """
        Execute a market order immediately (demo mode).
        
        Args:
            order: The order to execute
        """
        try:
            # In demo mode, we simulate immediate execution
            # In production, this would call exchange API
            
            order.status = OrderStatus.FILLED
            order.filled_quantity = order.quantity
            # Simulate fill price (in production, use actual market price)
            order.average_fill_price = order.price or 50000.0  # Placeholder
            order.executed_at = datetime.utcnow()

            # Create or update position
            self._update_position_from_order(order)

            self.db.commit()

        except Exception as e:
            logger.error(f"Error executing market order: {e}", exc_info=True)
            raise

    def _update_position_from_order(self, order: FuturesOrder) -> None:
        """
        Update position based on filled order.
        
        Args:
            order: The filled order
        """
        try:
            # Find existing open position
            position = self.db.query(FuturesPosition).filter(
                and_(
                    FuturesPosition.symbol == order.symbol,
                    FuturesPosition.is_open == True
                )
            ).first()

            if position:
                # Update existing position
                if position.side == order.side:
                    # Increase position
                    total_value = (position.quantity * position.entry_price) + \
                                 (order.filled_quantity * order.average_fill_price)
                    total_quantity = position.quantity + order.filled_quantity
                    position.entry_price = total_value / total_quantity if total_quantity > 0 else position.entry_price
                    position.quantity = total_quantity
                else:
                    # Close or reduce position
                    if order.filled_quantity >= position.quantity:
                        # Close position
                        realized_pnl = (order.average_fill_price - position.entry_price) * position.quantity
                        if position.side == OrderSide.SELL:
                            realized_pnl = -realized_pnl
                        
                        position.realized_pnl += realized_pnl
                        position.is_open = False
                        position.closed_at = datetime.utcnow()
                    else:
                        # Reduce position
                        realized_pnl = (order.average_fill_price - position.entry_price) * order.filled_quantity
                        if position.side == OrderSide.SELL:
                            realized_pnl = -realized_pnl
                        
                        position.realized_pnl += realized_pnl
                        position.quantity -= order.filled_quantity
            else:
                # Create new position
                position = FuturesPosition(
                    symbol=order.symbol,
                    side=order.side,
                    quantity=order.filled_quantity,
                    entry_price=order.average_fill_price,
                    current_price=order.average_fill_price,
                    exchange=order.exchange
                )
                self.db.add(position)

            self.db.commit()

        except Exception as e:
            logger.error(f"Error updating position: {e}", exc_info=True)
            raise

    def get_positions(
        self,
        symbol: Optional[str] = None,
        is_open: Optional[bool] = True
    ) -> List[Dict[str, Any]]:
        """
        Retrieve futures positions.
        
        Args:
            symbol: Filter by symbol (optional)
            is_open: Filter by open status (optional)
        
        Returns:
            List of position dictionaries
        """
        try:
            query = self.db.query(FuturesPosition)

            if symbol:
                query = query.filter(FuturesPosition.symbol == symbol.upper())

            if is_open is not None:
                query = query.filter(FuturesPosition.is_open == is_open)

            positions = query.order_by(FuturesPosition.opened_at.desc()).all()

            return [self._position_to_dict(p) for p in positions]

        except Exception as e:
            logger.error(f"Error retrieving positions: {e}", exc_info=True)
            raise

    def get_orders(
        self,
        symbol: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """
        List all trading orders.
        
        Args:
            symbol: Filter by symbol (optional)
            status: Filter by status (optional)
            limit: Maximum number of orders to return
        
        Returns:
            List of order dictionaries
        """
        try:
            query = self.db.query(FuturesOrder)

            if symbol:
                query = query.filter(FuturesOrder.symbol == symbol.upper())

            if status:
                query = query.filter(FuturesOrder.status == OrderStatus[status.upper()])

            orders = query.order_by(FuturesOrder.created_at.desc()).limit(limit).all()

            return [self._order_to_dict(o) for o in orders]

        except Exception as e:
            logger.error(f"Error retrieving orders: {e}", exc_info=True)
            raise

    def cancel_order(self, order_id: str) -> Dict[str, Any]:
        """
        Cancel a specific order.
        
        Args:
            order_id: The order ID to cancel
        
        Returns:
            Dict containing cancelled order details
        """
        try:
            order = self.db.query(FuturesOrder).filter(
                FuturesOrder.order_id == order_id
            ).first()

            if not order:
                raise ValueError(f"Order {order_id} not found")

            if order.status in [OrderStatus.FILLED, OrderStatus.CANCELLED]:
                raise ValueError(f"Cannot cancel order with status {order.status.value}")

            order.status = OrderStatus.CANCELLED
            order.cancelled_at = datetime.utcnow()

            self.db.commit()
            self.db.refresh(order)

            logger.info(f"Cancelled order {order_id}")

            return self._order_to_dict(order)

        except Exception as e:
            self.db.rollback()
            logger.error(f"Error cancelling order: {e}", exc_info=True)
            raise

    def _order_to_dict(self, order: FuturesOrder) -> Dict[str, Any]:
        """Convert order model to dictionary."""
        return {
            "id": order.id,
            "order_id": order.order_id,
            "symbol": order.symbol,
            "side": order.side.value if order.side else None,
            "order_type": order.order_type.value if order.order_type else None,
            "quantity": order.quantity,
            "price": order.price,
            "stop_price": order.stop_price,
            "status": order.status.value if order.status else None,
            "filled_quantity": order.filled_quantity,
            "average_fill_price": order.average_fill_price,
            "exchange": order.exchange,
            "created_at": order.created_at.isoformat() if order.created_at else None,
            "updated_at": order.updated_at.isoformat() if order.updated_at else None,
            "executed_at": order.executed_at.isoformat() if order.executed_at else None,
            "cancelled_at": order.cancelled_at.isoformat() if order.cancelled_at else None
        }

    def _position_to_dict(self, position: FuturesPosition) -> Dict[str, Any]:
        """Convert position model to dictionary."""
        return {
            "id": position.id,
            "symbol": position.symbol,
            "side": position.side.value if position.side else None,
            "quantity": position.quantity,
            "entry_price": position.entry_price,
            "current_price": position.current_price,
            "leverage": position.leverage,
            "unrealized_pnl": position.unrealized_pnl,
            "realized_pnl": position.realized_pnl,
            "exchange": position.exchange,
            "is_open": position.is_open,
            "opened_at": position.opened_at.isoformat() if position.opened_at else None,
            "closed_at": position.closed_at.isoformat() if position.closed_at else None,
            "updated_at": position.updated_at.isoformat() if position.updated_at else None
        }

