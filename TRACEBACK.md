# TRACEBACK.md - AI Context & Code Documentation

> **🎯 PURPOSE:** This file provides a comprehensive overview of the entire codebase. AI assistants MUST read this file before making any changes to understand what each file does, how files relate to each other, data flow, and critical patterns to follow.

---

## 🔄 CHANGE LOG (Traceback Records)

**Every change made to the codebase MUST be documented here:**

| Date | File(s) Changed | Change Description | Reason | AI Session |
|------|-----------------|-------------------|--------|------------|
| 2026-02-26 | TRACEBACK.md | Initial creation | Establish code documentation for AI context | Session 1 |
| 2026-02-26 | TRACEBACK.md | Complete rewrite with full codebase analysis | Comprehensive documentation of all modules | Session 1 |

---

## 📁 PROJECT ARCHITECTURE OVERVIEW

```
tracking-system/
├── tracking_app/          # 🐍 PRIMARY: Python Streamlit Application
│   ├── app.py             # Main entry point
│   ├── database.py        # SQLite database connection & schema
│   ├── models.py          # Data models (dataclasses)
│   ├── storage.py         # CRUD operations layer
│   ├── migration.py       # Data migration utilities
│   ├── components/        # Shared UI components
│   │   ├── sidebar.py     # Navigation sidebar
│   │   ├── session.py     # Session state management
│   │   ├── charts.py      # Chart components
│   │   └── metrics.py     # Metric card components
│   └── pages/             # Streamlit pages (18 pages)
├── brain/                 # 🧠 Backend intelligence modules
│   ├── core/              # Core brain architecture
│   ├── models/            # Scientific habit models
│   ├── analysis/          # Burnout & prediction
│   ├── tools/             # 100+ operation tools
│   ├── policies/          # Security & integrity rules
│   ├── state/             # State machines
│   ├── audit/             # Logging & compliance
│   ├── security/          # Encryption & auth
│   ├── immune/            # Self-healing system
│   └── notifications/     # Smart notifications
├── services/              # Service modules
│   ├── ai_provider.py     # AI integration (stub)
│   ├── notifications.py   # Desktop notifications
│   ├── email.py           # Email service
│   ├── debug_console.py   # Debug utilities
│   └── github_cortex_client.py  # GitHub integration
├── js/                    # ⚠️ LEGACY: JavaScript (migrating to Python)
├── css/                   # ⚠️ LEGACY: Styles (migrating to Streamlit)
├── index.html             # ⚠️ LEGACY: HTML entry point
├── db.py                  # Alternative database module
├── run.py                 # Application launcher script
└── tracking.db            # SQLite database file
```

**Technology Stack:**
- **Frontend:** Streamlit (Python) - replacing legacy HTML/JS
- **Database:** SQLite (tracking.db)
- **Models:** Python dataclasses
- **Primary Language:** Python 3.x
- **Scientific Algorithms:** Based on Loop Habit Tracker research

---

## 🐍 PYTHON APPLICATION (tracking_app/)

### Core Files

#### `tracking_app/app.py` - Main Entry Point

**Purpose:** Main Streamlit application entry point. Initializes the app and redirects to dashboard.

**Key Functions:**
| Function | Description |
|----------|-------------|
| `main()` | Application entry point - initializes session, renders sidebar, redirects to dashboard |

**Dependencies:**
- `streamlit` - UI framework
- `tracking_app/components/sidebar.py` - Sidebar rendering
- `tracking_app/components/session.py` - Session initialization

**Data Flow:**
```
User runs app.py → Init session state → Render sidebar → Redirect to dashboard
```

---

#### `tracking_app/database.py` - Database Connection & Schema

**Purpose:** Handles SQLite database connections, schema creation, and provides database utility functions.

**Key Classes:**
| Class | Description |
|-------|-------------|
| `Database` | Main database manager with thread-safe connections |

**Database Methods:**
| Method | Description |
|--------|-------------|
| `get_connection()` | Get SQLite connection for current thread |
| `transaction()` | Context manager for transactions (auto-commit/rollback) |
| `execute()` | Execute a SQL query |
| `fetch_one()` / `fetch_all()` | Query helpers returning dict-like rows |

