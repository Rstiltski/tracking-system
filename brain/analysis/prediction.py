"""
Predictive Context Sensitivity (PCS) Module

Implements PCS scoring to measure how much a habit depends on context factors.
Based on research from habit formation studies.

PCS Score Interpretation:
- 0-39%: Robust habit (low context dependency, mostly automatic)
- 40-69%: Moderate sensitivity (some context factors matter)
- 70-100%: Fragile habit (high context dependency, needs protection)
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime
import math


@dataclass
class ContextVariables:
    """
    Context factors that may influence habit completion.
    
    These variables are tracked to understand which factors
    affect habit success rates.
    """
    date: str = ""  # ISO date string
    sleep_hours: Optional[float] = None
    stress_level: Optional[int] = None  # 1-10 scale
    weather_score: Optional[float] = None  # 0-1 (bad to good weather)
    day_of_week: Optional[int] = None  # 0-6 (Monday=0)
    num_events: Optional[int] = None  # Calendar events that day
    mood_score: Optional[float] = None  # 0-1 (bad to good mood)
    location_home: Optional[bool] = None
    previous_day_completion: Optional[float] = None  # % of habits completed
    energy_level: Optional[int] = None  # 1-10 scale
    sleep_quality: Optional[float] = None  # 0-1 (poor to excellent)
    
    def to_feature_vector(self) -> List[float]:
        """Convert context to normalized feature vector for ML."""
        return [
            (self.sleep_hours or 7.0) / 12.0,  # Normalize to 0-1
            (self.stress_level or 5) / 10.0,
            self.weather_score or 0.5,
            (self.day_of_week or 0) / 6.0,
            min(1.0, (self.num_events or 0) / 10.0),
            self.mood_score or 0.5,
            1.0 if self.location_home else 0.5 if self.location_home is None else 0.0,
            self.previous_day_completion or 0.5,
            (self.energy_level or 5) / 10.0,
            self.sleep_quality or 0.5
        ]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'date': self.date,
            'sleep_hours': self.sleep_hours,
            'stress_level': self.stress_level,
            'weather_score': self.weather_score,
            'day_of_week': self.day_of_week,
            'num_events': self.num_events,
            'mood_score': self.mood_score,
            'location_home': self.location_home,
            'previous_day_completion': self.previous_day_completion,
            'energy_level': self.energy_level,
            'sleep_quality': self.sleep_quality
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ContextVariables':
        """Create from dictionary."""
        return cls(
            date=data.get('date', ''),
            sleep_hours=data.get('sleep_hours'),
            stress_level=data.get('stress_level'),
            weather_score=data.get('weather_score'),
            day_of_week=data.get('day_of_week'),
            num_events=data.get('num_events'),
            mood_score=data.get('mood_score'),
            location_home=data.get('location_home'),
            previous_day_completion=data.get('previous_day_completion'),
            energy_level=data.get('energy_level'),
            sleep_quality=data.get('sleep_quality')
        )


@dataclass
class PCSScore:
    """
    Predictive Context Sensitivity score for a habit.
    
    Higher scores indicate the habit is more sensitive to context
    and may need protection or environmental design.
    """
    habit_id: str
    habit_name: str
    pcs_score: float  # 0-100%
    context_factors: Dict[str, float]  # Factor name -> importance weight
    baseline_rate: float  # Average completion rate
    predicted_rate: float  # Context-adjusted predicted rate
    sample_size: int = 0
    confidence: float = 0.0  # 0-1 based on sample size
    calculated_at: datetime = field(default_factory=datetime.now)
    
    @property
    def fragility(self) -> str:
        """Interpret PCS as fragility level."""
        if self.pcs_score >= 70:
            return "fragile"
        elif self.pcs_score >= 40:
            return "moderate"
        return "robust"
    
    @property
    def fragility_emoji(self) -> str:
        """Get emoji for fragility level."""
        if self.pcs_score >= 70:
            return "⚠️"
        elif self.pcs_score >= 40:
            return "🔶"
        return "✅"
    
    @property
    def top_factors(self) -> List[Tuple[str, float]]:
        """Get top 3 context factors by importance."""
        sorted_factors = sorted(
            self.context_factors.items(), 
            key=lambda x: abs(x[1]), 
            reverse=True
        )
        return sorted_factors[:3]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'habit_id': self.habit_id,
            'habit_name': self.habit_name,
            'pcs_score': self.pcs_score,
            'fragility': self.fragility,
            'context_factors': self.context_factors,
            'baseline_rate': self.baseline_rate,
            'predicted_rate': self.predicted_rate,
            'sample_size': self.sample_size,
            'confidence': self.confidence,
            'calculated_at': self.calculated_at.isoformat()
        }


class PCSEngine:
    """
    Predictive Context Sensitivity calculation engine.
    
    Uses simplified LASSO regression to identify which context factors
    influence habit completion and calculate a fragility score.
    
    Example:
        engine = PCSEngine()
        
        # Calculate PCS for a habit
        score = engine.calculate_pcs(
            habit_id="habit-123",
            habit_name="Morning Run",
            completion_history=[True, False, True, True, ...],
            context_history=[ContextVariables(...), ...]
        )
        
        print(f"PCS Score: {score.pcs_score}%")
        print(f"Fragility: {score.fragility}")
        print(f"Top factors: {score.top_factors}")
    """
    
    FEATURE_NAMES = [
        'sleep_hours', 'stress_level', 'weather_score',
        'day_of_week', 'num_events', 'mood_score',
        'location_home', 'prev_completion', 'energy_level', 'sleep_quality'
    ]
    
    def __init__(self, regularization: float = 0.1, min_samples: int = 7):
        """
        Initialize PCS engine.
        
        Args:
            regularization: LASSO regularization strength (higher = more sparse)
            min_samples: Minimum samples needed for calculation
        """
        self.regularization = regularization
        self.min_samples = min_samples
        self.weights: Dict[str, float] = {}
        self.intercept: float = 0.5
    
    def calculate_pcs(
        self,
        habit_id: str,
        habit_name: str,
        completion_history: List[bool],
        context_history: List[ContextVariables]
    ) -> PCSScore:
        """
        Calculate PCS score for a habit.
        
        Args:
            habit_id: Unique identifier for the habit
            habit_name: Display name of the habit
            completion_history: List of completion status (True/False)
            context_history: List of context variables for each day
            
        Returns:
            PCSScore with fragility assessment
        """
        n = len(completion_history)
        
        # Handle insufficient data
        if n < self.min_samples:
            return PCSScore(
                habit_id=habit_id,
                habit_name=habit_name,
                pcs_score=0.0,
                context_factors={},
                baseline_rate=sum(completion_history) / n if n > 0 else 0.0,
                predicted_rate=0.0,
                sample_size=n,
                confidence=0.0
            )
        
        # Calculate baseline completion rate
        baseline_rate = sum(completion_history) / n
        
        # Prepare features
        X, y = self._prepare_features(context_history, completion_history)
        
        # Fit LASSO regression
        self._fit_lasso(X, y)
        
        # Calculate predictions
        predictions = [self._predict(x) for x in X]
        predicted_rate = sum(predictions) / len(predictions)
        
        # Calculate PCS score
        # PCS measures how much context affects the habit
        # High PCS = completion rate varies significantly with context
        if baseline_rate > 0:
            # Variance in predictions indicates context sensitivity
            variance = sum((p - predicted_rate) ** 2 for p in predictions) / len(predictions)
            # Normalize to 0-100 scale
            pcs = min(100, variance * 400)  # Scale factor for interpretability
            
            # Also consider how much predictions deviate from baseline
            deviation = abs(predicted_rate - baseline_rate) / max(baseline_rate, 0.01)
            pcs = (pcs + deviation * 50) / 2  # Average of variance and deviation
        else:
            pcs = 0.0
        
        # Get feature importance from weights
        context_factors = {}
        for i, name in enumerate(self.FEATURE_NAMES):
            weight = self.weights.get(f"f{i}", 0.0)
            if abs(weight) > 0.01:  # Only include non-zero weights
                context_factors[name] = round(abs(weight), 4)
        
        # Calculate confidence based on sample size
        confidence = min(1.0, n / 30.0)  # Full confidence at 30+ samples
        
        return PCSScore(
            habit_id=habit_id,
            habit_name=habit_name,
            pcs_score=round(min(100, max(0, pcs)), 1),
            context_factors=context_factors,
            baseline_rate=round(baseline_rate, 3),
            predicted_rate=round(predicted_rate, 3),
            sample_size=n,
            confidence=round(confidence, 2)
        )
    
    def analyze_all_habits(
        self,
        habits_data: Dict[str, Tuple[str, List[bool], List[ContextVariables]]]
    ) -> List[PCSScore]:
        """
        Calculate PCS scores for multiple habits.
        
        Args:
            habits_data: Dict mapping habit_id to (name, completions, contexts)
            
        Returns:
            List of PCSScores sorted by fragility (most fragile first)
        """
        scores = []
        
        for habit_id, (name, completions, contexts) in habits_data.items():
            score = self.calculate_pcs(habit_id, name, completions, contexts)
            scores.append(score)
        
        # Sort by PCS score (most fragile first)
        scores.sort(key=lambda s: s.pcs_score, reverse=True)
        return scores
    
    def get_protection_recommendations(self, score: PCSScore) -> List[str]:
        """
        Generate recommendations for protecting a fragile habit.
        
        Args:
            score: PCSScore for the habit
            
        Returns:
            List of actionable recommendations
        """
        recommendations = []
        
        if score.fragility == "robust":
            recommendations.append(
                f"✅ {score.habit_name} is well-established. Keep up the great work!"
            )
            return recommendations
        
        # Analyze top factors
        for factor, weight in score.top_factors:
            if factor == "sleep_hours" and weight > 0.1:
                recommendations.append(
                    "😴 This habit is sensitive to sleep. "
                    "Prioritize 7-8 hours of sleep for better success."
                )
            elif factor == "stress_level" and weight > 0.1:
                recommendations.append(
                    "🧘 Stress affects this habit. "
                    "Consider a brief mindfulness practice before the habit."
                )
            elif factor == "energy_level" and weight > 0.1:
                recommendations.append(
                    "⚡ Energy levels matter for this habit. "
                    "Schedule it during your peak energy hours."
                )
            elif factor == "day_of_week" and weight > 0.1:
                recommendations.append(
                    "📅 This habit varies by day. "
                    "Consider different approaches for different days."
                )
            elif factor == "location_home" and weight > 0.1:
                recommendations.append(
                    "🏠 Location affects this habit. "
                    "Create a consistent environment for habit execution."
                )
            elif factor == "prev_completion" and weight > 0.1:
                recommendations.append(
                    "🔗 Momentum matters. "
                    "Focus on not breaking the chain once started."
                )
            elif factor == "num_events" and weight > 0.1:
                recommendations.append(
                    "📆 Busy days affect this habit. "
                    "Set a reminder or reduce the habit size on busy days."
                )
        
        if score.fragility == "fragile":
            recommendations.insert(0,
                f"⚠️ {score.habit_name} needs protection. "
                "Consider habit stacking or environmental design."
            )
        elif score.fragility == "moderate":
            recommendations.insert(0,
                f"🔶 {score.habit_name} has moderate sensitivity. "
                "Monitor the factors above for best results."
            )
        
        return recommendations
    
    def _prepare_features(
        self,
        context_history: List[ContextVariables],
        completion_history: List[bool]
    ) -> Tuple[List[List[float]], List[float]]:
        """Prepare feature matrix and target vector."""
        X = []
        y = []
        
        for ctx, completed in zip(context_history, completion_history):
            X.append(ctx.to_feature_vector())
            y.append(1.0 if completed else 0.0)
        
        return X, y
    
    def _fit_lasso(self, X: List[List[float]], y: List[float]) -> None:
        """
        Fit LASSO regression using coordinate descent.
        
        LASSO (Least Absolute Shrinkage and Selection Operator) performs
        feature selection by driving some weights to exactly zero.
        """
        n_features = len(X[0]) if X else 0
        n_samples = len(X)
        
        if n_features == 0 or n_samples == 0:
            return
        
        # Initialize weights
        self.weights = {f"f{i}": 0.0 for i in range(n_features)}
        self.intercept = sum(y) / n_samples
        
        # Coordinate descent with soft thresholding
        for iteration in range(100):
            weights_changed = False
            
            for j in range(n_features):
                # Compute partial residual
                rho = 0.0
                for i in range(n_samples):
                    # Prediction without feature j
                    pred = self.intercept
                    for k in range(n_features):
                        if k != j:
                            pred += self.weights[f"f{k}"] * X[i][k]
                    residual = y[i] - pred
                    rho += X[i][j] * residual
                
                rho /= n_samples
                
                # Soft thresholding (LASSO penalty)
                old_weight = self.weights[f"f{j}"]
                if rho < -self.regularization:
                    self.weights[f"f{j}"] = rho + self.regularization
                elif rho > self.regularization:
                    self.weights[f"f{j}"] = rho - self.regularization
                else:
                    self.weights[f"f{j}"] = 0.0
                
                if abs(self.weights[f"f{j}"] - old_weight) > 1e-6:
                    weights_changed = True
            
            # Update intercept
            self.intercept = sum(y) / n_samples
            for j in range(n_features):
                self.intercept -= self.weights[f"f{j}"] * sum(X[i][j] for i in range(n_samples)) / n_samples
            
            # Early stopping if converged
            if not weights_changed:
                break
    
    def _predict(self, x: List[float]) -> float:
        """Predict completion probability using sigmoid."""
        z = self.intercept
        for j, val in enumerate(x):
            z += self.weights.get(f"f{j}", 0.0) * val
        
        # Sigmoid function with clamping
        z = max(-10, min(10, z))
        return 1.0 / (1.0 + math.exp(-z))
    
    def get_feature_importance(self) -> Dict[str, float]:
        """Get current feature importance from fitted model."""
        return {
            name: abs(self.weights.get(f"f{i}", 0.0))
            for i, name in enumerate(self.FEATURE_NAMES)
            if abs(self.weights.get(f"f{i}", 0.0)) > 0.01
        }