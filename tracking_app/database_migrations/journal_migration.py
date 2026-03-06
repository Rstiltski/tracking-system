"""
Database Migration - Journal Pages (Diary, Journal, Private Todos)

Migration: Add journal-related tables
Version: 9

Tables added:
- diary_entries: Private diary entries
- journal_entries: General journal entries  
- private_todos: Private todo items

Usage:
    python3 -m tracking_app.database_migrations.journal_migration
"""
import sqlite3
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent.parent / "tracking.db"


def migrate(conn: sqlite3.Connection) -> None:
    """Apply journal pages migration."""
    logger.info("Applying journal pages migration...")

    # Create diary_entries table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS diary_entries (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL DEFAULT '',
            content TEXT NOT NULL DEFAULT '',
            entry_date TEXT NOT NULL,
            mood TEXT DEFAULT 'good',
            tags TEXT DEFAULT '[]',
            is_private INTEGER DEFAULT 1,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)

    # Create journal_entries table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS journal_entries (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL DEFAULT '',
            content TEXT NOT NULL DEFAULT '',
            category TEXT DEFAULT 'free_write',
            tags TEXT DEFAULT '[]',
            is_private INTEGER DEFAULT 1,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)

    # Create private_todos table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS private_todos (
            id TEXT PRIMARY KEY,
            title TEXT NOT NULL,
            description TEXT DEFAULT '',
            priority TEXT DEFAULT 'medium',
            due_date TEXT,
            completed INTEGER DEFAULT 0,
            category TEXT DEFAULT '',
            is_private INTEGER DEFAULT 1,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL
        )
    """)

    # Create indexes for diary_entries
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_diary_entries_date
        ON diary_entries(entry_date DESC)
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_diary_entries_mood
        ON diary_entries(mood)
    """)

    # Create indexes for journal_entries
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_journal_entries_category
        ON journal_entries(category)
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_journal_entries_created
        ON journal_entries(created_at DESC)
    """)

    # Create indexes for private_todos
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_private_todos_completed
        ON private_todos(completed, due_date)
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_private_todos_priority
        ON private_todos(priority)
    """)

    # Update schema version
    conn.execute("""
        INSERT OR REPLACE INTO schema_version (version, applied_at)
        VALUES (9, ?)
    """, (datetime.now().isoformat(),))

    conn.commit()
    logger.info("Journal pages migration applied successfully!")


def run_migration() -> None:
    """Run the migration."""
    conn = sqlite3.connect(str(DB_PATH))
    try:
        migrate(conn)
    finally:
        conn.close()


if __name__ == "__main__":
    run_migration()