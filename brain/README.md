# 🧠 Brain System - AI-Native Architecture

**The central nervous system for the Tracking System.**

---

## 🧭 Quick Navigation

| Want to... | Go to... |
|------------|----------|
| **Get started** | [GETTING_STARTED.md](../GETTING_STARTED.md) |
| **Understand rules** | [PROJECT_RULES.md](../PROJECT_RULES.md) |
| **Find features** | [FEATURE_MAP.md](../FEATURE_MAP.md) |
| **See research** | [docs/research/](../docs/research/) |

---

## 🤖 LLM Operational Guide for Brain Module

When working with the Brain system, the LLM must:

### Non-Linear, Holistic Reasoning
- **Assume the user doesn't know how to code** - Explain all changes in plain language
- **Analyze every request holistically** - Consider impact on entire Brain architecture
- **Ask clarifying questions** - Understand the broader goal before implementing
- **Take full responsibility** - Make all changes, tests, and documentation updates

### Brain-Specific Rules
1. **NO direct database access** - All operations through Tools
2. **NO auto-editing scripts** - Scripts detect only, never modify
3. **NO placeholders** - Complete implementations only
4. **ALWAYS log to audit** - Every command recorded
5. **ALWAYS validate transitions** - State machines enforced

### Expansion Ideas
When adding features to the Brain:
- **Linear**: Add new tools, policies, or state machines following existing patterns
- **Non-linear**: Consider AI-native features, self-healing capabilities, or cross-brain coordination

---

## TABLE OF CONTENTS

| # | Section | Key Info |
|---|---------|----------|
| 1 | Overview | What is the Brain? |
| 2 | Architecture | System design |
| 3 | Command Flow | Request lifecycle |
| 4 | Components | Module breakdown |
| 5 | Quick Start | Get started |
| 6 | Tool Registry | Available tools |
| 7 | Risk Tiers | Safety classification |
| 8 | State Machines | Entity lifecycle |
| 9 | Policies | Validation rules |
| 10 | Audit System | Logging & compliance |
| 11 | Development | Making changes |
| 12 | Cross-References | Documentation map |

---

## §1 Overview

The Brain is the **central nervous system** of the Tracking System. It provides:

- **Command Routing**: Validates and routes all commands
- **Policy Enforcement**: Security, integrity, and business rules
- **State Management**: Entity lifecycle and transitions
- **Tool Execution**: 100+ operation tools
- **Audit Logging**: Complete action history
- **Risk Assessment**: Safety classification for all operations

**Core Principle:** Every modification flows through the Brain. No direct database access.

---

## §2 Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                          BRAIN                                   │
│                    (brain/core/brain.py)                        │
│                                                                 │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐    │
│  │  Router  │──▶│ Policies │──▶│  State   │──▶│  Tools   │    │
│  │          │   │          │   │ Machine  │   │          │    │
│  └──────────┘   └──────────┘   └──────────┘   └──────────┘    │
│       │              │              │              │           │
│       ▼              ▼              ▼              ▼           │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │              Audit Log (append-only)                      │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
                        ┌────────────────┐
                        │   Database     │
                        │   (SQLite)     │
                        └────────────────┘
