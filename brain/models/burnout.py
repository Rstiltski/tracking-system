"""
Burnout Risk Model - Early warning system for habit abandonment.

Based on behavioral science research on habit formation and dropout patterns:

1. Burnout Detection Factors:
   - Score trend: 5+ consecutive days of declining scores
   - Completion rate drop: >20% week-over-week decrease
   - Multiple habits declining simultaneously
   - Streak freeze usage frequency
   - Time since last "easy" difficulty rating

2. Risk Levels:
   - Low (0-25): Healthy habit formation
   - Moderate (26-50): Monitor closely
   - High (51-75): Intervention recommended
   - Critical (76-100): Immediate action needed

3. Intervention Strategy:
   - Moderate: Show encouragement, suggest rest day
   - High: Suggest habit modification, reduce scope
   - Critical: Recommend break, create relapse prevention plan

References:
- Lally, P., et al. (2010). "How are habits formed"
- Gardner, B., et al. (2012). "Habit formation process"
- Research on implementation intentions and habit persistence
"""
from enum import Enum
from dataclasses import dataclass, field
from datetime import date
from typing import List, Dict, Any, Optional
import uuid


class BurnoutRiskLevel(str, Enum):
    """
    Burnout risk levels with intervention thresholds.

    Each level corresponds to a risk score range and
    recommended intervention strategy.
    """
    LOW = "low"  # 0-25: Healthy
    MODERATE = "moderate"  # 26-50: Monitor
    HIGH = "high"  # 51-75: Intervene
    CRITICAL = "critical"  # 76-100: Urgent


class ContributingFactor(str, Enum):
    """
    Factors that contribute to burnout risk.

    Each factor can be tracked and weighted in the
    overall risk calculation.
    """
    DECLINING_SCORE_TREND = "declining_score_trend"
    COMPLETION_RATE_DROP = "completion_rate_drop"
    MULTIPLE_HABITS_DECLINING = "multiple_habits_declining"
    FREQUENT_STREAK_FREEZES = "frequent_streak_freezes"
    NO_DIFFICULTY_ADJUSTMENT = "no_difficulty_adjustment"
    LOW_AUTOMATICITY = "low_automaticity"
    PERFECT_STREAK_PRESSURE = "perfect_streak_pressure"
    NEGATIVE_SENTIMENT = "negative_sentiment"


