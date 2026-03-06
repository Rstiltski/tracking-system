"""
Helper functions for the Diary page.

Utility functions for mood handling, date formatting, and entry processing.
"""

from datetime import date, datetime
from typing import Optional

from .constants import DIARY_MOOD_EMOJIS, DIARY_MOOD_COLORS


def get_mood_emoji(mood: str) -> str:
    """
    Get the emoji for a mood.

    Args:
        mood: The mood string

    Returns:
        Emoji string for the mood
    """
    return DIARY_MOOD_EMOJIS.get(mood, "🙂")


def get_mood_color(mood: str) -> str:
    """
    Get the color for a mood.

    Args:
        mood: The mood string

    Returns:
        Hex color string for the mood
    """
    return DIARY_MOOD_COLORS.get(mood, "#eab308")


def format_entry_date(entry_date: date) -> str:
    """
    Format a date for display.

    Args:
        entry_date: The date to format

    Returns:
        Formatted date string
    """
    today = date.today()
    yesterday = today - __import__('datetime').timedelta(days=1)

    if entry_date == today:
        return "Today"
    elif entry_date == yesterday:
        return "Yesterday"
    else:
        # Format as "Monday, January 1"
        return entry_date.strftime("%A, %B %d")


def format_entry_time(created_at: datetime) -> str:
    """
    Format a timestamp for display.

    Args:
        created_at: The timestamp to format

    Returns:
        Formatted time string
    """
    if created_at is None:
        return ""

    today = date.today()
    entry_date = created_at.date()

    if entry_date == today:
        return created_at.strftime("%I:%M %p")
    else:
        return created_at.strftime("%b %d at %I:%M %p")


def get_relative_date(entry_date: date) -> str:
    """
    Get a relative date string (e.g., "2 days ago").

    Args:
        entry_date: The date to compare

    Returns:
        Relative date string
    """
    today = date.today()
    diff = (today - entry_date).days

    if diff == 0:
        return "Today"
    elif diff == 1:
        return "Yesterday"
    elif diff < 7:
        return f"{diff} days ago"
    elif diff < 30:
        weeks = diff // 7
        return f"{weeks} week{'s' if weeks > 1 else ''} ago"
    else:
        months = diff // 30
        return f"{months} month{'s' if months > 1 else ''} ago"


def get_word_count(text: str) -> int:
    """
    Count the number of words in a text.

    Args:
        text: The text to count

    Returns:
        Word count
    """
    if not text:
        return 0
    return len(text.split())


def truncate_text(text: str, max_length: int = 100) -> str:
    """
    Truncate text to a maximum length.

    Args:
        text: The text to truncate
        max_length: Maximum length

    Returns:
        Truncated text with ellipsis if needed
    """
    if not text:
        return ""
    if len(text) <= max_length:
        return text
    return text[:max_length].rsplit(' ', 1)[0] + "..."