"""
Session state management for the Data Lifecycle page.

Handles initialization and management of Streamlit session state variables.
"""

import streamlit as st


def init_session_state():
    """Initialize session state variables for the Data Lifecycle page."""
    if 'show_reset_confirm' not in st.session_state:
        st.session_state.show_reset_confirm = False
    
    if 'show_erasure_confirm' not in st.session_state:
        st.session_state.show_erasure_confirm = False