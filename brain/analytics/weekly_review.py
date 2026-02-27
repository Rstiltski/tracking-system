"""
Weekly Review Analytics Engine

Generates comprehensive weekly reviews for habit tracking including:
- Completion metrics
- Streak analysis
- Score improvements
- Insight generation

Usage:
    from brain.analytics.weekly_review import WeeklyReviewGenerator
    
    generator = WeeklyReviewGenerator(storage, user_id)
    review = generator.generate_review(week_number, year)
"""
from datetime import date, timedelta, datetime
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass, field
import logging

logger = logging.getLogger(__name__)


@dataclass
class WeeklyReview:
    """
    A weekly review summary.

    Attributes:
        week_number: ISO week number
        year: Year
        user_id: User ID
        total_habits: Total active habits
        total_completions: Total habit completions
        completion_rate: Overall completion rate
        best_habit: Habit with best improvement
        needs_attention: Habits needing attention
        streak_milestones: Streaks achieved this week
        xp_earned: XP earned this week
        insights: Generated insights
        generated_at: When review was generated
    """
    week_number: int = 0
    year: int = 0
    user_id: str = ""
    total_habits: int = 0
    total_completions: int = 0
    completion_rate: float = 0.0
    best_habit: Optional[Dict[str, Any]] = None
    needs_attention: List[Dict[str, Any]] = field(default_factory=list)
    streak_milestones: List[Dict[str, Any]] = field(default_factory=list)
    xp_earned: int = 0
    insights: List[str] = field(default_factory=list)
    generated_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "week_number": self.week_number,
            "year": self.year,
            "user_id": self.user_id,
            "total_habits": self.total_habits,
            "total_completions": self.total_completions,
            "completion_rate": self.completion_rate,
            "best_habit": self.best_habit,
            "needs_attention": self.needs_attention,
            "streak_milestones": self.streak_milestones,
            "xp_earned": self.xp_earned,
            "insights": self.insights,
            "generated_at": self.generated_at.isoformat()
        }


