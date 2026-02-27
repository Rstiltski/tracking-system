"""
Database Migration - Relapse Prevention Plans

This migration adds tables for tracking relapse prevention plans and their usage.

Migration: Add relapse prevention plan tables
Version: 4 (incrementing from schema_version = 3)

Tables added:
- relapse_prevention_plans: User-created prevention plans
- relapse_plan_usage: Record of plan usage

Usage:
    python3 -m tracking_app.database_migrations.relapse_migration
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
    Apply relapse prevention plans migration.

    Creates the relapse_prevention_plans and relapse_plan_usage tables.

    Args:
        conn: SQLite database connection
    """
    logger.info("Applying relapse prevention plans migration...")

    # Create relapse prevention plans table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS relapse_prevention_plans (
            id TEXT PRIMARY KEY,
            habit_id TEXT NOT NULL,
            user_id TEXT DEFAULT '',
            category TEXT NOT NULL DEFAULT 'custom',
            trigger TEXT NOT NULL DEFAULT 'custom',
            if_condition TEXT NOT NULL,
            then_action TEXT NOT NULL,
            action_type TEXT DEFAULT 'reduce',
            backup_plan TEXT DEFAULT '',
            is_active INTEGER DEFAULT 1,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            last_used TIMESTAMP,
            effectiveness INTEGER,
            usage_count INTEGER DEFAULT 0,
            FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE
        )
    """)

    # Create relapse plan usage table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS relapse_plan_usage (
            id TEXT PRIMARY KEY,
            plan_id TEXT NOT NULL,
            habit_id TEXT NOT NULL,
            used_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            situation TEXT DEFAULT '',
            action_taken TEXT DEFAULT '',
            effectiveness INTEGER,
            notes TEXT DEFAULT '',
            FOREIGN KEY (plan_id) REFERENCES relapse_prevention_plans(id) ON DELETE CASCADE,
            FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE
        )
    """)

    # Create indexes for faster lookups
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_relapse_plans_habit
        ON relapse_prevention_plans(habit_id, is_active)
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_relapse_usage_habit
        ON relapse_plan_usage(habit_id, used_at DESC)
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_relapse_usage_plan
        ON relapse_plan_usage(plan_id, used_at DESC)
    """)

    # Update schema version
    conn.execute("""
        INSERT OR REPLACE INTO schema_version (version, applied_at)
        VALUES (4, ?)
    """, (datetime.now().isoformat(),))

    conn.commit()
    logger.info("Relapse prevention plans migration applied successfully!")


def rollback(conn: sqlite3.Connection) -> None:
    """
    Rollback relapse prevention plans migration.

    Drops the relapse prevention tables and related indexes.

    WARNING: This will delete all relapse prevention plan data!

    Args:
        conn: SQLite database connection
    """
    logger.warning("Rolling back relapse prevention plans migration...")

    # Drop indexes
    conn.execute("DROP INDEX IF EXISTS idx_relapse_plans_habit")
    conn.execute("DROP INDEX IF EXISTS idx_relapse_usage_habit")
    conn.execute("DROP INDEX IF EXISTS idx_relapse_usage_plan")

    # Drop tables
    conn.execute("DROP TABLE IF EXISTS relapse_plan_usage")
    conn.execute("DROP TABLE IF EXISTS relapse_prevention_plans")

    # Update schema version
    conn.execute("""
        INSERT OR REPLACE INTO schema_version (version, applied_at)
        VALUES (3, ?)
    """, (datetime.now().isoformat(),))

    conn.commit()
    logger.info("Relapse prevention plans migration rolled back successfully!")


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
