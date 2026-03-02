"""
Helper functions for the Friends page.

Contains utility functions for friend management and activity formatting.
"""

from .constants import (
    ACTIVITY_TYPE_COMPLETION,
    ACTIVITY_TYPE_STREAK,
    ACTIVITY_TYPE_ACHIEVEMENT,
)


def format_activity_message(activity: dict) -> str:
    """
    Format an activity into a display message.
    
    Args:
        activity: Activity dictionary with user_name, activity_type, etc.
        
    Returns:
        Formatted message string
    """
    user_name = activity.get('user_name', 'Friend')
    activity_type = activity.get('activity_type', '')
    habit_name = activity.get('habit_name', '')
    
    if activity_type == ACTIVITY_TYPE_COMPLETION:
        return f"✅ {user_name} completed **{habit_name}**"
    elif activity_type == ACTIVITY_TYPE_STREAK:
        days = activity.get('details', {}).get('days', 0)
        return f"🔥 {user_name} reached a {days}-day streak on **{habit_name}**"
    elif activity_type == ACTIVITY_TYPE_ACHIEVEMENT:
        achievement = activity.get('details', {}).get('achievement', '')
        return f"🏆 {user_name} earned **{achievement}**"
    else:
        return f"{user_name} shared an activity"


def get_friend_manager():
    """
    Get or create the FriendManager instance.
    
    Returns:
        FriendManager instance
    """
    from brain.social.friend_manager import FriendManager
    from tracking_app.storage import get_storage
    
    storage = get_storage()
    user_id = "user-123"  # Demo user ID
    return FriendManager(storage, user_id)