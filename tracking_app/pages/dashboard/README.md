# 📊 Dashboard Module

Main overview dashboard for the Veryfyn Tracking System.

---

## Quick Links

| File | Purpose |
|------|---------|
| [`__init__.py`](__init__.py) | Public API exports |
| [`constants.py`](constants.py) | Layout config, colors |
| [`helpers.py`](helpers.py) | Summary calculations |
| [`session_state.py`](session_state.py) | Dashboard state |
| [`components.py`](components.py) | UI render functions |

---

## Features

- **Overview Summary**: Quick stats for all areas
- **Recent Activity**: Latest habits, tasks, entries
- **Progress Charts**: Visual progress indicators
- **Quick Actions**: Shortcuts to common actions
- **Customizable Layout**: Configurable widgets

---

## Public API

### Constants

```python
from tracking_app.pages.dashboard import (
    WIDGET_OPTIONS,      # Available widgets
    LAYOUT_OPTIONS,      # Layout configurations
    CHART_COLORS,        # Chart color schemes
)
```

### Helper Functions

```python
from tracking_app.pages.dashboard import (
    get_summary_stats,   # Get overview statistics
    get_recent_activity, # Get recent entries
    calculate_streaks,   # Calculate current streaks
)
```

### Components

```python
from tracking_app.pages.dashboard import (
    render_header,       # Page header
    render_summary,      # Summary statistics
    render_quick_actions,# Quick action buttons
    render_recent,       # Recent activity widget
    render_charts,       # Progress charts
)
```

---

## Usage Example

```python
import streamlit as st
from tracking_app.pages.dashboard import (
    init_session_state,
    render_header,
    render_summary,
    render_quick_actions,
)

init_session_state()
render_header()
render_summary()
render_quick_actions()
```

---

## Dependencies

- `streamlit` - UI framework
- `tracking_app.pages` - All page modules

---

## Related Pages

- **All Pages**: Dashboard links to all features
- **Insights**: Detailed analytics
- **Weekly Review**: Weekly summary

---

## Cross-References

| Topic | File |
|-------|------|
| AI entry point | `../AI_START_HERE.md` |
| Project overview | `../README.md` |
| Backend architecture | `../brain/README.md` |
| Page module pattern | `../patterns/page_module.md` |
| Dashboard implementation | `../tracking_app/pages/dashboard.py` |
| Streamlit components | `../tracking_app/components/` |

---

**Last Updated:** March 2026
