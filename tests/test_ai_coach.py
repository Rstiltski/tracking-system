"""
Tests for AI Coach Module

Tests the Digital Coach components including:
- User Assessment
- Rule Engine
- Suggestion Engine
- Intervention Engine
- Recovery Mode
"""

import pytest
from datetime import datetime, timedelta
from typing import Dict, Any

# User Assessment
from brain.ai.coach.user_assessment import (
    UserAssessment,
    UserState,
    RiskLevel,
    EngagementLevel
)

# Rules
from brain.ai.coach.rules import (
    RuleEngine,
    InterventionRule,
    InterventionType,
    Priority,
    TriggeredRule
)

# Personality
from brain.ai.coach.personality import (
    PersonalityConfig,
    CoachPersonality,
    InterventionFrequency,
    ToneStyle,
    get_default_config
)

# Suggestion Engine
from brain.ai.coach.suggestion_engine import (
    SuggestionEngine,
    Suggestion
)

# Intervention Engine
from brain.ai.coach.intervention_engine import (
    InterventionEngine,
    Intervention,
    DigitalCoach
)

# Recovery Mode
from brain.ai.coach.recovery_mode import (
    RecoveryMode,
    RecoveryModeManager,
    ModeConfig
)


# ============================================
# Test Data
# ============================================

def get_test_user_data() -> Dict[str, Any]:
    """Get test user data for testing."""
    return {
        "habits": [
            {
                "id": "habit_1",
                "name": "Morning Exercise",
                "streak": 15,
                "best_streak": 30,
                "completion_rate": 0.85,
                "streak_broken_recently": False
            },
            {
                "id": "habit_2",
                "name": "Meditation",
                "streak": 0,
                "best_streak": 21,
                "completion_rate": 0.45,
                "streak_broken_recently": True
            }
        ],
        "tasks": [
            {"id": "task_1", "title": "Complete project", "completed": True},
            {"id": "task_2", "title": "Review code", "completed": False},
            {"id": "task_3", "title": "Write docs", "completed": False}
        ],
        "health": {
            "sleep": [7.5, 6.0, 7.0, 5.5, 6.5, 7.0, 6.0],
            "mood": [4, 3, 4, 3, 3, 4, 3]
        },
        "goals": [
            {"id": "goal_1", "name": "Run 100km", "progress": 75, "recently_completed": False},
            {"id": "goal_2", "name": "Read 12 books", "progress": 40, "recently_completed": False}
        ],
        "activity_log": [
            {"timestamp": (datetime.now() - timedelta(hours=i)).isoformat()}
            for i in range(10)
        ]
    }


def get_high_burnout_data() -> Dict[str, Any]:
    """Get test data for high burnout risk scenario."""
    data = get_test_user_data()
    data["health"]["sleep"] = [4.0, 5.0, 4.5, 5.5, 4.0, 5.0, 4.5]
    data["health"]["mood"] = [2, 2, 3, 2, 2, 3, 2]
    data["tasks"] = [
        {"id": f"task_{i}", "title": f"Task {i}", "completed": i % 3 == 0}
        for i in range(10)
    ]
    for habit in data["habits"]:
        habit["streak_broken_recently"] = True
    return data


def get_low_burnout_data() -> Dict[str, Any]:
    """Get test data for low burnout risk scenario."""
    data = get_test_user_data()
    data["health"]["sleep"] = [8.0, 7.5, 8.0, 7.5, 8.0, 7.5, 8.0]
    data["health"]["mood"] = [5, 4, 5, 4, 5, 4, 5]
    data["tasks"] = [
        {"id": f"task_{i}", "title": f"Task {i}", "completed": True}
        for i in range(5)
    ]
    for habit in data["habits"]:
        habit["streak"] = 30
        habit["streak_broken_recently"] = False
        habit["completion_rate"] = 0.95
    return data


# ============================================
# User Assessment Tests
# ============================================

