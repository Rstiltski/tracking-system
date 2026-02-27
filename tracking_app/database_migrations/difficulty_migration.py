"""
Database Migration - Habit Difficulty Tracking

This migration adds tables for tracking habit difficulty ratings and adjustments.

Migration: Add difficulty tracking tables
Version: 3 (incrementing from schema_version = 2)

Tables added:
- difficulty_ratings: User difficulty ratings
- difficulty_adjustments: Record of adjustments made

Usage:
    python3 -m tracking_app.database_migrations.difficulty_migration
"""
import sqlite3
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent.parent / "tracking.db"


def migrate(conn: sqlite3.Connection) -> None:
    """
    Apply difficulty tracking migration.

    Creates the difficulty_ratings and difficulty_adjustments tables.

    Args:
        conn: SQLite database connection
    """
    logger.info("Applying difficulty tracking migration...")

    # Create difficulty ratings table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS difficulty_ratings (
            id TEXT PRIMARY KEY,
            habit_id TEXT NOT NULL,
            user_id TEXT DEFAULT '',
            rating TEXT NOT NULL DEFAULT 'just_right',
            notes TEXT DEFAULT '',
            rated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            adjustment_made INTEGER DEFAULT 0,
            adjustment_type TEXT,
            adjustment_details TEXT DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE
        )
    """)

    # Create difficulty adjustments table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS difficulty_adjustments (
            id TEXT PRIMARY KEY,
            habit_id TEXT NOT NULL,
            user_id TEXT DEFAULT '',
            adjustment_type TEXT NOT NULL,
            old_value TEXT,
            new_value TEXT,
            reason TEXT DEFAULT '',
            adjusted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            effectiveness INTEGER,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE
        )
    """)

    # Create indexes for faster lookups
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_difficulty_ratings_habit
        ON difficulty_ratings(habit_id, rated_at DESC)
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_difficulty_adjustments_habit
        ON difficulty_adjustments(habit_id, adjusted_at DESC)
    """)

    # Update schema version
    conn.execute("""
        INSERT OR REPLACE INTO schema_version (version, applied_at)
        VALUES (3, ?)
    """, (datetime.now().isoformat(),))

    conn.commit()
    logger.info("Difficulty tracking migration applied successfully!")


def rollback(conn: sqlite3.Connection) -> None:
    """
    Rollback difficulty tracking migration.

    Drops the difficulty tracking tables and related indexes.

    WARNING: This will delete all difficulty rating and adjustment data!

    Args:
        conn: SQLite database connection
    """
    logger.warning("Rolling back difficulty tracking migration...")

    # Drop indexes
    conn.execute("DROP INDEX IF EXISTS idx_difficulty_ratings_habit")
    conn.execute("DROP INDEX IF EXISTS idx_difficulty_adjustments_habit")

    # Drop tables
    conn.execute("DROP TABLE IF EXISTS difficulty_ratings")
    conn.execute("DROP TABLE IF EXISTS difficulty_adjustments")

    # Update schema version
    conn.execute("""
        INSERT OR REPLACE INTO schema_version (version, applied_at)
        VALUES (2, ?)
    """, (datetime.now().isoformat(),))

    conn.commit()
    logger.info("Difficulty tracking migration rolled back successfully!")


def run_migration() -> None:
    """Run the migration."""
    import sqlite3

    conn = sqlite3.connect(str(DB_PATH))
    try:
        migrate(conn)
    finally:
        conn.close()


def run_rollback() -> None:
    """Run the rollback."""
    import sqlite3

    conn = sqlite3.connect(str(DB_PATH))
    try:
        rollback(conn)
    finally:
        conn.close()


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1 and sys.argv[1] == "rollback":
        run_rollback()
    else:
        run_migration()
