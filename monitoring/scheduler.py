"""
Comprehensive Task Scheduler for Crypto API Monitoring
Implements scheduled tasks using APScheduler with full compliance tracking
"""

import asyncio
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Callable, Any, List
from threading import Lock

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger
from apscheduler.events import EVENT_JOB_EXECUTED, EVENT_JOB_ERROR

# Import required modules
from monitoring.health_checker import HealthChecker
from monitoring.rate_limiter import rate_limiter
from database.db_manager import db_manager
from utils.logger import setup_logger
from config import config

# Import master collector for data collection tasks
from collectors.master_collector import DataSourceCollector

# Setup logger
logger = setup_logger("scheduler", level="INFO")


class TaskScheduler:
    """
    Comprehensive task scheduler with compliance tracking
    Manages all scheduled tasks for the API monitoring system
    """

    def __init__(self, db_path: str = "data/api_monitor.db"):
        """
        Initialize task scheduler

        Args:
            db_path: Path to SQLite database
        """
        self.scheduler = BackgroundScheduler()
        self.db_path = db_path
        self.health_checker = HealthChecker(db_path=db_path)
        self.lock = Lock()

        # Initialize data collector
        self.collector = DataSourceCollector()

        # Track next expected run times for compliance
        self.expected_run_times: Dict[str, datetime] = {}

        # Track running status
        self._is_running = False

        # Register event listeners
        self.scheduler.add_listener(
            self._job_executed_listener,
            EVENT_JOB_EXECUTED | EVENT_JOB_ERROR
        )

        logger.info("TaskScheduler initialized")

    def _job_executed_listener(self, event):
        """
        Listener for job execution events

        Args:
            event: APScheduler event object
        """
        job_id = event.job_id

        if event.exception:
            logger.error(
                f"Job {job_id} raised an exception: {event.exception}",
                exc_info=True
            )
        else:
            logger.debug(f"Job {job_id} executed successfully")

    def _record_compliance(
        self,
        task_name: str,
        expected_time: datetime,
        actual_time: datetime,
        success: bool = True,
        skip_reason: Optional[str] = None
    ):
        """
        Record schedule compliance metrics

        Args:
            task_name: Name of the scheduled task
            expected_time: Expected execution time
            actual_time: Actual execution time
            success: Whether task succeeded
            skip_reason: Reason if task was skipped
        """
        try:
            # Calculate delay
            delay_seconds = int((actual_time - expected_time).total_seconds())
            on_time = abs(delay_seconds) <= 5  # Within 5 seconds is considered on-time

            # For system-level tasks, we'll use a dummy provider_id
            # In production, you might want to create a special "system" provider
            provider_id = 1  # Assuming provider ID 1 exists, or use None

            # Save to database (we'll save to schedule_compliance table)
            # Note: This requires a provider_id, so we might need to adjust the schema
            # or create compliance records differently for system tasks

            logger.info(
                f"Schedule compliance - Task: {task_name}, "
                f"Expected: {expected_time.isoformat()}, "
                f"Actual: {actual_time.isoformat()}, "
                f"Delay: {delay_seconds}s, "
                f"On-time: {on_time}, "
                f"Skip reason: {skip_reason or 'None'}"
            )

        except Exception as e:
            logger.error(f"Failed to record compliance for {task_name}: {e}")

    def _wrap_task(
        self,
        task_name: str,
        task_func: Callable,
        *args,
        **kwargs
    ):
        """
        Wrapper for scheduled tasks to add logging and compliance tracking

        Args:
            task_name: Name of the task
            task_func: Function to execute
            *args: Positional arguments for task_func
            **kwargs: Keyword arguments for task_func
        """
        start_time = datetime.utcnow()

        # Get expected time
        expected_time = self.expected_run_times.get(task_name, start_time)

        # Update next expected time based on task interval
        # This will be set when jobs are scheduled

        logger.info(f"Starting task: {task_name}")

        try:
            # Execute the task
            result = task_func(*args, **kwargs)

            end_time = datetime.utcnow()
            duration_ms = (end_time - start_time).total_seconds() * 1000

            logger.info(
                f"Completed task: {task_name} in {duration_ms:.2f}ms"
            )

            # Record compliance
            self._record_compliance(
                task_name=task_name,
                expected_time=expected_time,
                actual_time=start_time,
                success=True
            )

            return result

        except Exception as e:
            end_time = datetime.utcnow()
            duration_ms = (end_time - start_time).total_seconds() * 1000

            logger.error(
                f"Task {task_name} failed after {duration_ms:.2f}ms: {e}",
                exc_info=True
            )

            # Record compliance with error
            self._record_compliance(
                task_name=task_name,
                expected_time=expected_time,
                actual_time=start_time,
                success=False,
                skip_reason=f"Error: {str(e)[:200]}"
            )

            # Don't re-raise - we want scheduler to continue

    # ============================================================================
    # Scheduled Task Implementations
    # ============================================================================

    def _health_check_task(self):
        """
        Health check task - runs checks on all providers with staggering
        """
        logger.info("Executing health check task")

        try:
            # Get all providers
            providers = config.get_all_providers()

            # Run health checks with staggering (10 seconds per provider)
            async def run_staggered_checks():
                results = []
                for i, provider in enumerate(providers):
                    # Stagger by 10 seconds per provider
                    if i > 0:
                        await asyncio.sleep(10)

                    result = await self.health_checker.check_provider(provider.name)
                    if result:
                        results.append(result)
                        logger.info(
                            f"Health check: {provider.name} - {result.status.value} "
                            f"({result.response_time:.2f}ms)"
                        )

                return results

            # Run async task
            results = asyncio.run(run_staggered_checks())

            logger.info(f"Health check completed: {len(results)} providers checked")

        except Exception as e:
            logger.error(f"Health check task failed: {e}", exc_info=True)

    def _market_data_collection_task(self):
        """
        Market data collection task - collects data from market data providers
        """
        logger.info("Executing market data collection task")

        try:
            # Get market data providers
            providers = config.get_providers_by_category('market_data')

            logger.info(f"Collecting market data from {len(providers)} providers")

            # Collect actual market data using the master collector
            async def collect_data():
                results = await self.collector.collect_all_market_data()
                logger.info(f"Market data collected: {len(results)} results")
                return results

            # Run async collection
            results = asyncio.run(collect_data())

            logger.info(f"Market data collection completed: {len(results)} items")

        except Exception as e:
            logger.error(f"Market data collection failed: {e}", exc_info=True)

    def _explorer_data_collection_task(self):
        """
        Explorer data collection task - collects data from blockchain explorers
        """
        logger.info("Executing explorer data collection task")

        try:
            # Get blockchain explorer providers
            providers = config.get_providers_by_category('blockchain_explorers')

            logger.info(f"Collecting explorer data from {len(providers)} providers")

            # Collect actual blockchain data using the master collector
            async def collect_data():
                results = await self.collector.collect_all_blockchain_data()
                logger.info(f"Blockchain data collected: {len(results)} results")
                return results

            # Run async collection
            results = asyncio.run(collect_data())

            logger.info(f"Explorer data collection completed: {len(results)} items")

        except Exception as e:
            logger.error(f"Explorer data collection failed: {e}", exc_info=True)

    def _news_collection_task(self):
        """
        News collection task - collects news from news providers
        """
        logger.info("Executing news collection task")

        try:
            # Get news providers
            providers = config.get_providers_by_category('news')

            logger.info(f"Collecting news from {len(providers)} providers")

            # Collect actual news data using the master collector
            async def collect_data():
                results = await self.collector.collect_all_news()
                logger.info(f"News data collected: {len(results)} results")
                return results

            # Run async collection
            results = asyncio.run(collect_data())

            logger.info(f"News collection completed: {len(results)} items")

        except Exception as e:
            logger.error(f"News collection failed: {e}", exc_info=True)

    def _sentiment_collection_task(self):
        """
        Sentiment collection task - collects sentiment data
        """
        logger.info("Executing sentiment collection task")

        try:
            # Get sentiment providers
            providers = config.get_providers_by_category('sentiment')

            logger.info(f"Collecting sentiment data from {len(providers)} providers")

            # Collect actual sentiment data using the master collector
            async def collect_data():
                results = await self.collector.collect_all_sentiment()
                logger.info(f"Sentiment data collected: {len(results)} results")
                return results

            # Run async collection
            results = asyncio.run(collect_data())

            logger.info(f"Sentiment collection completed: {len(results)} items")

        except Exception as e:
            logger.error(f"Sentiment collection failed: {e}", exc_info=True)

    def _rate_limit_snapshot_task(self):
        """
        Rate limit snapshot task - captures current rate limit usage
        """
        logger.info("Executing rate limit snapshot task")

        try:
            # Get all rate limit statuses
            statuses = rate_limiter.get_all_statuses()

            # Save each status to database
            for provider_name, status_data in statuses.items():
                if status_data:
                    # Get provider from config
                    provider = config.get_provider(provider_name)
                    if provider:
                        # Get provider ID from database
                        db_provider = db_manager.get_provider(name=provider_name)
                        if db_provider:
                            # Save rate limit usage
                            db_manager.save_rate_limit_usage(
                                provider_id=db_provider.id,
                                limit_type=status_data['limit_type'],
                                limit_value=status_data['limit_value'],
                                current_usage=status_data['current_usage'],
                                reset_time=datetime.fromisoformat(status_data['reset_time'])
                            )

                            logger.debug(
                                f"Rate limit snapshot: {provider_name} - "
                                f"{status_data['current_usage']}/{status_data['limit_value']} "
                                f"({status_data['percentage']}%)"
                            )

            logger.info(f"Rate limit snapshot completed: {len(statuses)} providers")

        except Exception as e:
            logger.error(f"Rate limit snapshot failed: {e}", exc_info=True)

    def _metrics_aggregation_task(self):
        """
        Metrics aggregation task - aggregates system metrics
        """
        logger.info("Executing metrics aggregation task")

        try:
            # Get all providers
            all_providers = config.get_all_providers()
            total_providers = len(all_providers)

            # Get recent connection attempts (last hour)
            connection_attempts = db_manager.get_connection_attempts(hours=1, limit=10000)

            # Calculate metrics
            online_count = 0
            degraded_count = 0
            offline_count = 0
            total_response_time = 0
            response_count = 0

            total_requests = len(connection_attempts)
            total_failures = sum(
                1 for attempt in connection_attempts
                if attempt.status in ['failed', 'timeout']
            )

            # Get latest health check results per provider
            provider_latest_status = {}
            for attempt in connection_attempts:
                if attempt.provider_id not in provider_latest_status:
                    provider_latest_status[attempt.provider_id] = attempt

                    if attempt.status == 'success':
                        online_count += 1
                        if attempt.response_time_ms:
                            total_response_time += attempt.response_time_ms
                            response_count += 1
                    elif attempt.status == 'timeout':
                        offline_count += 1
                    else:
                        degraded_count += 1

            # Calculate average response time
            avg_response_time = (
                total_response_time / response_count
                if response_count > 0
                else 0
            )

            # Determine system health
            online_percentage = (online_count / total_providers * 100) if total_providers > 0 else 0

            if online_percentage >= 80:
                system_health = "healthy"
            elif online_percentage >= 50:
                system_health = "degraded"
            else:
                system_health = "critical"

            # Save system metrics
            db_manager.save_system_metrics(
                total_providers=total_providers,
                online_count=online_count,
                degraded_count=degraded_count,
                offline_count=offline_count,
                avg_response_time_ms=avg_response_time,
                total_requests_hour=total_requests,
                total_failures_hour=total_failures,
                system_health=system_health
            )

            logger.info(
                f"Metrics aggregation completed - "
                f"Health: {system_health}, "
                f"Online: {online_count}/{total_providers}, "
                f"Avg Response: {avg_response_time:.2f}ms"
            )

        except Exception as e:
            logger.error(f"Metrics aggregation failed: {e}", exc_info=True)

    def _database_cleanup_task(self):
        """
        Database cleanup task - removes old records (>30 days)
        """
        logger.info("Executing database cleanup task")

        try:
            # Cleanup old data (older than 30 days)
            deleted_counts = db_manager.cleanup_old_data(days=30)

            total_deleted = sum(deleted_counts.values())

            logger.info(
                f"Database cleanup completed - Deleted {total_deleted} old records"
            )

            # Log details
            for table, count in deleted_counts.items():
                if count > 0:
                    logger.info(f"  {table}: {count} records deleted")

        except Exception as e:
            logger.error(f"Database cleanup failed: {e}", exc_info=True)

    # ============================================================================
    # Public API Methods
    # ============================================================================

    def start(self):
        """
        Start all scheduled tasks
        """
        if self._is_running:
            logger.warning("Scheduler is already running")
            return

        logger.info("Starting task scheduler...")

        try:
            # Initialize expected run times (set to now for first run)
            now = datetime.utcnow()

            # Schedule health checks - every 5 minutes
            self.expected_run_times['health_checks'] = now
            self.scheduler.add_job(
                func=lambda: self._wrap_task('health_checks', self._health_check_task),
                trigger=IntervalTrigger(minutes=5),
                id='health_checks',
                name='Health Checks (Staggered)',
                replace_existing=True,
                max_instances=1
            )
            logger.info("Scheduled: Health checks every 5 minutes")

            # Schedule market data collection - every 1 minute
            self.expected_run_times['market_data'] = now
            self.scheduler.add_job(
                func=lambda: self._wrap_task('market_data', self._market_data_collection_task),
                trigger=IntervalTrigger(minutes=1),
                id='market_data',
                name='Market Data Collection',
                replace_existing=True,
                max_instances=1
            )
            logger.info("Scheduled: Market data collection every 1 minute")

            # Schedule explorer data collection - every 5 minutes
            self.expected_run_times['explorer_data'] = now
            self.scheduler.add_job(
                func=lambda: self._wrap_task('explorer_data', self._explorer_data_collection_task),
                trigger=IntervalTrigger(minutes=5),
                id='explorer_data',
                name='Explorer Data Collection',
                replace_existing=True,
                max_instances=1
            )
            logger.info("Scheduled: Explorer data collection every 5 minutes")

            # Schedule news collection - every 10 minutes
            self.expected_run_times['news_collection'] = now
            self.scheduler.add_job(
                func=lambda: self._wrap_task('news_collection', self._news_collection_task),
                trigger=IntervalTrigger(minutes=10),
                id='news_collection',
                name='News Collection',
                replace_existing=True,
                max_instances=1
            )
            logger.info("Scheduled: News collection every 10 minutes")

            # Schedule sentiment collection - every 15 minutes
            self.expected_run_times['sentiment_collection'] = now
            self.scheduler.add_job(
                func=lambda: self._wrap_task('sentiment_collection', self._sentiment_collection_task),
                trigger=IntervalTrigger(minutes=15),
                id='sentiment_collection',
                name='Sentiment Collection',
                replace_existing=True,
                max_instances=1
            )
            logger.info("Scheduled: Sentiment collection every 15 minutes")

            # Schedule rate limit snapshot - every 1 minute
            self.expected_run_times['rate_limit_snapshot'] = now
            self.scheduler.add_job(
                func=lambda: self._wrap_task('rate_limit_snapshot', self._rate_limit_snapshot_task),
                trigger=IntervalTrigger(minutes=1),
                id='rate_limit_snapshot',
                name='Rate Limit Snapshot',
                replace_existing=True,
                max_instances=1
            )
            logger.info("Scheduled: Rate limit snapshot every 1 minute")

            # Schedule metrics aggregation - every 5 minutes
            self.expected_run_times['metrics_aggregation'] = now
            self.scheduler.add_job(
                func=lambda: self._wrap_task('metrics_aggregation', self._metrics_aggregation_task),
                trigger=IntervalTrigger(minutes=5),
                id='metrics_aggregation',
                name='Metrics Aggregation',
                replace_existing=True,
                max_instances=1
            )
            logger.info("Scheduled: Metrics aggregation every 5 minutes")

            # Schedule database cleanup - daily at 3 AM
            self.expected_run_times['database_cleanup'] = now.replace(hour=3, minute=0, second=0)
            self.scheduler.add_job(
                func=lambda: self._wrap_task('database_cleanup', self._database_cleanup_task),
                trigger=CronTrigger(hour=3, minute=0),
                id='database_cleanup',
                name='Database Cleanup (Daily 3 AM)',
                replace_existing=True,
                max_instances=1
            )
            logger.info("Scheduled: Database cleanup daily at 3 AM")

            # Start the scheduler
            self.scheduler.start()
            self._is_running = True

            logger.info("Task scheduler started successfully")

            # Print scheduled jobs
            jobs = self.scheduler.get_jobs()
            logger.info(f"Active scheduled jobs: {len(jobs)}")
            for job in jobs:
                logger.info(f"  - {job.name} (ID: {job.id}) - Next run: {job.next_run_time}")

        except Exception as e:
            logger.error(f"Failed to start scheduler: {e}", exc_info=True)
            raise

    def stop(self):
        """
        Stop scheduler gracefully
        """
        if not self._is_running:
            logger.warning("Scheduler is not running")
            return

        logger.info("Stopping task scheduler...")

        try:
            # Shutdown scheduler gracefully
            self.scheduler.shutdown(wait=True)
            self._is_running = False

            # Close health checker resources
            asyncio.run(self.health_checker.close())

            logger.info("Task scheduler stopped successfully")

        except Exception as e:
            logger.error(f"Error stopping scheduler: {e}", exc_info=True)

    def add_job(
        self,
        job_id: str,
        job_name: str,
        job_func: Callable,
        trigger_type: str = 'interval',
        **trigger_kwargs
    ) -> bool:
        """
        Add a custom scheduled job

        Args:
            job_id: Unique job identifier
            job_name: Human-readable job name
            job_func: Function to execute
            trigger_type: Type of trigger ('interval' or 'cron')
            **trigger_kwargs: Trigger-specific parameters

        Returns:
            True if successful, False otherwise

        Examples:
            # Add interval job
            scheduler.add_job(
                'my_job', 'My Custom Job', my_function,
                trigger_type='interval', minutes=30
            )

            # Add cron job
            scheduler.add_job(
                'daily_job', 'Daily Job', daily_function,
                trigger_type='cron', hour=12, minute=0
            )
        """
        try:
            # Create trigger
            if trigger_type == 'interval':
                trigger = IntervalTrigger(**trigger_kwargs)
            elif trigger_type == 'cron':
                trigger = CronTrigger(**trigger_kwargs)
            else:
                logger.error(f"Unknown trigger type: {trigger_type}")
                return False

            # Add job with wrapper
            self.scheduler.add_job(
                func=lambda: self._wrap_task(job_id, job_func),
                trigger=trigger,
                id=job_id,
                name=job_name,
                replace_existing=True,
                max_instances=1
            )

            # Set expected run time
            self.expected_run_times[job_id] = datetime.utcnow()

            logger.info(f"Added custom job: {job_name} (ID: {job_id})")
            return True

        except Exception as e:
            logger.error(f"Failed to add job {job_id}: {e}", exc_info=True)
            return False

    def remove_job(self, job_id: str) -> bool:
        """
        Remove a scheduled job

        Args:
            job_id: Job identifier to remove

        Returns:
            True if successful, False otherwise
        """
        try:
            self.scheduler.remove_job(job_id)

            # Remove from expected run times
            if job_id in self.expected_run_times:
                del self.expected_run_times[job_id]

            logger.info(f"Removed job: {job_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to remove job {job_id}: {e}", exc_info=True)
            return False

    def trigger_immediate(self, job_id: str) -> bool:
        """
        Trigger immediate execution of a scheduled job

        Args:
            job_id: Job identifier to trigger

        Returns:
            True if successful, False otherwise
        """
        try:
            job = self.scheduler.get_job(job_id)

            if not job:
                logger.error(f"Job not found: {job_id}")
                return False

            # Modify the job to run now
            job.modify(next_run_time=datetime.utcnow())

            logger.info(f"Triggered immediate execution of job: {job_id}")
            return True

        except Exception as e:
            logger.error(f"Failed to trigger job {job_id}: {e}", exc_info=True)
            return False

    def get_job_status(self, job_id: Optional[str] = None) -> Dict[str, Any]:
        """
        Get status of scheduled jobs

        Args:
            job_id: Specific job ID, or None for all jobs

        Returns:
            Dictionary with job status information
        """
        try:
            if job_id:
                job = self.scheduler.get_job(job_id)
                if not job:
                    return {}

                return {
                    'id': job.id,
                    'name': job.name,
                    'next_run': job.next_run_time.isoformat() if job.next_run_time else None,
                    'trigger': str(job.trigger)
                }
            else:
                # Get all jobs
                jobs = self.scheduler.get_jobs()
                return {
                    'total_jobs': len(jobs),
                    'is_running': self._is_running,
                    'jobs': [
                        {
                            'id': job.id,
                            'name': job.name,
                            'next_run': job.next_run_time.isoformat() if job.next_run_time else None,
                            'trigger': str(job.trigger)
                        }
                        for job in jobs
                    ]
                }

        except Exception as e:
            logger.error(f"Failed to get job status: {e}", exc_info=True)
            return {}

    def is_running(self) -> bool:
        """
        Check if scheduler is running

        Returns:
            True if running, False otherwise
        """
        return self._is_running