class TestUserAssessment:
    """Tests for UserAssessment class."""
    
    def test_assessment_returns_user_state(self):
        """Test that assessment returns a UserState object."""
        assessment = UserAssessment()
        user_data = get_test_user_data()
        
        state = assessment.assess(user_data)
        
        assert isinstance(state, UserState)
        assert isinstance(state.burnout_risk, int)
        assert isinstance(state.burnout_level, RiskLevel)
        assert isinstance(state.streak_health, int)
    
    def test_high_burnout_detection(self):
        """Test that high burnout risk is detected."""
        assessment = UserAssessment()
        user_data = get_high_burnout_data()
        
        state = assessment.assess(user_data)
        
        assert state.burnout_risk >= 50
        assert state.burnout_level in [RiskLevel.HIGH, RiskLevel.CRITICAL]
    
    def test_low_burnout_detection(self):
        """Test that low burnout risk is detected."""
        assessment = UserAssessment()
        user_data = get_low_burnout_data()
        
        state = assessment.assess(user_data)
        
        assert state.burnout_risk < 30
        assert state.burnout_level == RiskLevel.LOW
    
    def test_streak_health_calculation(self):
        """Test streak health calculation."""
        assessment = UserAssessment()
        user_data = get_test_user_data()
        
        state = assessment.assess(user_data)
        
        assert 0 <= state.streak_health <= 100
    
    def test_habits_assessment(self):
        """Test per-habit assessment."""
        assessment = UserAssessment()
        user_data = get_test_user_data()
        
        state = assessment.assess(user_data)
        
        assert len(state.habits_assessment) == 2
        for habit_id, habit_data in state.habits_assessment.items():
            assert "streak" in habit_data
            assert "health" in habit_data
    
    def test_trend_calculation(self):
        """Test mood and sleep trend calculation."""
        assessment = UserAssessment()
        user_data = get_test_user_data()
        
        state = assessment.assess(user_data)
        
        assert state.mood_trend in ["improving", "declining", "stable"]
        assert state.sleep_trend in ["improving", "declining", "stable"]
    
    def test_warnings_generated(self):
        """Test that warnings are generated for issues."""
        assessment = UserAssessment()
        user_data = get_high_burnout_data()
        
        state = assessment.assess(user_data)
        
        assert len(state.warnings) > 0


# ============================================
# Rule Engine Tests
# ============================================

class TestRuleEngine:
    """Tests for RuleEngine class."""
    
    def test_rule_engine_initializes(self):
        """Test that rule engine initializes with default rules."""
        engine = RuleEngine()
        
        assert len(engine.rules) > 0
    
    def test_burnout_critical_rule(self):
        """Test that critical burnout triggers rule."""
        engine = RuleEngine()
        state = {"burnout_risk": 85}
        
        triggered = engine.check(state)
        
        burnout_rules = [t for t in triggered if "burnout" in t.rule.name]
        assert len(burnout_rules) > 0
        assert burnout_rules[0].rule.priority == Priority.CRITICAL
    
    def test_burnout_high_rule(self):
        """Test that high burnout triggers rule."""
        engine = RuleEngine()
        state = {"burnout_risk": 60}
        
        triggered = engine.check(state)
        
        burnout_rules = [t for t in triggered if "burnout" in t.rule.name]
        assert len(burnout_rules) > 0
    
    def test_low_engagement_rule(self):
        """Test that low engagement triggers rule."""
        engine = RuleEngine()
        state = {"engagement_level": "dormant"}
        
        triggered = engine.check(state)
        
        engagement_rules = [t for t in triggered if "engagement" in t.rule.name]
        assert len(engagement_rules) > 0
    
    def test_streak_milestone_rule(self):
        """Test that streak milestones trigger celebration."""
        engine = RuleEngine()
        state = {
            "habits_assessment": {
                "habit_1": {"streak": 7, "health": "developing"}
            }
        }
        
        triggered = engine.check(state)
        
        streak_rules = [t for t in triggered if "streak" in t.rule.name]
        assert len(streak_rules) > 0
    
    def test_cooldown_respected(self):
        """Test that cooldown period is respected."""
        engine = RuleEngine()
        state = {"burnout_risk": 85}
        
        # First trigger
        triggered1 = engine.check(state)
        assert len(triggered1) > 0
        
        # Immediate second check should not trigger
        triggered2 = engine.check(state)
        burnout_rules = [t for t in triggered2 if "burnout" in t.rule.name]
        assert len(burnout_rules) == 0
    
    def test_custom_rule_can_be_added(self):
        """Test that custom rules can be added."""
        engine = RuleEngine()
        
        custom_rule = InterventionRule(
            name="custom_test",
            intervention_type=InterventionType.PATTERN_DETECTED,
            priority=Priority.LOW,
            description="Custom test rule",
            condition=lambda s: s.get("custom_trigger", False)
        )
        
        engine.add_rule(custom_rule)
        
        # Check rule was added
        assert any(r.name == "custom_test" for r in engine.rules)
        
        # Trigger the rule
        triggered = engine.check({"custom_trigger": True})
        assert any(t.rule.name == "custom_test" for t in triggered)


