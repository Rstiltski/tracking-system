"""
Session State Management - Unified State Handling

Provides consistent session state management across all pages.
Handles storage, XP, level, and user preferences.

Usage:
    from tracking_app.components.session import init_session_state, get_storage
"""
import streamlit as st
from typing import Optional
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tracking_app.storage import Storage, get_storage as _get_storage


def init_session_state():
    """
    Initialize all session state variables.
    
    Sets up:
    - storage: Database storage instance
    - user_xp: User's current XP
    - user_level: User's current level
    - theme: UI theme preference
    """
    # Storage instance
    if 'storage' not in st.session_state:
        st.session_state.storage = _get_storage()
    
    # User stats
    if 'user_xp' not in st.session_state:
        st.session_state.user_xp = st.session_state.storage.get_xp()
    
    if 'user_level' not in st.session_state:
        st.session_state.user_level = st.session_state.storage.get_level()
    
    # Theme preference
    if 'theme' not in st.session_state:
        saved_theme = st.session_state.storage.get_user_data('theme')
        # Default to 'dark' if no saved theme
        st.session_state.theme = saved_theme if saved_theme else 'dark'
    
    # Streak freezes
    if 'streak_freezes' not in st.session_state:
        st.session_state.streak_freezes = st.session_state.storage.get_streak_freezes()


def get_storage() -> Storage:
    """
    Get the storage instance from session state.
    
    Returns:
        Storage instance
    """
    if 'storage' not in st.session_state:
        init_session_state()
    return st.session_state.storage


def get_xp_for_level(level: int) -> int:
    """
    Calculate XP required for a given level.
    
    Formula: 100 + (level - 2) * 150
    - Level 1: 0 XP
    - Level 2: 100 XP
    - Level 3: 250 XP
    - Level 4: 400 XP
    - etc.
    
    Args:
        level: Target level
        
    Returns:
        XP required to reach that level
    """
    if level <= 1:
        return 0
    return 100 + (level - 2) * 150


def get_level_from_xp(xp: int) -> int:
    """
    Calculate level from total XP.
    
    Args:
        xp: Total XP earned
        
    Returns:
        Current level based on XP
    """
    level = 1
    while xp >= get_xp_for_level(level + 1):
        level += 1
    return level


def add_xp(amount: int) -> int:
    """
    Add XP and update level.
    
    Args:
        amount: XP to add
        
    Returns:
        New total XP
    """
    storage = get_storage()
    new_xp = storage.add_xp(amount)
    st.session_state.user_xp = new_xp
    st.session_state.user_level = get_level_from_xp(new_xp)
    return new_xp


def get_user_data(key: str, default=None):
    """
    Get user data from storage.
    
    Args:
        key: Data key
        default: Default value if not found
        
    Returns:
        Stored value or default
    """
    storage = get_storage()
    return storage.get_user_data(key, default)


def set_user_data(key: str, value):
    """
    Set user data in storage.
    
    Args:
        key: Data key
        value: Value to store
    """
    storage = get_storage()
    storage.set_user_data(key, value)


def refresh_user_stats():
    """Refresh user stats from storage."""
    storage = get_storage()
    st.session_state.user_xp = storage.get_xp()
    st.session_state.user_level = storage.get_level()
    st.session_state.streak_freezes = storage.get_streak_freezes()


__all__ = [
    "init_session_state",
    "get_storage",
    "get_xp_for_level",
    "get_level_from_xp",
    "add_xp",
    "get_user_data",
    "set_user_data",
    "refresh_user_stats",
]