"""
Lifecycle Manager

Main orchestrator for data lifecycle management.
Coordinates retention, archive, purge, and recovery operations.

All implementation is in Python 3.10+
"""

import sqlite3
from datetime import datetime
from typing import Optional, List, Dict, Any
import logging
from pathlib import Path

from brain.lifecycle.models import (
    RetentionPolicy,
    DeletedRecord,
    DataReset,
    ErasureRequest,
    LifecycleJob,
    LifecycleResult,
    ResetType,
    ErasureStatus,
)
from brain.lifecycle.retention import RetentionEngine
from brain.lifecycle.archive import ArchiveManager
from brain.lifecycle.purge import PurgeManager
from brain.lifecycle.recovery import RecoveryManager


logger = logging.getLogger(__name__)


class LifecycleManager:
    """
    Main orchestrator for data lifecycle management.
    
    Coordinates all lifecycle operations:
    - Retention policy evaluation and enforcement
    - Soft delete with recovery window
    - Permanent purge of expired records
    - Recovery of soft-deleted records
    - GDPR compliance operations
    
    Example:
        manager = LifecycleManager('tracking.db')
        
        # Apply all retention policies
        result = manager.apply_retention_policies()
        
        # Archive a specific record
        deleted = manager.archive_entity('tasks', 'task-123')
        
        # Recover within 30-day window
        manager.recover_entity('tasks', 'task-123')
    """
    
    def __init__(
        self,
        db_path: str = None,
        db_connection: sqlite3.Connection = None,
        recovery_days: int = 30
    ):
        """
        Initialize lifecycle manager.
        
        Args:
            db_path: Path to SQLite database
            db_connection: Existing database connection (takes precedence)
            recovery_days: Number of days for recovery window
        """
        self.db_path = db_path
        self._external_db = db_connection is not None
        
        if db_connection:
            self.db = db_connection
        elif db_path:
            self.db = sqlite3.connect(db_path)
        else:
            self.db = None
        
        # Initialize components
        self.retention = RetentionEngine(self.db)
        self.archive = ArchiveManager(self.db, recovery_days)
        self.purge = PurgeManager(self.db)
        self.recovery = RecoveryManager(self.db)
        
        # Ensure tables exist
        self._ensure_tables()
    
    def _ensure_tables(self) -> None:
        """Create required tables if they don't exist."""
        if self.db is None:
            return
        
        cursor = self.db.cursor()
        
        # Retention policies table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS retention_policies (
                id TEXT PRIMARY KEY,
                entity_type TEXT UNIQUE NOT NULL,
                archive_after_days INTEGER,
                delete_after_days INTEGER,
                enabled INTEGER DEFAULT 1,
                cascade_to TEXT,
                created_at TEXT,
                updated_at TEXT
            )
        ''')
        
        # Deleted records table (for recovery)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS deleted_records (
                id TEXT PRIMARY KEY,
                entity_type TEXT NOT NULL,
                entity_id TEXT NOT NULL,
                original_data TEXT,
                deleted_at TEXT,
                recovery_until TEXT,
                purge_status TEXT DEFAULT 'recoverable',
                cascade_source TEXT,
                deletion_reason TEXT,
                deleted_by TEXT
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
                started_at TEXT,
                completed_at TEXT,
                error_message TEXT,
                created_at TEXT
            )
        ''')
        
        # Data reset tracking
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS data_resets (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                reset_type TEXT,
                modules TEXT,
                backup_created INTEGER,
                backup_id TEXT,
                status TEXT,
                records_affected INTEGER,
                started_at TEXT,
                completed_at TEXT,
                error_message TEXT,
                confirmation_token TEXT,
                created_at TEXT
            )
        ''')
        
        # GDPR erasure requests
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS erasure_requests (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                status TEXT,
                requested_at TEXT,
                verified_at TEXT,
                grace_period_until TEXT,
                executed_at TEXT,
                data_export_path TEXT,
                verification_token TEXT,
                cancellation_reason TEXT,
                created_at TEXT
            )
        ''')
        
        self.db.commit()
    
    def apply_retention_policies(self) -> LifecycleResult:
        """
        Apply all enabled retention policies.
        
        Archives records past archive threshold.
        Purges records past delete threshold.
        
        Returns:
            LifecycleResult with operation statistics
        """
        result = LifecycleResult(operation="apply_retention_policies")
        start_time = datetime.now()
        
        try:
            # Create job record
            job = LifecycleJob(
                job_type="retention_enforcement",
                status="running",
                started_at=start_time
            )
            self._save_job(job)
            
            # Get all enabled policies
            policies = self.retention.get_all_policies(enabled_only=True)
            
            for policy in policies:
                # Archive expired records
                archived = self.archive.archive_expired(policy)
                result.records_archived += archived
                
                # Purge records past recovery window
                purged = self.purge.purge_expired(policy)
                result.records_purged += purged
            
            result.success = True
            result.records_affected = result.records_archived + result.records_purged
            
            # Update job
            job.status = "completed"
            job.completed_at = datetime.now()
            job.records_archived = result.records_archived
            job.records_purged = result.records_purged
            job.records_processed = result.records_affected
            job.duration_seconds = (datetime.now() - start_time).total_seconds()
            self._update_job(job)
            
        except Exception as e:
            result.error_message = str(e)
            logger.error(f"Retention policy enforcement failed: {e}")
        
        return result
    
    def archive_entity(
        self,
        entity_type: str,
        entity_id: str,
        reason: str = "user",
        user_id: str = ""
    ) -> DeletedRecord:
        """
        Archive (soft delete) an entity.
        
        Args:
            entity_type: Type of entity
            entity_id: ID of entity
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
            entity_id: ID of entity
            
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
        
        Only works if recovery window has expired.
        
        Args:
            entity_type: Type of entity
            entity_id: ID of entity
            
        Returns:
            LifecycleResult with purge status
        """
        return self.purge.purge(entity_type, entity_id)
    
    def get_retention_policy(self, entity_type: str) -> Optional[RetentionPolicy]:
        """Get retention policy for an entity type."""
        return self.retention.get_policy(entity_type)
    
    def update_retention_policy(self, policy: RetentionPolicy) -> None:
        """Update or create a retention policy."""
        self.retention.update_policy(policy)
    
    def list_deleted_records(
        self,
        entity_type: str = None,
        recoverable_only: bool = True
    ) -> List[DeletedRecord]:
        """List soft-deleted records."""
        return self.archive.list_deleted(entity_type, recoverable_only)
    
    def count_recoverable(self, entity_type: str = None) -> int:
        """Count recoverable records."""
        return self.archive.count_recoverable(entity_type)
    
    def run_cleanup(self) -> LifecycleResult:
        """
        Run scheduled cleanup.
        
        Purges all records past recovery window.
        
        Returns:
            LifecycleResult with cleanup statistics
        """
        result = LifecycleResult(operation="cleanup")
        start_time = datetime.now()
        
        try:
            # Purge expired records
            purged = self.purge.purge_expired()
            result.records_purged = purged
            result.records_affected = purged
            result.success = True
            
        except Exception as e:
            result.error_message = str(e)
            logger.error(f"Cleanup failed: {e}")
        
        result.duration_seconds = (datetime.now() - start_time).total_seconds()
        return result
    
    def _save_job(self, job: LifecycleJob) -> None:
        """Save job record to database."""
        if self.db is None:
            return
        
        cursor = self.db.cursor()
        cursor.execute('''
            INSERT INTO lifecycle_jobs
            (id, job_type, entity_type, status, started_at, created_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            job.id,
            job.job_type,
            job.entity_type,
            job.status,
            job.started_at.isoformat() if job.started_at else None,
            job.created_at.isoformat()
        ))
        self.db.commit()
    
    def _update_job(self, job: LifecycleJob) -> None:
        """Update job record in database."""
        if self.db is None:
            return
        
        cursor = self.db.cursor()
        cursor.execute('''
            UPDATE lifecycle_jobs SET
                records_processed = ?,
                records_archived = ?,
                records_purged = ?,
                records_recovered = ?,
                duration_seconds = ?,
                status = ?,
                completed_at = ?
            WHERE id = ?
        ''', (
            job.records_processed,
            job.records_archived,
            job.records_purged,
            job.records_recovered,
            job.duration_seconds,
            job.status,
            job.completed_at.isoformat() if job.completed_at else None,
            job.id
        ))
        self.db.commit()
    
    def close(self) -> None:
        """Close database connection if we own it."""
        if self.db and not self._external_db:
            self.db.close()