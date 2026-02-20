# Phase 5.4: Data Lifecycle Management - Implementation Plan

**Created:** February 19, 2026  
**Status:** 📋 Ready for Implementation  
**Duration:** 5-6 days  
**Dependencies:** Phase 5.3 (Backup & Restore) 📋 Ready for Implementation  
**Research:** Required - GDPR compliance patterns, data archival strategies

---

## 🎯 Executive Summary

Phase 5.4 implements **Data Lifecycle Management** for the Veryfyn tracking system with:

- **Per-entity retention policies** - Different rules for different data types
- **Soft delete with recovery window** - 30-day safety net before permanent deletion
- **GDPR compliance** - Right to access, erasure, and portability
- **Automated lifecycle scheduling** - APScheduler for archive/purge jobs
- **Cascade delete handling** - Safe deletion of related records

All implementation follows **PROJECT_RULES.md** - Python 3.10+ with dataclasses, Streamlit UI.

---

## 🧠 Brain Context Protocol

**This module follows the Brain Context Protocol:**

1. **README.md files are source of truth** - Context loaded from documentation
2. **The brain folder is the thinking process** - All operations through brain architecture
3. **Simple prompts yield deep understanding** - AI interprets holistically

**Required Reading:**
- [PROJECT_RULES.md](../PROJECT_RULES.md) - Python-first development rules
- [brain/README.md](../brain/README.md) - Brain architecture
- [BRAIN_CONTEXT_PROTOCOL.md](../BRAIN_CONTEXT_PROTOCOL.md) - LLM interaction rules

---

## 📐 Architecture Overview

### System Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    LIFECYCLE MANAGEMENT ARCHITECTURE                     │
└─────────────────────────────────────────────────────────────────────────┘

┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  APScheduler    │────▶│ LifecycleManager │────▶│  Retention      │
│  (Background)   │     │  (Orchestrator)  │     │  Engine         │
│                 │     │                  │     │                 │
│  • Archive 3AM  │     │  • Apply policies│     │  • Per-entity   │
│  • Purge 4AM    │     │  • Cascade delete│     │  • Configurable │
│  • Cleanup 5AM  │     │  • Recovery mgmt │     │  • Defaults     │
└─────────────────┘     └──────────────────┘     └─────────────────┘
         │                       │                        │
         │                       ▼                        ▼
         │              ┌──────────────────┐     ┌─────────────────┐
         │              │  ArchiveManager  │     │  GDPR           │
         │              │  (Soft Delete)   │     │  Compliance     │
         │              │                  │     │                 │
         │              │  • Mark deleted  │     │  • Right to     │
         │              │  • Recovery 30d  │     │    access       │
         │              │  • Compress      │     │  • Right to     │
         │              └──────────────────┘     │    erasure      │
         │                       │               │  • Portability  │
         │                       ▼               └─────────────────┘
         │              ┌──────────────────┐
         │              │  PurgeManager    │
         │              │  (Hard Delete)   │
         │              │                  │
         │              │  • Recovery exp  │
         │              │  • Cascade purge │
         │              │  • Audit trail   │
         │              └──────────────────┘
         │                       │
         ▼                       ▼
┌─────────────────┐     ┌──────────────────┐
│  Streamlit UI   │     │  Audit Log       │
│                 │     │                  │
│  • Policies     │     │  • All actions   │
│  • Recovery     │     │  • User tracking │
│  • Reset        │     │  • Compliance    │
│  • GDPR         │     │                  │
└─────────────────┘     └──────────────────┘
```

### Module Structure

```
brain/lifecycle/
├── __init__.py              # Package exports, version info
├── models.py                # RetentionPolicy, DeletedRecord, DataReset, ErasureRequest
├── manager.py               # LifecycleManager - main orchestrator class
├── retention.py             # RetentionEngine - per-entity retention rules
├── archive.py               # ArchiveManager - soft delete with recovery
├── purge.py                 # PurgeManager - permanent deletion
├── scheduler.py             # LifecycleScheduler - APScheduler integration
├── gdpr.py                  # GDPRCompliance - GDPR utilities
├── recovery.py              # RecoveryManager - recovery window management
├── anonymizer.py            # DataAnonymizer - privacy-preserving analytics
└── cascade.py               # CascadeHandler - cascade delete rules

tracking_app/pages/
└── data_lifecycle.py        # Streamlit UI page

tests/
└── test_lifecycle.py        # pytest tests
```

---

## 📦 Data Models

### models.py - Core Dataclasses

Following the pattern from `brain/data_import/models.py` and `brain/backup/models.py`:

```python
"""
Data Lifecycle Models

Python dataclasses for lifecycle management.
Implements retention policies, soft delete, GDPR compliance.

All implementation is in Python 3.10+
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any, Set
from enum import Enum
import uuid
import json


class RetentionAction(Enum):
    """Actions that can be taken on a record."""
    KEEP = "keep"               # Within retention period
    ARCHIVE = "archive"         # Past archive threshold, soft delete
    PURGE = "purge"             # Past delete threshold, permanent delete


class PurgeStatus(Enum):
    """Status of a soft-deleted record."""
    RECOVERABLE = "recoverable"         # Within recovery window
    PENDING_PURGE = "pending_purge"     # Recovery expired, awaiting purge
    PURGED = "purged"                   # Permanently deleted


class ResetType(Enum):
    """Types of data reset operations."""
    FULL = "full"               # Delete all user data
    MODULE = "module"           # Reset specific module(s)
    ARCHIVE = "archive"         # Clear archived data only
    SOFT = "soft"               # Mark as incomplete (preserve history)


class ErasureStatus(Enum):
    """GDPR erasure request status."""
    PENDING = "pending"         # Request submitted
    VERIFIED = "verified"       # User identity verified
    GRACE_PERIOD = "grace_period"  # 30-day grace period active
    APPROVED = "approved"       # Approved for execution
    EXECUTED = "executed"       # Data erased
    CANCELLED = "cancelled"     # User cancelled request


@dataclass
class RetentionPolicy:
    """
    Data retention policy configuration per entity type.
    
    Defines how long data is kept before archiving and deletion.
    Different entity types have different requirements.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    entity_type: str = ""               # 'habit_log', 'task', 'transaction', etc.
    archive_after_days: int = 365       # Soft delete after N days
    delete_after_days: int = 730        # Permanent delete after N days (None = never)
    enabled: bool = True
    cascade_to: List[str] = field(default_factory=list)  # Related entities to cascade
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for SQLite storage."""
        return {
            'id': self.id,
            'entity_type': self.entity_type,
            'archive_after_days': self.archive_after_days,
            'delete_after_days': self.delete_after_days,
            'enabled': self.enabled,
            'cascade_to': ','.join(self.cascade_to) if self.cascade_to else '',
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RetentionPolicy':
        """Create instance from SQLite row dictionary."""
        cascade = data.get('cascade_to', '')
        return cls(
            id=data.get('id', str(uuid.uuid4())),
            entity_type=data.get('entity_type', ''),
            archive_after_days=data.get('archive_after_days', 365),
            delete_after_days=data.get('delete_after_days', 730),
            enabled=bool(data.get('enabled', 1)),
            cascade_to=cascade.split(',') if cascade else [],
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.now(),
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else datetime.now(),
        )


@dataclass
class DeletedRecord:
    """
    Tracks soft-deleted records for recovery.
    
    Provides a 30-day safety window before permanent deletion.
    Stores original data as JSON for potential recovery.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    entity_type: str = ""               # 'habit', 'task', 'transaction', etc.
    entity_id: str = ""                 # Original record ID
    original_data: Dict[str, Any] = field(default_factory=dict)  # JSON of original record
    deleted_at: datetime = field(default_factory=datetime.now)
    recovery_until: datetime = None     # When record can be permanently purged
    purge_status: PurgeStatus = PurgeStatus.RECOVERABLE
    cascade_source: Optional[str] = None  # ID of parent deletion if cascade
    deletion_reason: str = ""           # 'user', 'retention', 'gdpr', 'reset'
    deleted_by: str = ""                # User ID who initiated deletion
    
    def __post_init__(self):
        """Set default recovery window if not specified."""
        if self.recovery_until is None:
            self.recovery_until = datetime.now() + timedelta(days=30)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for SQLite storage."""
        return {
            'id': self.id,
            'entity_type': self.entity_type,
            'entity_id': self.entity_id,
            'original_data': json.dumps(self.original_data),
            'deleted_at': self.deleted_at.isoformat(),
            'recovery_until': self.recovery_until.isoformat(),
            'purge_status': self.purge_status.value,
            'cascade_source': self.cascade_source,
            'deletion_reason': self.deletion_reason,
            'deleted_by': self.deleted_by,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DeletedRecord':
        """Create instance from SQLite row dictionary."""
        return cls(
            id=data.get('id', str(uuid.uuid4())),
            entity_type=data.get('entity_type', ''),
            entity_id=data.get('entity_id', ''),
            original_data=json.loads(data.get('original_data', '{}')),
            deleted_at=datetime.fromisoformat(data['deleted_at']) if data.get('deleted_at') else datetime.now(),
            recovery_until=datetime.fromisoformat(data['recovery_until']) if data.get('recovery_until') else datetime.now() + timedelta(days=30),
            purge_status=PurgeStatus(data.get('purge_status', 'recoverable')),
            cascade_source=data.get('cascade_source'),
            deletion_reason=data.get('deletion_reason', ''),
            deleted_by=data.get('deleted_by', ''),
        )

    def is_recoverable(self) -> bool:
        """Check if record is still within recovery window."""
        return (
            self.purge_status == PurgeStatus.RECOVERABLE and
            datetime.now() < self.recovery_until
        )


@dataclass
class DataReset:
    """
    Track data reset operations.
    
    Records all reset operations for audit purposes.
    Optional backup is created before reset.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    reset_type: ResetType = ResetType.FULL
    modules: List[str] = field(default_factory=list)  # For module-specific reset
    backup_created: bool = False
    backup_id: Optional[str] = None       # Reference to backup job
    status: str = "pending"
    records_affected: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    confirmation_token: Optional[str] = None  # For two-step confirmation
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for SQLite storage."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'reset_type': self.reset_type.value,
            'modules': ','.join(self.modules) if self.modules else '',
            'backup_created': self.backup_created,
            'backup_id': self.backup_id,
            'status': self.status,
            'records_affected': self.records_affected,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'error_message': self.error_message,
            'confirmation_token': self.confirmation_token,
            'created_at': self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DataReset':
        """Create instance from SQLite row dictionary."""
        modules = data.get('modules', '')
        return cls(
            id=data.get('id', str(uuid.uuid4())),
            user_id=data.get('user_id', ''),
            reset_type=ResetType(data.get('reset_type', 'full')),
            modules=modules.split(',') if modules else [],
            backup_created=bool(data.get('backup_created', 0)),
            backup_id=data.get('backup_id'),
            status=data.get('status', 'pending'),
            records_affected=data.get('records_affected', 0),
            started_at=datetime.fromisoformat(data['started_at']) if data.get('started_at') else None,
            completed_at=datetime.fromisoformat(data['completed_at']) if data.get('completed_at') else None,
            error_message=data.get('error_message'),
            confirmation_token=data.get('confirmation_token'),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.now(),
        )


