"""
Session state management for the Habit Experiments page.

Handles initialization and state management for experiment data.
"""

import streamlit as st
from typing import Any, Optional


def init_session_state() -> None:
    """
    Initialize session state variables for the habit experiments page.
    """
    # Initialize storage
    if 'storage' not in st.session_state:
        from tracking_app.storage import get_storage
        st.session_state.storage = get_storage()
    
    # Initialize user ID
    if 'user_id' not in st.session_state:
        st.session_state.user_id = ""


def get_storage():
    """Get the storage instance from session state."""
    return st.session_state.storage


def get_user_id() -> str:
    """Get the current user ID from session state."""
    return st.session_state.user_id