"""
Constants for the Data Export page.

Contains export-related configuration values.
"""

from typing import Dict

# Default user ID for exports
DEFAULT_USER_ID = "default"

# Export format options
FORMAT_OPTIONS: Dict[str, str] = {
    'JSON': 'json',
    'CSV': 'csv',
    'SQLite': 'sqlite'
}

# Default export settings
DEFAULT_INCLUDE_ARCHIVED = False
DEFAULT_COMPRESSION = True
DEFAULT_SELECT_ALL = True

# Module preview limit
MODULE_PREVIEW_LIMIT = 5

# Default paths (relative to project root)
DEFAULT_DB_NAME = "tracking.db"
DEFAULT_EXPORT_DIR = "exports"