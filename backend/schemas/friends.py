"""
Friends API Schemas

Pydantic models for friends/social validation and serialization.

Phase 13: Decoupled Architecture - Backend Schemas
"""

from pydantic import BaseModel, Field
from typing import List, Optional


class FriendBase(BaseModel):
    """Base schema for friends."""
    pass


class FriendResponse(BaseModel):
    """Schema for friend response."""
    id: str = Field(description="Friend relationship ID")
    user_id: str = Field(description="User ID")
    friend_id: str = Field(description="Friend's user ID")
    friend_name: str = Field(default="", description="Friend's display name")
    status: str = Field(default="pending", description="Friend status")
    created_at: Optional[str] = None

    class Config:
        from_attributes = True


class FriendFeedItem(BaseModel):
    """Schema for friend activity feed item."""
    id: str
    friend_id: str
    friend_name: str
    action_type: str
    action_description: str
    timestamp: Optional[str] = None


class FriendRequestResponse(BaseModel):
    """Schema for friend request response."""
    id: str
    from_user_id: str
    from_user_name: str
    status: str
    created_at: Optional[str] = None
