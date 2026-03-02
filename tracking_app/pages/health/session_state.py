"""
Session state management for the Health page.

Handles initialization and management of Streamlit session state variables.
"""

import streamlit as st
from datetime import date

from tracking_app.storage import get_storage


def init_session_state():
    """
    Initialize session state variables for the Health page.
    
    Sets up:
    - storage: Storage instance for data access
    - selected_date: Currently selected date
    """
    if 'storage' not in st.session_state:
        st.session_state.storage = get_storage()
    
    if 'selected_date' not in st.session_state:
        st.session_state.selected_date = date.today()