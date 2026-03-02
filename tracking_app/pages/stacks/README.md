# 📚 Stacks Module

Habit stacking and routine management for the Veryfyn Tracking System.

---

## Quick Links

| File | Purpose |
|------|---------|
| [`__init__.py`](__init__.py) | Public API exports |
| [`constants.py`](constants.py) | Stack types, templates |
| [`helpers.py`](helpers.py) | Stack management logic |
| [`session_state.py`](session_state.py) | Stacks state |
| [`components.py`](components.py) | UI render functions |

---

## Features

- **Habit Stacking**: Stack habits together
- **Routines**: Create morning/evening routines
- **Templates**: Pre-built stack templates
- **Ordering**: Custom habit ordering
- **Time Blocks**: Time-based stacks

---

## Public API

### Constants

```python
from tracking_app.pages.stacks import (
    STACK_TYPES,         # Stack type options
    TIME_BLOCKS,         # Time block options
    STACK_TEMPLATES,     # Pre-built templates
)
```

### Helper Functions

```python
from tracking_app.pages.stacks import (
    create_stack,        # Create new stack
    add_to_stack,        # Add habit to stack
    reorder_stack,       # Reorder habits
)
```

### Components

```python
from tracking_app.pages.stacks import (
    render_header,       # Page header
    render_stack_list,   # Stacks overview
    render_stack_detail, # Single stack view
    render_stack_form,   # Stack creation form
)
```

---

## Usage Example

```python
import streamlit as st
from tracking_app.pages.stacks import (
    init_session_state,
    render_header,
    render_stack_list,
    render_stack_detail,
)

init_session_state()
render_header()
render_stack_list()
render_stack_detail()
```

---

## Dependencies

- `streamlit` - UI framework
- `tracking_app.models` - Stack model
- `tracking_app.pages.habits` - Habit integration

---

## Related Pages

- **Habits**: Habit management
- **Time**: Time tracking
- **Habit Reminders**: Stack reminders