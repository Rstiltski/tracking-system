# 🎁 Rewards Module

Points, rewards, and redemption system for the Veryfyn Tracking System.

---

## Quick Links

| File | Purpose |
|------|---------|
| [`__init__.py`](__init__.py) | Public API exports |
| [`constants.py`](constants.py) | Reward types, point values |
| [`helpers.py`](helpers.py) | Reward calculations |
| [`session_state.py`](session_state.py) | Rewards state |
| [`components.py`](components.py) | UI render functions |

---

## Features

- **Points System**: Earn points for activities
- **Badges**: Unlock achievement badges
- **Rewards Store**: Redeem points for rewards
- **Streak Bonuses**: Bonus points for streaks
- **Custom Rewards**: Create personal rewards

---

## Public API

### Constants

```python
from tracking_app.pages.rewards import (
    POINT_VALUES,        # Points per activity
    BADGE_TYPES,         # Badge categories
    REWARD_CATALOG,      # Available rewards
)
```

### Helper Functions

```python
from tracking_app.pages.rewards import (
    award_points,        # Award points to user
    check_badges,        # Check for new badges
    redeem_reward,       # Redeem a reward
)
```

### Components

```python
from tracking_app.pages.rewards import (
    render_header,       # Page header
    render_points_display, # Points balance
    render_badges,       # Badge collection
    render_store,        # Rewards store
)
```

---

## Usage Example

```python
import streamlit as st
from tracking_app.pages.rewards import (
    init_session_state,
    render_header,
    render_points_display,
    render_badges,
)

init_session_state()
render_header()
render_points_display()
render_badges()
```

---

## Dependencies

- `streamlit` - UI framework
- `tracking_app.models` - Reward models
- `tracking_app.storage` - Data storage

---

## Related Pages

- **Achievements**: Achievement tracking
- **Challenges**: Challenge rewards
- **Leaderboards**: Points rankings