# 🏆 Leaderboards Module

Rankings and leaderboards for the Veryfyn Tracking System.

---

## Quick Links

| File | Purpose |
|------|---------|
| [`__init__.py`](__init__.py) | Public API exports |
| [`constants.py`](constants.py) | Leaderboard types, periods |
| [`helpers.py`](helpers.py) | Ranking calculations |
| [`session_state.py`](session_state.py) | Leaderboards state |
| [`components.py`](components.py) | UI render functions |

---

## Features

- **Global Rankings**: Compare with all users
- **Friends Rankings**: Compare with friends
- **Category Boards**: Category-specific rankings
- **Time Periods**: Daily, weekly, monthly boards
- **Achievements**: Achievement-based rankings

---

## Public API

### Constants

```python
from tracking_app.pages.leaderboards import (
    LEADERBOARD_TYPES,   # Leaderboard categories
    TIME_PERIODS,        # Ranking periods
    RANKING_METRICS,     # What's being ranked
)
```

### Helper Functions

```python
from tracking_app.pages.leaderboards import (
    calculate_rankings,  # Calculate rankings
    get_user_rank,       # Get user's rank
    get_top_users,       # Get top N users
)
```

### Components

```python
from tracking_app.pages.leaderboards import (
    render_header,       # Page header
    render_leaderboard,  # Leaderboard table
    render_filter_bar,   # Filter controls
    render_user_rank,    # User's rank display
)
```

---

## Usage Example

```python
import streamlit as st
from tracking_app.pages.leaderboards import (
    init_session_state,
    render_header,
    render_filter_bar,
    render_leaderboard,
)

init_session_state()
render_header()
render_filter_bar()
render_leaderboard()
```

---

## Dependencies

- `streamlit` - UI framework
- `pandas` - Data handling
- `tracking_app.models` - User models

---

## Related Pages

- **Friends**: Friend management
- **Challenges**: Challenge rankings
- **Rewards**: Points and rewards

---

## Cross-References

| Topic | File |
|-------|------|
| AI entry point | `../AI_START_HERE.md` |
| Project overview | `../README.md` |
| Backend architecture | `../brain/README.md` |
| Page module pattern | `../patterns/page_module.md` |
| Leaderboard implementation | `../tracking_app/pages/leaderboards.py` |
| User models | `../brain/models/` |
| Challenge integration | `../tracking_app/pages/challenges/` |

---

**Last Updated:** March 2026
