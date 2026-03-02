"""
Session state management for the Data Export page.

Handles initialization and management of Streamlit session state variables.
"""

import streamlit as st


def init_session_state():
    """Initialize session state variables for the Data Export page."""
    if 'export_in_progress' not in st.session_state:
        st.session_state.export_in_progress = False
    
    if 'last_export' not in st.session_state:
        st.session_state.last_export = None