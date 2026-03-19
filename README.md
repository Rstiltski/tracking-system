# 🎯 Veryfyn - Personal Tracking System

**A colorful, gamified personal tracking system for habits, finances, tasks, health, time, and goals with streaks, statistics, and motivation features.**

---

## 🔗 Neural Synapse

**Rule IDs:** DOC_005  
**Core File:** [brain/CORE_RULES.md](brain/CORE_RULES.md)  
**Neural Hub:** [brain/NEURAL_HUB.md](brain/NEURAL_HUB.md)  
**Event Bus:** [brain/nervous_system.py](brain/nervous_system.py)

| Connection | Target | Purpose |
|------------|--------|---------|
| Motor | [brain/CORE_RULES.md](brain/CORE_RULES.md) | Rule registry |
| Rules | [PROJECT_RULES.md](PROJECT_RULES.md) | Development guidelines |
| Patterns | [patterns/](patterns/) | Code templates |

---

## 🧭 Quick Navigation

| Want to... | Go to... |
|------------|----------|
| **AI entry point** | [AI_START_HERE.md](AI_START_HERE.md) |
| **Get started** | [GETTING_STARTED.md](GETTING_STARTED.md) |
| **Understand rules** | [PROJECT_RULES.md](PROJECT_RULES.md) |
| **Find a feature** | [FEATURE_MAP.md](FEATURE_MAP.md) |
| **See roadmap** | [ROADMAP.md](ROADMAP.md) |
| **Check tasks** | [TODO.md](TODO.md) |
| **Read research** | [docs/research/](docs/research/) |
| **Understand Brain** | [brain/README.md](brain/README.md) |

---

## TABLE OF CONTENTS

| # | Section | Key Info |
|---|---------|----------|
| 1 | Overview | What is Veryfyn? |
| 2 | Quick Start | Get running in seconds |
| 3 | Features | Core functionality |
| 4 | Architecture | System design |
| 5 | Brain System | Backend architecture |
| 6 | Project Structure | File organization |
| 7 | Technology Stack | Tools used |
| 8 | Gamification | XP & achievements |
| 9 | Development | Coding standards |
| 10 | Testing | Quality assurance |
| 11 | Configuration | Customization |
| 12 | Troubleshooting | Common fixes |
| 13 | Contributing | How to help |
| 14 | Cross-References | Documentation map |

---

## §1 Overview

Veryfyn is a **complete personal tracking system** with an integrated Brain backend architecture. Originally built as a habit tracker, it has evolved into a **comprehensive life management platform** with:

- **Primary Interface**: Python Streamlit for core operations (32+ pages)
- **Phase 13 Platform**: Next-gen decoupled architecture (React/Tailwind UI + FastAPI Backend)
- **Backend Components**: Python-based Brain system for data management
- **Storage**: Browser LocalStorage + SQLite for Brain operations
- **Gamification**: XP, levels, achievements, and celebrations

### Current Development Status

| Phase | Status | Details |
|-------|--------|---------|
| Phase 13 | ✅ Complete | React + FastAPI Backend (16 API routes) |
| Phase 14 | ✅ Complete | React Frontend (14 views), Page Consolidation |

**The core idea:** Track every aspect of your life with immediate visual feedback, streaks, and rewards - all running locally in your browser.

---

## §2 Quick Start

### Quick Setup

**1. Clone the repository:**
```bash
git clone https://github.com/Rstiltski/tracking-system.git
cd tracking-system
```

**2. Install dependencies:**
```bash
pip install -r requirements.txt
```

**3. Run the system:**
```bash
python3 run.py
```

**4. Open http://localhost:8501 in your browser.**

---

### Main Entry Points

| Entry Point | Description |
|-------------|-------------|
| `run.py` | Main Streamlit application launcher |
| `tracking_app/app.py` | Streamlit app entry point |
| `tracking_app/pages/` | Streamlit UI pages |
| `brain/tools/` | Operation tools |
| `index.html` | Browser-only interface |

---

### Navigation Tips

The app uses **Streamlit native multi-page navigation**:

| Area | Location |
|------|----------|
| All Pages | `tracking_app/pages/` |
| Sidebar | Auto-generated from pages |
| Main App | `tracking_app/app.py` |
| Custom Nav | NOT RECOMMENDED (use Streamlit native) |

**Important:** Do not create custom `st.sidebar.radio()` navigation. Use Streamlit's built-in multi-page app features. See `decisions.log` (DECISION_030).
| UI pages | `tracking_app/pages/` |
| Business logic | `services/` and `database/queries/` |

