# 🔔 Notification Settings Module

Global notification configuration for the Veryfyn Tracking System.

---

## Quick Links

| File | Purpose |
|------|---------|
| [`__init__.py`](__init__.py) | Public API exports |
| [`constants.py`](constants.py) | Notification types, sounds |
| [`helpers.py`](helpers.py) | Settings management |
| [`session_state.py`](session_state.py) | Settings state |
| [`components.py`](components.py) | UI render functions |

---

## Features

- **Notification Types**: Configure different notification types
- **Delivery Channels**: Email, push, in-app notifications
- **Quiet Hours**: Set do-not-disturb times
- **Sounds**: Custom notification sounds
- **Digest Mode**: Batch notifications

---

## Public API

### Constants

```python
from tracking_app.pages.notification_settings import (
    NOTIFICATION_TYPES,  # Available notification types
    DELIVERY_CHANNELS,   # Delivery options
    SOUND_OPTIONS,       # Sound choices
)
```

### Helper Functions

```python
from tracking_app.pages.notification_settings import (
    update_settings,     # Update notification settings
    get_settings,        # Get current settings
    toggle_notifications,# Toggle on/off
)
```

### Components

```python
from tracking_app.pages.notification_settings import (
    render_header,       # Page header
    render_settings_form,# Settings configuration
    render_quiet_hours,  # Quiet hours settings
    render_preview,      # Notification preview
)
```

---

## Usage Example

```python
import streamlit as st
from tracking_app.pages.notification_settings import (
    init_session_state,
    render_header,
    render_settings_form,
)

init_session_state()
render_header()
render_settings_form()
```

---

## Dependencies

- `streamlit` - UI framework
- `tracking_app.storage` - Settings storage

---

## Related Pages

- **Habit Reminders**: Habit-specific reminders
- **Goal Alerts**: Goal-specific alerts
- **Task Alerts**: Task-specific alerts