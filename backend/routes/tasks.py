"""
Tasks API Routes

REST endpoints for task operations.
Wraps the existing tracking_app/storage.py functions.

Phase 13: Decoupled Architecture Migration
Step 4: Migrate More Features

Endpoints:
- GET /api/tasks - List all tasks
- POST /api/tasks - Create new task
- GET /api/tasks/{task_id} - Get single task
- PUT /api/tasks/{task_id} - Update task
- DELETE /api/tasks/{task_id} - Delete task
- POST /api/tasks/{task_id}/complete - Mark task complete
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from typing import List, Optional
import logging
from tracking_app.storage import Storage

from backend.schemas.tasks import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
    TaskListResponse,
)

# Initialize router
router = APIRouter(prefix="/api/tasks", tags=["tasks"])

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


@router.get("", response_model=TaskListResponse)
async def get_tasks(
    include_completed: bool = Query(default=False, description="Include completed tasks"),
    storage: Storage = Depends(get_storage),
) -> TaskListResponse:
    """Get all tasks."""
    try:
        tasks = storage.get_tasks(include_completed=include_completed)
        
        task_responses = [
            TaskResponse(
                id=t.id,
                title=t.title,
                description=t.description,
                due_date=t.due_date,
                priority=t.priority,
                category=t.category,
                completed=t.completed,
                completed_at=t.completed_at,
                created_at=t.created_at,
                updated_at=t.updated_at,
            )
            for t in tasks
        ]
        
        return TaskListResponse(
            tasks=task_responses,
            total=len(task_responses),
        )
    except Exception as e:
        logger.error(f"Error getting tasks: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/{task_id}", response_model=TaskResponse)
async def get_task(
    task_id: str,
    storage: Storage = Depends(get_storage),
) -> TaskResponse:
    """Get a single task by ID."""
    try:
        task = storage.get_task(task_id)
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return TaskResponse(
            id=task.id,
            title=task.title,
            description=task.description,
            due_date=task.due_date,
            priority=task.priority,
            category=task.category,
            completed=task.completed,
            completed_at=task.completed_at,
            created_at=task.created_at,
            updated_at=task.updated_at,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting task {task_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("", response_model=TaskResponse, status_code=201)
async def create_task(
    task_data: TaskCreate,
    storage: Storage = Depends(get_storage),
) -> TaskResponse:
    """Create a new task."""
    try:
        task = storage.create_task(
            title=task_data.title,
            description=task_data.description,
            due_date=task_data.due_date,
            priority=task_data.priority,
            category=task_data.category,
        )
        
        return TaskResponse(
            id=task.id,
            title=task.title,
            description=task.description,
            due_date=task.due_date,
            priority=task.priority,
            category=task.category,
            completed=task.completed,
            completed_at=task.completed_at,
            created_at=task.created_at,
            updated_at=task.updated_at,
        )
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.put("/{task_id}", response_model=TaskResponse)
async def update_task(
    task_id: str,
    task_data: TaskUpdate,
    storage: Storage = Depends(get_storage),
) -> TaskResponse:
    """Update an existing task."""
    try:
        task = storage.get_task(task_id)
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        # Build update kwargs from provided fields
        update_kwargs = {}
        if task_data.title is not None:
            update_kwargs["title"] = task_data.title
        if task_data.description is not None:
            update_kwargs["description"] = task_data.description
        if task_data.due_date is not None:
            update_kwargs["due_date"] = task_data.due_date
        if task_data.priority is not None:
            update_kwargs["priority"] = task_data.priority
        if task_data.category is not None:
            update_kwargs["category"] = task_data.category
        if task_data.completed is not None:
            update_kwargs["completed"] = task_data.completed
        
        updated_task = storage.update_task(task_id, **update_kwargs) if update_kwargs else task
        
        return TaskResponse(
            id=updated_task.id,
            title=updated_task.title,
            description=updated_task.description,
            due_date=updated_task.due_date,
            priority=updated_task.priority,
            category=updated_task.category,
            completed=updated_task.completed,
            completed_at=updated_task.completed_at,
            created_at=updated_task.created_at,
            updated_at=updated_task.updated_at,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating task {task_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/{task_id}/complete", response_model=TaskResponse)
async def complete_task(
    task_id: str,
    storage: Storage = Depends(get_storage),
) -> TaskResponse:
    """Mark a task as complete."""
    try:
        task = storage.complete_task(task_id)
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        return TaskResponse(
            id=task.id,
            title=task.title,
            description=task.description,
            due_date=task.due_date,
            priority=task.priority,
            category=task.category,
            completed=task.completed,
            completed_at=task.completed_at,
            created_at=task.created_at,
            updated_at=task.updated_at,
        )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error completing task {task_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/{task_id}", status_code=204)
async def delete_task(
    task_id: str,
    storage: Storage = Depends(get_storage),
):
    """Delete a task."""
    try:
        task = storage.get_task(task_id)
        
        if not task:
            raise HTTPException(status_code=404, detail="Task not found")
        
        storage.delete_task(task_id)
        return None
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting task {task_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))
