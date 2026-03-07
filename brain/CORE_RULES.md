# 🧠 CORE RULES - Neural Synapse Registry

**THE MASTER FILE containing ALL project rules for the Veryfyn Tracking System.**

---

## 🎯 Purpose

This file serves as the **central nervous system reference** for all rules, constraints, and guidelines. Every rule-containing file in the project links back to this registry via synaptic hooks.

---

## 📋 Rule Index

### Language Rules (LANG_) - Python-First Development

| ID | Rule | Source | Enforcement | Synapses |
|----|------|--------|-------------|----------|
| LANG_001 | **Python-First**: All new features MUST be implemented in Python/Streamlit | PROJECT_RULES.md | 🔴 CRITICAL | [brain/__init__.py](./__init__.py) |
| LANG_002 | **No new JavaScript**: JavaScript/HTML/CSS files are LEGACY only | PROJECT_RULES.md | 🔴 CRITICAL | [js/](../js/) |
| LANG_003 | **Use Type Hints**: All Python functions must have type annotations | PROJECT_RULES.md | 🟠 HIGH | [brain/core/types.py](./core/types.py) |
| LANG_004 | **Use Dataclasses**: Data models must use Python dataclasses | PROJECT_RULES.md | 🟠 HIGH | [brain/models/](./models/) |
| LANG_005 | **Follow PEP 8**: Snake_case for functions/variables | PROJECT_RULES.md | 🟡 MEDIUM | - |

### Modification Rules (MOD_) - Targeted Updates

| ID | Rule | Source | Enforcement | Synapses |
|----|------|--------|-------------|----------|
| MOD_001 | **Single-Page Modification**: Only modify the specific file being worked on | PROJECT_RULES.md | 🔴 CRITICAL | - |
| MOD_002 | **Minimal Changes**: Make minimal, targeted changes to achieve the goal | PROJECT_RULES.md | 🟠 HIGH | - |
| MOD_003 | **No Cascading Changes**: Don't modify multiple pages in a single task | PROJECT_RULES.md | 🟠 HIGH | - |
| MOD_004 | **Test Independently**: Test single page independently before integration | PROJECT_RULES.md | 🟡 MEDIUM | - |

### Brain Rules (BRAIN_) - Core Architecture

| ID | Rule | Source | Enforcement | Synapses |
|----|------|--------|-------------|----------|
| BRAIN_001 | **No Direct Database Access**: All operations through Tools | brain/__init__.py | 🔴 CRITICAL | [brain/core/brain.py](./core/brain.py) |
| BRAIN_002 | **Always Log to Audit**: Every command must be recorded | brain/__init__.py | 🔴 CRITICAL | [brain/audit/](./audit/) |
| BRAIN_003 | **No Auto-Editing Scripts**: Scripts detect only, never modify | brain/__init__.py | 🔴 CRITICAL | [brain/immune/](./immune/) |
| BRAIN_004 | **No Placeholders**: Complete implementations only | brain/__init__.py | 🔴 CRITICAL | - |
| BRAIN_005 | **Validate Transitions**: State machines must be enforced | brain/__init__.py | 🔴 CRITICAL | [brain/state/](./state/) |

### Validation Rules (VALID_) - Rule System

| ID | Rule | Source | Enforcement | Synapses |
|----|------|--------|-------------|----------|
| VALID_001 | **Rule Definition Schema**: All rules must follow formal schema | brain/rules/schema.py | 🟠 HIGH | [brain/rules/schema.py](./rules/schema.py) |
| VALID_002 | **Conflict Detection**: Validator must detect rule conflicts | brain/rules/validator.py | 🟠 HIGH | [brain/rules/validator.py](./rules/validator.py) |
| VALID_003 | **Version Control**: Rules must be versioned | brain/rules/version_control.py | 🟡 MEDIUM | [brain/rules/version_control.py](./rules/version_control.py) |
| VALID_004 | **Preconditions Required**: Rules must have defined preconditions | brain/rules/schema.py | 🟠 HIGH | - |
| VALID_005 | **Actions Required**: Rules must have defined actions | brain/rules/schema.py | 🟠 HIGH | - |