**Global Functions:**
| Function | Description |
|----------|-------------|
| `get_db()` | Get global database instance (singleton) |
| `init_db()` | Initialize database with required tables |
| `generate_id()` | Generate UUID for entities |

**Database Tables:**
| Table | Purpose |
|-------|--------|
| `habits` | Habit definitions |
| `habit_entries` | Habit completion records |
| `streak_freezes` | Streak freeze tracking |
| `user_inventory` | User data (XP, level, settings) |
| `tasks` | Task/todo items |
| `transactions` | Financial transactions |
| `health_entries` | Health tracking data |
| `goals` | Goal tracking |
| `achievements` | Achievement/badge records |
| `events` | Event sourcing |
| `habit_stacks` | Phase 3.1 habit stacking |
| `stack_items` | Stack item relationships |
| `stack_completions` | Stack completion tracking |
| `srbai_results` | Habit automaticity surveys |
| `implementation_intentions` | Phase 3.2 if-then planning |
| `intention_triggers` | Intention trigger logs |
| `rewards` | Phase 3.3 rewards |
| `user_reward_history` | Reward history |
| `user_reward_stats` | Reward statistics |
| `notifications` | Phase 4 notifications |
| `push_subscriptions` | Web Push subscriptions |
| `notification_logs` | Delivery tracking |
| `reminder_schedules` | Reminder configurations |
| `completion_history` | Smart scheduling data |
| `notification_preferences` | User preferences |
| `vapid_config` | Web Push authentication |

**Important Notes:**
- Thread-safe via thread-local connections
- Foreign keys enabled by default
- Row factory returns dict-like objects
- Schema version tracking included

---

#### `tracking_app/models.py` - Data Models

**Purpose:** Defines all data models as Python dataclasses. Central source of truth for data structure.

**Enums:**
| Enum | Values |
|------|--------|
| `FrequencyType` | DAILY, WEEKLY, CUSTOM |
| `HabitType` | BOOLEAN, NUMERICAL |
| `Priority` | LOW, MEDIUM, HIGH |
| `TransactionType` | INCOME, EXPENSE |
| `Mood` | GREAT, GOOD, OKAY, BAD |

**Data Models:**
| Model | Purpose | Key Fields |
|-------|---------|------------|
| `Habit` | Habit definition | id, name, frequency, icon, color, target_value |
| `HabitEntry` | Habit completion record | id, habit_id, entry_date, value, skipped |
| `Task` | Todo item | id, title, due_date, priority, completed |
| `Transaction` | Financial record | id, description, amount, type, category |
| `HealthEntry` | Health tracking | id, entry_date, weight, sleep_hours, mood |
| `Goal` | Goal tracking | id, title, target, current, progress_percentage |
| `Achievement` | Badge/achievement | id, name, icon, xp_reward, unlocked_at |

**Each Model Has:**
- `__post_init__()` - Set defaults (UUID, timestamps)
- `to_dict()` - Serialize to dictionary
- `from_dict()` - Deserialize from dictionary

---

#### `tracking_app/storage.py` - Storage/CRUD Layer

**Purpose:** Central data persistence layer. ALL data operations go through this class.

**Key Class:** `Storage`

**Habits Methods:**
| Method | Description |
|--------|-------------|
| `get_habits(include_archived)` | Get all habits |
| `get_habit(habit_id)` | Get single habit |
| `create_habit(name, ...)` | Create new habit |
| `update_habit(habit_id, **updates)` | Update habit |
| `delete_habit(habit_id)` | Delete habit |
| `archive_habit(habit_id)` / `unarchive_habit(habit_id)` | Soft delete |

**Habit Entries Methods:**
| Method | Description |
|--------|-------------|
| `get_habit_entries(habit_id, start_date, end_date)` | Get entries |
| `get_habit_entry(habit_id, entry_date)` | Get specific entry |
| `mark_habit_complete(habit_id, entry_date, value)` | Mark complete |
| `unmark_habit_complete(habit_id, entry_date)` | Remove completion |
| `skip_habit(habit_id, entry_date, reason)` | Mark as skipped |

