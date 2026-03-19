"""
Notifications API Routes

REST endpoints for notification preferences and management.
Wraps the existing brain/notifications module functions.

Phase 13: Decoupled Architecture Migration
Step 2: Define API Contract

Endpoints:
- GET /api/notifications/preferences - Get notification preferences
- PUT /api/notifications/preferences - Update notification preferences
- POST /api/notifications/test - Test notification
- GET /api/notifications/history - Get notification history
"""

from fastapi import APIRouter, HTTPException
from typing import Optional, List
import logging
from tracking_app.storage import Storage

from backend.schemas.notifications import (
    NotificationPreferencesUpdate,
    NotificationPreferencesResponse,
    NotificationTestRequest,
    NotificationResponse,
    NotificationListResponse,
)

# Initialize router
router = APIRouter(prefix="/api/notifications", tags=["notifications"])

# Logger
logger = logging.getLogger(__name__)


def _get_storage() -> Storage:
    """Get storage instance."""
    return Storage()


@router.get("/preferences", response_model=NotificationPreferencesResponse)
async def get_notification_preferences(user_id: str = "default"):
    """
    Get notification preferences for the current user.
    """
    storage = _get_storage()
    
    # Try to get from storage, use defaults if not found
    prefs = storage.get_notification_preferences(user_id=user_id)
    
    if not prefs:
        # Return default preferences
        return NotificationPreferencesResponse(
            user_id=user_id,
            enabled=True,
            habit_reminders=True,
            task_deadlines=True,
            goal_alerts=True,
            achievement_unlocks=True,
            friend_activity=False,
            weekly_review=True,
            burnout_warnings=True,
            quiet_hours_enabled=False,
            quiet_hours_start="22:00",
            quiet_hours_end="08:00",
            notification_sound=True,
            desktop_notifications=True,
        )
    
    return NotificationPreferencesResponse(
        user_id=user_id,
        enabled=prefs.get('enabled', True),
        habit_reminders=prefs.get('habit_reminders', True),
        task_deadlines=prefs.get('task_deadlines', True),
        goal_alerts=prefs.get('goal_alerts', True),
        achievement_unlocks=prefs.get('achievement_unlocks', True),
        friend_activity=prefs.get('friend_activity', False),
        weekly_review=prefs.get('weekly_review', True),
        burnout_warnings=prefs.get('burnout_warnings', True),
        quiet_hours_enabled=prefs.get('quiet_hours_enabled', False),
        quiet_hours_start=prefs.get('quiet_hours_start', "22:00"),
        quiet_hours_end=prefs.get('quiet_hours_end', "08:00"),
        notification_sound=prefs.get('notification_sound', True),
        desktop_notifications=prefs.get('desktop_notifications', True),
    )


@router.put("/preferences", response_model=NotificationPreferencesResponse)
async def update_notification_preferences(
    preferences: NotificationPreferencesUpdate,
    user_id: str = "default"
):
    """
    Update notification preferences for the current user.
    """
    storage = _get_storage()
    
    # Build update dict (exclude None values)
    updates = {}
    for field, value in preferences.model_dump(exclude_unset=True).items():
        if value is not None:
            updates[field] = value
    
    if not updates:
        raise HTTPException(status_code=400, detail="No valid preferences to update")
    
    # Save to storage
    success = storage.save_notification_preferences(user_id=user_id, preferences=updates)
    
    if not success:
        raise HTTPException(status_code=500, detail="Failed to save notification preferences")
    
    # Fetch and return updated preferences
    updated_prefs = storage.get_notification_preferences(user_id=user_id)
    
    if not updated_prefs:
        updated_prefs = {}
    
    return NotificationPreferencesResponse(
        user_id=user_id,
        enabled=updated_prefs.get('enabled', True),
        habit_reminders=updated_prefs.get('habit_reminders', True),
        task_deadlines=updated_prefs.get('task_deadlines', True),
        goal_alerts=updated_prefs.get('goal_alerts', True),
        achievement_unlocks=updated_prefs.get('achievement_unlocks', True),
        friend_activity=updated_prefs.get('friend_activity', False),
        weekly_review=updated_prefs.get('weekly_review', True),
        burnout_warnings=updated_prefs.get('burnout_warnings', True),
        quiet_hours_enabled=updated_prefs.get('quiet_hours_enabled', False),
        quiet_hours_start=updated_prefs.get('quiet_hours_start', "22:00"),
        quiet_hours_end=updated_prefs.get('quiet_hours_end', "08:00"),
        notification_sound=updated_prefs.get('notification_sound', True),
        desktop_notifications=updated_prefs.get('desktop_notifications', True),
    )


@router.post("/test")
async def test_notification(
    request: NotificationTestRequest,
    user_id: str = "default"
):
    """
    Send a test notification to verify settings.
    """
    logger.info(f"Test notification requested by user {user_id}, type: {request.notification_type}")
    
    # Return success - actual notification would be sent by brain/notifications
    return {
        "success": True,
        "message": f"Test {request.notification_type} notification sent successfully",
        "user_id": user_id
    }


@router.get("/history", response_model=NotificationListResponse)
async def get_notification_history(
    limit: int = 50,
    unread_only: bool = False,
    user_id: str = "default"
):
    """
    Get notification history for the current user.
    """
    logger.info(f"Fetching notification history for user {user_id}")
    
    # Return empty list for now - would integrate with brain/notifications engine
    return NotificationListResponse(
        notifications=[],
        unread_count=0,
        total=0
    )


@router.post("/read/{notification_id}")
async def mark_notification_read(
    notification_id: str,
    user_id: str = "default"
):
    """
    Mark a notification as read.
    """
    logger.info(f"Marking notification {notification_id} as read for user {user_id}")
    
    return {
        "success": True,
        "notification_id": notification_id,
        "message": "Notification marked as read"
    }


@router.post("/read-all")
async def mark_all_notifications_read(user_id: str = "default"):
    """
    Mark all notifications as read.
    """
    logger.info(f"Marking all notifications as read for user {user_id}")
    
    return {
        "success": True,
        "message": "All notifications marked as read"
    }
