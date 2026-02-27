"""
Database Migration - SRBAI Automaticity Survey

Migration: Add SRBAI survey tables
Version: 10

Tables added:
- srbai_results: Survey responses and automaticity scores

Usage:
    python3 -m tracking_app.database_migrations.srbai_migration
"""
import sqlite3
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent.parent / "tracking.db"


def migrate(conn: sqlite3.Connection) -> None:
    """Apply SRBAI migration."""
    logger.info("Applying SRBAI automaticity survey migration...")

    # Create srbai_results table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS srbai_results (
            id TEXT PRIMARY KEY,
            habit_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            q1_automatic INTEGER NOT NULL,
            q2_without_thinking INTEGER NOT NULL,
            q3_start_unintentionally INTEGER NOT NULL,
            q4_difficult_not_to_do INTEGER NOT NULL,
            automaticity_score REAL NOT NULL,
            is_habit_formed INTEGER NOT NULL,
            habit_strength TEXT NOT NULL,
            survey_date DATE NOT NULL,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE
        )
    """)

    # Create indexes
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_srbai_habit
        ON srbai_results(habit_id, survey_date DESC)
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_srbai_user
        ON srbai_results(user_id, survey_date DESC)
    """)

    # Update schema version
    conn.execute("""
        INSERT OR REPLACE INTO schema_version (version, applied_at)
        VALUES (10, ?)
    """, (datetime.now().isoformat(),))

    conn.commit()
    logger.info("SRBAI migration applied successfully!")


def run_migration() -> None:
    """Run the migration."""
    conn = sqlite3.connect(str(DB_PATH))
    try:
        migrate(conn)
    finally:
        conn.close()


if __name__ == "__main__":
    run_migration()
