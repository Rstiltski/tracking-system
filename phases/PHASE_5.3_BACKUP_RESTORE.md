# Phase 5.3: Backup & Restore System - Implementation Plan

**Created:** February 19, 2026  
**Status:** 📋 Ready for Implementation  
**Duration:** 5-7 days  
**Dependencies:** Phase 5.2 (Data Import) ✅ Complete  
**Research:** ✅ Complete - See [BACKUP_RESTORE_RESEARCH.md](../docs/research/BACKUP_RESTORE_RESEARCH.md)

---

## 🎯 Executive Summary

Phase 5.3 implements a **Python-based backup and restore system** with:

- **Automated scheduled backups** using APScheduler BackgroundScheduler
- **SHA-256 checksum verification** for data integrity
- **GFS (Grandfather-Father-Son) retention policies** for balanced backup lifecycle
- **Hard-link deduplication** for storage efficiency
- **One-click restore** with confirmation workflow

All implementation follows **PROJECT_RULES.md** - Python 3.10+ with dataclasses, Streamlit UI.

---

## 📐 Architecture Overview

### System Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        BACKUP SYSTEM ARCHITECTURE                        │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  APScheduler    │────▶│  BackupManager   │────▶│  Storage        │
│  (Background)   │     │  (Orchestrator)  │     │  (Dedup Engine) │
│                 │     │                  │     │  (Hard Links)   │
│  • Daily 2AM    │     │  • Full backup   │     │                 │
│  • Weekly Sun   │     │  • Incremental   │     │  • Size check   │
│  • Monthly 1st  │     │  • Manifest gen  │     │  • Hash check   │
└─────────────────┘     └──────────────────┘     └─────────────────┘
         │                       │                        │
         │                       ▼                        ▼
         │              ┌──────────────────┐     ┌─────────────────┐
         │              │  Verifier        │     │  Retention      │
         │              │  (SHA-256)       │     │  Policy (GFS)   │
         │              │                  │     │                 │
         │              │  • Chunked read  │     │  • Daily: 7     │
         │              │  • 64KB buffer   │     │  • Weekly: 4    │
         │              │  • Manifest      │     │  • Monthly: 12  │
         │              └──────────────────┘     └─────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐     ┌──────────────────┐
│  Streamlit UI   │     │  RestoreManager  │
│                 │     │                  │
│  • Status       │     │  • Verify checksum
│  • History      │     │  • Confirm dialog│
│  • Manual       │     │  • Transaction   │
│  • Restore      │     │  • Rollback      │
└─────────────────┘     └──────────────────┘
```

### Module Structure

```
brain/backup/
├── __init__.py              # Package exports, version info
├── models.py                # BackupJob, BackupSchedule, RetentionPolicy dataclasses
├── manager.py               # BackupManager - main orchestrator class
├── scheduler.py             # BackupScheduler - APScheduler integration
├── retention.py             # GFSRetentionPolicy - retention engine
├── restore.py               # RestoreManager - restore with confirmation
├── verifier.py              # BackupVerifier - SHA-256 checksum
├── manifest.py              # BackupManifest - JSON manifest handling
└── dedup.py                 # DeduplicationEngine - hard link dedup (optional)

tracking_app/pages/
└── backup_restore.py        # Streamlit UI page

tests/
└── test_backup.py           # pytest tests with pyfakefs
```

---

## 📦 Data Models

### models.py - Core Dataclasses

Following the exact pattern from `brain/data_import/models.py`:

```python
"""
Backup System Models

Python dataclasses for backup job tracking and scheduling.
All implementation is in Python 3.10+
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any, Set
from enum import Enum
import uuid
import json


class BackupType(Enum):
    """Types of backups supported."""
    FULL = "full"                    # Complete database copy
    INCREMENTAL = "incremental"      # Changes since last backup (hard links)


class BackupStatus(Enum):
    """Backup job status lifecycle."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    VERIFIED = "verified"            # Checksum verified


class BackupFrequency(Enum):
    """Backup schedule frequency options."""
    HOURLY = "hourly"
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


@dataclass
class BackupJob:
    """
    Represents a single backup job.
    
    Tracks the complete lifecycle of a backup from creation through
    verification. Stored in SQLite for history and analytics.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    backup_type: BackupType = BackupType.FULL
    status: BackupStatus = BackupStatus.PENDING
    file_path: str = ""                          # Path to backup file
    file_size_bytes: int = 0
    checksum: str = ""                           # SHA-256 hash
    record_count: int = 0                        # Number of records backed up
    previous_backup_id: Optional[str] = None     # For incremental chains
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    verified_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None        # When backup can be deleted
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for SQLite storage."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'backup_type': self.backup_type.value,
            'status': self.status.value,
            'file_path': self.file_path,
            'file_size_bytes': self.file_size_bytes,
            'checksum': self.checksum,
            'record_count': self.record_count,
            'previous_backup_id': self.previous_backup_id,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'verified_at': self.verified_at.isoformat() if self.verified_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'error_message': self.error_message,
            'metadata': json.dumps(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BackupJob':
        """Create instance from SQLite row dictionary."""
        return cls(
            id=data.get('id', str(uuid.uuid4())),
            user_id=data.get('user_id', ''),
            backup_type=BackupType(data.get('backup_type', 'full')),
            status=BackupStatus(data.get('status', 'pending')),
            file_path=data.get('file_path', ''),
            file_size_bytes=data.get('file_size_bytes', 0),
            checksum=data.get('checksum', ''),
            record_count=data.get('record_count', 0),
            previous_backup_id=data.get('previous_backup_id'),
            started_at=datetime.fromisoformat(data['started_at']) if data.get('started_at') else None,
            completed_at=datetime.fromisoformat(data['completed_at']) if data.get('completed_at') else None,
            verified_at=datetime.fromisoformat(data['verified_at']) if data.get('verified_at') else None,
            expires_at=datetime.fromisoformat(data['expires_at']) if data.get('expires_at') else None,
            error_message=data.get('error_message'),
            metadata=json.loads(data.get('metadata', '{}')),
        )


@dataclass
class BackupSchedule:
    """
    Automated backup schedule configuration.
    
    Defines when automatic backups should be created.
    Managed by BackupScheduler using APScheduler.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    enabled: bool = True
    frequency: BackupFrequency = BackupFrequency.DAILY
    time_of_day: str = "02:00"                   # HH:MM format (24h)
    day_of_week: int = 6                         # 0=Monday, 6=Sunday (for weekly)
    day_of_month: int = 1                        # 1-28 (for monthly)
    backup_type: BackupType = BackupType.FULL
    retention_daily: int = 7                     # Keep N daily backups
    retention_weekly: int = 4                    # Keep N weekly backups
    retention_monthly: int = 12                  # Keep N monthly backups
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for SQLite storage."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'enabled': self.enabled,
            'frequency': self.frequency.value,
            'time_of_day': self.time_of_day,
            'day_of_week': self.day_of_week,
            'day_of_month': self.day_of_month,
            'backup_type': self.backup_type.value,
            'retention_daily': self.retention_daily,
            'retention_weekly': self.retention_weekly,
            'retention_monthly': self.retention_monthly,
            'last_run': self.last_run.isoformat() if self.last_run else None,
            'next_run': self.next_run.isoformat() if self.next_run else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BackupSchedule':
        """Create instance from SQLite row dictionary."""
        return cls(
            id=data.get('id', str(uuid.uuid4())),
            user_id=data.get('user_id', ''),
            enabled=bool(data.get('enabled', 1)),
            frequency=BackupFrequency(data.get('frequency', 'daily')),
            time_of_day=data.get('time_of_day', '02:00'),
            day_of_week=data.get('day_of_week', 6),
            day_of_month=data.get('day_of_month', 1),
            backup_type=BackupType(data.get('backup_type', 'full')),
            retention_daily=data.get('retention_daily', 7),
            retention_weekly=data.get('retention_weekly', 4),
            retention_monthly=data.get('retention_monthly', 12),
            last_run=datetime.fromisoformat(data['last_run']) if data.get('last_run') else None,
            next_run=datetime.fromisoformat(data['next_run']) if data.get('next_run') else None,
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.now(),
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else datetime.now(),
        )


