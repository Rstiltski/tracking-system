# 🛡️ Immune System - Self-Healing & Protection

**The system's immune response for self-healing and protection.**

---

## Overview

The `brain/immune/` directory implements the system's immune system - a collection of components that monitor system health, detect anomalies, and automatically repair issues.

---

## Components

| File | Purpose |
|------|---------|
| `fingerprinter.py` | Code fingerprinting for change detection |
| `homeostasis.py` | System balance and equilibrium |
| `quarantine.py` | Problem isolation and containment |
| `memory_monitor.py` | Memory usage monitoring |
| `worker.py` | Background processing for immune tasks |

---

## Key Features

### Fingerprinter
Detects changes in code and data:

```python
from brain.immune.fingerprinter import Fingerprinter

fingerprinter = Fingerprinter()

# Generate fingerprint
fp = fingerprinter.fingerprint_file("brain/core/brain.py")

# Check for changes
if fingerprinter.has_changed("brain/core/brain.py"):
    print("File has been modified")
```

### Homeostasis
Maintains system balance:

```python
from brain.immune.homeostasis import Homeostasis

homeostasis = Homeostasis()

# Check system balance
status = homeostasis.check_balance()

# Restore balance if needed
if not status.is_balanced:
    homeostasis.restore_balance()
```

### Quarantine
Isolates problematic components:

```python
from brain.immune.quarantine import Quarantine

quarantine = Quarantine()

# Quarantine a problematic component
quarantine.isolate("problematic_module")

# Check quarantine status
if quarantine.is_isolated("problematic_module"):
    print("Module is quarantined")

# Release from quarantine
quarantine.release("problematic_module")
```

### Memory Monitor
Tracks memory usage:

```python
from brain.immune.memory_monitor import MemoryMonitor

monitor = MemoryMonitor()

# Get memory stats
stats = monitor.get_stats()

# Check for memory pressure
if monitor.is_under_pressure():
    monitor.trigger_cleanup()
```

---

## Tests

Located in `brain/immune/tests/`:

| File | Tests |
|------|-------|
| `test_fingerprinter.py` | Fingerprinting functionality |
| `test_homeostasis.py` | Balance maintenance |
| `test_quarantine.py` | Isolation and containment |

Run tests:
```bash
python -m pytest brain/immune/tests/
```

---

## Cross-References

| Topic | File |
|-------|------|
| Core brain | `brain/core/README.md` |
| Invariants | `brain/invariants/README.md` |
| Repair brain | `brain/brains/repair_brain.py` |
| Security protocols | `brain/SECURITY_PLAYBOOK.md` |

---

**Last Updated:** February 2026