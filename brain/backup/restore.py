"""
Restore Engine

Database restoration with pre-restore validation.
Implements safe restore workflow with checksum verification.

All implementation is in Python 3.10+

The restore process follows these steps:
1. Validate backup integrity (checksum verification)
2. Create safety backup of current database
3. Perform restoration
4. Verify restored database
5. Rollback on failure
"""

import sqlite3
import shutil
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import logging

from brain.backup.models import BackupJob, RestoreResult, BackupStatus
from brain.backup.verifier import BackupVerifier
from brain.backup.manifest import ManifestManager


logger = logging.getLogger(__name__)


class RestoreEngine:
    """
    Safe database restoration engine.
    
    Implements a safe restore workflow:
    1. Validate backup exists and has valid checksum
    2. Create safety backup of current database
    3. Restore the backup
    4. Verify the restored database
    5. Rollback to safety backup if verification fails
    
    Example:
        >>> engine = RestoreEngine()
        >>> result = engine.restore(
        ...     backup_path=Path('backups/backup_20240101.db'),
        ...     target_path=Path('tracking.db')
        ... )
        >>> if result.success:
        ...     print(f"Restored {result.records_restored} records")
    """
    
    def __init__(
        self,
        verify_checksum: bool = True,
        create_safety_backup: bool = True
    ):
        """
        Initialize restore engine.
        
        Args:
            verify_checksum: Whether to verify checksums before restore
            create_safety_backup: Whether to backup current DB before restore
        """
        self.verify_checksum = verify_checksum
        self.create_safety_backup = create_safety_backup
        self.verifier = BackupVerifier()
        self.manifest_manager = ManifestManager()
    
    def restore(
        self,
        backup_path: Path,
        target_path: Path,
        expected_checksum: Optional[str] = None
    ) -> RestoreResult:
        """
        Restore database from backup file.
        
        Args:
            backup_path: Path to backup file
            target_path: Path to restore to
            expected_checksum: Optional expected checksum for verification
            
        Returns:
            RestoreResult with outcome details
        """
        result = RestoreResult(
            backup_id="",
            records_restored=0,
            tables_restored=0
        )
        
        start_time = datetime.now()
        safety_backup_path: Optional[Path] = None
        
        try:
            # Step 1: Validate backup exists
            if not backup_path.exists():
                raise FileNotFoundError(f"Backup not found: {backup_path}")
            
            # Step 2: Verify checksum if provided
            if self.verify_checksum and expected_checksum:
                if not self.verifier.verify(backup_path, expected_checksum):
                    raise ValueError("Backup checksum verification failed")
                result.checksum_verified = True
            
            # Step 3: Create safety backup of current database
            if self.create_safety_backup and target_path.exists():
                safety_backup_path = self._create_safety_backup(target_path)
                result.details['safety_backup'] = str(safety_backup_path)
            
            # Step 4: Perform restore
            logger.info(f"Restoring {backup_path} to {target_path}")
            
            # Ensure target directory exists
            target_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy backup to target
            shutil.copy2(backup_path, target_path)
            
            # Step 5: Verify restored database
            if not self._verify_restored_database(target_path):
                raise ValueError("Restored database verification failed")
            
            # Step 6: Count records
            counts = self._get_table_counts(target_path)
            result.records_restored = sum(counts.values())
            result.tables_restored = len(counts)
            result.details['table_counts'] = counts
            
            # Success
            result.success = True
            logger.info(
                f"Restore completed: {result.records_restored} records "
                f"across {result.tables_restored} tables"
            )
            
        except Exception as e:
            result.success = False
            result.error_message = str(e)
            logger.error(f"Restore failed: {e}")
            
            # Attempt rollback
            if safety_backup_path and safety_backup_path.exists():
                logger.info("Attempting rollback to safety backup")
                try:
                    shutil.copy2(safety_backup_path, target_path)
                    result.details['rollback'] = True
                    logger.info("Rollback successful")
                except Exception as rollback_error:
                    result.details['rollback_error'] = str(rollback_error)
                    logger.error(f"Rollback failed: {rollback_error}")
        
        finally:
            # Clean up safety backup
            if safety_backup_path and safety_backup_path.exists():
                try:
                    safety_backup_path.unlink()
                    logger.debug(f"Cleaned up safety backup: {safety_backup_path}")
                except Exception:
                    pass
        
        result.duration_seconds = (datetime.now() - start_time).total_seconds()
        return result
    
    def restore_from_job(
        self,
        job: BackupJob,
        target_path: Optional[Path] = None
    ) -> RestoreResult:
        """
        Restore database from a BackupJob.
        
        Convenience method that extracts paths from the job.
        
        Args:
            job: BackupJob to restore from
            target_path: Target path (default: original db path)
            
        Returns:
            RestoreResult with outcome details
        """
        backup_path = Path(job.file_path) if job.file_path else None
        
        if not backup_path or not backup_path.exists():
            return RestoreResult(
                success=False,
                backup_id=job.id,
                error_message=f"Backup file not found: {job.file_path}"
            )
        
        result = self.restore(
            backup_path=backup_path,
            target_path=target_path or backup_path.parent.parent / "tracking.db",
            expected_checksum=job.checksum
        )
        
        result.backup_id = job.id
        return result
    
    def _create_safety_backup(self, db_path: Path) -> Path:
        """
        Create a safety backup before restore.
        
        Args:
            db_path: Path to database to backup
            
        Returns:
            Path to safety backup
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        safety_path = db_path.with_suffix(f".safety_{timestamp}.db")
        
        shutil.copy2(db_path, safety_path)
        logger.info(f"Created safety backup: {safety_path}")
        
        return safety_path
    
    def _verify_restored_database(self, db_path: Path) -> bool:
        """
        Verify restored database is valid SQLite.
        
        Args:
            db_path: Path to restored database
            
        Returns:
            True if database is valid
        """
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Run integrity check
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()
            
            conn.close()
            
            if result[0] == 'ok':
                logger.debug("Database integrity check passed")
                return True
            else:
                logger.error(f"Database integrity check failed: {result[0]}")
                return False
                
        except Exception as e:
            logger.error(f"Database verification failed: {e}")
            return False
    
    def _get_table_counts(self, db_path: Path) -> Dict[str, int]:
        """
        Get record counts per table.
        
        Args:
            db_path: Path to SQLite database
            
        Returns:
            Dictionary mapping table names to row counts
        """
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' "
            "AND name NOT LIKE 'sqlite_%'"
        )
        tables = [row[0] for row in cursor.fetchall()]
        
        counts = {}
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                counts[table] = cursor.fetchone()[0]
            except Exception:
                counts[table] = 0
        
        conn.close()
        return counts


class RestorePlanner:
    """
    Plans restore operations for incremental backup chains.
    
    For incremental backups, determines the correct restore sequence
    by walking the chain back to the parent full backup.
    
    Example:
        >>> planner = RestorePlanner()
        >>> plan = planner.create_restore_plan(latest_backup, backup_manager)
        >>> for step in plan.steps:
        ...     print(f"Restore {step.backup_id} ({step.backup_type})")
    """
    
    def create_restore_plan(
        self,
        target_backup: BackupJob,
        backup_manager
    ) -> 'RestorePlan':
        """
        Create a restore plan for a target backup.
        
        For incremental backups, includes all parent backups
        that need to be restored first.
        
        Args:
            target_backup: The backup to restore
            backup_manager: BackupManager for looking up backups
            
        Returns:
            RestorePlan with ordered restore steps
        """
        steps = []
        current = target_backup
        
        # Walk back through chain
        while current:
            steps.append(RestoreStep(
                backup_id=current.id,
                backup_type=current.backup_type.value,
                file_path=current.file_path or "",
                checksum=current.checksum or "",
                position=len(steps)
            ))
            
            if current.previous_backup_id:
                current = backup_manager.get_backup(current.previous_backup_id)
            else:
                current = None
        
        # Reverse to get correct order (full backup first)
        steps.reverse()
        
        # Update positions
        for i, step in enumerate(steps):
            step.position = i
        
        return RestorePlan(
            target_backup_id=target_backup.id,
            steps=steps,
            requires_incremental_restore=len(steps) > 1
        )


class RestoreStep:
    """A single step in a restore plan."""
    
    def __init__(
        self,
        backup_id: str,
        backup_type: str,
        file_path: str,
        checksum: str,
        position: int = 0
    ):
        self.backup_id = backup_id
        self.backup_type = backup_type
        self.file_path = file_path
        self.checksum = checksum
        self.position = position
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'backup_id': self.backup_id,
            'backup_type': self.backup_type,
            'file_path': self.file_path,
            'checksum': self.checksum,
            'position': self.position,
        }


class RestorePlan:
    """Complete restore plan with ordered steps."""
    
    def __init__(
        self,
        target_backup_id: str,
        steps: list,
        requires_incremental_restore: bool = False
    ):
        self.target_backup_id = target_backup_id
        self.steps = steps
        self.requires_incremental_restore = requires_incremental_restore
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'target_backup_id': self.target_backup_id,
            'steps': [s.to_dict() for s in self.steps],
            'requires_incremental_restore': self.requires_incremental_restore,
            'total_steps': len(self.steps),
        }
    
    def __len__(self) -> int:
        """Return number of steps."""
        return len(self.steps)


def preview_restore(
    backup_path: Path,
    target_path: Path
) -> Dict[str, Any]:
    """
    Preview a restore operation without executing.
    
    Provides information about what would be restored.
    
    Args:
        backup_path: Path to backup file
        target_path: Target path for restore
        
    Returns:
        Dictionary with preview information
    """
    preview = {
        'backup_exists': backup_path.exists(),
        'target_exists': target_path.exists(),
        'backup_size_bytes': 0,
        'backup_size_mb': 0,
        'tables': {},
        'total_records': 0,
        'can_restore': False,
    }
    
    if not backup_path.exists():
        preview['error'] = f"Backup not found: {backup_path}"
        return preview
    
    try:
        # Get backup info
        preview['backup_size_bytes'] = backup_path.stat().st_size
        preview['backup_size_mb'] = preview['backup_size_bytes'] / (1024 * 1024)
        
        # Get table counts
        conn = sqlite3.connect(str(backup_path))
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' "
            "AND name NOT LIKE 'sqlite_%'"
        )
        tables = [row[0] for row in cursor.fetchall()]
        
        for table in tables:
            cursor.execute(f"SELECT COUNT(*) FROM {table}")
            preview['tables'][table] = cursor.fetchone()[0]
        
        conn.close()
        
        preview['total_records'] = sum(preview['tables'].values())
        preview['can_restore'] = True
        
    except Exception as e:
        preview['error'] = str(e)
    
    return preview