# Phase 5: Data Management & Portability

**Duration:** 2-3 weeks
**Status:** 📋 Not Started
**Dependencies:** Phase 4 Complete
**Created:** February 18, 2026

---

## ⚠️ Implementation Language Clarification

**This entire phase is implemented in Python 3.10+**

When this document mentions **JSON**, **CSV**, or **SQLite**, these refer to **data formats**, not programming languages:

| Term | What It Is | Python Module |
|------|------------|---------------|
| **JSON** | Data interchange format | `import json` (Python stdlib) |
| **CSV** | Tabular data format | `import csv` (Python stdlib) |
| **SQLite** | Database format | `import sqlite3` (Python stdlib) |
| **ZIP** | Compression format | `from zipfile import ZipFile` (Python stdlib) |

**All code implementation is 100% Python.** No other programming languages are used.

---

## Overview

Phase 5 focuses on data portability, backup, and management capabilities. This phase ensures users have full control over their data with export/import functionality, automated backups, and data lifecycle management.

**Implementation Language:** Python 3.10+
**Key Libraries:** sqlite3 (stdlib), json (stdlib), csv (stdlib), zipfile (stdlib), hashlib (stdlib), APScheduler

---

## Goals

| Goal | Success Metric |
|------|----------------|
| Python export modules | Users can export all data using Python modules |
| Python import modules | Users can restore data using Python importers |
| Automated backups | Python-based scheduled backups with APScheduler |
| Data reset options | Users can selectively or fully reset their data |
| Cloud sync readiness | Python architecture supports future cloud synchronization |

---

## Phase 5.1: Data Export System

**Priority:** High
**Effort:** Medium
**Duration:** 4-5 days
**Status:** 📋 Not Started

### Problem

Users need to export their data for:
- Backup purposes
- Migration to other systems
- Data analysis in external tools
- Compliance with data portability regulations

Without export capabilities, users are locked into the system and risk data loss.

### Solution

Implement comprehensive data export functionality in Python:
- Python modules for data extraction from SQLite
- Multiple output formats (JSON files, CSV files, SQLite dumps)
- Scheduled automated exports via APScheduler
- Secure download links with token-based authentication

### Python Implementation Architecture

```
brain/data_export/
├── __init__.py              # Package initialization
├── exporter.py              # Main DataExporter class
├── serializers/             # Python serializer modules
│   ├── __init__.py
│   ├── json_serializer.py  # Python json module wrapper
│   ├── csv_serializer.py   # Python csv module wrapper
│   └── sqlite_serializer.py # SQLite dump utilities
├── download.py              # Secure download token generation
└── history.py               # Export history tracking
```

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Export         │────▶│  Data            │────▶│  Format         │
│  Request        │     │  Collector       │     │  Serializer     │
│  Handler        │     │                  │     │                 │
└─────────────────┘     └──────────────────┘     └─────────────────┘
         │                       │                        │
         ▼                       ▼                        ▼
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Export         │     │  Compression      │     │  Secure         │
│  History        │     │  & Packaging      │     │  Download       │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

### Python Data Model Implementation

```python
"""
Data Export Models

Python dataclasses for export request tracking and history.
Uses Python standard library: json, csv, sqlite3, zipfile, hashlib
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional, List, Dict, Any
from enum import Enum
import uuid
import json


class ExportFormat(Enum):
    """Supported export formats (data formats, not programming languages)."""
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
```

### Export Formats Explained

**Important:** JSON, CSV, and SQLite are **data formats**, not programming languages. All implementation is in Python.

| Format | Type | Python Module | Use Case |
|--------|------|---------------|----------|
| **JSON** | Data interchange | `json` (stdlib) | Structured data, easy to parse |
| **CSV** | Tabular data | `csv` (stdlib) | Spreadsheet compatibility |
| **SQLite** | Database dump | `sqlite3` (stdlib) | Complete database backup |
| **ZIP** | Compression | `zipfile` (stdlib) | Reduce file size for download |


