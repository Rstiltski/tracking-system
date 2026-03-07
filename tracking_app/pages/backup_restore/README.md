# 💾 Backup & Restore Module

Data backup and restoration for the Veryfyn Tracking System.

---

## Quick Links

| File | Purpose |
|------|---------|
| [`__init__.py`](__init__.py) | Public API exports |
| [`constants.py`](constants.py) | Backup formats, paths |
| [`helpers.py`](helpers.py) | Backup creation logic |
| [`session_state.py`](session_state.py) | Backup state |
| [`components.py`](components.py) | UI render functions |

---

## Features

- **Full Backup**: Backup all data
- **Selective Backup**: Choose what to backup
- **Restore**: Restore from backup file
- **Schedule**: Automatic backup scheduling
- **Cloud Sync**: Optional cloud backup

---

## Public API

### Constants

```python
from tracking_app.pages.backup_restore import (
    BACKUP_FORMATS,      # Supported formats
    BACKUP_PATHS,        # Default backup locations
    SCHEDULE_OPTIONS,    # Schedule frequencies
)
```

### Helper Functions

```python
from tracking_app.pages.backup_restore import (
    create_backup,       # Create backup file
    restore_backup,      # Restore from backup
    validate_backup,     # Validate backup file
)
```

### Components

```python
from tracking_app.pages.backup_restore import (
    render_header,       # Page header
    render_backup_form,  # Backup creation form
    render_restore_form, # Restore form
    render_history,      # Backup history
)
```

---

## Usage Example

```python
import streamlit as st
from tracking_app.pages.backup_restore import (
    init_session_state,
    render_header,
    render_backup_form,
    render_restore_form,
)

init_session_state()
render_header()
render_backup_form()
render_restore_form()
```

---

## Dependencies

- `streamlit` - UI framework
- `json` - Data serialization
- `datetime` - Timestamp handling
- `tracking_app.storage` - Data storage

---

## Related Pages

- **Data Export**: Export specific data
- **Data Import**: Import data
- **Data Lifecycle**: Data management

---

## Cross-References

| Topic | File |
|-------|------|
| AI entry point | `../AI_START_HERE.md` |
| Project overview | `../README.md` |
| Backend architecture | `../brain/README.md` |
| Page module pattern | `../patterns/page_module.md` |
| Security protocols | `../brain/SECURITY_PLAYBOOK.md` |
| Backup & restore implementation | `../tracking_app/pages/backup_restore.py` |
| Storage models | `../brain/models/` |
| Data export integration | `../tracking_app/pages/data_export/` |

---

**Last Updated:** March 2026
