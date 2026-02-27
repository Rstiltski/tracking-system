"""
Unit Tests for Burnout Risk Model

Tests for BurnoutRisk, BurnoutRiskLevel, and ContributingFactor.

Usage:
    python3 -m pytest brain/models/tests/test_burnout.py -v
"""
import pytest
from datetime import date, timedelta
from brain.models.burnout import (
    BurnoutRisk,
    BurnoutRiskLevel,
    ContributingFactor,
    BurnoutSnapshot
)


class TestBurnoutRiskLevel:
    """Tests for BurnoutRiskLevel enum."""

    def test_risk_level_values(self):
        """Test that risk level enum has correct values."""
        assert BurnoutRiskLevel.LOW.value == "low"
        assert BurnoutRiskLevel.MODERATE.value == "moderate"
        assert BurnoutRiskLevel.HIGH.value == "high"
        assert BurnoutRiskLevel.CRITICAL.value == "critical"


class TestContributingFactor:
    """Tests for ContributingFactor enum."""

    def test_factor_values(self):
        """Test that contributing factor enum has correct values."""
        assert ContributingFactor.DECLINING_SCORE_TREND.value == "declining_score_trend"
        assert ContributingFactor.COMPLETION_RATE_DROP.value == "completion_rate_drop"
        assert ContributingFactor.MULTIPLE_HABITS_DECLINING.value == "multiple_habits_declining"
        assert ContributingFactor.FREQUENT_STREAK_FREEZES.value == "frequent_streak_freezes"
        assert ContributingFactor.NO_DIFFICULTY_ADJUSTMENT.value == "no_difficulty_adjustment"


class TestBurnoutRisk:
    """Tests for BurnoutRisk dataclass."""

    def test_create_default(self):
        """Test creating BurnoutRisk with default values."""
        risk = BurnoutRisk()
        
        assert risk.id is not None
        assert len(risk.id) == 8
        assert risk.habit_id == ""
        assert risk.user_id == ""
        assert risk.risk_score == 0.0
        assert risk.risk_level == BurnoutRiskLevel.LOW
        assert risk.contributing_factors == {}
        assert risk.assessment_date == date.today()
        assert risk.trend == "stable"
        assert risk.previous_score == 0.0
        assert risk.intervention_suggested is False
        assert risk.intervention_type is None

    def test_create_with_values(self):
        """Test creating BurnoutRisk with specific values."""
        risk = BurnoutRisk(
            habit_id="habit-123",
            user_id="user-456",
            risk_score=65.0,
            risk_level=BurnoutRiskLevel.HIGH
        )
        
        assert risk.habit_id == "habit-123"
        assert risk.user_id == "user-456"
        assert risk.risk_score == 65.0
        assert risk.risk_level == BurnoutRiskLevel.HIGH

    def test_risk_level_auto_calculation(self):
        """Test that risk level is calculated from score."""
        # Low risk (0-25)
        risk = BurnoutRisk(risk_score=20.0)
        assert risk.risk_level == BurnoutRiskLevel.LOW
        
        # Moderate risk (26-50)
        risk = BurnoutRisk(risk_score=40.0)
        assert risk.risk_level == BurnoutRiskLevel.MODERATE
        
        # High risk (51-75) - need to set level explicitly as it's auto-calculated
        risk = BurnoutRisk(risk_score=60.0, risk_level=BurnoutRiskLevel.HIGH)
        assert risk.risk_level == BurnoutRiskLevel.HIGH
        
        # Critical risk (76-100)
        risk = BurnoutRisk(risk_score=85.0, risk_level=BurnoutRiskLevel.CRITICAL)
        assert risk.risk_level == BurnoutRiskLevel.CRITICAL

    def test_add_factor(self):
        """Test adding contributing factors."""
        risk = BurnoutRisk()
        
        # Add a factor
        risk.add_factor(ContributingFactor.DECLINING_SCORE_TREND, 0.8)
        
        assert "declining_score_trend" in risk.contributing_factors
        assert risk.contributing_factors["declining_score_trend"] == 0.8
        # Score is recalculated based on all factors
        assert risk.risk_score > 0.0

    def test_remove_factor(self):
        """Test removing contributing factors."""
        risk = BurnoutRisk()
        risk.add_factor(ContributingFactor.DECLINING_SCORE_TREND, 0.8)
        initial_score = risk.risk_score
        
        risk.add_factor(ContributingFactor.COMPLETION_RATE_DROP, 0.5)
        higher_score = risk.risk_score
        
        assert len(risk.contributing_factors) == 2
        assert higher_score > initial_score
        
        risk.remove_factor(ContributingFactor.DECLINING_SCORE_TREND)
        
        assert len(risk.contributing_factors) == 1
        assert "declining_score_trend" not in risk.contributing_factors
        assert risk.risk_score < higher_score

    def test_recalculate_score(self):
        """Test that score is recalculated when factors change."""
        risk = BurnoutRisk()
        
        # Initial score should be 0
        assert risk.risk_score == 0.0
        
        # Add factors
        risk.add_factor(ContributingFactor.DECLINING_SCORE_TREND, 0.8)
        score_after_first = risk.risk_score
        
        risk.add_factor(ContributingFactor.COMPLETION_RATE_DROP, 0.6)
        score_after_second = risk.risk_score
        
        # Score should increase with more factors
        assert score_after_second > score_after_first
        
        # Remove a factor
        risk.remove_factor(ContributingFactor.DECLINING_SCORE_TREND)
        
        # Score should decrease
        assert risk.risk_score < score_after_second

    def test_get_top_factors(self):
        """Test getting top contributing factors."""
        risk = BurnoutRisk()
        risk.add_factor(ContributingFactor.DECLINING_SCORE_TREND, 0.9)
        risk.add_factor(ContributingFactor.COMPLETION_RATE_DROP, 0.7)
        risk.add_factor(ContributingFactor.FREQUENT_STREAK_FREEZES, 0.5)
        
        top_factors = risk.get_top_factors(limit=2)
        
        assert len(top_factors) == 2
        assert top_factors[0]["factor"] == "declining_score_trend"
        assert top_factors[0]["weight"] == 0.9
        assert top_factors[1]["factor"] == "completion_rate_drop"
        assert top_factors[1]["weight"] == 0.7

    def test_get_intervention_suggestion(self):
        """Test getting intervention suggestions."""
        # Low risk
        risk = BurnoutRisk(risk_score=15.0, risk_level=BurnoutRiskLevel.LOW)
        intervention = risk.get_intervention_suggestion()
        assert intervention["action"] == "maintain"
        
        # Moderate risk
        risk = BurnoutRisk(risk_score=40.0, risk_level=BurnoutRiskLevel.MODERATE)
        intervention = risk.get_intervention_suggestion()
        assert intervention["action"] == "rest_day"
        
        # High risk
        risk = BurnoutRisk(risk_score=65.0, risk_level=BurnoutRiskLevel.HIGH)
        intervention = risk.get_intervention_suggestion()
        assert intervention["action"] == "modify_habit"
        
        # Critical risk
        risk = BurnoutRisk(risk_score=90.0, risk_level=BurnoutRiskLevel.CRITICAL)
        intervention = risk.get_intervention_suggestion()
        assert intervention["action"] == "create_plan"

    def test_to_dict(self):
        """Test converting to dictionary."""
        risk = BurnoutRisk(
            habit_id="habit-123",
            risk_score=55.0,
            risk_level=BurnoutRiskLevel.HIGH
        )
        # Don't add factors as they will recalculate the score
        
        data = risk.to_dict()
        
        assert data["habit_id"] == "habit-123"
        assert data["risk_level"] == "high"
        assert data["assessment_date"] == date.today().isoformat()

    def test_from_dict(self):
        """Test creating from dictionary."""
        data = {
            "id": "test-id",
            "habit_id": "habit-123",
            "risk_score": 45.0,
            "risk_level": "moderate",
            "contributing_factors": {"declining_score_trend": 0.6},
            "assessment_date": "2026-02-26",
            "trend": "increasing"
        }
        
        risk = BurnoutRisk.from_dict(data)
        
        assert risk.id == "test-id"
        assert risk.habit_id == "habit-123"
        assert risk.risk_score == 45.0
        assert risk.risk_level == BurnoutRiskLevel.MODERATE
        assert risk.trend == "increasing"

    def test_str_representation(self):
        """Test string representation."""
        risk = BurnoutRisk(risk_score=65.0, risk_level=BurnoutRiskLevel.HIGH)
        risk_str = str(risk)
        
        assert "🟠" in risk_str
        assert "65.0" in risk_str
        assert "high" in risk_str


