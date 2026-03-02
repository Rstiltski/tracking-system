"""
Session state management for the Goals page.

Handles initialization and management of Streamlit session state variables.
"""

import streamlit as st

from tracking_app.storage import get_storage


def init_session_state():
    """
    Initialize session state variables for the Goals page.
    
    Sets up:
    - storage: Storage instance for data access
    - user_xp: Current XP points
    - user_level: Current level
    - editing_goal: ID of goal being edited (or None)
    """
    if 'storage' not in st.session_state:
        st.session_state.storage = get_storage()
    
    if 'user_xp' not in st.session_state:
        st.session_state.user_xp = st.session_state.storage.get_xp()
    
    if 'user_level' not in st.session_state:
        st.session_state.user_level = st.session_state.storage.get_level()
    
    if 'editing_goal' not in st.session_state:
        st.session_state.editing_goal = None