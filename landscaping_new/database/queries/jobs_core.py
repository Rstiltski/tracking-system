"""
Job Management Database Queries

Handles all database operations related to job management.
Following the architecture rules, this module focuses solely on job-related queries.
"""
from __future__ import annotations
import sqlite3
from typing import Dict, Any, Optional, List
from database.connection import get_conn

def get_job(job_id: int) -> Optional[Dict[str, Any]]:
    """Get a job by ID."""
    conn = get_conn()
    conn.row_factory = sqlite3.Row
    
    try:
        result = conn.execute("""
            SELECT j.id, j.customer_id, j.title, j.description, j.status, 
                   j.scheduled_date, j.completed_date, j.created_at, j.updated_at,
                   c.name as customer_name, c.email as customer_email
            FROM jobs j
            LEFT JOIN customers c ON j.customer_id = c.id
            WHERE j.id = ?
        """, (job_id,))
        
        job = result.fetchone()
        return dict(job) if job else None
    finally:
        conn.close()

def create_job(customer_id: int, title: str, description: str = None, 
               scheduled_date: str = None, status: str = 'pending') -> Optional[Dict[str, Any]]:
    """Create a new job."""
    conn = get_conn()
    conn.row_factory = sqlite3.Row
    
    try:
        result = conn.execute("""
            INSERT INTO jobs (customer_id, title, description, scheduled_date, status)
            VALUES (?, ?, ?, ?, ?)
            RETURNING id, customer_id, title, description, status, scheduled_date, created_at
        """, (customer_id, title, description, scheduled_date, status))
        
        conn.commit()
        job_data = result.fetchone()
        
        if job_data:
            return dict(job_data)
        else:
            return None
    except sqlite3.IntegrityError as e:
        # Handle any constraint violations
        raise ValueError(f"Error creating job: {str(e)}")
    finally:
        conn.close()

def update_job(job_id: int, **kwargs) -> bool:
    """Update job information."""
    conn = get_conn()
    
    # Prepare update fields and values
    allowed_fields = {'title', 'description', 'status', 'scheduled_date', 'completed_date'}
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
    values.append(job_id)  # For WHERE clause
    
    try:
        query = f"UPDATE jobs SET {', '.join(update_fields)} WHERE id = ?"
        conn.execute(query, values)
        conn.commit()
        return conn.total_changes > 0
    finally:
        conn.close()

def list_jobs(limit: int = 100, offset: int = 0, status: str = None) -> List[Dict[str, Any]]:
    """List jobs with pagination and optional status filter."""
    conn = get_conn()
    conn.row_factory = sqlite3.Row
    
    try:
        query = """
            SELECT j.id, j.customer_id, j.title, j.description, j.status, 
                   j.scheduled_date, j.completed_date, j.created_at, j.updated_at,
                   c.name as customer_name
            FROM jobs j
            LEFT JOIN customers c ON j.customer_id = c.id
        """
        
        params = []
        if status:
            query += " WHERE j.status = ?"
            params.append(status)
        
        query += " ORDER BY j.created_at DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])
        
        result = conn.execute(query, params)
        return [dict(row) for row in result.fetchall()]
    finally:
        conn.close()

def list_jobs_for_customer(customer_id: int, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
    """List jobs for a specific customer."""
    conn = get_conn()
    conn.row_factory = sqlite3.Row
    
    try:
        result = conn.execute("""
            SELECT j.id, j.customer_id, j.title, j.description, j.status, 
                   j.scheduled_date, j.completed_date, j.created_at, j.updated_at,
                   c.name as customer_name
            FROM jobs j
            LEFT JOIN customers c ON j.customer_id = c.id
            WHERE j.customer_id = ?
            ORDER BY j.created_at DESC
            LIMIT ? OFFSET ?
        """, (customer_id, limit, offset))
        
        return [dict(row) for row in result.fetchall()]
    finally:
        conn.close()

def list_jobs_for_date(date: str) -> List[Dict[str, Any]]:
    """List jobs scheduled for a specific date."""
    conn = get_conn()
    conn.row_factory = sqlite3.Row
    
    try:
        result = conn.execute("""
            SELECT j.id, j.customer_id, j.title, j.description, j.status, 
                   j.scheduled_date, j.completed_date, j.created_at, j.updated_at,
                   c.name as customer_name, c.email as customer_email
            FROM jobs j
            LEFT JOIN customers c ON j.customer_id = c.id
            WHERE j.scheduled_date = ?
            ORDER BY j.created_at DESC
        """, (date,))
        
        return [dict(row) for row in result.fetchall()]
    finally:
        conn.close()

def count_jobs(status: str = None) -> int:
    """Count the number of jobs, optionally filtered by status."""
    conn = get_conn()
    conn.row_factory = sqlite3.Row
    
    try:
        query = "SELECT COUNT(*) as count FROM jobs"
        params = []
        
        if status:
            query += " WHERE status = ?"
            params.append(status)
        
        result = conn.execute(query, params)
        return result.fetchone()['count']
    finally:
        conn.close()

def delete_job(job_id: int) -> bool:
    """Delete a job (soft delete by removing from schedule, but keeping records)."""
    conn = get_conn()
    
    try:
        # For now, we'll mark the job as cancelled rather than deleting
        conn.execute("UPDATE jobs SET status = 'cancelled', updated_at = CURRENT_TIMESTAMP WHERE id = ?", (job_id,))
        conn.commit()
        return conn.total_changes > 0
    finally:
        conn.close()

def complete_job(job_id: int) -> bool:
    """Mark a job as completed."""
    conn = get_conn()
    
    try:
        conn.execute("""
            UPDATE jobs 
            SET status = 'completed', completed_date = CURRENT_TIMESTAMP, updated_at = CURRENT_TIMESTAMP 
            WHERE id = ?
        """, (job_id,))
        conn.commit()
        return conn.total_changes > 0
    finally:
        conn.close()

def get_job_summary(job_id: int) -> Optional[Dict[str, Any]]:
    """Get a summary of a job with related information."""
    conn = get_conn()
    conn.row_factory = sqlite3.Row
    
    try:
        # This would join with other tables like materials, time tracking, etc.
        # For now, we'll just return the basic job info
        result = conn.execute("""
            SELECT j.id, j.customer_id, j.title, j.description, j.status, 
                   j.scheduled_date, j.completed_date, j.created_at, j.updated_at,
                   c.name as customer_name, c.email as customer_email
            FROM jobs j
            LEFT JOIN customers c ON j.customer_id = c.id
            WHERE j.id = ?
        """, (job_id,))
        
        return dict(result.fetchone()) if result.fetchone() else None
    finally:
        conn.close()