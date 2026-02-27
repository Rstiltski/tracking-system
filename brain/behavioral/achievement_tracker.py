"""
Achievement Tracker - Track and unlock achievements.

This tracker monitors user progress and automatically unlocks achievements
when requirements are met.

Usage:
    from brain.behavioral.achievement_tracker import AchievementTracker
    
    tracker = AchievementTracker(storage, user_id)
    tracker.check_achievements()
    unlocked = tracker.get_unlocked_achievements()
"""
from datetime import date, datetime
from typing import List, Dict, Any, Optional
import logging

from brain.models.achievement import (
    Achievement,
    AchievementCategory,
    AchievementTier,
    UserAchievement,
    DEFAULT_ACHIEVEMENTS,
    get_xp_multiplier,
)

logger = logging.getLogger(__name__)


class AchievementTracker:
    """
    Tracks and unlocks user achievements.

    Usage:
        tracker = AchievementTracker(storage, user_id)
        tracker.check_achievements()
    """

    def __init__(self, storage: Any, user_id: str = ""):
        """
        Initialize achievement tracker.

        Args:
            storage: Storage instance
            user_id: User ID
        """
        self.storage = storage
        self.user_id = user_id
        self._achievements = DEFAULT_ACHIEVEMENTS.copy()

    def check_achievements(self) -> List[Achievement]:
        """
        Check and unlock achievements for user.

        Returns:
            List of newly unlocked achievements
        """
        newly_unlocked = []

        # Get user data
        user_data = self._collect_user_data()

        # Check each achievement
        for achievement in self._achievements:
            # Skip if already unlocked
            if self._is_achievement_unlocked(achievement.id):
                continue

            # Check if requirement is met
            if achievement.check_requirement(user_data):
                self._unlock_achievement(achievement)
                newly_unlocked.append(achievement)
                logger.info(
                    f"User {self.user_id} unlocked achievement: {achievement.name}"
                )

        return newly_unlocked

    def _collect_user_data(self) -> Dict[str, Any]:
        """
        Collect user data for achievement checking.

        Returns:
            Dict with user metrics
        """
        habits = self.storage.get_habits(include_archived=False)

        # Calculate metrics
        total_completions = 0
        max_streak = 0
        perfect_weeks = 0

        for habit in habits:
            streak = self._calculate_streak(habit.id)
            max_streak = max(max_streak, streak)

            # Count completions (last 7 days for perfect week check)
            completions = self._count_recent_completions(habit.id, 7)
            total_completions += completions

            if completions == 7:
                perfect_weeks += 1

        return {
            "streak": max_streak,
            "total_completions": total_completions,
            "perfect_weeks": perfect_weeks,
            "habit_count": len(habits),
        }

    def _calculate_streak(self, habit_id: str) -> int:
        """Calculate current streak for a habit."""
        streak = 0
        today = date.today()

        for i in range(365):
            check_date = today - timedelta(days=i)
            entry = self.storage.get_habit_entry(habit_id, check_date)
            if entry and hasattr(entry, 'value') and entry.value > 0:
                streak += 1
            else:
                break

        return streak

    def _count_recent_completions(self, habit_id: str, days: int) -> int:
        """Count completions in last N days."""
        completions = 0
        today = date.today()

        for i in range(days):
            check_date = today - timedelta(days=i)
            entry = self.storage.get_habit_entry(habit_id, check_date)
            if entry and hasattr(entry, 'value') and entry.value > 0:
                completions += 1

        return completions

    def _is_achievement_unlocked(self, achievement_id: str) -> bool:
        """Check if achievement is already unlocked."""
        if hasattr(self.storage, 'get_user_achievement'):
            return self.storage.get_user_achievement(
                self.user_id, achievement_id
            ) is not None
        return False

    def _unlock_achievement(self, achievement: Achievement) -> None:
        """
        Unlock an achievement.

        Args:
            achievement: Achievement to unlock
        """
        user_achievement = UserAchievement(
            achievement_id=achievement.id,
            user_id=self.user_id,
            xp_awarded=achievement.xp_reward
        )

        # Save to storage
        if hasattr(self.storage, 'unlock_achievement'):
            self.storage.unlock_achievement(
                self.user_id,
                achievement.id,
                achievement.xp_reward
            )

        # Add XP
        if hasattr(self.storage, 'add_xp'):
            self.storage.add_xp(achievement.xp_reward)

    def get_unlocked_achievements(self) -> List[UserAchievement]:
        """
        Get user's unlocked achievements.

        Returns:
            List of unlocked achievements
        """
        if hasattr(self.storage, 'get_user_achievements'):
            return self.storage.get_user_achievements(self.user_id)
        return []

    def get_locked_achievements(self) -> List[Achievement]:
        """
        Get achievements not yet unlocked.

        Returns:
            List of locked achievements
        """
        unlocked_ids = {
            ua.achievement_id for ua in self.get_unlocked_achievements()
        }

        return [
            a for a in self._achievements
            if a.id not in unlocked_ids
        ]

    def get_progress_toward_achievement(
        self,
        achievement: Achievement
    ) -> Dict[str, Any]:
        """
        Get progress toward an achievement.

        Args:
            achievement: Achievement to check

        Returns:
            Progress dict with current, required, and percentage
        """
        user_data = self._collect_user_data()

        req_type = achievement.requirement_data.get("type")
        req_value = achievement.requirement_data.get("value", 0)

        current = 0
        if req_type == "streak_days":
            current = user_data.get("streak", 0)
        elif req_type == "perfect_weeks":
            current = user_data.get("perfect_weeks", 0)
        elif req_type == "total_completions":
            current = user_data.get("total_completions", 0)

        percentage = (current / req_value * 100) if req_value > 0 else 0

        return {
            "achievement_id": achievement.id,
            "achievement_name": achievement.name,
            "current": current,
            "required": req_value,
            "percentage": min(100, percentage)
        }

    def get_xp_multiplier(self) -> float:
        """
        Get current XP multiplier based on achievements/streaks.

        Returns:
            XP multiplier (1.0 = no bonus)
        """
        user_data = self._collect_user_data()
        streak = user_data.get("streak", 0)
        return get_xp_multiplier(streak)


# Import timedelta at module level
from datetime import timedelta


__all__ = [
    "AchievementTracker",
]
