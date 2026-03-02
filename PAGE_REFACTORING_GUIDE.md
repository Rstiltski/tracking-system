# 📦 Page Refactoring Guide

**Complete documentation of the modular refactoring process for the Veryfyn Tracking System.**

---

## 🧭 Quick Navigation

| Want to... | Go to... |
|------------|----------|
| **Get started** | [GETTING_STARTED.md](GETTING_STARTED.md) |
| **Understand rules** | [PROJECT_RULES.md](PROJECT_RULES.md) |
| **Find features** | [FEATURE_MAP.md](FEATURE_MAP.md) |
| **See roadmap** | [ROADMAP.md](ROADMAP.md) |

---

## TABLE OF CONTENTS

| # | Section | Key Info |
|---|---------|----------|
| 1 | Overview | What was done |
| 2 | Motivation | Why we refactored |
| 3 | Pattern | Modular structure |
| 4 | Before & After | File comparison |
| 5 | Refactored Pages | Complete list |
| 6 | File Purposes | What each file does |
| 7 | Testing | Validation procedures |
| 8 | Extending | How to add new pages |
| 9 | Troubleshooting | Common issues |

---

## §1 Overview

This document describes the comprehensive refactoring of 27 Streamlit pages from single-file modules to modular component folders. Each page was split into consistent, focused files following the pattern established by the existing `habits/` folder.

### Key Achievements

| Metric | Value |
|--------|-------|
| Pages Refactored | 27 |
| New Files Created | ~135 |
| Code Organization | 5-file pattern per page |
| Documentation Files | 27 README.md files |

---

## §2 Motivation

### Problems with Single-File Pages

1. **Code Navigation**: 500+ line files are hard to navigate
2. **Testing Difficulty**: Cannot test helpers without Streamlit
3. **Code Reuse**: Functions embedded in pages can't be imported
4. **Maintenance**: Changes require understanding entire file
5. **Collaboration**: Multiple developers can't work on same page

### Benefits of Modular Structure

| Benefit | Description |
|---------|-------------|
| **Separation of Concerns** | Each file has single responsibility |
| **Testability** | Helpers can be unit tested independently |
| **Reusability** | Helper functions can be imported elsewhere |
| **Maintainability** | Easier to find and modify specific functionality |
| **Consistency** | All pages follow same structure |

---

## §3 The Modular Pattern

Each page module follows this consistent 5-file structure:

```
page_name/
├── __init__.py        # Public exports
├── constants.py       # Configuration & constants
├── helpers.py         # Pure functions (no Streamlit)
├── session_state.py   # Session state management
├── components.py      # UI render functions
└── README.md          # Documentation
```

### File Responsibilities

| File | Purpose | Dependencies |
|------|---------|--------------|
| `__init__.py` | Exports public API | All modules |
| `constants.py` | Icons, colors, options, labels | None |
| `helpers.py` | Data processing, calculations | datetime, typing |
| `session_state.py` | st.session_state initialization | streamlit, helpers |
| `components.py` | UI render functions | streamlit, helpers, constants |
| `README.md` | Module documentation | N/A |

### Dependency Rules

```
constants.py  ←── No dependencies
     ↓
helpers.py    ←── Can import constants
     ↓
session_state.py ←── Can import helpers, constants
     ↓
components.py ←── Can import all above
     ↓
__init__.py   ←── Exports from all above
```

**Important**: `helpers.py` should NEVER import `streamlit` - this allows unit testing.

---

## §4 Before & After

### Before: Single File

```
tracking_app/pages/
├── finances.py          # 450 lines
├── health.py            # 520 lines
├── tasks.py             # 480 lines
├── goals.py             # 490 lines
└── ...
```

### After: Modular Folders

```
tracking_app/pages/
├── finances/
│   ├── __init__.py
│   ├── constants.py
│   ├── helpers.py
│   ├── session_state.py
│   ├── components.py
│   └── README.md
├── health/
│   ├── __init__.py
│   ├── constants.py
│   ├── helpers.py
│   ├── session_state.py
│   ├── components.py
│   └── README.md
└── ...
```

