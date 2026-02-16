# 📋 Personal Tracking System - Project Rules & Guidelines

## 🎯 Overview
This document outlines the rules, conventions, and best practices for developing the Personal Tracking System. All contributors and AI assistants must follow these guidelines to ensure consistency and quality.

### 🐍 PRIMARY LANGUAGE: Python

**Python is the primary language for this project.** All new development must be in Python.

- **Current State:** The project has a legacy JavaScript/HTML/CSS frontend that is being gradually migrated to Python
- **Target State:** Pure Python application using Streamlit for UI
- **Migration Strategy:** Gradual, chunked migration (see Migration Section below)

**Rule:** Any new feature or module MUST be implemented in Python first. JavaScript is only for maintaining existing functionality during the transition period.

---

## 🤖 LLM Operational Guide

### Non-Linear, Holistic LLM Reasoning Principles

When working on this project, the LLM must:

- **Assume the human user does not know how to code.** The LLM must do everything: planning, coding, integration, and explanation.
- **Analyze every user question:**
  - What is the user trying to achieve?
  - How does this request fit into the current program?
  - What is the purpose, and what else could it be used for?
  - What previous code, modules, or features does it need to tie into?
  - What future extensibility or alternate uses should be considered?
- **Always ask clarifying questions to build a bigger picture:**
  - What is the broader goal?
  - Are there related features or workflows?
  - Is there missing context or requirements?
- **Provide clear explanations and guidance for non-coders:**
  - Describe what is being changed and why.
  - Offer step-by-step instructions and summaries.
  - Document integration points and dependencies.
- **Take full responsibility for implementation:**
  - Make all code changes, updates, and tests.
  - Ensure robust, maintainable, and extensible solutions.
  - Update documentation and feature maps as needed.
- **For every user idea or request, always provide:**
  - **Linear expansion ideas:** Direct next steps, incremental improvements, and logical feature additions.
  - **Non-linear expansion ideas:** Creative, alternative, or cross-domain uses, integrations, and new directions.

---

## 🧭 Navigation & Context Gathering

### Required Reading Order
1. **Start with `README.md`** - Project overview and entry points
2. **Read `GETTING_STARTED.md`** - Setup instructions and workflow
3. **Use `FEATURE_MAP.md`** - Locate features and their corresponding files
4. **Open referenced documentation** - Part of standard workflow

### Key Documentation Files
| File | Purpose |
|------|---------|
| `README.md` | Project overview, quick start |
| `GETTING_STARTED.md` | Setup instructions, workflow guide |
| `FEATURE_MAP.md` | Feature locations and file mappings |
| `PROJECT_RULES.md` | This file - rules and conventions |
| `ROADMAP.md` | Development phases and timeline |
| `TODO.md` | Current tasks and priorities |

---

## 📐 Implementation Strategy

### Step-by-Step Workflow
1. Follow the setup instructions in `GETTING_STARTED.md`
2. For any referenced file or feature, open and review the relevant `.md` or code file
3. Use chunked docs and quick references for large files

### For New Features
1. Consult the roadmap in `GETTING_STARTED.md`
2. Check `FEATURE_MAP.md` for related existing features
3. Follow architecture rules in this document
4. For AI-native features, see `docs/research/AI_AND_PREDICTION.md`

### Coding & Editing Rules
- Make **minimal, targeted changes** to achieve the goal
- Follow existing code style and conventions
- Use **defensive coding patterns** for error handling (e.g., auto-create missing tables)
- Add tests and validation for new features
- **Never delete existing functionality** without migration path

---

## 🏗️ Project Architecture

### 📁 File Structure (Python-First)

