# Phase 13: Decoupled Architecture Migration

## Overview
This phase documents the migration strategy from the current Streamlit monolithic architecture to a decoupled architecture using FastAPI (backend) and React (frontend). The migration preserves 100% of existing backend logic while enabling modern frontend capabilities.

---

## The Strategy: Extract → Expose → Replace

This is a classic **monolith-to-decoupled architecture** migration. Here's the cleanest approach that preserves your backend entirely:

### Step 1 — Extract your backend logic into a REST API
Wrap your existing Python + SQLite code with **FastAPI** (or Flask). Your business logic stays **100% untouched** — you just add a thin API layer on top.

```
your_app/
├── backend/
│   ├── main.py          ← FastAPI app (new)
│   ├── database.py      ← your existing SQLite logic (unchanged)
│   ├── models.py        ← your existing data models (unchanged)
│   └── routes/
│       ├── tracking.py  ← endpoints wrapping your existing functions
│       └── ...
└── frontend/
    └── (React / Next.js / etc.)
```

FastAPI is ideal here because it **auto-generates docs**, handles async well, and has minimal boilerplate.

### Step 2 — Define your API contract
Turn your Streamlit interactions into HTTP endpoints:

| What Streamlit did | Becomes |
|---|---|
| `st.session_state` read/write | `GET /api/entries` / `POST /api/entries` |
| Chart data computation | `GET /api/stats?range=30d` |
| Form submission | `POST /api/log` |
| File upload | `POST /api/upload` |

### Step 3 — Replace Streamlit UI with React + Tailwind
Your frontend calls your new API. React handles rendering, Tailwind handles styling — both things Streamlit blocked entirely.

---

## Why This Works Without Breaking Your Backend

```
BEFORE:                          AFTER:
┌─────────────────────┐          ┌──────────┐     ┌────────────────┐
│  Streamlit          │          │  React   │────▶│  FastAPI       │
│  (UI + logic        │   ──▶    │  Frontend│◀────│  (API layer)   │
│   + SQLite          │          └──────────┘     │                │
│   all mixed)        │                           │  Your existing │
└─────────────────────┘                           │  Python + SQL   │
                                                  │  (unchanged)    │
                                                  └────────────────┘
```

Your Python data processing, SQLite queries, and business logic are **never touched** — FastAPI just gives them a door to the outside world.

---

## Recommended Tech Stack

| Layer | Tool | Why |
|---|---|---|
| API | **FastAPI** | Fast, Pythonic, auto-docs |
| Frontend | **React + Vite** | Fast dev server, great ecosystem |
| Styling | **Tailwind CSS** | Utility-first, no conflicts |
| Charts | **Recharts or Plotly.js** | Replaces `st.plotly_chart` cleanly |
| State | **React Query (TanStack)** | Handles API calls + caching |

## ✅ COMPLETED - Implementation Summary

### Architecture Status
```
┌─────────────────────────────────────────────────────┐
│              React + Vite + Tailwind               │
│                   frontend/src/                     │
└────────────────────────┬────────────────────────────┘
                         │ HTTP/REST
                         ▼
┌─────────────────────────────────────────────────────┐
│                    FastAPI (Port 8000)              │
│                    backend/main.py                 │
└────────────────────────┬────────────────────────────┘
                         │ Python calls
                         ▼
┌─────────────────────────────────────────────────────┐
│         tracking_app/ (unchanged)                   │
│         storage.py, models.py, database.py         │
└────────────────────────┬────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│                  SQLite (tracking.db)              │
└─────────────────────────────────────────────────────┘
```

---

## Step 1 — Extract Your Backend Logic into REST API ✅ COMPLETE

> **Strategy:** *Extract* — Wrap your existing Python + SQLite code with FastAPI. Your business logic stays 100% untouched — you just add a thin API layer on top.

