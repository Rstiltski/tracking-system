"""
Event Tracker - Track user actions and system events.

This module provides comprehensive event tracking for:
- Habit events (completion, skip, modification)
- User interactions (feature usage, UI clicks)
- Intervention logs (suggestions shown, actions taken)

Usage:
    from brain.analytics.event_tracker import EventTracker
    
    tracker = EventTracker(storage, user_id)
    tracker.log_habit_event(habit_id, "completed", {"streak": 7})
    tracker.log_interaction("difficulty_widget", "rated")
    tracker.log_intervention(habit_id, "burnout_warning", "dismissed")
"""
from datetime import datetime, date
from typing import Dict, Any, Optional, List
from enum import Enum
import logging
import json

logger = logging.getLogger(__name__)


class HabitEventType(str, Enum):
    """Types of habit events."""
    COMPLETED = "completed"
    SKIPPED = "skipped"
    UNMARKED = "unmarked"
    MODIFIED = "modified"
    CREATED = "created"
    ARCHIVED = "archived"
    DELETED = "deleted"


class InteractionType(str, Enum):
    """Types of user interactions."""
    VIEW = "view"
    CLICK = "click"
    RATE = "rate"
    DISMISS = "dismiss"
    APPLY = "apply"
    CREATE = "create"
    EDIT = "edit"
    DELETE = "delete"


class InterventionType(str, Enum):
    """Types of interventions."""
    BURNOUT_WARNING = "burnout_warning"
    DIFFICULTY_SUGGESTION = "difficulty_suggestion"
    RELAPSE_PLAN = "relapse_plan"
    TEMPLATE_SUGGESTION = "template_suggestion"
    ACHIEVEMENT_UNLOCK = "achievement_unlock"


class EventTracker:
    """
    Tracks user actions and system events.

    Usage:
        tracker = EventTracker(storage, user_id)
    """

    def __init__(self, storage: Any, user_id: str = ""):
        """
        Initialize event tracker.

        Args:
            storage: Storage instance
            user_id: User ID
        """
        self.storage = storage
        self.user_id = user_id

    def log_habit_event(
        self,
        habit_id: str,
        event_type: HabitEventType,
        event_data: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log a habit-related event.

        Args:
            habit_id: Habit ID
            event_type: Type of event
            event_data: Additional event data
        """
        event = {
            "id": self._generate_id(),
            "habit_id": habit_id,
            "user_id": self.user_id,
            "event_type": event_type.value,
            "event_data": json.dumps(event_data or {}),
            "timestamp": datetime.now().isoformat()
        }

        # Store event
        if hasattr(self.storage, 'log_habit_event'):
            self.storage.log_habit_event(event)
        else:
            # Fallback: just log to logger
            logger.info(f"Habit event: {event_type.value} for {habit_id}")

    def log_interaction(
        self,
        feature: str,
        action: InteractionType,
        metadata: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log a user interaction with a feature.

        Args:
            feature: Feature name
            action: Type of interaction
            metadata: Additional metadata
        """
        interaction = {
            "id": self._generate_id(),
            "user_id": self.user_id,
            "feature": feature,
            "action": action.value,
            "metadata": json.dumps(metadata or {}),
            "timestamp": datetime.now().isoformat()
        }

        if hasattr(self.storage, 'log_interaction'):
            self.storage.log_interaction(interaction)
        else:
            logger.info(f"Interaction: {action.value} on {feature}")

    def log_intervention(
        self,
        habit_id: str,
        intervention_type: InterventionType,
        user_action: str,
        details: Optional[Dict[str, Any]] = None
    ) -> None:
        """
        Log an intervention shown to user.

        Args:
            habit_id: Habit ID
            intervention_type: Type of intervention
            user_action: User's response (accepted, dismissed, etc.)
            details: Additional details
        """
        intervention = {
            "id": self._generate_id(),
            "habit_id": habit_id,
            "user_id": self.user_id,
            "intervention_type": intervention_type.value,
            "user_action": user_action,
            "details": json.dumps(details or {}),
            "timestamp": datetime.now().isoformat()
        }

        if hasattr(self.storage, 'log_intervention'):
            self.storage.log_intervention(intervention)
        else:
            logger.info(f"Intervention: {intervention_type.value} - {user_action}")

    def _generate_id(self) -> str:
        """Generate unique event ID."""
        import uuid
        return str(uuid.uuid4())[:8]

    def get_user_events(
        self,
        limit: int = 100,
        event_type: Optional[HabitEventType] = None
    ) -> List[Dict[str, Any]]:
        """
        Get user's habit events.

        Args:
            limit: Maximum events to return
            event_type: Optional type filter

        Returns:
            List of events
        """
        if hasattr(self.storage, 'get_user_events'):
            return self.storage.get_user_events(
                self.user_id,
                limit,
                event_type.value if event_type else None
            )
        return []

    def get_interaction_stats(
        self,
        feature: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get interaction statistics.

        Args:
            feature: Optional feature filter

        Returns:
            Stats dict
        """
        if hasattr(self.storage, 'get_interaction_stats'):
            return self.storage.get_interaction_stats(
                self.user_id,
                feature
            )
        return {}


__all__ = [
    "EventTracker",
    "HabitEventType",
    "InteractionType",
    "InterventionType",
]
