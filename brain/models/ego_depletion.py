"""
Ego-Depletion Model - Self-Monitoring Fatigue Detection

Implements detection and response to self-monitoring fatigue before abandonment.

Features:
- Depletion indicators (tracking gaps, rushed logging, avoidance)
- Fatigue score calculation
- Intervention triggers (moderate vs severe)
- Rest & recovery protocol

Based on Task 11.1.6 from PHASE_11_INTEGRATION_ROADMAP.md

Research Basis:
- Ego depletion theory: self-control is limited resource
- Fatigue from continuous self-monitoring
- Prevention before abandonment
"""

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum


# =============================================================================
# ENUMS
# =============================================================================

class DepletionLevel(str, Enum):
    """Level of ego depletion."""
    NONE = "none"          # No depletion detected
    LOW = "low"           # Early signs
    MODERATE = "moderate" # Needs intervention
    HIGH = "high"         # Critical - risk of abandonment
    CRITICAL = "critical"  # Immediate intervention needed


class DepletionIndicator(str, Enum):
    """Types of depletion indicators."""
    TRACKING_GAP = "tracking_gap"       # Missing days
    RUSHED_LOGGING = "rushed_logging"   # Quick, unthoughtful entries
    AVOIDANCE = "avoidance"            # Delayed tracking
    DECLINING_QUALITY = "declining_quality"  # Less detail
    NEGATIVE_SENTIMENT = "negative_sentiment"  # Frustration in notes
    SKIPPED_HABITS = "skipped_habits"  # Missing scheduled habits


# =============================================================================
# DEPLETION INDICATORS
# =============================================================================

# Indicator thresholds
TRACKING_GAP_DAYS = 2  # Days without tracking to trigger
RUSHED_LOGGING_SECONDS = 5  # Less than this = rushed
AVOIDANCE_HOURS = 24  # More than this delay = avoidance
QUALITY_DECLINE_DAYS = 7  # Days to check for quality decline


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class DepletionSignal:
    """A signal indicating potential ego depletion."""
    indicator: DepletionIndicator
    severity: float  # 0.0 to 1.0
    evidence: List[str]
    detected_at: datetime


@dataclass
class EgoDepletionAssessment:
    """
    Complete ego depletion assessment.
    
    Attributes:
        level: Overall depletion level
        signals: Individual depletion signals
        fatigue_score: Calculated fatigue score (0.0 to 1.0)
        intervention_recommended: Type of intervention needed
    """
    level: DepletionLevel = DepletionLevel.NONE
    signals: List[DepletionSignal] = field(default_factory=list)
    fatigue_score: float = 0.0
    intervention_recommended: str = ""
    assessment_date: datetime = field(default_factory=datetime.now)
    
    def should_intervene(self) -> bool:
        """Check if intervention is needed."""
        return self.level in [DepletionLevel.MODERATE, DepletionLevel.HIGH, DepletionLevel.CRITICAL]
    
    def is_critical(self) -> bool:
        """Check if this is a critical situation."""
        return self.level in [DepletionLevel.HIGH, DepletionLevel.CRITICAL]


# =============================================================================
# FATIGUE DETECTOR
# =============================================================================

