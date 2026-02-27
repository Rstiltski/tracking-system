"""
Suggestion Engine - Generate smart habit suggestions.

Usage:
    from brain.ai.suggestion_engine import SuggestionEngine
    
    engine = SuggestionEngine(storage, user_id)
    suggestions = engine.get_suggestions(limit=5)
"""
from typing import List, Dict, Any, Optional
from brain.models.suggestion import (
    Suggestion,
    SuggestionType,
    SuggestionPriority,
    SUGGESTION_TEMPLATES,
)


class SuggestionEngine:
    """
    Generates personalized habit suggestions.

    Usage:
        engine = SuggestionEngine(storage, user_id)
    """

    def __init__(self, storage: Any, user_id: str = ""):
        """
        Initialize suggestion engine.

        Args:
            storage: Storage instance
            user_id: User ID
        """
        self.storage = storage
        self.user_id = user_id

    def get_suggestions(self, limit: int = 5) -> List[Suggestion]:
        """
        Get personalized suggestions.

        Args:
            limit: Maximum suggestions to return

        Returns:
            List of suggestions
        """
        suggestions = []

        # Get user's habits
        habits = self.storage.get_habits(include_archived=False)

        for habit in habits:
            # Analyze each habit for suggestions
            habit_suggestions = self._analyze_habit(habit)
            suggestions.extend(habit_suggestions)

        # Sort by priority
        priority_order = {
            SuggestionPriority.HIGH: 0,
            SuggestionPriority.MEDIUM: 1,
            SuggestionPriority.LOW: 2,
        }
        suggestions.sort(key=lambda s: priority_order.get(s.priority, 3))

        return suggestions[:limit]

    def _analyze_habit(self, habit: Any) -> List[Suggestion]:
        """
        Analyze a habit for suggestions.

        Args:
            habit: Habit object

        Returns:
            List of suggestions
        """
        suggestions = []

        # Get habit metrics
        streak = self._get_streak(habit.id)
        completion_rate = self._get_completion_rate(habit.id)

        # Declining streak suggestion
        if streak < 3 and streak > 0:
            suggestions.append(self._create_suggestion(
                "declining_streak",
                habit.id,
                {"habit_name": habit.name}
            ))

        # Low completion suggestion
        if completion_rate < 0.50:
            suggestions.append(self._create_suggestion(
                "low_completion",
                habit.id,
                {"habit_name": habit.name}
            ))

        # Ready for challenge suggestion
        if completion_rate > 0.90:
            suggestions.append(self._create_suggestion(
                "ready_for_challenge",
                habit.id,
                {"habit_name": habit.name}
            ))

        # Perfect week encouragement
        if completion_rate == 1.0:
            suggestions.append(self._create_suggestion(
                "perfect_week",
                habit.id,
                {"habit_name": habit.name}
            ))

        return suggestions

    def _create_suggestion(
        self,
        template_key: str,
        habit_id: str,
        context: Dict[str, Any]
    ) -> Suggestion:
        """
        Create suggestion from template.

        Args:
            template_key: Template key
            habit_id: Habit ID
            context: Context for formatting

        Returns:
            Suggestion object
        """
        template = SUGGESTION_TEMPLATES.get(template_key, {})

        # Format strings with context
        title = template.get("title", "").format(**context)
        description = template.get("description", "").format(**context)
        action = template.get("action", "").format(**context)

        return Suggestion(
            habit_id=habit_id,
            user_id=self.user_id,
            suggestion_type=template.get("type", SuggestionType.PATTERN),
            priority=template.get("priority", SuggestionPriority.MEDIUM),
            title=title,
            description=description,
            action=action
        )

    def _get_streak(self, habit_id: str) -> int:
        """Get current streak for habit."""
        streak = 0
        from datetime import date, timedelta
        today = date.today()

        for i in range(365):
            check_date = today - timedelta(days=i)
            entry = self.storage.get_habit_entry(habit_id, check_date)
            if entry and hasattr(entry, 'value') and entry.value > 0:
                streak += 1
            else:
                break

        return streak

    def _get_completion_rate(self, habit_id: str, days: int = 7) -> float:
        """Get completion rate for habit."""
        from datetime import date, timedelta
        today = date.today()
        completed = 0

        for i in range(days):
            check_date = today - timedelta(days=i)
            entry = self.storage.get_habit_entry(habit_id, check_date)
            if entry and hasattr(entry, 'value') and entry.value > 0:
                completed += 1

        return completed / days if days > 0 else 0.0

    def dismiss_suggestion(self, suggestion_id: str) -> bool:
        """
        Dismiss a suggestion.

        Args:
            suggestion_id: Suggestion ID

        Returns:
            True if dismissed
        """
        if hasattr(self.storage, 'dismiss_suggestion'):
            return self.storage.dismiss_suggestion(suggestion_id)
        return False

    def record_action(self, suggestion_id: str) -> bool:
        """
        Record that user acted on suggestion.

        Args:
            suggestion_id: Suggestion ID

        Returns:
            True if recorded
        """
        if hasattr(self.storage, 'record_suggestion_action'):
            return self.storage.record_suggestion_action(suggestion_id)
        return False


__all__ = [
    "SuggestionEngine",
]