### Policy Rules (POLICY_) - Safety & Security

| ID | Rule | Source | Enforcement | Synapses |
|----|------|--------|-------------|----------|
| POLICY_001 | **Authentication Required**: All operations require auth | brain/policies/security.py | 🔴 CRITICAL | [brain/policies/](./policies/) |
| POLICY_002 | **Role-Based Access**: Access control by role | brain/policies/security.py | 🔴 CRITICAL | - |
| POLICY_003 | **Data Validation**: Validate before save | brain/policies/integrity.py | 🟠 HIGH | [brain/policies/integrity.py](./policies/integrity.py) |
| POLICY_004 | **Foreign Key Constraints**: Enforce relationships | brain/policies/integrity.py | 🟠 HIGH | - |
| POLICY_005 | **Rate Limiting**: Limit message frequency | brain/policies/communications.py | 🟡 MEDIUM | - |

### Invariant Rules (INVAR_) - Business Logic

| ID | Rule | Source | Enforcement | Synapses |
|----|------|--------|-------------|----------|
| INVAR_001 | **Financial Rules**: Money invariants must hold | brain/invariants/money_invariants.py | 🔴 CRITICAL | [brain/invariants/](./invariants/) |
| INVAR_002 | **Relationship Rules**: Linking invariants must hold | brain/invariants/linking_invariants.py | 🟠 HIGH | - |
| INVAR_003 | **Duplicate Prevention**: Idempotency must be enforced | brain/invariants/idempotency_invariants.py | 🟠 HIGH | - |
| INVAR_004 | **Scoring Rules**: Invariant scoring must be consistent | brain/invariants/scorer.py | 🟡 MEDIUM | - |
| INVAR_005 | **Invariant Verification**: Checker must validate all invariants | brain/invariants/checker.py | 🟠 HIGH | - |

### State Rules (STATE_) - Entity Lifecycle

| ID | Rule | Source | Enforcement | Synapses |
|----|------|--------|-------------|----------|
| STATE_001 | **Valid Transitions Only**: State transitions must be valid | brain/state/manager.py | 🔴 CRITICAL | [brain/state/](./state/) |
| STATE_002 | **Job Lifecycle**: DRAFT → QUOTED → BOOKED → SCHEDULED → IN_PROGRESS → COMPLETED | brain/state/job_machine.py | 🟠 HIGH | - |
| STATE_003 | **Invoice Lifecycle**: DRAFT → SENT → VIEWED → PAID | brain/state/invoice_machine.py | 🟠 HIGH | - |
| STATE_004 | **Quote Lifecycle**: DRAFT → SENT → ACCEPTED → CONVERTED | brain/state/quote_machine.py | 🟠 HIGH | - |
| STATE_005 | **Cancellation Path**: Valid cancellation paths only | brain/state/manager.py | 🟠 HIGH | - |

### Event Rules (EVENT_) - Nervous System Communication

| ID | Rule | Source | Enforcement | Synapses |
|----|------|--------|-------------|----------|
| EVENT_001 | **Brains Never Import Each Other**: No direct code imports between brains | nervous_system.py | 🔴 CRITICAL | [nervous_system.py](./nervous_system.py) |
| EVENT_002 | **Communication Only Via Events**: All inter-brain communication through events | nervous_system.py | 🔴 CRITICAL | - |
| EVENT_003 | **Event Persistence**: Events must be persisted for reliability | nervous_system.py | 🟠 HIGH | - |
| EVENT_004 | **Priority Handling**: Handlers execute by priority | nervous_system.py | 🟡 MEDIUM | - |
| EVENT_005 | **Error Isolation**: One handler failing doesn't affect others | nervous_system.py | 🟠 HIGH | - |

### Guardrail Rules (GUARD_) - Safety Middleware

