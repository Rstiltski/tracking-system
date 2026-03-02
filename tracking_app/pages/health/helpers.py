"""
Helper functions for the Health page.

Contains utility functions for calculations and formatting.
"""

from typing import List, Optional
from collections import Counter

from tracking_app.models import HealthEntry

from .constants import MOOD_ICONS, MOOD_COLORS, MOOD_VALUES


def get_mood_icon(mood: str) -> str:
    """
    Get emoji for mood.
    
    Args:
        mood: Mood value string
        
    Returns:
        Emoji icon for the mood
    """
    return MOOD_ICONS.get(mood, "😐")


def get_mood_color(mood: str) -> str:
    """
    Get color for mood.
    
    Args:
        mood: Mood value string
        
    Returns:
        Hex color code for the mood
    """
    return MOOD_COLORS.get(mood, "#6b7280")


def get_mood_value(mood: str) -> int:
    """
    Get numeric value for mood (for charts).
    
    Args:
        mood: Mood value string
        
    Returns:
        Numeric value (1-4)
    """
    return MOOD_VALUES.get(mood, 2)


def calculate_average(entries: List[HealthEntry], field: str) -> Optional[float]:
    """
    Calculate average for a field.
    
    Args:
        entries: List of HealthEntry objects
        field: Field name to average
        
    Returns:
        Average value or None if no data
    """
    values = [getattr(e, field) for e in entries if getattr(e, field) is not None]
    if not values:
        return None
    return sum(values) / len(values)


def get_health_trend(entries: List[HealthEntry], field: str) -> str:
    """
    Get trend direction for a health metric.
    
    Args:
        entries: List of HealthEntry objects
        field: Field name to analyze
        
    Returns:
        Trend direction: "up", "down", or "stable"
    """
    if len(entries) < 2:
        return "stable"
    
    values = [(e.entry_date, getattr(e, field)) for e in entries if getattr(e, field) is not None]
    values.sort(key=lambda x: x[0])
    
    if len(values) < 2:
        return "stable"
    
    recent = values[-1][1]
    previous = values[-2][1]
    
    if recent > previous:
        return "up"
    elif recent < previous:
        return "down"
    return "stable"


def get_most_common_mood(entries: List[HealthEntry]) -> Optional[str]:
    """
    Get the most common mood from entries.
    
    Args:
        entries: List of HealthEntry objects
        
    Returns:
        Most common mood value or None
    """
    moods = [e.mood for e in entries if e.mood]
    if not moods:
        return None
    return Counter(moods).most_common(1)[0][0]


def format_trend_icon(trend: str) -> str:
    """
    Get icon for trend direction.
    
    Args:
        trend: Trend direction string
        
    Returns:
        Emoji icon for the trend
    """
    icons = {
        "up": "📈",
        "down": "📉",
        "stable": "➡️"
    }
    return icons.get(trend, "➡️")