# 📊 Habit Analytics Module

Detailed analytics for habit tracking in the Veryfyn Tracking System.

---

## Quick Links

| File | Purpose |
|------|---------|
| [`__init__.py`](__init__.py) | Public API exports |
| [`constants.py`](constants.py) | Analytics types, ranges |
| [`helpers.py`](helpers.py) | Analytics calculations |
| [`session_state.py`](session_state.py) | Analytics state |
| [`components.py`](components.py) | UI render functions |

---

## Features

- **Streak Analysis**: Track habit streaks
- **Completion Rates**: Calculate completion percentages
- **Trends**: Identify habit trends over time
- **Comparisons**: Compare habits side-by-side
- **Heat Maps**: Visual activity heat maps

---

## Public API

### Constants

```python
from tracking_app.pages.habit_analytics import (
    ANALYSIS_TYPES,      # Available analysis types
    DATE_RANGES,         # Analysis date ranges
    CHART_OPTIONS,       # Chart configuration
)
```

### Helper Functions

```python
from tracking_app.pages.habit_analytics import (
    calculate_streaks,   # Calculate habit streaks
    calculate_rate,      # Calculate completion rate
    generate_trends,     # Generate trend data
)
```

### Components

```python
from tracking_app.pages.habit_analytics import (
    render_header,       # Page header
    render_habit_selector, # Habit selection
    render_analytics,    # Analytics display
    render_heatmap,      # Activity heat map
)
```

---

## Usage Example

```python
import streamlit as st
from tracking_app.pages.habit_analytics import (
    init_session_state,
    render_header,
    render_habit_selector,
    render_analytics,
)

init_session_state()
render_header()
render_habit_selector()
render_analytics()
```

---

## Dependencies

- `streamlit` - UI framework
- `pandas` - Data analysis
- `plotly` - Chart visualization

---

## Related Pages

- **Habits**: Habit management
- **Insights**: General insights
- **Weekly Review**: Weekly habit summary

---

## Cross-References

| Topic | File |
|-------|------|
| AI entry point | `../AI_START_HERE.md` |
| Project overview | `../README.md` |
| Backend architecture | `../brain/README.md` |
| Page module pattern | `../patterns/page_module.md` |
| Habit analytics implementation | `../tracking_app/pages/habit_analytics.py` |
| Habit models | `../brain/models/` |
| Insights integration | `../tracking_app/pages/insights/` |

---

**Last Updated:** March 2026
