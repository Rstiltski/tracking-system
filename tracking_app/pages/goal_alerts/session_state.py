"""
Session state management for the Goal Alerts page.

Handles initialization and management of Streamlit session state variables.
"""

import streamlit as st

from .constants import DEFAULT_USER_ID


def init_session_state():
    """Initialize session state variables for the Goal Alerts page."""
    if 'user_id' not in st.session_state:
        st.session_state.user_id = DEFAULT_USER_ID
    
    if 'goal_alerts_enabled' not in st.session_state:
        st.session_state.goal_alerts_enabled = True
    
    if 'milestone_enabled' not in st.session_state:
        st.session_state.milestone_enabled = True
    
    if 'deadline_enabled' not in st.session_state:
        st.session_state.deadline_enabled = True