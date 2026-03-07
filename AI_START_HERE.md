# 🎯 Veryfyn Tracking System - Master Index

**Project Root:** `tracking-system/`
**Primary Interface:** Python Streamlit (`tracking_app/`)
**Backend Core:** The Brain (`brain/`)

---

## 🚨 LLM/Contributor Rules (MANDATORY)

**ALL contributors (LLMs and humans) MUST follow these rules for every workflow, code change, or feature addition:**

1. **Read ALL referenced documentation:**
   - Whenever documentation references another file (such as `.md` files), you MUST open and read that referenced file as part of the workflow.
   - Do not skip any referenced documentation—open and review each one before proceeding with any step or task.

2. **Follow Project Conventions:**
   - Use only the documented directories, file structures, and configuration files.
   - Never invent new paths or structures unless explicitly instructed by the documentation or project owner.
   - **Python-First (LANG_001):** All new features MUST be implemented in Python/Streamlit. No new JavaScript/HTML/CSS.

3. **Check Before You Change:**
   - Before making any code or documentation change, confirm the correct location, naming, and workflow by re-reading the relevant markdown files and checking the workspace structure.
   - If in doubt, search the workspace for existing directories, files, or configuration entries.

4. **Single-Page Modification Rule (MOD_001):**
   - When working on a page/module, ONLY modify that specific file.
   - NEVER modify multiple pages in a single task unless explicitly required.

5. **Document Your Steps:**
   - When adding features or making changes, update the relevant documentation (`FEATURE_MAP.md`, `decisions.log`, etc.) as part of your workflow.

6. **Enforcement:**
   - These rules are not optional. Any deviation may result in broken workflows, lost work, or rejected contributions.

---

## 🤖 Agent Operational Note

All contributors and automated agents MUST read [`GETTING_STARTED.md`](GETTING_STARTED.md) before making changes. This document contains critical setup steps, required tooling checks, and the approved workflow for implementing features, running tests, and making changes.

**Agents should not modify code or documentation before confirming they have followed the steps in `GETTING_STARTED.md`.**

---

## 🚨 LLM START HERE (MANDATORY CONTEXT)

**AI Agents must load these files to understand the project:**

| Sequence | File | Purpose |
|----------|------|---------|
| 1 | [`CONTEXT.md`](CONTEXT.md) | **MASTER REFERENCE** - Load this first |
| 2 | [`brain/CORE_RULES.md`](brain/CORE_RULES.md) | Immutable project laws (58+ rules) |
| 3 | [`brain/AI_RULES.md`](brain/AI_RULES.md) | Thinking protocol (4-Phase Workflow) |
| 4 | [`session.json`](session.json) | Current memory state |
| 5 | [`decisions.log`](decisions.log) | Implementation history |

**Command:** "Follow CONTEXT.md" triggers the full context loading sequence.

---

## 📋 Essential LLM Files

The following files are required for LLM workflow, navigation, and operational guidance:

| File | Purpose |
|------|---------|
| [`CONTEXT.md`](CONTEXT.md) | Master context reference for AI agents |
| [`brain/CORE_RULES.md`](brain/CORE_RULES.md) | All 58+ project rules (CRITICAL) |
| [`brain/AI_RULES.md`](brain/AI_RULES.md) | 4-Phase thinking protocol |
| [`PROJECT_RULES.md`](PROJECT_RULES.md) | Coding standards (Python-First, Single-Page Rule) |
| [`FEATURE_MAP.md`](FEATURE_MAP.md) | Maps every feature to its source file |
| [`session.json`](session.json) | Working memory (current state) |
| [`decisions.log`](decisions.log) | Long-term memory (decision history) |
| [`ROADMAP.md`](ROADMAP.md) | Strategic development plan |
| [`GETTING_STARTED.md`](GETTING_STARTED.md) | Onboarding guide for developers |

---

## 🚦 Quick Start & Requirements

**Follow these steps to get up and running:**

### 1. Prerequisites
- Python 3.10+
- SQLite3

### 2. Installation
```bash
# Create and activate virtual environment (MANDATORY)
python3 -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\Activate.ps1

# Install project dependencies
pip install -r requirements.txt
```

### 3. Run Application
```bash
# Launch the Streamlit interface
streamlit run tracking_app/app.py
```

### 4. Development Mode
- The database is auto-initialized at `tracking_app/tracking.db`
- See `GETTING_STARTED.md` for detailed workflow

---

## 🐛 Debug Mode

To enable full debug logging and error details:

**Option 1: Environment Variables**
```bash
export DEBUG=True
export LOG_LEVEL=DEBUG
streamlit run tracking_app/app.py
```

**Option 2: Create .env file**
```bash
# In project root, create .env file
DEBUG=True
LOG_LEVEL=DEBUG
```

Debug mode shows:
- Full error stack traces
- All log messages (DEBUG level and above)
- Step-by-step execution logs
- Database query debugging

---

## 📚 Documentation Library

### 🧭 Navigation & Planning
| Document | Purpose |
|----------|---------|
| [`README.md`](README.md) | Project overview and architecture |
| [`FEATURE_MAP.md`](FEATURE_MAP.md) | Maps every feature to its source file |
| [`ROADMAP.md`](ROADMAP.md) | Strategic development plan |
| [`CHUNKED_TODO_GUIDELINES.md`](CHUNKED_TODO_GUIDELINES.md) | Active task list |
| [`PROJECT_RULES.md`](PROJECT_RULES.md) | Coding standards (Python-First, Single-Page Rule) |

