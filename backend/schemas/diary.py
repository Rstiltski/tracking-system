"""
Diary API Schemas

Pydantic models for diary entry validation and serialization.

Phase 13: Decoupled Architecture - Backend Schemas
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import date


class DiaryEntryBase(BaseModel):
    """Base schema for diary entries."""
    title: str = Field(default="", description="Entry title")
    content: str = Field(default="", description="Entry content")
    mood: Optional[str] = Field(default=None, description="Mood indicator")
    tags: List[str] = Field(default_factory=list, description="List of tags")


class DiaryEntryCreate(DiaryEntryBase):
    """Schema for creating a new diary entry."""
    entry_date: Optional[date] = Field(default=None, description="Entry date")


class DiaryEntryUpdate(BaseModel):
    """Schema for updating an existing diary entry."""
    title: Optional[str] = Field(default=None, description="Entry title")
    content: Optional[str] = Field(default=None, description="Entry content")
    mood: Optional[str] = Field(default=None, description="Mood indicator")
    tags: Optional[List[str]] = Field(default=None, description="List of tags")


class DiaryEntryResponse(DiaryEntryBase):
    """Schema for diary entry response."""
    id: str = Field(description="Unique identifier")
    entry_date: Optional[date] = Field(default=None, description="Entry date")
    created_at: Optional[str] = Field(default=None, description="Creation timestamp")
    updated_at: Optional[str] = Field(default=None, description="Update timestamp")

    class Config:
        from_attributes = True


class DiarySearchResponse(BaseModel):
    """Schema for diary search results."""
    entries: List[DiaryEntryResponse]
    total: int
    query: str
