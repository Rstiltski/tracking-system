"""
Journal API Schemas

Pydantic models for journal entry validation and serialization.

Phase 13: Decoupled Architecture - Backend Schemas
"""

from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class JournalEntryBase(BaseModel):
    """Base schema for journal entries."""
    title: str = Field(default="", description="Entry title")
    content: str = Field(default="", description="Entry content (supports Markdown)")
    category: str = Field(default="free_write", description="Category for organization")
    tags: List[str] = Field(default_factory=list, description="List of tags")
    is_private: bool = Field(default=True, description="Privacy flag")


class JournalEntryCreate(JournalEntryBase):
    """Schema for creating a new journal entry."""
    pass


class JournalEntryUpdate(BaseModel):
    """Schema for updating an existing journal entry."""
    title: Optional[str] = Field(default=None, description="Entry title")
    content: Optional[str] = Field(default=None, description="Entry content")
    category: Optional[str] = Field(default=None, description="Category for organization")
    tags: Optional[List[str]] = Field(default=None, description="List of tags")
    is_private: Optional[bool] = Field(default=None, description="Privacy flag")


class JournalEntryResponse(JournalEntryBase):
    """Schema for journal entry response."""
    id: str = Field(description="Unique identifier")
    created_at: Optional[datetime] = Field(default=None, description="Creation timestamp")
    updated_at: Optional[datetime] = Field(default=None, description="Last update timestamp")

    class Config:
        from_attributes = True


class JournalListResponse(BaseModel):
    """Schema for list of journal entries response."""
    entries: List[JournalEntryResponse] = Field(default_factory=list, description="List of journal entries")
    total: int = Field(default=0, description="Total number of entries")


class JournalSearchResponse(BaseModel):
    """Schema for journal search response."""
    entries: List[JournalEntryResponse] = Field(default_factory=list, description="Search results")
    query: str = Field(description="Search query")
    total: int = Field(default=0, description="Total number of matches")
