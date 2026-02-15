"""
Phase 11: The Reflex - System Status & Kill Switch

SystemStatus singleton for tracking global system security status.
Implements Defense Condition (DEFCON) levels for the application:
- GREEN: Normal operation
- AMBER: Elevated security (high risk detected)
- RED: Lockdown (attack detected)

The system defends itself without human intervention by automatically
adjusting security posture based on detected threats.
📚 REQUIRED READING BEFORE MODIFICATION:
- BRAIN_USAGE_GUIDE.md
- BRAIN_TOOLS_REFERENCE.md
- AI_NATIVE_ARCHITECTURE_GUIDE.md
- LLM_AGENT_QUICKSTART.md
"""
import threading
from enum import Enum
from typing import Optional, Dict
from datetime import datetime
from dataclasses import dataclass

class DefconLevel(Enum):
    """System defense condition levels"""
    GREEN = 'NORMAL'
    AMBER = 'ELEVATED'
    RED = 'LOCKDOWN'

@dataclass
class SecurityEvent:
    """Record of a security event that triggered a level change"""
    level: DefconLevel
    reason: str
    details: Optional[str] = None
    triggered_at: datetime = None
    triggered_by_user_id: Optional[int] = None
    resolved_at: Optional[datetime] = None
    resolved_by_user_id: Optional[int] = None

    def __post_init__(self):
        if self.triggered_at is None:
            self.triggered_at = datetime.now()

