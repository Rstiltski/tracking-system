"""
Helper functions for the Leaderboards page.

Contains data retrieval and processing functions.
"""

from datetime import date, timedelta
from typing import Dict, Any, List, Optional

from .constants import (
    DEFAULT_COMPETITION_DURATION_DAYS,
    LEADERBOARD_TOP_DISPLAY_COUNT,
)


def calculate_days_remaining(end_date: str) -> int:
    """
    Calculate days remaining in a competition.
    
    Args:
        end_date: End date as ISO string
        
    Returns:
        Number of days remaining
    """
    try:
        end = date.fromisoformat(end_date)
        return (end - date.today()).days
    except (ValueError, TypeError):
        return 0


def calculate_progress(start_date: str, end_date: str) -> float:
    """
    Calculate competition progress as a percentage.
    
    Args:
        start_date: Start date as ISO string
        end_date: End date as ISO string
        
    Returns:
        Progress as a float between 0 and 1
    """
    try:
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)
        total_days = (end - start).days
        if total_days <= 0:
            return 1.0
        days_elapsed = (date.today() - start).days
        return min(1.0, days_elapsed / total_days)
    except (ValueError, TypeError):
        return 0.0


def format_competition_type(comp_type: str) -> str:
    """
    Format competition type for display.
    
    Args:
        comp_type: Competition type string
        
    Returns:
        Formatted competition type
    """
    return comp_type.replace('_', ' ').title()


def get_medal_for_position(position: int) -> str:
    """
    Get medal emoji for leaderboard position.
    
    Args:
        position: Leaderboard position (1-indexed)
        
    Returns:
        Medal emoji or position number
    """
    if position == 1:
        return "🥇"
    elif position == 2:
        return "🥈"
    elif position == 3:
        return "🥉"
    else:
        return f"{position}."


def get_default_end_date() -> date:
    """
    Get default competition end date.
    
    Returns:
        Default end date (7 days from today)
    """
    return date.today() + timedelta(days=DEFAULT_COMPETITION_DURATION_DAYS)