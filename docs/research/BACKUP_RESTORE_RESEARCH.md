# Backup and Restore System Research

**Phase 5.3: Backup & Restore System Implementation Research**

**Created:** February 18, 2026  
**Status:** Complete

---

## Overview

This document consolidates research on Python-based backup, restoration, and verification systems. The research focuses on:

1. Incremental backup architectures with hard link deduplication
2. SHA-256 checksum verification for data integrity
3. Grandfather-Father-Son (GFS) retention policies
4. APScheduler automation for scheduled backups
5. Streamlit-based visualization and control
6. Testing strategies with pytest and pyfakefs

---

## 1. Incremental Backup Architectures

### The Challenge

Backup systems must balance two conflicting requirements:
- **Storage Efficiency**: Minimize disk usage
- **Restoration Velocity**: Minimize recovery time

### Change Detection Methods

#### 1.1 Metadata-Based Detection

Uses file metadata (mtime, size) as the primary signal for change.

**Advantages:**
- High performance (comparing integers is computationally inexpensive)
- Avoids I/O bottleneck of reading file contents

**Risks:**
- False negatives if timestamp is programmatically reset
- May miss "silent" changes where metadata is preserved but content altered

#### 1.2 Content-Based Verification (Cryptographic Hashing)

Uses a cryptographic hash (SHA-256) as the immutable signature of file content.

**Hybrid Implementation Strategy:**

| Tier | Check | Description |
|------|-------|-------------|
| Tier 1 | Size | If file size differs, content has definitively changed |
| Tier 2 | Time | If size identical but mtime differs, treat as changed |
| Tier 3 | Hash | If size and mtime identical, compute SHA-256 for guaranteed integrity |

### Hard Link Deduplication

The industry-standard approach for file-based backups.

**How It Works:**
- Every backup is a full directory tree
- Unchanged files are not copied; instead, hard links point to the same inode
- Decouples logical view from physical storage
- Deleting old backups doesn't break newer ones (reference counting)

**Implementation Pattern:**

```python
import os
import shutil
from pathlib import Path

def perform_incremental_backup(source: Path, dest: Path, previous_backup: Path = None):
    """
    Copies files from source to dest.
    If previous_backup exists and file is unchanged, hard link instead of copy.
    """
    for file in source.rglob('*'):
        if file.is_file():
            rel_path = file.relative_to(source)
            dest_file = dest / rel_path
            prev_file = previous_backup / rel_path if previous_backup else None
            
            # Check if unchanged (Size + Mtime check first for speed)
            if prev_file and prev_file.exists() and \
               file.stat().st_mtime == prev_file.stat().st_mtime and \
               file.stat().st_size == prev_file.stat().st_size:
                # Hard Link (Fast, space efficient)
                os.link(prev_file, dest_file)
            else:
                # Copy (New or Modified)
                shutil.copy2(file, dest_file)
```

### Repository Comparison

| Feature | PyHardLinkBackup | Incremental-Backup-System | CTFd-Backup-Tool |
|---------|------------------|---------------------------|------------------|
| Change Detection | Size + SHA-256 Hash | Timestamp + Size | Timestamp + Size + SHA-256 |
| Deduplication | Hard Links (os.link) | None (Copy only) | Skip Unchanged |
| State Storage | Filesystem Inspection | In-Memory comparison | JSON Manifest |
| Use Case | System/Filesystem Backup | Simple Directory Mirroring | Application-Specific |

---

## 2. Cryptographic Integrity: SHA-256 Standard

### Why SHA-256?

| Algorithm | Collision Resistance | Performance | Recommendation |
|-----------|---------------------|-------------|----------------|
| MD5 | Weak (broken) | Fast | ❌ Not recommended |
| CRC32 | None (checksum only) | Very Fast | ❌ Not for security |
| SHA-256 | Strong | Fast (with CPU extensions) | ✅ Recommended |
| SHA-512 | Strong | Slightly slower | ✅ Acceptable |

### Implementation: Chunked Reading

**Critical:** Always use chunked reading to maintain constant memory footprint.

```python
import hashlib
from pathlib import Path

def generate_file_hash(file_path: Path, buffer_size: int = 65536) -> str:
    """
    Calculates SHA-256 hash of a file using chunked reading.
    
    Memory footprint remains constant (64KB) regardless of file size.
    """
    sha256 = hashlib.sha256()
    
    with open(file_path, 'rb') as f:
        while chunk := f.read(buffer_size):
            sha256.update(chunk)
    
    return sha256.hexdigest()
```

