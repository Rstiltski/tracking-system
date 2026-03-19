# 🧠 CONTEXT.md - AI Master Reference

**Mention this file to load full project context. The AI will understand and follow all procedures.**

---

## 📁 FILE LIST

### Core Documentation
| File | Purpose | When to Use |
|------|---------|-------------|
| `AI_START_HERE.md` | **AI ENTRY POINT** - Master index for AI agents | Start here for AI context |
| `brain/CORE_RULES.md` | **MASTER FILE** - All 58+ rules | Check any rule |
| `brain/NEURAL_HUB.md` | Central navigation hub | Find your way |
| `brain/AI_RULES.md` | AI thinking protocol (4-phase workflow) | Execute tasks |
| `brain/SECURITY_PLAYBOOK.md` | Security protocols and audit requirements | Security reference |
| `PROJECT_RULES.md` | Detailed development guidelines | Write code |
| `README.md` | Project overview | Get oriented |
| `ROADMAP.md` | Strategic development plan | Plan features |
| `ARCHITECTURE_DECISIONS.md` | **Architecture clarification** (Brain vs. Data Backend) | Understand true architecture |
| `ARCHITECTURAL_MAP.md` | Visual architecture diagrams | See system structure |
| `phases/PHASE_*.md` | Phase implementation docs | Phase details |
| `TODO.md` | Task tracking | Find work |

### Memory System
| File | Purpose | When to Use |
|------|---------|-------------|
| `session.json` | Working memory (current state) | Check progress |
| `decisions.log` | Long-term memory (decision history) | Review choices |
| `.context.md` | Synapse registry (technical mapping) | Find connections |

### Patterns & Templates
| File | Purpose | When to Use |
|------|---------|-------------|
| `patterns/prompt_template.md` | Five-Component prompt framework | Structure requests |
| `patterns/page_module.md` | Page module pattern | Create new pages |

---

## 🔄 LOADING SEQUENCE

When you mention this file, load context in this order:

```
1. brain/CORE_RULES.md    → All rules loaded
2. brain/AI_RULES.md      → Thinking protocol loaded
3. ARCHITECTURE_DECISIONS.md → Architecture clarification loaded
4. session.json           → Current state loaded
5. decisions.log          → History loaded
6. patterns/              → Patterns available
```

---

## ⚠️ CRITICAL RULES (Never Violate)

| ID | Rule | Description |
|----|------|-------------|
| **LANG_001** | Python-First | All new features in Python/Streamlit |
| **BRAIN_001** | No Direct DB | All operations through Storage class |
| **BRAIN_002** | Always Audit | Every command must be logged (if using Brain core) |
| **EVENT_001** | No Brain Imports | Brains never import each other |
| **MOD_001** | Single-Page | Only modify the specific file |
| **AI_001** | Five-Component | All prompts need Purpose, Users, Features, Constraints, Quality |
| **AI_002** | No "Simple" | Never use "simple" without definition |

---

## 🏗️ ARCHITECTURE CLARIFICATION (CRITICAL)

### Three-Layer Architecture

```
┌─────────────────────────────────────────┐
│   UI Layer                              │
│   - Streamlit (✅ 32+ pages, primary)   │
│   - React + FastAPI (🟡 Phase 13, ~10%) │
└───────────────┬─────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│   Data Backend (tracking_app/)          │
│   - storage.py ← ALL CRUD HERE          │
│   - models.py ← Data classes            │
│   - database.py ← SQLite connection     │
└───────────────┬─────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│   Intelligence Layer (brain/)           │
│   - analysis/ ← ML/analytics            │
│   - behavioral/ ← Habit science          │
│   - notifications/ ← Reminders          │
│   - core/ ← ⚠️ OVER-ENGINEERED          │
└───────────────┬─────────────────────────┘
                 │
                 ▼
┌─────────────────────────────────────────┐
│   SQLite Database (tracking.db)         │
└─────────────────────────────────────────┘
```

