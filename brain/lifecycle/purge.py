"""
Purge Manager

Permanent deletion of records past recovery window.
Maintains audit trail of all purges.

All implementation is in Python 3.10+
"""

import sqlite3
from datetime import datetime
from typing import List, Optional
import logging

from brain.lifecycle.models import (
    DeletedRecord,
    PurgeStatus,
    LifecycleResult
)


logger = logging.getLogger(__name__)


class PurgeManager:
    """
    Manages permanent deletion of records.
    
    Only purges records that:
    1. Are in deleted_records table
    2. Have purge_status = 'recoverable'
    3. Are past recovery_until date
    
    Example:
        manager = PurgeManager(db_connection)
        
        # Purge a specific record
        result = manager.purge('tasks', 'task-123')
        
        # Purge all expired records
        count = manager.purge_expired()
    """
    
    def __init__(self, db_connection: sqlite3.Connection = None):
        """
        Initialize purge manager.
        
        Args:
            db_connection: SQLite database connection
        """
        self.db = db_connection
    
    def purge(
        self,
        entity_type: str,
        entity_id: str
    ) -> LifecycleResult:
        """
        Permanently delete a record.
        
        Args:
            entity_type: Type of entity
            entity_id: ID of entity
            
        Returns:
            LifecycleResult with purge status
        """
        result = LifecycleResult(operation="purge")
        
        try:
            # Get deleted record
            deleted = self._get_deleted_record(entity_type, entity_id)
            
            if not deleted:
                result.error_message = "Record not found in deleted records"
                return result
            
            if not self._can_purge(deleted):
                result.error_message = "Record cannot be purged (still in recovery)"
                return result
            
            # Delete from deleted_records
            self._delete_purged_record(deleted.id)
            
            # Update status
            result.success = True
            result.records_purged = 1
            result.records_affected = 1
            
            logger.info(f"Purged {entity_type}/{entity_id}")
            
        except Exception as e:
            result.error_message = str(e)
            logger.error(f"Purge failed: {e}")
        
        return result
    
    def purge_expired(self, policy=None) -> int:
        """
        Purge all records past recovery window.
        
        Args:
            policy: Optional retention policy to filter by entity
            
        Returns:
            Number of records purged
        """
        if self.db is None:
            return 0
        
        cursor = self.db.cursor()
        
        # Find expired records
        query = '''
            SELECT id, entity_type, entity_id
            FROM deleted_records
            WHERE purge_status = ?
            AND recovery_until < ?
        '''
        params = [PurgeStatus.RECOVERABLE.value, datetime.now().isoformat()]
        
        if policy:
            query += " AND entity_type = ?"
            params.append(policy.entity_type)
        
        cursor.execute(query, params)
        expired = cursor.fetchall()
        purged_count = 0
        
        for row in expired:
            deleted_id = row[0]
            
            # Delete the record
            cursor.execute(
                "DELETE FROM deleted_records WHERE id = ?",
                (deleted_id,)
            )
            
            purged_count += 1
        
        self.db.commit()
        
        if purged_count > 0:
            logger.info(f"Purged {purged_count} expired records")
        
        return purged_count
    
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
    
    def _can_purge(self, deleted: DeletedRecord) -> bool:
        """Check if record can be purged."""
        return (
            deleted.purge_status in (PurgeStatus.RECOVERABLE, PurgeStatus.PENDING_PURGE)
            and datetime.now() >= deleted.recovery_until
        )
    
    def _delete_purged_record(self, deleted_id: str) -> None:
        """Delete record from deleted_records table."""
        if self.db is None:
            return
        
        cursor = self.db.cursor()
        cursor.execute(
            "DELETE FROM deleted_records WHERE id = ?",
            (deleted_id,)
        )
        self.db.commit()
    
    def count_pending_purge(self) -> int:
        """
        Count records pending purge.
        
        Returns:
            Number of records past recovery window
        """
        if self.db is None:
            return 0
        
        cursor = self.db.cursor()
        cursor.execute('''
            SELECT COUNT(*) FROM deleted_records
            WHERE purge_status = ? 
            AND recovery_until < ?
        ''', (PurgeStatus.RECOVERABLE.value, datetime.now().isoformat()))
        
        return cursor.fetchone()[0]