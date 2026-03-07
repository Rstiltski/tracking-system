# 💭 Emotional Health Module

Emotional health tracking and mood management for the Veryfyn Tracking System.

---

## Quick Links

| File | Purpose |
|------|---------|
| [`__init__.py`](__init__.py) | Public API exports |
| [`constants.py`](constants.py) | Mood types, emotions |
| [`helpers.py`](helpers.py) | Mood analysis logic |
| [`session_state.py`](session_state.py) | Emotional state |
| [`components.py`](components.py) | UI render functions |

---

## Features

- **Mood Tracking**: Log daily moods
- **Emotion Journal**: Record emotions with context
- **Patterns**: Identify emotional patterns
- **Triggers**: Track emotional triggers
- **Insights**: Mood trend analysis

---

## Public API

### Constants

```python
from tracking_app.pages.emotional_health import (
    MOOD_TYPES,          # Available mood types
    EMOTION_CATEGORIES,  # Emotion categories
    INTENSITY_LEVELS,    # Intensity scale
)
```

### Helper Functions

```python
from tracking_app.pages.emotional_health import (
    log_mood,            # Log a mood entry
    analyze_patterns,    # Analyze mood patterns
    get_mood_trends,     # Get mood trends
)
```

### Components

```python
from tracking_app.pages.emotional_health import (
    render_header,       # Page header
    render_mood_picker,  # Mood selection UI
    render_journal_form, # Journal entry form
    render_mood_chart,   # Mood visualization
)
```

---

## Usage Example

```python
import streamlit as st
from tracking_app.pages.emotional_health import (
    init_session_state,
    render_header,
    render_mood_picker,
    render_mood_chart,
)

init_session_state()
render_header()
render_mood_picker()
render_mood_chart()
```

---

## Dependencies

- `streamlit` - UI framework
- `datetime` - Date handling
- `plotly` - Chart visualization

---

## Related Pages

- **Health**: Physical health tracking
- **Insights**: Mood trend analysis
- **Weekly Review**: Weekly mood summary

---

## Cross-References

| Topic | File |
|-------|------|
| AI entry point | `../AI_START_HERE.md` |
| Project overview | `../README.md` |
| Backend architecture | `../brain/README.md` |
| Page module pattern | `../patterns/page_module.md` |
| Emotional health implementation | `../tracking_app/pages/emotional_health.py` |
| Emotional models | `../brain/models/` |
| Health integration | `../tracking_app/pages/health/` |

---

**Last Updated:** March 2026
