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
| **Read research** | [docs/research/](docs/research/) - [Clone research repos](#research-repositories) |
| **Understand Brain** | [brain/README.md](brain/README.md) |

---

## TABLE OF CONTENTS

| # | Section | Key Info |
|---|---------|----------|
| 1 | Overview | What is Veryfyn? |
| 2 | Quick Start | Get running in seconds |
| 3 | Features | Core functionality |
| 4 | Architecture | System design |
| 5 | Brain System | AI-native architecture |
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

## 🤖 LLM Operational Guide

When working on this project, follow these principles:

- **Assume the user doesn't know how to code** - The LLM must do everything: planning, coding, integration, and explanation
- **Analyze every request holistically** - Consider purpose, context, integration points, and future extensibility
- **Ask clarifying questions** - Build a bigger picture before implementing
- **Provide clear explanations** - Describe what's being changed and why
- **Take full responsibility** - Make all changes, tests, and documentation updates
- **Suggest expansions** - Provide both linear (direct next steps) and non-linear (creative) ideas

**See [PROJECT_RULES.md](PROJECT_RULES.md) for complete LLM guidelines.**

---

## §1 Overview

Veryfyn is a **complete personal tracking system** with an integrated AI Brain architecture. Originally built as a habit tracker, it has evolved into a **comprehensive life management platform** with:

- **Frontend**: Pure HTML/CSS/JavaScript (no framework dependencies)
- **Backend**: Python-based Brain system for AI-native operations
- **Storage**: Browser LocalStorage + SQLite for Brain operations
- **Gamification**: XP, levels, achievements, and celebrations

**The core idea:** Track every aspect of your life with immediate visual feedback, streaks, and rewards - all running locally in your browser with optional AI-enhanced features.

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

**2. Initialize the database:**
```bash
python3 init_db_script.py
python3 force_admin_reset.py
```

**3. Run the system:**
```bash
python3 run_system.py
```

**4. Open http://localhost:8501 in your browser.**

---

### Main Entry Points

| Entry Point | Description |
|-------------|-------------|
| `run_system.py` | Main admin interface |
| `app/pages/` | Streamlit UI pages |
| `brain/tools/` | LLM tools |
| `overlay/pipeline/main_brain.py` | LLM pipeline orchestration |
| `modules_config.json` | Module management |

---

### Navigation Tips

| Area | Location |
|------|----------|
| UI pages | `app/pages/` |
| Business logic | `services/` and `database/queries/` |
| LLM brains and tools | `brain/` and `overlay/pipeline/` |

---

### LLM Integration

The system is designed for safe, modular code editing via LLMs.

- Use the **Brain pipeline** for multi-step code generation and review
- **Audit logs** and **risk-tier gating** ensure safe changes

---

### Useful Links

| Document | Description |
|----------|-------------|
| [README.md](README.md) | Full documentation (this file) |
| [FEATURE_MAP.md](FEATURE_MAP.md) | Feature-to-file mapping |

---

### Troubleshooting

| Issue | Solution |
|-------|----------|
| Errors | Enable debug mode (see README.md) |
| Change history | Check audit logs |

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
- Overview of all tracking metrics
- Quick access to habits and tasks
- Weekly progress charts
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

The Brain is the central nervous system for AI-native operations. Every command flows through the Brain:

1. **Router** validates and routes commands
2. **Policies** check preconditions (security, integrity)
3. **State Machines** validate transitions
4. **Tools** execute operations
5. **Audit Log** records everything

### 🧠 Brain Context Protocol

**IMPORTANT:** This project follows the Brain Context Protocol for AI interaction.

**The Three Laws:**
1. **README.md files are the source of truth** - Always load context from READMEs
2. **The brain folder is the thinking process** - All operations flow through brain architecture
3. **Simple prompts yield deep understanding** - AI interprets deeply, not literally

**See [BRAIN_CONTEXT_PROTOCOL.md](BRAIN_CONTEXT_PROTOCOL.md) for the full protocol.**

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

**See [brain/README.md](brain/README.md) for detailed Brain documentation.**

---

## §6 Project Structure

```
tracking-system/
├── index.html              # Main HTML entry point
├── README.md               # This file
├── PROJECT_RULES.md        # Development guidelines
├── TRACKING_SYSTEM_DESIGN.md  # Architecture design
├── TODO.md                 # Project tracking
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
│   └── dataExport.js       # Import/export functionality
│
├── assets/
│   ├── icons/              # Icon assets
│   └── sounds/             # Sound effects
│
└── brain/                  # AI Brain System
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
    ├── fork/               # Fork engine
    └── design/             # Design documentation
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
streamlit run run_system.py --server.port=8502
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
| **AI interaction rules** | `BRAIN_CONTEXT_PROTOCOL.md` |
| Brain context module | `brain/context/README.md` |
| Development guidelines | `PROJECT_RULES.md` |
| Architecture design | `TRACKING_SYSTEM_DESIGN.md` |
| Feature-to-file mapping | `FEATURE_MAP.md` |
| Brain system details | `brain/README.md` |
| Brain design docs | `brain/design/README.md` |
| Tool contracts | `brain/design/04_tool_contracts.md` |
| State machines | `brain/design/01_state_machines.md` |
| Command namespace | `brain/design/00_command_namespace.md` |

---

## Research Repositories

The `docs/research/` directory contains research documents with references to open-source repositories. To clone these reference repositories for deeper analysis:

### Phase 2.1: Correlation Engine Research

```bash
# Granger causality and VAR models
git clone https://github.com/roqua/autovar.git

# Automatic insights and NLG
git clone https://github.com/p0lloc/perfice.git

# Correlation matrix dashboard
git clone https://github.com/markrai/fitbaus.git

# Time-lagged cross-correlation
git clone https://github.com/farhanaugustine/Temporal_Behavior_Analysis.git

# ML for lag detection
git clone https://github.com/gianlucatruda/quantified-sleep.git

# Data unification infrastructure
git clone https://github.com/karlicoss/HPI.git
```

### Phase 5.3: Backup & Restore Research

```bash
# Hard link deduplication
git clone https://github.com/jedie/PyHardLinkBackup.git

# Retention management
git clone https://github.com/charles-001/backup-warden.git

# JSON manifest patterns
git clone https://github.com/mlgzackfly/CTFd-Backup-Tool.git

# Checksum comparison
git clone https://github.com/soerenkoehler/checksum-diff.git

# Job scheduling
git clone https://github.com/agronholm/apscheduler.git

# Filesystem mocking for tests
git clone https://github.com/pytest-dev/pyfakefs.git
```

### Habit Tracking Research

```bash
# Habit Score algorithm
git clone https://github.com/iSoron/uhabits.git

# RPG gamification
git clone https://github.com/HabitRPG/habitica.git

# Event sourcing
git clone https://github.com/ActivityWatch/activitywatch.git

# AI-native logging
git clone https://github.com/mr-karan/gullak.git

# Flexible tracking
git clone https://github.com/open-nomie/nomie6-oss.git

# N-of-1 trials
git clone https://github.com/hpi-studyu/studyu.git
```

See [docs/research/](docs/research/) for detailed research documents.

---

## License

This project is open source and available under the [MIT License](LICENSE).

---

**Made with ❤️ for personal productivity**

**LLM-native. Auditable. Production-ready.**