@dataclass
class ErasureRequest:
    """
    GDPR erasure request (Right to be Forgotten).
    
    Manages the complete lifecycle of an erasure request,
    including verification, grace period, and execution.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    status: ErasureStatus = ErasureStatus.PENDING
    requested_at: datetime = field(default_factory=datetime.now)
    verified_at: Optional[datetime] = None
    grace_period_until: Optional[datetime] = None  # 30-day grace period
    executed_at: Optional[datetime] = None
    data_export_path: Optional[str] = None  # Backup before erasure
    verification_token: Optional[str] = None  # Email verification token
    cancellation_reason: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)

    def __post_init__(self):
        """Set grace period after verification."""
        if self.status == ErasureStatus.GRACE_PERIOD and self.grace_period_until is None:
            self.grace_period_until = datetime.now() + timedelta(days=30)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for SQLite storage."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'status': self.status.value,
            'requested_at': self.requested_at.isoformat(),
            'verified_at': self.verified_at.isoformat() if self.verified_at else None,
            'grace_period_until': self.grace_period_until.isoformat() if self.grace_period_until else None,
            'executed_at': self.executed_at.isoformat() if self.executed_at else None,
            'data_export_path': self.data_export_path,
            'verification_token': self.verification_token,
            'cancellation_reason': self.cancellation_reason,
            'created_at': self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ErasureRequest':
        """Create instance from SQLite row dictionary."""
        return cls(
            id=data.get('id', str(uuid.uuid4())),
            user_id=data.get('user_id', ''),
            status=ErasureStatus(data.get('status', 'pending')),
            requested_at=datetime.fromisoformat(data['requested_at']) if data.get('requested_at') else datetime.now(),
            verified_at=datetime.fromisoformat(data['verified_at']) if data.get('verified_at') else None,
            grace_period_until=datetime.fromisoformat(data['grace_period_until']) if data.get('grace_period_until') else None,
            executed_at=datetime.fromisoformat(data['executed_at']) if data.get('executed_at') else None,
            data_export_path=data.get('data_export_path'),
            verification_token=data.get('verification_token'),
            cancellation_reason=data.get('cancellation_reason'),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.now(),
        )

    def can_execute(self) -> bool:
        """Check if erasure can be executed."""
        return (
            self.status == ErasureStatus.APPROVED or
            (self.status == ErasureStatus.GRACE_PERIOD and
             self.grace_period_until and
             datetime.now() >= self.grace_period_until)
        )


@dataclass
class LifecycleJob:
    """
    Tracks automated lifecycle jobs.
    
    Records execution of archive, purge, and cleanup jobs.
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    job_type: str = ""                   # 'archive', 'purge', 'recovery_cleanup'
    entity_type: Optional[str] = None    # Specific entity or all
    records_processed: int = 0
    records_archived: int = 0
    records_purged: int = 0
    records_recovered: int = 0
    duration_seconds: float = 0.0
    status: str = "pending"
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for SQLite storage."""
        return {
            'id': self.id,
            'job_type': self.job_type,
            'entity_type': self.entity_type,
            'records_processed': self.records_processed,
            'records_archived': self.records_archived,
            'records_purged': self.records_purged,
            'records_recovered': self.records_recovered,
            'duration_seconds': self.duration_seconds,
            'status': self.status,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'LifecycleJob':
        """Create instance from SQLite row dictionary."""
        return cls(
            id=data.get('id', str(uuid.uuid4())),
            job_type=data.get('job_type', ''),
            entity_type=data.get('entity_type'),
            records_processed=data.get('records_processed', 0),
            records_archived=data.get('records_archived', 0),
            records_purged=data.get('records_purged', 0),
            records_recovered=data.get('records_recovered', 0),
            duration_seconds=data.get('duration_seconds', 0.0),
            status=data.get('status', 'pending'),
            started_at=datetime.fromisoformat(data['started_at']) if data.get('started_at') else None,
            completed_at=datetime.fromisoformat(data['completed_at']) if data.get('completed_at') else None,
            error_message=data.get('error_message'),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.now(),
        )


@dataclass
class LifecycleResult:
    """Result of a lifecycle operation."""
    success: bool = False
    operation: str = ""
    records_affected: int = 0
    records_archived: int = 0
    records_purged: int = 0
    records_recovered: int = 0
    duration_seconds: float = 0.0
    error_message: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'success': self.success,
            'operation': self.operation,
            'records_affected': self.records_affected,
            'records_archived': self.records_archived,
            'records_purged': self.records_purged,
            'records_recovered': self.records_recovered,
            'duration_seconds': self.duration_seconds,
            'error_message': self.error_message,
            'details': self.details,
        }
```

---

## 🔧 Core Components

### 1. manager.py - LifecycleManager

Main orchestrator class for lifecycle operations:

```python
"""
Lifecycle Manager

Main Python class for orchestrating data lifecycle operations.
Coordinates retention, archival, purge, and GDPR compliance.

