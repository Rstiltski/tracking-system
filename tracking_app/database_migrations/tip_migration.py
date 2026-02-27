"""
Database Migration - Environment Tips

Migration: Add environment tip tables
Version: 11

Tables added:
- user_tip_interactions: Track user interactions with tips

Usage:
    python3 -m tracking_app.database_migrations.tip_migration
"""
import sqlite3
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent.parent / "tracking.db"


def migrate(conn: sqlite3.Connection) -> None:
    """Apply environment tip migration."""
    logger.info("Applying environment tip migration...")

    # Create user_tip_interactions table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS user_tip_interactions (
            id TEXT PRIMARY KEY,
            tip_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            habit_id TEXT,
            action TEXT NOT NULL DEFAULT 'viewed',
            notes TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE SET NULL
        )
    """)

    # Create indexes
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_tip_interactions_user
        ON user_tip_interactions(user_id, created_at DESC)
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_tip_interactions_habit
        ON user_tip_interactions(habit_id, created_at DESC)
    """)

    # Update schema version
    conn.execute("""
        INSERT OR REPLACE INTO schema_version (version, applied_at)
        VALUES (11, ?)
    """, (datetime.now().isoformat(),))

    conn.commit()
    logger.info("Environment tip migration applied successfully!")


def run_migration() -> None:
    """Run the migration."""
    conn = sqlite3.connect(str(DB_PATH))
    try:
        migrate(conn)
    finally:
        conn.close()


if __name__ == "__main__":
    run_migration()