| ID | Rule | Source | Enforcement | Synapses |
|----|------|--------|-------------|----------|
| GUARD_001 | **Loop Detection**: Detect and prevent infinite loops | brain/core/guardrails.py | 🔴 CRITICAL | [brain/core/guardrails.py](./core/guardrails.py) |
| GUARD_002 | **Sanity Checks**: Validate operation sanity | brain/core/guardrails.py | 🟠 HIGH | - |
| GUARD_003 | **Rate Limiting**: Protect against excessive operations | brain/core/guardrails.py | 🟠 HIGH | - |
| GUARD_004 | **Resource Protection**: Prevent resource exhaustion | brain/core/guardrails.py | 🟠 HIGH | - |
| GUARD_005 | **Graceful Degradation**: Handle failures gracefully | brain/core/guardrails.py | 🟡 MEDIUM | - |

### Risk Tier Rules (RISK_) - Safety Classification

| ID | Rule | Source | Enforcement | Synapses |
|----|------|--------|-------------|----------|
| RISK_001 | **TRIVIAL (1)**: Read-only, safe updates - No confirmation | brain/core/enums.py | 🟢 LOW | - |
| RISK_002 | **LOW (2)**: Standard operations - No confirmation | brain/core/enums.py | 🟢 LOW | - |
| RISK_003 | **MEDIUM (3)**: Customer-facing changes - No confirmation | brain/core/enums.py | 🟡 MEDIUM | - |
| RISK_004 | **HIGH (4)**: Financial, bulk operations - Confirmation required | brain/core/enums.py | 🟠 HIGH | [brain/fork/](./fork/) |
| RISK_005 | **CRITICAL (5)**: Irreversible, destructive - Confirmation + nuclear codes | brain/core/enums.py | 🔴 CRITICAL | - |

### UI/UX Rules (UI_) - Interface Guidelines

| ID | Rule | Source | Enforcement | Synapses |
|----|------|--------|-------------|----------|
| UI_001 | **Mobile-First**: Responsive design starting from mobile | PROJECT_RULES.md | 🟠 HIGH | [css/styles.css](../css/styles.css) |
| UI_002 | **Dark Mode Support**: All UI must support dark mode | PROJECT_RULES.md | 🟠 HIGH | - |
| UI_003 | **Accessibility**: WCAG 2.1 AA compliance | PROJECT_RULES.md | 🟡 MEDIUM | - |
| UI_004 | **Animations Under 300ms**: UI feedback animations | PROJECT_RULES.md | 🟡 MEDIUM | - |
| UI_005 | **Toast Notifications**: Use App.showToast for messages | PROJECT_RULES.md | 🟡 MEDIUM | [js/app.js](../js/app.js) |

### Documentation Rules (DOC_) - Documentation Standards

| ID | Rule | Source | Enforcement | Synapses |
|----|------|--------|-------------|----------|
| DOC_001 | **File Headers**: Add file header comments explaining purpose | PROJECT_RULES.md | 🟡 MEDIUM | - |
| DOC_002 | **Docstrings**: Document all functions with docstrings | PROJECT_RULES.md | 🟠 HIGH | - |
| DOC_003 | **Update FEATURE_MAP**: Update when adding new features | PROJECT_RULES.md | 🟡 MEDIUM | [FEATURE_MAP.md](../FEATURE_MAP.md) |
| DOC_004 | **Conventional Commits**: Use conventional commit format | PROJECT_RULES.md | 🟡 MEDIUM | - |
| DOC_005 | **Keep Docs Consistent**: Same structure across all doc files | PROJECT_RULES.md | 🟠 HIGH | - |

### AI Communication Rules (AI_) - Vibe Coding Protocol