@dataclass
class ExportHistory:
    """Track export history for analytics."""
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
```

### Export Modules

| Module | Tables/Data |
|--------|-------------|
| **Habits** | habits, habit_logs, streaks, reminders |
| **Tasks** | tasks, task_logs, priorities, categories |
| **Goals** | goals, goal_progress, milestones |
| **Finances** | transactions, categories, budgets |
| **Health** | health_entries, metrics, mood_logs |
| **Time** | time_entries, projects, categories |
| **Gamification** | achievements, xp_logs, levels |
| **System** | users, preferences, settings |

### Tasks

**Research Required First:**
- [ ] Create research document: `docs/research/DATA_MANAGEMENT_PATTERNS.md`
  - Research export/import patterns in open-source projects
  - Study backup strategies in similar applications
  - Analyze data portability standards (GDPR, etc.)
  - Review compression algorithms for SQLite databases

**After Research Complete:**
- [ ] Design export data model and schema (based on research findings)
- [ ] Implement `DataExporter` class (following researched patterns)
- [ ] Create JSON serializer using Python's `json` module
- [ ] Create CSV serializer using Python's `csv` module
- [ ] Implement SQLite dump functionality using `sqlite3` module
- [ ] Add compression using Python's `zipfile` module
- [ ] Create export request handler
- [ ] Implement secure download token system
- [ ] Add export history tracking
- [ ] Create Streamlit export UI
- [ ] Write unit tests for export functionality

### Implementation Location

- `brain/data_export/__init__.py`
- `brain/data_export/exporter.py`
- `brain/data_export/serializers.py`
- `brain/data_export/download.py`
- `tracking_app/pages/data_export.py` (Streamlit UI)

---

## Phase 5.2: Data Import System

**Priority:** High
**Effort:** Medium
**Duration:** 4-5 days
**Status:** ✅ Complete

### Problem

Users need to import data when:
- Restoring from a backup
- Migrating from another system
- Merging data from multiple sources
- Reverting to a previous state

Without import capabilities, data restoration is impossible.

### Solution

Implement robust data import functionality in Python:
- Python-based file parsers (json, csv modules)
- Validation engine with comprehensive checks
- Conflict detection and resolution strategies
- Transaction-based imports using SQLite transactions
- Rollback capability on failure

### Python Implementation Architecture

```
brain/data_import/
├── __init__.py              # Package initialization
├── importer.py              # Main DataImporter class
├── parsers/                 # Python parser modules
│   ├── __init__.py
│   ├── json_parser.py      # Python json module wrapper
│   └── csv_parser.py       # Python csv module wrapper
├── validator.py             # Data validation engine
├── conflict_resolver.py     # Conflict detection and resolution
└── preview.py               # Import preview functionality
```

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  File Upload    │────▶│  Format          │────▶│  Validation     │
│  & Detection    │     │  Detector        │     │  Engine         │
└─────────────────┘     └──────────────────┘     └─────────────────┘
         │                       │                        │
         ▼                       ▼                        ▼
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Conflict       │◀────│  Data            │────▶│  Transaction    │
│  Resolution     │     │  Transformer     │     │  Importer       │
└─────────────────┘     └──────────────────┘     └─────────────────┘
         │
         ▼
┌─────────────────┐
│  Import Report  │
│  & Analytics    │
└─────────────────┘
```

### Python Data Model Implementation

```python
"""
Data Import Models

Python dataclasses for import request tracking and validation.
Uses Python standard library: json, csv, sqlite3, hashlib
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
```

### Import Formats Explained

**Important:** JSON and CSV are **data formats**, not programming languages. All implementation is in Python.

| Format | Type | Python Module | Implementation |
|--------|------|---------------|----------------|
| **JSON** | Data interchange | `json` (stdlib) | `json.load()` for parsing |
| **CSV** | Tabular data | `csv` (stdlib) | `csv.DictReader()` for parsing |
| **SQLite** | Database | `sqlite3` (stdlib) | `sqlite3.connect()` for direct DB import |


