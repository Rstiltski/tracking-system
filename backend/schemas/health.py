"""
Health Schemas

Pydantic models for health entry request/response validation.

Based on the existing HealthEntry model in tracking_app/models.py

Phase 13: Decoupled Architecture Migration
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime


class HealthEntryBase(BaseModel):
    """Base health entry schema with common fields."""
    
    entry_date: date = Field(default_factory=date.today, description="Date of the entry")
    weight: Optional[float] = Field(None, ge=0, description="Weight measurement")
    sleep_hours: Optional[float] = Field(None, ge=0, le=24, description="Hours of sleep")
    mood: str = Field(default="good", description="Mood rating: bad, poor, good, great")
    notes: str = Field(default="", max_length=1000, description="Optional notes")


class HealthEntryCreate(HealthEntryBase):
    """
    Schema for creating a new health entry.
    
    Used in POST /api/health request body.
    """
    pass


class HealthEntryUpdate(BaseModel):
    """
    Schema for updating an existing health entry.
    
    Used in PUT /api/health/{id} request body.
    """
    entry_date: Optional[date] = None
    weight: Optional[float] = Field(None, ge=0)
    sleep_hours: Optional[float] = Field(None, ge=0, le=24)
    mood: Optional[str] = None
    notes: Optional[str] = None


class HealthEntryResponse(HealthEntryBase):
    """
    Schema for health entry response.
    """
    id: str = Field(..., description="Unique entry identifier")
    created_at: datetime = Field(..., description="Creation timestamp")
    
    class Config:
        from_attributes = True


class HealthEntryListResponse(BaseModel):
    """
    Schema for list of health entries response.
    """
    entries: List[HealthEntryResponse] = Field(default_factory=list)
    total: int = Field(..., description="Total number of entries")
