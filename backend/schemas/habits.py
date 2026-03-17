"""
Habit Schemas

Pydantic models for habit request/response validation.
These models validate API requests and format responses.

Based on the existing Habit model in tracking_app/models.py

Phase 13: Decoupled Architecture Migration
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class HabitBase(BaseModel):
    """Base habit schema with common fields."""
    
    name: str = Field(..., min_length=1, max_length=200, description="Habit name")
    description: str = Field(default="", max_length=1000, description="Optional description")
    frequency: str = Field(default="daily", description="Frequency type: daily, weekly, custom")
    icon: str = Field(default="🎯", description="Emoji icon")
    color: str = Field(default="#6366f1", description="Hex color code")
    habit_type: str = Field(default="boolean", description="boolean or numerical")
    category: str = Field(default="general", description="Habit category")
    target_value: float = Field(default=0.0, description="Target for numerical habits")
    target_type: str = Field(default="at_least", description="at_least or at_most")


class HabitCreate(HabitBase):
    """
    Schema for creating a new habit.
    
    Used in POST /api/habits request body.
    """
    pass


class HabitUpdate(BaseModel):
    """
    Schema for updating an existing habit.
    
    All fields are optional - only provided fields will be updated.
    
    Used in PUT /api/habits/{id} request body.
    """
    name: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    frequency: Optional[str] = None
    icon: Optional[str] = None
    color: Optional[str] = None
    habit_type: Optional[str] = None
    category: Optional[str] = None
    target_value: Optional[float] = None
    target_type: Optional[str] = None
    archived: Optional[bool] = None


class HabitResponse(HabitBase):
    """
    Schema for habit response.
    
    Used in GET /api/habits response body.
    All fields are included for complete habit information.
    """
    id: str = Field(..., description="Unique habit identifier")
    archived: bool = Field(default=False, description="Whether habit is archived")
    frequency_data: List[int] = Field(default=[1, 1], description="Custom frequency data")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True


class HabitListResponse(BaseModel):
    """
    Schema for list of habits response.
    
    Used in GET /api/habits response body.
    """
    habits: List[HabitResponse] = Field(default_factory=list, description="List of habits")
    total: int = Field(..., description="Total number of habits")
