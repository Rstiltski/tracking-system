"""
Identity Reconstruction Tools

Support users through identity transitions.

Based on Task 11.3.2 from PHASE_11_INTEGRATION_ROADMAP.md

Supporting identity change - career change, new parent, recovery, etc.
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional


# =============================================================================
# TYPES
# =============================================================================

class TransitionType(Enum):
    """Types of life transitions."""
    CAREER_CHANGE = "career_change"
    NEW_PARENTHOOD = "new_parenthood"
    RELATIONSHIP_CHANGE = "relationship_change"
    RECOVERY = "recovery"
    RETIREMENT = "retirement"
    HEALTH_CHALLENGE = "health_challenge"
    LOCATION_CHANGE = "location_change"
    SPIRITUAL_AWAKENING = "spiritual_awakening"
    AGING = "aging"
    CUSTOM = "custom"


class IdentityStage(Enum):
    """Stages of identity reconstruction."""
    DENIAL = "denial"
    RESISTANCE = "resistance"
    EXPLORATION = "exploration"
    INTEGRATION = "integration"
    EMBRACING = "embracing"


# =============================================================================
# MODELS
# =============================================================================

@dataclass
class IdentityTransition:
    """A major life transition."""
    id: str
    user_id: str
    name: str
    transition_type: TransitionType
    
    # Description
    description: str
    old_identity: str  # Who they were
    new_identity: str  # Who they're becoming
    
    # Timeline
    start_date: datetime
    target_date: Optional[datetime] = None
    
    # Stage
    current_stage: IdentityStage = IdentityStage.DENIAL
    
    # Tracking
    milestones: List[str] = field(default_factory=list)
    old_habits_to_release: List[str] = field(default_factory=list)
    new_habits_to_form: List[str] = field(default_factory=list)


@dataclass
class IdentityNarrative:
    """A narrative about self-identity."""
    id: str
    user_id: str
    transition_id: str
    timestamp: datetime
    narrative: str
    emotional_valence: float  # -1 to 1
    confidence: float  # 0 to 1


@dataclass
class HabitPattern:
    """A habit pattern from old identity that may need releasing."""
    id: str
    user_id: str
    transition_id: str
    habit_name: str
    old_pattern: str  # How it served old identity
    new_pattern: str  # How it conflicts with new identity
    release_difficulty: int  # 1-10
    is_released: bool = False


# =============================================================================
# IDENTITY RECONSTRUCTION ENGINE
# =============================================================================

class IdentityReconstructionEngine:
    """
    Identity reconstruction tools.
    
    Features:
    - Track major life transitions
    - Monitor identity narratives
    - Identify old habit patterns
    - Support through stages
    """
    
    def __init__(self):
        """Initialize the engine."""
        self.transitions: Dict[str, IdentityTransition] = {}
        self.narratives: Dict[str, List[IdentityNarrative]] = {}
        self.habit_patterns: Dict[str, List[HabitPattern]] = {}
    
    def create_transition(
        self,
        user_id: str,
        name: str,
        transition_type: TransitionType,
        description: str,
        old_identity: str,
        new_identity: str,
        start_date: datetime,
        target_date: Optional[datetime] = None
    ) -> IdentityTransition:
        """Create a new identity transition."""
        import uuid
        
        transition = IdentityTransition(
            id=str(uuid.uuid4()),
            user_id=user_id,
            name=name,
            transition_type=transition_type,
            description=description,
            old_identity=old_identity,
            new_identity=new_identity,
            start_date=start_date,
            target_date=target_date
        )
        
        self.transitions[transition.id] = transition
        self.narratives[transition.id] = []
        self.habit_patterns[transition.id] = []
        
        return transition
    
    def update_stage(
        self,
        transition_id: str,
        new_stage: IdentityStage
    ) -> None:
        """Update the current stage."""
        transition = self.transitions.get(transition_id)
        if transition:
            transition.current_stage = new_stage
    
    def add_milestone(
        self,
        transition_id: str,
        milestone: str
    ) -> None:
        """Add a milestone."""
        transition = self.transitions.get(transition_id)
        if transition:
            transition.milestones.append(milestone)
    
    def record_narrative(
        self,
        user_id: str,
        transition_id: str,
        narrative: str,
        emotional_valence: float,
        confidence: float
    ) -> IdentityNarrative:
        """Record an identity narrative."""
        import uuid
        
        story = IdentityNarrative(
            id=str(uuid.uuid4()),
            user_id=user_id,
            transition_id=transition_id,
            timestamp=datetime.now(),
            narrative=narrative,
            emotional_valence=emotional_valence,
            confidence=confidence
        )
        
        self.narratives[transition_id].append(story)
        return story
    
    def add_habit_pattern(
        self,
        user_id: str,
        transition_id: str,
        habit_name: str,
        old_pattern: str,
        new_pattern: str,
        release_difficulty: int
    ) -> HabitPattern:
        """Add an old habit pattern to release."""
        import uuid
        
        pattern = HabitPattern(
            id=str(uuid.uuid4()),
            user_id=user_id,
            transition_id=transition_id,
            habit_name=habit_name,
            old_pattern=old_pattern,
            new_pattern=new_pattern,
            release_difficulty=release_difficulty
        )
        
        self.habit_patterns[transition_id].append(pattern)
        return pattern
    
    def mark_habit_released(self, pattern_id: str) -> None:
        """Mark a habit as released."""
        for patterns in self.habit_patterns.values():
            for p in patterns:
                if p.id == pattern_id:
                    p.is_released = True
                    return
    
    def get_progress_report(self, transition_id: str) -> Dict:
        """Get a progress report."""
        transition = self.transitions.get(transition_id)
        if not transition:
            return {}
        
        narratives = self.narratives.get(transition_id, [])
        patterns = self.habit_patterns.get(transition_id, [])
        
        # Calculate emotional trend
        if narratives:
            emotions = [n.emotional_valence for n in narratives]
            avg_emotion = sum(emotions) / len(emotions)
            emotion_trend = "improving" if emotions[-1] > emotions[0] else "stable"
        else:
            avg_emotion = 0
            emotion_trend = "unknown"
        
        # Calculate release progress
        total_patterns = len(patterns)
        released = sum(1 for p in patterns if p.is_released)
        
        # Stage progress
        stage_order = list(IdentityStage)
        current_idx = stage_order.index(transition.current_stage)
        stage_progress = (current_idx + 1) / len(stage_order) * 100
        
        return {
            "transition_name": transition.name,
            "current_stage": transition.current_stage.value,
            "stage_progress_pct": stage_progress,
            "milestones_count": len(transition.milestones),
            "old_habits_tracked": total_patterns,
            "habits_released": released,
            "habit_release_pct": (released / total_patterns * 100) if total_patterns > 0 else 0,
            "narratives_count": len(narratives),
            "avg_emotional_valence": avg_emotion,
            "emotion_trend": emotion_trend,
            "old_identity": transition.old_identity,
            "new_identity": transition.new_identity
        }
    
    def get_user_transitions(self, user_id: str) -> List[IdentityTransition]:
        """Get all transitions for a user."""
        return [
            t for t in self.transitions.values()
            if t.user_id == user_id
        ]


def create_engine() -> IdentityReconstructionEngine:
    """Factory function."""
    return IdentityReconstructionEngine()
