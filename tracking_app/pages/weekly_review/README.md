# 📋 Weekly Review Module

Weekly progress review and reflection for the Veryfyn Tracking System.

---

## Quick Links

| File | Purpose |
|------|---------|
| [`__init__.py`](__init__.py) | Public API exports |
| `constants.py` | Review sections, prompts |
| [`helpers.py`](helpers.py) | Review calculations |
| [`session_state.py`](session_state.py) | Review state |
| [`components.py`](components.py) | UI render functions |

---

## Features

- **Progress Summary**: Weekly progress overview
- **Habit Review**: Habit performance analysis
- **Goal Check-in**: Goal progress review
- **Reflection Prompts**: Guided reflection questions
- **Weekly Goals**: Set goals for next week

---

## Public API

### Constants

```python
from tracking_app.pages.weekly_review import (
    REVIEW_SECTIONS,     # Review categories
    REFLECTION_PROMPTS,  # Guided questions
    RATING_SCALE,        # Self-rating options
)
```

### Helper Functions

```python
from tracking_app.pages.weekly_review import (
    generate_review,     # Generate weekly review
    calculate_score,     # Calculate weekly score
    save_review,         # Save review to storage
)
```

### Components

```python
from tracking_app.pages.weekly_review import (
    render_header,       # Page header
    render_summary,      # Progress summary
    render_reflection,   # Reflection section
    render_next_week,    # Next week planning
)
```

---

## Usage Example

```python
import streamlit as st
from tracking_app.pages.weekly_review import (
    init_session_state,
    render_header,
    render_summary,
    render_reflection,
)

init_session_state()
render_header()
render_summary()
render_reflection()
```

---

## Dependencies

- `streamlit` - UI framework
- `tracking_app.models` - Review model
- `tracking_app.storage` - Data storage

---

## Related Pages

- **Insights**: Long-term insights
- **Habits**: Habit tracking
- **Goals**: Goal management