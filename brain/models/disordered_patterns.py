"""
Disordered Patterns Model - Detection & Safeguards

Implements safeguards against disordered eating patterns triggered by rigid tracking.

Features:
- Orthorexia risk detection
- Calorie limit enforcement
- Maximum entries per day limits
- Rest day requirements
- Data fasting protocols

Based on Task 11.1.1 from PHASE_11_INTEGRATION_ROADMAP.md

Ethical Principles:
- NEVER enable disordered patterns
- ALWAYS provide resources when risk detected
- Frame flexibility as health, not failure
"""

from dataclasses import dataclass, field
from datetime import date, datetime, timedelta
from typing import Dict, List, Optional
from enum import Enum


# =============================================================================
# CONSTANTS - SAFETY LIMITS
# =============================================================================

# Absolute minimum - cannot be bypassed
MIN_CALORIE_LIMIT = 1200

# Maximum entries per day to prevent obsessive logging
MAX_DAILY_ENTRIES = 10

# Required rest days per week
REQUIRED_REST_DAYS_PER_WEEK = 1

# Maximum consecutive tracking days before forced break
MAX_CONSECUTIVE_TRACKING_DAYS = 6


# =============================================================================
# ENUMS
# =============================================================================

class RiskLevel(Enum):
    """Risk level for disordered patterns."""
    NONE = "none"
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    CRITICAL = "critical"


class PatternType(Enum):
    """Types of disordered patterns to detect."""
    CALORIE_RESTRICTION = "calorie_restriction"
    OBSESSIVE_LOGGING = "obsessive_logging"
    COMPULSIVE_TRACKING = "compulsive_tracking"
    PERFECTIONISM = "perfectionism"
    FOOD_RESTRICTION = "food_restriction"


# =============================================================================
# DATA CLASSES
# =============================================================================

@dataclass
class PatternSignal:
    """A signal indicating potential disordered pattern."""
    pattern_type: PatternType
    risk_level: RiskLevel
    confidence: float  # 0.0 to 1.0
    evidence: List[str]
    detected_at: datetime


@dataclass
class OrthorexiaRisk:
    """
    Comprehensive orthorexia risk assessment.
    
    Attributes:
        overall_risk: Overall risk level
        signals: Individual pattern signals
        recommended_actions: Actions to take
        resources: Support resources to display
    """
    overall_risk: RiskLevel = RiskLevel.NONE
    signals: List[PatternSignal] = field(default_factory=list)
    recommended_actions: List[str] = field(default_factory=list)
    resources: List[str] = field(default_factory=list)
    assessment_date: datetime = field(default_factory=datetime.now)
    
    def has_risk(self) -> bool:
        """Check if there's any elevated risk."""
        return self.overall_risk != RiskLevel.NONE
    
    def should_intervene(self) -> bool:
        """Check if intervention is needed."""
        return self.overall_risk in [RiskLevel.MODERATE, RiskLevel.HIGH, RiskLevel.CRITICAL]


# =============================================================================
# DETECTION LOGIC
# =============================================================================

