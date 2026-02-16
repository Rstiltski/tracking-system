"""
Invoices Queries Module

This module provides query functions for invoices.
"""

from tracking_app.database import get_db, Database

def get_invoices():
    """Function for getting invoices"""
    with get_db() as conn:
        cursor = conn.execute("SELECT * FROM invoices")
        return cursor.fetchall()

def get_invoice_by_id(invoice_id):
    """Function for getting an invoice by ID"""
    with get_db() as conn:
        cursor = conn.execute("SELECT * FROM invoices WHERE id = ?", (invoice_id,))
        return cursor.fetchone()