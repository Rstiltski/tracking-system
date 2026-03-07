# ⚠️ Task Alerts Module

Task deadline and reminder alerts for the Veryfyn Tracking System.

---

## Quick Links

| File | Purpose |
|------|---------|
| [`__init__.py`](__init__.py) | Public API exports |
| [`constants.py`](constants.py) | Alert types, priorities |
| [`helpers.py`](helpers.py) | Alert management logic |
| [`session_state.py`](session_state.py) | Alerts state |
| [`components.py`](components.py) | UI render functions |

---

## Features

- **Deadline Alerts**: Task deadline notifications
- **Priority Alerts**: Priority-based alerts
- **Escalation**: Alert escalation rules
- **Snooze**: Snooze alert functionality
- **Smart Alerts**: AI-powered alert timing

---

## Public API

### Constants

```python
from tracking_app.pages.task_alerts import (
    ALERT_TYPES,         # Alert type options
    PRIORITY_LEVELS,     # Priority settings
    ESCALATION_RULES,    # Escalation config
)
```

### Helper Functions

```python
from tracking_app.pages.task_alerts import (
    create_alert,        # Create new alert
    trigger_alert,       # Trigger an alert
    dismiss_alert,       # Dismiss alert
)
```

### Components

```python
from tracking_app.pages.task_alerts import (
    render_header,       # Page header
    render_alert_list,   # Active alerts
    render_alert_form,   # Alert configuration
    render_alert_preview,# Alert preview
)
```

---

## Usage Example

```python
import streamlit as st
from tracking_app.pages.task_alerts import (
    init_session_state,
    render_header,
    render_alert_list,
)

init_session_state()
render_header()
render_alert_list()
```

---

## Dependencies

- `streamlit` - UI framework
- `tracking_app.models` - Task model
- `tracking_app.pages.tasks` - Task integration

---

## Related Pages

- **Tasks**: Task management
- **Notification Settings**: Global notifications
- **Goals**: Goal alerts

---

## Cross-References

| Topic | File |
|-------|------|
| AI entry point | `../AI_START_HERE.md` |
| Project overview | `../README.md` |
| Backend architecture | `../brain/README.md` |
| Page module pattern | `../patterns/page_module.md` |
| Task alerts implementation | `../tracking_app/pages/task_alerts.py` |
| Alert models | `../brain/models/` |
| Task integration | `../tracking_app/pages/tasks/` |

---

**Last Updated:** March 2026