```
tracking-system/
├── tracking_app/               # 🐍 PRIMARY: Python Streamlit Application
│   ├── app.py                  # Main Streamlit entry point
│   ├── database.py             # SQLite database connection
│   ├── models.py               # Data models (Habit, Task, etc.)
│   ├── storage.py              # Storage API (replaces js/storage.js)
│   ├── pages/                  # Streamlit pages
│   │   ├── dashboard.py        # Dashboard view
│   │   ├── habits.py           # Habits tracking
│   │   ├── tasks.py            # Tasks/Todos
│   │   ├── finances.py         # Finances/Budget
│   │   ├── health.py           # Health metrics
│   │   ├── time.py             # Time tracking
│   │   ├── goals.py            # Goals tracking
│   │   └── achievements.py     # Achievements/Gamification
│   ├── charts.py               # Plotly chart definitions
│   └── utils.py                # Utility functions
│
├── brain/                      # 🧠 Python AI/Brain Module
│   ├── core/                   # Core brain components
│   ├── brains/                 # Specialized brain modules
│   ├── tools/                  # Tool definitions
│   ├── policies/               # Validation policies
│   ├── state/                  # State machines
│   ├── audit/                  # Audit logging
│   ├── security/               # Security components
│   └── design/                 # Design documents
│
├── landscaping_new/            # Landscaping management module (Python/Streamlit)
│
├── js/                         # ⚠️ LEGACY: JavaScript modules (migrating to Python)
│   ├── app.js                  # Main application controller
│   ├── storage.js              # Data persistence layer
│   ├── habits.js               # Habits module
│   ├── tasks.js                # Tasks/Todos module
│   ├── finances.js             # Finances/Budget module
│   ├── health.js               # Health metrics module
│   ├── time.js                 # Time tracking module
│   ├── goals.js                # Goals module
│   ├── achievements.js         # Achievements/gamification module
│   └── charts.js               # Chart visualization
│
├── css/                        # ⚠️ LEGACY: Styles (migrating to Streamlit)
│   └── styles.css
│
├── index.html                  # ⚠️ LEGACY: HTML entry point (migrating to Streamlit)
│
├── docs/
│   ├── research/               # Research documentation
│   ├── specs/                  # Feature specifications
│   ├── schemas/                # Data schemas
│   └── guides/                 # Implementation guides
│
├── assets/
│   ├── icons/                  # Icon assets
│   └── sounds/                 # Sound effects
│
├── phases/                     # Phase implementation docs
├── templates/                  # Chunked todo templates
└── PROJECT_RULES.md            # This file
```

### 🔧 Python Module Pattern

Each Python module MUST follow this pattern:

```python
"""
module_name.py - Brief Description

Detailed description of the module's purpose and functionality.
"""

from dataclasses import dataclass
from typing import Optional, List
from datetime import datetime

# 1. Configuration/constants first
DEFAULT_ICON = "🎯"
DEFAULT_COLOR = "#6366f1"

# 2. Data classes/models
@dataclass
class Item:
    """Represents an item in the system."""
    id: str
    name: str
    created_at: datetime
    
    def to_dict(self) -> dict:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "name": self.name,
            "created_at": self.created_at.isoformat()
        }
    
    @classmethod
    def from_dict(cls, data: dict) -> "Item":
        """Create instance from dictionary."""
        return cls(
            id=data["id"],
            name=data["name"],
            created_at=datetime.fromisoformat(data["created_at"])
        )

# 3. Manager/Service class
class ItemManager:
    """Manages CRUD operations for items."""
    
    def __init__(self, db_connection):
        self.db = db_connection
    
    def get_all(self) -> List[Item]:
        """Retrieve all items."""
        pass
    
    def get_by_id(self, item_id: str) -> Optional[Item]:
        """Retrieve a single item by ID."""
        pass
    
    def create(self, name: str) -> Item:
        """Create a new item."""
        pass
    
    def update(self, item_id: str, **updates) -> Optional[Item]:
        """Update an existing item."""
        pass
    
    def delete(self, item_id: str) -> bool:
        """Delete an item."""
        pass

# 4. Utility functions
def validate_item_name(name: str) -> bool:
    """Validate item name meets requirements."""
    return len(name.strip()) > 0
```

### 📦 Streamlit Page Pattern

Each Streamlit page MUST follow this pattern:

