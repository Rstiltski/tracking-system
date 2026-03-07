# 📥 Data Import Module

Data import functionality for the Veryfyn Tracking System.

---

## Quick Links

| File | Purpose |
|------|---------|
| [`__init__.py`](__init__.py) | Public API exports |
| [`constants.py`](constants.py) | Import formats, options |
| [`helpers.py`](helpers.py) | Import parsing logic |
| [`session_state.py`](session_state.py) | Import state |
| [`components.py`](components.py) | UI render functions |

---

## Features

- **Multiple Formats**: CSV, JSON, Excel import
- **Validation**: Data validation before import
- **Mapping**: Field mapping for imports
- **Preview**: Preview data before importing
- **Conflict Resolution**: Handle duplicate data

---

## Public API

### Constants

```python
from tracking_app.pages.data_import import (
    IMPORT_FORMATS,      # Supported import formats
    FIELD_MAPPINGS,      # Default field mappings
    CONFLICT_OPTIONS,    # Conflict resolution options
)
```

### Helper Functions

```python
from tracking_app.pages.data_import import (
    parse_csv,           # Parse CSV file
    parse_json,          # Parse JSON file
    validate_import_data,# Validate imported data
)
```

### Components

```python
from tracking_app.pages.data_import import (
    render_header,       # Page header
    render_file_upload,  # File upload widget
    render_field_mapping,# Field mapping UI
    render_preview,      # Data preview
    render_import_button,# Import trigger
)
```

---

## Usage Example

```python
import streamlit as st
from tracking_app.pages.data_import import (
    init_session_state,
    render_header,
    render_file_upload,
    render_preview,
)

init_session_state()
render_header()
render_file_upload()
render_preview()
```

---

## Dependencies

- `streamlit` - UI framework
- `pandas` - Data manipulation
- `io` - File handling

---

## Related Pages

- **Data Export**: Export data
- **Backup & Restore**: Full restore
- **Data Lifecycle**: Data management

---

## Cross-References

| Topic | File |
|-------|------|
| AI entry point | `../AI_START_HERE.md` |
| Project overview | `../README.md` |
| Backend architecture | `../brain/README.md` |
| Page module pattern | `../patterns/page_module.md` |
| Data import implementation | `../tracking_app/pages/data_import.py` |
| Data models | `../brain/models/` |
| Export integration | `../tracking_app/pages/data_export/` |

---

**Last Updated:** March 2026
