"""
Constants for the Data Import page.

Contains import-related configuration values.
"""

from typing import List

# Default user ID for imports
DEFAULT_USER_ID = "default"

# Supported file types
SUPPORTED_FILE_TYPES: List[str] = ["json", "csv", "zip"]

# Available import modules
AVAILABLE_MODULES: List[str] = [
    "habits",
    "tasks",
    "goals",
    "transactions",
    "health_entries",
    "time_entries",
    "achievements"
]

# Default settings
DEFAULT_DRY_RUN = True
DEFAULT_SELECTED_MODULES = AVAILABLE_MODULES.copy()

# Conflict resolution help text
CONFLICT_HELP = "How to handle records that already exist"

# Conflict strategy descriptions
CONFLICT_STRATEGY_DESCRIPTIONS = {
    "skip": "Keep existing records, skip duplicates (safest)",
    "overwrite": "Replace existing records with imported data",
    "merge": "Combine fields from both records",
    "duplicate": "Keep both records with new IDs"
}