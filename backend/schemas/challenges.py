"""
Challenges API Schemas

Pydantic models for challenge validation and serialization.

Phase 13: Decoupled Architecture - Backend Schemas
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime, date


class ChallengeBase(BaseModel):
    """Base schema for challenges."""
    name: str = Field(description="Challenge name")
    description: str = Field(default="", description="Challenge description")
    target: int = Field(description="Target value to achieve")
    unit: str = Field(default="days", description="Unit of measurement")
    start_date: Optional[date] = Field(default=None, description="Start date")
    end_date: Optional[date] = Field(default=None, description="End date")
    is_public: bool = Field(default=False, description="Public challenge")


class ChallengeCreate(ChallengeBase):
    """Schema for creating a challenge."""
    pass


class ChallengeUpdate(BaseModel):
    """Schema for updating a challenge."""
    name: Optional[str] = None
    description: Optional[str] = None
    target: Optional[int] = None
    end_date: Optional[date] = None
    status: Optional[str] = None


class ChallengeResponse(ChallengeBase):
    """Schema for challenge response."""
    id: str = Field(description="Unique identifier")
    creator_id: str = Field(description="Creator user ID")
    status: str = Field(description="Challenge status")
    participants_count: int = Field(default=0, description="Number of participants")
    created_at: Optional[str] = None

    class Config:
        from_attributes = True


class ChallengeParticipantResponse(BaseModel):
    """Schema for challenge participant."""
    id: str
    user_id: str
    challenge_id: str
    progress: int = 0
    joined_at: Optional[str] = None
