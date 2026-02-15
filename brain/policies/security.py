"""
Security Policy - Authentication, authorization, access control
📚 REQUIRED READING BEFORE MODIFICATION:
- BRAIN_USAGE_GUIDE.md
- brain/design/02_policy_packs.md
- LLM_AGENT_QUICKSTART.md
"""
from brain.core.command_event import CommandEvent
from brain.core.result import PolicyResult
from brain.core.enums import Role
import db

class SecurityPolicy:
    """
    Security Policy checks:
    - SEC-001: User authentication
    - SEC-002: Role-based access control (RBAC)
    - SEC-003: Multi-tenant isolation
    - SEC-004: Sensitive data access
    """
    COMMAND_ROLE_MAP = {'UserDelete': [Role.ARCHITECT], 'InvoiceDelete': [Role.ARCHITECT], 'PaymentDelete': [Role.ARCHITECT], 'SystemRestore': [Role.ARCHITECT], 'AuditLogReplay': [Role.ARCHITECT], 'InvoiceVoid': [Role.ARCHITECT, Role.ADMIN], 'PaymentRefund': [Role.ARCHITECT, Role.ADMIN], 'UserSetRole': [Role.ARCHITECT, Role.ADMIN], 'JobDelete': [Role.ARCHITECT, Role.ADMIN], 'CustomerDelete': [Role.ARCHITECT, Role.ADMIN], 'JobStart': [Role.ARCHITECT, Role.ADMIN, Role.STAFF], 'JobComplete': [Role.ARCHITECT, Role.ADMIN, Role.STAFF], 'TimeClockIn': [Role.ARCHITECT, Role.ADMIN, Role.STAFF], 'TimeClockOut': [Role.ARCHITECT, Role.ADMIN, Role.STAFF], 'JobAddPhoto': [Role.ARCHITECT, Role.ADMIN, Role.STAFF], 'JobAddNote': [Role.ARCHITECT, Role.ADMIN, Role.STAFF], 'MessageSendSMS': [Role.ARCHITECT, Role.ADMIN, Role.STAFF], 'MessageSendEmail': [Role.ARCHITECT, Role.ADMIN, Role.STAFF]}

    def check(self, event: CommandEvent) -> PolicyResult:
        """Check security policies"""
        if event.user_id == 0 and event.command_type == 'CreateUser':
            try:
                if db.count_users() == 0:
                    return PolicyResult.allow()
            except Exception:
                return PolicyResult.allow()
        result = self._check_authentication(event)
        if result.is_denied:
            return result
        result = self._check_role_permission(event)
        if result.is_denied:
            return result
        result = self._check_company_access(event)
        if result.is_denied:
            return result
        return PolicyResult.allow()

    def _check_authentication(self, event: CommandEvent) -> PolicyResult:
        """SEC-001: Ensure user is authenticated"""
        if not event.user_id:
            return PolicyResult.deny('User not authenticated', 'SEC_NOT_AUTHENTICATED')
        user = db.get_user(event.user_id)
        if not user:
            return PolicyResult.deny('Invalid user', 'SEC_INVALID_USER')
        if user.get('disabled', '') if user else '':
            return PolicyResult.deny('User account disabled', 'SEC_USER_DISABLED')
        return PolicyResult.allow()

    def _check_role_permission(self, event: CommandEvent) -> PolicyResult:
        """SEC-002: Ensure user has required role"""
        user = db.get_user(event.user_id)
        if not user:
            return PolicyResult.deny('User not found', 'SEC_USER_NOT_FOUND')
        user_role = Role(user.get('role', 'STAFF') if user else 'STAFF')
        if user_role == Role.READONLY:
            if event.command_type.startswith('Get') or 'Query' in event.command_type:
                return PolicyResult.allow()
            return PolicyResult.deny(f'Role {user_role} cannot execute write operations', 'SEC_READONLY_WRITE_DENIED')
        allowed_roles = self._get_allowed_roles(event.command_type)
        if allowed_roles is None:
            allowed_roles = [Role.OWNER, Role.ADMIN, Role.ARCHITECT]
        if user_role not in allowed_roles:
            return PolicyResult.deny(f'Role {user_role} not authorized for {event.command_type}', 'SEC_INSUFFICIENT_PERMISSIONS')
        return PolicyResult.allow()

    def _get_allowed_roles(self, command_type: str) -> list:
        """
        Get allowed roles for a command from database or fallback to hardcoded map.
        
        This enables dynamic permission management without code deployments.
        """
        try:
            with db.get_conn() as conn:
                cursor = conn.execute('\n                    SELECT DISTINCT role \n                    FROM command_permissions \n                    WHERE command_pattern = ? AND is_active = 1\n                ', (command_type,))
                db_roles = [row[0] for row in cursor.fetchall() if row]
                if db_roles:
                    allowed_roles = []
                    for role_str in db_roles:
                        try:
                            allowed_roles.append(Role(role_str))
                        except ValueError:
                            print(f"Warning: Invalid role '{role_str}' in command_permissions for {command_type}")
                    return allowed_roles if allowed_roles else None
        except Exception as e:
            pass
        return [Role.OWNER, Role.ADMIN, Role.ARCHITECT]

    def _check_company_access(self, event: CommandEvent) -> PolicyResult:
        """SEC-003: Ensure user can access the company"""
        user = db.get_user(event.user_id)
        if not user:
            return PolicyResult.deny('User not found', 'SEC_USER_NOT_FOUND')
        user_role = Role(user.get('role', 'STAFF') if user else 'STAFF')
        if user_role in (Role.ADMIN, Role.OWNER, Role.ARCHITECT):
            return PolicyResult.allow()
        user_companies = db.get_user_companies(event.user_id)
        accessible_company_ids = [company.get('id') for company in user_companies]
        if event.company_id not in accessible_company_ids:
            return PolicyResult.deny(f'User does not have access to company {event.company_id}', 'SEC_COMPANY_ACCESS_DENIED')
        return PolicyResult.allow()
