"""
Helper functions for the Habit Reminders page.

Contains data retrieval and processing functions.
"""

from datetime import time
from typing import Dict, Any, List, Optional

from .constants import (
    DEFAULT_REMINDER_TIME_HOUR,
    DEFAULT_REMINDER_TIME_MINUTE,
    DAYS_OF_WEEK,
)


def parse_time(time_str: str) -> time:
    """
    Parse time string to time object.
    
    Args:
        time_str: Time string in HH:MM format
        
    Returns:
        time object
    """
    try:
        parts = time_str.split(':')
        return time(int(parts[0]), int(parts[1]))
    except (ValueError, IndexError):
        return time(DEFAULT_REMINDER_TIME_HOUR, DEFAULT_REMINDER_TIME_MINUTE)


def format_time(t: time) -> str:
    """
    Format time object to string.
    
    Args:
        t: time object
        
    Returns:
        Formatted time string
    """
    return t.strftime("%H:%M")


def get_user_habits(user_id: str, storage) -> List[Dict[str, Any]]:
    """
    Get user's habits from database.
    
    Args:
        user_id: User ID
        storage: Storage instance
        
    Returns:
        List of habit dictionaries
    """
    if storage is None:
        return _get_sample_habits()
    
    try:
        habits = storage.get_habits(user_id)
        return [
            {
                'id': h.id,
                'name': h.name,
                'reminder_enabled': getattr(h, 'reminder_enabled', True),
                'reminder_time': getattr(h, 'reminder_time', '08:00'),
                'smart_scheduling': getattr(h, 'smart_scheduling', False),
                'smart_time': getattr(h, 'smart_time', None),
                'confidence': getattr(h, 'confidence', 0),
                'days': getattr(h, 'days', DAYS_OF_WEEK),
            }
            for h in habits
        ]
    except Exception:
        return _get_sample_habits()


def get_today_reminders(user_id: str, scheduler) -> List[Dict[str, Any]]:
    """
    Get today's scheduled reminders.
    
    Args:
        user_id: User ID
        scheduler: Notification scheduler instance
        
    Returns:
        List of reminder dictionaries
    """
    if scheduler is None:
        return _get_sample_reminders()
    
    try:
        reminders = scheduler.get_todays_reminders(user_id)
        return [
            {
                'id': r.id,
                'habit_name': r.habit_name,
                'time': format_time(r.scheduled_time),
                'status': r.status,
            }
            for r in reminders
        ]
    except Exception:
        return _get_sample_reminders()


def _get_sample_habits() -> List[Dict[str, Any]]:
    """Get sample habits for demonstration."""
    return [
        {
            'id': 'habit-1',
            'name': 'Morning Meditation',
            'reminder_enabled': True,
            'reminder_time': '07:00',
            'smart_scheduling': True,
            'smart_time': '06:45',
            'confidence': 0.85,
            'days': DAYS_OF_WEEK
        },
        {
            'id': 'habit-2',
            'name': 'Drink Water',
            'reminder_enabled': True,
            'reminder_time': '09:00',
            'smart_scheduling': False,
            'days': DAYS_OF_WEEK
        },
        {
            'id': 'habit-3',
            'name': 'Evening Journal',
            'reminder_enabled': True,
            'reminder_time': '21:00',
            'smart_scheduling': True,
            'smart_time': '20:30',
            'confidence': 0.72,
            'days': DAYS_OF_WEEK
        },
    ]


def _get_sample_reminders() -> List[Dict[str, Any]]:
    """Get sample reminders for demonstration."""
    return [
        {
            'id': 'rem-1',
            'habit_name': 'Morning Meditation',
            'time': '07:00',
            'status': 'sent'
        },
        {
            'id': 'rem-2',
            'habit_name': 'Drink Water',
            'time': '09:00',
            'status': 'scheduled'
        },
        {
            'id': 'rem-3',
            'habit_name': 'Evening Journal',
            'time': '21:00',
            'status': 'scheduled'
        },
    ]