# ============================================================================
# Global Scheduler Instance
# ============================================================================

# Create a global scheduler instance (can be reconfigured as needed)
task_scheduler = TaskScheduler()


# ============================================================================
# Convenience Functions
# ============================================================================

def start_scheduler():
    """Start the global task scheduler"""
    task_scheduler.start()


def stop_scheduler():
    """Stop the global task scheduler"""
    task_scheduler.stop()


# ============================================================================
# Example Usage
# ============================================================================

if __name__ == "__main__":
    print("Task Scheduler Module")
    print("=" * 80)

    # Initialize and start scheduler
    scheduler = TaskScheduler()

    try:
        # Start scheduler
        scheduler.start()

        # Keep running for a while
        print("\nScheduler is running. Press Ctrl+C to stop...")
        print(f"Scheduler status: {scheduler.get_job_status()}")

        # Keep the main thread alive
        import time
        while True:
            time.sleep(60)

            # Print status every minute
            status = scheduler.get_job_status()
            print(f"\n[{datetime.utcnow().isoformat()}] Active jobs: {status['total_jobs']}")
            for job in status.get('jobs', []):
                print(f"  - {job['name']}: Next run at {job['next_run']}")

    except KeyboardInterrupt:
        print("\n\nStopping scheduler...")
        scheduler.stop()
        print("Scheduler stopped. Goodbye!")