```python
"""
pages/page_name.py - Page Description

Streamlit page for [functionality].
"""

import streamlit as st
from tracking_app.storage import Storage
from tracking_app.models import Item

def render_sidebar():
    """Render page-specific sidebar elements."""
    pass

def render_main_content():
    """Render the main page content."""
    pass

def handle_add_item():
    """Handle adding a new item."""
    pass

def handle_edit_item(item_id: str):
    """Handle editing an existing item."""
    pass

def main():
    """Main page entry point."""
    st.title("Page Title")
    
    render_sidebar()
    render_main_content()

if __name__ == "__main__":
    main()
```

---

## 💻 Coding Standards

### 🐍 Python Rules (PRIMARY)

1. **Follow PEP 8 Style Guide**
   ```python
   # ✅ Good - snake_case for functions/variables
   def calculate_streak(habit_id: str) -> int:
       completed_dates = get_completed_dates(habit_id)
       return len(completed_dates)

   # ❌ Bad - camelCase for functions
   def calculateStreak(habitId):
       completedDates = getCompletedDates(habitId)
       return len(completedDates)
   ```

2. **Use Type Hints**
   ```python
   # ✅ Good
   from typing import Optional, List
   
   def get_habit(habit_id: str) -> Optional[Habit]:
       """Retrieve a habit by ID."""
       return habits.get(habit_id)
   
   def get_all_habits() -> List[Habit]:
       """Retrieve all habits."""
       return list(habits.values())

   # ❌ Bad - No type hints
   def get_habit(habit_id):
       return habits.get(habit_id)
   ```

3. **Use Dataclasses for Models**
   ```python
   # ✅ Good
   from dataclasses import dataclass
   from datetime import datetime
   
   @dataclass
   class Habit:
       id: str
       name: str
       icon: str = "🎯"
       color: str = "#6366f1"
       created_at: datetime = None
       
       def __post_init__(self):
           if self.created_at is None:
               self.created_at = datetime.now()
   ```

4. **Use Docstrings for Documentation**
   ```python
   # ✅ Good
   def calculate_streak(habit_id: str) -> int:
       """
       Calculate the current streak for a habit.
       
       Args:
           habit_id: The unique identifier of the habit.
           
       Returns:
           The number of consecutive days the habit has been completed.
           
       Example:
           >>> calculate_streak("habit_123")
           7
       """
       # Implementation
       pass
   ```

5. **Use f-strings for String Formatting**
   ```python
   # ✅ Good
   message = f"Habit '{habit.name}' completed! +{xp} XP"

   # ❌ Bad
   message = "Habit '{}' completed! +{} XP".format(habit.name, xp)
   # ❌ Worse
   message = "Habit '" + habit.name + "' completed! +" + str(xp) + " XP"
   ```

6. **Use Context Managers for Resources**
   ```python
   # ✅ Good
   with sqlite3.connect(DATABASE_PATH) as conn:
       cursor = conn.cursor()
       cursor.execute("SELECT * FROM habits")
       
   # ❌ Bad
   conn = sqlite3.connect(DATABASE_PATH)
   cursor = conn.cursor()
   cursor.execute("SELECT * FROM habits")
   conn.close()  # Might not close on exception
   ```

7. **Use List/Dict Comprehensions**
   ```python
   # ✅ Good
   completed_habits = [h for h in habits if h.completed_today]
   habit_names = {h.id: h.name for h in habits}

   # ❌ Bad
   completed_habits = []
   for h in habits:
       if h.completed_today:
           completed_habits.append(h)
   ```

8. **Use Pydantic for API/Data Validation**
   ```python
   # ✅ Good
   from pydantic import BaseModel, validator
   
   class HabitCreate(BaseModel):
       name: str
       icon: str = "🎯"
       color: str = "#6366f1"
       
       @validator('name')
       def name_not_empty(cls, v):
           if not v.strip():
               raise ValueError('Name cannot be empty')
           return v
   ```

### 📦 Streamlit-Specific Rules

1. **Use st.session_state for State Management**
   ```python
   # ✅ Good
   if 'habits' not in st.session_state:
       st.session_state.habits = load_habits()
   
   habits = st.session_state.habits

   # ❌ Bad - Global variables don't persist across reruns
   habits = load_habits()
   ```

