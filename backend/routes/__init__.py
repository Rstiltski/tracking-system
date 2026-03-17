"""
API Routes

Route modules for the FastAPI application.

Phase 13: Decoupled Architecture Migration
"""

from backend.routes import habits
from backend.routes import tasks
from backend.routes import goals
from backend.routes import health

__all__ = ["habits", "tasks", "goals", "health"]
