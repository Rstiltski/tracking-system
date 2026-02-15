"""
Customer Management Database Queries

Handles all database operations related to customer management.
Following the architecture rules, this module focuses solely on customer-related queries.
"""
from __future__ import annotations
import sqlite3
from typing import Dict, Any, Optional, List
from database.connection import get_conn

def get_customer(customer_id: int) -> Optional[Dict[str, Any]]:
    """Get a customer by ID."""
    conn = get_conn()
    conn.row_factory = sqlite3.Row
    
    try:
        result = conn.execute("""
            SELECT id, name, email, phone, address, created_at, updated_at, is_active
            FROM customers 
            WHERE id = ? AND is_active = 1
        """, (customer_id,))
        
        customer = result.fetchone()
        return dict(customer) if customer else None
    finally:
        conn.close()

def create_customer(name: str, email: str = None, phone: str = None, address: str = None) -> Optional[Dict[str, Any]]:
    """Create a new customer."""
    conn = get_conn()
    conn.row_factory = sqlite3.Row
    
    try:
        result = conn.execute("""
            INSERT INTO customers (name, email, phone, address)
            VALUES (?, ?, ?, ?)
            RETURNING id, name, email, phone, address, created_at
        """, (name, email, phone, address))
        
        conn.commit()
        customer_data = result.fetchone()
        
        if customer_data:
            return dict(customer_data)
        else:
            return None
    except sqlite3.IntegrityError as e:
        # Handle any constraint violations
        raise ValueError(f"Error creating customer: {str(e)}")
    finally:
        conn.close()

def update_customer(customer_id: int, **kwargs) -> bool:
    """Update customer information."""
    conn = get_conn()
    
    # Prepare update fields and values
    allowed_fields = {'name', 'email', 'phone', 'address', 'is_active'}
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
    values.append(customer_id)  # For WHERE clause
    
    try:
        query = f"UPDATE customers SET {', '.join(update_fields)} WHERE id = ?"
        conn.execute(query, values)
        conn.commit()
        return conn.total_changes > 0
    finally:
        conn.close()

def list_customers(limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    """List customers with pagination."""
    conn = get_conn()
    conn.row_factory = sqlite3.Row
    
    try:
        result = conn.execute("""
            SELECT id, name, email, phone, address, created_at, updated_at, is_active
            FROM customers 
            WHERE is_active = 1
            ORDER BY created_at DESC
            LIMIT ? OFFSET ?
        """, (limit, offset))
        
        return [dict(row) for row in result.fetchall()]
    finally:
        conn.close()

def search_customers(query: str) -> List[Dict[str, Any]]:
    """Search customers by name, email, or phone."""
    conn = get_conn()
    conn.row_factory = sqlite3.Row
    
    try:
        search_term = f"%{query}%"
        result = conn.execute("""
            SELECT id, name, email, phone, address, created_at, updated_at, is_active
            FROM customers 
            WHERE is_active = 1 
            AND (name LIKE ? OR email LIKE ? OR phone LIKE ?)
            ORDER BY name
        """, (search_term, search_term, search_term))
        
        return [dict(row) for row in result.fetchall()]
    finally:
        conn.close()

def count_customers() -> int:
    """Count the number of active customers in the system."""
    conn = get_conn()
    conn.row_factory = sqlite3.Row
    
    try:
        result = conn.execute("SELECT COUNT(*) as count FROM customers WHERE is_active = 1").fetchone()
        return result['count']
    finally:
        conn.close()

def delete_customer(customer_id: int) -> bool:
    """Soft delete a customer by setting is_active to 0."""
    conn = get_conn()
    
    try:
        conn.execute("UPDATE customers SET is_active = 0, updated_at = CURRENT_TIMESTAMP WHERE id = ?", (customer_id,))
        conn.commit()
        return conn.total_changes > 0
    finally:
        conn.close()

def get_customer_jobs(customer_id: int) -> List[Dict[str, Any]]:
    """Get all jobs associated with a customer."""
    conn = get_conn()
    conn.row_factory = sqlite3.Row
    
    try:
        result = conn.execute("""
            SELECT id, title, description, status, scheduled_date, completed_date, created_at, updated_at
            FROM jobs 
            WHERE customer_id = ?
            ORDER BY created_at DESC
        """, (customer_id,))
        
        return [dict(row) for row in result.fetchall()]
    finally:
        conn.close()