### ⚠️ Critical: Brain is NOT the Data Backend

| Layer | Purpose | Use For |
|-------|---------|---------|
| **📦 Data Backend** (`tracking_app/`) | Data persistence & CRUD | **ALL** habit/task/goal storage |
| **🧠 Intelligence Layer** (`brain/`) | AI/ML analytics | Correlations, predictions, burnout detection |
| **🎨 UI Layer** | User interface | Streamlit (primary) or React (Phase 13) |

**For simple CRUD:** Call `tracking_app/storage.py` **directly**

**For AI analytics:** Call `brain/analysis/` or `brain/behavioral/`

**DON'T use Brain core** (`brain/core/brain.py`) for personal tracking CRUD - it's over-engineered for business SaaS.

---

## 📝 VIBE CODING TEMPLATE

Use this template for all requests:

```markdown
## PURPOSE
[What problem does this solve? Who benefits? What defines success?]

## USERS
[Who will use this? What are their characteristics? What devices/contexts?]

## FEATURES
[What specifically should users be able to do? List each feature with details]

## CONSTRAINTS
[What limitations exist? What must it work with? What should it NOT do?]

## QUALITY STANDARDS
[How polished should it be? What level of completeness?]
```

### Quality Phrases to Include

| Aspect | Phrase |
|--------|--------|
| Visual | "Should look professional and production-ready, not like a prototype" |
| Responsive | "Must work well on desktop, tablet, and mobile devices" |
| Errors | "Should handle errors gracefully with helpful user-friendly messages" |
| Feedback | "Provide clear visual feedback for all user actions" |
| Performance | "Should load quickly and feel responsive" |

---

## 🧠 4-PHASE WORKFLOW

Every task follows this workflow from `brain/AI_RULES.md`:

### Phase 1: INTERROGATION
Analyze for ambiguity. Ask 3 critical questions:
1. What if this conflicts with existing patterns?
2. How does this fit into the current system architecture?
3. What dependencies or edge cases might be affected?

### Phase 2: TRANSLATION
Rewrite vague input into a "Serious Prompt" with full specification.

### Phase 3: ROADMAP VERIFICATION
Check if this is the correct next step or if dependencies are missing.

### Phase 4: EXECUTION
Implement the solution. Update the 5-file memory.

---

## 📊 CURRENT SESSION STATE

Check `session.json` for:
- Active prompt
- Current phase
- Progress percentage
- Active file
- Vibe coding context
- **Project phase status** (Phase 1-6 verified complete)

---

## 📈 PHASE VERIFICATION STATUS

**Last Verified:** March 19, 2026

| Phase | Name | Status | Tests |
|-------|------|--------|-------|
| Phase 1 | Foundation Strengthening | ✅ Verified | 31 passing |
| Phase 2 | Intelligence Layer | ✅ Verified | Files exist |
| Phase 3 | Behavioral Science | ✅ Verified | Files exist |
| Phase 4 | Automation & Integration | ✅ Verified | Files exist |
| Phase 5 | Data Management | ✅ Verified | Files exist |
| Phase 6 | UI-Backend Integration | ✅ Verified | Files exist |
| Phase 7 | Polish & Enhancement | ✅ Complete | Performance optimization |
| Phase 8 | Advanced Performance | ✅ Complete | 4 systems implemented |
| Phase 9 | Advanced Reporting & Social | ✅ Complete | Reports, Widgets, Social features |
| Phase 10 | Core Enhancements | ✅ Complete | Habit Score, Streak Freeze |
| Phase 11 | Advanced Support & Safeguards | ✅ Complete | Safeguards, Privacy |
| Phase 12 | UI/UX Redesign | ✅ Complete | Design System |
| Phase 13 | Decoupled Architecture | ✅ Complete | React + FastAPI (16 routes) |
| Phase 14 | Page Consolidation | ✅ Complete | React Frontend (14 views) |

**All Phases 1-14 have been verified complete.** Project is fully implemented.

