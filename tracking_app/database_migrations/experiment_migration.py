"""
Database Migration - Habit Experiments

Migration: Add experiment tables
Version: 14

Tables added:
- habit_experiments: Experiment definitions
- experiment_results: Experiment results

Usage:
    python3 -m tracking_app.database_migrations.experiment_migration
"""
import sqlite3
from pathlib import Path
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = Path(__file__).parent.parent.parent / "tracking.db"


def migrate(conn: sqlite3.Connection) -> None:
    """Apply experiment migration."""
    logger.info("Applying habit experiments migration...")

    # Create habit_experiments table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS habit_experiments (
            id TEXT PRIMARY KEY,
            habit_id TEXT NOT NULL,
            user_id TEXT NOT NULL,
            name TEXT NOT NULL,
            experiment_type TEXT NOT NULL,
            hypothesis TEXT,
            variant_a TEXT NOT NULL,
            variant_b TEXT NOT NULL,
            duration_days INTEGER DEFAULT 7,
            success_metric TEXT DEFAULT 'completion_rate',
            status TEXT DEFAULT 'draft',
            start_date DATE,
            end_date DATE,
            results TEXT DEFAULT '{}',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (habit_id) REFERENCES habits(id) ON DELETE CASCADE
        )
    """)

    # Create experiment_results table
    conn.execute("""
        CREATE TABLE IF NOT EXISTS experiment_results (
            id TEXT PRIMARY KEY,
            experiment_id TEXT NOT NULL,
            variant TEXT NOT NULL,
            date DATE NOT NULL,
            completed INTEGER DEFAULT 0,
            notes TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (experiment_id) REFERENCES habit_experiments(id) ON DELETE CASCADE
        )
    """)

    # Create indexes
    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_experiments_user
        ON habit_experiments(user_id, status)
    """)

    conn.execute("""
        CREATE INDEX IF NOT EXISTS idx_experiment_results_experiment
        ON experiment_results(experiment_id, date)
    """)

    # Update schema version
    conn.execute("""
        INSERT OR REPLACE INTO schema_version (version, applied_at)
        VALUES (14, ?)
    """, (datetime.now().isoformat(),))

    conn.commit()
    logger.info("Habit experiments migration applied successfully!")


def run_migration() -> None:
    """Run the migration."""
    conn = sqlite3.connect(str(DB_PATH))
    try:
        migrate(conn)
    finally:
        conn.close()


if __name__ == "__main__":
    run_migration()
