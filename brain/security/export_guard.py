"""
Phase 9.2: Export Guard - Data Theft Prevention

Prevent bulk data theft via CSV export with:
- Watermarking: Hidden column to track who exported the data
- Rate limiting: Max 1 export per hour for non-admin users
- Tripwire: Large exports (>500 rows) require step-up authentication
- Admin alerts: Notify admins of exports >1000 rows
- Audit logging: Track all exports with full details

Example:
    guard = ExportGuard(user_id=5, company_id=1)
    
    # Check if export is allowed
    if not guard.check_rate_limit():
        raise Exception("Export rate limit exceeded")
    
    # Add watermark to data
    data_with_watermark = guard.add_watermark(customer_data)
    
    # Log the export
    guard.log_export('customers', len(customer_data), file_size)
📚 REQUIRED READING BEFORE MODIFICATION:
- SECURITY_GUIDE.md
- BRAIN_USAGE_GUIDE.md
- LLM_AGENT_QUICKSTART.md
"""
import hashlib
import time
from typing import List, Dict, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass
from app.pages.debugging_dashboard import is_admin

@dataclass
class ExportLimitException(Exception):
    """Exception raised when export rate limit is exceeded"""
    message: str
    retry_after_seconds: int = 0

@dataclass
class StepUpAuthRequiredException(Exception):
    """Exception raised when step-up authentication is required"""
    message: str
    row_count: int

