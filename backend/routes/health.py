"""
Health API Routes

REST endpoints for health tracking operations.
Wraps the existing tracking_app/storage.py functions.

Phase 13: Decoupled Architecture Migration
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
from datetime import date
import logging
from tracking_app.storage import Storage

from backend.schemas.health import (
    HealthEntryCreate,
    HealthEntryUpdate,
    HealthEntryResponse,
    HealthEntryListResponse,
)

# Initialize router
router = APIRouter(prefix="/api/health", tags=["health"])

# Logger
logger = logging.getLogger(__name__)


def get_storage():
    """Dependency to get storage instance."""
    try:
        from tracking_app.storage import Storage
        return Storage()
    except ImportError as e:
        logger.error(f"Failed to import Storage: {e}")
        raise HTTPException(status_code=500, detail="Storage module not available")


@router.get("", response_model=HealthEntryListResponse)
async def get_health_entries(
    start_date: Optional[date] = Query(default=None, description="Start date filter"),
    end_date: Optional[date] = Query(default=None, description="End date filter"),
    storage: Storage = Depends(get_storage),
) -> HealthEntryListResponse:
    """Get health entries."""
    try:
        entries = storage.get_health_entries(start_date=start_date, end_date=end_date)
        
        entry_responses = [
            HealthEntryResponse(
                id=e.id,
                entry_date=e.entry_date,
                weight=e.weight,
                sleep_hours=e.sleep_hours,
                mood=e.mood,
                notes=e.notes,
                created_at=e.created_at,
            )
            for e in entries
        ]
        
        return HealthEntryListResponse(
            entries=entry_responses,
            total=len(entry_responses),
        )
    except Exception as e:
        logger.error(f"Error getting health entries: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/date/{entry_date}", response_model=HealthEntryResponse)
async def get_health_entry_by_date(
    entry_date: date,
    storage: Storage = Depends(get_storage),
) -> HealthEntryResponse:
    """Get health entry for a specific date."""
    try:
        entry = storage.get_health_entry(entry_date)
        
        if not entry:
            raise HTTPException(status_code=404, detail="Health entry not found")
        
        return HealthEntryResponse(
            id=entry.id,
            entry_date=entry.entry_date,
            weight=entry.weight,
            sleep_hours=entry.sleep_hours,
            mood=entry.mood,
            notes=entry.notes,
            created_at=entry.created_at,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting health entry: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("", response_model=HealthEntryResponse, status_code=201)
async def create_health_entry(
    entry_data: HealthEntryCreate,
    storage: Storage = Depends(get_storage),
) -> HealthEntryResponse:
    """Create a new health entry."""
    try:
        entry = storage.create_health_entry(
            entry_date=entry_data.entry_date,
            weight=entry_data.weight,
            sleep_hours=entry_data.sleep_hours,
            mood=entry_data.mood,
            notes=entry_data.notes,
        )
        
        return HealthEntryResponse(
            id=entry.id,
            entry_date=entry.entry_date,
            weight=entry.weight,
            sleep_hours=entry.sleep_hours,
            mood=entry.mood,
            notes=entry.notes,
            created_at=entry.created_at,
        )
    except Exception as e:
        logger.error(f"Error creating health entry: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{entry_id}", response_model=HealthEntryResponse)
async def update_health_entry(
    entry_id: str,
    entry_data: HealthEntryUpdate,
    storage: Storage = Depends(get_storage),
) -> HealthEntryResponse:
    """Update an existing health entry."""
    try:
        # Build update kwargs
        update_kwargs = {}
        if entry_data.weight is not None:
            update_kwargs["weight"] = entry_data.weight
        if entry_data.sleep_hours is not None:
            update_kwargs["sleep_hours"] = entry_data.sleep_hours
        if entry_data.mood is not None:
            update_kwargs["mood"] = entry_data.mood
        if entry_data.notes is not None:
            update_kwargs["notes"] = entry_data.notes
        
        if not update_kwargs:
            raise HTTPException(status_code=400, detail="No fields to update")
        
        entry = storage.update_health_entry(entry_id, **update_kwargs)
        
        if not entry:
            raise HTTPException(status_code=404, detail="Health entry not found")
        
        return HealthEntryResponse(
            id=entry.id,
            entry_date=entry.entry_date,
            weight=entry.weight,
            sleep_hours=entry.sleep_hours,
            mood=entry.mood,
            notes=entry.notes,
            created_at=entry.created_at,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating health entry: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{entry_id}", status_code=204)
async def delete_health_entry(
    entry_id: str,
    storage: Storage = Depends(get_storage),
):
    """Delete a health entry."""
    try:
        success = storage.delete_health_entry(entry_id)
        
        if not success:
            raise HTTPException(status_code=404, detail="Health entry not found")
        
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting health entry: {e}")
        raise HTTPException(status_code=500, detail=str(e))