```

---

## §3 Command Flow

Every command follows this 10-step lifecycle:

1. **UI** creates a `CommandEvent` (e.g., `TaskCreate`, `GoalUpdate`)
2. **Router** validates structure and routes to handler
3. **Policies** check preconditions (security, integrity)
4. **State Machine** validates transitions (if applicable)
5. **Planner** generates execution plan (list of tool calls)
6. **Risk Checker** determines if confirmation needed
7. If high-risk → **Fork Engine** runs dry-run, returns diff to UI
8. UI displays diff → user confirms → Brain executes
9. **Tool Layer** executes plan (wrapped database calls)
10. **Audit Log** records command, plan, results, errors

---

## §4 Components

### Core (`brain/core/`)
| File | Purpose |
|------|---------|
| `brain.py` | Main entry point, orchestrates all operations |
| `router.py` | Routes commands to execution plans |
| `result.py` | Result types (BrainResult, ToolOutput) |
| `tool.py` | Base Tool class and contracts |
| `enums.py` | Risk tiers, status codes |
| `guardrails.py` | Safety middleware |
| `cerebellum.py` | Coordination and timing |
| `command_event.py` | Command event structure |

### Tools (`brain/tools/`)
100+ tools organized by domain:
- `job_tools.py` - Job operations
- `customer_tools.py` - Customer management
- `financial_tools.py` - Invoices, payments
- `scheduling_tools.py` - Scheduling operations
- `communication_tools.py` - Messaging
- `materials_tools.py` - Inventory
- `registry.py` - Tool registration

### Policies (`brain/policies/`)
| File | Purpose |
|------|---------|
| `engine.py` | Policy orchestration |
| `security.py` | Authentication, authorization |
| `integrity.py` | Data integrity rules |
| `scheduling.py` | Scheduling constraints |
| `communications.py` | Communication limits |

### State Machines (`brain/state/`)
| File | Entity |
|------|--------|
| `job_machine.py` | Job lifecycle |
| `invoice_machine.py` | Invoice lifecycle |
| `payment_machine.py` | Payment lifecycle |
| `quote_machine.py` | Quote lifecycle |
| `manager.py` | State machine coordination |

### Audit (`brain/audit/`)
| File | Purpose |
|------|---------|
| `logger.py` | Audit logging |
| `schema.py` | Audit schema definition |

### Security (`brain/security/`)
| File | Purpose |
|------|---------|
| `crypto_engine.py` | Encryption |
| `neural_link.py` | Secure command channel |
| `export_guard.py` | Data export protection |
| `ai_policy_enforcer.py` | AI operation policies |

### Invariants (`brain/invariants/`)
| File | Purpose |
|------|---------|
| `checker.py` | Invariant verification |
| `money_invariants.py` | Financial rules |
| `linking_invariants.py` | Relationship rules |
| `idempotency_invariants.py` | Duplicate prevention |
| `scorer.py` | Invariant scoring |

### Immune System (`brain/immune/`)
| File | Purpose |
|------|---------|
| `fingerprinter.py` | Code fingerprinting |
| `homeostasis.py` | System balance |
| `quarantine.py` | Problem isolation |
| `memory_monitor.py` | Memory management |
| `worker.py` | Background processing |

### Privacy (`brain/privacy/`)
| File | Purpose |
|------|---------|
| `tokenizer.py` | Data tokenization |
| `vault.py` | Secure storage |

### Fork Engine (`brain/fork/`)
| File | Purpose |
|------|---------|
| `engine.py` | Dry-run execution |
| `confirmation.py` | Confirmation tokens |

### Specialized Brains (`brain/brains/`)
| File | Purpose |
|------|---------|
| `ops_brain.py` | Operations |
| `finance_brain.py` | Financial operations |
| `relation_brain.py` | Relationships |
| `diagnosis_brain.py` | Diagnostics |
| `repair_brain.py` | Self-repair |
| `scanner_brain.py` | Code scanning |
| `test_brain.py` | Testing |
| `validator_brain.py` | Validation |
| `meta_brain.py` | Meta-operations |
| `docs_brain.py` | Documentation |

### Context Module (`brain/context/`)
| File | Purpose |
|------|---------|
| `context_loader.py` | Loads README.md files as AI context |
| `thinking_brain.py` | Processes prompts through brain architecture |

---

## §5 Quick Start

### Basic Usage

```python
from brain.core.brain import Brain
from brain.core.command_event import CommandEvent

# Initialize Brain
brain = Brain()

# Create a command event
event = CommandEvent(
    command_type="TaskCreate",
    params={
        "title": "Complete project",
        "priority": "high",
        "due_date": "2026-02-20"
    },
    user_id="user123"
)

# Execute command
result = brain.run(event)

if result.success:
    print(f"Task created: {result.data}")
else:
    print(f"Error: {result.error_message}")
```

### With Confirmation (High-Risk Operations)

```python
# First call returns confirmation required
result = brain.run(event)

if result.requires_confirmation:
    # Show diff to user
    print(f"Changes: {result.dry_run_preview}")
    
    # User confirms
    confirmed_event = CommandEvent(
        command_type="TaskDelete",
        params={"task_id": "123"},
        user_id="user123",
        confirmation_token=result.confirmation_token
    )
    
    # Execute with confirmation
    final_result = brain.run(confirmed_event)
```

---

## §6 Tool Registry

### Tool Categories

| Category | Tools | Risk Level |
|----------|-------|------------|
| Job Management | CreateJob, UpdateJob, DeleteJob | LOW-CRITICAL |
| Customer | CreateCustomer, UpdateCustomer | LOW |
| Financial | CreateInvoice, RecordPayment | HIGH |
| Communication | SendMessage, SendBulkMessage | MEDIUM-HIGH |
| Scheduling | ScheduleJob, RescheduleJob | MEDIUM |
| Inventory | CreateMaterial, AdjustInventory | MEDIUM |
| Time Tracking | ClockIn, ClockOut | LOW |
| Portal | GeneratePortalToken, RevokePortalToken | MEDIUM |

### Registering Tools

```python
# Eager registration
registry.register(MyTool())

