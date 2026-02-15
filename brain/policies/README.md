# 📋 Policies - Validation Rules Engine

**Precondition checks for all operations.**

---

## Overview

The `brain/policies/` directory contains the policy engine and individual policies that validate preconditions before any operation is executed.

---

## Components

| File | Purpose |
|------|---------|
| `engine.py` | Policy orchestration engine |
| `security.py` | Authentication and authorization |
| `integrity.py` | Data integrity validation |
| `scheduling.py` | Scheduling constraints |
| `communications.py` | Communication limits |

---

## Policy Engine

The main engine orchestrates all policy checks:

```python
from brain.policies.engine import PolicyEngine

engine = PolicyEngine()

# Check all policies for a command
result = engine.check(command_event)

if result.is_denied:
    print(f"Denied: {result.message}")
elif result.is_duplicate:
    print(f"Duplicate: {result.cached_result}")
```

---

## Security Policy

Authentication and authorization checks:

```python
from brain.policies.security import SecurityPolicy

security = SecurityPolicy()

# Check authentication
result = security.check_auth(user_id="user123")

# Check authorization
result = security.check_permission(
    user_id="user123",
    action="InvoiceVoid",
    resource="invoice:456"
)

# Check role
result = security.check_role(user_id="user123", required_role="admin")
```

**Checks:**
- User is authenticated
- User has required role
- User has permission for action
- Session is valid

---

## Integrity Policy

Data integrity validation:

```python
from brain.policies.integrity import IntegrityPolicy

integrity = IntegrityPolicy()

# Validate data before save
result = integrity.validate(
    entity_type="invoice",
    data=invoice_data
)

# Check foreign keys
result = integrity.check_foreign_keys(
    entity_type="job",
    data={"customer_id": "123"}
)
```

**Checks:**
- Required fields present
- Data types correct
- Foreign keys valid
- Unique constraints satisfied

---

## Scheduling Policy

Scheduling constraints:

```python
from brain.policies.scheduling import SchedulingPolicy

scheduling = SchedulingPolicy()

# Check availability
result = scheduling.check_availability(
    resource_id="crew1",
    date="2026-02-20",
    time_slot="09:00-12:00"
)

# Check conflicts
result = scheduling.check_conflicts(
    job_id="123",
    scheduled_date="2026-02-20"
)
```

**Checks:**
- Resource availability
- No scheduling conflicts
- Time slot validity
- Crew capacity

---

## Communications Policy

Communication limits and validation:

```python
from brain.policies.communications import CommunicationsPolicy

comms = CommunicationsPolicy()

# Check rate limits
result = comms.check_rate_limit(
    user_id="user123",
    action="send_email"
)

# Validate message
result = comms.validate_message(
    message="Hello",
    recipients=["user1", "user2"]
)
```

**Checks:**
- Rate limits not exceeded
- Message content valid
- Recipients valid
- Template compliance

---

## Policy Result

All policies return a consistent result:

```python
class PolicyResult:
    is_allowed: bool      # Operation can proceed
    is_denied: bool       # Operation is denied
    is_duplicate: bool    # Duplicate operation detected
    error_code: str       # Error code if denied
    message: str          # Human-readable message
    cached_result: dict   # Cached result for duplicates
```

---

## Creating a New Policy

1. Create policy file in `brain/policies/`
2. Implement the check method
3. Register with the engine

```python
# brain/policies/my_policy.py
from brain.policies.engine import PolicyResult

class MyPolicy:
    """My custom policy."""
    
    def check(self, event) -> PolicyResult:
        """Check the policy."""
        # Validation logic
        if not self._is_valid(event):
            return PolicyResult(
                is_denied=True,
                error_code="MY_POLICY_VIOLATION",
                message="Policy violation description"
            )
        
        return PolicyResult(is_allowed=True)
```

---

## Cross-References

| Topic | File |
|-------|------|
| Policy specs | `brain/design/02_policy_packs.md` |
| Core brain | `brain/core/README.md` |
| Invariants | `brain/invariants/README.md` |

---

**Last Updated:** February 2026