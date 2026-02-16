"""
Database Connection Module (db)

This module provides database connection functions that are used throughout the Brain system.
It serves as an abstraction layer for database operations.
"""

import sqlite3
import os
from pathlib import Path
from contextlib import contextmanager
from typing import Optional


# Default database path
DEFAULT_DB_PATH = Path(__file__).parent.parent / "tracking.db"


def get_sqlite_conn(db_path: Optional[str] = None):
    """
    Get a connection to the SQLite database.
    
    Args:
        db_path: Optional path to database file. Uses default if not provided.
        
    Returns:
        sqlite3.Connection object
    """
    if db_path is None:
        db_path = str(DEFAULT_DB_PATH)
    
    conn = sqlite3.connect(db_path)
    # Enable foreign key constraints
    conn.execute("PRAGMA foreign_keys = ON")
    # Row factory for easier access to columns by name
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def get_db_connection(db_path: Optional[str] = None):
    """
    Context manager for database connections.
    
    Args:
        db_path: Optional path to database file. Uses default if not provided.
    """
    conn = get_sqlite_conn(db_path)
    try:
        yield conn
        conn.commit()
    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()


def init_db(db_path: Optional[str] = None):
    """
    Initialize the database with required tables.
    
    Args:
        db_path: Optional path to database file. Uses default if not provided.
    """
    if db_path is None:
        db_path = str(DEFAULT_DB_PATH)
    
    with get_db_connection(db_path) as conn:
        # Create habits table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS habits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                streak INTEGER DEFAULT 0,
                completed_today BOOLEAN DEFAULT 0
            )
        """)
        
        # Create tasks table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                completed BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                due_date TIMESTAMP,
                priority TEXT DEFAULT 'medium'
            )
        """)
        
        # Create transactions table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS transactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount REAL NOT NULL,
                description TEXT,
                category TEXT,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                transaction_type TEXT CHECK(transaction_type IN ('income', 'expense'))
            )
        """)
        
        # Create health_entries table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS health_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                metric TEXT NOT NULL,
                value REAL NOT NULL,
                unit TEXT,
                date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                notes TEXT
            )
        """)
        
        # Create goals table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS goals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                target_value REAL,
                current_value REAL DEFAULT 0,
                unit TEXT,
                deadline TIMESTAMP,
                completed BOOLEAN DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create brain_audit_log table for audit logging
        conn.execute("""
            CREATE TABLE IF NOT EXISTS brain_audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                command_id TEXT,
                command_type TEXT,
                command_params TEXT,
                user_id INTEGER,
                company_id INTEGER,
                received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_at TIMESTAMP,
                duration_ms INTEGER,
                status TEXT,
                error_code TEXT,
                error_message TEXT,
                risk_tier TEXT,
                confirmation_required BOOLEAN,
                entity_type TEXT,
                entity_id INTEGER,
                state_before TEXT,
                state_after TEXT
            )
        """)
        
        conn.commit()


# Initialize the database when this module is imported
if __name__ != '__main__':  # Don't initialize during testing
    try:
        init_db()
    except Exception as e:
        print(f"Warning: Could not initialize database: {e}")


def get_connection():
    """
    Legacy function name to maintain compatibility with existing code.
    """
    return get_sqlite_conn()


def get_conn():
    """
    Another legacy function name to maintain compatibility with existing code.
    """
    return get_sqlite_conn()


def get_db():
    """
    Yet another legacy function name to maintain compatibility with existing code.
    """
    return get_sqlite_conn()