"""
Helper functions for the Goal Alerts page.

Contains utility functions for goal alert data retrieval.
"""

from typing import List, Dict, Any

from .constants import DEFAULT_USER_ID


def get_user_goals(user_id: str = DEFAULT_USER_ID) -> List[Dict[str, Any]]:
    """
    Get user's goals from database.
    
    Args:
        user_id: User ID to fetch goals for
        
    Returns:
        List of goal dictionaries
    """
    # In real implementation, fetch from database
    return [
        {
            'id': 'goal-1',
            'name': 'Run 100 miles this month',
            'progress': 67,
            'deadline': 'Feb 28, 2026',
            'alerts_enabled': True,
            'milestones_enabled': True,
            'deadline_enabled': True
        },
        {
            'id': 'goal-2',
            'name': 'Save $1000',
            'progress': 45,
            'deadline': 'Mar 31, 2026',
            'alerts_enabled': True,
            'milestones_enabled': True,
            'deadline_enabled': True
        },
        {
            'id': 'goal-3',
            'name': 'Read 12 books this year',
            'progress': 25,
            'deadline': 'Dec 31, 2026',
            'alerts_enabled': True,
            'milestones_enabled': True,
            'deadline_enabled': False
        },
    ]


def get_recent_milestones(user_id: str = DEFAULT_USER_ID) -> List[Dict[str, Any]]:
    """
    Get recently celebrated milestones.
    
    Args:
        user_id: User ID to fetch milestones for
        
    Returns:
        List of milestone dictionaries
    """
    return [
        {
            'goal_name': 'Run 100 miles this month',
            'percentage': 50,
            'milestone': 'Halfway there!',
            'celebrated_at': '2 days ago'
        },
        {
            'goal_name': 'Save $1000',
            'percentage': 25,
            'milestone': 'Quarter way!',
            'celebrated_at': '1 week ago'
        },
    ]


def get_goal_progress(user_id: str = DEFAULT_USER_ID) -> List[Dict[str, Any]]:
    """
    Get goal progress data.
    
    Args:
        user_id: User ID to fetch progress for
        
    Returns:
        List of goal progress dictionaries
    """
    return [
        {
            'name': 'Run 100 miles this month',
            'progress': 67,
            'on_track': True
        },
        {
            'name': 'Save $1000',
            'progress': 45,
            'on_track': True
        },
        {
            'name': 'Read 12 books this year',
            'progress': 25,
            'on_track': False
        },
    ]