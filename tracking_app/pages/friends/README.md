# 👥 Friends Module

Social features and friend management for the Veryfyn Tracking System.

---

## Quick Links

| File | Purpose |
|------|---------|
| [`__init__.py`](__init__.py) | Public API exports |
| [`constants.py`](constants.py) | Friend status, types |
| [`helpers.py`](helpers.py) | Friend operations |
| [`session_state.py`](session_state.py) | Friends state |
| [`components.py`](components.py) | UI render functions |

---

## Features

- **Add Friends**: Send and accept friend requests
- **Activity Feed**: See friends' progress
- **Sharing**: Share goals and achievements
- **Comparisons**: Compare progress with friends
- **Accountability**: Accountability partnerships

---

## Public API

### Constants

```python
from tracking_app.pages.friends import (
    FRIEND_STATUS,       # Friend status options
    PRIVACY_LEVELS,      # Sharing privacy levels
    ACTIVITY_TYPES,      # Activity feed types
)
```

### Helper Functions

```python
from tracking_app.pages.friends import (
    send_request,        # Send friend request
    accept_request,      # Accept friend request
    get_activity_feed,   # Get friends' activities
)
```

### Components

```python
from tracking_app.pages.friends import (
    render_header,       # Page header
    render_friends_list, # Friends list view
    render_requests,     # Friend requests
    render_activity_feed,# Activity feed
)
```

---

## Usage Example

```python
import streamlit as st
from tracking_app.pages.friends import (
    init_session_state,
    render_header,
    render_friends_list,
    render_activity_feed,
)

init_session_state()
render_header()
render_friends_list()
render_activity_feed()
```

---

## Dependencies

- `streamlit` - UI framework
- `tracking_app.models` - User models
- `tracking_app.storage` - Data storage

---

## Related Pages

- **Leaderboards**: Compare rankings
- **Challenges**: Challenge friends
- **Achievements**: Share achievements

---

## Cross-References

| Topic | File |
|-------|------|
| AI entry point | `../AI_START_HERE.md` |
| Project overview | `../README.md` |
| Backend architecture | `../brain/README.md` |
| Page module pattern | `../patterns/page_module.md` |
| Friends implementation | `../tracking_app/pages/friends.py` |
| User models | `../brain/models/` |
| Leaderboard integration | `../tracking_app/pages/leaderboards/` |

---

**Last Updated:** March 2026
