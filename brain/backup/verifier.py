"""
Backup Verifier

SHA-256 checksum verification for backup integrity.
Uses chunked reading for constant memory footprint (64KB buffer).

All implementation is in Python 3.10+

This module enforces the integrity guarantee of the backup system
by providing cryptographic verification of backup files.
"""

import hashlib
from pathlib import Path
from typing import Optional, Tuple
import logging


logger = logging.getLogger(__name__)


class BackupVerifier:
    """
    Verifies backup integrity using SHA-256 checksums.
    
    Uses chunked reading (64KB buffer) to maintain constant
    memory footprint regardless of file size.
    
    This is critical for handling large backup files without
    causing memory exhaustion.
    
    Example:
        >>> verifier = BackupVerifier()
        >>> checksum = verifier.generate_checksum(Path('backup.db'))
        >>> len(checksum)
        64  # SHA-256 produces 64 hex characters
        >>> verifier.verify(Path('backup.db'), checksum)
        True
    
    Memory Complexity:
        O(1) - Constant 64KB buffer regardless of file size
    """
    
    # 64KB buffer for chunked reading
    # This provides optimal balance between I/O efficiency and memory usage
    BUFFER_SIZE = 65536
    
    def generate_checksum(self, file_path: Path) -> str:
        """
        Generate SHA-256 checksum for a file.
        
        Uses chunked reading to maintain constant memory footprint.
        This is essential for large backup files.
        
        Args:
            file_path: Path to the file to hash
            
        Returns:
            Hexadecimal SHA-256 checksum string (64 characters)
            
        Raises:
            FileNotFoundError: If file does not exist
            PermissionError: If file cannot be read
            IOError: If file read fails
            
        Example:
            >>> verifier = BackupVerifier()
            >>> checksum = verifier.generate_checksum(Path('tracking.db'))
            >>> len(checksum)
            64
        """
        sha256 = hashlib.sha256()
        
        with open(file_path, 'rb') as f:
            while chunk := f.read(self.BUFFER_SIZE):
                sha256.update(chunk)
        
        checksum = sha256.hexdigest()
        logger.debug(f"Generated checksum for {file_path}: {checksum[:16]}...")
        
        return checksum
    
    def verify(self, file_path: Path, expected_checksum: str) -> bool:
        """
        Verify file against expected checksum.
        
        Args:
            file_path: Path to the file to verify
            expected_checksum: Expected SHA-256 checksum (64 hex chars)
            
        Returns:
            True if checksums match, False otherwise
            
        Example:
            >>> verifier = BackupVerifier()
            >>> verifier.verify(Path('backup.db'), 'abc123...')
            True
        """
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return False
        
        if len(expected_checksum) != 64:
            logger.error(f"Invalid checksum length: {len(expected_checksum)} (expected 64)")
            return False
        
        actual_checksum = self.generate_checksum(file_path)
        
        if actual_checksum == expected_checksum:
            logger.info(f"Checksum verified for {file_path}")
            return True
        else:
            logger.error(
                f"Checksum mismatch for {file_path}: "
                f"expected {expected_checksum[:16]}..., "
                f"got {actual_checksum[:16]}..."
            )
            return False
    
    def verify_manifest(
        self,
        backup_path: Path,
        manifest_checksum: str
    ) -> bool:
        """
        Verify backup against manifest checksum.
        
        Convenience method for verifying backups using stored
        checksums from manifest files.
        
        Args:
            backup_path: Path to backup file
            manifest_checksum: Checksum from manifest file
            
        Returns:
            True if verified, False otherwise
        """
        return self.verify(backup_path, manifest_checksum)
    
    def quick_verify(self, file_path: Path) -> Optional[str]:
        """
        Quick verification - returns checksum or None if file unreadable.
        
        Non-throwing version of generate_checksum for use in
        validation pipelines where failures should be handled gracefully.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Checksum string or None on error
        """
        try:
            return self.generate_checksum(file_path)
        except Exception as e:
            logger.error(f"Quick verify failed for {file_path}: {e}")
            return None
    
    def compare_files(
        self,
        file1_path: Path,
        file2_path: Path
    ) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Compare two files by checksum.
        
        Useful for verifying backup copies match originals.
        
        Args:
            file1_path: Path to first file
            file2_path: Path to second file
            
        Returns:
            Tuple of (match, checksum1, checksum2)
            - match: True if files are identical
            - checksum1: Checksum of first file (or None on error)
            - checksum2: Checksum of second file (or None on error)
        """
        checksum1 = self.quick_verify(file1_path)
        checksum2 = self.quick_verify(file2_path)
        
        if checksum1 is None or checksum2 is None:
            return (False, checksum1, checksum2)
        
        return (checksum1 == checksum2, checksum1, checksum2)
    
    def verify_size_match(
        self,
        file_path: Path,
        expected_size: int
    ) -> bool:
        """
        Quick size check before computing checksum.
        
        Tier 1 verification: If sizes don't match, contents can't match.
        This avoids expensive checksum computation for obvious mismatches.
        
        Args:
            file_path: Path to file
            expected_size: Expected file size in bytes
            
        Returns:
            True if sizes match, False otherwise
        """
        if not file_path.exists():
            logger.error(f"File not found: {file_path}")
            return False
        
        actual_size = file_path.stat().st_size
        
        if actual_size == expected_size:
            return True
        else:
            logger.debug(
                f"Size mismatch for {file_path}: "
                f"expected {expected_size}, got {actual_size}"
            )
            return False


class TieredVerifier:
    """
    Three-tier verification strategy for optimal performance.
    
    Implements the tiered verification approach from research:
    - Tier 1: Size check (instant)
    - Tier 2: Modification time check (instant)
    - Tier 3: Full SHA-256 checksum (expensive)
    
    This minimizes I/O while ensuring integrity.
    
    Example:
        >>> verifier = TieredVerifier()
        >>> result = verifier.verify_tiered(
        ...     Path('backup.db'),
        ...     expected_size=1024,
        ...     expected_mtime=datetime.now(),
        ...     expected_checksum='abc...'
        ... )
    """
    
    def __init__(self, use_mtime: bool = True):
        """
        Initialize tiered verifier.
        
        Args:
            use_mtime: Whether to use mtime as Tier 2 check
        """
        self.use_mtime = use_mtime
        self.hash_verifier = BackupVerifier()
    
    def verify_tiered(
        self,
        file_path: Path,
        expected_size: Optional[int] = None,
        expected_mtime: Optional[float] = None,
        expected_checksum: Optional[str] = None
    ) -> Tuple[bool, str]:
        """
        Perform tiered verification.
        
        Progresses through tiers until verification is conclusive
        or all tiers are exhausted.
        
        Args:
            file_path: Path to file to verify
            expected_size: Expected file size (Tier 1)
            expected_mtime: Expected modification time (Tier 2)
            expected_checksum: Expected SHA-256 checksum (Tier 3)
            
        Returns:
            Tuple of (verified, tier_used)
            - verified: True if file passes verification
            - tier_used: Which tier provided the result
        """
        if not file_path.exists():
            return (False, "not_found")
        
        # Tier 1: Size check
        if expected_size is not None:
            actual_size = file_path.stat().st_size
            if actual_size != expected_size:
                return (False, "tier1_size")
        
        # Tier 2: Modification time check
        if self.use_mtime and expected_mtime is not None:
            actual_mtime = file_path.stat().st_mtime
            if actual_mtime != expected_mtime:
                # mtime differs, need full check
                pass
            else:
                # mtime matches, file likely unchanged
                return (True, "tier2_mtime")
        
        # Tier 3: Full checksum
        if expected_checksum is not None:
            actual_checksum = self.hash_verifier.generate_checksum(file_path)
            if actual_checksum == expected_checksum:
                return (True, "tier3_checksum")
            else:
                return (False, "tier3_checksum")
        
        # No verification criteria provided
        return (True, "no_criteria")