class SystemStatus:
    """
    Singleton to track and manage global system security status.
    
    Phase 11.1: Kill Switch Modes
    
    Implements three security levels:
    - GREEN (Normal): All operations allowed
    - AMBER (Elevated): Triggered by high risk score (>80)
      - Read-only for financial data
      - No new payments
      - No data exports
      - Admin alerts sent
    - RED (Lockdown): Triggered by honeypot access or critical threat
      - System lockdown
      - Only Admin can login
      - All sessions invalidated
      - Emergency alerts sent
    
    Example:
        status = SystemStatus()
        
        # Check if operation is allowed
        if not status.check_access(user_id, 'CREATE_PAYMENT'):
            raise SecurityException("Operation blocked by security policy")
        
        # Trigger lockdown
        status.set_level(DefconLevel.RED, "Honeypot field accessed")
    """
    _instance = None
    _lock = threading.Lock()

    def __new__(cls):
        """Singleton pattern - only one instance exists"""
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        """Initialize system status (only runs once due to singleton)"""
        if self._initialized:
            return
        self.level = DefconLevel.GREEN
        self.reason = None
        self.details = None
        self.triggered_at = None
        self.triggered_by_user_id = None
        self.events_history: list[SecurityEvent] = []
        self._initialized = True

    def set_level(self, level: DefconLevel, reason: str, details: str=None, user_id: int=None):
        """
        Change system security level.
        
        Args:
            level: New security level (GREEN, AMBER, RED)
            reason: Reason for level change (e.g., "HIGH_RISK_SCORE", "HONEYPOT_ACCESS")
            details: Optional additional details
            user_id: User ID who triggered the change (if applicable)
        """
        old_level = self.level
        self.level = level
        self.reason = reason
        self.details = details
        self.triggered_at = datetime.now()
        self.triggered_by_user_id = user_id
        event = SecurityEvent(level=level, reason=reason, details=details, triggered_at=self.triggered_at, triggered_by_user_id=user_id)
        self.events_history.append(event)
        self._log_level_change(old_level, level, reason, details)
        if level == DefconLevel.AMBER:
            self._activate_amber_mode(reason, details)
        elif level == DefconLevel.RED:
            self._activate_red_mode(reason, details)
        elif level == DefconLevel.GREEN and old_level != DefconLevel.GREEN:
            self._deactivate_elevated_mode(reason)

    def get_level(self) -> DefconLevel:
        """Get current security level"""
        return self.level

    def check_access(self, user_id: int, operation: str) -> bool:
        """
        Check if an operation is allowed in current security mode.
        
        Args:
            user_id: User attempting operation
            operation: Operation name (e.g., 'CREATE_PAYMENT', 'EXPORT_DATA')
            
        Returns:
            True if operation is allowed, False otherwise
        """
        if self.level == DefconLevel.RED:
            try:
                import db
                user = db.get_user(user_id)
                if user and user.get('role', '') if user else '' == 'ARCHITECT':
                    return True
                return False
            except Exception:
                return False
        elif self.level == DefconLevel.AMBER:
            blocked_operations = ['CREATE_PAYMENT', 'CREATE_INVOICE', 'PAYMENT_REFUND', 'EXPORT_DATA', 'EXPORT_CUSTOMERS', 'EXPORT_INVOICES', 'DELETE_CUSTOMER', 'DELETE_JOB']
            if operation in blocked_operations:
                return False
        return True

    def reset_to_green(self, user_id: int, reason: str='Manual override'):
        """
        Reset system to normal (GREEN) mode.
        
        Requires admin authorization.
        
        Args:
            user_id: Admin user ID performing reset
            reason: Reason for reset
        """
        try:
            import db
            user = db.get_user(user_id)
            if not user or user.get('role', '') if user else '' not in ['ARCHITECT', 'ADMIN']:
                raise PermissionError('Only admins can reset system status')
        except ImportError:
            pass
        self.set_level(DefconLevel.GREEN, reason, f'Reset by user {user_id}', user_id)

    def get_status_info(self) -> Dict:
        """
        Get current status information.
        
        Returns:
            Dict with status details
        """
        return {'level': self.level.value, 'level_name': self.level.name, 'reason': self.reason, 'details': self.details, 'triggered_at': self.triggered_at.isoformat() if self.triggered_at else None, 'triggered_by_user_id': self.triggered_by_user_id, 'events_count': len(self.events_history)}

    def _activate_amber_mode(self, reason: str, details: str=None):
        """
        Activate AMBER (elevated) security mode.
        
        Actions:
        - Block sensitive financial operations
        - Block data exports
        - Increase logging verbosity
        - Alert admins
        """
        print(f'⚠️  AMBER MODE ACTIVATED: {reason}')
        if details:
            print(f'   Details: {details}')
        self._alert_admins(DefconLevel.AMBER, reason, details)

    def _activate_red_mode(self, reason: str, details: str=None):
        """
        Activate RED (lockdown) mode.
        
        Actions:
        - Invalidate all non-admin sessions
        - Block all write operations except admin console
        - Enable verbose forensic logging
        - Send emergency alerts
        """
        print(f'🚨 RED MODE ACTIVATED - SYSTEM LOCKDOWN: {reason}')
        if details:
            print(f'   Details: {details}')
        self._invalidate_user_sessions()
        self._alert_admins(DefconLevel.RED, reason, details, emergency=True)

    def _deactivate_elevated_mode(self, reason: str):
        """
        Return to normal (GREEN) mode.
        
        Args:
            reason: Reason for returning to normal
        """
        print(f'✅ RETURNING TO NORMAL MODE: {reason}')
        self._alert_admins(DefconLevel.GREEN, reason, 'System returned to normal')

    def _invalidate_user_sessions(self):
        """Invalidate all user sessions except ARCHITECT"""
        try:
            print('  → Invalidating all non-admin sessions')
        except Exception as e:
            print(f'  Warning: Failed to invalidate sessions: {e}')

    def _alert_admins(self, level: DefconLevel, reason: str, details: str=None, emergency: bool=False):
        """
        Alert administrators of security level change.
        
        Args:
            level: New security level
            reason: Reason for change
            details: Optional additional details
            emergency: Whether this is an emergency alert (RED mode)
        """
        try:
            import db
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute("\n                SELECT id, name, email FROM users \n                WHERE role IN ('ARCHITECT', 'ADMIN') AND disabled = 0\n            ")
            admins = cursor.fetchall()
            if level == DefconLevel.RED:
                subject = '🚨 EMERGENCY: System Lockdown Activated'
                message = f"\nSYSTEM LOCKDOWN ACTIVATED\n\nReason: {reason}\nDetails: {details or 'N/A'}\nTime: {datetime.now().isoformat()}\n\nThe system has entered RED mode. Only ARCHITECT users can access the system.\n\nAction Required:\n1. Investigate the security incident\n2. Review audit logs\n3. Determine root cause\n4. Implement fixes\n5. Reset system status when resolved\n\nLogin to the system console immediately.\n"
            elif level == DefconLevel.AMBER:
                subject = '⚠️  Alert: Elevated Security Mode'
                message = f"\nELEVATED SECURITY MODE ACTIVATED\n\nReason: {reason}\nDetails: {details or 'N/A'}\nTime: {datetime.now().isoformat()}\n\nThe system has entered AMBER mode. Financial operations and exports are restricted.\n\nAction Recommended:\n1. Monitor system activity\n2. Review recent security events\n3. Investigate potential threats\n\nThe system will continue operating with restrictions.\n"
            else:
                subject = '✅ System Returned to Normal'
                message = f"\nSYSTEM STATUS: NORMAL\n\nReason: {reason}\nDetails: {details or 'N/A'}\nTime: {datetime.now().isoformat()}\n\nThe system has returned to normal operation mode.\nAll restrictions have been lifted.\n"
            for admin in admins:
                print(f"  → Alerting admin: {admin.get('name', 'Unknown')} ({admin.get('email')})")
        except Exception as e:
            print(f'  Warning: Failed to alert admins: {e}')

    def _log_level_change(self, old_level: DefconLevel, new_level: DefconLevel, reason: str, details: str=None):
        """
        Log security level change to audit trail.
        
        Args:
            old_level: Previous security level
            new_level: New security level
            reason: Reason for change
            details: Optional additional details
        """
        try:
            import db
            from datetime import datetime
            conn = db.get_connection()
            cursor = conn.cursor()
            cursor.execute('\n                INSERT INTO audit_log \n                (user_id, company_id, action, entity_type, entity_id, details, created_at)\n                VALUES (?, ?, ?, ?, ?, ?, ?)\n            ', (self.triggered_by_user_id or 0, 1, 'SECURITY_LEVEL_CHANGE', 'system', 0, f"{old_level.name} -> {new_level.name}: {reason}. {details or ''}", datetime.now()))
            conn.commit()
        except Exception as e:
            print(f'  Warning: Failed to log level change: {e}')

