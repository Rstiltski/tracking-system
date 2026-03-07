# 🧠 NEURAL HUB - Central Cortex Entry Point

**The central nervous system hub that connects all neural pathways in the Veryfyn Tracking System.**

---

## 🎯 Purpose

This file serves as the **entry point** for AI navigation through the project. All neural pathways begin here, connecting to the master rule registry and the event bus.

---

## 🔗 Neural Synapses

### Primary Connections

| Region | Connection Type | Purpose | Target |
|--------|-----------------|---------|--------|
| **Rules Core** | 🔴 Motor | Master rule registry | [CORE_RULES.md](./CORE_RULES.md) |
| **Event Bus** | ⚡ Synaptic | Inter-brain communication | [nervous_system.py](./nervous_system.py) |
| **AI Protocol** | 🟣 Intelligence | AI thinking protocol | [AI_RULES.md](./AI_RULES.md) |

### Secondary Connections

| Region | Connection Type | Purpose | Target |
|--------|-----------------|---------|--------|
| **Project Entry** | ⚪ Entry | Main documentation | [README.md](../README.md) |
| **Project Rules** | 🟠 Logic | Detailed guidelines | [PROJECT_RULES.md](../PROJECT_RULES.md) |
| **Working Memory** | 💾 Storage | Session state | [session.json](../session.json) |
| **Long-term Memory** | 💾 Storage | Decision history | [decisions.log](../decisions.log) |
| **Synapse Registry** | 🔗 Map | Context mapping | [.context.md](../.context.md) |
| **Pattern Library** | 📋 Templates | Code patterns | [patterns/](../patterns/) |

---

## 🧭 Navigation Pathways

### Pathway 1: Start New Feature

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ NEURAL_HUB  │────▶│ CORE_RULES  │────▶│PROJECT_RULES│────▶│  patterns/  │
│  (You Here) │     │  (Rules)    │     │ (Guidelines)│     │ (Templates) │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

**Steps:**
1. Read [CORE_RULES.md](./CORE_RULES.md) - Load all project rules
2. Read [PROJECT_RULES.md](../PROJECT_RULES.md) - Detailed guidelines
3. Check [patterns/](../patterns/) - Reusable code patterns
4. Review [brain/rules/schema.py](./rules/schema.py) - Rule patterns

### Pathway 2: Debug Issue

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ NEURAL_HUB  │────▶│ CORE_RULES  │────▶│   immune/   │────▶│   audit/    │
│  (You Here) │     │  (Rules)    │     │(Self-Heal)  │     │   (Logs)    │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

**Steps:**
1. Read [CORE_RULES.md](./CORE_RULES.md) - Check GUARD_* and BRAIN_* rules
2. Read [brain/immune/](./immune/) - Self-healing system
3. Read [brain/core/guardrails.py](./core/guardrails.py) - Safety middleware
4. Read [brain/audit/](./audit/) - Audit logs

### Pathway 3: Plan Roadmap

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ NEURAL_HUB  │────▶│ CORE_RULES  │────▶│  roadmaps/  │────▶│   TODO.md   │
│  (You Here) │     │  (Rules)    │     │ (Strategy)  │     │   (Tasks)   │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

**Steps:**
1. Read [CORE_RULES.md](./CORE_RULES.md) - Check DOC_* rules
2. Read [docs/roadmaps/](../docs/roadmaps/) - Strategic plans
3. Read [TODO.md](../TODO.md) - Current tasks
4. Read [brain/ai/suggestion_engine.py](./ai/suggestion_engine.py) - AI insights

### Pathway 4: Add New Rule

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│ NEURAL_HUB  │────▶│ CORE_RULES  │────▶│rules/schema │────▶│  policies/  │
│  (You Here) │     │  (Rules)    │     │  (Schema)   │     │ (Policies)  │
└─────────────┘     └─────────────┘     └─────────────┘     └─────────────┘
```

**Steps:**
1. Read [CORE_RULES.md](./CORE_RULES.md) - Check VALID_* rules
2. Read [brain/rules/schema.py](./rules/schema.py) - Rule schema
3. Read [brain/rules/validator.py](./rules/validator.py) - Validation
4. Update [CORE_RULES.md](./CORE_RULES.md) - Register new rule

---

## ⚡ Event Bus Integration

The Neural Hub connects to the existing `nervous_system.py` event bus:

### Event Flow

```
┌─────────────────────────────────────────────────────────────────────────┐
│                          NEURAL HUB                                      │
│                      (Central Cortex)                                    │
└───────────────────────────────────┬─────────────────────────────────────┘
                                    │
                    ┌───────────────┴───────────────┐
                    │                               │
                    ▼                               ▼
        ┌─────────────────────┐         ┌─────────────────────┐
        │    CORE_RULES.md    │         │  nervous_system.py  │
        │   (Rule Registry)   │         │    (Event Bus)      │
        └─────────────────────┘         └──────────┬──────────┘
                                                   │
                    ┌──────────────────────────────┴──────────┐
                    │                                          │
                    ▼                                          ▼
        ┌─────────────────────┐                  ┌─────────────────────┐
        │     OpsBrain        │                  │    FinanceBrain     │
        │   (Operations)      │                  │    (Financial)      │
        └─────────────────────┘                  └─────────────────────┘
