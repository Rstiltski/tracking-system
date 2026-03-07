# 🔀 Fork Engine - Dry-Run Execution

**Safe preview of changes before committing.**

---

## Overview

The `brain/fork/` directory contains the fork engine for dry-run execution and confirmation management.

---

## Components

| File | Purpose |
|------|---------|
| `engine.py` | Fork engine for dry-run execution |
| `confirmation.py` | Confirmation token management |

---

## Fork Engine

Executes commands in a sandboxed environment:

```python
from brain.fork.engine import ForkEngine

engine = ForkEngine(db_connection)

# Execute in dry-run mode
with engine.fork() as fork_context:
    # Execute operations
    result = some_operation()
    
    # Track affected entities
    fork_context.track_entity("job", "123")
    
    # Get diffs
    diffs = fork_context.get_diffs()
    
    # Get new entities
    new = fork_context.get_new_entities()
```

---

## Confirmation Manager

Manages confirmation tokens for high-risk operations:

```python
from brain.fork.confirmation import ConfirmationManager

manager = ConfirmationManager(db_connection)

# Generate token
token = manager.generate_token(
    command_type="InvoiceVoid",
    params={...},
    user_id="user123",
    dry_run_result={...}
)

# Validate token
is_valid, error = manager.validate_token(
    token=token.token,
    command_type="InvoiceVoid",
    user_id="user123"
)

# Consume token (one-time use)
manager.consume_token(token.token)
```

---

## Dry-Run Result

```python
class DryRunResult:
    success: bool
    affected_entities: list
    diffs: list
    new_entities: list
    error: str
```

---

## Cross-References

| Topic | File |
|-------|------|
| AI entry point | `../AI_START_HERE.md` |
| Security playbook | `../SECURITY_PLAYBOOK.md` |
| Risk tiers | `brain/design/05_risk_tiers.md` |
| Core brain | `brain/core/README.md` |
| Router | `brain/core/router.py` |

---

**Last Updated:** March 2026
