# 🏅 Challenges Module

Challenge system for gamified goal achievement in the Veryfyn Tracking System.

---

## Quick Links

| File | Purpose |
|------|---------|
| [`__init__.py`](__init__.py) | Public API exports |
| [`constants.py`](constants.py) | Challenge types, rewards |
| [`helpers.py`](helpers.py) | Challenge progress logic |
| [`session_state.py`](session_state.py) | Challenge state |
| [`components.py`](components.py) | UI render functions |

---

## Features

- **Active Challenges**: Join and track challenges
- **Challenge Types**: Daily, weekly, monthly challenges
- **Progress Tracking**: Track challenge completion
- **Rewards**: Earn points and badges
- **Leaderboards**: Compare with others

---

## Public API

### Constants

```python
from tracking_app.pages.challenges import (
    CHALLENGE_TYPES,     # Challenge type options
    DIFFICULTY_LEVELS,   # Difficulty options
    REWARD_POINTS,       # Points per difficulty
)
```

### Helper Functions

```python
from tracking_app.pages.challenges import (
    calculate_progress,   # Calculate challenge progress
    check_completion,     # Check if challenge complete
    get_active_challenges,# Get user's active challenges
)
```

### Components

```python
from tracking_app.pages.challenges import (
    render_header,        # Page header
    render_challenge_list,# Active challenges list
    render_challenge_card,# Single challenge card
    render_join_form,     # Join challenge form
    render_progress,      # Progress display
)
```

---

## Usage Example

```python
import streamlit as st
from tracking_app.pages.challenges import (
    init_session_state,
    render_header,
    render_challenge_list,
    render_join_form,
)

init_session_state()
render_header()
render_challenge_list()
render_join_form()
```

---

## Dependencies

- `streamlit` - UI framework
- `datetime` - Date handling
- `tracking_app.models` - Challenge model

---

## Related Pages

- **Achievements**: Challenge achievements
- **Rewards**: Challenge rewards
- **Leaderboards**: Challenge rankings