"""
Constants for the Data Lifecycle page.

Contains lifecycle-related configuration values.
"""

from typing import List

# Default user ID
DEFAULT_USER_ID = "default"

# Default database name
DEFAULT_DB_NAME = "tracking.db"

# Reset type options
RESET_TYPES: List[str] = [
    "Module Reset (specific modules)",
    "Archive Reset (clear archived data)",
    "Full Reset (all data)"
]

# Modules available for reset
RESET_MODULES: List[str] = [
    'habits',
    'tasks',
    'goals',
    'finances',
    'health',
    'time'
]

# Default reset settings
DEFAULT_CREATE_BACKUP = True
DEFAULT_RESET_MODULES = ['habits']

# Erasure grace period (days)
ERASURE_GRACE_PERIOD_DAYS = 30

# Recovery window display limit
RECOVERY_DISPLAY_LIMIT = 10