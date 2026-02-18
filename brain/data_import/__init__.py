"""
Data Import Module

Python-based data import functionality for the tracking system.
Handles JSON, CSV, and SQLite import with validation and conflict resolution.

Module Structure:
- importer.py: Main DataImporter class
- parsers.py: JSON and CSV parsers using Python stdlib
- validator.py: Data validation engine
- conflict_resolver.py: Conflict detection and resolution
- preview.py: Import preview functionality
- models.py: Data models (ImportRequest, ImportStatus, etc.)

Usage:
    from brain.data_import import DataImporter
    
    importer = DataImporter(db_connection)
    result = importer.import_file('backup.json', user_id='user-123')
"""

from brain.data_import.importer import DataImporter
from brain.data_import.models import (
    ImportRequest,
    ImportStatus,
    ConflictStrategy,
    ImportPreview,
)

__all__ = [
    'DataImporter',
    'ImportRequest',
    'ImportStatus',
    'ConflictStrategy',
    'ImportPreview',
]
