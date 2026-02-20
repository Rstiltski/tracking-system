# 📋 Rules System - Formal Rule Definition and Management

**Complete rule management system with versioning, validation, and conflict detection.**

---

## Overview

The `brain/rules/` directory contains a comprehensive system for defining, validating, versioning, and managing business rules in the Veryfyn tracking system.

---

## Components

| File | Purpose |
|------|---------|
| `schema.py` | Formal rule definition schema |
| `validator.py` | Rule validation and conflict detection |
| `version_control.py` | Rule versioning and history |

---

## Quick Start

### Creating a Rule

```python
from brain.rules.schema import (
    RuleDefinition, RuleType, ConflictStrategy,
    Condition, Action, ConditionOperator, ActionType
)

# Create a simple validation rule
rule = RuleDefinition(
    rule_id="MONEY_001",
    rule_name="Payment Cannot Exceed Balance",
    rule_type=RuleType.INVARIANT,
    domain="finance",
    description="Ensures payment amounts do not exceed remaining invoice balance",
    preconditions=[
        Condition(
            field="payment.amount", 
            operator=ConditionOperator.GT, 
            value=0
        )
    ],
    actions=[
        Action(
            action_type=ActionType.BLOCK,
            message="Payment exceeds remaining balance"
        )
    ],
    priority=90,
    conflict_strategy=ConflictStrategy.BLOCK
)
```

### Validating a Rule

```python
from brain.rules.validator import RuleValidator

validator = RuleValidator()
result = validator.validate(rule)

if result.is_valid:
    print("Rule is valid!")
else:
    for error in result.errors:
        print(f"Error: {error.message}")
```

### Version Control

```python
from brain.rules.version_control import RuleVersionControl

vc = RuleVersionControl()

# Create a new rule
version = vc.create_rule(rule, author="developer")

# Update a rule
new_version = vc.update_rule(updated_rule, author="developer", reason="Fixed condition")

# Rollback to previous version
vc.rollback("MONEY_001", "1.0.0", author="admin")
```

---

## Rule Definition Schema

### Required Fields

| Field | Type | Description |
|-------|------|-------------|
| `rule_id` | str | Unique identifier (e.g., "MONEY_001") |
| `rule_name` | str | Human-readable name |
| `rule_type` | RuleType | Type of rule |
| `domain` | str | Domain (e.g., "finance", "scheduling") |

### Rule Types

| Type | Purpose |
|------|---------|
| `POLICY` | Preconditions that block execution |
| `INVARIANT` | Business rules that must always hold |
| `STATE` | State machine transition rules |
| `VALIDATION` | Input validation rules |
| `TRIGGER` | Event-driven rules |
| `TRANSFORMATION` | Data transformation rules |
| `COMPUTED` | Computed/derived value rules |

### Condition Operators

| Operator | Description |
|----------|-------------|
| `EQ` (==) | Equal |
| `NE` (!=) | Not equal |
| `GT` (>) | Greater than |
| `GTE` (>=) | Greater than or equal |
| `LT` (<) | Less than |
| `LTE` (<=) | Less than or equal |
| `IN` | Value in list |
| `NOT_IN` | Value not in list |
| `CONTAINS` | String/list contains |
| `MATCHES` | Regex match |
| `EXISTS` | Key exists |
| `IS_NULL` | Value is null |
| `AND` | Logical AND |
| `OR` | Logical OR |
| `NOT` | Logical NOT |

### Action Types

| Type | Purpose |
|------|---------|
| `BLOCK` | Block execution |
| `ALLOW` | Allow execution |
| `TRANSFORM` | Transform data |
| `NOTIFY` | Send notification |
| `LOG` | Log event |
| `TRIGGER` | Trigger another command |
| `COMPUTE` | Compute a value |
| `VALIDATE` | Validate and return result |
| `REPAIR` | Auto-repair an issue |

---

## Conflict Detection

The validator automatically detects:

- **Direct Conflicts**: Rules with same trigger, opposite actions
- **Priority Conflicts**: Circular priority dependencies
- **Dependency Conflicts**: Missing dependencies
- **Scope Conflicts**: Overlapping scopes

---

## Using Templates

Pre-defined templates for common patterns:

```python
from brain.rules.schema import create_rule_from_template

# Create a required field rule
rule = create_rule_from_template(
    "field_required",
    rule_id="VALID_001",
    rule_name="Invoice Number Required",
    domain="finance",
    field="invoice.number"
)
```

Available templates:
- `field_required` - Field must have a value
- `field_in_range` - Field must be within range
- `field_matches_pattern` - Field must match regex
- `state_transition` - Valid state transition rule

---

## Cross-References

| Topic | File |
|-------|------|
| Policies | `brain/policies/README.md` |
| Invariants | `brain/invariants/README.md` |
| State Machines | `brain/state/README.md` |
| Audit Log | `brain/audit/README.md` |

---

**Last Updated:** February 2026