"""
Deduplication Database

SQLite database for tracking deduplicated files.
Enables quick lookup of files by size and hash.

All implementation is in Python 3.10+
"""

import sqlite3
from pathlib import Path
from typing import Optional, List, Dict, Any
from datetime import datetime
import logging

from brain.backup.models import DedupRecord


logger = logging.getLogger(__name__)


class DedupDatabase:
    """
    Database for tracking deduplicated files.
    
    Stores file hashes, paths, and link counts to enable
    fast lookup when creating hard links.
    
    Schema:
        - dedup_records: Tracks files by hash
        - Index on file_size for quick size-based lookup
    
    Example:
        >>> db = DedupDatabase('dedup.db')
        >>> 
        >>> # Record a new file
        >>> db.record_file(
        ...     file_hash='abc123...',
        ...     original_path='/backups/backup1.db',
        ...     original_size=1024000
        ... )
        >>> 
        >>> # Find by size
        >>> matches = db.find_by_size(1024000)
        >>> for record in matches:
        ...     print(record.file_hash)
    """
    
    def __init__(self, db_path: str = "dedup.db"):
        """
        Initialize deduplication database.
        
        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self._ensure_tables()
    
    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection."""
        return sqlite3.connect(str(self.db_path))
    
    def _ensure_tables(self) -> None:
        """Create tables if they don't exist."""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Main dedup records table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS dedup_records (
                file_hash TEXT PRIMARY KEY,
                original_path TEXT NOT NULL,
                original_size INTEGER NOT NULL,
                link_count INTEGER DEFAULT 1,
                first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Index on size for quick lookup
        cursor.execute(
            'CREATE INDEX IF NOT EXISTS idx_dedup_size ON dedup_records(original_size)'
        )
        
        # Index on path for cleanup
        cursor.execute(
            'CREATE INDEX IF NOT EXISTS idx_dedup_path ON dedup_records(original_path)'
        )
        
        conn.commit()
        conn.close()
    
    def record_file(
        self,
        file_hash: str,
        original_path: str,
        original_size: int
    ) -> None:
        """
        Record a file in the dedup database.
        
        Args:
            file_hash: SHA-256 hash of file contents
            original_path: Path to the file
            original_size: Size in bytes
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        now = datetime.now().isoformat()
        
        cursor.execute('''
            INSERT OR REPLACE INTO dedup_records 
            (file_hash, original_path, original_size, link_count, first_seen, last_seen)
            VALUES (?, ?, ?, 1, ?, ?)
        ''', (file_hash, original_path, original_size, now, now))
        
        conn.commit()
        conn.close()
        
        logger.debug(f"Recorded file: {file_hash[:16]}... at {original_path}")
    
    def find_by_hash(self, file_hash: str) -> Optional[DedupRecord]:
        """
        Find a record by file hash.
        
        Args:
            file_hash: SHA-256 hash to search for
            
        Returns:
            DedupRecord or None if not found
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM dedup_records WHERE file_hash = ?",
            (file_hash,)
        )
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return self._row_to_record(row)
        return None
    
    def find_by_size(self, size: int) -> List[DedupRecord]:
        """
        Find all records matching a file size.
        
        This is the first tier in deduplication lookup.
        Files with different sizes cannot be duplicates.
        
        Args:
            size: File size in bytes
            
        Returns:
            List of DedupRecord with matching size
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM dedup_records WHERE original_size = ?",
            (size,)
        )
        
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_record(row) for row in rows]
    
    def find_by_path(self, path: str) -> Optional[DedupRecord]:
        """
        Find a record by file path.
        
        Args:
            path: File path to search for
            
        Returns:
            DedupRecord or None if not found
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT * FROM dedup_records WHERE original_path = ?",
            (path,)
        )
        
        row = cursor.fetchone()
        conn.close()
        
        if row:
            return self._row_to_record(row)
        return None
    
    def increment_link_count(self, file_hash: str) -> int:
        """
        Increment the link count for a file.
        
        Called when a new hard link is created to this file.
        
        Args:
            file_hash: Hash of the file
            
        Returns:
            New link count
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE dedup_records 
            SET link_count = link_count + 1, last_seen = ?
            WHERE file_hash = ?
        ''', (datetime.now().isoformat(), file_hash))
        
        cursor.execute(
            "SELECT link_count FROM dedup_records WHERE file_hash = ?",
            (file_hash,)
        )
        
        result = cursor.fetchone()
        conn.commit()
        conn.close()
        
        return result[0] if result else 0
    
    def decrement_link_count(self, file_hash: str) -> int:
        """
        Decrement the link count for a file.
        
        Called when a hard link is deleted.
        
        Args:
            file_hash: Hash of the file
            
        Returns:
            New link count
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE dedup_records 
            SET link_count = MAX(0, link_count - 1)
            WHERE file_hash = ?
        ''', (file_hash,))
        
        cursor.execute(
            "SELECT link_count FROM dedup_records WHERE file_hash = ?",
            (file_hash,)
        )
        
        result = cursor.fetchone()
        conn.commit()
        conn.close()
        
        return result[0] if result else 0
    
    def remove_record(self, file_hash: str) -> bool:
        """
        Remove a record from the database.
        
        Args:
            file_hash: Hash of file to remove
            
        Returns:
            True if record was removed
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "DELETE FROM dedup_records WHERE file_hash = ?",
            (file_hash,)
        )
        
        removed = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return removed
    
    def remove_by_path(self, path: str) -> bool:
        """
        Remove a record by file path.
        
        Args:
            path: Path of file to remove
            
        Returns:
            True if record was removed
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "DELETE FROM dedup_records WHERE original_path = ?",
            (path,)
        )
        
        removed = cursor.rowcount > 0
        conn.commit()
        conn.close()
        
        return removed
    
    def get_all_records(self) -> List[DedupRecord]:
        """
        Get all dedup records.
        
        Returns:
            List of all DedupRecord instances
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM dedup_records")
        
        rows = cursor.fetchall()
        conn.close()
        
        return [self._row_to_record(row) for row in rows]
    
    def get_statistics(self) -> Dict[str, Any]:
        """
        Get deduplication statistics.
        
        Returns:
            Dictionary with:
            - total_files: Total unique files tracked
            - total_links: Total hard links created
            - bytes_saved: Estimated storage saved
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Total unique files
        cursor.execute("SELECT COUNT(*) FROM dedup_records")
        total_files = cursor.fetchone()[0]
        
        # Total links (including originals)
        cursor.execute("SELECT SUM(link_count) FROM dedup_records")
        total_links = cursor.fetchone()[0] or 0
        
        # Calculate bytes saved
        # Each hard link after the first saves one copy
        cursor.execute('''
            SELECT SUM(original_size * (link_count - 1))
            FROM dedup_records
            WHERE link_count > 1
        ''')
        bytes_saved = cursor.fetchone()[0] or 0
        
        # Total storage used
        cursor.execute("SELECT SUM(original_size) FROM dedup_records")
        total_bytes = cursor.fetchone()[0] or 0
        
        conn.close()
        
        return {
            'total_files': total_files,
            'total_links': total_links,
            'total_links_created': total_links - total_files if total_links > total_files else 0,
            'bytes_saved': bytes_saved,
            'bytes_saved_mb': bytes_saved / (1024 * 1024),
            'total_bytes_tracked': total_bytes,
            'total_bytes_mb': total_bytes / (1024 * 1024),
        }
    
    def clear(self) -> int:
        """
        Clear all records from database.
        
        Returns:
            Number of records removed
        """
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM dedup_records")
        count = cursor.fetchone()[0]
        
        cursor.execute("DELETE FROM dedup_records")
        
        conn.commit()
        conn.close()
        
        return count
    
    def _row_to_record(self, row: tuple) -> DedupRecord:
        """Convert database row to DedupRecord."""
        return DedupRecord(
            file_hash=row[0],
            original_path=row[1],
            original_size=row[2],
            link_count=row[3],
            first_seen=datetime.fromisoformat(row[4]) if row[4] else datetime.now(),
            last_seen=datetime.fromisoformat(row[5]) if row[5] else datetime.now(),
        )


class DedupDatabaseManager:
    """
    High-level manager for dedup database operations.
    
    Provides convenience methods for common operations.
    """
    
    def __init__(self, db_path: str = "dedup.db"):
        """
        Initialize manager.
        
        Args:
            db_path: Path to SQLite database
        """
        self.db = DedupDatabase(db_path)
    
    def cleanup_missing_files(self) -> int:
        """
        Remove records for files that no longer exist.
        
        Returns:
            Number of orphan records removed
        """
        removed = 0
        
        for record in self.db.get_all_records():
            if not Path(record.original_path).exists():
                self.db.remove_record(record.file_hash)
                removed += 1
                logger.debug(f"Removed orphan record: {record.file_hash[:16]}...")
        
        if removed > 0:
            logger.info(f"Cleaned up {removed} orphan dedup records")
        
        return removed
    
    def recalculate_link_counts(self) -> Dict[str, int]:
        """
        Recalculate link counts by checking actual file inodes.
        
        Returns:
            Dictionary with 'corrected' and 'unchanged' counts
        """
        import os
        
        corrected = 0
        unchanged = 0
        
        for record in self.db.get_all_records():
            path = Path(record.original_path)
            
            if path.exists():
                try:
                    actual_links = path.stat().st_nlink
                    
                    if actual_links != record.link_count:
                        # Update the count
                        conn = sqlite3.connect(str(self.db.db_path))
                        cursor = conn.cursor()
                        cursor.execute(
                            "UPDATE dedup_records SET link_count = ? WHERE file_hash = ?",
                            (actual_links, record.file_hash)
                        )
                        conn.commit()
                        conn.close()
                        corrected += 1
                    else:
                        unchanged += 1
                        
                except OSError:
                    pass
        
        logger.info(
            f"Link count recalculation: {corrected} corrected, {unchanged} unchanged"
        )
        
        return {'corrected': corrected, 'unchanged': unchanged}
    
    def export_state(self) -> Dict[str, Any]:
        """
        Export database state for backup.
        
        Returns:
            Dictionary with all records
        """
        records = self.db.get_all_records()
        
        return {
            'exported_at': datetime.now().isoformat(),
            'total_records': len(records),
            'statistics': self.db.get_statistics(),
            'records': [r.to_dict() for r in records],
        }
    
    def import_state(self, state: Dict[str, Any]) -> int:
        """
        Import database state from backup.
        
        Args:
            state: Previously exported state
            
        Returns:
            Number of records imported
        """
        imported = 0
        
        for record_data in state.get('records', []):
            record = DedupRecord.from_dict(record_data)
            self.db.record_file(
                file_hash=record.file_hash,
                original_path=record.original_path,
                original_size=record.original_size
            )
            imported += 1
        
        logger.info(f"Imported {imported} dedup records")
        
        return imported