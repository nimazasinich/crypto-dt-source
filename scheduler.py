"""
Background Scheduler for API Health Checks
Runs periodic health checks with APScheduler
"""

import asyncio
import logging
from datetime import datetime
from apscheduler.schedulers.background import BackgroundScheduler as APScheduler
from apscheduler.triggers.interval import IntervalTrigger
from typing import Optional

logger = logging.getLogger(__name__)


class BackgroundScheduler:
    """Background scheduler for periodic health checks"""

    def __init__(self, monitor, database, interval_minutes: int = 5):
        """
        Initialize the scheduler

        Args:
            monitor: APIMonitor instance
            database: Database instance
            interval_minutes: Interval between health checks
        """
        self.monitor = monitor
        self.database = database
        self.interval_minutes = interval_minutes
        self.scheduler = APScheduler()
        self.last_run_time: Optional[datetime] = None
        self._running = False

    def _run_health_check(self):
        """Run health check and save results"""
        try:
            logger.info("Running scheduled health check...")
            self.last_run_time = datetime.now()

            # Run async health check
            results = asyncio.run(self.monitor.check_all())

            # Save to database
            self.database.save_health_checks(results)

            # Check for incidents (offline Tier 1 providers)
            for result in results:
                if result.status.value == "offline":
                    # Check if provider is Tier 1
                    resources = self.monitor.config.get_all_resources()
                    resource = next((r for r in resources if r.get('name') == result.provider_name), None)

                    if resource and resource.get('tier', 3) == 1:
                        # Create incident for Tier 1 outage
                        self.database.create_incident(
                            provider_name=result.provider_name,
                            category=result.category,
                            incident_type="service_offline",
                            description=f"Tier 1 provider offline: {result.error_message}",
                            severity="high"
                        )

                        # Create alert
                        self.database.create_alert(
                            provider_name=result.provider_name,
                            alert_type="tier1_offline",
                            message=f"Critical: Tier 1 provider {result.provider_name} is offline"
                        )

            logger.info(f"Health check completed. Checked {len(results)} providers.")

            # Cleanup old data (older than 7 days)
            self.database.cleanup_old_data(days=7)

            # Aggregate response times
            self.database.aggregate_response_times(period_hours=1)

        except Exception as e:
            logger.error(f"Error in scheduled health check: {e}")

    def start(self):
        """Start the scheduler"""
        if not self._running:
            try:
                # Add job with interval trigger
                self.scheduler.add_job(
                    func=self._run_health_check,
                    trigger=IntervalTrigger(minutes=self.interval_minutes),
                    id='health_check_job',
                    name='API Health Check',
                    replace_existing=True
                )

                self.scheduler.start()
                self._running = True
                logger.info(f"Scheduler started. Running every {self.interval_minutes} minutes.")

                # Run initial check
                self._run_health_check()

            except Exception as e:
                logger.error(f"Error starting scheduler: {e}")

    def stop(self):
        """Stop the scheduler"""
        if self._running:
            self.scheduler.shutdown()
            self._running = False
            logger.info("Scheduler stopped.")

    def update_interval(self, interval_minutes: int):
        """Update the check interval"""
        self.interval_minutes = interval_minutes

        if self._running:
            # Reschedule the job
            self.scheduler.reschedule_job(
                job_id='health_check_job',
                trigger=IntervalTrigger(minutes=interval_minutes)
            )
            logger.info(f"Scheduler interval updated to {interval_minutes} minutes.")

    def is_running(self) -> bool:
        """Check if scheduler is running"""
        return self._running

    def trigger_immediate_check(self):
        """Trigger an immediate health check"""
        logger.info("Triggering immediate health check...")
        self._run_health_check()
