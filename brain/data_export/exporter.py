"""
Data Exporter

Main orchestrator for data export operations.
Coordinates data collection, serialization, and packaging.

All implementation is in Python 3.10+
"""

import sqlite3
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict, Any
import logging
import zipfile
import os

from brain.data_export.models import (
    ExportRequest,
    ExportFormat,
    ExportStatus,
    ExportResult,
    EXPORT_MODULES,
)
from brain.data_export.serializers import (
    JSONSerializer,
    CSVSerializer,
    SQLiteSerializer,
    get_serializer,
)


logger = logging.getLogger(__name__)


class DataExporter:
    """
    Main orchestrator for data export operations.
    
    Handles:
    - Data collection from database
    - Format serialization
    - ZIP compression
    - Export request tracking
    
    Example:
        >>> exporter = DataExporter(db_path='tracking.db')
        >>> 
        >>> # Create export request
        >>> request = exporter.create_request(
        ...     user_id='user-1',
        ...     format='json',
        ...     modules=['habits', 'tasks']
        ... )
        >>> 
        >>> # Execute export
        >>> result = exporter.execute(request.id)
    """
    
    def __init__(
        self,
        db_path: str = None,
        db_connection: sqlite3.Connection = None,
        export_dir: str = None
    ):
        """
        Initialize data exporter.
        
        Args:
            db_path: Path to SQLite database
            db_connection: Existing database connection
            export_dir: Directory for export files
        """
        self.db_path = db_path
        self._external_db = db_connection is not None
        
        if db_connection:
            self.db = db_connection
        elif db_path:
            self.db = sqlite3.connect(db_path)
        else:
            self.db = None
        
        self.export_dir = Path(export_dir) if export_dir else Path('./exports')
        self.export_dir.mkdir(parents=True, exist_ok=True)
        
        # Track requests
        self._requests: Dict[str, ExportRequest] = {}
        
        # Ensure tables exist
        self._ensure_tables()
    
    def _ensure_tables(self) -> None:
        """Create required tables if they don't exist."""
        if self.db is None:
            return
        
        cursor = self.db.cursor()
        
        # Export requests table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS export_requests (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                format TEXT,
                modules TEXT,
                include_archived INTEGER,
                compression INTEGER,
                status TEXT,
                created_at TEXT,
                completed_at TEXT,
                file_path TEXT,
                download_token TEXT,
                expires_at TEXT,
                error_message TEXT
            )
        ''')
        
        # Export history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS export_history (
                id TEXT PRIMARY KEY,
                user_id TEXT,
                export_id TEXT,
                format TEXT,
                modules_exported TEXT,
                record_count INTEGER,
                file_size_bytes INTEGER,
                duration_seconds REAL,
                status TEXT,
                created_at TEXT
            )
        ''')
        
        self.db.commit()
    
    def create_request(
        self,
        user_id: str = "",
        format: str = "json",
        modules: List[str] = None,
        include_archived: bool = False,
        compression: bool = True
    ) -> ExportRequest:
        """
        Create an export request.
        
        Args:
            user_id: User requesting export
            format: Export format ('json', 'csv', 'sqlite')
            modules: Modules to export (empty = all)
            include_archived: Include soft-deleted records
            compression: Use ZIP compression
            
        Returns:
            ExportRequest tracking the request
        """
        request = ExportRequest(
            user_id=user_id,
            format=ExportFormat(format.lower()),
            modules=modules or [],
            include_archived=include_archived,
            compression=compression,
            status=ExportStatus.PENDING
        )
        
        # Save to database
        self._save_request(request)
        
        return request
    
    def execute(self, request_id: str) -> ExportResult:
        """
        Execute an export request.
        
        Args:
            request_id: ID of export request
            
        Returns:
            ExportResult with export details
        """
        result = ExportResult(export_id=request_id)
        start_time = datetime.now()
        
        # Get request
        request = self._get_request(request_id)
        if not request:
            result.error_message = "Request not found"
            return result
        
        try:
            # Update status
            request.status = ExportStatus.PROCESSING
            self._update_request(request)
            
            # Collect data
            data = self._collect_data(request.modules, request.include_archived)
            
            # Get serializer
            serializer = get_serializer(request.format.value)
            
            # Determine output path
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            extension = serializer.get_file_extension()
            
            if request.format == ExportFormat.CSV:
                output_path = self.export_dir / f"export_{timestamp}"
            else:
                output_path = self.export_dir / f"export_{timestamp}{extension}"
            
            # Serialize
            total_records = serializer.serialize(data, output_path)
            
            # Compress if requested
            if request.compression and request.format != ExportFormat.CSV:
                output_path = self._compress_file(output_path)
            
            # Update result
            result.success = True
            result.file_path = str(output_path)
            result.file_size_bytes = output_path.stat().st_size
            result.record_count = total_records
            result.modules_exported = list(data.keys())
            result.records_by_module = {k: len(v) for k, v in data.items()}
            result.duration_seconds = (datetime.now() - start_time).total_seconds()
            
            # Update request
            request.status = ExportStatus.COMPLETED
            request.completed_at = datetime.now()
            request.file_path = str(output_path)
            
            # Generate download token
            request.download_token = self._generate_token()
            request.expires_at = datetime.now() + timedelta(hours=24)
            
            self._update_request(request)
            
            # Record history
            self._record_history(request, result)
            
        except Exception as e:
            result.error_message = str(e)
            request.status = ExportStatus.FAILED
            request.error_message = str(e)
            self._update_request(request)
            logger.error(f"Export failed: {e}")
        
        return result
    
    def _collect_data(
        self,
        modules: List[str],
        include_archived: bool = False
    ) -> Dict[str, List[Dict[str, Any]]]:
        """
        Collect data from database.
        
        Args:
            modules: Modules to collect (empty = all)
            include_archived: Include soft-deleted records
            
        Returns:
            Dictionary mapping table names to row lists
        """
        if self.db is None:
            return {}
        
        data = {}
        cursor = self.db.cursor()
        
        # Determine which modules to export
        export_modules = modules if modules else list(EXPORT_MODULES.keys())
        
        for module_name in export_modules:
            module = EXPORT_MODULES.get(module_name)
            if not module:
                continue
            
            for table in module.tables:
                try:
                    # Check if table exists
                    cursor.execute(
                        "SELECT name FROM sqlite_master WHERE type='table' AND name=?",
                        (table,)
                    )
                    if not cursor.fetchone():
                        continue
                    
                    # Get all rows
                    cursor.execute(f"SELECT * FROM {table}")
                    columns = [desc[0] for desc in cursor.description]
                    rows = cursor.fetchall()
                    
                    data[table] = [dict(zip(columns, row)) for row in rows]
                    
                except Exception as e:
                    logger.warning(f"Failed to collect {table}: {e}")
                    data[table] = []
        
        return data
    
    def _compress_file(self, file_path: Path) -> Path:
        """
        Compress file to ZIP.
        
        Args:
            file_path: Path to file to compress
            
        Returns:
            Path to ZIP file
        """
        zip_path = file_path.with_suffix('.zip')
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
            zf.write(file_path, file_path.name)
        
        # Remove original file
        file_path.unlink()
        
        return zip_path
    
    def _generate_token(self) -> str:
        """Generate secure download token."""
        import secrets
        return secrets.token_urlsafe(32)
    
    def _save_request(self, request: ExportRequest) -> None:
        """Save request to database."""
        self._requests[request.id] = request
        
        if self.db is None:
            return
        
        cursor = self.db.cursor()
        data = request.to_dict()
        cursor.execute('''
            INSERT INTO export_requests
            (id, user_id, format, modules, include_archived, compression,
             status, created_at, completed_at, file_path, download_token,
             expires_at, error_message)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            data['id'], data['user_id'], data['format'], data['modules'],
            data['include_archived'], data['compression'], data['status'],
            data['created_at'], data['completed_at'], data['file_path'],
            data['download_token'], data['expires_at'], data['error_message']
        ))
        self.db.commit()
    
    def _get_request(self, request_id: str) -> Optional[ExportRequest]:
        """Get request from database."""
        if request_id in self._requests:
            return self._requests[request_id]
        
        if self.db is None:
            return None
        
        cursor = self.db.cursor()
        cursor.execute(
            "SELECT * FROM export_requests WHERE id = ?",
            (request_id,)
        )
        
        row = cursor.fetchone()
        if row:
            columns = [desc[0] for desc in cursor.description]
            return ExportRequest.from_dict(dict(zip(columns, row)))
        return None
    
    def _update_request(self, request: ExportRequest) -> None:
        """Update request in database."""
        self._requests[request.id] = request
        
        if self.db is None:
            return
        
        data = request.to_dict()
        cursor = self.db.cursor()
        cursor.execute('''
            UPDATE export_requests SET
                status = ?, completed_at = ?, file_path = ?,
                download_token = ?, expires_at = ?, error_message = ?
            WHERE id = ?
        ''', (
            data['status'], data['completed_at'], data['file_path'],
            data['download_token'], data['expires_at'], data['error_message'],
            data['id']
        ))
        self.db.commit()
    
    def _record_history(self, request: ExportRequest, result: ExportResult) -> None:
        """Record export in history."""
        if self.db is None:
            return
        
        cursor = self.db.cursor()
        cursor.execute('''
            INSERT INTO export_history
            (id, user_id, export_id, format, modules_exported, record_count,
             file_size_bytes, duration_seconds, status, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            request.id,
            request.user_id,
            request.id,
            request.format.value,
            ','.join(result.modules_exported),
            result.record_count,
            result.file_size_bytes,
            result.duration_seconds,
            request.status.value,
            datetime.now().isoformat()
        ))
        self.db.commit()
    
    def get_available_modules(self) -> Dict[str, Dict[str, str]]:
        """
        Get list of available export modules.
        
        Returns:
            Dictionary of module info
        """
        return {
            name: module.to_dict()
            for name, module in EXPORT_MODULES.items()
        }
    
    def get_request(self, request_id: str) -> Optional[ExportRequest]:
        """Get export request by ID."""
        return self._get_request(request_id)
    
    def list_requests(
        self,
        user_id: str = None,
        status: ExportStatus = None
    ) -> List[ExportRequest]:
        """List export requests."""
        if self.db is None:
            return list(self._requests.values())
        
        cursor = self.db.cursor()
        
        query = "SELECT * FROM export_requests WHERE 1=1"
        params = []
        
        if user_id:
            query += " AND user_id = ?"
            params.append(user_id)
        
        if status:
            query += " AND status = ?"
            params.append(status.value)
        
        query += " ORDER BY created_at DESC"
        
        cursor.execute(query, params)
        
        columns = [desc[0] for desc in cursor.description]
        return [
            ExportRequest.from_dict(dict(zip(columns, row)))
            for row in cursor.fetchall()
        ]
    
    def close(self) -> None:
        """Close database connection if we own it."""
        if self.db and not self._external_db:
            self.db.close()