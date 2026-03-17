"""
Journal API Routes

REST endpoints for journal operations.
Wraps the existing tracking_app/storage.py functions.

Phase 13: Decoupled Architecture Migration

Endpoints:
- GET /api/journal - List all journal entries
- POST /api/journal - Create new journal entry
- GET /api/journal/{entry_id} - Get single journal entry
- PUT /api/journal/{entry_id} - Update journal entry
- DELETE /api/journal/{entry_id} - Delete journal entry
- GET /api/journal/search - Search journal entries
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
import logging
from tracking_app.storage import Storage

from backend.schemas.journal import (
    JournalEntryCreate,
    JournalEntryUpdate,
    JournalEntryResponse,
    JournalListResponse,
    JournalSearchResponse,
)

# Initialize router
router = APIRouter(prefix="/api/journal", tags=["journal"])

# Logger
logger = logging.getLogger(__name__)


def get_storage():
    """
    Dependency to get storage instance.
    
    In a production app, this would handle database connection pooling.
    For now, we create a new storage instance per request.
    """
    try:
        from tracking_app.storage import Storage
        return Storage()
    except ImportError as e:
        logger.error(f"Failed to import Storage: {e}")
        raise HTTPException(status_code=500, detail="Storage module not available")


@router.get("", response_model=JournalListResponse)
async def get_journal_entries(
    category: Optional[str] = Query(default=None, description="Filter by category"),
    storage: Storage = Depends(get_storage),
) -> JournalListResponse:
    """
    Get all journal entries.
    
    Returns a list of all journal entries, optionally filtered by category.
    """
    try:
        if category:
            entries = storage.get_journal_entries(category=category)
        else:
            entries = storage.get_journal_entries()
        
        # Convert to response format
        response_entries = []
        for entry in entries:
            response_entries.append(JournalEntryResponse(
                id=entry.id,
                title=entry.title,
                content=entry.content,
                category=entry.category,
                tags=entry.tags,
                is_private=entry.is_private,
                created_at=entry.created_at,
                updated_at=entry.updated_at,
            ))
        
        return JournalListResponse(
            entries=response_entries,
            total=len(response_entries)
        )
    except Exception as e:
        logger.error(f"Error fetching journal entries: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/search", response_model=JournalSearchResponse)
async def search_journal_entries(
    q: str = Query(..., description="Search query"),
    limit: int = Query(default=50, description="Maximum results"),
    storage: Storage = Depends(get_storage),
) -> JournalSearchResponse:
    """
    Search journal entries by title or content.
    """
    try:
        entries = storage.search_journal_entries(query=q, limit=limit)
        
        response_entries = []
        for entry in entries:
            response_entries.append(JournalEntryResponse(
                id=entry.id,
                title=entry.title,
                content=entry.content,
                category=entry.category,
                tags=entry.tags,
                is_private=entry.is_private,
                created_at=entry.created_at,
                updated_at=entry.updated_at,
            ))
        
        return JournalSearchResponse(
            entries=response_entries,
            query=q,
            total=len(response_entries)
        )
    except Exception as e:
        logger.error(f"Error searching journal entries: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{entry_id}", response_model=JournalEntryResponse)
async def get_journal_entry(
    entry_id: str,
    storage: Storage = Depends(get_storage),
) -> JournalEntryResponse:
    """
    Get a single journal entry by ID.
    """
    try:
        entry = storage.get_journal_entry(entry_id)
        if not entry:
            raise HTTPException(status_code=404, detail="Journal entry not found")
        
        return JournalEntryResponse(
            id=entry.id,
            title=entry.title,
            content=entry.content,
            category=entry.category,
            tags=entry.tags,
            is_private=entry.is_private,
            created_at=entry.created_at,
            updated_at=entry.updated_at,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error fetching journal entry: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("", response_model=JournalEntryResponse, status_code=201)
async def create_journal_entry(
    entry: JournalEntryCreate,
    storage: Storage = Depends(get_storage),
) -> JournalEntryResponse:
    """
    Create a new journal entry.
    """
    try:
        new_entry = storage.create_journal_entry(
            title=entry.title,
            content=entry.content,
            category=entry.category,
            tags=entry.tags,
        )
        
        return JournalEntryResponse(
            id=new_entry.id,
            title=new_entry.title,
            content=new_entry.content,
            category=new_entry.category,
            tags=new_entry.tags,
            is_private=new_entry.is_private,
            created_at=new_entry.created_at,
            updated_at=new_entry.updated_at,
        )
    except Exception as e:
        logger.error(f"Error creating journal entry: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{entry_id}", response_model=JournalEntryResponse)
async def update_journal_entry(
    entry_id: str,
    entry: JournalEntryUpdate,
    storage: Storage = Depends(get_storage),
) -> JournalEntryResponse:
    """
    Update an existing journal entry.
    """
    try:
        # Build update dict, excluding None values
        updates = {}
        if entry.title is not None:
            updates['title'] = entry.title
        if entry.content is not None:
            updates['content'] = entry.content
        if entry.category is not None:
            updates['category'] = entry.category
        if entry.tags is not None:
            updates['tags'] = entry.tags
        
        updated_entry = storage.update_journal_entry(entry_id, **updates)
        
        if not updated_entry:
            raise HTTPException(status_code=404, detail="Journal entry not found")
        
        return JournalEntryResponse(
            id=updated_entry.id,
            title=updated_entry.title,
            content=updated_entry.content,
            category=updated_entry.category,
            tags=updated_entry.tags,
            is_private=updated_entry.is_private,
            created_at=updated_entry.created_at,
            updated_at=updated_entry.updated_at,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating journal entry: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{entry_id}")
async def delete_journal_entry(
    entry_id: str,
    storage: Storage = Depends(get_storage),
) -> dict:
    """
    Delete a journal entry.
    """
    try:
        success = storage.delete_journal_entry(entry_id)
        if not success:
            raise HTTPException(status_code=404, detail="Journal entry not found")
        
        return {"message": "Journal entry deleted successfully", "id": entry_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting journal entry: {e}")
        raise HTTPException(status_code=500, detail=str(e))
