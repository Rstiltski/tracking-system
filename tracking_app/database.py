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
            check_same_thread=False
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
        category TEXT DEFAULT 'general',
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
    
    -- Time entries (Phase 13 - Decoupled Architecture)
    CREATE TABLE IF NOT EXISTS time_entries (
        id TEXT PRIMARY KEY,
        category TEXT NOT NULL,
        duration_seconds INTEGER NOT NULL,
        entry_date DATE NOT NULL,
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
    
    -- Habit Stacks (Phase 3.1 - Habit Stacking)
    CREATE TABLE IF NOT EXISTS habit_stacks (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        name TEXT NOT NULL,
        trigger_description TEXT NOT NULL,
        anchor_category TEXT DEFAULT 'custom',
        is_active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Stack Items (links habits to stacks in order)
    CREATE TABLE IF NOT EXISTS stack_items (
        id TEXT PRIMARY KEY,
        stack_id TEXT NOT NULL,
        habit_id TEXT NOT NULL,
        position_index INTEGER NOT NULL,
        delay_seconds INTEGER DEFAULT 0,
        is_tiny INTEGER DEFAULT 1,
        tiny_version_description TEXT,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (stack_id) REFERENCES habit_stacks(id) ON DELETE CASCADE,
        FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE,
        UNIQUE(stack_id, habit_id)
    );
    
    -- Stack Completions (track stack effectiveness)
    CREATE TABLE IF NOT EXISTS stack_completions (
        id TEXT PRIMARY KEY,
        stack_id TEXT NOT NULL,
        completion_date DATE NOT NULL,
        completed_items TEXT DEFAULT '[]',
        completion_order TEXT DEFAULT '[]',
        conversion_rate REAL DEFAULT 0.0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (stack_id) REFERENCES habit_stacks(id) ON DELETE CASCADE
    );
    
    -- SRBAI Results (habit automaticity surveys)
    CREATE TABLE IF NOT EXISTS srbai_results (
        id TEXT PRIMARY KEY,
        habit_id TEXT NOT NULL,
        user_id TEXT NOT NULL,
        survey_date DATE NOT NULL,
        q1_automatic INTEGER NOT NULL,
        q2_without_thinking INTEGER NOT NULL,
        q3_start_unintentionally INTEGER NOT NULL,
        q4_difficult_not_to_do INTEGER NOT NULL,
        automaticity_score REAL,
        is_habit_formed INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE
    );
    
    -- Implementation Intentions (Phase 3.2 - If-Then Planning)
    CREATE TABLE IF NOT EXISTS implementation_intentions (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        goal_id TEXT,
        name TEXT NOT NULL,
        trigger_type TEXT NOT NULL,
        trigger_source TEXT NOT NULL,
        trigger_predicate TEXT NOT NULL,
        trigger_description TEXT,
        action_type TEXT NOT NULL,
        action_payload TEXT NOT NULL,
        action_priority INTEGER DEFAULT 0,
        action_delay_seconds INTEGER DEFAULT 0,
        is_active INTEGER DEFAULT 1,
        trigger_count INTEGER DEFAULT 0,
        success_count INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Intention Triggers (log when intentions are triggered)
    CREATE TABLE IF NOT EXISTS intention_triggers (
        id TEXT PRIMARY KEY,
        intention_id TEXT NOT NULL,
        triggered_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        context_data TEXT DEFAULT '{}',
        action_dispatched INTEGER DEFAULT 0,
        user_responded INTEGER DEFAULT 0,
        response_time_seconds REAL,
        FOREIGN KEY (intention_id) REFERENCES implementation_intentions(id) ON DELETE CASCADE
    );
    
    -- Rewards (Phase 3.3 - Variable Reward Scheduling)
    CREATE TABLE IF NOT EXISTS rewards (
        id TEXT PRIMARY KEY,
        name TEXT NOT NULL,
        reward_type TEXT NOT NULL,
        rarity TEXT NOT NULL,
        weight REAL DEFAULT 1.0,
        value INTEGER DEFAULT 0,
        icon TEXT DEFAULT '🎁',
        description TEXT DEFAULT '',
        is_active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- User Reward History (track rewards received)
    CREATE TABLE IF NOT EXISTS user_reward_history (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        reward_id TEXT NOT NULL,
        reward_name TEXT NOT NULL,
        rarity TEXT NOT NULL,
        received_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        context TEXT DEFAULT '{}',
        FOREIGN KEY (reward_id) REFERENCES rewards(id) ON DELETE CASCADE
    );
    
    -- User Reward Stats (aggregate stats per user)
    CREATE TABLE IF NOT EXISTS user_reward_stats (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL UNIQUE,
        total_rolls INTEGER DEFAULT 0,
        total_rewards INTEGER DEFAULT 0,
        common_count INTEGER DEFAULT 0,
        uncommon_count INTEGER DEFAULT 0,
        rare_count INTEGER DEFAULT 0,
        legendary_count INTEGER DEFAULT 0,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- ============================================
    -- Phase 4: Notifications & Reminders System
    -- ============================================
    
    -- Notifications table
    CREATE TABLE IF NOT EXISTS notifications (
        id TEXT PRIMARY KEY,
        type TEXT NOT NULL,
        title TEXT NOT NULL,
        message TEXT NOT NULL,
        priority TEXT DEFAULT 'medium',
        status TEXT DEFAULT 'pending',
        scheduled_for TIMESTAMP,
        sent_at TIMESTAMP,
        delivered_at TIMESTAMP,
        read INTEGER DEFAULT 0,
        entity_type TEXT,
        entity_id TEXT,
        action_url TEXT,
        metadata TEXT DEFAULT '{}',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Push subscriptions (Web Push API)
    CREATE TABLE IF NOT EXISTS push_subscriptions (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        endpoint TEXT NOT NULL UNIQUE,
        p256dh TEXT NOT NULL,
        auth TEXT NOT NULL,
        user_agent TEXT,
        device_name TEXT,
        last_active TIMESTAMP,
        is_active INTEGER DEFAULT 1,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Notification logs (delivery tracking)
    CREATE TABLE IF NOT EXISTS notification_logs (
        id TEXT PRIMARY KEY,
        notification_id TEXT NOT NULL,
        channel TEXT NOT NULL,
        status TEXT NOT NULL,
        error_message TEXT,
        response_code INTEGER,
        dispatched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        delivered_at TIMESTAMP,
        clicked_at TIMESTAMP,
        FOREIGN KEY (notification_id) REFERENCES notifications(id) ON DELETE CASCADE
    );
    
    -- Reminder schedules
    CREATE TABLE IF NOT EXISTS reminder_schedules (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        entity_type TEXT NOT NULL,
        entity_id TEXT NOT NULL,
        reminder_time TEXT,
        days_of_week TEXT DEFAULT '[]',
        enabled INTEGER DEFAULT 1,
        snooze_minutes INTEGER DEFAULT 5,
        max_snoozes INTEGER DEFAULT 3,
        current_snoozes INTEGER DEFAULT 0,
        is_smart INTEGER DEFAULT 0,
        smart_time TEXT,
        channels TEXT DEFAULT '["in_app"]',
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Completion history (for smart scheduling)
    CREATE TABLE IF NOT EXISTS completion_history (
        id TEXT PRIMARY KEY,
        user_id TEXT NOT NULL,
        entity_type TEXT NOT NULL,
        entity_id TEXT NOT NULL,
        completed_at TIMESTAMP NOT NULL,
        scheduled_for TIMESTAMP,
        variance_seconds INTEGER,
        reminder_sent INTEGER DEFAULT 0,
        snooze_count INTEGER DEFAULT 0,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Notification preferences
    CREATE TABLE IF NOT EXISTS notification_preferences (
        user_id TEXT PRIMARY KEY,
        enabled INTEGER DEFAULT 1,
        quiet_hours_start TEXT,
        quiet_hours_end TEXT,
        default_sound TEXT DEFAULT 'default',
        vibration_enabled INTEGER DEFAULT 1,
        habit_reminders_enabled INTEGER DEFAULT 1,
        task_reminders_enabled INTEGER DEFAULT 1,
        goal_reminders_enabled INTEGER DEFAULT 1,
        achievement_notifications_enabled INTEGER DEFAULT 1,
        streak_warnings_enabled INTEGER DEFAULT 1,
        daily_digest_enabled INTEGER DEFAULT 0,
        browser_notifications_enabled INTEGER DEFAULT 1,
        email_notifications_enabled INTEGER DEFAULT 0,
        email_address TEXT,
        smart_scheduling_enabled INTEGER DEFAULT 1,
        min_reminder_lead_minutes INTEGER DEFAULT 15,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- VAPID configuration (Web Push authentication)
    CREATE TABLE IF NOT EXISTS vapid_config (
        id INTEGER PRIMARY KEY CHECK (id = 1),
        subject TEXT NOT NULL,
        public_key TEXT NOT NULL,
        private_key TEXT NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    );
    
    -- Indexes for common queries
    CREATE INDEX IF NOT EXISTS idx_habit_entries_habit_id ON habit_entries(habit_id);
    CREATE INDEX IF NOT EXISTS idx_habit_entries_date ON habit_entries(entry_date);
    CREATE INDEX IF NOT EXISTS idx_events_entity ON events(entity_type, entity_id);
    CREATE INDEX IF NOT EXISTS idx_events_type ON events(event_type);
    CREATE INDEX IF NOT EXISTS idx_events_timestamp ON events(timestamp);
    CREATE INDEX IF NOT EXISTS idx_tasks_due_date ON tasks(due_date);
    CREATE INDEX IF NOT EXISTS idx_transactions_date ON transactions(trans_date);
    
    -- Notification indexes
    CREATE INDEX IF NOT EXISTS idx_notifications_status ON notifications(status);
    CREATE INDEX IF NOT EXISTS idx_notifications_scheduled ON notifications(scheduled_for);
    CREATE INDEX IF NOT EXISTS idx_notifications_entity ON notifications(entity_type, entity_id);
    CREATE INDEX IF NOT EXISTS idx_notification_logs_notification ON notification_logs(notification_id);
    CREATE INDEX IF NOT EXISTS idx_notification_logs_status ON notification_logs(status);
    CREATE INDEX IF NOT EXISTS idx_push_subscriptions_user ON push_subscriptions(user_id);
    CREATE INDEX IF NOT EXISTS idx_reminder_schedules_entity ON reminder_schedules(entity_type, entity_id);
    CREATE INDEX IF NOT EXISTS idx_completion_history_entity ON completion_history(entity_type, entity_id);
    CREATE INDEX IF NOT EXISTS idx_completion_history_completed ON completion_history(completed_at);
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