# Lazy registration (recommended)
registry.register_lazy(
    "MyTool",
    "brain.tools.my_tools",
    "MyToolClass"
)

# Auto-discovery
registry.auto_discover_tools()
```

---

## §7 Risk Tiers

| Tier | Level | Confirmation | Examples |
|------|-------|--------------|----------|
| TRIVIAL | 1 | No | GetJob, AddNote |
| LOW | 2 | No | CreateJob, UpdateJob |
| MEDIUM | 3 | No | SendInvoice, ScheduleJob |
| HIGH | 4 | Yes | RecordPayment, BulkOperations |
| CRITICAL | 5 | Yes + Nuclear Codes | DeleteJob, VoidInvoice |

### Risk Tier Assignment

```python
# In router.py
RISK_TIERS = {
    "JobCreate": RiskTier.LOW,
    "InvoiceVoid": RiskTier.CRITICAL,
    "PaymentRecord": RiskTier.HIGH,
    # ...
}
```

---

## §8 State Machines

### Job States

```
DRAFT → QUOTED → BOOKED → SCHEDULED → IN_PROGRESS → COMPLETED
                    ↓
                CANCELLED
```

### Invoice States

```
DRAFT → SENT → VIEWED → PAID
    ↓
  VOID
```

### Quote States

```
DRAFT → SENT → ACCEPTED → CONVERTED
    ↓
  DECLINED
```

---

## §9 Policies

### Security Policy
- Authentication required for all operations
- Role-based access control
- Session validation

### Integrity Policy
- Data validation before save
- Foreign key constraints
- Unique constraint enforcement

### Scheduling Policy
- No overlapping appointments
- Resource availability checks
- Time conflict detection

### Communications Policy
- Rate limiting on messages
- Bulk message confirmation
- Template validation

---

## §10 Audit System

### Audit Log Schema

```python
{
    "command_id": "uuid",
    "command_type": "TaskCreate",
    "user_id": "user123",
    "timestamp": "2026-02-13T14:00:00Z",
    "params": {...},
    "result": "SUCCESS",
    "duration_ms": 45,
    "entity_type": "task",
    "entity_id": "task123",
    "state_before": null,
    "state_after": "ACTIVE"
}
```

### Querying Audit Logs

```python
from brain.tools.audit_tools import ViewAuditLogTool

tool = ViewAuditLogTool()
result = tool.run({
    "start_date": "2026-02-01",
    "end_date": "2026-02-13",
    "user_id": "user123"
})
```

---

## §11 Development

### Adding a New Tool

1. Create tool file in `brain/tools/`
2. Inherit from `Tool` base class
3. Implement `input_schema` and `execute`
4. Register in `brain/core/brain.py`

```python
# brain/tools/my_tools.py
from brain.core.tool import Tool
from brain.core.result import ToolOutput

class MyNewTool(Tool):
    @property
    def name(self) -> str:
        return "MyNewTool"
    
    @property
    def description(self) -> str:
        return "Does something useful"
    
    @property
    def input_schema(self) -> dict:
        return {
            "type": "object",
            "properties": {
                "param1": {"type": "string"}
            },
            "required": ["param1"]
        }
    
    def execute(self, params: dict) -> ToolOutput:
        # Implementation
        return ToolOutput(success=True, data={"result": "ok"})
```

### Adding a New Policy

1. Create policy in `brain/policies/`
2. Add to policy engine
3. Define preconditions and error messages

---

## §12 Cross-References

| If you need... | Read this file |
|----------------|---------------|
| Command namespace | `design/00_command_namespace.md` |
| State machine specs | `design/01_state_machines.md` |
| Policy definitions | `design/02_policy_packs.md` |
| Invariant rules | `design/03_invariants.md` |
| Tool contracts | `design/04_tool_contracts.md` |
| Risk tier reference | `design/05_risk_tiers.md` |
| Audit schema | `design/06_audit_schema.md` |
| Roles & permissions | `design/07_roles_permissions.md` |
| Core documentation | `core/README.md` |
| Tools documentation | `tools/README.md` |

---

## Critical Rules

1. **NO direct database access** - All operations through Tools
2. **NO auto-editing scripts** - Scripts detect only, never modify
3. **NO placeholders** - Complete implementations only
4. **ALWAYS log to audit** - Every command recorded
5. **ALWAYS validate transitions** - State machines enforced

---

**Last Updated:** February 2026
**Maintained By:** System Architect