2. **Use st.columns for Layout**
   ```python
   # ✅ Good
   col1, col2, col3 = st.columns([1, 2, 1])
   with col1:
       st.metric("Habits", len(habits))
   with col2:
       st.metric("Streak", total_streak)
   with col3:
       st.metric("XP", user_xp)
   ```

3. **Use st.form for Data Entry**
   ```python
   # ✅ Good
   with st.form("add_habit"):
       name = st.text_input("Habit Name")
       icon = st.selectbox("Icon", ICONS)
       submitted = st.form_submit_button("Add Habit")
       if submitted and name:
           add_habit(name, icon)
   ```

### ⚠️ JavaScript Rules (LEGACY - Maintenance Only)

These rules apply ONLY to existing JavaScript code during the migration period. **No new JavaScript should be written.**

1. **Use const/let, never var**
2. **Use arrow functions for callbacks**
3. **Use optional chaining for DOM elements**
4. **Use template literals for HTML**

### ⚠️ CSS Rules (LEGACY - Maintenance Only)

CSS rules apply ONLY to existing styles during migration. Streamlit handles styling natively.

### ⚠️ HTML Rules (LEGACY - Maintenance Only)

HTML rules apply ONLY to existing markup during migration. Streamlit generates HTML automatically.

---

## 📊 Data Management Rules

### 💾 Storage Pattern (Python/SQLite)

All data MUST be managed through the `Storage` class in `tracking_app/storage.py`:

```python
# ✅ Good - Use Storage class
from tracking_app.storage import Storage

storage = Storage()
habits = storage.get_habits()
storage.save_habit(new_habit)

# ❌ Bad - Direct database access
import sqlite3
conn = sqlite3.connect('tracking.db')
cursor = conn.cursor()
cursor.execute("SELECT * FROM habits")
```

### 🗃️ Data Models (Python Dataclasses)

**Habit Model:**
```python
@dataclass
class Habit:
    id: str                    # Unique identifier (UUID)
    name: str                  # Habit name
    icon: str = "🎯"           # Emoji icon
    color: str = "#6366f1"     # Hex color code
    frequency: str = "daily"   # 'daily', 'weekly'
    created_at: datetime = None
    
    # Computed property - not stored
    @property
    def streak(self) -> int:
        """Calculate current streak."""
        return calculate_streak(self.id)
```

**Task Model:**
```python
@dataclass
class Task:
    id: str
    title: str
    description: str = ""
    due_date: datetime = None
    priority: str = "medium"   # 'low', 'medium', 'high'
    category: str = ""
    completed: bool = False
    created_at: datetime = None
```

**Transaction Model (Finances):**
```python
@dataclass
class Transaction:
    id: str
    description: str
    amount: float
    type: str                  # 'income', 'expense'
    category: str = ""
    date: datetime = None
    created_at: datetime = None
```

**Health Entry Model:**
```python
@dataclass
class HealthEntry:
    id: str
    date: datetime
    weight: float = None
    sleep_hours: float = None
    mood: str = "good"         # 'great', 'good', 'okay', 'bad'
    notes: str = ""
    created_at: datetime = None
```

**Goal Model:**
```python
@dataclass
class Goal:
    id: str
    title: str
    description: str = ""
    target: float = 0
    current: float = 0
    unit: str = ""
    deadline: datetime = None
    created_at: datetime = None
```

### 🗄️ Database Schema (SQLite)