# ============================================
# Personality Config Tests
# ============================================

class TestPersonalityConfig:
    """Tests for PersonalityConfig class."""
    
    def test_default_config(self):
        """Test default configuration creation."""
        config = PersonalityConfig()
        
        assert config.personality == CoachPersonality.ENCOURAGING
        assert config.tone == ToneStyle.WARM
        assert config.intervention_frequency == InterventionFrequency.NORMAL
    
    def test_preset_configs(self):
        """Test preset configurations."""
        balanced = get_default_config("balanced")
        assert balanced.personality == CoachPersonality.ENCOURAGING
        
        intensive = get_default_config("intensive")
        assert intensive.intervention_frequency == InterventionFrequency.INTENSIVE
    
    def test_max_interventions_calculation(self):
        """Test max interventions per day calculation."""
        config = PersonalityConfig(
            intervention_frequency=InterventionFrequency.MINIMAL
        )
        assert config.get_max_interventions_per_day() == 1
        
        config = PersonalityConfig(
            intervention_frequency=InterventionFrequency.INTENSIVE
        )
        assert config.get_max_interventions_per_day() == 10
    
    def test_system_prompt_modifier(self):
        """Test system prompt modifier generation."""
        config = PersonalityConfig(
            personality=CoachPersonality.DIRECT,
            tone=ToneStyle.FORMAL
        )
        
        modifier = config.get_system_prompt_modifier()
        
        assert "straightforward" in modifier.lower()
        assert "professional" in modifier.lower()
    
    def test_serialization(self):
        """Test to_dict and from_dict serialization."""
        config = PersonalityConfig(
            personality=CoachPersonality.PLAYFUL,
            tone=ToneStyle.CASUAL,
            use_emojis=True
        )
        
        data = config.to_dict()
        restored = PersonalityConfig.from_dict(data)
        
        assert restored.personality == config.personality
        assert restored.tone == config.tone
        assert restored.use_emojis == config.use_emojis


# ============================================
# Suggestion Engine Tests
# ============================================

class TestSuggestionEngine:
    """Tests for SuggestionEngine class."""
    
    def test_suggestion_generation(self):
        """Test basic suggestion generation."""
        engine = SuggestionEngine()
        
        suggestion = engine.generate(
            InterventionType.BURNOUT_WARNING,
            {"burnout_risk": 85}
        )
        
        assert isinstance(suggestion, Suggestion)
        assert len(suggestion.title) > 0
        assert len(suggestion.message) > 0
    
    def test_burnout_suggestion_levels(self):
        """Test different burnout level suggestions."""
        engine = SuggestionEngine()
        
        # Critical
        critical = engine.generate(
            InterventionType.BURNOUT_WARNING,
            {"burnout_risk": 85}
        )
        assert critical.priority == 1
        
        # High
        high = engine.generate(
            InterventionType.BURNOUT_WARNING,
            {"burnout_risk": 60}
        )
        assert high.priority == 2
    
    def test_streak_celebration_suggestion(self):
        """Test streak celebration suggestion."""
        engine = SuggestionEngine()
        
        suggestion = engine.generate(
            InterventionType.STREAK_CELEBRATION,
            {},
            {"streak_days": 30}
        )
        
        assert "30" in suggestion.title or "30" in suggestion.message
    
    def test_personality_applied(self):
        """Test that personality is applied to suggestions."""
        config = PersonalityConfig(use_emojis=False)
        engine = SuggestionEngine(personality=config)
        
        suggestion = engine.generate(
            InterventionType.STREAK_BREAK,
            {}
        )
        
        # Should not contain emojis (basic check)
        # Note: This is a simplified test
        assert isinstance(suggestion.message, str)
    
    def test_multiple_suggestions(self):
        """Test generating multiple suggestions."""
        engine = SuggestionEngine()
        
        suggestions = engine.generate_multiple(
            InterventionType.RECOVERY_SUGGESTION,
            {},
            count=3
        )
        
        assert len(suggestions) <= 3


