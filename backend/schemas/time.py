"""
Time Tracking Schema - Pydantic models for time entries API.

This schema handles time tracking entries which include:
- Timer-based tracking with categories
- Manual time entries
- Session-based timer state
"""

from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field


class TimeEntryBase(BaseModel):
    """Base time entry model."""
    category: str = Field(default="General", description="Time category")
    duration_seconds: int = Field(gt=0, description="Duration in seconds")
    entry_date: date = Field(default_factory=date.today, description="Date of entry")
    notes: Optional[str] = Field(None, description="Optional notes")


class TimeEntryCreate(TimeEntryBase):
    """Model for creating a new time entry."""
    pass


class TimeEntry(TimeEntryBase):
    """Complete time entry model with ID and timestamps."""
    id: str = Field(description="Unique identifier")
    created_at: datetime = Field(description="Creation timestamp")
    
    class Config:
        from_attributes = True


class TimerState(BaseModel):
    """Current timer state for a user session."""
    running: bool = Field(default=False, description="Is timer running")
    start_timestamp: Optional[float] = Field(None, description="Unix timestamp when started")
    elapsed_seconds: int = Field(default=0, description="Previously accumulated seconds")
    category: str = Field(default="General", description="Current timer category")


class TimerStartRequest(BaseModel):
    """Request to start the timer."""
    category: str = Field(default="General", description="Timer category")


class TimerStopRequest(BaseModel):
    """Request to stop the timer and save entry."""
    notes: Optional[str] = Field(None, description="Optional notes for the entry")


class TimeSummary(BaseModel):
    """Summary of time tracked for a period."""
    total_seconds: int = Field(description="Total seconds tracked")
    by_category: dict = Field(description="Seconds by category")
    entry_count: int = Field(description="Number of entries")


# Time categories matching the original app
TIME_CATEGORIES = [
    "General",
    "Work", 
    "Learning",
    "Exercise",
    "Personal",
    "Break",
    "Other",
]
