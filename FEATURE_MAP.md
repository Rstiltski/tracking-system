# 📍 Feature Map - Veryfyn Tracking System

**Feature-to-file mapping for developers.**

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

---

## §2 Documentation Structure

### Core Documentation
| Document | Purpose | When to Use |
|----------|---------|-------------|
| `AI_START_HERE.md` | AI entry point | Start here for AI context |
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

## §3 Frontend Features (Python-First)

### Main Application (Streamlit)
| Feature | File | Description |
|---------|------|-------------|
| Main Entry | `run.py` | Primary script to launch the app |
| App Main | `tracking_app/app.py` | Streamlit application entry point |
| Design System| `tracking_app/design/theme.py`| Glassmorphism & custom styling |
| Sidebar | `tracking_app/components/sidebar.py`| Dynamic categorized navigation |

### ⚠️ Legacy Frontend (JavaScript/HTML)
**Status:** Deprecated. Maintained for reference only.
| Feature | File | Description |
|---------|------|-------------|
| Legacy HTML | `index.html` | Old HTML entry point |
| Legacy Controller| `js/app.js` | Old JS application controller |

### Core Tracking Pages (Streamlit)
| Feature | File | Description |
|---------|------|-------------|
| Dashboard | `tracking_app/pages/dashboard.py` | Main overview and metrics |
| Habits | `tracking_app/pages/habits.py` | Habit tracking & engineering |
| Tasks | `tracking_app/pages/tasks.py` | Task & Todo management |
| Finances | `tracking_app/pages/finances.py` | Budget & transaction tracking |
| Health | `tracking_app/pages/health.py` | Health & mood metrics |
| Time | `tracking_app/pages/time.py` | Timer & time entry tracking |
| Goals | `tracking_app/pages/goals.py` | Goal setting & progress |

---

## §3.5 Decoupled API Backend (Phase 13)

**Status:** 🟡 **In Progress** - Backend complete, React frontend ~10% complete

**Architecture Note:** Phase 13 FastAPI backend is an **API layer** that calls `tracking_app/storage.py` directly. It does NOT duplicate business logic.

### FastAPI Server
| Feature | File | Description |
|---------|------|-------------|
| Main App | `backend/main.py` | FastAPI app with CORS, routers, health check |
| Config | `backend/config.py` | Settings using pydantic-settings |

### API Routes (All call tracking_app/storage.py)
| Feature | File | Description |
|---------|------|-------------|
| Habits CRUD | `backend/routes/habits.py` | GET/POST/PUT/DELETE habits → calls storage.py |
| Tasks CRUD | `backend/routes/tasks.py` | GET/POST/PUT/DELETE tasks + completion → calls storage.py |
| Goals CRUD | `backend/routes/goals.py` | GET/POST/PUT/DELETE goals + progress → calls storage.py |
| Health CRUD | `backend/routes/health.py` | GET/POST/PUT/DELETE health entries → calls storage.py |
| Time Tracking | `backend/routes/time.py` | Timer + time entries → calls storage.py |
| Finances | `backend/routes/finances.py` | Transactions + budget → calls storage.py |

### API Schemas (Pydantic)
| Feature | File | Description |
|---------|------|-------------|
| Habits Schemas | `backend/schemas/habits.py` | HabitRequest, HabitResponse |
| Tasks Schemas | `backend/schemas/tasks.py` | TaskRequest, TaskResponse |
| Goals Schemas | `backend/schemas/goals.py` | GoalRequest, GoalResponse |
| Health Schemas | `backend/schemas/health.py` | HealthRequest, HealthResponse |
| Time Schemas | `backend/schemas/time.py` | TimeEntryRequest, TimerResponse |
| Finances Schemas | `backend/schemas/finances.py` | TransactionRequest, BudgetResponse |

### React Frontend
| Feature | File | Description | Status |
|---------|------|-------------|--------|
| Main App | `frontend/src/App.jsx` | React app with navigation | ✅ Complete |
| Habits View | `frontend/src/App.jsx` | Habit tracking UI (CRUD) | ✅ Complete |
| Tasks View | `frontend/src/App.jsx` | Task management UI (CRUD) | ✅ Complete |
| Time View | `frontend/src/App.jsx` | Time tracking UI (entries) | ✅ Complete |
| Finances View | `frontend/src/App.jsx` | Financial tracking UI | ✅ Complete |
| Goals View | NOT IMPLEMENTED | Goal tracking UI | ❌ Not Started |
| Health View | NOT IMPLEMENTED | Health metrics UI | ❌ Not Started |
| Dashboard | `frontend/src/App.jsx` | Overview dashboard | ⚠️ Placeholder Only |