```sql
-- Habits table
CREATE TABLE habits (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    icon TEXT DEFAULT '🎯',
    color TEXT DEFAULT '#6366f1',
    frequency TEXT DEFAULT 'daily',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Habit completions (for streak calculation)
CREATE TABLE habit_completions (
    id TEXT PRIMARY KEY,
    habit_id TEXT NOT NULL,
    completed_at DATE NOT NULL,
    FOREIGN KEY (habit_id) REFERENCES habits(id),
    UNIQUE(habit_id, completed_at)
);

-- Tasks table
CREATE TABLE tasks (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    due_date TIMESTAMP,
    priority TEXT DEFAULT 'medium',
    category TEXT,
    completed BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Transactions table
CREATE TABLE transactions (
    id TEXT PRIMARY KEY,
    description TEXT NOT NULL,
    amount REAL NOT NULL,
    type TEXT NOT NULL,
    category TEXT,
    date TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Health entries table
CREATE TABLE health_entries (
    id TEXT PRIMARY KEY,
    date DATE NOT NULL,
    weight REAL,
    sleep_hours REAL,
    mood TEXT DEFAULT 'good',
    notes TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    UNIQUE(date)
);

-- Goals table
CREATE TABLE goals (
    id TEXT PRIMARY KEY,
    title TEXT NOT NULL,
    description TEXT,
    target REAL,
    current REAL DEFAULT 0,
    unit TEXT,
    deadline TIMESTAMP,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- User data (XP, level, settings)
CREATE TABLE user_data (
    key TEXT PRIMARY KEY,
    value TEXT NOT NULL
);

-- Achievements
CREATE TABLE achievements (
    id TEXT PRIMARY KEY,
    unlocked_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### ⚠️ Legacy Storage (JavaScript/LocalStorage)

The JavaScript frontend uses LocalStorage. During migration, data must be synchronized:

```python
# Migration utility in tracking_app/migrate.py
def migrate_from_localstorage(json_data: dict) -> None:
    """Migrate data from LocalStorage export to SQLite."""
    for habit_data in json_data.get('habits', []):
        habit = Habit.from_dict(habit_data)
        storage.save_habit(habit)
