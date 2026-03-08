"""
Habit Experiment Model - A/B testing for habits.

Allows users to test different approaches to habits:
- Morning vs Evening
- 5 min vs 10 min duration
- Different locations or methods

Usage:
    from brain.models.experiment import HabitExperiment, ExperimentStatus
"""
from enum import Enum
from dataclasses import dataclass, field
from datetime import datetime, date
from typing import Optional, Dict, Any, List
import uuid


class ExperimentStatus(str, Enum):
    """Status of an experiment."""
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    ANALYZING = "analyzing"
    ARCHIVED = "archived"


class ExperimentType(str, Enum):
    """Type of experiment."""
    TIMING = "timing"  # Morning vs Evening
    DURATION = "duration"  # 5 min vs 10 min
    LOCATION = "location"  # Home vs Gym
    METHOD = "method"  # Different approaches
    CUSTOM = "custom"


@dataclass
class ExperimentVariant:
    """
    A variant in an experiment (A or B).

    Attributes:
        id: Unique identifier
        name: Variant name (A or B)
        description: What makes this variant different
        target_value: Target for this variant
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = "A"
    description: str = ""
    target_value: Any = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "target_value": self.target_value
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExperimentVariant":
        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            name=data.get("name", "A"),
            description=data.get("description", ""),
            target_value=data.get("target_value")
        )


@dataclass
class HabitExperiment:
    """
    A habit experiment (A/B test).

    Attributes:
        id: Unique identifier
        habit_id: Habit being tested
        user_id: User ID
        name: Experiment name
        experiment_type: Type of experiment
        hypothesis: What you're testing
        variant_a: First variant
        variant_b: Second variant
        duration_days: How long to run
        success_metric: How to measure success
        status: Current status
        start_date: When started
        end_date: When ended
        results: Experiment results
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    habit_id: str = ""
    user_id: str = ""
    name: str = ""
    experiment_type: ExperimentType = ExperimentType.CUSTOM
    hypothesis: str = ""
    variant_a: ExperimentVariant = field(default_factory=ExperimentVariant)
    variant_b: ExperimentVariant = field(default_factory=ExperimentVariant)
    duration_days: int = 7
    success_metric: str = "completion_rate"
    status: ExperimentStatus = ExperimentStatus.DRAFT
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    results: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "habit_id": self.habit_id,
            "user_id": self.user_id,
            "name": self.name,
            "experiment_type": self.experiment_type.value,
            "hypothesis": self.hypothesis,
            "variant_a": self.variant_a.to_dict(),
            "variant_b": self.variant_b.to_dict(),
            "duration_days": self.duration_days,
            "success_metric": self.success_metric,
            "status": self.status.value,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "results": self.results,
            "created_at": self.created_at.isoformat()
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "HabitExperiment":
        # Handle variant_a and variant_b which may be stored as JSON strings in SQLite
        def parse_variant(v):
            if isinstance(v, dict):
                return v
            elif isinstance(v, str):
                import json
                try:
                    return json.loads(v)
                except:
                    return {}
            return {}
        
        variant_a_data = data.get("variant_a", {})
        variant_b_data = data.get("variant_b", {})
        
        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            habit_id=data.get("habit_id", ""),
            user_id=data.get("user_id", ""),
            name=data.get("name", ""),
            experiment_type=ExperimentType(data.get("experiment_type", "custom")),
            hypothesis=data.get("hypothesis", ""),
            variant_a=ExperimentVariant.from_dict(parse_variant(variant_a_data)),
            variant_b=ExperimentVariant.from_dict(parse_variant(variant_b_data)),
            duration_days=data.get("duration_days", 7),
            success_metric=data.get("success_metric", "completion_rate"),
            status=ExperimentStatus(data.get("status", "draft")),
            start_date=date.fromisoformat(data["start_date"]) if data.get("start_date") else None,
            end_date=date.fromisoformat(data["end_date"]) if data.get("end_date") else None,
            results=data.get("results", {}),
            created_at=datetime.fromisoformat(data["created_at"]) if data.get("created_at") else datetime.now()
        )

    def calculate_significance(self) -> Dict[str, Any]:
        """
        Calculate statistical significance.

        Returns:
            Significance data dict
        """
        # Simplified calculation
        # In production, use proper statistical tests
        variant_a_rate = self.results.get("variant_a_rate", 0)
        variant_b_rate = self.results.get("variant_b_rate", 0)

        difference = variant_b_rate - variant_a_rate
        relative_change = (difference / variant_a_rate * 100) if variant_a_rate > 0 else 0

        # Simplified confidence (not statistically rigorous)
        confidence = "low"
        if abs(difference) > 0.2:
            confidence = "medium"
        if abs(difference) > 0.4:
            confidence = "high"

        return {
            "difference": difference,
            "relative_change": relative_change,
            "confidence": confidence,
            "winner": "B" if difference > 0.05 else "A" if difference < -0.05 else "tie"
        }


