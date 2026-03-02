"""
Helper functions for the Task Alerts page.
"""

from typing import List, Dict, Any, Optional
from datetime import time, datetime, timedelta

from .constants import (
    URGENCY_COLORS,
    PRIORITY_ICONS,
    CHANNEL_OPTIONS,
    ALL_CHANNELS_OPTION,
)


def get_urgency_icon(urgency: str) -> str:
    """
    Get icon for urgency level.
    
    Args:
        urgency: Urgency level string
        
    Returns:
        Emoji icon for the urgency
    """
    return URGENCY_COLORS.get(urgency, '⚪')


def get_priority_icon(priority: str) -> str:
    """
    Get icon for priority level.
    
    Args:
        priority: Priority level string
        
    Returns:
        Emoji icon for the priority
    """
    return PRIORITY_ICONS.get(priority, '⚪')


def get_channel_options_with_all() -> List[str]:
    """
    Get channel options including 'All Channels'.
    
    Returns:
        List of channel options
    """
    return CHANNEL_OPTIONS + [ALL_CHANNELS_OPTION]


def format_time_for_display(t: time) -> str:
    """
    Format time for display.
    
    Args:
        t: Time object
        
    Returns:
        Formatted time string
    """
    return t.strftime("%I:%M %p")


def get_mock_today_alerts(user_id: str) -> List[Dict[str, Any]]:
    """
    Get mock today's task alerts for preview.
    
    Args:
        user_id: User ID
        
    Returns:
        List of alert dictionaries
    """
    return [
        {
            'id': 'alert-1',
            'task_name': 'Complete project proposal',
            'due_date': 'Today, 5:00 PM',
            'alert_time': '4:00 PM',
            'urgency': 'high',
            'channel': 'All Channels',
            'status': 'pending'
        },
        {
            'id': 'alert-2',
            'task_name': 'Review team feedback',
            'due_date': 'Tomorrow, 10:00 AM',
            'alert_time': '9:00 AM',
            'urgency': 'medium',
            'channel': 'Browser',
            'status': 'scheduled'
        },
        {
            'id': 'alert-3',
            'task_name': 'Update documentation',
            'due_date': 'Yesterday',
            'alert_time': '9:00 AM',
            'urgency': 'critical',
            'channel': 'All Channels',
            'status': 'sent'
        },
    ]


def get_default_priority_settings() -> Dict[str, Dict[str, Any]]:
    """
    Get default priority-based alert settings.
    
    Returns:
        Dictionary of priority settings
    """
    return {
        'high': {'enabled': True, 'channel': 'All Channels'},
        'medium': {'enabled': True, 'channel': 'Browser'},
        'low': {'enabled': False, 'channel': 'Email'},
    }


def calculate_urgency_from_hours(hours_until_deadline: int) -> str:
    """
    Calculate urgency level from hours until deadline.
    
    Args:
        hours_until_deadline: Hours until the deadline
        
    Returns:
        Urgency level string
    """
    if hours_until_deadline < 0:
        return 'critical'
    elif hours_until_deadline < 1:
        return 'critical'
    elif hours_until_deadline < 4:
        return 'high'
    elif hours_until_deadline < 24:
        return 'medium'
    else:
        return 'low'