@dataclass
class BackupManifest:
    """
    Backup manifest for integrity verification.
    
    Stored alongside each backup as a JSON file.
    Contains metadata and file checksums.
    """
    backup_id: str
    created_at: datetime
    backup_type: BackupType
    database_checksum: str                       # SHA-256 of main DB
    file_size_bytes: int
    record_count: int
    tables: Dict[str, int] = field(default_factory=dict)   # table_name -> row_count
    previous_backup_id: Optional[str] = None
    checksum_algorithm: str = "sha256"
    version: str = "1.0"

    def to_json(self) -> str:
        """Serialize to JSON string."""
        return json.dumps({
            'backup_id': self.backup_id,
            'created_at': self.created_at.isoformat(),
            'backup_type': self.backup_type.value,
            'database_checksum': self.database_checksum,
            'file_size_bytes': self.file_size_bytes,
            'record_count': self.record_count,
            'tables': self.tables,
            'previous_backup_id': self.previous_backup_id,
            'checksum_algorithm': self.checksum_algorithm,
            'version': self.version,
        }, indent=2)

    @classmethod
    def from_json(cls, json_str: str) -> 'BackupManifest':
        """Deserialize from JSON string."""
        data = json.loads(json_str)
        return cls(
            backup_id=data['backup_id'],
            created_at=datetime.fromisoformat(data['created_at']),
            backup_type=BackupType(data['backup_type']),
            database_checksum=data['database_checksum'],
            file_size_bytes=data['file_size_bytes'],
            record_count=data['record_count'],
            tables=data.get('tables', {}),
            previous_backup_id=data.get('previous_backup_id'),
            checksum_algorithm=data.get('checksum_algorithm', 'sha256'),
            version=data.get('version', '1.0'),
        )


@dataclass
class RestoreResult:
    """Result of a restore operation."""
    success: bool = False
    backup_id: str = ""
    records_restored: int = 0
    tables_restored: int = 0
    duration_seconds: float = 0.0
    checksum_verified: bool = False
    error_message: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'success': self.success,
            'backup_id': self.backup_id,
            'records_restored': self.records_restored,
            'tables_restored': self.tables_restored,
            'duration_seconds': self.duration_seconds,
            'checksum_verified': self.checksum_verified,
            'error_message': self.error_message,
            'details': self.details,
        }
```

---

## 🔧 Core Components

### 1. manager.py - BackupManager

Main orchestrator class for backup operations:

```python
"""
Backup Manager

Main Python class for orchestrating backup operations.
Coordinates backup creation, verification, and storage.

All implementation is in Python 3.10+
"""

import sqlite3
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

from brain.backup.models import (
    BackupJob,
    BackupType,
    BackupStatus,
    BackupManifest,
)
from brain.backup.verifier import BackupVerifier
from brain.backup.manifest import ManifestManager


logger = logging.getLogger(__name__)


class BackupManager:
    """
    Main backup orchestrator.
    
    Coordinates the full backup pipeline:
    1. Create backup directory structure
    2. Copy database file
    3. Generate SHA-256 checksum
    4. Create manifest file
    5. Apply deduplication (optional)
    6. Register backup in history
    
    Example:
        manager = BackupManager(db_path='tracking.db', backup_dir='backups/')
        
        # Create full backup
        job = manager.create_backup(user_id='user-123')
        
        if job.status == BackupStatus.COMPLETED:
            print(f"Backup created: {job.file_path}")
            print(f"Checksum: {job.checksum}")
    """
    
    def __init__(
        self,
        db_path: str = "tracking.db",
        backup_dir: str = "backups",
        db_connection: sqlite3.Connection = None
    ):
        """
        Initialize backup manager.
        
        Args:
            db_path: Path to SQLite database file
            backup_dir: Directory to store backups
            db_connection: Optional existing database connection
        """
        self.db_path = Path(db_path)
        self.backup_dir = Path(backup_dir)
        self.db = db_connection
        self.verifier = BackupVerifier()
        self.manifest_manager = ManifestManager()
        
        self._ensure_backup_directory()
    
    def _ensure_backup_directory(self) -> None:
        """Create backup directory if it doesn't exist."""
        self.backup_dir.mkdir(parents=True, exist_ok=True)
    
    def create_backup(
        self,
        user_id: str = "default",
        backup_type: BackupType = BackupType.FULL,
        previous_backup_id: Optional[str] = None
    ) -> BackupJob:
        """
        Create a new backup.
        
        Args:
            user_id: User ID for tracking
            backup_type: Full or incremental backup
            previous_backup_id: ID of previous backup (for incremental)
            
        Returns:
            BackupJob with backup details and status
        """
        # Create job record
        job = BackupJob(
            user_id=user_id,
            backup_type=backup_type,
            previous_backup_id=previous_backup_id,
            status=BackupStatus.PENDING,
            started_at=datetime.now()
        )
        
        try:
            # Update status
            job.status = BackupStatus.IN_PROGRESS
            
            # Generate backup filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"backup_{timestamp}_{job.id[:8]}.db"
            backup_path = self.backup_dir / backup_filename
            
            # Copy database file
            logger.info(f"Copying database to {backup_path}")
            shutil.copy2(self.db_path, backup_path)
            
            # Get file size
            job.file_path = str(backup_path)
            job.file_size_bytes = backup_path.stat().st_size
            
            # Generate checksum
            logger.info("Generating SHA-256 checksum")
            job.checksum = self.verifier.generate_checksum(backup_path)
            
            # Count records
            job.record_count = self._count_records(backup_path)
            
            # Create manifest
            manifest = BackupManifest(
                backup_id=job.id,
                created_at=datetime.now(),
                backup_type=backup_type,
                database_checksum=job.checksum,
                file_size_bytes=job.file_size_bytes,
                record_count=job.record_count,
                tables=self._get_table_counts(backup_path),
                previous_backup_id=previous_backup_id
            )
            
            # Save manifest
            manifest_path = backup_path.with_suffix('.manifest.json')
            self.manifest_manager.save(manifest, manifest_path)
            
            # Mark complete
            job.status = BackupStatus.COMPLETED
            job.completed_at = datetime.now()
            
            logger.info(f"Backup completed: {job.id}")
            
        except Exception as e:
            job.status = BackupStatus.FAILED
            job.error_message = str(e)
            job.completed_at = datetime.now()
            logger.error(f"Backup failed: {e}")
        
        # Save job to history
        self._save_job(job)
        
        return job
    
    def get_backup(self, backup_id: str) -> Optional[BackupJob]:
        """Retrieve a backup job by ID."""
        # Query from database
        pass
    
    def list_backups(
        self,
        user_id: str = None,
        status: BackupStatus = None,
        limit: int = 50
    ) -> List[BackupJob]:
        """List backup jobs with optional filtering."""
        pass
    
    def delete_backup(self, backup_id: str) -> bool:
        """Delete a backup and its manifest."""
        pass
    
    def verify_backup(self, backup_id: str) -> bool:
        """Verify backup integrity using checksum."""
        pass
    
    def _count_records(self, db_path: Path) -> int:
        """Count total records in database."""
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        total = 0
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            total += cursor.fetchone()[0]
        
        conn.close()
        return total
    
    def _get_table_counts(self, db_path: Path) -> Dict[str, int]:
        """Get record counts per table."""
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        counts = {}
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            counts[table] = cursor.fetchone()[0]
        
        conn.close()
        return counts
    
    def _save_job(self, job: BackupJob) -> None:
        """Save backup job to history database."""
        pass
