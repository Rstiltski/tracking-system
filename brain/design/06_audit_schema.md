# Audit Schema (Event Log + Replay)

**Rule:** Do not use scripts to edit code.

**Version:** 1.0
**Status:** Draft
**Last Updated:** 2026-01-01

## Overview

The **Audit Log** is an append-only record of every command executed by the Brain. It enables:

- ✅ **Full traceability** - Who did what, when, and why
- ✅ **Replay capability** - Reconstruct state at any point in time
- ✅ **Debugging** - Understand how current state was reached
- ✅ **Compliance** - Audit trail for financial operations
- ✅ **Rollback** - Undo operations (where possible)

## Core Principles

1. **Append-Only** - Never delete or modify audit log entries
2. **Complete** - Log every command, success or failure
3. **Immutable** - Once written, never changed
4. **Ordered** - Strict chronological ordering
5. **Replayable** - Sufficient data to replay any command

---

## Audit Log Schema

### Primary Table: `brain_audit_log`

```sql
CREATE TABLE brain_audit_log (
    -- Identity
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    command_id TEXT NOT NULL UNIQUE,  -- UUID for this command execution
    sequence_number INTEGER NOT NULL,  -- Monotonically increasing

    -- Command Details
    command_type TEXT NOT NULL,  -- e.g., "InvoiceCreate", "PaymentRecord"
    command_params TEXT NOT NULL,  -- JSON of command parameters
    idempotency_key TEXT,  -- For deduplication

    -- Execution Context
    user_id INTEGER NOT NULL,
    company_id INTEGER NOT NULL,
    session_id TEXT,  -- UI session or API session
    client_ip TEXT,
    user_agent TEXT,

    -- Timestamps
    received_at TIMESTAMP NOT NULL,  -- When command was received
    started_at TIMESTAMP,  -- When execution started
    completed_at TIMESTAMP,  -- When execution finished
    duration_ms INTEGER,  -- Execution time in milliseconds

    -- Execution Results
    status TEXT NOT NULL,  -- "SUCCESS", "FAILED", "DUPLICATE"
    result_data TEXT,  -- JSON of command result
    error_code TEXT,  -- Error code if failed
    error_message TEXT,  -- Error message if failed
    stack_trace TEXT,  -- Full stack trace if failed

    -- Confirmation & Risk
    risk_tier INTEGER NOT NULL,  -- 1-5
    confirmation_required BOOLEAN NOT NULL,
    confirmation_token TEXT,  -- If confirmation was required
    confirmation_at TIMESTAMP,  -- When user confirmed
    dry_run_result TEXT,  -- JSON of dry-run result (if performed)

    -- Tool Execution Plan
    plan TEXT,  -- JSON array of tool calls
    tool_results TEXT,  -- JSON array of tool results

    -- State Machine Transition (if applicable)
    entity_type TEXT,  -- e.g., "job", "invoice"
    entity_id INTEGER,  -- ID of entity
    state_before TEXT,  -- State before transition
    state_after TEXT,  -- State after transition

    -- Metadata
    metadata TEXT,  -- JSON of additional metadata
    tags TEXT,  -- Comma-separated tags for search

    -- Indexing
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,

    -- Indexes
    INDEX idx_command_id (command_id),
    INDEX idx_command_type (command_type),
    INDEX idx_user_id (user_id),
    INDEX idx_company_id (company_id),
    INDEX idx_entity (entity_type, entity_id),
    INDEX idx_created_at (created_at),
    INDEX idx_status (status),
    INDEX idx_idempotency_key (idempotency_key)
);
```

---

### Secondary Table: `brain_tool_calls`

**Purpose:** Log individual tool calls within a command execution.

```sql
CREATE TABLE brain_tool_calls (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    command_id TEXT NOT NULL,  -- Links to brain_audit_log
    tool_name TEXT NOT NULL,
    tool_params TEXT NOT NULL,  -- JSON
    tool_result TEXT,  -- JSON
    success BOOLEAN NOT NULL,
    error_code TEXT,
    error_message TEXT,
    started_at TIMESTAMP NOT NULL,
    completed_at TIMESTAMP,
    duration_ms INTEGER,

    FOREIGN KEY (command_id) REFERENCES brain_audit_log(command_id),
    INDEX idx_command_id (command_id),
    INDEX idx_tool_name (tool_name)
);
```

---

### Tertiary Table: `brain_state_transitions`

**Purpose:** Log state machine transitions.

