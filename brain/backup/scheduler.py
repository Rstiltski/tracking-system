"""
Backup Scheduler

Automated backup scheduling using APScheduler.
Supports hourly, daily, weekly, and monthly backup frequencies.

All implementation is in Python 3.10+

The scheduler integrates with the backup manager to provide
fully automated backup creation with configurable schedules.
"""

import sqlite3
from pathlib import Path
from typing import Optional, List, Callable
from datetime import datetime, timedelta
import logging
import threading

from brain.backup.models import BackupSchedule, BackupType, BackupFrequency
from brain.backup.manager import BackupManager


logger = logging.getLogger(__name__)


class BackupScheduler:
    """
    Automated backup scheduler.
    
    Uses APScheduler for reliable job scheduling with support for:
    - Hourly backups
    - Daily backups at specified time
    - Weekly backups on specified day
    - Monthly backups on specified day
    
    Example:
        >>> scheduler = BackupScheduler(backup_manager)
        >>> 
        >>> # Create a daily backup schedule
        >>> schedule = BackupSchedule(
        ...     user_id='user-123',
        ...     frequency=BackupFrequency.DAILY,
        ...     time_of_day='02:00',
        ...     backup_type=BackupType.FULL
        ... )
        >>> scheduler.add_schedule(schedule)
        >>> 
        >>> # Start the scheduler
        >>> scheduler.start()
    
    Attributes:
        backup_manager: BackupManager instance for creating backups
        schedules: Dictionary of schedule ID to BackupSchedule
        running: Whether the scheduler is active
    """
    
    def __init__(
        self,
        backup_manager: BackupManager,
        db_path: str = "tracking.db"
    ):
        """
        Initialize backup scheduler.
        
        Args:
            backup_manager: BackupManager for creating backups
            db_path: Path to database for schedule storage
        """
        self.backup_manager = backup_manager
        self.db_path = Path(db_path)
        self.schedules: dict = {}
        self.running = False
        self._scheduler = None
        self._lock = threading.Lock()
        
        # Load existing schedules
        self._load_schedules()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        return sqlite3.connect(str(self.db_path))
    
    def _load_schedules(self) -> None:
        """Load schedules from database."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM backup_schedules WHERE enabled = 1")
        rows = cursor.fetchall()
        
        columns = [desc[0] for desc in cursor.description]
        
        for row in rows:
            data = dict(zip(columns, row))
            schedule = BackupSchedule.from_dict(data)
            self.schedules[schedule.id] = schedule
        
        conn.close()
        logger.info(f"Loaded {len(self.schedules)} schedules")
    
    def start(self) -> None:
        """
        Start the backup scheduler.
        
        Initializes APScheduler and schedules all enabled jobs.
        """
        if self.running:
            logger.warning("Scheduler already running")
            return
        
        try:
            from apscheduler.schedulers.background import BackgroundScheduler
            from apscheduler.triggers.cron import CronTrigger
            
            self._scheduler = BackgroundScheduler()
            
            # Add jobs for each schedule
            for schedule_id, schedule in self.schedules.items():
                self._add_job_to_scheduler(schedule)
            
            self._scheduler.start()
            self.running = True
            logger.info("Backup scheduler started")
            
        except ImportError:
            logger.warning(
                "APScheduler not installed. Using simple timer-based scheduling."
            )
            self._start_simple_scheduler()
    
    def stop(self) -> None:
        """Stop the backup scheduler."""
        if not self.running:
            return
        
        if self._scheduler:
            self._scheduler.shutdown()
            self._scheduler = None
        
        self.running = False
        logger.info("Backup scheduler stopped")
    
    def add_schedule(self, schedule: BackupSchedule) -> None:
        """
        Add a new backup schedule.
        
        Args:
            schedule: BackupSchedule to add
        """
        with self._lock:
            # Save to database
            self._save_schedule(schedule)
            
            # Add to memory
            self.schedules[schedule.id] = schedule
            
            # Add to scheduler if running
            if self.running and self._scheduler:
                self._add_job_to_scheduler(schedule)
            
            logger.info(f"Added schedule: {schedule.id}")
    
    def remove_schedule(self, schedule_id: str) -> bool:
        """
        Remove a backup schedule.
        
        Args:
            schedule_id: ID of schedule to remove
            
        Returns:
            True if schedule was removed
        """
        with self._lock:
            if schedule_id not in self.schedules:
                return False
            
            # Remove from scheduler
            if self._scheduler:
                try:
                    self._scheduler.remove_job(schedule_id)
                except Exception:
                    pass
            
            # Remove from database
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "DELETE FROM backup_schedules WHERE id = ?",
                (schedule_id,)
            )
            conn.commit()
            conn.close()
            
            # Remove from memory
            del self.schedules[schedule_id]
            
            logger.info(f"Removed schedule: {schedule_id}")
            return True
    
    def update_schedule(self, schedule: BackupSchedule) -> None:
        """
        Update an existing schedule.
        
        Args:
            schedule: Updated BackupSchedule
        """
        schedule.updated_at = datetime.now()
        
        with self._lock:
            # Remove old job if scheduler is running
            if self._scheduler and schedule.id in self.schedules:
                try:
                    self._scheduler.remove_job(schedule.id)
                except Exception:
                    pass
            
            # Save to database
            self._save_schedule(schedule)
            
            # Update memory
            self.schedules[schedule.id] = schedule
            
            # Add new job if enabled
            if schedule.enabled and self._scheduler:
                self._add_job_to_scheduler(schedule)
            
            logger.info(f"Updated schedule: {schedule.id}")
    
    def get_schedule(self, schedule_id: str) -> Optional[BackupSchedule]:
        """
        Get a schedule by ID.
        
        Args:
            schedule_id: Schedule ID
            
        Returns:
            BackupSchedule or None
        """
        return self.schedules.get(schedule_id)
    
    def list_schedules(self, user_id: str = None) -> List[BackupSchedule]:
        """
        List all schedules.
        
        Args:
            user_id: Optional user ID filter
            
        Returns:
            List of BackupSchedule
        """
        if user_id:
            return [s for s in self.schedules.values() if s.user_id == user_id]
        return list(self.schedules.values())
    
    def _add_job_to_scheduler(self, schedule: BackupSchedule) -> None:
        """Add a job to APScheduler based on schedule configuration."""
        if not self._scheduler:
            return
        
        from apscheduler.triggers.cron import CronTrigger
        
        hour, minute = map(int, schedule.time_of_day.split(':'))
        
        if schedule.frequency == BackupFrequency.HOURLY:
            trigger = CronTrigger(minute=minute)
            
        elif schedule.frequency == BackupFrequency.DAILY:
            trigger = CronTrigger(hour=hour, minute=minute)
            
        elif schedule.frequency == BackupFrequency.WEEKLY:
            # day_of_week: 0=Monday, 6=Sunday
            trigger = CronTrigger(
                day_of_week=schedule.day_of_week,
                hour=hour,
                minute=minute
            )
            
        elif schedule.frequency == BackupFrequency.MONTHLY:
            trigger = CronTrigger(
                day=schedule.day_of_month,
                hour=hour,
                minute=minute
            )
        
        else:
            logger.error(f"Unknown frequency: {schedule.frequency}")
            return
        
        self._scheduler.add_job(
            func=self._run_backup,
            trigger=trigger,
            id=schedule.id,
            args=[schedule],
            replace_existing=True
        )
        
        logger.debug(f"Added job for schedule {schedule.id}")
    
    def _run_backup(self, schedule: BackupSchedule) -> None:
        """Execute a scheduled backup."""
        logger.info(f"Running scheduled backup: {schedule.id}")
        
        try:
            # Create backup
            job = self.backup_manager.create_backup(
                user_id=schedule.user_id,
                backup_type=schedule.backup_type
            )
            
            # Update schedule
            schedule.last_run = datetime.now()
            self._update_schedule_run(schedule)
            
            if job.status.value == 'completed':
                logger.info(f"Scheduled backup completed: {job.id}")
            else:
                logger.error(f"Scheduled backup failed: {job.error_message}")
            
        except Exception as e:
            logger.error(f"Scheduled backup error: {e}")
    
    def _save_schedule(self, schedule: BackupSchedule) -> None:
        """Save schedule to database."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        data = schedule.to_dict()
        
        cursor.execute('''
            INSERT OR REPLACE INTO backup_schedules (
                id, user_id, enabled, frequency, time_of_day,
                day_of_week, day_of_month, backup_type,
                retention_daily, retention_weekly, retention_monthly,
                last_run, next_run, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['id'],
            data['user_id'],
            data['enabled'],
            data['frequency'],
            data['time_of_day'],
            data['day_of_week'],
            data['day_of_month'],
            data['backup_type'],
            data['retention_daily'],
            data['retention_weekly'],
            data['retention_monthly'],
            data['last_run'],
            data['next_run'],
            data['created_at'],
            data['updated_at'],
        ))
        
        conn.commit()
        conn.close()
    
    def _update_schedule_run(self, schedule: BackupSchedule) -> None:
        """Update schedule after a run."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE backup_schedules 
            SET last_run = ?, updated_at = ?
            WHERE id = ?
        ''', (schedule.last_run.isoformat(), datetime.now().isoformat(), schedule.id))
        
        conn.commit()
        conn.close()
    
    def _start_simple_scheduler(self) -> None:
        """Start a simple timer-based scheduler (fallback without APScheduler)."""
        import time
        
        self.running = True
        
        def check_loop():
            while self.running:
                self._check_schedules()
                time.sleep(60)  # Check every minute
        
        thread = threading.Thread(target=check_loop, daemon=True)
        thread.start()
        
        logger.info("Started simple timer-based scheduler")
    
    def _check_schedules(self) -> None:
        """Check and run schedules (for simple scheduler)."""
        now = datetime.now()
        
        for schedule in self.schedules.values():
            if not schedule.enabled:
                continue
            
            should_run = False
            
            if schedule.frequency == BackupFrequency.HOURLY:
                # Run at the specified minute of each hour
                if now.minute == int(schedule.time_of_day.split(':')[1]):
                    should_run = self._should_run(schedule, timedelta(hours=1))
                    
            elif schedule.frequency == BackupFrequency.DAILY:
                hour, minute = map(int, schedule.time_of_day.split(':'))
                if now.hour == hour and now.minute == minute:
                    should_run = self._should_run(schedule, timedelta(days=1))
                    
            elif schedule.frequency == BackupFrequency.WEEKLY:
                hour, minute = map(int, schedule.time_of_day.split(':'))
                if (now.weekday() == schedule.day_of_week and 
                    now.hour == hour and now.minute == minute):
                    should_run = self._should_run(schedule, timedelta(weeks=1))
                    
            elif schedule.frequency == BackupFrequency.MONTHLY:
                hour, minute = map(int, schedule.time_of_day.split(':'))
                if (now.day == schedule.day_of_month and 
                    now.hour == hour and now.minute == minute):
                    should_run = self._should_run(schedule, timedelta(days=30))
            
            if should_run:
                self._run_backup(schedule)
    
    def _should_run(self, schedule: BackupSchedule, min_interval: timedelta) -> bool:
        """Check if enough time has passed since last run."""
        if schedule.last_run is None:
            return True
        
        elapsed = datetime.now() - schedule.last_run
        return elapsed >= min_interval


