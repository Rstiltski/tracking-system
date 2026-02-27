"""
Database Migration - Smart Suggestions

Migration: Add suggestion tables
Version: 13

Tables added:
- suggestions: Smart suggestions
- suggestion_feedback: User feedback on suggestions

Usage:
    python3 -m tracking_app.database_migrations.suggestion_migration
"""
import sqlite3
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent.parent / "tracking.db"


def migrate(conn: sqlite3.Connection) -> None:
    """Apply suggestion migration."""
    logger.info("Applying smart suggestions migration...")

    # Create suggestions table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS suggestions (
            id TEXT PRIMARY KEY,
            habit_id TEXT,
            user_id TEXT NOT NULL,
            suggestion_type TEXT NOT NULL,
            priority TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            action TEXT,
            metadata TEXT DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            dismissed INTEGER DEFAULT 0,
            acted_upon INTEGER DEFAULT 0,
            FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE SET NULL
        )
    """)

    # Create suggestion_feedback table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS suggestion_feedback (
            id TEXT PRIMARY KEY,
            suggestion_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            helpful INTEGER NOT NULL,
            notes TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (suggestion_id) REFERENCES suggestions(id) ON DELETE CASCADE
        )
    """)

    # Create indexes
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_suggestions_user
        ON suggestions(user_id, dismissed, created_at DESC)
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_feedback_suggestion
        ON suggestion_feedback(suggestion_id)
    """)

    # Update schema version
    conn.execute("""
        INSERT OR REPLACE INTO schema_version (version, applied_at)
        VALUES (13, ?)
    """, (datetime.now().isoformat(),))

    conn.commit()
    logger.info("Smart suggestions migration applied successfully!")


def run_migration() -> None:
    """Run the migration."""
    conn = sqlite3.connect(str(DB_PATH))
    try:
        migrate(conn)
    finally:
        conn.close()


if __name__ == "__main__":
    run_migration()
