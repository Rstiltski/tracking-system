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

## Performance System Auditing

The audit system also tracks performance optimization operations:

```python
# Log predictive loading operations
logger.log_performance_operation(
    operation_type="predictive_load",
    component="dashboard",
    duration_ms=120,
    success=True,
    cache_hit=True
)

# Log smart cache operations
logger.log_performance_operation(
    operation_type="smart_cache",
    cache_key="user_data_123",
    strategy="ml_optimized",
    hit_rate=0.85
)

# Log progressive loading events
logger.log_performance_operation(
    operation_type="progressive_load",
    content_type="critical",
    skeleton_shown=True,
    load_time_ms=800
)

# Log performance analytics events
logger.log_performance_operation(
    operation_type="performance_analytics",
    metric_type="page_load",
    value=1.2,
    threshold_exceeded=False
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
    ],
    "performance_metrics": {
        "predictive_loading": true,
        "cache_hit": false,
        "progressive_loading": true,
        "analytics_tracked": true
    }
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

### Performance Analytics Queries

```python
# Query performance system operations
performance_logs = tool.run({
    "start_date": "2026-03-01",
    "end_date": "2026-03-08",
    "operation_type": "performance_analytics",
    "metric_type": "page_load"
})

# Query cache performance
cache_logs = tool.run({
    "start_date": "2026-03-01",
    "end_date": "2026-03-08",
    "operation_type": "smart_cache",
    "cache_key": "user_data_*"
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
| Performance systems | `docs/PHASE_8_FINAL_SUMMARY.md` |
| Predictive loading | `docs/PREDICTIVE_LOADING_GUIDE.md` |
| Smart caching | `docs/SMART_CACHING_GUIDE.md` |
| Progressive loading | `docs/PROGRESSIVE_LOADING_GUIDE.md` |
| Performance analytics | `docs/PERFORMANCE_ANALYTICS_GUIDE.md` |

---

**Last Updated:** February 2026