All implementation is in Python 3.10+
"""

import sqlite3
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

from brain.lifecycle.models import (
    RetentionPolicy,
    DeletedRecord,
    DataReset,
    ErasureRequest,
    LifecycleJob,
    LifecycleResult,
    ResetType,
    PurgeStatus,
)
from brain.lifecycle.retention import RetentionEngine
from brain.lifecycle.archive import ArchiveManager
from brain.lifecycle.purge import PurgeManager
from brain.lifecycle.gdpr import GDPRCompliance
from brain.lifecycle.recovery import RecoveryManager
from brain.lifecycle.scheduler import LifecycleScheduler


logger = logging.getLogger(__name__)


class LifecycleManager:
    """
    Main lifecycle orchestrator.
    
    Coordinates the full lifecycle pipeline:
    1. Evaluate retention policies
    2. Archive expired records (soft delete)
    3. Purge records past recovery window
    4. Handle GDPR requests
    
    Example:
        manager = LifecycleManager(
            db_path='tracking.db',
            backup_dir='backups'
        )
        
        # Apply retention policies
        result = manager.apply_retention_policies()
        
        # Archive specific entity
        manager.archive_entity('task', 'task-123')
        
        # Recover deleted entity
        manager.recover_entity('task', 'task-123')
    """
    
    def __init__(
        self,
        db_path: str = "tracking.db",
        backup_dir: str = "backups",
        db_connection: sqlite3.Connection = None
    ):
        """
        Initialize lifecycle manager.
        
        Args:
            db_path: Path to SQLite database file
            backup_dir: Directory for backups before destructive operations
            db_connection: Optional existing database connection
        """
        self.db_path = Path(db_path)
        self.backup_dir = Path(backup_dir)
        self.db = db_connection
        
        # Initialize components
        self.retention = RetentionEngine(db_connection=self.db)
        self.archive = ArchiveManager(db_connection=self.db)
        self.purge = PurgeManager(db_connection=self.db)
        self.gdpr = GDPRCompliance(db_connection=self.db, backup_dir=backup_dir)
        self.recovery = RecoveryManager(db_connection=self.db)
        self.scheduler = LifecycleScheduler(self)
        
        self._ensure_tables()
    
    def _ensure_tables(self) -> None:
        """Create lifecycle tables if they don't exist."""
        if self.db is None:
            self.db = sqlite3.connect(str(self.db_path))
        
        cursor = self.db.cursor()
        
        # Retention policies table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS retention_policies (
                id TEXT PRIMARY KEY,
                entity_type TEXT UNIQUE NOT NULL,
                archive_after_days INTEGER DEFAULT 365,
                delete_after_days INTEGER DEFAULT 730,
                enabled BOOLEAN DEFAULT 1,
                cascade_to TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Deleted records table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS deleted_records (
                id TEXT PRIMARY KEY,
                entity_type TEXT NOT NULL,
                entity_id TEXT NOT NULL,
                original_data TEXT NOT NULL,
                deleted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                recovery_until TIMESTAMP NOT NULL,
                purge_status TEXT DEFAULT 'recoverable',
                cascade_source TEXT,
                deletion_reason TEXT,
                deleted_by TEXT
            )
        ''')
        
        # Data resets table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS data_resets (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                reset_type TEXT NOT NULL,
                modules TEXT,
                backup_created BOOLEAN DEFAULT 1,
                backup_id TEXT,
                status TEXT DEFAULT 'pending',
                records_affected INTEGER DEFAULT 0,
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                error_message TEXT,
                confirmation_token TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Erasure requests table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS erasure_requests (
                id TEXT PRIMARY KEY,
                user_id TEXT NOT NULL,
                status TEXT DEFAULT 'pending',
                requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                verified_at TIMESTAMP,
                grace_period_until TIMESTAMP,
                executed_at TIMESTAMP,
                data_export_path TEXT,
                verification_token TEXT,
                cancellation_reason TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Lifecycle jobs table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS lifecycle_jobs (
                id TEXT PRIMARY KEY,
                job_type TEXT NOT NULL,
                entity_type TEXT,
                records_processed INTEGER DEFAULT 0,
                records_archived INTEGER DEFAULT 0,
                records_purged INTEGER DEFAULT 0,
                records_recovered INTEGER DEFAULT 0,
                duration_seconds REAL,
                status TEXT DEFAULT 'pending',
                started_at TIMESTAMP,
                completed_at TIMESTAMP,
                error_message TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_retention_entity ON retention_policies(entity_type)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_deleted_recovery ON deleted_records(recovery_until)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_deleted_status ON deleted_records(purge_status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_erasure_user ON erasure_requests(user_id)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_lifecycle_type ON lifecycle_jobs(job_type)')
        
        self.db.commit()
    
    def apply_retention_policies(self) -> LifecycleResult:
        """
        Apply all retention policies.
        
        Evaluates all entities against their retention policies
        and performs necessary archival or purge operations.
        
        Returns:
            LifecycleResult with operation summary
        """
        start_time = datetime.now()
        result = LifecycleResult(operation="apply_retention_policies")
        
        try:
            # Get all enabled policies
            policies = self.retention.get_all_policies(enabled_only=True)
            
            total_archived = 0
            total_purged = 0
            
            for policy in policies:
                # Archive expired records
                archived = self.archive.archive_expired(policy)
                total_archived += archived
                
                # Purge records past recovery
                purged = self.purge.purge_expired(policy)
                total_purged += purged
            
            result.success = True
            result.records_archived = total_archived
            result.records_purged = total_purged
            result.records_affected = total_archived + total_purged
            result.duration_seconds = (datetime.now() - start_time).total_seconds()
            
            logger.info(
                f"Retention policies applied: {total_archived} archived, "
                f"{total_purged} purged"
            )
            
        except Exception as e:
            result.success = False
            result.error_message = str(e)
            logger.error(f"Retention policy application failed: {e}")
        
        return result
    
    def archive_entity(
        self,
        entity_type: str,
        entity_id: str,
        reason: str = "user",
        user_id: str = ""
    ) -> DeletedRecord:
        """
        Archive a single entity (soft delete).
        
        Args:
            entity_type: Type of entity (habit, task, etc.)
            entity_id: ID of the entity
            reason: Reason for deletion
            user_id: User who initiated deletion
            
        Returns:
            DeletedRecord tracking the deletion
        """
        return self.archive.archive(entity_type, entity_id, reason, user_id)
    
    def recover_entity(
        self,
        entity_type: str,
        entity_id: str
    ) -> LifecycleResult:
        """
        Recover a soft-deleted entity.
        
        Args:
            entity_type: Type of entity
            entity_id: ID of the entity
            
        Returns:
            LifecycleResult with recovery status
        """
        return self.recovery.recover(entity_type, entity_id)
    
    def purge_entity(
        self,
        entity_type: str,
        entity_id: str
    ) -> LifecycleResult:
        """
        Permanently delete an entity.
        
        Args:
            entity_type: Type of entity
            entity_id: ID of the entity
            
        Returns:
            LifecycleResult with purge status
        """
        return self.purge.purge(entity_type, entity_id)
    
    def reset_module(
        self,
        module: str,
        create_backup: bool = True,
        user_id: str = ""
    ) -> DataReset:
        """
        Reset all data for a specific module.
        
        Args:
            module: Module to reset (habits, tasks, etc.)
            create_backup: Whether to create backup first
            user_id: User initiating reset
            
        Returns:
            DataReset tracking the operation
        """
        return self._execute_reset(
            reset_type=ResetType.MODULE,
            modules=[module],
            create_backup=create_backup,
            user_id=user_id
        )
    
    def full_reset(
        self,
        create_backup: bool = True,
        user_id: str = ""
    ) -> DataReset:
        """
        Delete all user data.
        
        Args:
            create_backup: Whether to create backup first
            user_id: User initiating reset
            
        Returns:
            DataReset tracking the operation
        """
        return self._execute_reset(
            reset_type=ResetType.FULL,
            modules=[],
            create_backup=create_backup,
            user_id=user_id
        )
    
    def _execute_reset(
        self,
        reset_type: ResetType,
        modules: List[str],
        create_backup: bool,
        user_id: str
    ) -> DataReset:
        """Execute a reset operation."""
        reset = DataReset(
            user_id=user_id,
            reset_type=reset_type,
            modules=modules,
            backup_created=create_backup,
            status="pending",
            started_at=datetime.now()
        )
        
        try:
            # Create backup if requested
            if create_backup:
                # Integration with BackupManager would go here
                reset.backup_id = f"backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            # Execute reset based on type
            if reset_type == ResetType.FULL:
                reset.records_affected = self._full_reset()
            elif reset_type == ResetType.MODULE:
                reset.records_affected = self._module_reset(modules)
            
            reset.status = "completed"
            reset.completed_at = datetime.now()
            
        except Exception as e:
            reset.status = "failed"
            reset.error_message = str(e)
            reset.completed_at = datetime.now()
        
        return reset
    
    def _full_reset(self) -> int:
        """Execute full data reset."""
        # Implementation would clear all tables
        pass
    
    def _module_reset(self, modules: List[str]) -> int:
        """Execute module-specific reset."""
        # Implementation would clear specific module tables
        pass
    
    def get_deleted_records(
        self,
        entity_type: str = None,
        recoverable_only: bool = True
    ) -> List[DeletedRecord]:
        """Get list of deleted records."""
        return self.recovery.list_deleted(entity_type, recoverable_only)
    
    def start_scheduler(self) -> None:
        """Start the automated lifecycle scheduler."""
        self.scheduler.start()
    
    def stop_scheduler(self) -> None:
        """Stop the automated lifecycle scheduler."""
        self.scheduler.shutdown()
```

### 2. retention.py - RetentionEngine

Per-entity retention policy engine:

```python
"""
Retention Engine

Per-entity retention policy implementation.
Different data types have different retention requirements.

All implementation is in Python 3.10+
"""

import sqlite3
from datetime import datetime, timedelta
from typing import List, Optional, Dict, Any
from dataclasses import dataclass
import logging

from brain.lifecycle.models import RetentionPolicy, RetentionAction


logger = logging.getLogger(__name__)


# Default retention policies per entity type
DEFAULT_POLICIES = {
    'habits': {
        'archive_after_days': None,   # Never archive
        'delete_after_days': None,    # Never delete
        'cascade_to': ['habit_logs', 'habit_streaks']
    },
    'habit_logs': {
        'archive_after_days': 365,    # Archive after 1 year
        'delete_after_days': 730,     # Delete after 2 years
        'cascade_to': []
    },
    'tasks': {
        'archive_after_days': 90,     # Archive after 90 days
        'delete_after_days': 365,     # Delete after 1 year
        'cascade_to': ['task_logs']
    },
    'transactions': {
        'archive_after_days': 2555,   # Archive after 7 years
        'delete_after_days': None,    # Never delete (financial compliance)
        'cascade_to': []
    },
    'health_entries': {
        'archive_after_days': 365,    # Archive after 1 year
        'delete_after_days': 1825,    # Delete after 5 years
        'cascade_to': []
    },
    'time_entries': {
        'archive_after_days': 180,    # Archive after 6 months
        'delete_after_days': 365,     # Delete after 1 year
        'cascade_to': []
    },
    'goals': {
        'archive_after_days': 365,    # Archive after 1 year
        'delete_after_days': 1825,    # Delete after 5 years
        'cascade_to': ['goal_progress']
    },
    'xp_logs': {
        'archive_after_days': 90,     # Archive after 90 days
        'delete_after_days': 365,     # Delete after 1 year
        'cascade_to': []
    },
    'audit_logs': {
        'archive_after_days': 365,    # Archive after 1 year
        'delete_after_days': 2555,    # Delete after 7 years
        'cascade_to': []
    },
}


class RetentionEngine:
    """
    Per-entity retention policy engine.
    
    Manages retention policies for different entity types.
    Provides evaluation of what action to take on records.
    
    Example:
        engine = RetentionEngine(db_connection)
        
        # Get action for a record
        action = engine.evaluate('habit_logs', record)
        
        if action == RetentionAction.ARCHIVE:
            archive_manager.archive(record)
    """
    
    def __init__(self, db_connection: sqlite3.Connection = None):
        """
        Initialize retention engine.
        
        Args:
            db_connection: SQLite database connection
        """
        self.db = db_connection
        self._policies: Dict[str, RetentionPolicy] = {}
        self._load_policies()
    
    def _load_policies(self) -> None:
        """Load policies from database or use defaults."""
        if self.db is None:
            # Use defaults only
            self._policies = self._create_default_policies()
            return
        
        cursor = self.db.cursor()
        cursor.execute("SELECT * FROM retention_policies WHERE enabled = 1")
        
        for row in cursor.fetchall():
            policy = RetentionPolicy.from_dict(dict(row))
            self._policies[policy.entity_type] = policy
        
        # Create defaults for missing policies
        for entity_type, config in DEFAULT_POLICIES.items():
            if entity_type not in self._policies:
                policy = RetentionPolicy(
                    entity_type=entity_type,
                    archive_after_days=config['archive_after_days'] or 365,
                    delete_after_days=config['delete_after_days'] or 730,
                    cascade_to=config['cascade_to']
                )
                self._policies[entity_type] = policy
    
    def _create_default_policies(self) -> Dict[str, RetentionPolicy]:
        """Create default policies from configuration."""
        policies = {}
        for entity_type, config in DEFAULT_POLICIES.items():
            policies[entity_type] = RetentionPolicy(
                entity_type=entity_type,
                archive_after_days=config['archive_after_days'] or 365,
                delete_after_days=config['delete_after_days'] or 730,
                cascade_to=config['cascade_to']
            )
        return policies
    
    def get_policy(self, entity_type: str) -> Optional[RetentionPolicy]:
        """
        Get retention policy for an entity type.
        
        Args:
            entity_type: Type of entity
            
        Returns:
            RetentionPolicy or None if not found
        """
        return self._policies.get(entity_type)
    
    def get_all_policies(self, enabled_only: bool = True) -> List[RetentionPolicy]:
        """
        Get all retention policies.
        
        Args:
            enabled_only: Only return enabled policies
            
        Returns:
            List of retention policies
        """
        policies = list(self._policies.values())
        if enabled_only:
            policies = [p for p in policies if p.enabled]
        return policies
    
    def evaluate(
        self,
        entity_type: str,
        record: Dict[str, Any]
    ) -> RetentionAction:
        """
        Evaluate what action to take on a record.
        
        Args:
            entity_type: Type of entity
            record: Record to evaluate (must have 'created_at' or 'updated_at')
            
        Returns:
            RetentionAction indicating what to do
        """
        policy = self.get_policy(entity_type)
        if not policy:
            return RetentionAction.KEEP
        
        # Get record date
        record_date = record.get('created_at') or record.get('updated_at')
        if not record_date:
            return RetentionAction.KEEP
        
        if isinstance(record_date, str):
            record_date = datetime.fromisoformat(record_date)
        
        age_days = (datetime.now() - record_date).days
        
        # Check delete threshold first (higher priority)
        if policy.delete_after_days and age_days >= policy.delete_after_days:
            return RetentionAction.PURGE
        
        # Check archive threshold
        if policy.archive_after_days and age_days >= policy.archive_after_days:
            return RetentionAction.ARCHIVE
        
        return RetentionAction.KEEP
    
    def get_records_to_archive(self, entity_type: str) -> List[Dict[str, Any]]:
        """
        Get all records past archive threshold.
        
        Args:
            entity_type: Type of entity
            
        Returns:
            List of records to archive
        """
        policy = self.get_policy(entity_type)
        if not policy or not policy.archive_after_days:
            return []
        
        threshold = datetime.now() - timedelta(days=policy.archive_after_days)
        
        if self.db is None:
            return []
        
        cursor = self.db.cursor()
        
        # Get table name from entity type
        table_name = self._get_table_name(entity_type)
        
        cursor.execute(
            f"SELECT * FROM {table_name} WHERE created_at < ?",
            (threshold.isoformat(),)
        )
        
        return [dict(row) for row in cursor.fetchall()]
    
    def get_records_to_purge(self, entity_type: str) -> List[Dict[str, Any]]:
        """
        Get all records past delete threshold.
        
        Args:
            entity_type: Type of entity
            
        Returns:
            List of records to purge
        """
        policy = self.get_policy(entity_type)
        if not policy or not policy.delete_after_days:
            return []
        
        threshold = datetime.now() - timedelta(days=policy.delete_after_days)
        
        if self.db is None:
            return []
        
        cursor = self.db.cursor()
        table_name = self._get_table_name(entity_type)
        
        cursor.execute(
            f"SELECT * FROM {table_name} WHERE created_at < ?",
            (threshold.isoformat(),)
        )
        
        return [dict(row) for row in cursor.fetchall()]
    
    def update_policy(self, policy: RetentionPolicy) -> None:
        """
        Update or create a retention policy.
        
        Args:
            policy: Policy to update
        """
        if self.db is None:
            self._policies[policy.entity_type] = policy
            return
        
        cursor = self.db.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO retention_policies
            (id, entity_type, archive_after_days, delete_after_days, enabled, cascade_to, updated_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (
            policy.id,
            policy.entity_type,
            policy.archive_after_days,
            policy.delete_after_days,
            policy.enabled,
            ','.join(policy.cascade_to) if policy.cascade_to else '',
            datetime.now().isoformat()
        ))
        
        self.db.commit()
        self._policies[policy.entity_type] = policy
    
    def _get_table_name(self, entity_type: str) -> str:
        """Convert entity type to table name."""
        # Handle special cases
        mapping = {
            'habit_logs': 'habit_logs',
            'task_logs': 'task_logs',
            'health_entries': 'health_entries',
            'time_entries': 'time_entries',
            'xp_logs': 'xp_logs',
            'audit_logs': 'audit_log',
        }
        return mapping.get(entity_type, entity_type)
```

### 3. archive.py - ArchiveManager

Soft delete with recovery window:

```python
"""
Archive Manager

Soft delete functionality with recovery window.
Records are archived (marked deleted) but recoverable for 30 days.

All implementation is in Python 3.10+
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Optional, List
import json
import logging

from brain.lifecycle.models import DeletedRecord, PurgeStatus


logger = logging.getLogger(__name__)


# Default recovery window in days
DEFAULT_RECOVERY_DAYS = 30


class ArchiveManager:
    """
    Manages soft deletion of records.
    
    Instead of immediate deletion, records are:
    1. Copied to deleted_records table
    2. Original is deleted from source table
    3. Record is recoverable for 30 days
    
    Example:
        manager = ArchiveManager(db_connection)
        
        # Archive a record
        deleted = manager.archive('tasks', 'task-123')
        
        # Check if recoverable
        if deleted.is_recoverable():
            print("Can be recovered")
    """
    
    def __init__(
        self,
        db_connection: sqlite3.Connection = None,
        recovery_days: int = DEFAULT_RECOVERY_DAYS
    ):
        """
        Initialize archive manager.
        
        Args:
            db_connection: SQLite database connection
            recovery_days: Number of days records are recoverable
        """
        self.db = db_connection
        self.recovery_days = recovery_days
    
    def archive(
        self,
        entity_type: str,
        entity_id: str,
        reason: str = "user",
        user_id: str = ""
    ) -> DeletedRecord:
        """
        Archive a record (soft delete).
        
        Args:
            entity_type: Type of entity
            entity_id: ID of entity
            reason: Reason for deletion
            user_id: User who initiated deletion
            
        Returns:
            DeletedRecord tracking the deletion
        """
        # Get original record
        original = self._get_record(entity_type, entity_id)
        if not original:
            raise ValueError(f"Record not found: {entity_type}/{entity_id}")
        
        # Create deleted record
        deleted = DeletedRecord(
            entity_type=entity_type,
            entity_id=entity_id,
            original_data=original,
            recovery_until=datetime.now() + timedelta(days=self.recovery_days),
            purge_status=PurgeStatus.RECOVERABLE,
            deletion_reason=reason,
            deleted_by=user_id
        )
        
        # Save to deleted_records
        self._save_deleted_record(deleted)
        
        # Delete from source table
        self._delete_from_source(entity_type, entity_id)
        
        logger.info(f"Archived {entity_type}/{entity_id}, recoverable until {deleted.recovery_until}")
        
        return deleted
    
    def archive_expired(self, policy) -> int:
        """
        Archive all records past retention threshold.
        
        Args:
            policy: RetentionPolicy to apply
            
        Returns:
            Number of records archived
        """
        # Would integrate with RetentionEngine to find expired records
        pass
    
    def _get_record(
        self,
        entity_type: str,
        entity_id: str
    ) -> Optional[dict]:
        """Get record from source table."""
        if self.db is None:
            return None
        
        table_name = self._get_table_name(entity_type)
        cursor = self.db.cursor()
        
        cursor.execute(
            f"SELECT * FROM {table_name} WHERE id = ?",
            (entity_id,)
        )
        
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def _save_deleted_record(self, deleted: DeletedRecord) -> None:
        """Save deleted record to tracking table."""
        if self.db is None:
            return
        
        cursor = self.db.cursor()
        cursor.execute('''
            INSERT INTO deleted_records
            (id, entity_type, entity_id, original_data, deleted_at, 
             recovery_until, purge_status, deletion_reason, deleted_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            deleted.id,
            deleted.entity_type,
            deleted.entity_id,
            json.dumps(deleted.original_data),
            deleted.deleted_at.isoformat(),
            deleted.recovery_until.isoformat(),
            deleted.purge_status.value,
            deleted.deletion_reason,
            deleted.deleted_by
        ))
        
        self.db.commit()
    
    def _delete_from_source(
        self,
        entity_type: str,
        entity_id: str
    ) -> None:
        """Delete record from source table."""
        if self.db is None:
            return
        
        table_name = self._get_table_name(entity_type)
        cursor = self.db.cursor()
        
        cursor.execute(
            f"DELETE FROM {table_name} WHERE id = ?",
            (entity_id,)
        )
        
        self.db.commit()
    
    def _get_table_name(self, entity_type: str) -> str:
        """Convert entity type to table name."""
        mapping = {
            'habits': 'habits',
            'tasks': 'tasks',
            'transactions': 'transactions',
            'health_entries': 'health_entries',
            'time_entries': 'time_entries',
            'goals': 'goals',
        }
        return mapping.get(entity_type, entity_type)
