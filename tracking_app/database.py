"""
Database Module - SQLite Connection and Schema Management

This module handles database connections, schema creation, and basic
database operations for the tracking system.

Following PROJECT_RULES.md:
- Uses sqlite3 (built-in, no external dependencies)
- Context managers for connections
- Thread-safe connection handling
"""
from __future__ import annotations

import sqlite3
import threading
import uuid
import json
from contextlib import contextmanager
from datetime import datetime
from pathlib import Path
from typing import Generator, Optional, List, Dict, Any
import logging

# Initialize logger
logger = logging.getLogger(__name__)

# Database path
BASE_DIR = Path(__file__).parent.parent.resolve()
DB_PATH = BASE_DIR / "tracking.db"

# Thread-local storage for connections
_thread_local = threading.local()

# Schema version for migrations
SCHEMA_VERSION = 1


class Database:
    """
    Database manager for the tracking system.
    
    Provides connection pooling, schema management, and common operations.
    
    Usage:
        db = Database()
        with db.get_connection() as conn:
            cursor = conn.execute("SELECT * FROM habits")
            habits = cursor.fetchall()
    """
    
    def __init__(self, db_path: Optional[Path] = None):
        """
        Initialize database manager.
        
        Args:
            db_path: Optional custom database path (for testing)
        """
        self.db_path = db_path or DB_PATH
        self._local = threading.local()
    
    def get_connection(self) -> sqlite3.Connection:
        """
        Get a SQLite connection for the current thread.
        
        Returns:
            sqlite3.Connection: Database connection
        """
        if hasattr(self._local, 'connection') and self._local.connection:
            return self._local.connection
        
        conn = sqlite3.connect(
            str(self.db_path),
            check_same_thread=False,
            detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES
        )
        
        # Enable foreign keys
        conn.execute("PRAGMA foreign_keys = ON")
        
        # Use Row factory for dict-like access
        conn.row_factory = sqlite3.Row
        
        self._local.connection = conn
        logger.debug(f"Created new database connection for thread {threading.current_thread().ident}")
        
        return conn
    
    @contextmanager
    def transaction(self) -> Generator[sqlite3.Connection, None, None]:
        """
        Context manager for database transactions.
        
        Automatically commits on success, rolls back on error.
        
        Yields:
            sqlite3.Connection: Database connection
            
        Example:
            with db.transaction() as conn:
                conn.execute("INSERT INTO habits ...")
        """
        conn = self.get_connection()
        try:
            yield conn
            if conn.in_transaction:
                conn.commit()
        except Exception as e:
            conn.rollback()
            logger.error(f"Transaction rolled back: {e}")
            raise
    
    def execute(
        self,
        query: str,
        params: tuple = (),
        commit: bool = True
    ) -> sqlite3.Cursor:
        """
        Execute a SQL query.
        
        Args:
            query: SQL query string
            params: Query parameters
            commit: Whether to commit after execution
            
        Returns:
            sqlite3.Cursor: Query cursor
        """
        conn = self.get_connection()
        cursor = conn.execute(query, params)
        if commit:
            conn.commit()
        return cursor
    
    def execute_many(
        self,
        query: str,
        params_list: List[tuple],
        commit: bool = True
    ) -> sqlite3.Cursor:
        """
        Execute a SQL query with multiple parameter sets.
        
        Args:
            query: SQL query string
            params_list: List of parameter tuples
            commit: Whether to commit after execution
            
        Returns:
            sqlite3.Cursor: Query cursor
        """
        conn = self.get_connection()
        cursor = conn.executemany(query, params_list)
        if commit:
            conn.commit()
        return cursor
    
    def fetch_one(
        self,
        query: str,
        params: tuple = ()
    ) -> Optional[Dict[str, Any]]:
        """
        Execute a query and fetch a single row.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            Dictionary with row data or None
        """
        cursor = self.execute(query, params, commit=False)
        row = cursor.fetchone()
        return dict(row) if row else None
    
    def fetch_all(
        self,
        query: str,
        params: tuple = ()
    ) -> List[Dict[str, Any]]:
        """
        Execute a query and fetch all rows.
        
        Args:
            query: SQL query string
            params: Query parameters
            
        Returns:
            List of dictionaries with row data
        """
        cursor = self.execute(query, params, commit=False)
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def close(self) -> None:
        """Close the current thread's connection."""
        if hasattr(self._local, 'connection') and self._local.connection:
            self._local.connection.close()
            self._local.connection = None
            logger.debug("Closed database connection")


# Global database instance
_db: Optional[Database] = None


def get_db() -> Database:
    """
    Get the global database instance.
    
    Returns:
        Database: Global database manager
    """
    global _db
    if _db is None:
        _db = Database()
    return _db


