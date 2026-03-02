"""
Helper functions for the Backup & Restore page.

Contains backup management utilities.
"""

from pathlib import Path

from .constants import SIZE_UNITS, DEFAULT_USER_ID, DEFAULT_DB_NAME, DEFAULT_BACKUP_DIR


def format_size(size_bytes: float) -> str:
    """
    Format file size in human readable format.
    
    Args:
        size_bytes: Size in bytes
        
    Returns:
        Formatted size string (e.g., "1.5 MB")
    """
    for unit in SIZE_UNITS:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"


def get_backup_manager():
    """
    Get or create the backup manager instance.
    
    Returns:
        BackupManager instance or None if brain module not available
    """
    try:
        from brain.backup import BackupManager
        
        # Get paths
        db_path = get_db_path()
        backup_dir = get_backup_dir()
        
        return BackupManager(str(db_path), str(backup_dir))
    except ImportError:
        return None


def get_db_path() -> Path:
    """Get the database path."""
    return Path(__file__).parent.parent.parent / DEFAULT_DB_NAME


def get_backup_dir() -> Path:
    """Get the backup directory path."""
    return Path(__file__).parent.parent.parent / DEFAULT_BACKUP_DIR


def get_restore_engine():
    """
    Get a restore engine instance.
    
    Returns:
        RestoreEngine instance or None if brain module not available
    """
    try:
        from brain.backup import RestoreEngine
        return RestoreEngine(verify_checksum=True, create_safety_backup=True)
    except ImportError:
        return None


def get_retention_policy(daily: int, weekly: int, monthly: int):
    """
    Get a retention policy instance.
    
    Args:
        daily: Number of daily backups to keep
        weekly: Number of weekly backups to keep
        monthly: Number of monthly backups to keep
        
    Returns:
        RetentionPolicy instance or None if brain module not available
    """
    try:
        from brain.backup import RetentionPolicy
        return RetentionPolicy(daily=daily, weekly=weekly, monthly=monthly)
    except ImportError:
        return None