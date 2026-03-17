"""
Time Tracking API - FastAPI routes for time entries.

This API provides endpoints for:
- Timer state management (start/stop/pause) - in-memory
- Time entry CRUD operations - uses storage
- Time summaries and statistics
"""

import time as time_module
from datetime import date, datetime
from typing import Optional, List
from fastapi import APIRouter, HTTPException, Depends

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tracking_app.storage import get_storage, Storage
from backend.schemas.time import (
    TimeEntry as TimeEntrySchema,
    TimeEntryCreate,
    TimerState,
    TimerStartRequest,
    TimerStopRequest,
    TimeSummary,
    TIME_CATEGORIES,
)

# In-memory timer state (not persisted)
# Timer state is session-based in the original app
timer_state = TimerState()


router = APIRouter(prefix="/api/time", tags=["time"])


def get_storage_instance():
    """Get storage instance."""
    return get_storage()


@router.get("/categories", response_model=List[str])
async def get_categories():
    """Get available time categories."""
    return TIME_CATEGORIES


@router.get("/timer", response_model=TimerState)
async def get_timer_state():
    """Get current timer state."""
    return timer_state


@router.post("/timer/start", response_model=TimerState)
async def start_timer(request: TimerStartRequest):
    """Start the timer."""
    if timer_state.running:
        raise HTTPException(status_code=400, detail="Timer already running")
    
    timer_state.running = True
    timer_state.start_timestamp = time_module.time()
    timer_state.category = request.category
    
    return timer_state


@router.post("/timer/stop", response_model=TimeEntrySchema)
async def stop_timer(
    request: TimerStopRequest,
    storage: Storage = Depends(get_storage_instance),
):
    """Stop the timer and save the time entry."""
    if not timer_state.running:
        raise HTTPException(status_code=400, detail="Timer not running")
    
    # Calculate total elapsed time
    current_time = time_module.time()
    if timer_state.start_timestamp:
        session_seconds = int(current_time - timer_state.start_timestamp)
    else:
        session_seconds = 0
    
    total_seconds = timer_state.elapsed_seconds + session_seconds
    
    # Save to storage
    entry = storage.create_time_entry(
        category=timer_state.category,
        duration_seconds=total_seconds,
        entry_date=date.today(),
        notes=request.notes,
    )
    
    # Convert to API response format
    response = TimeEntrySchema(
        id=entry.id,
        category=entry.category,
        duration_seconds=entry.duration_seconds,
        entry_date=entry.entry_date,
        notes=entry.notes,
        created_at=entry.created_at,
    )
    
    # Reset timer state
    timer_state.running = False
    timer_state.start_timestamp = None
    timer_state.elapsed_seconds = 0
    
    return response


@router.post("/timer/pause", response_model=TimerState)
async def pause_timer():
    """Pause the timer without saving."""
    if not timer_state.running:
        raise HTTPException(status_code=400, detail="Timer not running")
    
    # Calculate elapsed time and add to accumulated
    current_time = time_module.time()
    if timer_state.start_timestamp:
        session_seconds = int(current_time - timer_state.start_timestamp)
    else:
        session_seconds = 0
    
    timer_state.elapsed_seconds += session_seconds
    timer_state.running = False
    timer_state.start_timestamp = None
    
    return timer_state


@router.post("/timer/reset", response_model=TimerState)
async def reset_timer():
    """Reset the timer without saving."""
    timer_state.running = False
    timer_state.start_timestamp = None
    timer_state.elapsed_seconds = 0
    timer_state.category = "General"
    
    return timer_state


@router.get("/entries", response_model=List[TimeEntrySchema])
async def get_entries(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    category: Optional[str] = None,
    limit: int = 100,
    storage: Storage = Depends(get_storage_instance),
):
    """
    Get time entries with optional filtering.
    
    - **start_date**: Filter entries from this date (YYYY-MM-DD)
    - **end_date**: Filter entries until this date (YYYY-MM-DD)
    - **category**: Filter by category
    - **limit**: Maximum number of entries to return
    """
    # Convert string dates to date objects
    start = date.fromisoformat(start_date) if start_date else None
    end = date.fromisoformat(end_date) if end_date else None
    
    entries = storage.get_time_entries(start, end, category)
    
    # Convert to API response format
    return [
        TimeEntrySchema(
            id=e.id,
            category=e.category,
            duration_seconds=e.duration_seconds,
            entry_date=e.entry_date,
            notes=e.notes,
            created_at=e.created_at,
        )
        for e in entries[:limit]
    ]


@router.post("/entries", response_model=TimeEntrySchema)
async def create_entry(
    entry: TimeEntryCreate,
    storage: Storage = Depends(get_storage_instance),
):
    """Create a new manual time entry."""
    new_entry = storage.create_time_entry(
        category=entry.category,
        duration_seconds=entry.duration_seconds,
        entry_date=entry.entry_date,
        notes=entry.notes,
    )
    
    return TimeEntrySchema(
        id=new_entry.id,
        category=new_entry.category,
        duration_seconds=new_entry.duration_seconds,
        entry_date=new_entry.entry_date,
        notes=new_entry.notes,
        created_at=new_entry.created_at,
    )


@router.get("/entries/{entry_id}", response_model=TimeEntrySchema)
async def get_entry(
    entry_id: str,
    storage: Storage = Depends(get_storage_instance),
):
    """Get a specific time entry by ID."""
    entry = storage.get_time_entry(entry_id)
    
    if not entry:
        raise HTTPException(status_code=404, detail="Entry not found")
    
    return TimeEntrySchema(
        id=entry.id,
        category=entry.category,
        duration_seconds=entry.duration_seconds,
        entry_date=entry.entry_date,
        notes=entry.notes,
        created_at=entry.created_at,
    )


@router.delete("/entries/{entry_id}")
async def delete_entry(
    entry_id: str,
    storage: Storage = Depends(get_storage_instance),
):
    """Delete a time entry."""
    success = storage.delete_time_entry(entry_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Entry not found")
    
    return {"message": "Entry deleted"}


@router.get("/summary", response_model=TimeSummary)
async def get_summary(
    start_date: Optional[str] = None,
    end_date: Optional[str] = None,
    storage: Storage = Depends(get_storage_instance),
):
    """
    Get time tracking summary for a period.
    
    - **start_date**: Start of period (YYYY-MM-DD)
    - **end_date**: End of period (YYYY-MM-DD)
    """
    # Convert string dates to date objects
    start = date.fromisoformat(start_date) if start_date else None
    end = date.fromisoformat(end_date) if end_date else None
    
    entries = storage.get_time_entries(start, end)
    
    # Calculate totals
    total_seconds = sum(e.duration_seconds for e in entries)
    
    # Group by category
    by_category = {}
    for entry in entries:
        if entry.category not in by_category:
            by_category[entry.category] = 0
        by_category[entry.category] += entry.duration_seconds
    
    return TimeSummary(
        total_seconds=total_seconds,
        by_category=by_category,
        entry_count=len(entries),
    )
