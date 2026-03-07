# 🎯 Goals Module

Goal setting and progress tracking for the Veryfyn Tracking System.

---

## Quick Links

| File | Purpose |
|------|---------|
| [`__init__.py`](__init__.py) | Public API exports |
| [`constants.py`](constants.py) | Goal types, status options |
| [`helpers.py`](helpers.py) | Progress calculations |
| [`session_state.py`](session_state.py) | Goal state management |
| [`components.py`](components.py) | UI render functions |

---

## Features

- **Goal Setting**: Create SMART goals
- **Progress Tracking**: Track progress percentage
- **Categories**: Organize goals by category
- **Deadlines**: Set target dates
- **Milestones**: Break goals into milestones

---

## Public API

### Constants

```python
from tracking_app.pages.goals import (
    GOAL_CATEGORIES,     # Goal category options
    STATUS_OPTIONS,      # Goal status options
    PRIORITY_LEVELS,     # Priority levels
)
```

### Helper Functions

```python
from tracking_app.pages.goals import (
    calculate_progress,   # Calculate completion %
    get_remaining_days,   # Days until deadline
    check_goal_complete,  # Check if goal achieved
)
```

### Components

```python
from tracking_app.pages.goals import (
    render_header,        # Page header
    render_goal_form,     # Add/edit goal form
    render_goal_list,     # Goal list display
    render_progress_chart,# Progress visualization
    render_goal_detail,   # Single goal detail
)
```

---

## Usage Example

```python
import streamlit as st
from tracking_app.pages.goals import (
    init_session_state,
    render_header,
    render_goal_form,
    render_goal_list,
)

init_session_state()
render_header()
render_goal_form()
render_goal_list()
```

---

## Dependencies

- `streamlit` - UI framework
- `datetime` - Date handling
- `tracking_app.models` - Goal model

---

## Related Pages

- **Goal Alerts**: Goal notifications
- **Insights**: Goal analytics
- **Achievements**: Goal achievements

---

## Cross-References

| Topic | File |
|-------|------|
| AI entry point | `../AI_START_HERE.md` |
| Project overview | `../README.md` |
| Backend architecture | `../brain/README.md` |
| Page module pattern | `../patterns/page_module.md` |
| Goal implementation | `../tracking_app/pages/goals.py` |
| Goal models | `../brain/models/` |
| Goal alerts | `../tracking_app/pages/goal_alerts/` |

---

**Last Updated:** March 2026
