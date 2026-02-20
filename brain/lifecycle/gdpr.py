"""
GDPR Compliance Module

Implements GDPR rights:
- Right to Access (Article 15)
- Right to Erasure (Article 17)
- Right to Portability (Article 20)

All implementation is in Python 3.10+
"""

import sqlite3
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any
import json
import logging
from pathlib import Path
import uuid

from brain.lifecycle.models import (
    ErasureRequest,
    ErasureStatus,
    LifecycleResult
)


logger = logging.getLogger(__name__)


class GDPRCompliance:
    """
    GDPR compliance utilities.
    
    Implements the key GDPR rights for user data:
    - Right to Access: Export all user data
    - Right to Erasure: Delete all user data (with grace period)
    - Right to Portability: Machine-readable export
    
    Example:
        gdpr = GDPRCompliance(db_connection)
        
        # Right to Access
        data = gdpr.export_user_data(user_id='user-123')
        
        # Right to Erasure
        request = gdpr.request_erasure(user_id='user-123')
    """
    
    def __init__(
        self,
        db_connection: sqlite3.Connection = None,
        export_dir: str = None
    ):
        """
        Initialize GDPR compliance module.
        
        Args:
            db_connection: SQLite database connection
            export_dir: Directory for data exports
        """
        self.db = db_connection
        self.export_dir = Path(export_dir) if export_dir else Path('./exports')
        self.export_dir.mkdir(parents=True, exist_ok=True)
    
    def export_user_data(
        self,
        user_id: str,
        format: str = 'json'
    ) -> Dict[str, Any]:
        """
        Export all user data (Right to Access - Article 15).
        
        Collects all data associated with the user across
        all tables and provides it in a structured format.
        
        Args:
            user_id: User identifier
            format: Export format ('json' or 'dict')
            
        Returns:
            Dictionary containing all user data
        """
        if self.db is None:
            return {'error': 'No database connection'}
        
        export_data = {
            'user_id': user_id,
            'exported_at': datetime.now().isoformat(),
            'gdpr_article': 'Article 15 - Right to Access',
            'data': {}
        }
        
        cursor = self.db.cursor()
        
        # Tables to export (with user_id column mapping)
        user_tables = {
            'habits': 'user_id',
            'tasks': 'user_id',
            'goals': 'user_id',
            'transactions': 'user_id',
            'health_entries': 'user_id',
            'time_entries': 'user_id',
            'habit_logs': 'user_id',
            'xp_logs': 'user_id',
        }
        
        for table, user_column in user_tables.items():
            try:
                cursor.execute(
                    f"SELECT * FROM {table} WHERE {user_column} = ?",
                    (user_id,)
                )
                columns = [desc[0] for desc in cursor.description]
                rows = cursor.fetchall()
                
                export_data['data'][table] = [
                    dict(zip(columns, row)) for row in rows
                ]
                
            except Exception as e:
                export_data['data'][table] = {'error': str(e)}
        
        # Add summary statistics
        export_data['summary'] = {
            table: len(records) if isinstance(records, list) else 0
            for table, records in export_data['data'].items()
        }
        
        return export_data
    
    def request_erasure(
        self,
        user_id: str
    ) -> ErasureRequest:
        """
        Request data erasure (Right to Erasure - Article 17).
        
        Creates an erasure request that goes through:
        1. Pending status
        2. Verification (email confirmation)
        3. 30-day grace period
        4. Execution
        
        Args:
            user_id: User identifier
            
        Returns:
            ErasureRequest tracking the request
        """
        request = ErasureRequest(
            user_id=user_id,
            status=ErasureStatus.PENDING,
            verification_token=str(uuid.uuid4())
        )
        
        # Save to database
        if self.db:
            cursor = self.db.cursor()
            cursor.execute('''
                INSERT INTO erasure_requests
                (id, user_id, status, requested_at, verification_token, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (
                request.id,
                request.user_id,
                request.status.value,
                request.requested_at.isoformat(),
                request.verification_token,
                request.created_at.isoformat()
            ))
            self.db.commit()
        
        logger.info(f"Erasure request created for user {user_id}")
        
        return request
    
    def verify_erasure_request(
        self,
        request_id: str,
        token: str
    ) -> Optional[ErasureRequest]:
        """
        Verify an erasure request.
        
        Validates the verification token and moves
        request to grace period status.
        
        Args:
            request_id: Erasure request ID
            token: Verification token
            
        Returns:
            Updated ErasureRequest or None if invalid
        """
        if self.db is None:
            return None
        
        cursor = self.db.cursor()
        cursor.execute(
            "SELECT * FROM erasure_requests WHERE id = ?",
            (request_id,)
        )
        
        row = cursor.fetchone()
        if not row:
            return None
        
        columns = [desc[0] for desc in cursor.description]
        request = ErasureRequest.from_dict(dict(zip(columns, row)))
        
        if request.verification_token != token:
            return None
        
        # Update to grace period
        request.status = ErasureStatus.GRACE_PERIOD
        request.verified_at = datetime.now()
        request.grace_period_until = datetime.now() + timedelta(days=30)
        
        cursor.execute('''
            UPDATE erasure_requests SET
                status = ?,
                verified_at = ?,
                grace_period_until = ?
            WHERE id = ?
        ''', (
            request.status.value,
            request.verified_at.isoformat(),
            request.grace_period_until.isoformat(),
            request.id
        ))
        self.db.commit()
        
        logger.info(f"Erasure request {request_id} verified, grace period started")
        
        return request
    
    def cancel_erasure_request(
        self,
        request_id: str,
        reason: str = None
    ) -> bool:
        """
        Cancel an erasure request.
        
        User can cancel during grace period.
        
        Args:
            request_id: Erasure request ID
            reason: Cancellation reason
            
        Returns:
            True if cancelled successfully
        """
        if self.db is None:
            return False
        
        cursor = self.db.cursor()
        cursor.execute(
            "SELECT * FROM erasure_requests WHERE id = ?",
            (request_id,)
        )
        
        row = cursor.fetchone()
        if not row:
            return False
        
        columns = [desc[0] for desc in cursor.description]
        request = ErasureRequest.from_dict(dict(zip(columns, row)))
        
        if request.status not in (ErasureStatus.PENDING, ErasureStatus.GRACE_PERIOD):
            return False
        
        cursor.execute('''
            UPDATE erasure_requests SET
                status = ?,
                cancellation_reason = ?
            WHERE id = ?
        ''', (ErasureStatus.CANCELLED.value, reason, request_id))
        self.db.commit()
        
        logger.info(f"Erasure request {request_id} cancelled")
        
        return True
    
    def execute_erasure(
        self,
        request_id: str
    ) -> LifecycleResult:
        """
        Execute an erasure request.
        
        Permanently deletes all user data.
        Only works after grace period expires.
        
        Args:
            request_id: Erasure request ID
            
        Returns:
            LifecycleResult with execution status
        """
        result = LifecycleResult(operation="gdpr_erasure")
        
        if self.db is None:
            result.error_message = "No database connection"
            return result
        
        cursor = self.db.cursor()
        cursor.execute(
            "SELECT * FROM erasure_requests WHERE id = ?",
            (request_id,)
        )
        
        row = cursor.fetchone()
        if not row:
            result.error_message = "Request not found"
            return result
        
        columns = [desc[0] for desc in cursor.description]
        request = ErasureRequest.from_dict(dict(zip(columns, row)))
        
        if not request.can_execute():
            result.error_message = "Request cannot be executed (grace period not expired)"
            return result
        
        # Create data export before deletion
        export_data = self.export_user_data(request.user_id)
        export_path = self.export_dir / f"erasure_export_{request.user_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(export_path, 'w') as f:
            json.dump(export_data, f, indent=2, default=str)
        
        # Delete from all tables
        user_tables = {
            'habits': 'user_id',
            'tasks': 'user_id',
            'goals': 'user_id',
            'transactions': 'user_id',
            'health_entries': 'user_id',
            'time_entries': 'user_id',
            'habit_logs': 'user_id',
            'xp_logs': 'user_id',
        }
        
        deleted_count = 0
        for table, user_column in user_tables.items():
            try:
                cursor.execute(
                    f"DELETE FROM {table} WHERE {user_column} = ?",
                    (request.user_id,)
                )
                deleted_count += cursor.rowcount
            except Exception as e:
                logger.warning(f"Failed to delete from {table}: {e}")
        
        # Update request status
        cursor.execute('''
            UPDATE erasure_requests SET
                status = ?,
                executed_at = ?,
                data_export_path = ?
            WHERE id = ?
        ''', (
            ErasureStatus.EXECUTED.value,
            datetime.now().isoformat(),
            str(export_path),
            request_id
        ))
        self.db.commit()
        
        result.success = True
        result.records_affected = deleted_count
        result.details = {'export_path': str(export_path)}
        
        logger.info(f"Erasure request {request_id} executed, {deleted_count} records deleted")
        
        return result
    
    def get_erasure_request(self, request_id: str) -> Optional[ErasureRequest]:
        """Get an erasure request by ID."""
        if self.db is None:
            return None
        
        cursor = self.db.cursor()
        cursor.execute(
            "SELECT * FROM erasure_requests WHERE id = ?",
            (request_id,)
        )
        
        row = cursor.fetchone()
        if row:
            columns = [desc[0] for desc in cursor.description]
            return ErasureRequest.from_dict(dict(zip(columns, row)))
        return None
    
    def list_erasure_requests(
        self,
        user_id: str = None,
        status: ErasureStatus = None
    ) -> List[ErasureRequest]:
        """List erasure requests."""
        if self.db is None:
            return []
        
        cursor = self.db.cursor()
        
        query = "SELECT * FROM erasure_requests WHERE 1=1"
        params = []
        
        if user_id:
            query += " AND user_id = ?"
            params.append(user_id)
        
        if status:
            query += " AND status = ?"
            params.append(status.value)
        
        query += " ORDER BY requested_at DESC"
        
        cursor.execute(query, params)
        
        columns = [desc[0] for desc in cursor.description]
        return [
            ErasureRequest.from_dict(dict(zip(columns, row)))
            for row in cursor.fetchall()
        ]
    
    def export_portable_data(
        self,
        user_id: str,
        format: str = 'json'
    ) -> Path:
        """
        Export data in portable format (Right to Portability - Article 20).
        
        Creates a machine-readable export that can be
        transmitted to another service provider.
        
        Args:
            user_id: User identifier
            format: Export format ('json' or 'csv')
            
        Returns:
            Path to exported file
        """
        data = self.export_user_data(user_id)
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        if format == 'json':
            export_path = self.export_dir / f"portable_export_{user_id}_{timestamp}.json"
            with open(export_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
        else:
            # CSV export (simplified - one file per table)
            export_path = self.export_dir / f"portable_export_{user_id}_{timestamp}"
            export_path.mkdir(parents=True, exist_ok=True)
            
            for table, records in data.get('data', {}).items():
                if isinstance(records, list) and records:
                    import csv
                    table_path = export_path / f"{table}.csv"
                    with open(table_path, 'w', newline='') as f:
                        writer = csv.DictWriter(f, fieldnames=records[0].keys())
                        writer.writeheader()
                        writer.writerows(records)
        
        logger.info(f"Portable export created at {export_path}")
        
        return export_path