| ID | Rule | Source | Enforcement | Synapses |
|----|------|--------|-------------|----------|
| AI_001 | **Five-Component Framework**: All prompts MUST address Purpose, Users, Features, Constraints, Quality Standards | AI_RULES.md | 🔴 CRITICAL | [brain/AI_RULES.md](./AI_RULES.md) |
| AI_002 | **No Undefined "Simple"**: Never use "simple" without defining what is included AND excluded | AI_RULES.md | 🔴 CRITICAL | - |
| AI_003 | **Specify Quality Standards**: Always include quality phrases for polish, responsiveness, error handling | AI_RULES.md | 🟠 HIGH | [patterns/prompt_template.md](../patterns/prompt_template.md) |
| AI_004 | **Include Edge Cases**: Always specify error handling and edge case behavior | AI_RULES.md | 🟠 HIGH | - |
| AI_005 | **Outcomes Not Implementation**: Focus on what users experience, not how it's built | AI_RULES.md | 🟠 HIGH | - |
| AI_006 | **Context Gap Prevention**: Always state WHO uses it, WHERE they use it, WHAT they need, WHY they need it | AI_RULES.md | 🟠 HIGH | - |
| AI_007 | **Vision-Execution Bridge**: Translate abstract terms (modern, professional) into specific design language | AI_RULES.md | 🟡 MEDIUM | - |
| AI_008 | **Iterative Refinement**: Build in phases, get feedback early, avoid large corrections | AI_RULES.md | 🟡 MEDIUM | - |

---

## 🔗 Synaptic Hooks by File

Each file contains rules and links back to this registry.

### Root Documentation
| File | Rule IDs | Neural Link |
|------|----------|-------------|
| [AI_START_HERE.md](../AI_START_HERE.md) | DOC_005 | AI Entry Point |
| [PROJECT_RULES.md](../PROJECT_RULES.md) | LANG_001-005, MOD_001-004, UI_001-005, DOC_001-005 | Primary Source |
| [README.md](../README.md) | DOC_005 | Entry Point |
| [TODO.md](../TODO.md) | DOC_003 | Task Tracking |
| [ROADMAP.md](../ROADMAP.md) | DOC_003, DOC_005 | Strategic Planning |

### Brain Core
| File | Rule IDs | Neural Link |
|------|----------|-------------|
| [brain/__init__.py](./__init__.py) | BRAIN_001-005 | Brain Entry |
| [brain/core/brain.py](./core/brain.py) | BRAIN_001, BRAIN_002 | Main Orchestrator |
| [brain/core/router.py](./core/router.py) | BRAIN_005 | Command Router |
| [brain/core/guardrails.py](./core/guardrails.py) | GUARD_001-005 | Safety Middleware |
| [brain/core/enums.py](./core/enums.py) | RISK_001-005 | Risk Tiers |

### Brain Rules
| File | Rule IDs | Neural Link |
|------|----------|-------------|
| [brain/rules/schema.py](./rules/schema.py) | VALID_001, VALID_004, VALID_005 | Rule Schema |
| [brain/rules/validator.py](./rules/validator.py) | VALID_002 | Rule Validator |
| [brain/rules/version_control.py](./rules/version_control.py) | VALID_003 | Rule Versioning |

### Brain Policies
| File | Rule IDs | Neural Link |
|------|----------|-------------|
| [brain/policies/security.py](./policies/security.py) | POLICY_001, POLICY_002 | Security Policies |
| [brain/policies/integrity.py](./policies/integrity.py) | POLICY_003, POLICY_004 | Integrity Policies |
| [brain/policies/communications.py](./policies/communications.py) | POLICY_005 | Communication Policies |

### Brain Invariants
| File | Rule IDs | Neural Link |
|------|----------|-------------|
| [brain/invariants/checker.py](./invariants/checker.py) | INVAR_005 | Invariant Checker |
| [brain/invariants/money_invariants.py](./invariants/money_invariants.py) | INVAR_001 | Financial Rules |
| [brain/invariants/linking_invariants.py](./invariants/linking_invariants.py) | INVAR_002 | Relationship Rules |
| [brain/invariants/idempotency_invariants.py](./invariants/idempotency_invariants.py) | INVAR_003 | Duplicate Prevention |

### Brain State
| File | Rule IDs | Neural Link |
|------|----------|-------------|
| [brain/state/manager.py](./state/manager.py) | STATE_001, STATE_005 | State Manager |
| [brain/state/job_machine.py](./state/job_machine.py) | STATE_002 | Job States |
| [brain/state/invoice_machine.py](./state/invoice_machine.py) | STATE_003 | Invoice States |
| [brain/state/quote_machine.py](./state/quote_machine.py) | STATE_004 | Quote States |

