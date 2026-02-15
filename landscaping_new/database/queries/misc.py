"""
Miscellaneous Database Queries

Contains miscellaneous database functions that don't fit in other specific modules.
Following the architecture rules, this should remain focused and not become a dumping ground.
"""
from __future__ import annotations
import sqlite3
from typing import Dict, Any, Optional, List
from database.connection import get_conn

def get_system_stats(include_sensitive: bool = False) -> dict:
    """Get system statistics."""
    conn = get_conn()
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
    conn = get_conn()
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
    conn = get_conn()
    
    try:
        conn.execute(
            "UPDATE settings SET value = ?, updated_at = CURRENT_TIMESTAMP WHERE key = ?",
            (value, key)
        )
        conn.commit()
        return conn.total_changes > 0
    finally:
        conn.close()

def count_users() -> int:
    """Count the number of users in the system."""
    conn = get_conn()
    conn.row_factory = sqlite3.Row
    
    try:
        result = conn.execute("SELECT COUNT(*) as count FROM users").fetchone()
        return result['count']
    finally:
        conn.close()

def create_user(username: str, email: str, password_hash: str, role: str = 'staff') -> Dict[str, Any]:
    """Create a new user account."""
    conn = get_conn()
    conn.row_factory = sqlite3.Row
    
    try:
        result = conn.execute("""
            INSERT INTO users (username, email, password_hash, role)
            VALUES (?, ?, ?, ?)
            RETURNING id, username, email, role, created_at
        """, (username, email, password_hash, role))
        
        conn.commit()
        user_data = result.fetchone()
        
        if user_data:
            return dict(user_data)
        else:
            return None
    except sqlite3.IntegrityError as e:
        # Handle duplicate username or email
        if "username" in str(e):
            raise ValueError(f"Username '{username}' already exists")
        elif "email" in str(e):
            raise ValueError(f"Email '{email}' already exists")
        else:
            raise e
    finally:
        conn.close()

def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """Authenticate a user with username and password."""
    import bcrypt
    
    conn = get_conn()
    conn.row_factory = sqlite3.Row
    
    try:
        result = conn.execute("""
            SELECT id, username, email, password_hash, role, is_active, must_change_password
            FROM users 
            WHERE username = ? AND is_active = 1
        """, (username,))
        
        user = result.fetchone()
        
        if user and bcrypt.checkpw(password.encode('utf-8'), user['password_hash'].encode('utf-8')):
            # Update last login
            conn.execute("UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = ?", (user['id'],))
            conn.commit()
            
            return dict(user)
        else:
            return None
    finally:
        conn.close()

def log_audit_event(user_id: int, action: str, entity_type: str, entity_id: int, 
                   old_values: Optional[str] = None, new_values: Optional[str] = None) -> bool:
    """Log an audit event to the audit trail."""
    conn = get_conn()
    
    try:
        conn.execute("""
            INSERT INTO audit_log (user_id, action, entity_type, entity_id, old_values, new_values)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (user_id, action, entity_type, entity_id, old_values, new_values))
        
        conn.commit()
        return True
    except Exception:
        conn.rollback()
        return False
    finally:
        conn.close()

def get_audit_trail(entity_type: Optional[str] = None, entity_id: Optional[int] = None, 
                   limit: int = 100) -> List[Dict[str, Any]]:
    """Get audit trail entries, optionally filtered by entity type and ID."""
    conn = get_conn()
    conn.row_factory = sqlite3.Row
    
    try:
        query = "SELECT * FROM audit_log"
        params = []
        
        conditions = []
        if entity_type:
            conditions.append("entity_type = ?")
            params.append(entity_type)
        if entity_id is not None:
            conditions.append("entity_id = ?")
            params.append(entity_id)
        
        if conditions:
            query += " WHERE " + " AND ".join(conditions)
        
        query += " ORDER BY timestamp DESC LIMIT ?"
        params.append(limit)
        
        result = conn.execute(query, params)
        return [dict(row) for row in result.fetchall()]
    finally:
        conn.close()