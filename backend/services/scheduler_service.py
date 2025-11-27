"""
Enhanced Scheduler Service
Manages periodic and real-time data updates with persistence
"""

import asyncio
import logging
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, asdict
import json
from collections import defaultdict
import httpx

logger = logging.getLogger(__name__)


@dataclass
class ScheduleTask:
    """Represents a scheduled task"""

    api_id: str
    name: str
    category: str
    interval: int  # seconds
    update_type: str  # realtime, periodic, scheduled
    enabled: bool
    last_update: Optional[datetime] = None
    next_update: Optional[datetime] = None
    last_status: Optional[str] = None  # success, failed, pending
    last_data: Optional[Dict[str, Any]] = None
    error_count: int = 0
    success_count: int = 0


class SchedulerService:
    """Advanced scheduler for managing API data updates"""

    def __init__(self, config_loader, db_manager=None):
        self.config_loader = config_loader
        self.db_manager = db_manager
        self.tasks: Dict[str, ScheduleTask] = {}
        self.running = False
        self.periodic_task = None
        self.realtime_tasks: Dict[str, asyncio.Task] = {}
        self.data_cache: Dict[str, Any] = {}
        self.callbacks: Dict[str, List[Callable]] = defaultdict(list)

        # Initialize tasks from config
        self._initialize_tasks()

    def _initialize_tasks(self):
        """Initialize schedule tasks from config loader"""
        apis = self.config_loader.get_all_apis()
        schedules = self.config_loader.schedules

        for api_id, api in apis.items():
            schedule = schedules.get(api_id, {})

            task = ScheduleTask(
                api_id=api_id,
                name=api.get("name", api_id),
                category=api.get("category", "unknown"),
                interval=schedule.get("interval", 300),
                update_type=api.get("update_type", "periodic"),
                enabled=schedule.get("enabled", True),
                next_update=datetime.now(),
            )

            self.tasks[api_id] = task

        logger.info(f"Initialized {len(self.tasks)} schedule tasks")

    async def start(self):
        """Start the scheduler"""
        if self.running:
            logger.warning("Scheduler already running")
            return

        self.running = True
        logger.info("Starting scheduler...")

        # Start periodic update loop
        self.periodic_task = asyncio.create_task(self._periodic_update_loop())

        # Start real-time tasks
        await self._start_realtime_tasks()

        logger.info("Scheduler started successfully")

    async def stop(self):
        """Stop the scheduler"""
        if not self.running:
            return

        self.running = False
        logger.info("Stopping scheduler...")

        # Cancel periodic task
        if self.periodic_task:
            self.periodic_task.cancel()
            try:
                await self.periodic_task
            except asyncio.CancelledError:
                pass

        # Cancel real-time tasks
        for task in self.realtime_tasks.values():
            task.cancel()

        logger.info("Scheduler stopped")

    async def _periodic_update_loop(self):
        """Main loop for periodic updates"""
        while self.running:
            try:
                # Get tasks due for update
                due_tasks = self._get_due_tasks()

                if due_tasks:
                    logger.info(f"Processing {len(due_tasks)} due tasks")

                    # Process tasks concurrently
                    await asyncio.gather(
                        *[self._execute_task(task) for task in due_tasks], return_exceptions=True
                    )

                # Sleep for a short interval
                await asyncio.sleep(5)  # Check every 5 seconds

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in periodic update loop: {e}")
                await asyncio.sleep(10)

    def _get_due_tasks(self) -> List[ScheduleTask]:
        """Get tasks that are due for update"""
        now = datetime.now()
        due_tasks = []

        for task in self.tasks.values():
            if not task.enabled:
                continue

            if task.update_type == "realtime":
                continue  # Real-time tasks handled separately

            if task.next_update is None or now >= task.next_update:
                due_tasks.append(task)

        return due_tasks

    async def _execute_task(self, task: ScheduleTask):
        """Execute a single scheduled task"""
        try:
            api = self.config_loader.apis.get(task.api_id)
            if not api:
                logger.error(f"API not found: {task.api_id}")
                return

            # Fetch data from API
            data = await self._fetch_api_data(api)

            # Update task status
            task.last_update = datetime.now()
            task.next_update = task.last_update + timedelta(seconds=task.interval)
            task.last_status = "success"
            task.last_data = data
            task.success_count += 1
            task.error_count = 0  # Reset error count on success

            # Cache data
            self.data_cache[task.api_id] = {
                "data": data,
                "timestamp": datetime.now(),
                "task": task.name,
            }

            # Save to database if available
            if self.db_manager:
                await self._save_to_database(task, data)

            # Trigger callbacks
            await self._trigger_callbacks(task.api_id, data)

            # Mark as updated in config loader
            self.config_loader.mark_updated(task.api_id)

            logger.info(f"✓ Updated {task.name} ({task.category})")

        except Exception as e:
            logger.error(f"✗ Failed to update {task.name}: {e}")
            task.last_status = "failed"
            task.error_count += 1

            # Increase interval on repeated failures
            if task.error_count >= 3:
                task.interval = min(task.interval * 2, 3600)  # Max 1 hour
                logger.warning(f"Increased interval for {task.name} to {task.interval}s")

    async def _fetch_api_data(self, api: Dict[str, Any]) -> Dict[str, Any]:
        """Fetch data from an API"""
        base_url = api.get("base_url", "")
        auth = api.get("auth", {})

        # Build request URL
        url = base_url

        # Handle authentication
        headers = {}
        params = {}

        auth_type = auth.get("type", "none")

        if auth_type == "apiKey" or auth_type == "apiKeyHeader":
            key = auth.get("key")
            header_name = auth.get("header_name", "X-API-Key")
            if key:
                headers[header_name] = key

        elif auth_type == "apiKeyQuery":
            key = auth.get("key")
            param_name = auth.get("param_name", "apikey")
            if key:
                params[param_name] = key

        elif auth_type == "apiKeyPath":
            key = auth.get("key")
            param_name = auth.get("param_name", "API_KEY")
            if key:
                url = url.replace(f"{{{param_name}}}", key)

        # Make request
        timeout = httpx.Timeout(10.0)

        async with httpx.AsyncClient(timeout=timeout) as client:
            # Handle different endpoints
            endpoints = api.get("endpoints")

            if isinstance(endpoints, dict) and "health" in endpoints:
                url = endpoints["health"]
            elif isinstance(endpoints, str):
                url = endpoints

            # Add query params
            if params:
                url = f"{url}{'&' if '?' in url else '?'}" + "&".join(
                    f"{k}={v}" for k, v in params.items()
                )

            response = await client.get(url, headers=headers)
            response.raise_for_status()

            return response.json()

    async def _save_to_database(self, task: ScheduleTask, data: Dict[str, Any]):
        """Save task data to database"""
        if not self.db_manager:
            return

        try:
            # Save using database manager
            await self.db_manager.save_collection_data(
                api_id=task.api_id, category=task.category, data=data, timestamp=datetime.now()
            )
        except Exception as e:
            logger.error(f"Error saving to database: {e}")

    async def _trigger_callbacks(self, api_id: str, data: Dict[str, Any]):
        """Trigger callbacks for API updates"""
        if api_id in self.callbacks:
            for callback in self.callbacks[api_id]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(api_id, data)
                    else:
                        callback(api_id, data)
                except Exception as e:
                    logger.error(f"Error in callback for {api_id}: {e}")

    async def _start_realtime_tasks(self):
        """Start WebSocket connections for real-time APIs"""
        realtime_apis = self.config_loader.get_realtime_apis()

        for api_id, api in realtime_apis.items():
            task = self.tasks.get(api_id)

            if task and task.enabled:
                # Create WebSocket task
                ws_task = asyncio.create_task(self._realtime_task(task, api))
                self.realtime_tasks[api_id] = ws_task

        logger.info(f"Started {len(self.realtime_tasks)} real-time tasks")

    async def _realtime_task(self, task: ScheduleTask, api: Dict[str, Any]):
        """Handle real-time WebSocket connection"""
        # This is a placeholder - implement WebSocket connection logic
        # based on the specific API requirements
        while self.running:
            try:
                # Connect to WebSocket
                # ws_url = api.get('base_url')
                # async with websockets.connect(ws_url) as ws:
                #     async for message in ws:
                #         data = json.loads(message)
                #         await self._handle_realtime_data(task, data)

                logger.info(f"Real-time task for {task.name} (placeholder)")
                await asyncio.sleep(60)  # Placeholder

            except asyncio.CancelledError:
                break
            except Exception as e:
                logger.error(f"Error in real-time task {task.name}: {e}")
                await asyncio.sleep(30)  # Retry after delay

    async def _handle_realtime_data(self, task: ScheduleTask, data: Dict[str, Any]):
        """Handle incoming real-time data"""
        task.last_update = datetime.now()
        task.last_status = "success"
        task.last_data = data
        task.success_count += 1

        # Cache data
        self.data_cache[task.api_id] = {
            "data": data,
            "timestamp": datetime.now(),
            "task": task.name,
        }

        # Save to database
        if self.db_manager:
            await self._save_to_database(task, data)

        # Trigger callbacks
        await self._trigger_callbacks(task.api_id, data)

    def register_callback(self, api_id: str, callback: Callable):
        """Register a callback for API updates"""
        self.callbacks[api_id].append(callback)

    def unregister_callback(self, api_id: str, callback: Callable):
        """Unregister a callback"""
        if api_id in self.callbacks:
            self.callbacks[api_id] = [cb for cb in self.callbacks[api_id] if cb != callback]

    def update_task_schedule(self, api_id: str, interval: int = None, enabled: bool = None):
        """Update schedule for a task"""
        if api_id in self.tasks:
            task = self.tasks[api_id]

            if interval is not None:
                task.interval = interval
                self.config_loader.update_schedule(api_id, interval=interval)

            if enabled is not None:
                task.enabled = enabled
                self.config_loader.update_schedule(api_id, enabled=enabled)

            logger.info(f"Updated schedule for {task.name}")

    def get_task_status(self, api_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific task"""
        task = self.tasks.get(api_id)

        if not task:
            return None

        return {
            "api_id": task.api_id,
            "name": task.name,
            "category": task.category,
            "interval": task.interval,
            "update_type": task.update_type,
            "enabled": task.enabled,
            "last_update": task.last_update.isoformat() if task.last_update else None,
            "next_update": task.next_update.isoformat() if task.next_update else None,
            "last_status": task.last_status,
            "success_count": task.success_count,
            "error_count": task.error_count,
        }

    def get_all_task_statuses(self) -> Dict[str, Any]:
        """Get status of all tasks"""
        return {api_id: self.get_task_status(api_id) for api_id in self.tasks.keys()}

    def get_cached_data(self, api_id: str) -> Optional[Dict[str, Any]]:
        """Get cached data for an API"""
        return self.data_cache.get(api_id)

    def get_all_cached_data(self) -> Dict[str, Any]:
        """Get all cached data"""
        return self.data_cache

    async def force_update(self, api_id: str) -> bool:
        """Force an immediate update for an API"""
        task = self.tasks.get(api_id)

        if not task:
            logger.error(f"Task not found: {api_id}")
            return False

        logger.info(f"Forcing update for {task.name}")
        await self._execute_task(task)

        return task.last_status == "success"

    def export_schedules(self, filepath: str):
        """Export schedules to JSON"""
        schedules_data = {
            api_id: {
                "name": task.name,
                "category": task.category,
                "interval": task.interval,
                "update_type": task.update_type,
                "enabled": task.enabled,
                "last_update": task.last_update.isoformat() if task.last_update else None,
                "success_count": task.success_count,
                "error_count": task.error_count,
            }
            for api_id, task in self.tasks.items()
        }

        with open(filepath, "w") as f:
            json.dump(schedules_data, f, indent=2)

        logger.info(f"Exported schedules to {filepath}")

    def import_schedules(self, filepath: str):
        """Import schedules from JSON"""
        with open(filepath, "r") as f:
            schedules_data = json.load(f)

        for api_id, schedule_data in schedules_data.items():
            if api_id in self.tasks:
                task = self.tasks[api_id]
                task.interval = schedule_data.get("interval", task.interval)
                task.enabled = schedule_data.get("enabled", task.enabled)

        logger.info(f"Imported schedules from {filepath}")
