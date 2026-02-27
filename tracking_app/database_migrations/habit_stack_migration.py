"""
Database Migration - Habit Stacking

Migration: Add habit stacking tables
Version: 9

Tables added:
- habit_stacks: Stack definitions
- stack_items: Individual habits in stacks
- stack_completions: Stack completion tracking

Usage:
    python3 -m tracking_app.database_migrations.habit_stack_migration
"""
import sqlite3
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent.parent / "tracking.db"


def migrate(conn: sqlite3.Connection) -> None:
    """Apply habit stacking migration."""
    logger.info("Applying habit stacking migration...")

    # Create habit_stacks table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS habit_stacks (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            name TEXT NOT NULL,
            trigger_description TEXT,
            anchor_category TEXT DEFAULT 'custom',
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create stack_items table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS stack_items (
            id TEXT PRIMARY KEY,
            stack_id TEXT NOT NULL,
            habit_id TEXT,
            position_index INTEGER NOT NULL,
            delay_seconds INTEGER DEFAULT 0,
            is_tiny INTEGER DEFAULT 1,
            tiny_description TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (stack_id) REFERENCES habit_stacks(id) ON DELETE CASCADE,
            FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE SET NULL
        )
    """)

    # Create stack_completions table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS stack_completions (
            id TEXT PRIMARY KEY,
            stack_id TEXT NOT NULL,
            completion_date DATE NOT NULL,
            completed_items TEXT DEFAULT '[]',
            completion_order TEXT DEFAULT '[]',
            conversion_rate REAL DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (stack_id) REFERENCES habit_stacks(id) ON DELETE CASCADE
        )
    """)

    # Create indexes
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_habit_stacks_user
        ON habit_stacks(user_id, is_active)
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_stack_items_stack
        ON stack_items(stack_id, position_index)
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_stack_completions_stack
        ON stack_completions(stack_id, completion_date)
    """)

    # Update schema version
    conn.execute("""
        INSERT OR REPLACE INTO schema_version (version, applied_at)
        VALUES (9, ?)
    """, (datetime.now().isoformat(),))

    conn.commit()
    logger.info("Habit stacking migration applied successfully!")


def run_migration() -> None:
    """Run the migration."""
    conn = sqlite3.connect(str(DB_PATH))
    try:
        migrate(conn)
    finally:
        conn.close()


if __name__ == "__main__":
    run_migration()
