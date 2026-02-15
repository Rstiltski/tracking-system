# Tracking System Architecture Design

## Overview
This document outlines the architectural design for the Tracking System, inspired by the Brain architecture. It adapts core concepts such as Command Events, Router, Policies, State Machines, Tool Layer, Database, and Audit Log to the context of a personal tracking system.

## DESIGN DOCUMENT INDEX
| File | Content | Lines |
|------|---------|-------|
| `00_command_namespace.md` | All commands for tasks, goals, finances, habits | Reference |
| `01_state_machines.md` | State transitions for tracking entities | Spec |
| `02_policy_packs.md` | Validation policies (Security, Data Integrity) | Spec |
| `03_invariants.md` | Business rules that MUST always hold | Spec |
| `04_tool_contracts.md` | Tool input/output specifications | Spec |
| `05_risk_tiers.md` | Risk classification for commands | Reference |
| `06_audit_schema.md` | Audit log structure & fields | Spec |
| `07_roles_permissions.md` | RBAC: who can do what | Reference |

## §1 Integrity Warning
The Tracking System implements a strict command flow to ensure data integrity. All modifications go through the Tool Layer, which wraps database operations. Verify that any new database function exists in `storage.js` before use.

## §2 Architecture Overview
```
┌─────────────────────────────────────────────────────────────────┐
│                Tracking System UI (Views + Components)          │
└─────────────────────────────────────────────────────────────────┘
                              │
                              ▼
                     ┌────────────────┐
                     │ CommandEvent   │ ← User intent as structured data
                     └────────┬───────┘
                              │
                              ▼
   ┌─────────────────────────────────────────────────────────────────┐
   │                         TRACKING BRAIN                           │
   │                                                               │
   │  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐    │
   │  │  Router  │──▶│ Policies │──▶│  State   │──▶│ Planner  │    │
   │  │          │   │          │   │ Machine  │   │          │    │
   │  └──────────┘   └──────────┘   └──────────┘   └──────────┘    │
   │                                                               │
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
                     │   Database     │
                     │ (IndexedDB)    │
                     └────────────────┘
```
*The Brain architecture is implemented using existing JS modules:
  - `js/tasks.js`, `js/goals.js`, `js/finances.js`, `js/habits.js` as tool wrappers.
  - `js/storage.js` as the database layer.
  - `js/app.js` as the UI entry point.*

## §3 Command Flow
1. **UI** creates a `CommandEvent` (e.g., `TaskCreate`, `GoalUpdate`).
2. **Router** validates structure and routes to appropriate handler.
3. **Policies** check preconditions (e.g., authentication, data integrity).
4. **State Machine** validates transitions (e.g., a `Task` can move from `Pending` to `InProgress`).
5. **Planner** generates execution plan (list of tool calls).
6. **Risk Checker** determines if user confirmation needed (e.g., financial changes).
7. If high-risk → **Confirmation Dialog** runs, returns diff to UI.
8. UI displays diff → user confirms → Brain executes.
9. **Tool Layer** executes plan (wrapped functions in `storage.js`).
10. **Audit Log** records command, plan, results, errors.

## §4 Phase 0 Success Criteria
- [x] All command types identified: `Task*`, `Goal*`, `Finance*`, `Habit*`.
- [x] State machines defined for `Task`, `Goal`, `Finance`, `Habit`.
- [x] Policies defined: `DataIntegrity`, `AccessControl`.
- [x] Invariants documented: e.g., `Task.id` uniqueness, `Goal.totalWeight` sum consistency.
- [x] All tools have typed contracts (input/output/errors) in `storage.js`.
- [x] Risk tiers assigned to every command (Tier 1-5).
- [x] Audit schema supports full replay (Event sourcing ready).
- [x] Roles and permissions mapped: `User`, `Admin`.

## §5 Current Status
The Tracking System architecture is functional. See individual JS files for current implementation state.

**See `TODO.md` for project tracking.**

## §6 Next Steps
**Phase 1: Command Implementation** (In Progress)
1. Implement all `Task*` commands.
2. Add state transition validation.
3. Enforce preconditions and side effects.
4. Implement invariants checking (15 rules).
5. Create reconciliation jobs for consistency.

**Estimated Duration:** 1-2 days
**Priority:** HIGH