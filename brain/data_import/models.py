"""
Data Import Models

Python dataclasses for import request tracking and validation.
Uses Python standard library: json, csv, sqlite3

All implementation is in Python 3.10+
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
import json


class ConflictStrategy(Enum):
    """
    How to handle data conflicts during import.
    
    These are strategies implemented in Python code,
    not external tools or languages.
    """
    SKIP = "skip"           # Skip conflicting records (Python: continue)
    OVERWRITE = "overwrite" # Replace existing with imported (Python: UPDATE)
    MERGE = "merge"         # Combine fields from both (Python: dict merge)
    DUPLICATE = "duplicate" # Keep both as separate records (Python: INSERT with new ID)


class ImportStatus(Enum):
    """Import job status."""
    PENDING = "pending"
    VALIDATING = "validating"
    IMPORTING = "importing"
    COMPLETED = "completed"
    FAILED = "failed"
    ROLLED_BACK = "rolled_back"


@dataclass
class ImportRequest:
    """
    Represents a data import request.
    
    Python implementation using dataclasses.
    All parsing handled by Python standard library modules.
    """
    id: str = ""
    user_id: str = ""
    file_path: str = ""
    format: str = ""  # 'json' or 'csv' - data formats
    conflict_strategy: ConflictStrategy = ConflictStrategy.SKIP
    modules_to_import: List[str] = field(default_factory=list)
    dry_run: bool = True  # Preview only
    status: ImportStatus = ImportStatus.PENDING
    validation_errors: List[str] = field(default_factory=list)
    import_summary: Optional[Dict[str, Any]] = None
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for SQLite storage."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'file_path': self.file_path,
            'format': self.format,
            'conflict_strategy': self.conflict_strategy.value,
            'modules_to_import': ','.join(self.modules_to_import),
            'dry_run': self.dry_run,
            'status': self.status.value,
            'validation_errors': ','.join(self.validation_errors),
            'import_summary': json.dumps(self.import_summary) if self.import_summary else None,
            'created_at': self.created_at.isoformat(),
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'error_message': self.error_message,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ImportRequest':
        """Create instance from SQLite row dictionary."""
        modules = data.get('modules_to_import', '')
        errors = data.get('validation_errors', '')
        return cls(
            id=data.get('id', str(uuid.uuid4())),
            user_id=data.get('user_id', ''),
            file_path=data.get('file_path', ''),
            format=data.get('format', 'json'),
            conflict_strategy=ConflictStrategy(data.get('conflict_strategy', 'skip')),
            modules_to_import=modules.split(',') if modules else [],
            dry_run=bool(data.get('dry_run', 1)),
            status=ImportStatus(data.get('status', 'pending')),
            validation_errors=errors.split(',') if errors else [],
            import_summary=json.loads(data['import_summary']) if data.get('import_summary') else None,
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.now(),
            completed_at=datetime.fromisoformat(data['completed_at']) if data.get('completed_at') else None,
            error_message=data.get('error_message'),
        )


@dataclass
class ImportPreview:
    """Preview of what will be imported."""
    total_records: int = 0
    records_by_module: Dict[str, int] = field(default_factory=dict)
    conflicts_detected: int = 0
    conflicts_by_module: Dict[str, int] = field(default_factory=dict)
    estimated_duration_seconds: float = 0.0
    warnings: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'total_records': self.total_records,
            'records_by_module': self.records_by_module,
            'conflicts_detected': self.conflicts_detected,
            'conflicts_by_module': self.conflicts_by_module,
            'estimated_duration_seconds': self.estimated_duration_seconds,
            'warnings': self.warnings,
        }


@dataclass
class ImportResult:
    """Result of an import operation."""
    success: bool = False
    records_imported: int = 0
    records_skipped: int = 0
    records_failed: int = 0
    conflicts_resolved: int = 0
    error_message: Optional[str] = None
    details: Dict[str, Any] = field(default_factory=dict)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            'success': self.success,
            'records_imported': self.records_imported,
            'records_skipped': self.records_skipped,
            'records_failed': self.records_failed,
            'conflicts_resolved': self.conflicts_resolved,
            'error_message': self.error_message,
            'details': self.details,
        }
