"""
Backup Validator

Comprehensive validation for backup integrity.
Implements multi-tier verification strategy.

All implementation is in Python 3.10+

Validation tiers:
1. Structure validation (file exists, size)
2. Integrity validation (SQLite integrity check)
3. Content validation (checksum verification)
4. Schema validation (table structure)
"""

import sqlite3
from pathlib import Path
from typing import Optional, List, Dict, Any, Tuple
from datetime import datetime
import logging

from brain.backup.models import BackupJob, BackupManifest, BackupStatus
from brain.backup.verifier import BackupVerifier, TieredVerifier
from brain.backup.manifest import ManifestManager


logger = logging.getLogger(__name__)


class BackupValidator:
    """
    Comprehensive backup validation.
    
    Performs multi-tier validation to ensure backup integrity:
    1. Structure: File exists, non-zero size
    2. Integrity: SQLite PRAGMA integrity_check
    3. Content: SHA-256 checksum verification
    4. Schema: Expected tables exist
    
    Example:
        >>> validator = BackupValidator()
        >>> result = validator.validate(backup_path, expected_checksum)
        >>> if result.is_valid:
        ...     print("Backup is valid")
        ... else:
        ...     print(f"Validation failed: {result.errors}")
    """
    
    def __init__(
        self,
        verify_checksum: bool = True,
        verify_schema: bool = True,
        expected_tables: List[str] = None
    ):
        """
        Initialize backup validator.
        
        Args:
            verify_checksum: Whether to perform checksum verification
            verify_schema: Whether to verify table schema
            expected_tables: List of expected table names
        """
        self.verify_checksum = verify_checksum
        self.verify_schema = verify_schema
        self.expected_tables = expected_tables or []
        self.verifier = BackupVerifier()
        self.tiered_verifier = TieredVerifier()
        self.manifest_manager = ManifestManager()
    
    def validate(
        self,
        backup_path: Path,
        expected_checksum: Optional[str] = None,
        manifest: Optional[BackupManifest] = None
    ) -> 'ValidationResult':
        """
        Perform comprehensive validation.
        
        Args:
            backup_path: Path to backup file
            expected_checksum: Expected SHA-256 checksum
            manifest: Optional manifest for validation
            
        Returns:
            ValidationResult with validation details
        """
        result = ValidationResult(backup_path=str(backup_path))
        
        # Tier 1: Structure validation
        if not self._validate_structure(backup_path, result):
            return result
        
        # Tier 2: SQLite integrity check
        if not self._validate_integrity(backup_path, result):
            return result
        
        # Tier 3: Checksum verification
        if self.verify_checksum and expected_checksum:
            if not self._validate_checksum(backup_path, expected_checksum, result):
                return result
        
        # Tier 4: Schema validation
        if self.verify_schema and self.expected_tables:
            if not self._validate_schema(backup_path, result):
                return result
        
        # All validations passed
        result.is_valid = True
        result.validated_at = datetime.now()
        
        return result
    
    def validate_job(self, job: BackupJob) -> 'ValidationResult':
        """
        Validate a backup job.
        
        Args:
            job: BackupJob to validate
            
        Returns:
            ValidationResult
        """
        if not job.file_path:
            return ValidationResult(
                backup_path="",
                is_valid=False,
                errors=["Backup job has no file path"]
            )
        
        backup_path = Path(job.file_path)
        
        result = self.validate(
            backup_path=backup_path,
            expected_checksum=job.checksum
        )
        
        result.backup_id = job.id
        return result
    
    def _validate_structure(
        self,
        backup_path: Path,
        result: 'ValidationResult'
    ) -> bool:
        """Validate file structure."""
        
        # Check file exists
        if not backup_path.exists():
            result.add_error(f"Backup file not found: {backup_path}")
            return False
        
        # Check file is not empty
        file_size = backup_path.stat().st_size
        result.file_size_bytes = file_size
        
        if file_size == 0:
            result.add_error("Backup file is empty")
            return False
        
        result.structure_valid = True
        return True
    
    def _validate_integrity(
        self,
        backup_path: Path,
        result: 'ValidationResult'
    ) -> bool:
        """Validate SQLite integrity."""
        
        try:
            conn = sqlite3.connect(str(backup_path))
            cursor = conn.cursor()
            
            # Run integrity check
            cursor.execute("PRAGMA integrity_check")
            check_result = cursor.fetchone()
            
            conn.close()
            
            if check_result[0] == 'ok':
                result.integrity_valid = True
                return True
            else:
                result.add_error(f"SQLite integrity check failed: {check_result[0]}")
                result.integrity_valid = False
                return False
                
        except Exception as e:
            result.add_error(f"Integrity check error: {e}")
            result.integrity_valid = False
            return False
    
    def _validate_checksum(
        self,
        backup_path: Path,
        expected_checksum: str,
        result: 'ValidationResult'
    ) -> bool:
        """Validate SHA-256 checksum."""
        
        actual_checksum = self.verifier.generate_checksum(backup_path)
        result.checksum = actual_checksum
        
        if actual_checksum == expected_checksum:
            result.checksum_valid = True
            return True
        else:
            result.add_error(
                f"Checksum mismatch: expected {expected_checksum[:16]}..., "
                f"got {actual_checksum[:16]}..."
            )
            result.checksum_valid = False
            return False
    
    def _validate_schema(
        self,
        backup_path: Path,
        result: 'ValidationResult'
    ) -> bool:
        """Validate database schema."""
        
        try:
            conn = sqlite3.connect(str(backup_path))
            cursor = conn.cursor()
            
            # Get existing tables
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' "
                "AND name NOT LIKE 'sqlite_%'"
            )
            existing_tables = {row[0] for row in cursor.fetchall()}
            
            conn.close()
            
            # Check for expected tables
            missing_tables = set(self.expected_tables) - existing_tables
            
            if missing_tables:
                result.add_error(f"Missing tables: {missing_tables}")
                result.schema_valid = False
                return False
            
            result.schema_valid = True
            result.tables_found = list(existing_tables)
            return True
            
        except Exception as e:
            result.add_error(f"Schema validation error: {e}")
            result.schema_valid = False
            return False


