"""
Session state management for the Habits page.

Handles initialization and management of Streamlit session state variables.
"""

import streamlit as st
from datetime import datetime, date

from tracking_app.storage import get_storage
from brain.models.streak import StreakFreeze

from .constants import INITIAL_STREAK_FREEZE_COUNT
from .helpers import get_local_date, get_level_from_xp


def init_session_state():
    """
    Initialize session state variables.
    
    Sets up:
    - storage: Storage instance for data access
    - user_xp: User's current XP
    - user_level: User's current level
    - editing_habit: ID of habit being edited (or None)
    - streak_freeze: Streak freeze inventory
    - show_add_habit_form: Toggle for add habit form
    - matrix_last_update: Timestamp for matrix refresh
    - habit_view_mode: 'week' or 'month' view
    - habit_current_date: Current date for navigation
    """
    if 'storage' not in st.session_state:
        st.session_state.storage = get_storage()
    
    if 'user_xp' not in st.session_state:
        st.session_state.user_xp = st.session_state.storage.get_xp()
    
    if 'user_level' not in st.session_state:
        st.session_state.user_level = st.session_state.storage.get_level()
    
    if 'editing_habit' not in st.session_state:
        st.session_state.editing_habit = None
    
    # Streak freeze inventory
    if 'streak_freeze' not in st.session_state:
        st.session_state.streak_freeze = load_streak_freeze()
    
    # Toggle for add habit form in spreadsheet view
    if 'show_add_habit_form' not in st.session_state:
        st.session_state.show_add_habit_form = False
    
    # Timestamp for forcing matrix widget refresh after changes
    if 'matrix_last_update' not in st.session_state:
        st.session_state.matrix_last_update = datetime.now().isoformat()
    
    # View mode: 'week' or 'month'
    if 'habit_view_mode' not in st.session_state:
        st.session_state.habit_view_mode = 'month'
    
    # Current date for navigation
    if 'habit_current_date' not in st.session_state:
        st.session_state.habit_current_date = get_local_date()


def load_streak_freeze() -> StreakFreeze:
    """
    Load streak freeze inventory from storage.
    
    Returns:
        StreakFreeze instance with current freeze count
    """
    storage = st.session_state.storage
    freeze_data = storage.get_user_data("streak_freeze", None)

    if freeze_data:
        return StreakFreeze.from_dict(freeze_data)
    return StreakFreeze(count=INITIAL_STREAK_FREEZE_COUNT)


def save_streak_freeze(freeze: StreakFreeze) -> None:
    """
    Save streak freeze inventory to storage.
    
    Args:
        freeze: StreakFreeze instance to save
    """
    storage = st.session_state.storage
    storage.set_user_data("streak_freeze", freeze.to_dict())
    st.session_state.streak_freeze = freeze


def use_streak_freeze_for_habit(habit_id: str) -> bool:
    """
    Use a streak freeze for a habit.

    Marks yesterday as "skipped" to preserve the streak.

    Args:
        habit_id: ID of the habit to use freeze for
        
    Returns:
        True if freeze was used successfully
    """
    from .helpers import get_local_date
    
    streak_freeze = st.session_state.streak_freeze
    yesterday = get_local_date() - timedelta(days=1)

    if not streak_freeze.is_available:
        return False

    if streak_freeze.use_freeze(habit_id, yesterday):
        # Mark yesterday as skipped in storage
        storage = st.session_state.storage
        storage.mark_habit_skipped(habit_id, yesterday)

        # Save updated freeze inventory
        save_streak_freeze(streak_freeze)
        return True

    return False


# Import timedelta for use_streak_freeze_for_habit
from datetime import timedelta