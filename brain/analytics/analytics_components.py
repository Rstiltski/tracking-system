"""
Analytics Components - Correlation and Trend Analysis.

Usage:
    from brain.analytics.correlations import CorrelationAnalyzer
    from brain.analytics.trends import TrendAnalyzer
"""
from datetime import date, timedelta
from typing import Dict, Any, List, Optional


class CorrelationAnalyzer:
    """
    Analyzes habit correlations and patterns.

    Usage:
        analyzer = CorrelationAnalyzer(storage, user_id)
    """

    def __init__(self, storage: Any, user_id: str = ""):
        self.storage = storage
        self.user_id = user_id

    def calculate_habit_correlations(self) -> List[Dict[str, Any]]:
        """
        Calculate correlations between habits.

        Returns:
            List of correlation data
        """
        habits = self.storage.get_habits(include_archived=False)
        correlations = []

        for i, habit1 in enumerate(habits):
            for habit2 in habits[i+1:]:
                corr = self._calculate_correlation(habit1.id, habit2.id)
                if abs(corr) > 0.3:  # Only show meaningful correlations
                    correlations.append({
                        "habit1": habit1.name,
                        "habit2": habit2.name,
                        "correlation": corr,
                        "strength": self._get_correlation_strength(corr)
                    })

        return correlations

    def _calculate_correlation(self, habit1_id: str, habit2_id: str, days: int = 30) -> float:
        """Calculate correlation between two habits."""
        today = date.today()
        
        both_done = 0
        either_done = 0

        for i in range(days):
            check_date = today - timedelta(days=i)
            
            entry1 = self.storage.get_habit_entry(habit1_id, check_date)
            entry2 = self.storage.get_habit_entry(habit2_id, check_date)
            
            done1 = entry1 and hasattr(entry1, 'value') and entry1.value > 0
            done2 = entry2 and hasattr(entry2, 'value') and entry2.value > 0
            
            if done1 and done2:
                both_done += 1
            if done1 or done2:
                either_done += 1

        if either_done == 0:
            return 0.0

        return both_done / either_done

    def _get_correlation_strength(self, corr: float) -> str:
        """Get correlation strength label."""
        abs_corr = abs(corr)
        if abs_corr >= 0.7:
            return "strong"
        elif abs_corr >= 0.5:
            return "moderate"
        elif abs_corr >= 0.3:
            return "weak"
        return "none"

    def get_day_of_week_patterns(self, habit_id: Optional[str] = None) -> Dict[str, float]:
        """
        Get completion rates by day of week.

        Returns:
            Dict mapping day name to completion rate
        """
        habits = []
        if habit_id:
            habit = self.storage.get_habit(habit_id)
            if habit:
                habits = [habit]
        else:
            habits = self.storage.get_habits(include_archived=False)

        day_totals = {i: 0 for i in range(7)}
        day_counts = {i: 0 for i in range(7)}

        today = date.today()
        for i in range(30):
            check_date = today - timedelta(days=i)
            day_of_week = check_date.weekday()
            day_counts[day_of_week] += 1

            for habit in habits:
                entry = self.storage.get_habit_entry(habit.id, check_date)
                if entry and hasattr(entry, 'value') and entry.value > 0:
                    day_totals[day_of_week] += 1

        day_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
        patterns = {}

        for i in range(7):
            patterns[day_names[i]] = day_totals[i] / day_counts[i] if day_counts[i] > 0 else 0.0

        return patterns


class TrendAnalyzer:
    """
    Analyzes habit trends and forecasts.

    Usage:
        analyzer = TrendAnalyzer(storage, habit_id)
    """

    def __init__(self, storage: Any, habit_id: str):
        self.storage = storage
        self.habit_id = habit_id

    def calculate_trends(self, days: int = 30) -> Dict[str, Any]:
        """
        Calculate trend data.

        Args:
            days: Number of days to analyze

        Returns:
            Trend data dict
        """
        today = date.today()
        
        # Split into two halves
        first_half = 0
        first_count = 0
        second_half = 0
        second_count = 0

        for i in range(days):
            check_date = today - timedelta(days=i)
            entry = self.storage.get_habit_entry(self.habit_id, check_date)
            completed = 1 if (entry and hasattr(entry, 'value') and entry.value > 0) else 0

            if i < days // 2:
                second_half += completed
                second_count += 1
            else:
                first_half += completed
                first_count += 1

        first_rate = first_half / first_count if first_count > 0 else 0
        second_rate = second_half / second_count if second_count > 0 else 0

        trend = "improving" if second_rate > first_rate else "declining" if second_rate < first_rate else "stable"

        return {
            "trend": trend,
            "first_half_rate": first_rate,
            "second_half_rate": second_rate,
            "change": second_rate - first_rate
        }

    def forecast_score(self, days_ahead: int = 7) -> Dict[str, Any]:
        """
        Forecast future performance.

        Args:
            days_ahead: Days to forecast

        Returns:
            Forecast dict
        """
        trend_data = self.calculate_trends()
        current_rate = trend_data["second_half_rate"]

        # Simple linear projection
        projected_rate = max(0, min(1, current_rate + (trend_data["change"] * days_ahead / 7)))

        return {
            "current_rate": current_rate,
            "projected_rate": projected_rate,
            "confidence": "low" if abs(trend_data["change"]) < 0.1 else "medium" if abs(trend_data["change"]) < 0.2 else "high"
        }


__all__ = [
    "CorrelationAnalyzer",
    "TrendAnalyzer",
]