**Tasks Methods:**
| Method | Description |
|--------|-------------|
| `get_tasks(include_completed)` | Get all tasks |
| `get_task(task_id)` | Get single task |
| `create_task(title, ...)` | Create task |
| `update_task(task_id, **updates)` | Update task |
| `complete_task(task_id)` | Mark complete |
| `delete_task(task_id)` | Delete task |

**Transactions Methods:**
| Method | Description |
|--------|-------------|
| `get_transactions(start_date, end_date)` | Get transactions |
| `create_transaction(description, amount, type, ...)` | Create transaction |
| `delete_transaction(transaction_id)` | Delete transaction |

**Health Entries Methods:**
| Method | Description |
|--------|-------------|
| `get_health_entries(start_date, end_date)` | Get entries |
| `get_health_entry(entry_date)` | Get specific entry |
| `create_health_entry(entry_date, weight, sleep_hours, ...)` | Create/update entry |

**Goals Methods:**
| Method | Description |
|--------|-------------|
| `get_goals(include_completed)` | Get goals |
| `get_goal(goal_id)` | Get single goal |
| `create_goal(title, target, ...)` | Create goal |
| `update_goal_progress(goal_id, current)` | Update progress |
| `delete_goal(goal_id)` | Delete goal |

**User Data Methods:**
| Method | Description |
|--------|-------------|
| `get_user_data(key, default)` | Get user setting |
| `set_user_data(key, value)` | Set user setting |
| `get_xp()` / `add_xp(amount)` | XP management |
| `get_level()` | Get current level |
| `get_streak_freezes()` / `use_streak_freeze()` / `add_streak_freeze(count)` | Streak freeze management |

**Achievements Methods:**
| Method | Description |
|--------|-------------|
| `get_achievements(unlocked_only)` | Get achievements |
| `unlock_achievement(achievement_id)` | Unlock achievement |

**Important Notes:**
- Singleton pattern via `get_storage()`
- All data MUST go through this class (PROJECT_RULES.md)
- Uses context managers for transactions

---

### Components (tracking_app/components/)

#### `tracking_app/components/session.py` - Session State Management

**Purpose:** Manages Streamlit session state initialization and user session data.

**Key Functions:**
| Function | Description |
|----------|-------------|
| `init_session_state()` | Initialize all session variables |
| `get_storage()` | Get storage instance from session |
| `get_level_from_xp(xp)` | Calculate level from XP |
| `get_xp_for_level(level)` | Get XP required for level |
| `add_xp(amount)` | Add XP and handle level-ups |
| `refresh_user_stats()` | Refresh stats from storage |

**Session State Variables:**
| Variable | Description |
|----------|-------------|
| `user_level` | Current user level |
| `user_xp` | Current XP total |
| `theme` | UI theme preference |
| `streak_freezes` | Available streak freezes |
| `storage` | Storage instance |

**XP/Level Formula:**
```
Level 1: 0 XP
Level 2: 100 XP
Level 3: 250 XP
Level N: 100 + (N - 2) * 150 XP
```

---

#### `tracking_app/components/sidebar.py` - Navigation Sidebar

**Purpose:** Renders consistent sidebar navigation across all pages.

**Key Function:**
| Function | Description |
|----------|-------------|
| `render_sidebar()` | Render complete sidebar with stats, navigation, theme toggle |

**Navigation Sections:**
- 📊 Tracking: Dashboard, Habits, Tasks, Finances, Health, Emotional Health, Time, Goals, Achievements
- 📦 Data: Export, Import, Backup, Lifecycle
- 🔔 Alerts: Notifications, Habit Reminders, Task Alerts, Goal Alerts

---

#### `tracking_app/components/charts.py` - Chart Components

**Purpose:** Provides chart components for data visualization.

