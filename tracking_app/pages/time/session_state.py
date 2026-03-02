"""
Session state management for the Time page.

Handles initialization and management of Streamlit session state variables.
"""

import streamlit as st

from tracking_app.storage import get_storage
from .constants import TIME_CATEGORIES


def init_session_state():
    """
    Initialize session state variables for the Time page.
    
    Sets up:
    - storage: Storage instance for data access
    - timer_running: Whether timer is currently running
    - timer_start: Unix timestamp when timer started
    - timer_elapsed: Previously elapsed seconds
    - timer_category: Current timer category
    - time_entries: List of time entries
    - show_manual_entry: Whether to show manual entry form
    """
    if 'storage' not in st.session_state:
        st.session_state.storage = get_storage()
    
    # Timer state
    if 'timer_running' not in st.session_state:
        st.session_state.timer_running = False
    
    if 'timer_start' not in st.session_state:
        st.session_state.timer_start = None
    
    if 'timer_elapsed' not in st.session_state:
        st.session_state.timer_elapsed = 0
    
    if 'timer_category' not in st.session_state:
        st.session_state.timer_category = TIME_CATEGORIES[0]
    
    # Time entries
    if 'time_entries' not in st.session_state:
        st.session_state.time_entries = []
    
    # Manual entry form
    if 'show_manual_entry' not in st.session_state:
        st.session_state.show_manual_entry = False


def reset_timer():
    """Reset timer state to initial values."""
    st.session_state.timer_running = False
    st.session_state.timer_start = None
    st.session_state.timer_elapsed = 0


def start_timer():
    """Start the timer."""
    import time as time_module
    st.session_state.timer_running = True
    st.session_state.timer_start = time_module.time()


def pause_timer(elapsed: int):
    """Pause the timer with current elapsed time."""
    st.session_state.timer_elapsed = elapsed
    st.session_state.timer_running = False
    st.session_state.timer_start = None