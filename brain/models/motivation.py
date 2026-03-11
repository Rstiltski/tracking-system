"""
Motivation Model - Eudaemonic Motivation Tracking

Implements eudaemonic (meaning-driven) motivation tracking:
- Motivation type assessment (eudaemonic vs hedonic vs utilitarian)
- Values-habit alignment scoring
- Purpose connection prompts
- Motivation drift detection

Based on Task 11.1.5 from PHASE_11_INTEGRATION_ROADMAP.md

Research Basis:
- Eudaemonic wellbeing: meaning and purpose in life
- Hedonic wellbeing: pleasure and positive emotion
- Utilitarian wellbeing: usefulness and productivity
- Eudaemonic is strongest predictor of habit retention
"""

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum


# =============================================================================
# ENUMS
# =============================================================================

class MotivationType(str, Enum):
    """Types of motivation."""
    EUDAEMONIC = "eudaemonic"    # Meaning-driven (strongest retention)
    HEDONIC = "hedonic"          # Pleasure-driven
    UTILITARIAN = "utilitarian"  # Utility-driven
    MIXED = "mixed"              # Combination of types


class MotivationDrift(str, Enum):
    """Types of motivation drift."""
    NONE = "none"
    DECLINING = "declining"       # Less motivated over time
    SHIFTING = "shifting"          # Changing motivation type
    DISCONNECTED = "disconnected"  # Lost connection to purpose


# =============================================================================
# VALUES & PURPOSE
# =============================================================================

# Core values for alignment assessment
CORE_VALUES = [
    "health",
    "family",
    "career",
    "growth",
    "creativity",
    "community",
    "nature",
    "spirituality",
    "finance",
    "relationships",
    "learning",
    "impact",
    "freedom",
    "balance",
    "wellbeing",
]

# Sample purposes for different motivation types
SAMPLE_PURPOSES = {
    MotivationType.EUDAEMONIC: [
        "Making a positive impact on others",
        "Living according to my values",
        "Becoming the best version of myself",
        "Contributing to something meaningful",
        "Living a purposeful life",
        "Growing as a person every day",
    ],
    MotivationType.HEDONIC: [
        "Enjoying life's pleasures",
        "Feeling happy and content",
        "Having fun and excitement",
        "Experiencing joy daily",
        "Living in the moment",
        "Maximizing positive experiences",
    ],
    MotivationType.UTILITARIAN: [
        "Being productive and efficient",
        "Achieving concrete goals",
        "Building useful skills",
        "Getting things done",
        "Being disciplined and focused",
        "Maximizing my potential",
    ],
}


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class ValueAlignment:
    """Alignment between a habit and a core value."""
    value: str
    alignment_score: float  # 0.0 to 1.0
    evidence: List[str] = field(default_factory=list)


@dataclass
class MotivationProfile:
    """
    User's motivation profile.
    
    Attributes:
        primary_type: Main motivation type
        secondary_type: Secondary motivation type (if mixed)
        why_statement: User's "why" for tracking
        values: List of core values (prioritized)
        alignment_scores: Alignment of habits to values
    """
    primary_type: MotivationType = MotivationType.MIXED
    secondary_type: Optional[MotivationType] = None
    why_statement: str = ""
    values: List[str] = field(default_factory=list)
    alignment_scores: List[ValueAlignment] = field(default_factory=list)
    last_assessment: datetime = field(default_factory=datetime.now)
    
    def get_top_values(self, n: int = 3) -> List[str]:
        """Get top N values."""
        return self.values[:n] if len(self.values) >= n else self.values
    
    def get_alignment_score(self) -> float:
        """Get overall alignment score."""
        if not self.alignment_scores:
            return 0.0
        return sum(s.alignment_score for s in self.alignment_scores) / len(self.alignment_scores)


@dataclass
class MotivationDriftDetection:
    """
    Detection of motivation drift.
    
    Attributes:
        drift_type: Type of drift detected
        severity: How severe the drift is (0.0 to 1.0)
        indicators: What triggered the detection
        recommendations: How to address the drift
    """
    drift_type: MotivationDrift = MotivationDrift.NONE
    severity: float = 0.0
    indicators: List[str] = field(default_factory=list)
    recommendations: List[str] = field(default_factory=list)


# =============================================================================
# MOTIVATION ASSESSMENT
# =============================================================================