---

### Browser-Only Mode

For the standalone tracking interface without the backend:

```bash
# Open directly in browser
open index.html
```

No server required - runs entirely in the browser using LocalStorage.

---

## §3 Features

### 📊 Dashboard
- **Single unified dashboard** (`tracking_app/pages/dashboard.py`)
- Overview of all tracking metrics with real data
- Habit Scores using brain models (exponential smoothing algorithm)
- Today's habits with quick completion
- Active tasks with priority indicators
- Goals progress visualization
- Burnout risk indicator with wellbeing check
- Weekly habit completion charts
- Recent activity feed
- Quick action buttons for common tasks
- Motivational quotes

### ✅ Habits Tracker
- Create and track daily habits
- Streak counter for consistency
- Custom icons and colors
- Habit completion logging

### 📋 Tasks & Todos
- Add tasks with priorities and categories
- Due date tracking
- Filter by status (all/active/completed)
- Task completion rewards

### 💰 Finances & Budget
- Track income and expenses
- Category-based transactions
- Budget monitoring
- Expense visualization charts

### ❤️ Health Metrics
- Weight tracking with charts
- Sleep hours logging
- Mood tracking with emoji selector
- Health score calculation

### 🌈 Emotional Health (RGB Model)
- **Scientific emotion tracking** based on neurotransmitter model
- **Three primary emotions**: Dopamine (Joy), Norepinephrine (Stress), Serotonin (Satisfaction)
- **Visual representation**: Emotions map to RGB colors
- **15 quick presets**: Joyful, Excited, Content, Calm, Anxious, etc.
- **Custom sliders**: Fine-tune neurotransmitter levels
- **Pattern detection**: Analyze emotional trends over time
- **Modifiers**: Track Oxytocin (bonding), Endorphins (euphoria), GABA (calm)

### ⏱️ Time & Productivity
- Built-in timer/stopwatch
- **Timer persistence** - Timer state survives page refreshes and browser sessions
- Automatic elapsed time calculation when restoring running timers
- Time entry logging by category
- Time distribution charts
- Daily activity overview

### 🔔 Notifications
- Desktop notifications for reminders
- **Notification settings panel** - Configure notification preferences
- Customizable notification sounds and styles
- Habit, task, and goal reminders
- Configurable reminder types

### 📊 Charts & Visualization
- **Real-time chart updates** - Charts update automatically when data changes
- Weekly, monthly, and daily views
- Financial trends visualization
- Health metrics tracking charts
- Time distribution charts

### ✅ Form Validation
- **Input validation** - Comprehensive form validation system
- Real-time validation feedback
- Custom validation rules for each data type
- Error messages and visual indicators

### 🎯 Goals & Progress
- Set personal goals with targets
- Progress tracking with visual bars
- Deadline management
- Goal completion celebrations

### 🏆 Achievements & Rewards
- XP and level system
- Unlockable achievement badges
- Gamification elements
- Celebration effects (confetti!)

### 🧠 Intelligence & Insights
- **Correlation Engine** - Discover relationships between habits/health/mood
- **Burnout Prediction** - Early warning system with risk indicators
- **Predictive Context Sensitivity** - Understand what influences your habits
- **Natural Language Insights** - Readable analysis of your data
- **Weekly Review** - Automated weekly summary and reflection

### 📊 Habit Analytics
- **Habit Score Algorithm** - Weighted moving average (forgiving, no instant streak reset)
- **Streak Freeze System** - Preserve streaks on missed days
- **Habit Stacking** - Link habits together for chain completion
- **Difficulty Adjustment** - Dynamic difficulty based on performance
- **Habit Templates** - Pre-built habit plans for common goals
- **Self-Experiments** - A/B testing for personal habits

### 🎯 Challenges & Competitions
- Create personal challenges with targets
- Track challenge progress
- Compete with friends
- Challenge completion rewards

### 👥 Social Features
- **Friends System** - Add and manage friends
- **Leaderboards** - Compare progress with friends
- **Template Sharing** - Share habit templates with others
- **Accountability Partners** - Social commitment mechanisms

### 🎁 Variable Rewards
- **Random Loot Drops** - Variable rewards on habit completion
- **Rarity Tiers** - Common, Rare, Epic, Legendary items
- **Mystery Achievements** - Hidden unlockable achievements
- **Bonus XP Events** - Surprise multiplier events

---