class DisorderedPatternDetector:
    """
    Detects patterns that may indicate disordered eating.
    
    Uses multiple signals to assess risk:
    - Calorie intake patterns
    - Logging frequency
    - Streak patterns
    - Entry patterns
    """
    
    def __init__(self, storage=None):
        """
        Initialize the detector.
        
        Args:
            storage: Optional storage for data access
        """
        self.storage = storage
    
    def assess_risk(
        self,
        user_id: str,
        entries: List[Dict] = None,
        calories_data: List[int] = None
    ) -> OrthorexiaRisk:
        """
        Assess orthorexia risk for a user.
        
        Args:
            user_id: User to assess
            entries: Recent tracking entries
            calories_data: Recent calorie intakes
            
        Returns:
            OrthorexiaRisk with assessment
        """
        risk = OrthorexiaRisk()
        
        # Default to no entries if not provided
        if entries is None:
            entries = []
        
        # Check for calorie restriction patterns
        if calories_data:
            calorie_signal = self._check_calorie_patterns(calories_data)
            if calorie_signal:
                risk.signals.append(calorie_signal)
        
        # Check for obsessive logging
        logging_signal = self._check_logging_patterns(entries)
        if logging_signal:
            risk.signals.append(logging_signal)
        
        # Check for compulsive tracking
        tracking_signal = self._check_tracking_streak(entries)
        if tracking_signal:
            risk.signals.append(tracking_signal)
        
        # Calculate overall risk
        risk.overall_risk = self._calculate_overall_risk(risk.signals)
        
        # Generate recommendations
        risk.recommended_actions = self._generate_recommendations(risk)
        
        # Add resources if needed
        if risk.should_intervene():
            risk.resources = self._get_support_resources()
        
        return risk
    
    def _check_calorie_patterns(self, calories: List[int]) -> Optional[PatternSignal]:
        """Check for calorie restriction patterns."""
        if not calories:
            return None
        
        # Calculate statistics
        avg_calories = sum(calories) / len(calories)
        low_calorie_days = sum(1 for c in calories if c < MIN_CALORIE_LIMIT)
        
        evidence = []
        confidence = 0.0
        
        # Check for consistently low calories
        if avg_calories < MIN_CALORIE_LIMIT:
            evidence.append(f"Average intake ({avg_calories:.0f} cal) below minimum ({MIN_CALORIE_LIMIT})")
            confidence += 0.4
        
        # Check for frequent low-calorie days
        if low_calorie_days / len(calories) > 0.5:
            evidence.append(f"{low_calorie_days} days with intake below minimum in last {len(calories)} days")
            confidence += 0.3
        
        if evidence:
            return PatternSignal(
                pattern_type=PatternType.CALORIE_RESTRICTION,
                risk_level=self._confidence_to_risk(confidence),
                confidence=confidence,
                evidence=evidence,
                detected_at=datetime.now()
            )
        
        return None
    
    def _check_logging_patterns(self, entries: List[Dict]) -> Optional[PatternSignal]:
        """Check for obsessive logging patterns."""
        if not entries:
            return None
        
        # Count entries per day
        entries_by_date: Dict[date, int] = {}
        for entry in entries:
            entry_date = entry.get("date", date.today())
            if isinstance(entry_date, str):
                entry_date = date.fromisoformat(entry_date)
            entries_by_date[entry_date] = entries_by_date.get(entry_date, 0) + 1
        
        # Find max entries in a day
        max_entries = max(entries_by_date.values()) if entries_by_date else 0
        high_frequency_days = sum(1 for count in entries_by_date.values() if count > MAX_DAILY_ENTRIES)
        
        evidence = []
        confidence = 0.0
        
        if max_entries > MAX_DAILY_ENTRIES:
            evidence.append(f"Maximum {max_entries} entries in a single day (limit: {MAX_DAILY_ENTRIES})")
            confidence += 0.3
        
        if high_frequency_days > 0:
            evidence.append(f"{high_frequency_days} days with excessive entries")
            confidence += 0.2
        
        if evidence:
            return PatternSignal(
                pattern_type=PatternType.OBSESSIVE_LOGGING,
                risk_level=self._confidence_to_risk(confidence),
                confidence=confidence,
                evidence=evidence,
                detected_at=datetime.now()
            )
        
        return None
    
    def _check_tracking_streak(self, entries: List[Dict]) -> Optional[PatternSignal]:
        """Check for compulsive tracking without breaks."""
        if not entries:
            return None
        
        # Get unique dates
        entry_dates = set()
        for entry in entries:
            entry_date = entry.get("date", date.today())
            if isinstance(entry_date, str):
                entry_date = date.fromisoformat(entry_date)
            entry_dates.add(entry_date)
        
        # Sort dates
        sorted_dates = sorted(entry_dates)
        
        # Check consecutive days
        consecutive_days = 1
        max_consecutive = 1
        
        for i in range(1, len(sorted_dates)):
            if (sorted_dates[i] - sorted_dates[i-1]).days == 1:
                consecutive_days += 1
                max_consecutive = max(max_consecutive, consecutive_days)
            else:
                consecutive_days = 1
        
        evidence = []
        confidence = 0.0
        
        if max_consecutive >= MAX_CONSECUTIVE_TRACKING_DAYS:
            evidence.append(f"{max_consecutive} consecutive tracking days without break")
            confidence += 0.3
        
        if max_consecutive >= MAX_CONSECUTIVE_TRACKING_DAYS + 2:
            confidence += 0.2
            evidence.append("No rest days in extended period")
        
        if evidence:
            return PatternSignal(
                pattern_type=PatternType.COMPULSIVE_TRACKING,
                risk_level=self._confidence_to_risk(confidence),
                confidence=confidence,
                evidence=evidence,
                detected_at=datetime.now()
            )
        
        return None
    
    def _confidence_to_risk(self, confidence: float) -> RiskLevel:
        """Convert confidence score to risk level."""
        if confidence < 0.2:
            return RiskLevel.NONE
        elif confidence < 0.4:
            return RiskLevel.LOW
        elif confidence < 0.6:
            return RiskLevel.MODERATE
        elif confidence < 0.8:
            return RiskLevel.HIGH
        else:
            return RiskLevel.CRITICAL
    
    def _calculate_overall_risk(self, signals: List[PatternSignal]) -> RiskLevel:
        """Calculate overall risk from individual signals."""
        if not signals:
            return RiskLevel.NONE
        
        # Take the highest risk level
        risk_values = {
            RiskLevel.NONE: 0,
            RiskLevel.LOW: 1,
            RiskLevel.MODERATE: 2,
            RiskLevel.HIGH: 3,
            RiskLevel.CRITICAL: 4
        }
        
        max_risk = max(signals, key=lambda s: risk_values[s.risk_level])
        return max_risk.risk_level
    
    def _generate_recommendations(self, risk: OrthorexiaRisk) -> List[str]:
        """Generate recommended actions based on risk."""
        recommendations = []
        
        if risk.overall_risk == RiskLevel.LOW:
            recommendations.append("Consider taking a rest day from tracking")
        
        elif risk.overall_risk == RiskLevel.MODERATE:
            recommendations.append("Please take at least 1-2 rest days this week")
            recommendations.append("Try intuitive eating - honor hunger cues")
            recommendations.append("Consider speaking with a health professional")
        
        elif risk.overall_risk == RiskLevel.HIGH:
            recommendations.append("IMPORTANT: Please take a break from tracking")
            recommendations.append("Your wellbeing is more important than perfect tracking")
            recommendations.append("Consider connecting with support resources")
        
        elif risk.overall_risk == RiskLevel.CRITICAL:
            recommendations.append("URGENT: Please stop tracking and seek support")
            recommendations.append("This level of tracking may be harmful to your health")
            recommendations.append("Professional support is strongly recommended")
        
        return recommendations
    
    def _get_support_resources(self) -> List[str]:
        """Get support resources for users."""
        return [
            "National Eating Disorders Association: 1-800-931-2237",
            "NEDA Helpline: https://www.nationaleatingdisorders.org/helpline",
            "Crisis Text Line: Text HOME to 741741",
        ]