```

### 2. scheduler.py - BackupScheduler

APScheduler integration for automated backups:

```python
"""
Backup Scheduler

APScheduler BackgroundScheduler integration for automated backups.
Designed for Streamlit apps where main thread is occupied by UI.

All implementation is in Python 3.10+
"""

import atexit
import logging
from datetime import datetime, timedelta
from typing import Optional, Callable

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger

from brain.backup.models import BackupSchedule, BackupFrequency, BackupType
from brain.backup.manager import BackupManager


logger = logging.getLogger(__name__)


class BackupScheduler:
    """
    Manages scheduled backup jobs using APScheduler.
    
    Uses BackgroundScheduler to run backup jobs in a dedicated thread,
    preventing interference with the Streamlit UI event loop.
    
    Example:
        scheduler = BackupScheduler(backup_manager)
        scheduler.add_daily_backup(hour=2, minute=0)
        scheduler.start()
        
        # Check next run time
        print(f"Next backup: {scheduler.get_next_run()}")
    """
    
    def __init__(self, backup_manager: BackupManager):
        """
        Initialize backup scheduler.
        
        Args:
            backup_manager: BackupManager instance for creating backups
        """
        self.backup_manager = backup_manager
        self.scheduler = BackgroundScheduler()
        self._started = False
        
        # Register shutdown handler
        atexit.register(self.shutdown)
    
    def start(self) -> None:
        """Start the scheduler."""
        if not self._started:
            self.scheduler.start()
            self._started = True
            logger.info("Backup scheduler started")
    
    def shutdown(self, wait: bool = False) -> None:
        """
        Shutdown the scheduler.
        
        Args:
            wait: If True, wait for running jobs to complete
        """
        if self._started:
            self.scheduler.shutdown(wait=wait)
            self._started = False
            logger.info("Backup scheduler shutdown")
    
    def add_daily_backup(
        self,
        hour: int = 2,
        minute: int = 0,
        backup_type: BackupType = BackupType.FULL,
        job_id: str = "daily_backup"
    ) -> None:
        """
        Schedule a daily backup.
        
        Args:
            hour: Hour of day (0-23)
            minute: Minute of hour (0-59)
            backup_type: Type of backup to create
            job_id: Unique identifier for the job
        """
        self.scheduler.add_job(
            func=self._run_backup,
            trigger=CronTrigger(hour=hour, minute=minute),
            id=job_id,
            args=[backup_type],
            max_instances=1,      # Prevent concurrent backups
            coalesce=True,        # Fire only once if missed
            misfire_grace_time=3600,  # 1 hour grace period
            replace_existing=True
        )
        logger.info(f"Scheduled daily backup at {hour:02d}:{minute:02d}")
    
    def add_weekly_backup(
        self,
        day_of_week: int = 6,    # 0=Monday, 6=Sunday
        hour: int = 2,
        minute: int = 0,
        backup_type: BackupType = BackupType.FULL,
        job_id: str = "weekly_backup"
    ) -> None:
        """
        Schedule a weekly backup.
        
        Args:
            day_of_week: Day of week (0=Monday, 6=Sunday)
            hour: Hour of day (0-23)
            minute: Minute of hour (0-59)
            backup_type: Type of backup to create
            job_id: Unique identifier for the job
        """
        self.scheduler.add_job(
            func=self._run_backup,
            trigger=CronTrigger(day_of_week=day_of_week, hour=hour, minute=minute),
            id=job_id,
            args=[backup_type],
            max_instances=1,
            coalesce=True,
            misfire_grace_time=86400,  # 24 hour grace for weekly
            replace_existing=True
        )
        logger.info(f"Scheduled weekly backup for day {day_of_week} at {hour:02d}:{minute:02d}")
    
    def add_monthly_backup(
        self,
        day_of_month: int = 1,
        hour: int = 2,
        minute: int = 0,
        backup_type: BackupType = BackupType.FULL,
        job_id: str = "monthly_backup"
    ) -> None:
        """
        Schedule a monthly backup.
        
        Args:
            day_of_month: Day of month (1-28, to avoid month-end issues)
            hour: Hour of day (0-23)
            minute: Minute of hour (0-59)
            backup_type: Type of backup to create
            job_id: Unique identifier for the job
        """
        self.scheduler.add_job(
            func=self._run_backup,
            trigger=CronTrigger(day=day_of_month, hour=hour, minute=minute),
            id=job_id,
            args=[backup_type],
            max_instances=1,
            coalesce=True,
            misfire_grace_time=86400,  # 24 hour grace
            replace_existing=True
        )
        logger.info(f"Scheduled monthly backup for day {day_of_month} at {hour:02d}:{minute:02d}")
    
    def remove_job(self, job_id: str) -> bool:
        """
        Remove a scheduled job.
        
        Args:
            job_id: ID of the job to remove
            
        Returns:
            True if job was removed, False if not found
        """
        try:
            self.scheduler.remove_job(job_id)
            logger.info(f"Removed scheduled job: {job_id}")
            return True
        except Exception:
            return False
    
    def get_next_run(self, job_id: str = "daily_backup") -> Optional[datetime]:
        """
        Get the next scheduled run time for a job.
        
        Args:
            job_id: ID of the job
            
        Returns:
            Next run time or None if job doesn't exist
        """
        job = self.scheduler.get_job(job_id)
        return job.next_run_time if job else None
    
    def get_all_jobs(self) -> list:
        """Get all scheduled jobs."""
        return self.scheduler.get_jobs()
    
    def _run_backup(self, backup_type: BackupType) -> None:
        """
        Execute a backup job (called by scheduler).
        
        Args:
            backup_type: Type of backup to create
        """
        try:
            logger.info(f"Starting scheduled {backup_type.value} backup")
            job = self.backup_manager.create_backup(backup_type=backup_type)
            
            if job.status.value == "completed":
                logger.info(f"Scheduled backup completed: {job.id}")
            else:
                logger.error(f"Scheduled backup failed: {job.error_message}")
                
        except Exception as e:
            logger.error(f"Scheduled backup error: {e}")
    
    def add_from_schedule(self, schedule: BackupSchedule) -> None:
        """
        Add jobs from a BackupSchedule configuration.
        
        Args:
            schedule: BackupSchedule instance
        """
        if not schedule.enabled:
            return
        
        if schedule.frequency == BackupFrequency.DAILY:
            hour, minute = map(int, schedule.time_of_day.split(':'))
            self.add_daily_backup(
                hour=hour,
                minute=minute,
                backup_type=schedule.backup_type,
                job_id=f"daily_{schedule.id}"
            )
        elif schedule.frequency == BackupFrequency.WEEKLY:
            hour, minute = map(int, schedule.time_of_day.split(':'))
            self.add_weekly_backup(
                day_of_week=schedule.day_of_week,
                hour=hour,
                minute=minute,
                backup_type=schedule.backup_type,
                job_id=f"weekly_{schedule.id}"
            )
        elif schedule.frequency == BackupFrequency.MONTHLY:
            hour, minute = map(int, schedule.time_of_day.split(':'))
            self.add_monthly_backup(
                day_of_month=schedule.day_of_month,
                hour=hour,
                minute=minute,
                backup_type=schedule.backup_type,
                job_id=f"monthly_{schedule.id}"
            )
