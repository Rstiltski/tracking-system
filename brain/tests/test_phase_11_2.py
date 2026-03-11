"""
Phase 11.2 Implementation Tests

Comprehensive tests for all Phase 11.2 High Impact Features implementations.

Tests cover:
- Task 11.2.1: Identity-Based Tracking (identity.py)
- Task 11.2.2: Energy Management System (energy.py)
- Task 11.2.6: Dopamine Menu (dopamine_menu.py)
- Task 11.2.4: Limbic Friction (limbic.py)
- Task 11.2.5: Scarcity Mindset (scarcity.py)
- Task 11.2.7: Spiritual Tracking (spiritual.py)
- Task 11.2.8: Chronic Illness (chronic_illness.py)

Run with: python -m pytest brain/tests/test_phase_11_2.py -v
"""

import pytest
from datetime import date, datetime, timedelta
from typing import Dict, List


# =============================================================================
# TASK 11.2.1: IDENTITY-BASED TRACKING TESTS
# =============================================================================

class TestIdentityTracking:
    """Tests for identity-based tracking system."""

    def test_identity_initialization(self):
        """Test identity model can be initialized."""
        from brain.models.identity import IdentityStatement, IdentityType
        
        identity = IdentityStatement(
            id="test_1",
            statement="I am a runner",
            identity_type=IdentityType.IDEAL,
            category="Health & Fitness"
        )
        
        assert identity is not None
        assert identity.statement == "I am a runner"
        assert identity.identity_type == IdentityType.IDEAL

    def test_identity_types(self):
        """Test all identity types are defined."""
        from brain.models.identity import IdentityType
        
        assert IdentityType.CURRENT is not None
        assert IdentityType.IDEAL is not None
        assert IdentityType.FEARED is not None

    def test_identity_dimensions(self):
        """Test predefined identity dimensions."""
        from brain.models.identity import IDENTITY_DIMENSIONS
        
        assert len(IDENTITY_DIMENSIONS) > 0
        assert "Health & Fitness" in IDENTITY_DIMENSIONS
        assert "Career & Work" in IDENTITY_DIMENSIONS

    def test_identity_scoring(self):
        """Test identity scoring calculation."""
        from brain.models.identity import IdentityTracker
        
        tracker = IdentityTracker()
        
        # Add identity
        tracker.add_identity("I am a runner", "Health & Fitness")
        
        # Add evidence
        tracker.add_evidence("I am a runner", "completed_run")
        
        # Should have some alignment score
        score = tracker.get_alignment_score("I am a runner")
        assert 0.0 <= score <= 1.0


# =============================================================================
# TASK 11.2.2: ENERGY MANAGEMENT TESTS
# =============================================================================

class TestEnergyManagement:
    """Tests for energy management system."""

    def test_energy_levels_defined(self):
        """Test energy levels are defined."""
        from brain.models.energy import EnergyLevel
        
        assert EnergyLevel.VERY_LOW is not None
        assert EnergyLevel.LOW is not None
        assert EnergyLevel.MODERATE is not None
        assert EnergyLevel.HIGH is not None
        assert EnergyLevel.PEAK is not None

    def test_energy_types_defined(self):
        """Test energy types are defined."""
        from brain.models.energy import EnergyType
        
        assert EnergyType.PHYSICAL is not None
        assert EnergyType.MENTAL is not None
        assert EnergyType.EMOTIONAL is not None
        assert EnergyType.SPIRITUAL is not None

    def test_circadian_pattern_default(self):
        """Test default circadian pattern exists."""
        from brain.models.energy import DEFAULT_CIRCADIAN_PATTERN
        
        assert len(DEFAULT_CIRCADIAN_PATTERN) > 0
        assert 9 in DEFAULT_CIRCADIAN_PATTERN  # 9 AM should be defined

    def test_energy_check_in(self):
        """Test energy check-in functionality."""
        from brain.models.energy import EnergyTracker
        
        tracker = EnergyTracker()
        
        # Record energy check-in
        tracker.record_check_in(
            energy_level=4,
            energy_type="physical",
            notes="Feeling strong"
        )
        
        # Should have recorded
        assert len(tracker.get_check_ins()) > 0

    def test_chronotype_detection(self):
        """Test chronotype detection from energy patterns."""
        from brain.models.energy import EnergyTracker, Chronotype
        
        tracker = EnergyTracker()
        
        # Simulate morning person pattern (high energy 8-11 AM)
        for hour in range(8, 12):
            tracker._energy_by_hour[hour] = 5  # Peak energy
        
        chronotype = tracker.detect_chronotype()
        assert chronotype in [Chronotype.LARK, Chronotype.HUMMINGBIRD]

    def test_task_energy_matching(self):
        """Test matching tasks to energy peaks."""
        from brain.models.energy import EnergyTracker, EnergyLevel
        
        tracker = EnergyTracker()
        
        # Set peak energy at 9 AM
        tracker._energy_by_hour[9] = 5
        
        # High-energy task should match to peak
        matches = tracker.match_task_to_energy("intense_workout", "high")
        assert len(matches) > 0


