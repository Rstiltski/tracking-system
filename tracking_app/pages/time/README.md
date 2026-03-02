# ⏱️ Time Module

Time tracking and productivity analysis for the Veryfyn Tracking System.

---

## Quick Links

| File | Purpose |
|------|---------|
| [`__init__.py`](__init__.py) | Public API exports |
| [`constants.py`](constants.py) | Time categories, formats |
| [`helpers.py`](helpers.py) | Duration calculations |
| [`session_state.py`](session_state.py) | Timer state |
| [`components.py`](components.py) | UI render functions |

---

## Features

- **Time Tracking**: Track time spent on activities
- **Timer**: Start/stop timer for tasks
- **Categories**: Categorize time entries
- **Reports**: Daily/weekly time reports
- **Productivity Analysis**: Analyze time distribution

---

## Public API

### Constants

```python
from tracking_app.pages.time import (
    TIME_CATEGORIES,     # Time entry categories
    DISPLAY_FORMATS,     # Time display formats
    DEFAULT_INTERVAL,    # Default timer interval
)
```

### Helper Functions

```python
from tracking_app.pages.time import (
    format_duration,     # Format seconds to HH:MM:SS
    calculate_total_time,# Sum time entries
    get_productivity_score,  # Calculate productivity
)
```

### Components

```python
from tracking_app.pages.time import (
    render_header,       # Page header
    render_timer,        # Timer widget
    render_time_entry,   # Add time entry form
    render_time_log,     # Time log display
    render_summary,      # Time summary chart
)
```

---

## Usage Example

```python
import streamlit as st
from tracking_app.pages.time import (
    init_session_state,
    render_header,
    render_timer,
    render_time_log,
)

init_session_state()
render_header()
render_timer()
render_time_log()
```

---

## Dependencies

- `streamlit` - UI framework
- `datetime` - Date/time handling
- `tracking_app.models` - TimeEntry model

---

## Related Pages

- **Tasks**: Link time to tasks
- **Insights**: Time analytics
- **Goals**: Time-based goals