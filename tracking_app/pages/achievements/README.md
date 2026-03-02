# 🏆 Achievements Module

Gamification and achievement system for the Veryfyn Tracking System.

---

## Quick Links

| File | Purpose |
|------|---------|
| [`__init__.py`](__init__.py) | Public API exports |
| [`constants.py`](constants.py) | Achievement definitions, tiers |
| [`helpers.py`](helpers.py) | Achievement unlocking logic |
| [`session_state.py`](session_state.py) | Achievement state |
| [`components.py`](components.py) | UI render functions |

---

## Features

- **Achievement System**: Unlock achievements for milestones
- **Tiers**: Bronze, silver, gold, platinum levels
- **Points**: Earn points for achievements
- **Progress Tracking**: Track progress toward achievements
- **Badges**: Visual badge display

---

## Public API

### Constants

```python
from tracking_app.pages.achievements import (
    ACHIEVEMENT_DEFINITIONS,  # All achievement definitions
    TIER_COLORS,              # Colors for each tier
    TIER_POINTS,              # Points per tier
)
```

### Helper Functions

```python
from tracking_app.pages.achievements import (
    check_achievements,       # Check for newly unlocked
    get_achievement_progress, # Get progress percentage
    calculate_total_points,   # Sum of achievement points
)
```

### Components

```python
from tracking_app.pages.achievements import (
    render_header,            # Page header
    render_achievement_grid,  # Achievement badges grid
    render_achievement_detail,# Single achievement detail
    render_progress_summary,  # Points and progress
)
```

---

## Usage Example

```python
import streamlit as st
from tracking_app.pages.achievements import (
    init_session_state,
    render_header,
    render_achievement_grid,
    render_progress_summary,
)

init_session_state()
render_header()
render_progress_summary()
render_achievement_grid()
```

---

## Dependencies

- `streamlit` - UI framework
- `tracking_app.models` - Achievement model

---

## Related Pages

- **Rewards**: Variable reward system
- **Challenges**: Challenge achievements
- **Leaderboards**: Compare achievements