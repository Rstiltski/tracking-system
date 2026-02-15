"""
Db - Database Facade

This is the main database facade that follows the architecture rules.
It acts as a switchboard for the database layer, delegating to specific query modules
without running SQL directly.

📚 REQUIRED READING BEFORE MODIFICATION:
- ARCHITECTURE_RULES.md (Facade Pattern)
- MASTER_RULES.md
"""
from __future__ import annotations

import warnings
warnings.warn(
    "db.py is deprecated. Use database.queries.* modules instead.",
    DeprecationWarning,
    stacklevel=2
)

# Conditional streamlit import for test compatibility
try:
    import streamlit as st
    HAS_STREAMLIT = True
except ImportError:
    HAS_STREAMLIT = False
    st = None

from database.connection import (
    get_conn,
    init_connection_pool,
    override_connection,
    should_commit,
    DB_PATH,
)

# Export connection utilities
get_conn = get_conn
get_sqlite_conn = lambda: get_conn()  # Simple alias
DB_PATH = DB_PATH

# Initialize connection pool
init_connection_pool()

def init_db() -> None:
    """Initialize the database with required tables and default data."""
    from database import init_db as init_db_impl
    init_db_impl()

# Dynamic dispatcher to query modules
def __getattr__(name: str):
    """
    Dynamic attribute access to delegate to appropriate query modules.
    
    This follows the facade pattern where db.py doesn't run SQL directly
    but delegates to specific modules in database.queries.*
    """
    # Map common function names to their appropriate modules
    function_mapping = {
        # Customer functions
        'get_customer': 'database.queries.customers',
        'create_customer': 'database.queries.customers',
        'update_customer': 'database.queries.customers',
        'list_customers': 'database.queries.customers',
        
        # Job functions
        'get_job': 'database.queries.jobs_core',
        'create_job': 'database.queries.jobs_core',
        'update_job': 'database.queries.jobs_core',
        'list_jobs': 'database.queries.jobs_core',
        
        # User functions
        'get_user': 'database.queries.users',
        'create_user': 'database.queries.users',
        'update_user': 'database.queries.users',
        'authenticate_user': 'database.queries.users',
        'count_users': 'database.queries.users',
        
        # Settings functions
        'get_setting': 'database.queries.misc',
        'update_setting': 'database.queries.misc',
        'get_system_stats': 'database.queries.misc',
        
        # Audit functions
        'log_audit_event': 'database.queries.audit',
        'get_audit_trail': 'database.queries.audit',
    }
    
    if name in function_mapping:
        module_name = function_mapping[name]
        try:
            module = __import__(module_name, fromlist=[name])
            func = getattr(module, name)
            return func
        except (ImportError, AttributeError):
            # If the function doesn't exist in the mapped module, raise AttributeError
            raise AttributeError(f"Function '{name}' not found in facade")
    
    # For any other attribute access, raise AttributeError
    raise AttributeError(f"module 'db' has no attribute '{name}'")

# Export common functions that are safe to expose at the facade level
__all__ = [
    'get_conn',
    'get_sqlite_conn',
    'DB_PATH',
    'init_db',
    # These will be dynamically dispatched via __getattr__
    'get_customer', 'create_customer', 'update_customer', 'list_customers',
    'get_job', 'create_job', 'update_job', 'list_jobs',
    'get_user', 'create_user', 'update_user', 'authenticate_user', 'count_users',
    'get_setting', 'update_setting', 'get_system_stats',
    'log_audit_event', 'get_audit_trail'
]