@dataclass
class ImportPreview:
    """Preview of what will be imported."""
    total_records: int = 0
    records_by_module: Dict[str, int] = field(default_factory=dict)
    conflicts_detected: int = 0
    conflicts_by_module: Dict[str, int] = field(default_factory=dict)
    estimated_duration_seconds: float = 0.0
    warnings: List[str] = field(default_factory=list)
```

### Import Validation Rules

| Check | Description |
|-------|-------------|
| **Format Validation** | File matches declared format |
| **Schema Validation** | Data structure matches expected schema |
| **Data Type Validation** | Field types are correct (int, string, date) |
| **Referential Integrity** | Foreign keys reference valid records |
| **Duplicate Detection** | Identify records that already exist |
| **Circular Dependencies** | Detect circular references |

### Tasks

**Research Required First:** (can be combined with 5.1 research)
- [x] Research import validation patterns
- [x] Study conflict resolution strategies in data migration tools
- [x] Review transaction patterns for atomic imports

**After Research Complete:**
- [x] Design import data model and schema (based on research findings)
- [x] Implement `DataImporter` class (following researched patterns)
- [x] Create JSON parser using Python's `json` module
- [x] Create CSV parser using Python's `csv` module
- [x] Implement validation engine (research-based rules)
- [x] Create conflict detection system
- [x] Implement conflict resolution strategies (from research)
- [x] Add transaction-based import using SQLite transactions
- [x] Create rollback mechanism
- [x] Build import preview functionality
- [x] Create Streamlit import UI
- [x] Write unit tests for import functionality

### Implementation Location

**Completed Files:**
- ✅ `brain/data_import/__init__.py` - Package initialization
- ✅ `brain/data_import/models.py` - Data models (ImportRequest, ImportStatus, etc.)
- ✅ `brain/data_import/parsers.py` - JSON, CSV, SQLite parsers
- ✅ `brain/data_import/validator.py` - Validation engine
- ✅ `brain/data_import/conflict_resolver.py` - Conflict detection and resolution
- ✅ `brain/data_import/importer.py` - Main DataImporter class
- ✅ `tracking_app/pages/data_import.py` - Streamlit UI
- ✅ `tests/test_data_import.py` - Unit and integration tests

**Total:** ~2,080 lines of Python code across 8 files

---

## Phase 5.3: Backup & Restore System

**Priority:** High
**Effort:** Medium
**Duration:** 4-5 days
**Status:** 📋 Not Started
**Research:** ✅ Complete - See [BACKUP_RESTORE_RESEARCH.md](../docs/research/BACKUP_RESTORE_RESEARCH.md)

### Problem

Users risk losing data due to:
- Accidental deletion
- System failures
- Corruption
- User errors

Without automated backups, data recovery is impossible or manual.

### Solution

Implement automated backup system in Python based on research findings:
- **APScheduler** for scheduled automatic backups (BackgroundScheduler for Streamlit)
- **SHA-256 checksum** verification using Python's `hashlib` module
- **GFS (Grandfather-Father-Son)** retention policy for balanced backup lifecycle
- **Hard link deduplication** for storage efficiency (optional)
- One-click restore functionality with confirmation workflow

### Research Summary

Based on comprehensive research documented in [BACKUP_RESTORE_RESEARCH.md](../docs/research/BACKUP_RESTORE_RESEARCH.md):

#### Key Findings

| Topic | Research Finding | Implementation |
|-------|------------------|----------------|
| **Change Detection** | Hybrid approach: Size → Time → Hash | Tier 1: Size check, Tier 2: mtime check, Tier 3: SHA-256 |
| **Deduplication** | Hard links (os.link) for unchanged files | PyHardLinkBackup pattern |
| **Integrity** | SHA-256 with chunked reading (64KB buffer) | Constant memory footprint |
| **Retention** | GFS scheme: Daily (7), Weekly (4), Monthly (12) | Protection list methodology |
| **Scheduling** | BackgroundScheduler with max_instances=1 | Prevents concurrent backup jobs |
| **Testing** | pyfakefs for filesystem mocking | No real disk I/O in tests |

#### Reference Repositories Analyzed

| Repository | Key Feature | URL |
|------------|-------------|-----|
| PyHardLinkBackup | Hard link deduplication | https://github.com/jedie/PyHardLinkBackup |
| backup-warden | Retention management | https://github.com/charles-001/backup-warden |
| CTFd-Backup-Tool | JSON manifest patterns | https://github.com/mlgzackfly/CTFd-Backup-Tool |
| checksum-diff | Checksum comparison | https://github.com/soerenkoehler/checksum-diff |
| apscheduler | Job scheduling | https://github.com/agronholm/apscheduler |
| pyfakefs | Filesystem mocking | https://github.com/pytest-dev/pyfakefs |

### Python Implementation Architecture

```
brain/backup/
├── __init__.py              # Package initialization
├── manager.py               # Main BackupManager class
├── scheduler.py             # APScheduler integration (BackgroundScheduler)
├── restore.py               # Restore functionality
├── retention.py             # GFS retention policy engine
├── verifier.py              # SHA-256 checksum verification
├── manifest.py              # Backup manifest handling
└── models.py                # Data models (BackupJob, BackupSchedule)
```

```
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Backup         │────▶│  Backup          │────▶│  Storage        │
│  Scheduler      │     │  Creator         │     │  Manager        │
│  (APScheduler)  │     │                  │     │                 │
│  Background     │     │  Incremental/    │     │  Hard Links     │
└─────────────────┘     │  Full            │     │  (Dedup)        │
         │              └──────────────────┘     └─────────────────┘
         │                       │                        │
         ▼                       ▼                        ▼