### Main Page File (After Refactoring)

Each main page file now just orchestrates the components:

```python
"""
Finances page - Financial tracking and budgeting.

Streamlit page for managing income, expenses, and budgets.
"""

import streamlit as st

from .finances import (
    init_session_state,
    render_header,
    render_summary,
    render_filters,
    render_add_transaction_form,
    render_transactions_list,
    render_category_breakdown,
)


def main():
    """Main entry point for the Finances page."""
    init_session_state()
    
    render_header()
    render_summary()
    render_filters()
    
    col1, col2 = st.columns([1, 1])
    
    with col1:
        render_add_transaction_form()
    
    with col2:
        render_category_breakdown()
    
    render_transactions_list()


if __name__ == "__main__":
    main()
```

---

## §5 Refactored Pages

### Complete List of Refactored Pages

| # | Page | Folder | Purpose |
|---|------|--------|---------|
| 1 | Dashboard | `dashboard/` | Main overview |
| 2 | Habits | `habits/` | Habit tracking |
| 3 | Tasks | `tasks/` | Task management |
| 4 | Finances | `finances/` | Financial tracking |
| 5 | Health | `health/` | Health metrics |
| 6 | Goals | `goals/` | Goal tracking |
| 7 | Time | `time/` | Time tracking |
| 8 | Achievements | `achievements/` | Gamification |
| 9 | Insights | `insights/` | Analytics |
| 10 | Challenges | `challenges/` | Challenge system |
| 11 | Backup & Restore | `backup_restore/` | Data backup |
| 12 | Data Export | `data_export/` | Export functionality |
| 13 | Data Import | `data_import/` | Import functionality |
| 14 | Data Lifecycle | `data_lifecycle/` | Data management |
| 15 | Emotional Health | `emotional_health/` | Emotion tracking |
| 16 | Friends | `friends/` | Social features |
| 17 | Goal Alerts | `goal_alerts/` | Goal notifications |
| 18 | Habit Analytics | `habit_analytics/` | Habit analysis |
| 19 | Habit Experiments | `habit_experiments/` | A/B testing |
| 20 | Habit Reminders | `habit_reminders/` | Habit notifications |
| 21 | Leaderboards | `leaderboards/` | Rankings |
| 22 | Notification Settings | `notification_settings/` | Preferences |
| 23 | Rewards | `rewards/` | Variable rewards |
| 24 | Stacks | `stacks/` | Habit stacking |
| 25 | Task Alerts | `task_alerts/` | Task notifications |
| 26 | Template Sharing | `template_sharing/` | Template exchange |
| 27 | Weekly Review | `weekly_review/` | Weekly summary |

---

## §6 File Purposes

### `__init__.py` - Public API

Exports the public interface of the module:

```python
"""
Finances module - Financial tracking components.

Public API for the Finances page.
"""

from .constants import (
    EXPENSE_CATEGORIES,
    INCOME_CATEGORIES,
    PERIOD_OPTIONS,
    TYPE_OPTIONS,
)
from .helpers import (
    format_currency,
    calculate_totals,
    get_category_totals,
    get_date_range,
)
from .session_state import init_session_state
from .components import (
    render_header,
    render_summary,
    render_add_transaction_form,
    render_filters,
    render_transactions_list,
    render_category_breakdown,
)

__all__ = [
    # Constants
    "EXPENSE_CATEGORIES",
    "INCOME_CATEGORIES",
    "PERIOD_OPTIONS",
    "TYPE_OPTIONS",
    # Helpers
    "format_currency",
    "calculate_totals",
    "get_category_totals",
    "get_date_range",
    # Session State
    "init_session_state",
    # Components
    "render_header",
    "render_summary",
    "render_add_transaction_form",
    "render_filters",
    "render_transactions_list",
    "render_category_breakdown",
]
```

### `constants.py` - Configuration

