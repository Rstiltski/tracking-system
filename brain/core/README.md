# 🧠 Brain Core - Central Orchestration

**The heart of the Brain system.**

---

## Overview

The `brain/core/` directory contains the essential components that power the Brain's central nervous system functionality. Every command flows through these modules.

---

## Components

| File | Purpose |
|------|---------|
| `brain.py` | Main entry point - orchestrates all operations |
| `router.py` | Routes commands to execution plans |
| `result.py` | Result types (BrainResult, ToolOutput) |
| `tool.py` | Base Tool class and contracts |
| `enums.py` | Risk tiers, status codes, enums |
| `guardrails.py` | Safety middleware and sanity checks |
| `cerebellum.py` | Coordination and timing |
| `command_event.py` | Command event structure |
| `events.py` | Event types and handlers |
| `types.py` | Type definitions |
| `contracts.py` | Interface contracts |
| `stem.py` | Core stem functionality |
| `integration.py` | Integration layer |
| `system_status.py` | System health monitoring |
| `secure_channel.py` | Secure communication |
| `nonce_ledger.py` | Nonce management for idempotency |
| `learning_mode_middleware.py` | Learning mode support |

---

## Main Components

### Brain (`brain.py`)

The main entry point for all command execution:

```python
from brain.core.brain import Brain
from brain.core.command_event import CommandEvent

brain = Brain()
result = brain.run(command_event)
```

**Key Responsibilities:**
- Command orchestration
- Tool registry management
- Policy engine coordination
- State machine integration
- Audit logging
- Error handling

### Router (`router.py`)

Routes commands to execution plans:

```python
router = Router()
plan = router.route(event)  # Returns list of tool calls
risk_tier = router.get_risk_tier("JobCreate")
requires_confirmation = router.requires_confirmation("InvoiceVoid")
```

**Key Features:**
- Command-to-tool mapping
- Risk tier classification
- Confirmation requirements

### Result Types (`result.py`)

Standardized result objects:

```python
# BrainResult
result = BrainResult(
    success=True,
    status="SUCCESS",
    data={...},
    command_id="uuid",
    command_type="TaskCreate"
)

# ToolOutput
output = ToolOutput(
    success=True,
    data={...},
    error_code=None,
    error_message=None
)
```

### Tool Base (`tool.py`)

Base class for all tools:

```python
from brain.core.tool import Tool
from brain.core.result import ToolOutput

class MyTool(Tool):
    @property
    def name(self) -> str:
        return "MyTool"
    
    @property
    def description(self) -> str:
        return "Tool description"
    
    @property
    def input_schema(self) -> dict:
        return {"type": "object", "properties": {...}}
    
    def execute(self, params: dict) -> ToolOutput:
        # Implementation
        return ToolOutput(success=True, data={...})
```

---

## Risk Tiers (`enums.py`)

| Tier | Level | Description |
|------|-------|-------------|
| TRIVIAL | 1 | Read-only, safe updates |
| LOW | 2 | Standard operations |
| MEDIUM | 3 | Customer-facing changes |
| HIGH | 4 | Financial, bulk operations |
| CRITICAL | 5 | Irreversible, destructive |

---

## Guardrails (`guardrails.py`)

Safety middleware for:
- Loop detection
- Sanity checks
- Rate limiting
- Resource protection

---

## Command Event (`command_event.py`)

Structure for all commands:

```python
event = CommandEvent(
    command_id="uuid",
    command_type="TaskCreate",
    params={"title": "New Task"},
    user_id="user123",
    company_id="company1",
    confirmation_token=None
)
```

---

## Usage Examples

### Basic Command Execution

```python
from brain.core.brain import Brain
from brain.core.command_event import CommandEvent

brain = Brain()
event = CommandEvent(
    command_type="TaskCreate",
    params={"title": "My Task"},
    user_id="user1"
)
result = brain.run(event)
```

### High-Risk Operation with Confirmation

```python
# First call - returns confirmation required
event = CommandEvent(
    command_type="TaskDelete",
    params={"task_id": "123"},
    user_id="user1"
)
result = brain.run(event)

# Get confirmation token
if result.requires_confirmation:
    token = result.confirmation_token
    
    # Second call with confirmation
    confirmed_event = CommandEvent(
        command_type="TaskDelete",
        params={"task_id": "123"},
        user_id="user1",
        confirmation_token=token
    )
    final_result = brain.run(confirmed_event)
```

---

## Cross-References

| Topic | File |
|-------|------|
| AI entry point | `../AI_START_HERE.md` |
| Security protocols | `../SECURITY_PLAYBOOK.md` |
| Tool registry | `brain/tools/README.md` |
| Policies | `brain/policies/README.md` |
| State machines | `brain/state/README.md` |
| Design docs | `brain/design/README.md` |

---

**Last Updated:** February 2026