┌─────────────────┐     ┌──────────────────┐     ┌─────────────────┐
│  Retention      │     │  Backup          │     │  Restore        │
│  Policy (GFS)   │     │  Verification    │     │  Manager        │
│  Daily/Weekly/  │     │  (SHA-256)       │     │  + Confirmation │
│  Monthly        │     │  Manifest        │     │                 │
└─────────────────┘     └──────────────────┘     └─────────────────┘
```

### Data Model

```python
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
from enum import Enum
import uuid
import json


class BackupType(Enum):
    """Types of backups."""
    FULL = "full"  # Complete system backup
    INCREMENTAL = "incremental"  # Changes since last backup (hard links)
    DIFFERENTIAL = "differential"  # Changes since last full backup


class BackupStatus(Enum):
    """Backup job status."""
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    VERIFIED = "verified"


@dataclass
class BackupJob:
    """Represents a backup job."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    backup_type: BackupType = BackupType.FULL
    status: BackupStatus = BackupStatus.PENDING
    file_path: str = ""
    file_size_bytes: int = 0
    checksum: str = ""  # SHA-256 for verification
    record_count: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    verified_at: Optional[datetime] = None
    expires_at: Optional[datetime] = None
    error_message: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'backup_type': self.backup_type.value,
            'status': self.status.value,
            'file_path': self.file_path,
            'file_size_bytes': self.file_size_bytes,
            'checksum': self.checksum,
            'record_count': self.record_count,
            'started_at': self.started_at.isoformat() if self.started_at else None,
            'completed_at': self.completed_at.isoformat() if self.completed_at else None,
            'verified_at': self.verified_at.isoformat() if self.verified_at else None,
            'expires_at': self.expires_at.isoformat() if self.expires_at else None,
            'error_message': self.error_message,
            'metadata': json.dumps(self.metadata),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BackupJob':
        """Create instance from dictionary."""
        return cls(
            id=data.get('id', str(uuid.uuid4())),
            user_id=data.get('user_id', ''),
            backup_type=BackupType(data.get('backup_type', 'full')),
            status=BackupStatus(data.get('status', 'pending')),
            file_path=data.get('file_path', ''),
            file_size_bytes=data.get('file_size_bytes', 0),
            checksum=data.get('checksum', ''),
            record_count=data.get('record_count', 0),
            started_at=datetime.fromisoformat(data['started_at']) if data.get('started_at') else None,
            completed_at=datetime.fromisoformat(data['completed_at']) if data.get('completed_at') else None,
            verified_at=datetime.fromisoformat(data['verified_at']) if data.get('verified_at') else None,
            expires_at=datetime.fromisoformat(data['expires_at']) if data.get('expires_at') else None,
            error_message=data.get('error_message'),
            metadata=json.loads(data.get('metadata', '{}')),
        )


@dataclass
class BackupSchedule:
    """Automated backup schedule configuration."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    enabled: bool = True
    frequency: str = "daily"  # daily, weekly, monthly
    time_of_day: str = "02:00"  # HH:MM format
    backup_type: BackupType = BackupType.FULL
    retention_count: int = 7  # Keep N backups
    retention_days: int = 30  # Keep backups for N days
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)
```

### GFS Retention Policy (Grandfather-Father-Son)

The gold standard for balancing granularity with longevity:

| Generation | Frequency | Retention | Purpose |
|------------|-----------|-----------|---------|
| **Son** | Daily | 7 days | Immediate recovery from recent errors |
| **Father** | Weekly | 4 weeks | Roll back to a state from earlier in the month |
| **Grandfather** | Monthly | 12 months | Seasonal analysis or quarterly audits |
| **Archive** | Yearly | 7 years | Legal compliance |

**Implementation Pattern (Protection List Methodology):**

```python
def apply_gfs_retention(backups: List[BackupInfo], daily_keep: int = 7,
                         weekly_keep: int = 4, monthly_keep: int = 12) -> Set[str]:
    """
    Apply GFS retention policy using protection list methodology.
    Fail-safe design: builds a "keep set" rather than a "delete list".
    """
    keep_set = set()
    now = datetime.now()
    sorted_backups = sorted(backups, key=lambda b: b.created_at, reverse=True)
    
    daily_count = weekly_count = monthly_count = 0
    
    for backup in sorted_backups:
        age_days = (now - backup.created_at).days
        
        # Daily: Keep last N days
        if age_days < daily_keep and daily_count < daily_keep:
            keep_set.add(backup.id)
            daily_count += 1
        # Weekly: Keep oldest backup in each week
        elif weekly_count < weekly_keep:
            keep_set.add(backup.id)
            weekly_count += 1
        # Monthly: Keep oldest backup in each month
        elif monthly_count < monthly_keep:
            keep_set.add(backup.id)
            monthly_count += 1
    
    return keep_set