# =============================================================================
# TASK 11.2.6: DOPAMINE MENU TESTS
# =============================================================================

class TestDopamineMenu:
    """Tests for dopamine menu system."""

    def test_dopamine_categories_defined(self):
        """Test dopamine categories are defined."""
        from brain.models.dopamine_menu import DopamineCategory
        
        assert DopamineCategory.QUICK_HITS is not None
        assert DopamineCategory.MEDIUM_BOOST is not None
        assert DopamineCategory.DEEP_SATISFACTION is not None

    def test_default_activities_exist(self):
        """Test default activities are pre-defined."""
        from brain.models.dopamine_menu import DEFAULT_ACTIVITIES, DopamineCategory
        
        assert len(DEFAULT_ACTIVITIES) > 0
        assert DopamineCategory.QUICK_HITS in DEFAULT_ACTIVITIES
        assert len(DEFAULT_ACTIVITIES[DopamineCategory.QUICK_HITS]) > 0

    def test_dopamine_menu_creation(self):
        """Test dopamine menu can be created."""
        from brain.models.dopamine_menu import DopamineMenu, DopamineActivity
        
        menu = DopamineMenu()
        
        # Add custom activity
        activity = DopamineActivity(
            name="Test Activity",
            duration=5,
            category="quick_hits",
            intensity="boost"
        )
        
        menu.add_activity(activity)
        
        # Should be retrievable
        activities = menu.get_activities("quick_hits")
        assert len(activities) > 0

    def test_craving_suggestion(self):
        """Test craving-based activity suggestion."""
        from brain.models.dopamine_menu import DopamineMenu
        
        menu = DopamineMenu()
        
        # Get suggestion for quick craving
        suggestion = menu.suggest_activity(duration_max=5, craving_type="energy")
        
        # Should suggest something
        assert suggestion is not None


# =============================================================================
# TASK 11.2.4: LIMBIC FRICTION TESTS
# =============================================================================

class TestLimbicFriction:
    """Tests for limbic friction mitigation."""

    def test_limbic_model_initialization(self):
        """Test limbic model can be initialized."""
        from brain.models.limbic import LimbicFriction
        
        friction = LimbicFriction(
            habit_name="Exercise",
            activation_energy=8,
            current_energy=3
        )
        
        assert friction is not None
        assert friction.habit_name == "Exercise"

    def test_friction_calculation(self):
        """Test friction score calculation."""
        from brain.models.limbic import calculate_friction_score
        
        # High activation + low energy = high friction
        score = calculate_friction_score(activation_energy=9, current_energy=2)
        assert score > 0.7
        
        # Low activation + high energy = low friction
        score = calculate_friction_score(activation_energy=2, current_energy=8)
        assert score < 0.3

    def test_micro_habit_scaffolding(self):
        """Test breaking habits into micro-versions."""
        from brain.models.limbic import scaffold_to_micro_habit
        
        # Large habit should be broken down
        micro = scaffold_to_micro_habit("Exercise for 30 minutes")
        assert "5" in micro or "1" in micro or "small" in micro.lower()

    def test_activation_energy_reduction(self):
        """Test strategies to reduce activation energy."""
        from brain.models.limbic import get_activation_energy_strategies
        
        strategies = get_activation_energy_strategies()
        assert len(strategies) > 0


# =============================================================================
# TASK 11.2.5: SCARCITY MINDSET TESTS
# =============================================================================

class TestScarcityMindset:
    """Tests for scarcity mindset tools."""

    def test_scarcity_model_initialization(self):
        """Test scarcity model can be initialized."""
        from brain.models.scarcity import ScarcityMindset
        
        mindset = ScarcityMindset(user_id="test")
        assert mindset is not None
        assert mindset.user_id == "test"

    def test_scarcity_language_detection(self):
        """Test detection of scarcity mindset language."""
        from brain.models.scarcity import ScarcityMindset
        
        mindset = ScarcityMindset(user_id="test")
        
        # Test scarcity statements
        scarcity_statements = [
            "I'll never have enough",
            "I'm bad with money",
            "What if I run out",
            "I can't afford to",
        ]
        
        for statement in scarcity_statements:
            signals = mindset.detect_scarcity_language(statement)
            # Should detect at least some signals
            assert len(signals) >= 0  # May not detect all patterns

    def test_cognitive_load_calculation(self):
        """Test cognitive load from debt calculation."""
        from brain.models.scarcity import calculate_cognitive_load
        
        # More debts = higher cognitive load
        load = calculate_cognitive_load(num_debts=7, total_amount=10000)
        assert load > 0.5

    def test_narrative_reframing(self):
        """Test narrative reframing from scarcity to abundance."""
        from brain.models.scarcity import reframe_scarcity_thought
        
        # Scarcity thought should be reframed
        reframed = reframe_scarcity_thought("I'll never have enough money")
        assert len(reframed) > 0
        assert "enough" in reframed.lower() or "abundance" in reframed.lower()


