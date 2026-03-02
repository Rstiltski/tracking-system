# 🎯 Veryfyn - Personal Tracking System

**A colorful, gamified personal tracking system for habits, finances, tasks, health, time, and goals with streaks, statistics, and motivation features.**

---

## 🧭 Quick Navigation

| Want to... | Go to... |
|------------|----------|
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

- **Frontend**: Pure HTML/CSS/JavaScript (no framework dependencies)
- **Backend**: Python-based Brain system for data management
- **Storage**: Browser LocalStorage + SQLite for Brain operations
- **Gamification**: XP, levels, achievements, and celebrations

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

| Area | Location |
|------|----------|
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
│                    (index.html + js/*.js)                       │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                     STORAGE LAYER                               │
│                   (js/storage.js)                               │
│              LocalStorage / IndexedDB                           │
└────────────────────────────────┬────────────────────────────────┘
                                 │
                                 ▼
┌─────────────────────────────────────────────────────────────────┐
│                        BRAIN SYSTEM                             │
│                    (brain/core/brain.py)                        │
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
│
├── tracking_app/           # Streamlit Application
│   ├── app.py              # Main app entry point
│   ├── models.py           # Data models
│   ├── storage.py          # Storage layer
│   ├── database.py         # Database connection
│   ├── migration.py        # Migration utilities
│   ├── pages/              # Streamlit UI pages
│   │   ├── dashboard.py    # Main dashboard
│   │   ├── habits.py       # Habits tracker
│   │   ├── tasks.py        # Tasks/Todos
│   │   ├── finances.py     # Finances/Budget
│   │   ├── health.py       # Health metrics
│   │   ├── emotional_health.py  # Emotional tracking
│   │   ├── time.py         # Time tracking
│   │   ├── goals.py        # Goals management
│   │   ├── achievements.py # Achievements page
│   │   ├── challenges.py   # Challenges system
│   │   ├── friends.py      # Social features
│   │   ├── leaderboards.py # Leaderboards
│   │   ├── insights.py     # Intelligence insights
│   │   ├── stacks.py       # Habit stacking
│   │   ├── rewards.py      # Variable rewards
│   │   ├── habit_analytics.py   # Habit analytics
│   │   ├── habit_experiments.py # Self-experiments
│   │   ├── weekly_review.py     # Weekly review
│   │   ├── backup_restore.py    # Backup management
│   │   ├── data_export.py       # Data export
│   │   ├── data_import.py       # Data import
│   │   ├── data_lifecycle.py    # Data lifecycle
│   │   ├── goal_alerts.py       # Goal alerts
│   │   ├── habit_reminders.py   # Habit reminders
│   │   ├── notification_settings.py  # Notification config
│   │   ├── task_alerts.py       # Task alerts
│   │   └── template_sharing.py  # Template sharing
│   ├── components/         # Reusable UI components
│   │   ├── session.py      # Session management
│   │   ├── sidebar.py      # Sidebar component
│   │   ├── metrics.py      # Metric displays
│   │   ├── charts.py       # Chart components
│   │   ├── achievement_card.py  # Achievement cards
│   │   ├── burnout_card.py      # Burnout indicator
│   │   ├── difficulty_widget.py # Difficulty selector
│   │   ├── relapse_plan_wizard.py  # Relapse planning
│   │   ├── srbai_survey.py      # SRBAI survey
│   │   ├── stack_visualizer.py  # Habit stack viz
│   │   ├── suggestion_card.py   # Suggestion cards
│   │   ├── template_browser.py  # Template browser
│   │   ├── timing_indicator.py  # Timing display
│   │   └── tip_card.py          # Tip display
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
├── services/               # Business logic services
│   ├── notifications.py    # Notification service
│   ├── email.py            # Email service
│   ├── ai_provider.py      # AI integration
│   ├── debug_console.py    # Debug console service
│   └── github_cortex_client.py  # GitHub integration
│
├── database/               # Database layer
│   ├── connection.py       # DB connection
│   └── queries/            # Query modules
│
├── css/
│   └── styles.css          # All styles (organized by sections)
│
├── js/
│   ├── app.js              # Main application controller
│   ├── storage.js          # Data persistence layer
│   ├── habits.js           # Habits module
│   ├── tasks.js            # Tasks/Todos module
│   ├── finances.js         # Finances/Budget module
│   ├── health.js           # Health metrics module
│   ├── time.js             # Time tracking module
│   ├── goals.js            # Goals module
│   ├── achievements.js     # Achievements/gamification
│   ├── charts.js           # Chart visualization
│   ├── notifications.js    # Notification system
│   ├── dataExport.js       # Import/export functionality
│   ├── habit-stacking.js   # Habit stacking (frontend)
│   ├── implementation-intentions.js  # Implementation intentions
│   ├── rewards.js          # Variable rewards (frontend)
│   ├── validation.js       # Form validation
│   ├── enhanced-charts.js  # Advanced charts
│   ├── enhanced-goals.js   # Enhanced goals module
│   ├── enhanced-goal-model.js  # Enhanced goal model
│   └── variable-goal-tracker.js  # Variable goal tracking
│
├── assets/                 # Static assets
│   ├── icons/              # Icon assets
│   └── sounds/             # Sound effects
│
├── backups/                # Backup storage
├── exports/                # Exported data
├── templates/              # Habit templates
│
├── docs/                   # Documentation
│   ├── research/           # Research documents
│   ├── specs/              # Specifications
│   ├── schemas/            # Data schemas
│   └── guides/             # User guides
│
├── tests/                  # Test suite
│
├── phases/                 # Phase documentation
│
└── brain/                  # Backend System
    ├── nervous_system.py   # Main brain orchestrator
    ├── core/               # Core brain components
    ├── tools/              # Operation tools
    ├── brains/             # Specialized brains
    ├── policies/           # Validation policies
    ├── state/              # State machines
    ├── audit/              # Audit logging
    ├── security/           # Security components
    ├── invariants/         # Business rules
    ├── immune/             # Self-healing system
    ├── privacy/            # Privacy features
    ├── design/             # Design documentation
    ├── analysis/           # Correlation & prediction
    ├── behavioral/         # Behavioral science features
    ├── models/             # Data models
    ├── notifications/      # Notification engine
    ├── ai/                 # AI suggestion engine
    ├── analytics/          # Analytics components
    ├── backup/             # Backup management
    ├── lifecycle/          # Data lifecycle
    ├── social/             # Social features
    ├── monitoring/         # System monitoring
    ├── context/            # Context loading
    ├── data_export/        # Data export
    ├── data_import/        # Data import
    ├── rules/              # Rule engine
    ├── fork/               # Brain forking
    └── assets/             # Brain assets
```

---

## §7 Technology Stack

### Frontend
- **HTML5** - Semantic markup
- **CSS3** - Custom properties, Flexbox, Grid, Animations
- **JavaScript (ES6+)** - Module pattern, LocalStorage
- **Chart.js** - Data visualization

### Backend (Brain System)
- **Python 3.8+** - Core language
- **SQLite** - Database
- **Streamlit** - Admin interface

### Key Principles
- **No framework dependencies** for frontend
- **Mobile-first** responsive design
- **Offline-capable** with LocalStorage
- **Privacy-focused** - all data stays local

---

## §8 Gamification

### ⭐ XP System
| Action | XP Reward |
|--------|-----------|
| Completing a habit | +10 XP |
| Completing a task (low priority) | +5 XP |
| Completing a task (medium priority) | +10 XP |
| Completing a task (high priority) | +20 XP |
| Reaching a goal | +50 XP |
| Maintaining a 7-day streak | +25 XP |

### 🏆 Level Progression
| Level | XP Required |
|-------|-------------|
| Level 1 | 0 XP |
| Level 2 | 100 XP |
| Level 3 | 250 XP |
| Level N | Previous + 150 XP |

### 🎖️ Achievements
Achievements are defined with:
- Unique ID
- Name and description
- Icon/emoji
- XP reward
- Unlock condition

---

## §9 Development

### Coding Standards

**JavaScript:**
- Use `const`/`let`, never `var`
- Arrow functions for callbacks
- Template literals for HTML
- Optional chaining for DOM elements

**CSS:**
- Use CSS custom properties for theming
- BEM-like naming convention
- Support dark mode with `data-theme`

**HTML:**
- Use semantic elements
- Add data attributes for JavaScript hooks
- Include accessibility attributes

### Module Pattern
Each JavaScript module follows this structure:
```javascript
const ModuleName = {
    config: { /* settings */ },
    items: [],
    
    init() { /* initialization */ },
    loadData() { /* fetch data */ },
    saveData() { /* persist data */ },
    render() { /* update UI */ }
};