```

### SHA-256 Checksum Implementation

**Critical:** Use chunked reading to maintain constant memory footprint:

```python
import hashlib
from pathlib import Path

def generate_file_hash(file_path: Path, buffer_size: int = 65536) -> str:
    """
    Calculates SHA-256 hash using chunked reading.
    Memory footprint: 64KB constant, regardless of file size.
    """
    sha256 = hashlib.sha256()
    with open(file_path, 'rb') as f:
        while chunk := f.read(buffer_size):
            sha256.update(chunk)
    return sha256.hexdigest()
```

### APScheduler Integration for Streamlit

Use `BackgroundScheduler` since Streamlit's main thread is occupied by the UI event loop:

```python
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
import atexit

class BackupScheduler:
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        atexit.register(lambda: self.scheduler.shutdown(wait=False))
    
    def add_daily_backup(self, hour: int = 2, minute: int = 0):
        self.scheduler.add_job(
            func=self.run_backup,
            trigger=CronTrigger(hour=hour, minute=minute),
            id='daily_backup',
            max_instances=1,  # Prevent overlap
            coalesce=True,    # Fire only once if missed
            replace_existing=True
        )
```

### Backup Verification Methods

| Method | Speed | Reliability | Recommended Use |
|--------|-------|-------------|-----------------|
| **Size + ModTime** | Very High | Low (misses content changes) | Frequent, low-risk checks |
| **Partial Hash (Header)** | High | Moderate | Quick sanity checks |
| **Full SHA-256** | Low | Very High | Weekly deep verification |
| **Bit-for-Bit Compare** | Very Low | Maximum | Restoration testing only |

### Streamlit UI Patterns

**Session State Management:**
```python
def init_session_state():
    if 'backup_in_progress' not in st.session_state:
        st.session_state.backup_in_progress = False
    if 'show_restore_confirm' not in st.session_state:
        st.session_state.show_restore_confirm = False
