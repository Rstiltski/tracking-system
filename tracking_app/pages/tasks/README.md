# ✅ Tasks Module

Task management and productivity tracking for the Veryfyn Tracking System.

---

## Quick Links

| File | Purpose |
|------|---------|
| [`__init__.py`](__init__.py) | Public API exports |
| [`constants.py`](constants.py) | Priority levels, status options |
| [`helpers.py`](helpers.py) | Task filtering, sorting |
| [`session_state.py`](session_state.py) | Task view state |
| [`components.py`](components.py) | UI render functions |

---

## Features

- **Task CRUD**: Create, read, update, delete tasks
- **Priority Levels**: High, medium, low priority
- **Due Dates**: Set and track due dates
- **Categories**: Organize tasks by category
- **Completion Tracking**: Mark tasks complete

---

## Public API

### Constants

```python
from tracking_app.pages.tasks import (
    PRIORITY_OPTIONS,    # Priority levels
    STATUS_OPTIONS,      # Task status options
    CATEGORY_OPTIONS,    # Task categories
)
```

### Helper Functions

```python
from tracking_app.pages.tasks import (
    filter_tasks,        # Filter tasks by criteria
    sort_tasks,          # Sort tasks by field
    get_overdue_tasks,   # Get overdue tasks
    calculate_completion_rate,  # Calculate completion %
)
```

### Components

```python
from tracking_app.pages.tasks import (
    render_header,       # Page header
    render_task_form,    # Add/edit task form
    render_task_list,    # Task list display
    render_filters,      # Filter controls
    render_stats,        # Task statistics
)
```

---

## Usage Example

```python
import streamlit as st
from tracking_app.pages.tasks import (
    init_session_state,
    render_header,
    render_task_form,
    render_task_list,
)

init_session_state()
render_header()
render_task_form()
render_task_list()
```

---

## Dependencies

- `streamlit` - UI framework
- `datetime` - Date handling
- `tracking_app.models` - Task model

---

## Related Pages

- **Task Alerts**: Task notifications
- **Time**: Time tracking for tasks
- **Goals**: Task-related goals

---

## Cross-References

| Topic | File |
|-------|------|
| AI entry point | `../AI_START_HERE.md` |
| Project overview | `../README.md` |
| Backend architecture | `../brain/README.md` |
| Page module pattern | `../patterns/page_module.md` |
| Task implementation | `../tracking_app/pages/tasks.py` |
| Task models | `../brain/models/` |
| Task alerts | `../tracking_app/pages/task_alerts/` |

---

**Last Updated:** March 2026
