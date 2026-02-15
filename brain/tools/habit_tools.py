"""
Habit Tools - Tools for habit management in the brain system.

These tools integrate with the brain's tool system and can be used
by AI agents or directly by the application.

Each tool follows the brain's tool contract pattern.
"""
from datetime import date, timedelta
from typing import List, Optional, Dict, Any
import json

from brain.models import (
    Habit, HabitType, HabitScore,
    Frequency, StreakFreeze
)
from brain.brains.habit_brain import HabitBrain
from brain.tools.decorators import tool


# === Habit Management Tools ===

@tool(
    name="create_habit",
    description="Create a new habit to track",
    parameters={
        "name": {"type": "string", "description": "Name of the habit"},
        "frequency": {"type": "string", "enum": ["daily", "weekly", "custom"], "default": "daily"},
        "icon": {"type": "string", "description": "Emoji icon for the habit", "default": "🎯"},
        "description": {"type": "string", "description": "Optional description", "default": ""}
    }
)
def create_habit_tool(
    brain: HabitBrain,
    name: str,
    frequency: str = "daily",
    icon: str = "🎯",
    description: str = ""
) -> Dict[str, Any]:
    """
    Create a new habit.
    
    Args:
        brain: The HabitBrain instance
        name: Habit name
        frequency: "daily", "weekly", or "custom"
        icon: Emoji icon
        description: Optional description
    
    Returns:
        Result with created habit data
    """
    result = brain.create_habit(
        name=name,
        frequency=frequency,
        icon=icon,
        description=description
    )
    
    if result.success:
        return {
            "success": True,
            "habit": result.data.to_dict(),
            "message": result.message
        }
    return {"success": False, "error": result.message}


@tool(
    name="list_habits",
    description="List all habits with their current scores and streaks"
)
def list_habits_tool(brain: HabitBrain) -> Dict[str, Any]:
    """
    List all habits.
    
    Args:
        brain: The HabitBrain instance
    
    Returns:
        List of habits with scores
    """
    habits = brain.get_all_habits()
    
    return {
        "success": True,
        "habits": [
            {
                "id": h.id,
                "name": h.name,
                "icon": h.icon,
                "score": h.score.percentage,
                "score_category": h.score.get_category(),
                "streak": h.streak_count,
                "frequency": str(h.frequency)
            }
            for h in habits
        ],
        "total": len(habits)
    }


@tool(
    name="get_habit_score",
    description="Get the current score for a habit",
    parameters={
        "habit_id": {"type": "string", "description": "ID of the habit"}
    }
)
def get_habit_score_tool(brain: HabitBrain, habit_id: str) -> Dict[str, Any]:
    """
    Get a habit's score.
    
    Args:
        brain: The HabitBrain instance
        habit_id: ID of the habit
    
    Returns:
        Score information
    """
    score = brain.get_score(habit_id)
    
    if score is None:
        return {"success": False, "error": "Habit not found"}
    
    return {
        "success": True,
        "habit_id": habit_id,
        "score": {
            "value": score.value,
            "percentage": score.percentage,
            "trend": score.trend,
            "category": score.get_category()
        }
    }


@tool(
    name="mark_habit_complete",
    description="Mark a habit as completed for today or a specific date",
    parameters={
        "habit_id": {"type": "string", "description": "ID of the habit"},
        "date": {"type": "string", "description": "Date in YYYY-MM-DD format (optional)", "default": "today"}
    }
)
def mark_habit_complete_tool(
    brain: HabitBrain,
    habit_id: str,
    date_str: Optional[str] = None
) -> Dict[str, Any]:
    """
    Mark a habit as completed.
    
    Args:
        brain: The HabitBrain instance
        habit_id: ID of the habit
        date_str: Optional date string (YYYY-MM-DD), defaults to today
    
    Returns:
        Result of the operation
    """
    entry_date = None
    if date_str and date_str != "today":
        try:
            entry_date = date.fromisoformat(date_str)
        except ValueError:
            return {"success": False, "error": "Invalid date format. Use YYYY-MM-DD"}
    
    result = brain.mark_completed(habit_id, entry_date)
    
    if result.success:
        habit = brain.get_habit(habit_id)
        return {
            "success": True,
            "message": result.message,
            "habit": {
                "name": habit.name if habit else None,
                "new_score": habit.score.percentage if habit else None,
                "streak": habit.streak_count if habit else None
            }
        }
    return {"success": False, "error": result.message}


