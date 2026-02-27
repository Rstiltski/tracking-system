"""
Heatmap Generator - GitHub-style contribution graphs.

Generates contribution heatmaps for habit tracking.

Usage:
    from brain.analytics.heatmap import HeatmapGenerator
    
    generator = HeatmapGenerator(storage, user_id)
    heatmap_data = generator.generate_heatmap(year=2026)
"""
from datetime import date, timedelta
from typing import Dict, Any, List, Optional
import calendar


class HeatmapGenerator:
    """
    Generates GitHub-style contribution heatmaps.

    Usage:
        generator = HeatmapGenerator(storage, user_id)
    """

    def __init__(self, storage: Any, user_id: str = ""):
        """
        Initialize heatmap generator.

        Args:
            storage: Storage instance
            user_id: User ID
        """
        self.storage = storage
        self.user_id = user_id

    def generate_heatmap(
        self,
        year: Optional[int] = None,
        habit_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate contribution heatmap data.

        Args:
            year: Year to generate (default: current year)
            habit_id: Optional specific habit ID

        Returns:
            Heatmap data dict with contributions by date
        """
        if year is None:
            year = date.today().year

        # Get all contributions for the year
        contributions = self._get_contributions(year, habit_id)

        # Generate heatmap data
        return {
            "year": year,
            "habit_id": habit_id,
            "total": sum(contributions.values()),
            "contributions": contributions,
            "levels": self._calculate_levels(contributions)
        }

    def _get_contributions(
        self,
        year: int,
        habit_id: Optional[str] = None
    ) -> Dict[str, int]:
        """
        Get contribution counts for each day.

        Args:
            year: Year
            habit_id: Optional habit ID

        Returns:
            Dict mapping date strings to contribution counts
        """
        contributions = {}
        
        # Initialize all days to 0
        start_date = date(year, 1, 1)
        end_date = date(year, 12, 31)
        current = start_date
        
        while current <= end_date:
            contributions[current.isoformat()] = 0
            current += timedelta(days=1)

        # Get habits
        if habit_id:
            habits = [self.storage.get_habit(habit_id)] if self.storage.get_habit(habit_id) else []
        else:
            habits = self.storage.get_habits(include_archived=False)

        # Count contributions
        for habit in habits:
            if not habit:
                continue
                
            for day in range(365):
                check_date = start_date + timedelta(days=day)
                if check_date.year != year:
                    continue
                    
                entry = self.storage.get_habit_entry(habit.id, check_date)
                if entry and hasattr(entry, 'value') and entry.value > 0:
                    date_str = check_date.isoformat()
                    contributions[date_str] = contributions.get(date_str, 0) + 1

        return contributions

    def _calculate_levels(
        self,
        contributions: Dict[str, int]
    ) -> Dict[int, int]:
        """
        Calculate contribution levels (0-4).

        Args:
            contributions: Contribution counts by date

        Returns:
            Dict mapping level (0-4) to count of days
        """
        levels = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0}
        
        if not contributions:
            return levels

        # Get max contributions per day
        max_contribs = max(contributions.values()) if contributions else 1

        # Assign levels
        for count in contributions.values():
            if count == 0:
                levels[0] += 1
            elif max_contribs <= 1:
                levels[1] += 1
            else:
                level = min(4, int((count / max_contribs) * 4) + 1)
                levels[level] += 1

        return levels

    def get_streak_data(
        self,
        habit_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get current and best streak data.

        Args:
            habit_id: Optional habit ID

        Returns:
            Streak data dict
        """
        habits = []
        
        if habit_id:
            habit = self.storage.get_habit(habit_id)
            if habit:
                habits = [habit]
        else:
            habits = self.storage.get_habits(include_archived=False)

        total_current = 0
        total_best = 0

        for habit in habits:
            current = self._calculate_streak(habit.id)
            best = self._calculate_best_streak(habit.id)
            total_current = max(total_current, current)
            total_best = max(total_best, best)

        return {
            "current": total_current,
            "best": total_best
        }

    def _calculate_streak(self, habit_id: str) -> int:
        """Calculate current streak."""
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

    def _calculate_best_streak(self, habit_id: str) -> int:
        """Calculate best streak ever."""
        best = 0
        current = 0
        today = date.today()

        for i in range(365 * 3):  # Check last 3 years
            check_date = today - timedelta(days=i)
            entry = self.storage.get_habit_entry(habit_id, check_date)
            
            if entry and hasattr(entry, 'value') and entry.value > 0:
                current += 1
                best = max(best, current)
            else:
                current = 0

        return best

    def get_summary_stats(self, year: Optional[int] = None) -> Dict[str, Any]:
        """
        Get summary statistics.

        Args:
            year: Year to analyze

        Returns:
            Summary stats dict
        """
        if year is None:
            year = date.today().year

        heatmap = self.generate_heatmap(year)
        streak_data = self.get_streak_data()

        return {
            "year": year,
            "total_contributions": heatmap["total"],
            "current_streak": streak_data["current"],
            "best_streak": streak_data["best"],
            "levels": heatmap["levels"]
        }


__all__ = [
    "HeatmapGenerator",
]
