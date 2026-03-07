# 🧠 Specialized Brains - Domain-Specific Intelligence

**Specialized brain modules for different domains.**

---

## Overview

The `brain/brains/` directory contains specialized brain modules that handle domain-specific operations. Each brain focuses on a particular area of functionality.

---

## Available Brains

| File | Purpose |
|------|---------|
| `ops_brain.py` | Operations - job management, scheduling |
| `finance_brain.py` | Financial operations - invoices, payments |
| `relation_brain.py` | Relationships - customers, contacts |
| `diagnosis_brain.py` | Diagnostics - system health analysis |
| `repair_brain.py` | Self-repair - automatic issue fixing |
| `scanner_brain.py` | Code scanning - analysis and detection |
| `test_brain.py` | Testing - test execution and validation |
| `validator_brain.py` | Validation - data and rule verification |
| `meta_brain.py` | Meta-operations - brain introspection |
| `docs_brain.py` | Documentation - doc generation and lookup |

---

## Brain Architecture

Each specialized brain follows a consistent pattern:

```python
class SpecializedBrain:
    """Domain-specific brain for [domain]."""
    
    def __init__(self, cerebellum, nervous_system, db_connection):
        self.cerebellum = cerebellum
        self.nervous_system = nervous_system
        self.db = db_connection
    
    def process(self, command):
        """Process a command in this domain."""
        pass
    
    def validate(self, params):
        """Validate parameters for this domain."""
        pass
```

---

## Ops Brain

Handles operational tasks:

```python
from brain.brains.ops_brain import OpsBrain

ops = OpsBrain(cerebellum, nervous_system, db)

# Job operations
ops.process({"action": "schedule_job", "job_id": "123", "date": "2026-02-20"})

# Resource allocation
ops.process({"action": "allocate_resources", "job_id": "123"})
```

**Capabilities:**
- Job scheduling
- Resource allocation
- Crew assignment
- Status updates

---

## Finance Brain

Handles financial operations:

```python
from brain.brains.finance_brain import FinanceBrain

finance = FinanceBrain(cerebellum, nervous_system, db)

# Invoice operations
finance.process({"action": "create_invoice", "customer_id": "456"})

# Payment processing
finance.process({"action": "record_payment", "invoice_id": "789", "amount": 150.00})
```

**Capabilities:**
- Invoice creation and management
- Payment processing
- Financial reporting
- Credit note handling

---

## Relation Brain

Handles relationships:

```python
from brain.brains.relation_brain import RelationBrain

relations = RelationBrain(cerebellum, nervous_system, db)

# Customer operations
relations.process({"action": "link_contact", "customer_id": "123", "contact_id": "456"})
```

**Capabilities:**
- Customer management
- Contact linking
- Relationship mapping

---

## Diagnosis Brain

System diagnostics:

```python
from brain.brains.diagnosis_brain import DiagnosisBrain

diagnosis = DiagnosisBrain(cerebellum, nervous_system, db)

# Run diagnostics
report = diagnosis.run_full_diagnosis()

# Check specific component
status = diagnosis.check_component("database")
```

**Capabilities:**
- System health checks
- Performance analysis
- Error detection
- Status reporting

---

## Repair Brain

Self-repair capabilities:

```python
from brain.brains.repair_brain import RepairBrain

repair = RepairBrain(cerebellum, nervous_system, db)

# Auto-repair detected issues
repair.fix_issue(issue_id="abc123")

# Validate repairs
repair.validate_fix(issue_id="abc123")
```

**Capabilities:**
- Automatic issue detection
- Self-healing operations
- Data reconciliation
- Integrity restoration

---

## Scanner Brain

Code and data scanning:

```python
from brain.brains.scanner_brain import ScannerBrain

scanner = ScannerBrain(cerebellum, nervous_system, db)

# Scan for issues
results = scanner.scan_codebase()

# Find patterns
matches = scanner.find_pattern("deprecated_function")
```

**Capabilities:**
- Code analysis
- Pattern detection
- Anomaly identification
- Security scanning

---

## Test Brain

Testing operations:

```python
from brain.brains.test_brain import TestBrain

tester = TestBrain(cerebellum, nervous_system, db)

# Run tests
results = tester.run_suite("unit")

# Validate functionality
validation = tester.validate_feature("invoicing")
```

**Capabilities:**
- Test execution
- Result validation
- Coverage analysis
- Regression detection

---

## Validator Brain

Data validation:

```python
from brain.brains.validator_brain import ValidatorBrain

validator = ValidatorBrain(cerebellum, nervous_system, db)

# Validate data
result = validator.validate({"customer": customer_data})

# Check business rules
violations = validator.check_rules(entity_type="invoice", data=invoice_data)
```

**Capabilities:**
- Schema validation
- Business rule checking
- Data integrity verification
- Constraint validation

---

## Meta Brain

Brain introspection:

```python
from brain.brains.meta_brain import MetaBrain

meta = MetaBrain(cerebellum, nervous_system, db)

# Get brain status
status = meta.get_status()

# List capabilities
capabilities = meta.list_capabilities()
```

**Capabilities:**
- Self-introspection
- Capability listing
- Status monitoring
- Configuration management

---

## Docs Brain

Documentation operations:

```python
from brain.brains.docs_brain import DocsBrain

docs = DocsBrain(cerebellum, nervous_system, db)

# Generate documentation
docs.generate_for_tool("CreateJob")

# Look up documentation
info = docs.lookup("InvoiceCreate")
```

**Capabilities:**
- Documentation generation
- API reference lookup
- Example generation
- Schema documentation

---

## Creating a New Brain

1. Create the brain file in `brain/brains/`
2. Implement the standard interface
3. Register with the main brain

```python
# brain/brains/my_brain.py
from brain.core.result import BrainResult

class MyBrain:
    """Brain for my domain."""
    
    def __init__(self, cerebellum, nervous_system, db_connection):
        self.cerebellum = cerebellum
        self.nervous_system = nervous_system
        self.db = db_connection
    
    def process(self, command: dict) -> BrainResult:
        """Process a command."""
        # Implementation
        return BrainResult(success=True, data={})
    
    def validate(self, params: dict) -> bool:
        """Validate parameters."""
        # Implementation
        return True
```

---

## Cross-References

| Topic | File |
|-------|------|
| AI entry point | `../AI_START_HERE.md` |
| Security playbook | `../SECURITY_PLAYBOOK.md` |
| Core brain | `brain/core/README.md` |
| Tools | `brain/tools/README.md` |
| Policies | `brain/policies/README.md` |

---

**Last Updated:** March 2026