@dataclass
class BurnoutRisk:
    """
    A burnout risk assessment for a habit.

    Tracks the risk score, level, and contributing factors
    to enable early intervention and prevent habit abandonment.

    Attributes:
        id: Unique identifier
        habit_id: ID of the habit being assessed
        user_id: ID of the user (for multi-user support)
        risk_score: Overall risk score (0-100)
        risk_level: Categorized risk level
        contributing_factors: List of factors with weights
        assessment_date: Date of this assessment
        trend: Whether risk is increasing, stable, or decreasing
        previous_score: Previous assessment's score (for trend)
        intervention_suggested: Whether intervention is recommended
        intervention_type: Type of intervention suggested
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    habit_id: str = ""
    user_id: str = ""
    risk_score: float = 0.0
    risk_level: BurnoutRiskLevel = BurnoutRiskLevel.LOW
    contributing_factors: Dict[str, float] = field(default_factory=dict)
    assessment_date: date = field(default_factory=date.today)
    trend: str = "stable"  # "increasing", "stable", "decreasing"
    previous_score: float = 0.0
    intervention_suggested: bool = False
    intervention_type: Optional[str] = None

    def __post_init__(self):
        """Ensure risk level matches score after initialization."""
        # Only calculate level if not explicitly set
        if not self.risk_level or self.risk_level == BurnoutRiskLevel.LOW and self.risk_score > 25:
            self.risk_level = self._calculate_risk_level()

    def _calculate_risk_level(self) -> BurnoutRiskLevel:
        """
        Calculate risk level from score.

        Returns:
            Appropriate BurnoutRiskLevel for current score
        """
        if self.risk_score <= 25:
            return BurnoutRiskLevel.LOW
        elif self.risk_score <= 50:
            return BurnoutRiskLevel.MODERATE
        elif self.risk_score <= 75:
            return BurnoutRiskLevel.HIGH
        else:
            return BurnoutRiskLevel.CRITICAL

    def add_factor(self, factor: ContributingFactor, weight: float) -> None:
        """
        Add a contributing factor with weight.

        Args:
            factor: The contributing factor
            weight: Weight/importance of this factor (0.0-1.0)
        """
        self.contributing_factors[factor.value] = weight
        self._recalculate_score()

    def remove_factor(self, factor: ContributingFactor) -> None:
        """
        Remove a contributing factor.

        Args:
            factor: The factor to remove
        """
        if factor.value in self.contributing_factors:
            del self.contributing_factors[factor.value]
            self._recalculate_score()

    def _recalculate_score(self) -> None:
        """Recalculate overall risk score from factors."""
        if not self.contributing_factors:
            self.risk_score = 0.0
        else:
            # Sum of all factor weights, normalized to 0-100
            total_weight = sum(self.contributing_factors.values())
            max_possible = len(ContributingFactor)  # Max if all factors at 1.0
            self.risk_score = min(100.0, (total_weight / max_possible) * 100)

        self.risk_level = self._calculate_risk_level()

        # Update trend
        if self.previous_score > 0:
            if self.risk_score > self.previous_score + 5:
                self.trend = "increasing"
            elif self.risk_score < self.previous_score - 5:
                self.trend = "decreasing"
            else:
                self.trend = "stable"

    def get_top_factors(self, limit: int = 3) -> List[Dict[str, Any]]:
        """
        Get top contributing factors by weight.

        Args:
            limit: Maximum number of factors to return

        Returns:
            List of dicts with factor name and weight, sorted by weight
        """
        sorted_factors = sorted(
            self.contributing_factors.items(),
            key=lambda x: x[1],
            reverse=True
        )
        return [
            {"factor": factor, "weight": weight}
            for factor, weight in sorted_factors[:limit]
        ]

    def get_intervention_suggestion(self) -> Dict[str, str]:
        """
        Get suggested intervention based on risk level and factors.

        Returns:
            Dict with 'title', 'description', and 'action' keys
        """
        interventions = {
            BurnoutRiskLevel.LOW: {
                "title": "Keep it up! 🌟",
                "description": "Your habit formation is healthy. Continue your current approach.",
                "action": "maintain"
            },
            BurnoutRiskLevel.MODERATE: {
                "title": "Time for a check-in 🤔",
                "description": "Some warning signs detected. Consider a rest day or reflection.",
                "action": "rest_day"
            },
            BurnoutRiskLevel.HIGH: {
                "title": "Let's adjust your approach 📊",
                "description": "Multiple warning signs detected. Consider making the habit easier.",
                "action": "modify_habit"
            },
            BurnoutRiskLevel.CRITICAL: {
                "title": "Prevent relapse now! ⚠️",
                "description": "High risk of abandoning this habit. Create a prevention plan.",
                "action": "create_plan"
            }
        }

        return interventions.get(
            self.risk_level,
            interventions[BurnoutRiskLevel.LOW]
        )

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert to dictionary for serialization.

        Returns:
            Dictionary representation of burnout risk
        """
        return {
            "id": self.id,
            "habit_id": self.habit_id,
            "user_id": self.user_id,
            "risk_score": round(self.risk_score, 2),
            "risk_level": self.risk_level.value,
            "contributing_factors": self.contributing_factors,
            "assessment_date": self.assessment_date.isoformat(),
            "trend": self.trend,
            "previous_score": self.previous_score,
            "intervention_suggested": self.intervention_suggested,
            "intervention_type": self.intervention_type
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BurnoutRisk":
        """
        Create from dictionary.

        Args:
            data: Dictionary with burnout risk data

        Returns:
            New BurnoutRisk instance
        """
        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            habit_id=data.get("habit_id", ""),
            user_id=data.get("user_id", ""),
            risk_score=data.get("risk_score", 0.0),
            risk_level=BurnoutRiskLevel(data.get("risk_level", "low")),
            contributing_factors=data.get("contributing_factors", {}),
            assessment_date=date.fromisoformat(data["assessment_date"]) if "assessment_date" in data else date.today(),
            trend=data.get("trend", "stable"),
            previous_score=data.get("previous_score", 0.0),
            intervention_suggested=data.get("intervention_suggested", False),
            intervention_type=data.get("intervention_type")
        )

    def __str__(self) -> str:
        """String representation."""
        emoji = {
            BurnoutRiskLevel.LOW: "🟢",
            BurnoutRiskLevel.MODERATE: "🟡",
            BurnoutRiskLevel.HIGH: "🟠",
            BurnoutRiskLevel.CRITICAL: "🔴"
        }.get(self.risk_level, "⚪")

        return f"{emoji} Burnout Risk: {self.risk_score:.1f}% ({self.risk_level.value})"


@dataclass
class BurnoutSnapshot:
    """
    Historical snapshot of burnout risk for tracking trends.

    Used to store periodic assessments and analyze risk patterns over time.

    Attributes:
        id: Unique identifier
        habit_id: ID of the habit
        risk_score: Risk score at time of snapshot
        risk_level: Risk level at time of snapshot
        top_factors: Top 3 contributing factors
        snapshot_date: Date of snapshot
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    habit_id: str = ""
    risk_score: float = 0.0
    risk_level: BurnoutRiskLevel = BurnoutRiskLevel.LOW
    top_factors: List[str] = field(default_factory=list)
    snapshot_date: date = field(default_factory=date.today)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "id": self.id,
            "habit_id": self.habit_id,
            "risk_score": round(self.risk_score, 2),
            "risk_level": self.risk_level.value,
            "top_factors": self.top_factors,
            "snapshot_date": self.snapshot_date.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "BurnoutSnapshot":
        """Create from dictionary."""
        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            habit_id=data.get("habit_id", ""),
            risk_score=data.get("risk_score", 0.0),
            risk_level=BurnoutRiskLevel(data.get("risk_level", "low")),
            top_factors=data.get("top_factors", []),
            snapshot_date=date.fromisoformat(data["snapshot_date"]) if "snapshot_date" in data else date.today()
        )
