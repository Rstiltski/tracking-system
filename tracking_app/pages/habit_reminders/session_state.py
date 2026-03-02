"""
Session state management for the Habit Reminders page.

Handles initialization and state management.
"""

import streamlit as st
from typing import Any, Optional


def init_session_state() -> None:
    """
    Initialize session state variables for the habit reminders page.
    """
    # Initialize storage
    if 'storage' not in st.session_state:
        from tracking_app.storage import get_storage
        st.session_state.storage = get_storage()
    
    # Initialize user ID
    if 'user_id' not in st.session_state:
        st.session_state.user_id = "default"
    
    # Initialize scheduler
    if 'scheduler' not in st.session_state:
        try:
            from brain.notifications.scheduler import get_scheduler
            st.session_state.scheduler = get_scheduler()
        except ImportError:
            st.session_state.scheduler = None
    
    # Initialize settings
    if 'reminder_settings' not in st.session_state:
        st.session_state.reminder_settings = {
            'default_time': '08:00',
            'default_snooze': 5,
            'smart_enabled': True,
            'min_samples': 5,
            'confidence_threshold': 0.7,
            'streak_protection': True,
            'warning_hours': 8,
            'escalation_hours': 4,
            'critical_hours': 2,
            'max_snoozes': 3,
            'snooze_escalation': True,
            'snooze_options': [5, 10, 15, 30],
        }


def get_storage():
    """Get the storage instance from session state."""
    return st.session_state.storage


def get_user_id() -> str:
    """Get the current user ID from session state."""
    return st.session_state.user_id


def get_scheduler():
    """Get the scheduler instance from session state."""
    return st.session_state.scheduler


def get_settings() -> dict:
    """Get the current reminder settings."""
    return st.session_state.reminder_settings


def update_settings(new_settings: dict) -> None:
    """
    Update reminder settings.
    
    Args:
        new_settings: Dictionary of settings to update
    """
    st.session_state.reminder_settings.update(new_settings)