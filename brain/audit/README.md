# 📝 Audit - Logging & Compliance

**Complete audit trail for all operations.**

---

## Overview

The `brain/audit/` directory contains the audit logging system that records every command and operation for compliance and debugging.

---

## Components

| File | Purpose |
|------|---------|
| `logger.py` | Audit logger implementation |
| `schema.py` | Audit log schema definition |

---

## Audit Logger

Records all operations:

```python
from brain.audit.logger import AuditLogger

logger = AuditLogger()

# Log command received
logger.log_command_received(event, risk_tier)

# Log command started
logger.log_command_started(command_id)

# Log tool call
logger.log_tool_call(
    command_id="123",
    tool_name="CreateJob",
    params={...},
    result={...},
    success=True
)

# Log command completed
logger.log_command_completed(
    command_id="123",
    result=result,
    duration_ms=45
)

# Log state transition
logger.log_state_transition(
    command_id="123",
    entity_type="job",
    entity_id="456",
    state_before="DRAFT",
    state_after="QUOTED",
    transition_valid=True
)
```

---

## Audit Schema

```python
{
    "command_id": "uuid",
    "command_type": "TaskCreate",
    "user_id": "user123",
    "company_id": "company1",
    "timestamp": "2026-02-13T14:00:00Z",
    "params": {...},
    "result": "SUCCESS",
    "duration_ms": 45,
    "entity_type": "task",
    "entity_id": "task123",
    "state_before": null,
    "state_after": "ACTIVE",
    "tool_calls": [
        {
            "tool": "CreateTask",
            "success": true,
            "data": {...}
        }
    ]
}
```

---

## Querying Audit Logs

```python
from brain.tools.audit_tools import ViewAuditLogTool

tool = ViewAuditLogTool()
result = tool.run({
    "start_date": "2026-02-01",
    "end_date": "2026-02-13",
    "user_id": "user123",
    "command_type": "InvoiceCreate"
})
```

---

## Cross-References

| Topic | File |
|-------|------|
| AI entry point | `../AI_START_HERE.md` |
| Security playbook | `../SECURITY_PLAYBOOK.md` |
| Audit schema specs | `brain/design/06_audit_schema.md` |
| Core brain | `brain/core/README.md` |
| Audit tools | `brain/tools/audit_tools.py` |

---

**Last Updated:** February 2026