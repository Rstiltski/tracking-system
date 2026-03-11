"""
Scarcity Mindset Tools

Tools to counter scarcity thinking and financial anxiety.

Based on Task 11.2.5 from PHASE_11_INTEGRATION_ROADMAP.md

Financial anxiety is a major blocker!
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from enum import Enum
from typing import Dict, List, Optional


# =============================================================================
# TYPES
# =============================================================================

class ScarcityTrigger(Enum):
    """Triggers for scarcity thinking."""
    TIME = "time"           # "I don't have enough time"
    MONEY = "money"         # "I can't afford it"
    ENERGY = "energy"       # "I'm too tired"
    OPPORTUNITY = "opportunity"  # "It's now or never"
    RESOURCES = "resources"  # "I don't have the tools"


class AbundanceReframe(Enum):
    """Abundance reframes for scarcity thoughts."""
    TIME = "Time is abundant - I can create more"
    MONEY = "Money flows to me - I can earn more"
    ENERGY = "Energy is renewable - I can rest and restore"
    OPPORTUNITY = "Opportunities are everywhere - I create my own"
    RESOURCES = "Resources are abundant - I can be creative"


# =============================================================================
# MODELS
# =============================================================================

@dataclass
class ScarcityThought:
    """A scarcity thought recorded."""
    id: str
    user_id: str
    timestamp: datetime
    trigger: ScarcityTrigger
    thought: str
    intensity: int  # 1-10
    
    # Reframing
    reframe: Optional[str] = None
    reframe_applied: bool = False
    
    # Result
    resolved: bool = False
    resolution_note: Optional[str] = None


@dataclass
class AbundancePractice:
    """An abundance-building practice."""
    id: str
    user_id: str
    practice_type: str
    description: str
    completed_at: datetime
    impact_score: int = 1  # How much it helped


# =============================================================================
# SCARCITY MINDSET ENGINE
# =============================================================================

class ScarcityEngine:
    """
    Manages scarcity mindset interventions.
    
    Features:
    - Scarcity thought tracking
    - Automatic reframe suggestions
    - Abundance practice logging
    - Progress tracking
    """
    
    def __init__(self):
        """Initialize the engine."""
        self.thoughts: List[ScarcityThought] = []
        self.practices: List[AbundancePractice] = []
        
        # Mapping of triggers to reframe
        self.reframe_map = {
            ScarcityTrigger.TIME: AbundanceReframe.TIME.value,
            ScarcityTrigger.MONEY: AbundanceReframe.MONEY.value,
            ScarcityTrigger.ENERGY: AbundanceReframe.ENERGY.value,
            ScarcityTrigger.OPPORTUNITY: AbundanceReframe.OPPORTUNITY.value,
            ScarcityTrigger.RESOURCES: AbundanceReframe.RESOURCES.value,
        }
    
    def record_thought(
        self,
        user_id: str,
        trigger: ScarcityTrigger,
        thought: str,
        intensity: int = 5
    ) -> ScarcityThought:
        """Record a scarcity thought."""
        import uuid
        
        scarcity_thought = ScarcityThought(
            id=str(uuid.uuid4()),
            user_id=user_id,
            timestamp=datetime.now(),
            trigger=trigger,
            thought=thought,
            intensity=intensity,
            reframe=self.reframe_map.get(trigger)
        )
        
        self.thoughts.append(scarcity_thought)
        return scarcity_thought
    
    def apply_reframe(
        self,
        thought_id: str,
        resolution_note: Optional[str] = None
    ) -> None:
        """Apply reframe to a thought."""
        for thought in self.thoughts:
            if thought.id == thought_id:
                thought.reframe_applied = True
                thought.resolved = True
                thought.resolution_note = resolution_note
                break
    
    def log_practice(
        self,
        user_id: str,
        practice_type: str,
        description: str,
        impact_score: int = 3
    ) -> AbundancePractice:
        """Log an abundance-building practice."""
        import uuid
        
        practice = AbundancePractice(
            id=str(uuid.uuid4()),
            user_id=user_id,
            practice_type=practice_type,
            description=description,
            completed_at=datetime.now(),
            impact_score=impact_score
        )
        
        self.practices.append(practice)
        return practice
    
    def get_thoughts(
        self, 
        user_id: str, 
        days: int = 30
    ) -> List[ScarcityThought]:
        """Get recent scarcity thoughts."""
        from datetime import timedelta
        
        cutoff = datetime.now() - timedelta(days=days)
        
        return [
            t for t in self.thoughts
            if t.user_id == user_id and t.timestamp >= cutoff
        ]
    
    def get_stats(self, user_id: str) -> Dict:
        """Get scarcity mindset stats."""
        thoughts = self.get_thoughts(user_id)
        practices = [
            p for p in self.practices
            if p.user_id == user_id
        ]
        
        # Trigger breakdown
        trigger_counts = {}
        for t in thoughts:
            trigger_counts[t.trigger.value] = trigger_counts.get(t.trigger.value, 0) + 1
        
        # Resolution rate
        resolved = sum(1 for t in thoughts if t.resolved)
        resolution_rate = resolved / len(thoughts) if thoughts else 0
        
        return {
            "total_thoughts": len(thoughts),
            "resolved": resolved,
            "resolution_rate": resolution_rate,
            "practices_completed": len(practices),
            "trigger_breakdown": trigger_counts,
            "avg_intensity": sum(t.intensity for t in thoughts) / len(thoughts) if thoughts else 0
        }
    
    def get_abundance_suggestions(self, trigger: ScarcityTrigger) -> List[str]:
        """Get abundance-building suggestions for a trigger."""
        suggestions = {
            ScarcityTrigger.TIME: [
                "Schedule 'creative time' - 30 mins of uninterrupted work",
                "Time-block your most important task",
                "Say no to one thing to say yes to what matters"
            ],
            ScarcityTrigger.MONEY: [
                "List 3 things you're grateful for that money can't buy",
                "Create a 'small win' money goal",
                "Practice visualize abundance flowing to you"
            ],
            ScarcityTrigger.ENERGY: [
                "Take a 10-minute walk",
                "Do 5 minutes of deep breathing",
                "Rest without guilt - it's productive"
            ],
            ScarcityTrigger.OPPORTUNITY: [
                "Remember: This isn't the only opportunity",
                "Create your own opportunity",
                "Trust that better matches are coming"
            ],
            ScarcityTrigger.RESOURCES: [
                "What would you do with unlimited resources? Start small.",
                "Borrow, trade, or rent instead of buy",
                "Get creative with what you have"
            ]
        }
        
        return suggestions.get(trigger, ["Practice gratitude"])


def create_engine() -> ScarcityEngine:
    """Factory function."""
    return ScarcityEngine()
