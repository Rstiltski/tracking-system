"""
Helper functions for the Tasks page.

Contains utility functions for priorities, dates, and XP calculations.
"""

from datetime import datetime, date
from typing import Optional

from .constants import (
    PRIORITY_COLORS,
    PRIORITY_ICONS,
    XP_REWARDS,
    BASE_XP_PER_LEVEL,
    XP_INCREMENT_PER_LEVEL,
)


def get_priority_color(priority: str) -> str:
    """
    Get color for priority level.
    
    Args:
        priority: Priority level string
        
    Returns:
        Hex color code
    """
    return PRIORITY_COLORS.get(priority, "#6b7280")


def get_priority_icon(priority: str) -> str:
    """
    Get icon for priority level.
    
    Args:
        priority: Priority level string
        
    Returns:
        Emoji icon
    """
    return PRIORITY_ICONS.get(priority, "⚪")


def is_overdue(due_date: Optional[datetime]) -> bool:
    """
    Check if a task is overdue.
    
    Args:
        due_date: Due date datetime
        
    Returns:
        True if overdue
    """
    if not due_date:
        return False
    return due_date.date() < date.today()


def is_due_today(due_date: Optional[datetime]) -> bool:
    """
    Check if a task is due today.
    
    Args:
        due_date: Due date datetime
        
    Returns:
        True if due today
    """
    if not due_date:
        return False
    return due_date.date() == date.today()


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
    return BASE_XP_PER_LEVEL + (level - 2) * XP_INCREMENT_PER_LEVEL


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


def get_xp_reward(priority: str) -> int:
    """
    Get XP reward for completing a task.
    
    Args:
        priority: Task priority
        
    Returns:
        XP points to award
    """
    return XP_REWARDS.get(priority, 10)


def get_task_sort_key(task):
    """
    Get sort key for task ordering.
    
    Sort order: completed last, then overdue first, then by priority,
    then by due date.
    
    Args:
        task: Task object
        
    Returns:
        Tuple for sorting
    """
    priority_score = {"high": 0, "medium": 1, "low": 2}.get(task.priority, 3)
    overdue_score = 0 if is_overdue(task.due_date) and not task.completed else 1
    due_score = task.due_date.timestamp() if task.due_date else float('inf')
    
    return (task.completed, overdue_score, priority_score, due_score)