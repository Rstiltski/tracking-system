"""
Attachment Theory Integration

Integrate attachment styles into habit formation.

Based on Task 11.3.4 from PHASE_11_INTEGRATION_ROADMAP.md

Attachment styles affect habit formation and partner interactions.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional


# =============================================================================
# TYPES
# =============================================================================

class AttachmentStyle(Enum):
    """Four primary attachment styles."""
    SECURE = "secure"
    ANXIOUS = "anxious"
    AVOIDANT = "avoidant"
    DISORGANIZED = "disorganized"


class TriggerContext(Enum):
    """Contexts that trigger attachment responses."""
    PARTNER_UNAVAILABLE = "partner_unavailable"
    EMOTIONAL_DISTANCE = "emotional_distance"
    DEMANDING_GOALS = "demanding_goals"
    SOCIAL_COMPARISON = "social_comparison"
    FAILURE = "failure"
    SUCCESS = "success"


# =============================================================================
# MODELS
# =============================================================================

@dataclass
class AttachmentProfile:
    """User's attachment profile."""
    id: str
    user_id: str
    
    # Primary style
    primary_style: AttachmentStyle
    
    # Dimensions (0-1)
    anxiety: float  # High = anxious
    avoidance: float  # High = avoidant
    
    # History
    relationship_history: str = ""
    identified_date: Optional[datetime] = None
    
    # Triggers
    known_triggers: List[str] = field(default_factory=list)
    
    # Coping strategies
    secure_strategies: List[str] = field(default_factory=list)
    trigger_responses: Dict[str, str] = field(default_factory=dict)


@dataclass
class AttachmentEvent:
    """An event triggering attachment response."""
    id: str
    user_id: str
    timestamp: datetime
    
    # Context
    trigger: TriggerContext
    context_description: str
    
    # Response
    response_type: str  # What they did
    emotional_state: float  # -1 to 1
    impact: str  # positive, negative, neutral
    
    # Habit impact
    affected_habits: List[str] = field(default_factory=list)


@dataclass
class HabitAttachmentMapping:
    """How attachment style affects specific habits."""
    id: str
    user_id: str
    habit_id: str
    attachment_sensitivity: float
    trigger_contexts: List[TriggerContext]
    pattern_description: str
    recommended_approach: str
    
    def __post_init__(self):
        if isinstance(self.trigger_contexts, list):
            # Keep as-is
            pass


# =============================================================================
# ATTACHMENT-AWARE ENGINE
# =============================================================================

