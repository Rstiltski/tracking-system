"""
Helper functions for the Notification Settings page.
"""

from datetime import time
from typing import Optional, Dict, Any

from .constants import TYPE_ICONS, DEFAULT_QUIET_HOURS_START, DEFAULT_QUIET_HOURS_END


def get_type_icon(notification_type: str) -> str:
    """
    Get icon for notification type.
    
    Args:
        notification_type: Type of notification
        
    Returns:
        Icon emoji string
    """
    return TYPE_ICONS.get(notification_type, '🔔')


def get_default_quiet_hours_start() -> time:
    """Get default quiet hours start time."""
    return time(*DEFAULT_QUIET_HOURS_START)


def get_default_quiet_hours_end() -> time:
    """Get default quiet hours end time."""
    return time(*DEFAULT_QUIET_HOURS_END)


def calculate_success_rate(stats: Dict[str, Any]) -> float:
    """
    Calculate notification delivery success rate.
    
    Args:
        stats: Statistics dictionary from preference manager
        
    Returns:
        Success rate as percentage
    """
    by_status = stats.get('by_status', {})
    sent = by_status.get('sent', 0)
    failed = by_status.get('failed', 0)
    total = sent + failed
    
    if total > 0:
        return (sent / total) * 100
    return 0.0


def format_channel_status(channel: str, status: str) -> str:
    """
    Format channel and status for display.
    
    Args:
        channel: Notification channel name
        status: Delivery status
        
    Returns:
        Formatted status string
    """
    return f"Channel: `{channel}` | Status: `{status}`"