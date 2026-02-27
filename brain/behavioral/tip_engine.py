"""
Environment Tip Engine - Personalized tip recommendations.

Usage:
    from brain.behavioral.tip_engine import TipEngine
    
    engine = TipEngine(storage, user_id)
    tips = engine.get_personalized_tips(habit_id)
"""
from typing import List, Dict, Any, Optional
from brain.models.environment_tip import (
    EnvironmentTip,
    TipCategory,
    HabitType,
    UserTipInteraction,
    DEFAULT_TIPS,
    get_tips_by_habit_type,
)


class TipEngine:
    """
    Provides personalized environment tips.

    Usage:
        engine = TipEngine(storage, user_id)
    """

    def __init__(self, storage: Any, user_id: str = ""):
        """
        Initialize tip engine.

        Args:
            storage: Storage instance
            user_id: User ID
        """
        self.storage = storage
        self.user_id = user_id

    def get_personalized_tips(
        self,
        habit_id: str,
        limit: int = 3
    ) -> List[EnvironmentTip]:
        """
        Get personalized tips for a habit.

        Args:
            habit_id: Habit ID
            limit: Maximum tips to return

        Returns:
            List of recommended tips
        """
        # Get habit info
        habit = self.storage.get_habit(habit_id)
        if not habit:
            return DEFAULT_TIPS[:limit]

        # Determine habit type from name
        habit_type = self._infer_habit_type(habit.name)

        # Get matching tips
        tips = get_tips_by_habit_type(habit_type, DEFAULT_TIPS)

        # Filter out already-tried tips
        tried_tip_ids = self._get_tried_tip_ids(habit_id)
        tips = [t for t in tips if t.id not in tried_tip_ids]

        # Sort by effectiveness
        tips.sort(key=lambda t: t.effectiveness, reverse=True)

        return tips[:limit]

    def _infer_habit_type(self, habit_name: str) -> HabitType:
        """
        Infer habit type from name.

        Args:
            habit_name: Habit name

        Returns:
            Inferred HabitType
        """
        name_lower = habit_name.lower()

        mappings = {
            "exercise": HabitType.EXERCISE,
            "workout": HabitType.EXERCISE,
            "run": HabitType.EXERCISE,
            "gym": HabitType.EXERCISE,
            "meditation": HabitType.MEDITATION,
            "meditate": HabitType.MEDITATION,
            "mindfulness": HabitType.MEDITATION,
            "read": HabitType.READING,
            "reading": HabitType.READING,
            "book": HabitType.READING,
            "write": HabitType.WRITING,
            "writing": HabitType.WRITING,
            "journal": HabitType.WRITING,
            "sleep": HabitType.SLEEP,
            "bed": HabitType.SLEEP,
            "eat": HabitType.NUTRITION,
            "diet": HabitType.NUTRITION,
            "water": HabitType.NUTRITION,
            "work": HabitType.PRODUCTIVITY,
            "focus": HabitType.PRODUCTIVITY,
            "study": HabitType.LEARNING,
            "learn": HabitType.LEARNING,
            "brush": HabitType.HYGIENE,
            "floss": HabitType.HYGIENE,
        }

        for keyword, habit_type in mappings.items():
            if keyword in name_lower:
                return habit_type

        return HabitType.GENERAL

    def _get_tried_tip_ids(self, habit_id: str) -> List[str]:
        """
        Get IDs of tips already tried for this habit.

        Args:
            habit_id: Habit ID

        Returns:
            List of tried tip IDs
        """
        if hasattr(self.storage, 'get_tip_interactions'):
            interactions = self.storage.get_tip_interactions(
                self.user_id,
                habit_id
            )
            return [i["tip_id"] for i in interactions]
        return []

    def record_tip_interaction(
        self,
        tip_id: str,
        habit_id: str,
        action: str,
        notes: str = ""
    ) -> UserTipInteraction:
        """
        Record user interaction with a tip.

        Args:
            tip_id: Tip ID
            habit_id: Habit ID
            action: Action type
            notes: Optional notes

        Returns:
            Created interaction
        """
        interaction = UserTipInteraction(
            tip_id=tip_id,
            user_id=self.user_id,
            habit_id=habit_id,
            action=action,
            notes=notes
        )

        if hasattr(self.storage, 'save_tip_interaction'):
            self.storage.save_tip_interaction(interaction.to_dict())

        return interaction

    def get_tips_by_category(
        self,
        category: TipCategory,
        limit: int = 5
    ) -> List[EnvironmentTip]:
        """
        Get tips by category.

        Args:
            category: Tip category
            limit: Maximum tips to return

        Returns:
            List of tips
        """
        from brain.models.environment_tip import get_tips_by_category
        tips = get_tips_by_category(category, DEFAULT_TIPS)
        return tips[:limit]


__all__ = [
    "TipEngine",
]
