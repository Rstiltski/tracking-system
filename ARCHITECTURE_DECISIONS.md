# 🏗️ Architecture Decision Record (ADR)

**Date:** March 17, 2026
**Status:** Approved
**Deciders:** Project Team

---

## 📋 Overview

This document clarifies the **true architecture** of the Veryfyn tracking system, distinguishing between the three architectural layers and explaining design decisions.

---

## 🎯 Architecture Clarification

### Critical Distinction: Brain vs. Data Backend

**The Brain is NOT the data backend.** This is a common misconception that needs clarification.

| Layer | Purpose | Files | Used For |
|-------|---------|-------|----------|
| **📦 Data Backend** | Data persistence & CRUD | `tracking_app/storage.py`, `models.py`, `database.py` | All habit/task/goal data storage |
| **🧠 Intelligence Layer** | AI/ML analytics & insights | `brain/analysis/`, `brain/behavioral/`, `brain/notifications/` | Correlations, predictions, burnout detection, habit stacking |
| **🎨 UI Layer** | User interface | Streamlit pages OR React + FastAPI | User interaction |

**Simple CRUD operations** (create habit, complete task) → Call `tracking_app/storage.py` **directly**

**AI commands** (analyze patterns, suggest interventions) → Flow through `brain/core/brain.py` (optional, over-engineered for personal tracking)

---

## 🏛️ System Architecture

### Three-Layer Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    UI LAYER (Choose One)                        │
├─────────────────────────────────────────────────────────────────┤
│  Mode 1: Streamlit (✅ Primary - 32+ pages, 100% features)      │
│  Mode 2: React + FastAPI (🟡 Phase 13 - 4 pages, ~10% features) │
│  Mode 3: Legacy JS (❌ Deprecated - being migrated)             │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              DATA BACKEND (tracking_app/)                       │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  storage.py (2,977 lines) ← All CRUD operations           │  │
│  │  models.py ← Data classes (Habit, Task, Goal, etc.)       │  │
│  │  database.py ← SQLite connection                          │  │
│  └───────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│           INTELLIGENCE LAYER (brain/)                           │
│  ┌───────────────────────────────────────────────────────────┐  │
│  │  analysis/ ← Correlations, predictions, burnout (ML)      │  │
│  │  behavioral/ ← Habit stacking, implementation intentions  │  │
│  │  notifications/ ← Reminders, alerts (APScheduler)         │  │
│  │  core/ ← ⚠️ OVER-ENGINEERED (business SaaS, not tracker) │  │
│  └───────────────────────────────────────────────────────────┘  │
└────────────────────────────┬────────────────────────────────────┘
                             │
                             ▼
┌─────────────────────────────────────────────────────────────────┐
│              SQLite Database (tracking.db)                      │
└─────────────────────────────────────────────────────────────────┘
```

---

## 📊 Layer Details

### Layer 1: Data Backend (`tracking_app/`) ✅ PRIMARY

**Purpose:** Core data persistence and CRUD operations

**Technology:** Python + SQLite

**Key Files:**
- `storage.py` (2,977 lines) - All CRUD via Storage class
- `models.py` - Data classes (Habit, Task, Goal, HealthEntry, Transaction, TimeEntry)
- `database.py` - SQLite connection management
- `pages/` - 32+ Streamlit pages
- `components/` - Reusable Streamlit components

**Usage Example:**
```python
from tracking_app.storage import Storage

storage = Storage()

# CRUD operations
storage.create_habit("Exercise", icon="🏃")
habits = storage.get_habits()
storage.complete_task(task_id)
storage.delete_habit(habit_id)
```

**Status:** ✅ **Complete** - All features working, used by both Streamlit and FastAPI

---

### Layer 2: Intelligence Layer (`brain/`) 🧠

**Purpose:** Advanced analytics, predictions, and behavioral science

**Technology:** Python + ML libraries (scikit-learn, numpy, pandas)

**Sub-layers:**

#### 📈 Analysis Engine (`brain/analysis/`)
- `correlation.py` (646 lines) - Pearson/Spearman, fragility index
- `prediction.py` (1,057 lines) - Predictive Context Sensitivity (PCS)
- `burnout.py` (507 lines) - Burnout risk prediction

**Usage:**
```python
from brain.analysis.correlation import CorrelationEngine
from brain.analysis.burnout import BurnoutPredictor

