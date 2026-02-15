"""
User Management Database Queries

Handles all database operations related to user management.
Following the architecture rules, this module focuses solely on user-related queries.
"""
from __future__ import annotations
import sqlite3
import bcrypt
from typing import Dict, Any, Optional, List
from database.connection import get_conn

def get_user(user_id: int) -> Optional[Dict[str, Any]]:
    """Get a user by ID."""
    conn = get_conn()
    conn.row_factory = sqlite3.Row
    
    try:
        result = conn.execute("""
            SELECT id, username, email, role, created_at, updated_at, 
                   last_login, is_active, must_change_password
            FROM users 
            WHERE id = ? AND is_active = 1
        """, (user_id,))
        
        user = result.fetchone()
        return dict(user) if user else None
    finally:
        conn.close()

def get_user_by_username(username: str) -> Optional[Dict[str, Any]]:
    """Get a user by username."""
    conn = get_conn()
    conn.row_factory = sqlite3.Row
    
    try:
        result = conn.execute("""
            SELECT id, username, email, role, created_at, updated_at, 
                   last_login, is_active, must_change_password
            FROM users 
            WHERE username = ? AND is_active = 1
        """, (username,))
        
        user = result.fetchone()
        return dict(user) if user else None
    finally:
        conn.close()

def create_user(username: str, email: str, role: str = 'staff', password: str = None) -> Optional[Dict[str, Any]]:
    """Create a new user account."""
    conn = get_conn()
    conn.row_factory = sqlite3.Row
    
    # Hash the password if provided
    if password:
        password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    else:
        # Generate a random temporary password
        import secrets
        import string
        temp_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
        password_hash = bcrypt.hashpw(temp_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    try:
        result = conn.execute("""
            INSERT INTO users (username, email, password_hash, role, must_change_password)
            VALUES (?, ?, ?, ?, ?)
            RETURNING id, username, email, role, created_at
        """, (username, email, password_hash, role, 1 if password is None else 0))
        
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

def update_user(user_id: int, **kwargs) -> bool:
    """Update user information."""
    conn = get_conn()
    
    # Prepare update fields and values
    allowed_fields = {'username', 'email', 'role', 'is_active', 'must_change_password'}
    update_fields = []
    values = []
    
    for field, value in kwargs.items():
        if field in allowed_fields:
            update_fields.append(f"{field} = ?")
            values.append(value)
    
    if not update_fields:
        return False  # No valid fields to update
    
    # Add updated_at timestamp
    update_fields.append("updated_at = CURRENT_TIMESTAMP")
    values.append(user_id)  # For WHERE clause
    
    try:
        query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = ?"
        conn.execute(query, values)
        conn.commit()
        return conn.total_changes > 0
    finally:
        conn.close()

def authenticate_user(username: str, password: str) -> Optional[Dict[str, Any]]:
    """Authenticate a user with username and password."""
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

def change_password(user_id: int, new_password: str, old_password: str = None) -> bool:
    """Change a user's password."""
    conn = get_conn()
    
    # Hash the new password
    password_hash = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    try:
        if old_password:
            # Verify old password first
            current_user = get_user(user_id)
            if not current_user:
                return False
                
            if not bcrypt.checkpw(old_password.encode('utf-8'), current_user['password_hash'].encode('utf-8')):
                return False  # Old password doesn't match
            
            # Update password and reset must_change_password flag
            conn.execute("""
                UPDATE users 
                SET password_hash = ?, must_change_password = 0, updated_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            """, (password_hash, user_id))
        else:
            # Admin password change (no old password verification)
            conn.execute("""
                UPDATE users 
                SET password_hash = ?, must_change_password = 0, updated_at = CURRENT_TIMESTAMP 
                WHERE id = ?
            """, (password_hash, user_id))
        
        conn.commit()
        return True
    finally:
        conn.close()

def list_users(limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    """List users with pagination."""
    conn = get_conn()
    conn.row_factory = sqlite3.Row
    
    try:
        result = conn.execute("""
            SELECT id, username, email, role, created_at, updated_at, 
                   last_login, is_active, must_change_password
            FROM users 
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """, (limit, offset))
        
        return [dict(row) for row in result.fetchall()]
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

def delete_user(user_id: int) -> bool:
    """Soft delete a user by setting is_active to 0."""
    conn = get_conn()
    
    try:
        conn.execute("UPDATE users SET is_active = 0, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (user_id,))
        conn.commit()
        return conn.total_changes > 0
    finally:
        conn.close()

def reset_user_password(user_id: int) -> str:
    """Reset a user's password to a random temporary password."""
    import secrets
    import string
    
    conn = get_conn()
    
    # Generate a random temporary password
    temp_password = ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(12))
    password_hash = bcrypt.hashpw(temp_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    
    try:
        conn.execute("""
            UPDATE users 
            SET password_hash = ?, must_change_password = 1, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        """, (password_hash, user_id))
        
        conn.commit()
        return temp_password
    finally:
        conn.close()