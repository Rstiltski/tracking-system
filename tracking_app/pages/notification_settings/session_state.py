"""
Session state management for the Notification Settings page.
"""

import streamlit as st
from typing import Optional, Any

from brain.notifications.preferences import get_preference_manager

from .constants import DEFAULT_USER_ID


def init_session_state() -> None:
    """
    Initialize session state variables for the notification settings page.
    """
    # Initialize user ID
    if 'user_id' not in st.session_state:
        st.session_state.user_id = DEFAULT_USER_ID
    
    # Initialize preference manager
    if 'preference_manager' not in st.session_state:
        st.session_state.preference_manager = get_preference_manager()


def get_user_id() -> str:
    """Get the current user ID from session state."""
    return st.session_state.user_id


def get_preference_manager():
    """Get the preference manager from session state."""
    return st.session_state.preference_manager


def get_current_preferences():
    """Get current user preferences."""
    pm = get_preference_manager()
    user_id = get_user_id()
    return pm.get_user_preferences(user_id)