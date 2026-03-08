"""
Helper functions for the Habits page.

Contains utility functions for streak calculation, score computation,
date handling, and other common operations.
"""

import streamlit as st
from datetime import datetime, date, timedelta
from typing import Dict, Optional, Any, List

from tracking_app.storage import Storage
from tracking_app.models import HabitEntry
from brain.models.habit import HabitScore, ScoreList, NumericalHabitTarget
from brain.models.frequency import Frequency
from brain.models.entry import EntryList

from .constants import (
    MAX_STREAK_LOOKBACK_DAYS,
    DEFAULT_SCORE_LOOKBACK_DAYS,
    DEFAULT_COMPLETION_RATE_DAYS,
    SCORE_CATEGORIES,
)


@st.cache_data(ttl=300)
def get_habits_batch_data(habit_ids: str, _storage_hash: str) -> Dict[str, Dict]:
    """
    Batch load habit data for multiple habits to avoid N+1 queries.
    
    This function loads all entries for multiple habits in a single call,
    reducing database queries from O(n) to O(1).
    
    Args:
        habit_ids: Comma-separated habit IDs
        _storage_hash: Hash of storage to ensure cache invalidation
        
    Returns:
        Dictionary mapping habit_id to {entries, streak, completion_rate, score}
    """
    # Parse habit IDs
    habit_id_list = habit_ids.split(",") if habit_ids else []
    if not habit_id_list:
        return {}
    
    # This is a placeholder - actual implementation would batch load
    # For now, this demonstrates the pattern to use
    return {}


def get_local_date() -> date:
    """
    Get the current local date with timezone handling.

    Returns:
        Current date in local timezone
    """
    # Use datetime.now() for local time instead of date.today()
    # This respects the system's timezone settings
    return datetime.now().date()


def is_entry_completed(entry: Optional[HabitEntry]) -> bool:
    """
    Check if a habit entry represents a completion.

    Handles both boolean and numerical habit completion logic.

    Args:
        entry: The habit entry to check

    Returns:
        True if the entry represents a completed habit
    """
    if entry is None:
        return False

    # Check if explicitly skipped
    if hasattr(entry, 'skipped') and entry.skipped:
        return False

    # Check if completed (value > 0 means completed)
    if hasattr(entry, 'value'):
        return entry.value > 0

    return False


def calculate_streak(storage: Storage, habit_id: str) -> int:
    """
    Calculate current streak for a habit.
    
    Args:
        storage: Storage instance for data access
        habit_id: ID of the habit to calculate streak for
        
    Returns:
        Number of consecutive days the habit has been completed
    """
    streak = 0
    today = get_local_date()

    for i in range(MAX_STREAK_LOOKBACK_DAYS):
        check_date = today - timedelta(days=i)
        entry = storage.get_habit_entry(habit_id, check_date)

        if is_entry_completed(entry):
            streak += 1
        else:
            break

    return streak


def get_completion_rate(storage: Storage, habit_id: str, days: int = DEFAULT_COMPLETION_RATE_DAYS) -> float:
    """
    Get completion rate for a habit over N days.
    
    Args:
        storage: Storage instance for data access
        habit_id: ID of the habit to calculate rate for
        days: Number of days to look back
        
    Returns:
        Completion rate as a percentage (0-100)
    """
    today = get_local_date()
    completed = 0

    for i in range(days):
        check_date = today - timedelta(days=i)
        entry = storage.get_habit_entry(habit_id, check_date)
        if is_entry_completed(entry):
            completed += 1

    return (completed / days) * 100


def calculate_habit_score(storage: Storage, habit_id: str, lookback_days: int = DEFAULT_SCORE_LOOKBACK_DAYS) -> HabitScore:
    """
    Calculate habit score using exponential smoothing algorithm.

    This uses the scientific scoring system from brain/models/habit.py:
    - Score from 0.0 to 1.0 (displayed as 0-100%)
    - Frequency-aware multiplier: 0.5^(√frequency / 13)
    - Recent days have higher weight
    - Gradual decay on misses, not reset to zero

    Args:
        storage: Storage instance for data access
        habit_id: ID of the habit to calculate score for
        lookback_days: Number of days to consider (default: 90)

    Returns:
        HabitScore with value, trend, and timestamp
    """
    today = get_local_date()
    from_date = today - timedelta(days=lookback_days)

    # Build entry list for score computation
    entries = EntryList(habit_id=habit_id)

    # Get habit to check if it's numerical
    habit = storage.get_habit(habit_id)
    is_numerical = bool(habit and habit.habit_type == "numerical")
    target_value = habit.target_value if habit and hasattr(habit, 'target_value') else 0.0
    target_type = habit.target_type if habit and hasattr(habit, 'target_type') else "at_least"

    # Populate entries from storage
    for i in range(lookback_days + 1):
        check_date = from_date + timedelta(days=i)
        entry = storage.get_habit_entry(habit_id, check_date)

        if entry:
            if hasattr(entry, 'skipped') and entry.skipped:
                entries.mark_skipped(check_date)
            elif entry.value > 0:  # value > 0 means completed
                entries.mark_completed(check_date)

    # Create frequency (assume daily for now)
    frequency = Frequency.daily()

    # Create score list and recompute with proper numerical habit parameters
    score_list = ScoreList()
    score_list.recompute(
        frequency=frequency,
        entries=entries,
        from_date=from_date,
        to_date=today,
        is_numerical=is_numerical,
        target_value=target_value,
        numerical_target_type=NumericalHabitTarget(target_type) if target_type in ["at_least", "at_most"] else NumericalHabitTarget.AT_LEAST
    )

    return score_list.current