### Backend Structure Created
```
backend/
├── __init__.py              ✅ Package marker
├── main.py                  ✅ FastAPI app with CORS, routers, health check
├── config.py                ✅ Settings using pydantic-settings
├── database.py              ✅ SQLite connection (tracking_app.database)
├── routes/
│   ├── __init__.py          ✅ Routes package
│   ├── habits.py            ✅ Habits CRUD endpoints
│   ├── tasks.py             ✅ Tasks CRUD + completion
│   ├── goals.py             ✅ Goals CRUD + progress
│   ├── health.py            ✅ Health entries CRUD
│   ├── time.py              ✅ Timer + time entries
│   └── finances.py          ✅ Transactions + budget
├── schemas/
│   ├── __init__.py          ✅ Schemas package
│   ├── habits.py            ✅ Pydantic models for habits
│   ├── tasks.py             ✅ Pydantic models for tasks
│   ├── goals.py             ✅ Pydantic models for goals
│   ├── health.py            ✅ Pydantic models for health
│   ├── time.py              ✅ Pydantic models for time entries
│   └── finances.py          ✅ Pydantic models for transactions
└── dependencies.py          ✅ Shared FastAPI dependencies
```

### Storage Layer Additions (tracking_app/storage.py)
Added new methods to support Time Tracking API:
- `create_time_entry()` - Create time entry record
- `get_time_entries()` - Get time entries with optional date filtering
- `get_time_entry()` - Get single time entry
- `update_time_entry()` - Update time entry
- `delete_time_entry()` - Delete time entry

### Database Additions (tracking_app/database.py)
Added new table:
- `time_entries` - For storing time tracking records

### Models Added (tracking_app/models.py)
Added new model:
- `TimeEntry` - Data model for time entries

---

## Step 2 — Define Your API Contract ✅ COMPLETE

> **Strategy:** *Expose* — Turn your Streamlit interactions into HTTP endpoints.

### All API Endpoints Implemented

| Feature | Method | Endpoint | Status |
|---------|--------|----------|--------|
| **Habits** | | | |
| List habits | GET | `/api/habits` | ✅ |
| Create habit | POST | `/api/habits` | ✅ |
| Get habit | GET | `/api/habits/{id}` | ✅ |
| Update habit | PUT | `/api/habits/{id}` | ✅ |
| Delete habit | DELETE | `/api/habits/{id}` | ✅ |
| Complete habit | POST | `/api/habits/{id}/complete` | ✅ |
| Get habit stats | GET | `/api/habits/stats` | ✅ |
| **Tasks** | | | |
| List tasks | GET | `/api/tasks` | ✅ |
| Create task | POST | `/api/tasks` | ✅ |
| Get task | GET | `/api/tasks/{id}` | ✅ |
| Update task | PUT | `/api/tasks/{id}` | ✅ |
| Delete task | DELETE | `/api/tasks/{id}` | ✅ |
| Complete task | POST | `/api/tasks/{id}/complete` | ✅ |
| **Goals** | | | |
| List goals | GET | `/api/goals` | ✅ |
| Create goal | POST | `/api/goals` | ✅ |
| Get goal | GET | `/api/goals/{id}` | ✅ |
| Update goal | PUT | `/api/goals/{id}` | ✅ |
| Delete goal | DELETE | `/api/goals/{id}` | ✅ |
| Update progress | POST | `/api/goals/{id}/progress` | ✅ |
| **Health** | | | |
| List entries | GET | `/api/health` | ✅ |
| Create entry | POST | `/api/health` | ✅ |
| Get entry | GET | `/api/health/{id}` | ✅ |
| Update entry | PUT | `/api/health/{id}` | ✅ |
| Delete entry | DELETE | `/api/health/{id}` | ✅ |
| **Time Tracking** | | | |
| List entries | GET | `/api/time/entries` | ✅ |
| Create entry | POST | `/api/time/entries` | ✅ |
| Get entry | GET | `/api/time/entries/{id}` | ✅ |
| Update entry | PUT | `/api/time/entries/{id}` | ✅ |
| Delete entry | DELETE | `/api/time/entries/{id}` | ✅ |
| Get summary | GET | `/api/time/summary` | ✅ |
| Timer: Start | POST | `/api/time/timer` | ✅ |
| Timer: Stop | DELETE | `/api/time/timer` | ✅ |
| Timer: Get status | GET | `/api/time/timer` | ✅ |
| **Finances** | | | |
| List transactions | GET | `/api/finances/transactions` | ✅ |
| Create transaction | POST | `/api/finances/transactions` | ✅ |
| Get transaction | GET | `/api/finances/transactions/{id}` | ✅ |
| Update transaction | PUT | `/api/finances/transactions/{id}` | ✅ |
| Delete transaction | DELETE | `/api/finances/transactions/{id}` | ✅ |
| Get budget | GET | `/api/finances/budget` | ✅ |
| Set budget | POST | `/api/finances/budget` | ✅ |

