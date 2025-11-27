"""
Connection Manager - مدیریت اتصالات WebSocket و Session
"""

import asyncio
import json
import uuid
from typing import Dict, Set, Optional, Any
from datetime import datetime
from dataclasses import dataclass, asdict
from fastapi import WebSocket
import logging

logger = logging.getLogger(__name__)


@dataclass
class ClientSession:
    """اطلاعات Session کلاینت"""

    session_id: str
    client_type: str  # 'browser', 'api', 'mobile'
    connected_at: datetime
    last_activity: datetime
    ip_address: Optional[str] = None
    user_agent: Optional[str] = None
    metadata: Dict[str, Any] = None

    def to_dict(self):
        return {
            "session_id": self.session_id,
            "client_type": self.client_type,
            "connected_at": self.connected_at.isoformat(),
            "last_activity": self.last_activity.isoformat(),
            "ip_address": self.ip_address,
            "user_agent": self.user_agent,
            "metadata": self.metadata or {},
        }


class ConnectionManager:
    """مدیر اتصالات WebSocket و Session"""

    def __init__(self):
        # WebSocket connections
        self.active_connections: Dict[str, WebSocket] = {}

        # Sessions (برای همه انواع کلاینت‌ها)
        self.sessions: Dict[str, ClientSession] = {}

        # Subscription groups (برای broadcast انتخابی)
        self.subscriptions: Dict[str, Set[str]] = {
            "market": set(),
            "prices": set(),
            "news": set(),
            "alerts": set(),
            "all": set(),
        }

        # Statistics
        self.total_connections = 0
        self.total_messages_sent = 0
        self.total_messages_received = 0

    async def connect(
        self, websocket: WebSocket, client_type: str = "browser", metadata: Optional[Dict] = None
    ) -> str:
        """
        اتصال کلاینت جدید

        Returns:
            session_id
        """
        await websocket.accept()

        session_id = str(uuid.uuid4())

        # ذخیره WebSocket
        self.active_connections[session_id] = websocket

        # ایجاد Session
        session = ClientSession(
            session_id=session_id,
            client_type=client_type,
            connected_at=datetime.now(),
            last_activity=datetime.now(),
            metadata=metadata or {},
        )
        self.sessions[session_id] = session

        # Subscribe به گروه all
        self.subscriptions["all"].add(session_id)

        self.total_connections += 1

        logger.info(f"Client connected: {session_id} ({client_type})")

        # اطلاع به همه از تعداد کاربران آنلاین
        await self.broadcast_stats()

        return session_id

    def disconnect(self, session_id: str):
        """قطع اتصال کلاینت"""
        # حذف WebSocket
        if session_id in self.active_connections:
            del self.active_connections[session_id]

        # حذف از subscriptions
        for group in self.subscriptions.values():
            group.discard(session_id)

        # حذف session
        if session_id in self.sessions:
            del self.sessions[session_id]

        logger.info(f"Client disconnected: {session_id}")

        # اطلاع به همه
        asyncio.create_task(self.broadcast_stats())

    async def send_personal_message(self, message: Dict[str, Any], session_id: str):
        """ارسال پیام به یک کلاینت خاص"""
        if session_id in self.active_connections:
            try:
                websocket = self.active_connections[session_id]
                await websocket.send_json(message)

                # به‌روزرسانی آخرین فعالیت
                if session_id in self.sessions:
                    self.sessions[session_id].last_activity = datetime.now()

                self.total_messages_sent += 1

            except Exception as e:
                logger.error(f"Error sending message to {session_id}: {e}")
                self.disconnect(session_id)

    async def broadcast(self, message: Dict[str, Any], group: str = "all"):
        """ارسال پیام به گروهی از کلاینت‌ها"""
        if group not in self.subscriptions:
            group = "all"

        session_ids = self.subscriptions[group].copy()

        disconnected = []
        for session_id in session_ids:
            if session_id in self.active_connections:
                try:
                    websocket = self.active_connections[session_id]
                    await websocket.send_json(message)
                    self.total_messages_sent += 1
                except Exception as e:
                    logger.error(f"Error broadcasting to {session_id}: {e}")
                    disconnected.append(session_id)

        # پاکسازی اتصالات قطع شده
        for session_id in disconnected:
            self.disconnect(session_id)

    async def broadcast_stats(self):
        """ارسال آمار کلی به همه کلاینت‌ها"""
        stats = self.get_stats()
        await self.broadcast(
            {"type": "stats_update", "data": stats, "timestamp": datetime.now().isoformat()}
        )

    def subscribe(self, session_id: str, group: str):
        """اضافه کردن به گروه subscription"""
        if group in self.subscriptions:
            self.subscriptions[group].add(session_id)
            logger.info(f"Session {session_id} subscribed to {group}")
            return True
        return False

    def unsubscribe(self, session_id: str, group: str):
        """حذف از گروه subscription"""
        if group in self.subscriptions:
            self.subscriptions[group].discard(session_id)
            logger.info(f"Session {session_id} unsubscribed from {group}")
            return True
        return False

    def get_stats(self) -> Dict[str, Any]:
        """دریافت آمار اتصالات"""
        # تفکیک بر اساس نوع کلاینت
        client_types = {}
        for session in self.sessions.values():
            client_type = session.client_type
            client_types[client_type] = client_types.get(client_type, 0) + 1

        # آمار subscriptions
        subscription_stats = {group: len(members) for group, members in self.subscriptions.items()}

        return {
            "active_connections": len(self.active_connections),
            "total_sessions": len(self.sessions),
            "total_connections_ever": self.total_connections,
            "messages_sent": self.total_messages_sent,
            "messages_received": self.total_messages_received,
            "client_types": client_types,
            "subscriptions": subscription_stats,
            "timestamp": datetime.now().isoformat(),
        }

    def get_sessions(self) -> Dict[str, Dict[str, Any]]:
        """دریافت لیست session‌های فعال"""
        return {sid: session.to_dict() for sid, session in self.sessions.items()}

    async def send_market_update(self, data: Dict[str, Any]):
        """ارسال به‌روزرسانی بازار"""
        await self.broadcast(
            {"type": "market_update", "data": data, "timestamp": datetime.now().isoformat()},
            group="market",
        )

    async def send_price_update(self, symbol: str, price: float, change: float):
        """ارسال به‌روزرسانی قیمت"""
        await self.broadcast(
            {
                "type": "price_update",
                "data": {"symbol": symbol, "price": price, "change_24h": change},
                "timestamp": datetime.now().isoformat(),
            },
            group="prices",
        )

    async def send_alert(self, alert_type: str, message: str, severity: str = "info"):
        """ارسال هشدار"""
        await self.broadcast(
            {
                "type": "alert",
                "data": {"alert_type": alert_type, "message": message, "severity": severity},
                "timestamp": datetime.now().isoformat(),
            },
            group="alerts",
        )

    async def heartbeat(self):
        """ارسال heartbeat برای check کردن اتصالات"""
        await self.broadcast({"type": "heartbeat", "timestamp": datetime.now().isoformat()})


# Global instance
connection_manager = ConnectionManager()


def get_connection_manager() -> ConnectionManager:
    """دریافت instance مدیر اتصالات"""
    return connection_manager