Contains all static configuration:

```python
"""
Constants for the Finances page.

Contains all static configuration: icons, colors, categories, options.
"""

# Icons
INCOME_ICON = "📈"
EXPENSE_ICON = "📉"
BALANCE_ICON = "💰"

# Categories
EXPENSE_CATEGORIES = [
    "Food & Dining",
    "Transportation",
    "Housing",
    "Utilities",
    "Entertainment",
    "Healthcare",
    "Shopping",
    "Education",
    "Personal Care",
    "Other",
]

INCOME_CATEGORIES = [
    "Salary",
    "Freelance",
    "Investments",
    "Gifts",
    "Other Income",
]

# Filter options
PERIOD_OPTIONS = {
    "all": "All Time",
    "today": "Today",
    "week": "This Week",
    "month": "This Month",
    "year": "This Year",
}

TYPE_OPTIONS = {
    "all": "All Types",
    "income": "Income Only",
    "expense": "Expenses Only",
}
```

### `helpers.py` - Pure Functions

Contains all business logic without UI dependencies:

```python
"""
Helper functions for the Finances page.

Pure functions for data processing - NO Streamlit dependencies.
This allows unit testing without mocking Streamlit.
"""

from datetime import date, timedelta
from typing import List, Dict, Any


def format_currency(amount: float, currency: str = "$") -> str:
    """
    Format a number as currency.
    
    Args:
        amount: The amount to format
        currency: Currency symbol (default: $)
    
    Returns:
        Formatted currency string
    """
    return f"{currency}{amount:,.2f}"


def calculate_totals(transactions: List[Any]) -> Dict[str, float]:
    """
    Calculate income, expenses, and balance from transactions.
    
    Args:
        transactions: List of Transaction objects
    
    Returns:
        Dict with 'income', 'expenses', and 'balance' keys
    """
    income = sum(t.amount for t in transactions if t.type == "income")
    expenses = sum(t.amount for t in transactions if t.type == "expense")
    
    return {
        "income": income,
        "expenses": expenses,
        "balance": income - expenses,
    }


def get_date_range(period: str) -> tuple:
    """
    Get start and end dates for a period.
    
    Args:
        period: Period key ('all', 'today', 'week', 'month', 'year')
    
    Returns:
        Tuple of (start_date, end_date)
    """
    today = date.today()
    
    if period == "all":
        return None, None
    elif period == "today":
        return today, today
    elif period == "week":
        start = today - timedelta(days=today.weekday())
        return start, today
    elif period == "month":
        start = today.replace(day=1)
        return start, today
    elif period == "year":
        start = today.replace(month=1, day=1)
        return start, today
    
    return None, None
```

### `session_state.py` - State Management

Manages Streamlit session state:

```python
"""
Session state management for the Finances page.

Handles initialization and management of st.session_state variables.
"""

import streamlit as st
from typing import Any


def init_session_state() -> None:
    """
    Initialize all session state variables for the Finances page.
    
    This should be called at the start of the page render.
    """
    # Filter period
    if "filter_period" not in st.session_state:
        st.session_state.filter_period = "month"
    
    # Filter type
    if "filter_type" not in st.session_state:
        st.session_state.filter_type = "all"


def get_filter_period() -> str:
    """Get the current filter period."""
    return st.session_state.get("filter_period", "month")


def set_filter_period(period: str) -> None:
    """Set the filter period."""
    st.session_state.filter_period = period
```

### `components.py` - UI Rendering

Contains all Streamlit UI components:

