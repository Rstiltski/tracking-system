"""
Conflict Resolver

Python-based conflict detection and resolution for data imports.
Implements four strategies: SKIP, OVERWRITE, MERGE, DUPLICATE

All implementation is in Python 3.10+
"""

from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import json


class ConflictResolution(Enum):
    """Result of conflict resolution."""
    SKIPPED = "skipped"
    OVERWRITTEN = "overwritten"
    MERGED = "merged"
    DUPLICATED = "duplicated"
    NO_CONFLICT = "no_conflict"


@dataclass
class ConflictRecord:
    """Represents a detected conflict."""
    module: str
    imported_id: str
    existing_id: str
    field: str
    imported_value: Any
    existing_value: Any
    resolution: ConflictResolution = ConflictResolution.NO_CONFLICT
    resolved_value: Any = None


class ConflictResolver:
    """
    Detects and resolves conflicts during import.
    
    Four strategies:
    - SKIP: Keep existing record, skip imported
    - OVERWRITE: Replace existing with imported
    - MERGE: Combine fields from both records
    - DUPLICATE: Keep both as separate records
    """
    
    def __init__(self, db_connection=None):
        """
        Initialize conflict resolver.
        
        Args:
            db_connection: SQLite database connection
        """
        self.db = db_connection
        self.conflicts: List[ConflictRecord] = []
        self.resolutions: Dict[str, ConflictResolution] = {}
    
    def detect_conflicts(
        self,
        modules: Dict[str, List[Dict[str, Any]]]
    ) -> List[ConflictRecord]:
        """
        Detect conflicts between imported data and database.
        
        Args:
            modules: Dictionary mapping module names to records
            
        Returns:
            List of detected conflicts
        """
        self.conflicts = []
        
        for module_name, records in modules.items():
            for record in records:
                conflicts = self._detect_module_conflicts(
                    module_name, record
                )
                self.conflicts.extend(conflicts)
        
        return self.conflicts
    
    def _detect_module_conflicts(
        self,
        module_name: str,
        record: Dict[str, Any]
    ) -> List[ConflictRecord]:
        """Detect conflicts for a single record."""
        conflicts = []
        
        if not self.db:
            return conflicts
        
        # Check by ID
        if 'id' in record:
            conflict = self._check_by_id(
                module_name, record['id'], record
            )
            if conflict:
                conflicts.append(conflict)
        
        # Check by unique fields (e.g., email, username)
        unique_fields = self._get_unique_fields(module_name)
        for field_name in unique_fields:
            if field_name in record:
                conflict = self._check_by_field(
                    module_name, field_name, record[field_name], record
                )
                if conflict:
                    conflicts.append(conflict)
        
        return conflicts
    
    def _check_by_id(
        self,
        module_name: str,
        record_id: str,
        record: Dict[str, Any]
    ) -> Optional[ConflictRecord]:
        """Check if record ID already exists."""
        table_name = self._get_table_name(module_name)
        
        try:
            cursor = self.db.execute(
                f"SELECT * FROM {table_name} WHERE id = ?",
                (record_id,)
            )
            existing = cursor.fetchone()
            
            if existing:
                # Convert row to dict
                existing_dict = dict(existing)
                
                # Find first differing field
                for field, value in record.items():
                    if field in existing_dict:
                        existing_value = existing_dict[field]
                        if value != existing_value:
                            return ConflictRecord(
                                module=module_name,
                                imported_id=record_id,
                                existing_id=record_id,
                                field=field,
                                imported_value=value,
                                existing_value=existing_value
                            )
        except Exception:
            pass  # Table might not exist
        
        return None
    
    def _check_by_field(
        self,
        module_name: str,
        field_name: str,
        value: Any,
        record: Dict[str, Any]
    ) -> Optional[ConflictRecord]:
        """Check if unique field value already exists."""
        table_name = self._get_table_name(module_name)
        
        try:
            cursor = self.db.execute(
                f"SELECT * FROM {table_name} WHERE {field_name} = ?",
                (value,)
            )
            existing = cursor.fetchone()
            
            if existing:
                existing_dict = dict(existing)
                return ConflictRecord(
                    module=module_name,
                    imported_id=record.get('id', 'unknown'),
                    existing_id=existing_dict.get('id', 'unknown'),
                    field=field_name,
                    imported_value=value,
                    existing_value=value
                )
        except Exception:
            pass
        
        return None
    
    def resolve(
        self,
        conflict: ConflictRecord,
        strategy: 'ConflictStrategy'
    ) -> ConflictResolution:
        """
        Resolve a conflict using specified strategy.
        
        Args:
            conflict: Conflict to resolve
            strategy: Resolution strategy
            
        Returns:
            Resolution result
        """
        if strategy == ConflictStrategy.SKIP:
            return self._resolve_skip(conflict)
        elif strategy == ConflictStrategy.OVERWRITE:
            return self._resolve_overwrite(conflict)
        elif strategy == ConflictStrategy.MERGE:
            return self._resolve_merge(conflict)
        elif strategy == ConflictStrategy.DUPLICATE:
            return self._resolve_duplicate(conflict)
        
        return ConflictResolution.NO_CONFLICT
    
    def _resolve_skip(
        self,
        conflict: ConflictRecord
    ) -> ConflictResolution:
        """Skip imported record, keep existing."""
        conflict.resolution = ConflictResolution.SKIPPED
        conflict.resolved_value = conflict.existing_value
        return ConflictResolution.SKIPPED
    
    def _resolve_overwrite(
        self,
        conflict: ConflictRecord
    ) -> ConflictResolution:
        """Overwrite existing with imported."""
        conflict.resolution = ConflictResolution.OVERWRITTEN
        conflict.resolved_value = conflict.imported_value
        return ConflictResolution.OVERWRITTEN
    
    def _resolve_merge(
        self,
        conflict: ConflictRecord
    ) -> ConflictResolution:
        """Merge fields from both records."""
        conflict.resolution = ConflictResolution.MERGED
        # Prefer non-None values, imported takes precedence
        conflict.resolved_value = conflict.imported_value
        return ConflictResolution.MERGED
    
    def _resolve_duplicate(
        self,
        conflict: ConflictRecord
    ) -> ConflictResolution:
        """Keep both records with new ID."""
        conflict.resolution = ConflictResolution.DUPLICATED
        # Generate new ID for imported record
        import uuid
        conflict.resolved_value = str(uuid.uuid4())
        return ConflictResolution.DUPLICATED
    
    def apply_resolution(
        self,
        conflict: ConflictRecord,
        record: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Apply resolution to record.
        
        Args:
            conflict: Resolved conflict
            record: Imported record
            
        Returns:
            Modified record ready for import
        """
        if conflict.resolution == ConflictResolution.SKIPPED:
            return None  # Skip this record
        
        elif conflict.resolution == ConflictResolution.OVERWRITTEN:
            return record  # Use imported as-is
        
        elif conflict.resolution == ConflictResolution.MERGED:
            # Merge with existing
            if self.db:
                existing = self._get_existing_record(
                    conflict.module, conflict.existing_id
                )
                if existing:
                    return {**existing, **record}
            return record
        
        elif conflict.resolution == ConflictResolution.DUPLICATED:
            # Generate new ID
            import uuid
            return {**record, 'id': str(uuid.uuid4())}
        
        return record
    
    def _get_existing_record(
        self,
        module_name: str,
        record_id: str
    ) -> Optional[Dict[str, Any]]:
        """Get existing record from database."""
        if not self.db:
            return None
        
        table_name = self._get_table_name(module_name)
        
        try:
            cursor = self.db.execute(
                f"SELECT * FROM {table_name} WHERE id = ?",
                (record_id,)
            )
            row = cursor.fetchone()
            return dict(row) if row else None
        except Exception:
            return None
    
    def _get_table_name(self, module_name: str) -> str:
        """Convert module name to table name."""
        # Simple conversion, can be extended
        table_map = {
            'habits': 'habits',
            'tasks': 'tasks',
            'goals': 'goals',
            'transactions': 'transactions',
            'health_entries': 'health_entries',
            'time_entries': 'time_entries',
            'achievements': 'achievements',
        }
        return table_map.get(module_name, module_name)
    
    def _get_unique_fields(self, module_name: str) -> List[str]:
        """Get unique fields for a module."""
        unique = {
            'users': ['email', 'username'],
            'habits': [],  # Only ID is unique
            'tasks': [],
            'transactions': [],
        }
        return unique.get(module_name, [])
    
    def get_summary(self) -> Dict[str, Any]:
        """Get conflict resolution summary."""
        counts = {
            'skipped': 0,
            'overwritten': 0,
            'merged': 0,
            'duplicated': 0,
            'no_conflict': 0,
        }
        
        for conflict in self.conflicts:
            key = conflict.resolution.value
            counts[key] = counts.get(key, 0) + 1
        
        return {
            'total_conflicts': len(self.conflicts),
            'resolutions': counts,
        }


class ConflictStrategy(Enum):
    """Strategy for resolving conflicts."""
    SKIP = "skip"
    OVERWRITE = "overwrite"
    MERGE = "merge"
    DUPLICATE = "duplicate"