**Key Functions:**
| Function | Description |
|----------|-------------|
| `render_weekly_chart(data)` | Render weekly progress bar chart |
| `render_score_trend_chart(scores)` | Render score trend line chart |
| `render_habit_completion_heatmap(data)` | Render habit completion heatmap |
| `render_category_breakdown(categories)` | Render pie chart for categories |
| `render_progress_over_time(data)` | Render multi-line progress chart |

---

#### `tracking_app/components/metrics.py` - Metric Card Components

**Purpose:** Provides reusable metric card components.

**Key Functions:**
| Function | Description |
|----------|-------------|
| `render_metric_card(label, value, delta, icon)` | Basic metric display |
| `render_habit_score_card(score_value, habit_name, trend)` | Habit score with category |
| `render_progress_card(title, current, target, unit, icon)` | Progress with bar |
| `render_streak_card(streak_count, streak_freezes, best_streak)` | Streak display |
| `render_burnout_risk_card(risk_score, risk_level, factors)` | Burnout indicator |

**Score Categories:**
| Score Range | Category | Color | Emoji |
|-------------|----------|-------|-------|
| 85-100% | Excellent | #4CAF50 | 🌟 |
| 70-84% | Strong | #8BC34A | 💪 |
| 50-69% | Developing | #FFC107 | 🌱 |
| 30-49% | Building | #FF9800 | 🔧 |
| 0-29% | Starting | #F44336 | 🆕 |

---

### Pages (tracking_app/pages/)

#### Streamlit Page Pattern

```python
# Page Pattern:
1. Page configuration (st.set_page_config)
2. Import shared components
3. Helper functions
4. Render functions
5. main() function
```

---

#### `tracking_app/pages/dashboard.py` - Main Dashboard

**Purpose:** Main overview page showing all tracking metrics.

**Key Functions:**
| Function | Description |
|----------|-------------|
| `get_todays_habits(storage)` | Get habits with completion status |
| `get_active_tasks(storage)` | Get tasks with counts |
| `get_goals_progress(storage)` | Get goals with progress |
| `get_weekly_habit_data(storage, days)` | Get weekly chart data |
| `calculate_habit_scores(storage)` | Calculate scores using brain models |
| `calculate_streak(storage, habits)` | Calculate overall streak |
| `get_burnout_risk(storage)` | Calculate burnout risk |
| `get_recent_activity(storage)` | Get activity feed |

**Render Functions:**
| Function | Description |
|----------|-------------|
| `render_welcome()` | Welcome message with level/XP |
| `render_quick_stats()` | Stats row (habits, tasks, goals, streak) |
| `render_habit_scores_section()` | Habit scores using brain models |
| `render_quick_actions()` | Quick action buttons |
| `render_todays_habits()` | Today's habits with toggles |
| `render_active_tasks()` | Active tasks with completion |
| `render_goals_progress()` | Goals progress bars |
| `render_burnout_indicator()` | Burnout risk display |
| `render_activity_feed()` | Recent activity feed |
| `render_motivational_quote()` | Random motivational quote |

---

#### Other Pages (Brief Descriptions)

| Page | Purpose |
|------|---------|
| `habits.py` | Habit management and tracking |
| `tasks.py` | Task/todo management |
| `finances.py` | Financial tracking |
| `health.py` | Health metrics tracking |
| `emotional_health.py` | RGB mood model tracking |
| `time.py` | Time tracking |
| `goals.py` | Goal management |
| `achievements.py` | Achievements/gamification display |
| `data_export.py` | Export data to JSON/CSV |
| `data_import.py` | Import data from files |
| `backup_restore.py` | Database backup/restore |
| `data_lifecycle.py` | Data retention management |
| `notification_settings.py` | Notification preferences |
| `habit_reminders.py` | Habit reminder configuration |
| `task_alerts.py` | Task deadline alerts |
| `goal_alerts.py` | Goal deadline alerts |

---

## 🧠 BRAIN MODULE (brain/)

