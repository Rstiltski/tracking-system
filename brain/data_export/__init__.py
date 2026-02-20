"""
Data Export Module

Comprehensive data export functionality with:
- Multiple output formats (JSON, CSV, SQLite)
- Module-based export selection
- Secure download tokens
- Export history tracking

All implementation is in Python 3.10+

Example:
    >>> from brain.data_export import DataExporter
    >>> 
    >>> exporter = DataExporter(db_path='tracking.db')
    >>> 
    >>> # Export all data to JSON
    >>> request = exporter.create_export(format='json')
    >>> 
    >>> # Export specific modules
    >>> request = exporter.create_export(
    ...     format='csv',
    ...     modules=['habits', 'tasks']
    ... )
"""

# Core models
from brain.data_export.models import (
    ExportRequest,
    ExportFormat,
    ExportStatus,
    ExportHistory,
    ExportResult,
    EXPORT_MODULES,
)

# Core functionality
from brain.data_export.exporter import DataExporter
from brain.data_export.serializers import (
    JSONSerializer,
    CSVSerializer,
    SQLiteSerializer,
)
from brain.data_export.download import DownloadManager
from brain.data_export.history import ExportHistoryManager


__all__ = [
    # Models
    'ExportRequest',
    'ExportFormat',
    'ExportStatus',
    'ExportHistory',
    
    # Core
    'DataExporter',
    'JSONSerializer',
    'CSVSerializer',
    'SQLiteSerializer',
    'DownloadManager',
    'ExportHistoryManager',
]


# Version info
__version__ = '1.0.0'
__author__ = 'Tracking System'