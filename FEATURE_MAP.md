# 📍 Feature Map - TrackLife Tracking System

**Feature-to-file mapping for developers and LLMs.**

---

## 🧭 Quick Navigation

| Want to... | Go to... |
|------------|----------|
| **Get started** | [GETTING_STARTED.md](GETTING_STARTED.md) |
| **Understand rules** | [PROJECT_RULES.md](PROJECT_RULES.md) |
| **See research** | [docs/research/](docs/research/) |
| **Read Brain docs** | [brain/README.md](brain/README.md) |

---

## TABLE OF CONTENTS

| # | Section | Key Info |
|---|---------|----------|
| 1 | Overview | How to use this map |
| 2 | Documentation | Docs structure |
| 3 | Frontend Features | UI components |
| 4 | Backend Features | Brain system |
| 5 | Database | Data layer |
| 6 | Configuration | Settings files |

---

## §1 Overview

This document maps features to their implementation files. Use it to quickly find where functionality is implemented.

### For LLMs

When using this map:
1. **Start with the feature type** - Identify what category the feature belongs to
2. **Find the file** - Use the tables to locate implementation files
3. **Check related files** - Look for dependencies and integration points
4. **Read the docs** - Check `docs/` for specifications and guides

---

## §2 Documentation Structure

### Core Documentation
| Document | Purpose | When to Use |
|----------|---------|-------------|
| `README.md` | Project overview | First time, quick reference |
| `GETTING_STARTED.md` | Setup & workflow | Starting work, onboarding |
| `PROJECT_RULES.md` | Rules & conventions | Before any coding |
| `FEATURE_MAP.md` | This file | Finding feature locations |
| `ROADMAP.md` | Development phases | Planning features |
| `TODO.md` | Current tasks | Checking priorities |

### Research Documentation (`docs/research/`)
| Document | Content | When to Use |
|----------|---------|-------------|
| `RESEARCH_SUMMARY.md` | Overview of all research | Understanding the big picture |
| `BEHAVIORAL_SCIENCE.md` | Habit formation science | Building habit features |
| `TECHNICAL_ARCHITECTURES.md` | System architectures | Architecture decisions |
| `OPEN_SOURCE_PROJECTS.md` | Similar project analysis | Feature inspiration |
| `AI_AND_PREDICTION.md` | AI and prediction features | Adding AI features |

### Specification Documents (`docs/specs/`)
| Document | Content | When to Use |
|----------|---------|-------------|
| `HABIT_SCORE_SPEC.md` | Habit scoring algorithm | Modifying habit scoring |

### Schema Documents (`docs/schemas/`)
| Document | Content | When to Use |
|----------|---------|-------------|
| `EVENT_SCHEMA.md` | Event sourcing schema | Adding event logging |

### Guide Documents (`docs/guides/`)
| Document | Content | When to Use |
|----------|---------|-------------|
| `INDEXEDDB_MIGRATION.md` | Storage migration | Upgrading storage layer |

### Phase Documents (`phases/`)
| Document | Content | When to Use |
|----------|---------|-------------|
| `PHASE_1_FOUNDATION.md` | Foundation phase details | Understanding base architecture |

---

## §2 Frontend Features

### Dashboard
| Feature | File | Description |
|---------|------|-------------|
| Main UI | `index.html` | Main HTML entry point |
| App Controller | `js/app.js` | Main application controller |
| Charts | `js/charts.js` | Chart visualization |
| Notifications | `js/notifications.js` | Notification system |

### Habits Tracker
| Feature | File | Description |
|---------|------|-------------|
| Habits Module | `js/habits.js` | Habits tracking logic |
| Streaks | `js/habits.js` | Streak counter |
| Completion | `js/habits.js` | Habit completion logging |

### Tasks & Todos
| Feature | File | Description |
|---------|------|-------------|
| Tasks Module | `js/tasks.js` | Tasks/Todos logic |
| Priorities | `js/tasks.js` | Priority handling |
| Filtering | `js/tasks.js` | Status filtering |

### Finances & Budget
| Feature | File | Description |
|---------|------|-------------|
| Finances Module | `js/finances.js` | Financial tracking |
| Budget | `js/finances.js` | Budget monitoring |
| Charts | `js/charts.js` | Expense visualization |

### Health Metrics
| Feature | File | Description |
|---------|------|-------------|
| Health Module | `js/health.js` | Health metrics logic |
| Weight Tracking | `js/health.js` | Weight charts |
| Mood Tracking | `js/health.js` | Mood selector |

