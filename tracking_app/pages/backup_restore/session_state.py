"""
Session state management for the Backup & Restore page.

Handles initialization and management of Streamlit session state variables.
"""

import streamlit as st


def init_session_state():
    """Initialize session state variables for the Backup & Restore page."""
    if 'backup_in_progress' not in st.session_state:
        st.session_state.backup_in_progress = False
    
    if 'restore_in_progress' not in st.session_state:
        st.session_state.restore_in_progress = False
    
    if 'show_restore_confirm' not in st.session_state:
        st.session_state.show_restore_confirm = False
    
    if 'selected_backup' not in st.session_state:
        st.session_state.selected_backup = None