### The Manifest Pattern

A manifest acts as the source of truth for backup state.

```python
import json
from dataclasses import dataclass, field, asdict
from datetime import datetime
from typing import Dict, List, Optional

@dataclass
class FileManifest:
    """Manifest entry for a single file."""
    path: str
    checksum: str
    size: int
    modified_time: str
    
@dataclass
class BackupManifest:
    """Complete backup manifest."""
    backup_id: str
    created_at: str
    backup_type: str  # full, incremental, differential
    files: List[FileManifest] = field(default_factory=list)
    total_size: int = 0
    total_files: int = 0
    
    def to_json(self, path: Path):
        with open(path, 'w') as f:
            json.dump(asdict(self), f, indent=2)
    
    @classmethod
    def from_json(cls, path: Path) -> 'BackupManifest':
        with open(path, 'r') as f:
            data = json.load(f)
        return cls(**data)
```

### Verification Strategies

| Strategy | Description | When to Use |
|----------|-------------|-------------|
| **Sample-Based** | Random subset (e.g., 20 files) | Daily verification |
| **Full Scrub** | Read every byte | Weekly/Monthly |
| **Block-Level** | Hash fixed-size chunks | Large files (databases, VMs) |

---

## 3. Retention Policy: GFS Algorithm

### Grandfather-Father-Son (GFS) Scheme

The gold standard for balancing granularity with longevity.

| Generation | Frequency | Retention | Purpose |
|------------|-----------|-----------|---------|
| **Son** | Daily | 7 days | Immediate recovery |
| **Father** | Weekly | 4 weeks | Roll back within month |
| **Grandfather** | Monthly | 12 months | Seasonal/quarterly analysis |
| **Archive** | Yearly | 7 years | Legal compliance |

### Implementation: Protection List Methodology

Fail-safe design that prevents accidental data loss.

```python
from datetime import datetime, timedelta
from typing import List, Set
from dataclasses import dataclass

@dataclass
class BackupInfo:
    id: str
    created_at: datetime
    file_path: str
    size: int

def apply_gfs_retention(
    backups: List[BackupInfo],
    daily_keep: int = 7,
    weekly_keep: int = 4,
    monthly_keep: int = 12
) -> Set[str]:
    """
    Apply GFS retention policy using protection list methodology.
    
    Returns set of backup IDs to KEEP.
    """
    keep_set = set()
    now = datetime.now()
    
    # Sort backups by date (newest first)
    sorted_backups = sorted(backups, key=lambda b: b.created_at, reverse=True)
    
    # Track what we've kept for each category
    daily_count = 0
    weekly_count = 0
    monthly_count = 0
    
    for backup in sorted_backups:
        age_days = (now - backup.created_at).days
        
        # Daily: Keep last N days
        if age_days < daily_keep and daily_count < daily_keep:
            keep_set.add(backup.id)
            daily_count += 1
            continue
            
        # Weekly: Keep oldest backup in each week (up to N weeks)
        week_num = backup.created_at.isocalendar()[1]
        if age_days < daily_keep + (weekly_keep * 7):
            # Check if we already have a backup for this week
            week_key = f"week_{backup.created_at.year}_{week_num}"
            if weekly_count < weekly_keep:
                keep_set.add(backup.id)
                weekly_count += 1
                continue
                
        # Monthly: Keep oldest backup in each month (up to N months)
        month_key = f"month_{backup.created_at.year}_{backup.created_at.month}"
        if monthly_count < monthly_keep:
            keep_set.add(backup.id)
            monthly_count += 1
    
    return keep_set
```

### Strict vs Relaxed Rotation

| Approach | Description | Best For |
|----------|-------------|----------|
| **Strict** | Rigid time buckets (ISO week starts Monday) | Servers (always on) |
| **Relaxed** | Count backwards from present | Laptops/Workstations |

---

## 4. APScheduler Integration

### BackgroundScheduler for Streamlit

In Streamlit apps, the main thread is occupied by the UI event loop. Use `BackgroundScheduler` to spawn a dedicated thread for job management.

