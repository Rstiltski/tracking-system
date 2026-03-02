"""
Session state management for the Finances page.

Handles initialization and management of Streamlit session state variables.
"""

import streamlit as st

from tracking_app.storage import get_storage


def init_session_state():
    """
    Initialize session state variables for the Finances page.
    
    Sets up:
    - storage: Storage instance for data access
    - filter_period: Current time period filter
    - filter_type: Current transaction type filter
    """
    if 'storage' not in st.session_state:
        st.session_state.storage = get_storage()
    
    if 'filter_period' not in st.session_state:
        st.session_state.filter_period = "this_month"
    
    if 'filter_type' not in st.session_state:
        st.session_state.filter_type = "all"
    
    if 'show_add_transaction' not in st.session_state:
        st.session_state.show_add_transaction = False
    
    if 'editing_transaction' not in st.session_state:
        st.session_state.editing_transaction = None