The Brain is the **central nervous system** of the Veryfyn Tracking System.

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────────┐
│                          BRAIN                                   │
│                    (brain/core/brain.py)                        │
│                                                                 │
│  ┌──────────┐   ┌──────────┐   ┌──────────┐   ┌──────────┐    │
│  │  Router  │──▶│ Policies │──▶│  State   │──▶│  Tools   │    │
│  │          │   │          │   │ Machine  │   │          │    │
│  └──────────┘   └──────────┘   └──────────┘   └──────────┘    │
│       │              │              │              │           │
│       ▼              ▼              ▼              ▼           │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │              Audit Log (append-only)                      │ │
│  └───────────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────────┘
```

### Core (`brain/core/`)

| File | Purpose |
|------|---------|
| `brain.py` | Main entry point, orchestrates all operations |
| `router.py` | Routes commands to execution plans |
| `result.py` | Result types (BrainResult, ToolOutput) |
| `tool.py` | Base Tool class and contracts |
| `enums.py` | Risk tiers, status codes |
| `guardrails.py` | Safety middleware |
| `cerebellum.py` | Coordination and timing |
| `command_event.py` | Command event structure |

### Models (`brain/models/`)

#### `brain/models/habit.py` - Scientific Habit Scoring

**Purpose:** Core habit entity with scientific scoring based on Loop Habit Tracker's algorithm.

**Key Classes:**
| Class | Description |
|-------|-------------|
| `HabitScore` | Score with trend tracking (0.0-1.0) |
| `ScoreList` | List of scores over time |
| `Habit` | Full habit entity with scoring |

**Scoring Algorithm:**
```
Based on exponential smoothing with Holt's Linear Trend:

1. Multiplier: 0.5^(√frequency / 13)
2. Level: α * checkmark + (1-α) * (prev_level + prev_trend)
3. Trend: β * (level - prev_level) + (1-β) * prev_trend

