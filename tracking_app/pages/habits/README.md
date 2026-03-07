# ✅ Habits Module

Habit tracking and management for the Veryfyn Tracking System.

---

## Quick Links

| File | Purpose |
|------|---------|
| [`__init__.py`](__init__.py) | Public API exports |
| [`constants.py`](constants.py) | Habit types, frequencies |
| [`helpers.py`](helpers.py) | Habit management logic |
| [`session_state.py`](session_state.py) | Habits state |
| [`card_view.py`](card_view.py) | Card view component |
| [`edit_form.py`](edit_form.py) | Edit form component |
| [`progress_rings.py`](progress_rings.py) | Progress visualization |

---

## Features

- **Habit Tracking**: Track daily/weekly habits
- **Streaks**: Track consecutive completions
- **Categories**: Organize habits by category
- **Progress Rings**: Visual progress indicators
- **Multiple Views**: Card and spreadsheet views

---

## Public API

### Constants

```python
from tracking_app.pages.habits import (
    HABIT_TYPES,         # Habit type options
    FREQUENCY_OPTIONS,   # Tracking frequency
    CATEGORY_OPTIONS,    # Habit categories
)
```

### Helper Functions

```python
from tracking_app.pages.habits import (
    create_habit,        # Create new habit
    update_habit,        # Update habit
    delete_habit,        # Delete habit
    complete_habit,      # Mark habit complete
)
```

### Components

```python
from tracking_app.pages.habits import (
    render_header,       # Page header
    render_habit_cards,  # Card view
    render_spreadsheet,  # Spreadsheet view
    render_add_form,     # Add habit form
)
```

---

## Usage Example

```python
import streamlit as st
from tracking_app.pages.habits import (
    init_session_state,
    render_header,
    render_habit_cards,
    render_add_form,
)

init_session_state()
render_header()
render_habit_cards()
render_add_form()
```

---

## Views

### Card View
Visual card-based display of habits with progress rings.

### Spreadsheet View
Table-based view for bulk editing and overview.

---

## Dependencies

- `streamlit` - UI framework
- `tracking_app.models` - Habit model
- `tracking_app.storage` - Data storage

---

## Related Pages

- **Habit Analytics**: Habit insights
- **Habit Reminders**: Habit reminders
- **Habit Experiments**: Habit experiments
- **Stacks**: Habit stacking

---

## Cross-References

| Topic | File |
|-------|------|
| AI entry point | `../AI_START_HERE.md` |
| Project overview | `../README.md` |
| Backend architecture | `../brain/README.md` |
| Page module pattern | `../patterns/page_module.md` |
| Habit implementation | `../tracking_app/pages/habits.py` |
| Habit models | `../brain/models/` |
| Habit analytics | `../tracking_app/pages/habit_analytics/` |

---

**Last Updated:** March 2026