```sql
CREATE TABLE brain_state_transitions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    command_id TEXT NOT NULL,  -- Links to brain_audit_log
    entity_type TEXT NOT NULL,  -- "job", "invoice", "payment"
    entity_id INTEGER NOT NULL,
    state_before TEXT NOT NULL,
    state_after TEXT NOT NULL,
    transition_valid BOOLEAN NOT NULL,  -- Was transition allowed?
    preconditions_met BOOLEAN NOT NULL,
    side_effects TEXT,  -- JSON array of side effects executed
    transitioned_at TIMESTAMP NOT NULL,

    FOREIGN KEY (command_id) REFERENCES brain_audit_log(command_id),
    INDEX idx_command_id (command_id),
    INDEX idx_entity (entity_type, entity_id)
);
```

---

## Audit Log Entry Example

### Successful Payment Recording

```json
{
    "id": 12345,
    "command_id": "550e8400-e29b-41d4-a716-446655440000",
    "sequence_number": 12345,
    "command_type": "PaymentRecord",
    "command_params": {
        "invoice_id": 789,
        "amount": 2500.00,
        "payment_method": "bank_transfer",
        "payment_date": "2026-01-15",
        "reference": "REF-ABC123"
    },
    "idempotency_key": "payment-789-2026-01-15-2500",
    "user_id": 5,
    "company_id": 1,
    "session_id": "sess_abc123",
    "client_ip": "192.168.1.100",
    "user_agent": "Mozilla/5.0...",
    "received_at": "2026-01-15T10:30:00Z",
    "started_at": "2026-01-15T10:30:01Z",
    "completed_at": "2026-01-15T10:30:02.500Z",
    "duration_ms": 1500,
    "status": "SUCCESS",
    "result_data": {
        "payment_id": 456,
        "invoice_balance": 0.00
    },
    "error_code": null,
    "error_message": null,
    "stack_trace": null,
    "risk_tier": 4,
    "confirmation_required": true,
    "confirmation_token": "conf_xyz789",
    "confirmation_at": "2026-01-15T10:30:00Z",
    "dry_run_result": {
        "diff": {
            "updates": [
                {
                    "table": "invoices",
                    "id": 789,
                    "fields": {
                        "amount_paid": {"before": 0.00, "after": 2500.00},
                        "balance_due": {"before": 2500.00, "after": 0.00},
                        "status": {"before": "SENT", "after": "PAID"}
                    }
                }
            ],
            "inserts": [
                {
                    "table": "payments",
                    "fields": {
                        "amount": 2500.00,
                        "payment_method": "bank_transfer"
                    }
                }
            ]
        }
    },
    "plan": [
        {
            "tool": "RecordPayment",
            "params": {
                "invoice_id": 789,
                "amount": 2500.00,
                "payment_method": "bank_transfer"
            }
        },
        {
            "tool": "UpdateInvoiceStatus",
            "params": {
                "invoice_id": 789,
                "status": "PAID"
            }
        },
        {
            "tool": "GenerateReceipt",
            "params": {
                "payment_id": 456
            }
        },
        {
            "tool": "SendReceipt",
            "params": {
                "payment_id": 456,
                "channel": "email"
            }
        }
    ],
    "tool_results": [
        {"tool": "RecordPayment", "success": true, "payment_id": 456},
        {"tool": "UpdateInvoiceStatus", "success": true},
        {"tool": "GenerateReceipt", "success": true, "receipt_id": 789},
        {"tool": "SendReceipt", "success": true, "message_id": 101}
    ],
    "entity_type": "invoice",
    "entity_id": 789,
    "state_before": "SENT",
    "state_after": "PAID",
    "metadata": {
        "invoice_no": "INV-2024-123",
        "customer_name": "John Smith"
    },
    "tags": "payment,invoice,financial",
    "created_at": "2026-01-15T10:30:02.500Z"
}
```

---

### Failed Command Example

```json
{
    "id": 12346,
    "command_id": "660e8400-e29b-41d4-a716-446655440001",
    "sequence_number": 12346,
    "command_type": "PaymentRecord",
    "command_params": {
        "invoice_id": 790,
        "amount": 3000.00,
        "payment_method": "cash"
    },
    "user_id": 5,
    "company_id": 1,
    "received_at": "2026-01-15T11:00:00Z",
    "started_at": "2026-01-15T11:00:01Z",
    "completed_at": "2026-01-15T11:00:01.200Z",
    "duration_ms": 200,
    "status": "FAILED",
    "result_data": null,
    "error_code": "INT_MONEY_OVERPAYMENT",
    "error_message": "Payment amount 3000.00 exceeds remaining balance 2500.00",
    "stack_trace": "Traceback (most recent call last):\\n  File ...",
    "risk_tier": 4,
    "confirmation_required": true,
    "confirmation_token": "conf_abc456",
    "confirmation_at": "2026-01-15T11:00:00Z",
    "dry_run_result": null,
    "plan": null,
    "tool_results": null,
    "entity_type": "invoice",
    "entity_id": 790,
    "state_before": "SENT",
    "state_after": "SENT",
    "metadata": null,
    "tags": "payment,error",
    "created_at": "2026-01-15T11:00:01.200Z"
}
```