class ExportGuard:
    """
    Security guard for CSV exports to prevent data theft.
    
    Phase 9.2: Export Guard
    
    Features:
    - Watermarking: Adds hidden tracking column to exports
    - Rate limiting: Restricts export frequency per user
    - Tripwire: Requires re-authentication for large exports
    - Admin alerts: Notifies admins of suspicious exports
    - Audit logging: Complete export history
    
    Usage:
        guard = ExportGuard(user_id=current_user['id'], company_id=1)
        
        # Check if export allowed
        guard.check_rate_limit()
        
        # Check if step-up auth needed
        if guard.requires_step_up_auth(row_count):
            # Prompt user to re-enter password
            verify_password(password)
        
        # Add watermark and export
        data = guard.add_watermark(data, export_type='customers')
        guard.log_export('customers', len(data), file_size)
    """
    RATE_LIMIT_HOURS = 1
    STEP_UP_AUTH_THRESHOLD = 500
    ADMIN_ALERT_THRESHOLD = 1000

    def __init__(self, user_id: int, company_id: int=1, is_admin: bool=False, db_connection=None):
        """
        Initialize Export Guard.
        
        Args:
            user_id: User performing the export
            company_id: Company ID for multi-tenant isolation
            is_admin: Whether user is admin (bypasses rate limits)
            db_connection: Database connection (optional, will create if not provided)
        """
        self.user_id = user_id
        self.company_id = company_id
        self.is_admin = is_admin
        self._conn = db_connection
        self._ensure_tables_exist()

    def _get_connection(self):
        """Get database connection"""
        if self._conn is None:
            try:
                import db
                self._conn = db.get_connection()
            except ImportError:
                raise ImportError('Database module not available')
        return self._conn

    def _ensure_tables_exist(self):
        """Ensure export_log table exists"""
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute("\n                SELECT name FROM sqlite_master \n                WHERE type='table' AND name='export_log'\n            ")
            if not cursor.fetchone():
                migration_path = 'migrations/phase_9_2_export_guard.sql'
                try:
                    with open(migration_path, 'r') as f:
                        migration_sql = f.read()
                    cursor.executescript(migration_sql)
                    conn.commit()
                except FileNotFoundError:
                    cursor.execute('\n                        CREATE TABLE IF NOT EXISTS export_log (\n                            id INTEGER PRIMARY KEY AUTOINCREMENT,\n                            user_id INTEGER NOT NULL,\n                            table_name VARCHAR(50) NOT NULL,\n                            row_count INTEGER NOT NULL,\n                            export_id VARCHAR(100) NOT NULL UNIQUE,\n                            exported_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\n                            step_up_auth_used BOOLEAN DEFAULT 0,\n                            file_size_bytes INTEGER,\n                            ip_address VARCHAR(50),\n                            user_agent TEXT,\n                            FOREIGN KEY (user_id) REFERENCES users(id)\n                        )\n                    ')
                    cursor.execute('\n                        CREATE INDEX IF NOT EXISTS idx_export_log_user_time \n                        ON export_log(user_id, exported_at)\n                    ')
                    conn.commit()
        except Exception as e:
            print(f'Warning: Could not ensure export_log table exists: {e}')

    def generate_export_id(self, table_name: str=None) -> str:
        """
        Generate unique export ID for tracking.
        
        Args:
            table_name: Optional table name to include in ID
            
        Returns:
            Unique export ID (SHA256 hash)
        """
        timestamp = datetime.now().isoformat()
        data = f"{self.user_id}:{self.company_id}:{timestamp}:{table_name or ''}"
        return hashlib.sha256(data.encode()).hexdigest()[:32]

    def check_rate_limit(self) -> Tuple[bool, Optional[int]]:
        """
        Check if user has exceeded export rate limit.
        
        Returns:
            (allowed, retry_after_seconds) - (True, 0) if allowed, (False, seconds) if denied
        """
        if self.is_admin:
            return (True, 0)
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cutoff = datetime.now() - timedelta(hours=self.RATE_LIMIT_HOURS)
            cursor.execute('\n                SELECT exported_at FROM export_log\n                WHERE user_id = ?\n                AND exported_at > ?\n                ORDER BY exported_at DESC\n                LIMIT 1\n            ', (self.user_id, cutoff))
            row = cursor.fetchone()
            if row:
                last_export = datetime.fromisoformat(((((((((((((((row[0] if row else None) if row else None) if row else None) if row else None) if row else None) if row else None) if row else None) if row else None) if row else None) if row else None) if row else None) if row else None) if row else None) if row else None) if row else None)
                time_since_export = (datetime.now() - last_export).total_seconds()
                rate_limit_seconds = self.RATE_LIMIT_HOURS * 3600
                if time_since_export < rate_limit_seconds:
                    retry_after = int(rate_limit_seconds - time_since_export)
                    return (False, retry_after)
            return (True, 0)
        except Exception as e:
            print(f'Warning: Rate limit check failed: {e}')
            return (True, 0)

    def requires_step_up_auth(self, row_count: int) -> bool:
        """
        Check if export requires step-up authentication.
        
        Args:
            row_count: Number of rows being exported
            
        Returns:
            True if step-up auth required (re-enter password)
        """
        return row_count > self.STEP_UP_AUTH_THRESHOLD

    def requires_admin_alert(self, row_count: int) -> bool:
        """
        Check if export should trigger admin alert.
        
        Args:
            row_count: Number of rows being exported
            
        Returns:
            True if admin should be alerted
        """
        return row_count > self.ADMIN_ALERT_THRESHOLD

    def add_watermark(self, data: List[Dict], export_type: str='unknown') -> List[Dict]:
        """
        Add watermark column to export data.
        
        The watermark is a hidden column that tracks:
        - Who exported the data (user_id)
        - When it was exported (timestamp)
        - Unique export ID for tracking
        
        Args:
            data: List of dictionaries (rows to export)
            export_type: Type of data being exported
            
        Returns:
            Data with watermark column added
        """
        if not data:
            return data
        export_id = self.generate_export_id(export_type)
        timestamp = datetime.now().isoformat()
        watermark_value = f'{self.user_id}_{timestamp}_{export_id}'
        watermarked_data = []
        for row in data:
            row_copy = row.copy()
            row_copy['_watermark'] = watermark_value
            watermarked_data.append(row_copy)
        return watermarked_data

    def log_export(self, table_name: str, row_count: int, file_size_bytes: int=None, step_up_auth_used: bool=False, ip_address: str=None, user_agent: str=None) -> str:
        """
        Log export to audit trail.
        
        Args:
            table_name: Name of table/entity exported
            row_count: Number of rows exported
            file_size_bytes: Size of exported file (optional)
            step_up_auth_used: Whether step-up auth was used
            ip_address: IP address of user (optional)
            user_agent: User agent string (optional)
            
        Returns:
            Export ID for tracking
        """
        export_id = self.generate_export_id(table_name)
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('\n                INSERT INTO export_log \n                (user_id, table_name, row_count, export_id, exported_at,\n                 step_up_auth_used, file_size_bytes, ip_address, user_agent)\n                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)\n            ', (self.user_id, table_name, row_count, export_id, datetime.now(), step_up_auth_used, file_size_bytes, ip_address, user_agent))
            conn.commit()
            if self.requires_admin_alert(row_count):
                self._alert_admin_large_export(table_name, row_count, export_id)
            return export_id
        except Exception as e:
            print(f'Warning: Failed to log export: {e}')
            return export_id

    def _alert_admin_large_export(self, table_name: str, row_count: int, export_id: str):
        """
        Alert administrators of large export.
        
        Args:
            table_name: Table that was exported
            row_count: Number of rows
            export_id: Export ID for tracking
        """
        try:
            import db
            from services import send_email
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('\n                INSERT INTO audit_log \n                (user_id, company_id, action, entity_type, entity_id, details, created_at)\n                VALUES (?, ?, ?, ?, ?, ?, ?)\n            ', (self.user_id, self.company_id, 'LARGE_EXPORT_ALERT', 'export', export_id, f'User {self.user_id} exported {row_count} rows from {table_name}. Export ID: {export_id}', datetime.now()))
            conn.commit()
            user = db.get_user(self.user_id)
            company = db.get_company(self.company_id)
            with db.get_conn() as conn:
                cursor = conn.execute("\n                    SELECT DISTINCT u.id, u.username, u.email\n                    FROM users u\n                    JOIN user_company_roles ucr ON u.id = ucr.user_id\n                    WHERE ucr.company_id = ?\n                    AND ucr.role IN ('Admin', 'Architect')\n                    AND u.email IS NOT NULL\n                    AND u.email != ''\n                    AND u.is_active = 1\n                ", (self.company_id,))
                admins = [{'id': ((((((((((((((row[0] if row else None) if row else None) if row else None) if row else None) if row else None) if row else None) if row else None) if row else None) if row else None) if row else None) if row else None) if row else None) if row else None) if row else None) if row else None, 'username': row[1], 'email': row[2]} for row in cursor.fetchall()]
            if not admins or not user:
                print(f'🚨 ALERT: User {self.user_id} exported {row_count} rows from {table_name}')
                return
            subject = f'🚨 Large Data Export Alert: {row_count} records exported'
            user_username = user.get('username', 'Unknown') if user else 'Unknown'
            user_email = user.get('email', 'N/A') if user else 'N/A'
            company_name = company.get('name', 'Unknown Company') if company else 'Unknown Company'
            body = f"Large Data Export Detected\n\nCompany: {company_name}\nUser: {user_username} ({user_email})\nUser ID: {self.user_id}\n\nExport Details:\n- Table: {table_name}\n- Records: {row_count:,} rows\n- Export ID: {export_id}\n- Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\nThis export exceeded the threshold of {self.ADMIN_ALERT_THRESHOLD:,} rows and triggered an automatic security alert.\n\nAction Required:\nPlease verify this export was authorized. If this activity seems suspicious:\n1. Review the audit log for details\n2. Contact the user to verify the export purpose\n3. Check if the exported data contains sensitive information\n\nExport History:\nYou can view complete export history in the Admin Dashboard under Security > Export Logs.\n\n---\nThis is an automated security notification from your Landscaping Management System.\n"
            for admin in admins:
                try:
                    send_email(to_email=admin.get('email', 0), subject=subject, body=body, from_email='security-alerts@landscaping-app.com')
                    print(f"✅ Sent export alert email to {admin.get('username', 0)} ({admin.get('email', 0)})")
                except Exception as email_error:
                    print(f"⚠️  Failed to send email to {admin.get('email', 0)}: {email_error}")
            print(f'🚨 ALERT: User {self.user_id} exported {row_count} rows from {table_name} - {len(admins)} admins notified')
        except Exception as e:
            print(f'Warning: Failed to alert admins: {e}')

    def get_export_history(self, limit: int=100) -> List[Dict]:
        """
        Get export history for this user.
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of export records
        """
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('\n                SELECT id, table_name, row_count, export_id, exported_at,\n                       step_up_auth_used, file_size_bytes\n                FROM export_log\n                WHERE user_id = ?\n                ORDER BY exported_at DESC\n                LIMIT ?\n            ', (self.user_id, limit))
            exports = []
            for row in cursor.fetchall():
                exports.append({'id': ((((((((((((((row[0] if row else None) if row else None) if row else None) if row else None) if row else None) if row else None) if row else None) if row else None) if row else None) if row else None) if row else None) if row else None) if row else None) if row else None) if row else None, 'table_name': row[1], 'row_count': row[2], 'export_id': row[3], 'exported_at': row[4], 'step_up_auth_used': bool(row[5]), 'file_size_bytes': row[6]})
            return exports
        except Exception as e:
            print(f'Warning: Failed to get export history: {e}')
            return []

    def get_all_exports(self, limit: int=500) -> List[Dict]:
        """
        Get all exports across all users (admin only).
        
        Args:
            limit: Maximum number of records to return
            
        Returns:
            List of export records
        """
        if not self.is_admin:
            raise PermissionError('Only admins can view all exports')
        try:
            conn = self._get_connection()
            cursor = conn.cursor()
            cursor.execute('\n                SELECT el.id, el.user_id, u.name as user_name, el.table_name, \n                       el.row_count, el.export_id, el.exported_at,\n                       el.step_up_auth_used, el.file_size_bytes\n                FROM export_log el\n                LEFT JOIN users u ON el.user_id = u.id\n                ORDER BY el.exported_at DESC\n                LIMIT ?\n            ', (limit,))
            exports = []
            for row in cursor.fetchall():
                exports.append({'id': ((((((((((((((row[0] if row else None) if row else None) if row else None) if row else None) if row else None) if row else None) if row else None) if row else None) if row else None) if row else None) if row else None) if row else None) if row else None) if row else None) if row else None, 'user_id': row[1], 'user_name': row[2], 'table_name': row[3], 'row_count': row[4], 'export_id': row[5], 'exported_at': row[6], 'step_up_auth_used': bool(row[7]), 'file_size_bytes': row[8]})
            return exports
        except Exception as e:
            print(f'Warning: Failed to get all exports: {e}')
            return []

def check_export_allowed(user_id: int, is_admin: bool=False) -> Tuple[bool, Optional[str]]:
    """
    Check if user is allowed to export data.
    
    Args:
        user_id: User attempting export
        is_admin: Whether user is admin
        
    Returns:
        (allowed, error_message) - (True, None) if allowed, (False, msg) if denied
    """
    guard = ExportGuard(user_id=user_id, is_admin=is_admin)
    allowed, retry_after = guard.check_rate_limit()
    if not allowed:
        minutes = retry_after // 60
        return (False, f'Export rate limit exceeded. Try again in {minutes} minutes.')
    return (True, None)

def add_export_watermark(data: List[Dict], user_id: int, export_type: str='unknown') -> List[Dict]:
    """
    Add watermark to export data.
    
    Args:
        data: Data to watermark
        user_id: User performing export
        export_type: Type of export
        
    Returns:
        Watermarked data
    """
    guard = ExportGuard(user_id=user_id)
    return guard.add_watermark(data, export_type)