"""
Backup Manager

Main Python class for orchestrating backup operations.
Coordinates backup creation, verification, and storage.

All implementation is in Python 3.10+

The BackupManager implements the complete backup pipeline:
1. Create backup directory structure
2. Copy database file
3. Generate SHA-256 checksum
4. Create manifest file
5. Apply deduplication (optional)
6. Register backup in history
"""

import sqlite3
import shutil
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
import logging
import json

from brain.backup.models import (
    BackupJob,
    BackupSchedule,
    BackupManifest,
    BackupStatistics,
    BackupType,
    BackupStatus,
)
from brain.backup.verifier import BackupVerifier
from brain.backup.manifest import ManifestManager


logger = logging.getLogger(__name__)


class BackupManager:
    """
    Main backup orchestrator.
    
    Coordinates the full backup pipeline:
    1. Evaluate retention policies
    2. Archive expired records (soft delete)
    3. Purge records past recovery window
    4. Handle GDPR requests
    
    Example:
        >>> manager = BackupManager(
        ...     db_path='tracking.db',
        ...     backup_dir='backups/'
        ... )
        >>> job = manager.create_backup(user_id='user-123')
        >>> if job.status == BackupStatus.COMPLETED:
        ...     print(f"Backup: {job.file_path}")
        ...     print(f"Checksum: {job.checksum}")
    
    Attributes:
        db_path: Path to the source SQLite database
        backup_dir: Directory where backups are stored
        db: Active database connection (optional)
        verifier: BackupVerifier instance for checksums
        manifest_manager: ManifestManager for manifest handling
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
        
        # Initialize components
        self.verifier = BackupVerifier()
        self.manifest_manager = ManifestManager()
        
        # Ensure backup directory exists
        self._ensure_backup_directory()
        
        # Initialize database tables
        self._ensure_tables()
    
    def _ensure_backup_directory(self) -> None:
        """Create backup directory if it doesn't exist."""
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Backup directory: {self.backup_dir}")
    
    def _ensure_tables(self) -> None:
        """Create backup tracking tables if they don't exist."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Backup jobs table
        cursor.execute('''
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
            )
        ''')
        
        # Backup schedules table
        cursor.execute('''
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
            )
        ''')
        
        # Create indexes
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_backup_jobs_status ON backup_jobs(status)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_backup_jobs_created ON backup_jobs(created_at)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_backup_schedules_enabled ON backup_schedules(enabled)')
        
        conn.commit()
        if conn != self.db:
            conn.close()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        if self.db is not None:
            return self.db
        return sqlite3.connect(str(self.db_path))
    
    def create_backup(
        self,
        user_id: str = "default",
        backup_type: BackupType = BackupType.FULL,
        previous_backup_id: Optional[str] = None
    ) -> BackupJob:
        """
        Create a new backup.
        
        This is the main entry point for backup creation.
        It handles the complete backup pipeline.
        
        Args:
            user_id: User ID for tracking
            backup_type: FULL or INCREMENTAL
            previous_backup_id: ID of previous backup (for incremental)
            
        Returns:
            BackupJob with backup details and status
            
        Example:
            >>> job = manager.create_backup(
            ...     user_id='user-123',
            ...     backup_type=BackupType.FULL
            ... )
            >>> print(f"Backup created: {job.file_path}")
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
            self._save_job(job)
            
            # Generate backup filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_filename = f"backup_{timestamp}_{job.id[:8]}.db"
            backup_path = self.backup_dir / backup_filename
            
            # Copy database file
            logger.info(f"Copying database to {backup_path}")
            if not self.db_path.exists():
                raise FileNotFoundError(f"Database not found: {self.db_path}")
            
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
            manifest_path = self.manifest_manager.get_manifest_path(backup_path)
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
        """
        Retrieve a backup job by ID.
        
        Args:
            backup_id: Unique backup identifier
            
        Returns:
            BackupJob or None if not found
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM backup_jobs WHERE id = ?",
            (backup_id,)
        )
        
        row = cursor.fetchone()
        
        if conn != self.db:
            conn.close()
        
        if row:
            columns = [desc[0] for desc in cursor.description]
            data = dict(zip(columns, row))
            return BackupJob.from_dict(data)
        
        return None
    
    def list_backups(
        self,
        user_id: str = None,
        status: BackupStatus = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[BackupJob]:
        """
        List backup jobs with optional filtering.
        
        Args:
            user_id: Filter by user ID
            status: Filter by status
            limit: Maximum number of results
            offset: Offset for pagination
            
        Returns:
            List of BackupJob instances
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        query = "SELECT * FROM backup_jobs WHERE 1=1"
        params = []
        
        if user_id:
            query += " AND user_id = ?"
            params.append(user_id)
        
        if status:
            query += " AND status = ?"
            params.append(status.value)
        
        query += " ORDER BY created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        cursor.execute(query, params)
        rows = cursor.fetchall()
        
        if conn != self.db:
            conn.close()
        
        columns = [desc[0] for desc in cursor.description]
        return [BackupJob.from_dict(dict(zip(columns, row))) for row in rows]
    
    def delete_backup(self, backup_id: str) -> bool:
        """
        Delete a backup and its manifest.
        
        Args:
            backup_id: ID of backup to delete
            
        Returns:
            True if deleted, False if not found
        """
        job = self.get_backup(backup_id)
        
        if not job:
            return False
        
        backup_path = Path(job.file_path) if job.file_path else None
        
        # Delete backup file
        if backup_path and backup_path.exists():
            backup_path.unlink()
            logger.info(f"Deleted backup file: {backup_path}")
        
        # Delete manifest
        if backup_path:
            self.manifest_manager.delete(backup_path)
        
        # Delete from database
        conn = self._get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM backup_jobs WHERE id = ?", (backup_id,))
        
        if conn != self.db:
            conn.commit()
            conn.close()
        
        logger.info(f"Deleted backup job: {backup_id}")
        return True
    
    def verify_backup(self, backup_id: str) -> bool:
        """
        Verify backup integrity using checksum.
        
        Args:
            backup_id: ID of backup to verify
            
        Returns:
            True if verification passed, False otherwise
        """
        job = self.get_backup(backup_id)
        
        if not job or not job.file_path:
            return False
        
        backup_path = Path(job.file_path)
        
        if not backup_path.exists():
            logger.error(f"Backup file not found: {backup_path}")
            return False
        
        # Verify checksum
        verified = self.verifier.verify(backup_path, job.checksum)
        
        if verified:
            # Update verified timestamp
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute(
                "UPDATE backup_jobs SET verified_at = ? WHERE id = ?",
                (datetime.now().isoformat(), backup_id)
            )
            
            if conn != self.db:
                conn.commit()
                conn.close()
            
            job.verified_at = datetime.now()
            job.status = BackupStatus.VERIFIED
            logger.info(f"Backup verified: {backup_id}")
        
        return verified
    
    def get_statistics(self) -> BackupStatistics:
        """
        Get backup system statistics.
        
        Returns:
            BackupStatistics with current state
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        stats = BackupStatistics()
        
        # Total backups
        cursor.execute("SELECT COUNT(*) FROM backup_jobs")
        stats.total_backups = cursor.fetchone()[0]
        
        # Total size
        cursor.execute("SELECT SUM(file_size_bytes) FROM backup_jobs")
        result = cursor.fetchone()[0]
        stats.total_size_bytes = result if result else 0
        
        # Successful/failed counts
        cursor.execute(
            "SELECT COUNT(*) FROM backup_jobs WHERE status = ?",
            (BackupStatus.COMPLETED.value,)
        )
        stats.successful_backups = cursor.fetchone()[0]
        
        cursor.execute(
            "SELECT COUNT(*) FROM backup_jobs WHERE status = ?",
            (BackupStatus.FAILED.value,)
        )
        stats.failed_backups = cursor.fetchone()[0]
        
        # Oldest/newest
        cursor.execute(
            "SELECT MIN(completed_at) FROM backup_jobs WHERE completed_at IS NOT NULL"
        )
        result = cursor.fetchone()[0]
        stats.oldest_backup = datetime.fromisoformat(result) if result else None
        
        cursor.execute(
            "SELECT MAX(completed_at) FROM backup_jobs WHERE completed_at IS NOT NULL"
        )
        result = cursor.fetchone()[0]
        stats.newest_backup = datetime.fromisoformat(result) if result else None
        
        # Last backup status
        cursor.execute('''
            SELECT status FROM backup_jobs 
            WHERE completed_at IS NOT NULL 
            ORDER BY completed_at DESC LIMIT 1
        ''')
        result = cursor.fetchone()
        if result:
            stats.last_backup_status = BackupStatus(result[0])
        
        if conn != self.db:
            conn.close()
        
        return stats
    
    def _count_records(self, db_path: Path) -> int:
        """
        Count total records in database.
        
        Args:
            db_path: Path to SQLite database
            
        Returns:
            Total record count across all tables
        """
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        # Get all tables
        cursor.execute(
            "SELECT name FROM sqlite_master WHERE type='table' "
            "AND name NOT LIKE 'sqlite_%'"
        )
        tables = [row[0] for row in cursor.fetchall()]
        
        total = 0
        for table in tables:
            try:
                cursor.execute(f"SELECT COUNT(*) FROM {table}")
                total += cursor.fetchone()[0]
            except Exception:
                pass
        
        conn.close()
        return total
    
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
    
    def _save_job(self, job: BackupJob) -> None:
        """
        Save backup job to history database.
        
        Args:
            job: BackupJob to save
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        data = job.to_dict()
        
        cursor.execute('''
            INSERT OR REPLACE INTO backup_jobs (
                id, user_id, backup_type, status, file_path,
                file_size_bytes, checksum, record_count,
                previous_backup_id, started_at, completed_at,
                verified_at, expires_at, error_message, metadata
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['id'],
            data['user_id'],
            data['backup_type'],
            data['status'],
            data['file_path'],
            data['file_size_bytes'],
            data['checksum'],
            data['record_count'],
            data['previous_backup_id'],
            data['started_at'],
            data['completed_at'],
            data['verified_at'],
            data['expires_at'],
            data['error_message'],
            data['metadata'],
        ))
        
        if conn != self.db:
            conn.commit()
            conn.close()
    
    def cleanup_old_backups(self, keep_count: int = 10) -> int:
        """
        Remove old backups beyond retention limit.
        
        Args:
            keep_count: Number of recent backups to keep
            
        Returns:
            Number of backups deleted
        """
        backups = self.list_backups(limit=1000)
        
        if len(backups) <= keep_count:
            return 0
        
        # Sort by date, keep most recent
        backups.sort(key=lambda b: b.completed_at or datetime.min, reverse=True)
        
        to_delete = backups[keep_count:]
        deleted = 0
        
        for backup in to_delete:
            if self.delete_backup(backup.id):
                deleted += 1
        
        logger.info(f"Cleaned up {deleted} old backups")
        return deleted