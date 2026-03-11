"""
Limbic Friction Mitigation

Reduce the "activation energy" needed to start tasks.

Based on Task 11.2.4 from PHASE_11_INTEGRATION_ROADMAP.md

Reduces activation energy - makes starting easier!
"""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Dict, List, Optional


# =============================================================================
# TYPES
# =============================================================================

class FrictionType(Enum):
    """Types of friction."""
    EMOTIONAL = "emotional"       # Fear, anxiety
    COGNITIVE = "cognitive"       # Overthinking
    MOTIVATIONAL = "motivational" # Lack of drive
    PHYSICAL = "physical"        # Physical resistance


class StrategyType(Enum):
    """Strategies to reduce friction."""
    MICROTASK = "microtask"           # Break into tiny steps
    ENVIRONMENT = "environment"        # Make it easy
    MINDFUL = "mindful"             # Breathing, presence
    REFRAME = "reframe"             # Change perspective
    COMMITMENT = "commitment"       # Public commitment


# =============================================================================
# MODELS
# =============================================================================

@dataclass
class FrictionEvent:
    """A friction event when trying to start."""
    id: str
    user_id: str
    timestamp: datetime
    task_name: str
    friction_type: FrictionType
    intensity: int  # 1-10
    
    # How it was resolved
    resolved: bool = False
    strategy_used: Optional[StrategyType] = None
    time_to_start_seconds: Optional[int] = None


@dataclass
class Strategy:
    """A friction-reducing strategy."""
    id: str
    name: str
    description: str
    friction_types: List[FrictionType]
    effectiveness: int  # 1-5


# =============================================================================
# LIMBIC FRICTION ENGINE
# =============================================================================

class LimbicFrictionEngine:
    """
    Reduces limbic friction - the mental resistance to starting tasks.
    
    Features:
    - Friction detection
    - Strategy recommendations
    - Effectiveness tracking
    - Pattern analysis
    """
    
    def __init__(self):
        """Initialize the engine."""
        self.events: List[FrictionEvent] = []
        self._init_strategies()
    
    def _init_strategies(self):
        """Initialize strategy library."""
        self.strategies = [
            Strategy(
                id="micro_5min",
                name="5-Minute Start",
                description="Commit to just 5 minutes. Often you'll continue.",
                friction_types=[FrictionType.MOTIVATIONAL, FrictionType.COGNITIVE],
                effectiveness=5
            ),
            Strategy(
                id="micro_1page",
                name="Just 1 Page",
                description="Read just one page. Stop if you want.",
                friction_types=[FrictionType.MOTIVATIONAL],
                effectiveness=4
            ),
            Strategy(
                id="env_remove_barrier",
                name="Remove Environment Barriers",
                description="Put the book on your pillow. Lay out workout clothes.",
                friction_types=[FrictionType.PHYSICAL],
                effectiveness=5
            ),
            Strategy(
                id="breathe_4_7",
                name="4-7-8 Breathing",
                description="Inhale 4s, hold 7s, exhale 8s. Repeat 3x.",
                friction_types=[FrictionType.EMOTIONAL],
                effectiveness=5
            ),
            Strategy(
                id="body_scan",
                name="Body Scan",
                description="Notice where tension is. Breathe into those areas.",
                friction_types=[FrictionType.EMOTIONAL],
                effectiveness=4
            ),
            Strategy(
                id="reframe_why",
                name="Reframe: Why Am I Doing This?",
                description="Connect to deeper purpose. Why does this matter?",
                friction_types=[FrictionType.MOTIVATIONAL, FrictionType.COGNITIVE],
                effectiveness=4
            ),
            Strategy(
                id="reframe_identity",
                name="Reframe: Who Am I?",
                description="I'm not 'trying to exercise', I 'am someone who exercises'.",
                friction_types=[FrictionType.MOTIVATIONAL],
                effectiveness=5
            ),
            Strategy(
                id="public_commit",
                name="Tell Someone",
                description="Text someone your intention. Accountability helps.",
                friction_types=[FrictionType.MOTIVATIONAL],
                effectiveness=4
            ),
        ]
    
    def record_friction(
        self,
        user_id: str,
        task_name: str,
        friction_type: FrictionType,
        intensity: int = 5
    ) -> FrictionEvent:
        """Record a friction event."""
        import uuid
        
        event = FrictionEvent(
            id=str(uuid.uuid4()),
            user_id=user_id,
            timestamp=datetime.now(),
            task_name=task_name,
            friction_type=friction_type,
            intensity=intensity
        )
        
        self.events.append(event)
        return event
    
    def resolve_friction(
        self,
        event_id: str,
        strategy_used: StrategyType,
        time_to_start: int
    ) -> None:
        """Resolve a friction event."""
        for event in self.events:
            if event.id == event_id:
                event.resolved = True
                event.strategy_used = strategy_used
                event.time_to_start_seconds = time_to_start
                break
    
    def get_strategies(
        self, 
        friction_type: Optional[FrictionType] = None
    ) -> List[Strategy]:
        """Get recommended strategies."""
        if friction_type:
            return [s for s in self.strategies if friction_type in s.friction_types]
        return self.strategies
    
    def get_task_strategies(self, task_name: str) -> List[Strategy]:
        """Get strategies for a specific task based on history."""
        # Get friction types for this task
        task_events = [e for e in self.events if e.task_name == task_name]
        
        if not task_events:
            return self.strategies[:3]  # Return top strategies
        
        # Find most common friction type
        type_counts = {}
        for e in task_events:
            type_counts[e.friction_type] = type_counts.get(e.friction_type, 0) + 1
        
        most_common = max(type_counts, key=type_counts.get)
        
        return self.get_strategies(most_common)
    
    def get_stats(self, user_id: str) -> Dict:
        """Get friction statistics."""
        events = [e for e in self.events if e.user_id == user_id]
        
        if not events:
            return {
                "total_events": 0,
                "resolved": 0,
                "avg_intensity": 0,
                "most_common_type": None,
                "avg_time_to_start": 0
            }
        
        resolved = sum(1 for e in events if e.resolved)
        
        # Most common type
        type_counts = {}
        for e in events:
            type_counts[e.friction_type.value] = type_counts.get(e.friction_type.value, 0) + 1
        
        most_common = max(type_counts, key=type_counts.get) if type_counts else None
        
        # Avg time to start
        times = [e.time_to_start_seconds for e in events if e.time_to_start_seconds]
        avg_time = sum(times) / len(times) if times else 0
        
        return {
            "total_events": len(events),
            "resolved": resolved,
            "avg_intensity": sum(e.intensity for e in events) / len(events),
            "most_common_type": most_common,
            "avg_time_to_start": avg_time
        }


def create_engine() -> LimbicFrictionEngine:
    """Factory function."""
    return LimbicFrictionEngine()