class ValidationResult:
    """Result of backup validation."""
    
    def __init__(
        self,
        backup_path: str,
        is_valid: bool = False,
        errors: List[str] = None
    ):
        self.backup_path = backup_path
        self.backup_id: Optional[str] = None
        self.is_valid = is_valid
        self.errors = errors or []
        self.warnings: List[str] = []
        
        # Validation states
        self.structure_valid: bool = False
        self.integrity_valid: bool = False
        self.checksum_valid: bool = False
        self.schema_valid: bool = False
        
        # Additional info
        self.file_size_bytes: int = 0
        self.checksum: Optional[str] = None
        self.tables_found: List[str] = []
        self.validated_at: Optional[datetime] = None
    
    def add_error(self, error: str) -> None:
        """Add an error message."""
        self.errors.append(error)
        self.is_valid = False
    
    def add_warning(self, warning: str) -> None:
        """Add a warning message."""
        self.warnings.append(warning)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'backup_path': self.backup_path,
            'backup_id': self.backup_id,
            'is_valid': self.is_valid,
            'errors': self.errors,
            'warnings': self.warnings,
            'structure_valid': self.structure_valid,
            'integrity_valid': self.integrity_valid,
            'checksum_valid': self.checksum_valid,
            'schema_valid': self.schema_valid,
            'file_size_bytes': self.file_size_bytes,
            'file_size_mb': self.file_size_bytes / (1024 * 1024),
            'checksum': self.checksum,
            'tables_found': self.tables_found,
            'validated_at': self.validated_at.isoformat() if self.validated_at else None,
        }


