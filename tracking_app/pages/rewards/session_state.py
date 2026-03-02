"""
Session state management for the Rewards page.
"""

import streamlit as st

from tracking_app.storage import get_storage

from brain.behavioral.rewards import Reward, RewardEngine, create_default_engine

from .constants import DEFAULT_USER_ID


def init_session_state() -> None:
    """Initialize session state variables."""
    if 'storage' not in st.session_state:
        st.session_state.storage = get_storage()
    
    if 'user_xp' not in st.session_state:
        st.session_state.user_xp = st.session_state.storage.get_xp()
    
    if 'user_level' not in st.session_state:
        st.session_state.user_level = st.session_state.storage.get_level()
    
    if 'reward_engine' not in st.session_state:
        st.session_state.reward_engine = load_reward_engine()
    
    if 'last_roll_result' not in st.session_state:
        st.session_state.last_roll_result = None
    
    if 'rolling' not in st.session_state:
        st.session_state.rolling = False


def load_reward_engine() -> RewardEngine:
    """
    Load or create the reward engine.
    
    Returns:
        RewardEngine instance with custom rewards loaded
    """
    engine = create_default_engine()
    
    # Load custom rewards from storage
    storage = st.session_state.storage
    custom_rewards = storage.get_user_data("custom_rewards", [])
    
    for reward_dict in custom_rewards:
        try:
            reward = Reward.from_dict(reward_dict)
            engine.add_reward(reward)
        except Exception:
            pass
    
    return engine


def save_reward_history(engine: RewardEngine) -> None:
    """
    Save reward history to storage.
    
    Args:
        engine: The reward engine with histories to save
    """
    storage = st.session_state.storage
    # Save histories
    for user_id, history in engine.histories.items():
        storage.set_user_data(f"reward_history_{user_id}", history.to_dict())


def get_storage():
    """Get the storage instance from session state."""
    return st.session_state.storage


def get_reward_engine() -> RewardEngine:
    """Get the reward engine from session state."""
    return st.session_state.reward_engine


def get_user_xp() -> int:
    """Get the user's current XP."""
    return st.session_state.user_xp


def get_user_level() -> int:
    """Get the user's current level."""
    return st.session_state.user_level


def get_last_roll_result():
    """Get the last roll result."""
    return st.session_state.last_roll_result


def set_last_roll_result(result) -> None:
    """Set the last roll result."""
    st.session_state.last_roll_result = result


def update_user_xp(xp: int) -> None:
    """Update the user's XP in session state."""
    st.session_state.user_xp = xp


def refresh_user_stats() -> None:
    """Refresh user XP and level from storage."""
    storage = st.session_state.storage
    st.session_state.user_xp = storage.get_xp()
    st.session_state.user_level = storage.get_level()