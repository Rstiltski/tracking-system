"""
Data Importer

Main Python class for orchestrating data imports.
Coordinates parsing, validation, conflict resolution, and transaction-based import.

All implementation is in Python 3.10+
"""

import sqlite3
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import json

from brain.data_import.models import (
    ImportRequest,
    ImportStatus,
    ConflictStrategy,
    ImportResult,
    ImportPreview,
)
from brain.data_import.parsers import JSONParser, CSVParser, SQLiteImporter
from brain.data_import.validator import ImportValidator
from brain.data_import.conflict_resolver import (
    ConflictResolver,
    ConflictStrategy as ConflictStrategyEnum,
)


class DataImporter:
    """
    Main data import orchestrator.
    
    Coordinates the full import pipeline:
    1. Parse import file (JSON/CSV/SQLite)
    2. Validate data (schema, types, integrity)
    3. Detect conflicts
    4. Resolve conflicts per strategy
    5. Import in transaction
    
    Example:
        importer = DataImporter(db_connection)
        
        # Preview import
        preview = importer.preview('backup.json')
        print(f"Will import {preview.total_records} records")
        
        # Execute import
        result = importer.import_file(
            'backup.json',
            user_id='user-123',
            strategy=ConflictStrategy.SKIP
        )
        
        if result.success:
            print(f"Imported {result.records_imported} records")
    """
    
    def __init__(self, db_connection=None, db_path: str = None):
        """
        Initialize data importer.
        
        Args:
            db_connection: Existing SQLite connection
            db_path: Path to SQLite database (if no connection)
        """
        self.db = db_connection
        self.db_path = db_path
        self._ensure_db_connection()
    
    def _ensure_db_connection(self):
        """Ensure database connection exists."""
        if self.db is None and self.db_path:
            self.db = sqlite3.connect(self.db_path)
            self.db.row_factory = sqlite3.Row
    
    def preview(
        self,
        file_path: str,
        modules: List[str] = None
    ) -> ImportPreview:
        """
        Preview import without committing.
        
        Args:
            file_path: Path to import file
            modules: Specific modules to import (None = all)
            
        Returns:
            ImportPreview with record counts and conflicts
        """
        preview_data = self._parse_file(file_path)
        
        # Filter modules if specified
        if modules:
            preview_data.modules = {
                k: v for k, v in preview_data.modules.items()
                if k in modules
            }
        
        # Count records
        total = sum(len(records) for records in preview_data.modules.values())
        by_module = {
            name: len(records)
            for name, records in preview_data.modules.items()
        }
        
        # Detect conflicts
        resolver = ConflictResolver(self.db)
        conflicts = resolver.detect_conflicts(preview_data.modules)
        
        conflicts_by_module = {}
        for conflict in conflicts:
            conflicts_by_module[conflict.module] = (
                conflicts_by_module.get(conflict.module, 0) + 1
            )
        
        return ImportPreview(
            total_records=total,
            records_by_module=by_module,
            conflicts_detected=len(conflicts),
            conflicts_by_module=conflicts_by_module,
            estimated_duration_seconds=total * 0.01,  # ~10ms per record
            warnings=preview_data.warnings
        )
    
    def import_file(
        self,
        file_path: str,
        user_id: str = "default",
        strategy: ConflictStrategy = ConflictStrategy.SKIP,
        modules: List[str] = None,
        dry_run: bool = True
    ) -> ImportResult:
        """
        Import data from file.
        
        Args:
            file_path: Path to import file
            user_id: User ID for tracking
            strategy: Conflict resolution strategy
            modules: Specific modules to import (None = all)
            dry_run: If True, don't commit changes
            
        Returns:
            ImportResult with import statistics
        """
        # Create import request
        request = ImportRequest(
            user_id=user_id,
            file_path=file_path,
            format=Path(file_path).suffix[1:],  # Remove dot
            conflict_strategy=strategy,
            modules_to_import=modules or [],
            dry_run=dry_run,
        )
        
        try:
            # Parse file
            parsed_data = self._parse_file(file_path)
            
            # Filter modules if specified
            if modules:
                parsed_data.modules = {
                    k: v for k, v in parsed_data.modules.items()
                    if k in modules
                }
            
            # Validate
            validator = ImportValidator(self.db)
            is_valid, errors = validator.validate_all(parsed_data.modules)
            
            if not is_valid:
                request.status = ImportStatus.FAILED
                request.validation_errors = [
                    f"{e.module}.{e.field}: {e.message}"
                    for e in errors
                ]
                return ImportResult(
                    success=False,
                    error_message=f"Validation failed: {len(errors)} errors"
                )
            
            # Detect and resolve conflicts
            resolver = ConflictResolver(self.db)
            conflicts = resolver.detect_conflicts(parsed_data.modules)
            
            # Apply conflict resolution strategy
            strategy_enum = ConflictStrategyEnum(strategy.value)
            resolved_modules = self._apply_conflict_resolution(
                parsed_data.modules, resolver, strategy_enum
            )
            
            # Import data
            if dry_run:
                return ImportResult(
                    success=True,
                    records_imported=sum(
                        len(records) for records in resolved_modules.values()
                    ),
                    conflicts_resolved=len(conflicts),
                    details={'dry_run': True}
                )
            
            # Execute import in transaction
            result = self._execute_import(resolved_modules)
            
            request.status = ImportStatus.COMPLETED
            request.import_summary = result.to_dict()
            
            return result
            
        except Exception as e:
            request.status = ImportStatus.FAILED
            request.error_message = str(e)
            
            return ImportResult(
                success=False,
                error_message=str(e)
            )
        
        finally:
            # Save import request to history
            self._save_import_request(request)
    
    def _parse_file(self, file_path: str):
        """Parse import file based on format."""
        path = Path(file_path)
        suffix = path.suffix.lower()
        
        if suffix == '.json':
            parser = JSONParser(file_path)
            return parser.parse()
        elif suffix == '.csv':
            parser = CSVParser(file_path)
            return parser.parse()
        elif suffix == '.zip':
            parser = CSVParser(file_path)
            return parser.parse()
        elif suffix in ['.db', '.sqlite', '.sqlite3']:
            # SQLite import is handled differently
            raise NotImplementedError(
                "SQLite direct import not yet implemented"
            )
        else:
            raise ValueError(f"Unsupported file format: {suffix}")
    
    def _apply_conflict_resolution(
        self,
        modules: Dict[str, List[Dict[str, Any]]],
        resolver: ConflictResolver,
        strategy: ConflictStrategyEnum
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Apply conflict resolution to all records.
        
        Args:
            modules: Parsed module data
            resolver: Conflict resolver instance
            strategy: Resolution strategy
            
        Returns:
            Modified modules with conflicts resolved
        """
        resolved = {}
        
        for module_name, records in modules.items():
            resolved_records = []
            
            for record in records:
                # Find conflicts for this record
                record_conflicts = [
                    c for c in resolver.conflicts
                    if c.imported_id == record.get('id')
                ]
                
                if not record_conflicts:
                    # No conflicts, include as-is
                    resolved_records.append(record)
                    continue
                
                # Apply resolution for each conflict
                modified_record = record.copy()
                skip_record = False
                
                for conflict in record_conflicts:
                    resolution = resolver.resolve(conflict, strategy)
                    
                    if resolution == ConflictStrategyEnum.SKIP:
                        skip_record = True
                        break
                    
                    resolved_record = resolver.apply_resolution(
                        conflict, modified_record
                    )
                    
                    if resolved_record is None:
                        skip_record = True
                        break
                    
                    modified_record = resolved_record
                
                if not skip_record:
                    resolved_records.append(modified_record)
            
            resolved[module_name] = resolved_records
        
        return resolved
    
    def _execute_import(
        self,
        modules: Dict[str, List[Dict[str, Any]]]
    ) -> ImportResult:
        """
        Execute import in transaction.
        
        Args:
            modules: Resolved module data
            
        Returns:
            ImportResult with statistics
        """
        if not self.db:
            return ImportResult(
                success=False,
                error_message="No database connection"
            )
        
        stats = {
            'imported': 0,
            'skipped': 0,
            'failed': 0,
        }
        
        try:
            # Begin transaction
            for module_name, records in modules.items():
                table_name = self._get_table_name(module_name)
                
                for record in records:
                    try:
                        self._insert_record(table_name, record)
                        stats['imported'] += 1
                    except Exception as e:
                        stats['failed'] += 1
            
            # Commit transaction
            self.db.commit()
            
            return ImportResult(
                success=True,
                records_imported=stats['imported'],
                records_skipped=stats['skipped'],
                records_failed=stats['failed'],
            )
            
        except Exception as e:
            # Rollback on error
            self.db.rollback()
            
            return ImportResult(
                success=False,
                error_message=f"Import failed: {str(e)}",
                details=stats
            )
    
    def _insert_record(
        self,
        table_name: str,
        record: Dict[str, Any]
    ) -> None:
        """
        Insert or replace a single record.
        
        Args:
            table_name: Target table name
            record: Record dictionary
        """
        if not record:
            return
        
        # Build INSERT OR REPLACE statement
        columns = list(record.keys())
        placeholders = ','.join(['?' for _ in columns])
        columns_str = ','.join(columns)
        
        values = [
            self._serialize_value(record[col])
            for col in columns
        ]
        
        self.db.execute(
            f"""INSERT OR REPLACE INTO {table_name}
                ({columns_str}) VALUES ({placeholders})""",
            values
        )
    
    def _serialize_value(self, value: Any) -> Any:
        """Serialize value for SQLite storage."""
        if value is None:
            return None
        elif isinstance(value, (dict, list)):
            return json.dumps(value)
        elif isinstance(value, datetime):
            return value.isoformat()
        else:
            return value
    
    def _get_table_name(self, module_name: str) -> str:
        """Convert module name to table name."""
        table_map = {
            'habits': 'habits',
            'tasks': 'tasks',
            'goals': 'goals',
            'transactions': 'transactions',
            'health_entries': 'health_entries',
            'time_entries': 'time_entries',
            'achievements': 'achievements',
            'xp_logs': 'xp_logs',
        }
        return table_map.get(module_name, module_name)
    
    def _save_import_request(self, request: ImportRequest) -> None:
        """Save import request to history."""
        if not self.db:
            return
        
        try:
            self.db.execute(
                """INSERT INTO import_requests
                   (id, user_id, file_path, format, conflict_strategy,
                    modules_to_import, dry_run, status, validation_errors,
                    import_summary, created_at, completed_at, error_message)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    request.id, request.user_id, request.file_path,
                    request.format, request.conflict_strategy.value,
                    ','.join(request.modules_to_import), request.dry_run,
                    request.status.value, ','.join(request.validation_errors),
                    json.dumps(request.import_summary) if request.import_summary else None,
                    request.created_at.isoformat(),
                    request.completed_at.isoformat() if request.completed_at else None,
                    request.error_message,
                )
            )
            self.db.commit()
        except Exception:
            pass  # Table might not exist yet
