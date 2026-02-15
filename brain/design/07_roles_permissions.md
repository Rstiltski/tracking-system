# Roles & Permissions (RBAC)

**Rule:** Do not use scripts to edit code.

**Version:** 1.0
**Status:** Draft
**Last Updated:** 2026-01-01

## Overview

The system uses **Role-Based Access Control (RBAC)** to manage permissions. Each user is assigned a role, and each role has specific permissions.

## Role Hierarchy

```
Architect (God Mode)
    └─ Admin (Business Owner)
        └─ Staff (Crew/Field Worker)
            └─ ReadOnly (Viewer/Accountant)
```

**Inheritance:** Higher roles inherit all permissions from lower roles.

---

## Roles

### 1. Architect (God Mode)

**Purpose:** System administrator with unrestricted access.

**Typical Users:**
- System developers
- Technical support
- Emergency access

**Permissions:**
- ✅ All commands
- ✅ Delete any entity
- ✅ Void invoices
- ✅ Restore from backup
- ✅ Replay audit logs
- ✅ Modify system settings
- ✅ Create/delete users
- ✅ Change user roles
- ✅ Access audit logs
- ✅ Override policies

**Restrictions:**
- None (unrestricted access)

**Special Powers:**
- Can execute commands even if policies fail
- Can override confirmation gates
- Can access all companies (multi-tenant bypass)

---

### 2. Admin (Business Owner)

**Purpose:** Business owner or manager with full operational control.

**Typical Users:**
- Business owner
- Office manager
- Senior administrator

**Permissions:**
- ✅ All job operations (create, update, schedule, complete, cancel)
- ✅ All customer operations (create, update, merge, mark VIP)
- ✅ All financial operations (create invoices, record payments, create quotes)
- ✅ Send communications (SMS, email, bulk)
- ✅ Create/update materials and suppliers
- ✅ Manage crew (assign, update availability)
- ✅ Approve timesheets
- ✅ Record expenses
- ✅ Generate reports
- ✅ Update company settings
- ✅ Create/disable users (Staff and ReadOnly only)
- ✅ View audit logs

**Restrictions:**
- ❌ Cannot delete users
- ❌ Cannot change Architect or Admin roles
- ❌ Cannot restore from backup
- ❌ Cannot replay audit logs
- ❌ Cannot override system policies

**Financial Powers:**
- ✅ Void invoices (with reason)
- ✅ Process refunds (with reason)
- ✅ Create credit notes

---

### 3. Staff (Crew/Field Worker)

**Purpose:** Front-line workers doing jobs and basic admin.

**Typical Users:**
- Gardeners
- Landscapers
- Junior admin staff

**Permissions:**
- ✅ View jobs assigned to them
- ✅ Update job status (start, pause, resume, complete)
- ✅ Add job photos and notes
- ✅ Clock in/out (time tracking)
- ✅ Record materials used
- ✅ Submit timesheets
- ✅ View customers (read-only)
- ✅ View own work logs
- ✅ Create expenses (for approval)
- ✅ Send individual SMS/email to customers
- ✅ View calendar (own jobs)

**Restrictions:**
- ❌ Cannot create/delete jobs
- ❌ Cannot create/delete customers
- ❌ Cannot create invoices
- ❌ Cannot record payments
- ❌ Cannot send quotes
- ❌ Cannot send bulk messages
- ❌ Cannot access financial reports
- ❌ Cannot manage users
- ❌ Cannot update system settings
- ❌ Cannot approve timesheets
- ❌ Cannot view audit logs

**Special Constraints:**
- Can only view/update jobs assigned to them (row-level security)
- Cannot see other staff members' timesheets
- Cannot modify completed jobs

---

### 4. ReadOnly (Viewer/Accountant)

**Purpose:** View-only access for accountants, auditors, or stakeholders.

**Typical Users:**
- External accountant
- Bookkeeper
- Auditor
- Investor/stakeholder

**Permissions:**
- ✅ View all jobs
- ✅ View all customers
- ✅ View all invoices
- ✅ View all payments
- ✅ View all quotes
- ✅ View all expenses
- ✅ View financial reports
- ✅ View timesheets
- ✅ View calendar
- ✅ Export data (CSV, PDF)

