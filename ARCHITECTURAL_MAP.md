# Architectural Map for Veryfyn Tracking System

## System Overview

The Veryfyn Tracking System is a comprehensive personal tracking platform with **three architectural layers**:

1. **Data Backend** (`tracking_app/`) - Core data persistence and CRUD operations
2. **Intelligence Layer** (`brain/`) - AI/ML analytics, behavioral science, predictions
3. **UI Layer** - Streamlit (monolith) OR React + FastAPI (Phase 13 decoupled)

### ⚠️ Critical Architecture Distinction

**The Brain is NOT the data backend.** The Brain is an **intelligence overlay** for AI-driven operations:

| Layer | Purpose | Files | Used For |
|-------|---------|-------|----------|
| **📦 Data Backend** | Data persistence & CRUD | `tracking_app/storage.py`, `models.py`, `database.py` | All habit/task/goal data storage |
| **🧠 Intelligence Layer** | AI/ML analytics & insights | `brain/analysis/`, `brain/behavioral/`, `brain/notifications/` | Correlations, predictions, burnout detection, habit stacking |
| **🎨 UI Layer** | User interface | Streamlit pages OR React + FastAPI | User interaction |

**Simple CRUD operations** (create habit, complete task) → Call `tracking_app/storage.py` **directly**

**AI commands** (analyze patterns, suggest interventions) → Flow through `brain/core/brain.py`

---

## Architecture Modes

### Mode 1: Streamlit Monolith (Primary - Recommended)
```
┌─────────────────────────────────────────┐
│   Streamlit UI (32+ pages)              │
│   tracking_app/pages/                   │
│   - dashboard.py                        │
│   - habits.py, tasks.py, goals.py       │
│   - health.py, time.py, finances.py     │
│   - 25+ advanced pages                  │
└───────────────┬─────────────────────────┘
                │ Direct Python calls
                ▼
┌─────────────────────────────────────────┐
│   Data Backend (tracking_app/)          │
│   - storage.py    ← All CRUD here       │
│   - models.py     ← Data classes        │
│   - database.py   ← SQLite connection   │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│   Intelligence Layer (brain/)           │
│   - analysis/       ← Correlations      │
│   - behavioral/     ← Habit science     │
│   - notifications/  ← Reminders         │
└───────────────┬─────────────────────────┘
                │
                ▼
┌─────────────────────────────────────────┐
│   SQLite Database (tracking.db)         │
└─────────────────────────────────────────┘
```

**Status:** ✅ **Complete** - 32+ pages, all features working

---

### Mode 2: Decoupled React + FastAPI (Phase 13)
```
┌─────────────────────────────────────────────────────┐
│              React Frontend (frontend/src/)         │
│   ┌─────────────────────────────────────────────┐   │
│   │  App.jsx                                    │   │
│   │  ├── HabitsView (CRUD) ✅                   │   │
│   │  ├── TasksView (CRUD) ✅                    │   │
│   │  ├── TimeView (entries) ✅                  │   │
│   │  ├── FinancesView (transactions) ✅         │   │
│   │  ├── GoalsView ❌ NOT IMPLEMENTED           │   │
│   │  ├── HealthView ❌ NOT IMPLEMENTED          │   │
│   │  └── Dashboard ⚠️ Placeholder only          │   │
│   └─────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────┘
                         │ HTTP/REST
                         ▼
┌─────────────────────────────────────────────────────┐
│           FastAPI Backend (backend/)                │
│   main.py (CORS, routers)                           │
│   ├── routes/habits.py → calls storage.py           │
│   ├── routes/tasks.py → calls storage.py            │
│   ├── routes/goals.py → calls storage.py            │
│   ├── routes/health.py → calls storage.py           │
│   ├── routes/time.py → calls storage.py             │
│   └── routes/finances.py → calls storage.py         │
│   schemas/ (Pydantic validation)                    │
└────────────────────────┬────────────────────────────┘
                         │ Direct Python calls
                         ▼
┌─────────────────────────────────────────────────────┐
│        Data Backend (tracking_app/ - unchanged!)    │
│   ┌─────────────────────────────────────────────┐   │
│   │  storage.py    → All CRUD operations        │   │
│   │  models.py     → Habit, Task, Goal, etc.    │   │
│   │  database.py   → SQLite connection          │   │
│   └─────────────────────────────────────────────┘   │
└────────────────────────┬────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│   SQLite Database (tracking.db)                     │
│   - habits, tasks, goals, health_entries            │
│   - transactions, time_entries                      │
└─────────────────────────────────────────────────────┘
```

