"""
Database Queries Module - Compatibility Layer

This module provides compatibility for imports like 'from database.queries import invoices'
by redirecting to the actual database implementation.
"""

# Placeholder for invoices query module
# This would normally contain specific query functions for invoices
from tracking_app.database import get_db, Database

def get_invoices():
    """Placeholder function for getting invoices"""
    with get_db() as conn:
        cursor = conn.execute("SELECT * FROM invoices")
        return cursor.fetchall()

def get_invoice_by_id(invoice_id):
    """Placeholder function for getting an invoice by ID"""
    with get_db() as conn:
        cursor = conn.execute("SELECT * FROM invoices WHERE id = ?", (invoice_id,))
        return cursor.fetchone()