# =============================================================================
# GUARDRAIL FUNCTIONS
# =============================================================================

def check_calorie_limit(calories: int) -> tuple[bool, str]:
    """
    Check if calories meet the minimum limit.
    
    Args:
        calories: Calorie intake to check
        
    Returns:
        Tuple of (is_allowed, message)
    """
    if calories < MIN_CALORIE_LIMIT:
        return False, f"⚠️ Intake below safe minimum ({MIN_CALORIE_LIMIT} cal). Please prioritize your health."
    return True, ""


def check_daily_entry_limit(entries_today: int) -> tuple[bool, str]:
    """
    Check if daily entry count is within safe limits.
    
    Args:
        entries_today: Number of entries today
        
    Returns:
        Tuple of (is_allowed, message)
    """
    if entries_today >= MAX_DAILY_ENTRIES:
        return False, f"⚠️ You've reached the daily limit ({MAX_DAILY_ENTRIES} entries). Taking a break is healthy!"
    return True, ""


def check_rest_day_required(entries: List[date]) -> tuple[bool, str]:
    """
    Check if a rest day is required.
    
    Args:
        entries: List of dates with entries
        
    Returns:
        Tuple of (is_required, message)
    """
    today = date.today()
    week_ago = today - timedelta(days=7)
    
    # Get entries from last week
    recent_entries = [e for e in entries if e >= week_ago]
    
    # Check if any rest days
    has_rest_day = False
    for i in range(7):
        check_date = today - timedelta(days=i)
        if check_date not in recent_entries:
            has_rest_day = True
            break
    
    if not has_rest_day and len(recent_entries) >= 6:
        return True, "📢 You've tracked for 6+ days. A rest day is recommended for healthy tracking!"
    
    return False, ""


# =============================================================================
# DATA FASTING PROTOCOL
# =============================================================================

@dataclass
class DataFastingProtocol:
    """
    Data fasting protocol - scheduled breaks from tracking.
    
    Encourages:
    - Weekend off from tracking
    - Intuitive eating periods
    - Untracked meals
    """
    enabled: bool = True
    fasting_days: List[int] = field(default_factory=lambda: [5, 6])  # Saturday, Sunday
    
    def is_fasting_day(self, check_date: date = None) -> bool:
        """Check if today is a fasting day."""
        if check_date is None:
            check_date = date.today()
        # weekday() returns 0=Monday, 6=Sunday
        return check_date.weekday() in self.fasting_days
    
    def get_fasting_message(self) -> str:
        """Get the fasting day message."""
        return "🌿 Today is a data fast day. Try intuitive eating - honor your hunger and fullness cues!"


# =============================================================================
# FACTORY
# =============================================================================

def create_pattern_detector(storage=None) -> DisorderedPatternDetector:
    """Factory function to create a pattern detector."""
    return DisorderedPatternDetector(storage=storage)
