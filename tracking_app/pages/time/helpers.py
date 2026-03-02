"""
Helper functions for the Time page.

Contains utility functions for time formatting and calculations.
"""

import time as time_module
from datetime import datetime, date, timedelta
from typing import Dict, List, Optional


def format_duration(seconds: int) -> str:
    """
    Format seconds into HH:MM:SS.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        Formatted string like "01:30:45"
    """
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def format_hours(hours: float) -> str:
    """
    Format hours into readable string.
    
    Args:
        hours: Duration in hours
        
    Returns:
        Formatted string like "1.5h" or "45m"
    """
    if hours < 1:
        return f"{int(hours * 60)}m"
    return f"{hours:.1f}h"


def get_current_elapsed(timer_running: bool, timer_start: Optional[float], timer_elapsed: int) -> int:
    """
    Get current elapsed time including running timer.
    
    Args:
        timer_running: Whether timer is currently running
        timer_start: Unix timestamp when timer started
        timer_elapsed: Previously elapsed seconds
        
    Returns:
        Total elapsed seconds
    """
    if timer_running and timer_start:
        additional = int(time_module.time() - timer_start)
        return timer_elapsed + additional
    return timer_elapsed


def calculate_xp(seconds: int) -> int:
    """
    Calculate XP earned from time tracked.
    
    Args:
        seconds: Duration in seconds
        
    Returns:
        XP points earned
    """
    from .constants import XP_PER_MINUTE, XP_MINIMUM
    
    xp = max(XP_MINIMUM, int(seconds / 60))  # 1 XP per minute, min 5
    return xp


def calculate_xp_for_hours(hours: float) -> int:
    """
    Calculate XP earned from hours tracked.
    
    Args:
        hours: Duration in hours
        
    Returns:
        XP points earned
    """
    from .constants import XP_PER_HOUR
    
    return int(hours * XP_PER_HOUR)


def aggregate_daily_totals(entries: List[Dict], week_start: date, today: date) -> Dict[date, float]:
    """
    Aggregate time entries by day.
    
    Args:
        entries: List of time entry dictionaries
        week_start: Start date of the week
        today: Current date
        
    Returns:
        Dictionary mapping dates to total hours
    """
    daily_totals = {}
    
    for i in range(7):
        day = week_start + timedelta(days=i)
        daily_totals[day] = 0
    
    for entry in entries:
        entry_date = date.fromisoformat(entry['date'])
        if week_start <= entry_date <= today:
            daily_totals[entry_date] += entry['duration_hours']
    
    return daily_totals


def aggregate_category_totals(entries: List[Dict], week_start: date, today: date) -> Dict[str, float]:
    """
    Aggregate time entries by category.
    
    Args:
        entries: List of time entry dictionaries
        week_start: Start date of the week
        today: Current date
        
    Returns:
        Dictionary mapping categories to total hours
    """
    category_totals = {}
    
    for entry in entries:
        entry_date = date.fromisoformat(entry['date'])
        if week_start <= entry_date <= today:
            cat = entry['category']
            if cat not in category_totals:
                category_totals[cat] = 0
            category_totals[cat] += entry['duration_hours']
    
    return category_totals