```

**Confirmation Modal for Destructive Operations:**
- Show warning before restore: "⚠️ This will overwrite current data"
- Require secondary "Yes, Restore" button click
- Use `st.session_state` to track dialog state

### Tasks

**Research Complete:**
- [x] Research backup strategies in similar Python applications
- [x] Study retention policy best practices (GFS scheme)
- [x] Review checksum algorithms for data verification (SHA-256 recommended)
- [x] Analyze APScheduler patterns for Streamlit apps
- [x] Study testing strategies with pyfakefs

**Implementation Tasks:**
- [ ] Implement `BackupManager` class with full backup creation
- [ ] Create `BackupScheduler` with APScheduler BackgroundScheduler
- [ ] Implement SHA-256 checksum verification with chunked reading
- [ ] Create GFS retention policy engine
- [ ] Implement restore functionality with confirmation workflow
- [ ] Add backup manifest generation (JSON format)
- [ ] Create Streamlit backup/restore UI with session state
- [ ] Write unit tests using pyfakefs for filesystem mocking
- [ ] Write integration tests for round-trip backup/restore

### Testing Strategy

**Unit Tests (pyfakefs):**
```python
from pyfakefs import fake_filesystem

def test_incremental_backup(fake_fs):
    """Test that incremental backup creates hard links for unchanged files."""
    # Create fake filesystem
    fs = fake_filesystem.FakeFilesystem()
    fs.create_dir('/source')
    fs.create_file('/source/file1.txt', contents='content1')
    
    # Run backup and verify hard link (same inode)
    perform_incremental_backup(Path('/source'), Path('/backup1'), None)
    perform_incremental_backup(Path('/source'), Path('/backup2'), Path('/backup1'))
    
    assert fs.get_object('/backup1/file1.txt').st_ino == \
           fs.get_object('/backup2/file1.txt').st_ino
```

**Integration Tests:**
- Round-trip test: Create → Backup → Delete → Restore → Verify
- Incremental test: Verify hard links for unchanged files
- Retention test: Mock time, verify GFS pruning

### Implementation Location

- `brain/backup/__init__.py`
- `brain/backup/manager.py`
- `brain/backup/scheduler.py`
- `brain/backup/retention.py`
- `brain/backup/restore.py`
- `brain/backup/verifier.py`
- `brain/backup/manifest.py`
- `brain/backup/models.py`
- `tracking_app/pages/backup_restore.py` (Streamlit UI)
- `tests/test_backup.py` (Unit and integration tests)

---

## Phase 5.4: Data Lifecycle Management

**Priority:** Medium
**Effort:** Low-Medium
**Duration:** 3-4 days
**Status:** 📋 Not Started

### Problem

Over time, systems accumulate:
- Old archived data
- Temporary files
- Expired sessions
- Orphaned records

Without lifecycle management, databases grow unbounded and performance degrades.

### Solution

Implement data lifecycle management:
- Configurable data retention policies
- Automated archival of old data
- Safe data purge functionality
- Data reset options (partial/full)
- GDPR compliance (right to erasure)

### Data Model

```python
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, Dict, Any


