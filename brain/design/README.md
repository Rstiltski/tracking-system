# Brain Architecture Documentation

**Rule:** Do not use scripts to edit code.

**System Status:** Under Repair
*The core Brain architecture is sound, but some tools may be missing underlying database queries.*

## TABLE OF CONTENTS

| # | Section | Purpose |
|---|---------|---------|
| 1 | Integrity Warning | Hollow tool check procedure |
| 2 | Architecture Overview | System diagram |
| 3 | Command Flow | 10-step request lifecycle |
| 4 | Phase 0 Criteria | Design phase checklist |
| 5 | Current Status | Implementation state |

## DESIGN DOCUMENT INDEX

| File | Content | Lines |
|------|---------|-------|
| `00_command_namespace.md` | All 130+ commands by domain | Reference |
| `01_state_machines.md` | State transitions (Job, Invoice, Quote, Payment) | Spec |
| `02_policy_packs.md` | Validation policies (Security, Integrity) | Spec |
| `03_invariants.md` | Business rules that MUST always hold | Spec |
| `04_tool_contracts.md` | Tool input/output specifications | Spec |
| `05_risk_tiers.md` | Risk classification: Tier 1-5 | Reference |
| `06_audit_schema.md` | Audit log structure & fields | Spec |
| `07_roles_permissions.md` | RBAC: who can do what | Reference |

---

## §1 Integrity Warning (Hollow Tools)
The Brain's "Tool Registry" is fully populated, but some tools may fail at runtime because the database functions they call were stripped out.

**Before relying on a Tool:**
1. Check `brain/tools/[tool_name].py`.
2. Find the `db.*` call it makes.
3. Verify that function exists in `database/queries/`.

## §2 Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                         Streamlit UI                             │
│                    (Views + Components)                          │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
                    ┌────────────────┐
                    │  CommandEvent  │  ← User intent as structured data
                    └────────┬───────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│                          BRAIN                                   │
│                                                                   │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐    │
│  │  Router  │──▶│ Policies │──▶│  State   │──▶│ Planner  │    │
│  │          │   │          │   │ Machine  │   │          │    │
│  └──────────┘   └──────────┘   └──────────┘   └──────────┘    │
│                                                      │           │
│                                                      ▼           │
│                                              ┌──────────────┐   │
│                                              │  Tool Layer  │   │
│                                              └──────┬───────┘   │
│                                                      │           │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │              Audit Log (append-only)                      │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                             │
                             ▼
                    ┌────────────────┐
                    │   Tool Layer   │  ← Wraps db.py functions
                    └────────┬───────┘
                             │
                             ▼
                    ┌────────────────┐
                    │   Database     │
                    │ (SQLite/Postgres)
                    └────────────────┘
```

## §3 Command Flow

1. **UI** creates a `CommandEvent` (e.g., `InvoiceCreate`)
2. **Router** validates structure and routes to handler
3. **Policies** check preconditions (Integrity, Security, etc.)
4. **State Machine** validates transitions (if applicable)
5. **Planner** generates execution plan (list of tool calls)
6. **Risk Checker** determines if confirmation needed
7. If high-risk → **Fork Engine** runs dry-run, returns diff to UI
8. UI displays diff → user confirms → Brain executes
9. **Tool Layer** executes plan (wrapped db.* calls)
10. **Audit Log** records command, plan, results, errors

## §4 Phase 0 Success Criteria

- [x] All commands identified and categorized (130 commands across 10 domains)
- [x] State machines fully specified with transition tables (Job, Invoice, Payment, Quote, Message)
- [x] All policies defined with clear preconditions (Security, Integrity, Scheduling, Comms)
- [x] All invariants documented with enforcement strategies (Money, Linking, Idempotency, Evidence, Temporal)
- [x] All tools have typed contracts (input/output/errors) (18 core tools defined, 70 total planned)
- [x] Risk tiers assigned to every command (Tier 1-5 classification)
- [x] Audit schema supports full replay (Event sourcing ready)
- [x] Roles and permissions mapped to commands (Architect, Admin, Staff, ReadOnly)
- [x] Design documentation complete (5,140 lines across 9 files)

## §5 Current Status

The Brain architecture is implemented and functional. See individual files for current state.

**See [ROADMAP.md](../../ROADMAP.md) for project tracking.**

## §6 Next Steps

**Phase 2: State Machines & Invariants** (Ready to Start)
1. Implement state machine engine (5 state machines)
2. Add state transition validation
3. Enforce preconditions and side effects
4. Implement invariants checking (25 rules)
5. Create reconciliation jobs

**Estimated Duration:** 2-3 days
**Priority:** HIGH

## §7 References

- **[Main Roadmap](../../ROADMAP.md)** - Complete project tracking and status
- **[Phase 0 Summary](../../PHASE_0_SUMMARY.md)** - Design phase details
- **[Phase 1 Summary](../../PHASE_1_SUMMARY.md)** - Core implementation details
- **[Phase 1.5 Summary](../../PHASE_1.5_SUMMARY.md)** - Financial tools implementation
- Current codebase: `db.py` (95+ database functions)
- Current UI: `app.py` + `views/` (15+ pages)

---

**Last Updated:** 2026-01-26
**Maintained By:** Architect