```python
"""
UI components for the Finances page.

Contains all render functions for the financial tracking interface.
"""

import streamlit as st
from datetime import date

from tracking_app.models import Transaction

from .constants import EXPENSE_CATEGORIES, INCOME_CATEGORIES
from .helpers import get_date_range, calculate_totals, format_currency
from .session_state import get_filter_period


def render_header():
    """Render page header."""
    st.title("💰 Finances")
    st.markdown("Track your income, expenses, and monitor your budget.")


def render_summary():
    """Render financial summary metrics."""
    storage = st.session_state.storage
    start_date, end_date = get_date_range(get_filter_period())
    
    transactions = storage.get_transactions(start_date=start_date, end_date=end_date)
    totals = calculate_totals(transactions)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("📈 Income", format_currency(totals['income']))
    
    with col2:
        st.metric("📉 Expenses", format_currency(totals['expenses']))
    
    with col3:
        st.metric("💰 Balance", format_currency(totals['balance']))
```

---

## §7 Testing

### Import Validation Test

Test that all modules can be imported:

```python
"""Test that all page modules can be imported."""

def test_import_finances():
    from tracking_app.pages.finances import (
        EXPENSE_CATEGORIES,
        format_currency,
        init_session_state,
        render_header,
    )
    assert len(EXPENSE_CATEGORIES) > 0

def test_import_health():
    from tracking_app.pages.health import (
        MOOD_OPTIONS,
        calculate_health_score,
        init_session_state,
        render_header,
    )
    assert len(MOOD_OPTIONS) > 0
```

### Helper Function Unit Tests

Test pure functions without Streamlit:

```python
"""Unit tests for helper functions."""

from tracking_app.pages.finances.helpers import (
    format_currency,
    calculate_totals,
    get_date_range,
)


def test_format_currency():
    assert format_currency(100.50) == "$100.50"
    assert format_currency(1000) == "$1,000.00"
    assert format_currency(0) == "$0.00"


def test_calculate_totals():
    from dataclasses import dataclass
    
    @dataclass
    class MockTransaction:
        amount: float
        type: str
    
    transactions = [
        MockTransaction(100, "income"),
        MockTransaction(50, "expense"),
        MockTransaction(200, "income"),
    ]
    
    totals = calculate_totals(transactions)
    
    assert totals["income"] == 300
    assert totals["expenses"] == 50
    assert totals["balance"] == 250
```

---

## §8 Extending

### Adding a New Page

1. Create the page folder:

```bash
mkdir tracking_app/pages/new_page
```

2. Create the 5 files:

```bash
touch tracking_app/pages/new_page/__init__.py
touch tracking_app/pages/new_page/constants.py
touch tracking_app/pages/new_page/helpers.py
touch tracking_app/pages/new_page/session_state.py
touch tracking_app/pages/new_page/components.py
touch tracking_app/pages/new_page/README.md
```

3. Implement each file following the pattern

4. Create the main page file:

```bash
touch tracking_app/pages/new_page.py
```

5. Add to `__init__.py` of the pages package

### Adding Functions to Existing Pages

1. **Constants**: Add to `constants.py`
2. **Business Logic**: Add to `helpers.py` (no Streamlit imports!)
3. **State Variables**: Add to `session_state.py`
4. **UI Components**: Add to `components.py`
5. **Export**: Add to `__init__.py` if public

---

## §9 Troubleshooting

### Common Issues

| Issue | Cause | Solution |
|-------|-------|----------|
| Import error | Missing `__init__.py` | Create `__init__.py` with exports |
| Circular import | Wrong dependency order | Check dependency rules |
| Streamlit in helpers | `st` imported in helpers.py | Move to components.py |
| Session state not persisting | Not calling `init_session_state()` | Call at page start |
| Function not found | Not exported from `__init__.py` | Add to `__all__` |

### Debug Import Issues

```python
# Debug imports
try:
    from tracking_app.pages.finances import format_currency
except ImportError as e:
    print(f"Import error: {e}")
    # Check __init__.py exports
```

---

## 📚 Related Documentation

| If you need... | Read this file |
|----------------|---------------|
| Development guidelines | `PROJECT_RULES.md` |
| Architecture design | `TRACKING_SYSTEM_DESIGN.md` |
| Feature-to-file mapping | `FEATURE_MAP.md` |
| Page-specific docs | `tracking_app/pages/*/README.md` |

---

**Last Updated:** March 2026
**Version:** 1.0.0