"""
Session state management for the Tasks page.

Handles initialization and management of Streamlit session state variables.
"""

import streamlit as st

from tracking_app.storage import get_storage
from tracking_app.pages.tasks.helpers import get_level_from_xp


def init_session_state():
    """
    Initialize session state variables for the Tasks page.
    
    Sets up:
    - storage: Storage instance for data access
    - user_xp: Current XP points
    - user_level: Current level
    - editing_task: ID of task being edited (or None)
    - filter_status: Current status filter
    - filter_priority: Current priority filter
    - filter_category: Current category filter
    """
    if 'storage' not in st.session_state:
        st.session_state.storage = get_storage()
    
    if 'user_xp' not in st.session_state:
        st.session_state.user_xp = st.session_state.storage.get_xp()
    
    if 'user_level' not in st.session_state:
        st.session_state.user_level = get_level_from_xp(st.session_state.user_xp)
    
    if 'editing_task' not in st.session_state:
        st.session_state.editing_task = None
    
    if 'filter_status' not in st.session_state:
        st.session_state.filter_status = "all"
    
    if 'filter_priority' not in st.session_state:
        st.session_state.filter_priority = "all"
    
    if 'filter_category' not in st.session_state:
        st.session_state.filter_category = "All Categories"