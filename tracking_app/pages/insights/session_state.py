"""
Session state management for the Insights page.

Handles initialization and management of Streamlit session state variables.
"""

import streamlit as st

from tracking_app.storage import get_storage


def init_session_state():
    """Initialize session state variables for the Insights page."""
    if 'storage' not in st.session_state:
        st.session_state.storage = get_storage()
    
    if 'user_xp' not in st.session_state:
        st.session_state.user_xp = st.session_state.storage.get_xp()
    
    if 'user_level' not in st.session_state:
        st.session_state.user_level = st.session_state.storage.get_level()