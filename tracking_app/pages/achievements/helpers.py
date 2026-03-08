"""
Helper functions for the Achievements page.

Contains utility functions for XP calculations and formatting.
"""

from typing import Tuple

import streamlit as st

from .constants import BASE_XP_PER_LEVEL, XP_INCREMENT_PER_LEVEL


@st.cache_data(ttl=3600, show_spinner=False)
def get_xp_for_level(level: int) -> int:
    """
    Calculate XP required for a given level.
    
    Args:
        level: Target level
        
    Returns:
        XP required for that level
    """
    if level <= 1:
        return 0
    return BASE_XP_PER_LEVEL + (level - 2) * XP_INCREMENT_PER_LEVEL


@st.cache_data(ttl=3600, show_spinner=False)
def get_level_from_xp(xp: int) -> int:
    """
    Calculate level from total XP.
    
    Args:
        xp: Total XP points
        
    Returns:
        Current level
    """
    level = 1
    while xp >= get_xp_for_level(level + 1):
        level += 1
    return level


@st.cache_data(ttl=3600, show_spinner=False)
def get_xp_progress(xp: int, level: int) -> Tuple[int, int, float]:
    """
    Get XP progress towards next level.
    
    Args:
        xp: Current total XP
        level: Current level
        
    Returns:
        Tuple of (xp_in_current_level, xp_needed_for_next, percentage)
    """
    current_level_xp = get_xp_for_level(level)
    next_level_xp = get_xp_for_level(level + 1)
    
    xp_in_level = xp - current_level_xp
    xp_needed = next_level_xp - current_level_xp
    
    percentage = (xp_in_level / xp_needed * 100) if xp_needed > 0 else 100
    
    return xp_in_level, xp_needed, percentage


def get_xp_remaining(xp: int, level: int) -> int:
    """
    Get XP remaining to reach next level.
    
    Args:
        xp: Current total XP
        level: Current level
        
    Returns:
        XP needed for next level
    """
    xp_in_level, xp_needed, _ = get_xp_progress(xp, level)
    return xp_needed - xp_in_level


def format_xp(xp: int) -> str:
    """
    Format XP with commas.
    
    Args:
        xp: XP amount
        
    Returns:
        Formatted string
    """
    return f"{xp:,}"