window.ModuleName = ModuleName;
```

**See [PROJECT_RULES.md](PROJECT_RULES.md) for complete guidelines.**

---

## §10 Testing

### Manual Testing Checklist

**Functionality:**
- [ ] All CRUD operations work correctly
- [ ] Data persists after page refresh
- [ ] Navigation between views works
- [ ] Modals open and close properly
- [ ] Forms validate input correctly

**UI/UX:**
- [ ] Responsive on mobile, tablet, desktop
- [ ] Dark mode displays correctly
- [ ] Animations are smooth
- [ ] No console errors

**Brain System:**
```bash
# Run Brain tests
python -m pytest brain/immune/tests/
```

---

## §11 Configuration

### Theme
Click the 🌙 button in the header to toggle light/dark mode. Theme preference is saved automatically.

### Data Storage
All data is stored locally in your browser's LocalStorage:
- No account required
- Data stays on your device
- Export/import functionality available

### Timer Persistence
The timer state is automatically saved and restored:
- Timer seconds, running state, and category are persisted
- If the timer was running when the page was closed, elapsed time is calculated on restore
- Timer continues counting even if you close and reopen the browser
- Storage key: `veryfyn_timer_state`

### Notification Settings
Configure notification preferences through the settings panel:
- Enable/disable desktop notifications
- Choose notification sound (Default, Chime, Bell)
- Set notification style (Standard or Urgent)
- Toggle habit, task, and goal reminders independently
- Storage key: `veryfyn_notification_settings`

### Environment Variables (Brain System)
```bash
# .env file
DATABASE_PATH=veryfyn.db
SECRET_KEY=<auto-generated>
ENVIRONMENT=development
DEBUG=True
```

---

## §12 Troubleshooting

### App won't start
```bash
# Check dependencies
pip install -r requirements.txt

