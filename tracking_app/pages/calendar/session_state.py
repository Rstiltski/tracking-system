"""
Session state management for the Calendar page.

Handles initialization and management of Streamlit session state variables.
"""

import streamlit as st
from datetime import date
from typing import Optional


def init_session_state():
    """
    Initialize session state variables for the Calendar page.
    
    Sets up:
    - calendar_view_date: Current month being viewed
    - selected_date: Currently selected date (or None)
    - show_day_detail: Whether to show day detail modal
    """
    if 'calendar_view_date' not in st.session_state:
        st.session_state.calendar_view_date = date.today()
    
    if 'calendar_selected_date' not in st.session_state:
        st.session_state.calendar_selected_date = None
    
    if 'calendar_show_detail' not in st.session_state:
        st.session_state.calendar_show_detail = False


def get_view_date() -> date:
    """Get current calendar view date."""
    return st.session_state.get('calendar_view_date', date.today())


def set_view_date(view_date: date) -> None:
    """Set calendar view date."""
    st.session_state.calendar_view_date = view_date


def get_selected_date() -> Optional[date]:
    """Get currently selected date."""
    return st.session_state.get('calendar_selected_date')


def set_selected_date(selected_date: Optional[date]) -> None:
    """Set selected date."""
    st.session_state.calendar_selected_date = selected_date
    st.session_state.calendar_show_detail = selected_date is not None


def clear_selected_date() -> None:
    """Clear selected date."""
    st.session_state.calendar_selected_date = None
    st.session_state.calendar_show_detail = False