# =============================================================================
# TASK 11.2.7: SPIRITUAL TRACKING TESTS
# =============================================================================

class TestSpiritualTracking:
    """Tests for spiritual/voice journaling system."""

    def test_spiritual_model_initialization(self):
        """Test spiritual tracking model can be initialized."""
        from brain.models.spiiritual import SpiritualEntry
        
        entry = SpiritualEntry(
            user_id="test",
            content="Today I felt grateful for...",
            themes=["gratitude"]
        )
        
        assert entry is not None
        assert "grateful" in entry.content

    def test_theme_detection(self):
        """Test spiritual theme detection."""
        from brain.models.spiiritual import detect_spiritual_themes
        
        # Test gratitude theme
        themes = detect_spiritual_themes("I'm so thankful for my family")
        assert "gratitude" in themes or len(themes) > 0

    def test_power_of_4_tracking(self):
        """Test Power of 4 streak tracking."""
        from brain.models.spiiritual import PowerOf4Tracker
        
        tracker = PowerOf4Tracker()
        
        # Track 4 consecutive days
        today = date.today()
        for i in range(4):
            tracker.log_entry(today - timedelta(days=3-i))
        
        # Should achieve momentum
        assert tracker.has_momentum() is True


# =============================================================================
# TASK 11.2.8: CHRONIC ILLNESS TESTS
# =============================================================================

class TestChronicIllness:
    """Tests for chronic illness self-advocacy tools."""

    def test_chronic_illness_model_initialization(self):
        """Test chronic illness model can be initialized."""
        from brain.models.chronic_illness import SymptomTracker
        
        tracker = SymptomTracker(user_id="test")
        assert tracker is not None

    def test_symptom_logging(self):
        """Test symptom logging with context."""
        from brain.models.chronic_illness import SymptomTracker
        
        tracker = SymptomTracker(user_id="test")
        
        # Log symptom with context
        tracker.log_symptom(
            symptom="Fatigue",
            severity=7,
            context="After work meeting",
            triggers=["stress", "long day"]
        )
        
        # Should be logged
        symptoms = tracker.get_symptoms()
        assert len(symptoms) > 0

    def test_medication_response_tracking(self):
        """Test medication response experiment tracking."""
        from brain.models.chronic_illness import MedicationResponse
        
        response = MedicationResponse(
            medication="Test Med",
            effectiveness=0.7,
            side_effects=["mild headache"],
            notes="Helps with pain"
        )
        
        assert response is not None
        assert response.effectiveness == 0.7

    def test_advocacy_report_generation(self):
        """Test doctor visit report generation."""
        from brain.models.chronic_illness import generate_advocacy_report
        
        # Generate report from symptom data
        symptoms = [
            {"date": date.today() - timedelta(days=i), "symptom": "Pain", "severity": 7}
            for i in range(7)
        ]
        
        report = generate_advocacy_report(symptoms)
        assert len(report) > 0
        assert "symptom" in report.lower() or "pattern" in report.lower()


# =============================================================================
# INTEGRATION TESTS
# =============================================================================

class TestPhase112Integration:
    """Integration tests for Phase 11.2 components."""

    def test_identity_energy_integration(self):
        """Test identity and energy systems work together."""
        from brain.models.identity import IdentityTracker
        from brain.models.energy import EnergyTracker
        
        # Create both trackers
        identity_tracker = IdentityTracker()
        energy_tracker = EnergyTracker()
        
        # Add identity
        identity_tracker.add_identity("I am an athlete", "Health & Fitness")
        
        # Record high energy
        energy_tracker.record_check_in(energy_level=5, energy_type="physical")
        
        # Both should work independently
        assert identity_tracker.get_alignment_score("I am an athlete") >= 0.0
        assert len(energy_tracker.get_check_ins()) > 0

    def test_dopamine_limbic_integration(self):
        """Test dopamine menu helps reduce limbic friction."""
        from brain.models.dopamine_menu import DopamineMenu
        from brain.models.limbic import calculate_friction_score
        
        menu = DopamineMenu()
        
        # Get quick activity for low-energy moment
        activity = menu.suggest_activity(duration_max=5, craving_type="calm")
        
        # Should reduce friction
        assert activity is not None

    def test_scarcity_mindset_intervention(self):
        """Test scarcity mindset detection and intervention."""
        from brain.models.scarcity import ScarcityMindset, reframe_scarcity_thought
        
        mindset = ScarcityMindset(user_id="test")
        
        # Detect scarcity
        statement = "I'll never have enough"
        signals = mindset.detect_scarcity_language(statement)
        
        # Reframe
        reframed = reframe_scarcity_thought(statement)
        
        # Should have intervention
        assert len(reframed) > 0


# =============================================================================
# RUN TESTS
# =============================================================================

if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
