"""
Database Migration - Habit Notes

Migration: Add habit notes tables
Version: 7

Tables added:
- habit_notes: User notes and reflections

Usage:
    python3 -m tracking_app.database_migrations.note_migration
"""
import sqlite3
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent.parent / "tracking.db"


def migrate(conn: sqlite3.Connection) -> None:
    """Apply habit notes migration."""
    logger.info("Applying habit notes migration...")

    conn.execute("""
        CREATE TABLE IF NOT EXISTS habit_notes (
            id TEXT PRIMARY KEY,
            habit_id TEXT NOT NULL,
            user_id TEXT DEFAULT '',
            note_type TEXT DEFAULT 'daily',
            content TEXT NOT NULL,
            mood INTEGER,
            energy INTEGER,
            tags TEXT DEFAULT '[]',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            entry_date DATE,
            FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE
        )
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_habit_notes_habit
        ON habit_notes(habit_id, entry_date DESC)
    """)

    conn.execute("""
        INSERT OR REPLACE INTO schema_version (version, applied_at)
        VALUES (7, ?)
    """, (datetime.now().isoformat(),))

    conn.commit()
    logger.info("Habit notes migration applied successfully!")


def run_migration() -> None:
    """Run the migration."""
    conn = sqlite3.connect(str(DB_PATH))
    try:
        migrate(conn)
    finally:
        conn.close()


if __name__ == "__main__":
    run_migration()
