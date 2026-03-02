"""
Session state management for the Data Import page.

Handles initialization and management of Streamlit session state variables.
"""

import streamlit as st


def init_session_state():
    """Initialize session state variables for the Data Import page."""
    if 'import_in_progress' not in st.session_state:
        st.session_state.import_in_progress = False
    
    if 'last_import' not in st.session_state:
        st.session_state.last_import = None
    
    if 'current_preview' not in st.session_state:
        st.session_state.current_preview = None