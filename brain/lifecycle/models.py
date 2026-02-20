"""
Data Lifecycle Models

Python dataclasses for lifecycle management.
Implements retention policies, soft delete, GDPR compliance.

All implementation is in Python 3.10+
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
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
    
    Attributes:
        id: Unique identifier
        entity_type: Type of entity (habit_log, task, transaction, etc.)
        archive_after_days: Days before soft delete
        delete_after_days: Days before permanent deletion (None = never)
        enabled: Whether policy is active
        cascade_to: Related entities to cascade deletion to
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    entity_type: str = ""
    archive_after_days: int = 365
    delete_after_days: int = 730
    enabled: bool = True
    cascade_to: List[str] = field(default_factory=list)
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
    
    Attributes:
        id: Unique identifier
        entity_type: Type of entity
        entity_id: Original record ID
        original_data: JSON of original record
        deleted_at: When record was deleted
        recovery_until: When record can be permanently purged
        purge_status: Current status
        cascade_source: ID of parent deletion if cascade
        deletion_reason: Reason for deletion
        deleted_by: User who initiated deletion
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    entity_type: str = ""
    entity_id: str = ""
    original_data: Dict[str, Any] = field(default_factory=dict)
    deleted_at: datetime = field(default_factory=datetime.now)
    recovery_until: datetime = None
    purge_status: PurgeStatus = PurgeStatus.RECOVERABLE
    cascade_source: Optional[str] = None
    deletion_reason: str = ""
    deleted_by: str = ""
    
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
    
    Attributes:
        id: Unique identifier
        user_id: User who requested reset
        reset_type: Type of reset
        modules: Modules to reset (for module-specific reset)
        backup_created: Whether backup was created
        backup_id: Reference to backup job
        status: Current status
        records_affected: Number of records affected
        confirmation_token: For two-step confirmation
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    reset_type: ResetType = ResetType.FULL
    modules: List[str] = field(default_factory=list)
    backup_created: bool = False
    backup_id: Optional[str] = None
    status: str = "pending"
    records_affected: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
    confirmation_token: Optional[str] = None
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
    
    Attributes:
        id: Unique identifier
        user_id: User requesting erasure
        status: Current status
        requested_at: When request was made
        verified_at: When user identity was verified
        grace_period_until: End of 30-day grace period
        executed_at: When erasure was executed
        data_export_path: Backup before erasure
        verification_token: Email verification token
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    status: ErasureStatus = ErasureStatus.PENDING
    requested_at: datetime = field(default_factory=datetime.now)
    verified_at: Optional[datetime] = None
    grace_period_until: Optional[datetime] = None
    executed_at: Optional[datetime] = None
    data_export_path: Optional[str] = None
    verification_token: Optional[str] = None
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
    
    Attributes:
        id: Unique identifier
        job_type: Type of job (archive, purge, recovery_cleanup)
        entity_type: Specific entity or all
        records_processed: Total records processed
        records_archived: Records archived
        records_purged: Records purged
        records_recovered: Records recovered
        duration_seconds: Job duration
        status: Current status
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    job_type: str = ""
    entity_type: Optional[str] = None
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