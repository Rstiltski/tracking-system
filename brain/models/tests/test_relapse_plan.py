"""
Unit Tests for Relapse Prevention Plan Model

Tests for PlanCategory, PlanTrigger, RelapsePreventionPlan, and related classes.

Usage:
    python3 -m pytest brain/models/tests/test_relapse_plan.py -v
"""
import pytest
from datetime import datetime, timedelta
from brain.models.relapse_plan import (
    PlanCategory,
    PlanTrigger,
    RelapsePreventionPlan,
    PlanTemplate,
    PlanUsage,
    DEFAULT_PLAN_TEMPLATES,
)


class TestPlanCategory:
    """Tests for PlanCategory enum."""

    def test_category_values(self):
        """Test that category enum has correct values."""
        assert PlanCategory.MISSED_DAY.value == "missed_day"
        assert PlanCategory.TRAVEL.value == "travel"
        assert PlanCategory.LOW_MOTIVATION.value == "low_motivation"
        assert PlanCategory.TIME_CRUNCH.value == "time_crunch"
        assert PlanCategory.STRESS.value == "stress"
        assert PlanCategory.SOCIAL.value == "social"
        assert PlanCategory.CUSTOM.value == "custom"


class TestPlanTrigger:
    """Tests for PlanTrigger enum."""

    def test_trigger_values(self):
        """Test that trigger enum has correct values."""
        assert PlanTrigger.MISSED_YESTERDAY.value == "missed_yesterday"
        assert PlanTrigger.STREAK_below_3.value == "streak_below_3"
        assert PlanTrigger.SCORE_BELOW_50.value == "score_below_50"
        assert PlanTrigger.BURNOUT_MODERATE.value == "burnout_moderate"
        assert PlanTrigger.BURNOUT_HIGH.value == "burnout_high"
        assert PlanTrigger.CUSTOM.value == "custom"


class TestRelapsePreventionPlan:
    """Tests for RelapsePreventionPlan dataclass."""

    def test_create_default(self):
        """Test creating plan with default values."""
        plan = RelapsePreventionPlan()
        
        assert plan.id is not None
        assert len(plan.id) == 8
        assert plan.habit_id == ""
        assert plan.user_id == ""
        assert plan.category == PlanCategory.CUSTOM
        assert plan.trigger == PlanTrigger.CUSTOM
        assert plan.is_active is True
        assert plan.usage_count == 0
        assert plan.effectiveness is None

    def test_create_with_values(self):
        """Test creating plan with specific values."""
        plan = RelapsePreventionPlan(
            habit_id="habit-123",
            user_id="user-456",
            category=PlanCategory.MISSED_DAY,
            trigger=PlanTrigger.MISSED_YESTERDAY,
            if_condition="I miss a day",
            then_action="Do a tiny version the next day",
            action_type="reduce",
            backup_plan="Just show up for 30 seconds"
        )
        
        assert plan.habit_id == "habit-123"
        assert plan.user_id == "user-456"
        assert plan.category == PlanCategory.MISSED_DAY
        assert plan.trigger == PlanTrigger.MISSED_YESTERDAY
        assert plan.if_condition == "I miss a day"
        assert plan.then_action == "Do a tiny version the next day"
        assert plan.action_type == "reduce"
        assert plan.backup_plan == "Just show up for 30 seconds"

    def test_get_if_then_text(self):
        """Test getting if-then statement."""
        plan = RelapsePreventionPlan(
            if_condition="I'm traveling",
            then_action="Do a simplified version"
        )
        
        if_then = plan.get_if_then_text()
        
        assert "If I'm traveling" in if_then
        assert "then I will Do a simplified version" in if_then

    def test_record_usage(self):
        """Test recording plan usage."""
        plan = RelapsePreventionPlan()
        
        assert plan.usage_count == 0
        assert plan.last_used is None
        assert plan.effectiveness is None
        
        # Record usage with effectiveness
        plan.record_usage(effectiveness_rating=5)
        
        assert plan.usage_count == 1
        assert plan.last_used is not None
        assert plan.effectiveness == 5
        
        # Record another usage
        plan.record_usage(effectiveness_rating=4)
        
        assert plan.usage_count == 2
        # Should be weighted average
        assert plan.effectiveness is not None

    def test_to_dict(self):
        """Test converting to dictionary."""
        plan = RelapsePreventionPlan(
            habit_id="habit-123",
            category=PlanCategory.TIME_CRUNCH,
            if_condition="I'm busy",
            then_action="Do 1 minute"
        )
        
        data = plan.to_dict()
        
        assert data["habit_id"] == "habit-123"
        assert data["category"] == "time_crunch"
        assert data["if_condition"] == "I'm busy"
        assert data["then_action"] == "Do 1 minute"
        assert "id" in data
        assert "is_active" in data

    def test_from_dict(self):
        """Test creating from dictionary."""
        data = {
            "id": "plan-id",
            "habit_id": "habit-789",
            "category": "travel",
            "trigger": "traveling",
            "if_condition": "I'm away from home",
            "then_action": "Do home version",
            "action_type": "substitute",
            "is_active": True,
            "usage_count": 3,
            "effectiveness": 4,
            "created_at": "2026-02-26T10:00:00"
        }
        
        plan = RelapsePreventionPlan.from_dict(data)
        
        assert plan.id == "plan-id"
        assert plan.habit_id == "habit-789"
        assert plan.category == PlanCategory.TRAVEL
        assert plan.trigger == PlanTrigger.TRAVELING
        assert plan.if_condition == "I'm away from home"
        assert plan.then_action == "Do home version"
        assert plan.usage_count == 3
        assert plan.effectiveness == 4

    def test_str_representation(self):
        """Test string representation."""
        plan = RelapsePreventionPlan(category=PlanCategory.MISSED_DAY)
        plan_str = str(plan)
        
        assert "📅" in plan_str
        assert "Missed Day" in plan_str


