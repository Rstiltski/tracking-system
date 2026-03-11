"""
Fixed Mindset Detection Model

Detects fixed mindset patterns and triggers challenge de-escalation.

Based on Task 11.1.7 from PHASE_11_INTEGRATION_ROADMAP.md

Complements Growth Mindset (11.1.4) - when users show fixed mindset patterns,
the system automatically scales down challenge difficulty.
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional


# =============================================================================
# FIXED MINDSET PATTERNS
# =============================================================================

# Language patterns indicating fixed mindset
FIXED_MINDSET_PATTERNS = [
    "i can't",
    "i'm not good at",
    "i'll never be able to",
    "i'm terrible at",
    "i give up",
    "it's too hard",
    "i'm not smart enough",
    "i don't have the talent",
    "i was born this way",
    "either i'm good at it or i'm not",
    "there's no point trying",
    "i'll just fail anyway",
    "others are just better",
    "i don't have what it takes",
    "i'm stuck",
    "i can't improve",
    "it's impossible",
    "i'm a failure",
    "nothing works for me",
    "i'm hopeless",
    "why try",
    "too difficult",
    "not meant for me",
]


# Challenge difficulty levels
class ChallengeLevel(Enum):
    """Difficulty levels for habits/challenges."""
    VERY_EASY = 1
    EASY = 2
    MODERATE = 3
    CHALLENGING = 4
    VERY_HARD = 5
    EXTREME = 6


# De-escalation triggers
DEESCALATION_TRIGGERS = {
    "repeated_skip": 3,  # Skip 3+ times
    "low_completion": 0.4,  # Below 40% completion
    "fixed_language": 2,  # 2+ fixed mindset statements
    "frustration_signals": 3,  # 3+ frustration indicators
}


@dataclass
class ChallengeMetrics:
    """Metrics for a specific challenge/habit."""
    challenge_id: str
    current_level: ChallengeLevel
    total_attempts: int = 0
    successful_completions: int = 0
    skipped_count: int = 0
    consecutive_failures: int = 0
    fixed_mindset_signals: int = 0
    last_attempt: Optional[datetime] = None


@dataclass
class FixedMindsetDetection:
    """Result of fixed mindset detection."""
    is_fixed_mindset: bool
    confidence: float  # 0.0 to 1.0
    triggers: List[str]
    recommended_action: str  # "deescalate", "maintain", "encourage"
    new_level: Optional[ChallengeLevel] = None


class FixedMindsetDetector:
    """
    Detects fixed mindset patterns and manages challenge difficulty.
    
    Features:
    - Language pattern detection
    - Completion rate analysis
    - Automatic de-escalation
    - Recovery encouragement
    """
    
    def __init__(self):
        """Initialize the detector."""
        self.challenges: Dict[str, ChallengeMetrics] = {}
        self.min_level = ChallengeLevel.VERY_EASY
        self.max_level = ChallengeLevel.EXTREME
    
    def register_challenge(self, challenge_id: str, initial_level: ChallengeLevel = ChallengeLevel.MODERATE) -> ChallengeMetrics:
        """Register a new challenge for tracking."""
        metrics = ChallengeMetrics(
            challenge_id=challenge_id,
            current_level=initial_level,
            last_attempt=datetime.now()
        )
        self.challenges[challenge_id] = metrics
        return metrics
    
    def record_attempt(self, challenge_id: str, completed: bool, has_fixed_language: bool = False) -> None:
        """Record an attempt at a challenge."""
        if challenge_id not in self.challenges:
            self.register_challenge(challenge_id)
        
        metrics = self.challenges[challenge_id]
        metrics.total_attempts += 1
        metrics.last_attempt = datetime.now()
        
        if completed:
            metrics.successful_completions += 1
            metrics.consecutive_failures = 0
        else:
            metrics.consecutive_failures += 1
        
        if has_fixed_language:
            metrics.fixed_mindset_signals += 1
    
    def record_skip(self, challenge_id: str) -> None:
        """Record a skipped challenge."""
        if challenge_id not in self.challenges:
            self.register_challenge(challenge_id)
        
        metrics = self.challenges[challenge_id]
        metrics.skipped_count += 1
        metrics.last_attempt = datetime.now()
    
    def detect(self, challenge_id: str) -> FixedMindsetDetection:
        """
        Detect fixed mindset patterns for a challenge.
        
        Returns:
            FixedMindsetDetection with analysis and recommendations
        """
        if challenge_id not in self.challenges:
            return FixedMindsetDetection(
                is_fixed_mindset=False,
                confidence=0.0,
                triggers=[],
                recommended_action="maintain"
            )
        
        metrics = self.challenges[challenge_id]
        triggers = []
        
        # Check completion rate
        if metrics.total_attempts > 0:
            completion_rate = metrics.successful_completions / metrics.total_attempts
            if completion_rate < DEESCALATION_TRIGGERS["low_completion"]:
                triggers.append("low_completion")
        
        # Check consecutive failures
        if metrics.consecutive_failures >= 3:
            triggers.append("consecutive_failures")
        
        # Check skipped count
        if metrics.skipped_count >= DEESCALATION_TRIGGERS["repeated_skip"]:
            triggers.append("repeated_skip")
        
        # Check fixed mindset language
        if metrics.fixed_mindset_signals >= DEESCALATION_TRIGGERS["fixed_language"]:
            triggers.append("fixed_language")
        
        # Determine confidence
        confidence = min(len(triggers) * 0.3, 1.0)
        
        # Determine recommended action
        if len(triggers) >= 2:
            recommended_action = "deescalate"
            # Calculate new level
            current_idx = metrics.current_level.value
            new_level_value = max(1, current_idx - 1)
            new_level = ChallengeLevel(new_level_value)
        elif len(triggers) == 1:
            recommended_action = "encourage"
            new_level = None
        else:
            recommended_action = "maintain"
            new_level = None
        
        return FixedMindsetDetection(
            is_fixed_mindset=len(triggers) > 0,
            confidence=confidence,
            triggers=triggers,
            recommended_action=recommended_action,
            new_level=new_level
        )
    
    def get_current_level(self, challenge_id: str) -> ChallengeLevel:
        """Get current challenge level."""
        if challenge_id not in self.challenges:
            return ChallengeLevel.MODERATE
        return self.challenges[challenge_id].current_level
    
    def apply_recommendation(self, challenge_id: str) -> ChallengeLevel:
        """Apply de-escalation recommendation."""
        detection = self.detect(challenge_id)
        
        if detection.recommended_action == "deescalate" and detection.new_level:
            self.challenges[challenge_id].current_level = detection.new_level
            return detection.new_level
        
        return self.get_current_level(challenge_id)


def create_detector() -> FixedMindsetDetector:
    """Factory function to create a detector."""
    return FixedMindsetDetector()
