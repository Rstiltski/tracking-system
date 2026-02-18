# Backup Repositories Analysis

**Analysis of cloned repositories for actionable improvements to Veryfyn's backup system.**

**Date:** February 18, 2026

---

## Repositories Analyzed

| Repository | Key Feature | Relevance |
|------------|-------------|-----------|
| PyHardLinkBackup | Hard link deduplication | ⭐⭐⭐⭐⭐ |
| backup-warden | GFS retention policies | ⭐⭐⭐⭐⭐ |
| apscheduler | Job scheduling | ⭐⭐⭐⭐⭐ |
| CTFd-Backup-Tool | JSON manifest patterns | ⭐⭐⭐⭐ |
| checksum-diff | Checksum comparison | ⭐⭐⭐ |
| pyfakefs | Filesystem mocking | ⭐⭐⭐⭐ |

---

## Key Findings & Actionable Improvements

### 1. PyHardLinkBackup: Deduplication Strategy

**Pattern Found:**
```python
# Tiered deduplication logic
if size < size_db.MIN_SIZE:
    # Small file -> always copy without deduplication
    file_hash = copy_and_hash(src_path, dst_path)
elif size in size_db:
    # Check hash database for duplicates
    if existing_path := hash_db.get(file_hash):
        os.link(existing_path, dst_path)  # Hard link!
    else:
        copy_with_progress(src_path, dst_path)
else:
    # New size -> can't be duplicate -> copy and hash
    file_hash = copy_and_hash(src_path, dst_path)
    size_db.add(size)
    hash_db[file_hash] = dst_path
```

**Improvement for Veryfyn:**
- Implement `FileSizeDatabase` and `FileHashDatabase` classes
- Use tiered approach: Size check → Hash check → Hard link or copy
- Store hashes in SQLite for persistence across backup runs

**Recommended Implementation:**
```python
# brain/backup/dedup.py
class DeduplicationEngine:
    """File deduplication using size and hash databases."""
    
    def __init__(self, db_path: Path):
        self.size_db = self._load_size_db(db_path)
        self.hash_db = self._load_hash_db(db_path)
        self.min_size = 1024  # Skip dedup for files < 1KB
    
    def should_hardlink(self, src_path: Path) -> tuple[bool, Path | None]:
        """Check if file should be hard-linked instead of copied."""
        size = src_path.stat().st_size
        
        if size < self.min_size:
            return False, None
        
        if size not in self.size_db:
            return False, None
        
        file_hash = self._compute_hash(src_path)
        if file_hash in self.hash_db:
            return True, self.hash_db[file_hash]
        
        return False, None
```

---

### 2. backup-warden: Retention Policy Features

**Key Features Found:**

| Feature | Description | Veryfyn Application |
|---------|-------------|---------------------|
| `--relaxed` | Don't enforce strict time windows | Better for irregular backup schedules |
| `--prefer-recent` | Keep most recent in each slot | Alternative to "oldest in slot" |
| `--filestat` | Use file mtime instead of filename | For backups without timestamp in name |
| `include_list`/`exclude_list` | fnmatch patterns for filtering | Selective backup retention |
| `--no-recency-check` | Skip 24-hour warning | For weekly/monthly schedules |

**Improvement for Veryfyn:**
- Add `relaxed` mode for non-server environments (laptops)
- Add `prefer_recent` option for different user preferences
- Implement include/exclude patterns for selective retention

**Recommended Implementation:**
```python
# brain/backup/retention.py
@dataclass
class RetentionConfig:
    """Configuration for GFS retention policy."""
    daily: int = 7
    weekly: int = 4
    monthly: int = 12
    yearly: int = 3
    
    # New options from backup-warden research
    relaxed: bool = False  # Don't enforce strict time windows
    prefer_recent: bool = False  # Keep most recent in slot
    include_patterns: list[str] = field(default_factory=list)
    exclude_patterns: list[str] = field(default_factory=list)
    recency_check: bool = True  # Warn if no backup in 24h
```

---

### 3. APScheduler: Modern API Pattern

**Pattern Found (v4.x):**
```python
from apscheduler import Scheduler
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.cron import CronTrigger

# Context manager pattern
with Scheduler() as scheduler:
    scheduler.add_schedule(tick, IntervalTrigger(seconds=1))
    scheduler.run_until_stopped()
```

**Key Differences from v3.x:**
- Uses context manager (`with Scheduler()`)
- `add_schedule()` instead of `add_job()`
- Cleaner trigger imports

**Improvement for Veryfyn:**
- Update to APScheduler v4.x API
- Use context manager for automatic cleanup
- Implement `run_until_stopped()` pattern for Streamlit integration

**Recommended Implementation:**
```python
# brain/backup/scheduler.py
from contextlib import contextmanager
from apscheduler import Scheduler
from apscheduler.triggers.cron import CronTrigger

@contextmanager
def backup_scheduler():
    """Context manager for backup scheduler."""
    scheduler = Scheduler()
    try:
        yield scheduler
    finally:
        scheduler.stop()

class BackupSchedulerService:
    def add_daily_backup(self, hour: int = 2, minute: int = 0):
        with backup_scheduler() as scheduler:
            scheduler.add_schedule(
                self.run_backup,
                CronTrigger(hour=hour, minute=minute)
            )
```

---

### 4. CTFd-Backup-Tool: JSON Manifest Pattern

**Pattern Found:**
```json
{
  "metadata": {
    "timestamp": "2026-02-18T10:00:00Z",
    "version": "1.0",
    "checksum_algorithm": "sha256"
  },
  "files": [
    {
      "path": "tracking.db",
      "size": 1048576,
      "checksum": "abc123...",
      "modified": "2026-02-18T09:00:00Z"
    }
  ]
}
```

