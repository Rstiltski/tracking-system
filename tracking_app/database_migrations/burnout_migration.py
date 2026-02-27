"""
Database Migration - Burnout Risk Tracking

This migration adds tables for tracking burnout risk assessments.

Migration: Add burnout_risk_snapshots table
Version: 2 (incrementing from schema_version = 1)

Tables added:
- burnout_risk_snapshots: Historical burnout risk assessments

Usage:
    python3 -m tracking_app.database_migrations.burnout_migration
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
    Apply burnout risk tracking migration.

    Creates the burnout_risk_snapshots table if it doesn't exist.

    Args:
        conn: SQLite database connection
    """
    logger.info("Applying burnout risk tracking migration...")

    # Create burnout risk snapshots table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS burnout_risk_snapshots (
            id TEXT PRIMARY KEY,
            habit_id TEXT NOT NULL,
            user_id TEXT DEFAULT '',
            risk_score REAL NOT NULL DEFAULT 0.0,
            risk_level TEXT NOT NULL DEFAULT 'low',
            contributing_factors TEXT DEFAULT '{}',
            assessment_date DATE NOT NULL,
            trend TEXT DEFAULT 'stable',
            previous_score REAL DEFAULT 0.0,
            intervention_suggested INTEGER DEFAULT 0,
            intervention_type TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE
        )
    """)

    # Create index for faster lookups by habit_id and assessment_date
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_burnout_habit_date
        ON burnout_risk_snapshots(habit_id, assessment_date)
    """)

    # Create index for finding at-risk habits
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_burnout_risk_level
        ON burnout_risk_snapshots(risk_level, assessment_date)
    """)

    # Update schema version
    conn.execute("""
        INSERT OR REPLACE INTO schema_version (version, applied_at)
        VALUES (2, ?)
    """, (datetime.now().isoformat(),))

    conn.commit()
    logger.info("Burnout risk tracking migration applied successfully!")


def rollback(conn: sqlite3.Connection) -> None:
    """
    Rollback burnout risk tracking migration.

    Drops the burnout_risk_snapshots table and related indexes.

    WARNING: This will delete all burnout risk data!

    Args:
        conn: SQLite database connection
    """
    logger.warning("Rolling back burnout risk tracking migration...")

    # Drop indexes
    conn.execute("DROP INDEX IF EXISTS idx_burnout_habit_date")
    conn.execute("DROP INDEX IF EXISTS idx_burnout_risk_level")

    # Drop table
    conn.execute("DROP TABLE IF EXISTS burnout_risk_snapshots")

    # Update schema version
    conn.execute("""
        INSERT OR REPLACE INTO schema_version (version, applied_at)
        VALUES (1, ?)
    """, (datetime.now().isoformat(),))

    conn.commit()
    logger.info("Burnout risk tracking migration rolled back successfully!")


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