**Status:** 🟡 **In Progress** - Backend complete, React frontend has ~10% of Streamlit features

---

### Mode 3: Legacy JavaScript (DEPRECATED - Being Migrated)
```
┌─────────────────────────────────────────┐
│   Legacy HTML/JS Frontend               │
│   index.html                            │
│   js/habits.js, tasks.js, etc.          │
│   css/styles.css                        │
└───────────────┬─────────────────────────┘
                │ LocalStorage (browser)
                ▼
┌─────────────────────────────────────────┐
│   Browser LocalStorage                  │
│   ⚠️ Limited to ~5-10MB                 │
│   ⚠️ No query capability                │
│   ⚠️ Being migrated to Python/Streamlit │
└─────────────────────────────────────────┘
```

**Status:** ❌ **Deprecated** - Migration to Python/Streamlit in progress

## Component Structure

### 1. Data Backend (`tracking_app/`) - PRIMARY BACKEND ✅

**Location:** `tracking-system/tracking_app/`

**Purpose:** Core data persistence and CRUD operations for all tracking data

**Technology:** Python + SQLite

**Components:**
- `storage.py` (2,977 lines) - All CRUD operations via Storage class
- `models.py` - Data classes (Habit, Task, Goal, HealthEntry, Transaction, TimeEntry)
- `database.py` - SQLite connection management
- `pages/` - 32+ Streamlit pages (habits, tasks, goals, health, time, finances, etc.)
- `components/` - Reusable Streamlit components (sidebar, charts, metrics)

**Usage:**
```python
# Simple CRUD - Direct data operations
from tracking_app.storage import Storage

storage = Storage()
storage.create_habit("Exercise")      # Create
habits = storage.get_habits()         # Read
storage.complete_task(task_id)        # Update
storage.delete_habit(habit_id)        # Delete
```

**Status:** ✅ **Complete** - All features working, used by both Streamlit and FastAPI

---

### 2. Intelligence Layer (`brain/`) - AI/ML Analytics 🧠

**Location:** `tracking-system/brain/`

**Purpose:** Advanced analytics, predictions, and behavioral science

**Technology:** Python + ML libraries (scikit-learn, numpy, pandas)

**Components:**

#### Analysis Engine (`brain/analysis/`)
- `correlation.py` (646 lines) - Pearson/Spearman correlations, fragility index
- `prediction.py` (1,057 lines) - Predictive Context Sensitivity (PCS) engine
- `burnout.py` (507 lines) - Burnout risk prediction with interventions

#### Behavioral Science (`brain/behavioral/`)
- `habit_stacking.py` (835 lines) - BJ Fogg habit stacking methodology
- `implementation_intentions.py` (638 lines) - Gollwitzer implementation intentions
- `rewards.py` (598 lines) - Variable reward schedules
- `accountability.py` (430 lines) - Social accountability systems

#### Notifications (`brain/notifications/`)
- `engine.py` (400+ lines) - Notification engine
- `scheduler.py` (200+ lines) - APScheduler integration
- Task alerts, goal alerts, habit reminders

#### Brain Core (`brain/core/`) - ⚠️ OVER-ENGINEERED
- `brain.py` - AI command router for business operations
- `router.py`, `policies/`, `state/`, `tools/` - Enterprise command processing

**⚠️ Critical Note:** The Brain core (`brain/core/`) was designed for a **business management SaaS** (jobs, customers, invoices, crews), NOT personal tracking. For simple CRUD operations, use `tracking_app/storage.py` directly.

**Usage:**
```python
# Analytics - Call intelligence layer directly
from brain.analysis.correlation import CorrelationEngine
from brain.analysis.burnout import BurnoutPredictor

correlation = CorrelationEngine().analyze(habits, health)
burnout_risk = BurnoutPredictor().assess(user_data)
```

**Status:** ✅ **Complete** - Advanced ML/analytics working

---

### 3. FastAPI Backend (`backend/`) - Phase 13 API Layer

**Location:** `tracking-system/backend/`

**Purpose:** REST API for decoupled React frontend

**Technology:** FastAPI + Pydantic + Uvicorn