**Improvement for Veryfyn:**
- Include metadata section with version and algorithm
- Track individual file checksums
- Store modification timestamps for incremental detection

---

### 5. pyfakefs: Testing Strategy

**Pattern Found:**
```python
from pyfakefs import fake_filesystem

def test_backup(fake_filesystem):
    fs = fake_filesystem.FakeFilesystem()
    fs.create_dir('/backup')
    fs.create_file('/source/file.txt', contents='data')
    
    # Test without touching real filesystem
    perform_backup(Path('/source'), Path('/backup'))
    
    assert fs.exists('/backup/file.txt')
```

**Improvement for Veryfyn:**
- Use `fake_filesystem` fixture for all backup tests
- Test hard link behavior without real disk I/O
- Simulate edge cases (disk full, permission denied)

---

## Recommended Changes to Phase 5.3

### Add to Implementation Tasks:

1. **Deduplication Engine** (from PyHardLinkBackup)
   - [ ] Implement `FileSizeDatabase` class
   - [ ] Implement `FileHashDatabase` class  
   - [ ] Create `DeduplicationEngine` with tiered logic
   - [ ] Add hard link creation for unchanged files

2. **Enhanced Retention Options** (from backup-warden)
   - [ ] Add `relaxed` mode for irregular schedules
   - [ ] Add `prefer_recent` option
   - [ ] Implement include/exclude patterns
   - [ ] Add recency check with configurable threshold

3. **Modern APScheduler Integration** (from apscheduler v4)
   - [ ] Update to context manager pattern
   - [ ] Use `add_schedule()` API
   - [ ] Implement graceful shutdown

4. **Enhanced Manifest Format** (from CTFd-Backup-Tool)
   - [ ] Add metadata section with version info
   - [ ] Include per-file checksums
   - [ ] Store modification timestamps

5. **Testing with pyfakefs**
   - [ ] Add `fake_filesystem` fixture to conftest.py
   - [ ] Create unit tests for deduplication
   - [ ] Test retention policy without real files
   - [ ] Simulate error conditions

---

## Code Snippets for Implementation

### Deduplication Database

```python
# brain/backup/dedup_db.py
import sqlite3
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

@dataclass
class FileInfo:
    path: Path
    size: int
    hash: str
    modified: float

class DeduplicationDatabase:
    """SQLite-backed deduplication database."""
    
    def __init__(self, db_path: Path):
        self.conn = sqlite3.connect(str(db_path))
        self._init_tables()
    
    def _init_tables(self):
        self.conn.execute('''
            CREATE TABLE IF NOT EXISTS file_hashes (
                hash TEXT PRIMARY KEY,
                path TEXT NOT NULL,
                size INTEGER NOT NULL,
                modified REAL NOT NULL
            )
        ''')
        self.conn.execute('''
            CREATE INDEX IF NOT EXISTS idx_size 
            ON file_hashes(size)
        ''')
    
    def find_by_size(self, size: int) -> list[FileInfo]:
        cursor = self.conn.execute(
            'SELECT path, size, hash, modified FROM file_hashes WHERE size = ?',
            (size,)
        )
        return [FileInfo(Path(r[0]), r[1], r[2], r[3]) for r in cursor]
    
    def find_by_hash(self, hash: str) -> Optional[FileInfo]:
        cursor = self.conn.execute(
            'SELECT path, size, hash, modified FROM file_hashes WHERE hash = ?',
            (hash,)
        )
        row = cursor.fetchone()
        return FileInfo(Path(row[0]), row[1], row[2], row[3]) if row else None
    
    def add_file(self, info: FileInfo):
        self.conn.execute(
            'INSERT OR REPLACE INTO file_hashes (hash, path, size, modified) VALUES (?, ?, ?, ?)',
            (info.hash, str(info.path), info.size, info.modified)
        )
        self.conn.commit()
```

### Enhanced Retention Policy

```python
# brain/backup/retention_enhanced.py
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Set, List
import fnmatch

@dataclass
class EnhancedRetentionConfig:
    """Enhanced GFS retention configuration."""
    daily: int = 7
    weekly: int = 4
    monthly: int = 12
    yearly: int = 3
    
    # Enhanced options from backup-warden
    relaxed: bool = False
    prefer_recent: bool = False
    include_patterns: List[str] = field(default_factory=list)
    exclude_patterns: List[str] = field(default_factory=list)
    recency_check_hours: int = 24
    
    def matches_include(self, backup_name: str) -> bool:
        if not self.include_patterns:
            return True
        return any(fnmatch.fnmatch(backup_name, p) for p in self.include_patterns)
    
    def matches_exclude(self, backup_name: str) -> bool:
        return any(fnmatch.fnmatch(backup_name, p) for p in self.exclude_patterns)
    
    def should_keep(self, backup_name: str) -> bool:
        if self.matches_exclude(backup_name):
            return False
        return self.matches_include(backup_name)
```

---

## Summary

The cloned repositories provide production-tested patterns that can significantly improve Veryfyn's backup system:

| Improvement | Source | Impact | Effort |
|-------------|--------|--------|--------|
| Tiered deduplication | PyHardLinkBackup | Storage savings | Medium |
| Relaxed retention mode | backup-warden | Better UX | Low |
| Modern scheduler API | apscheduler v4 | Cleaner code | Low |
| Enhanced manifest | CTFd-Backup-Tool | Better tracking | Low |
| Fake filesystem testing | pyfakefs | Faster tests | Low |

**Recommendation:** Implement these improvements incrementally, starting with the testing infrastructure (pyfakefs) and retention enhancements (backup-warden patterns).

---

*Analysis completed: February 18, 2026*