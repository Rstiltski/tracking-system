"""
Backup System Module

Comprehensive backup and restore system with:
- SHA-256 checksum verification
- Hard-link deduplication
- GFS retention policy
- Automated scheduling
- Safe restoration

All implementation is in Python 3.10+

Example:
    >>> from brain.backup import BackupManager, BackupType
    >>> 
    >>> # Create a backup
    >>> manager = BackupManager(db_path='tracking.db')
    >>> job = manager.create_backup(user_id='user-123')
    >>> 
    >>> # Verify backup
    >>> if manager.verify_backup(job.id):
    ...     print("Backup verified successfully")
    
Architecture:
    The backup system follows a modular design:
    
    - models.py: Data classes for backup jobs, schedules, manifests
    - manager.py: Main orchestrator for backup operations
    - verifier.py: SHA-256 checksum verification
    - manifest.py: JSON manifest handling
    - dedup.py: Hard-link deduplication engine
    - dedup_db.py: Deduplication tracking database
    - scheduler.py: APScheduler integration for automation
    - retention.py: GFS retention policy engine
    - restore.py: Safe database restoration
    - validator.py: Multi-tier backup validation
"""

# Core models
from brain.backup.models import (
    BackupJob,
    BackupSchedule,
    BackupManifest,
    BackupStatistics,
    BackupType,
    BackupStatus,
    BackupFrequency,
    RestoreResult,
    DedupRecord,
)

# Core functionality
from brain.backup.manager import BackupManager
from brain.backup.verifier import BackupVerifier, TieredVerifier
from brain.backup.manifest import ManifestManager, ManifestCache

# Deduplication
from brain.backup.dedup import (
    DeduplicationEngine,
    NoOpDedupEngine,
    DedupResult,
    BackupDedupResult,
    supports_hard_links,
)
from brain.backup.dedup_db import DedupDatabase, DedupDatabaseManager

# Automation
from brain.backup.scheduler import (
    BackupScheduler,
    ScheduleBuilder,
)
from brain.backup.retention import (
    RetentionPolicy,
    RetentionManager,
    ArchivePolicy,
    calculate_storage_savings,
)

# Restoration and validation
from brain.backup.restore import (
    RestoreEngine,
    RestorePlanner,
    RestorePlan,
    RestoreStep,
    preview_restore,
)
from brain.backup.validator import (
    BackupValidator,
    ValidationResult,
    BackupHealthChecker,
    HealthCheckResult,
    quick_validate,
)


__all__ = [
    # Models
    'BackupJob',
    'BackupSchedule',
    'BackupManifest',
    'BackupStatistics',
    'BackupType',
    'BackupStatus',
    'BackupFrequency',
    'RestoreResult',
    'DedupRecord',
    
    # Core
    'BackupManager',
    'BackupVerifier',
    'TieredVerifier',
    'ManifestManager',
    'ManifestCache',
    
    # Deduplication
    'DeduplicationEngine',
    'NoOpDedupEngine',
    'DedupResult',
    'BackupDedupResult',
    'DedupDatabase',
    'DedupDatabaseManager',
    'supports_hard_links',
    
    # Automation
    'BackupScheduler',
    'ScheduleBuilder',
    'RetentionPolicy',
    'RetentionManager',
    'ArchivePolicy',
    'calculate_storage_savings',
    
    # Restoration
    'RestoreEngine',
    'RestorePlanner',
    'RestorePlan',
    'RestoreStep',
    'preview_restore',
    
    # Validation
    'BackupValidator',
    'ValidationResult',
    'BackupHealthChecker',
    'HealthCheckResult',
    'quick_validate',
]


# Version info
__version__ = '1.0.0'
__author__ = 'Tracking System'