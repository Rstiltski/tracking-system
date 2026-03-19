"""
Habit Difficulty Adjuster - Automatic difficulty adjustment suggestions.

This engine analyzes user ratings and performance data to suggest
evidence-based habit modifications.

Key Features:
1. Suggestion Generation - Based on ratings and completion rates
2. Tiny Habit Conversion - Scale down to < 2 minute version
3. Progressive Overload - Gradually increase difficulty
4. Adjustment Tracking - Record and analyze effectiveness

Usage:
    from brain.behavioral.difficulty_adjuster import DifficultyAdjuster
    
    adjuster = DifficultyAdjuster(storage, habit_id)
    suggestion = adjuster.generate_suggestion()
    
    if suggestion:
        adjuster.apply_suggestion(suggestion)
"""
from datetime import date, timedelta
from typing import List, Dict, Any, Optional, Tuple
import logging

from brain.models.habit_difficulty import (
    DifficultyRating,
    AdjustmentType,
    DifficultyRatingEntry,
    DifficultyAdjustment,
    DifficultySuggestion,
    SUGGESTION_TEMPLATES,
)

logger = logging.getLogger(__name__)


class DifficultyAdjuster:
    """
    Adjusts habit difficulty based on user feedback and performance.

    Implements BJ Fogg's Tiny Habits methodology:
    - Start small (< 2 minutes)
    - Scale gradually (10-20% increases)
    - Reduce to tiny version when struggling

    Usage:
        adjuster = DifficultyAdjuster(storage, habit_id)
        suggestion = adjuster.generate_suggestion()
    """

    # Completion rate thresholds
    HIGH_COMPLETION_RATE = 0.85  # 85%+ = ready for challenge
    LOW_COMPLETION_RATE = 0.50  # < 50% = too difficult

    # Streak thresholds
    READY_FOR_INCREASE_STREAK = 7  # 7+ days = ready for increase
    STRUGGLING_STREAK = 3  # < 3 days = consider reduction

    # Adjustment parameters
    INCREASE_PERCENTAGE = 0.15  # 15% increase
    DECREASE_PERCENTAGE = 0.50  # 50% reduction (tiny version)

    def __init__(self, storage: Any, habit_id: str, user_id: str = ""):
        """
        Initialize difficulty adjuster.

        Args:
            storage: Storage instance for data access
            habit_id: ID of the habit to adjust
            user_id: ID of the user (optional)
        """
        self.storage = storage
        self.habit_id = habit_id
        self.user_id = user_id

    def generate_suggestion(self) -> Optional[DifficultySuggestion]:
        """
        Generate a difficulty adjustment suggestion.

        Analyzes user ratings and performance data to suggest
        an appropriate adjustment.

        Returns:
            DifficultySuggestion or None if no adjustment needed
        """
        # Get latest rating
        latest_rating = self.storage.get_difficulty_rating(self.habit_id)

        # If user recently rated, prioritize their feedback
        if latest_rating:
            # Handle both dict (from storage) and Model instances
            if isinstance(latest_rating, dict):
                rating_obj = DifficultyRatingEntry.from_dict(latest_rating)
            else:
                rating_obj = latest_rating
                
            suggestion = self._suggestion_from_rating(rating_obj)
            if suggestion:
                return suggestion

        # Otherwise, analyze performance data
        return self._suggestion_from_performance()

    def _suggestion_from_rating(
        self,
        rating: DifficultyRatingEntry
    ) -> Optional[DifficultySuggestion]:
        """
        Generate suggestion from user rating.

        Args:
            rating: Latest difficulty rating

        Returns:
            DifficultySuggestion or None
        """
        if rating.rating == DifficultyRating.TOO_EASY:
            return self._create_increase_suggestion(rating)
        elif rating.rating == DifficultyRating.TOO_HARD:
            return self._create_decrease_suggestion(rating)
        
        return None

    def _create_increase_suggestion(
        self,
        rating: DifficultyRatingEntry
    ) -> DifficultySuggestion:
        """
        Create suggestion to increase difficulty.

        Args:
            rating: User rating indicating too easy

        Returns:
            DifficultySuggestion for increase
        """
        habit = self.storage.get_habit(self.habit_id)
        current_target = habit.target_value if habit else 1.0
        new_target = current_target * (1 + self.INCREASE_PERCENTAGE)

        template = SUGGESTION_TEMPLATES[DifficultyRating.TOO_EASY]

        return DifficultySuggestion(
            habit_id=self.habit_id,
            suggestion_type=AdjustmentType.INCREASE_TARGET,
            title=template["title"],
            description=template["description"],
            current_value=current_target,
            suggested_value=round(new_target, 2),
            reason=f"You rated this habit as '{rating.rating.value.replace('_', ' ')}'. "
                   f"Consider increasing the target by {int(self.INCREASE_PERCENTAGE * 100)}%.",
            confidence=0.9  # High confidence from explicit feedback
        )

    def _create_decrease_suggestion(
        self,
        rating: DifficultyRatingEntry
    ) -> DifficultySuggestion:
        """
        Create suggestion to decrease difficulty (tiny version).

        Args:
            rating: User rating indicating too hard

        Returns:
            DifficultySuggestion for decrease
        """
        habit = self.storage.get_habit(self.habit_id)
        current_target = habit.target_value if habit else 1.0
        new_target = current_target * (1 - self.DECREASE_PERCENTAGE)

        template = SUGGESTION_TEMPLATES[DifficultyRating.TOO_HARD]

        return DifficultySuggestion(
            habit_id=self.habit_id,
            suggestion_type=AdjustmentType.DECREASE_TARGET,
            title=template["title"],
            description=template["description"],
            current_value=current_target,
            suggested_value=round(new_target, 2),
            reason=f"You rated this habit as '{rating.rating.value.replace('_', ' ')}'. "
                   f"Let's make it tiny - reduce by {int(self.DECREASE_PERCENTAGE * 100)}%.",
            confidence=0.95  # Very high confidence - user struggling
        )

    def _suggestion_from_performance(self) -> Optional[DifficultySuggestion]:
        """
        Generate suggestion from performance data.

        Analyzes completion rates and streaks to suggest adjustments.

        Returns:
            DifficultySuggestion or None
        """
        completion_rate = self._calculate_completion_rate(days=14)
        current_streak = self._calculate_current_streak()

        # High completion + long streak = ready for challenge
        if completion_rate >= self.HIGH_COMPLETION_RATE and current_streak >= self.READY_FOR_INCREASE_STREAK:
            return self._create_performance_increase_suggestion(completion_rate, current_streak)

        # Low completion + short streak = struggling
        if completion_rate < self.LOW_COMPLETION_RATE and current_streak < self.STRUGGLING_STREAK:
            return self._create_performance_decrease_suggestion(completion_rate, current_streak)

        return None

    def _create_performance_increase_suggestion(
        self,
        completion_rate: float,
        current_streak: int
    ) -> DifficultySuggestion:
        """
        Create suggestion based on high performance.

        Args:
            completion_rate: Current completion rate
            current_streak: Current streak length

        Returns:
            DifficultySuggestion for increase
        """
        habit = self.storage.get_habit(self.habit_id)
        current_target = habit.target_value if habit else 1.0
        new_target = current_target * (1 + self.INCREASE_PERCENTAGE)

        return DifficultySuggestion(
            habit_id=self.habit_id,
            suggestion_type=AdjustmentType.INCREASE_TARGET,
            title="Great progress! Ready for more? 🎉",
            description="You've been crushing this habit! Time to level up.",
            current_value=current_target,
            suggested_value=round(new_target, 2),
            reason=f"{completion_rate:.0f}% completion rate over {current_streak} days. "
                   f"You're ready for a challenge!",
            confidence=0.75  # Medium-high confidence from performance
        )

    def _create_performance_decrease_suggestion(
        self,
        completion_rate: float,
        current_streak: int
    ) -> DifficultySuggestion:
        """
        Create suggestion based on low performance.

        Args:
            completion_rate: Current completion rate
            current_streak: Current streak length

        Returns:
            DifficultySuggestion for decrease
        """
        habit = self.storage.get_habit(self.habit_id)
        current_target = habit.target_value if habit else 1.0
        new_target = max(0.1, current_target * (1 - self.DECREASE_PERCENTAGE))

        return DifficultySuggestion(
            habit_id=self.habit_id,
            suggestion_type=AdjustmentType.DECREASE_TARGET,
            title="Let's make it easier 🐜",
            description="This habit seems challenging. Try the 2-minute version!",
            current_value=current_target,
            suggested_value=round(new_target, 2),
            reason=f"{completion_rate:.0f}% completion rate. "
                   f"Making it tiny will help build consistency.",
            confidence=0.70  # Medium confidence from performance
        )

    def apply_suggestion(
        self,
        suggestion: DifficultySuggestion,
        user_reason: str = ""
    ) -> DifficultyAdjustment:
        """
        Apply a difficulty adjustment suggestion.

        Args:
            suggestion: Suggestion to apply
            user_reason: Optional user-provided reason

        Returns:
            DifficultyAdjustment record
        """
        habit = self.storage.get_habit(self.habit_id)

        if not habit:
            raise ValueError(f"Habit {self.habit_id} not found")

        # Create adjustment record
        adjustment = DifficultyAdjustment(
            habit_id=self.habit_id,
            user_id=self.user_id,
            adjustment_type=suggestion.suggestion_type,
            old_value=suggestion.current_value,
            new_value=suggestion.suggested_value,
            reason=user_reason or suggestion.reason
        )

        # Apply the adjustment based on type
        if suggestion.suggestion_type == AdjustmentType.INCREASE_TARGET:
            self.storage.update_habit(
                self.habit_id,
                target_value=suggestion.suggested_value
            )
        elif suggestion.suggestion_type == AdjustmentType.DECREASE_TARGET:
            self.storage.update_habit(
                self.habit_id,
                target_value=suggestion.suggested_value
            )
        elif suggestion.suggestion_type == AdjustmentType.CHANGE_FREQUENCY:
            self.storage.update_habit(
                self.habit_id,
                frequency=suggestion.suggested_value
            )

        # Save adjustment record
        self.storage.save_difficulty_adjustment(self.habit_id, adjustment.to_dict())

        logger.info(
            f"Applied difficulty adjustment to habit {self.habit_id}: "
            f"{suggestion.suggestion_type.value} from {suggestion.current_value} "
            f"to {suggestion.suggested_value}"
        )

        return adjustment

    def record_rating(
        self,
        rating: DifficultyRating,
        notes: str = ""
    ) -> DifficultyRatingEntry:
        """
        Record a difficulty rating from the user.

        Args:
            rating: User's difficulty rating
            notes: Optional user notes

        Returns:
            DifficultyRatingEntry record
        """
        entry = DifficultyRatingEntry(
            habit_id=self.habit_id,
            user_id=self.user_id,
            rating=rating,
            notes=notes
        )

        # Save rating
        self.storage.save_difficulty_rating(self.habit_id, entry.to_dict())

        logger.info(
            f"Recorded difficulty rating for habit {self.habit_id}: {rating.value}"
        )

        return entry

    def _calculate_completion_rate(self, days: int = 14) -> float:
        """
        Calculate completion rate over N days.

        Args:
            days: Number of days to analyze

        Returns:
            Completion rate (0.0-1.0)
        """
        today = date.today()
        completed = 0

        for i in range(days):
            check_date = today - timedelta(days=i)
            entry = self.storage.get_habit_entry(self.habit_id, check_date)
            if entry and hasattr(entry, 'value') and entry.value > 0:
                completed += 1

        return completed / days if days > 0 else 0.0

    def _calculate_current_streak(self) -> int:
        """
        Calculate current streak.

        Returns:
            Current streak length in days
        """
        streak = 0
        today = date.today()

        for i in range(365):
            check_date = today - timedelta(days=i)
            entry = self.storage.get_habit_entry(self.habit_id, check_date)
            if entry and hasattr(entry, 'value') and entry.value > 0:
                streak += 1
            else:
                break

        return streak

    def get_adjustment_history(self, limit: int = 10) -> List[DifficultyAdjustment]:
        """
        Get adjustment history for this habit.

        Args:
            limit: Maximum number of records to return

        Returns:
            List of DifficultyAdjustment records
        """
        history = self.storage.get_difficulty_adjustment_history(self.habit_id, limit)
        return [DifficultyAdjustment.from_dict(h) for h in history]

    def get_effectiveness_stats(self) -> Dict[str, float]:
        """
        Get effectiveness statistics for adjustments.

        Returns:
            Dict with average effectiveness and count
        """
        history = self.get_adjustment_history(limit=50)
        
        if not history:
            return {"average_effectiveness": 0.0, "count": 0}

        effectiveness_ratings = [
            h.effectiveness for h in history if h.effectiveness is not None
        ]

        if not effectiveness_ratings:
            return {"average_effectiveness": 0.0, "count": len(history)}

        return {
            "average_effectiveness": sum(effectiveness_ratings) / len(effectiveness_ratings),
            "count": len(history)
        }


def get_tiny_habit_version(habit_name: str, current_target: float) -> str:
    """
    Generate a "tiny version" description for a habit.

    Based on BJ Fogg's 2-minute rule.

    Args:
        habit_name: Name of the habit
        current_target: Current target value

    Returns:
        Tiny version description
    """
    tiny_versions = {
        "exercise": "2 minutes of stretching",
        "meditation": "1 minute of deep breathing",
        "reading": "Read 1 page",
        "writing": "Write 1 sentence",
        "water": "Drink 1 glass",
        "practice": "Practice for 2 minutes",
    }

    # Check for keyword matches
    habit_lower = habit_name.lower()
    for keyword, tiny in tiny_versions.items():
        if keyword in habit_lower:
            return tiny

    # Default: reduce to 2-minute version
    return f"2-minute version of {habit_name}"


__all__ = [
    "DifficultyAdjuster",
    "get_tiny_habit_version",
]
