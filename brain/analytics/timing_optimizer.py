"""
Timing Optimizer - Find optimal times for habit performance.

Based on analysis of completion patterns by time and day.

Usage:
    from brain.analytics.timing_optimizer import TimingOptimizer
    
    optimizer = TimingOptimizer(storage, habit_id)
    best_times = optimizer.analyze_optimal_time()
"""
from datetime import date, timedelta, datetime
from typing import Dict, Any, List, Optional


class TimingOptimizer:
    """
    Analyzes and recommends optimal timing for habits.

    Usage:
        optimizer = TimingOptimizer(storage, habit_id)
    """

    def __init__(self, storage: Any, habit_id: str):
        """
        Initialize timing optimizer.

        Args:
            storage: Storage instance
            habit_id: Habit ID
        """
        self.storage = storage
        self.habit_id = habit_id

    def analyze_optimal_time(self, days: int = 30) -> Dict[str, Any]:
        """
        Analyze optimal time for habit performance.

        Args:
            days: Number of days to analyze

        Returns:
            Optimal time data dict
        """
        # Get completion data by hour
        hour_data = self._get_hourly_completions(days)
        
        # Get completion data by day of week
        day_data = self._get_day_completions(days)

        # Find best times
        best_hour = max(hour_data, key=hour_data.get) if hour_data else 9
        best_day = max(day_data, key=day_data.get) if day_data else "Monday"

        return {
            "best_hour": best_hour,
            "best_hour_label": self._format_hour(best_hour),
            "best_day": best_day,
            "hourly_data": hour_data,
            "daily_data": day_data,
            "consistency_score": self._calculate_consistency(days)
        }

    def _format_hour(self, hour: int) -> str:
        """
        Format hour to readable label.

        Args:
            hour: Hour (0-23)

        Returns:
            Formatted hour string (e.g., "9 AM", "2 PM")
        """
        if hour == 0:
            return "12 AM"
        elif hour < 12:
            return f"{hour} AM"
        elif hour == 12:
            return "12 PM"
        else:
            return f"{hour - 12} PM"

    def _get_hourly_completions(self, days: int = 30) -> Dict[int, float]:
        """
        Get completion rates by hour.

        Note: Since we don't track exact time, we'll simulate based on patterns
        """
        # In production, this would use actual timestamp data
        # For now, return uniform distribution
        return {hour: 0.5 for hour in range(24)}

    def _get_day_completions(self, days: int = 30) -> Dict[str, float]:
        """
        Get completion rates by day of week.

        Args:
            days: Number of days to analyze

        Returns:
            Dict mapping day name to completion rate
        """
        today = date.today()
        day_totals = {i: 0 for i in range(7)}
        day_counts = {i: 0 for i in range(7)}

        for i in range(days):
            check_date = today - timedelta(days=i)
            day_of_week = check_date.weekday()
            day_counts[day_of_week] += 1

            entry = self.storage.get_habit_entry(self.habit_id, check_date)
            if entry and hasattr(entry, 'value') and entry.value > 0:
                day_totals[day_of_week] += 1

        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        rates = {}

        for i in range(7):
            rates[day_names[i]] = (
                day_totals[i] / day_counts[i] if day_counts[i] > 0 else 0.0
            )

        return rates

    def _calculate_consistency(self, days: int = 30) -> float:
        """
        Calculate consistency score.

        Args:
            days: Number of days

        Returns:
            Consistency score (0-1)
        """
        today = date.today()
        completed = 0

        for i in range(days):
            check_date = today - timedelta(days=i)
            entry = self.storage.get_habit_entry(self.habit_id, check_date)
            if entry and hasattr(entry, 'value') and entry.value > 0:
                completed += 1

        return completed / days

    def get_best_times(self, habit_type: str = "general") -> List[Dict[str, Any]]:
        """
        Get recommended best times for habit type.

        Args:
            habit_type: Type of habit

        Returns:
            List of recommended times
        """
        # Research-based recommendations by habit type
        recommendations = {
            "exercise": {
                "best": "Morning (6-9 AM)",
                "reason": "Higher consistency, boosts metabolism for day"
            },
            "meditation": {
                "best": "Morning or Evening",
                "reason": "Sets tone for day or helps unwind"
            },
            "reading": {
                "best": "Evening (8-10 PM)",
                "reason": "Relaxing before bed, better retention"
            },
            "learning": {
                "best": "Morning (9-11 AM)",
                "reason": "Peak cognitive performance"
            },
            "writing": {
                "best": "Morning (6-8 AM)",
                "reason": "Fewer distractions, fresh mind"
            }
        }

        rec = recommendations.get(habit_type, {
            "best": "Consistent time daily",
            "reason": "Consistency matters more than specific time"
        })

        analysis = self.analyze_optimal_time()

        return [
            {
                "recommendation": f"Best day: {analysis['best_day']}",
                "type": "data-driven"
            },
            {
                "recommendation": rec["best"],
                "reason": rec["reason"],
                "type": "research-based"
            }
        ]

    def suggest_schedule_change(self) -> Optional[Dict[str, Any]]:
        """
        Suggest schedule optimization.

        Returns:
            Suggestion dict or None
        """
        analysis = self.analyze_optimal_time()
        
        if analysis["consistency_score"] < 0.5:
            return {
                "type": "schedule_change",
                "title": "Consider Changing Time",
                "description": f"Your consistency is {analysis['consistency_score']:.0%}. Try {analysis['best_day']}s.",
                "action": f"Switch to {analysis['best_day']} for better consistency"
            }
        
        return None


__all__ = [
    "TimingOptimizer",
]