@dataclass
class ExperimentResult:
    """
    Result of an experiment period.

    Attributes:
        id: Unique identifier
        experiment_id: Experiment ID
        variant: Which variant (A or B)
        date: Date of result
        completed: Whether habit was completed
        notes: Optional notes
    """
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    experiment_id: str = ""
    variant: str = "A"
    date: date = field(default_factory=date.today)
    completed: bool = False
    notes: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "experiment_id": self.experiment_id,
            "variant": self.variant,
            "date": self.date.isoformat(),
            "completed": self.completed,
            "notes": self.notes
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExperimentResult":
        return cls(
            id=data.get("id", str(uuid.uuid4())[:8]),
            experiment_id=data.get("experiment_id", ""),
            variant=data.get("variant", "A"),
            date=date.fromisoformat(data["date"]) if data.get("date") else date.today(),
            completed=data.get("completed", False),
            notes=data.get("notes", "")
        )


# Pre-defined experiment templates
EXPERIMENT_TEMPLATES = {
    "morning_vs_evening": {
        "type": ExperimentType.TIMING,
        "name": "Morning vs Evening",
        "hypothesis": "I will be more consistent in the morning",
        "variant_a": {"name": "Morning", "description": "Before 12 PM"},
        "variant_b": {"name": "Evening", "description": "After 6 PM"},
        "duration_days": 14
    },
    "short_vs_long": {
        "type": ExperimentType.DURATION,
        "name": "5 min vs 10 min",
        "hypothesis": "Shorter duration will have better consistency",
        "variant_a": {"name": "5 minutes", "description": "Just 5 minutes"},
        "variant_b": {"name": "10 minutes", "description": "Full 10 minutes"},
        "duration_days": 14
    },
    "home_vs_gym": {
        "type": ExperimentType.LOCATION,
        "name": "Home vs Gym",
        "hypothesis": "Working out at home will be more consistent",
        "variant_a": {"name": "Home", "description": "Work out at home"},
        "variant_b": {"name": "Gym", "description": "Work out at gym"},
        "duration_days": 21
    }
}


def create_experiment_from_template(
    template_key: str,
    habit_id: str,
    user_id: str
) -> HabitExperiment:
    """
    Create experiment from template.

    Args:
        template_key: Template key
        habit_id: Habit ID
        user_id: User ID

    Returns:
        HabitExperiment object
    """
    template = EXPERIMENT_TEMPLATES.get(template_key)
    if not template:
        raise ValueError(f"Unknown template: {template_key}")

    return HabitExperiment(
        habit_id=habit_id,
        user_id=user_id,
        name=template["name"],
        experiment_type=template["type"],
        hypothesis=template["hypothesis"],
        variant_a=ExperimentVariant(**template["variant_a"]),
        variant_b=ExperimentVariant(**template["variant_b"]),
        duration_days=template["duration_days"]
    )


__all__ = [
    "ExperimentStatus",
    "ExperimentType",
    "ExperimentVariant",
    "HabitExperiment",
    "ExperimentResult",
    "EXPERIMENT_TEMPLATES",
    "create_experiment_from_template",
]
