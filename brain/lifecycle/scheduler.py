"""
Lifecycle Scheduler

Automated scheduling of lifecycle jobs using APScheduler.
Handles retention enforcement, cleanup, and GDPR processing.

All implementation is in Python 3.10+
"""

import sqlite3
from datetime import datetime
from typing import Optional, Callable
import logging

try:
    from apscheduler.schedulers.background import BackgroundScheduler
    from apscheduler.triggers.cron import CronTrigger
    from apscheduler.triggers.interval import IntervalTrigger
    APSCHEDULER_AVAILABLE = True
except ImportError:
    APSCHEDULER_AVAILABLE = False
    BackgroundScheduler = None
    CronTrigger = None
    IntervalTrigger = None

from brain.lifecycle.manager import LifecycleManager
from brain.lifecycle.gdpr import GDPRCompliance


logger = logging.getLogger(__name__)


class LifecycleScheduler:
    """
    Scheduler for automated lifecycle operations.
    
    Schedules:
    - Daily retention enforcement
    - Weekly cleanup of expired records
    - Daily GDPR erasure processing
    
    Example:
        scheduler = LifecycleScheduler(db_path='tracking.db')
        scheduler.start()
        
        # Later...
        scheduler.stop()
    """
    
    def __init__(
        self,
        db_path: str = None,
        db_connection: sqlite3.Connection = None
    ):
        """
        Initialize lifecycle scheduler.
        
        Args:
            db_path: Path to SQLite database
            db_connection: Existing database connection
        """
        self.db_path = db_path
        self.db_connection = db_connection
        
        self.manager = LifecycleManager(
            db_path=db_path,
            db_connection=db_connection
        )
        self.gdpr = GDPRCompliance(db_connection=db_connection)
        
        if APSCHEDULER_AVAILABLE:
            self.scheduler = BackgroundScheduler()
        else:
            self.scheduler = None
            logger.warning("APScheduler not available, scheduling disabled")
        
        self._jobs_added = False
    
    def start(self) -> bool:
        """
        Start the scheduler.
        
        Adds default jobs if not already added.
        
        Returns:
            True if scheduler started successfully
        """
        if self.scheduler is None:
            logger.warning("Cannot start scheduler: APScheduler not available")
            return False
        
        if not self._jobs_added:
            self._add_default_jobs()
            self._jobs_added = True
        
        self.scheduler.start()
        logger.info("Lifecycle scheduler started")
        return True
    
    def stop(self) -> None:
        """Stop the scheduler."""
        if self.scheduler:
            self.scheduler.shutdown()
            logger.info("Lifecycle scheduler stopped")
    
    def _add_default_jobs(self) -> None:
        """Add default scheduled jobs."""
        # Daily retention enforcement at 2 AM
        self.scheduler.add_job(
            self._run_retention_enforcement,
            CronTrigger(hour=2, minute=0),
            id='retention_enforcement',
            name='Daily Retention Enforcement',
            replace_existing=True
        )
        
        # Weekly cleanup on Sunday at 3 AM
        self.scheduler.add_job(
            self._run_cleanup,
            CronTrigger(day_of_week='sun', hour=3, minute=0),
            id='weekly_cleanup',
            name='Weekly Cleanup',
            replace_existing=True
        )
        
        # Daily GDPR erasure processing at 4 AM
        self.scheduler.add_job(
            self._process_gdpr_requests,
            CronTrigger(hour=4, minute=0),
            id='gdpr_processing',
            name='Daily GDPR Processing',
            replace_existing=True
        )
        
        logger.info("Default lifecycle jobs added")
    
    def _run_retention_enforcement(self) -> None:
        """Run retention policy enforcement."""
        try:
            logger.info("Running scheduled retention enforcement")
            result = self.manager.apply_retention_policies()
            logger.info(f"Retention enforcement complete: {result.to_dict()}")
        except Exception as e:
            logger.error(f"Retention enforcement failed: {e}")
    
    def _run_cleanup(self) -> None:
        """Run cleanup of expired records."""
        try:
            logger.info("Running scheduled cleanup")
            result = self.manager.run_cleanup()
            logger.info(f"Cleanup complete: {result.to_dict()}")
        except Exception as e:
            logger.error(f"Cleanup failed: {e}")
    
    def _process_gdpr_requests(self) -> None:
        """Process pending GDPR erasure requests."""
        try:
            logger.info("Processing GDPR erasure requests")
            
            # Find requests ready for execution
            requests = self.gdpr.list_erasure_requests()
            processed = 0
            
            for request in requests:
                if request.can_execute():
                    result = self.gdpr.execute_erasure(request.id)
                    if result.success:
                        processed += 1
            
            logger.info(f"GDPR processing complete: {processed} requests executed")
        except Exception as e:
            logger.error(f"GDPR processing failed: {e}")
    
    def add_job(
        self,
        func: Callable,
        trigger,
        job_id: str,
        **kwargs
    ) -> Optional[str]:
        """
        Add a custom job to the scheduler.
        
        Args:
            func: Function to execute
            trigger: APScheduler trigger
            job_id: Unique job identifier
            **kwargs: Additional job arguments
            
        Returns:
            Job ID or None if scheduler unavailable
        """
        if self.scheduler is None:
            return None
        
        self.scheduler.add_job(
            func,
            trigger,
            id=job_id,
            replace_existing=True,
            **kwargs
        )
        
        return job_id
    
    def remove_job(self, job_id: str) -> bool:
        """
        Remove a job from the scheduler.
        
        Args:
            job_id: Job identifier
            
        Returns:
            True if job was removed
        """
        if self.scheduler is None:
            return False
        
        self.scheduler.remove_job(job_id)
        return True
    
    def get_jobs(self) -> list:
        """
        Get all scheduled jobs.
        
        Returns:
            List of job information dictionaries
        """
        if self.scheduler is None:
            return []
        
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                'id': job.id,
                'name': job.name,
                'next_run': str(job.next_run_time) if job.next_run_time else None,
                'trigger': str(job.trigger),
            })
        
        return jobs
    
    def run_job_now(self, job_id: str) -> bool:
        """
        Trigger a job to run immediately.
        
        Args:
            job_id: Job identifier
            
        Returns:
            True if job was triggered
        """
        if self.scheduler is None:
            return False
        
        job = self.scheduler.get_job(job_id)
        if job:
            job.func()
            return True
        return False