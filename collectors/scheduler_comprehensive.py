"""
Comprehensive Scheduler for All Data Sources
Schedules and runs data collection from all available sources with configurable intervals
"""

import asyncio
import json
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Optional, Any
from pathlib import Path
from utils.logger import setup_logger
from collectors.master_collector import DataSourceCollector

logger = setup_logger("comprehensive_scheduler")


class ComprehensiveScheduler:
    """
    Comprehensive scheduler that manages data collection from all sources
    """

    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize the comprehensive scheduler

        Args:
            config_file: Path to scheduler configuration file
        """
        self.collector = DataSourceCollector()
        self.config_file = config_file or "scheduler_config.json"
        self.config = self._load_config()
        self.last_run_times: Dict[str, datetime] = {}
        self.running = False
        logger.info("Comprehensive Scheduler initialized")

    def _load_config(self) -> Dict[str, Any]:
        """
        Load scheduler configuration

        Returns:
            Configuration dict
        """
        default_config = {
            "schedules": {
                "market_data": {"interval_seconds": 60, "enabled": True},  # Every 1 minute
                "blockchain": {"interval_seconds": 300, "enabled": True},  # Every 5 minutes
                "news": {"interval_seconds": 600, "enabled": True},  # Every 10 minutes
                "sentiment": {"interval_seconds": 1800, "enabled": True},  # Every 30 minutes
                "whale_tracking": {"interval_seconds": 300, "enabled": True},  # Every 5 minutes
                "full_collection": {"interval_seconds": 3600, "enabled": True},  # Every 1 hour
            },
            "max_retries": 3,
            "retry_delay_seconds": 5,
            "persist_results": True,
            "results_directory": "data/collections",
        }

        config_path = Path(self.config_file)
        if config_path.exists():
            try:
                with open(config_path, "r") as f:
                    loaded_config = json.load(f)
                    # Merge with defaults
                    default_config.update(loaded_config)
                    logger.info(f"Loaded scheduler config from {config_path}")
            except Exception as e:
                logger.error(f"Error loading config file: {e}, using defaults")

        return default_config

    def save_config(self):
        """Save current configuration to file"""
        try:
            config_path = Path(self.config_file)
            config_path.parent.mkdir(parents=True, exist_ok=True)

            with open(config_path, "w") as f:
                json.dump(self.config, f, indent=2)

            logger.info(f"Saved scheduler config to {config_path}")
        except Exception as e:
            logger.error(f"Error saving config: {e}")

    async def _save_results(self, category: str, results: Any):
        """
        Save collection results to file

        Args:
            category: Category name
            results: Results to save
        """
        if not self.config.get("persist_results", True):
            return

        try:
            results_dir = Path(self.config.get("results_directory", "data/collections"))
            results_dir.mkdir(parents=True, exist_ok=True)

            timestamp = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
            filename = results_dir / f"{category}_{timestamp}.json"

            with open(filename, "w") as f:
                json.dump(results, f, indent=2, default=str)

            logger.info(f"Saved {category} results to {filename}")
        except Exception as e:
            logger.error(f"Error saving results: {e}")

    def should_run(self, category: str) -> bool:
        """
        Check if a category should run based on its schedule

        Args:
            category: Category name

        Returns:
            True if should run, False otherwise
        """
        schedule = self.config.get("schedules", {}).get(category, {})

        if not schedule.get("enabled", True):
            return False

        interval = schedule.get("interval_seconds", 3600)
        last_run = self.last_run_times.get(category)

        if not last_run:
            return True

        elapsed = (datetime.now(timezone.utc) - last_run).total_seconds()
        return elapsed >= interval

    async def run_category_with_retry(self, category: str) -> Optional[Any]:
        """
        Run a category collection with retry logic

        Args:
            category: Category name

        Returns:
            Collection results or None if failed
        """
        max_retries = self.config.get("max_retries", 3)
        retry_delay = self.config.get("retry_delay_seconds", 5)

        for attempt in range(max_retries):
            try:
                logger.info(f"Running {category} collection (attempt {attempt + 1}/{max_retries})")

                if category == "full_collection":
                    results = await self.collector.collect_all_data()
                else:
                    results = await self.collector.collect_category(category)

                self.last_run_times[category] = datetime.now(timezone.utc)

                # Save results
                await self._save_results(category, results)

                return results

            except Exception as e:
                logger.error(f"Error in {category} collection (attempt {attempt + 1}): {e}")

                if attempt < max_retries - 1:
                    logger.info(f"Retrying in {retry_delay} seconds...")
                    await asyncio.sleep(retry_delay)
                else:
                    logger.error(f"Failed {category} collection after {max_retries} attempts")
                    return None

    async def run_cycle(self):
        """Run one scheduler cycle - check and run due categories"""
        logger.info("Running scheduler cycle...")

        categories = self.config.get("schedules", {}).keys()
        tasks = []

        for category in categories:
            if self.should_run(category):
                logger.info(f"Scheduling {category} collection")
                task = self.run_category_with_retry(category)
                tasks.append((category, task))

        if tasks:
            # Run all due collections in parallel
            results = await asyncio.gather(*[task for _, task in tasks], return_exceptions=True)

            for (category, _), result in zip(tasks, results):
                if isinstance(result, Exception):
                    logger.error(f"{category} collection failed: {str(result)}")
                else:
                    if result:
                        stats = result.get("statistics", {}) if isinstance(result, dict) else None
                        if stats:
                            logger.info(
                                f"{category} collection complete: "
                                f"{stats.get('successful_sources', 'N/A')}/{stats.get('total_sources', 'N/A')} successful"
                            )
        else:
            logger.info("No collections due in this cycle")

    async def run_forever(self, cycle_interval: int = 30):
        """
        Run the scheduler forever with specified cycle interval

        Args:
            cycle_interval: Seconds between scheduler cycles
        """
        self.running = True
        logger.info(f"Starting comprehensive scheduler (cycle interval: {cycle_interval}s)")

        try:
            while self.running:
                await self.run_cycle()

                # Wait for next cycle
                logger.info(f"Waiting {cycle_interval} seconds until next cycle...")
                await asyncio.sleep(cycle_interval)

        except KeyboardInterrupt:
            logger.info("Scheduler interrupted by user")
        except Exception as e:
            logger.error(f"Scheduler error: {e}")
        finally:
            self.running = False
            logger.info("Scheduler stopped")

    def stop(self):
        """Stop the scheduler"""
        logger.info("Stopping scheduler...")
        self.running = False

    async def run_once(self, category: Optional[str] = None):
        """
        Run a single collection immediately

        Args:
            category: Category to run, or None for full collection
        """
        if category:
            logger.info(f"Running single {category} collection...")
            results = await self.run_category_with_retry(category)
        else:
            logger.info("Running single full collection...")
            results = await self.run_category_with_retry("full_collection")

        return results

    def get_status(self) -> Dict[str, Any]:
        """
        Get scheduler status

        Returns:
            Dict with scheduler status information
        """
        now = datetime.now(timezone.utc)
        status = {"running": self.running, "current_time": now.isoformat(), "schedules": {}}

        for category, schedule in self.config.get("schedules", {}).items():
            last_run = self.last_run_times.get(category)
            interval = schedule.get("interval_seconds", 0)

            next_run = None
            if last_run:
                next_run = last_run + timedelta(seconds=interval)

            time_until_next = None
            if next_run:
                time_until_next = (next_run - now).total_seconds()

            status["schedules"][category] = {
                "enabled": schedule.get("enabled", True),
                "interval_seconds": interval,
                "last_run": last_run.isoformat() if last_run else None,
                "next_run": next_run.isoformat() if next_run else None,
                "seconds_until_next": round(time_until_next, 2) if time_until_next else None,
                "should_run_now": self.should_run(category),
            }

        return status

    def update_schedule(
        self, category: str, interval_seconds: Optional[int] = None, enabled: Optional[bool] = None
    ):
        """
        Update schedule for a category

        Args:
            category: Category name
            interval_seconds: New interval in seconds
            enabled: Enable/disable the schedule
        """
        if category not in self.config.get("schedules", {}):
            logger.error(f"Unknown category: {category}")
            return

        if interval_seconds is not None:
            self.config["schedules"][category]["interval_seconds"] = interval_seconds
            logger.info(f"Updated {category} interval to {interval_seconds}s")

        if enabled is not None:
            self.config["schedules"][category]["enabled"] = enabled
            logger.info(f"{'Enabled' if enabled else 'Disabled'} {category} schedule")

        self.save_config()


# Example usage
if __name__ == "__main__":

    async def main():
        scheduler = ComprehensiveScheduler()

        # Show status
        print("\n" + "=" * 80)
        print("COMPREHENSIVE SCHEDULER STATUS")
        print("=" * 80)

        status = scheduler.get_status()
        print(f"Running: {status['running']}")
        print(f"Current Time: {status['current_time']}")
        print("\nSchedules:")
        print("-" * 80)

        for category, sched in status["schedules"].items():
            enabled = "✓" if sched["enabled"] else "✗"
            interval = sched["interval_seconds"]
            next_run = sched.get("seconds_until_next", "N/A")

            print(f"{enabled} {category:20} | Interval: {interval:6}s | Next in: {next_run}")

        print("=" * 80)

        # Run once as example
        print("\nRunning market_data collection once as example...")
        results = await scheduler.run_once("market_data")

        if results:
            print(f"\nCollected {len(results)} market data sources")
            successful = sum(1 for r in results if r.get("success", False))
            print(f"Successful: {successful}/{len(results)}")

        print("\n" + "=" * 80)
        print("To run scheduler forever, use: scheduler.run_forever()")
        print("=" * 80)

    asyncio.run(main())
