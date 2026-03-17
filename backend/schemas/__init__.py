"""
Pydantic Schemas

Request and response models for the API.
These sit between the existing models and the API endpoints.

Phase 13: Decoupled Architecture Migration
"""

from backend.schemas.habits import (
    HabitCreate,
    HabitUpdate,
    HabitResponse,
)

from backend.schemas.tasks import (
    TaskCreate,
    TaskUpdate,
    TaskResponse,
)

from backend.schemas.goals import (
    GoalCreate,
    GoalUpdate,
    GoalResponse,
)

from backend.schemas.health import (
    HealthEntryCreate,
    HealthEntryUpdate,
    HealthEntryResponse,
)

__all__ = [
    "HabitCreate",
    "HabitUpdate", 
    "HabitResponse",
    "TaskCreate",
    "TaskUpdate", 
    "TaskResponse",
    "GoalCreate",
    "GoalUpdate",
    "GoalResponse",
    "HealthEntryCreate",
    "HealthEntryUpdate",
    "HealthEntryResponse",
]
