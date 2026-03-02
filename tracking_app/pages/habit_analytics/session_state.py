"""
Session state management for the Habit Analytics page.

Handles initialization and state management for analytics data.
"""

import streamlit as st
from typing import Any, Optional


def init_session_state() -> None:
    """
    Initialize session state variables for the habit analytics page.
    """
    # Initialize storage
    if 'storage' not in st.session_state:
        from tracking_app.storage import get_storage
        st.session_state.storage = get_storage()
    
    # Initialize user ID
    if 'user_id' not in st.session_state:
        st.session_state.user_id = ""
    
    # Initialize analytics-specific state
    if 'analytics_year' not in st.session_state:
        st.session_state.analytics_year = 2026


def get_storage():
    """Get the storage instance from session state."""
    return st.session_state.storage


def get_user_id() -> str:
    """Get the current user ID from session state."""
    return st.session_state.user_id


def get_analytics_year() -> int:
    """Get the selected analytics year."""
    return st.session_state.get('analytics_year', 2026)


def set_analytics_year(year: int) -> None:
    """Set the analytics year."""
    st.session_state.analytics_year = year