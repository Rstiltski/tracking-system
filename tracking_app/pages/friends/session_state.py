"""
Session state management for the Friends page.

Handles initialization and management of Streamlit session state variables.
"""

import streamlit as st

from .constants import DEFAULT_USER_ID


def init_session_state():
    """Initialize session state variables for the Friends page."""
    if 'storage' not in st.session_state:
        from tracking_app.storage import get_storage
        st.session_state.storage = get_storage()
    
    if 'user_id' not in st.session_state:
        st.session_state.user_id = DEFAULT_USER_ID