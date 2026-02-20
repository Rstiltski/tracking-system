"""
Manifest Manager

Handles backup manifest (JSON) creation and loading.
Manifests store metadata and checksums for integrity verification.

All implementation is in Python 3.10+

The manifest file sits alongside each backup and contains:
- Backup ID and timestamps
- SHA-256 checksum of the database
- Record counts per table
- Chain information for incremental backups
"""

import json
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime
import logging

from brain.backup.models import BackupManifest, BackupType


logger = logging.getLogger(__name__)


class ManifestManager:
    """
    Manages backup manifest files.
    
    Manifests are JSON files stored alongside backups with
    the .manifest.json extension. They provide:
    
    1. Integrity verification via checksums
    2. Quick metadata lookup without parsing backups
    3. Chain validation for incremental backups
    4. Historical tracking of backup contents
    
    Example:
        >>> manager = ManifestManager()
        >>> manifest = BackupManifest(
        ...     backup_id="backup-123",
        ...     database_checksum="abc123...",
        ...     record_count=1000
        ... )
        >>> manager.save(manifest, Path('backup.db.manifest.json'))
        >>> loaded = manager.load(Path('backup.db.manifest.json'))
        >>> loaded.database_checksum
        'abc123...'
    """
    
    # Manifest file extension
    MANIFEST_SUFFIX = '.manifest.json'
    
    def save(self, manifest: BackupManifest, path: Path) -> None:
        """
        Save manifest to JSON file.
        
        Creates parent directories if needed.
        
        Args:
            manifest: BackupManifest to save
            path: Path to save manifest file
            
        Raises:
            OSError: If file cannot be written
        """
        # Ensure parent directory exists
        path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(path, 'w', encoding='utf-8') as f:
            f.write(manifest.to_json())
        
        logger.info(f"Saved manifest to {path}")
    
    def load(self, path: Path) -> Optional[BackupManifest]:
        """
        Load manifest from JSON file.
        
        Args:
            path: Path to manifest file
            
        Returns:
            BackupManifest or None if file doesn't exist or is invalid
        """
        if not path.exists():
            logger.warning(f"Manifest not found: {path}")
            return None
        
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            manifest = BackupManifest.from_json(content)
            logger.debug(f"Loaded manifest from {path}")
            return manifest
            
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in manifest {path}: {e}")
            return None
        except Exception as e:
            logger.error(f"Failed to load manifest {path}: {e}")
            return None
    
    def exists(self, backup_path: Path) -> bool:
        """
        Check if manifest exists for a backup.
        
        Args:
            backup_path: Path to backup file
            
        Returns:
            True if manifest file exists
        """
        manifest_path = self.get_manifest_path(backup_path)
        return manifest_path.exists()
    
    def get_manifest_path(self, backup_path: Path) -> Path:
        """
        Get the manifest path for a backup file.
        
        Args:
            backup_path: Path to backup file (e.g., backup.db)
            
        Returns:
            Path to manifest file (e.g., backup.db.manifest.json)
        """
        # Remove any existing suffix and add manifest suffix
        return backup_path.with_suffix(self.MANIFEST_SUFFIX)
    
    def delete(self, backup_path: Path) -> bool:
        """
        Delete manifest file for a backup.
        
        Args:
            backup_path: Path to backup file
            
        Returns:
            True if manifest was deleted, False if not found
        """
        manifest_path = self.get_manifest_path(backup_path)
        
        if manifest_path.exists():
            manifest_path.unlink()
            logger.info(f"Deleted manifest: {manifest_path}")
            return True
        
        return False
    
    def create_manifest(
        self,
        backup_id: str,
        backup_type: BackupType,
        db_path: Path,
        checksum: str,
        previous_backup_id: Optional[str] = None
    ) -> BackupManifest:
        """
        Create a new manifest for a backup.
        
        Convenience method that gathers all required information
        and creates a properly populated manifest.
        
        Args:
            backup_id: Unique backup identifier
            backup_type: FULL or INCREMENTAL
            db_path: Path to the database file
            checksum: SHA-256 checksum of the backup
            previous_backup_id: For incremental chains
            
        Returns:
            Populated BackupManifest
        """
        # Get file size
        file_size = db_path.stat().st_size if db_path.exists() else 0
        
        # Get table counts
        tables = self._get_table_counts(db_path)
        
        # Calculate total records
        record_count = sum(tables.values())
        
        manifest = BackupManifest(
            backup_id=backup_id,
            created_at=datetime.now(),
            backup_type=backup_type,
            database_checksum=checksum,
            file_size_bytes=file_size,
            record_count=record_count,
            tables=tables,
            previous_backup_id=previous_backup_id,
        )
        
        return manifest
    
    def _get_table_counts(self, db_path: Path) -> Dict[str, int]:
        """
        Get record counts per table from SQLite database.
        
        Args:
            db_path: Path to SQLite database
            
        Returns:
            Dictionary mapping table names to row counts
        """
        if not db_path.exists():
            return {}
        
        try:
            import sqlite3
            
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            
            # Get all tables
            cursor.execute(
                "SELECT name FROM sqlite_master WHERE type='table' "
                "AND name NOT LIKE 'sqlite_%'"
            )
            tables = [row[0] for row in cursor.fetchall()]
            
            counts = {}
            for table in tables:
                try:
                    cursor.execute(f"SELECT COUNT(*) FROM {table}")
                    counts[table] = cursor.fetchone()[0]
                except Exception:
                    counts[table] = 0
            
            conn.close()
            return counts
            
        except Exception as e:
            logger.error(f"Failed to get table counts: {e}")
            return {}
    
    def validate_chain(
        self,
        manifest: BackupManifest,
        previous_manifest: Optional[BackupManifest]
    ) -> bool:
        """
        Validate an incremental backup chain.
        
        For incremental backups, verify that the previous backup
        referenced in the manifest actually exists and is valid.
        
        Args:
            manifest: Current backup manifest
            previous_manifest: Manifest of previous backup in chain
            
        Returns:
            True if chain is valid, False otherwise
        """
        if manifest.backup_type == BackupType.FULL:
            # Full backups don't need chain validation
            return True
        
        if manifest.backup_type == BackupType.INCREMENTAL:
            if previous_manifest is None:
                logger.error("Incremental backup missing previous manifest")
                return False
            
            if manifest.previous_backup_id != previous_manifest.backup_id:
                logger.error(
                    f"Chain break: expected {manifest.previous_backup_id}, "
                    f"got {previous_manifest.backup_id}"
                )
                return False
            
            return True
        
        return True


