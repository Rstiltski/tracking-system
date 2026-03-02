# 📈 Insights Module

Analytics and insights generation for the Veryfyn Tracking System.

---

## Quick Links

| File | Purpose |
|------|---------|
| [`__init__.py`](__init__.py) | Public API exports |
| [`constants.py`](constants.py) | Chart types, date ranges |
| [`helpers.py`](helpers.py) | Analytics calculations |
| [`session_state.py`](session_state.py) | Insights state |
| [`components.py`](components.py) | UI render functions |

---

## Features

- **Trend Analysis**: Track trends over time
- **Correlations**: Find patterns in data
- **Predictions**: AI-powered predictions
- **Reports**: Generate insight reports
- **Export**: Export analytics data

---

## Public API

### Constants

```python
from tracking_app.pages.insights import (
    DATE_RANGES,         # Available date ranges
    CHART_TYPES,         # Chart type options
    METRIC_OPTIONS,      # Analyzable metrics
)
```

### Helper Functions

```python
from tracking_app.pages.insights import (
    calculate_trends,    # Calculate trend data
    find_correlations,   # Find data correlations
    generate_insights,   # Generate AI insights
)
```

### Components

```python
from tracking_app.pages.insights import (
    render_header,       # Page header
    render_date_selector,# Date range picker
    render_charts,       # Analytics charts
    render_insights,     # Generated insights
    render_report,       # Full report view
)
```

---

## Usage Example

```python
import streamlit as st
from tracking_app.pages.insights import (
    init_session_state,
    render_header,
    render_date_selector,
    render_charts,
)

init_session_state()
render_header()
render_date_selector()
render_charts()
```

---

## Dependencies

- `streamlit` - UI framework
- `pandas` - Data analysis
- `tracking_app.models` - Data models

---

## Related Pages

- **Dashboard**: Overview summary
- **Weekly Review**: Weekly insights
- **Habit Analytics**: Habit-specific analysis