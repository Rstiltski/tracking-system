"""
Burnout Detection Engine - Early warning system for habit abandonment.

This engine analyzes habit patterns to detect burnout risk before users quit.
It uses multiple risk factors to calculate a comprehensive risk score.

Risk Factors:
1. Score Trend: 5+ consecutive days of declining scores
2. Completion Rate Drop: >20% week-over-week decrease
3. Multiple Habits Declining: Several habits showing negative trends
4. Streak Freeze Frequency: Excessive use of streak freezes
5. No Difficulty Adjustment: Habit never adjusted despite struggles

Usage:
    from brain.behavioral.burnout_detection import BurnoutDetector
    
    detector = BurnoutDetector(storage, habit_id)
    risk = detector.calculate_risk()
    
    if risk.risk_level != BurnoutRiskLevel.LOW:
        intervention = risk.get_intervention_suggestion()
        # Show intervention to user
"""
from datetime import date, timedelta
from typing import List, Dict, Any, Optional, Tuple
import logging

from brain.models.burnout import (
    BurnoutRisk,
    BurnoutRiskLevel,
    ContributingFactor,
    BurnoutSnapshot
)
from brain.models.habit import HabitScore

logger = logging.getLogger(__name__)


class BurnoutDetector:
    """
    Detects burnout risk for habits.

    Analyzes multiple factors to calculate a comprehensive
    burnout risk score and suggests interventions.

    Usage:
        detector = BurnoutDetector(storage, habit_id)
        risk = detector.calculate_risk()
    """

    # Risk factor weights (importance in final score)
    SCORE_TREND_WEIGHT = 0.30  # 30% of total risk
    COMPLETION_DROP_WEIGHT = 0.25  # 25% of total risk
    MULTIPLE_HABITS_WEIGHT = 0.15  # 15% of total risk
    STREAK_FREEZE_WEIGHT = 0.15  # 15% of total risk
    DIFFICULTY_WEIGHT = 0.15  # 15% of total risk

    # Thresholds
    DECLINING_DAYS_THRESHOLD = 5  # 5+ consecutive declining days
    COMPLETION_DROP_THRESHOLD = 0.20  # 20% drop in completion rate
    STREAK_FREEZE_THRESHOLD = 3  # 3+ freezes in 30 days
    LOOKBACK_DAYS = 30  # Analyze last 30 days

    def __init__(self, storage: Any, habit_id: str, user_id: str = ""):
        """
        Initialize burnout detector.

        Args:
            storage: Storage instance for data access
            habit_id: ID of the habit to analyze
            user_id: ID of the user (optional)
        """
        self.storage = storage
        self.habit_id = habit_id
        self.user_id = user_id

    def calculate_risk(self) -> BurnoutRisk:
        """
        Calculate burnout risk for the habit.

        Analyzes all risk factors and returns a comprehensive
        risk assessment.

        Returns:
            BurnoutRisk with score, level, and contributing factors
        """
        risk = BurnoutRisk(
            habit_id=self.habit_id,
            user_id=self.user_id,
            assessment_date=date.today()
        )

        # Get previous risk score for trend calculation
        previous_risk = self.storage.get_burnout_risk(self.habit_id)
        if previous_risk:
            risk.previous_score = previous_risk.risk_score

        # Calculate each risk factor
        self._analyze_score_trend(risk)
        self._analyze_completion_rate_drop(risk)
        self._analyze_multiple_habits_declining(risk)
        self._analyze_streak_freeze_usage(risk)
        self._analyze_difficulty_adjustment(risk)

        # Recalculate final score (done in add_factor)
        risk._recalculate_score()

        # Determine if intervention is suggested
        if risk.risk_level in [BurnoutRiskLevel.MODERATE, BurnoutRiskLevel.HIGH, BurnoutRiskLevel.CRITICAL]:
            risk.intervention_suggested = True
            intervention = risk.get_intervention_suggestion()
            risk.intervention_type = intervention["action"]

        return risk

    def _analyze_score_trend(self, risk: BurnoutRisk) -> None:
        """
        Analyze score trend for declining pattern.

        Risk factor: 5+ consecutive days of declining scores.

        Args:
            risk: BurnoutRisk object to update
        """
        today = date.today()
        consecutive_declining = 0
        previous_score = None

        for i in range(self.LOOKBACK_DAYS):
            check_date = today - timedelta(days=i)
            score = self._get_habit_score_for_date(check_date)

            if score is None:
                continue

            if previous_score is not None and score < previous_score:
                consecutive_declining += 1
            else:
                consecutive_declining = 0

            previous_score = score

            # Early exit if threshold reached
            if consecutive_declining >= self.DECLINING_DAYS_THRESHOLD:
                break

        # Add factor if threshold exceeded
        if consecutive_declining >= self.DECLINING_DAYS_THRESHOLD:
            # Weight increases with more declining days
            weight = min(1.0, consecutive_declining / 10.0)
            risk.add_factor(ContributingFactor.DECLINING_SCORE_TREND, weight)
            logger.info(
                f"Habit {self.habit_id}: Score declining for {consecutive_declining} days "
                f"(weight: {weight:.2f})"
            )

    def _analyze_completion_rate_drop(self, risk: BurnoutRisk) -> None:
        """
        Analyze completion rate for significant drops.

        Risk factor: >20% week-over-week decrease in completion rate.

        Args:
            risk: BurnoutRisk object to update
        """
        today = date.today()

        # Calculate this week's completion rate
        this_week_completed = 0
        for i in range(7):
            check_date = today - timedelta(days=i)
            entry = self.storage.get_habit_entry(self.habit_id, check_date)
            if entry and hasattr(entry, 'value') and entry.value > 0:
                this_week_completed += 1

        this_week_rate = this_week_completed / 7.0

        # Calculate last week's completion rate
        last_week_completed = 0
        for i in range(7, 14):
            check_date = today - timedelta(days=i)
            entry = self.storage.get_habit_entry(self.habit_id, check_date)
            if entry and hasattr(entry, 'value') and entry.value > 0:
                last_week_completed += 1

        last_week_rate = last_week_completed / 7.0

        # Check for significant drop
        if last_week_rate > 0:
            drop_percentage = (last_week_rate - this_week_rate) / last_week_rate
            if drop_percentage > self.COMPLETION_DROP_THRESHOLD:
                # Weight increases with larger drop
                weight = min(1.0, drop_percentage)
                risk.add_factor(ContributingFactor.COMPLETION_RATE_DROP, weight)
                logger.info(
                    f"Habit {self.habit_id}: Completion rate dropped {drop_percentage:.1%} "
                    f"(weight: {weight:.2f})"
                )

    def _analyze_multiple_habits_declining(self, risk: BurnoutRisk) -> None:
        """
        Analyze if multiple habits are declining simultaneously.

        Risk factor: Multiple habits showing negative trends.

        Args:
            risk: BurnoutRisk object to update
        """
        # Get all habits for this user
        all_habits = self.storage.get_habits(include_archived=False)
        declining_count = 0

        for habit in all_habits:
            if habit.id == self.habit_id:
                continue

            # Check if this habit is declining
            today = date.today()
            declining_days = 0

            for i in range(5):
                check_date = today - timedelta(days=i)
                score = self._get_habit_score_for_date(check_date, habit.id)

                if score is not None:
                    prev_score = self._get_habit_score_for_date(
                        today - timedelta(days=i+1),
                        habit.id
                    )
                    if prev_score is not None and score < prev_score:
                        declining_days += 1

            if declining_days >= 3:
                declining_count += 1

        # If 3+ other habits are declining, add factor
        if declining_count >= 3:
            weight = min(1.0, declining_count / 5.0)
            risk.add_factor(ContributingFactor.MULTIPLE_HABITS_DECLINING, weight)
            logger.info(
                f"Habit {self.habit_id}: {declining_count} other habits declining "
                f"(weight: {weight:.2f})"
            )

    def _analyze_streak_freeze_usage(self, risk: BurnoutRisk) -> None:
        """
        Analyze streak freeze usage frequency.

        Risk factor: Excessive use of streak freezes (3+ in 30 days).

        Args:
            risk: BurnoutRisk object to update
        """
        today = date.today()
        freeze_count = 0

        # Count streak freezes in last 30 days
        # This assumes storage tracks freeze usage
        for i in range(self.LOOKBACK_DAYS):
            check_date = today - timedelta(days=i)
            # Check if freeze was used on this date
            # This is a placeholder - actual implementation depends on storage
            if hasattr(self.storage, 'get_streak_freeze_usage'):
                if self.storage.get_streak_freeze_usage(self.habit_id, check_date):
                    freeze_count += 1

        if freeze_count >= self.STREAK_FREEZE_THRESHOLD:
            weight = min(1.0, freeze_count / 5.0)
            risk.add_factor(ContributingFactor.FREQUENT_STREAK_FREEZES, weight)
            logger.info(
                f"Habit {self.habit_id}: {freeze_count} streak freezes in 30 days "
                f"(weight: {weight:.2f})"
            )

    def _analyze_difficulty_adjustment(self, risk: BurnoutRisk) -> None:
        """
        Analyze if habit has been adjusted for difficulty.

        Risk factor: No difficulty adjustment despite struggles.

        Args:
            risk: BurnoutRisk object to update
        """
        # Check if habit has difficulty rating
        if hasattr(self.storage, 'get_difficulty_rating'):
            difficulty = self.storage.get_difficulty_rating(self.habit_id)

            # If rated "Too Hard" but no adjustment made
            if difficulty and difficulty.get("rating") == "too_hard":
                if not difficulty.get("adjustment_made", False):
                    risk.add_factor(ContributingFactor.NO_DIFFICULTY_ADJUSTMENT, 0.7)
                    logger.info(
                        f"Habit {self.habit_id}: Rated 'Too Hard' but no adjustment made"
                    )

    def _get_habit_score_for_date(
        self,
        check_date: date,
        habit_id: Optional[str] = None
    ) -> Optional[float]:
        """
        Get habit score for a specific date.

        Args:
            check_date: Date to get score for
            habit_id: Habit ID (uses self.habit_id if not provided)

        Returns:
            Score value (0.0-1.0) or None if not available
        """
        habit_id = habit_id or self.habit_id

        # Try to get score from storage
        if hasattr(self.storage, 'get_habit_score'):
            score = self.storage.get_habit_score(habit_id, check_date)
            if score:
                return score.value if hasattr(score, 'value') else score

        # Fallback: calculate score from entries
        # This is a simplified calculation
        entries = []
        for i in range(7):
            entry_date = check_date - timedelta(days=i)
            entry = self.storage.get_habit_entry(habit_id, entry_date)
            if entry and hasattr(entry, 'value'):
                entries.append(1 if entry.value > 0 else 0)

        if entries:
            return sum(entries) / len(entries)

        return None

    def get_all_at_risk_habits(self) -> List[Dict[str, Any]]:
        """
        Get all habits with moderate+ burnout risk.

        Returns:
            List of dicts with habit_id, risk_score, risk_level, and top factors
        """
        all_habits = self.storage.get_habits(include_archived=False)
        at_risk = []

        for habit in all_habits:
            detector = BurnoutDetector(self.storage, habit.id, self.user_id)
            risk = detector.calculate_risk()

            if risk.risk_level != BurnoutRiskLevel.LOW:
                at_risk.append({
                    "habit_id": habit.id,
                    "habit_name": habit.name,
                    "risk": risk.to_dict(),
                    "intervention": risk.get_intervention_suggestion()
                })

        # Sort by risk score (highest first)
        at_risk.sort(key=lambda x: x["risk"]["risk_score"], reverse=True)
        return at_risk

    def save_risk_assessment(self, risk: BurnoutRisk) -> None:
        """
        Save risk assessment to storage.

        Args:
            risk: BurnoutRisk assessment to save
        """
        self.storage.save_burnout_risk(self.habit_id, risk.to_dict())
        logger.info(f"Saved burnout risk for habit {self.habit_id}: {risk.risk_score:.1f}%")


def check_all_habits_for_burnout(storage: Any, user_id: str = "") -> List[BurnoutRisk]:
    """
    Check all habits for burnout risk.

    Convenience function to analyze all habits and return
    those with elevated risk.

    Args:
        storage: Storage instance for data access
        user_id: User ID (optional)

    Returns:
        List of BurnoutRisk objects for at-risk habits
    """
    all_habits = storage.get_habits(include_archived=False)
    at_risk_habits = []

    for habit in all_habits:
        detector = BurnoutDetector(storage, habit.id, user_id)
        risk = detector.calculate_risk()

        if risk.risk_level != BurnoutRiskLevel.LOW:
            at_risk_habits.append(risk)
            detector.save_risk_assessment(risk)

    return at_risk_habits
