# 🚨 Goal Alerts Module

Goal alert configuration and management for the Veryfyn Tracking System.

---

## Quick Links

| File | Purpose |
|------|---------|
| [`__init__.py`](__init__.py) | Public API exports |
| [`constants.py`](constants.py) | Alert types, thresholds |
| [`helpers.py`](helpers.py) | Alert trigger logic |
| [`session_state.py`](session_state.py) | Alerts state |
| [`components.py`](components.py) | UI render functions |

---

## Features

- **Progress Alerts**: Alerts for goal progress
- **Deadline Alerts**: Deadline approaching notifications
- **Milestone Alerts**: Milestone achievement alerts
- **Custom Thresholds**: Set custom alert thresholds
- **Delivery Methods**: Multiple notification channels

---

## Public API

### Constants

```python
from tracking_app.pages.goal_alerts import (
    ALERT_TYPES,         # Alert type options
    THRESHOLD_OPTIONS,   # Threshold percentages
    DELIVERY_METHODS,    # Notification channels
)
```

### Helper Functions

```python
from tracking_app.pages.goal_alerts import (
    create_alert,        # Create new alert
    check_alerts,        # Check alert conditions
    trigger_alert,       # Trigger alert notification
)
```

### Components

```python
from tracking_app.pages.goal_alerts import (
    render_header,       # Page header
    render_alert_list,   # Configured alerts
    render_alert_form,   # Alert creation form
    render_alert_history,# Alert history view
)
```

---

## Usage Example

```python
import streamlit as st
from tracking_app.pages.goal_alerts import (
    init_session_state,
    render_header,
    render_alert_list,
    render_alert_form,
)

init_session_state()
render_header()
render_alert_list()
render_alert_form()
```

---

## Dependencies

- `streamlit` - UI framework
- `datetime` - Date handling
- `tracking_app.models` - Goal model

---

## Related Pages

- **Goals**: Goal management
- **Notification Settings**: Global notifications
- **Task Alerts**: Task-specific alerts

---

## Cross-References

| Topic | File |
|-------|------|
| AI entry point | `../AI_START_HERE.md` |
| Project overview | `../README.md` |
| Backend architecture | `../brain/README.md` |
| Page module pattern | `../patterns/page_module.md` |
| Goal alerts implementation | `../tracking_app/pages/goal_alerts.py` |
| Alert models | `../brain/models/` |
| Goal integration | `../tracking_app/pages/goals/` |

---

**Last Updated:** March 2026