---

## Audit Log Lifecycle

### 1. Command Received

```python
# Create audit log entry immediately
audit_entry = {
    "command_id": str(uuid4()),
    "sequence_number": get_next_sequence(),
    "command_type": event.command_type,
    "command_params": json.dumps(event.params),
    "user_id": event.user_id,
    "company_id": event.company_id,
    "received_at": datetime.utcnow(),
    "status": "PENDING",
    "risk_tier": get_risk_tier(event.command_type),
    "confirmation_required": requires_confirmation(event),
}

audit_id = db.insert("brain_audit_log", audit_entry)
```

### 2. Command Execution Starts

```python
db.update("brain_audit_log", audit_id, {
    "started_at": datetime.utcnow(),
    "status": "EXECUTING"
})
```

### 3. Tools Execute

```python
for tool_call in plan:
    tool_call_entry = {
        "command_id": audit_entry["command_id"],
        "tool_name": tool_call.name,
        "tool_params": json.dumps(tool_call.params),
        "started_at": datetime.utcnow()
    }
    tool_call_id = db.insert("brain_tool_calls", tool_call_entry)

    # Execute tool
    result = execute_tool(tool_call)

    # Update tool call
    db.update("brain_tool_calls", tool_call_id, {
        "tool_result": json.dumps(result.data),
        "success": result.success,
        "error_code": result.error_code,
        "error_message": result.error_message,
        "completed_at": datetime.utcnow(),
        "duration_ms": calculate_duration()
    })
```

### 4. Command Completes

```python
db.update("brain_audit_log", audit_id, {
    "completed_at": datetime.utcnow(),
    "duration_ms": calculate_duration(),
    "status": "SUCCESS",
    "result_data": json.dumps(result),
    "plan": json.dumps(plan),
    "tool_results": json.dumps(tool_results),
    "state_before": entity.state_before,
    "state_after": entity.state_after
})
```

### 5. Command Fails

```python
db.update("brain_audit_log", audit_id, {
    "completed_at": datetime.utcnow(),
    "duration_ms": calculate_duration(),
    "status": "FAILED",
    "error_code": error.code,
    "error_message": str(error),
    "stack_trace": traceback.format_exc()
})
```

---

## Replay Capability

### Use Cases

1. **Debug Production Issues** - Replay failed commands to reproduce bugs
2. **Audit Investigations** - Reconstruct sequence of events
3. **Data Recovery** - Replay commands after backup restore
4. **Testing** - Replay production commands in test environment

### Replay Engine

```python
class ReplayEngine:
    """Replays commands from audit log"""

    def replay_command(self, command_id: str, dry_run: bool = True) -> ReplayResult:
        """Replay a single command by ID"""

        # Load audit log entry
        audit_entry = db.get("brain_audit_log", command_id=command_id)

        if not audit_entry:
            raise ValueError(f"Command {command_id} not found in audit log")

        # Reconstruct command event
        event = CommandEvent(
            command_id=audit_entry["command_id"],
            command_type=audit_entry["command_type"],
            params=json.loads(audit_entry["command_params"]),
            user_id=audit_entry["user_id"],
            company_id=audit_entry["company_id"],
            timestamp=audit_entry["received_at"]
        )

        # Execute in dry-run mode by default
        if dry_run:
            result = brain.dry_run(event)
        else:
            result = brain.run(event)

        return ReplayResult(
            original_status=audit_entry["status"],
            original_result=json.loads(audit_entry["result_data"] or "{}"),
            replay_result=result,
            differences=self.compare_results(audit_entry, result)
        )

    def replay_sequence(
        self,
        from_sequence: int,
        to_sequence: int,
        dry_run: bool = True
    ) -> list[ReplayResult]:
        """Replay a sequence of commands"""

        entries = db.query(
            "brain_audit_log",
            where="sequence_number BETWEEN ? AND ?",
            params=[from_sequence, to_sequence],
            order_by="sequence_number ASC"
        )

        results = []
        for entry in entries:
            result = self.replay_command(entry["command_id"], dry_run)
            results.append(result)

        return results

    def replay_entity_history(
        self,
        entity_type: str,
        entity_id: int
    ) -> list[ReplayResult]:
        """Replay all commands affecting an entity"""

        entries = db.query(
            "brain_audit_log",
            where="entity_type = ? AND entity_id = ?",
            params=[entity_type, entity_id],
            order_by="sequence_number ASC"
        )

        results = []
        for entry in entries:
            result = self.replay_command(entry["command_id"], dry_run=True)
            results.append(result)

        return results
```

### Replay Constraints

**Not all commands can be replayed:**