@dataclass
class RetentionPolicy:
    """Data retention policy configuration."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    entity_type: str = ""  # 'habit', 'task', 'goal', etc.
    archive_after_days: int = 365  # Archive after N days
    delete_after_days: int = 730  # Delete after N days
    enabled: bool = True
    last_run: Optional[datetime] = None
    created_at: datetime = field(default_factory=datetime.now)
    updated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for storage."""
        return {
            'id': self.id,
            'entity_type': self.entity_type,
            'archive_after_days': self.archive_after_days,
            'delete_after_days': self.delete_after_days,
            'enabled': self.enabled,
            'last_run': self.last_run.isoformat() if self.last_run else None,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat(),
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'RetentionPolicy':
        """Create instance from dictionary."""
        return cls(
            id=data.get('id', str(uuid.uuid4())),
            entity_type=data.get('entity_type', ''),
            archive_after_days=data.get('archive_after_days', 365),
            delete_after_days=data.get('delete_after_days', 730),
            enabled=bool(data.get('enabled', 1)),
            last_run=datetime.fromisoformat(data['last_run']) if data.get('last_run') else None,
            created_at=datetime.fromisoformat(data['created_at']) if data.get('created_at') else datetime.now(),
            updated_at=datetime.fromisoformat(data['updated_at']) if data.get('updated_at') else datetime.now(),
        )


@dataclass
class DataReset:
    """Track data reset operations."""
    id: str = field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = ""
    reset_type: str = "full"  # full, partial, module-specific
    modules: list = field(default_factory=list)
    backup_created: bool = True
    backup_id: Optional[str] = None
    status: str = "pending"
    records_affected: int = 0
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    error_message: Optional[str] = None
```

### Reset Options

| Reset Type | Description | Use Case |
|------------|-------------|----------|
| **Full Reset** | Delete all user data | Starting fresh |
| **Module Reset** | Reset specific module (habits, tasks) | Restart specific area |
| **Archive Reset** | Clear archived data only | Free up space |
| **Soft Reset** | Mark as incomplete instead of deleting | Preserve history |

### Tasks

**Research Required First:**
- [ ] Research data retention policies and best practices
- [ ] Study GDPR erasure requirements
- [ ] Review archival patterns in long-term data storage

**After Research Complete:**
- [ ] Design retention policy data model (based on research findings)
- [ ] Implement `LifecycleManager` class (following researched patterns)
- [ ] Create archival scheduler
- [ ] Implement data purge functionality
- [ ] Add reset confirmation workflow
- [ ] Create Streamlit lifecycle management UI
- [ ] Implement GDPR erasure compliance (from research)
- [ ] Write unit tests for lifecycle functionality

### Implementation Location

- `brain/lifecycle/__init__.py`
- `brain/lifecycle/manager.py`
- `brain/lifecycle/retention.py`
- `brain/lifecycle/archive.py`
- `tracking_app/pages/data_lifecycle.py` (Streamlit UI)

---

## Success Criteria

| Criteria | How to Verify |
|----------|---------------|
| Export works | Can export all data to JSON/CSV |
| Import works | Can restore data from export file |
| Backups work | Automated backups created on schedule |
| Restore works | Can restore from backup successfully |
| Lifecycle works | Old data archived/deleted per policy |
| Reset works | Can selectively or fully reset data |

---

## Dependencies

All implementation is in **Python 3.10+**. The following Python packages are required:

| Dependency | Purpose | Install | Python Module |
|------------|---------|---------|---------------|
| **APScheduler** | Backup scheduling | `pip install apscheduler` | `from apscheduler.schedulers.background import BackgroundScheduler` |
| **zipfile** | Export compression | Built-in (stdlib) | `from zipfile import ZipFile` |
| **hashlib** | Checksum verification | Built-in (stdlib) | `from hashlib import sha256` |
| **json** | JSON export/import | Built-in (stdlib) | `import json` |
| **csv** | CSV export/import | Built-in (stdlib) | `import csv` |
| **sqlite3** | SQLite database operations | Built-in (stdlib) | `import sqlite3` |

### Python Standard Library Usage

Phase 5 relies heavily on Python's standard library - no external dependencies required for core functionality:

```python
# Export functionality
import json           # JSON serialization
import csv            # CSV writing
import sqlite3        # Database access
import zipfile        # Compression

# Import functionality  
import json           # JSON parsing
import csv            # CSV reading
import sqlite3        # Database restore

# Backup functionality
import hashlib        # SHA-256 checksums
import zipfile        # Backup compression
from apscheduler.schedulers.background import BackgroundScheduler  # Scheduling
```

---

## Integration Points

| Component | Integration |
|-----------|-------------|
| **Database** | Direct SQLite access for export/import |
| **Notifications** | Alert when backup/export complete |
| **Audit System** | Log all export/import/backup operations |
| **Security** | Encrypt sensitive exports, secure download tokens |

---

## Security Considerations

| Concern | Mitigation |
|---------|------------|
| **Data Exposure** | Encrypt exports, secure download links |
| **Unauthorized Access** | Require authentication for export/import |
| **Data Tampering** | Checksum verification on imports |
| **Malicious Imports** | Validate all imported data |
| **Privacy** | Redact sensitive data in exports (optional) |

---

## Performance Considerations

| Challenge | Solution |
|-----------|----------|
| **Large Exports** | Stream data, don't load all in memory |
| **Long Imports** | Background processing with progress updates |
| **Database Locking** | Use transactions, minimize lock time |
| **Storage Space** | Compress exports, enforce retention policies |

---

## Future Enhancements (Phase 5+)

| Enhancement | Description |
|-------------|-------------|
| **Cloud Sync** | Sync data to cloud storage (Dropbox, Google Drive) |
| **Version Control** | Track data changes over time |
| **Data Merging** | Merge data from multiple sources |
| **Scheduled Reports** | Email periodic data summaries |
| **API Access** | REST API for programmatic export/import |

---

## Research Required

**Before starting implementation, create the following research document:**

### Primary Research Document
- **Location:** `docs/research/DATA_MANAGEMENT_PATTERNS.md`
- **Status:** 📋 Not Started
- **Template:** Follow format in `docs/research/RESEARCH_SUMMARY.md`

### Research Topics

1. **Data Export/Import Patterns**
   - Export formats used in open-source personal tracking apps
   - Import validation strategies
   - Conflict resolution approaches (skip, merge, overwrite)
   - Transaction patterns for atomic operations

2. **Backup Strategies**
   - Full vs. incremental vs. differential backups
   - Optimal backup frequencies for personal apps
   - Retention policy recommendations
   - Checksum algorithms (MD5, SHA-256, etc.)

3. **Data Portability Standards**
   - GDPR data portability requirements
   - Right to erasure (right to be forgotten)
   - Industry best practices for data export

4. **Compression & Storage**
   - Compression algorithms for SQLite databases
   - Trade-offs: compression ratio vs. speed
   - Storage optimization techniques

### Research Process

Follow the established research paper format (see `docs/research/RESEARCH_SUMMARY.md`):

1. **Gather sources** - Open-source projects, academic papers, industry standards
2. **Synthesize findings** - Extract key patterns and best practices
3. **Create visualizations** - Architecture diagrams, comparison tables
4. **Document conclusions** - Clear recommendations for implementation
5. **Link to phase document** - Reference research in task lists

### Existing Research to Leverage

| Document | Relevant Content |
|----------|------------------|
| `docs/research/RESEARCH_SUMMARY.md` | Local-first architecture, data sovereignty |
| `docs/research/TECHNICAL_ARCHITECTURES.md` | Database patterns, event sourcing |
| `docs/research/OPEN_SOURCE_PROJECTS.md` | Similar project analysis |

---

## Testing Strategy

### Unit Tests
- Export serializer tests
- Import parser tests
- Validation engine tests
- Backup creation tests

### Integration Tests
- Full export/import cycle
- Backup and restore workflow
- Conflict resolution scenarios

### Edge Cases
- Empty database export
- Corrupted import file handling
- Very large datasets (>100k records)
- Concurrent export requests

---

*Last updated: February 18, 2026*
*Status: 📋 Phase 5 Not Started - Ready for Implementation*
