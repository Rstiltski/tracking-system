"""
Database Initialization for Landscaping System

Initializes the database schema and sets up basic data structures.
Following the architecture rules, this handles schema creation and initial data seeding.
"""
from __future__ import annotations
import sqlite3
import logging
from pathlib import Path
from typing import List, Tuple

# Initialize logger
logger = logging.getLogger(__name__)

# Database path - using dynamic resolution as per architecture rules
BASE_DIR = Path(__file__).parent.parent.resolve()
DB_PATH = BASE_DIR / "landscaping.db"

def init_db() -> None:
    """Initialize the database with all required tables."""
    logger.info(f"Initializing database at: {DB_PATH}")
    
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row  # Enable dict-like access to rows
    conn.execute("PRAGMA foreign_keys = ON")  # Enable foreign key constraints
    
    try:
        # Create users table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                role TEXT NOT NULL DEFAULT 'staff',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_login TIMESTAMP,
                is_active BOOLEAN DEFAULT 1,
                must_change_password BOOLEAN DEFAULT 0
            )
        """)
        
        # Create customers table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                email TEXT,
                phone TEXT,
                address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active BOOLEAN DEFAULT 1
            )
        """)
        
        # Create jobs table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS jobs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                description TEXT,
                status TEXT DEFAULT 'pending',
                scheduled_date DATE,
                completed_date DATE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers (id)
            )
        """)
        
        # Create settings table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key TEXT UNIQUE NOT NULL,
                value TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create audit log table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS audit_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action TEXT NOT NULL,
                entity_type TEXT,
                entity_id INTEGER,
                old_values TEXT,
                new_values TEXT,
                ip_address TEXT,
                user_agent TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        """)
        
        # Insert default settings
        default_settings = [
            ('company_name', 'Landscaping Co.', 'Company name for display'),
            ('company_address', '123 Main St, City, State 12345', 'Company address'),
            ('default_hourly_rate', '75.00', 'Default hourly rate for labor'),
            ('tax_rate', '8.5', 'Default tax rate percentage'),
            ('payment_terms', 'Net 30', 'Default payment terms'),
            ('email_signature', 'Best regards,\nThe Landscaping Team', 'Default email signature')
        ]
        
        for key, value, description in default_settings:
            conn.execute("""
                INSERT OR IGNORE INTO settings (key, value, description)
                VALUES (?, ?, ?)
            """, (key, value, description))
        
        # Create admin user if none exists
        cursor = conn.execute("SELECT COUNT(*) as count FROM users")
        user_count = cursor.fetchone()['count']
        
        if user_count == 0:
            # Create default admin user
            import bcrypt
            password_hash = bcrypt.hashpw(b"admin123", bcrypt.gensalt()).decode('utf-8')
            
            conn.execute("""
                INSERT INTO users (username, email, password_hash, role, is_active)
                VALUES (?, ?, ?, ?, ?)
            """, ("admin", "admin@landscaping.com", password_hash, "admin", 1))
            
            logger.info("Created default admin user: admin / admin123")
        
        # Commit all changes
        conn.commit()
        logger.info("Database initialized successfully")
        
    except Exception as e:
        logger.error(f"Error initializing database: {e}")
        conn.rollback()
        raise
    finally:
        conn.close()

def get_system_stats(include_sensitive: bool = False) -> dict:
    """Get system statistics."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    
    try:
        # Count users
        user_count = conn.execute("SELECT COUNT(*) as count FROM users WHERE is_active = 1").fetchone()['count']
        
        # Count customers
        customer_count = conn.execute("SELECT COUNT(*) as count FROM customers WHERE is_active = 1").fetchone()['count']
        
        # Count jobs
        job_count = conn.execute("SELECT COUNT(*) as count FROM jobs").fetchone()['count']
        
        stats = {
            'user_count': user_count,
            'customer_count': customer_count,
            'job_count': job_count,
            'database_path': str(DB_PATH),
            'database_size_mb': round(Path(DB_PATH).stat().st_size / (1024 * 1024), 2)
        }
        
        if include_sensitive:
            # Add sensitive stats if requested
            stats['last_login'] = conn.execute(
                "SELECT MAX(last_login) as last_login FROM users WHERE last_login IS NOT NULL"
            ).fetchone()['last_login']
        
        return stats
    finally:
        conn.close()

def get_setting(key: str) -> str:
    """Get a setting value by key."""
    conn = sqlite3.connect(str(DB_PATH))
    conn.row_factory = sqlite3.Row
    
    try:
        result = conn.execute(
            "SELECT value FROM settings WHERE key = ?", (key,)
        ).fetchone()
        
        return result['value'] if result else None
    finally:
        conn.close()

def update_setting(key: str, value: str) -> bool:
    """Update a setting value."""
    conn = sqlite3.connect(str(DB_PATH))
    
    try:
        conn.execute(
            "UPDATE settings SET value = ?, updated_at = CURRENT_TIMESTAMP WHERE key = ?",
            (value, key)
        )
        conn.commit()
        return conn.total_changes > 0
    finally:
        conn.close()

if __name__ == "__main__":
    init_db()
    print("Database initialized successfully!")
    print("System stats:", get_system_stats())