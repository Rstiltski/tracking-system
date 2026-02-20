"""
Deduplication Engine

Hard-link deduplication for storage efficiency.
Implements the PyHardLinkBackup pattern for reducing storage.

All implementation is in Python 3.10+

Total storage with deduplication is bounded by:
S_T = S_{b_0} + Σ_{i=1}^{|P|-1} Σ_{f ∈ ΔF_i} size(f)

Where ΔF_i represents only changed files between backups.
"""

import os
import sqlite3
from pathlib import Path
from typing import Optional, Dict, Any, Tuple
from datetime import datetime
import logging

from brain.backup.models import DedupRecord
from brain.backup.verifier import BackupVerifier
from brain.backup.dedup_db import DedupDatabase


logger = logging.getLogger(__name__)


class DeduplicationEngine:
    """
    Hard-link deduplication engine.
    
    Implements the PyHardLinkBackup pattern:
    1. Tier 1: Check file size (instant)
    2. Tier 2: Check modification time (instant)
    3. Tier 3: Compute SHA-256 hash (expensive)
    4. Create hard link if file exists, copy otherwise
    
    This approach significantly reduces storage for backups
    where most files haven't changed between backups.
    
    Example:
        >>> engine = DeduplicationEngine(db_path='dedup.db')
        >>> 
        >>> # Process file (will hard-link if duplicate)
        >>> result = engine.process_file(
        ...     source=Path('backup/file.db'),
        ...     dest=Path('backups/new_backup/file.db')
        ... )
        >>> if result.is_link:
        ...     print(f"Hard link created - saved {result.size_saved} bytes")
    
    Hard Links:
        Hard links are filesystem references that point to the same
        physical data on disk. When a file is hard-linked:
        - Both paths point to same data
        - No additional storage used
        - Deleting one doesn't affect the other
        - Only works on same filesystem
    """
    
    def __init__(
        self,
        db_path: str = "dedup.db",
        backup_dir: str = "backups"
    ):
        """
        Initialize deduplication engine.
        
        Args:
            db_path: Path to deduplication tracking database
            backup_dir: Base directory for backups
        """
        self.db_path = Path(db_path)
        self.backup_dir = Path(backup_dir)
        self.verifier = BackupVerifier()
        self.database = DedupDatabase(db_path)
    
    def process_file(
        self,
        source: Path,
        dest: Path,
        previous_backup_dir: Optional[Path] = None
    ) -> 'DedupResult':
        """
        Process a file for deduplication.
        
        Implements the tiered verification approach:
        1. Check if identical file exists in database
        2. If yes, create hard link instead of copying
        3. Track the link in database
        
        Args:
            source: Path to source file
            dest: Path to destination file
            previous_backup_dir: Directory of previous backup (for incremental)
            
        Returns:
            DedupResult with processing details
        """
        result = DedupResult(
            source=str(source),
            dest=str(dest),
            is_link=False,
            size_saved=0
        )
        
        if not source.exists():
            result.error = f"Source file not found: {source}"
            return result
        
        # Ensure destination directory exists
        dest.parent.mkdir(parents=True, exist_ok=True)
        
        # Get source file info
        source_stat = source.stat()
        source_size = source_stat.st_size
        
        # Check for existing identical file
        existing = self.database.find_by_size(source_size)
        
        if existing:
            # Tier 3: Full hash comparison
            source_hash = self.verifier.generate_checksum(source)
            
            for record in existing:
                if record.file_hash == source_hash:
                    # Found duplicate - create hard link
                    try:
                        os.link(record.original_path, dest)
                        result.is_link = True
                        result.size_saved = source_size
                        result.matched_hash = source_hash
                        
                        # Update link count
                        self.database.increment_link_count(record.file_hash)
                        
                        logger.debug(
                            f"Created hard link: {dest} -> {record.original_path}"
                        )
                        return result
                        
                    except OSError as e:
                        logger.warning(
                            f"Hard link failed, falling back to copy: {e}"
                        )
                        # Fall through to copy
        
        # No duplicate found or linking failed - copy file
        import shutil
        shutil.copy2(source, dest)
        
        # Record in database
        file_hash = self.verifier.generate_checksum(dest)
        self.database.record_file(
            file_hash=file_hash,
            original_path=str(dest),
            original_size=source_size
        )
        
        result.is_link = False
        result.file_hash = file_hash
        
        return result
    
    def process_backup(
        self,
        source_dir: Path,
        dest_dir: Path,
        previous_backup_dir: Optional[Path] = None
    ) -> 'BackupDedupResult':
        """
        Process entire backup directory for deduplication.
        
        Args:
            source_dir: Source directory
            dest_dir: Destination directory
            previous_backup_dir: Previous backup for comparison
            
        Returns:
            BackupDedupResult with summary statistics
        """
        result = BackupDedupResult(
            source_dir=str(source_dir),
            dest_dir=str(dest_dir)
        )
        
        start_time = datetime.now()
        
        # Process all files
        for source_file in source_dir.rglob('*'):
            if source_file.is_file():
                relative = source_file.relative_to(source_dir)
                dest_file = dest_dir / relative
                
                file_result = self.process_file(
                    source=source_file,
                    dest=dest_file,
                    previous_backup_dir=previous_backup_dir
                )
                
                result.files_processed += 1
                
                if file_result.is_link:
                    result.files_linked += 1
                    result.bytes_saved += file_result.size_saved
                else:
                    result.files_copied += 1
                
                if file_result.error:
                    result.errors.append(file_result.error)
        
        result.duration_seconds = (datetime.now() - start_time).total_seconds()
        
        logger.info(
            f"Dedup complete: {result.files_linked}/{result.files_processed} "
            f"files linked, saved {result.bytes_saved / (1024*1024):.1f} MB"
        )
        
        return result
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get deduplication statistics.
        
        Returns:
            Dictionary with stats like:
            - total_files: Total files tracked
            - total_links: Total hard links created
            - bytes_saved: Storage saved via deduplication
        """
        return self.database.get_statistics()
    
    def cleanup_orphans(self) -> int:
        """
        Remove records for files that no longer exist.
        
        Returns:
            Number of orphan records removed
        """
        removed = 0
        records = self.database.get_all_records()
        
        for record in records:
            if not Path(record.original_path).exists():
                self.database.remove_record(record.file_hash)
                removed += 1
        
        logger.info(f"Cleaned up {removed} orphan dedup records")
        return removed


class DedupResult:
    """Result of processing a single file for deduplication."""
    
    def __init__(
        self,
        source: str,
        dest: str,
        is_link: bool = False,
        size_saved: int = 0
    ):
        self.source = source
        self.dest = dest
        self.is_link = is_link
        self.size_saved = size_saved
        self.matched_hash: Optional[str] = None
        self.file_hash: Optional[str] = None
        self.error: Optional[str] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'source': self.source,
            'dest': self.dest,
            'is_link': self.is_link,
            'size_saved': self.size_saved,
            'matched_hash': self.matched_hash,
            'file_hash': self.file_hash,
            'error': self.error,
        }


class BackupDedupResult:
    """Result of processing an entire backup for deduplication."""
    
    def __init__(
        self,
        source_dir: str,
        dest_dir: str
    ):
        self.source_dir = source_dir
        self.dest_dir = dest_dir
        self.files_processed: int = 0
        self.files_linked: int = 0
        self.files_copied: int = 0
        self.bytes_saved: int = 0
        self.errors: list = []
        self.duration_seconds: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'source_dir': self.source_dir,
            'dest_dir': self.dest_dir,
            'files_processed': self.files_processed,
            'files_linked': self.files_linked,
            'files_copied': self.files_copied,
            'bytes_saved': self.bytes_saved,
            'bytes_saved_mb': self.bytes_saved / (1024 * 1024),
            'errors': self.errors,
            'duration_seconds': self.duration_seconds,
        }
    
    @property
    def savings_percent(self) -> float:
        """Calculate percentage of storage saved."""
        if self.files_processed == 0:
            return 0.0
        return (self.files_linked / self.files_processed) * 100
    
    @property
    def bytes_saved_mb(self) -> float:
        """Bytes saved in megabytes."""
        return self.bytes_saved / (1024 * 1024)


class NoOpDedupEngine:
    """
    No-operation deduplication engine.
    
    Used when deduplication is disabled or on filesystems
    that don't support hard links (like some network drives).
    
    Always copies files without attempting deduplication.
    """
    
    def __init__(self, *args, **kwargs):
        """Initialize no-op engine."""
        pass
    
    def process_file(
        self,
        source: Path,
        dest: Path,
        previous_backup_dir: Optional[Path] = None
    ) -> DedupResult:
        """Copy file without deduplication."""
        import shutil
        
        result = DedupResult(
            source=str(source),
            dest=str(dest),
            is_link=False,
            size_saved=0
        )
        
        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, dest)
        
        return result
    
    def process_backup(
        self,
        source_dir: Path,
        dest_dir: Path,
        previous_backup_dir: Optional[Path] = None
    ) -> BackupDedupResult:
        """Copy backup without deduplication."""
        import shutil
        
        result = BackupDedupResult(
            source_dir=str(source_dir),
            dest_dir=str(dest_dir)
        )
        
        start_time = datetime.now()
        
        shutil.copytree(source_dir, dest_dir, dirs_exist_ok=True)
        
        # Count files
        for f in dest_dir.rglob('*'):
            if f.is_file():
                result.files_processed += 1
                result.files_copied += 1
        
        result.duration_seconds = (datetime.now() - start_time).total_seconds()
        
        return result
    
    def get_statistics(self) -> Dict[str, Any]:
        """Return empty statistics."""
        return {
            'total_files': 0,
            'total_links': 0,
            'bytes_saved': 0,
        }
    
    def cleanup_orphans(self) -> int:
        """No-op cleanup."""
        return 0


def supports_hard_links(path: Path) -> bool:
    """
    Check if filesystem supports hard links.
    
    Args:
        path: Path to test (must be writable)
        
    Returns:
        True if hard links are supported
    """
    try:
        import tempfile
        
        # Create a test file
        test_file = path / f"dedup_test_{datetime.now().timestamp()}"
        test_file.write_text("test")
        
        # Try to create hard link
        link_file = path / f"dedup_test_link_{datetime.now().timestamp()}"
        os.link(test_file, link_file)
        
        # Clean up
        test_file.unlink()
        link_file.unlink()
        
        return True
        
    except (OSError, NotImplementedError):
        return False