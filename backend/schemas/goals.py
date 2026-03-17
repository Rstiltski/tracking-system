"""
Goal Schemas

Pydantic models for goal request/response validation.

Based on the existing Goal model in tracking_app/models.py

Phase 13: Decoupled Architecture Migration
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class GoalBase(BaseModel):
    """Base goal schema with common fields."""
    
    title: str = Field(..., min_length=1, max_length=200, description="Goal title")
    description: str = Field(default="", max_length=1000, description="Optional description")
    target: float = Field(default=0.0, ge=0, description="Target value")
    unit: str = Field(default="", description="Unit of measurement")
    deadline: Optional[datetime] = Field(None, description="Goal deadline (optional)")


class GoalCreate(GoalBase):
    """
    Schema for creating a new goal.
    
    Used in POST /api/goals request body.
    """
    pass


class GoalUpdate(BaseModel):
    """
    Schema for updating an existing goal.
    
    All fields are optional - only provided fields will be updated.
    
    Used in PUT /api/goals/{id} request body.
    """
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    target: Optional[float] = Field(None, ge=0)
    current: Optional[float] = Field(None, ge=0)
    unit: Optional[str] = None
    deadline: Optional[datetime] = None
    completed: Optional[bool] = None


class GoalProgressUpdate(BaseModel):
    """Schema for updating goal progress."""
    current: float = Field(..., ge=0, description="Current progress value")


class GoalResponse(GoalBase):
    """
    Schema for goal response.
    
    Used in GET /api/goals response body.
    """
    id: str = Field(..., description="Unique goal identifier")
    current: float = Field(default=0.0, description="Current progress")
    completed: bool = Field(default=False, description="Whether goal is completed")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True


class GoalListResponse(BaseModel):
    """
    Schema for list of goals response.
    
    Used in GET /api/goals response body.
    """
    goals: List[GoalResponse] = Field(default_factory=list, description="List of goals")
    total: int = Field(..., description="Total number of goals")
