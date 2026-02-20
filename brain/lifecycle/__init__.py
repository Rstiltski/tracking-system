"""
Data Lifecycle Management Module

Comprehensive data lifecycle management with:
- Per-entity retention policies
- Soft delete with recovery window
- GDPR compliance (Right to Access, Erasure, Portability)
- Automated lifecycle scheduling

All implementation is in Python 3.10+

Example:
    >>> from brain.lifecycle import LifecycleManager
    >>> 
    >>> manager = LifecycleManager(db_path='tracking.db')
    >>> 
    >>> # Apply retention policies
    >>> result = manager.apply_retention_policies()
    >>> 
    >>> # Archive a record
    >>> deleted = manager.archive_entity('task', 'task-123')
    >>> 
    >>> # Recover within 30-day window
    >>> manager.recover_entity('task', 'task-123')
"""

# Core models
from brain.lifecycle.models import (
    RetentionPolicy,
    DeletedRecord,
    DataReset,
    ErasureRequest,
    LifecycleJob,
    LifecycleResult,
    RetentionAction,
    PurgeStatus,
    ResetType,
    ErasureStatus,
)

# Core functionality
from brain.lifecycle.manager import LifecycleManager
from brain.lifecycle.retention import RetentionEngine
from brain.lifecycle.archive import ArchiveManager
from brain.lifecycle.purge import PurgeManager
from brain.lifecycle.recovery import RecoveryManager
from brain.lifecycle.gdpr import GDPRCompliance
from brain.lifecycle.scheduler import LifecycleScheduler


__all__ = [
    # Models
    'RetentionPolicy',
    'DeletedRecord',
    'DataReset',
    'ErasureRequest',
    'LifecycleJob',
    'LifecycleResult',
    'RetentionAction',
    'PurgeStatus',
    'ResetType',
    'ErasureStatus',
    
    # Core
    'LifecycleManager',
    'RetentionEngine',
    'ArchiveManager',
    'PurgeManager',
    'RecoveryManager',
    'GDPRCompliance',
    'LifecycleScheduler',
]


# Version info
__version__ = '1.0.0'
__author__ = 'Tracking System'