```python
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from datetime import datetime
import atexit

class BackupScheduler:
    """Manages scheduled backup jobs using APScheduler."""
    
    def __init__(self):
        self.scheduler = BackgroundScheduler()
        self.scheduler.start()
        # Ensure clean shutdown
        atexit.register(lambda: self.scheduler.shutdown(wait=False))
    
    def add_daily_backup(self, hour: int = 2, minute: int = 0):
        """Schedule daily backup at specified time."""
        self.scheduler.add_job(
            func=self.run_backup,
            trigger=CronTrigger(hour=hour, minute=minute),
            id='daily_backup',
            max_instances=1,  # Prevent overlap
            coalesce=True,    # Fire only once if missed
            replace_existing=True
        )
    
    def add_weekly_backup(self, day_of_week: int = 6, hour: int = 2):
        """Schedule weekly backup (0=Monday, 6=Sunday)."""
        self.scheduler.add_job(
            func=self.run_backup,
            trigger=CronTrigger(day_of_week=day_of_week, hour=hour),
            id='weekly_backup',
            max_instances=1,
            coalesce=True,
            replace_existing=True
        )
    
    def run_backup(self):
        """Execute backup job."""
        # Backup logic here
        pass
    
    def get_next_run(self) -> datetime:
        """Get next scheduled run time."""
        job = self.scheduler.get_job('daily_backup')
        return job.next_run_time if job else None
```

### Concurrency Handling

| Parameter | Purpose | Recommended Value |
|-----------|---------|-------------------|
| `max_instances` | Prevent concurrent job execution | 1 |
| `coalesce` | Fire only once after missed runs | True |
| `misfire_grace_time` | Seconds after scheduled time to still run | 3600 (1 hour) |

---

## 5. Streamlit UI Patterns

### Session State Management

Streamlit re-runs the entire script on every interaction. Use `st.session_state` for persistence.

```python
import streamlit as st
from datetime import datetime

def init_session_state():
    """Initialize session state variables."""
    if 'backup_in_progress' not in st.session_state:
        st.session_state.backup_in_progress = False
    if 'last_backup_time' not in st.session_state:
        st.session_state.last_backup_time = None
    if 'backup_history' not in st.session_state:
        st.session_state.backup_history = []
    if 'show_restore_confirm' not in st.session_state:
        st.session_state.show_restore_confirm = False

def backup_page():
    st.title("Backup & Restore")
    init_session_state()
    
    # Status display
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Last Backup", st.session_state.last_backup_time or "Never")
    with col2:
        st.metric("Total Backups", len(st.session_state.backup_history))
    with col3:
        status = "🟢 Healthy" if not st.session_state.backup_in_progress else "🟡 In Progress"
        st.metric("Status", status)
    
    # Backup button
    if st.button("Create Backup", disabled=st.session_state.backup_in_progress):
        st.session_state.backup_in_progress = True
        with st.spinner("Creating backup..."):
            # Run backup in background thread
            pass
        st.session_state.backup_in_progress = False
        st.rerun()
```

### Confirmation Modal for Destructive Operations

```python
def restore_with_confirmation(backup_id: str):
    """Show confirmation dialog before restore."""
    if not st.session_state.show_restore_confirm:
        if st.button("Restore", key=f"restore_{backup_id}"):
            st.session_state.show_restore_confirm = True
            st.session_state.pending_restore = backup_id
            st.rerun()
    else:
        st.warning("⚠️ This will overwrite current data. Are you sure?")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Yes, Restore", type="primary"):
                # Execute restore
                st.session_state.show_restore_confirm = False
                st.success("Restore completed!")
        with col2:
            if st.button("Cancel"):
                st.session_state.show_restore_confirm = False
                st.rerun()
```

### Progress Bar for Long Operations

```python
import threading
import time

class BackupProgress:
    def __init__(self):
        self.progress = 0
        self.status = "Starting..."
        
def run_backup_with_progress():
    progress = BackupProgress()
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    def backup_thread():
        for i in range(100):
            time.sleep(0.1)  # Simulate work
            progress.progress = i + 1
            progress.status = f"Processing file {i+1}/100"
    
    thread = threading.Thread(target=backup_thread)
    thread.start()
    
    while thread.is_alive():
        progress_bar.progress(progress.progress / 100)
        status_text.text(progress.status)
        time.sleep(0.1)
    
    progress_bar.progress(1.0)
    status_text.text("Backup complete!")
```

---

## 6. Testing Strategy

### pyfakefs for Filesystem Mocking

Test backup logic without touching the real disk.