```

### 4. purge.py - PurgeManager

Permanent deletion with audit trail:

```python
"""
Purge Manager

Permanent deletion of records past recovery window.
Maintains audit trail of all purges.

All implementation is in Python 3.10+
"""

import sqlite3
from datetime import datetime
from typing import List, Optional
import logging

from brain.lifecycle.models import (
    DeletedRecord,
    PurgeStatus,
    LifecycleResult
)


logger = logging.getLogger(__name__)


class PurgeManager:
    """
    Manages permanent deletion of records.
    
    Only purges records that:
    1. Are in deleted_records table
    2. Have purge_status = 'pending_purge'
    3. Are past recovery_until date
    
    Example:
        manager = PurgeManager(db_connection)
        
        # Purge a specific record
        result = manager.purge('tasks', 'task-123')
        
        # Purge all expired records
        count = manager.purge_expired()
    """
    
    def __init__(self, db_connection: sqlite3.Connection = None):
        """
        Initialize purge manager.
        
        Args:
            db_connection: SQLite database connection
        """
        self.db = db_connection
    
    def purge(
        self,
        entity_type: str,
        entity_id: str
    ) -> LifecycleResult:
        """
        Permanently delete a record.
        
        Args:
            entity_type: Type of entity
            entity_id: ID of entity
            
        Returns:
            LifecycleResult with purge status
        """
        result = LifecycleResult(operation="purge")
        
        try:
            # Get deleted record
            deleted = self._get_deleted_record(entity_type, entity_id)
            
            if not deleted:
                result.error_message = "Record not found in deleted records"
                return result
            
            if not self._can_purge(deleted):
                result.error_message = "Record cannot be purged (still in recovery)"
                return result
            
            # Delete from deleted_records
            self._delete_purged_record(deleted.id)
            
            # Update status
            result.success = True
            result.records_purged = 1
            result.records_affected = 1
            
            logger.info(f"Purged {entity_type}/{entity_id}")
            
        except Exception as e:
            result.error_message = str(e)
            logger.error(f"Purge failed: {e}")
        
        return result
    
    def purge_expired(self, policy=None) -> int:
        """
        Purge all records past recovery window.
        
        Args:
            policy: Optional retention policy to filter by entity
            
        Returns:
            Number of records purged
        """
        if self.db is None:
            return 0
        
        cursor = self.db.cursor()
        
        # Find expired records
        cursor.execute('''
            SELECT id, entity_type, entity_id
            FROM deleted_records
            WHERE purge_status = 'recoverable'
            AND recovery_until < ?
        ''', (datetime.now().isoformat(),))
        
        expired = cursor.fetchall()
        purged_count = 0
        
        for row in expired:
            deleted_id = row[0]
            
            # Delete the record
            cursor.execute(
                "DELETE FROM deleted_records WHERE id = ?",
                (deleted_id,)
            )
            
            purged_count += 1
        
        self.db.commit()
        
        if purged_count > 0:
            logger.info(f"Purged {purged_count} expired records")
        
        return purged_count
    
    def _get_deleted_record(
        self,
        entity_type: str,
        entity_id: str
    ) -> Optional[DeletedRecord]:
        """Get deleted record from tracking table."""
        if self.db is None:
            return None
        
        cursor = self.db.cursor()
        cursor.execute('''
            SELECT * FROM deleted_records
            WHERE entity_type = ? AND entity_id = ?
        ''', (entity_type, entity_id))
        
        row = cursor.fetchone()
        if row:
            return DeletedRecord.from_dict(dict(row))
        return None
    
    def _can_purge(self, deleted: DeletedRecord) -> bool:
        """Check if record can be purged."""
        return (
            deleted.purge_status in (PurgeStatus.RECOVERABLE, PurgeStatus.PENDING_PURGE)
            and datetime.now() >= deleted.recovery_until
        )
    
    def _delete_purged_record(self, deleted_id: str) -> None:
        """Delete record from deleted_records table."""
        if self.db is None:
            return
        
        cursor = self.db.cursor()
        cursor.execute(
            "DELETE FROM deleted_records WHERE id = ?",
            (deleted_id,)
        )
        self.db.commit()