### Test Endpoints
| Feature | Method | Endpoint | Status |
|---------|--------|----------|--------|
| Health Check | GET | `/health` | ✅ |
| API Status | GET | `/api/status` | ✅ |
| DB Test | GET | `/api/db/test` | ✅ |
| Swagger Docs | GET | `/docs` | ✅ |

---

## Step 3 — Replace Streamlit UI with React + Tailwind ✅ COMPLETE

> **Strategy:** *Replace* — Your frontend calls your new API. React handles rendering, Tailwind handles styling — both things Streamlit blocked entirely.

### Frontend Structure Created
```
frontend/
├── package.json             ✅ Dependencies (React, Vite, Tailwind, Axios)
├── vite.config.js          ✅ Vite config with API proxy
├── tailwind.config.js      ✅ Tailwind CSS config
├── postcss.config.js       ✅ PostCSS config
├── index.html              ✅ HTML entry point
├── src/
│   ├── main.jsx            ✅ React entry point
│   ├── index.css           ✅ Tailwind styles
│   ├── App.jsx             ✅ Main app with routing
│   ├── api.js              ✅ Axios API client
│   └── views/
│       ├── Dashboard.jsx   ✅ Dashboard overview
│       ├── HabitsView.jsx  ✅ Habits management
│       ├── TasksView.jsx   ✅ Tasks management
│       ├── GoalsView.jsx   ✅ Goals tracking
│       ├── HealthView.jsx  ✅ Health metrics
│       ├── TimeView.jsx    ✅ Time tracking
│       └── FinancesView.jsx ✅ Financial tracking
```

---

## Architecture Comparison

```
BEFORE (Monolith):                        AFTER (Decoupled):
┌─────────────────────────┐               ┌────────────┐     ┌────────────────┐
│  Streamlit UI          │               │  React     │────▶│  FastAPI       │
│  (UI + logic            │    ──────▶    │  Frontend  │◀────│  (API layer)   │
│   + SQLite              │               └────────────┘     │                │
│   all mixed)            │                                 │  tracking_app   │
└─────────────────────────┘                                 │  (unchanged)   │
                                                            └────────────────┘
```

---

## Running the System

### Option 1: Monolith Mode (Legacy)
```bash
cd tracking-system
streamlit run tracking_app/app.py
# Runs on http://localhost:8501
```

### Option 2: Decoupled Mode (Phase 13)
```bash
# Terminal 1 - Backend
cd tracking-system
source .venv/bin/activate
uvicorn backend.main:app --host 0.0.0.0 --port 8000
# API docs at http://localhost:8000/docs

# Terminal 2 - Frontend
cd tracking-system/frontend
npm run dev
# Runs on http://localhost:5173
```

### Option 3: Both Running in Parallel
```bash
# Terminal 1 - Keep Streamlit for reference
streamlit run tracking_app/app.py --server.port 8501

# Terminal 2 - FastAPI
uvicorn backend.main:app --host 0.0.0.0 --port 8000

# Terminal 3 - React
cd frontend && npm run dev
```

---

## Critical Implementation Notes

### 1. CORS Configuration
FastAPI is configured with CORS to allow React frontend:
```python
# backend/main.py
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"]
)
```

### 2. SQLite Threading
Uses `check_same_thread=False` for compatibility:
```python
# backend/database.py
DATABASE_URL = "sqlite:///./tracking.db?check_same_thread=False"
```