class AttachmentEngine:
    """
    Attachment theory integration.
    
    Features:
    - Profile attachment style
    - Track attachment events
    - Map attachment to habits
    - Suggest secure responses
    """
    
    def __init__(self):
        """Initialize the engine."""
        self.profiles: Dict[str, AttachmentProfile] = {}
        self.events: Dict[str, List[AttachmentEvent]] = {}
        self.habit_mappings: Dict[str, List[HabitAttachmentMapping]] = {}
    
    def create_profile(
        self,
        user_id: str,
        primary_style: AttachmentStyle,
        anxiety: float,
        avoidance: float,
        relationship_history: str = ""
    ) -> AttachmentProfile:
        """Create an attachment profile."""
        import uuid
        
        profile = AttachmentProfile(
            id=str(uuid.uuid4()),
            user_id=user_id,
            primary_style=primary_style,
            anxiety=anxiety,
            avoidance=avoidance,
            relationship_history=relationship_history,
            identified_date=datetime.now()
        )
        
        self.profiles[user_id] = profile
        self.events[user_id] = []
        self.habit_mappings[user_id] = []
        
        # Add default triggers based on style
        self._set_default_triggers(profile)
        
        return profile
    
    def _set_default_triggers(self, profile: AttachmentProfile) -> None:
        """Set default triggers based on attachment style."""
        if profile.primary_style == AttachmentStyle.ANXIOUS:
            profile.known_triggers = [
                "partner takes long to respond",
                "feeling ignored",
                "social media comparison"
            ]
            profile.secure_strategies = [
                "wait before responding",
                "self-soothe first",
                "communicate needs clearly"
            ]
        elif profile.primary_style == AttachmentStyle.AVOIDANT:
            profile.known_triggers = [
                "partner wants more closeness",
                "being asked about feelings",
                "demands for accountability"
            ]
            profile.secure_strategies = [
                "take space before reacting",
                " journal first",
                "explain need for space kindly"
            ]
        elif profile.primary_style == AttachmentStyle.DISORGANIZED:
            profile.known_triggers = [
                "conflict situations",
                "intimacy",
                "being vulnerable"
            ]
            profile.secure_strategies = [
                "pause and breathe",
                "seek neutral third party",
                "grounding techniques"
            ]
        else:  # Secure
            profile.secure_strategies = [
                "open communication",
                "balanced independence",
                "seek support when needed"
            ]
    
    def record_event(
        self,
        user_id: str,
        trigger: TriggerContext,
        context_description: str,
        response_type: str,
        emotional_state: float,
        affected_habits: List[str] = None,
        impact: str = "neutral"
    ) -> AttachmentEvent:
        """Record an attachment event."""
        import uuid
        
        event = AttachmentEvent(
            id=str(uuid.uuid4()),
            user_id=user_id,
            timestamp=datetime.now(),
            trigger=trigger,
            context_description=context_description,
            response_type=response_type,
            emotional_state=emotional_state,
            affected_habits=affected_habits or [],
            impact=impact
        )
        
        self.events[user_id].append(event)
        return event
    
    def get_secure_response_suggestion(
        self,
        user_id: str,
        trigger: TriggerContext
    ) -> str:
        """Get a secure response suggestion."""
        profile = self.profiles.get(user_id)
        if not profile:
            return "Unknown attachment style"
        
        # Map triggers to suggestions
        trigger_map = {
            TriggerContext.PARTNER_UNAVAILABLE: {
                AttachmentStyle.SECURE: "Send a calm message and use time productively",
                AttachmentStyle.ANXIOUS: "Wait 10 minutes before reaching out, practice self-soothing",
                AttachmentStyle.AVOIDANT: "Respect your need for space while maintaining connection",
                AttachmentStyle.DISORGANIZED: "Ground yourself first, then decide on response"
            },
            TriggerContext.FAILURE: {
                AttachmentStyle.SECURE: "Acknowledge setback, plan next step",
                AttachmentStyle.ANXIOUS: "Don't catastrophize - one failure doesn't define you",
                AttachmentStyle.AVOIDANT: "Avoid dismissing feelings - acknowledge and move forward",
                AttachmentStyle.DISORGANIZED: "Safety first - use grounding before processing"
            },
            TriggerContext.DEMANDING_GOALS: {
                AttachmentStyle.SECURE: "Break into smaller steps",
                AttachmentStyle.ANXIOUS: "Don't overextend - set realistic targets",
                AttachmentStyle.AVOIDANT: "Commitment is okay - you don't have to do everything alone",
                AttachmentStyle.DISORGANIZED: "Start small - avoid overwhelm"
            }
        }
        
        return trigger_map.get(trigger, {}).get(
            profile.primary_style,
            "Use your established secure strategies"
        )
    
    def create_habit_mapping(
        self,
        user_id: str,
        habit_id: str,
        attachment_sensitivity: float,
        trigger_contexts: List[TriggerContext],
        pattern_description: str,
        recommended_approach: str
    ) -> HabitAttachmentMapping:
        """Create a habit-attachment mapping."""
        import uuid
        
        mapping = HabitAttachmentMapping(
            id=str(uuid.uuid4()),
            user_id=user_id,
            habit_id=habit_id,
            attachment_sensitivity=attachment_sensitivity,
            trigger_contexts=trigger_contexts,
            pattern_description=pattern_description,
            recommended_approach=recommended_approach
        )
        
        self.habit_mappings[user_id].append(mapping)
        return mapping
    
    def analyze_attachment_habit_impact(self, user_id: str) -> Dict:
        """Analyze how attachment impacts habits."""
        events = self.events.get(user_id, [])
        mappings = self.habit_mappings.get(user_id, [])
        
        # Count by impact
        positive = sum(1 for e in events if e.impact == "positive")
        negative = sum(1 for e in events if e.impact == "negative")
        
        # Find high sensitivity habits
        high_sensitivity = [
            m for m in mappings
            if m.attachment_sensitivity > 0.7
        ]
        
        return {
            "total_events": len(events),
            "positive_responses": positive,
            "negative_responses": negative,
            "high_sensitivity_habits": len(high_sensitivity),
            "sensitivity_habits_detail": [
                {"habit": m.habit_id, "sensitivity": m.attachment_sensitivity}
                for m in high_sensitivity
            ]
        }
    
    def get_profile(self, user_id: str) -> Optional[AttachmentProfile]:
        """Get user's attachment profile."""
        return self.profiles.get(user_id)


def create_engine() -> AttachmentEngine:
    """Factory function."""
    return AttachmentEngine()
