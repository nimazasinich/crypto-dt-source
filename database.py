"""
SQLite Database Module for Persistent Storage
Stores health metrics, incidents, and historical data
"""

import sqlite3
import json
import logging
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from pathlib import Path
from contextlib import contextmanager
from monitor import HealthCheckResult, HealthStatus

logger = logging.getLogger(__name__)


class Database:
    """SQLite database manager for metrics and history"""

    def __init__(self, db_path: str = "data/health_metrics.db"):
        """Initialize database connection"""
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_database()

    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Enable column access by name
        try:
            yield conn
            conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()

    def _init_database(self):
        """Initialize database schema"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Status log table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS status_log (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    provider_name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    status TEXT NOT NULL,
                    response_time REAL,
                    status_code INTEGER,
                    error_message TEXT,
                    endpoint_tested TEXT,
                    timestamp REAL NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Response times table (aggregated)
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS response_times (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    provider_name TEXT NOT NULL,
                    avg_response_time REAL NOT NULL,
                    min_response_time REAL NOT NULL,
                    max_response_time REAL NOT NULL,
                    sample_count INTEGER NOT NULL,
                    period_start TIMESTAMP NOT NULL,
                    period_end TIMESTAMP NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Incidents table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS incidents (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    provider_name TEXT NOT NULL,
                    category TEXT NOT NULL,
                    incident_type TEXT NOT NULL,
                    description TEXT,
                    severity TEXT,
                    start_time TIMESTAMP NOT NULL,
                    end_time TIMESTAMP,
                    duration_seconds INTEGER,
                    resolved BOOLEAN DEFAULT 0,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Alerts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    provider_name TEXT NOT NULL,
                    alert_type TEXT NOT NULL,
                    message TEXT,
                    threshold_value REAL,
                    actual_value REAL,
                    triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    acknowledged BOOLEAN DEFAULT 0
                )
            """)

            # Configuration table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS configuration (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)

            # Create indexes
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_status_log_provider
                ON status_log(provider_name, timestamp)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_status_log_timestamp
                ON status_log(timestamp)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_incidents_provider
                ON incidents(provider_name, start_time)
            """)

            logger.info("Database initialized successfully")

    def save_health_check(self, result: HealthCheckResult):
        """Save a single health check result"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO status_log
                (provider_name, category, status, response_time, status_code,
                 error_message, endpoint_tested, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                result.provider_name,
                result.category,
                result.status.value,
                result.response_time,
                result.status_code,
                result.error_message,
                result.endpoint_tested,
                result.timestamp
            ))

    def save_health_checks(self, results: List[HealthCheckResult]):
        """Save multiple health check results"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.executemany("""
                INSERT INTO status_log
                (provider_name, category, status, response_time, status_code,
                 error_message, endpoint_tested, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, [
                (r.provider_name, r.category, r.status.value, r.response_time,
                 r.status_code, r.error_message, r.endpoint_tested, r.timestamp)
                for r in results
            ])
        logger.info(f"Saved {len(results)} health check results")

    def get_recent_status(
        self,
        provider_name: Optional[str] = None,
        hours: int = 24,
        limit: int = 1000
    ) -> List[Dict]:
        """Get recent status logs"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cutoff_time = datetime.now() - timedelta(hours=hours)

            if provider_name:
                query = """
                    SELECT * FROM status_log
                    WHERE provider_name = ? AND created_at >= ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """
                cursor.execute(query, (provider_name, cutoff_time, limit))
            else:
                query = """
                    SELECT * FROM status_log
                    WHERE created_at >= ?
                    ORDER BY timestamp DESC
                    LIMIT ?
                """
                cursor.execute(query, (cutoff_time, limit))

            return [dict(row) for row in cursor.fetchall()]

    def get_uptime_percentage(
        self,
        provider_name: str,
        hours: int = 24
    ) -> float:
        """Calculate uptime percentage from database"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cutoff_time = datetime.now() - timedelta(hours=hours)

            cursor.execute("""
                SELECT
                    COUNT(*) as total,
                    SUM(CASE WHEN status = 'online' THEN 1 ELSE 0 END) as online
                FROM status_log
                WHERE provider_name = ? AND created_at >= ?
            """, (provider_name, cutoff_time))

            row = cursor.fetchone()
            if row['total'] > 0:
                return round((row['online'] / row['total']) * 100, 2)
            return 0.0

    def get_avg_response_time(
        self,
        provider_name: str,
        hours: int = 24
    ) -> float:
        """Get average response time from database"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cutoff_time = datetime.now() - timedelta(hours=hours)

            cursor.execute("""
                SELECT AVG(response_time) as avg_time
                FROM status_log
                WHERE provider_name = ?
                  AND created_at >= ?
                  AND response_time IS NOT NULL
            """, (provider_name, cutoff_time))

            row = cursor.fetchone()
            return round(row['avg_time'], 2) if row['avg_time'] else 0.0

    def create_incident(
        self,
        provider_name: str,
        category: str,
        incident_type: str,
        description: str,
        severity: str = "medium"
    ) -> int:
        """Create a new incident"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO incidents
                (provider_name, category, incident_type, description, severity, start_time)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (provider_name, category, incident_type, description, severity, datetime.now()))
            return cursor.lastrowid

    def resolve_incident(self, incident_id: int):
        """Resolve an incident"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Get start time
            cursor.execute("SELECT start_time FROM incidents WHERE id = ?", (incident_id,))
            row = cursor.fetchone()
            if not row:
                return

            start_time = datetime.fromisoformat(row['start_time'])
            end_time = datetime.now()
            duration = int((end_time - start_time).total_seconds())

            cursor.execute("""
                UPDATE incidents
                SET end_time = ?, duration_seconds = ?, resolved = 1
                WHERE id = ?
            """, (end_time, duration, incident_id))

    def get_active_incidents(self) -> List[Dict]:
        """Get all active incidents"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM incidents
                WHERE resolved = 0
                ORDER BY start_time DESC
            """)
            return [dict(row) for row in cursor.fetchall()]

    def get_incident_history(self, hours: int = 24, limit: int = 100) -> List[Dict]:
        """Get incident history"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cutoff_time = datetime.now() - timedelta(hours=hours)

            cursor.execute("""
                SELECT * FROM incidents
                WHERE start_time >= ?
                ORDER BY start_time DESC
                LIMIT ?
            """, (cutoff_time, limit))

            return [dict(row) for row in cursor.fetchall()]

    def create_alert(
        self,
        provider_name: str,
        alert_type: str,
        message: str,
        threshold_value: Optional[float] = None,
        actual_value: Optional[float] = None
    ) -> int:
        """Create a new alert"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO alerts
                (provider_name, alert_type, message, threshold_value, actual_value)
                VALUES (?, ?, ?, ?, ?)
            """, (provider_name, alert_type, message, threshold_value, actual_value))
            return cursor.lastrowid

    def get_unacknowledged_alerts(self) -> List[Dict]:
        """Get all unacknowledged alerts"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT * FROM alerts
                WHERE acknowledged = 0
                ORDER BY triggered_at DESC
            """)
            return [dict(row) for row in cursor.fetchall()]

    def acknowledge_alert(self, alert_id: int):
        """Acknowledge an alert"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                UPDATE alerts
                SET acknowledged = 1
                WHERE id = ?
            """, (alert_id,))

    def aggregate_response_times(self, period_hours: int = 1):
        """Aggregate response times for the period"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            period_start = datetime.now() - timedelta(hours=period_hours)

            cursor.execute("""
                INSERT INTO response_times
                (provider_name, avg_response_time, min_response_time, max_response_time,
                 sample_count, period_start, period_end)
                SELECT
                    provider_name,
                    AVG(response_time) as avg_time,
                    MIN(response_time) as min_time,
                    MAX(response_time) as max_time,
                    COUNT(*) as count,
                    ? as period_start,
                    ? as period_end
                FROM status_log
                WHERE created_at >= ? AND response_time IS NOT NULL
                GROUP BY provider_name
            """, (period_start, datetime.now(), period_start))

            logger.info(f"Aggregated response times for period: {period_start}")

    def cleanup_old_data(self, days: int = 7):
        """Clean up data older than specified days"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cutoff_date = datetime.now() - timedelta(days=days)

            # Delete old status logs
            cursor.execute("""
                DELETE FROM status_log
                WHERE created_at < ?
            """, (cutoff_date,))
            deleted_logs = cursor.rowcount

            # Delete old resolved incidents
            cursor.execute("""
                DELETE FROM incidents
                WHERE resolved = 1 AND end_time < ?
            """, (cutoff_date,))
            deleted_incidents = cursor.rowcount

            # Delete old acknowledged alerts
            cursor.execute("""
                DELETE FROM alerts
                WHERE acknowledged = 1 AND triggered_at < ?
            """, (cutoff_date,))
            deleted_alerts = cursor.rowcount

            logger.info(
                f"Cleanup: {deleted_logs} logs, {deleted_incidents} incidents, "
                f"{deleted_alerts} alerts older than {days} days"
            )

    def get_provider_stats(self, provider_name: str, hours: int = 24) -> Dict:
        """Get comprehensive stats for a provider"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            cutoff_time = datetime.now() - timedelta(hours=hours)

            # Get status distribution
            cursor.execute("""
                SELECT
                    status,
                    COUNT(*) as count
                FROM status_log
                WHERE provider_name = ? AND created_at >= ?
                GROUP BY status
            """, (provider_name, cutoff_time))

            status_dist = {row['status']: row['count'] for row in cursor.fetchall()}

            # Get response time stats
            cursor.execute("""
                SELECT
                    AVG(response_time) as avg_time,
                    MIN(response_time) as min_time,
                    MAX(response_time) as max_time,
                    COUNT(*) as total_checks
                FROM status_log
                WHERE provider_name = ?
                  AND created_at >= ?
                  AND response_time IS NOT NULL
            """, (provider_name, cutoff_time))

            row = cursor.fetchone()

            return {
                'provider_name': provider_name,
                'period_hours': hours,
                'status_distribution': status_dist,
                'avg_response_time': round(row['avg_time'], 2) if row['avg_time'] else 0,
                'min_response_time': round(row['min_time'], 2) if row['min_time'] else 0,
                'max_response_time': round(row['max_time'], 2) if row['max_time'] else 0,
                'total_checks': row['total_checks'] or 0,
                'uptime_percentage': self.get_uptime_percentage(provider_name, hours)
            }

    def export_to_csv(self, output_path: str, hours: int = 24):
        """Export recent data to CSV"""
        import csv

        with self.get_connection() as conn:
            cursor = conn.cursor()

            cutoff_time = datetime.now() - timedelta(hours=hours)

            cursor.execute("""
                SELECT * FROM status_log
                WHERE created_at >= ?
                ORDER BY timestamp DESC
            """, (cutoff_time,))

            rows = cursor.fetchall()

            if rows:
                with open(output_path, 'w', newline='') as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=rows[0].keys())
                    writer.writeheader()
                    for row in rows:
                        writer.writerow(dict(row))

                logger.info(f"Exported {len(rows)} rows to {output_path}")
