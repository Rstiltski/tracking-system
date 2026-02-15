# 📐 Invariants - Business Rules Engine

**Business rules that MUST always hold true.**

---

## Overview

The `brain/invariants/` directory contains the invariant checking system - business rules that must always be satisfied for the system to be in a valid state.

---

## Components

| File | Purpose |
|------|---------|
| `checker.py` | Main invariant checker |
| `money_invariants.py` | Financial integrity rules |
| `linking_invariants.py` | Relationship integrity rules |
| `idempotency_invariants.py` | Duplicate prevention rules |
| `scorer.py` | Invariant violation scoring |

---

## Invariant Categories

### Money Invariants
Financial integrity rules:

```python
from brain.invariants.money_invariants import MoneyInvariants

money = MoneyInvariants()

# Check invoice totals
violations = money.check_invoice_total(invoice_id="123")

# Verify payment amounts
result = money.verify_payment_amount(payment_id="456")
```

**Rules:**
- Invoice total = sum of line items
- Payment amount cannot exceed invoice balance
- Credit notes must balance with original invoice

### Linking Invariants
Relationship integrity:

```python
from brain.invariants.linking_invariants import LinkingInvariants

linking = LinkingInvariants()

# Check foreign key integrity
violations = linking.check_job_customer_link(job_id="123")

# Verify all references exist
result = linking.verify_references("invoice", invoice_id="456")
```

**Rules:**
- Jobs must have valid customer references
- Invoices must have valid job references
- Payments must reference valid invoices

### Idempotency Invariants
Duplicate prevention:

```python
from brain.invariants.idempotency_invariants import IdempotencyInvariants

idempotency = IdempotencyInvariants()

# Check for duplicate operations
is_duplicate = idempotency.check_duplicate(
    operation="InvoiceCreate",
    key="INV-2026-001"
)

# Record operation for future checks
idempotency.record(operation="InvoiceCreate", key="INV-2026-001")
```

**Rules:**
- No duplicate invoice numbers
- No duplicate payment references
- No duplicate job references

---

## Invariant Checker

Main checker orchestrates all invariant checks:

```python
from brain.invariants.checker import InvariantChecker

checker = InvariantChecker()

# Run all invariants for an entity
violations = checker.check_all(
    entity_type="invoice",
    entity_id="123"
)

# Check specific invariant
result = checker.check("money.invoice_total", invoice_id="123")

# Get violation score
score = checker.get_violation_score(violations)
```

---

## Violation Scoring

The scorer assigns severity to violations:

```python
from brain.invariants.scorer import InvariantScorer

scorer = InvariantScorer()

# Score violations
score = scorer.score(violations)

# Get severity level
severity = scorer.get_severity(score)
# Returns: "LOW", "MEDIUM", "HIGH", "CRITICAL"
```

---

## Reconciliation

Use the reconciliation tool to fix violations:

```python
from brain.tools.reconciliation_tools import ReconcileInvariantsTool

tool = ReconcileInvariantsTool()
result = tool.run({
    "entity_type": "invoice",
    "entity_id": "123",
    "auto_fix": True
})
```

---

## Cross-References

| Topic | File |
|-------|------|
| Invariant specs | `brain/design/03_invariants.md` |
| Reconciliation tool | `brain/tools/reconciliation_tools.py` |
| Immune system | `brain/immune/README.md` |

---

**Last Updated:** February 2026