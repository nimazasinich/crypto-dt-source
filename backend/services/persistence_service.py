"""
Persistence Service
Handles data persistence with multiple export formats (JSON, CSV, database)
"""
import json
import csv
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
from pathlib import Path
import asyncio
from collections import defaultdict
import pandas as pd

logger = logging.getLogger(__name__)


class PersistenceService:
    """Service for persisting data in multiple formats"""

    def __init__(self, db_manager=None, data_dir: str = 'data'):
        self.db_manager = db_manager
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)

        # In-memory cache for quick access
        self.cache: Dict[str, Any] = {}
        self.history: Dict[str, List[Dict[str, Any]]] = defaultdict(list)
        self.max_history_per_api = 1000  # Keep last 1000 records per API

    async def save_api_data(
        self,
        api_id: str,
        data: Dict[str, Any],
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        Save API data with metadata

        Args:
            api_id: API identifier
            data: Data to save
            metadata: Additional metadata (category, source, etc.)

        Returns:
            Success status
        """
        try:
            timestamp = datetime.now()

            # Create data record
            record = {
                'api_id': api_id,
                'timestamp': timestamp.isoformat(),
                'data': data,
                'metadata': metadata or {}
            }

            # Update cache
            self.cache[api_id] = record

            # Add to history
            self.history[api_id].append(record)

            # Trim history if needed
            if len(self.history[api_id]) > self.max_history_per_api:
                self.history[api_id] = self.history[api_id][-self.max_history_per_api:]

            # Save to database if available
            if self.db_manager:
                await self._save_to_database(api_id, data, metadata, timestamp)

            logger.debug(f"Saved data for {api_id}")
            return True

        except Exception as e:
            logger.error(f"Error saving data for {api_id}: {e}")
            return False

    async def _save_to_database(
        self,
        api_id: str,
        data: Dict[str, Any],
        metadata: Dict[str, Any],
        timestamp: datetime
    ):
        """Save data to database"""
        if not self.db_manager:
            return

        try:
            # Save using database manager methods
            category = metadata.get('category', 'unknown')

            with self.db_manager.get_session() as session:
                # Find or create provider
                from database.models import Provider, DataCollection

                provider = session.query(Provider).filter_by(name=api_id).first()

                if not provider:
                    # Create new provider
                    provider = Provider(
                        name=api_id,
                        category=category,
                        endpoint_url=metadata.get('url', ''),
                        requires_key=metadata.get('requires_key', False),
                        priority_tier=metadata.get('priority', 3)
                    )
                    session.add(provider)
                    session.flush()

                # Create data collection record
                collection = DataCollection(
                    provider_id=provider.id,
                    category=category,
                    scheduled_time=timestamp,
                    actual_fetch_time=timestamp,
                    data_timestamp=timestamp,
                    staleness_minutes=0,
                    record_count=len(data) if isinstance(data, (list, dict)) else 1,
                    payload_size_bytes=len(json.dumps(data)),
                    on_schedule=True
                )
                session.add(collection)

        except Exception as e:
            logger.error(f"Error saving to database: {e}")

    def get_cached_data(self, api_id: str) -> Optional[Dict[str, Any]]:
        """Get cached data for an API"""
        return self.cache.get(api_id)

    def get_all_cached_data(self) -> Dict[str, Any]:
        """Get all cached data"""
        return self.cache.copy()

    def get_history(self, api_id: str, limit: int = 100) -> List[Dict[str, Any]]:
        """Get historical data for an API"""
        history = self.history.get(api_id, [])
        return history[-limit:] if limit else history

    def get_all_history(self) -> Dict[str, List[Dict[str, Any]]]:
        """Get all historical data"""
        return dict(self.history)

    async def export_to_json(
        self,
        filepath: str,
        api_ids: Optional[List[str]] = None,
        include_history: bool = False
    ) -> bool:
        """
        Export data to JSON file

        Args:
            filepath: Output file path
            api_ids: Specific APIs to export (None = all)
            include_history: Include historical data

        Returns:
            Success status
        """
        try:
            filepath = Path(filepath)
            filepath.parent.mkdir(parents=True, exist_ok=True)

            # Prepare data
            if include_history:
                data = {
                    'cache': self.cache,
                    'history': dict(self.history),
                    'exported_at': datetime.now().isoformat()
                }
            else:
                data = {
                    'cache': self.cache,
                    'exported_at': datetime.now().isoformat()
                }

            # Filter by API IDs if specified
            if api_ids:
                if 'cache' in data:
                    data['cache'] = {k: v for k, v in data['cache'].items() if k in api_ids}
                if 'history' in data:
                    data['history'] = {k: v for k, v in data['history'].items() if k in api_ids}

            # Write to file
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, default=str)

            logger.info(f"Exported data to JSON: {filepath}")
            return True

        except Exception as e:
            logger.error(f"Error exporting to JSON: {e}")
            return False

    async def export_to_csv(
        self,
        filepath: str,
        api_ids: Optional[List[str]] = None,
        flatten: bool = True
    ) -> bool:
        """
        Export data to CSV file

        Args:
            filepath: Output file path
            api_ids: Specific APIs to export (None = all)
            flatten: Flatten nested data structures

        Returns:
            Success status
        """
        try:
            filepath = Path(filepath)
            filepath.parent.mkdir(parents=True, exist_ok=True)

            # Prepare rows
            rows = []

            cache_items = self.cache.items()
            if api_ids:
                cache_items = [(k, v) for k, v in cache_items if k in api_ids]

            for api_id, record in cache_items:
                row = {
                    'api_id': api_id,
                    'timestamp': record.get('timestamp'),
                    'category': record.get('metadata', {}).get('category', ''),
                }

                # Flatten data if requested
                if flatten:
                    data = record.get('data', {})
                    if isinstance(data, dict):
                        for key, value in data.items():
                            # Simple flattening - only first level
                            if isinstance(value, (str, int, float, bool)):
                                row[f'data_{key}'] = value
                            else:
                                row[f'data_{key}'] = json.dumps(value)
                else:
                    row['data'] = json.dumps(record.get('data'))

                rows.append(row)

            # Write CSV
            if rows:
                df = pd.DataFrame(rows)
                df.to_csv(filepath, index=False)
                logger.info(f"Exported data to CSV: {filepath}")
                return True
            else:
                logger.warning("No data to export to CSV")
                return False

        except Exception as e:
            logger.error(f"Error exporting to CSV: {e}")
            return False

    async def export_history_to_csv(
        self,
        filepath: str,
        api_id: str
    ) -> bool:
        """
        Export historical data for a specific API to CSV

        Args:
            filepath: Output file path
            api_id: API identifier

        Returns:
            Success status
        """
        try:
            filepath = Path(filepath)
            filepath.parent.mkdir(parents=True, exist_ok=True)

            history = self.history.get(api_id, [])

            if not history:
                logger.warning(f"No history data for {api_id}")
                return False

            # Prepare rows
            rows = []
            for record in history:
                row = {
                    'timestamp': record.get('timestamp'),
                    'api_id': record.get('api_id'),
                    'data': json.dumps(record.get('data'))
                }
                rows.append(row)

            # Write CSV
            df = pd.DataFrame(rows)
            df.to_csv(filepath, index=False)

            logger.info(f"Exported history for {api_id} to CSV: {filepath}")
            return True

        except Exception as e:
            logger.error(f"Error exporting history to CSV: {e}")
            return False

    async def import_from_json(self, filepath: str) -> bool:
        """
        Import data from JSON file

        Args:
            filepath: Input file path

        Returns:
            Success status
        """
        try:
            filepath = Path(filepath)

            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)

            # Import cache
            if 'cache' in data:
                self.cache.update(data['cache'])

            # Import history
            if 'history' in data:
                for api_id, records in data['history'].items():
                    self.history[api_id].extend(records)

                    # Trim if needed
                    if len(self.history[api_id]) > self.max_history_per_api:
                        self.history[api_id] = self.history[api_id][-self.max_history_per_api:]

            logger.info(f"Imported data from JSON: {filepath}")
            return True

        except Exception as e:
            logger.error(f"Error importing from JSON: {e}")
            return False

    async def backup_all_data(self, backup_dir: Optional[str] = None) -> str:
        """
        Create a backup of all data

        Args:
            backup_dir: Backup directory (uses default if None)

        Returns:
            Path to backup file
        """
        try:
            if backup_dir:
                backup_path = Path(backup_dir)
            else:
                backup_path = self.data_dir / 'backups'

            backup_path.mkdir(parents=True, exist_ok=True)

            # Create backup filename with timestamp
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_file = backup_path / f'backup_{timestamp}.json'

            # Export everything
            await self.export_to_json(
                str(backup_file),
                include_history=True
            )

            logger.info(f"Created backup: {backup_file}")
            return str(backup_file)

        except Exception as e:
            logger.error(f"Error creating backup: {e}")
            raise

    async def restore_from_backup(self, backup_file: str) -> bool:
        """
        Restore data from a backup file

        Args:
            backup_file: Path to backup file

        Returns:
            Success status
        """
        try:
            logger.info(f"Restoring from backup: {backup_file}")
            success = await self.import_from_json(backup_file)

            if success:
                logger.info("Backup restored successfully")

            return success

        except Exception as e:
            logger.error(f"Error restoring from backup: {e}")
            return False

    def clear_cache(self):
        """Clear all cached data"""
        self.cache.clear()
        logger.info("Cache cleared")

    def clear_history(self, api_id: Optional[str] = None):
        """Clear history for specific API or all"""
        if api_id:
            if api_id in self.history:
                del self.history[api_id]
                logger.info(f"Cleared history for {api_id}")
        else:
            self.history.clear()
            logger.info("Cleared all history")

    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about stored data"""
        total_cached = len(self.cache)
        total_history_records = sum(len(records) for records in self.history.values())

        api_stats = {}
        for api_id, records in self.history.items():
            if records:
                timestamps = [
                    datetime.fromisoformat(r['timestamp'])
                    for r in records
                    if 'timestamp' in r
                ]

                if timestamps:
                    api_stats[api_id] = {
                        'record_count': len(records),
                        'oldest': min(timestamps).isoformat(),
                        'newest': max(timestamps).isoformat()
                    }

        return {
            'cached_apis': total_cached,
            'total_history_records': total_history_records,
            'apis_with_history': len(self.history),
            'api_statistics': api_stats
        }

    async def cleanup_old_data(self, days: int = 7) -> int:
        """
        Remove data older than specified days

        Args:
            days: Number of days to keep

        Returns:
            Number of records removed
        """
        try:
            cutoff = datetime.now() - timedelta(days=days)
            removed_count = 0

            for api_id, records in list(self.history.items()):
                original_count = len(records)

                # Filter out old records
                self.history[api_id] = [
                    r for r in records
                    if datetime.fromisoformat(r['timestamp']) > cutoff
                ]

                removed_count += original_count - len(self.history[api_id])

                # Remove empty histories
                if not self.history[api_id]:
                    del self.history[api_id]

            logger.info(f"Cleaned up {removed_count} old records (older than {days} days)")
            return removed_count

        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
            return 0

    async def save_collection_data(
        self,
        api_id: str,
        category: str,
        data: Dict[str, Any],
        timestamp: datetime
    ):
        """
        Save data collection (compatibility method for scheduler)

        Args:
            api_id: API identifier
            category: Data category
            data: Collected data
            timestamp: Collection timestamp
        """
        metadata = {
            'category': category,
            'collection_time': timestamp.isoformat()
        }

        await self.save_api_data(api_id, data, metadata)
