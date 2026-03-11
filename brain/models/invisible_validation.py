"""
Invisible Data Validation

Validate both:
1. Implicit/ambient sensor data (steps, heart rate, sleep)
2. Internal states (emotions, motivation, subjective experience)

Based on Task 11.3.10 from PHASE_11_INTEGRATION_ROADMAP.md
Based on INSIGHT-004 from ALGORITHMIC_SELF_DEEP_ANALYSIS.md

Key Insight: When users compare "invisible" personal data (internal states,
emotions, subtle behaviors) with their actual daily experiences, they frequently
feel upset or confused. This leads to abandonment.

This module validates BOTH types of invisible data:
- Sensor data accuracy (outliers, gaps, inconsistencies)
- Internal state validation (emotional context, resistance, subjective experience)
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional


# =============================================================================
# TYPES
# =============================================================================

class DataSource(Enum):
    """Sources of invisible data."""
    # Ambient/Sensor data
    LOCATION = "location"
    SCREEN_TIME = "screen_time"
    STEP_COUNT = "step_count"
    HEART_RATE = "heart_rate"
    SLEEP = "sleep"
    APP_USAGE = "app_usage"
    CALENDAR = "calendar"
    
    # Internal states (INSIGHT-004 addition)
    EMOTIONAL_STATE = "emotional_state"
    MOTIVATION = "motivation"
    ENERGY = "energy"
    STRESS = "stress"
    MOOD = "mood"
    SUBJECTIVE_EXPERIENCE = "subjective_experience"
    
    CUSTOM = "custom"


class ValidationStatus(Enum):
    """Status of data validation."""
    PENDING = "pending"
    VALIDATED = "validated"
    FLAGGED = "flagged"
    CORRECTED = "corrected"
    REJECTED = "rejected"


class AnomalyType(Enum):
    """Types of data anomalies."""
    OUTLIER = "outlier"  # Unrealistic value
    GAP = "gap"  # Missing data
    INCONSISTENCY = "inconsistency"  # Contradicts other data
    DELAY = "delay"  # Stale data
    DUPLICATE = "duplicate"  # Repeated entry
    
    # Internal state anomalies (INSIGHT-004 addition)
    EMOTIONAL_CONFLICT = "emotional_conflict"  # Emotion doesn't match outcome
    RESISTANCE_MISMATCH = "resistance_mismatch"  # High resistance but completed
    GUILT_PATTERN = "guilt_pattern"  # Guilt after miss (abandonment risk)


# =============================================================================
# INTERNAL STATE MODELS (INSIGHT-004 Addition)
# =============================================================================

class EmotionalContext(Enum):
    """Emotional context during activity."""
    CALM = "calm"
    RUSHED = "rushed"
    ENTHUSIASTIC = "enthusiastic"
    RELUCTANT = "reluctant"
    ANXIOUS = "anxious"
    PROUD = "proud"
    GUILTY = "guilty"
    NEUTRAL = "neutral"


@dataclass
class InternalStateData:
    """
    Internal state data for habit/activity tracking.
    
    Based on INSIGHT-004: The "Invisible Data" Problem
    
    Captures:
    - Emotional context (how did it feel?)
    - Internal resistance (how hard was it?)
    - Completion quality (did full version?)
    - Subjective experience (what was it like?)
    - External barriers (what interfered?)
    """
    id: str
    user_id: str
    activity_id: str
    timestamp: datetime
    
    # Observable
    completed: bool = True
    
    # Invisible internal states (INSIGHT-004)
    completion_quality: float = 1.0  # 0-1 scale (did full version?)
    emotional_context: EmotionalContext = EmotionalContext.NEUTRAL
    internal_resistance: int = 0  # 1-10 scale (how hard was it?)
    external_barriers: List[str] = field(default_factory=list)
    subjective_experience: str = ""  # User's own words
    would_repeat: bool = True
    
    # Validation
    validated: bool = False
    validation_message: Optional[str] = None

    def to_dict(self) -> Dict:
        """Convert to dictionary for storage."""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "activity_id": self.activity_id,
            "timestamp": self.timestamp.isoformat(),
            "completed": self.completed,
            "completion_quality": self.completion_quality,
            "emotional_context": self.emotional_context.value,
            "internal_resistance": self.internal_resistance,
            "external_barriers": self.external_barriers,
            "subjective_experience": self.subjective_experience,
            "would_repeat": self.would_repeat,
            "validated": self.validated,
            "validation_message": self.validation_message,
        }

    @classmethod
    def from_dict(cls, data: Dict) -> "InternalStateData":
        """Create from dictionary."""
        return cls(
            id=data["id"],
            user_id=data["user_id"],
            activity_id=data["activity_id"],
            timestamp=datetime.fromisoformat(data["timestamp"]),
            completed=data.get("completed", True),
            completion_quality=data.get("completion_quality", 1.0),
            emotional_context=EmotionalContext(data.get("emotional_context", "neutral")),
            internal_resistance=data.get("internal_resistance", 0),
            external_barriers=data.get("external_barriers", []),
            subjective_experience=data.get("subjective_experience", ""),
            would_repeat=data.get("would_repeat", True),
            validated=data.get("validated", False),
            validation_message=data.get("validation_message"),
        )


# =============================================================================
# ORIGINAL MODELS (Ambient/Sensor Data)
# =============================================================================

@dataclass
class DataPoint:
    """An invisible data point (sensor/ambient)."""
    id: str
    user_id: str
    source: DataSource

    # Value
    value: float
    unit: str

    # Timing
    timestamp: datetime

    # Context
    location: Optional[str] = None
    activity: Optional[str] = None

    # Validation
    status: ValidationStatus = ValidationStatus.PENDING
    confidence: float = 1.0  # 0-1


@dataclass
class ValidationRule:
    """Rule for validating data."""
    id: str
    source: DataSource

    # Rule
    name: str
    description: str

    # Parameters
    min_value: Optional[float] = None
    max_value: Optional[float] = None
    max_gap_hours: Optional[int] = None

    # Logic
    requires_correlation: bool = False
    correlation_source: Optional[DataSource] = None


@dataclass
class ValidationResult:
    """Result of data validation."""
    id: str
    data_point_id: str
    timestamp: datetime

    # Result
    status: ValidationStatus
    is_valid: bool

    # Details
    anomaly_type: Optional[AnomalyType] = None
    details: str = ""
    confidence: float = 1.0


# =============================================================================
# INVISIBLE DATA VALIDATOR
# =============================================================================

class InvisibleDataValidator:
    """
    Validate invisible/ambient data.

    Features:
    - Rule-based validation for sensor data
    - Anomaly detection
    - Cross-source correlation
    - Auto-correction
    - Internal state validation (INSIGHT-004)
    - Emotional context validation
    - Subjective experience acknowledgment
    """

    def __init__(self):
        """Initialize the validator."""
        # Sensor data
        self.data_points: Dict[str, DataPoint] = {}
        self.rules: Dict[DataSource, List[ValidationRule]] = {
            source: [] for source in DataSource
        }
        self.results: Dict[str, List[ValidationResult]] = {}

        # Internal state data (INSIGHT-004 addition)
        self.internal_states: Dict[str, InternalStateData] = {}

        # Initialize default rules
        self._setup_default_rules()

    def _setup_default_rules(self) -> None:
        """Set up default validation rules."""
        import uuid

        rules = [
            ValidationRule(
                id=str(uuid.uuid4()),
                source=DataSource.STEP_COUNT,
                name="Max Steps Per Day",
                description="Steps cannot exceed realistic daily maximum",
                max_value=50000
            ),
            ValidationRule(
                id=str(uuid.uuid4()),
                source=DataSource.SCREEN_TIME,
                name="Max Screen Time",
                description="Screen time cannot exceed 24 hours",
                max_value=24 * 60  # minutes
            ),
            ValidationRule(
                id=str(uuid.uuid4()),
                source=DataSource.HEART_RATE,
                name="Heart Rate Range",
                description="Heart rate must be in valid range",
                min_value=30,
                max_value=220
            ),
            ValidationRule(
                id=str(uuid.uuid4()),
                source=DataSource.SLEEP,
                name="Sleep Duration",
                description="Sleep must be between 0 and 24 hours",
                max_value=24
            ),
        ]

        for rule in rules:
            self.rules[rule.source].append(rule)

    # =============================================================================
    # SENSOR DATA VALIDATION (Original)
    # =============================================================================

    def add_data_point(
        self,
        user_id: str,
        source: DataSource,
        value: float,
        unit: str,
        timestamp: datetime,
        location: Optional[str] = None,
        activity: Optional[str] = None
    ) -> DataPoint:
        """Add a data point for validation."""
        import uuid

        point = DataPoint(
            id=str(uuid.uuid4()),
            user_id=user_id,
            source=source,
            value=value,
            unit=unit,
            timestamp=timestamp,
            location=location,
            activity=activity
        )

        self.data_points[point.id] = point
        return point

    def validate(self, data_point_id: str) -> ValidationResult:
        """Validate a data point."""
        import uuid

        point = self.data_points.get(data_point_id)
        if not point:
            raise ValueError("Data point not found")

        rules = self.rules.get(point.source, [])

        # Check each rule
        is_valid = True
        anomaly = None
        details = ""

        for rule in rules:
            # Range check
            if rule.min_value is not None and point.value < rule.min_value:
                is_valid = False
                anomaly = AnomalyType.OUTLIER
                details = f"Value {point.value} below minimum {rule.min_value}"
                break

            if rule.max_value is not None and point.value > rule.max_value:
                is_valid = False
                anomaly = AnomalyType.OUTLIER
                details = f"Value {point.value} exceeds maximum {rule.max_value}"
                break

        # Check for gaps (if we have previous data)
        if is_valid:
            user_points = [
                p for p in self.data_points.values()
                if p.user_id == point.user_id and p.source == point.source
            ]
            if user_points:
                # Sort by timestamp
                sorted_points = sorted(user_points, key=lambda p: p.timestamp)
                prev = None
                for p in sorted_points:
                    if p.id == point.id:
                        break
                    prev = p

                if prev:
                    gap = (point.timestamp - prev.timestamp).total_seconds() / 3600
                    if gap > 24:  # More than 24 hours gap
                        anomaly = AnomalyType.GAP
                        details = f"Large gap of {gap:.1f} hours since last reading"

        # Determine status
        if is_valid:
            status = ValidationStatus.VALIDATED
            point.status = ValidationStatus.VALIDATED
        else:
            status = ValidationStatus.FLAGGED
            point.status = ValidationStatus.FLAGGED

        result = ValidationResult(
            id=str(uuid.uuid4()),
            data_point_id=point.id,
            timestamp=datetime.now(),
            status=status,
            is_valid=is_valid,
            anomaly_type=anomaly,
            details=details
        )

        # Store result
        if point.user_id not in self.results:
            self.results[point.user_id] = []
        self.results[point.user_id].append(result)

        return result

    # =============================================================================
    # INTERNAL STATE VALIDATION (INSIGHT-004 Addition)
    # =============================================================================

    def add_internal_state(
        self,
        user_id: str,
        activity_id: str,
        completed: bool = True,
        completion_quality: float = 1.0,
        emotional_context: EmotionalContext = EmotionalContext.NEUTRAL,
        internal_resistance: int = 0,
        external_barriers: List[str] = None,
        subjective_experience: str = ""
    ) -> InternalStateData:
        """
        Add internal state data for validation.
        
        Based on INSIGHT-004: Capture invisible internal states to prevent
        user confusion and abandonment.
        """
        import uuid

        state = InternalStateData(
            id=str(uuid.uuid4()),
            user_id=user_id,
            activity_id=activity_id,
            timestamp=datetime.now(),
            completed=completed,
            completion_quality=completion_quality,
            emotional_context=emotional_context,
            internal_resistance=internal_resistance,
            external_barriers=external_barriers or [],
            subjective_experience=subjective_experience
        )

        self.internal_states[state.id] = state
        return state

    def validate_internal_state(self, state_id: str) -> str:
        """
        Validate internal state and provide compassionate response.
        
        Based on INSIGHT-004 research:
        - Validate the full experience (not just binary success/failure)
        - Acknowledge difficulty
        - Reframe guilt
        - Celebrate showing up despite resistance
        
        Returns:
            Validation message for the user
        """
        state = self.internal_states.get(state_id)
        if not state:
            raise ValueError("Internal state not found")

        message = ""

        # Case 1: Completed despite high resistance
        if state.completed and state.internal_resistance >= 7:
            message = f"""
            🌟 You did this even though it felt really hard today (resistance: {state.internal_resistance}/10).
            
            That's not just discipline - that's commitment to who you're becoming.
            
            Would it help to make this easier tomorrow?
            """
            state.validated = True
            state.validation_message = message

        # Case 2: Completed but rushed/stressed
        elif state.completed and state.emotional_context == EmotionalContext.RUSHED:
            message = """
            ✅ You showed up, even though it felt rushed.
            
            Progress isn't always pretty - sometimes it's just showing up.
            
            Tomorrow, could you give yourself 5 extra minutes?
            """
            state.validated = True
            state.validation_message = message

        # Case 3: Didn't complete and feeling guilty
        elif not state.completed and state.emotional_context == EmotionalContext.GUILTY:
            message = """
            💚 We notice you're feeling guilty about missing.
            
            Self-compassion research shows that guilt actually REDUCES motivation for tomorrow.
            
            Try this instead: "I'm learning what makes this habit difficult.
            What's one small adjustment I can make?"
            
            [Reframe] [Be Kind to Yourself]
            """
            state.validated = True
            state.validation_message = message

        # Case 4: Partial completion (quality < 1.0)
        elif state.completed and state.completion_quality < 1.0:
            message = f"""
            📈 You did {state.completion_quality*100:.0f}% of the habit today.
            
            Partial completion is still completion!
            
            What got in the way of 100%? That's your lever for tomorrow.
            """
            state.validated = True
            state.validation_message = message

        # Case 5: Enthusiastic completion - celebrate!
        elif state.completed and state.emotional_context == EmotionalContext.ENTHUSIASTIC:
            message = """
            🎉 You did this with ENTHUSIASM!
            
            This is what sustainable habits feel like.
            
            Remember this feeling - it's your compass pointing toward what matters.
            """
            state.validated = True
            state.validation_message = message

        # Case 6: Standard completion
        elif state.completed:
            message = f"""
            ✅ Done! 
            
            {state.subjective_experience if state.subjective_experience else "Keep building momentum!"}
            """
            state.validated = True
            state.validation_message = message

        # Case 7: Didn't complete - learning opportunity
        else:
            barriers = ", ".join(state.external_barriers) if state.external_barriers else "unknown factors"
            message = f"""
            🌱 Today didn't work out. That's data, not failure.
            
            Barriers identified: {barriers}
            
            What's one tiny adjustment for tomorrow?
            """
            state.validated = True
            state.validation_message = message

        return message.strip()

    def validate_all_internal_states(self, user_id: str) -> Dict:
        """Validate all internal states for a user."""
        user_states = [
            s for s in self.internal_states.values()
            if s.user_id == user_id
        ]

        validated = 0
        messages = []

        for state in user_states:
            if not state.validated:
                message = self.validate_internal_state(state.id)
                messages.append({
                    "activity_id": state.activity_id,
                    "completed": state.completed,
                    "emotional_context": state.emotional_context.value,
                    "resistance": state.internal_resistance,
                    "validation_message": message
                })
                validated += 1

        return {
            "total_states": len(user_states),
            "validated": validated,
            "messages": messages
        }

    # =============================================================================
    # COMBINED VALIDATION (Sensor + Internal)
    # =============================================================================

    def validate_all(self, user_id: str) -> Dict:
        """Validate all data for a user (sensor + internal states)."""
        # Sensor data validation
        sensor_result = self._validate_sensor_data(user_id)
        
        # Internal state validation
        internal_result = self.validate_all_internal_states(user_id)

        return {
            "sensor_data": sensor_result,
            "internal_states": internal_result,
            "total_data_points": sensor_result["total_points"] + internal_result["total_states"],
            "overall_validation_rate": (
                (sensor_result["validated"] + internal_result["validated"]) /
                max(1, sensor_result["total_points"] + internal_result["total_states"]) * 100
            )
        }

    def _validate_sensor_data(self, user_id: str) -> Dict:
        """Validate sensor data only."""
        user_points = [
            p for p in self.data_points.values()
            if p.user_id == user_id
        ]

        validated = 0
        flagged = 0
        anomalies = []

        for point in user_points:
            result = self.validate(point.id)
            if result.is_valid:
                validated += 1
            else:
                flagged += 1
                anomalies.append({
                    "source": point.source.value,
                    "value": point.value,
                    "anomaly": result.anomaly_type.value if result.anomaly_type else "unknown",
                    "details": result.details
                })

        return {
            "total_points": len(user_points),
            "validated": validated,
            "flagged": flagged,
            "validation_rate": (validated / len(user_points) * 100) if user_points else 0,
            "anomalies": anomalies
        }

    def get_data_summary(self, user_id: str) -> Dict:
        """Get summary of user's invisible data (sensor + internal)."""
        sensor_summary = self._get_sensor_summary(user_id)
        internal_summary = self._get_internal_summary(user_id)

        return {
            "sensor_data": sensor_summary,
            "internal_states": internal_summary,
            "combined_insights": self._generate_combined_insights(user_id)
        }

    def _get_sensor_summary(self, user_id: str) -> Dict:
        """Get sensor data summary."""
        user_points = [
            p for p in self.data_points.values()
            if p.user_id == user_id
        ]

        # Group by source
        by_source = {}
        for point in user_points:
            source = point.source.value
            if source not in by_source:
                by_source[source] = {"count": 0, "values": []}
            by_source[source]["count"] += 1
            by_source[source]["values"].append(point.value)

        # Calculate averages
        for source, data in by_source.items():
            if data["values"]:
                data["avg"] = sum(data["values"]) / len(data["values"])
                data["min"] = min(data["values"])
                data["max"] = max(data["values"])

        return {
            "total_points": len(user_points),
            "sources": list(by_source.keys()),
            "by_source": by_source
        }

    def _get_internal_summary(self, user_id: str) -> Dict:
        """Get internal state summary."""
        user_states = [
            s for s in self.internal_states.values()
            if s.user_id == user_id
        ]

        if not user_states:
            return {"total_states": 0, "insights": []}

        # Calculate averages
        avg_quality = sum(s.completion_quality for s in user_states) / len(user_states)
        avg_resistance = sum(s.internal_resistance for s in user_states) / len(user_states)
        completion_rate = sum(1 for s in user_states if s.completed) / len(user_states)

        # Emotional context distribution
        emotion_counts = {}
        for state in user_states:
            emotion = state.emotional_context.value
            emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1

        return {
            "total_states": len(user_states),
            "avg_completion_quality": avg_quality,
            "avg_internal_resistance": avg_resistance,
            "completion_rate": completion_rate,
            "emotional_context_distribution": emotion_counts,
            "insights": self._generate_internal_insights(user_states)
        }

    def _generate_internal_insights(self, states: List[InternalStateData]) -> List[str]:
        """Generate insights from internal state patterns."""
        insights = []

        if not states:
            return insights

        # High resistance but completing = grit
        high_resistance_completions = [
            s for s in states if s.completed and s.internal_resistance >= 7
        ]
        if high_resistance_completions:
            insights.append(f"🏆 You've shown grit {len(high_resistance_completions)} times - completing despite high resistance")

        # Guilt after missing = abandonment risk
        guilty_misses = [
            s for s in states if not s.completed and s.emotional_context == EmotionalContext.GUILTY
        ]
        if guilty_misses:
            insights.append("💚 Consider self-compassion practices - guilt after missing can lead to abandonment")

        # Enthusiastic completions = sustainable
        enthusiastic = [
            s for s in states if s.completed and s.emotional_context == EmotionalContext.ENTHUSIASTIC
        ]
        if enthusiastic:
            insights.append(f"🎉 {len(enthusiastic)} enthusiastic completions - this is sustainable habit energy!")

        return insights

    def _generate_combined_insights(self, user_id: str) -> List[str]:
        """Generate combined insights from sensor + internal data."""
        insights = []

        # Example: High step count but high stress
        steps_data = [p for p in self.data_points.values() if p.user_id == user_id and p.source == DataSource.STEP_COUNT]
        stress_states = [s for s in self.internal_states.values() if s.user_id == user_id and s.emotional_context == EmotionalContext.ANXIOUS]

        if steps_data and stress_states:
            avg_steps = sum(p.value for p in steps_data) / len(steps_data)
            if avg_steps > 10000:
                insights.append("⚖️ High activity but high stress - consider rest days for recovery")

        return insights


def create_validator() -> InvisibleDataValidator:
    """Factory function."""
    return InvisibleDataValidator()