class ManifestCache:
    """
    In-memory cache for frequently accessed manifests.
    
    Reduces disk I/O for repeated manifest lookups.
    Uses LRU (Least Recently Used) eviction.
    
    Example:
        >>> cache = ManifestCache(max_size=100)
        >>> cache.get(Path('backup.db.manifest.json'))
        >>> cache.put(Path('backup.db.manifest.json'), manifest)
    """
    
    def __init__(self, max_size: int = 100):
        """
        Initialize manifest cache.
        
        Args:
            max_size: Maximum number of manifests to cache
        """
        self.max_size = max_size
        self._cache: Dict[str, BackupManifest] = {}
        self._access_order: list = []
    
    def get(self, path: Path) -> Optional[BackupManifest]:
        """
        Get manifest from cache.
        
        Args:
            path: Path to manifest file
            
        Returns:
            Cached manifest or None if not cached
        """
        key = str(path)
        return self._cache.get(key)
    
    def put(self, path: Path, manifest: BackupManifest) -> None:
        """
        Add manifest to cache.
        
        Evicts oldest entry if cache is full.
        
        Args:
            path: Path to manifest file
            manifest: Manifest to cache
        """
        key = str(path)
        
        # Evict if full and key not already cached
        if len(self._cache) >= self.max_size and key not in self._cache:
            oldest_key = self._access_order.pop(0)
            del self._cache[oldest_key]
        
        # Update access order
        if key in self._access_order:
            self._access_order.remove(key)
        self._access_order.append(key)
        
        self._cache[key] = manifest
    
    def invalidate(self, path: Path) -> None:
        """
        Remove manifest from cache.
        
        Args:
            path: Path to manifest file
        """
        key = str(path)
        
        if key in self._cache:
            del self._cache[key]
            self._access_order.remove(key)
    
    def clear(self) -> None:
        """Clear entire cache."""
        self._cache.clear()
        self._access_order.clear()
    
    def __len__(self) -> int:
        """Return number of cached manifests."""
        return len(self._cache)