### Time & Productivity
| Feature | File | Description |
|---------|------|-------------|
| Time Module | `js/time.js` | Time tracking |
| Timer | `js/time.js` | Stopwatch functionality |
| Categories | `js/time.js` | Time categorization |

### Goals & Progress
| Feature | File | Description |
|---------|------|-------------|
| Goals Module | `js/goals.js` | Goals tracking |
| Progress Bars | `js/goals.js` | Visual progress |
| Deadlines | `js/goals.js` | Deadline management |

### Gamification
| Feature | File | Description |
|---------|------|-------------|
| Achievements | `js/achievements.js` | Achievement system |
| XP System | `js/achievements.js` | XP and levels |
| Celebrations | `js/achievements.js` | Confetti effects |

### Data Management
| Feature | File | Description |
|---------|------|-------------|
| Storage | `js/storage.js` | LocalStorage layer |
| Export/Import | `js/dataExport.js` | Data portability |

### Styling
| Feature | File | Description |
|---------|------|-------------|
| Styles | `css/styles.css` | All CSS styles |
| Dark Mode | `css/styles.css` | Theme switching |

---

## §3 Backend Features (Brain System)

### Core Components
| Feature | File | Description |
|---------|------|-------------|
| Brain Core | `brain/core/brain.py` | Main orchestration |
| Router | `brain/core/router.py` | Command routing |
| Result Types | `brain/core/result.py` | Result structures |
| Tool Base | `brain/core/tool.py` | Tool base class |
| Guardrails | `brain/core/guardrails.py` | Safety middleware |
| Events | `brain/core/events.py` | Event system |
| Enums | `brain/core/enums.py` | Risk tiers, status codes |

### Tools (100+)
| Category | File | Tools |
|----------|------|-------|
| Job Management | `brain/tools/job_tools.py` | CreateJob, UpdateJob, DeleteJob |
| Customer | `brain/tools/customer_tools.py` | Customer CRUD |
| Financial | `brain/tools/financial_tools.py` | Invoices, payments |
| Scheduling | `brain/tools/scheduling_tools.py` | Scheduling operations |
| Communication | `brain/tools/communication_tools.py` | Messaging |
| Materials | `brain/tools/materials_tools.py` | Inventory |
| Time Tracking | `brain/tools/time_tracking_tools.py` | Clock in/out |
| Portal | `brain/tools/portal_tools.py` | Customer portal |
| Admin | `brain/tools/admin_tools.py` | Admin operations |
| Audit | `brain/tools/audit_tools.py` | Audit queries |
| Bulk Ops | `brain/tools/bulk_operations.py` | Bulk actions |
| Delete | `brain/tools/delete_tools.py` | Safe deletion |
| Quotes | `brain/tools/quote_tools.py` | Quote management |
| Crew | `brain/tools/crew_management_tools.py` | Staff management |
| Reconciliation | `brain/tools/reconciliation_tools.py` | Financial reconciliation |
| Recurring Jobs | `brain/tools/recurring_job_tools.py` | Recurring schedules |
| Job Actuals | `brain/tools/job_actuals_tools.py` | Actual vs estimated |
| Job Extensions | `brain/tools/job_extensions.py` | Job extras |
| Job Customer | `brain/tools/job_customer_tools.py` | Job-customer linking |
| Expense/Credit | `brain/tools/expense_credit_tools.py` | Expenses and credits |
| Misc | `brain/tools/misc_tools.py` | Miscellaneous |
| Registry | `brain/tools/registry.py` | Tool registration |

### Policies
| Feature | File | Description |
|---------|------|-------------|
| Policy Engine | `brain/policies/engine.py` | Policy orchestration |
| Security | `brain/policies/security.py` | Auth policies |
| Integrity | `brain/policies/integrity.py` | Data integrity |
| Scheduling | `brain/policies/scheduling.py` | Scheduling rules |
| Communications | `brain/policies/communications.py` | Message limits |

### State Machines
| Entity | File | States |
|--------|------|--------|
| Jobs | `brain/state/job_machine.py` | DRAFT → COMPLETED |
| Invoices | `brain/state/invoice_machine.py` | DRAFT → PAID |
| Payments | `brain/state/payment_machine.py` | PENDING → COMPLETED |
| Quotes | `brain/state/quote_machine.py` | DRAFT → CONVERTED |
| Manager | `brain/state/manager.py` | State coordination |