### Nervous System
| File | Rule IDs | Neural Link |
|------|----------|-------------|
| [brain/nervous_system.py](./nervous_system.py) | EVENT_001-005 | Event Bus |

---

## ⚡ Event Bus Integration

The following rules trigger events through `nervous_system.py`:

### Event Types and Handlers

| Event Type | Trigger Rule | Handler Brain | Action |
|------------|--------------|---------------|--------|
| `JOB_COMPLETED` | STATE_002 | FinanceBrain | Create invoice |
| `JOB_COMPLETED` | STATE_002 | RelationBrain | Send thank you SMS |
| `INVOICE_PAID` | STATE_003 | RelationBrain | Send receipt |
| `INVOICE_VIEWED` | STATE_003 | OpsBrain | Log engagement |
| `QUOTE_ACCEPTED` | STATE_004 | OpsBrain | Convert to job |

### Event Flow Diagram

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│    OpsBrain     │     │  NervousSystem  │     │  FinanceBrain   │
│                 │     │   (Event Bus)   │     │                 │
│  JOB_COMPLETED  │────▶│  EVENT_001-005  │────▶│  Create Invoice │
│                 │     │                 │     │                 │
└─────────────────┘     └─────────────────┘     └─────────────────┘
                               │
                               ▼
                        ┌─────────────────┐
                        │  RelationBrain  │
                        │                 │
                        │  Send Thank You │
                        └─────────────────┘
```

---

## 📚 Context Loading Sequences

For AI to load context in the correct order:

### Start New Feature
```
1. README.md (Entry Point)
2. CORE_RULES.md (This File)
3. PROJECT_RULES.md (Detailed Guidelines)
4. brain/rules/schema.py (Rule Patterns)
5. patterns/ (Code Patterns)
```

### Debug Issue
```
1. CORE_RULES.md (This File)
2. brain/immune/ (Self-Healing)
3. brain/core/guardrails.py (Safety Rules)
4. brain/audit/ (Audit Logs)
```

### Plan Roadmap
```
1. CORE_RULES.md (This File)
2. docs/roadmaps/ (Strategic Plans)
3. TODO.md (Task Tracking)
4. brain/ai/suggestion_engine.py (AI Insights)
```

### Add New Rule
```
1. CORE_RULES.md (This File)
2. brain/rules/schema.py (Rule Schema)
3. brain/rules/validator.py (Validation)
4. brain/policies/ (Policy Integration)
```

---

## 🎯 Quick Reference

### Critical Rules (Never Violate)
- LANG_001: Python-First Development
- BRAIN_001: No Direct Database Access
- BRAIN_002: Always Log to Audit
- EVENT_001: Brains Never Import Each Other
- EVENT_002: Communication Only Via Events

### High Priority Rules (Strongly Enforce)
- MOD_001: Single-Page Modification
- VALID_001: Rule Definition Schema
- POLICY_001: Authentication Required
- STATE_001: Valid Transitions Only

### Medium Priority Rules (Should Follow)
- LANG_005: Follow PEP 8
- DOC_004: Conventional Commits
- UI_004: Animations Under 300ms

---

## 📁 Related Files

| File | Purpose |
|------|---------|
| [NEURAL_HUB.md](./NEURAL_HUB.md) | Central cortex entry point |
| [AI_RULES.md](./AI_RULES.md) | AI thinking protocol |
| [SECURITY_PLAYBOOK.md](./SECURITY_PLAYBOOK.md) | Security protocols & audit requirements |
| [nervous_system.py](./nervous_system.py) | Event bus implementation |
| [.context.md](../.context.md) | Synapse registry |
| [session.json](../session.json) | Working memory |
| [decisions.log](../decisions.log) | Long-term memory |

---

**Last Updated:** March 2026  
**Maintained By:** Neural System Architect  
**Version:** 1.0.0