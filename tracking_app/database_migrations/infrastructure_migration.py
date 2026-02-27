"""
Database Migration - Data Infrastructure (Events & Analytics)

Migration: Add event tracking tables
Version: 8

Tables added:
- habit_events: Habit-related events
- user_interactions: User feature interactions
- intervention_log: Intervention tracking

Usage:
    python3 -m tracking_app.database_migrations.infrastructure_migration
"""
import sqlite3
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent.parent / "tracking.db"


def migrate(conn: sqlite3.Connection) -> None:
    """Apply data infrastructure migration."""
    logger.info("Applying data infrastructure migration...")

    # Create habit_events table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS habit_events (
            id TEXT PRIMARY KEY,
            habit_id TEXT NOT NULL,
            user_id TEXT DEFAULT '',
            event_type TEXT NOT NULL,
            event_data TEXT DEFAULT '{}',
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE
        )
    """)

    # Create user_interactions table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS user_interactions (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            feature TEXT NOT NULL,
            action TEXT NOT NULL,
            metadata TEXT DEFAULT '{}',
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create intervention_log table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS intervention_log (
            id TEXT PRIMARY KEY,
            habit_id TEXT,
            user_id TEXT NOT NULL,
            intervention_type TEXT NOT NULL,
            user_action TEXT,
            details TEXT DEFAULT '{}',
            timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE SET NULL
        )
    """)

    # Create indexes
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_habit_events_user
        ON habit_events(user_id, timestamp DESC)
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_user_interactions_user
        ON user_interactions(user_id, timestamp DESC)
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_intervention_log_user
        ON intervention_log(user_id, timestamp DESC)
    """)

    # Update schema version
    conn.execute("""
        INSERT OR REPLACE INTO schema_version (version, applied_at)
        VALUES (8, ?)
    """, (datetime.now().isoformat(),))

    conn.commit()
    logger.info("Data infrastructure migration applied successfully!")


def run_migration() -> None:
    """Run the migration."""
    conn = sqlite3.connect(str(DB_PATH))
    try:
        migrate(conn)
    finally:
        conn.close()


if __name__ == "__main__":
    run_migration()
