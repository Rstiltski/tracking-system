"""
Diary Page - Private Diary/Journal

Streamlit page for personal diary entries with mood tracking,
tags, and calendar view.

Usage:
    streamlit run tracking_app/pages/diary.py

Features:
- Private diary entries with Markdown support
- Mood tracking with emoji indicators
- Tag system for organization
- Calendar view for browsing entries
- Search functionality
- Writing prompts for inspiration
"""
import streamlit as st
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tracking_app.storage import get_storage
from tracking_app.components.sidebar import render_sidebar

# Import all components from the diary package
from tracking_app.pages.diary import (
    # Session state
    init_session_state,
    # Components
    render_header,
    render_add_entry_form,
    render_entry_list,
    render_calendar_view,
    render_search,
    render_edit_form,
)


# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="Diary - Veryfyn",
    page_icon="📔",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =============================================================================
# MAIN FUNCTION
# =============================================================================

def main():
    """Main page entry point."""
    # Initialize session state
    init_session_state()
    
    # Render sidebar
    render_sidebar()
    
    # Main content
    render_header()
    st.divider()
    
    # Get storage instance
    storage = st.session_state.storage
    
    # Check if editing an entry
    if st.session_state.diary_editing_entry:
        entry = storage.get_diary_entry(st.session_state.diary_editing_entry)
        if entry:
            render_edit_form(storage, entry)
            return
        else:
            st.session_state.diary_editing_entry = None
    
    # Search and filter
    search_query, mood_filter = render_search(storage)
    st.divider()
    
    # Get entries based on search/filter
    if search_query:
        entries = storage.search_diary_entries(search_query)
    elif mood_filter:
        entries = storage.get_diary_entries(mood=mood_filter)
    else:
        entries = storage.get_diary_entries()
    
    # View mode tabs
    tab_list, tab_calendar = st.tabs(["📝 Entries", "📅 Calendar"])
    
    with tab_list:
        # Add entry form (collapsible)
        with st.expander("✨ Add New Entry", expanded=False):
            render_add_entry_form(storage)
        
        st.divider()
        
        # Entry list
        render_entry_list(storage, entries)
    
    with tab_calendar:
        # Calendar view
        render_calendar_view(
            storage,
            st.session_state.diary_calendar_year,
            st.session_state.diary_calendar_month
        )


if __name__ == "__main__":
    main()