"""
Database Connection Module - Compatibility Layer

This module provides compatibility for imports like 'from database.connection import get_conn'
by redirecting to the actual database implementation.
"""

from db import get_connection, get_conn, get_db, get_sqlite_conn

# Expose the same functions that are expected by the existing code
get_conn = get_conn
get_connection = get_connection
get_db = get_db