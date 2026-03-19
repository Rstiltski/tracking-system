"""
Privacy Settings API Schemas

Pydantic models for privacy settings validation and serialization.

Phase 13: Decoupled Architecture - Backend Schemas
"""

from pydantic import BaseModel, Field
from typing import Optional, List


class PrivacySettingsBase(BaseModel):
    """Base schema for privacy settings."""
    share_habits_with_friends: bool = Field(default=False, description="Share habit progress with friends")
    share_achievements: bool = Field(default=True, description="Share achievements publicly")
    share_stats: bool = Field(default=False, description="Share statistics on leaderboards")
    allow_friend_requests: bool = Field(default=True, description="Allow friend requests")
    show_on_public_leaderboards: bool = Field(default=False, description="Show on public leaderboards")
    data_collection_enabled: bool = Field(default=True, description="Allow anonymized data collection")
    analytics_enabled: bool = Field(default=True, description="Allow usage analytics")
    streak_visible: bool = Field(default=True, description="Show streak to friends")
    xp_visible: bool = Field(default=True, description="Show XP to friends")
    level_visible: bool = Field(default=True, description="Show level to friends")
    insights_visible: bool = Field(default=True, description="Share insights with accountability partners")


class PrivacySettingsUpdate(BaseModel):
    """Schema for updating privacy settings."""
    share_habits_with_friends: Optional[bool] = None
    share_achievements: Optional[bool] = None
    share_stats: Optional[bool] = None
    allow_friend_requests: Optional[bool] = None
    show_on_public_leaderboards: Optional[bool] = None
    data_collection_enabled: Optional[bool] = None
    analytics_enabled: Optional[bool] = None
    streak_visible: Optional[bool] = None
    xp_visible: Optional[bool] = None
    level_visible: Optional[bool] = None
    insights_visible: Optional[bool] = None


class PrivacySettingsResponse(PrivacySettingsBase):
    """Schema for privacy settings response."""
    user_id: str = Field(description="User ID")

    class Config:
        from_attributes = True


class DataExportRequest(BaseModel):
    """Schema for data export request."""
    format: str = Field(default="json", description="Export format: json, csv, sqlite")
    include: Optional[List[str]] = Field(
        default=None,
        description="Data types to include: habits, tasks, health, finances, journal, diary"
    )


class DataExportResponse(BaseModel):
    """Schema for data export response."""
    file_path: str
    format: str
    record_counts: dict
