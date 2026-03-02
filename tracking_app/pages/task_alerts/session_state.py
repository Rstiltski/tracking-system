"""
Session state management for the Task Alerts page.
"""

import streamlit as st
from datetime import time
from typing import Dict, Any

from .constants import (
    DEFAULT_USER_ID,
    DEFAULT_EARLY_WARNING_HOURS,
    DEFAULT_FINAL_WARNING_HOURS,
    DEFAULT_MEDIUM_THRESHOLD_HOURS,
    DEFAULT_HIGH_THRESHOLD_HOURS,
    DEFAULT_DIGEST_TIME_HOUR,
    DEFAULT_DIGEST_TIME_MINUTE,
)


def init_session_state() -> None:
    """Initialize session state variables for task alerts settings."""
    # General settings
    if 'task_alerts_enabled' not in st.session_state:
        st.session_state.task_alerts_enabled = True
    
    # Deadline warning thresholds
    if 'early_warning_hours' not in st.session_state:
        st.session_state.early_warning_hours = DEFAULT_EARLY_WARNING_HOURS
    
    if 'early_channel' not in st.session_state:
        st.session_state.early_channel = "Email"
    
    if 'final_warning_hours' not in st.session_state:
        st.session_state.final_warning_hours = DEFAULT_FINAL_WARNING_HOURS
    
    if 'final_channel' not in st.session_state:
        st.session_state.final_channel = "All Channels"
    
    # Progressive urgency
    if 'progressive_enabled' not in st.session_state:
        st.session_state.progressive_enabled = True
    
    if 'medium_threshold' not in st.session_state:
        st.session_state.medium_threshold = DEFAULT_MEDIUM_THRESHOLD_HOURS
    
    if 'high_threshold' not in st.session_state:
        st.session_state.high_threshold = DEFAULT_HIGH_THRESHOLD_HOURS
    
    # Daily digest
    if 'digest_enabled' not in st.session_state:
        st.session_state.digest_enabled = True
    
    if 'digest_time' not in st.session_state:
        st.session_state.digest_time = time(DEFAULT_DIGEST_TIME_HOUR, DEFAULT_DIGEST_TIME_MINUTE)
    
    if 'digest_channel' not in st.session_state:
        st.session_state.digest_channel = "Email"
    
    if 'include_due_today' not in st.session_state:
        st.session_state.include_due_today = True
    
    if 'include_overdue' not in st.session_state:
        st.session_state.include_overdue = True
    
    if 'include_upcoming' not in st.session_state:
        st.session_state.include_upcoming = True
    
    if 'include_completed' not in st.session_state:
        st.session_state.include_completed = False
    
    # Overdue handling
    if 'overdue_enabled' not in st.session_state:
        st.session_state.overdue_enabled = True
    
    if 'overdue_frequency' not in st.session_state:
        st.session_state.overdue_frequency = "Daily"
    
    if 'max_reminders' not in st.session_state:
        st.session_state.max_reminders = 3
    
    # Priority settings
    if 'priority_settings' not in st.session_state:
        st.session_state.priority_settings = {
            'high': {'enabled': True, 'channel': 'All Channels'},
            'medium': {'enabled': True, 'channel': 'Browser'},
            'low': {'enabled': False, 'channel': 'Email'},
        }


def get_task_alerts_enabled() -> bool:
    """Get task alerts enabled status."""
    return st.session_state.task_alerts_enabled


def set_task_alerts_enabled(value: bool) -> None:
    """Set task alerts enabled status."""
    st.session_state.task_alerts_enabled = value


def get_progressive_enabled() -> bool:
    """Get progressive urgency enabled status."""
    return st.session_state.progressive_enabled


def get_digest_enabled() -> bool:
    """Get daily digest enabled status."""
    return st.session_state.digest_enabled


def get_overdue_enabled() -> bool:
    """Get overdue alerts enabled status."""
    return st.session_state.overdue_enabled


def get_priority_settings() -> Dict[str, Dict[str, Any]]:
    """Get priority-based alert settings."""
    return st.session_state.priority_settings