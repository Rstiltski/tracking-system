"""
Unit Tests for Habit Difficulty Model

Tests for DifficultyRating, AdjustmentType, and related dataclasses.

Usage:
    python3 -m pytest brain/models/tests/test_difficulty.py -v
"""
import pytest
from datetime import datetime
from brain.models.habit_difficulty import (
    DifficultyRating,
    AdjustmentType,
    DifficultyRatingEntry,
    DifficultyAdjustment,
    DifficultySuggestion,
    SUGGESTION_TEMPLATES,
)


class TestDifficultyRating:
    """Tests for DifficultyRating enum."""

    def test_rating_values(self):
        """Test that rating enum has correct values."""
        assert DifficultyRating.TOO_EASY.value == "too_easy"
        assert DifficultyRating.JUST_RIGHT.value == "just_right"
        assert DifficultyRating.TOO_HARD.value == "too_hard"


class TestAdjustmentType:
    """Tests for AdjustmentType enum."""

    def test_type_values(self):
        """Test that adjustment type enum has correct values."""
        assert AdjustmentType.INCREASE_TARGET.value == "increase_target"
        assert AdjustmentType.DECREASE_TARGET.value == "decrease_target"
        assert AdjustmentType.CHANGE_FREQUENCY.value == "change_frequency"
        assert AdjustmentType.ADD_SUPPORT.value == "add_support"
        assert AdjustmentType.NO_CHANGE.value == "no_change"


class TestDifficultyRatingEntry:
    """Tests for DifficultyRatingEntry dataclass."""

    def test_create_default(self):
        """Test creating rating with default values."""
        entry = DifficultyRatingEntry()
        
        assert entry.id is not None
        assert len(entry.id) == 8
        assert entry.habit_id == ""
        assert entry.user_id == ""
        assert entry.rating == DifficultyRating.JUST_RIGHT
        assert entry.notes == ""
        assert entry.adjustment_made is False
        assert entry.adjustment_type is None

    def test_create_with_values(self):
        """Test creating rating with specific values."""
        entry = DifficultyRatingEntry(
            habit_id="habit-123",
            user_id="user-456",
            rating=DifficultyRating.TOO_HARD,
            notes="This is too challenging"
        )
        
        assert entry.habit_id == "habit-123"
        assert entry.user_id == "user-456"
        assert entry.rating == DifficultyRating.TOO_HARD
        assert entry.notes == "This is too challenging"

    def test_to_dict(self):
        """Test converting to dictionary."""
        entry = DifficultyRatingEntry(
            habit_id="habit-123",
            rating=DifficultyRating.TOO_EASY
        )
        
        data = entry.to_dict()
        
        assert data["habit_id"] == "habit-123"
        assert data["rating"] == "too_easy"
        assert "id" in data
        assert "rated_at" in data

    def test_from_dict(self):
        """Test creating from dictionary."""
        data = {
            "id": "test-id",
            "habit_id": "habit-789",
            "rating": "too_hard",
            "notes": "Too difficult",
            "rated_at": "2026-02-26T10:00:00"
        }
        
        entry = DifficultyRatingEntry.from_dict(data)
        
        assert entry.id == "test-id"
        assert entry.habit_id == "habit-789"
        assert entry.rating == DifficultyRating.TOO_HARD
        assert entry.notes == "Too difficult"

    def test_str_representation(self):
        """Test string representation."""
        entry = DifficultyRatingEntry(rating=DifficultyRating.TOO_HARD)
        entry_str = str(entry)
        
        assert "📉" in entry_str
        assert "too hard" in entry_str.lower()


class TestDifficultyAdjustment:
    """Tests for DifficultyAdjustment dataclass."""

    def test_create_default(self):
        """Test creating adjustment with default values."""
        adjustment = DifficultyAdjustment()
        
        assert adjustment.id is not None
        assert adjustment.adjustment_type == AdjustmentType.NO_CHANGE
        assert adjustment.old_value is None
        assert adjustment.new_value is None
        assert adjustment.effectiveness is None

    def test_create_with_values(self):
        """Test creating adjustment with specific values."""
        adjustment = DifficultyAdjustment(
            habit_id="habit-123",
            adjustment_type=AdjustmentType.DECREASE_TARGET,
            old_value=1.0,
            new_value=0.5,
            reason="User rated as too hard"
        )
        
        assert adjustment.habit_id == "habit-123"
        assert adjustment.adjustment_type == AdjustmentType.DECREASE_TARGET
        assert adjustment.old_value == 1.0
        assert adjustment.new_value == 0.5
        assert adjustment.reason == "User rated as too hard"

    def test_effectiveness_validation(self):
        """Test that effectiveness is clamped to 1-5 range."""
        # Too low
        adjustment = DifficultyAdjustment(effectiveness=0)
        assert adjustment.effectiveness == 1
        
        # Too high
        adjustment = DifficultyAdjustment(effectiveness=10)
        assert adjustment.effectiveness == 5
        
        # Valid
        adjustment = DifficultyAdjustment(effectiveness=4)
        assert adjustment.effectiveness == 4

    def test_to_dict(self):
        """Test converting to dictionary."""
        adjustment = DifficultyAdjustment(
            adjustment_type=AdjustmentType.INCREASE_TARGET,
            old_value=1.0,
            new_value=1.15,
            effectiveness=5
        )
        
        data = adjustment.to_dict()
        
        assert data["adjustment_type"] == "increase_target"
        assert data["old_value"] == 1.0
        assert data["new_value"] == 1.15
        assert data["effectiveness"] == 5

    def test_from_dict(self):
        """Test creating from dictionary."""
        data = {
            "id": "adj-id",
            "habit_id": "habit-123",
            "adjustment_type": "decrease_target",
            "old_value": 2.0,
            "new_value": 1.0,
            "reason": "Testing",
            "effectiveness": 4,
            "adjusted_at": "2026-02-26T12:00:00"
        }
        
        adjustment = DifficultyAdjustment.from_dict(data)
        
        assert adjustment.id == "adj-id"
        assert adjustment.habit_id == "habit-123"
        assert adjustment.adjustment_type == AdjustmentType.DECREASE_TARGET
        assert adjustment.old_value == 2.0
        assert adjustment.new_value == 1.0
        assert adjustment.effectiveness == 4

    def test_str_representation(self):
        """Test string representation."""
        adjustment = DifficultyAdjustment(adjustment_type=AdjustmentType.INCREASE_TARGET)
        adj_str = str(adjustment)
        
        assert "⬆️" in adj_str
        assert "increase target" in adj_str.lower()