class ScheduleBuilder:
    """
    Builder for creating backup schedules.
    
    Provides a fluent interface for schedule creation.
    
    Example:
        >>> schedule = (ScheduleBuilder()
        ...     .for_user('user-123')
        ...     .daily()
        ...     .at_time('02:00')
        ...     .full_backup()
        ...     .retention(daily=7, weekly=4, monthly=12)
        ...     .build())
    """
    
    def __init__(self):
        """Initialize builder with defaults."""
        self._user_id = "default"
        self._frequency = BackupFrequency.DAILY
        self._time_of_day = "02:00"
        self._day_of_week = 6  # Sunday
        self._day_of_month = 1
        self._backup_type = BackupType.FULL
        self._retention_daily = 7
        self._retention_weekly = 4
        self._retention_monthly = 12
        self._enabled = True
    
    def for_user(self, user_id: str) -> 'ScheduleBuilder':
        """Set user ID."""
        self._user_id = user_id
        return self
    
    def hourly(self) -> 'ScheduleBuilder':
        """Set hourly frequency."""
        self._frequency = BackupFrequency.HOURLY
        return self
    
    def daily(self) -> 'ScheduleBuilder':
        """Set daily frequency."""
        self._frequency = BackupFrequency.DAILY
        return self
    
    def weekly(self, day_of_week: int = 6) -> 'ScheduleBuilder':
        """Set weekly frequency."""
        self._frequency = BackupFrequency.WEEKLY
        self._day_of_week = day_of_week
        return self
    
    def monthly(self, day_of_month: int = 1) -> 'ScheduleBuilder':
        """Set monthly frequency."""
        self._frequency = BackupFrequency.MONTHLY
        self._day_of_month = day_of_month
        return self
    
    def at_time(self, time: str) -> 'ScheduleBuilder':
        """Set time of day (HH:MM format)."""
        self._time_of_day = time
        return self
    
    def full_backup(self) -> 'ScheduleBuilder':
        """Set backup type to FULL."""
        self._backup_type = BackupType.FULL
        return self
    
    def incremental_backup(self) -> 'ScheduleBuilder':
        """Set backup type to INCREMENTAL."""
        self._backup_type = BackupType.INCREMENTAL
        return self
    
    def retention(
        self,
        daily: int = 7,
        weekly: int = 4,
        monthly: int = 12
    ) -> 'ScheduleBuilder':
        """Set retention policy."""
        self._retention_daily = daily
        self._retention_weekly = weekly
        self._retention_monthly = monthly
        return self
    
    def enabled(self, enabled: bool = True) -> 'ScheduleBuilder':
        """Set enabled status."""
        self._enabled = enabled
        return self
    
    def disabled(self) -> 'ScheduleBuilder':
        """Disable the schedule."""
        return self.enabled(False)
    
    def build(self) -> BackupSchedule:
        """Build the schedule."""
        return BackupSchedule(
            user_id=self._user_id,
            enabled=self._enabled,
            frequency=self._frequency,
            time_of_day=self._time_of_day,
            day_of_week=self._day_of_week,
            day_of_month=self._day_of_month,
            backup_type=self._backup_type,
            retention_daily=self._retention_daily,
            retention_weekly=self._retention_weekly,
            retention_monthly=self._retention_monthly,
        )