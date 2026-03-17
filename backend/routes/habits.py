"""
Habits API Routes

REST endpoints for habit operations.
Wraps the existing tracking_app/storage.py functions.

Phase 13: Decoupled Architecture Migration
Step 2: Define API Contract

Endpoints:
- GET /api/habits - List all habits
- POST /api/habits - Create new habit
- GET /api/habits/{habit_id} - Get single habit
- PUT /api/habits/{habit_id} - Update habit
- DELETE /api/habits/{habit_id} - Delete habit
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
import logging
from tracking_app.storage import Storage

from backend.schemas.habits import (
    HabitCreate,
    HabitUpdate,
    HabitResponse,
    HabitListResponse,
)

# Initialize router
router = APIRouter(prefix="/api/habits", tags=["habits"])

# Logger
logger = logging.getLogger(__name__)


def _parse_frequency_data(freq_data) -> List[int]:
    """Parse frequency_data from various formats to list of ints."""
    if not freq_data:
        return [1, 1]
    if isinstance(freq_data, list):
        return freq_data
    if isinstance(freq_data, tuple):
        return list(freq_data)
    if isinstance(freq_data, str):
        # Handle formats like "{1, 1}" or "(1, 1)"
        try:
            import ast
            parsed = ast.literal_eval(freq_data)
            return list(parsed) if isinstance(parsed, (list, tuple)) else [1, 1]
        except:
            return [1, 1]
    return [1, 1]


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


@router.get("", response_model=HabitListResponse)
async def get_habits(
    include_archived: bool = Query(default=False, description="Include archived habits"),
    storage: Storage = Depends(get_storage),
) -> HabitListResponse:
    """
    Get all habits.
    
    Returns a list of all habits, optionally including archived ones.
    
    Args:
        include_archived: Whether to include archived habits
        
    Returns:
        HabitListResponse with list of habits and total count
    """
    try:
        habits = storage.get_habits(include_archived=include_archived)
        
        # Convert to response schema
        habit_responses = [
            HabitResponse(
                id=h.id,
                name=h.name,
                description=h.description,
                frequency=h.frequency,
                frequency_data=_parse_frequency_data(h.frequency_data),
                habit_type=h.habit_type,
                color=h.color,
                icon=h.icon,
                target_value=h.target_value,
                target_type=h.target_type,
                category=h.category,
                archived=h.archived,
                created_at=h.created_at,
                updated_at=h.updated_at,
            )
            for h in habits
        ]
        
        return HabitListResponse(
            habits=habit_responses,
            total=len(habit_responses),
        )
    except Exception as e:
        logger.error(f"Error getting habits: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{habit_id}", response_model=HabitResponse)
async def get_habit(
    habit_id: str,
    storage: Storage = Depends(get_storage),
) -> HabitResponse:
    """
    Get a single habit by ID.
    
    Args:
        habit_id: The habit ID
        
    Returns:
        HabitResponse with habit details
        
    Raises:
        HTTPException 404 if habit not found
    """
    try:
        habit = storage.get_habit(habit_id)
        
        if not habit:
            raise HTTPException(status_code=404, detail="Habit not found")
        
        return HabitResponse(
            id=habit.id,
            name=habit.name,
            description=habit.description,
            frequency=habit.frequency,
            frequency_data=_parse_frequency_data(habit.frequency_data),
            habit_type=habit.habit_type,
            color=habit.color,
            icon=habit.icon,
            target_value=habit.target_value,
            target_type=habit.target_type,
            category=habit.category,
            archived=habit.archived,
            created_at=habit.created_at,
            updated_at=habit.updated_at,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting habit {habit_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("", response_model=HabitResponse, status_code=201)
async def create_habit(
    habit_data: HabitCreate,
    storage: Storage = Depends(get_storage),
) -> HabitResponse:
    """
    Create a new habit.
    
    Args:
        habit_data: Habit creation data
        
    Returns:
        HabitResponse with created habit
    """
    try:
        # Call existing storage method
        habit = storage.create_habit(
            name=habit_data.name,
            description=habit_data.description,
            frequency=habit_data.frequency,
            icon=habit_data.icon,
            color=habit_data.color,
            habit_type=habit_data.habit_type,
            category=habit_data.category,
            target_value=habit_data.target_value,
            target_type=habit_data.target_type,
        )
        
        return HabitResponse(
            id=habit.id,
            name=habit.name,
            description=habit.description,
            frequency=habit.frequency,
            frequency_data=_parse_frequency_data(habit.frequency_data),
            habit_type=habit.habit_type,
            color=habit.color,
            icon=habit.icon,
            target_value=habit.target_value,
            target_type=habit.target_type,
            category=habit.category,
            archived=habit.archived,
            created_at=habit.created_at,
            updated_at=habit.updated_at,
        )
    except Exception as e:
        logger.error(f"Error creating habit: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{habit_id}", response_model=HabitResponse)
async def update_habit(
    habit_id: str,
    habit_data: HabitUpdate,
    storage: Storage = Depends(get_storage),
) -> HabitResponse:
    """
    Update an existing habit.
    
    Args:
        habit_id: The habit ID
        habit_data: Habit update data (only provided fields are updated)
        
    Returns:
        HabitResponse with updated habit
        
    Raises:
        HTTPException 404 if habit not found
    """
    try:
        # First get the existing habit
        habit = storage.get_habit(habit_id)
        
        if not habit:
            raise HTTPException(status_code=404, detail="Habit not found")
        
        # Build update kwargs from provided fields
        update_kwargs = {}
        if habit_data.name is not None:
            update_kwargs["name"] = habit_data.name
        if habit_data.description is not None:
            update_kwargs["description"] = habit_data.description
        if habit_data.frequency is not None:
            update_kwargs["frequency"] = habit_data.frequency
        if habit_data.icon is not None:
            update_kwargs["icon"] = habit_data.icon
        if habit_data.color is not None:
            update_kwargs["color"] = habit_data.color
        if habit_data.habit_type is not None:
            update_kwargs["habit_type"] = habit_data.habit_type
        if habit_data.category is not None:
            update_kwargs["category"] = habit_data.category
        if habit_data.target_value is not None:
            update_kwargs["target_value"] = habit_data.target_value
        if habit_data.target_type is not None:
            update_kwargs["target_type"] = habit_data.target_type
        if habit_data.archived is not None:
            update_kwargs["archived"] = habit_data.archived
        
        # Call update method
        if update_kwargs:
            updated_habit = storage.update_habit(habit_id, **update_kwargs)
        else:
            updated_habit = habit
        
        return HabitResponse(
            id=updated_habit.id,
            name=updated_habit.name,
            description=updated_habit.description,
            frequency=updated_habit.frequency,
            frequency_data=_parse_frequency_data(updated_habit.frequency_data),
            habit_type=updated_habit.habit_type,
            color=updated_habit.color,
            icon=updated_habit.icon,
            target_value=updated_habit.target_value,
            target_type=updated_habit.target_type,
            category=updated_habit.category,
            archived=updated_habit.archived,
            created_at=updated_habit.created_at,
            updated_at=updated_habit.updated_at,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating habit {habit_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{habit_id}", status_code=204)
async def delete_habit(
    habit_id: str,
    storage: Storage = Depends(get_storage),
):
    """
    Delete a habit.
    
    Args:
        habit_id: The habit ID
        
    Raises:
        HTTPException 404 if habit not found
    """
    try:
        # First check if habit exists
        habit = storage.get_habit(habit_id)
        
        if not habit:
            raise HTTPException(status_code=404, detail="Habit not found")
        
        # Delete the habit
        storage.delete_habit(habit_id)
        
        # Return 204 No Content on success
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting habit {habit_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
