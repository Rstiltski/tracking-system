"""
Database Connection Module

This module handles database connections and connection pooling for the landscaping system.
Following the architecture rules, this is part of the database layer that db.py delegates to.
"""
from __future__ import annotations
import sqlite3
import threading
from contextlib import contextmanager
from pathlib import Path
import os
import logging
from typing import Generator, Optional

# Initialize logger
logger = logging.getLogger(__name__)

# Database path - using dynamic resolution as per architecture rules
BASE_DIR = Path(__file__).parent.parent.resolve()
DB_PATH = BASE_DIR / "landscaping.db"

# Thread-local storage for connections
_thread_local = threading.local()

# Connection pool (simple implementation)
_connections = []
_max_connections = 10
_connection_lock = threading.Lock()

def init_connection_pool(max_connections: int = 10) -> None:
    """Initialize the connection pool with the specified maximum connections."""
    global _max_connections
    _max_connections = max_connections
    logger.info(f"Initialized connection pool with max {max_connections} connections")

def get_sqlite_conn() -> sqlite3.Connection:
    """Get a SQLite connection, either from thread-local storage or create a new one."""
    # Check if we already have a connection for this thread
    if hasattr(_thread_local, 'connection'):
        return _thread_local.connection
    
    # Create a new connection
    conn = sqlite3.connect(
        str(DB_PATH),
        check_same_thread=False,  # Allow multiple threads to use the connection
        detect_types=sqlite3.PARSE_DECLTYPES
    )
    
    # Configure the connection
    conn.row_factory = sqlite3.Row  # Enable dict-like access to rows
    conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
    
    # Store in thread-local storage
    _thread_local.connection = conn
    
    logger.debug(f"Created new database connection for thread {threading.current_thread().ident}")
    return conn

def get_conn() -> sqlite3.Connection:
    """Alias for get_sqlite_conn to maintain compatibility."""
    return get_sqlite_conn()

@contextmanager
def get_db():
    """Context manager for database connections."""
    conn = get_conn()
    try:
        yield conn
        # Only commit if autocommit is not disabled
        if conn.in_transaction:
            conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Database transaction rolled back due to error: {e}")
        raise
    finally:
        # Don't close the connection here since we're using connection pooling
        pass

def override_connection(db_path: str) -> None:
    """Override the default database path - primarily for testing."""
    global DB_PATH
    DB_PATH = Path(db_path)
    logger.info(f"Overridden database path to: {DB_PATH}")

def should_commit(conn: sqlite3.Connection) -> bool:
    """Check if the connection should commit (i.e., is in a transaction)."""
    return conn.in_transaction

def close_all_connections() -> None:
    """Close all connections in the pool."""
    global _connections
    with _connection_lock:
        for conn in _connections:
            try:
                conn.close()
            except Exception as e:
                logger.error(f"Error closing connection: {e}")
        _connections.clear()
    logger.info("Closed all database connections")

def get_db_size() -> int:
    """Get the size of the database file in bytes."""
    if DB_PATH.exists():
        return DB_PATH.stat().st_size
    return 0

# Initialize the connection pool when module is loaded
init_connection_pool()