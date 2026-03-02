"""
Constants for the Backup & Restore page.

Contains backup-related configuration values.
"""

from typing import List

# Default user ID for backups
DEFAULT_USER_ID = "default"

# Retention policy defaults
DEFAULT_DAILY_BACKUPS = 7
DEFAULT_WEEKLY_BACKUPS = 4
DEFAULT_MONTHLY_BACKUPS = 12

# Retention limits
MIN_DAILY_BACKUPS = 1
MAX_DAILY_BACKUPS = 30
MIN_WEEKLY_BACKUPS = 1
MAX_WEEKLY_BACKUPS = 12
MIN_MONTHLY_BACKUPS = 1
MAX_MONTHLY_BACKUPS = 24

# Size units for formatting
SIZE_UNITS = ['B', 'KB', 'MB', 'GB', 'TB']

# Default paths (relative to project root)
DEFAULT_DB_NAME = "tracking.db"
DEFAULT_BACKUP_DIR = "backups"