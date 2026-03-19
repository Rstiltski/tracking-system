"""
Diary API Routes

REST endpoints for diary operations.
Wraps the existing tracking_app/storage.py functions.

Phase 13: Decoupled Architecture Migration
Step 2: Define API Contract

Endpoints:
- GET /api/diary - List diary entries
- POST /api/diary - Create diary entry
- GET /api/diary/{entry_id} - Get single entry
- PUT /api/diary/{entry_id} - Update entry
- DELETE /api/diary/{entry_id} - Delete entry
- GET /api/diary/date/{date} - Get entry by date
- GET /api/diary/search - Search entries
"""

from fastapi import APIRouter, HTTPException, Query
from typing import List, Optional
from datetime import date, datetime
import logging
from tracking_app.storage import Storage

from backend.schemas.diary import (
    DiaryEntryCreate,
    DiaryEntryUpdate,
    DiaryEntryResponse,
    DiarySearchResponse,
)

# Initialize router
router = APIRouter(prefix="/api/diary", tags=["diary"])

# Logger
logger = logging.getLogger(__name__)


def _get_storage() -> Storage:
    """Get storage instance."""
    return Storage()


@router.get("", response_model=List[DiaryEntryResponse])
async def get_diary_entries(
    start_date: Optional[date] = Query(None, description="Filter by start date"),
    end_date: Optional[date] = Query(None, description="Filter by end date"),
    limit: int = Query(50, ge=1, le=500, description="Maximum entries to return"),
):
    """
    Get all diary entries with optional date filtering.
    """
    storage = _get_storage()
    entries = storage.get_diary_entries(
        start_date=start_date,
        end_date=end_date,
        limit=limit
    )
    return [
        DiaryEntryResponse(
            id=entry.get('id', ''),
            title=entry.get('title', ''),
            content=entry.get('content', ''),
            mood=entry.get('mood'),
            tags=entry.get('tags', []),
            entry_date=entry.get('entry_date'),
            created_at=entry.get('created_at'),
            updated_at=entry.get('updated_at'),
        )
        for entry in entries
    ]


@router.post("", response_model=DiaryEntryResponse, status_code=201)
async def create_diary_entry(entry: DiaryEntryCreate):
    """
    Create a new diary entry.
    """
    storage = _get_storage()
    entry_data = {
        'title': entry.title,
        'content': entry.content,
        'mood': entry.mood,
        'tags': entry.tags,
        'entry_date': entry.entry_date.isoformat() if entry.entry_date else None,
    }
    
    new_entry = storage.create_diary_entry(**entry_data)
    
    if not new_entry:
        raise HTTPException(status_code=500, detail="Failed to create diary entry")
    
    return DiaryEntryResponse(
        id=new_entry.get('id', ''),
        title=new_entry.get('title', ''),
        content=new_entry.get('content', ''),
        mood=new_entry.get('mood'),
        tags=new_entry.get('tags', []),
        entry_date=new_entry.get('entry_date'),
        created_at=new_entry.get('created_at'),
        updated_at=new_entry.get('updated_at'),
    )


@router.get("/search", response_model=DiarySearchResponse)
async def search_diary_entries(
    query: str = Query(..., min_length=1, description="Search query"),
    limit: int = Query(50, ge=1, le=500, description="Maximum results"),
):
    """
    Search diary entries by content or title.
    """
    storage = _get_storage()
    entries = storage.search_diary_entries(query=query, limit=limit)
    
    return DiarySearchResponse(
        entries=[
            DiaryEntryResponse(
                id=entry.get('id', ''),
                title=entry.get('title', ''),
                content=entry.get('content', ''),
                mood=entry.get('mood'),
                tags=entry.get('tags', []),
                entry_date=entry.get('entry_date'),
                created_at=entry.get('created_at'),
                updated_at=entry.get('updated_at'),
            )
            for entry in entries
        ],
        total=len(entries),
        query=query,
    )


@router.get("/date/{entry_date}", response_model=DiaryEntryResponse)
async def get_diary_entry_by_date(entry_date: date):
    """
    Get diary entry for a specific date.
    """
    storage = _get_storage()
    entry = storage.get_diary_entry_by_date(entry_date=entry_date)
    
    if not entry:
        raise HTTPException(status_code=404, detail="No entry found for this date")
    
    return DiaryEntryResponse(
        id=entry.get('id', ''),
        title=entry.get('title', ''),
        content=entry.get('content', ''),
        mood=entry.get('mood'),
        tags=entry.get('tags', []),
        entry_date=entry.get('entry_date'),
        created_at=entry.get('created_at'),
        updated_at=entry.get('updated_at'),
    )


@router.get("/{entry_id}", response_model=DiaryEntryResponse)
async def get_diary_entry(entry_id: str):
    """
    Get a single diary entry by ID.
    """
    storage = _get_storage()
    entry = storage.get_diary_entry(entry_id=entry_id)
    
    if not entry:
        raise HTTPException(status_code=404, detail="Diary entry not found")
    
    return DiaryEntryResponse(
        id=entry.get('id', ''),
        title=entry.get('title', ''),
        content=entry.get('content', ''),
        mood=entry.get('mood'),
        tags=entry.get('tags', []),
        entry_date=entry.get('entry_date'),
        created_at=entry.get('created_at'),
        updated_at=entry.get('updated_at'),
    )


@router.put("/{entry_id}", response_model=DiaryEntryResponse)
async def update_diary_entry(entry_id: str, entry: DiaryEntryUpdate):
    """
    Update an existing diary entry.
    """
    storage = _get_storage()
    
    # Build update dict
    updates = {}
    if entry.title is not None:
        updates['title'] = entry.title
    if entry.content is not None:
        updates['content'] = entry.content
    if entry.mood is not None:
        updates['mood'] = entry.mood
    if entry.tags is not None:
        updates['tags'] = entry.tags
    
    updated_entry = storage.update_diary_entry(entry_id, **updates)
    
    if not updated_entry:
        raise HTTPException(status_code=404, detail="Diary entry not found")
    
    return DiaryEntryResponse(
        id=updated_entry.get('id', ''),
        title=updated_entry.get('title', ''),
        content=updated_entry.get('content', ''),
        mood=updated_entry.get('mood'),
        tags=updated_entry.get('tags', []),
        entry_date=updated_entry.get('entry_date'),
        created_at=updated_entry.get('created_at'),
        updated_at=updated_entry.get('updated_at'),
    )


@router.delete("/{entry_id}", status_code=204)
async def delete_diary_entry(entry_id: str):
    """
    Delete a diary entry.
    """
    storage = _get_storage()
    success = storage.delete_diary_entry(entry_id=entry_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Diary entry not found")
    
    return None
