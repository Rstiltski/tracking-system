"""
Database Migration - Habit Templates

This migration adds tables for storing habit templates and user custom templates.

Migration: Add habit template tables
Version: 5 (incrementing from schema_version = 4)

Tables added:
- habit_templates: Pre-built and custom templates
- template_habits: Habits within templates
- user_template_applications: Track template usage

Usage:
    python3 -m tracking_app.database_migrations.template_migration
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
    Apply habit template migration.

    Creates template tables.

    Args:
        conn: SQLite database connection
    """
    logger.info("Applying habit template migration...")

    # Create habit_templates table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS habit_templates (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            category TEXT DEFAULT 'custom',
            difficulty TEXT DEFAULT 'beginner',
            total_duration INTEGER DEFAULT 0,
            tags TEXT DEFAULT '[]',
            author TEXT DEFAULT 'System',
            is_public INTEGER DEFAULT 1,
            usage_count INTEGER DEFAULT 0,
            rating REAL DEFAULT 0.0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            user_id TEXT DEFAULT ''
        )
    """)

    # Create template_habits table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS template_habits (
            id TEXT PRIMARY KEY,
            template_id TEXT NOT NULL,
            name TEXT NOT NULL,
            description TEXT,
            icon TEXT DEFAULT '🎯',
            color TEXT DEFAULT '#6366f1',
            frequency TEXT DEFAULT 'daily',
            habit_type TEXT DEFAULT 'boolean',
            target_value REAL DEFAULT 0,
            target_type TEXT DEFAULT 'at_least',
            position INTEGER DEFAULT 0,
            duration_minutes INTEGER DEFAULT 2,
            category TEXT DEFAULT '',
            FOREIGN KEY (template_id) REFERENCES habit_templates(id) ON DELETE CASCADE
        )
    """)

    # Create user_template_applications table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS user_template_applications (
            id TEXT PRIMARY KEY,
            template_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            habits_created INTEGER DEFAULT 0,
            success INTEGER DEFAULT 1,
            FOREIGN KEY (template_id) REFERENCES habit_templates(id)
        )
    """)

    # Create indexes
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_templates_category
        ON habit_templates(category, is_public)
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_template_habits_template
        ON template_habits(template_id, position)
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_template_applications_user
        ON user_template_applications(user_id, applied_at)
    """)

    # Update schema version
    conn.execute("""
        INSERT OR REPLACE INTO schema_version (version, applied_at)
        VALUES (5, ?)
    """, (datetime.now().isoformat(),))

    conn.commit()
    logger.info("Habit template migration applied successfully!")


def rollback(conn: sqlite3.Connection) -> None:
    """
    Rollback habit template migration.

    Args:
        conn: SQLite database connection
    """
    logger.warning("Rolling back habit template migration...")

    # Drop indexes
    conn.execute("DROP INDEX IF EXISTS idx_templates_category")
    conn.execute("DROP INDEX IF EXISTS idx_template_habits_template")
    conn.execute("DROP INDEX IF EXISTS idx_template_applications_user")

    # Drop tables
    conn.execute("DROP TABLE IF EXISTS user_template_applications")
    conn.execute("DROP TABLE IF EXISTS template_habits")
    conn.execute("DROP TABLE IF EXISTS habit_templates")

    # Update schema version
    conn.execute("""
        INSERT OR REPLACE INTO schema_version (version, applied_at)
        VALUES (4, ?)
    """, (datetime.now().isoformat(),))

    conn.commit()
    logger.info("Habit template migration rolled back successfully!")


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
