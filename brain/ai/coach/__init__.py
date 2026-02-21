"""
Brain AI Coach - Digital Coach Module

The Digital Coach is a proactive AI that monitors user data, detects patterns
and anomalies, and intervenes with suggestions before problems occur.

Components:
- InterventionEngine: Core intervention logic
- UserAssessment: Evaluate user state across dimensions
- SuggestionEngine: Generate actionable suggestions
- RecoveryMode: Adaptive coaching based on user state
- Rules: Intervention trigger rules
- Personality: Coach personality configuration

Usage:
    from brain.ai.coach import DigitalCoach, CoachPersonality
    
    coach = DigitalCoach(personality=CoachPersonality.ENCOURAGING)
    interventions = coach.check_and_intervene(user_data)
"""

from brain.ai.coach.personality import CoachPersonality, PersonalityConfig
from brain.ai.coach.user_assessment import UserAssessment, UserState
from brain.ai.coach.rules import InterventionRule, RuleEngine
from brain.ai.coach.suggestion_engine import SuggestionEngine
from brain.ai.coach.intervention_engine import InterventionEngine, Intervention, DigitalCoach
from brain.ai.coach.recovery_mode import RecoveryMode, RecoveryModeManager

__all__ = [
    "DigitalCoach",
    "CoachPersonality",
    "PersonalityConfig",
    "UserAssessment",
    "UserState",
    "InterventionRule",
    "RuleEngine",
    "SuggestionEngine",
    "InterventionEngine",
    "Intervention",
    "RecoveryMode",
    "RecoveryModeManager",
]
