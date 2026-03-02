"""
Helper functions for the Challenges page.

Contains challenge management utilities.
"""

import streamlit as st

from tracking_app.storage import get_storage

from .constants import DEFAULT_USER_ID


def get_challenge_manager():
    """
    Get or create the challenge manager instance.
    
    Returns:
        ChallengeManager instance
    """
    try:
        from brain.social.challenge_manager import ChallengeManager
        storage = st.session_state.get('storage', get_storage())
        user_id = st.session_state.get('user_id', DEFAULT_USER_ID)
        return ChallengeManager(storage, user_id)
    except ImportError:
        return None


def calculate_challenge_progress(challenge: dict) -> float:
    """
    Calculate the time progress of a challenge.
    
    Args:
        challenge: Challenge dictionary
        
    Returns:
        Progress as a float between 0 and 1
    """
    from datetime import date
    
    start = date.fromisoformat(challenge['start_date'])
    end = date.fromisoformat(challenge['end_date'])
    total_days = (end - start).days
    
    if total_days <= 0:
        return 0
    
    days_elapsed = (date.today() - start).days
    return min(1.0, days_elapsed / total_days)


def get_days_remaining(challenge: dict) -> int:
    """
    Get the number of days remaining in a challenge.
    
    Args:
        challenge: Challenge dictionary
        
    Returns:
        Number of days remaining
    """
    from datetime import date
    
    end = date.fromisoformat(challenge['end_date'])
    remaining = (end - date.today()).days
    return max(0, remaining)