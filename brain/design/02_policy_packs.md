# Policy Packs v1

**Rule:** Do not use scripts to edit code.

**Version:** 1.0
**Status:** Draft
**Last Updated:** 2026-01-01

## Overview

**Policy Packs** are collections of validation rules that run **before** a command is executed. They enforce business rules, prevent invalid operations, and maintain system integrity.

## Policy Execution Order

```
CommandEvent → Router
                 ↓
              Policies (run in order)
                 ├─ Security Policy (authentication, authorization)
                 ├─ Integrity Policy (data consistency, business rules)
                 ├─ Scheduling Policy (conflicts, availability)
                 └─ Comms Policy (rate limits, deduplication)
                 ↓
              State Machine (if applicable)
                 ↓
              Planner → Tools
```

## Policy Packs

1. [Security Policy](#1-security-policy)
2. [Integrity Policy](#2-integrity-policy)
3. [Scheduling Policy](#3-scheduling-policy)
4. [Comms Policy](#4-comms-policy)

---

## 1. Security Policy

**Purpose:** Ensure authentication, authorization, and access control.

### Rules

#### SEC-001: User Authentication

**Applies to:** All commands

**Rule:**
```python
def check_authentication(event: CommandEvent) -> PolicyResult:
    """Ensure user is authenticated"""
    if not event.user_id:
        return PolicyResult.DENY("User not authenticated")

    user = get_user(event.user_id)
    if not user or user.disabled:
        return PolicyResult.DENY("Invalid or disabled user")

    return PolicyResult.ALLOW
```

**Error Code:** `SEC_NOT_AUTHENTICATED`

---

#### SEC-002: Role-Based Access Control (RBAC)

**Applies to:** All commands

**Rule:**
```python
COMMAND_ROLE_MAP = {
    # Admin-only commands
    "UserDelete": [Role.ARCHITECT, Role.ADMIN],
    "UserSetRole": [Role.ARCHITECT, Role.ADMIN],
    "InvoiceVoid": [Role.ARCHITECT, Role.ADMIN],
    "PaymentRefund": [Role.ARCHITECT, Role.ADMIN],
    "SystemRestore": [Role.ARCHITECT],

    # Admin + Staff commands
    "JobCreate": [Role.ARCHITECT, Role.ADMIN, Role.STAFF],
    "JobUpdate": [Role.ARCHITECT, Role.ADMIN, Role.STAFF],
    "InvoiceCreate": [Role.ARCHITECT, Role.ADMIN, Role.STAFF],
    "PaymentRecord": [Role.ARCHITECT, Role.ADMIN, Role.STAFF],

    # Read-only cannot execute most commands
    # (only query operations allowed)
}

def check_role_permission(event: CommandEvent) -> PolicyResult:
    """Ensure user has required role"""
    allowed_roles = COMMAND_ROLE_MAP.get(event.command_type, [])

    if not allowed_roles:
        # Default: STAFF and above
        allowed_roles = [Role.ARCHITECT, Role.ADMIN, Role.STAFF]

    user = get_user(event.user_id)
    if user.role not in allowed_roles:
        return PolicyResult.DENY(
            f"Role {user.role} not authorized for {event.command_type}"
        )

    return PolicyResult.ALLOW
```

**Error Code:** `SEC_INSUFFICIENT_PERMISSIONS`

---

#### SEC-003: Multi-Tenant Isolation

**Applies to:** All commands

**Rule:**
```python
def check_company_access(event: CommandEvent) -> PolicyResult:
    """Ensure user can access the company"""
    user = get_user(event.user_id)

    if event.company_id not in user.company_ids:
        return PolicyResult.DENY(
            f"User does not have access to company {event.company_id}"
        )

    return PolicyResult.ALLOW
```

**Error Code:** `SEC_COMPANY_ACCESS_DENIED`

---

#### SEC-004: Sensitive Data Access

**Applies to:** Commands accessing customer payment details, passwords

**Rule:**
```python
SENSITIVE_COMMANDS = [
    "UserResetPassword",
    "PaymentRecord",
    "PaymentRefund",
    "CustomerUpdate",  # if updating payment details
]

def check_sensitive_access(event: CommandEvent) -> PolicyResult:
    """Require elevated permissions for sensitive data"""
    if event.command_type not in SENSITIVE_COMMANDS:
        return PolicyResult.ALLOW

    user = get_user(event.user_id)

    # Require Admin or Architect for sensitive ops
    if user.role not in [Role.ARCHITECT, Role.ADMIN]:
        return PolicyResult.DENY(
            "Sensitive operation requires Admin role"
        )

    return PolicyResult.ALLOW
```

**Error Code:** `SEC_SENSITIVE_ACCESS_DENIED`

---

## 2. Integrity Policy

**Purpose:** Enforce business rules and data consistency.

### Rules

#### INT-001: Entity Existence

**Applies to:** Commands referencing jobs, customers, invoices, etc.

**Rule:**
```python
def check_entity_exists(event: CommandEvent) -> PolicyResult:
    """Ensure referenced entities exist"""

    # Job commands
    if "Job" in event.command_type:
        if job_id := event.params.get("job_id"):
            if not job_exists(job_id):
                return PolicyResult.DENY(f"Job {job_id} does not exist")

    # Customer commands
    if "Customer" in event.command_type:
        if customer_id := event.params.get("customer_id"):
            if not customer_exists(customer_id):
                return PolicyResult.DENY(f"Customer {customer_id} does not exist")

    # Invoice commands
    if "Invoice" in event.command_type:
        if invoice_id := event.params.get("invoice_id"):
            if not invoice_exists(invoice_id):
                return PolicyResult.DENY(f"Invoice {invoice_id} does not exist")

    return PolicyResult.ALLOW
```

**Error Code:** `INT_ENTITY_NOT_FOUND`

---

#### INT-002: Required Fields

**Applies to:** Create commands

**Rule:**
```python
REQUIRED_FIELDS = {
    "JobCreate": ["customer_id", "title", "job_type"],
    "CustomerCreate": ["name", "phone"],
    "InvoiceCreate": ["job_id", "invoice_no", "total"],
    "PaymentRecord": ["invoice_id", "amount", "payment_method"],
    "QuoteCreate": ["job_id", "quoted_price"],
}

def check_required_fields(event: CommandEvent) -> PolicyResult:
    """Ensure all required fields are present"""
    required = REQUIRED_FIELDS.get(event.command_type, [])

    for field in required:
        if field not in event.params or event.params[field] is None:
            return PolicyResult.DENY(f"Required field missing: {field}")

    return PolicyResult.ALLOW
```

**Error Code:** `INT_MISSING_REQUIRED_FIELD`

---

#### INT-003: Field Validation

**Applies to:** All commands with validated fields

**Rule:**
```python
def check_field_validation(event: CommandEvent) -> PolicyResult:
    """Validate field formats and ranges"""

    # Email validation
    if email := event.params.get("email"):
        if not is_valid_email(email):
            return PolicyResult.DENY(f"Invalid email: {email}")

    # Phone validation
    if phone := event.params.get("phone"):
        if not is_valid_phone(phone):
            return PolicyResult.DENY(f"Invalid phone: {phone}")

    # Amount validation
    if amount := event.params.get("amount"):
        if amount <= 0:
            return PolicyResult.DENY("Amount must be positive")

    # Date validation
    if job_date := event.params.get("job_date"):
        if job_date < today():
            return PolicyResult.DENY("Job date cannot be in the past")

    return PolicyResult.ALLOW
```

**Error Code:** `INT_INVALID_FIELD_VALUE`

---

#### INT-004: Money Consistency

**Applies to:** Financial commands

**Rule:**
```python
def check_money_consistency(event: CommandEvent) -> PolicyResult:
    """Ensure financial operations are valid"""

    # Payment cannot exceed invoice total
    if event.command_type == "PaymentRecord":
        invoice_id = event.params["invoice_id"]
        amount = event.params["amount"]

        invoice = get_invoice(invoice_id)
        remaining = invoice.total - invoice.amount_paid

        if amount > remaining:
            return PolicyResult.DENY(
                f"Payment amount {amount} exceeds remaining balance {remaining}"
            )

    # Refund cannot exceed paid amount
    if event.command_type == "PaymentRefund":
        payment_id = event.params["payment_id"]
        refund_amount = event.params["amount"]

        payment = get_payment(payment_id)

        if refund_amount > payment.amount:
            return PolicyResult.DENY(
                f"Refund amount {refund_amount} exceeds payment {payment.amount}"
            )

    # Invoice total must match line items
    if event.command_type == "InvoiceCreate":
        line_items = event.params.get("line_items", [])
        declared_total = event.params.get("total", 0)

        calculated_total = sum(item["amount"] for item in line_items)

        if abs(declared_total - calculated_total) > 0.01:  # Tolerance for rounding
            return PolicyResult.DENY(
                f"Invoice total {declared_total} does not match line items {calculated_total}"
            )

    return PolicyResult.ALLOW
```

**Error Code:** `INT_MONEY_INCONSISTENCY`

---

#### INT-005: Job-Invoice Linkage

**Applies to:** Invoice and payment commands

**Rule:**
```python
def check_job_invoice_linkage(event: CommandEvent) -> PolicyResult:
    """Ensure job and invoice are properly linked"""

    # Cannot invoice a job twice
    if event.command_type == "InvoiceCreate":
        job_id = event.params["job_id"]
        job = get_job(job_id)

        if job.invoice_no:
            return PolicyResult.DENY(
                f"Job {job_id} already has invoice {job.invoice_no}"
            )

    # Cannot invoice incomplete job
    if event.command_type == "InvoiceCreate":
        job_id = event.params["job_id"]
        job = get_job(job_id)

        if job.status not in ["COMPLETED", "AWAITING_SIGNOFF"]:
            return PolicyResult.DENY(
                f"Job {job_id} must be completed before invoicing (status: {job.status})"
            )

    return PolicyResult.ALLOW
```

**Error Code:** `INT_LINKAGE_VIOLATION`

---

#### INT-006: Idempotency Check

**Applies to:** Commands with idempotency keys

**Rule:**
```python
def check_idempotency(event: CommandEvent) -> PolicyResult:
    """Prevent duplicate command execution"""

    if not event.idempotency_key:
        return PolicyResult.ALLOW  # No idempotency required

    # Check if command with this key was already executed
    existing = get_command_by_idempotency_key(
        event.command_type,
        event.idempotency_key
    )

    if existing:
        # Return cached result instead of re-executing
        return PolicyResult.DUPLICATE(existing.result)

    return PolicyResult.ALLOW
```

**Error Code:** `INT_DUPLICATE_COMMAND` (informational)

---

## 3. Scheduling Policy

**Purpose:** Prevent scheduling conflicts and resource over-allocation.

### Rules

#### SCH-001: Crew Availability

**Applies to:** `JobSchedule`, `JobAssignCrew`

**Rule:**
```python
def check_crew_availability(event: CommandEvent) -> PolicyResult:
    """Ensure crew is available on job date"""

    if event.command_type not in ["JobSchedule", "JobAssignCrew"]:
        return PolicyResult.ALLOW

    job_date = event.params.get("job_date")
    crew_ids = event.params.get("crew_ids", [])

    for crew_id in crew_ids:
        unavailable = find_unavailable_crew_for_date(job_date)
        if crew_id in unavailable:
            crew = get_user(crew_id)
            return PolicyResult.DENY(
                f"{crew.name} is unavailable on {job_date}"
            )

    return PolicyResult.ALLOW
```

**Error Code:** `SCH_CREW_UNAVAILABLE`

---

#### SCH-002: Crew Conflict Detection

**Applies to:** `JobSchedule`, `JobAssignCrew`

**Rule:**
```python
def check_crew_conflicts(event: CommandEvent) -> PolicyResult:
    """Ensure crew is not double-booked"""

    if event.command_type not in ["JobSchedule", "JobAssignCrew"]:
        return PolicyResult.ALLOW

    job_date = event.params.get("job_date")
    crew_ids = event.params.get("crew_ids", [])

    for crew_id in crew_ids:
        conflicts = find_crew_conflicts(crew_id, job_date)

        if conflicts:
            crew = get_user(crew_id)
            conflict_jobs = ", ".join([f"Job {j.id}" for j in conflicts])
            return PolicyResult.DENY(
                f"{crew.name} is already assigned to {conflict_jobs} on {job_date}"
            )

    return PolicyResult.ALLOW
```

**Error Code:** `SCH_CREW_CONFLICT`

---

#### SCH-003: Vehicle Availability

**Applies to:** `JobAssignVehicle`

**Rule:**
```python
def check_vehicle_availability(event: CommandEvent) -> PolicyResult:
    """Ensure vehicle is available on job date"""

    if event.command_type != "JobAssignVehicle":
        return PolicyResult.ALLOW

    vehicle_id = event.params.get("vehicle_id")
    job_date = event.params.get("job_date")

    conflicts = find_vehicle_conflicts(vehicle_id, job_date)

    if conflicts:
        vehicle = get_vehicle(vehicle_id)
        conflict_jobs = ", ".join([f"Job {j.id}" for j in conflicts])
        return PolicyResult.DENY(
            f"Vehicle {vehicle.registration} is already assigned to {conflict_jobs} on {job_date}"
        )

    return PolicyResult.ALLOW
```

**Error Code:** `SCH_VEHICLE_CONFLICT`

---

#### SCH-004: Capacity Limits

**Applies to:** `JobSchedule`

**Rule:**
```python
def check_daily_capacity(event: CommandEvent) -> PolicyResult:
    """Ensure daily capacity is not exceeded"""

    if event.command_type != "JobSchedule":
        return PolicyResult.ALLOW

    job_date = event.params.get("job_date")
    estimated_hours = event.params.get("estimated_hours", 4)  # Default

    capacity = calculate_daily_capacity(job_date)

    if capacity.available_hours < estimated_hours:
        return PolicyResult.WARN(
            f"Low capacity on {job_date}: {capacity.available_hours} hours available, {estimated_hours} required"
        )

    return PolicyResult.ALLOW
```

**Error Code:** `SCH_CAPACITY_WARNING` (warning, not block)

---

## 4. Comms Policy

**Purpose:** Prevent spam, enforce rate limits, and ensure communication compliance.

### Rules

#### COMM-001: Rate Limiting

**Applies to:** `MessageSendSMS`, `MessageSendEmail`, `MessageSendBulk*`

**Rule:**
```python
RATE_LIMITS = {
    "MessageSendSMS": (10, 60),  # 10 SMS per 60 seconds
    "MessageSendEmail": (20, 60),  # 20 emails per 60 seconds
    "MessageSendBulkSMS": (100, 3600),  # 100 bulk SMS per hour
    "MessageSendBulkEmail": (200, 3600),  # 200 bulk emails per hour
}

def check_rate_limit(event: CommandEvent) -> PolicyResult:
    """Enforce rate limits on messaging"""

    if event.command_type not in RATE_LIMITS:
        return PolicyResult.ALLOW

    limit, window = RATE_LIMITS[event.command_type]

    recent_count = count_recent_messages(
        event.command_type,
        window_seconds=window
    )

    if recent_count >= limit:
        return PolicyResult.DENY(
            f"Rate limit exceeded: {limit} {event.command_type} per {window}s"
        )

    return PolicyResult.ALLOW
```

**Error Code:** `COMM_RATE_LIMIT_EXCEEDED`

---

#### COMM-002: Duplicate Message Prevention

**Applies to:** `MessageSendSMS`, `MessageSendEmail`

**Rule:**
```python
def check_duplicate_message(event: CommandEvent) -> PolicyResult:
    """Prevent sending duplicate messages within short window"""

    if event.command_type not in ["MessageSendSMS", "MessageSendEmail"]:
        return PolicyResult.ALLOW

    recipient = event.params.get("recipient")
    message_body = event.params.get("message")

    # Check for duplicate in last 5 minutes
    duplicate = find_recent_message(
        recipient=recipient,
        message_body=message_body,
        within_seconds=300
    )

    if duplicate:
        return PolicyResult.DENY(
            f"Duplicate message to {recipient} sent {duplicate.sent_at}"
        )

    return PolicyResult.ALLOW
```

**Error Code:** `COMM_DUPLICATE_MESSAGE`

---

#### COMM-003: Contact Preference Enforcement

**Applies to:** `MessageSendSMS`, `MessageSendEmail`

**Rule:**
```python
def check_contact_preferences(event: CommandEvent) -> PolicyResult:
    """Respect customer contact preferences"""

    if event.command_type not in ["MessageSendSMS", "MessageSendEmail"]:
        return PolicyResult.ALLOW

    customer_id = event.params.get("customer_id")
    channel = "sms" if "SMS" in event.command_type else "email"

    customer = get_customer(customer_id)

    # Check if customer opted out of this channel
    if channel == "sms" and not customer.allow_sms:
        return PolicyResult.DENY(
            f"Customer {customer.name} has opted out of SMS"
        )

    if channel == "email" and not customer.allow_email:
        return PolicyResult.DENY(
            f"Customer {customer.name} has opted out of email"
        )

    return PolicyResult.ALLOW
```

**Error Code:** `COMM_CONTACT_PREFERENCE_VIOLATION`

---

#### COMM-004: Quiet Hours

**Applies to:** `MessageSendSMS`

**Rule:**
```python
QUIET_HOURS_START = 21  # 9 PM
QUIET_HOURS_END = 8     # 8 AM

def check_quiet_hours(event: CommandEvent) -> PolicyResult:
    """Prevent SMS during quiet hours"""

    if event.command_type != "MessageSendSMS":
        return PolicyResult.ALLOW

    current_hour = datetime.now().hour

    if QUIET_HOURS_START <= current_hour or current_hour < QUIET_HOURS_END:
        return PolicyResult.WARN(
            f"Sending SMS during quiet hours ({QUIET_HOURS_START}:00-{QUIET_HOURS_END}:00)"
        )

    return PolicyResult.ALLOW
```

**Error Code:** `COMM_QUIET_HOURS_WARNING` (warning, not block)

---

## Policy Result Types

```python
@dataclass
class PolicyResult:
    """Result of policy check"""
    status: str  # ALLOW, DENY, WARN, DUPLICATE
    message: Optional[str] = None
    error_code: Optional[str] = None
    cached_result: Optional[Any] = None  # For duplicate commands

    @staticmethod
    def ALLOW() -> PolicyResult:
        return PolicyResult(status="ALLOW")

    @staticmethod
    def DENY(message: str, error_code: str = None) -> PolicyResult:
        return PolicyResult(status="DENY", message=message, error_code=error_code)

    @staticmethod
    def WARN(message: str) -> PolicyResult:
        return PolicyResult(status="WARN", message=message)

    @staticmethod
    def DUPLICATE(cached_result: Any) -> PolicyResult:
        return PolicyResult(
            status="DUPLICATE",
            message="Command already executed (idempotent)",
            cached_result=cached_result
        )
```

---

## Policy Execution

```python
class PolicyEngine:
    """Executes policies in order"""

    def __init__(self):
        self.policies = [
            SecurityPolicy(),
            IntegrityPolicy(),
            SchedulingPolicy(),
            CommsPolicy(),
        ]

    def check(self, event: CommandEvent) -> PolicyResult:
        """Run all policies"""

        for policy in self.policies:
            result = policy.check(event)

            if result.status == "DENY":
                # Hard failure - stop execution
                return result

            if result.status == "DUPLICATE":
                # Return cached result
                return result

            if result.status == "WARN":
                # Log warning but continue
                log_warning(result.message)

        return PolicyResult.ALLOW()
```

---

## Next Steps

1. ✅ Define policy packs
2. ⏳ Implement policy engine (Phase 2)
3. ⏳ Add policy tests
4. ⏳ Create policy override mechanism (for admin)
5. ⏳ Add policy audit logging

---

**Status:** ✅ Approved - Security and integrity policies operational
**Reviewer:** Development Team
**Approved:** ✅ 2026-01-06 (RBAC, multi-tenant isolation verified)