class EgoDepletionDetector:
    """
    Detects ego depletion from user behavior patterns.
    
    Uses multiple signals:
    - Tracking gaps
    - Logging speed
    - Avoidance patterns
    - Entry quality
    """
    
    def __init__(self):
        """Initialize the detector."""
        self._signal_history: List[DepletionSignal] = []
    
    def assess_depletion(
        self,
        user_id: str,
        entry_dates: List[date] = None,
        logging_times: Dict[date, float] = None,
        entry_lengths: Dict[date, int] = None,
        habit_completions: Dict[date, float] = None
    ) -> EgoDepletionAssessment:
        """
        Assess ego depletion for a user.
        
        Args:
            user_id: User to assess
            entry_dates: Dates with entries
            logging_times: Time spent logging (seconds) per date
            entry_lengths: Length of entries per date
            habit_completions: Completion rate per date
            
        Returns:
            EgoDepletionAssessment
        """
        assessment = EgoDepletionAssessment()
        
        # Check tracking gaps
        if entry_dates:
            gap_signal = self._check_tracking_gaps(entry_dates)
            if gap_signal:
                assessment.signals.append(gap_signal)
        
        # Check rushed logging
        if logging_times:
            rushed_signal = self._check_rushed_logging(logging_times)
            if rushed_signal:
                assessment.signals.append(rushed_signal)
        
        # Check avoidance patterns
        if entry_dates:
            avoidance_signal = self._check_avoidance(entry_dates)
            if avoidance_signal:
                assessment.signals.append(avoidance_signal)
        
        # Check declining quality
        if entry_lengths:
            quality_signal = self._check_quality_decline(entry_lengths)
            if quality_signal:
                assessment.signals.append(quality_signal)
        
        # Check declining habit completions
        if habit_completions:
            completion_signal = self._check_completion_decline(habit_completions)
            if completion_signal:
                assessment.signals.append(completion_signal)
        
        # Calculate overall assessment
        assessment.fatigue_score = self._calculate_fatigue_score(assessment.signals)
        assessment.level = self._score_to_level(assessment.fatigue_score)
        assessment.intervention_recommended = self._get_intervention(assessment.level)
        
        return assessment
    
    def _check_tracking_gaps(self, entry_dates: List[date]) -> Optional[DepletionSignal]:
        """Check for tracking gaps."""
        if not entry_dates:
            return None
        
        today = date.today()
        sorted_dates = sorted(entry_dates, reverse=True)
        
        # Check for gaps
        gaps = []
        for i in range(len(sorted_dates) - 1):
            gap_days = (sorted_dates[i] - sorted_dates[i+1]).days
            if gap_days > 1:
                gaps.append(gap_days)
        
        if gaps:
            max_gap = max(gaps)
            severity = min(max_gap / 7, 1.0)  # Cap at 1.0
            
            return DepletionSignal(
                indicator=DepletionIndicator.TRACKING_GAP,
                severity=severity,
                evidence=[f"Gap of {g} days found" for g in gaps],
                detected_at=datetime.now()
            )
        
        return None
    
    def _check_rushed_logging(self, logging_times: Dict[date, float]) -> Optional[DepletionSignal]:
        """Check for rushed logging patterns."""
        rushed_count = sum(1 for t in logging_times.values() if t < RUSHED_LOGGING_SECONDS)
        
        if rushed_count > 0:
            severity = min(rushed_count / 7, 1.0)
            
            return DepletionSignal(
                indicator=DepletionIndicator.RUSHED_LOGGING,
                severity=severity,
                evidence=[f"{rushed_count} rushed entries in recent history"],
                detected_at=datetime.now()
            )
        
        return None
    
    def _check_avoidance(self, entry_dates: List[date]) -> Optional[DepletionSignal]:
        """Check for tracking avoidance."""
        if not entry_dates:
            return None
        
        today = date.today()
        most_recent = max(entry_dates)
        days_delay = (today - most_recent).days
        
        if days_delay >= AVOIDANCE_HOURS // 24:
            severity = min(days_delay / 7, 1.0)
            
            return DepletionSignal(
                indicator=DepletionIndicator.AVOIDANCE,
                severity=severity,
                evidence=[f"Delayed tracking by {days_delay} days"],
                detected_at=datetime.now()
            )
        
        return None
    
    def _check_quality_decline(self, entry_lengths: Dict[date, int]) -> Optional[DepletionSignal]:
        """Check for declining entry quality."""
        if len(entry_lengths) < 5:
            return None
        
        sorted_lengths = [entry_lengths[d] for d in sorted(entry_lengths.keys())]
        
        # Compare recent to older
        recent_avg = sum(sorted_lengths[-3:]) / 3
        older_avg = sum(sorted_lengths[:-3]) / max(len(sorted_lengths) - 3, 1)
        
        if older_avg > 0:
            decline_ratio = 1 - (recent_avg / older_avg)
            
            if decline_ratio > 0.3:  # 30% decline
                severity = min(decline_ratio, 1.0)
                
                return DepletionSignal(
                    indicator=DepletionIndicator.DECLINING_QUALITY,
                    severity=severity,
                    evidence=[f"Entry length declined by {decline_ratio:.0%}"],
                    detected_at=datetime.now()
                )
        
        return None
    
    def _check_completion_decline(self, completions: Dict[date, float]) -> Optional[DepletionSignal]:
        """Check for declining habit completion rates."""
        if len(completions) < 7:
            return None
        
        sorted_completions = [completions[d] for d in sorted(completions.keys())]
        
        # Compare recent to older
        recent_avg = sum(sorted_completions[-7:]) / 7
        older_avg = sum(sorted_completions[:-7]) / max(len(sorted_completions) - 7, 1)
        
        if older_avg > 0:
            decline_ratio = 1 - (recent_avg / older_avg)
            
            if decline_ratio > 0.3:  # 30% decline
                severity = min(decline_ratio, 1.0)
                
                return DepletionSignal(
                    indicator=DepletionIndicator.SKIPPED_HABITS,
                    severity=severity,
                    evidence=[f"Completion rate declined by {decline_ratio:.0%}"],
                    detected_at=datetime.now()
                )
        
        return None
    
    def _calculate_fatigue_score(self, signals: List[DepletionSignal]) -> float:
        """Calculate overall fatigue score from signals."""
        if not signals:
            return 0.0
        
        # Weighted average based on indicator type
        weights = {
            DepletionIndicator.TRACKING_GAP: 0.3,
            DepletionIndicator.RUSHED_LOGGING: 0.2,
            DepletionIndicator.AVOIDANCE: 0.25,
            DepletionIndicator.DECLINING_QUALITY: 0.15,
            DepletionIndicator.SKIPPED_HABITS: 0.1,
        }
        
        total_weight = 0.0
        weighted_sum = 0.0
        
        for signal in signals:
            weight = weights.get(signal.indicator, 0.2)
            weighted_sum += signal.severity * weight
            total_weight += weight
        
        return weighted_sum / total_weight if total_weight > 0 else 0.0
    
    def _score_to_level(self, score: float) -> DepletionLevel:
        """Convert score to depletion level."""
        if score < 0.1:
            return DepletionLevel.NONE
        elif score < 0.3:
            return DepletionLevel.LOW
        elif score < 0.5:
            return DepletionLevel.MODERATE
        elif score < 0.7:
            return DepletionLevel.HIGH
        else:
            return DepletionLevel.CRITICAL
    
    def _get_intervention(self, level: DepletionLevel) -> str:
        """Get recommended intervention for level."""
        interventions = {
            DepletionLevel.NONE: "Continue normal operation",
            DepletionLevel.LOW: "Offer gentle encouragement",
            DepletionLevel.MODERATE: "Suggest rest day, offer simplified tracking",
            DepletionLevel.HIGH: "Strongly recommend break, reduce tracking load",
            DepletionLevel.CRITICAL: "Urgent intervention, suggest extended break",
        }
        return interventions.get(level, "Continue normal operation")


