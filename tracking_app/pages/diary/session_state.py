"""
Session state management for the Diary page.

Initializes and manages session state variables for diary functionality.
"""

import streamlit as st
from datetime import date


def init_session_state():
    """Initialize diary page session state variables."""
    # View mode
    if 'diary_view_mode' not in st.session_state:
        st.session_state.diary_view_mode = 'list'  # 'list' or 'calendar'

    # Selected date for viewing/adding entries
    if 'diary_selected_date' not in st.session_state:
        st.session_state.diary_selected_date = date.today()

    # Editing state
    if 'diary_editing_entry' not in st.session_state:
        st.session_state.diary_editing_entry = None

    # Show add form
    if 'diary_show_add_form' not in st.session_state:
        st.session_state.diary_show_add_form = False

    # Search query
    if 'diary_search_query' not in st.session_state:
        st.session_state.diary_search_query = ""

    # Filter mood
    if 'diary_filter_mood' not in st.session_state:
        st.session_state.diary_filter_mood = None

    # Calendar month view
    if 'diary_calendar_month' not in st.session_state:
        st.session_state.diary_calendar_month = date.today().month
        st.session_state.diary_calendar_year = date.today().year