## §4 Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    TRACKING SYSTEM UI                           │
│                    (index.html + js/*.js)                        │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                     STORAGE LAYER                               │
│                   (js/storage.js)                               │
│              LocalStorage / IndexedDB                          │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                        BRAIN SYSTEM                             │
│                    (brain/core/brain.py)                       │
│                                                                 │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐    │
│  │  Router  │──▶│ Policies │──▶│  State   │──▶│  Tools   │    │
│  │          │   │          │   │ Machine  │   │          │    │
│  └──────────┘   └──────────┘   └──────────┘   └──────────┘    │
│                                                                 │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │              Audit Log (append-only)                      │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
                                 │
                                 ▼
                        ┌────────────────┐
                        │   Database     │
                        │   (SQLite)     │
                        └────────────────┘
```

---

## §5 Brain System

The Brain is the central nervous system for data operations. Every command flows through the Brain:

1. **Router** validates and routes commands
2. **Policies** check preconditions (security, integrity)
3. **State Machines** validate transitions
4. **Tools** execute operations
5. **Audit Log** records everything

### Key Components

| Component | Location | Purpose |
|-----------|----------|---------|
| Brain Core | `brain/core/` | Main orchestration |
| Tools | `brain/tools/` | 100+ operation tools |
| Policies | `brain/policies/` | Validation rules |
| State Machines | `brain/state/` | Entity lifecycle |
| Audit | `brain/audit/` | Logging & compliance |
| Security | `brain/security/` | Encryption & access |
| Security Playbook | `brain/SECURITY_PLAYBOOK.md` | Security protocols & audit requirements |
| Invariants | `brain/invariants/` | Business rules |
| Immune System | `brain/immune/` | Self-healing |
| Analysis | `brain/analysis/` | Correlation, prediction, burnout detection |
| Behavioral | `brain/behavioral/` | Habit stacking, rewards, accountability |
| Models | `brain/models/` | Habit, streak, emotional state models |
| Notifications | `brain/notifications/` | Reminder engine and scheduling |
| AI | `brain/ai/` | AI suggestion engine |
| Analytics | `brain/analytics/` | Event tracking, heatmaps, timing optimization |
| Backup | `brain/backup/` | Backup management and restoration |
| Lifecycle | `brain/lifecycle/` | Data lifecycle and GDPR compliance |
| Social | `brain/social/` | Friends, competitions, sharing |
| Monitoring | `brain/monitoring/` | System health and anomaly detection |
| Context | `brain/context/` | Context loading and thinking brain |
| Data Export/Import | `brain/data_export/`, `brain/data_import/` | Data portability |
| Rules | `brain/rules/` | Rule engine |
| Fork | `brain/fork/` | Brain forking capabilities |
| Assets | `brain/assets/` | Brain static assets |

**See [brain/README.md](brain/README.md) for detailed Brain documentation.**

---

## §6 Project Structure

```
tracking-system/
├── run.py                  # Main Streamlit launcher
├── index.html              # Browser-only HTML entry point
├── requirements.txt        # Python dependencies
├── pyproject.toml          # Project configuration
│
├── README.md               # This file
├── PROJECT_RULES.md        # Development guidelines
├── TRACKING_SYSTEM_DESIGN.md  # Architecture design
├── ROADMAP.md              # Development roadmap
├── FEATURE_MAP.md          # Feature-to-file mapping
├── GETTING_STARTED.md      # Onboarding guide
├── ARCHITECTURAL_MAP.md    # System architecture map
├── TODO.md                 # Project tracking
├── CONTEXT.md              # AI master reference
│
├── frontend/               # React Frontend (Phase 13)
│   ├── src/               # React source code
│   ├── vite.config.js     # Vite configuration
│   ├── tailwind.config.js # Tailwind CSS config
│   └── package.json       # NPM dependencies
│
├── backend/               # FastAPI Backend (Phase 13)
│   ├── main.py            # FastAPI application
│   ├── config.py          # Configuration
│   ├── routes/            # API routes
│   └── schemas/           # Pydantic schemas
│
├── tracking_app/          # Streamlit Application (Primary)
│   ├── app.py             # Main app entry point
│   ├── models.py          # Data models
│   ├── storage.py         # Storage layer
│   ├── database.py        # Database connection
│   ├── migration.py       # Migration utilities
│   ├── pages/             # Streamlit UI pages
│   │   ├── dashboard.py   # Main dashboard
│   │   ├── habits.py      # Habits tracker
│   │   ├── tasks.py       # Tasks/Todos
│   │   ├── finances.py    # Finances/Budget
│   │   ├── health.py      # Health metrics
│   │   ├── emotional_health.py  # Emotional tracking
│   │   ├── time.py        # Time tracking
│   │   ├── goals.py       # Goals management
│   │   ├── achievements.py # Achievements page
│   │   ├── challenges.py  # Challenges system
│   │   ├── friends.py     # Social features
│   │   ├── leaderboards.py # Leaderboards
│   │   ├── insights.py    # Intelligence insights
│   │   ├── stacks.py      # Habit stacking
│   │   ├── rewards.py     # Variable rewards
│   │   ├── habit_analytics.py  # Habit analytics
│   │   ├── habit_experiments.py # Self-experiments
│   │   ├── weekly_review.py    # Weekly review
│   │   ├── backup_restore.py   # Backup management
│   │   ├── data_export.py      # Data export
│   │   ├── data_import.py      # Data import
│   │   ├── data_lifecycle.py   # Data lifecycle
│   │   ├── goal_alerts.py     # Goal alerts
│   │   ├── habit_reminders.py  # Habit reminders
│   │   ├── notification_settings.py  # Notification config
│   │   ├── task_alerts.py     # Task alerts
│   │   └── template_sharing.py # Template sharing
│   ├── components/        # Reusable UI components
│   │   ├── session.py     # Session management
│   │   ├── sidebar.py     # Sidebar component
│   │   ├── metrics.py     # Metric displays
│   │   ├── charts.py      # Chart components
│   │   ├── achievement_card.py  # Achievement cards
│   │   ├── burnout_card.py      # Burnout indicator
│   │   ├── difficulty_widget.py # Difficulty selector
│   │   ├── relapse_plan_wizard.py  # Relapse planning
│   │   ├── srbai_survey.py     # SRBAI survey
│   │   ├── stack_visualizer.py  # Habit stack viz
│   │   ├── suggestion_card.py   # Suggestion cards
│   │   ├── template_browser.py  # Template browser
│   │   ├── timing_indicator.py # Timing display
│   │   └── tip_card.py         # Tip display
│   └── database_migrations/  # Database migrations
│       ├── achievement_migration.py
│       ├── burnout_migration.py
│       ├── challenge_migration.py
│       ├── difficulty_migration.py
│       ├── experiment_migration.py
│       ├── friend_migration.py
│       ├── habit_stack_migration.py
│       ├── infrastructure_migration.py
│       ├── intention_migration.py
│       ├── note_migration.py
│       ├── relapse_migration.py
│       ├── social_features_migration.py
│       ├── srbai_migration.py
│       ├── suggestion_migration.py
│       ├── template_migration.py
│       └── tip_migration.py
│
├── services/              # Business logic services
│   ├── notifications.py   # Notification service
│   ├── email.py           # Email service
│   ├── ai_provider.py     # AI integration
│   ├── debug_console.py   # Debug console service
│   └── github_cortex_client.py  # GitHub integration
│
├── database/              # Database layer
│   ├── connection.py      # DB connection
│   └── queries/           # Query modules
│
├── brain/                 # Intelligence Layer
│   ├── nervous_system.py  # Main brain orchestrator
│   ├── core/              # Core brain components
│   ├── tools/             # Operation tools
│   ├── brains/            # Specialized brains
│   ├── policies/          # Validation policies
│   ├── state/            # State machines
│   ├── audit/             # Audit logging
│   ├── security/          # Security components
│   ├── invariants/        # Business rules
│   ├── immune/            # Self-healing system
│   ├── privacy/           # Privacy features
│   ├── design/            # Design documentation
│   ├── analysis/          # Correlation & prediction
│   ├── behavioral/        # Behavioral science features
│   ├── models/            # Data models
│   ├── notifications/     # Notification engine
│   ├── ai/                # AI suggestion engine
│   ├── analytics/         # Analytics components
│   ├── backup/            # Backup management
│   └── ...                # And more
│
├── patterns/              # Code patterns
│   ├── prompt_template.md # Prompt framework
│   └── page_module.md     # Page pattern
│
├── css/
│   └── styles.css         # All styles
│
├── js/                    # Legacy JavaScript modules
│   ├── app.js             # Main application controller
│   ├── storage.js         # Data persistence layer
│   └── ...                # (being migrated to Streamlit)
│
├── assets/                # Static assets
│   ├── icons/             # Icon assets
│   └── sounds/            # Sound effects
│
├── backups/               # Backup storage
├── exports/               # Exported data
├── templates/             # Habit templates
│
├── docs/                  # Documentation
│   ├── research/          # Research documents
│   ├── specs/             # Specifications
│   ├── schemas/           # Data schemas
│   └── guides/            # User guides
│
└── tests/                 # Test suite