**Note:** React frontend has only 4 basic CRUD views (~10% of Streamlit's 32+ pages)

---

## §4 Backend Features (Brain System)

### ⚠️ Architecture Clarification

**The Brain is NOT the data backend.** The Brain is an **intelligence layer** for AI/ML analytics.

| Layer | Purpose | Files |
|-------|---------|-------|
| **📦 Data Backend** | Data persistence & CRUD | `tracking_app/storage.py`, `models.py`, `database.py` |
| **🧠 Intelligence Layer** | AI/ML analytics | `brain/analysis/`, `brain/behavioral/`, `brain/notifications/` |
| **⚠️ Brain Core** | Business SaaS commands | `brain/core/` (over-engineered for personal tracking) |

**For simple CRUD:** Use `tracking_app/storage.py` directly

**For AI analytics:** Use `brain/analysis/` or `brain/behavioral/`

### Core Components
| Feature | File | Description |
|---------|------|-------------|
| Brain Core | `brain/core/brain.py` | Main orchestration (⚠️ over-engineered) |
| Router | `brain/core/router.py` | Command routing |
| Result Types | `brain/core/result.py` | Result structures |
| Tool Base | `brain/core/tool.py` | Tool base class |
| Guardrails | `brain/core/guardrails.py` | Safety middleware |
| Events | `brain/core/events.py` | Event system |
| Enums | `brain/core/enums.py` | Risk tiers, status codes |

### Tools (100+) - ⚠️ FOR BUSINESS SAAS, NOT PERSONAL TRACKING

**Note:** These tools are for a **landscaping business management system**, not personal habit tracking.

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
| Security Playbook | `brain/SECURITY_PLAYBOOK.md` | Security protocols & audit requirements |

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

## §5 Database

### Connection & Queries
| Feature | File | Description |
|---------|------|-------------|
| Connection | `database/connection.py` | DB connection |
| Init | `database/__init__.py` | Database init |
| Queries | `database/queries/` | Query modules |

### Schema
| Feature | File | Description |
|---------|------|-------------|
| Database File | `tracking.db` | SQLite database |
| DB Facade | `db.py` | Database switchboard |

---

## §6 Configuration

| Config | File | Description |
|--------|------|-------------|
| Project Rules | `PROJECT_RULES.md` | Development guidelines |
| Design Doc | `TRACKING_SYSTEM_DESIGN.md` | Architecture design |
| TODO | `TODO.md` | Project tracking |
| Workspace | `veryfyn.code-workspace` | VS Code workspace |

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
→ `js/` for frontend modules or `tracking_app/pages/` for Streamlit

**Want to modify database queries?**
→ `database/queries/`

**Want to understand the architecture?**
→ `brain/design/` for design documents

---

## Phase 11 Features (Complete!)

### Phase 11.1: Foundation + Safeguards
| Feature | Model File | UI File |
|---------|------------|----------|
| Orthorexia Safeguards | `brain/models/disordered_patterns.py` | `tracking_app/components/healthy_tracking_guardrails.py` |
| Privacy Dashboard | `brain/models/privacy_preferences.py` | `tracking_app/pages/privacy_dashboard.py` |
| Data Minimization | `brain/models/data_audit.py` | `brain/policies/data_minimization.py` |
| Growth Mindset | `brain/models/mindset.py` | `tracking_app/components/mindset_interventions.py` |
| Eudaemonic Motivation | `brain/models/motivation.py` | `tracking_app/pages/purpose_tracker.py` |
| Ego-Depletion Detection | `brain/models/ego_depletion.py` | `tracking_app/components/rest_prompts.py` |
| Fixed Mindset Detection | `brain/models/fixed_mindset.py` | `tracking_app/components/challenge_scaler.py` |
| 4-Day Momentum | `brain/models/momentum.py` | `tracking_app/components/momentum_counter.py` |

### Phase 11.2: High Impact Features
| Feature | Model File | UI File |
|---------|------------|----------|
| Identity Integration | `brain/models/identity.py` | `tracking_app/pages/identity.py` |
| Energy Management | `brain/models/energy.py` | `tracking_app/pages/energy.py` |
| Commitment Devices | `brain/models/commitment.py` | `tracking_app/pages/commitments.py` |
| Dopamine Menu | `brain/models/dopamine_menu.py` | `tracking_app/components/dopamine_menu.py` |
| Spiritual Tracking | `brain/models/spiritual.py` | `tracking_app/pages/spiritual.py` |
| Gratitude Practice | `brain/models/gratitude.py` | `tracking_app/pages/gratitude.py` |
| Data Audit Trail | `brain/models/data_audit.py` | - |
| Privacy Preferences | `brain/models/privacy_preferences.py` | `tracking_app/pages/privacy_dashboard.py` |
| Scarcity Mindset | `brain/models/scarcity.py` | `tracking_app/pages/abundance.py` |
| Partner Tracking | `brain/models/dyadic.py` | `tracking_app/pages/partners.py` |
| Social Safeguards | `brain/models/social_safeguards.py` | `tracking_app/pages/social.py` |
| Self-Monitoring Fatigue | `brain/models/self_monitoring_fatigue.py` | `tracking_app/components/self_monitoring_fatigue.py` |

### Phase 11.3: Enhanced Support
| Feature | Model File |
|---------|------------|
| Passive Tracking | `brain/models/passive_tracking.py` |
| Identity Reconstruction | `brain/models/identity_reconstruction.py` |
| N-of-1 Experiments | `brain/models/experiments.py` |
| Attachment Theory | `brain/models/attachment.py` |
| Dual Citizen Co-Creation | `brain/models/dual_citizen.py` |
| Self-Gaming Detection | `brain/models/self_gaming.py` |
| Biographical Disruption | `brain/models/biographical_disruption.py` |
| Streak Optimization | `brain/models/streak_optimization.py` |
| Micro/Macro Hole Response | `brain/models/hole_response.py` |
| Invisible Data Validation | `brain/models/invisible_validation.py` |

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