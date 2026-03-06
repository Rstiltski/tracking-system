"""
Calendar and Time Views Data Processing

Phase 7.4: Provides data processing for calendar views, weekly summaries,
and heatmap visualizations.

Features:
- Monthly calendar grid data
- Weekly summary statistics
- Daily detail aggregation
- Heatmap data generation
- Streak visualization data
"""

from datetime import date, datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, field
from collections import defaultdict
import calendar
import logging

logger = logging.getLogger(__name__)


class TimeViewsProcessor:
    """
    Processes tracking data into calendar-friendly formats.
    
    Handles weekly summaries, monthly views, heatmaps, and date navigation.
    """
    
    def __init__(self, tracking_data: dict = None, storage: Optional[Any] = None):
        """
        Args:
            tracking_data: Dictionary with dates as keys, habit records as values.
                Example: {"2026-03-01": {"habits": {...}, "tasks": [...]}, ...}
            storage: Optional storage backend for fetching habit data
        """
        self.raw_data = tracking_data or {}
        self.storage = storage
        self.parsed_data = self._parse_dates()

    def _parse_dates(self) -> dict:
        """Convert string date keys to date objects."""
        parsed = {}
        for date_str, record in self.raw_data.items():
            try:
                if isinstance(date_str, str):
                    d = datetime.strptime(date_str, "%Y-%m-%d").date()
                else:
                    d = date_str
                parsed[d] = record
            except (ValueError, TypeError):
                continue
        return parsed

    # ──────────────────────────────────────────────
    # Day Detail
    # ──────────────────────────────────────────────

    def get_day_detail(self, target_date: date) -> dict:
        """
        Get full detail for a single day.
        
        Returns:
            {
                "date": date,
                "date_str": "2026-03-01",
                "day_name": "Sunday",
                "has_data": True,
                "habits": {...},
                "tasks": [...],
                "completion_rate": 0.67,
                "average_score": 5.0,
                "completed_count": 2,
                "total_count": 3,
            }
        """
        record = self.parsed_data.get(target_date, {})
        
        # If no data in parsed_data, try storage
        if not record and self.storage:
            record = self._fetch_from_storage(target_date)
        
        habits = record.get("habits", {})
        tasks = record.get("tasks", [])

        total_habits = len(habits)
        completed_habits = sum(
            1 for h in habits.values() if h.get("completed", False)
        )
        scores = [
            h.get("score", 0) for h in habits.values() if h.get("completed", False)
        ]

        total_tasks = len(tasks)
        completed_tasks = sum(1 for t in tasks if t.get("completed", False))

        total_items = total_habits + total_tasks
        completed_items = completed_habits + completed_tasks

        completion_rate = completed_items / total_items if total_items > 0 else 0.0
        average_score = sum(scores) / len(scores) if scores else 0.0

        return {
            "date": target_date,
            "date_str": target_date.strftime("%Y-%m-%d"),
            "day_name": target_date.strftime("%A"),
            "has_data": bool(record),
            "habits": habits,
            "tasks": tasks,
            "notes": record.get("notes", ""),
            "completion_rate": round(completion_rate, 2),
            "average_score": round(average_score, 1),
            "completed_habits": completed_habits,
            "total_habits": total_habits,
            "completed_tasks": completed_tasks,
            "total_tasks": total_tasks,
            "completed_count": completed_items,
            "total_count": total_items,
            "is_today": target_date == date.today(),
            "is_future": target_date > date.today(),
        }

    def _fetch_from_storage(self, target_date: date) -> dict:
        """Fetch data from storage backend."""
        if not self.storage:
            return {}
        
        try:
            # Try different storage methods
            if hasattr(self.storage, 'get_habit_entries'):
                entries = self.storage.get_habit_entries(target_date)
                if entries:
                    habits = {}
                    for e in entries:
                        habits[e.get('name', 'Unknown')] = {
                            'completed': e.get('completed', False),
                            'score': e.get('score', 0)
                        }
                    return {'habits': habits, 'tasks': []}
        except Exception as e:
            logger.warning("Error fetching from storage for %s: %s", target_date, e)
        
        return {}

    # ──────────────────────────────────────────────
    # Weekly Summary
    # ──────────────────────────────────────────────

    def get_week_start(self, target_date: date, start_monday: bool = True) -> date:
        """Get the start of the week containing target_date."""
        if start_monday:
            days_back = target_date.weekday()  # Monday = 0
        else:
            days_back = (target_date.weekday() + 1) % 7  # Sunday = 0
        return target_date - timedelta(days=days_back)

    def get_weekly_summary(
        self, target_date: date = None, start_monday: bool = True
    ) -> dict:
        """
        Get a 7-day summary for the week containing target_date.
        """
        target_date = target_date or date.today()
        week_start = self.get_week_start(target_date, start_monday)
        week_end = week_start + timedelta(days=6)

        days = []
        for i in range(7):
            day = week_start + timedelta(days=i)
            days.append(self.get_day_detail(day))

        # Habit breakdown across the week
        all_habit_names = set()
        for day in days:
            all_habit_names.update(day["habits"].keys())

        habit_breakdown = {}
        for habit_name in sorted(all_habit_names):
            completed_days = 0
            total_days = 0
            scores = []
            for day in days:
                if habit_name in day["habits"]:
                    total_days += 1
                    habit_info = day["habits"][habit_name]
                    if habit_info.get("completed", False):
                        completed_days += 1
                        scores.append(habit_info.get("score", 0))

            rate = completed_days / total_days if total_days > 0 else 0.0
            avg_score = sum(scores) / len(scores) if scores else 0.0

            habit_breakdown[habit_name] = {
                "completed_days": completed_days,
                "total_days": total_days,
                "rate": round(rate, 2),
                "avg_score": round(avg_score, 1),
            }

        # Best and worst habits
        best_habit = None
        worst_habit = None
        if habit_breakdown:
            sorted_habits = sorted(
                habit_breakdown.items(), key=lambda x: x[1]["rate"], reverse=True
            )
            best_habit = sorted_habits[0][0] if sorted_habits else None
            worst_habit = sorted_habits[-1][0] if sorted_habits else None

        # Overall stats
        days_with_data = [d for d in days if d["has_data"]]
        overall_completion = (
            sum(d["completion_rate"] for d in days_with_data) / len(days_with_data)
            if days_with_data
            else 0.0
        )
        overall_score = (
            sum(d["average_score"] for d in days_with_data) / len(days_with_data)
            if days_with_data
            else 0.0
        )

        # Week-over-week comparison
        prev_week_start = week_start - timedelta(days=7)
        comparison = self._compare_weeks(prev_week_start, week_start, start_monday)

        return {
            "week_start": week_start,
            "week_end": week_end,
            "week_label": self._format_week_label(week_start, week_end),
            "days": days,
            "days_with_data": len(days_with_data),
            "overall_completion_rate": round(overall_completion, 2),
            "overall_average_score": round(overall_score, 1),
            "best_habit": best_habit,
            "worst_habit": worst_habit,
            "habit_breakdown": habit_breakdown,
            "comparison": comparison,
        }

    def _format_week_label(self, start: date, end: date) -> str:
        """Format a human-readable week label."""
        if start.month == end.month:
            return f"{start.strftime('%b %d')} - {end.strftime('%d, %Y')}"
        if start.year == end.year:
            return f"{start.strftime('%b %d')} - {end.strftime('%b %d, %Y')}"
        return f"{start.strftime('%b %d, %Y')} - {end.strftime('%b %d, %Y')}"

    def _compare_weeks(
        self, prev_start: date, curr_start: date, start_monday: bool
    ) -> dict:
        """Compare two consecutive weeks."""
        prev_days = []
        curr_days = []
        for i in range(7):
            prev_days.append(self.get_day_detail(prev_start + timedelta(days=i)))
            curr_days.append(self.get_day_detail(curr_start + timedelta(days=i)))

        def week_avg_completion(days_list):
            with_data = [d for d in days_list if d["has_data"]]
            if not with_data:
                return 0.0
            return sum(d["completion_rate"] for d in with_data) / len(with_data)

        def week_avg_score(days_list):
            with_data = [d for d in days_list if d["has_data"]]
            if not with_data:
                return 0.0
            return sum(d["average_score"] for d in with_data) / len(with_data)

        prev_completion = week_avg_completion(prev_days)
        curr_completion = week_avg_completion(curr_days)
        prev_score = week_avg_score(prev_days)
        curr_score = week_avg_score(curr_days)

        completion_delta = curr_completion - prev_completion
        score_delta = curr_score - prev_score

        return {
            "prev_completion_rate": round(prev_completion, 2),
            "curr_completion_rate": round(curr_completion, 2),
            "completion_delta": round(completion_delta, 2),
            "completion_trend": "up" if completion_delta > 0.01 else ("down" if completion_delta < -0.01 else "flat"),
            "prev_average_score": round(prev_score, 1),
            "curr_average_score": round(curr_score, 1),
            "score_delta": round(score_delta, 1),
            "score_trend": "up" if score_delta > 0.1 else ("down" if score_delta < -0.1 else "flat"),
        }

    # ──────────────────────────────────────────────
    # Monthly View
    # ──────────────────────────────────────────────

    def get_monthly_view(self, year: int, month: int) -> dict:
        """
        Get monthly calendar grid with completion data.
        """
        num_days = calendar.monthrange(year, month)[1]
        first_weekday = date(year, month, 1).weekday()  # 0=Monday

        days = []
        for day_num in range(1, num_days + 1):
            d = date(year, month, day_num)
            days.append(self.get_day_detail(d))

        # Build calendar grid (weeks as rows, Mon-Sun as columns)
        grid = []
        current_row = [None] * first_weekday
        for day_detail in days:
            current_row.append(day_detail)
            if len(current_row) == 7:
                grid.append(current_row)
                current_row = []
        if current_row:
            while len(current_row) < 7:
                current_row.append(None)
            grid.append(current_row)

        # Stats
        days_with_data = [d for d in days if d["has_data"]]
        overall_completion = (
            sum(d["completion_rate"] for d in days_with_data) / len(days_with_data)
            if days_with_data
            else 0.0
        )
        overall_score = (
            sum(d["average_score"] for d in days_with_data) / len(days_with_data)
            if days_with_data
            else 0.0
        )

        # Habit breakdown for the month
        all_habit_names = set()
        for day in days:
            all_habit_names.update(day["habits"].keys())

        habit_breakdown = {}
        for habit_name in sorted(all_habit_names):
            completed_days = 0
            total_days = 0
            scores = []
            for day in days:
                if habit_name in day["habits"]:
                    total_days += 1
                    if day["habits"][habit_name].get("completed", False):
                        completed_days += 1
                        scores.append(day["habits"][habit_name].get("score", 0))

            rate = completed_days / total_days if total_days > 0 else 0.0
            avg_score = sum(scores) / len(scores) if scores else 0.0

            habit_breakdown[habit_name] = {
                "completed_days": completed_days,
                "total_days": total_days,
                "rate": round(rate, 2),
                "avg_score": round(avg_score, 1),
            }

        # Monthly trend
        trend = self._compute_monthly_trend(days)

        return {
            "year": year,
            "month": month,
            "month_name": calendar.month_name[month],
            "month_label": f"{calendar.month_name[month]} {year}",
            "num_days": num_days,
            "first_weekday": first_weekday,
            "calendar_grid": grid,
            "days": days,
            "total_days_tracked": len(days_with_data),
            "overall_completion_rate": round(overall_completion, 2),
            "overall_average_score": round(overall_score, 1),
            "habit_breakdown": habit_breakdown,
            "trend": trend,
        }

    def _compute_monthly_trend(self, days: list) -> dict:
        """Split month into quarters and track progression."""
        chunk_size = max(len(days) // 4, 1)
        quarters = []
        for i in range(0, len(days), chunk_size):
            chunk = days[i : i + chunk_size]
            with_data = [d for d in chunk if d["has_data"]]
            if with_data:
                avg = sum(d["completion_rate"] for d in with_data) / len(with_data)
                quarters.append(round(avg, 2))
            else:
                quarters.append(0.0)

        while len(quarters) < 4:
            quarters.append(0.0)
        quarters = quarters[:4]

        if quarters[0] > 0 and quarters[-1] > 0:
            if quarters[-1] > quarters[0] + 0.05:
                direction = "improving"
            elif quarters[-1] < quarters[0] - 0.05:
                direction = "declining"
            else:
                direction = "stable"
        else:
            direction = "insufficient_data"

        return {
            "quarter_rates": quarters,
            "direction": direction,
        }

    # ──────────────────────────────────────────────
    # Heatmap Data
    # ──────────────────────────────────────────────

    def get_heatmap_data(
        self,
        start_date: date = None,
        end_date: date = None,
        habit_name: Optional[str] = None,
        days: int = 90,
    ) -> list:
        """
        Generate heatmap data for a date range.
        
        Returns:
            [
                {
                    "date": date,
                    "date_str": "2026-03-01",
                    "value": 0.75,
                    "level": 3,  # 0-4 for color coding
                    "label": "3/4 completed",
                    "has_data": True,
                },
                ...
            ]
        """
        if end_date is None:
            end_date = date.today()
        if start_date is None:
            start_date = end_date - timedelta(days=days - 1)

        heatmap = []
        current = start_date
        while current <= end_date:
            day = self.get_day_detail(current)

            if habit_name:
                # Single habit mode
                if habit_name in day["habits"]:
                    completed = day["habits"][habit_name].get("completed", False)
                    score = day["habits"][habit_name].get("score", 0)
                    value = score / 10.0 if completed else 0.0
                    label = f"{habit_name}: {'✓' if completed else '✗'} (score: {score})"
                    has_data = True
                else:
                    value = 0.0
                    label = f"{habit_name}: no data"
                    has_data = False
            else:
                # Overall mode
                value = day["completion_rate"]
                label = f"{day['completed_count']}/{day['total_count']} completed"
                has_data = day["has_data"]

            # Map value (0.0-1.0) to level (0-4)
            if not has_data:
                level = -1  # no data
            elif value == 0:
                level = 0
            elif value < 0.25:
                level = 1
            elif value < 0.5:
                level = 2
            elif value < 0.75:
                level = 3
            else:
                level = 4

            heatmap.append(
                {
                    "date": current,
                    "date_str": current.strftime("%Y-%m-%d"),
                    "value": round(value, 2),
                    "level": level,
                    "label": label,
                    "has_data": has_data,
                    "total_habits": day["total_habits"],
                    "completed_habits": day["completed_habits"],
                    "completion_rate": day["completion_rate"],
                    "is_today": day["is_today"],
                    "is_future": day["is_future"],
                }
            )
            current += timedelta(days=1)

        return heatmap

    # ──────────────────────────────────────────────
    # Streaks
    # ──────────────────────────────────────────────

    def get_streaks(self, habit_name: Optional[str] = None) -> dict:
        """
        Calculate current and longest streaks.
        """
        sorted_dates = sorted(self.parsed_data.keys())
        if not sorted_dates:
            return {
                "current_streak": 0,
                "longest_streak": 0,
                "longest_streak_start": None,
                "longest_streak_end": None,
                "total_completed_days": 0,
                "total_tracked_days": 0,
            }

        def is_completed(d: date) -> bool:
            record = self.parsed_data.get(d, {})
            habits = record.get("habits", {})
            if habit_name:
                return habits.get(habit_name, {}).get("completed", False)
            else:
                if not habits:
                    return False
                return all(h.get("completed", False) for h in habits.values())

        first_date = sorted_dates[0]
        last_date = sorted_dates[-1]

        current_streak = 0
        longest_streak = 0
        longest_start = None
        longest_end = None
        streak_start = None
        running_streak = 0
        total_completed = 0
        total_tracked = 0

        current = first_date
        while current <= last_date:
            if current in self.parsed_data:
                total_tracked += 1
                if is_completed(current):
                    total_completed += 1
                    if running_streak == 0:
                        streak_start = current
                    running_streak += 1

                    if running_streak > longest_streak:
                        longest_streak = running_streak
                        longest_start = streak_start
                        longest_end = current
                else:
                    running_streak = 0
            else:
                running_streak = 0

            current += timedelta(days=1)

        # Current streak: count backwards from today
        today = date.today()
        check_date = min(today, last_date)
        current_streak = 0
        while check_date >= first_date:
            if check_date in self.parsed_data and is_completed(check_date):
                current_streak += 1
                check_date -= timedelta(days=1)
            else:
                break

        return {
            "current_streak": current_streak,
            "longest_streak": longest_streak,
            "longest_streak_start": longest_start,
            "longest_streak_end": longest_end,
            "total_completed_days": total_completed,
            "total_tracked_days": total_tracked,
        }

    # ──────────────────────────────────────────────
    # Navigation Helpers
    # ──────────────────────────────────────────────

    def get_prev_next_month(self, year: int, month: int) -> dict:
        """Get previous and next month references."""
        first_of_month = date(year, month, 1)
        prev_month_last = first_of_month - timedelta(days=1)
        if month == 12:
            next_year, next_month = year + 1, 1
        else:
            next_year, next_month = year, month + 1

        return {
            "prev_year": prev_month_last.year,
            "prev_month": prev_month_last.month,
            "prev_label": f"{calendar.month_name[prev_month_last.month]} {prev_month_last.year}",
            "next_year": next_year,
            "next_month": next_month,
            "next_label": f"{calendar.month_name[next_month]} {next_year}",
        }

    def get_prev_next_week(
        self, target_date: date, start_monday: bool = True
    ) -> dict:
        """Get previous and next week references."""
        week_start = self.get_week_start(target_date, start_monday)
        prev_week = week_start - timedelta(days=7)
        next_week = week_start + timedelta(days=7)

        return {
            "prev_week_start": prev_week,
            "prev_label": self._format_week_label(prev_week, prev_week + timedelta(days=6)),
            "next_week_start": next_week,
            "next_label": self._format_week_label(next_week, next_week + timedelta(days=6)),
        }

    # ──────────────────────────────────────────────
    # Export
    # ──────────────────────────────────────────────

    def export_monthly_text(self, year: int, month: int) -> str:
        """Generate a printable text calendar with completion data."""
        view = self.get_monthly_view(year, month)
        lines = []

        lines.append(f"{'=' * 60}")
        lines.append(f"{view['month_label']:^60}")
        lines.append(f"{'=' * 60}")
        lines.append("")

        # Header row
        day_names = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
        header = "  ".join(f"{d:>7}" for d in day_names)
        lines.append(header)
        lines.append("-" * 65)

        # Calendar rows
        for week_row in view["calendar_grid"]:
            day_cells = []
            status_cells = []
            for cell in week_row:
                if cell is None:
                    day_cells.append(f"{'':>7}")
                    status_cells.append(f"{'':>7}")
                else:
                    day_num = cell["date"].day
                    rate = cell["completion_rate"]
                    if not cell["has_data"]:
                        symbol = "  -  "
                    elif rate >= 0.75:
                        symbol = " ███ "
                    elif rate >= 0.5:
                        symbol = " ▓▓▓ "
                    elif rate >= 0.25:
                        symbol = " ░░░ "
                    elif rate > 0:
                        symbol = " ·── "
                    else:
                        symbol = " ___ "

                    day_cells.append(f"{day_num:>4}   ")
                    status_cells.append(f"{symbol}  ")

            lines.append("  ".join(day_cells))
            lines.append("  ".join(status_cells))
            lines.append("")

        # Legend
        lines.append("-" * 65)
        lines.append("Legend:  ███ ≥75%  ▓▓▓ ≥50%  ░░░ ≥25%  ·── >0%  ___ 0%  - no data")
        lines.append("")

        # Stats
        lines.append(f"Overall Completion: {view['overall_completion_rate']:.0%}")
        lines.append(f"Average Score: {view['overall_average_score']:.1f}/10")
        lines.append(f"Days Tracked: {view['total_days_tracked']}/{view['num_days']}")

        return "\n".join(lines)


# Legacy compatibility - keep old names
DayData = dict
WeekData = dict
MonthData = dict
CalendarProcessor = TimeViewsProcessor


__all__ = [
    "TimeViewsProcessor",
    "CalendarProcessor",  # Alias for backward compatibility
    "DayData",
    "WeekData", 
    "MonthData",
]