```python
import pytest
from pyfakefs import fake_filesystem
from pathlib import Path

class TestBackupSystem:
    
    @pytest.fixture
    def fake_fs(self):
        """Create a fake filesystem for testing."""
        fs = fake_filesystem.FakeFilesystem()
        fake_os = fake_filesystem.FakeOsModule(fs)
        fake_path = fake_filesystem.FakePathModule(fs)
        
        # Create test structure
        fs.create_dir('/source')
        fs.create_file('/source/file1.txt', contents='content1')
        fs.create_file('/source/file2.txt', contents='content2')
        fs.create_dir('/backup')
        
        return fs
    
    def test_incremental_backup(self, fake_fs):
        """Test that incremental backup creates hard links for unchanged files."""
        # Setup
        source = Path('/source')
        backup1 = Path('/backup/backup1')
        backup2 = Path('/backup/backup2')
        
        # First backup
        perform_incremental_backup(source, backup1, None)
        
        # Second backup (no changes)
        perform_incremental_backup(source, backup2, backup1)
        
        # Verify hard link (same inode)
        assert fake_fs.get_object('/backup/backup1/file1.txt').st_ino == \
               fake_fs.get_object('/backup/backup2/file1.txt').st_ino
    
    def test_checksum_verification(self, fake_fs):
        """Test SHA-256 checksum calculation."""
        fs = fake_fs
        fs.create_file('/test/file.txt', contents='test content')
        
        checksum = generate_file_hash(Path('/test/file.txt'))
        assert len(checksum) == 64  # SHA-256 produces 64 hex chars
        assert checksum == hashlib.sha256(b'test content').hexdigest()
```

### Integration Test: Round Trip

```python
def test_backup_restore_round_trip():
    """Test complete backup and restore cycle."""
    # 1. Create source data
    source_data = {"habits": [{"id": 1, "name": "Exercise"}]}
    
    # 2. Create backup
    backup_id = backup_manager.create_backup(source_data)
    
    # 3. Verify backup exists
    assert backup_manager.backup_exists(backup_id)
    
    # 4. Modify source data
    source_data["habits"][0]["name"] = "Modified"
    
    # 5. Restore from backup
    restored_data = backup_manager.restore_backup(backup_id)
    
    # 6. Verify restored data matches original
    assert restored_data["habits"][0]["name"] == "Exercise"
```

### Streamlit AppTest

```python
from streamlit.testing.v1 import AppTest

def test_backup_ui():
    """Test Streamlit backup UI."""
    at = AppTest.from_file("tracking_app/pages/backup_restore.py")
    at.run()
    
    # Check initial state
    assert not at.button("Create Backup").disabled
    
    # Click backup button
    at.button("Create Backup").click()
    at.run()
    
    # Verify success message
    assert any("Backup completed" in str(s) for s in at.success)
```

---

## 7. Recommended Architecture

### Directory Structure

```
brain/backup/
├── __init__.py              # Package initialization
├── manager.py               # Main BackupManager class
├── scheduler.py             # APScheduler integration
├── restore.py               # Restore functionality
├── retention.py             # GFS retention policy engine
├── verifier.py              # SHA-256 checksum verification
├── manifest.py              # Backup manifest handling
└── models.py                # Data models (BackupJob, BackupSchedule)
```

### Key Implementation Priorities

| Priority | Component | Effort | Impact |
|----------|-----------|--------|--------|
| 1 | SHA-256 checksum verification | Low | High |
| 2 | GFS retention policy | Medium | High |
| 3 | APScheduler integration | Medium | High |
| 4 | Hard link deduplication | Medium | Medium |
| 5 | Streamlit UI | Medium | High |
| 6 | pyfakefs testing | Low | Medium |

---

## 8. Reference Repositories

| Repository | Key Feature | URL |
|------------|-------------|-----|
| PyHardLinkBackup | Hard link deduplication | https://github.com/jedie/PyHardLinkBackup |
| backup-warden | Retention management | https://github.com/charles-001/backup-warden |
| CTFd-Backup-Tool | Manifest patterns | https://github.com/mlgzackfly/CTFd-Backup-Tool |
| checksum-diff | Checksum comparison | https://github.com/soerenkoehler/checksum-diff |
| apscheduler | Job scheduling | https://github.com/agronholm/apscheduler |
| pyfakefs | Filesystem mocking | https://github.com/pytest-dev/pyfakefs |

---

## Cross-References

| Related Document | Content |
|------------------|---------|
| [RESEARCH_SUMMARY.md](RESEARCH_SUMMARY.md) | Overview of all research |
| [TECHNICAL_ARCHITECTURES.md](TECHNICAL_ARCHITECTURES.md) | Database patterns |
| [../phases/PHASE_5_DATA_MANAGEMENT.md](../../phases/PHASE_5_DATA_MANAGEMENT.md) | Implementation phase |

---

*Last updated: February 2026*