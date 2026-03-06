"""Session state management for the Journal page."""

import streamlit as st

def init_session_state():
    if 'journal_editing_entry' not in st.session_state:
        st.session_state.journal_editing_entry = None
    if 'journal_filter_category' not in st.session_state:
        st.session_state.journal_filter_category = None