---

## 🎯 HOW TO USE THIS FILE

### Option 1: Simple Mention
Just say: **"Follow CONTEXT.md"** or **"Load context"**

### Option 2: With Request
Say: **"Following CONTEXT.md, [your request]"**

### Option 3: For Specific Tasks
- **"Following CONTEXT.md, create a new page"** → AI loads page_module.md pattern
- **"Following CONTEXT.md, debug an issue"** → AI loads immune/ and audit/
- **"Following CONTEXT.md, plan a feature"** → AI follows 4-phase workflow

---

## 🗂️ PROJECT STRUCTURE

```
tracking-system/
├── CONTEXT.md              ← YOU ARE HERE
├── session.json            ← Working memory
├── decisions.log           ← Long-term memory
├── .context.md             ← Synapse registry
├── PROJECT_RULES.md        ← Development guidelines
├── README.md               ← Project overview
├── ROADMAP.md              ← Strategic plan
├── TODO.md                 ← Task tracking
├── FEATURE_MAP.md          ← Feature locations
│
├── brain/                  ← Intelligence Layer
│   ├── CORE_RULES.md       ← Master rule registry
│   ├── NEURAL_HUB.md       ← Navigation hub
│   ├── AI_RULES.md         ← AI protocol
│   ├── nervous_system.py   ← Event bus
│   ├── core/               ← Core brain components
│   ├── models/             ← Data models
│   ├── tools/              ← 100+ operation tools
│   ├── policies/           ← Validation rules
│   ├── state/              ← State machines
│   ├── audit/              ← Audit logging
│   └── brains/             ← Specialized brains
│
├── frontend/               ← React Frontend (Phase 13)
│   ├── src/               ← React source code
│   ├── vite.config.js     ← Vite configuration
│   └── package.json       ← NPM dependencies
│
├── backend/               ← FastAPI Backend (Phase 13)
│   ├── main.py            ← FastAPI application
│   ├── config.py          ← Configuration
│   ├── routes/            ← API routes
│   └── schemas/           ← Pydantic schemas
│
├── tracking_app/          ← Streamlit Application (Primary)
│   ├── app.py            ← Main entry
│   ├── storage.py        ← Data persistence
│   ├── pages/            ← UI pages
│   └── components/       ← UI components
│
├── patterns/              ← Code patterns
│   ├── prompt_template.md ← Prompt framework
│   └── page_module.md     ← Page pattern
│
└── docs/                  ← Documentation
    └── research/          ← Research notes
```

---

## 🔗 QUICK LINKS

| Want to... | Go to... |
|------------|----------|
| **AI entry point** | [AI_START_HERE.md](AI_START_HERE.md) |
| Check rules | [brain/CORE_RULES.md](brain/CORE_RULES.md) |
| Navigate project | [brain/NEURAL_HUB.md](brain/NEURAL_HUB.md) |
| See AI protocol | [brain/AI_RULES.md](brain/AI_RULES.md) |
| Security protocols | [brain/SECURITY_PLAYBOOK.md](brain/SECURITY_PLAYBOOK.md) |
| Structure a prompt | [patterns/prompt_template.md](patterns/prompt_template.md) |
| See current state | [session.json](session.json) |
| Review decisions | [decisions.log](decisions.log) |
| Plan development | [ROADMAP.md](ROADMAP.md) |
| Find tasks | [TODO.md](TODO.md) |

---

## 📋 CHECKLIST BEFORE ANY TASK

- [ ] Loaded CORE_RULES.md?
- [ ] Checked session.json state?
- [ ] Following 4-phase workflow?
- [ ] Using Five-Component template?
- [ ] Checked relevant patterns?
- [ ] Verified critical rules?

---

**Last Updated:** March 2026  
**Version:** 1.0.0  
**Maintained By:** Neural System Architect

---

> **💡 TIP:** Bookmark this file. Mention it at the start of any conversation to give the AI full context.