Alpha (α) = 0.052 for 66-day mastery calibration
Beta (β) = 0.01 for trend smoothing
```

**After 66 consecutive days, score reaches ~97%**

---

#### `brain/models/frequency.py` - Frequency Definitions

**Purpose:** Defines habit frequency types and calculations.

---

#### `brain/models/entry.py` - Entry Tracking

**Purpose:** Habit entry/completion tracking.

---

#### `brain/models/streak.py` - Streak Calculation

**Purpose:** Streak calculation and management.

---

#### `brain/models/emotional_state.py` - RGB Emotion Model

**Purpose:** RGB-based emotional state representation.

---

### Analysis (`brain/analysis/`)

#### `brain/analysis/burnout.py` - Burnout Prediction

**Purpose:** Predicts and helps prevent user burnout by monitoring behavioral indicators.

**Key Classes:**
| Class | Description |
|-------|-------------|
| `BurnoutIndicators` | Input indicators for burnout prediction |
| `BurnoutRisk` | Risk assessment result |
| `BurnoutPredictor` | Main prediction engine |
| `BurnoutMonitor` | Continuous monitoring system |

**Burnout Indicators:**
| Indicator | Description |
|-----------|-------------|
| `completion_rate_trend` | -1 to 1 (declining to improving) |
| `sleep_deviation` | Hours below/above baseline |
| `stress_level` | 1-10 scale |
| `days_since_checkin` | Days without app interaction |
| `streak_breaks` | Number of recent streak breaks |
| `mood_trend` | -1 to 1 (declining to improving) |
| `task_overload` | Tasks due / capacity ratio |
| `habit_load` | Number of active habits |
| `missed_days` | Consecutive missed days |

**Risk Levels:**
| Level | Score Range |
|-------|-------------|
| Critical | 75-100% |
| High | 50-74% |
| Moderate | 25-49% |
| Low | 0-24% |

---

#### `brain/analysis/correlation.py` - Correlation Analysis

**Purpose:** Analyzes correlations between tracking metrics.

---

#### `brain/analysis/prediction.py` - Predictive Analytics

**Purpose:** Machine learning predictions for user behavior.

---

### Tools (`brain/tools/`)

100+ tools organized by domain.

---

### Policies (`brain/policies/`)

| File | Purpose |
|------|---------|
| `engine.py` | Policy orchestration |
| `security.py` | Authentication, authorization |
| `integrity.py` | Data integrity rules |
| `scheduling.py` | Scheduling constraints |
| `communications.py` | Communication limits |

---

### State Machines (`brain/state/`)

| File | Entity |
|------|--------|
| `job_machine.py` | Job lifecycle |
| `invoice_machine.py` | Invoice lifecycle |
| `payment_machine.py` | Payment lifecycle |
| `quote_machine.py` | Quote lifecycle |
| `manager.py` | State machine coordination |

---

### Audit (`brain/audit/`)

| File | Purpose |
|------|---------|
| `logger.py` | Audit logging |
| `schema.py` | Audit schema definition |
| `event_store.py` | Event sourcing |
| `event_replay.py` | Event replay for debugging |

---

### Security (`brain/security/`)

| File | Purpose |
|------|---------|
| `crypto_engine.py` | Encryption |
| `neural_link.py` | Secure command channel |
| `export_guard.py` | Data export protection |
| `ai_policy_enforcer.py` | AI operation policies |

---

### Immune System (`brain/immune/`)

| File | Purpose |
|------|---------|
| `fingerprinter.py` | Code fingerprinting |
| `homeostasis.py` | System balance |
| `quarantine.py` | Problem isolation |
| `memory_monitor.py` | Memory management |
| `worker.py` | Background processing |

---

### Notifications (`brain/notifications/`)

| File | Purpose |
|------|---------|
| `engine.py` | Notification orchestration |
| `channels.py` | Delivery channels |
| `scheduler.py` | Smart scheduling |
| `templates.py` | Message templates |
| `preferences.py` | User preferences |
| `habit_reminders.py` | Habit-specific reminders |
| `task_alerts.py` | Task-specific alerts |
| `goal_alerts.py` | Goal-specific alerts |

---

### Specialized Brains (`brain/brains/`)

| File | Purpose |
|------|---------|
| `ops_brain.py` | Operations |
| `finance_brain.py` | Financial operations |
| `relation_brain.py` | Relationships |
| `diagnosis_brain.py` | Diagnostics |
| `repair_brain.py` | Self-repair |
| `scanner_brain.py` | Code scanning |
| `test_brain.py` | Testing |
| `validator_brain.py` | Validation |
| `meta_brain.py` | Meta-operations |
| `docs_brain.py` | Documentation |

---

## 📦 SERVICES (services/)

#### `services/ai_provider.py` - AI Provider Service

**Purpose:** AI integration service for predictions and insights (stub implementation).

**Key Class:**
| Class | Description |
|-------|-------------|
| `AIProvider` | AI provider with complete/chat methods |

**Note:** This is a stub. Configure with a real provider for actual AI responses.

---

#### `services/notifications.py` - Notification Service

**Purpose:** Core notification handling for desktop and in-app notifications.

**Key Classes:**
| Class | Description |
|-------|-------------|
| `NotificationType` | Enum: INFO, SUCCESS, WARNING, ERROR, HABIT_REMINDER, TASK_REMINDER, GOAL_REMINDER |
| `Notification` | Dataclass: title, message, type, sound, urgent |
| `Notifications` | Main service class |

**Key Methods:**
| Method | Description |
|--------|-------------|
| `send(notification)` | Send a notification |
| `show_toast(title, message, type)` | Show in-app toast |
| `send_habit_reminder(habit_name)` | Send habit reminder |
| `send_task_reminder(task_title, due_date)` | Send task reminder |
| `send_goal_reminder(goal_title, progress)` | Send goal reminder |
| `register_handler(type, handler)` | Register custom handler |
| `update_settings(settings)` | Update notification settings |

---

#### `services/email.py` - Email Service

**Purpose:** Email notification service.

---

#### `services/debug_console.py` - Debug Console

**Purpose:** Debug and logging utilities.

---

#### `services/github_cortex_client.py` - GitHub Integration

**Purpose:** GitHub API integration.

---

## 🔧 ROOT FILES

#### `run.py` - Application Launcher

**Purpose:** Simple script to launch the Streamlit application.

```python
subprocess.run([sys.executable, "-m", "streamlit", "run", app_path])
```

**Usage:** `python run.py`

---

#### `db.py` - Alternative Database Module

**Purpose:** Alternative database connection module (legacy compatibility).

**Key Functions:**
| Function | Description |
|----------|-------------|
| `get_sqlite_conn(db_path)` | Get connection |
| `get_db_connection(db_path)` | Context manager |
| `init_db(db_path)` | Initialize basic tables |

**Note:** Main application uses `tracking_app/database.py`. This is for legacy compatibility.

---

## ⚠️ LEGACY FILES (JavaScript/HTML/CSS)

These files are being migrated to Python/Streamlit. **No new development should occur here.**

### `js/` - JavaScript Modules

| File | Purpose | Python Replacement |
|------|---------|-------------------|
| `app.js` | Main JS controller | `tracking_app/app.py` |
| `storage.js` | LocalStorage operations | `tracking_app/storage.py` |
| `habits.js` | Habits module | `tracking_app/pages/habits.py` |
| `tasks.js` | Tasks module | `tracking_app/pages/tasks.py` |
| `finances.js` | Finances module | `tracking_app/pages/finances.py` |
| `health.js` | Health module | `tracking_app/pages/health.py` |
| `time.js` | Time tracking | `tracking_app/pages/time.py` |
| `goals.js` | Goals module | `tracking_app/pages/goals.py` |
| `achievements.js` | Achievements | `tracking_app/pages/achievements.py` |
| `charts.js` | Chart visualization | `tracking_app/components/charts.py` |
| `habit-stacking.js` | Habit stacking | `brain/behavioral/habit_stacking.py` |
| `implementation-intentions.js` | If-then planning | `brain/behavioral/implementation_intentions.py` |
| `rewards.js` | Rewards system | `brain/behavioral/rewards.py` |
| `notifications.js` | Notifications | `services/notifications.py` |

### `css/styles.css` - Legacy Styles

Streamlit handles styling natively. This file is for legacy HTML only.

### `index.html` - Legacy Entry Point

Legacy HTML entry point. Streamlit generates HTML automatically.

---

## 🗄️ DATABASE SCHEMA QUICK REFERENCE

### Core Tables

```sql
-- Habits
habits (id, name, description, frequency, habit_type, color, icon, 
        target_value, target_type, archived, created_at, updated_at)