class WeeklyReviewGenerator:
    """
    Generates weekly review summaries.

    Analyzes habit data to create comprehensive weekly reviews
    with metrics, milestones, and actionable insights.

    Usage:
        generator = WeeklyReviewGenerator(storage, user_id)
        review = generator.generate_review(week_number=47, year=2026)
    """

    # Milestone thresholds
    STREAK_MILESTONES = [7, 14, 21, 30, 60, 90, 180, 365]
    COMPLETION_EXCELLENCE = 0.90  # 90%+ completion rate
    COMPLETION_STRUGGLING = 0.50  # < 50% completion rate

    def __init__(self, storage: Any, user_id: str = ""):
        """
        Initialize review generator.

        Args:
            storage: Storage instance
            user_id: User ID
        """
        self.storage = storage
        self.user_id = user_id

    def generate_review(
        self,
        week_number: Optional[int] = None,
        year: Optional[int] = None
    ) -> WeeklyReview:
        """
        Generate a weekly review.

        Args:
            week_number: ISO week number (default: current week)
            year: Year (default: current year)

        Returns:
            WeeklyReview with metrics and insights
        """
        # Use current week if not specified
        if week_number is None or year is None:
            today = date.today()
            iso_calendar = today.isocalendar()
            week_number = iso_calendar.week
            year = iso_calendar.year

        # Get week date range
        week_start, week_end = self._get_week_dates(week_number, year)

        # Get all habits
        habits = self.storage.get_habits(include_archived=False)

        # Initialize review
        review = WeeklyReview(
            week_number=week_number,
            year=year,
            user_id=self.user_id
        )

        if not habits:
            review.insights.append("🌱 Start your first habit to begin tracking!")
            return review

        # Calculate metrics
        review.total_habits = len(habits)
        
        # Analyze each habit
        habit_metrics = []
        for habit in habits:
            metrics = self._analyze_habit_for_week(habit, week_start, week_end)
            habit_metrics.append(metrics)

        # Aggregate metrics
        review.total_completions = sum(m['completions'] for m in habit_metrics)
        review.completion_rate = self._calculate_overall_completion_rate(habit_metrics)
        review.xp_earned = review.total_completions * 10  # 10 XP per completion

        # Find best and worst performers
        review.best_habit = self._find_best_performer(habit_metrics)
        review.needs_attention = self._find_needs_attention(habit_metrics)

        # Find streak milestones
        review.streak_milestones = self._find_streak_milestones(habits, week_start, week_end)

        # Generate insights
        review.insights = self._generate_insights(review, habit_metrics)

        review.generated_at = datetime.now()

        logger.info(
            f"Generated weekly review for week {week_number}/{year}: "
            f"{review.completion_rate:.0f}% completion rate"
        )

        return review

    def _get_week_dates(
        self,
        week_number: int,
        year: int
    ) -> Tuple[date, date]:
        """
        Get start and end dates for an ISO week.

        Args:
            week_number: ISO week number
            year: Year

        Returns:
            Tuple of (week_start, week_end) dates
        """
        # Find the Monday of the given week
        jan_4 = date(year, 1, 4)  # January 4th is always in week 1
        week_1_monday = jan_4 - timedelta(days=jan_4.weekday())
        week_start = week_1_monday + timedelta(weeks=week_number - 1)
        week_end = week_start + timedelta(days=6)

        return week_start, week_end

    def _analyze_habit_for_week(
        self,
        habit: Any,
        week_start: date,
        week_end: date
    ) -> Dict[str, Any]:
        """
        Analyze a single habit for the week.

        Args:
            habit: Habit object
            week_start: Week start date
            week_end: Week end date

        Returns:
            Dict with habit metrics
        """
        completions = 0
        days_in_week = 7

        # Count completions
        current_date = week_start
        while current_date <= week_end:
            entry = self.storage.get_habit_entry(habit.id, current_date)
            if entry and hasattr(entry, 'value') and entry.value > 0:
                completions += 1
            current_date += timedelta(days=1)

        # Get current streak
        streak = self._calculate_streak(habit.id)

        # Get score
        score = self._get_habit_score(habit.id)

        # Calculate completion rate
        completion_rate = completions / days_in_week if days_in_week > 0 else 0

        return {
            'habit_id': habit.id,
            'habit_name': habit.name,
            'habit_icon': habit.icon if hasattr(habit, 'icon') else '🎯',
            'completions': completions,
            'completion_rate': completion_rate,
            'streak': streak,
            'score': score,
            'perfect_week': completions == days_in_week
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

    def _get_habit_score(self, habit_id: str) -> float:
        """Get current habit score."""
        if hasattr(self.storage, 'get_habit_score'):
            score = self.storage.get_habit_score(habit_id)
            return score.value if score else 0.0
        return 0.0

    def _calculate_overall_completion_rate(
        self,
        habit_metrics: List[Dict[str, Any]]
    ) -> float:
        """
        Calculate overall completion rate.

        Args:
            habit_metrics: List of habit metrics

        Returns:
            Overall completion rate (0.0-1.0)
        """
        if not habit_metrics:
            return 0.0

        total_possible = len(habit_metrics) * 7  # 7 days per week
        total_completed = sum(m['completions'] for m in habit_metrics)

        return total_completed / total_possible if total_possible > 0 else 0.0

    def _find_best_performer(
        self,
        habit_metrics: List[Dict[str, Any]]
    ) -> Optional[Dict[str, Any]]:
        """
        Find the best performing habit.

        Args:
            habit_metrics: List of habit metrics

        Returns:
            Dict with best habit info or None
        """
        if not habit_metrics:
            return None

        # Sort by completion rate
        sorted_habits = sorted(
            habit_metrics,
            key=lambda x: x['completion_rate'],
            reverse=True
        )

        best = sorted_habits[0]
        return {
            'habit_id': best['habit_id'],
            'name': best['habit_name'],
            'icon': best['habit_icon'],
            'completion_rate': best['completion_rate'],
            'completions': best['completions']
        }

    def _find_needs_attention(
        self,
        habit_metrics: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """
        Find habits needing attention.

        Args:
            habit_metrics: List of habit metrics

        Returns:
            List of habits needing attention
        """
        attention = []

        for metrics in habit_metrics:
            if metrics['completion_rate'] < self.COMPLETION_STRUGGLING:
                attention.append({
                    'habit_id': metrics['habit_id'],
                    'name': metrics['habit_name'],
                    'icon': metrics['habit_icon'],
                    'completion_rate': metrics['completion_rate'],
                    'reason': 'Low completion rate'
                })

        return attention

    def _find_streak_milestones(
        self,
        habits: List[Any],
        week_start: date,
        week_end: date
    ) -> List[Dict[str, Any]]:
        """
        Find streak milestones achieved this week.

        Args:
            habits: List of habits
            week_start: Week start date
            week_end: Week end date

        Returns:
            List of milestone achievements
        """
        milestones = []

        for habit in habits:
            streak = self._calculate_streak(habit.id)

            # Check if any milestone was reached this week
            for milestone in self.STREAK_MILESTONES:
                if streak >= milestone:
                    # Check if milestone was reached this week
                    milestone_date = week_end - timedelta(days=streak - milestone)
                    if week_start <= milestone_date <= week_end:
                        milestones.append({
                            'habit_id': habit.id,
                            'habit_name': habit.name,
                            'milestone': milestone,
                            'reached_date': milestone_date.isoformat()
                        })

        return milestones

    def _generate_insights(
        self,
        review: WeeklyReview,
        habit_metrics: List[Dict[str, Any]]
    ) -> List[str]:
        """
        Generate insights from review data.

        Args:
            review: WeeklyReview object
            habit_metrics: List of habit metrics

        Returns:
            List of insight strings
        """
        insights = []

        # Overall performance insights
        if review.completion_rate >= self.COMPLETION_EXCELLENCE:
            insights.append(
                f"🌟 Outstanding! {review.completion_rate:.0f}% completion rate this week!"
            )
        elif review.completion_rate >= 0.70:
            insights.append(
                f"👍 Great work! {review.completion_rate:.0f}% completion rate."
            )
        elif review.completion_rate >= 0.50:
            insights.append(
                f"💪 Keep going! {review.completion_rate:.0f}% completion rate. "
                "You're building momentum!"
            )
        else:
            insights.append(
                f"🌱 Every habit starts small. "
                f"Focus on consistency, not perfection."
            )

        # Perfect week insights
        perfect_weeks = [m for m in habit_metrics if m.get('perfect_week')]
        if perfect_weeks:
            if len(perfect_weeks) == 1:
                habit = perfect_weeks[0]
                insights.append(
                    f"🎯 Perfect week for {habit['habit_name']}! "
                    f"All 7 days completed!"
                )
            else:
                insights.append(
                    f"🏆 {len(perfect_weeks)} habits with perfect weeks!"
                )

        # Streak insights
        if review.streak_milestones:
            for milestone in review.streak_milestones[:2]:  # Show top 2
                insights.append(
                    f"🔥 {milestone['habit_name']} reached "
                    f"{milestone['milestone']}-day streak!"
                )

        # Needs attention insights
        if review.needs_attention:
            if len(review.needs_attention) == 1:
                habit = review.needs_attention[0]
                insights.append(
                    f"💡 Consider adjusting {habit['name']} - "
                    "smaller steps lead to bigger wins!"
                )
            else:
                insights.append(
                    f"📝 {len(review.needs_attention)} habits could use "
                    "a difficulty adjustment. Review your plans!"
                )

        # XP insights
        if review.xp_earned >= 100:
            insights.append(f"⭐ You earned {review.xp_earned} XP this week!")

        # Consistency insight
        consistent_habits = [
            m for m in habit_metrics
            if m['completion_rate'] >= self.COMPLETION_EXCELLENCE
        ]
        if len(consistent_habits) >= 3:
            insights.append(
                f"🎯 You have {len(consistent_habits)} highly consistent habits. "
                "That's the secret to lasting change!"
            )

        return insights

    def get_weekly_review_history(
        self,
        limit: int = 10
    ) -> List[WeeklyReview]:
        """
        Get historical weekly reviews.

        Args:
            limit: Maximum number of reviews to return

        Returns:
            List of WeeklyReview objects
        """
        # This would query stored reviews from database
        # For now, generate on-the-fly for recent weeks
        reviews = []
        today = date.today()
        iso_calendar = today.isocalendar()
        current_week = iso_calendar.week
        current_year = iso_calendar.year

        for i in range(limit):
            # Calculate week number going backwards
            week_offset = current_week - i
            year_offset = current_year
            
            # Handle year boundary
            while week_offset < 1:
                year_offset -= 1
                # Get last week of previous year
                dec_31 = date(year_offset, 12, 31)
                week_offset = dec_31.isocalendar().week

            review = self.generate_review(week_offset, year_offset)
            reviews.append(review)

        return reviews


__all__ = [
    "WeeklyReview",
    "WeeklyReviewGenerator",
]