class MotivationAssessor:
    """
    Assess and track user motivation.
    
    Uses responses to determine motivation type and alignment.
    """
    
    def __init__(self):
        """Initialize the assessor."""
        self._history: List[MotivationProfile] = []
    
    def assess_from_responses(
        self,
        why_answers: List[str],
        value_choices: List[str],
        habit_descriptions: List[str] = None
    ) -> MotivationProfile:
        """
        Assess motivation type from user responses.
        
        Args:
            why_answers: Answers to "why" questions
            value_choices: Selected core values
            habit_descriptions: Optional habit descriptions
            
        Returns:
            MotivationProfile with assessment
        """
        profile = MotivationProfile(
            values=value_choices[:5] if value_choices else [],
            why_statement="; ".join(why_answers) if why_answers else "",
            last_assessment=datetime.now()
        )
        
        # Determine primary motivation type from responses
        eudaemonic_count = 0
        hedonic_count = 0
        utilitarian_count = 0
        
        all_text = " ".join(why_answers).lower() if why_answers else ""
        
        # Count keywords
        eudaemonic_keywords = ["meaning", "purpose", "impact", "values", "grow", "contribute", "better"]
        hedonic_keywords = ["happy", "joy", "pleasure", "fun", "enjoy", "feel good"]
        utilitarian_keywords = ["achieve", "goal", "productive", "efficient", "get done", "build"]
        
        for kw in eudaemonic_keywords:
            if kw in all_text:
                eudaemonic_count += 1
        for kw in hedonic_keywords:
            if kw in all_text:
                hedonic_count += 1
        for kw in utilitarian_keywords:
            if kw in all_text:
                utilitarian_count += 1
        
        # Determine type
        if eudaemonic_count >= hedonic_count and eudaemonic_count >= utilitarian_count:
            profile.primary_type = MotivationType.EUDAEMONIC
        elif hedonic_count >= eudaemonic_count and hedonic_count >= utilitarian_count:
            profile.primary_type = MotivationType.HEDONIC
        elif utilitarian_count > 0:
            profile.primary_type = MotivationType.UTILITARIAN
        
        # Calculate alignment scores based on values
        profile.alignment_scores = self._calculate_alignment(value_choices, habit_descriptions)
        
        self._history.append(profile)
        
        return profile
    
    def _calculate_alignment(
        self,
        values: List[str],
        habits: List[str] = None
    ) -> List[ValueAlignment]:
        """Calculate value-habit alignment scores."""
        alignments = []
        
        for value in values[:5]:
            # Simplified alignment - in production, use ML model
            alignment = ValueAlignment(
                value=value,
                alignment_score=0.8,  # Default positive alignment
                evidence=["User selected this as core value"]
            )
            alignments.append(alignment)
        
        return alignments
    
    def detect_drift(
        self,
        current_profile: MotivationProfile,
        completion_rates: List[float] = None,
        recent_why: str = None
    ) -> MotivationDriftDetection:
        """
        Detect motivation drift.
        
        Args:
            current_profile: Current motivation profile
            completion_rates: Recent completion rates
            recent_why: Recent "why" statement
            
        Returns:
            MotivationDriftDetection with results
        """
        detection = MotivationDriftDetection()
        
        # Check completion rate decline
        if completion_rates and len(completion_rates) >= 7:
            recent = completion_rates[-7:]
            older = completion_rates[-14:-7] if len(completion_rates) >= 14 else recent
            
            recent_avg = sum(recent) / len(recent)
            older_avg = sum(older) / len(older)
            
            if recent_avg < older_avg * 0.7:  # 30% decline
                detection.severity = (older_avg - recent_avg) / older_avg
                detection.drift_type = MotivationDrift.DECLINING
                detection.indicators.append(f"Completion rate dropped from {older_avg:.0%} to {recent_avg:.0%}")
                detection.recommendations.append("Let's reconnect with your 'why'")
        
        # Check for motivation shift
        if recent_why:
            recent_text = recent_why.lower()
            if current_profile.why_statement:
                old_text = current_profile.why_statement.lower()
                
                # Check for keyword changes
                old_eudaemonic = any(kw in old_text for kw in ["meaning", "purpose", "impact"])
                new_eudaemonic = any(kw in recent_text for kw in ["meaning", "purpose", "impact"])
                
                if old_eudaemonic != new_eudaemonic:
                    detection.severity = 0.5
                    detection.drift_type = MotivationDrift.SHIFTING
                    detection.indicators.append("Your motivation seems to be shifting")
        
        return detection


# =============================================================================
# PURPOSE PROMPTS
# =============================================================================

PURPOSE_PROMPTS = {
    MotivationType.EUDAEMONIC: [
        "🌟 How does completing this habit connect to your deeper purpose?",
        "💫 Which of your values does this habit support?",
        "🎯 How does this habit help you become the person you want to be?",
        "🌱 What impact will this have on your long-term journey?",
    ],
    MotivationType.HEDONIC: [
        "😊 How will completing this make you feel?",
        "🎉 What pleasure or joy does this bring you?",
        "✨ How can you make this habit more enjoyable?",
        "💖 What's the happiness benefit of this habit?",
    ],
    MotivationType.UTILITARIAN: [
        "📊 What goal does this habit help you achieve?",
        "⚡ How does this make you more productive?",
        "🎯 What concrete result will this produce?",
        "💪 What's the practical benefit of this habit?",
    ],
}

CONNECTION_PROMPTS = [
    "🌟 Remember: This habit connects to your value of [VALUE]",
    "💫 You're doing this because [WHY]",
    "🎯 Each completion brings you closer to [GOAL]",
    "🌱 This builds toward [PURPOSE]",
    "✨ Your future self will thank you for [ACTION]",
]


# =============================================================================
# FACTORY
# =============================================================================

def create_motivation_assessor() -> MotivationAssessor:
    """Factory function to create a motivation assessor."""
    return MotivationAssessor()


def get_purpose_prompt(motivation_type: MotivationType) -> str:
    """Get a purpose connection prompt for the user's motivation type."""
    prompts = PURPOSE_PROMPTS.get(motivation_type, PURPOSE_PROMPTS[MotivationType.MIXED])
    import random
    return random.choice(prompts)
