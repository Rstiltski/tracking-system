"""
Experiment Tracker - Track and analyze habit experiments.

Usage:
    from brain.analytics.experiment_tracker import ExperimentTracker
    
    tracker = ExperimentTracker(storage, user_id)
    tracker.create_experiment(experiment_data)
"""
from typing import List, Dict, Any, Optional
from brain.models.experiment import (
    HabitExperiment,
    ExperimentResult,
    ExperimentStatus,
    ExperimentType,
)


class ExperimentTracker:
    """
    Tracks habit experiments.

    Usage:
        tracker = ExperimentTracker(storage, user_id)
    """

    def __init__(self, storage: Any, user_id: str = ""):
        """
        Initialize experiment tracker.

        Args:
            storage: Storage instance
            user_id: User ID
        """
        self.storage = storage
        self.user_id = user_id

    def create_experiment(
        self,
        habit_id: str,
        name: str,
        hypothesis: str,
        variant_a: Dict[str, Any],
        variant_b: Dict[str, Any],
        experiment_type: str = "custom",
        duration_days: int = 7
    ) -> HabitExperiment:
        """
        Create a new experiment.

        Args:
            habit_id: Habit ID
            name: Experiment name
            hypothesis: What you're testing
            variant_a: Variant A config
            variant_b: Variant B config
            experiment_type: Type of experiment
            duration_days: Duration

        Returns:
            Created HabitExperiment
        """
        from brain.models.experiment import ExperimentVariant
        
        experiment = HabitExperiment(
            habit_id=habit_id,
            user_id=self.user_id,
            name=name,
            experiment_type=ExperimentType(experiment_type),
            hypothesis=hypothesis,
            variant_a=ExperimentVariant(**variant_a),
            variant_b=ExperimentVariant(**variant_b),
            duration_days=duration_days
        )

        # Save to storage
        if hasattr(self.storage, 'save_experiment'):
            self.storage.save_experiment(experiment.to_dict())

        return experiment

    def get_experiments(
        self,
        status: Optional[ExperimentStatus] = None
    ) -> List[HabitExperiment]:
        """
        Get user's experiments.

        Args:
            status: Optional status filter

        Returns:
            List of experiments
        """
        if hasattr(self.storage, 'get_experiments'):
            experiments_data = self.storage.get_experiments(self.user_id, status.value if status else None)
            return [HabitExperiment.from_dict(e) for e in experiments_data]
        return []

    def get_active_experiment(self, habit_id: str) -> Optional[HabitExperiment]:
        """
        Get active experiment for a habit.

        Args:
            habit_id: Habit ID

        Returns:
            Active experiment or None
        """
        experiments = self.get_experiments(ExperimentStatus.ACTIVE)
        for exp in experiments:
            if exp.habit_id == habit_id:
                return exp
        return None

    def record_result(
        self,
        experiment_id: str,
        variant: str,
        completed: bool,
        notes: str = ""
    ) -> ExperimentResult:
        """
        Record experiment result.

        Args:
            experiment_id: Experiment ID
            variant: Which variant (A or B)
            completed: Whether completed
            notes: Optional notes

        Returns:
            Created ExperimentResult
        """
        result = ExperimentResult(
            experiment_id=experiment_id,
            variant=variant,
            completed=completed,
            notes=notes
        )

        if hasattr(self.storage, 'save_experiment_result'):
            self.storage.save_experiment_result(result.to_dict())

        return result

    def calculate_results(self, experiment_id: str) -> Dict[str, Any]:
        """
        Calculate experiment results.

        Args:
            experiment_id: Experiment ID

        Returns:
            Results dict
        """
        if hasattr(self.storage, 'get_experiment_results'):
            results_data = self.storage.get_experiment_results(experiment_id)
            
            # Calculate rates
            variant_a = [r for r in results_data if r.get('variant') == 'A']
            variant_b = [r for r in results_data if r.get('variant') == 'B']

            a_rate = sum(1 for r in variant_a if r.get('completed', False)) / len(variant_a) if variant_a else 0
            b_rate = sum(1 for r in variant_b if r.get('completed', False)) / len(variant_b) if variant_b else 0

            return {
                "variant_a_rate": a_rate,
                "variant_b_rate": b_rate,
                "variant_a_count": len(variant_a),
                "variant_b_count": len(variant_b)
            }

        return {}

    def end_experiment(
        self,
        experiment_id: str,
        results: Optional[Dict[str, Any]] = None
    ) -> bool:
        """
        End an experiment.

        Args:
            experiment_id: Experiment ID
            results: Optional results data

        Returns:
            True if ended
        """
        if hasattr(self.storage, 'end_experiment'):
            return self.storage.end_experiment(experiment_id, results)
        return False


__all__ = [
    "ExperimentTracker",
]
