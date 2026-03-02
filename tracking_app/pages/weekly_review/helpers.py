"""
Helper functions for the Weekly Review page.
"""

from datetime import date, timedelta
from typing import Any

from .constants import (
    COMPLETION_RATE_EXCELLENT,
    COMPLETION_RATE_GOOD,
    COMPLETION_RATE_MODERATE,
    EMOJI_EXCELLENT,
    EMOJI_GOOD,
    EMOJI_MODERATE,
    EMOJI_NEEDS_WORK,
    STREAK_MAX_DAYS,
)


def get_completion_emoji(rate: float) -> str:
    """
    Get emoji for completion rate.

    Args:
        rate: Completion rate (0.0-1.0)

    Returns:
        Emoji string
    """
    if rate >= COMPLETION_RATE_EXCELLENT:
        return EMOJI_EXCELLENT
    elif rate >= COMPLETION_RATE_GOOD:
        return EMOJI_GOOD
    elif rate >= COMPLETION_RATE_MODERATE:
        return EMOJI_MODERATE
    else:
        return EMOJI_NEEDS_WORK


def count_weekly_completions(
    storage: Any,
    habit_id: str,
    week_number: int,
    year: int
) -> int:
    """
    Count completions for a habit in a specific week.

    Args:
        storage: Storage instance
        habit_id: Habit ID
        week_number: ISO week number
        year: Year

    Returns:
        Number of completions
    """
    # Get week dates
    jan_4 = date(year, 1, 4)
    week_1_monday = jan_4 - timedelta(days=jan_4.weekday())
    week_start = week_1_monday + timedelta(weeks=week_number - 1)
    week_end = week_start + timedelta(days=6)

    # Count completions
    completions = 0
    current_date = week_start
    while current_date <= week_end:
        entry = storage.get_habit_entry(habit_id, current_date)
        if entry and hasattr(entry, 'value') and entry.value > 0:
            completions += 1
        current_date += timedelta(days=1)

    return completions


def calculate_streak(storage: Any, habit_id: str) -> int:
    """
    Calculate current streak for a habit.

    Args:
        storage: Storage instance
        habit_id: Habit ID

    Returns:
        Current streak count
    """
    streak = 0
    today = date.today()

    for i in range(STREAK_MAX_DAYS):
        check_date = today - timedelta(days=i)
        entry = storage.get_habit_entry(habit_id, check_date)
        if entry and hasattr(entry, 'value') and entry.value > 0:
            streak += 1
        else:
            break

    return streak


def get_week_dates(week_number: int, year: int) -> tuple:
    """
    Get start and end dates for a specific week.

    Args:
        week_number: ISO week number
        year: Year

    Returns:
        Tuple of (start_date, end_date)
    """
    jan_4 = date(year, 1, 4)
    week_1_monday = jan_4 - timedelta(days=jan_4.weekday())
    week_start = week_1_monday + timedelta(weeks=week_number - 1)
    week_end = week_start + timedelta(days=6)
    return week_start, week_end


def format_completion_rate(rate: float) -> str:
    """
    Format completion rate as percentage string.

    Args:
        rate: Completion rate (0.0-1.0)

    Returns:
        Formatted percentage string
    """
    return f"{rate:.0f}%"


def get_habit_display_name(habit: Any) -> str:
    """
    Get display name for a habit with icon.

    Args:
        habit: Habit object

    Returns:
        Formatted habit name with icon
    """
    icon = getattr(habit, 'icon', '🎯')
    return f"{icon} {habit.name}"