### 🧠 The Brain (Backend)
| Document | Purpose |
|----------|---------|
| [`brain/README.md`](brain/README.md) | Architecture of the backend system |
| [`brain/CORE_RULES.md`](brain/CORE_RULES.md) | Self-healing and protection systems |
| [`brain/AI_RULES.md`](brain/AI_RULES.md) | Deep dive into state machines, policies, and tools |

### 🔬 Research & Specifications
| Document | Purpose |
|----------|---------|
| [`docs/research/`](docs/research/) | Behavioral science and technical research |
| [`docs/specs/`](docs/specs/) | Feature specifications (Habit Score, Emotional State) |
| [`docs/schemas/`](docs/schemas/) | Data and audit schemas |

### 📊 Implementation History
| Document | Purpose |
|----------|---------|
| [`decisions.log`](decisions.log) | Log of all architectural choices |
| [`PHASE_*_SUMMARY.md`](PHASE_*_SUMMARY.md) | Detailed logs of completed phases (1-7) |

### 🛠️ Developer Guides
| Document | Purpose |
|----------|---------|
| [`GETTING_STARTED.md`](GETTING_STARTED.md) | Onboarding guide for new developers |
| [`ARCHITECTURAL_MAP.md`](ARCHITECTURAL_MAP.md) | High-level system architecture |
| [`PAGE_REFACTORING_GUIDE.md`](PAGE_REFACTORING_GUIDE.md) | Guidelines for refactoring pages |
| [`MODULE_MANAGEMENT_ROADMAP.md`](MODULE_MANAGEMENT_ROADMAP.md) | Module management strategy |

---

## 🏗️ Project Structure Overview

```
tracking-system/
├── tracking_app/              # Main Streamlit application
│   ├── app.py                # Entry point
│   ├── storage.py            # Data persistence layer
│   ├── database.py           # Database connection
│   ├── components/           # Reusable UI components
│   │   ├── sidebar.py        # Navigation sidebar
│   │   ├── session.py        # Session state management
│   │   ├── charts.py         # Chart components
│   │   └── responsive.py     # Mobile responsiveness
│   └── pages/                # Feature pages (32 pages)
│       ├── dashboard/        # Main dashboard
│       ├── habits/           # Habit tracking
│       ├── tasks/            # Task management
│       ├── goals/            # Goal tracking
│       ├── health/           # Health metrics
│       ├── finances/         # Financial tracking
│       ├── time/             # Time tracking
│       ├── calendar/         # Calendar view
│       └── [24 more pages]   # Additional feature pages
│
├── brain/                    # Backend intelligence
│   ├── CORE_RULES.md         # Immutable laws (58+ rules)
│   ├── AI_RULES.md           # AI workflow (4-Phase)
│   ├── NEURAL_HUB.md         # Navigation hub
│   ├── core/                 # Core brain components
│   ├── tools/                # 100+ operation tools
│   ├── policies/             # Validation rules
│   ├── state/                # State machines
│   ├── audit/                # Audit logging
│   ├── immune/               # Self-healing system
│   └── brains/               # Specialized brains
│
├── docs/                     # Documentation folders
│   ├── research/             # Research documents
│   ├── specs/                # Technical specifications
│   └── schemas/              # Data schemas
│
├── patterns/                 # Code patterns
│   ├── prompt_template.md    # Five-Component prompt framework
│   └── page_module.md        # Page module pattern
│
├── CONTEXT.md                # Master context reference
├── AI_START_HERE.md          # This file - AI entry point
├── FEATURE_MAP.md            # Feature mapping
├── ROADMAP.md                # Development roadmap
├── session.json              # Working memory
├── decisions.log             # Long-term memory
└── requirements.txt          # Python dependencies
```

---

## 🎯 Key Commands

| Task | Command |
|------|---------|
| Create Virtual Environment | `python3 -m venv .venv` |
| Activate Virtual Environment | `source .venv/bin/activate` |
| Install Dependencies | `pip install -r requirements.txt` |
| Run App | `streamlit run tracking_app/app.py` |
| Run with Port | `streamlit run tracking_app/app.py --server.port 8501` |
| Check Database | `sqlite3 tracking_app/tracking.db ".tables"` |
| Run Tests | `python -m pytest brain/immune/tests/` |

---

## 📊 Project Status

| Phase | Status | Description |
|-------|--------|-------------|
| Phase 1: Foundation | ✅ Verified | Data architecture, Habit Score, Streak Freeze |
| Phase 2: Intelligence | ✅ Verified | Correlation, prediction, analysis |
| Phase 3: Behavioral | ✅ Verified | Habit stacking, rewards, accountability |
| Phase 4: Automation | ✅ Verified | Notifications, alerts, reminders |
| Phase 5: Data Management | ✅ Verified | Backup, export, lifecycle |
| Phase 6: UI-Backend | ✅ Verified | Streamlit integration |
| Phase 7: Polish | ✅ Complete | Charts, mobile, performance |
| Phase 8: Advanced Performance | ✅ Complete | 4 advanced performance systems |

**Status:** Production Ready - Enterprise Grade Performance

---

## 🔗 Quick Links

| Want to... | Go to... |
|------------|----------|
| **Get started** | [`GETTING_STARTED.md`](GETTING_STARTED.md) |
| **Understand rules** | [`PROJECT_RULES.md`](PROJECT_RULES.md) |
| **Find a feature** | [`FEATURE_MAP.md`](FEATURE_MAP.md) |
| **See roadmap** | [`ROADMAP.md`](ROADMAP.md) |
| **Check current state** | [`session.json`](session.json) |
| **Review decisions** | [`decisions.log`](decisions.log) |
| **Understand Brain** | [`brain/README.md`](brain/README.md) |

---

**Last Updated:** March 7, 2026
**Version:** 1.1.0
**Status:** Production Ready