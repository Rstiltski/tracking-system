"""
Social Comparison Safeguards

Prevent harmful social comparison. Focus on self-progress.

Based on Task 11.2.12 from PHASE_11_INTEGRATION_ROADMAP.md

Prevents harm from social comparison!
"""

from dataclasses import dataclass, field
from datetime import datetime, date
from enum import Enum
from typing import Dict, List, Optional


# =============================================================================
# TYPES
# =============================================================================

class ComparisonType(Enum):
    """Types of social comparison."""
    UPWARD = "upward"       # Comparing to "better" others
    DOWNWARD = "downward"   # Comparing to "worse" others
    LATERAL = "lateral"     # Comparing to "equal" others


class TriggerSource(Enum):
    """Sources of comparison triggers."""
    SOCIAL_MEDIA = "social_media"
    FRIENDS = "friends"
    FAMILY = "family"
    WORK = "work"
    MEDIA = "media"
    INTERNAL = "internal"  # Self-generated


# =============================================================================
# MODELS
# =============================================================================

@dataclass
class ComparisonEvent:
    """A social comparison event."""
    id: str
    user_id: str
    timestamp: datetime
    comparison_type: ComparisonType
    trigger_source: TriggerSource
    trigger_content: str  # What triggered it
    
    # Impact
    mood_before: int  # 1-10
    mood_after: int  # 1-10
    impact_score: int  # -5 to +5
    
    # Intervention
    intervention_applied: bool = False
    intervention_type: Optional[str] = None


@dataclass
class PersonalBest:
    """A personal best record."""
    id: str
    user_id: str
    metric: str
    value: float
    achieved_at: datetime
    context: str


# =============================================================================
# SOCIAL COMPARISON SAFEGUARDS ENGINE
# =============================================================================

class SocialSafeguardsEngine:
    """
    Manages social comparison safeguards.
    
    Features:
    - Comparison event tracking
    - Mood impact analysis
    - Intervention suggestions
    - Personal best focus
    """
    
    def __init__(self):
        """Initialize the engine."""
        self.events: List[ComparisonEvent] = []
        self.personal_bests: List[PersonalBest] = []
    
    def record_comparison(
        self,
        user_id: str,
        comparison_type: ComparisonType,
        trigger_source: TriggerSource,
        trigger_content: str,
        mood_before: int,
        mood_after: int
    ) -> ComparisonEvent:
        """Record a comparison event."""
        import uuid
        
        impact = mood_after - mood_before
        
        event = ComparisonEvent(
            id=str(uuid.uuid4()),
            user_id=user_id,
            timestamp=datetime.now(),
            comparison_type=comparison_type,
            trigger_source=trigger_source,
            trigger_content=trigger_content,
            mood_before=mood_before,
            mood_after=mood_after,
            impact_score=impact
        )
        
        self.events.append(event)
        return event
    
    def apply_intervention(
        self,
        event_id: str,
        intervention_type: str
    ) -> None:
        """Apply an intervention to a comparison event."""
        for event in self.events:
            if event.id == event_id:
                event.intervention_applied = True
                event.intervention_type = intervention_type
                break
    
    def add_personal_best(
        self,
        user_id: str,
        metric: str,
        value: float,
        context: str
    ) -> PersonalBest:
        """Record a personal best."""
        import uuid
        
        pb = PersonalBest(
            id=str(uuid.uuid4()),
            user_id=user_id,
            metric=metric,
            value=value,
            achieved_at=datetime.now(),
            context=context
        )
        
        self.personal_bests.append(pb)
        return pb
    
    def get_interventions(self, comparison_type: ComparisonType) -> List[str]:
        """Get intervention suggestions for comparison type."""
        interventions = {
            ComparisonType.UPWARD: [
                "🎯 Focus on YOUR progress, not others' outcomes",
                "📊 Compare your today to your yesterday",
                "💡 What can you learn from them?",
                "🌟 Everyone's journey is different",
                "⏰ Focus on long-term, not short-term"
            ],
            ComparisonType.DOWNWARD: [
                "🙌 Great! Use this to build confidence",
                "💪 Remember - you started somewhere too",
                "🤝 Offer help if you can",
                "🌱 Growth is what matters"
            ],
            ComparisonType.LATERAL: [
                "🤔 What can you collaborate on?",
                "💪 You're on similar paths - support each other",
                "🌟 Focus on your unique strengths"
            ]
        }
        
        return interventions.get(comparison_type, ["Focus on your journey"])
    
    def get_recent_events(
        self, 
        user_id: str, 
        days: int = 30
    ) -> List[ComparisonEvent]:
        """Get recent comparison events."""
        from datetime import timedelta
        
        cutoff = datetime.now() - timedelta(days=days)
        
        return [
            e for e in self.events
            if e.user_id == user_id and e.timestamp >= cutoff
        ]
    
    def get_stats(self, user_id: str) -> Dict:
        """Get comparison statistics."""
        events = self.get_recent_events(user_id)
        
        if not events:
            return {
                "total_events": 0,
                "avg_mood_impact": 0,
                "most_common_trigger": None,
                "interventions_used": 0
            }
        
        # Mood impact
        avg_impact = sum(e.impact_score for e in events) / len(events)
        
        # Most common trigger
        trigger_counts = {}
        for e in events:
            trigger_counts[e.trigger_source.value] = trigger_counts.get(e.trigger_source.value, 0) + 1
        
        most_common = max(trigger_counts, key=trigger_counts.get) if trigger_counts else None
        
        # Interventions
        interventions = sum(1 for e in events if e.intervention_applied)
        
        return {
            "total_events": len(events),
            "avg_mood_impact": avg_impact,
            "most_common_trigger": most_common,
            "interventions_used": interventions,
            "personal_bests": len([pb for pb in self.personal_bests if pb.user_id == user_id])
        }


def create_engine() -> SocialSafeguardsEngine:
    """Factory function."""
    return SocialSafeguardsEngine()
