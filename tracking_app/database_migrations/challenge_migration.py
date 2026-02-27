"""
Database Migration - Group Challenges

Migration: Add challenge tables
Version: 17

Tables added:
- group_challenges: Challenge definitions
- challenge_participants: Challenge participants
- challenge_checkins: Daily check-ins
- challenge_certificates: Completion certificates

Usage:
    python3 -m tracking_app.database_migrations.challenge_migration
"""
import sqlite3
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent.parent / "tracking.db"


def migrate(conn: sqlite3.Connection) -> None:
    """Apply group challenges migration."""
    logger.info("Applying group challenges migration...")

    # Create group_challenges table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS group_challenges (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            challenge_type TEXT NOT NULL,
            description TEXT,
            status TEXT DEFAULT 'draft',
            start_date DATE,
            end_date DATE,
            creator_id TEXT,
            max_participants INTEGER DEFAULT 0,
            is_public INTEGER DEFAULT 1,
            goal_description TEXT,
            certificate_template TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (creator_id) REFERENCES users(id)
        )
    """)

    # Create challenge_participants table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS challenge_participants (
            id TEXT PRIMARY KEY,
            challenge_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            progress REAL DEFAULT 0,
            completions INTEGER DEFAULT 0,
            streak INTEGER DEFAULT 0,
            completed INTEGER DEFAULT 0,
            certificate_earned INTEGER DEFAULT 0,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (challenge_id) REFERENCES group_challenges(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    # Create challenge_checkins table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS challenge_checkins (
            id TEXT PRIMARY KEY,
            challenge_id TEXT NOT NULL,
            participant_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            check_in_date DATE NOT NULL,
            completed INTEGER DEFAULT 0,
            notes TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (challenge_id) REFERENCES group_challenges(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    # Create challenge_certificates table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS challenge_certificates (
            id TEXT PRIMARY KEY,
            challenge_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            certificate_url TEXT,
            earned_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (challenge_id) REFERENCES group_challenges(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    # Create indexes
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_challenges_status
        ON group_challenges(status, is_public)
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_participants_challenge
        ON challenge_participants(challenge_id, progress DESC)
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_checkins_challenge
        ON challenge_checkins(challenge_id, check_in_date DESC)
    """)

    # Update schema version
    conn.execute("""
        INSERT OR REPLACE INTO schema_version (version, applied_at)
        VALUES (17, ?)
    """, (datetime.now().isoformat(),))

    conn.commit()
    logger.info("Group challenges migration applied successfully!")


def run_migration() -> None:
    """Run the migration."""
    conn = sqlite3.connect(str(DB_PATH))
    try:
        migrate(conn)
    finally:
        conn.close()


if __name__ == "__main__":
    run_migration()
