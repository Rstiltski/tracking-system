# ⏰ Habit Reminders Module

Habit reminder configuration and management for the Veryfyn Tracking System.

---

## Quick Links

| File | Purpose |
|------|---------|
| [`__init__.py`](__init__.py) | Public API exports |
| [`constants.py`](constants.py) | Reminder types, frequencies |
| [`helpers.py`](helpers.py) | Reminder scheduling logic |
| [`session_state.py`](session_state.py) | Reminders state |
| [`components.py`](components.py) | UI render functions |

---

## Features

- **Time-based Reminders**: Set specific reminder times
- **Frequency Options**: Daily, weekly, custom frequency
- **Multiple Reminders**: Multiple reminders per habit
- **Snooze**: Snooze functionality
- **Smart Reminders**: AI-suggested reminder times

---

## Public API

### Constants

```python
from tracking_app.pages.habit_reminders import (
    REMINDER_TYPES,      # Reminder type options
    FREQUENCY_OPTIONS,   # Frequency choices
    SNOOZE_OPTIONS,      # Snooze durations
)
```

### Helper Functions

```python
from tracking_app.pages.habit_reminders import (
    create_reminder,     # Create new reminder
    schedule_reminder,   # Schedule reminder
    get_next_reminder,   # Get next reminder time
)
```

### Components

```python
from tracking_app.pages.habit_reminders import (
    render_header,       # Page header
    render_reminder_list,# Configured reminders
    render_reminder_form,# Reminder creation form
    render_calendar,     # Calendar view
)
```

---

## Usage Example

```python
import streamlit as st
from tracking_app.pages.habit_reminders import (
    init_session_state,
    render_header,
    render_reminder_list,
    render_reminder_form,
)

init_session_state()
render_header()
render_reminder_list()
render_reminder_form()
```

---

## Dependencies

- `streamlit` - UI framework
- `datetime` - Time handling
- `tracking_app.models` - Habit model

---

## Related Pages

- **Habits**: Habit management
- **Notification Settings**: Global notifications
- **Habit Analytics**: Habit tracking