-- Habit Entries
habit_entries (id, habit_id, entry_date, value, notes, skipped, created_at)

-- Tasks
tasks (id, title, description, due_date, priority, category, 
       completed, completed_at, created_at, updated_at)

-- Transactions
transactions (id, description, amount, type, category, trans_date, created_at)

-- Health
health_entries (id, entry_date, weight, sleep_hours, mood, notes, created_at)

-- Goals
goals (id, title, description, target, current, unit, deadline, 
       completed, created_at, updated_at)

-- User Data
user_inventory (key, value, updated_at)

-- Achievements
achievements (id, name, description, icon, xp_reward, unlocked_at, created_at)

-- Events (Event Sourcing)
events (id, event_type, entity_type, entity_id, timestamp, version, payload, metadata)

-- Notifications (Phase 4)
notifications (id, type, title, message, priority, status, scheduled_for, 
              sent_at, delivered_at, read, entity_type, entity_id, action_url, 
              metadata, created_at, updated_at)

-- Notification Preferences
notification_preferences (user_id, enabled, quiet_hours_start, quiet_hours_end,
                         habit_reminders_enabled, task_reminders_enabled, 
                         goal_reminders_enabled, smart_scheduling_enabled, ...)

-- Reminder Schedules
reminder_schedules (id, user_id, entity_type, entity_id, reminder_time,
                    days_of_week, enabled, is_smart, smart_time, channels, ...)
