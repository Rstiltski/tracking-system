"""
Recovery Manager

Recovers soft-deleted records within the recovery window.
Provides a safety net for accidental deletions.

All implementation is in Python 3.10+
"""

import sqlite3
from datetime import datetime
from typing import Optional
import logging

from brain.lifecycle.models import (
    DeletedRecord,
    PurgeStatus,
    LifecycleResult
)


logger = logging.getLogger(__name__)


class RecoveryManager:
    """
    Manages recovery of soft-deleted records.
    
    Records can only be recovered if:
    1. They are in deleted_records table
    2. purge_status = 'recoverable'
    3. recovery_until > now
    
    Example:
        manager = RecoveryManager(db_connection)
        
        # Check if recoverable
        if manager.can_recover('tasks', 'task-123'):
            result = manager.recover('tasks', 'task-123')
    """
    
    def __init__(self, db_connection: sqlite3.Connection = None):
        """
        Initialize recovery manager.
        
        Args:
            db_connection: SQLite database connection
        """
        self.db = db_connection
    
    def can_recover(
        self,
        entity_type: str,
        entity_id: str
    ) -> bool:
        """
        Check if a record can be recovered.
        
        Args:
            entity_type: Type of entity
            entity_id: ID of entity
            
        Returns:
            True if record can be recovered
        """
        deleted = self._get_deleted_record(entity_type, entity_id)
        return deleted is not None and deleted.is_recoverable()
    
    def recover(
        self,
        entity_type: str,
        entity_id: str
    ) -> LifecycleResult:
        """
        Recover a soft-deleted record.
        
        Restores the record to its original table and
        removes it from deleted_records.
        
        Args:
            entity_type: Type of entity
            entity_id: ID of entity
            
        Returns:
            LifecycleResult with recovery status
        """
        result = LifecycleResult(operation="recover")
        
        try:
            # Get deleted record
            deleted = self._get_deleted_record(entity_type, entity_id)
            
            if not deleted:
                result.error_message = "Record not found in deleted records"
                return result
            
            if not deleted.is_recoverable():
                result.error_message = "Record cannot be recovered (past recovery window)"
                return result
            
            # Restore to source table
            self._restore_record(deleted)
            
            # Delete from deleted_records
            self._remove_deleted_record(deleted.id)
            
            result.success = True
            result.records_recovered = 1
            result.records_affected = 1
            
            logger.info(f"Recovered {entity_type}/{entity_id}")
            
        except Exception as e:
            result.error_message = str(e)
            logger.error(f"Recovery failed: {e}")
        
        return result
    
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
        return self._get_deleted_record(entity_type, entity_id)
    
    def _get_deleted_record(
        self,
        entity_type: str,
        entity_id: str
    ) -> Optional[DeletedRecord]:
        """Get deleted record from tracking table."""
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
    
    def _restore_record(self, deleted: DeletedRecord) -> None:
        """Restore record to source table."""
        if self.db is None:
            return
        
        table_name = self._get_table_name(deleted.entity_type)
        cursor = self.db.cursor()
        
        # Build INSERT from original_data
        data = deleted.original_data
        columns = list(data.keys())
        placeholders = ', '.join(['?' for _ in columns])
        values = [data.get(col) for col in columns]
        
        column_list = ', '.join(columns)
        query = f"INSERT INTO {table_name} ({column_list}) VALUES ({placeholders})"
        
        cursor.execute(query, values)
        self.db.commit()
    
    def _remove_deleted_record(self, deleted_id: str) -> None:
        """Remove record from deleted_records table."""
        if self.db is None:
            return
        
        cursor = self.db.cursor()
        cursor.execute(
            "DELETE FROM deleted_records WHERE id = ?",
            (deleted_id,)
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