def init_db() -> None:
    """
    Initialize the database with required tables.
    
    Creates all tables if they don't exist.
    """
    db = get_db()
    
    # Create schema
    schema_sql = """
    -- Schema version tracking
    CREATE TABLE IF NOT EXISTS schema_version (
        version INTEGER PRIMARY KEY,
        applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Habits table
    CREATE TABLE IF NOT EXISTS habits (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT DEFAULT '',
        frequency TEXT DEFAULT 'daily',
        frequency_data TEXT DEFAULT '{}',
        habit_type TEXT DEFAULT 'boolean',
        color TEXT DEFAULT '#6366f1',
        icon TEXT DEFAULT '🎯',
        target_value REAL DEFAULT 0,
        target_type TEXT DEFAULT 'at_least',
        archived INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Habit entries (completions)
    CREATE TABLE IF NOT EXISTS habit_entries (
        id TEXT PRIMARY KEY,
        habit_id TEXT NOT NULL,
        entry_date DATE NOT NULL,
        value REAL DEFAULT 1.0,
        notes TEXT DEFAULT '',
        skipped INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE,
        UNIQUE(habit_id, entry_date)
    );
    
    -- Streak freezes
    CREATE TABLE IF NOT EXISTS streak_freezes (
        id TEXT PRIMARY KEY,
        habit_id TEXT,
        freeze_date DATE NOT NULL,
        action TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE SET NULL
    );
    
    -- User inventory (XP, freezes, etc.)
    CREATE TABLE IF NOT EXISTS user_inventory (
        key TEXT PRIMARY KEY,
        value TEXT NOT NULL,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Tasks table
    CREATE TABLE IF NOT EXISTS tasks (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT DEFAULT '',
        due_date TIMESTAMP,
        priority TEXT DEFAULT 'medium',
        category TEXT DEFAULT '',
        completed INTEGER DEFAULT 0,
        completed_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Transactions (finances)
    CREATE TABLE IF NOT EXISTS transactions (
        id TEXT PRIMARY KEY,
        description TEXT NOT NULL,
        amount REAL NOT NULL,
        type TEXT NOT NULL,
        category TEXT DEFAULT '',
        trans_date DATE,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Health entries
    CREATE TABLE IF NOT EXISTS health_entries (
        id TEXT PRIMARY KEY,
        entry_date DATE NOT NULL UNIQUE,
        weight REAL,
        sleep_hours REAL,
        mood TEXT DEFAULT 'good',
        notes TEXT DEFAULT '',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Goals
    CREATE TABLE IF NOT EXISTS goals (
        id TEXT PRIMARY KEY,
        title TEXT NOT NULL,
        description TEXT DEFAULT '',
        target REAL DEFAULT 0,
        current REAL DEFAULT 0,
        unit TEXT DEFAULT '',
        deadline TIMESTAMP,
        completed INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Achievements
    CREATE TABLE IF NOT EXISTS achievements (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        description TEXT DEFAULT '',
        icon TEXT DEFAULT '🏆',
        xp_reward INTEGER DEFAULT 0,
        unlocked_at TIMESTAMP,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Events (for event sourcing)
    CREATE TABLE IF NOT EXISTS events (
        id TEXT PRIMARY KEY,
        event_type TEXT NOT NULL,
        entity_type TEXT NOT NULL,
        entity_id TEXT NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        version TEXT DEFAULT '1.0',
        payload TEXT DEFAULT '{}',
        metadata TEXT DEFAULT '{}'
    );
    
    -- Indexes for common queries
    CREATE INDEX IF NOT EXISTS idx_habit_entries_habit_id ON habit_entries(habit_id);
    CREATE INDEX IF NOT EXISTS idx_habit_entries_date ON habit_entries(entry_date);
    CREATE INDEX IF NOT EXISTS idx_events_entity ON events(entity_type, entity_id);
    CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type);
    CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp);
    CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date);
    CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(trans_date);
    """
    
    with db.transaction() as conn:
        conn.executescript(schema_sql)
        
        # Check if we need to set schema version
        cursor = conn.execute("SELECT COUNT(*) FROM schema_version")
        if cursor.fetchone()[0] == 0:
            conn.execute(
                "INSERT INTO schema_version (version) VALUES (?)",
                (SCHEMA_VERSION,)
            )
    
    logger.info(f"Database initialized at {DB_PATH}")
    
    # Initialize default user data
    _init_default_data(db)


def _init_default_data(db: Database) -> None:
    """Initialize default user data."""
    defaults = {
        "xp": "0",
        "level": "1",
        "streak_freezes": "3",
        "max_streak_freezes": "10",
        "theme": "light"
    }
    
    with db.transaction() as conn:
        for key, value in defaults.items():
            # Only insert if not exists
            conn.execute(
                """INSERT OR IGNORE INTO user_inventory (key, value) 
                   VALUES (?, ?)""",
                (key, value)
            )


def generate_id() -> str:
    """Generate a unique ID for entities."""
    return str(uuid.uuid4())


# Export
__all__ = [
    "Database",
    "get_db",
    "init_db",
    "DB_PATH",
    "generate_id",
]