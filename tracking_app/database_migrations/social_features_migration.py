"""
Database Migration - Competitions & Template Sharing

Migration: Add competition and template sharing tables
Version: 16

Tables added:
- competitions: Competition definitions
- competition_participants: Competition participants
- leaderboard_entries: Leaderboard entries
- shared_templates: Shared templates
- template_ratings: Template ratings

Usage:
    python3 -m tracking_app.database_migrations.social_features_migration
"""
import sqlite3
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent.parent / "tracking.db"


def migrate(conn: sqlite3.Connection) -> None:
    """Apply social features migration."""
    logger.info("Applying competitions & template sharing migration...")

    # Create competitions table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS competitions (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            competition_type TEXT NOT NULL,
            status TEXT DEFAULT 'draft',
            start_date DATE,
            end_date DATE,
            creator_id TEXT,
            max_participants INTEGER DEFAULT 0,
            is_public INTEGER DEFAULT 1,
            prize TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (creator_id) REFERENCES users(id)
        )
    """)

    # Create competition_participants table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS competition_participants (
            id TEXT PRIMARY KEY,
            competition_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            score REAL DEFAULT 0,
            rank INTEGER DEFAULT 0,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (competition_id) REFERENCES competitions(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    # Create shared_templates table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS shared_templates (
            id TEXT PRIMARY KEY,
            template_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            is_public INTEGER DEFAULT 1,
            clone_count INTEGER DEFAULT 0,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    # Create template_ratings table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS template_ratings (
            id TEXT PRIMARY KEY,
            shared_template_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            rating INTEGER NOT NULL,
            review TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (shared_template_id) REFERENCES shared_templates(id) ON DELETE CASCADE,
            FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
        )
    """)

    # Create indexes
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_competitions_status
        ON competitions(status, is_public)
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_participants_competition
        ON competition_participants(competition_id, score DESC)
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_shared_templates_public
        ON shared_templates(is_public, created_at DESC)
    """)

    # Update schema version
    conn.execute("""
        INSERT OR REPLACE INTO schema_version (version, applied_at)
        VALUES (16, ?)
    """, (datetime.now().isoformat(),))

    conn.commit()
    logger.info("Social features migration applied successfully!")


def run_migration() -> None:
    """Run the migration."""
    conn = sqlite3.connect(str(DB_PATH))
    try:
        migrate(conn)
    finally:
        conn.close()


if __name__ == "__main__":
    run_migration()