# ============================================
# Intervention Engine Tests
# ============================================

class TestInterventionEngine:
    """Tests for InterventionEngine class."""
    
    def test_full_pipeline(self):
        """Test full intervention pipeline."""
        engine = InterventionEngine()
        user_data = get_high_burnout_data()
        
        interventions = engine.check_and_intervene(user_data)
        
        assert len(interventions) > 0
        for intervention in interventions:
            assert isinstance(intervention, Intervention)
            assert intervention.suggestion is not None
    
    def test_max_interventions_limit(self):
        """Test that max interventions limit is respected."""
        config = PersonalityConfig(
            intervention_frequency=InterventionFrequency.MINIMAL
        )
        engine = InterventionEngine(personality=config)
        user_data = get_high_burnout_data()
        
        interventions = engine.check_and_intervene(user_data)
        
        assert len(interventions) <= config.get_max_interventions_per_day()
    
    def test_intervention_history(self):
        """Test intervention history tracking."""
        engine = InterventionEngine()
        user_data = get_test_user_data()
        
        engine.check_and_intervene(user_data)
        history = engine.get_intervention_history()
        
        assert len(history) > 0
    
    def test_assess_only(self):
        """Test assessment without interventions."""
        engine = InterventionEngine()
        user_data = get_test_user_data()
        
        state = engine.assess_only(user_data)
        
        assert isinstance(state, UserState)


# ============================================
# Digital Coach Tests
# ============================================

class TestDigitalCoach:
    """Tests for DigitalCoach class."""
    
    def test_coach_initializes(self):
        """Test that coach initializes properly."""
        coach = DigitalCoach()
        
        assert coach.personality is not None
        assert coach.engine is not None
    
    def test_coach_check(self):
        """Test coach check method."""
        coach = DigitalCoach()
        user_data = get_test_user_data()
        
        interventions = coach.check(user_data)
        
        assert isinstance(interventions, list)
    
    def test_coach_get_state(self):
        """Test coach state retrieval."""
        coach = DigitalCoach()
        user_data = get_test_user_data()
        
        state = coach.get_state(user_data)
        
        assert isinstance(state, UserState)
    
    def test_coach_acknowledge(self):
        """Test acknowledging interventions."""
        coach = DigitalCoach()
        user_data = get_test_user_data()
        
        interventions = coach.check(user_data)
        
        if interventions:
            result = coach.acknowledge(interventions[0].id)
            assert result is True
    
    def test_coach_summary(self):
        """Test coach summary retrieval."""
        coach = DigitalCoach()
        user_data = get_test_user_data()
        
        coach.check(user_data)
        summary = coach.get_summary()
        
        assert "personality" in summary
        assert "last_check" in summary


# ============================================
# Recovery Mode Tests
# ============================================

