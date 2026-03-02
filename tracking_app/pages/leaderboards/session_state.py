"""
Session state management for the Leaderboards page.

Handles initialization and state management.
"""

import streamlit as st
from typing import Any, Optional


def init_session_state() -> None:
    """
    Initialize session state variables for the leaderboards page.
    """
    # Initialize storage
    if 'storage' not in st.session_state:
        from tracking_app.storage import get_storage
        st.session_state.storage = get_storage()
    
    # Initialize user ID
    if 'user_id' not in st.session_state:
        st.session_state.user_id = "user-123"  # Demo user ID


def get_storage():
    """Get the storage instance from session state."""
    return st.session_state.storage


def get_user_id() -> str:
    """Get the current user ID from session state."""
    return st.session_state.user_id