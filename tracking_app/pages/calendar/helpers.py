"""
Helper functions for the Calendar page.

Contains utility functions for calendar calculations and data fetching.
"""

import streamlit as st
from datetime import date, timedelta
from typing import Dict, List, Any, Optional

from .constants import (
    get_month_name,
    WEEKDAY_LABELS,
    COMPLETION_NONE,
    MAX_DETAIL_ITEMS,
)


def get_month_calendar_dates(view_date: date) -> tuple[date, date, List[date]]:
    """
    Get calendar dates for a month view.
    
    Args:
        view_date: Any date in the month to view
        
    Returns:
        Tuple of (first_day, last_day, dates_list)
    """
    # First day of month
    first_day = view_date.replace(day=1)
    
    # Last day of month
    if view_date.month == 12:
        last_day = view_date.replace(year=view_date.year + 1, month=1, day=1) - timedelta(days=1)
    else:
        last_day = view_date.replace(month=view_date.month + 1, day=1) - timedelta(days=1)
    
    # Calculate calendar grid dates (starting from Monday of first week)
    # Find first Monday before or on first day of month
    first_weekday = first_day.weekday()  # 0=Monday, 6=Sunday
    calendar_start = first_day - timedelta(days=first_weekday)
    
    # Generate 6 weeks of dates (42 days)
    dates = []
    current = calendar_start
    for _ in range(42):
        dates.append(current)
        current += timedelta(days=1)
    
    return first_day, last_day, dates


@st.cache_data(ttl=300, show_spinner=False)
def get_month_completion_data(
    storage: Any,
    habit_ids: List[str],
    dates: List[date]
) -> Dict[date, Dict[str, Any]]:
    """
    Get completion data for each date in the calendar.
    
    Args:
        storage: Storage instance
        habit_ids: List of habit IDs
        dates: List of dates to fetch
        
    Returns:
        Dict mapping date to completion data
    """
    if not habit_ids or not dates:
        return {}
    
    completion_data = {}
    
    # Get all entries for the date range
    min_date = min(dates)
    max_date = max(dates)
    
    # Build completion data for each date
    for d in dates:
        completed_count = 0
        total_habits = len(habit_ids)
        
        for habit_id in habit_ids:
            entry = storage.get_habit_entry(habit_id, d)
            if entry and hasattr(entry, 'completed') and entry.completed:
                completed_count += 1
            elif entry and hasattr(entry, 'value') and entry.value > 0:
                completed_count += 1
        
        rate = completed_count / total_habits if total_habits > 0 else COMPLETION_NONE
        
        completion_data[d] = {
            "completed": completed_count,
            "total": total_habits,
            "rate": rate,
            "is_future": d > date.today(),
            "is_today": d == date.today(),
        }
    
    return completion_data


def get_day_detail_data(
    storage: Any,
    selected_date: date,
    habit_ids: List[str]
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Get detailed data for a selected day.
    
    Args:
        storage: Storage instance
        selected_date: Date to get details for
        habit_ids: List of habit IDs
        
    Returns:
        Dict with habits, tasks, goals data
    """
    result = {
        "habits": [],
        "tasks": [],
        "goals": [],
    }
    
    # Get habits completed that day
    habits = storage.get_habits()
    for habit in habit_ids[:MAX_DETAIL_ITEMS]:
        entry = storage.get_habit_entry(habit.id, selected_date)
        if entry:
            is_completed = (hasattr(entry, 'completed') and entry.completed) or \
                          (hasattr(entry, 'value') and entry.value > 0)
            result["habits"].append({
                "id": habit.id,
                "name": habit.name,
                "icon": getattr(habit, 'icon', '🎯'),
                "completed": is_completed,
            })
    
    return result


def navigate_month(current: date, direction: int) -> date:
    """
    Navigate to previous/next month.
    
    Args:
        current: Current view date
        direction: -1 for previous, 1 for next
        
    Returns:
        New date in target month
    """
    month = current.month + direction
    year = current.year
    
    if month < 1:
        month = 12
        year -= 1
    elif month > 12:
        month = 1
        year += 1
    
    # Keep the same day, but clamp to valid range
    import calendar
    max_day = calendar.monthrange(year, month)[1]
    day = min(current.day, max_day)
    
    return date(year, month, day)


def format_date_display(d: date) -> str:
    """Format date for display."""
    return d.strftime("%B %d, %Y")