class TestPlanTemplate:
    """Tests for PlanTemplate dataclass."""

    def test_create_template(self):
        """Test creating a plan template."""
        template = PlanTemplate(
            category=PlanCategory.LOW_MOTIVATION,
            name="The 2-Minute Rule",
            description="For when motivation is zero",
            if_condition="I have zero motivation",
            then_action="Do just 2 minutes",
            action_type="reduce",
            effectiveness_rating=4.5
        )
        
        assert template.category == PlanCategory.LOW_MOTIVATION
        assert template.name == "The 2-Minute Rule"
        assert template.description == "For when motivation is zero"
        assert template.if_condition == "I have zero motivation"
        assert template.then_action == "Do just 2 minutes"
        assert template.effectiveness_rating == 4.5

    def test_template_to_dict(self):
        """Test converting template to dictionary."""
        template = PlanTemplate(
            name="Test Template",
            if_condition="Test if",
            then_action="Test then"
        )
        
        data = template.to_dict()
        
        assert data["name"] == "Test Template"
        assert data["if_condition"] == "Test if"
        assert data["then_action"] == "Test then"
        assert "id" in data

    def test_template_from_dict(self):
        """Test creating template from dictionary."""
        data = {
            "id": "template-id",
            "category": "stress",
            "name": "Stress Plan",
            "if_condition": "I'm stressed",
            "then_action": "Relax",
            "effectiveness_rating": 3.8
        }
        
        template = PlanTemplate.from_dict(data)
        
        assert template.id == "template-id"
        assert template.category == PlanCategory.STRESS
        assert template.name == "Stress Plan"
        assert template.effectiveness_rating == 3.8


class TestPlanUsage:
    """Tests for PlanUsage dataclass."""

    def test_create_usage(self):
        """Test creating a plan usage record."""
        usage = PlanUsage(
            plan_id="plan-123",
            habit_id="habit-456",
            situation="Was too busy",
            action_taken="Did 1 minute version",
            effectiveness=4,
            notes="Worked well"
        )
        
        assert usage.plan_id == "plan-123"
        assert usage.habit_id == "habit-456"
        assert usage.situation == "Was too busy"
        assert usage.action_taken == "Did 1 minute version"
        assert usage.effectiveness == 4
        assert usage.notes == "Worked well"

    def test_usage_to_dict(self):
        """Test converting usage to dictionary."""
        usage = PlanUsage(
            plan_id="plan-123",
            effectiveness=5
        )
        
        data = usage.to_dict()
        
        assert data["plan_id"] == "plan-123"
        assert data["effectiveness"] == 5
        assert "id" in data
        assert "used_at" in data

    def test_usage_from_dict(self):
        """Test creating usage from dictionary."""
        data = {
            "id": "usage-id",
            "plan_id": "plan-789",
            "habit_id": "habit-123",
            "used_at": "2026-02-26T15:00:00",
            "situation": "Traveling",
            "effectiveness": 3
        }
        
        usage = PlanUsage.from_dict(data)
        
        assert usage.id == "usage-id"
        assert usage.plan_id == "plan-789"
        assert usage.habit_id == "habit-123"
        assert usage.situation == "Traveling"
        assert usage.effectiveness == 3


class TestDefaultTemplates:
    """Tests for default plan templates."""

    def test_templates_exist(self):
        """Test that default templates exist."""
        assert len(DEFAULT_PLAN_TEMPLATES) > 0

    def test_template_categories_covered(self):
        """Test that all major categories have templates."""
        categories_in_templates = {t.category for t in DEFAULT_PLAN_TEMPLATES}
        
        # Check major categories are covered
        assert PlanCategory.MISSED_DAY in categories_in_templates
        assert PlanCategory.LOW_MOTIVATION in categories_in_templates
        assert PlanCategory.TIME_CRUNCH in categories_in_templates

    def test_template_structure(self):
        """Test that all templates have required fields."""
        for template in DEFAULT_PLAN_TEMPLATES:
            assert template.id is not None
            assert template.name
            assert template.description
            assert template.if_condition
            assert template.then_action
            assert template.category

    def test_missed_day_templates(self):
        """Test missed day templates."""
        missed_day_templates = [
            t for t in DEFAULT_PLAN_TEMPLATES
            if t.category == PlanCategory.MISSED_DAY
        ]
        
        assert len(missed_day_templates) >= 2
        
        # Check for "Never Miss Twice" template
        names = [t.name for t in missed_day_templates]
        assert "Never Miss Twice" in names or "The Fresh Start" in names

    def test_effectiveness_ratings(self):
        """Test that templates have effectiveness ratings."""
        for template in DEFAULT_PLAN_TEMPLATES:
            # All templates should have some effectiveness rating
            assert template.effectiveness_rating >= 0.0
            assert template.effectiveness_rating <= 5.0


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