```

### Event Types (from nervous_system.py)

| Event | Emitter | Listener | Action |
|-------|---------|----------|--------|
| `JOB_COMPLETED` | OpsBrain | FinanceBrain | Create invoice |
| `JOB_COMPLETED` | OpsBrain | RelationBrain | Send thank you |
| `INVOICE_PAID` | FinanceBrain | RelationBrain | Send receipt |
| `QUOTE_ACCEPTED` | OpsBrain | OpsBrain | Convert to job |

---

## 🧠 Brain Regions

The Neural Hub connects to these brain regions:

### Core Region (brain/core/)
| File | Function | Rules |
|------|----------|-------|
| [brain.py](./core/brain.py) | Main orchestrator | BRAIN_001, BRAIN_002 |
| [router.py](./core/router.py) | Command routing | BRAIN_005 |
| [guardrails.py](./core/guardrails.py) | Safety middleware | GUARD_001-005 |
| [enums.py](./core/enums.py) | Risk tiers | RISK_001-005 |

### Rules Region (brain/rules/)
| File | Function | Rules |
|------|----------|-------|
| [schema.py](./rules/schema.py) | Rule definitions | VALID_001, VALID_004, VALID_005 |
| [validator.py](./rules/validator.py) | Rule validation | VALID_002 |
| [version_control.py](./rules/version_control.py) | Rule versioning | VALID_003 |

### Policy Region (brain/policies/)
| File | Function | Rules |
|------|----------|-------|
| [security.py](./policies/security.py) | Security policies | POLICY_001, POLICY_002 |
| [integrity.py](./policies/integrity.py) | Data integrity | POLICY_003, POLICY_004 |
| [communications.py](./policies/communications.py) | Message limits | POLICY_005 |

### State Region (brain/state/)
| File | Function | Rules |
|------|----------|-------|
| [manager.py](./state/manager.py) | State coordination | STATE_001, STATE_005 |
| [job_machine.py](./state/job_machine.py) | Job lifecycle | STATE_002 |
| [invoice_machine.py](./state/invoice_machine.py) | Invoice lifecycle | STATE_003 |

### AI Region (brain/ai/)
| File | Function | Rules |
|------|----------|-------|
| [suggestion_engine.py](./ai/suggestion_engine.py) | AI suggestions | - |

---

## 📋 Quick Start for AI

### Before Starting Any Task:

1. **Load Core Rules**: Read [CORE_RULES.md](./CORE_RULES.md)
2. **Check Session State**: Read [session.json](../session.json)
3. **Review Context**: Read [.context.md](../.context.md)
4. **Follow Protocol**: Read [AI_RULES.md](./AI_RULES.md)

### Critical Rules to Remember:

| ID | Rule | Enforcement |
|----|------|-------------|
| LANG_001 | Python-First Development | 🔴 CRITICAL |
| BRAIN_001 | No Direct Database Access | 🔴 CRITICAL |
| BRAIN_002 | Always Log to Audit | 🔴 CRITICAL |
| EVENT_001 | Brains Never Import Each Other | 🔴 CRITICAL |
| MOD_001 | Single-Page Modification | 🔴 CRITICAL |

---

## 📁 5-File Memory System

| File | Purpose | Type |
|------|---------|------|
| [session.json](../session.json) | Working memory - current state | ⚡ Active |
| [decisions.log](../decisions.log) | Long-term memory - decision history | 💾 Storage |
| [.context.md](../.context.md) | Synapse registry - context mapping | 🔗 Map |
| [patterns/](../patterns/) | Engram library - code patterns | 📋 Templates |
| [CORE_RULES.md](./CORE_RULES.md) | Rule registry - all project rules | 🧠 Core |

---

## 🔄 Memory Update Protocol

After completing any task:

1. **Update session.json** - Set new active prompt and progress
2. **Append to decisions.log** - Record decisions made
3. **Update .context.md** - Add new context if needed
4. **Create pattern** - If reusable code was created

---

## 📚 Related Files

| File | Purpose |
|------|---------|
| [AI_START_HERE.md](../AI_START_HERE.md) | **AI entry point** - Start here |
| [CORE_RULES.md](./CORE_RULES.md) | **MASTER FILE** - All rules |
| [AI_RULES.md](./AI_RULES.md) | AI thinking protocol |
| [SECURITY_PLAYBOOK.md](./SECURITY_PLAYBOOK.md) | Security protocols & audit requirements |
| [nervous_system.py](./nervous_system.py) | Event bus implementation |
| [README.md](../README.md) | Project entry point |

---

**Last Updated:** March 2026  
**Maintained By:** Neural System Architect  
**Version:** 1.0.0