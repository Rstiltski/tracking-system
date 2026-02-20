"""
Download Manager

Secure download token generation and validation.
Provides secure, time-limited download links.

All implementation is in Python 3.10+
"""

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, Tuple
import logging
import secrets
import hashlib


logger = logging.getLogger(__name__)


# Default token expiration in hours
DEFAULT_EXPIRATION_HOURS = 24


class DownloadManager:
    """
    Manages secure download tokens.
    
    Provides:
    - Token generation with expiration
    - Token validation
    - File retrieval
    
    Example:
        >>> manager = DownloadManager()
        >>> 
        >>> # Generate token
        >>> token = manager.create_token('export.zip')
        >>> 
        >>> # Validate and get file
        >>> file_path = manager.validate_token(token)
    """
    
    def __init__(
        self,
        db_connection: sqlite3.Connection = None,
        expiration_hours: int = DEFAULT_EXPIRATION_HOURS
    ):
        """
        Initialize download manager.
        
        Args:
            db_connection: SQLite database connection
            expiration_hours: Hours until token expires
        """
        self.db = db_connection
        self.expiration_hours = expiration_hours
    
    def create_token(
        self,
        file_path: str,
        user_id: str = ""
    ) -> str:
        """
        Create a secure download token.
        
        Args:
            file_path: Path to file for download
            user_id: User who can download
            
        Returns:
            Secure download token
        """
        # Generate secure token
        token = secrets.token_urlsafe(32)
        
        # Create token hash for storage
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        expires_at = datetime.now() + timedelta(hours=self.expiration_hours)
        
        if self.db:
            cursor = self.db.cursor()
            cursor.execute('''
                INSERT INTO download_tokens
                (token_hash, file_path, user_id, expires_at, created_at)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                token_hash,
                file_path,
                user_id,
                expires_at.isoformat(),
                datetime.now().isoformat()
            ))
            self.db.commit()
        
        return token
    
    def validate_token(
        self,
        token: str,
        user_id: str = None
    ) -> Optional[Path]:
        """
        Validate a download token.
        
        Args:
            token: Download token to validate
            user_id: Optional user ID to check ownership
            
        Returns:
            Path to file if valid, None otherwise
        """
        if self.db is None:
            return None
        
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        cursor = self.db.cursor()
        cursor.execute('''
            SELECT file_path, user_id, expires_at
            FROM download_tokens
            WHERE token_hash = ?
        ''', (token_hash,))
        
        row = cursor.fetchone()
        if not row:
            return None
        
        file_path, token_user_id, expires_at = row
        expires_at = datetime.fromisoformat(expires_at)
        
        # Check expiration
        if datetime.now() > expires_at:
            self._delete_token(token_hash)
            return None
        
        # Check user if specified
        if user_id and token_user_id and token_user_id != user_id:
            return None
        
        # Check file exists
        path = Path(file_path)
        if not path.exists():
            return None
        
        return path
    
    def revoke_token(self, token: str) -> bool:
        """
        Revoke a download token.
        
        Args:
            token: Token to revoke
            
        Returns:
            True if token was revoked
        """
        if self.db is None:
            return False
        
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        return self._delete_token(token_hash)
    
    def _delete_token(self, token_hash: str) -> bool:
        """Delete token from database."""
        if self.db is None:
            return False
        
        cursor = self.db.cursor()
        cursor.execute(
            "DELETE FROM download_tokens WHERE token_hash = ?",
            (token_hash,)
        )
        self.db.commit()
        
        return cursor.rowcount > 0
    
    def cleanup_expired(self) -> int:
        """
        Remove all expired tokens.
        
        Returns:
            Number of tokens removed
        """
        if self.db is None:
            return 0
        
        cursor = self.db.cursor()
        cursor.execute(
            "DELETE FROM download_tokens WHERE expires_at < ?",
            (datetime.now().isoformat(),)
        )
        self.db.commit()
        
        count = cursor.rowcount
        if count > 0:
            logger.info(f"Cleaned up {count} expired download tokens")
        
        return count
    
    def ensure_tables(self) -> None:
        """Create required tables if they don't exist."""
        if self.db is None:
            return
        
        cursor = self.db.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS download_tokens (
                token_hash TEXT PRIMARY KEY,
                file_path TEXT NOT NULL,
                user_id TEXT,
                expires_at TEXT NOT NULL,
                created_at TEXT,
                downloaded_at TEXT
            )
        ''')
        self.db.commit()