```

### 3. retention.py - GFS Retention Policy

Grandfather-Father-Son retention engine:

```python
"""
Retention Policy Engine

GFS (Grandfather-Father-Son) retention policy implementation.
Balances backup granularity with storage efficiency.

All implementation is in Python 3.10+
"""

from datetime import datetime, timedelta
from typing import List, Set, Optional
from dataclasses import dataclass
import logging

from brain.backup.models import BackupJob


logger = logging.getLogger(__name__)


@dataclass
class RetentionConfig:
    """Configuration for GFS retention policy."""
    daily_keep: int = 7        # Keep last 7 daily backups
    weekly_keep: int = 4       # Keep last 4 weekly backups  
    monthly_keep: int = 12     # Keep last 12 monthly backups
    yearly_keep: int = 3       # Keep last 3 yearly backups
    
    # Enhanced options from backup-warden research
    relaxed: bool = False      # Don't enforce strict time windows
    prefer_recent: bool = True # Keep most recent in slot (vs oldest)


class GFSRetentionPolicy:
    """
    GFS (Grandfather-Father-Son) retention policy engine.
    
    Implements the industry-standard backup rotation scheme:
    - Son (Daily): Keep for immediate recovery
    - Father (Weekly): Keep for month-level rollback
    - Grandfather (Monthly): Keep for year-level compliance
    - Archive (Yearly): Keep for long-term retention
    
    Uses "protection list" methodology - builds a set of backups
    to KEEP rather than a set to DELETE (fail-safe design).
    
    Example:
        policy = GFSRetentionPolicy()
        backups = backup_manager.list_backups()
        
        keep_ids = policy.apply(backups)
        
        for backup in backups:
            if backup.id not in keep_ids:
                backup_manager.delete_backup(backup.id)
    """
    
    def __init__(self, config: RetentionConfig = None):
        """
        Initialize retention policy.
        
        Args:
            config: Retention configuration (uses defaults if None)
        """
        self.config = config or RetentionConfig()
    
    def apply(self, backups: List[BackupJob]) -> Set[str]:
        """
        Apply GFS retention policy to backup list.
        
        Args:
            backups: List of backup jobs to evaluate
            
        Returns:
            Set of backup IDs to KEEP (all others can be deleted)
        """
        if not backups:
            return set()
        
        keep_set = set()
        now = datetime.now()
        
        # Sort by date (newest first)
        sorted_backups = sorted(
            [b for b in backups if b.completed_at],
            key=lambda b: b.completed_at,
            reverse=True
        )
        
        # Track what we've kept per category
        daily_count = 0
        weekly_count = 0
        monthly_count = 0
        yearly_count = 0
        
        # Track slots we've filled
        weeks_filled = set()   # (year, week_num)
        months_filled = set()  # (year, month)
        years_filled = set()   # year
        
        for backup in sorted_backups:
            age_days = (now - backup.completed_at).days
            backup_date = backup.completed_at
            
            # Yearly: Keep one per year
            year_key = backup_date.year
            if yearly_count < self.config.yearly_keep:
                if year_key not in years_filled:
                    keep_set.add(backup.id)
                    years_filled.add(year_key)
                    yearly_count += 1
                    continue
            
            # Monthly: Keep one per month
            month_key = (backup_date.year, backup_date.month)
            if monthly_count < self.config.monthly_keep:
                if month_key not in months_filled:
                    keep_set.add(backup.id)
                    months_filled.add(month_key)
                    monthly_count += 1
                    continue
            
            # Weekly: Keep one per week
            week_num = backup_date.isocalendar()[1]
            week_key = (backup_date.year, week_num)
            if weekly_count < self.config.weekly_keep:
                if week_key not in weeks_filled:
                    keep_set.add(backup.id)
                    weeks_filled.add(week_key)
                    weekly_count += 1
                    continue
            
            # Daily: Keep last N days
            if age_days < self.config.daily_keep and daily_count < self.config.daily_keep:
                keep_set.add(backup.id)
                daily_count += 1
        
        logger.info(
            f"Retention policy: keeping {len(keep_set)}/{len(backups)} backups "
            f"(daily={daily_count}, weekly={weekly_count}, monthly={monthly_count}, yearly={yearly_count})"
        )
        
        return keep_set
    
    def get_deletable(self, backups: List[BackupJob]) -> List[BackupJob]:
        """
        Get list of backups that can be deleted.
        
        Args:
            backups: List of backup jobs to evaluate
            
        Returns:
            List of backup jobs that can be safely deleted
        """
        keep_ids = self.apply(backups)
        return [b for b in backups if b.id not in keep_ids]
    
    def get_next_expiry(
        self,
        backups: List[BackupJob]
    ) -> Optional[tuple[BackupJob, datetime]]:
        """
        Get the next backup that will expire.
        
        Args:
            backups: List of backup jobs
            
        Returns:
            Tuple of (backup, expiry_date) or None if none expiring
        """
        deletable = self.get_deletable(backups)
        if not deletable:
            return None
        
        # Return oldest deletable backup
        oldest = min(deletable, key=lambda b: b.completed_at)
        return (oldest, oldest.completed_at)
```

### 4. verifier.py - BackupVerifier

SHA-256 checksum verification:

```python
"""
Backup Verifier

SHA-256 checksum verification for backup integrity.
Uses chunked reading for constant memory footprint.

All implementation is in Python 3.10+
"""

import hashlib
from pathlib import Path
from typing import Optional
import logging


logger = logging.getLogger(__name__)