```

---

## 🔗 KEY DEPENDENCIES & DATA FLOW

### Application Flow

```
run.py
  └── streamlit run tracking_app/app.py
        ├── init_session_state() [components/session.py]
        ├── render_sidebar() [components/sidebar.py]
        └── st.switch_page("pages/dashboard.py")
              └── get_storage() [storage.py]
                    └── get_db() [database.py]
                          └── SQLite (tracking.db)
```

### Import Dependencies

```
app.py
  ├── components/sidebar.py
  └── components/session.py
        └── storage.py
              ├── database.py
              └── models.py

All pages:
  ├── components/sidebar.py
  ├── components/session.py
  ├── storage.py
  └── models.py

Dashboard page:
  ├── brain/models/habit.py (optional, with fallback)
  └── brain/analysis/burnout.py (optional, with fallback)
```

---

## 📝 QUICK REFERENCE FOR AI

### Before Making ANY Changes

1. **Read this file (TRACEBACK.md)** - Understand context
2. **Read PROJECT_RULES.md** - Follow conventions
3. **Check related files** - Understand dependencies
4. **Update TRACEBACK.md** - Document changes

### Python Conventions

- **Use snake_case** for functions/variables
- **Use type hints** on all functions
- **Use dataclasses** for models
- **Use f-strings** for formatting
- **Use context managers** for resources
- **Follow PEP 8**

### Streamlit Patterns

- **Use st.session_state** for state persistence
- **Use st.columns** for layout
- **Use st.form** for data entry
- **Call st.rerun()** after state changes

### Data Operations

- **ALWAYS use Storage class** - Never direct DB access
- **Get storage via get_storage()** - Singleton pattern
- **Return model instances** - Not raw dictionaries

### Creating New Pages

1. Create file in `tracking_app/pages/`
2. Follow Streamlit Page Pattern
3. Import shared components
4. Add to sidebar navigation in `components/sidebar.py`
5. Document in this file

### Adding New Models

1. Create dataclass in `models.py`
2. Add to_dict() and from_dict() methods
3. Add to __all__ exports
4. Create table in `database.py`
5. Add CRUD methods in `storage.py`
6. Document in this file

---

## 🎯 COMMON TASKS - WHAT TO MODIFY

| Task | Files to Modify |
|------|-----------------|
| Add new habit feature | `models.py`, `database.py`, `storage.py`, `pages/habits.py` |
| Add new page | Create `pages/new_page.py`, update `components/sidebar.py` |
| Add new data model | `models.py`, `database.py`, `storage.py` |
| Change sidebar | `components/sidebar.py` |
| Add notification type | `services/notifications.py`, `database.py`, `pages/notification_settings.py` |
| Fix database issue | `database.py`, possibly `storage.py` |
| Add achievement | `models.py`, `database.py`, `storage.py`, `pages/achievements.py` |
| Change XP calculation | `components/session.py`, `storage.py` |
| Add burnout indicator | `brain/analysis/burnout.py`, `pages/dashboard.py` |
| Modify habit scoring | `brain/models/habit.py` |

---

## 📚 RELATED DOCUMENTATION

| Want to... | Go to... |
|------------|----------|
| **Get started** | [GETTING_STARTED.md](GETTING_STARTED.md) |
| **Understand rules** | [PROJECT_RULES.md](PROJECT_RULES.md) |
| **Find a feature** | [FEATURE_MAP.md](FEATURE_MAP.md) |
| **See roadmap** | [ROADMAP.md](ROADMAP.md) |
| **Check tasks** | [TODO.md](TODO.md) |
| **Understand brain** | [brain/README.md](brain/README.md) |

---

## 🚨 CRITICAL RULES

1. **NO direct database access** - All operations through Storage class
2. **NO auto-editing scripts** - Scripts detect only, never modify
3. **NO placeholders** - Complete implementations only
4. **ALWAYS log to audit** - Every command recorded (when using Brain)
5. **ALWAYS validate transitions** - State machines enforced
6. **ALWAYS update this file** - When making changes

---

*Last updated: 2026-02-26*
*Version: 2.0.0 - Complete codebase documentation*