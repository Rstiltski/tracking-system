"""
Data Export Models

Python dataclasses for export request tracking and history.
Uses Python standard library: json, csv, sqlite3, zipfile

All implementation is in Python 3.10+
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from enum import Enum
import uuid
import json


class ExportFormat(Enum):
    """
    Supported export formats.
    
    These are data formats, not programming languages.
    All serialization is done in Python using stdlib modules.
    """
    JSON = "json"           # JavaScript Object Notation (data interchange format)
    CSV = "csv"             # Comma-Separated Values (tabular data format)
    SQLITE = "sqlite"       # SQLite database dump (binary format)


class ExportStatus(Enum):
    """Export job status."""
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    EXPIRED = "expired"


@dataclass
class ExportRequest:
    """
    Represents a data export request.
    
    Python implementation using dataclasses for clean data modeling.
    All serialization/deserialization handled by Python standard library.
    
    Attributes:
        id: Unique identifier
        user_id: User who requested export
        format: Export format (json, csv, sqlite)
        modules: Modules to export (empty = all)
        include_archived: Include soft-deleted records
        compression: Use ZIP compression
        status: Current status
        created_at: When request was created
        completed_at: When export completed
        file_path: Path to exported file
        download_token: Token for secure download
        expires_at: When download link expires
        error_message: Error if failed
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    format: ExportFormat = ExportFormat.JSON
    modules: List[str] = field(default_factory=list)  # Empty = all modules
    include_archived: bool = False
    compression: bool = True  # Use zipfile for compression
    status: ExportStatus = ExportStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    file_path: Optional[str] = None
    download_token: Optional[str] = None
    expires_at: Optional[datetime] = None
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for SQLite storage."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'format': self.format.value,
            'modules': ','.join(self.modules) if self.modules else '',
            'include_archived': self.include_archived,
            'compression': self.compression,
            'status': self.status.value,
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'file_path': self.file_path,
            'download_token': self.download_token,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'error_message': self.error_message,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExportRequest':
        """Create instance from SQLite row dictionary."""
        modules = data.get('modules', '')
        return cls(
            id=data.get('id', str(uuid.uuid4())),
            user_id=data.get('user_id', ''),
            format=ExportFormat(data.get('format', 'json')),
            modules=modules.split(',') if modules else [],
            include_archived=bool(data.get('include_archived', 0)),
            compression=bool(data.get('compression', 1)),
            status=ExportStatus(data.get('status', 'pending')),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.now(),
            completed_at=datetime.fromisoformat(data['completed_at']) if data.get('completed_at') else None,
            file_path=data.get('file_path'),
            download_token=data.get('download_token'),
            expires_at=datetime.fromisoformat(data['expires_at']) if data.get('expires_at') else None,
            error_message=data.get('error_message'),
        )

    def is_expired(self) -> bool:
        """Check if export has expired."""
        if self.expires_at is None:
            return False
        return datetime.now() > self.expires_at

    def is_ready(self) -> bool:
        """Check if export is ready for download."""
        return (
            self.status == ExportStatus.COMPLETED and
            self.file_path is not None and
            not self.is_expired()
        )


