"""Compat layer for DatabaseManager to provide methods expected by legacy app code.

This module monkey-patches the DatabaseManager class from database.db_manager
to add:
- log_provider_status
- get_uptime_percentage
- get_avg_response_time

The implementations are lightweight and defensive: if the underlying engine
is not available, they fail gracefully instead of raising errors.
"""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Optional

try:
    from sqlalchemy import text as _sa_text
except Exception:  # pragma: no cover - extremely defensive
    _sa_text = None  # type: ignore

try:
    from .db_manager import DatabaseManager  # type: ignore
except Exception:  # pragma: no cover
    DatabaseManager = None  # type: ignore


def _get_engine(instance) -> Optional[object]:
    """Best-effort helper to get an SQLAlchemy engine from the manager."""
    return getattr(instance, "engine", None)


def _ensure_table(conn) -> None:
    """Create provider_status table if it does not exist yet."""
    if _sa_text is None:
        return
    conn.execute(
        _sa_text(
            """
            CREATE TABLE IF NOT EXISTS provider_status (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                provider_name TEXT NOT NULL,
                category TEXT NOT NULL,
                status TEXT NOT NULL,
                response_time REAL,
                status_code INTEGER,
                error_message TEXT,
                endpoint_tested TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
    )


def _log_provider_status(
    self,
    provider_name: str,
    category: str,
    status: str,
    response_time: Optional[float] = None,
    status_code: Optional[int] = None,
    endpoint_tested: Optional[str] = None,
    error_message: Optional[str] = None,
) -> None:
    """Insert a status row into provider_status.

    This is a best-effort logger; if no engine is available it silently returns.
    """
    engine = _get_engine(self)
    if engine is None or _sa_text is None:
        return

    now = datetime.utcnow()
    try:
        with engine.begin() as conn:  # type: ignore[call-arg]
            _ensure_table(conn)
            conn.execute(
                _sa_text(
                    """
                    INSERT INTO provider_status (
                        provider_name,
                        category,
                        status,
                        response_time,
                        status_code,
                        error_message,
                        endpoint_tested,
                        created_at
                    )
                    VALUES (
                        :provider_name,
                        :category,
                        :status,
                        :response_time,
                        :status_code,
                        :error_message,
                        :endpoint_tested,
                        :created_at
                    )
                    """
                ),
                {
                    "provider_name": provider_name,
                    "category": category,
                    "status": status,
                    "response_time": response_time,
                    "status_code": status_code,
                    "error_message": error_message,
                    "endpoint_tested": endpoint_tested,
                    "created_at": now,
                },
            )
    except Exception:  # pragma: no cover - we never want this to crash the app
        # Swallow DB errors; health endpoints must not bring the whole app down.
        return


def _get_uptime_percentage(self, provider_name: str, hours: int = 24) -> float:
    """Compute uptime percentage for a provider in the last N hours.

    Uptime is calculated as the ratio of rows with status='online' to total
    rows in the provider_status table within the given time window.
    """
    engine = _get_engine(self)
    if engine is None or _sa_text is None:
        return 0.0

    cutoff = datetime.utcnow() - timedelta(hours=hours)
    try:
        with engine.begin() as conn:  # type: ignore[call-arg]
            _ensure_table(conn)
            result = conn.execute(
                _sa_text(
                    """
                    SELECT
                        COUNT(*) AS total,
                        SUM(CASE WHEN status = 'online' THEN 1 ELSE 0 END) AS online
                    FROM provider_status
                    WHERE provider_name = :provider_name
                      AND created_at >= :cutoff
                    """
                ),
                {"provider_name": provider_name, "cutoff": cutoff},
            ).first()
    except Exception:
        return 0.0

    if not result or result[0] in (None, 0):
        return 0.0

    total = float(result[0] or 0)
    online = float(result[1] or 0)
    return round(100.0 * online / total, 2)


def _get_avg_response_time(self, provider_name: str, hours: int = 24) -> float:
    """Average response time (ms) for a provider over the last N hours."""
    engine = _get_engine(self)
    if engine is None or _sa_text is None:
        return 0.0

    cutoff = datetime.utcnow() - timedelta(hours=hours)
    try:
        with engine.begin() as conn:  # type: ignore[call-arg]
            _ensure_table(conn)
            result = conn.execute(
                _sa_text(
                    """
                    SELECT AVG(response_time) AS avg_response
                    FROM provider_status
                    WHERE provider_name = :provider_name
                      AND response_time IS NOT NULL
                      AND created_at >= :cutoff
                    """
                ),
                {"provider_name": provider_name, "cutoff": cutoff},
            ).first()
    except Exception:
        return 0.0

    if not result or result[0] is None:
        return 0.0

    return round(float(result[0]), 2)


# Apply monkey-patches when this module is imported.
if DatabaseManager is not None:  # pragma: no cover
    if not hasattr(DatabaseManager, "log_provider_status"):
        DatabaseManager.log_provider_status = _log_provider_status  # type: ignore[attr-defined]
    if not hasattr(DatabaseManager, "get_uptime_percentage"):
        DatabaseManager.get_uptime_percentage = _get_uptime_percentage  # type: ignore[attr-defined]
    if not hasattr(DatabaseManager, "get_avg_response_time"):
        DatabaseManager.get_avg_response_time = _get_avg_response_time  # type: ignore[attr-defined]