# =============================================================================
# REST PROTOCOL
# =============================================================================

REST_RECOMMENDATIONS = {
    DepletionLevel.LOW: [
        "Consider taking a shorter break today",
        "Your tracking can be flexible - it's okay to miss a day",
    ],
    DepletionLevel.MODERATE: [
        "A rest day is recommended - your willpower needs recharging",
        "Try 'scaling back' instead of complete tracking",
        "Small breaks prevent bigger abandonments",
    ],
    DepletionLevel.HIGH: [
        "Please take a break - your wellbeing matters more than tracking",
        "Consider taking 2-3 days completely off",
        "The app will be here when you return",
    ],
    DepletionLevel.CRITICAL: [
        "URGENT: Please prioritize rest over tracking",
        "Consider an extended break (1-2 weeks)",
        "Your mental health is more important than streaks",
    ],
}


class RestProtocol:
    """
    Rest and recovery protocol for ego depletion.
    
    Frames rest as strategic, not failure.
    """
    
    @staticmethod
    def get_rest_message(level: DepletionLevel) -> str:
        """Get rest message for depletion level."""
        messages = REST_RECOMMENDATIONS.get(level, REST_RECOMMENDATIONS[DepletionLevel.LOW])
        import random
        return random.choice(messages)
    
    @staticmethod
    def get_recovery_suggestions() -> List[str]:
        """Get suggestions for recovery."""
        return [
            "Get adequate sleep",
            "Take a walk in nature",
            "Practice mindfulness or meditation",
            "Connect with supportive people",
            "Do something enjoyable without tracking",
            "Remember why you started",
        ]


# =============================================================================
# FACTORY
# =============================================================================

def create_depletion_detector() -> EgoDepletionDetector:
    """Factory function to create a depletion detector."""
    return EgoDepletionDetector()
