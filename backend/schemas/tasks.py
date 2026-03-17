"""
Task Schemas

Pydantic models for task request/response validation.
These models validate API requests and format responses.

Based on the existing Task model in tracking_app/models.py

Phase 13: Decoupled Architecture Migration
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime


class TaskBase(BaseModel):
    """Base task schema with common fields."""
    
    title: str = Field(..., min_length=1, max_length=200, description="Task title")
    description: str = Field(default="", max_length=1000, description="Optional description")
    due_date: Optional[datetime] = Field(None, description="Due date (optional)")
    priority: str = Field(default="medium", description="Priority: low, medium, high, urgent")
    category: str = Field(default="", description="Category for grouping")


class TaskCreate(TaskBase):
    """
    Schema for creating a new task.
    
    Used in POST /api/tasks request body.
    """
    pass


class TaskUpdate(BaseModel):
    """
    Schema for updating an existing task.
    
    All fields are optional - only provided fields will be updated.
    
    Used in PUT /api/tasks/{id} request body.
    """
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    description: Optional[str] = Field(None, max_length=1000)
    due_date: Optional[datetime] = None
    priority: Optional[str] = None
    category: Optional[str] = None
    completed: Optional[bool] = None


class TaskResponse(TaskBase):
    """
    Schema for task response.
    
    Used in GET /api/tasks response body.
    All fields are included for complete task information.
    """
    id: str = Field(..., description="Unique task identifier")
    completed: bool = Field(default=False, description="Whether task is completed")
    completed_at: Optional[datetime] = Field(None, description="Completion timestamp")
    created_at: datetime = Field(..., description="Creation timestamp")
    updated_at: datetime = Field(..., description="Last update timestamp")
    
    class Config:
        from_attributes = True


class TaskListResponse(BaseModel):
    """
    Schema for list of tasks response.
    
    Used in GET /api/tasks response body.
    """
    tasks: List[TaskResponse] = Field(default_factory=list, description="List of tasks")
    total: int = Field(..., description="Total number of tasks")
