"""
Notifications API Schemas

Pydantic models for notification preferences validation and serialization.

Phase 13: Decoupled Architecture - Backend Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class NotificationPreferencesBase(BaseModel):
    """Base schema for notification preferences."""
    enabled: bool = Field(default=True, description="Enable notifications")
    habit_reminders: bool = Field(default=True, description="Habit reminder notifications")
    task_deadlines: bool = Field(default=True, description="Task deadline notifications")
    goal_alerts: bool = Field(default=True, description="Goal milestone notifications")
    achievement_unlocks: bool = Field(default=True, description="Achievement unlock notifications")
    friend_activity: bool = Field(default=False, description="Friend activity notifications")
    weekly_review: bool = Field(default=True, description="Weekly review notifications")
    burnout_warnings: bool = Field(default=True, description="Burnout warning notifications")
    quiet_hours_enabled: bool = Field(default=False, description="Enable quiet hours")
    quiet_hours_start: Optional[str] = Field(default="22:00", description="Quiet hours start time (HH:MM)")
    quiet_hours_end: Optional[str] = Field(default="08:00", description="Quiet hours end time (HH:MM)")
    notification_sound: bool = Field(default=True, description="Enable notification sounds")
    desktop_notifications: bool = Field(default=True, description="Enable desktop notifications")


class NotificationPreferencesUpdate(BaseModel):
    """Schema for updating notification preferences."""
    enabled: Optional[bool] = None
    habit_reminders: Optional[bool] = None
    task_deadlines: Optional[bool] = None
    goal_alerts: Optional[bool] = None
    achievement_unlocks: Optional[bool] = None
    friend_activity: Optional[bool] = None
    weekly_review: Optional[bool] = None
    burnout_warnings: Optional[bool] = None
    quiet_hours_enabled: Optional[bool] = None
    quiet_hours_start: Optional[str] = None
    quiet_hours_end: Optional[str] = None
    notification_sound: Optional[bool] = None
    desktop_notifications: Optional[bool] = None


class NotificationPreferencesResponse(NotificationPreferencesBase):
    """Schema for notification preferences response."""
    user_id: str = Field(description="User ID")

    class Config:
        from_attributes = True


class NotificationTestRequest(BaseModel):
    """Schema for testing notifications."""
    notification_type: str = Field(description="Type of notification to test")


class NotificationResponse(BaseModel):
    """Schema for notification response."""
    id: str
    title: str
    message: str
    notification_type: str
    created_at: Optional[str] = None
    read: bool = False


class NotificationListResponse(BaseModel):
    """Schema for notification list response."""
    notifications: List[NotificationResponse]
    unread_count: int
    total: int
