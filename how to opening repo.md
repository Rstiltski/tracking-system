# 📖 How to Open the Veryfyn Repository

**A step-by-step guide to opening and running the Veryfyn Personal Tracking System project.**

---

## 📋 Table of Contents

| # | Section |
|---|---------|
| 1 | [Prerequisites](#1-prerequisites) |
| 2 | [Running Modes](#2-running-modes) |
| 3 | [Running the Streamlit App](#3-running-the-streamlit-app) |
| 4 | [Running the Decoupled Architecture](#4-running-the-decoupled-architecture) |
| 5 | [What We've Done](#5-what-weve-done) |
| 6 | [Quick Reference](#6-quick-reference) |

---

## §1 Prerequisites

Before opening the project, ensure you have the following installed:

| Tool | Purpose | Download |
|------|---------|----------|
| **VS Code** | Code editor | [code.visualstudio.com](https://code.visualstudio.com/) |
| **Git** | Version control | [git-scm.com](https://git-scm.com/) |
| **Python 3.8+** | Backend runtime | [python.org](https://www.python.org/) |
| **Node.js 18+** | Frontend runtime | [nodejs.org](https://nodejs.org/) |
| **Web Browser** | Running the app | Chrome, Firefox, Safari, or Edge |

### Install Python Dependencies

```bash
# Navigate to the project folder
cd tracking-system

# Install Python dependencies
pip install -r requirements.txt
```

### Install Node Dependencies (for React frontend)

```bash
cd tracking-system/frontend
npm install
```

---

## §2 Running Modes

Veryfyn can run in **three different modes**:

| Mode | Frontend | Backend | Port | Use Case |
|------|----------|---------|------|----------|
| **Streamlit** | Streamlit | Python | 8501 | Legacy, quick testing |
| **Decoupled** | React+Vite | FastAPI | 5173/8000 | New Phase 13 architecture |
| **Both** | Both running | Both | All | Development |

---

## §3 Running the Streamlit App (Legacy Mode)

### Quick Start

```bash
# From the tracking-system folder
python run.py
```

This will automatically start the Streamlit server on **port 8501**.

### Alternative: Direct Streamlit Command

```bash
# Navigate to project folder
cd tracking-system

# Run Streamlit directly
streamlit run tracking_app/app.py --server.port 8501
```

### Access the Application

Open your browser and navigate to:

| URL | Description |
|-----|-------------|
| **http://localhost:8501** | Local access (this computer) |

### Theme Toggle

The app now uses Streamlit's default theme. To switch between light and dark mode:
1. Click the **menu** icon (top right)
2. Go to **Settings**
3. Under **Theme**, select **Light** or **Dark**

---

## §4 Running the Decoupled Architecture (Phase 13)

This is the **new recommended mode** using FastAPI + React:

### Option 1: Run Both Frontend and Backend

**Terminal 1 - Backend (FastAPI):**
```bash
cd tracking-system
source .venv/bin/activate  # or activate your virtualenv
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

**Terminal 2 - Frontend (React):**
```bash
cd tracking-system/frontend
npm run dev
```

### Access the Application

| Component | URL | Description |
|-----------|-----|-------------|
| **React Frontend** | http://localhost:5173 | Main application |
| **FastAPI Docs** | http://localhost:8000/docs | API documentation |
| **API Health** | http://localhost:5173/api-test | API test dashboard |

### Option 2: Run Only Backend (for API testing)

```bash
cd tracking-system
source .venv/bin/activate
uvicorn backend.main:app --host 0.0.0.0 --port 8000
```

Then visit http://localhost:8000/docs to test the API interactively.

### API Endpoints Available

| Feature | Endpoint |
|---------|----------|
| Habits CRUD | `/api/habits` |
| Tasks CRUD | `/api/tasks` |
| Goals CRUD | `/api/goals` |
| Health | `/api/health` |
| Time Tracking | `/api/time` |
| Finances | `/api/finances` |

---

## §5 What We've Done

Here's a summary of recent improvements to the Veryfyn project:

### Recent Fixes

| Date | Change |
|------|--------|
| March 2026 | Fixed calendar page - rewrote to work correctly with storage |
| March 2026 | Removed custom theme - now uses Streamlit's default dark/light |
| March 2026 | Fixed Phase12 pages - simplified to render properly |

### Current Architecture (Phase 13)

The project now uses a **decoupled architecture**:

```
┌─────────────────────────────────────────────────────┐
│              React + Vite + Tailwind               │
│                   frontend/src/                    │
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

### Current Features

- **📊 Dashboard** - Overview of all tracking data
- **✅ Habits** - Track daily habits with streaks
- **📝 Tasks** - Todo management
- **💰 Finances** - Budget tracking
- **❤️ Health** - Health metrics
- **⏰ Time** - Time tracking
- **🎯 Goals** - Goal setting and progress
- **🏆 Achievements** - Gamification elements
- **📅 Calendar** - Visual calendar view
- **🔄 Backup/Restore** - Data management

### Tech Stack

| Layer | Technology |
|-------|------------|
| Frontend | React + Vite + Tailwind |
| API | FastAPI (Python) |
| Backend | Python |
| Database | SQLite |

---

## §6 Quick Reference

### Common Commands

| Action | Command |
|--------|---------|
| Start Streamlit | `python run.py` |
| Start FastAPI | `uvicorn backend.main:app --port 8000` |
| Start React | `cd frontend && npm run dev` |
| Stop server | Press `Ctrl+C` in terminal |
| Kill stuck process | `pkill -f streamlit` |

### Port Reference

| Service | Port | URL |
|---------|------|-----|
| Streamlit | 8501 | http://localhost:8501 |
| FastAPI | 8000 | http://localhost:8000/docs |
| React | 5173 | http://localhost:5173 |

### Troubleshooting

**"Port 8501 already in use"**

```bash
# Kill existing Streamlit processes
pkill -f streamlit

# Or find and kill specific process
lsof -i :8501
kill -9 <PID>
```

**"Port 8000 already in use"**

```bash
# Kill existing uvicorn processes
pkill -f uvicorn

# Or find and kill specific process
lsof -i :8000
kill -9 <PID>
```

**Database issues**

The database (`tracking.db`) is auto-initialized on first run. If you need to reset:

```bash
# Delete the database file
rm tracking.db

# Restart the app - it will recreate the database
python run.py
```

---

**Last Updated:** March 2026