**Restrictions:**
- ❌ Cannot execute ANY commands (read-only)
- ❌ Cannot create/update/delete anything
- ❌ Cannot send communications
- ❌ Cannot approve timesheets
- ❌ Cannot record payments
- ❌ Cannot manage users
- ❌ Cannot view audit logs

**Special Constraints:**
- All write operations blocked
- Can only query data

---

## Permission Matrix

### Job Operations

| Command | Architect | Admin | Staff | ReadOnly |
|---------|-----------|-------|-------|----------|
| `JobCreate` | ✅ | ✅ | ❌ | ❌ |
| `JobUpdate` | ✅ | ✅ | ⚠️* | ❌ |
| `JobDelete` | ✅ | ✅ | ❌ | ❌ |
| `JobQuote` | ✅ | ✅ | ❌ | ❌ |
| `JobBook` | ✅ | ✅ | ❌ | ❌ |
| `JobSchedule` | ✅ | ✅ | ❌ | ❌ |
| `JobStart` | ✅ | ✅ | ✅ | ❌ |
| `JobComplete` | ✅ | ✅ | ✅ | ❌ |
| `JobCancel` | ✅ | ✅ | ❌ | ❌ |
| `JobAddPhoto` | ✅ | ✅ | ✅ | ❌ |
| `JobAddNote` | ✅ | ✅ | ✅ | ❌ |
| `GetJob` | ✅ | ✅ | ⚠️* | ✅ |

*Staff can only update/view jobs assigned to them

---

### Customer Operations

| Command | Architect | Admin | Staff | ReadOnly |
|---------|-----------|-------|-------|----------|
| `CustomerCreate` | ✅ | ✅ | ❌ | ❌ |
| `CustomerUpdate` | ✅ | ✅ | ❌ | ❌ |
| `CustomerDelete` | ✅ | ✅ | ❌ | ❌ |
| `CustomerMerge` | ✅ | ✅ | ❌ | ❌ |
| `CustomerAddNote` | ✅ | ✅ | ✅ | ❌ |
| `CustomerSetVIP` | ✅ | ✅ | ❌ | ❌ |
| `GetCustomer` | ✅ | ✅ | ✅ | ✅ |

---

### Financial Operations

| Command | Architect | Admin | Staff | ReadOnly |
|---------|-----------|-------|-------|----------|
| `InvoiceCreate` | ✅ | ✅ | ❌ | ❌ |
| `InvoiceSend` | ✅ | ✅ | ❌ | ❌ |
| `InvoiceVoid` | ✅ | ✅ | ❌ | ❌ |
| `InvoiceDelete` | ✅ | ❌ | ❌ | ❌ |
| `PaymentRecord` | ✅ | ✅ | ❌ | ❌ |
| `PaymentRefund` | ✅ | ✅ | ❌ | ❌ |
| `PaymentDelete` | ✅ | ❌ | ❌ | ❌ |
| `QuoteCreate` | ✅ | ✅ | ❌ | ❌ |
| `QuoteSend` | ✅ | ✅ | ❌ | ❌ |
| `ExpenseCreate` | ✅ | ✅ | ✅ | ❌ |
| `GetInvoice` | ✅ | ✅ | ❌ | ✅ |
| `GetPayment` | ✅ | ✅ | ❌ | ✅ |

---

### Communication Operations

| Command | Architect | Admin | Staff | ReadOnly |
|---------|-----------|-------|-------|----------|
| `MessageSendSMS` | ✅ | ✅ | ✅ | ❌ |
| `MessageSendEmail` | ✅ | ✅ | ✅ | ❌ |
| `MessageSendBulkSMS` | ✅ | ✅ | ❌ | ❌ |
| `MessageSendBulkEmail` | ✅ | ✅ | ❌ | ❌ |
| `MessageSchedule` | ✅ | ✅ | ❌ | ❌ |

---

### Time Tracking

| Command | Architect | Admin | Staff | ReadOnly |
|---------|-----------|-------|-------|----------|
| `TimeClockIn` | ✅ | ✅ | ✅ | ❌ |
| `TimeClockOut` | ✅ | ✅ | ✅ | ❌ |
| `TimeStartBreak` | ✅ | ✅ | ✅ | ❌ |
| `TimeEndBreak` | ✅ | ✅ | ✅ | ❌ |
| `TimesheetSubmit` | ✅ | ✅ | ✅ | ❌ |
| `TimesheetApprove` | ✅ | ✅ | ❌ | ❌ |
| `TimesheetReject` | ✅ | ✅ | ❌ | ❌ |