| Command Type | Replayable | Notes |
|--------------|------------|-------|
| Read operations | ✅ Yes | Idempotent, no side effects |
| Create operations | ⚠️ Conditional | Only if idempotency key used |
| Update operations | ✅ Yes | Usually safe to replay |
| Delete operations | ❌ No | Cannot un-delete |
| Send messages | ❌ No | Would re-send messages |
| External API calls | ❌ No | May have side effects |

**Replay Safety:**
- Always replay in **dry-run mode** first
- Verify **state consistency** before committing
- Use **transaction isolation** to prevent conflicts

---

## Audit Log Queries

### Common Queries

#### 1. Get all commands by user
```sql
SELECT * FROM brain_audit_log
WHERE user_id = ?
ORDER BY created_at DESC
LIMIT 100;
```

#### 2. Get failed commands in last 24 hours
```sql
SELECT * FROM brain_audit_log
WHERE status = 'FAILED'
  AND created_at >= datetime('now', '-1 day')
ORDER BY created_at DESC;
```

#### 3. Get all financial commands
```sql
SELECT * FROM brain_audit_log
WHERE command_type IN ('InvoiceCreate', 'InvoiceSend', 'PaymentRecord', 'PaymentRefund')
  AND company_id = ?
ORDER BY created_at DESC;
```

#### 4. Get entity history
```sql
SELECT * FROM brain_audit_log
WHERE entity_type = 'invoice'
  AND entity_id = 789
ORDER BY sequence_number ASC;
```

#### 5. Get commands requiring confirmation
```sql
SELECT * FROM brain_audit_log
WHERE confirmation_required = 1
  AND confirmation_token IS NOT NULL
  AND created_at >= datetime('now', '-7 days')
ORDER BY created_at DESC;
```

#### 6. Performance analysis
```sql
SELECT
    command_type,
    COUNT(*) as count,
    AVG(duration_ms) as avg_duration,
    MAX(duration_ms) as max_duration,
    SUM(CASE WHEN status = 'FAILED' THEN 1 ELSE 0 END) as failures
FROM brain_audit_log
WHERE created_at >= datetime('now', '-30 days')
GROUP BY command_type
ORDER BY count DESC;
```

---

## Audit Log Retention

### Retention Policy

| Command Type | Retention Period | Reason |
|--------------|------------------|--------|
| Financial operations | **7 years** | Legal compliance (UK tax) |
| Customer comms | **2 years** | GDPR compliance |
| User operations | **1 year** | Security audit |
| System operations | **90 days** | Debug window |
| Read operations | **30 days** | Performance/debug |

### Archival Strategy

```python
def archive_old_logs():
    """Archive old audit logs to cold storage"""

    # Archive logs older than retention period
    cutoff_date = datetime.utcnow() - timedelta(days=365)

    # Export to JSON
    old_logs = db.query(
        "brain_audit_log",
        where="created_at < ? AND command_type NOT IN (?)",
        params=[cutoff_date, FINANCIAL_COMMANDS]
    )

    # Write to archive
    archive_file = f"audit_archive_{cutoff_date.strftime('%Y-%m-%d')}.jsonl"
    with open(archive_file, "w") as f:
        for log in old_logs:
            f.write(json.dumps(log) + "\\n")

    # Delete from active database
    db.delete(
        "brain_audit_log",
        where="created_at < ? AND command_type NOT IN (?)",
        params=[cutoff_date, FINANCIAL_COMMANDS]
    )
```

---

## Event Sourcing (Optional Future Enhancement)

**Phase 9+:** The audit log can evolve into full event sourcing.

**Event Sourcing Principles:**
1. Store only events (commands), not state
2. Rebuild state by replaying events
3. State is derived, events are source of truth

**Benefits:**
- Perfect audit trail
- Time travel (view state at any point)
- Debug by replay
- Multiple read models (projections)

**Implementation:**
```python
class EventStore:
    """Full event sourcing implementation"""

    def append(self, event: CommandEvent):
        """Append event to stream"""
        pass

    def get_stream(self, entity_type: str, entity_id: int) -> list[Event]:
        """Get all events for an entity"""
        pass

    def rebuild_state(self, entity_type: str, entity_id: int) -> dict:
        """Rebuild entity state by replaying events"""
        stream = self.get_stream(entity_type, entity_id)
        state = {}
        for event in stream:
            state = apply_event(state, event)
        return state
```

---

## Next Steps

1. ✅ Define audit schema
2. ⏳ Implement audit logging (Phase 1)
3. ⏳ Build replay engine (Phase 3)
4. ⏳ Create audit UI (query, replay) (Phase 4)
5. ⏳ Implement retention policy (Phase 2)

---

**Status:** Approved - Audit system implemented
**Reviewer:** Development Team