@dataclass
class ExportHistory:
    """
    Track export history for analytics.
    
    Maintains a record of all exports for:
    - Audit purposes
    - Usage analytics
    - Storage management
    
    Attributes:
        id: Unique identifier
        user_id: User who performed export
        export_id: Reference to export request
        format: Export format used
        modules_exported: Comma-separated list of modules
        record_count: Total records exported
        file_size_bytes: Size of exported file
        duration_seconds: Time taken for export
        status: Final status
        created_at: When record was created
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    export_id: str = ""
    format: str = ""
    modules_exported: str = ""
    record_count: int = 0
    file_size_bytes: int = 0
    duration_seconds: float = 0.0
    status: str = ""
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for SQLite storage."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'export_id': self.export_id,
            'format': self.format,
            'modules_exported': self.modules_exported,
            'record_count': self.record_count,
            'file_size_bytes': self.file_size_bytes,
            'duration_seconds': self.duration_seconds,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ExportHistory':
        """Create instance from SQLite row dictionary."""
        return cls(
            id=data.get('id', str(uuid.uuid4())),
            user_id=data.get('user_id', ''),
            export_id=data.get('export_id', ''),
            format=data.get('format', ''),
            modules_exported=data.get('modules_exported', ''),
            record_count=data.get('record_count', 0),
            file_size_bytes=data.get('file_size_bytes', 0),
            duration_seconds=data.get('duration_seconds', 0.0),
            status=data.get('status', ''),
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.now(),
        )


@dataclass
class ExportModule:
    """
    Defines an exportable module.
    
    Each module maps to database tables and defines
    what data is included in the export.
    
    Attributes:
        name: Module identifier
        display_name: Human-readable name
        tables: List of database tables
        description: What this module contains
    """
    name: str = ""
    display_name: str = ""
    tables: List[str] = field(default_factory=list)
    description: str = ""

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'name': self.name,
            'display_name': self.display_name,
            'tables': self.tables,
            'description': self.description,
        }


# Define all exportable modules
EXPORT_MODULES: Dict[str, ExportModule] = {
    'habits': ExportModule(
        name='habits',
        display_name='Habits',
        tables=['habits', 'habit_logs', 'streaks'],
        description='Habit definitions, completion logs, and streak data'
    ),
    'tasks': ExportModule(
        name='tasks',
        display_name='Tasks',
        tables=['tasks', 'task_logs', 'priorities'],
        description='Tasks, completion history, and priority settings'
    ),
    'goals': ExportModule(
        name='goals',
        display_name='Goals',
        tables=['goals', 'goal_progress', 'milestones'],
        description='Goals, progress tracking, and milestones'
    ),
    'finances': ExportModule(
        name='finances',
        display_name='Finances',
        tables=['transactions', 'categories', 'budgets'],
        description='Financial transactions, categories, and budgets'
    ),
    'health': ExportModule(
        name='health',
        display_name='Health',
        tables=['health_entries', 'metrics', 'mood_logs'],
        description='Health metrics, mood logs, and wellness data'
    ),
    'time': ExportModule(
        name='time',
        display_name='Time Tracking',
        tables=['time_entries', 'projects', 'categories'],
        description='Time entries, projects, and time categories'
    ),
    'gamification': ExportModule(
        name='gamification',
        display_name='Gamification',
        tables=['achievements', 'xp_logs', 'levels'],
        description='Achievements, XP history, and level progression'
    ),
    'system': ExportModule(
        name='system',
        display_name='System',
        tables=['users', 'preferences', 'settings'],
        description='User accounts, preferences, and system settings'
    ),
}


@dataclass
class ExportResult:
    """
    Result of an export operation.
    
    Contains statistics and file information
    after an export completes.
    
    Attributes:
        success: Whether export succeeded
        export_id: ID of export request
        file_path: Path to exported file
        file_size_bytes: Size of exported file
        record_count: Total records exported
        modules_exported: List of modules included
        duration_seconds: Time taken
        error_message: Error if failed
    """
    success: bool = False
    export_id: str = ""
    file_path: Optional[str] = None
    file_size_bytes: int = 0
    record_count: int = 0
    modules_exported: List[str] = field(default_factory=list)
    records_by_module: Dict[str, int] = field(default_factory=dict)
    duration_seconds: float = 0.0
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'success': self.success,
            'export_id': self.export_id,
            'file_path': self.file_path,
            'file_size_bytes': self.file_size_bytes,
            'record_count': self.record_count,
            'modules_exported': self.modules_exported,
            'records_by_module': self.records_by_module,
            'duration_seconds': self.duration_seconds,
            'error_message': self.error_message,
        }