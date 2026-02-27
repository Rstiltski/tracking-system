"""
Database Migration - Achievement System

This migration adds tables for tracking achievements and user progress.

Migration: Add achievement tables
Version: 6 (incrementing from schema_version = 5)

Tables added:
- achievements: Achievement definitions
- user_achievements: User's unlocked achievements

Usage:
    python3 -m tracking_app.database_migrations.achievement_migration
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
    Apply achievement migration.

    Creates achievement tables.

    Args:
        conn: SQLite database connection
    """
    logger.info("Applying achievement migration...")

    # Create achievements table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS achievements (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            category TEXT DEFAULT 'streak',
            tier TEXT DEFAULT 'bronze',
            icon TEXT DEFAULT '🏆',
            xp_reward INTEGER DEFAULT 50,
            requirement TEXT,
            requirement_data TEXT DEFAULT '{}',
            is_hidden INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Create user_achievements table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS user_achievements (
            id TEXT PRIMARY KEY,
            achievement_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            xp_awarded INTEGER DEFAULT 0,
            FOREIGN KEY (achievement_id) REFERENCES achievements(id) ON DELETE CASCADE
        )
    """)

    # Create indexes
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_user_achievements_user
        ON user_achievements(user_id, unlocked_at)
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_achievements_category
        ON achievements(category)
    """)

    # Insert default achievements
    default_achievements = [
        ("achieve_streak_7", "Week Warrior", "Maintain a 7-day streak", "streak", "bronze", "🔥", 50, '{"type": "streak_days", "value": 7}'),
        ("achieve_streak_30", "Month Master", "Maintain a 30-day streak", "streak", "silver", "🌟", 150, '{"type": "streak_days", "value": 30}'),
        ("achieve_streak_90", "Quarter Queen/King", "Maintain a 90-day streak", "streak", "gold", "👑", 400, '{"type": "streak_days", "value": 90}'),
        ("achieve_first_habit", "First Step", "Create your first habit", "special", "bronze", "🌱", 25, '{"type": "first_habit", "value": 1}'),
    ]

    for achieve_id, name, desc, category, tier, icon, xp, req_data in default_achievements:
        conn.execute(
            """INSERT OR IGNORE INTO achievements
               (id, name, description, category, tier, icon, xp_reward, requirement_data)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (achieve_id, name, desc, category, tier, icon, xp, req_data)
        )

    # Update schema version
    conn.execute("""
        INSERT OR REPLACE INTO schema_version (version, applied_at)
        VALUES (6, ?)
    """, (datetime.now().isoformat(),))

    conn.commit()
    logger.info("Achievement migration applied successfully!")


def rollback(conn: sqlite3.Connection) -> None:
    """
    Rollback achievement migration.

    Args:
        conn: SQLite database connection
    """
    logger.warning("Rolling back achievement migration...")

    # Drop indexes
    conn.execute("DROP INDEX IF EXISTS idx_user_achievements_user")
    conn.execute("DROP INDEX IF EXISTS idx_achievements_category")

    # Drop tables
    conn.execute("DROP TABLE IF EXISTS user_achievements")
    conn.execute("DROP TABLE IF EXISTS achievements")

    # Update schema version
    conn.execute("""
        INSERT OR REPLACE INTO schema_version (version, applied_at)
        VALUES (5, ?)
    """, (datetime.now().isoformat(),))

    conn.commit()
    logger.info("Achievement migration rolled back successfully!")


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