---

### User Management

| Command | Architect | Admin | Staff | ReadOnly |
|---------|-----------|-------|-------|----------|
| `UserCreate` | ✅ | ⚠️* | ❌ | ❌ |
| `UserUpdate` | ✅ | ⚠️* | ❌ | ❌ |
| `UserDelete` | ✅ | ❌ | ❌ | ❌ |
| `UserSetRole` | ✅ | ⚠️* | ❌ | ❌ |
| `UserDisable` | ✅ | ⚠️* | ❌ | ❌ |
| `UserResetPassword` | ✅ | ⚠️* | ❌ | ❌ |

*Admin can only manage Staff and ReadOnly users, not other Admins or Architects

---

### System Operations

| Command | Architect | Admin | Staff | ReadOnly |
|---------|-----------|-------|-------|----------|
| `SettingsUpdate` | ✅ | ⚠️* | ❌ | ❌ |
| `CompanyUpdate` | ✅ | ✅ | ❌ | ❌ |
| `AuditLogQuery` | ✅ | ✅ | ❌ | ❌ |
| `AuditLogReplay` | ✅ | ❌ | ❌ | ❌ |
| `SystemBackup` | ✅ | ❌ | ❌ | ❌ |
| `SystemRestore` | ✅ | ❌ | ❌ | ❌ |

*Admin can only update non-critical settings

---

## Row-Level Security (RLS)

**Staff users** have row-level security applied:

### Jobs
```python
def filter_jobs_for_staff(user_id: int, jobs: list) -> list:
    """Staff can only see jobs assigned to them"""
    return [
        job for job in jobs
        if user_id in job.assigned_crew_ids
    ]
```

### Time Entries
```python
def filter_time_entries_for_staff(user_id: int, entries: list) -> list:
    """Staff can only see their own time entries"""
    return [
        entry for entry in entries
        if entry.user_id == user_id
    ]
```

### Expenses
```python
def filter_expenses_for_staff(user_id: int, expenses: list) -> list:
    """Staff can only see expenses they created"""
    return [
        expense for expense in expenses
        if expense.created_by == user_id
    ]
```

---

## Permission Enforcement

### Implementation

```python
class PermissionChecker:
    """Checks if user has permission to execute command"""

    COMMAND_ROLE_MAP = {
        # Architect-only
        "UserDelete": [Role.ARCHITECT],
        "InvoiceDelete": [Role.ARCHITECT],
        "PaymentDelete": [Role.ARCHITECT],
        "SystemRestore": [Role.ARCHITECT],
        "AuditLogReplay": [Role.ARCHITECT],

        # Architect + Admin
        "InvoiceVoid": [Role.ARCHITECT, Role.ADMIN],
        "PaymentRefund": [Role.ARCHITECT, Role.ADMIN],
        "UserSetRole": [Role.ARCHITECT, Role.ADMIN],
        "JobDelete": [Role.ARCHITECT, Role.ADMIN],
        "CustomerDelete": [Role.ARCHITECT, Role.ADMIN],

        # Architect + Admin + Staff
        "JobStart": [Role.ARCHITECT, Role.ADMIN, Role.STAFF],
        "JobComplete": [Role.ARCHITECT, Role.ADMIN, Role.STAFF],
        "TimeClockIn": [Role.ARCHITECT, Role.ADMIN, Role.STAFF],
        "TimeClockOut": [Role.ARCHITECT, Role.ADMIN, Role.STAFF],
        "JobAddPhoto": [Role.ARCHITECT, Role.ADMIN, Role.STAFF],
        "JobAddNote": [Role.ARCHITECT, Role.ADMIN, Role.STAFF],
        "MessageSendSMS": [Role.ARCHITECT, Role.ADMIN, Role.STAFF],
        "MessageSendEmail": [Role.ARCHITECT, Role.ADMIN, Role.STAFF],

        # Default: Architect + Admin
        # (All other commands)
    }

    def check_permission(self, user: User, command_type: str) -> bool:
        """Check if user has permission to execute command"""

        # ReadOnly role blocked from all write operations
        if user.role == Role.READONLY:
            if command_type.startswith("Get") or command_type.endswith("Query"):
                return True
            return False

        # Get allowed roles for command
        allowed_roles = self.COMMAND_ROLE_MAP.get(command_type)

        # If not in map, default to Admin and above
        if allowed_roles is None:
            allowed_roles = [Role.ARCHITECT, Role.ADMIN]

        # Check if user's role is allowed
        return user.role in allowed_roles

    def check_row_level_access(
        self,
        user: User,
        entity_type: str,
        entity_id: int
    ) -> bool:
        """Check if user can access specific entity"""

        # Architect and Admin can access everything
        if user.role in [Role.ARCHITECT, Role.ADMIN]:
            return True

        # ReadOnly can view everything
        if user.role == Role.READONLY:
            return True

        # Staff: Check row-level permissions
        if user.role == Role.STAFF:
            if entity_type == "job":
                job = get_job(entity_id)
                return user.id in job.assigned_crew_ids

            if entity_type == "time_entry":
                entry = get_time_entry(entity_id)
                return entry.user_id == user.id

            if entity_type == "expense":
                expense = get_expense(entity_id)
                return expense.created_by == user.id

            # Other entities: no access
            return False

        return False
```