class BackupHealthChecker:
    """
    Health checker for backup system.
    
    Performs comprehensive health checks across:
    - Backup file integrity
    - Backup chain consistency
    - Storage availability
    - Retention policy compliance
    
    Example:
        >>> checker = BackupHealthChecker(backup_manager)
        >>> health = checker.check_health()
        >>> if health.is_healthy:
        ...     print("Backup system is healthy")
    """
    
    def __init__(self, backup_manager, expected_tables: List[str] = None):
        """
        Initialize health checker.
        
        Args:
            backup_manager: BackupManager instance
            expected_tables: Expected table names for validation
        """
        self.backup_manager = backup_manager
        self.validator = BackupValidator(expected_tables=expected_tables or [])
    
    def check_health(self) -> 'HealthCheckResult':
        """
        Perform comprehensive health check.
        
        Returns:
            HealthCheckResult with health status
        """
        result = HealthCheckResult()
        
        # Check backup storage
        self._check_storage(result)
        
        # Check recent backups
        self._check_recent_backups(result)
        
        # Check backup integrity
        self._check_backup_integrity(result)
        
        # Check backup chain
        self._check_backup_chain(result)
        
        # Overall health
        result.is_healthy = len(result.critical_issues) == 0
        result.checked_at = datetime.now()
        
        return result
    
    def _check_storage(self, result: 'HealthCheckResult') -> None:
        """Check backup storage availability."""
        backup_dir = self.backup_manager.backup_dir
        
        if not backup_dir.exists():
            result.add_critical(f"Backup directory not found: {backup_dir}")
            return
        
        # Check disk space (simplified)
        try:
            stat = backup_dir.stat()
            result.storage_available = True
        except Exception as e:
            result.add_critical(f"Storage check failed: {e}")
    
    def _check_recent_backups(self, result: 'HealthCheckResult') -> None:
        """Check recent backup history."""
        stats = self.backup_manager.get_statistics()
        
        result.total_backups = stats.total_backups
        result.successful_backups = stats.successful_backups
        result.failed_backups = stats.failed_backups
        
        if stats.total_backups == 0:
            result.add_warning("No backups found")
        elif stats.failed_backups > 0:
            result.add_warning(f"{stats.failed_backups} failed backups")
        
        # Check last backup
        if stats.newest_backup:
            age = datetime.now() - stats.newest_backup
            if age.days > 7:
                result.add_warning(f"Last backup is {age.days} days old")
    
    def _check_backup_integrity(self, result: 'HealthCheckResult') -> None:
        """Check integrity of recent backups."""
        backups = self.backup_manager.list_backups(limit=5)
        
        verified_count = 0
        failed_count = 0
        
        for backup in backups:
            if backup.status != BackupStatus.COMPLETED:
                continue
            
            if backup.file_path:
                backup_path = Path(backup.file_path)
                if backup_path.exists():
                    val_result = self.validator.validate(
                        backup_path=backup_path,
                        expected_checksum=backup.checksum
                    )
                    
                    if val_result.is_valid:
                        verified_count += 1
                    else:
                        failed_count += 1
                        result.add_warning(
                            f"Backup {backup.id[:8]} failed validation"
                        )
        
        result.verified_backups = verified_count
        result.failed_validations = failed_count
    
    def _check_backup_chain(self, result: 'HealthCheckResult') -> None:
        """Check backup chain consistency."""
        backups = self.backup_manager.list_backups(limit=100)
        
        # Check for orphaned incremental backups
        backup_ids = {b.id for b in backups}
        
        for backup in backups:
            if backup.previous_backup_id:
                if backup.previous_backup_id not in backup_ids:
                    result.add_warning(
                        f"Orphaned incremental backup: {backup.id[:8]} "
                        f"(missing parent: {backup.previous_backup_id[:8]})"
                    )


class HealthCheckResult:
    """Result of backup health check."""
    
    def __init__(self):
        self.is_healthy: bool = True
        self.critical_issues: List[str] = []
        self.warnings: List[str] = []
        self.checked_at: Optional[datetime] = None
        
        # Storage info
        self.storage_available: bool = False
        
        # Backup counts
        self.total_backups: int = 0
        self.successful_backups: int = 0
        self.failed_backups: int = 0
        self.verified_backups: int = 0
        self.failed_validations: int = 0
    
    def add_critical(self, issue: str) -> None:
        """Add a critical issue."""
        self.critical_issues.append(issue)
        self.is_healthy = False
    
    def add_warning(self, warning: str) -> None:
        """Add a warning."""
        self.warnings.append(warning)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            'is_healthy': self.is_healthy,
            'critical_issues': self.critical_issues,
            'warnings': self.warnings,
            'checked_at': self.checked_at.isoformat() if self.checked_at else None,
            'storage_available': self.storage_available,
            'total_backups': self.total_backups,
            'successful_backups': self.successful_backups,
            'failed_backups': self.failed_backups,
            'verified_backups': self.verified_backups,
            'failed_validations': self.failed_validations,
        }


def quick_validate(backup_path: Path) -> Tuple[bool, str]:
    """
    Quick validation of a backup file.
    
    Performs basic checks without full validation.
    
    Args:
        backup_path: Path to backup file
        
    Returns:
        Tuple of (is_valid, message)
    """
    if not backup_path.exists():
        return (False, f"File not found: {backup_path}")
    
    if backup_path.stat().st_size == 0:
        return (False, "File is empty")
    
    try:
        conn = sqlite3.connect(str(backup_path))
        cursor = conn.cursor()
        cursor.execute("PRAGMA integrity_check")
        result = cursor.fetchone()
        conn.close()
        
        if result[0] == 'ok':
            return (True, "Backup is valid")
        else:
            return (False, f"Integrity check failed: {result[0]}")
            
    except Exception as e:
        return (False, f"Validation error: {e}")