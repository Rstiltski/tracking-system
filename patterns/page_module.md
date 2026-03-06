# Page Module Pattern

**Standard structure for Streamlit pages in the Veryfyn Tracking System.**

---

## Context

Use this pattern when creating a new Streamlit page in `tracking_app/pages/`. This pattern ensures consistency with existing pages (like diary, journal) and follows project rules.

---

## Structure

A page module consists of:

```
tracking_app/pages/page_name/
├── __init__.py         # Module exports
├── constants.py        # Page constants
├── helpers.py          # Helper functions
├── session_state.py    # Session state management
└── components.py       # UI components
```

Plus a main page file:
```
tracking_app/pages/page_name.py  # Main entry point
```

---

## Implementation

### 1. `__init__.py`

```python
"""
page_name module - Brief description.

Detailed description of what this page does.
"""

from .constants import *
from .helpers import *
from .session_state import *
from .components import *

__all__ = [
    # Export key functions/classes
]
```

### 2. `constants.py`

```python
"""
Constants for page_name.
"""

# Page configuration
PAGE_TITLE = "Page Name"
PAGE_ICON = "📋"

# Default values
DEFAULT_VALUE = "default"

# Options for selects
CATEGORY_OPTIONS = ["Option 1", "Option 2", "Option 3"]

# Messages
SUCCESS_MESSAGE = "Operation completed successfully."
ERROR_MESSAGE = "An error occurred."
```

### 3. `helpers.py`

```python
"""
Helper functions for page_name.
"""

from typing import List, Dict, Any, Optional
from datetime import datetime, date

def format_data(data: Any) -> str:
    """Format data for display."""
    pass

def validate_input(value: str) -> bool:
    """Validate user input."""
    return len(value.strip()) > 0

def process_data(raw_data: Dict) -> Dict:
    """Process raw data for storage."""
    return {
        "id": raw_data.get("id"),
        "processed_at": datetime.now().isoformat()
    }
```

### 4. `session_state.py`

```python
"""
Session state management for page_name.
"""

import streamlit as st
from typing import Optional, List, Dict, Any

def init_session_state() -> None:
    """Initialize session state variables for this page."""
    if "page_name_items" not in st.session_state:
        st.session_state.page_name_items = []
    
    if "page_name_selected" not in st.session_state:
        st.session_state.page_name_selected = None
    
    if "page_name_editing" not in st.session_state:
        st.session_state.page_name_editing = False

def get_items() -> List[Dict]:
    """Get items from session state."""
    return st.session_state.get("page_name_items", [])

def set_items(items: List[Dict]) -> None:
    """Set items in session state."""
    st.session_state.page_name_items = items

def clear_selection() -> None:
    """Clear current selection."""
    st.session_state.page_name_selected = None
    st.session_state.page_name_editing = False
```

### 5. `components.py`

```python
"""
UI components for page_name.
"""

import streamlit as st
from typing import List, Dict, Any, Optional, Callable

def render_header() -> None:
    """Render page header."""
    st.title("📋 Page Name")
    st.markdown("Brief description of this page.")

def render_item_card(item: Dict, on_edit: Callable, on_delete: Callable) -> None:
    """Render a single item card."""
    with st.container():
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            st.write(f"**{item.get('name', 'Unnamed')}**")
        
        with col2:
            if st.button("✏️", key=f"edit_{item['id']}"):
                on_edit(item['id'])
        
        with col3:
            if st.button("🗑️", key=f"delete_{item['id']}"):
                on_delete(item['id'])

def render_form(on_submit: Callable) -> None:
    """Render the add/edit form."""
    with st.form("page_name_form"):
        name = st.text_input("Name")
        category = st.selectbox("Category", ["Option 1", "Option 2"])
        
        submitted = st.form_submit_button("Submit")
        
        if submitted and name:
            on_submit({"name": name, "category": category})

def render_empty_state() -> None:
    """Render empty state message."""
    st.info("No items yet. Add your first item above!")

def render_metrics(items: List[Dict]) -> None:
    """Render page metrics."""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Total Items", len(items))
    
    with col2:
        active = len([i for i in items if i.get("active", True)])
        st.metric("Active", active)
    
    with col3:
        st.metric("Inactive", len(items) - active)
```

### 6. Main Page File (`page_name.py`)

```python
"""
pages/page_name.py - Page Description

Streamlit page for [functionality].
"""

import streamlit as st
from typing import Optional

# Import from module
from tracking_app.pages.page_name.constants import PAGE_TITLE, PAGE_ICON
from tracking_app.pages.page_name.session_state import (
    init_session_state,
    get_items,
    set_items,
    clear_selection
)
from tracking_app.pages.page_name.components import (
    render_header,
    render_item_card,
    render_form,
    render_empty_state,
    render_metrics
)
from tracking_app.pages.page_name.helpers import validate_input, process_data
from tracking_app.storage import Storage

def handle_add(data: dict) -> None:
    """Handle adding a new item."""
    if validate_input(data.get("name", "")):
        storage = Storage()
        # storage.add_item(data)
        st.success("Item added successfully!")
        st.rerun()

def handle_edit(item_id: str) -> None:
    """Handle editing an item."""
    st.session_state.page_name_selected = item_id
    st.session_state.page_name_editing = True

def handle_delete(item_id: str) -> None:
    """Handle deleting an item."""
    storage = Storage()
    # storage.delete_item(item_id)
    st.success("Item deleted successfully!")
    st.rerun()

def main() -> None:
    """Main page entry point."""
    # Set page config
    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon=PAGE_ICON,
        layout="wide"
    )
    
    # Initialize session state
    init_session_state()
    
    # Render header
    render_header()
    
    # Get data
    items = get_items()
    
    # Render metrics
    render_metrics(items)
    
    # Render form
    render_form(handle_add)
    
    # Render items or empty state
    if items:
        for item in items:
            render_item_card(item, handle_edit, handle_delete)
    else:
        render_empty_state()

if __name__ == "__main__":
    main()
```

---

## Rules Enforced

| Rule ID | Description |
|---------|-------------|
| LANG_001 | Python-First - Page must be Python/Streamlit |
| LANG_003 | Use Type Hints - All functions have type annotations |
| MOD_001 | Single-Page Modification - One page per task |
| DOC_002 | Docstrings - All functions documented |

---

## Example Implementations

### Real Examples in Project:
- `tracking_app/pages/diary/` - Diary page module
- `tracking_app/pages/journal/` - Journal page module
- `tracking_app/pages/habits/` - Habits page (legacy)

---

## Related Patterns

- [Form Component](./form_component.md) - For complex forms
- [Card Component](./card_component.md) - For item displays

---

## Checklist

When creating a new page, verify:

- [ ] Created module directory structure
- [ ] Created `__init__.py` with exports
- [ ] Created `constants.py` with page constants
- [ ] Created `helpers.py` with helper functions
- [ ] Created `session_state.py` with state management
- [ ] Created `components.py` with UI components
- [ ] Created main page file
- [ ] All functions have type hints
- [ ] All functions have docstrings
- [ ] Session state initialized properly
- [ ] Form validation implemented
- [ ] Empty state handled

---

**Last Updated:** March 2026  
**Version:** 1.0.0