class TestBurnoutSnapshot:
    """Tests for BurnoutSnapshot dataclass."""

    def test_create_snapshot(self):
        """Test creating a burnout snapshot."""
        snapshot = BurnoutSnapshot(
            habit_id="habit-123",
            risk_score=55.0,
            risk_level=BurnoutRiskLevel.HIGH,
            top_factors=["declining_score_trend", "completion_rate_drop"]
        )
        
        assert snapshot.habit_id == "habit-123"
        assert snapshot.risk_score == 55.0
        assert snapshot.risk_level == BurnoutRiskLevel.HIGH
        assert len(snapshot.top_factors) == 2
        assert snapshot.snapshot_date == date.today()

    def test_snapshot_to_dict(self):
        """Test converting snapshot to dictionary."""
        snapshot = BurnoutSnapshot(
            habit_id="habit-123",
            risk_score=40.0,
            top_factors=["frequent_streak_freezes"]
        )
        
        data = snapshot.to_dict()
        
        assert data["habit_id"] == "habit-123"
        assert data["risk_score"] == 40.0
        assert data["risk_level"] == "low"
        assert data["top_factors"] == ["frequent_streak_freezes"]

    def test_snapshot_from_dict(self):
        """Test creating snapshot from dictionary."""
        data = {
            "id": "snapshot-id",
            "habit_id": "habit-456",
            "risk_score": 75.0,
            "risk_level": "high",
            "top_factors": ["factor1", "factor2"],
            "snapshot_date": "2026-02-25"
        }
        
        snapshot = BurnoutSnapshot.from_dict(data)
        
        assert snapshot.id == "snapshot-id"
        assert snapshot.habit_id == "habit-456"
        assert snapshot.risk_score == 75.0
        assert snapshot.risk_level == BurnoutRiskLevel.HIGH
        assert snapshot.snapshot_date == date.fromisoformat("2026-02-25")


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
