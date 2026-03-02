# 📤 Data Export Module

Data export functionality for the Veryfyn Tracking System.

---

## Quick Links

| File | Purpose |
|------|---------|
| [`__init__.py`](__init__.py) | Public API exports |
| [`constants.py`](constants.py) | Export formats, options |
| [`helpers.py`](helpers.py) | Export generation logic |
| [`session_state.py`](session_state.py) | Export state |
| [`components.py`](components.py) | UI render functions |

---

## Features

- **Multiple Formats**: CSV, JSON, Excel export
- **Selective Export**: Choose specific data types
- **Date Range**: Export by date range
- **Templates**: Export habit/task templates
- **Reports**: Generate export reports

---

## Public API

### Constants

```python
from tracking_app.pages.data_export import (
    EXPORT_FORMATS,      # Supported export formats
    DATA_TYPES,          # Exportable data types
    DATE_RANGE_OPTIONS,  # Date range presets
)
```

### Helper Functions

```python
from tracking_app.pages.data_export import (
    export_to_csv,       # Export data as CSV
    export_to_json,      # Export data as JSON
    export_to_excel,     # Export data as Excel
)
```

### Components

```python
from tracking_app.pages.data_export import (
    render_header,       # Page header
    render_format_selector,# Format selection
    render_data_selector,  # Data type selection
    render_export_button,  # Export trigger
)
```

---

## Usage Example

```python
import streamlit as st
from tracking_app.pages.data_export import (
    init_session_state,
    render_header,
    render_format_selector,
    render_data_selector,
)

init_session_state()
render_header()
render_format_selector()
render_data_selector()
```

---

## Dependencies

- `streamlit` - UI framework
- `pandas` - Data manipulation
- `io` - File handling

---

## Related Pages

- **Data Import**: Import exported data
- **Backup & Restore**: Full backup
- **Data Lifecycle**: Data management