### Audit System
| Feature | File | Description |
|---------|------|-------------|
| Logger | `brain/audit/logger.py` | Audit logging |
| Schema | `brain/audit/schema.py` | Audit schema |

### Security
| Feature | File | Description |
|---------|------|-------------|
| Crypto | `brain/security/crypto_engine.py` | Encryption |
| Neural Link | `brain/security/neural_link.py` | Secure channel |
| Export Guard | `brain/security/export_guard.py` | Data protection |
| AI Policy | `brain/security/ai_policy_enforcer.py` | AI operation policies |

### Invariants
| Feature | File | Description |
|---------|------|-------------|
| Checker | `brain/invariants/checker.py` | Invariant verification |
| Money | `brain/invariants/money_invariants.py` | Financial rules |
| Linking | `brain/invariants/linking_invariants.py` | Relationship rules |
| Idempotency | `brain/invariants/idempotency_invariants.py` | Duplicate prevention |
| Scorer | `brain/invariants/scorer.py` | Invariant scoring |

### Immune System
| Feature | File | Description |
|---------|------|-------------|
| Fingerprinter | `brain/immune/fingerprinter.py` | Code fingerprinting |
| Homeostasis | `brain/immune/homeostasis.py` | System balance |
| Quarantine | `brain/immune/quarantine.py` | Problem isolation |
| Memory Monitor | `brain/immune/memory_monitor.py` | Memory management |
| Worker | `brain/immune/worker.py` | Background processing |

### Privacy
| Feature | File | Description |
|---------|------|-------------|
| Tokenizer | `brain/privacy/tokenizer.py` | Data tokenization |
| Vault | `brain/privacy/vault.py` | Secure storage |

### Fork Engine
| Feature | File | Description |
|---------|------|-------------|
| Engine | `brain/fork/engine.py` | Dry-run execution |
| Confirmation | `brain/fork/confirmation.py` | Confirmation tokens |

### Specialized Brains
| Brain | File | Purpose |
|-------|------|---------|
| Ops | `brain/brains/ops_brain.py` | Operations |
| Finance | `brain/brains/finance_brain.py` | Financial operations |
| Relation | `brain/brains/relation_brain.py` | Relationships |
| Diagnosis | `brain/brains/diagnosis_brain.py` | Diagnostics |
| Repair | `brain/brains/repair_brain.py` | Self-repair |
| Scanner | `brain/brains/scanner_brain.py` | Code scanning |
| Test | `brain/brains/test_brain.py` | Testing |
| Validator | `brain/brains/validator_brain.py` | Validation |
| Meta | `brain/brains/meta_brain.py` | Meta-operations |
| Docs | `brain/brains/docs_brain.py` | Documentation |

---

## §4 Database

### Connection & Queries
| Feature | File | Description |
|---------|------|-------------|
| Connection | `landscaping_new/database/connection.py` | DB connection |
| Init | `landscaping_new/database/__init__.py` | Database init |
| Queries | `landscaping_new/database/queries/` | Query modules |

### Schema
| Feature | File | Description |
|---------|------|-------------|
| Database File | `landscaping_new/landscaping.db` | SQLite database |
| DB Facade | `landscaping_new/db.py` | Database switchboard |

---

## §5 Configuration

| Config | File | Description |
|--------|------|-------------|
| Project Rules | `PROJECT_RULES.md` | Development guidelines |
| Design Doc | `TRACKING_SYSTEM_DESIGN.md` | Architecture design |
| TODO | `TODO.md` | Project tracking |
| Workspace | `tracking-system.code-workspace` | VS Code workspace |

---

## Quick Reference

### By Feature Type

**Want to add a new tool?**
→ `brain/tools/` and register in `brain/tools/registry.py`

**Want to add a new policy?**
→ `brain/policies/` and add to `brain/policies/engine.py`

**Want to add a new state machine?**
→ `brain/state/` and register in `brain/state/manager.py`

**Want to add a new UI page?**
→ `js/` for frontend modules or `landscaping_new/app/pages/` for Streamlit

**Want to modify database queries?**
→ `landscaping_new/database/queries/`

**Want to understand the architecture?**
→ `brain/design/` for design documents

---

## Cross-References

| Document | Content |
|----------|---------|
| [README.md](README.md) | Full documentation |
| [brain/README.md](brain/README.md) | Brain system details |
| [PROJECT_RULES.md](PROJECT_RULES.md) | Development guidelines |
| [TRACKING_SYSTEM_DESIGN.md](TRACKING_SYSTEM_DESIGN.md) | Architecture design |

---

**Last Updated:** February 2026