class BackupVerifier:
    """
    Verifies backup integrity using SHA-256 checksums.
    
    Uses chunked reading (64KB buffer) to maintain constant
    memory footprint regardless of file size.
    
    Example:
        verifier = BackupVerifier()
        
        # Generate checksum
        checksum = verifier.generate_checksum(Path('backup.db'))
        
        # Verify against expected
        is_valid = verifier.verify(Path('backup.db'), expected_checksum)
    """
    
    # 64KB buffer for chunked reading
    BUFFER_SIZE = 65536
    
    def generate_checksum(self, file_path: Path) -> str:
        """
        Generate SHA-256 checksum for a file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Hexadecimal SHA-256 checksum string (64 chars)
        """
        sha256 = hashlib.sha256()
        
        with open(file_path, 'rb') as f:
            while chunk := f.read(self.BUFFER_SIZE):
                sha256.update(chunk)
        
        checksum = sha256.hexdigest()
        logger.debug(f"Generated checksum for {file_path}: {checksum[:16]}...")
        
        return checksum
    
    def verify(self, file_path: Path, expected_checksum: str) -> bool:
        """
        Verify file against expected checksum.
        
        Args:
            file_path: Path to the file to verify
            expected_checksum: Expected SHA-256 checksum
            
        Returns:
            True if checksums match, False otherwise
        """
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return False
        
        actual_checksum = self.generate_checksum(file_path)
        
        if actual_checksum == expected_checksum:
            logger.info(f"Checksum verified for {file_path}")
            return True
        else:
            logger.error(
                f"Checksum mismatch for {file_path}: "
                f"expected {expected_checksum[:16]}..., "
                f"got {actual_checksum[:16]}..."
            )
            return False
    
    def verify_manifest(
        self,
        backup_path: Path,
        manifest_checksum: str
    ) -> bool:
        """
        Verify backup against manifest checksum.
        
        Args:
            backup_path: Path to backup file
            manifest_checksum: Checksum from manifest file
            
        Returns:
            True if verified, False otherwise
        """
        return self.verify(backup_path, manifest_checksum)
    
    def quick_verify(self, file_path: Path) -> Optional[str]:
        """
        Quick verification - returns checksum or None if file unreadable.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Checksum string or None on error
        """
        try:
            return self.generate_checksum(file_path)
        except Exception as e:
            logger.error(f"Quick verify failed for {file_path}: {e}")
            return None
```

### 5. restore.py - RestoreManager

Restore with confirmation workflow:

```python
"""
Restore Manager

Handles backup restoration with confirmation workflow.
Supports rollback on failure.

All implementation is in Python 3.10+
"""

import sqlite3
import shutil
from pathlib import Path
from typing import Optional
from datetime import datetime
import logging

from brain.backup.models import BackupJob, RestoreResult, BackupManifest
from brain.backup.verifier import BackupVerifier
from brain.backup.manifest import ManifestManager


logger = logging.getLogger(__name__)


class RestoreManager:
    """
    Manages backup restoration with safety checks.
    
    Restoration workflow:
    1. Verify backup checksum
    2. Create safety backup of current state
    3. Restore database from backup
    4. Verify restored database
    5. Rollback on failure
    
    Example:
        restore_manager = RestoreManager(db_path='tracking.db')
        
        # Restore with confirmation
        result = restore_manager.restore(
            backup_path=Path('backups/backup_20260219_020000.db'),
            create_safety_backup=True
        )
        
        if result.success:
            print(f"Restored {result.records_restored} records")
    """
    
    def __init__(
        self,
        db_path: str = "tracking.db",
        backup_dir: str = "backups",
        db_connection: sqlite3.Connection = None
    ):
        """
        Initialize restore manager.
        
        Args:
            db_path: Path to the active database
            backup_dir: Directory containing backups
            db_connection: Optional database connection
        """
        self.db_path = Path(db_path)
        self.backup_dir = Path(backup_dir)
        self.db = db_connection
        self.verifier = BackupVerifier()
        self.manifest_manager = ManifestManager()
    
    def restore(
        self,
        backup_path: Path,
        verify_checksum: bool = True,
        create_safety_backup: bool = True,
        expected_checksum: Optional[str] = None
    ) -> RestoreResult:
        """
        Restore database from backup.
        
        Args:
            backup_path: Path to backup file
            verify_checksum: Whether to verify checksum before restore
            create_safety_backup: Create backup of current state before restore
            expected_checksum: Expected checksum (loaded from manifest if None)
            
        Returns:
            RestoreResult with restoration details
        """
        start_time = datetime.now()
        result = RestoreResult(backup_id="")
        
        try:
            # Load manifest if available
            manifest_path = backup_path.with_suffix('.manifest.json')
            manifest = None
            if manifest_path.exists():
                manifest = self.manifest_manager.load(manifest_path)
                result.backup_id = manifest.backup_id
            
            # Verify checksum
            if verify_checksum:
                checksum = expected_checksum or (manifest.database_checksum if manifest else None)
                if checksum:
                    if not self.verifier.verify(backup_path, checksum):
                        return RestoreResult(
                            success=False,
                            error_message="Checksum verification failed"
                        )
                    result.checksum_verified = True
                else:
                    logger.warning("No checksum available for verification")
            
            # Create safety backup
            safety_backup_path = None
            if create_safety_backup and self.db_path.exists():
                safety_backup_path = self._create_safety_backup()
                logger.info(f"Created safety backup: {safety_backup_path}")
            
            # Close existing connections
            if self.db:
                self.db.close()
            
            # Restore database
            logger.info(f"Restoring database from {backup_path}")
            shutil.copy2(backup_path, self.db_path)
            
            # Verify restored database
            record_count = self._count_records(self.db_path)
            result.records_restored = record_count
            result.tables_restored = len(self._get_table_counts(self.db_path))
            
            # Calculate duration
            result.duration_seconds = (datetime.now() - start_time).total_seconds()
            
            result.success = True
            logger.info(f"Restore completed: {result.records_restored} records")
            
            # Clean up safety backup on success
            if safety_backup_path and safety_backup_path.exists():
                safety_backup_path.unlink()
                logger.info("Removed safety backup")
            
        except Exception as e:
            result.success = False
            result.error_message = str(e)
            logger.error(f"Restore failed: {e}")
            
            # Attempt rollback
            if create_safety_backup and 'safety_backup_path' in locals():
                self._rollback(safety_backup_path)
        
        return result
    
    def _create_safety_backup(self) -> Path:
        """Create a safety backup before restoration."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_safety")
        safety_path = self.backup_dir / f"safety_{timestamp}.db"
        shutil.copy2(self.db_path, safety_path)
        return safety_path
    
    def _rollback(self, safety_backup_path: Path) -> bool:
        """Rollback to safety backup."""
        try:
            if safety_backup_path.exists():
                shutil.copy2(safety_backup_path, self.db_path)
                logger.info("Rolled back to safety backup")
                return True
        except Exception as e:
            logger.error(f"Rollback failed: {e}")
        return False
    
    def _count_records(self, db_path: Path) -> int:
        """Count total records in database."""
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        total = 0
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            total += cursor.fetchone()[0]
        
        conn.close()
        return total
    
    def _get_table_counts(self, db_path: Path) -> dict:
        """Get record counts per table."""
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
        tables = [row[0] for row in cursor.fetchall()]
        
        counts = {}
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            counts[table] = cursor.fetchone()[0]
        
        conn.close()
        return counts
    
    def preview_restore(
        self,
        backup_path: Path
    ) -> dict:
        """
        Preview what would be restored.
        
        Args:
            backup_path: Path to backup file
            
        Returns:
            Dictionary with preview information
        """
        # Load manifest
        manifest_path = backup_path.with_suffix('.manifest.json')
        manifest = None
        if manifest_path.exists():
            manifest = self.manifest_manager.load(manifest_path)
        
        # Get backup stats
        backup_stats = {
            'file_size_bytes': backup_path.stat().st_size if backup_path.exists() else 0,
            'created_at': manifest.created_at if manifest else None,
            'record_count': manifest.record_count if manifest else 0,
            'tables': manifest.tables if manifest else {},
            'checksum': manifest.database_checksum if manifest else None,
        }
        
        # Compare with current
        current_stats = {
            'file_size_bytes': self.db_path.stat().st_size if self.db_path.exists() else 0,
            'record_count': self._count_records(self.db_path) if self.db_path.exists() else 0,
            'tables': self._get_table_counts(self.db_path) if self.db_path.exists() else {},
        }
        
        return {
            'backup': backup_stats,
            'current': current_stats,
            'difference': {
                'records': backup_stats['record_count'] - current_stats['record_count'],
                'size_bytes': backup_stats['file_size_bytes'] - current_stats['file_size_bytes'],
            }
        }
```

### 6. manifest.py - ManifestManager

```python
"""
Manifest Manager