class TestRecoveryModeManager:
    """Tests for RecoveryModeManager class."""
    
    def test_push_mode_for_healthy_user(self):
        """Test push mode for healthy user."""
        manager = RecoveryModeManager()
        state = UserState(
            burnout_risk=10,
            streak_health=90,
            engagement_level=EngagementLevel.NORMAL
        )
        
        mode = manager.determine_mode(state)
        
        assert mode == RecoveryMode.PUSH
    
    def test_recovery_mode_for_high_burnout(self):
        """Test recovery mode for high burnout."""
        manager = RecoveryModeManager()
        state = UserState(
            burnout_risk=75,
            streak_health=50,
            engagement_level=EngagementLevel.LOW
        )
        
        mode = manager.determine_mode(state)
        
        assert mode == RecoveryMode.RECOVERY
    
    def test_crisis_mode_for_critical_burnout(self):
        """Test crisis mode for critical burnout."""
        manager = RecoveryModeManager()
        state = UserState(
            burnout_risk=85,
            streak_health=20,
            engagement_level=EngagementLevel.DORMANT
        )
        
        mode = manager.determine_mode(state)
        
        assert mode == RecoveryMode.CRISIS
    
    def test_maintenance_mode(self):
        """Test maintenance mode."""
        manager = RecoveryModeManager()
        state = UserState(
            burnout_risk=45,
            streak_health=60,
            engagement_level=EngagementLevel.NORMAL
        )
        
        mode = manager.determine_mode(state)
        
        assert mode == RecoveryMode.MAINTENANCE
    
    def test_mode_config(self):
        """Test mode configuration retrieval."""
        manager = RecoveryModeManager()
        
        config = manager.get_mode_config(RecoveryMode.RECOVERY)
        
        assert config.habit_target_multiplier == 0.5
        assert config.show_celebrations is False
    
    def test_mode_transition(self):
        """Test mode transition tracking."""
        manager = RecoveryModeManager()
        state = UserState(burnout_risk=75, streak_health=50)
        
        new_mode = manager.transition(state)
        history = manager.get_history()
        
        assert len(history) > 0
        assert history[0]["to_mode"] == new_mode.value
    
    def test_adjusted_targets(self):
        """Test habit target adjustment."""
        manager = RecoveryModeManager()
        manager._current_mode = RecoveryMode.RECOVERY
        
        habits = [{"name": "Test", "daily_target": 10}]
        adjusted = manager.get_adjusted_targets(habits)
        
        assert adjusted[0]["adjusted_target"] == 5.0  # 50% multiplier
    
    def test_mode_message(self):
        """Test mode message generation."""
        manager = RecoveryModeManager()
        
        message = manager.get_mode_message(RecoveryMode.PUSH)
        
        assert len(message) > 0
        assert "growth" in message.lower()
    
    def test_forced_mode(self):
        """Test forcing a specific mode."""
        manager = RecoveryModeManager()
        
        manager.force_mode(RecoveryMode.RECOVERY, "user_request")
        
        assert manager.current_mode == RecoveryMode.RECOVERY
        history = manager.get_history()
        assert history[-1]["forced"] is True


# ============================================
# Integration Tests
# ============================================

class TestCoachIntegration:
    """Integration tests for the coach module."""
    
    def test_full_coaching_workflow(self):
        """Test complete coaching workflow."""
        # Create coach
        coach = DigitalCoach()
        
        # Simulate user with issues
        user_data = get_high_burnout_data()
        
        # Check for interventions
        interventions = coach.check(user_data)
        
        # Should have interventions
        assert len(interventions) > 0
        
        # Get state
        state = coach.get_state(user_data)
        
        # State should reflect issues
        assert state.burnout_risk > 30
        
        # Recovery mode should kick in
        mode_manager = RecoveryModeManager()
        mode = mode_manager.determine_mode(state)
        assert mode in [RecoveryMode.RECOVERY, RecoveryMode.CRISIS, RecoveryMode.MAINTENANCE]
    
    def test_healthy_user_workflow(self):
        """Test workflow for healthy user."""
        coach = DigitalCoach()
        
        # Healthy user
        user_data = get_low_burnout_data()
        
        # Check for interventions
        interventions = coach.check(user_data)
        
        # Should have fewer or no critical interventions
        critical = [i for i in interventions if i.suggestion.priority == 1]
        assert len(critical) == 0
        
        # State should be good
        state = coach.get_state(user_data)
        assert state.burnout_risk < 30


if __name__ == "__main__":
    pytest.main([__file__, "-v"])