"""
Archive Manager

Soft delete functionality with recovery window.
Records are archived (marked deleted) but recoverable for 30 days.

All implementation is in Python 3.10+
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Optional, List
import json
import logging

from brain.lifecycle.models import (
    DeletedRecord,
    PurgeStatus,
    LifecycleResult,
    RetentionPolicy
)


logger = logging.getLogger(__name__)


# Default recovery window in days
DEFAULT_RECOVERY_DAYS = 30


class ArchiveManager:
    """
    Manages soft deletion of records.
    
    Instead of immediate deletion, records are:
    1. Copied to deleted_records table
    2. Original is deleted from source table
    3. Record is recoverable for 30 days
    
    Example:
        manager = ArchiveManager(db_connection)
        
        # Archive a record
        deleted = manager.archive('tasks', 'task-123')
        
        # Check if recoverable
        if deleted.is_recoverable():
            print("Can be recovered")
    """
    
    def __init__(
        self,
        db_connection: sqlite3.Connection = None,
        recovery_days: int = DEFAULT_RECOVERY_DAYS
    ):
        """
        Initialize archive manager.
        
        Args:
            db_connection: SQLite database connection
            recovery_days: Number of days records are recoverable
        """
        self.db = db_connection
        self.recovery_days = recovery_days
    
    def archive(
        self,
        entity_type: str,
        entity_id: str,
        reason: str = "user",
        user_id: str = ""
    ) -> DeletedRecord:
        """
        Archive a record (soft delete).
        
        Args:
            entity_type: Type of entity
            entity_id: ID of entity
            reason: Reason for deletion
            user_id: User who initiated deletion
            
        Returns:
            DeletedRecord tracking the deletion
        """
        # Get original record
        original = self._get_record(entity_type, entity_id)
        if not original:
            raise ValueError(f"Record not found: {entity_type}/{entity_id}")
        
        # Create deleted record
        deleted = DeletedRecord(
            entity_type=entity_type,
            entity_id=entity_id,
            original_data=original,
            recovery_until=datetime.now() + timedelta(days=self.recovery_days),
            purge_status=PurgeStatus.RECOVERABLE,
            deletion_reason=reason,
            deleted_by=user_id
        )
        
        # Save to deleted_records
        self._save_deleted_record(deleted)
        
        # Delete from source table
        self._delete_from_source(entity_type, entity_id)
        
        logger.info(f"Archived {entity_type}/{entity_id}, recoverable until {deleted.recovery_until}")
        
        return deleted
    
    def archive_expired(self, policy: RetentionPolicy) -> int:
        """
        Archive all records past retention threshold.
        
        Args:
            policy: RetentionPolicy to apply
            
        Returns:
            Number of records archived
        """
        if self.db is None:
            return 0
        
        archived_count = 0
        threshold = datetime.now() - timedelta(days=policy.archive_after_days)
        table_name = self._get_table_name(policy.entity_type)
        
        try:
            cursor = self.db.cursor()
            
            # Get records to archive
            cursor.execute(
                f"SELECT id FROM {table_name} WHERE created_at < ?",
                (threshold.isoformat(),)
            )
            
            record_ids = [row[0] for row in cursor.fetchall()]
            
            # Archive each record
            for record_id in record_ids:
                try:
                    self.archive(
                        policy.entity_type,
                        str(record_id),
                        reason="retention",
                        user_id="system"
                    )
                    archived_count += 1
                except Exception as e:
                    logger.warning(f"Failed to archive {policy.entity_type}/{record_id}: {e}")
            
            if archived_count > 0:
                logger.info(f"Archived {archived_count} {policy.entity_type} records")
            
        except Exception as e:
            logger.error(f"Archive expired failed for {policy.entity_type}: {e}")
        
        return archived_count
    
    def get_deleted_record(
        self,
        entity_type: str,
        entity_id: str
    ) -> Optional[DeletedRecord]:
        """
        Get a deleted record.
        
        Args:
            entity_type: Type of entity
            entity_id: ID of entity
            
        Returns:
            DeletedRecord or None
        """
        if self.db is None:
            return None
        
        cursor = self.db.cursor()
        cursor.execute('''
            SELECT * FROM deleted_records
            WHERE entity_type = ? AND entity_id = ?
        ''', (entity_type, entity_id))
        
        row = cursor.fetchone()
        if row:
            columns = [desc[0] for desc in cursor.description]
            return DeletedRecord.from_dict(dict(zip(columns, row)))
        return None
    
    def list_deleted(
        self,
        entity_type: str = None,
        recoverable_only: bool = True
    ) -> List[DeletedRecord]:
        """
        List deleted records.
        
        Args:
            entity_type: Optional filter by entity type
            recoverable_only: Only return recoverable records
            
        Returns:
            List of DeletedRecord
        """
        if self.db is None:
            return []
        
        cursor = self.db.cursor()
        
        query = "SELECT * FROM deleted_records WHERE 1=1"
        params = []
        
        if entity_type:
            query += " AND entity_type = ?"
            params.append(entity_type)
        
        if recoverable_only:
            query += " AND purge_status = ? AND recovery_until > ?"
            params.extend([PurgeStatus.RECOVERABLE.value, datetime.now().isoformat()])
        
        query += " ORDER BY deleted_at DESC"
        
        cursor.execute(query, params)
        
        columns = [desc[0] for desc in cursor.description]
        return [DeletedRecord.from_dict(dict(zip(columns, row))) for row in cursor.fetchall()]
    
    def _get_record(
        self,
        entity_type: str,
        entity_id: str
    ) -> Optional[dict]:
        """Get record from source table."""
        if self.db is None:
            return None
        
        table_name = self._get_table_name(entity_type)
        cursor = self.db.cursor()
        
        try:
            cursor.execute(
                f"SELECT * FROM {table_name} WHERE id = ?",
                (entity_id,)
            )
            
            row = cursor.fetchone()
            if row:
                columns = [desc[0] for desc in cursor.description]
                return dict(zip(columns, row))
            return None
        except Exception:
            return None
    
    def _save_deleted_record(self, deleted: DeletedRecord) -> None:
        """Save deleted record to tracking table."""
        if self.db is None:
            return
        
        cursor = self.db.cursor()
        cursor.execute('''
            INSERT INTO deleted_records
            (id, entity_type, entity_id, original_data, deleted_at, 
             recovery_until, purge_status, deletion_reason, deleted_by)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            deleted.id,
            deleted.entity_type,
            deleted.entity_id,
            json.dumps(deleted.original_data),
            deleted.deleted_at.isoformat(),
            deleted.recovery_until.isoformat(),
            deleted.purge_status.value,
            deleted.deletion_reason,
            deleted.deleted_by
        ))
        
        self.db.commit()
    
    def _delete_from_source(
        self,
        entity_type: str,
        entity_id: str
    ) -> None:
        """Delete record from source table."""
        if self.db is None:
            return
        
        table_name = self._get_table_name(entity_type)
        cursor = self.db.cursor()
        
        cursor.execute(
            f"DELETE FROM {table_name} WHERE id = ?",
            (entity_id,)
        )
        
        self.db.commit()
    
    def _get_table_name(self, entity_type: str) -> str:
        """Convert entity type to table name."""
        mapping = {
            'habits': 'habits',
            'tasks': 'tasks',
            'transactions': 'transactions',
            'health_entries': 'health_entries',
            'time_entries': 'time_entries',
            'goals': 'goals',
            'habit_logs': 'habit_logs',
            'xp_logs': 'xp_logs',
        }
        return mapping.get(entity_type, entity_type)
    
    def count_recoverable(self, entity_type: str = None) -> int:
        """
        Count recoverable records.
        
        Args:
            entity_type: Optional filter by entity type
            
        Returns:
            Number of recoverable records
        """
        if self.db is None:
            return 0
        
        cursor = self.db.cursor()
        
        if entity_type:
            cursor.execute('''
                SELECT COUNT(*) FROM deleted_records
                WHERE entity_type = ? 
                AND purge_status = ? 
                AND recovery_until > ?
            ''', (entity_type, PurgeStatus.RECOVERABLE.value, datetime.now().isoformat()))
        else:
            cursor.execute('''
                SELECT COUNT(*) FROM deleted_records
                WHERE purge_status = ? 
                AND recovery_until > ?
            ''', (PurgeStatus.RECOVERABLE.value, datetime.now().isoformat()))
        
        return cursor.fetchone()[0]