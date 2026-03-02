# 📤 Template Sharing Module

Share and import templates for the Veryfyn Tracking System.

---

## Quick Links

| File | Purpose |
|------|---------|
| [`__init__.py`](__init__.py) | Public API exports |
| [`constants.py`](constants.py) | Template types, categories |
| `helpers.py` | Template sharing logic |
| `session_state.py` | Sharing state |
| `components.py` | UI render functions |

---

## Features

- **Share Templates**: Share your templates publicly
- **Import Templates**: Import community templates
- **Categories**: Browse by category
- **Ratings**: Rate and review templates
- **Favorites**: Save favorite templates

---

## Public API

### Constants

```python
from tracking_app.pages.template_sharing import (
    TEMPLATE_TYPES,      # Template categories
    SHARING_OPTIONS,     # Privacy options
    SORT_OPTIONS,        # Sort preferences
)
```

### Helper Functions

```python
from tracking_app.pages.template_sharing import (
    share_template,      # Share a template
    import_template,     # Import template
    get_popular,         # Get popular templates
)
```

### Components

```python
from tracking_app.pages.template_sharing import (
    render_header,       # Page header
    render_gallery,      # Template gallery
    render_template_card,# Template preview card
    render_import_form,  # Import form
)
```

---

## Usage Example

```python
import streamlit as st
from tracking_app.pages.template_sharing import (
    init_session_state,
    render_header,
    render_gallery,
)

init_session_state()
render_header()
render_gallery()
```

---

## Dependencies

- `streamlit` - UI framework
- `tracking_app.storage` - Template storage
- `json` - Template serialization

---

## Related Pages

- **Habits**: Habit templates
- **Goals**: Goal templates
- **Tasks**: Task templates