Handles backup manifest (JSON) creation and loading.

All implementation is in Python 3.10+
"""

import json
from pathlib import Path
from typing import Optional

from brain.backup.models import BackupManifest


class ManifestManager:
    """Manages backup manifest files."""
    
    def save(self, manifest: BackupManifest, path: Path) -> None:
        """Save manifest to JSON file."""
        with open(path, 'w') as f:
            f.write(manifest.to_json())
    
    def load(self, path: Path) -> Optional[BackupManifest]:
        """Load manifest from JSON file."""
        if not path.exists():
            return None
        
        with open(path, 'r') as f:
            return BackupManifest.from_json(f.read())
    
    def exists(self, backup_path: Path) -> bool:
        """Check if manifest exists for a backup."""
        manifest_path = backup_path.with_suffix('.manifest.json')
        return manifest_path.exists()
```

---

## 🖥️ Streamlit UI

### tracking_app/pages/backup_restore.py

```python
"""
Backup & Restore Page

Streamlit UI for backup management and restoration.
Uses session state for workflow tracking.

All implementation is in Python 3.10+
"""

import streamlit as st
from pathlib import Path
from datetime import datetime
import logging

from brain.backup.manager import BackupManager
from brain.backup.scheduler import BackupScheduler
from brain.backup.restore import RestoreManager
from brain.backup.retention import GFSRetentionPolicy, RetentionConfig
from brain.backup.models import BackupType, BackupStatus


logger = logging.getLogger(__name__)


def init_session_state():
    """Initialize session state variables."""
    if 'backup_in_progress' not in st.session_state:
        st.session_state.backup_in_progress = False
    if 'show_restore_confirm' not in st.session_state:
        st.session_state.show_restore_confirm = False
    if 'pending_restore' not in st.session_state:
        st.session_state.pending_restore = None
    if 'last_backup_time' not in st.session_state:
        st.session_state.last_backup_time = None


def render_status_metrics(backup_manager: BackupManager):
    """Render backup status metrics."""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Last Backup",
            st.session_state.last_backup_time or "Never"
        )
    
    with col2:
        backups = backup_manager.list_backups(limit=100)
        st.metric("Total Backups", len(backups))
    
    with col3:
        if backups:
            total_size = sum(b.file_size_bytes for b in backups)
            size_mb = total_size / (1024 * 1024)
            st.metric("Storage Used", f"{size_mb:.1f} MB")
        else:
            st.metric("Storage Used", "0 MB")
    
    with col4:
        status = "🟢 Ready" if not st.session_state.backup_in_progress else "🟡 In Progress"
        st.metric("Status", status)


def render_backup_section(backup_manager: BackupManager):
    """Render backup creation section."""
    st.subheader("Create Backup")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        backup_type = st.selectbox(
            "Backup Type",
            options=[BackupType.FULL, BackupType.INCREMENTAL],
            format_func=lambda x: x.value.title()
        )
    
    with col2:
        st.write("")  # Spacing
        st.write("")  # Spacing
        create_btn = st.button(
            "🔄 Create Backup",
            disabled=st.session_state.backup_in_progress,
            type="primary"
        )
    
    if create_btn:
        st.session_state.backup_in_progress = True
        
        with st.spinner("Creating backup..."):
            job = backup_manager.create_backup(backup_type=backup_type)
        
        st.session_state.backup_in_progress = False
        
        if job.status == BackupStatus.COMPLETED:
            st.success(f"✅ Backup created: {job.id[:8]}")
            st.info(f"Size: {job.file_size_bytes / 1024:.1f} KB | Records: {job.record_count}")
            st.session_state.last_backup_time = datetime.now().strftime("%Y-%m-%d %H:%M")
        else:
            st.error(f"❌ Backup failed: {job.error_message}")
        
        st.rerun()


def render_backup_history(backup_manager: BackupManager):
    """Render backup history list."""
    st.subheader("Backup History")
    
    backups = backup_manager.list_backups(limit=20)
    
    if not backups:
        st.info("No backups yet. Create your first backup above.")
        return
    
    for backup in backups:
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
            
            with col1:
                status_icon = "✅" if backup.status == BackupStatus.COMPLETED else "❌"
                st.write(f"{status_icon} **{backup.id[:8]}** ({backup.backup_type.value})")
                st.caption(f"Created: {backup.completed_at.strftime('%Y-%m-%d %H:%M') if backup.completed_at else 'N/A'}")
            
            with col2:
                size_kb = backup.file_size_bytes / 1024
                st.write(f"📦 {size_kb:.1f} KB")
                st.caption(f"{backup.record_count} records")
            
            with col3:
                if backup.checksum:
                    st.write(f"🔐 {backup.checksum[:12]}...")
                else:
                    st.write("—")
            
            with col4:
                if st.button("Restore", key=f"restore_{backup.id}"):
                    st.session_state.show_restore_confirm = True
                    st.session_state.pending_restore = backup
                    st.rerun()
        
        st.divider()


def render_restore_confirmation(
    backup_manager: BackupManager,
    restore_manager: RestoreManager
):
    """Render restore confirmation dialog."""
    if not st.session_state.show_restore_confirm:
        return
    
    backup = st.session_state.pending_restore
    
    st.warning("⚠️ **Warning: Restore Operation**")
    st.write(f"Restoring backup **{backup.id[:8]}** will overwrite your current data.")
    
    # Preview
    preview = restore_manager.preview_restore(Path(backup.file_path))
    
    col1, col2 = st.columns(2)
    with col1:
        st.write("**Backup:**")
        st.write(f"- Records: {preview['backup']['record_count']}")
        st.write(f"- Size: {preview['backup']['file_size_bytes'] / 1024:.1f} KB")
    
    with col2:
        st.write("**Current:**")
        st.write(f"- Records: {preview['current']['record_count']}")
        st.write(f"- Size: {preview['current']['file_size_bytes'] / 1024:.1f} KB")
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Yes, Restore", type="primary"):
            with st.spinner("Restoring..."):
                result = restore_manager.restore(
                    backup_path=Path(backup.file_path),
                    verify_checksum=True,
                    create_safety_backup=True
                )
            
            st.session_state.show_restore_confirm = False
            st.session_state.pending_restore = None
            
            if result.success:
                st.success(f"✅ Restored {result.records_restored} records!")
            else:
                st.error(f"❌ Restore failed: {result.error_message}")
            
            st.rerun()
    
    with col2:
        if st.button("❌ Cancel"):
            st.session_state.show_restore_confirm = False
            st.session_state.pending_restore = None
            st.rerun()


def render_schedule_section(scheduler: BackupScheduler):
    """Render backup schedule configuration."""
    st.subheader("Backup Schedule")
    
    enabled = st.checkbox("Enable Automatic Backups", value=True)
    
    col1, col2 = st.columns(2)
    
    with col1:
        frequency = st.selectbox(
            "Frequency",
            options=["Daily", "Weekly", "Monthly"]
        )
        
        time_str = st.time_input("Time of Day", value=datetime.now().replace(hour=2, minute=0))
    
    with col2:
        if frequency == "Weekly":
            day = st.selectbox(
                "Day of Week",
                options=["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"],
                index=6
            )
        elif frequency == "Monthly":
            day = st.number_input("Day of Month", min_value=1, max_value=28, value=1)
    
    # Show next scheduled run
    next_run = scheduler.get_next_run()
    if next_run:
        st.info(f"📅 Next scheduled backup: {next_run.strftime('%Y-%m-%d %H:%M')}")


def render_retention_section():
    """Render retention policy configuration."""
    st.subheader("Retention Policy")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        daily = st.number_input("Daily Backups", min_value=1, max_value=30, value=7)
    
    with col2:
        weekly = st.number_input("Weekly Backups", min_value=1, max_value=12, value=4)
    
    with col3:
        monthly = st.number_input("Monthly Backups", min_value=1, max_value=24, value=12)
    
    with col4:
        yearly = st.number_input("Yearly Backups", min_value=0, max_value=10, value=3)
    
    st.caption(
        f"GFS Policy: Keep {daily} daily + {weekly} weekly + {monthly} monthly + {yearly} yearly backups"
    )


def main():
    """Main page entry point."""
    st.title("📦 Backup & Restore")
    
    init_session_state()
    
    # Initialize managers
    backup_manager = BackupManager(
        db_path="tracking.db",
        backup_dir="backups"
    )
    
    restore_manager = RestoreManager(
        db_path="tracking.db",
        backup_dir="backups"
    )
    
    scheduler = BackupScheduler(backup_manager)
    scheduler.start()
    
    # Render sections
    render_status_metrics(backup_manager)
    
    st.divider()
    
    # Tabs for organization
    tab1, tab2, tab3 = st.tabs(["Backup", "History", "Settings"])
    
    with tab1:
        render_backup_section(backup_manager)
        render_schedule_section(scheduler)
    
    with tab2:
        render_backup_history(backup_manager)
        render_restore_confirmation(backup_manager, restore_manager)
    
    with tab3:
        render_retention_section()


if __name__ == "__main__":
    main()
```

---

## 🗄️ Database Schema

Add to SQLite database:

```sql
-- Backup job history
CREATE TABLE IF NOT EXISTS backup_jobs (
    id TEXT PRIMARY KEY,
    user_id TEXT,
    backup_type TEXT NOT NULL,
    status TEXT NOT NULL,
    file_path TEXT,
    file_size_bytes INTEGER DEFAULT 0,
    checksum TEXT,
    record_count INTEGER DEFAULT 0,
    previous_backup_id TEXT,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    verified_at TIMESTAMP,
    expires_at TIMESTAMP,
    error_message TEXT,
    metadata TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Backup schedules
CREATE TABLE IF NOT EXISTS backup_schedules (
    id TEXT PRIMARY KEY,
    user_id TEXT,
    enabled BOOLEAN DEFAULT 1,
    frequency TEXT NOT NULL,
    time_of_day TEXT DEFAULT '02:00',
    day_of_week INTEGER DEFAULT 6,
    day_of_month INTEGER DEFAULT 1,
    backup_type TEXT DEFAULT 'full',
    retention_daily INTEGER DEFAULT 7,
    retention_weekly INTEGER DEFAULT 4,
    retention_monthly INTEGER DEFAULT 12,
    last_run TIMESTAMP,
    next_run TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes for common queries
CREATE INDEX IF NOT EXISTS idx_backup_jobs_status ON backup_jobs(status);
CREATE INDEX IF NOT EXISTS idx_backup_jobs_created ON backup_jobs(created_at);
CREATE INDEX IF NOT EXISTS idx_backup_schedules_enabled ON backup_schedules(enabled);
```

---

## 🧪 Testing Strategy

### tests/test_backup.py

```python
"""
Backup System Tests