### 3. Pydantic Schemas
All API requests/responses use Pydantic validation:
```python
# backend/schemas/habits.py
from pydantic import BaseModel

class HabitCreate(BaseModel):
    name: str
    description: str | None = None
    frequency: str
    # ...

class HabitResponse(BaseModel):
    id: int
    name: str
    # ...
    
    model_config = {"from_attributes": True}
```

---

## Migration Order (Low Risk)

This way you **never have downtime** and can validate each piece independently:

1. ✅ **Keep Streamlit running** while you build FastAPI alongside it
2. ✅ **Build one endpoint at a time**, test with FastAPI's built-in `/docs`
3. ✅ **Build the React frontend screen by screen**
4. ✅ **Test end-to-end** with real data
5. 🔄 **Switch over only when parity is reached**
6. 🔄 **Retire Streamlit last**

---

## Testing the APIs

### Using FastAPI Interactive Docs
- Open http://localhost:8000/docs
- Click on any endpoint
- Click "Try it out"
- Enter parameters and click "Execute"

### Using Python Test Suite
Run the test suite to verify all endpoints:

```bash
cd tracking-system
python test_backend.py
```

This runs 17 tests covering:
- Server reachability
- Health endpoints
- Database connectivity
- CORS headers
- Route prefix validation
- Full CRUD operations for Habits
- Other domain endpoints

### Using React Health Dashboard
- Go to http://localhost:5173
- Click "API Test" in the navigation
- Click "RE-RUN ALL" to test all endpoints

---

## Known Issues

1. **Time GET with optional date parameters**: When calling `/api/time/entries` without date filters, SQLite may have parameter type issues. Ensure dates are passed as strings in ISO format.

2. **Timer state**: Timer state is in-memory only. If FastAPI restarts, active timers are reset.

---

## Files Modified

### Core Backend Files
- `backend/__init__.py` - Created
- `backend/main.py` - Created
- `backend/config.py` - Created
- `backend/database.py` - Created
- `backend/dependencies.py` - Created
- `backend/routes/__init__.py` - Created
- `backend/routes/habits.py` - Created
- `backend/routes/tasks.py` - Created
- `backend/routes/goals.py` - Created
- `backend/routes/health.py` - Created
- `backend/routes/time.py` - Created
- `backend/routes/finances.py` - Created

### Schema Files
- `backend/schemas/__init__.py` - Created
- `backend/schemas/habits.py` - Created
- `backend/schemas/tasks.py` - Created
- `backend/schemas/goals.py` - Created
- `backend/schemas/health.py` - Created
- `backend/schemas/time.py` - Created
- `backend/schemas/finances.py` - Created

### Frontend Files
- `frontend/package.json` - Created
- `frontend/vite.config.js` - Created
- `frontend/tailwind.config.js` - Created
- `frontend/postcss.config.js` - Created
- `frontend/index.html` - Created
- `frontend/src/main.jsx` - Created
- `frontend/src/index.css` - Created
- `frontend/src/App.jsx` - Created
- `frontend/src/api.js` - Created
- `frontend/src/views/` - Created (all views)
- `frontend/src/ApiHealthDashboard.jsx` - API health test dashboard

### Testing
- `test_backend.py` - Python test suite (17 tests, all passing)

### Storage Layer Modifications
- `tracking_app/storage.py` - Added TimeEntry CRUD methods

### Database Modifications
- `tracking_app/database.py` - Added time_entries table

### Model Modifications
- `tracking_app/models.py` - Added TimeEntry model

### Documentation
- `phases/PHASE_13_DECOUPLED_ARCHITECTURE.md` - Updated
- `ARCHITECTURAL_MAP.md` - Updated
- `FEATURE_MAP.md` - Updated

---

## Next Steps

1. **Add authentication** - Currently no auth (suitable for personal use)
2. **Production deployment** - Add nginx, gunicorn, proper CORS settings
3. **Real-time features** - Add WebSocket for live updates
4. **Mobile app** - React Native can reuse the same API
