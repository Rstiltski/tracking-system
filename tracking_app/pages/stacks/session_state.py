"""
Session state management for the Stacks page.
"""

import streamlit as st

from tracking_app.storage import get_storage

from brain.behavioral.habit_stacking import HabitStack, HabitStackingEngine

from .constants import DEFAULT_USER_ID


def init_session_state() -> None:
    """Initialize session state variables."""
    if 'storage' not in st.session_state:
        st.session_state.storage = get_storage()
    
    if 'user_xp' not in st.session_state:
        st.session_state.user_xp = st.session_state.storage.get_xp()
    
    if 'user_level' not in st.session_state:
        st.session_state.user_level = st.session_state.storage.get_level()
    
    if 'stack_engine' not in st.session_state:
        st.session_state.stack_engine = load_stack_engine()
    
    if 'creating_stack' not in st.session_state:
        st.session_state.creating_stack = False


def load_stack_engine() -> HabitStackingEngine:
    """
    Load or create the habit stacking engine.
    
    Returns:
        HabitStackingEngine instance with saved stacks loaded
    """
    engine = HabitStackingEngine()
    
    # Load stacks from storage
    storage = st.session_state.storage
    stacks_data = storage.get_user_data("habit_stacks", [])
    
    for stack_dict in stacks_data:
        try:
            stack = HabitStack.from_dict(stack_dict)
            engine.stacks[stack.id] = stack
        except Exception:
            pass
    
    return engine


def save_stack_engine(engine: HabitStackingEngine) -> None:
    """
    Save stacks to storage.
    
    Args:
        engine: The habit stacking engine with stacks to save
    """
    storage = st.session_state.storage
    stacks_data = [stack.to_dict() for stack in engine.stacks.values()]
    storage.set_user_data("habit_stacks", stacks_data)


def get_storage():
    """Get the storage instance from session state."""
    return st.session_state.storage


def get_stack_engine() -> HabitStackingEngine:
    """Get the stack engine from session state."""
    return st.session_state.stack_engine


def get_user_xp() -> int:
    """Get the user's current XP."""
    return st.session_state.user_xp


def get_user_level() -> int:
    """Get the user's current level."""
    return st.session_state.user_level


def is_creating_stack() -> bool:
    """Check if currently in stack creation mode."""
    return st.session_state.creating_stack


def set_creating_stack(value: bool) -> None:
    """Set stack creation mode."""
    st.session_state.creating_stack = value