class TestDifficultySuggestion:
    """Tests for DifficultySuggestion dataclass."""

    def test_create_suggestion(self):
        """Test creating a suggestion."""
        suggestion = DifficultySuggestion(
            habit_id="habit-123",
            suggestion_type=AdjustmentType.DECREASE_TARGET,
            title="Make it tiny",
            description="Reduce to 2-minute version",
            current_value=1.0,
            suggested_value=0.5,
            reason="User struggling",
            confidence=0.9
        )
        
        assert suggestion.habit_id == "habit-123"
        assert suggestion.suggestion_type == AdjustmentType.DECREASE_TARGET
        assert suggestion.title == "Make it tiny"
        assert suggestion.current_value == 1.0
        assert suggestion.suggested_value == 0.5
        assert suggestion.confidence == 0.9

    def test_get_action_text(self):
        """Test getting action button text."""
        suggestion = DifficultySuggestion(suggestion_type=AdjustmentType.INCREASE_TARGET)
        assert suggestion.get_action_text() == "Increase Target"
        
        suggestion = DifficultySuggestion(suggestion_type=AdjustmentType.DECREASE_TARGET)
        assert suggestion.get_action_text() == "Make It Tiny"
        
        suggestion = DifficultySuggestion(suggestion_type=AdjustmentType.CHANGE_FREQUENCY)
        assert suggestion.get_action_text() == "Reduce Frequency"
        
        suggestion = DifficultySuggestion(suggestion_type=AdjustmentType.NO_CHANGE)
        assert suggestion.get_action_text() == "Keep as Is"

    def test_to_dict(self):
        """Test converting to dictionary."""
        suggestion = DifficultySuggestion(
            habit_id="habit-123",
            suggestion_type=AdjustmentType.INCREASE_TARGET,
            confidence=0.85
        )
        
        data = suggestion.to_dict()
        
        assert data["habit_id"] == "habit-123"
        assert data["suggestion_type"] == "increase_target"
        assert data["confidence"] == 0.85

    def test_from_dict(self):
        """Test creating from dictionary."""
        data = {
            "habit_id": "habit-456",
            "suggestion_type": "decrease_target",
            "title": "Test",
            "confidence": 0.75
        }
        
        suggestion = DifficultySuggestion.from_dict(data)
        
        assert suggestion.habit_id == "habit-456"
        assert suggestion.suggestion_type == AdjustmentType.DECREASE_TARGET
        assert suggestion.title == "Test"
        assert suggestion.confidence == 0.75


class TestSuggestionTemplates:
    """Tests for suggestion templates."""

    def test_templates_exist(self):
        """Test that templates exist for all ratings."""
        assert DifficultyRating.TOO_EASY in SUGGESTION_TEMPLATES
        assert DifficultyRating.TOO_HARD in SUGGESTION_TEMPLATES

    def test_template_structure(self):
        """Test that templates have required fields."""
        for rating, template in SUGGESTION_TEMPLATES.items():
            assert "title" in template
            assert "description" in template
            assert "adjustment_type" in template
            assert "increase_percentage" in template or "decrease_percentage" in template

    def test_too_easy_template(self):
        """Test TOO_EASY template."""
        template = SUGGESTION_TEMPLATES[DifficultyRating.TOO_EASY]
        
        assert template["adjustment_type"] == AdjustmentType.INCREASE_TARGET
        assert template["increase_percentage"] == 0.15  # 15% increase

    def test_too_hard_template(self):
        """Test TOO_HARD template."""
        template = SUGGESTION_TEMPLATES[DifficultyRating.TOO_HARD]
        
        assert template["adjustment_type"] == AdjustmentType.DECREASE_TARGET
        assert template["decrease_percentage"] == 0.50  # 50% reduction


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