```

---

## 🎮 Gamification Rules

### ⭐ XP System
- Completing a habit: **+10 XP**
- Completing a task: **+5 XP** (low), **+10 XP** (medium), **+20 XP** (high)
- Reaching a goal: **+50 XP**
- Maintaining a 7-day streak: **+25 XP**

### 🏆 Level Progression
- Level 1: 0 XP
- Level 2: 100 XP
- Level 3: 250 XP
- Each subsequent level: Previous + 150 XP

### 🎖️ Achievement Definitions
Achievements should be defined with:
- Unique ID
- Name
- Description
- Icon/emoji
- XP reward
- Unlock condition (function)

---

## 🔔 UI/UX Rules

### 📱 Responsive Design
- Mobile-first approach
- Breakpoints:
  - Mobile: < 768px
  - Tablet: 768px - 1024px
  - Desktop: > 1024px

### 🎨 Color Palette
| Purpose | Light Mode | Dark Mode |
|---------|------------|-----------|
| Primary | #6366f1 | #818cf8 |
| Success | #10b981 | #34d399 |
| Warning | #f59e0b | #fbbf24 |
| Danger | #ef4444 | #f87171 |
| Background | #f8fafc | #0f172a |
| Text | #1e293b | #f1f5f9 |

### ✨ Animations
- Use CSS transitions for simple animations
- Use JavaScript for complex animations (confetti, etc.)
- Keep animations under 300ms for UI feedback
- Respect `prefers-reduced-motion` media query

### 🍞 Toast Notifications
Always use the App.showToast method:
```javascript
App.showToast('Habit completed! +10 XP', 'success');
App.showToast('Failed to save', 'error');
App.showToast('Don\'t forget to check your tasks', 'warning');
App.showToast('New feature available', 'info');
```

---

## 🔧 Troubleshooting & Debugging

### Debug Mode
- Enable debug mode in `.env` for detailed logs
- Check audit logs and error logs for context
- Use migration/repair scripts for database issues
- Consult troubleshooting guides for common errors

### Common Issues
| Issue | Solution |
|-------|----------|
| Data not persisting | Check Storage module, verify localStorage quota |
| Charts not rendering | Verify Chart.js loaded, check data format |
| Dark mode not working | Check `data-theme` attribute on `<html>` |
| Modals not opening | Check modal overlay z-index, verify event bindings |

---

## 📝 Documentation Rules

### 📖 Code Comments
- Add file header comments explaining purpose
- Document complex algorithms
- Explain "why" not "what" for non-obvious code

### 📋 Commit Messages
Follow conventional commits format:
```
feat: add habit streak freeze feature
fix: correct streak calculation for skipped days
docs: update README with new installation steps
style: format code according to project rules
refactor: extract chart rendering to separate module
test: add unit tests for streak calculation
chore: update dependencies
```

### 📄 Documentation Updates
When adding new features:
1. Update `FEATURE_MAP.md` with new feature location
2. Add integration steps to relevant guide
3. Update `GETTING_STARTED.md` if workflow changes
4. Create spec document in `docs/specs/` for complex features

---

## 🧪 Testing Checklist

Before submitting changes, verify:

### ✅ Functionality
- [ ] All CRUD operations work correctly
- [ ] Data persists after page refresh
- [ ] Navigation between views works
- [ ] Modals open and close properly
- [ ] Forms validate input correctly

### ✅ UI/UX
- [ ] Responsive on mobile, tablet, desktop
- [ ] Dark mode displays correctly
- [ ] Animations are smooth
- [ ] No console errors
- [ ] Accessibility features work

### ✅ Data
- [ ] LocalStorage operations don't fail
- [ ] Data migration handles old formats
- [ ] Export/import functionality works
- [ ] Reset functionality clears all data

---

## 🚀 Development Workflow

### 📋 Phase Progression
1. **Phase 1: Foundation** - Project setup, data architecture
2. **Phase 2: Core Features** - Individual tracking modules
3. **Phase 3: Views & Navigation** - UI structure
4. **Phase 4: Statistics** - Charts and visualizations
5. **Phase 5: Gamification** - XP, achievements, rewards
6. **Phase 6: Notifications** - Reminders system
7. **Phase 7: Polish** - Final testing and optimization

### 🔄 Phase Development Protocol

**CRITICAL: This protocol MUST be followed for ALL phases.**

1. **At the start of each phase**, the AI assistant should ONLY create the phase markdown documentation file (e.g., `phases/PHASE_X_*.md`)
2. **DO NOT implement any code** until the user provides research and guidance
3. **Work through each phase TOGETHER** with the user - they will provide research, then the AI updates the code based on that research
4. **Wait for explicit approval** before moving to implementation
5. **The user is the driver** - they research, provide information, and guide the direction

**Workflow:**
```
User provides research → AI reviews existing code → AI updates where necessary → User approves
```

**This ensures:**
- User maintains control over development direction
- Research is properly incorporated
- No premature implementation without context

### 🔄 Before Starting Work
1. Check `ROADMAP.md` for current phase
2. Review this rules document
3. Ensure you understand the module pattern
4. Test changes across all themes/views

---

## 🧠 Reasoning & Planning

### Task Breakdown
- Break down tasks into smaller steps
- Gather context before making changes
- Validate changes with tests and build tools
- Communicate roadmap and next steps in documentation

### Context Gathering Checklist
Before implementing any feature:
- [ ] Read relevant documentation
- [ ] Check for existing similar features
- [ ] Identify integration points
- [ ] Consider edge cases
- [ ] Plan for extensibility

---

## 🔄 Migration Section

### Migration Strategy: Gradual Chunked Migration

The project is migrating from JavaScript/HTML/CSS to pure Python/Streamlit. This migration follows the **chunked todo system** with 1-3 tasks per chunk.

#### Migration Phases

| Phase | Description | Status |
|-------|-------------|--------|
| **A: Foundation** | Create Python app structure, database, models | `[ ]` Not Started |
| **B: Modules** | Migrate each JS module to Python (habits, tasks, etc.) | `[ ]` Not Started |
| **C: Dashboard** | Migrate dashboard and charts | `[ ]` Not Started |
| **D: Finalize** | Deprecate JS frontend, update docs | `[ ]` Not Started |

#### Migration Rules

1. **New features MUST be in Python** - No new JavaScript code
2. **Maintain data compatibility** - Both frontends must work during migration
3. **One module at a time** - Complete each migration chunk before moving on
4. **Test after each chunk** - Verify both frontends work
5. **Update documentation** - Keep docs in sync with migration progress

#### Migration Progress Tracking

See `TODO.md` for detailed chunk breakdown and current progress.

#### File Migration Map

| JavaScript File | Python Replacement | Status |
|-----------------|-------------------|--------|
| `js/storage.js` | `tracking_app/storage.py` | `[ ]` |
| `js/habits.js` | `tracking_app/pages/habits.py` | `[ ]` |
| `js/tasks.js` | `tracking_app/pages/tasks.py` | `[ ]` |
| `js/finances.js` | `tracking_app/pages/finances.py` | `[ ]` |
| `js/health.js` | `tracking_app/pages/health.py` | `[ ]` |
| `js/time.js` | `tracking_app/pages/time.py` | `[ ]` |
| `js/goals.js` | `tracking_app/pages/goals.py` | `[ ]` |
| `js/achievements.js` | `tracking_app/pages/achievements.py` | `[ ]` |
| `js/charts.js` | `tracking_app/charts.py` | `[ ]` |
| `js/app.js` | `tracking_app/app.py` | `[ ]` |
| `index.html` | Streamlit auto-generated | `[ ]` |
| `css/styles.css` | Streamlit themes | `[ ]` |

---

## ⚠️ Important Reminders

### Python Development (PRIMARY)
1. **ALWAYS** implement new features in Python first
2. **ALWAYS** use type hints in Python functions
3. **ALWAYS** follow PEP 8 style guidelines
4. **ALWAYS** use dataclasses for data models
5. **ALWAYS** use context managers for database connections
6. **ALWAYS** write docstrings for all functions

### Legacy JavaScript (MAINTENANCE ONLY)
1. **NEVER** write new JavaScript code
2. **NEVER** modify `storage.js` data structure without migration logic
3. **ONLY** fix critical bugs in JavaScript during migration period

### General
1. **ALWAYS** explain changes in plain language for non-coders
2. **ALWAYS** provide linear and non-linear expansion ideas
3. **ALWAYS** test in both light and dark modes (Streamlit themes)
4. **ALWAYS** update documentation when making changes
5. **NEVER** delete existing functionality without migration path

---

## 📐 Documentation Consistency Rules

### ⚠️ CRITICAL: All Documentation Must Align

**Every table, format, and structure MUST be consistent across ALL documentation files.** Inconsistencies create confusion and are strictly prohibited.

### Navigation Tables

ALL navigation tables across ALL documentation files MUST use this EXACT format:

```markdown
| Want to... | Go to... |
|------------|----------|
| **Get started** | [GETTING_STARTED.md](GETTING_STARTED.md) |
| **Understand rules** | [PROJECT_RULES.md](PROJECT_RULES.md) |
| **Find a feature** | [FEATURE_MAP.md](FEATURE_MAP.md) |
| **See roadmap** | [ROADMAP.md](ROADMAP.md) |
| **Check tasks** | [TODO.md](TODO.md) |
| **Read research** | [docs/research/](docs/research/) |
| **Understand Brain** | [brain/README.md](brain/README.md) |
```

**Rules:**
- Header: Always `| Want to... | Go to... |`
- Left column: Bold action description (e.g., `**Get started**`)
- Right column: Markdown link to the file/location
- Same items in the same order in ALL files
- NEVER use different formats for navigation tables

### File Reference Tables

For tables that list files and their purposes, use:

```markdown
| File | Purpose |
|------|---------|
| `filename.md` | Description of purpose |
```

### Status Tables

For tables showing status or progress, use appropriate headers for the context:

```markdown
| Item | Status |
|------|--------|
| Feature A | ✅ Complete |
| Feature B | 🔄 In Progress |
```

### General Documentation Rules

1. **Same structure across files** - If a section exists in multiple files, use the same format
2. **Same ordering** - Items should appear in the same order across files
3. **Same styling** - Bold, italics, code blocks must be used consistently
4. **Same terminology** - Use the same terms for the same concepts
5. **No variations** - If unsure, check existing files and match exactly

### Before Creating Any Documentation

- [ ] Check existing documentation for the format used
- [ ] Copy the exact table structure from existing files
- [ ] Verify ordering matches other files
- [ ] Ensure styling (bold, links) is identical

---

## 📚 Related Documentation

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

*Last updated: February 2026*
*Version: 3.0.0 - Python-First Migration*
