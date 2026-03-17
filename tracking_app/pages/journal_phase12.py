"""
Journal Page - Personal Journaling (Phase 12 Design System)

Streamlit page for creating, editing, and browsing personal journal entries
using the Phase 12 Design System for consistent, accessible, and responsive UI.

Features (Phase 12):
- ✅ Phase 12 design system components (cards, buttons, alerts)
- ✅ Responsive layout that works on mobile, tablet, and desktop
- ✅ Accessibility features (focus indicators, skip links, ARIA labels)
- ✅ Better visual hierarchy with design tokens
- ✅ Loading states and empty states
- ✅ Improved color contrast (WCAG 2.1 AA compliant)
- ✅ Category-based organization with emoji indicators
- ✅ Search and filter functionality
- ✅ Rich text entry forms

Usage:
    streamlit run tracking_app/app.py
    # Navigate to Journal from sidebar
"""

import streamlit as st
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import Phase 12 Design System
from tracking_app.design.theme import apply_design_system, get_current_theme
from tracking_app.design.components import (
    render_page_header,
    render_section_header,
    render_card,
    render_button,
    render_button_group,
    render_alert,
    render_success_alert,
    render_warning_alert,
    render_info_alert,
    render_empty_state,
    render_loading_state,
)
from tracking_app.design.utils import (
    get_responsive_columns,
    render_responsive_container,
    render_focus_styles,
    render_skip_link,
    is_mobile,
    render_spacer,
    render_divider,
)

# Import existing functionality
from tracking_app.storage import get_storage
from tracking_app.components.sidebar import render_sidebar
from tracking_app.components.session import init_session_state

# Import journal components from the journal package
from tracking_app.pages.journal import (
    init_session_state as init_journal_session_state,
    render_header,
    render_add_entry_form,
    render_entry_card,
    render_entry_list,
    render_search,
    render_edit_form,
    JOURNAL_CATEGORIES,
    JOURNAL_CATEGORY_EMOJIS,
)


# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="Journal - Veryfyn",
    page_icon="📓",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply Phase 12 Design System theme
apply_design_system(theme=get_current_theme())

# Render accessibility features
render_focus_styles()


# =============================================================================
# SESSION STATE
# =============================================================================

def init_page_session_state():
    """Initialize page-specific session state."""
    # Initialize journal-specific session state
    init_journal_session_state()


# =============================================================================
# MAIN CONTENT
# =============================================================================

def render_journal_page():
    """Render the main journal page content."""
    # Initialize session state
    init_page_session_state()
    
    # Get storage
    storage = st.session_state.storage
    
    # Render page header with Phase 12 styling
    render_page_header(
        title="📓 Journal",
        subtitle="Your personal space for thoughts, reflections, and ideas",
        icon="📓"
    )
    
    render_divider(height="sm")
    
    # Check if editing an existing entry
    if st.session_state.journal_editing_entry:
        entry = storage.get_journal_entry(st.session_state.journal_editing_entry)
        if entry:
            render_section_header("✏️ Edit Entry")
            render_edit_form(storage, entry)
            return
        st.session_state.journal_editing_entry = None
    
    # Render search and filter
    query, category = render_search(storage)
    
    render_divider(height="sm")
    
    # Add new entry section
    with st.expander("✨ Add New Entry", expanded=False):
        render_add_entry_form(storage)
    
    render_divider(height="sm")
    
    # Get entries based on search/filter
    if query:
        entries = storage.search_journal_entries(query)
        if entries:
            render_info_alert(f"Found {len(entries)} entries matching '{query}'")
    elif category:
        entries = storage.get_journal_entries(category=category)
        if entries:
            render_info_alert(f"Showing {len(entries)} entries in {JOURNAL_CATEGORY_EMOJIS.get(category, '📝')} {category}")
    else:
        entries = storage.get_journal_entries()
    
    # Render entries
    if entries:
        render_entry_list(storage, entries)
    else:
        render_empty_state(
            icon="📝",
            title="No journal entries yet",
            message="Start writing your first entry to capture your thoughts and reflections.",
            action_label="Create First Entry",
            action_expander=True
        )


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def main():
    """Main entry point for the Journal page."""
    # Render sidebar
    render_sidebar()
    
    # Render main content
    render_journal_page()


if __name__ == "__main__":
    main()