correlation = CorrelationEngine().analyze(habits, health)
burnout_risk = BurnoutPredictor().assess(user_data)
```

#### 🧬 Behavioral Science (`brain/behavioral/`)
- `habit_stacking.py` (835 lines) - BJ Fogg methodology
- `implementation_intentions.py` (638 lines) - Gollwitzer (1999)
- `rewards.py` (598 lines) - Variable reward schedules
- `accountability.py` (430 lines) - Social accountability

#### 🔔 Notifications (`brain/notifications/`)
- `engine.py` (400+ lines) - Notification engine
- `scheduler.py` (200+ lines) - APScheduler integration

#### ⚠️ Brain Core (`brain/core/`) - OVER-ENGINEERED

**Critical Note:** The Brain core was designed for a **business management SaaS** (jobs, customers, invoices, crews), NOT personal tracking.

**Evidence from tool files:**
- `job_tools.py` - Job management
- `customer_tools.py` - Customer management
- `crew_management_tools.py` - Staff management
- `materials_tools.py` - Inventory
- `scheduling_tools.py` - Job scheduling

**For personal tracking, use `tracking_app/storage.py` directly for CRUD.**

---

### Layer 3: UI Layer (Choose One)

#### Mode 1: Streamlit Monolith ✅ PRIMARY - RECOMMENDED

**Location:** `tracking_app/pages/`

**Technology:** Python + Streamlit

**Pages:** 32+ fully-functional pages
- Core: Dashboard, Habits, Tasks, Goals, Health, Time, Finances
- Advanced: Emotional Health (RGB model), Achievements, Insights (ML)
- Behavioral: Stacks, Rewards, Challenges
- Social: Friends, Leaderboards, Partners
- Automation: Notifications, Task Alerts, Goal Alerts
- Data: Export, Import, Backup, Lifecycle

**Status:** ✅ **Complete** - 100% of features working

**Run:**
```bash
python run.py
# Opens at http://localhost:8501
```

---

#### Mode 2: React + FastAPI (Phase 13) 🟡 IN PROGRESS

**Backend:** `backend/`
- `main.py` - FastAPI app with CORS
- `routes/` - CRUD endpoints (habits, tasks, goals, health, time, finances)
- `schemas/` - Pydantic validation

**Frontend:** `frontend/src/`
- `App.jsx` - Main React app
- Views: Habits ✅, Tasks ✅, Time ✅, Finances ✅
- Views: Goals ❌, Health ❌, Dashboard ⚠️ Placeholder

**Status:** 🟡 **In Progress** - Backend complete, React has ~10% of Streamlit features

**Run:**
```bash
# Terminal 1: Backend
uvicorn backend.main:app --reload --port 8000

# Terminal 2: Frontend
cd frontend && npm run dev
```

---

#### Mode 3: Legacy JavaScript ❌ DEPRECATED

**Location:** `js/`, `css/`, `index.html`

**Status:** ❌ **Deprecated** - Being migrated to Python/Streamlit

**Issues:**
- Uses browser LocalStorage (~5-10MB limit)
- No query capability
- No server-side processing

---

## 🤔 Why This Architecture?

### Decision 1: Python-First Development

**Rationale:**
- Rapid development with Streamlit
- Single language (Python) for full stack
- Direct SQLite access (no ORM overhead)
- Easy ML integration (scikit-learn, numpy)

**Rule:** `PROJECT_RULES.md` - LANG_001: Python-First

---

### Decision 2: Storage Class Pattern

**Rationale:**
- Single source of truth for data
- Easy to test and maintain
- Type-safe operations
- Works with both Streamlit and FastAPI

**Pattern:**
```python
class Storage:
    """Central data persistence layer."""
    
    def create_habit(self, name, description, icon, frequency):
        # ...
    
    def get_habits(self, include_archived=False):
        # ...
    
    def complete_task(self, task_id):
        # ...
```

---

### Decision 3: Intelligence Layer Separation

**Rationale:**
- ML/analytics separate from CRUD
- Optional usage (not required for basic tracking)
- Easy to extend with new analyses
- Can be called on-demand or scheduled

**Example:**
```python
# Basic CRUD (no intelligence layer needed)
storage.create_habit("Exercise")

