"""
N-of-1 Experiment Tools

User as researcher - personal A/B testing.

Based on Task 11.3.3 from PHASE_11_INTEGRATION_ROADMAP.md

User as researcher - personal A/B testing!
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Dict, List, Optional


# =============================================================================
# TYPES
# =============================================================================

class ExperimentStatus(Enum):
    """Status of an experiment."""
    DRAFT = "draft"
    RUNNING = "running"
    COMPLETED = "completed"
    PAUSED = "paused"


class VariableType(Enum):
    """Types of variables."""
    HABIT = "habit"
    ENVIRONMENT = "environment"
    TIMING = "timing"
    TRIGGER = "trigger"
    REWARD = "reward"


# =============================================================================
# MODELS
# =============================================================================

@dataclass
class Experiment:
    """An N-of-1 experiment."""
    id: str
    user_id: str
    name: str
    description: str
    
    # Hypothesis
    hypothesis: str
    
    # Variables
    independent_variable: str  # What you change
    dependent_variable: str  # What you measure
    
    # Design
    duration_days: int
    start_date: Optional[datetime] = None
    
    # Status
    status: ExperimentStatus = ExperimentStatus.DRAFT
    
    # Results
    observations: List[str] = field(default_factory=list)


@dataclass
class Observation:
    """An observation during experiment."""
    id: str
    experiment_id: str
    timestamp: datetime
    condition: str  # A or B
    value: float
    notes: str = ""


# =============================================================================
# N-OF-1 EXPERIMENT ENGINE
# =============================================================================

class ExperimentEngine:
    """
    N-of-1 experiments - personal A/B testing.
    
    Features:
    - Experiment design
    - Data collection
    - Statistical analysis (simple)
    - Results interpretation
    """
    
    def __init__(self):
        """Initialize the engine."""
        self.experiments: Dict[str, Experiment] = {}
        self.observations: Dict[str, List[Observation]] = {}
    
    def create_experiment(
        self,
        user_id: str,
        name: str,
        description: str,
        hypothesis: str,
        independent_variable: str,
        dependent_variable: str,
        duration_days: int
    ) -> Experiment:
        """Create an experiment."""
        import uuid
        
        exp = Experiment(
            id=str(uuid.uuid4()),
            user_id=user_id,
            name=name,
            description=description,
            hypothesis=hypothesis,
            independent_variable=independent_variable,
            dependent_variable=dependent_variable,
            duration_days=duration_days
        )
        
        self.experiments[exp.id] = exp
        self.observations[exp.id] = []
        
        return exp
    
    def start_experiment(self, experiment_id: str) -> None:
        """Start an experiment."""
        exp = self.experiments.get(experiment_id)
        if exp:
            exp.status = ExperimentStatus.RUNNING
            exp.start_date = datetime.now()
    
    def pause_experiment(self, experiment_id: str) -> None:
        """Pause an experiment."""
        exp = self.experiments.get(experiment_id)
        if exp:
            exp.status = ExperimentStatus.PAUSED
    
    def record_observation(
        self,
        experiment_id: str,
        condition: str,
        value: float,
        notes: str = ""
    ) -> Observation:
        """Record an observation."""
        import uuid
        
        obs = Observation(
            id=str(uuid.uuid4()),
            experiment_id=experiment_id,
            timestamp=datetime.now(),
            condition=condition,
            value=value,
            notes=notes
        )
        
        self.observations[experiment_id].append(obs)
        return obs
    
    def analyze_results(self, experiment_id: str) -> Dict:
        """Analyze experiment results."""
        exp = self.experiments.get(experiment_id)
        if not exp:
            return {}
        
        obs = self.observations.get(experiment_id, [])
        
        # Separate by condition
        condition_a = [o.value for o in obs if o.condition == "A"]
        condition_b = [o.value for o in obs if o.condition == "B"]
        
        avg_a = sum(condition_a) / len(condition_a) if condition_a else 0
        avg_b = sum(condition_b) / len(condition_b) if condition_b else 0
        
        # Determine winner
        if len(condition_a) >= 3 and len(condition_b) >= 3:
            if avg_a > avg_b:
                winner = "A"
                improvement = ((avg_a - avg_b) / avg_b) * 100 if avg_b > 0 else 0
            elif avg_b > avg_a:
                winner = "B"
                improvement = ((avg_b - avg_a) / avg_a) * 100 if avg_a > 0 else 0
            else:
                winner = "tie"
                improvement = 0
        else:
            winner = "insufficient_data"
            improvement = 0
        
        return {
            "experiment_name": exp.name,
            "total_observations": len(obs),
            "condition_a_count": len(condition_a),
            "condition_b_count": len(condition_b),
            "condition_a_avg": avg_a,
            "condition_b_avg": avg_b,
            "winner": winner,
            "improvement_pct": improvement,
            "status": exp.status.value
        }
    
    def get_user_experiments(self, user_id: str) -> List[Experiment]:
        """Get all experiments for a user."""
        return [e for e in self.experiments.values() if e.user_id == user_id]


def create_engine() -> ExperimentEngine:
    """Factory function."""
    return ExperimentEngine()
