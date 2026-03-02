"""
Session state management for the Dashboard page.

Handles initialization and management of Streamlit session state variables.
"""

import streamlit as st

from tracking_app.components.session import init_session_state as base_init_session_state


def init_session_state():
    """
    Initialize session state variables for the Dashboard page.
    
    Extends the base session state initialization with dashboard-specific variables.
    """
    # Call base initialization
    base_init_session_state()
    
    # Dashboard-specific state
    # Currently no additional state needed beyond base session state