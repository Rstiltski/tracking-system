# 🔄 Data Lifecycle Module

Data lifecycle management for the Veryfyn Tracking System.

---

## Quick Links

| File | Purpose |
|------|---------|
| [`__init__.py`](__init__.py) | Public API exports |
| [`constants.py`](constants.py) | Lifecycle stages, options |
| [`helpers.py`](helpers.py) | Lifecycle operations |
| [`session_state.py`](session_state.py) | Lifecycle state |
| [`components.py`](components.py) | UI render functions |

---

## Features

- **Archive**: Archive old data
- **Purge**: Delete outdated data
- **Retention**: Set retention policies
- **Cleanup**: Automated cleanup
- **Restore**: Restore archived data

---

## Public API

### Constants

```python
from tracking_app.pages.data_lifecycle import (
    LIFECYCLE_STAGES,    # Data lifecycle stages
    RETENTION_PERIODS,   # Retention time options
    ARCHIVE_OPTIONS,     # Archive settings
)
```

### Helper Functions

```python
from tracking_app.pages.data_lifecycle import (
    archive_data,        # Archive old data
    purge_data,          # Delete old data
    get_lifecycle_status,# Get data lifecycle status
)
```

### Components

```python
from tracking_app.pages.data_lifecycle import (
    render_header,       # Page header
    render_retention_settings, # Retention policy UI
    render_archive_view, # Archived data view
    render_cleanup_form, # Cleanup form
)
```

---

## Usage Example

```python
import streamlit as st
from tracking_app.pages.data_lifecycle import (
    init_session_state,
    render_header,
    render_retention_settings,
    render_archive_view,
)

init_session_state()
render_header()
render_retention_settings()
render_archive_view()
```

---

## Dependencies

- `streamlit` - UI framework
- `datetime` - Date handling
- `tracking_app.storage` - Data storage

---

## Related Pages

- **Data Export**: Export data before cleanup
- **Data Import**: Import archived data
- **Backup & Restore**: Full backup

---

## Cross-References

| Topic | File |
|-------|------|
| AI entry point | `../AI_START_HERE.md` |
| Project overview | `../README.md` |
| Backend architecture | `../brain/README.md` |
| Page module pattern | `../patterns/page_module.md` |
| Data lifecycle implementation | `../tracking_app/pages/data_lifecycle.py` |
| Storage models | `../brain/models/` |
| Export integration | `../tracking_app/pages/data_export/` |

---

**Last Updated:** March 2026