Unit and integration tests using pytest and pyfakefs.
Tests backup creation, verification, restoration, and retention.

All implementation is in Python 3.10+
"""

import pytest
from pyfakefs import fake_filesystem
from pathlib import Path
from datetime import datetime, timedelta
import hashlib

from brain.backup.models import (
    BackupJob,
    BackupType,
    BackupStatus,
    BackupSchedule,
    BackupFrequency,
    BackupManifest,
)
from brain.backup.manager import BackupManager
from brain.backup.verifier import BackupVerifier
from brain.backup.retention import GFSRetentionPolicy, RetentionConfig
from brain.backup.restore import RestoreManager


# ============== Fixtures ==============

@pytest.fixture
def fake_fs():
    """Create a fake filesystem for testing."""
    fs = fake_filesystem.FakeFilesystem()
    fs.create_dir('/data')
    fs.create_dir('/backups')
    
    # Create a fake database
    fs.create_file('/data/tracking.db', contents=b'fake database content')
    
    return fs


@pytest.fixture
def sample_backup_job():
    """Create a sample backup job for testing."""
    return BackupJob(
        id="test-backup-123",
        user_id="user-1",
        backup_type=BackupType.FULL,
        status=BackupStatus.COMPLETED,
        file_path="/backups/backup_20260219_020000.db",
        file_size_bytes=1024000,
        checksum="abc123def456",
        record_count=100,
        completed_at=datetime.now()
    )


# ============== Model Tests ==============

class TestBackupJob:
    """Tests for BackupJob dataclass."""
    
    def test_create_backup_job(self):
        """Test creating a backup job."""
        job = BackupJob(
            user_id="user-1",
            backup_type=BackupType.FULL
        )
        
        assert job.status == BackupStatus.PENDING
        assert job.backup_type == BackupType.FULL
        assert job.file_size_bytes == 0
    
    def test_backup_job_to_dict(self, sample_backup_job):
        """Test serialization to dictionary."""
        data = sample_backup_job.to_dict()
        
        assert data['id'] == "test-backup-123"
        assert data['backup_type'] == "full"
        assert data['status'] == "completed"
    
    def test_backup_job_from_dict(self):
        """Test deserialization from dictionary."""
        data = {
            'id': 'test-123',
            'backup_type': 'incremental',
            'status': 'completed',
            'file_path': '/backups/test.db',
            'file_size_bytes': 2048,
            'checksum': 'abc123',
            'record_count': 50,
        }
        
        job = BackupJob.from_dict(data)
        
        assert job.id == 'test-123'
        assert job.backup_type == BackupType.INCREMENTAL
        assert job.file_size_bytes == 2048


class TestBackupManifest:
    """Tests for BackupManifest dataclass."""
    
    def test_manifest_serialization(self):
        """Test manifest JSON serialization."""
        manifest = BackupManifest(
            backup_id="backup-123",
            created_at=datetime.now(),
            backup_type=BackupType.FULL,
            database_checksum="abc123",
            file_size_bytes=1024,
            record_count=100,
            tables={'habits': 50, 'tasks': 50}
        )
        
        json_str = manifest.to_json()
        
        assert '"backup_id": "backup-123"' in json_str
        assert '"habits": 50' in json_str
    
    def test_manifest_deserialization(self):
        """Test manifest JSON deserialization."""
        json_str = '''{
            "backup_id": "backup-456",
            "created_at": "2026-02-19T02:00:00",
            "backup_type": "full",
            "database_checksum": "def456",
            "file_size_bytes": 2048,
            "record_count": 200,
            "tables": {"habits": 100},
            "version": "1.0"
        }'''
        
        manifest = BackupManifest.from_json(json_str)
        
        assert manifest.backup_id == "backup-456"
        assert manifest.record_count == 200


# ============== Verifier Tests ==============

class TestBackupVerifier:
    """Tests for BackupVerifier class."""
    
    def test_generate_checksum(self, fake_fs):
        """Test SHA-256 checksum generation."""
        verifier = BackupVerifier()
        
        # Create test file
        content = b"test content for checksum"
        fake_fs.create_file('/test/file.db', contents=content)
        
        checksum = verifier.generate_checksum(Path('/test/file.db'))
        
        # Verify it's a valid SHA-256 hex string
        assert len(checksum) == 64
        assert all(c in '0123456789abcdef' for c in checksum)
    
    def test_verify_matching_checksum(self, fake_fs):
        """Test verification with matching checksum."""
        verifier = BackupVerifier()
        
        content = b"test content"
        fake_fs.create_file('/test/file.db', contents=content)
        
        expected = hashlib.sha256(content).hexdigest()
        
        assert verifier.verify(Path('/test/file.db'), expected)
    
    def test_verify_mismatched_checksum(self, fake_fs):
        """Test verification with mismatched checksum."""
        verifier = BackupVerifier()
        
        fake_fs.create_file('/test/file.db', contents=b"test content")
        
        wrong_checksum = "0" * 64  # Wrong checksum
        
        assert not verifier.verify(Path('/test/file.db'), wrong_checksum)


# ============== Retention Tests ==============

class TestGFSRetentionPolicy:
    """Tests for GFS retention policy."""
    
    def create_backup_at_date(self, days_ago: int, backup_id: str) -> BackupJob:
        """Helper to create backup at a specific date."""
        return BackupJob(
            id=backup_id,
            status=BackupStatus.COMPLETED,
            completed_at=datetime.now() - timedelta(days=days_ago)
        )
    
    def test_retention_keeps_recent_backups(self):
        """Test that recent backups are kept."""
        policy = GFSRetentionPolicy(RetentionConfig(daily_keep=7))
        
        backups = [
            self.create_backup_at_date(0, "today"),
            self.create_backup_at_date(1, "yesterday"),
            self.create_backup_at_date(2, "2-days-ago"),
            self.create_backup_at_date(10, "10-days-ago"),
        ]
        
        keep_ids = policy.apply(backups)
        
        # Recent backups should be kept
        assert "today" in keep_ids
        assert "yesterday" in keep_ids
        assert "2-days-ago" in keep_ids
    
    def test_retention_removes_old_backups(self):
        """Test that old backups beyond retention are removed."""
        policy = GFSRetentionPolicy(RetentionConfig(
            daily_keep=3,
            weekly_keep=0,
            monthly_keep=0,
            yearly_keep=0
        ))
        
        backups = [
            self.create_backup_at_date(0, "today"),
            self.create_backup_at_date(1, "yesterday"),
            self.create_backup_at_date(5, "5-days-ago"),
            self.create_backup_at_date(10, "10-days-ago"),
        ]
        
        keep_ids = policy.apply(backups)
        
        # Old backups should not be kept
        assert "10-days-ago" not in keep_ids
    
    def test_gfs_keeps_weekly_monthly(self):
        """Test that GFS keeps weekly and monthly backups."""
        policy = GFSRetentionPolicy(RetentionConfig(
            daily_keep=2,
            weekly_keep=2,
            monthly_keep=2,
            yearly_keep=0
        ))
        
        backups = [
            self.create_backup_at_date(0, "today"),
            self.create_backup_at_date(1, "yesterday"),
            self.create_backup_at_date(7, "week-1"),
            self.create_backup_at_date(14, "week-2"),
            self.create_backup_at_date(30, "month-1"),
            self.create_backup_at_date(60, "month-2"),
        ]
        
        keep_ids = policy.apply(backups)
        
        # Should keep weekly and monthly
        assert len(keep_ids) >= 4  # At least some weekly/monthly


# ============== Integration Tests ==============

class TestBackupRestoreRoundTrip:
    """Integration tests for full backup/restore cycle."""
    
    def test_backup_creates_manifest(self, fake_fs):
        """Test that backup creates manifest file."""
        # This would test the full backup creation with manifest
        pass
    
    def test_restore_from_backup(self, fake_fs):
        """Test complete restore from backup."""
        # This would test the full restore workflow
        pass
    
    def test_checksum_verification_in_restore(self, fake_fs):
        """Test that restore verifies checksum."""
        # This would test checksum verification during restore
        pass
```

---

## 📋 Implementation Checklist

### Week 1: Core Components

| Day | Task | File | Priority |
|-----|------|------|----------|
| 1 | Create models.py with all dataclasses | `brain/backup/models.py` | High |
| 1 | Create __init__.py with exports | `brain/backup/__init__.py` | High |
| 2 | Implement BackupVerifier | `brain/backup/verifier.py` | High |
| 2 | Implement ManifestManager | `brain/backup/manifest.py` | High |
| 3 | Implement BackupManager | `brain/backup/manager.py` | High |
| 4 | Implement GFSRetentionPolicy | `brain/backup/retention.py` | High |
| 5 | Implement BackupScheduler | `brain/backup/scheduler.py` | High |

### Week 2: Restore & UI

| Day | Task | File | Priority |
|-----|------|------|----------|
| 1 | Implement RestoreManager | `brain/backup/restore.py` | High |
| 2 | Create database schema migration | `tracking_app/migration.py` | High |
| 3 | Implement Streamlit UI | `tracking_app/pages/backup_restore.py` | High |
| 4 | Write unit tests | `tests/test_backup.py` | Medium |
| 5 | Write integration tests | `tests/test_backup.py` | Medium |

### Optional Enhancements

| Task | File | Priority |
|------|------|----------|
| Hard-link deduplication | `brain/backup/dedup.py` | Low |
| Progress callbacks for UI | `brain/backup/manager.py` | Low |
| Backup encryption | `brain/backup/crypto.py` | Low |

---

## 🔗 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| apscheduler | >=3.10.0 | Job scheduling |
| pytest | >=7.0.0 | Testing |
| pyfakefs | >=5.0.0 | Filesystem mocking |

All other functionality uses Python standard library (sqlite3, hashlib, json, shutil, pathlib).

---

## 📚 Cross-References

| Document | Content |
|----------|---------|
| [BACKUP_RESTORE_RESEARCH.md](../docs/research/BACKUP_RESTORE_RESEARCH.md) | Research findings |
| [BACKUP_REPOS_ANALYSIS.md](../docs/research/BACKUP_REPOS_ANALYSIS.md) | Repository analysis |
| [PHASE_5_DATA_MANAGEMENT.md](PHASE_5_DATA_MANAGEMENT.md) | Phase 5 overview |
| [PROJECT_RULES.md](PROJECT_RULES.md) | Development guidelines |

---

*Last updated: February 19, 2026*
*Status: 📋 Ready for Implementation*