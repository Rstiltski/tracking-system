# 🔄 State Machines - Entity Lifecycle Management

**State machine implementations for entity lifecycle.**

---

## Overview

The `brain/state/` directory contains state machine implementations that manage entity lifecycles and validate state transitions.

---

## Components

| File | Purpose |
|------|---------|
| `machine.py` | Base state machine class |
| `manager.py` | State machine manager |
| `job_machine.py` | Job state machine |
| `invoice_machine.py` | Invoice state machine |
| `payment_machine.py` | Payment state machine |
| `quote_machine.py` | Quote state machine |

---

## Job State Machine

Manages job lifecycle:

```
DRAFT → QUOTED → BOOKED → SCHEDULED → IN_PROGRESS → COMPLETED
                    ↓
                CANCELLED
```

```python
from brain.state.job_machine import JobMachine

machine = JobMachine()

# Validate transition
result = machine.validate_transition(
    from_state="DRAFT",
    to_state="QUOTED",
    command="JobQuote"
)

# Get valid transitions
valid = machine.get_valid_states("BOOKED")
```

---

## Invoice State Machine

Manages invoice lifecycle:

```
DRAFT → SENT → VIEWED → PAID
    ↓
  VOID
```

```python
from brain.state.invoice_machine import InvoiceMachine

machine = InvoiceMachine()

# Check if can void
can_void = machine.can_transition("SENT", "VOID")

# Get next states
next_states = machine.get_valid_states("DRAFT")
```

---

## Payment State Machine

Manages payment lifecycle:

```
PENDING → CLEARED
    ↓
  FAILED
    ↓
  REFUNDED
```

```python
from brain.state.payment_machine import PaymentMachine

machine = PaymentMachine()

# Validate payment transition
result = machine.validate_transition("PENDING", "CLEARED")
```

---

## Quote State Machine

Manages quote lifecycle:

```
DRAFT → SENT → ACCEPTED → CONVERTED
    ↓
  DECLINED
```

```python
from brain.state.quote_machine import QuoteMachine

machine = QuoteMachine()

# Check if can accept
can_accept = machine.can_transition("SENT", "ACCEPTED")
```

---

## State Machine Manager

Coordinates all state machines:

```python
from brain.state.manager import StateMachineManager

manager = StateMachineManager()

# Validate any entity transition
result = manager.validate_transition(
    entity_type="job",
    entity_id="123",
    command="JobComplete",
    new_state="COMPLETED"
)
```

---

## Transition Result

All transitions return a result:

```python
class TransitionResult:
    success: bool
    from_state: str
    to_state: str
    error_message: str
    preconditions_met: bool
```

---

## Cross-References

| Topic | File |
|-------|------|
| State machine specs | `brain/design/01_state_machines.md` |
| Core brain | `brain/core/README.md` |
| Policies | `brain/policies/README.md` |

---

**Last Updated:** February 2026