# Check database exists
ls -la veryfyn.db
```

### Can't login
```bash
# Reset admin user
python force_admin_reset.py
```

### Data not persisting
- Check browser LocalStorage is enabled
- Try exporting and re-importing data
- Check browser console for errors

### Port already in use
```bash
# Kill existing process
pkill -f streamlit
streamlit run run.py --server.port=8502
```

---

## §13 Contributing

1. Read [PROJECT_RULES.md](PROJECT_RULES.md) for coding standards
2. Make your changes
3. Test thoroughly
4. Update relevant documentation
5. Commit with clear message

**Commit Message Format:**
```
feat: add habit streak freeze feature
fix: correct streak calculation for skipped days
docs: update README with new installation steps
```

---

## §14 Cross-References

| If you need... | Read this file |
|----------------|---------------|
| Development guidelines | `PROJECT_RULES.md` |
| Architecture design | `TRACKING_SYSTEM_DESIGN.md` |
| Feature-to-file mapping | `FEATURE_MAP.md` |
| Brain system details | `brain/README.md` |
| Brain design docs | `brain/design/README.md` |
| Tool contracts | `brain/design/04_tool_contracts.md` |
| State machines | `brain/design/01_state_machines.md` |
| Command namespace | `brain/design/00_command_namespace.md` |

---

## License

This project is open source and available under the [MIT License](LICENSE).

---

**Made with ❤️ for personal productivity**

**Auditable. Production-ready.**

---

**Last Updated:** March 2026
