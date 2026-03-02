"""
Helper functions for the Data Lifecycle page.

Contains lifecycle management utilities.
"""

from pathlib import Path
from typing import Optional

from .constants import DEFAULT_DB_NAME, DEFAULT_USER_ID


def get_lifecycle_manager():
    """
    Get or create the lifecycle manager instance.
    
    Returns:
        LifecycleManager instance or None if brain module not available
    """
    try:
        from brain.lifecycle import LifecycleManager
        
        db_path = Path(__file__).parent.parent.parent / DEFAULT_DB_NAME
        return LifecycleManager(db_path=str(db_path))
    except ImportError:
        return None


def get_gdpr_compliance():
    """
    Get or create the GDPR compliance instance.
    
    Returns:
        GDPRCompliance instance or None if brain module not available
    """
    try:
        from brain.lifecycle import GDPRCompliance
        
        db_path = Path(__file__).parent.parent.parent / DEFAULT_DB_NAME
        return GDPRCompliance(db_path=str(db_path))
    except ImportError:
        return None


def format_duration(days: int) -> str:
    """
    Format days into human readable duration.
    
    Args:
        days: Number of days
        
    Returns:
        Human readable duration string
    """
    if days >= 365:
        years = days // 365
        return f"{years} year{'s' if years > 1 else ''}"
    elif days >= 30:
        months = days // 30
        return f"{months} month{'s' if months > 1 else ''}"
    else:
        return f"{days} days"


def apply_retention_policies(manager):
    """
    Apply retention policies.
    
    Args:
        manager: LifecycleManager instance
        
    Returns:
        Result object or None on error
    """
    try:
        return manager.apply_retention_policies()
    except Exception:
        return None


def recover_entity(manager, entity_type: str, entity_id: str):
    """
    Recover a deleted entity.
    
    Args:
        manager: LifecycleManager instance
        entity_type: Type of entity
        entity_id: Entity ID
        
    Returns:
        Result object or None on error
    """
    try:
        return manager.recover_entity(entity_type, entity_id)
    except Exception:
        return None


def export_user_data(gdpr, user_id: str = DEFAULT_USER_ID):
    """
    Export user data for GDPR compliance.
    
    Args:
        gdpr: GDPRCompliance instance
        user_id: User ID
        
    Returns:
        User data dictionary or None on error
    """
    try:
        return gdpr.export_user_data(user_id)
    except Exception:
        return None


def export_portable_data(gdpr, user_id: str = DEFAULT_USER_ID):
    """
    Export portable data for GDPR compliance.
    
    Args:
        gdpr: GDPRCompliance instance
        user_id: User ID
        
    Returns:
        Export path or None on error
    """
    try:
        return gdpr.export_portable_data(user_id)
    except Exception:
        return None


def request_erasure(gdpr, user_id: str = DEFAULT_USER_ID):
    """
    Request data erasure for GDPR compliance.
    
    Args:
        gdpr: GDPRCompliance instance
        user_id: User ID
        
    Returns:
        Erasure request or None on error
    """
    try:
        return gdpr.request_erasure(user_id)
    except Exception:
        return None