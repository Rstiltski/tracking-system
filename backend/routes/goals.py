"""
Goals API Routes

REST endpoints for goal operations.
Wraps the existing tracking_app/storage.py functions.

Phase 13: Decoupled Architecture Migration
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import Optional
import logging
from tracking_app.storage import Storage

from backend.schemas.goals import (
    GoalCreate,
    GoalUpdate,
    GoalProgressUpdate,
    GoalResponse,
    GoalListResponse,
)

# Initialize router
router = APIRouter(prefix="/api/goals", tags=["goals"])

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


@router.get("", response_model=GoalListResponse)
async def get_goals(
    include_completed: bool = Query(default=False, description="Include completed goals"),
    storage: Storage = Depends(get_storage),
) -> GoalListResponse:
    """Get all goals."""
    try:
        goals = storage.get_goals(include_completed=include_completed)
        
        goal_responses = [
            GoalResponse(
                id=g.id,
                title=g.title,
                description=g.description,
                target=g.target,
                current=g.current,
                unit=g.unit,
                deadline=g.deadline,
                completed=g.completed,
                created_at=g.created_at,
                updated_at=g.updated_at,
            )
            for g in goals
        ]
        
        return GoalListResponse(
            goals=goal_responses,
            total=len(goal_responses),
        )
    except Exception as e:
        logger.error(f"Error getting goals: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{goal_id}", response_model=GoalResponse)
async def get_goal(
    goal_id: str,
    storage: Storage = Depends(get_storage),
) -> GoalResponse:
    """Get a single goal by ID."""
    try:
        goal = storage.get_goal(goal_id)
        
        if not goal:
            raise HTTPException(status_code=404, detail="Goal not found")
        
        return GoalResponse(
            id=goal.id,
            title=goal.title,
            description=goal.description,
            target=goal.target,
            current=goal.current,
            unit=goal.unit,
            deadline=goal.deadline,
            completed=goal.completed,
            created_at=goal.created_at,
            updated_at=goal.updated_at,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting goal {goal_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("", response_model=GoalResponse, status_code=201)
async def create_goal(
    goal_data: GoalCreate,
    storage: Storage = Depends(get_storage),
) -> GoalResponse:
    """Create a new goal."""
    try:
        goal = storage.create_goal(
            title=goal_data.title,
            description=goal_data.description,
            target=goal_data.target,
            unit=goal_data.unit,
            deadline=goal_data.deadline,
        )
        
        return GoalResponse(
            id=goal.id,
            title=goal.title,
            description=goal.description,
            target=goal.target,
            current=goal.current,
            unit=goal.unit,
            deadline=goal.deadline,
            completed=goal.completed,
            created_at=goal.created_at,
            updated_at=goal.updated_at,
        )
    except Exception as e:
        logger.error(f"Error creating goal: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{goal_id}", response_model=GoalResponse)
async def update_goal(
    goal_id: str,
    goal_data: GoalUpdate,
    storage: Storage = Depends(get_storage),
) -> GoalResponse:
    """Update an existing goal."""
    try:
        goal = storage.get_goal(goal_id)
        
        if not goal:
            raise HTTPException(status_code=404, detail="Goal not found")
        
        # Build update kwargs
        update_kwargs = {}
        if goal_data.title is not None:
            update_kwargs["title"] = goal_data.title
        if goal_data.description is not None:
            update_kwargs["description"] = goal_data.description
        if goal_data.target is not None:
            update_kwargs["target"] = goal_data.target
        if goal_data.current is not None:
            update_kwargs["current"] = goal_data.current
        if goal_data.unit is not None:
            update_kwargs["unit"] = goal_data.unit
        if goal_data.deadline is not None:
            update_kwargs["deadline"] = goal_data.deadline
        if goal_data.completed is not None:
            update_kwargs["completed"] = goal_data.completed
        
        # Use update_goal_progress if only current is being updated
        if goal_data.current is not None and len(update_kwargs) == 1:
            updated_goal = storage.update_goal_progress(goal_id, goal_data.current)
        elif update_kwargs:
            # Get the storage and update manually
            from tracking_app.models import Goal
            for key, value in update_kwargs.items():
                setattr(goal, key, value)
            goal.save()
            updated_goal = goal
        else:
            updated_goal = goal
        
        return GoalResponse(
            id=updated_goal.id,
            title=updated_goal.title,
            description=updated_goal.description,
            target=updated_goal.target,
            current=updated_goal.current,
            unit=updated_goal.unit,
            deadline=updated_goal.deadline,
            completed=updated_goal.completed,
            created_at=updated_goal.created_at,
            updated_at=updated_goal.updated_at,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating goal {goal_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{goal_id}/progress", response_model=GoalResponse)
async def update_goal_progress(
    goal_id: str,
    progress_data: GoalProgressUpdate,
    storage: Storage = Depends(get_storage),
) -> GoalResponse:
    """Update goal progress."""
    try:
        goal = storage.update_goal_progress(goal_id, progress_data.current)
        
        if not goal:
            raise HTTPException(status_code=404, detail="Goal not found")
        
        return GoalResponse(
            id=goal.id,
            title=goal.title,
            description=goal.description,
            target=goal.target,
            current=goal.current,
            unit=goal.unit,
            deadline=goal.deadline,
            completed=goal.completed,
            created_at=goal.created_at,
            updated_at=goal.updated_at,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating goal progress {goal_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{goal_id}", status_code=204)
async def delete_goal(
    goal_id: str,
    storage: Storage = Depends(get_storage),
):
    """Delete a goal."""
    try:
        goal = storage.get_goal(goal_id)
        
        if not goal:
            raise HTTPException(status_code=404, detail="Goal not found")
        
        storage.delete_goal(goal_id)
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting goal {goal_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