**Components:**
- `main.py` - FastAPI app with CORS, routers
- `config.py` - Settings with pydantic-settings
- `routes/` - API endpoints (habits, tasks, goals, health, time, finances)
- `schemas/` - Pydantic models for validation

**Usage:**
```python
# Backend routes call tracking_app storage
from tracking_app.storage import Storage

@router.get("/api/habits")
async def get_habits():
    storage = Storage()
    habits = storage.get_habits()
    return {"habits": [h.to_dict() for h in habits]}
```

**Status:** ✅ **Complete** - All CRUD endpoints working

---

### 4. React Frontend (`frontend/`) - Phase 13 UI

**Location:** `tracking-system/frontend/`

**Purpose:** Modern React-based user interface

**Technology:** React 18 + Vite + Tailwind CSS + Axios

**Components:**
- `src/App.jsx` - Main app with navigation
- Views: Habits, Tasks, Time, Finances (✅ Complete)
- Views: Goals, Health, Dashboard (❌ NOT IMPLEMENTED)

**Usage:**
```javascript
// React calls FastAPI endpoints
import axios from 'axios'

const API_BASE = '/api'

const response = await axios.get(`${API_BASE}/habits`)
const habits = response.data.habits
```

**Status:** 🟡 **In Progress** - Only 4 basic CRUD views implemented (~10% of Streamlit features)

---

### 5. Legacy JavaScript (`js/`) - DEPRECATED

**Location:** `tracking-system/js/`

**Status:** ❌ **Deprecated** - Being migrated to Python/Streamlit

**Files:**
- `app.js`, `storage.js`, `habits.js`, `tasks.js`, etc.
- Uses browser LocalStorage (limited to ~5-10MB)

**Migration:** All functionality being rebuilt in Python/Streamlit

## API Contract

| Feature | Endpoint | Methods |
|---------|----------|---------|
| Habits | `/api/habits` | GET, POST |
| Habit | `/api/habits/{id}` | GET, PUT, DELETE |
| Tasks | `/api/tasks` | GET, POST |
| Task | `/api/tasks/{id}` | GET, PUT, DELETE |
| Task Complete | `/api/tasks/{id}/complete` | POST |
| Goals | `/api/goals` | GET, POST |
| Goal | `/api/goals/{id}` | GET, PUT, DELETE |
| Goal Progress | `/api/goals/{id}/progress` | POST |
| Health | `/api/health` | GET, POST |
| Health Entry | `/api/health/{id}` | GET, PUT, DELETE |
| Time Entries | `/api/time/entries` | GET, POST |
| Time Entry | `/api/time/entries/{id}` | GET, PUT, DELETE |
| Time Summary | `/api/time/summary` | GET |
| Timer | `/api/time/timer` | GET, POST, DELETE |
| Transactions | `/api/finances/transactions` | GET, POST |
| Transaction | `/api/finances/transactions/{id}` | GET, PUT, DELETE |
| Budget | `/api/finances/budget` | GET, POST |

### Test Endpoints
| Feature | Endpoint | Methods |
|---------|----------|----------|
| Health Check | `/health` | GET |
| API Status | `/api/status` | GET |
| DB Test | `/api/db/test` | GET |
| Swagger Docs | `/docs` | GET |

## Data Models

### Backend Storage Models (tracking_app/models.py)
- `Habit` - Trackable habits with frequency
- `Task` - Todo items with status
- `Goal` - Goals with targets and deadlines
- `HealthEntry` - Health metrics records
- `Transaction` - Financial transactions
- `TimeEntry` - Time tracking records

### API Schemas (backend/schemas/)
- Pydantic models for request validation
- Response models with serialization
- All schemas in respective feature files

## Integration Points

### API → Storage
```python
# Backend routes call tracking_app storage methods
from tracking_app.storage import Storage
storage = Storage()

# Example: Get all habits
habits = storage.get_all_habits()
```

### Frontend → API
```javascript
// React calls FastAPI endpoints
const response = await fetch('http://localhost:8000/api/habits');
const habits = await response.json();
```

## Running the Decoupled System

### Backend
```bash
cd tracking-system
source .venv/bin/activate
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

### Frontend
```bash
cd tracking-system/frontend
npm run dev
```

### Both
- Backend runs on `http://localhost:8000`
- Frontend runs on `http://localhost:5173`
- CORS is configured to allow frontend access
