"""
Helper functions for the Goals page.

Contains utility functions for goal calculations and formatting.
"""

from datetime import datetime, date
from typing import Optional

from tracking_app.models import Goal

from .constants import STATUS_COLORS, OVERDUE_THRESHOLD, WARNING_DAYS_THRESHOLD


def get_xp_for_level(level: int) -> int:
    """
    Calculate XP required for a given level.
    
    Args:
        level: Target level
        
    Returns:
        XP required for that level
    """
    if level <= 1:
        return 0
    return 100 + (level - 2) * 150


def get_level_from_xp(xp: int) -> int:
    """
    Calculate level from total XP.
    
    Args:
        xp: Total XP points
        
    Returns:
        Current level
    """
    level = 1
    while xp >= get_xp_for_level(level + 1):
        level += 1
    return level


def get_days_remaining(deadline: Optional[datetime]) -> Optional[int]:
    """
    Get days remaining until deadline.
    
    Args:
        deadline: Deadline datetime
        
    Returns:
        Days remaining (negative if overdue), or None if no deadline
    """
    if not deadline:
        return None
    
    remaining = (deadline.date() - date.today()).days
    return remaining


def get_progress_status(goal: Goal) -> str:
    """
    Get status string for a goal.
    
    Args:
        goal: Goal object
        
    Returns:
        Human-readable status string
    """
    if goal.completed:
        return "✅ Completed"
    
    days = get_days_remaining(goal.deadline)
    
    if days is None:
        return f"📊 {goal.progress_percentage:.0f}% complete"
    
    if days < OVERDUE_THRESHOLD:
        return f"⚠️ Overdue by {abs(days)} days"
    elif days == 0:
        return "📅 Due today!"
    elif days <= WARNING_DAYS_THRESHOLD:
        return f"📅 {days} days left"
    else:
        return f"📊 {goal.progress_percentage:.0f}% • {days} days left"


def get_status_color(goal: Goal) -> str:
    """
    Get color for goal status.
    
    Args:
        goal: Goal object
        
    Returns:
        Hex color string
    """
    if goal.completed:
        return STATUS_COLORS["completed"]
    
    days = get_days_remaining(goal.deadline)
    
    if days is None:
        return STATUS_COLORS["active"]
    
    if days < OVERDUE_THRESHOLD:
        return STATUS_COLORS["overdue"]
    elif days <= WARNING_DAYS_THRESHOLD:
        return STATUS_COLORS["warning"]
    else:
        return STATUS_COLORS["active"]