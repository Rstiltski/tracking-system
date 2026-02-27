"""
Database Migration - Implementation Intentions

Migration: Add implementation intention tables
Version: 12

Tables added:
- implementation_intentions: If-Then plans

Usage:
    python3 -m tracking_app.database_migrations.intention_migration
"""
import sqlite3
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent.parent / "tracking.db"


def migrate(conn: sqlite3.Connection) -> None:
    """Apply implementation intention migration."""
    logger.info("Applying implementation intention migration...")

    # Create implementation_intentions table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS implementation_intentions (
            id TEXT PRIMARY KEY,
            habit_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            if_condition TEXT NOT NULL,
            then_action TEXT NOT NULL,
            trigger_type TEXT DEFAULT 'custom',
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            completed_count INTEGER DEFAULT 0,
            last_completed DATE,
            FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE
        )
    """)

    # Create indexes
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_intentions_habit
        ON implementation_intentions(habit_id, is_active)
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_intentions_user
        ON implementation_intentions(user_id, is_active)
    """)

    # Update schema version
    conn.execute("""
        INSERT OR REPLACE INTO schema_version (version, applied_at)
        VALUES (12, ?)
    """, (datetime.now().isoformat(),))

    conn.commit()
    logger.info("Implementation intention migration applied successfully!")


def run_migration() -> None:
    """Run the migration."""
    conn = sqlite3.connect(str(DB_PATH))
    try:
        migrate(conn)
    finally:
        conn.close()


if __name__ == "__main__":
    run_migration()