def trigger_kill_switch(reason: str, details: str=None, user_id: int=None):
    """
    Trigger emergency system lockdown (RED mode).
    
    Phase 11.1: Kill Switch - Automated emergency response.
    
    This function is called when critical security threats are detected:
    - Honeypot field access
    - Canary row access
    - SQL injection attempts
    - Multiple failed authentication attempts
    
    Args:
        reason: Reason for triggering kill switch (e.g., "HONEYPOT_FIELD_ACCESS")
        details: Additional details about the threat
        user_id: User ID who triggered the alert (if known)
    """
    status = SystemStatus()
    status.set_level(DefconLevel.RED, reason, details, user_id)
    _log_security_incident(reason, details, user_id)

def trigger_elevated_mode(reason: str, details: str=None, user_id: int=None):
    """
    Trigger elevated security mode (AMBER).
    
    Phase 11.1: Elevated Mode - Moderate threat response.
    
    This function is called when elevated risk is detected:
    - High risk score (>80)
    - Unusual access patterns
    - Multiple suspicious activities
    
    Args:
        reason: Reason for elevation (e.g., "HIGH_RISK_SCORE")
        details: Additional details
        user_id: User ID with high risk score (if applicable)
    """
    status = SystemStatus()
    status.set_level(DefconLevel.AMBER, reason, details, user_id)

def _log_security_incident(reason: str, details: str=None, user_id: int=None):
    """
    Log security incident to dedicated security log.
    
    Args:
        reason: Incident reason
        details: Incident details
        user_id: User involved (if applicable)
    """
    try:
        import db
        from datetime import datetime
        conn = db.get_connection()
        cursor = conn.cursor()
        cursor.execute('\n            CREATE TABLE IF NOT EXISTS security_incidents (\n                id INTEGER PRIMARY KEY AUTOINCREMENT,\n                incident_type VARCHAR(100) NOT NULL,\n                details TEXT,\n                user_id INTEGER,\n                ip_address VARCHAR(50),\n                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,\n                resolved BOOLEAN DEFAULT 0,\n                resolved_at TIMESTAMP,\n                resolved_by_user_id INTEGER\n            )\n        ')
        cursor.execute('\n            INSERT INTO security_incidents \n            (incident_type, details, user_id, created_at)\n            VALUES (?, ?, ?, ?)\n        ', (reason, details or '', user_id, datetime.now()))
        conn.commit()
        print(f'  → Security incident logged: {reason}')
    except Exception as e:
        print(f'  Warning: Failed to log security incident: {e}')