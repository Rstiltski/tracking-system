# 🏥 Health Module

Health metrics and wellness tracking for the Veryfyn Tracking System.

---

## Quick Links

| File | Purpose |
|------|---------|
| [`__init__.py`](__init__.py) | Public API exports |
| [`constants.py`](constants.py) | Mood options, health metrics |
| [`helpers.py`](helpers.py) | Health score calculations |
| [`session_state.py`](session_state.py) | Health tracking state |
| [`components.py`](components.py) | UI render functions |

---

## Features

- **Health Metrics**: Track weight, sleep, water intake
- **Mood Tracking**: Daily mood logging
- **Health Score**: Calculated wellness score
- **Trends View**: Visualize health trends over time
- **Goal Setting**: Set health-related goals

---

## Public API

### Constants

```python
from tracking_app.pages.health import (
    MOOD_OPTIONS,       # Mood selection options
    HEALTH_METRICS,     # Trackable health metrics
    SLEEP_QUALITY,      # Sleep quality options
)
```

### Helper Functions

```python
from tracking_app.pages.health import (
    calculate_health_score,  # Calculate overall health score
    get_trend_data,          # Get trend data for metrics
    format_metric_value,     # Format metric for display
)
```

### Components

```python
from tracking_app.pages.health import (
    render_header,           # Page header
    render_health_metrics,   # Health metrics input
    render_mood_tracker,     # Mood tracking UI
    render_trends,           # Trends visualization
    render_health_score,     # Health score display
)
```

---

## Usage Example

```python
import streamlit as st
from tracking_app.pages.health import (
    init_session_state,
    render_header,
    render_health_metrics,
    render_mood_tracker,
)

init_session_state()
render_header()
render_health_metrics()
render_mood_tracker()
```

---

## Dependencies

- `streamlit` - UI framework
- `datetime` - Date handling
- `tracking_app.models` - HealthEntry model

---

## Related Pages

- **Emotional Health**: Detailed emotion tracking
- **Insights**: Health analytics
- **Goals**: Health goals

---

## Cross-References

| Topic | File |
|-------|------|
| AI entry point | `../AI_START_HERE.md` |
| Project overview | `../README.md` |
| Backend architecture | `../brain/README.md` |
| Page module pattern | `../patterns/page_module.md` |
| Health implementation | `../tracking_app/pages/health.py` |
| Health models | `../brain/models/` |
| Emotional health | `../tracking_app/pages/emotional_health/` |

---

**Last Updated:** March 2026