---

## Permission Errors

### Error Codes

| Error Code | Description |
|------------|-------------|
| `SEC_NOT_AUTHENTICATED` | User not logged in |
| `SEC_INSUFFICIENT_PERMISSIONS` | User role doesn't have permission |
| `SEC_ROW_LEVEL_DENIED` | User doesn't have access to specific entity |
| `SEC_COMPANY_ACCESS_DENIED` | User doesn't belong to company |
| `SEC_SENSITIVE_ACCESS_DENIED` | Sensitive operation requires higher role |

### Error Responses

```python
# Permission denied
{
    "success": False,
    "error_code": "SEC_INSUFFICIENT_PERMISSIONS",
    "error_message": "Role STAFF not authorized for InvoiceCreate",
    "required_role": "ADMIN",
    "user_role": "STAFF"
}
```

```python
# Row-level denied
{
    "success": False,
    "error_code": "SEC_ROW_LEVEL_DENIED",
    "error_message": "You do not have access to Job #123",
    "entity_type": "job",
    "entity_id": 123
}
```

---

## Default Role Assignment

**New users are assigned roles based on context:**

| User Type | Default Role | Auto-Assigned |
|-----------|--------------|---------------|
| First user in company | Architect | ✅ Yes |
| Invited by Architect | Admin | ❌ No (manual) |
| Invited by Admin | Staff | ✅ Yes |
| Portal customer | ReadOnly | ✅ Yes |

---

## Role Transition Rules

### Allowed Transitions

| From | To | Who Can Do It |
|------|-----|---------------|
| Staff → Admin | Architect or Admin | Promotion |
| Staff → ReadOnly | Architect or Admin | Demotion |
| Admin → Staff | Architect only | Demotion |
| Admin → Architect | Architect only | Promotion |
| ReadOnly → Staff | Architect or Admin | Promotion |
| * → Architect | Architect only | Rare (should be avoided) |

### Forbidden Transitions

- ❌ Admin cannot change another Admin's role
- ❌ Staff cannot change any roles
- ❌ Cannot change own role
- ❌ Cannot demote the last Architect in company

---

## Multi-Tenant Isolation

**Company-level isolation:**

```python
def enforce_company_isolation(user: User, command: CommandEvent) -> bool:
    """Ensure user can only access their own company's data"""

    # Architect can bypass (for support)
    if user.role == Role.ARCHITECT and user.is_system_admin:
        return True

    # Check user has access to company
    if command.company_id not in user.company_ids:
        raise PermissionError(
            f"User does not have access to company {command.company_id}"
        )

    return True
```

---

## Next Steps

1. ✅ Define roles and permissions
2. ⏳ Implement permission checker (Phase 1)
3. ⏳ Implement row-level security (Phase 1)
4. ⏳ Add role management UI (Phase 4)
5. ⏳ Create permission tests (Phase 1)

---

**Status:** ✅ Approved - RBAC system with dynamic permissions operational
**Reviewer:** Development Team
**Approved:** ✅ 2026-01-06 (39 permissions seeded, database-driven RBAC active)
