"""
Export History Manager

Track and query export history for analytics.
Provides insights into export usage patterns.

All implementation is in Python 3.10+
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import logging


logger = logging.getLogger(__name__)


class ExportHistoryManager:
    """
    Manages export history tracking.
    
    Provides:
    - History recording
    - Statistics queries
    - Cleanup of old records
    
    Example:
        >>> manager = ExportHistoryManager(db_connection)
        >>> 
        >>> # Get user's export history
        >>> history = manager.get_user_history('user-1')
        >>> 
        >>> # Get statistics
        >>> stats = manager.get_statistics()
    """
    
    def __init__(self, db_connection: sqlite3.Connection = None):
        """
        Initialize history manager.
        
        Args:
            db_connection: SQLite database connection
        """
        self.db = db_connection
    
    def record(
        self,
        user_id: str,
        export_id: str,
        format: str,
        modules: List[str],
        record_count: int,
        file_size: int,
        duration: float,
        status: str
    ) -> None:
        """
        Record an export in history.
        
        Args:
            user_id: User who performed export
            export_id: Export request ID
            format: Export format
            modules: Modules exported
            record_count: Number of records
            file_size: File size in bytes
            duration: Duration in seconds
            status: Final status
        """
        if self.db is None:
            return
        
        cursor = self.db.cursor()
        cursor.execute('''
            INSERT INTO export_history
            (id, user_id, export_id, format, modules_exported, record_count,
             file_size_bytes, duration_seconds, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            export_id,
            user_id,
            export_id,
            format,
            ','.join(modules) if modules else '',
            record_count,
            file_size,
            duration,
            status,
            datetime.now().isoformat()
        ))
        self.db.commit()
    
    def get_user_history(
        self,
        user_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """
        Get export history for a user.
        
        Args:
            user_id: User identifier
            limit: Maximum records to return
            
        Returns:
            List of history records
        """
        if self.db is None:
            return []
        
        cursor = self.db.cursor()
        cursor.execute('''
            SELECT * FROM export_history
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ?
        ''', (user_id, limit))
        
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_recent(self, limit: int = 100) -> List[Dict[str, Any]]:
        """
        Get recent export history.
        
        Args:
            limit: Maximum records to return
            
        Returns:
            List of history records
        """
        if self.db is None:
            return []
        
        cursor = self.db.cursor()
        cursor.execute('''
            SELECT * FROM export_history
            ORDER BY created_at DESC
            LIMIT ?
        ''', (limit,))
        
        columns = [desc[0] for desc in cursor.description]
        return [dict(zip(columns, row)) for row in cursor.fetchall()]
    
    def get_statistics(
        self,
        days: int = 30
    ) -> Dict[str, Any]:
        """
        Get export statistics.
        
        Args:
            days: Number of days to include
            
        Returns:
            Dictionary with statistics
        """
        if self.db is None:
            return {}
        
        cursor = self.db.cursor()
        since = (datetime.now() - timedelta(days=days)).isoformat()
        
        stats = {}
        
        # Total exports
        cursor.execute('''
            SELECT COUNT(*) FROM export_history
            WHERE created_at >= ?
        ''', (since,))
        stats['total_exports'] = cursor.fetchone()[0]
        
        # By format
        cursor.execute('''
            SELECT format, COUNT(*)
            FROM export_history
            WHERE created_at >= ?
            GROUP BY format
        ''', (since,))
        stats['by_format'] = dict(cursor.fetchall())
        
        # Total records exported
        cursor.execute('''
            SELECT SUM(record_count) FROM export_history
            WHERE created_at >= ?
        ''', (since,))
        stats['total_records'] = cursor.fetchone()[0] or 0
        
        # Total size
        cursor.execute('''
            SELECT SUM(file_size_bytes) FROM export_history
            WHERE created_at >= ?
        ''', (since,))
        stats['total_size_bytes'] = cursor.fetchone()[0] or 0
        
        # Success rate
        cursor.execute('''
            SELECT
                COUNT(CASE WHEN status = 'completed' THEN 1 END) * 100.0 / COUNT(*)
            FROM export_history
            WHERE created_at >= ?
        ''', (since,))
        result = cursor.fetchone()[0]
        stats['success_rate'] = result if result else 0
        
        # Average duration
        cursor.execute('''
            SELECT AVG(duration_seconds) FROM export_history
            WHERE created_at >= ? AND status = 'completed'
        ''', (since,))
        stats['avg_duration_seconds'] = cursor.fetchone()[0] or 0
        
        return stats
    
    def cleanup_old(self, days: int = 90) -> int:
        """
        Remove old history records.
        
        Args:
            days: Remove records older than this
            
        Returns:
            Number of records removed
        """
        if self.db is None:
            return 0
        
        cursor = self.db.cursor()
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        
        cursor.execute(
            "DELETE FROM export_history WHERE created_at < ?",
            (cutoff,)
        )
        self.db.commit()
        
        count = cursor.rowcount
        if count > 0:
            logger.info(f"Cleaned up {count} old history records")
        
        return count
    
    def ensure_tables(self) -> None:
        """Create required tables if they don't exist."""
        if self.db is None:
            return
        
        cursor = self.db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS export_history (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                export_id TEXT,
                format TEXT,
                modules_exported TEXT,
                record_count INTEGER,
                file_size_bytes INTEGER,
                duration_seconds REAL,
                status TEXT,
                created_at TEXT
            )
        ''')
        self.db.commit()