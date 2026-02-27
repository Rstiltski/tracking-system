"""
Database Migration - Social Accountability (Friends)

Migration: Add friend/connection tables
Version: 15

Tables added:
- friendships: Friend connections
- cheers: Encouragement messages
- activity_shares: Shared activities
- user_privacy_settings: Privacy preferences

Usage:
    python3 -m tracking_app.database_migrations.friend_migration
"""
import sqlite3
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent.parent / "tracking.db"


def migrate(conn: sqlite3.Connection) -> None:
    """Apply friend system migration."""
    logger.info("Applying social accountability migration...")

    # Create friendships table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS friendships (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            friend_id TEXT NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (friend_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    # Create cheers table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS cheers (
            id TEXT PRIMARY KEY,
            sender_id TEXT NOT NULL,
            receiver_id TEXT NOT NULL,
            habit_id TEXT,
            message TEXT DEFAULT '',
            cheer_type TEXT DEFAULT 'general',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (receiver_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    # Create activity_shares table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS activity_shares (
            id TEXT PRIMARY KEY,
            user_id TEXT NOT NULL,
            activity_type TEXT NOT NULL,
            habit_id TEXT,
            habit_name TEXT,
            details TEXT DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    # Create user_privacy_settings table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS user_privacy_settings (
            user_id TEXT PRIMARY KEY,
            share_achievements INTEGER DEFAULT 1,
            share_streaks INTEGER DEFAULT 1,
            share_completions INTEGER DEFAULT 0,
            allow_cheers INTEGER DEFAULT 1,
            visible_to TEXT DEFAULT 'friends',
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    # Create indexes
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_friendships_user
        ON friendships(user_id, status)
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_friendships_friend
        ON friendships(friend_id, status)
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_cheers_receiver
        ON cheers(receiver_id, created_at DESC)
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_activity_shares_user
        ON activity_shares(user_id, created_at DESC)
    """)

    # Update schema version
    conn.execute("""
        INSERT OR REPLACE INTO schema_version (version, applied_at)
        VALUES (15, ?)
    """, (datetime.now().isoformat(),))

    conn.commit()
    logger.info("Social accountability migration applied successfully!")


def run_migration() -> None:
    """Run the migration."""
    conn = sqlite3.connect(str(DB_PATH))
    try:
        migrate(conn)
    finally:
        conn.close()


if __name__ == "__main__":
    run_migration()