```

### 5. gdpr.py - GDPRCompliance

GDPR compliance utilities:

```python
"""
GDPR Compliance

Implementation of GDPR rights:
- Article 15: Right to access
- Article 17: Right to erasure
- Article 20: Right to portability

All implementation is in Python 3.10+
"""

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Dict, Any, List
import json
import logging
import uuid

from brain.lifecycle.models import ErasureRequest, ErasureStatus


logger = logging.getLogger(__name__)


class GDPRCompliance:
    """
    GDPR compliance utilities.
    
    Implements the three main data rights:
    
    1. Right to Access (Article 15):
       - Export all data associated with user
       
    2. Right to Erasure (Article 17):
       - Delete all user data
       - 30-day grace period before execution
       
    3. Right to Portability (Article 20):
       - Export in machine-readable format
       
    Example:
        gdpr = GDPRCompliance(db_connection, backup_dir)
        
        # Request erasure
        request = gdpr.request_erasure(user_id)
        
        # Execute after grace period
        result = gdpr.execute_erasure(request.id)
    """
    
    def __init__(
        self,
        db_connection: sqlite3.Connection = None,
        backup_dir: str = "backups"
    ):
        """
        Initialize GDPR compliance.
        
        Args:
            db_connection: SQLite database connection
            backup_dir: Directory for data exports
        """
        self.db = db_connection
        self.backup_dir = Path(backup_dir)
        self.grace_period_days = 30
    
    # =====================
    # Article 15: Right to Access
    # =====================
    
    def export_user_data(
        self,
        user_id: str,
        format: str = 'json'
    ) -> Path:
        """
        Export all data associated with user (Article 15).
        
        Args:
            user_id: User ID
            format: Export format ('json', 'csv')
            
        Returns:
            Path to exported data file
        """
        data = self._collect_user_data(user_id)
        
        # Create export file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        export_path = self.backup_dir / f"gdpr_export_{user_id}_{timestamp}.json"
        
        with open(export_path, 'w') as f:
            json.dump(data, f, indent=2, default=str)
        
        logger.info(f"Exported user data for {user_id} to {export_path}")
        
        return export_path
    
    def _collect_user_data(self, user_id: str) -> Dict[str, Any]:
        """Collect all data associated with user."""
        if self.db is None:
            return {}
        
        data = {
            'user_id': user_id,
            'exported_at': datetime.now().isoformat(),
            'modules': {}
        }
        
        cursor = self.db.cursor()
        
        # Collect from each table
        tables = [
            'habits', 'tasks', 'goals', 'transactions',
            'health_entries', 'time_entries', 'xp_logs'
        ]
        
        for table in tables:
            try:
                cursor.execute(f"SELECT * FROM {table}")
                rows = cursor.fetchall()
                data['modules'][table] = [dict(row) for row in rows]
            except Exception:
                data['modules'][table] = []
        
        return data
    
    # =====================
    # Article 17: Right to Erasure
    # =====================
    
    def request_erasure(
        self,
        user_id: str
    ) -> ErasureRequest:
        """
        Request data erasure (Article 17).
        
        Creates a request that enters a 30-day grace period
        before execution.
        
        Args:
            user_id: User ID
            
        Returns:
            ErasureRequest with verification token
        """
        request = ErasureRequest(
            user_id=user_id,
            status=ErasureStatus.PENDING,
            verification_token=str(uuid.uuid4())
        )
        
        # Save request
        self._save_erasure_request(request)
        
        logger.info(f"Erasure request created for {user_id}")
        
        return request
    
    def verify_erasure_request(
        self,
        request_id: str,
        token: str
    ) -> bool:
        """
        Verify erasure request with token.
        
        Args:
            request_id: Request ID
            token: Verification token
            
        Returns:
            True if verified successfully
        """
        request = self._get_erasure_request(request_id)
        
        if not request:
            return False
        
        if request.verification_token != token:
            return False
        
        # Update status
        request.status = ErasureStatus.GRACE_PERIOD
        request.verified_at = datetime.now()
        request.grace_period_until = datetime.now() + timedelta(days=self.grace_period_days)
        
        self._update_erasure_request(request)
        
        logger.info(f"Erasure request {request_id} verified, grace period started")
        
        return True
    
    def execute_erasure(
        self,
        request_id: str
    ) -> Dict[str, Any]:
        """
        Execute erasure request.
        
        Can only be executed after grace period.
        
        Args:
            request_id: Request ID
            
        Returns:
            Result of erasure operation
        """
        request = self._get_erasure_request(request_id)
        
        if not request:
            return {'success': False, 'error': 'Request not found'}
        
        if not request.can_execute():
            return {'success': False, 'error': 'Cannot execute (still in grace period)'}
        
        # Create backup before erasure
        export_path = self.export_user_data(request.user_id)
        request.data_export_path = str(export_path)
        
        # Delete all user data
        deleted_count = self._delete_all_user_data(request.user_id)
        
        # Update request
        request.status = ErasureStatus.EXECUTED
        request.executed_at = datetime.now()
        self._update_erasure_request(request)
        
        logger.info(f"Erasure executed for {request.user_id}, {deleted_count} records deleted")
        
        return {
            'success': True,
            'records_deleted': deleted_count,
            'backup_path': str(export_path)
        }
    
    def cancel_erasure_request(
        self,
        request_id: str,
        reason: str = ""
    ) -> bool:
        """
        Cancel an erasure request.
        
        Can only cancel before execution.
        
        Args:
            request_id: Request ID
            reason: Cancellation reason
            
        Returns:
            True if cancelled successfully
        """
        request = self._get_erasure_request(request_id)
        
        if not request:
            return False
        
        if request.status == ErasureStatus.EXECUTED:
            return False
        
        request.status = ErasureStatus.CANCELLED
        request.cancellation_reason = reason
        
        self._update_erasure_request(request)
        
        logger.info(f"Erasure request {request_id} cancelled")
        
        return True
    
    def _delete_all_user_data(self, user_id: str) -> int:
        """Delete all data for a user."""
        if self.db is None:
            return 0
        
        cursor = self.db.cursor()
        total_deleted = 0
        
        tables = [
            'habits', 'tasks', 'goals', 'transactions',
            'health_entries', 'time_entries', 'xp_logs',
            'achievements', 'user_data'
        ]
        
        for table in tables:
            cursor.execute(f"DELETE FROM {table}")
            total_deleted += cursor.rowcount
        
        self.db.commit()
        
        return total_deleted
    
    # =====================
    # Article 20: Right to Portability
    # =====================
    
    def export_portable(
        self,
        user_id: str,
        format: str = 'json'
    ) -> Path:
        """
        Export data in portable format (Article 20).
        
        Args:
            user_id: User ID
            format: Export format
            
        Returns:
            Path to portable export
        """
        return self.export_user_data(user_id, format)
    
    # =====================
    # Helper Methods
    # =====================
    
    def _save_erasure_request(self, request: ErasureRequest) -> None:
        """Save erasure request to database."""
        if self.db is None:
            return
        
        cursor = self.db.cursor()
        cursor.execute('''
            INSERT INTO erasure_requests
            (id, user_id, status, requested_at, verification_token)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            request.id,
            request.user_id,
            request.status.value,
            request.requested_at.isoformat(),
            request.verification_token
        ))
        
        self.db.commit()
    
    def _get_erasure_request(self, request_id: str) -> Optional[ErasureRequest]:
        """Get erasure request by ID."""
        if self.db is None:
            return None
        
        cursor = self.db.cursor()
        cursor.execute(
            "SELECT * FROM erasure_requests WHERE id = ?",
            (request_id,)
        )
        
        row = cursor.fetchone()
        if row:
            return ErasureRequest.from_dict(dict(row))
        return None
    
    def _update_erasure_request(self, request: ErasureRequest) -> None:
        """Update erasure request in database."""
        if self.db is None:
            return
        
        cursor = self.db.cursor()
        cursor.execute('''
            UPDATE erasure_requests SET
                status = ?,
                verified_at = ?,
                grace_period_until = ?,
                executed_at = ?,
                data_export_path = ?,
                cancellation_reason = ?
            WHERE id = ?
        ''', (
            request.status.value,
            request.verified_at.isoformat() if request.verified_at else None,
            request.grace_period_until.isoformat() if request.grace_period_until else None,
            request.executed_at.isoformat() if request.executed_at else None,
            request.data_export_path,
            request.cancellation_reason,
            request.id
        ))
        
        self.db.commit()
```

---

## 🖥️ Streamlit UI

### tracking_app/pages/data_lifecycle.py

```python
"""
Data Lifecycle Management Page

Streamlit UI for lifecycle management.
Provides retention policy configuration, recovery, and GDPR compliance.

All implementation is in Python 3.10+
"""

import streamlit as st
from pathlib import Path
from datetime import datetime, timedelta
import logging

from brain.lifecycle.manager import LifecycleManager
from brain.lifecycle.models import RetentionPolicy, ResetType


logger = logging.getLogger(__name__)


def init_session_state():
    """Initialize session state variables."""
    if 'lifecycle_manager' not in st.session_state:
        st.session_state.lifecycle_manager = None
    if 'show_reset_confirm' not in st.session_state:
        st.session_state.show_reset_confirm = False
    if 'show_gdpr_confirm' not in st.session_state:
        st.session_state.show_gdpr_confirm = False
    if 'pending_reset' not in st.session_state:
        st.session_state.pending_reset = None


def get_lifecycle_manager() -> LifecycleManager:
    """Get or create lifecycle manager."""
    if st.session_state.lifecycle_manager is None:
        st.session_state.lifecycle_manager = LifecycleManager(
            db_path="tracking.db",
            backup_dir="backups"
        )
    return st.session_state.lifecycle_manager


def render_status_metrics(manager: LifecycleManager):
    """Render lifecycle status metrics."""
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        deleted_records = manager.get_deleted_records(recoverable_only=True)
        st.metric("Recoverable", len(deleted_records))
    
    with col2:
        policies = manager.retention.get_all_policies(enabled_only=True)
        st.metric("Active Policies", len(policies))
    
    with col3:
        # Storage metrics would go here
        st.metric("Storage Saved", "0 MB")
    
    with col4:
        status = "🟢 Active" if True else "🔴 Inactive"
        st.metric("Scheduler", status)


def render_retention_policies(manager: LifecycleManager):
    """Render retention policy configuration."""
    st.subheader("Retention Policies")
    
    policies = manager.retention.get_all_policies(enabled_only=False)
    
    # Display as editable table
    for policy in policies:
        with st.expander(f"**{policy.entity_type}**", expanded=False):
            col1, col2, col3 = st.columns(3)
            
            with col1:
                archive_days = st.number_input(
                    "Archive after (days)",
                    value=policy.archive_after_days,
                    key=f"archive_{policy.id}"
                )
            
            with col2:
                delete_days = st.number_input(
                    "Delete after (days)",
                    value=policy.delete_after_days or 0,
                    key=f"delete_{policy.id}"
                )
            
            with col3:
                enabled = st.checkbox(
                    "Enabled",
                    value=policy.enabled,
                    key=f"enabled_{policy.id}"
                )
            
            if st.button("Save", key=f"save_{policy.id}"):
                policy.archive_after_days = archive_days
                policy.delete_after_days = delete_days if delete_days > 0 else None
                policy.enabled = enabled
                manager.retention.update_policy(policy)
                st.success("Policy updated!")
                st.rerun()


def render_deleted_records(manager: LifecycleManager):
    """Render list of deleted records with recovery option."""
    st.subheader("Deleted Records (Recovery Window)")
    
    records = manager.get_deleted_records(recoverable_only=True)
    
    if not records:
        st.info("No deleted records in recovery window.")
        return
    
    for record in records:
        with st.container():
            col1, col2, col3, col4 = st.columns([3, 2, 2, 2])
            
            with col1:
                st.write(f"**{record.entity_type}** / {record.entity_id[:8]}")
                st.caption(f"Deleted: {record.deleted_at.strftime('%Y-%m-%d %H:%M')}")
            
            with col2:
                days_left = (record.recovery_until - datetime.now()).days
                st.write(f"⏱️ {days_left} days left")
            
            with col3:
                st.write(f"📝 {record.deletion_reason}")
            
            with col4:
                if st.button("Recover", key=f"recover_{record.id}"):
                    result = manager.recover_entity(
                        record.entity_type,
                        record.entity_id
                    )
                    if result.success:
                        st.success("Record recovered!")
                        st.rerun()
                    else:
                        st.error(f"Recovery failed: {result.error_message}")
        
        st.divider()


def render_reset_options(manager: LifecycleManager):
    """Render data reset options."""
    st.subheader("Data Reset")
    st.warning("⚠️ These operations are destructive. A backup will be created automatically.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.write("**Module Reset**")
        module = st.selectbox(
            "Select Module",
            options=['habits', 'tasks', 'goals', 'transactions', 'health_entries', 'time_entries']
        )
        
        if st.button("Reset Module", type="secondary"):
            st.session_state.show_reset_confirm = True
            st.session_state.pending_reset = {
                'type': 'module',
                'module': module
            }
            st.rerun()
    
    with col2:
        st.write("**Full Reset**")
        st.write("Delete ALL user data.")
        
        if st.button("Full Reset", type="primary"):
            st.session_state.show_reset_confirm = True
            st.session_state.pending_reset = {
                'type': 'full'
            }
            st.rerun()
    
    # Confirmation dialog
    if st.session_state.show_reset_confirm:
        render_reset_confirmation(manager)


def render_reset_confirmation(manager: LifecycleManager):
    """Render reset confirmation dialog."""
    st.warning("⚠️ **WARNING: Destructive Operation**")
    
    reset_info = st.session_state.pending_reset
    
    if reset_info['type'] == 'module':
        st.write(f"This will delete all data in the **{reset_info['module']}** module.")
    else:
        st.write("This will delete **ALL USER DATA**.")
    
    st.write("A backup will be created before the reset.")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("✅ Confirm Reset", type="primary"):
            if reset_info['type'] == 'module':
                result = manager.reset_module(
                    reset_info['module'],
                    create_backup=True,
                    user_id="default"
                )
            else:
                result = manager.full_reset(
                    create_backup=True,
                    user_id="default"
                )
            
            st.session_state.show_reset_confirm = False
            st.session_state.pending_reset = None
            
            if result.status == "completed":
                st.success(f"Reset complete! {result.records_affected} records affected.")
            else:
                st.error(f"Reset failed: {result.error_message}")
            
            st.rerun()
    
    with col2:
        if st.button("❌ Cancel"):
            st.session_state.show_reset_confirm = False
            st.session_state.pending_reset = None
            st.rerun()


def render_gdpr_section(manager: LifecycleManager):
    """Render GDPR compliance section."""
    st.subheader("GDPR Compliance")
    
    tab1, tab2, tab3 = st.tabs(["Right to Access", "Right to Erasure", "Right to Portability"])
    
    with tab1:
        st.write("**Article 15: Right to Access**")
        st.write("Export all data associated with your account.")
        
        if st.button("Export My Data"):
            with st.spinner("Exporting data..."):
                path = manager.gdpr.export_user_data("default")
            st.success(f"Data exported to: {path}")
    
    with tab2:
        st.write("**Article 17: Right to Erasure**")
        st.write("Request deletion of all your data.")
        st.warning("⚠️ This action has a 30-day grace period before execution.")
        
        if st.button("Request Data Erasure"):
            request = manager.gdpr.request_erasure("default")
            st.info(f"Erasure request created. Verification token: {request.verification_token}")
    
    with tab3:
        st.write("**Article 20: Right to Portability**")
        st.write("Export your data in a machine-readable format.")
        
        format_choice = st.selectbox("Format", ["JSON", "CSV"])
        
        if st.button("Export Portable Data"):
            with st.spinner("Exporting..."):
                path = manager.gdpr.export_portable("default", format_choice.lower())
            st.success(f"Data exported to: {path}")


def render_scheduler_section(manager: LifecycleManager):
    """Render automated scheduler configuration."""
    st.subheader("Automated Lifecycle Jobs")
    
    st.write("Configure automatic archival and cleanup:")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        archive_enabled = st.checkbox("Daily Archive", value=True)
        archive_time = st.time_input("Archive Time", value=datetime.now().replace(hour=3, minute=0))
    
    with col2:
        purge_enabled = st.checkbox("Daily Purge", value=True)
        purge_time = st.time_input("Purge Time", value=datetime.now().replace(hour=4, minute=0))
    
    with col3:
        cleanup_enabled = st.checkbox("Recovery Cleanup", value=True)
        cleanup_time = st.time_input("Cleanup Time", value=datetime.now().replace(hour=5, minute=0))
    
    st.caption("Last run: Never")


def main():
    """Main page entry point."""
    st.title("🗃️ Data Lifecycle Management")
    
    init_session_state()
    
    manager = get_lifecycle_manager()
    
    # Render sections
    render_status_metrics(manager)
    
    st.divider()
    
    # Tabs for organization
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "Policies",
        "Recovery",
        "Reset",
        "GDPR",
        "Scheduler"
    ])
    
    with tab1:
        render_retention_policies(manager)
    
    with tab2:
        render_deleted_records(manager)
    
    with tab3:
        render_reset_options(manager)
    
    with tab4:
        render_gdpr_section(manager)
    
    with tab5:
        render_scheduler_section(manager)


if __name__ == "__main__":
    main()
```

---

## 🗄️ Database Schema

Add to SQLite database:

```sql
-- Retention policies per entity type
CREATE TABLE IF NOT EXISTS retention_policies (
    id TEXT PRIMARY KEY,
    entity_type TEXT UNIQUE NOT NULL,
    archive_after_days INTEGER DEFAULT 365,
    delete_after_days INTEGER DEFAULT 730,
    enabled BOOLEAN DEFAULT 1,
    cascade_to TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Soft-deleted records (recovery window)
CREATE TABLE IF NOT EXISTS deleted_records (
    id TEXT PRIMARY KEY,
    entity_type TEXT NOT NULL,
    entity_id TEXT NOT NULL,
    original_data TEXT NOT NULL,
    deleted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    recovery_until TIMESTAMP NOT NULL,
    purge_status TEXT DEFAULT 'recoverable',
    cascade_source TEXT,
    deletion_reason TEXT,
    deleted_by TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Data reset operations
CREATE TABLE IF NOT EXISTS data_resets (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    reset_type TEXT NOT NULL,
    modules TEXT,
    backup_created BOOLEAN DEFAULT 1,
    backup_id TEXT,
    status TEXT DEFAULT 'pending',
    records_affected INTEGER DEFAULT 0,
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT,
    confirmation_token TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- GDPR erasure requests
CREATE TABLE IF NOT EXISTS erasure_requests (
    id TEXT PRIMARY KEY,
    user_id TEXT NOT NULL,
    status TEXT DEFAULT 'pending',
    requested_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    verified_at TIMESTAMP,
    grace_period_until TIMESTAMP,
    executed_at TIMESTAMP,
    data_export_path TEXT,
    verification_token TEXT,
    cancellation_reason TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Lifecycle job history
CREATE TABLE IF NOT EXISTS lifecycle_jobs (
    id TEXT PRIMARY KEY,
    job_type TEXT NOT NULL,
    entity_type TEXT,
    records_processed INTEGER DEFAULT 0,
    records_archived INTEGER DEFAULT 0,
    records_purged INTEGER DEFAULT 0,
    records_recovered INTEGER DEFAULT 0,
    duration_seconds REAL,
    status TEXT DEFAULT 'pending',
    started_at TIMESTAMP,
    completed_at TIMESTAMP,
    error_message TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX IF NOT EXISTS idx_retention_entity ON retention_policies(entity_type);
CREATE INDEX IF NOT EXISTS idx_deleted_recovery ON deleted_records(recovery_until);
CREATE INDEX IF NOT EXISTS idx_deleted_status ON deleted_records(purge_status);
CREATE INDEX IF NOT EXISTS idx_deleted_entity ON deleted_records(entity_type, entity_id);
CREATE INDEX IF NOT EXISTS idx_erasure_user ON erasure_requests(user_id);
CREATE INDEX IF NOT EXISTS idx_lifecycle_type ON lifecycle_jobs(job_type);
```

---

## 📋 Implementation Checklist

### Week 1: Core Components (Days 1-3)

| Day | Task | File | Status |
|-----|------|------|--------|
| 1 | Create models.py with all dataclasses | `brain/lifecycle/models.py` | [ ] |
| 1 | Create __init__.py with exports | `brain/lifecycle/__init__.py` | [ ] |
| 2 | Implement RetentionEngine | `brain/lifecycle/retention.py` | [ ] |
| 2 | Implement ArchiveManager | `brain/lifecycle/archive.py` | [ ] |
| 3 | Implement PurgeManager | `brain/lifecycle/purge.py` | [ ] |
| 3 | Implement LifecycleScheduler | `brain/lifecycle/scheduler.py` | [ ] |

### Week 1: Manager & GDPR (Days 4-5)

| Day | Task | File | Status |
|-----|------|------|--------|
| 4 | Implement LifecycleManager | `brain/lifecycle/manager.py` | [ ] |
| 4 | Implement GDPRCompliance | `brain/lifecycle/gdpr.py` | [ ] |
| 5 | Implement RecoveryManager | `brain/lifecycle/recovery.py` | [ ] |
| 5 | Create database schema migration | `tracking_app/migration.py` | [ ] |

### Week 2: UI & Testing (Days 1-2)

| Day | Task | File | Status |
|-----|------|------|--------|
| 1 | Implement Streamlit UI | `tracking_app/pages/data_lifecycle.py` | [ ] |
| 2 | Write unit tests | `tests/test_lifecycle.py` | [ ] |
| 2 | Write integration tests | `tests/test_lifecycle.py` | [ ] |

---

## 🔗 Dependencies

| Package | Version | Purpose |
|---------|---------|---------|
| apscheduler | >=3.10.0 | Job scheduling |
| pytest | >=7.0.0 | Testing |

All other functionality uses Python standard library (sqlite3, json, datetime, pathlib).

---

## 📚 Cross-References

| Document | Content |
|----------|---------|
| [PHASE_5_DATA_MANAGEMENT.md](PHASE_5_DATA_MANAGEMENT.md) | Phase 5 overview |
| [PHASE_5.3_BACKUP_RESTORE.md](PHASE_5.3_BACKUP_RESTORE.md) | Backup system |
| [PROJECT_RULES.md](../PROJECT_RULES.md) | Development guidelines |
| [brain/README.md](../brain/README.md) | Brain architecture |

---

*Last updated: February 19, 2026*
*Status: 📋 Ready for Implementation*