# Advanced analytics (call intelligence layer)
from brain.analysis.burnout import BurnoutPredictor
risk = BurnoutPredictor().assess(user_data)
```

---

### Decision 4: Phase 13 Decoupled Architecture

**Rationale:**
- Modern React frontend (if desired)
- REST API for potential mobile apps
- Separation of concerns
- **BUT:** Streamlit remains primary (faster development)

**Implementation:**
- FastAPI routes call `tracking_app/storage.py` directly
- No duplication of business logic
- React frontend is OPTIONAL enhancement

---

## ⚠️ What NOT to Do

### ❌ Don't Use Brain Core for Simple CRUD

**Wrong:**
```python
from brain.core.brain import Brain

brain = Brain()
brain.execute_command(
    CommandEvent(
        type="HABIT_CREATE",
        data={"name": "Exercise"}
    )
)
# Over-engineered! Router → Policies → State Machine → Tools → Audit
```

**Right:**
```python
from tracking_app.storage import Storage

storage = Storage()
storage.create_habit("Exercise")
# Simple, direct, fast
```

---

### ❌ Don't Access Database Directly

**Wrong:**
```python
import sqlite3
conn = sqlite3.connect('tracking.db')
cursor = conn.cursor()
cursor.execute("SELECT * FROM habits")
```

**Right:**
```python
from tracking_app.storage import Storage

storage = Storage()
habits = storage.get_habits()
```

---

### ❌ Don't Create New JavaScript Features

**Wrong:**
```javascript
// js/habits.js - DON'T ADD NEW FEATURES HERE
function createHabit(name) {
    // ...
}
```

**Right:**
```python
# tracking_app/pages/habits.py
def create_habit(name):
    storage.create_habit(name)
```

---

## 📈 Current Status

| Component | Status | Completion | Notes |
|-----------|--------|------------|-------|
| **Data Backend** (`tracking_app/`) | ✅ Complete | 100% | 2,977 lines, all CRUD working |
| **Streamlit UI** (32+ pages) | ✅ Complete | 100% | All features working |
| **Intelligence Layer** (`brain/`) | ✅ Complete | 100% | ML/analytics working |
| **FastAPI Backend** (`backend/`) | ✅ Complete | 100% | All CRUD endpoints |
| **React Frontend** (`frontend/`) | 🟡 In Progress | ~10% | 4 basic views only |
| **Legacy JavaScript** (`js/`) | ❌ Deprecated | - | Being migrated |

---

## 🎯 Recommendations

### For Personal Tracking (Your Use Case)

1. **Use Streamlit as primary UI** - 32+ pages, 100% features
2. **Call `tracking_app/storage.py` directly** - Simple CRUD
3. **Use intelligence layer for analytics** - Correlations, predictions
4. **Ignore Brain core** - Over-engineered for personal tracking
5. **Finish Phase 13 React if desired** - Modern UI, but not required

### For Business Management SaaS (Different Project)

1. **Use Brain core** - Appropriate for complex business logic
2. **Implement full command routing** - Policy enforcement needed
3. **Use state machines** - Job/invoice workflows
4. **Audit trail required** - Compliance, team access

---

## 📚 Related Documents

- `ARCHITECTURAL_MAP.md` - Visual architecture diagrams
- `PROJECT_RULES.md` - Development guidelines (Python-First rule)
- `FEATURE_MAP.md` - Feature-to-file mapping
- `ROADMAP.md` - Development phases
- `brain/README.md` - Brain system documentation
- `docs/research/TECHNICAL_ARCHITECTURES.md` - Architecture research

---

## 🏆 Conclusion

**The architecture is sound, but over-engineered in places:**

✅ **Data Backend** (`tracking_app/`) - Perfect, simple, Pythonic
✅ **Intelligence Layer** (`brain/analysis/`, `brain/behavioral/`) - Brilliant ML/analytics
✅ **Streamlit UI** - Excellent rapid development
⚠️ **Brain Core** (`brain/core/`) - Over-engineered for personal tracking
✅ **Phase 13 FastAPI** - Good optional enhancement
🟡 **Phase 13 React** - Nice-to-have, but only ~10% complete

**Recommendation:** Use what works (Streamlit + storage.py), ignore the complexity (Brain core), and finish React only if you want a modern UI.
