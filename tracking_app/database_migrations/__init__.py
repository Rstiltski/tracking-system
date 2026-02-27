"""
Database Migrations - Schema Evolution

This package contains database migrations for evolving the schema
over time while preserving data.

Usage:
    # Run all pending migrations
    python3 -m tracking_app.database_migrations
    
    # Run specific migration
    python3 -m tracking_app.database_migrations.burnout_migration
    
    # Rollback specific migration
    python3 -m tracking_app.database_migrations.burnout_migration rollback
"""