def get_score_category(score: float) -> Dict[str, str]:
    """
    Get the score category for display.

    Args:
        score: Score value (0.0 to 1.0)

    Returns:
        Dict with 'label', 'color', and 'emoji' keys
    """
    # Iterate through categories in order (highest to lowest threshold)
    for category in ["excellent", "strong", "developing", "building", "starting"]:
        if score >= SCORE_CATEGORIES[category]["min"]:
            return SCORE_CATEGORIES[category]
    return SCORE_CATEGORIES["starting"]


def get_trend_indicator(trend: float) -> Dict[str, str]:
    """
    Get trend indicator for display.
    
    Args:
        trend: Trend value (-1.0 to 1.0)
        
    Returns:
        Dict with 'icon', 'color', and 'label' keys
    """
    if trend > 0.01:
        return {"icon": "↑", "color": "green", "label": "improving"}
    elif trend < -0.01:
        return {"icon": "↓", "color": "red", "label": "declining"}
    else:
        return {"icon": "→", "color": "gray", "label": "stable"}


def check_streak_break_yesterday(storage: Storage, habit_id: str) -> bool:
    """
    Check if streak was broken yesterday (can be frozen).

    Returns True if:
    - Yesterday was NOT completed
    - There was a streak before yesterday
    
    Args:
        storage: Storage instance for data access
        habit_id: ID of the habit to check
        
    Returns:
        True if streak was broken yesterday and can be frozen
    """
    today = get_local_date()
    yesterday = today - timedelta(days=1)

    # Check if yesterday was NOT completed
    yesterday_entry = storage.get_habit_entry(habit_id, yesterday)
    if is_entry_completed(yesterday_entry):
        return False  # Yesterday was completed, no break

    # Check if there was a streak before yesterday
    streak_before = 0
    for i in range(2, MAX_STREAK_LOOKBACK_DAYS):  # Start from day before yesterday
        check_date = today - timedelta(days=i)
        entry = storage.get_habit_entry(habit_id, check_date)

        if is_entry_completed(entry):
            streak_before += 1
        else:
            break

    # If there was a streak of at least 1 day before yesterday, the break can be frozen
    return streak_before >= 1


def get_week_start(date_val: date) -> date:
    """
    Get the Monday of the week containing the given date.
    
    Args:
        date_val: The date to find the week start for
        
    Returns:
        The Monday of that week
    """
    return date_val - timedelta(days=date_val.weekday())


def get_month_start(date_val: date) -> date:
    """
    Get the first day of the month containing the given date.
    
    Args:
        date_val: The date to find the month start for
        
    Returns:
        The first day of that month
    """
    return date_val.replace(day=1)


def get_time_until_midnight() -> Dict[str, int]:
    """
    Calculate time remaining until midnight.
    
    Returns:
        Dict with 'hours', 'minutes', 'seconds' keys
    """
    now = datetime.now()
    tomorrow = now.replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
    diff = tomorrow - now
    
    total_seconds = int(diff.total_seconds())
    hours = total_seconds // 3600
    minutes = (total_seconds % 3600) // 60
    seconds = total_seconds % 60
    
    return {"hours": hours, "minutes": minutes, "seconds": seconds}


def get_xp_for_level(level: int) -> int:
    """
    Calculate XP required for a given level.
    
    Args:
        level: The level to calculate XP for
        
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


def get_xp_progress_in_level(xp: int) -> Dict[str, Any]:
    """
    Calculate XP progress within the current level.

    Args:
        xp: Total XP earned

    Returns:
        Dict with 'level', 'current_xp', 'xp_needed', and 'progress_percent' keys
    """
    current_level = get_level_from_xp(xp)
    xp_for_current_level = get_xp_for_level(current_level)
    xp_for_next_level = get_xp_for_level(current_level + 1)

    xp_in_level = xp - xp_for_current_level
    xp_needed = xp_for_next_level - xp_for_current_level

    progress_percent = (xp_in_level / xp_needed * 100) if xp_needed > 0 else 100

    return {
        "level": current_level,
        "current_xp": xp_in_level,
        "xp_needed": xp_needed,
        "progress_percent": min(progress_percent, 100),
    }