@tool(
    name="get_habits_summary",
    description="Get a summary of all habits including scores, streaks, and inventory"
)
def get_habits_summary_tool(brain: HabitBrain) -> Dict[str, Any]:
    """
    Get habits summary.
    
    Args:
        brain: The HabitBrain instance
    
    Returns:
        Summary statistics
    """
    return {
        "success": True,
        **brain.get_habits_summary()
    }


@tool(
    name="purchase_streak_freeze",
    description="Purchase a streak freeze using XP"
)
def purchase_streak_freeze_tool(brain: HabitBrain) -> Dict[str, Any]:
    """
    Purchase a streak freeze.
    
    Args:
        brain: The HabitBrain instance
    
    Returns:
        Result of the purchase
    """
    result = brain.purchase_freeze()
    
    return {
        "success": result.success,
        "message": result.message if result.success else result.error,
        "freezes_available": brain.get_freeze_count(),
        "xp_remaining": brain.inventory.total_xp
    }


@tool(
    name="use_streak_freeze",
    description="Use a streak freeze to preserve a streak on a missed day",
    parameters={
        "habit_id": {"type": "string", "description": "ID of the habit"},
        "date": {"type": "string", "description": "Date to freeze in YYYY-MM-DD format"}
    }
)
def use_streak_freeze_tool(
    brain: HabitBrain,
    habit_id: str,
    date_str: str
) -> Dict[str, Any]:
    """
    Use a streak freeze.
    
    Args:
        brain: The HabitBrain instance
        habit_id: ID of the habit
        date_str: Date to freeze (YYYY-MM-DD)
    
    Returns:
        Result of using the freeze
    """
    try:
        freeze_date = date.fromisoformat(date_str)
    except ValueError:
        return {"success": False, "error": "Invalid date format. Use YYYY-MM-DD"}
    
    result = brain.use_freeze(habit_id, freeze_date)
    
    return {
        "success": result.success,
        "message": result.message if result.success else result.error,
        "freezes_remaining": brain.get_freeze_count()
    }


@tool(
    name="get_score_history",
    description="Get score history for a habit over a number of days",
    parameters={
        "habit_id": {"type": "string", "description": "ID of the habit"},
        "days": {"type": "integer", "description": "Number of days of history", "default": 30}
    }
)
def get_score_history_tool(
    brain: HabitBrain,
    habit_id: str,
    days: int = 30
) -> Dict[str, Any]:
    """
    Get score history for a habit.
    
    Args:
        brain: The HabitBrain instance
        habit_id: ID of the habit
        days: Number of days of history
    
    Returns:
        Score history data
    """
    scores = brain.get_score_history(habit_id, days)
    
    if not scores:
        return {"success": False, "error": "Habit not found or no history"}
    
    return {
        "success": True,
        "habit_id": habit_id,
        "days": days,
        "scores": [
            {
                "date": s.timestamp.isoformat(),
                "value": s.value,
                "percentage": s.percentage,
                "trend": s.trend
            }
            for s in scores
        ],
        "average_score": sum(s.value for s in scores) / len(scores)
    }


@tool(
    name="delete_habit",
    description="Delete a habit permanently",
    parameters={
        "habit_id": {"type": "string", "description": "ID of the habit to delete"}
    }
)
def delete_habit_tool(brain: HabitBrain, habit_id: str) -> Dict[str, Any]:
    """
    Delete a habit.
    
    Args:
        brain: The HabitBrain instance
        habit_id: ID of the habit to delete
    
    Returns:
        Result of deletion
    """
    result = brain.delete_habit(habit_id)
    
    return {
        "success": result.success,
        "message": result.message if result.success else result.error
    }


# Export all tools
HABIT_TOOLS = [
    create_habit_tool,
    list_habits_tool,
    get_habit_score_tool,
    mark_habit_complete_tool,
    get_habits_summary_tool,
    purchase_streak_freeze_tool,
    use_streak_freeze_tool,
    get_score_history_tool,
    delete_habit_tool,
]


def register_habit_tools():
    """
    Register all habit tools with the brain's tool registry.
    
    Usage:
        from brain.tools.habit_tools import register_habit_tools
        register_habit_tools()
    """
    from brain.tools.registry import ToolRegistry
    
    for tool_func in HABIT_TOOLS:
        ToolRegistry.register(tool_func)