"""
Predictive Context Sensitivity (PCS) Module

Implements PCS scoring to measure how much a habit depends on context factors.
Based on research from Buyalskaya, Ho, Milkman, et al. (2023) - 
"What can machine learning teach us about habit formation?" PNAS.

Key Concepts:
- PCS (Predicting Context Sensitivity): Measures habit predictability from context
- AUC (Area Under Curve): Primary metric for habit strength
- Dependency Ratio: External vs Internal context dependency
- Fragility Index: Combined score indicating habit vulnerability

Fragility Interpretation:
- 0-39%: Robust habit (low context dependency, mostly automatic)
- 40-69%: Moderate sensitivity (some context factors matter)
- 70-100%: Fragile habit (high context dependency, needs protection)
"""

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime
import math
import random


# Feature classification for dependency analysis
INTERNAL_FEATURES = ['prev_completion']  # Autoregressive - self-sustaining
EXTERNAL_FEATURES = [
    'sleep_hours', 'stress_level', 'weather_score',
    'day_of_week', 'num_events', 'mood_score',
    'location_home', 'energy_level', 'sleep_quality'
]

FEATURE_NAMES = INTERNAL_FEATURES + EXTERNAL_FEATURES


@dataclass
class ContextVariables:
    """
    Context factors that may influence habit completion.
    
    These variables are tracked to understand which factors
    affect habit success rates. Based on research showing
    context stability is prerequisite for habit automatization.
    
    References:
    - Stojanovic et al. (2020, 2022) on context stability
    - Buyalskaya et al. (2023) on PCS measurement
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
        """
        Convert context to normalized feature vector for ML.
        
        Feature order matches FEATURE_NAMES constant.
        All values normalized to 0-1 range for LASSO regression.
        """
        return [
            # Internal features (autoregressive)
            self.previous_day_completion or 0.5,
            # External features
            (self.sleep_hours or 7.0) / 12.0,  # Normalize to 0-1
            (self.stress_level or 5) / 10.0,
            self.weather_score or 0.5,
            (self.day_of_week or 0) / 6.0,
            min(1.0, (self.num_events or 0) / 10.0),
            self.mood_score or 0.5,
            1.0 if self.location_home else 0.5 if self.location_home is None else 0.0,
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
    
    Based on Buyalskaya et al. (2023) PNAS research on habit formation.
    
    Key Metrics:
    - auc_score: Area Under ROC Curve (0-1), measures predictability
    - dependency_ratio: External vs Internal context dependency
    - fragility_index: Combined score (0-100) indicating habit vulnerability
    
    A rising AUC over time indicates habit consolidation.
    A fluctuating or low AUC despite high frequency suggests fragile behavior.
    """
    habit_id: str
    habit_name: str
    pcs_score: float  # 0-100% (legacy, now equals fragility_index)
    context_factors: Dict[str, float]  # Factor name -> importance weight
    baseline_rate: float  # Average completion rate
    predicted_rate: float  # Context-adjusted predicted rate
    sample_size: int = 0
    confidence: float = 0.0  # 0-1 based on sample size
    calculated_at: datetime = field(default_factory=datetime.now)
    
    # New fields from research paper
    auc_score: float = 0.5  # Area Under ROC Curve (0-1)
    dependency_ratio: float = 0.0  # External/Internal coefficient ratio
    autoregressive_weight: float = 0.0  # Self-prediction strength (Y_{t-1})
    external_dependency: Dict[str, float] = field(default_factory=dict)  # External factors only
    fragility_index: float = 0.0  # Combined 0-100 score
    internal_strength: float = 0.0  # Strength of autoregressive features
    external_sensitivity: float = 0.0  # Sensitivity to external context
    
    @property
    def fragility(self) -> str:
        """
        Interpret Fragility Index as fragility level.
        
        Based on research thresholds:
        - Robust: Behavior is automatic, low context dependency
        - Moderate: Some context sensitivity, monitor
        - Fragile: High context dependency, needs protection
        """
        if self.fragility_index >= 70:
            return "fragile"
        elif self.fragility_index >= 40:
            return "moderate"
        return "robust"
    
    @property
    def fragility_emoji(self) -> str:
        """Get emoji for fragility level."""
        if self.fragility_index >= 70:
            return "⚠️"
        elif self.fragility_index >= 40:
            return "🔶"
        return "✅"
    
    @property
    def habit_strength(self) -> str:
        """
        Interpret AUC as habit strength.
        
        AUC interpretation from research:
        - > 0.8: Strong habit (highly predictable)
        - 0.6-0.8: Moderate habit
        - 0.5-0.6: Weak/no habit (random or willpower-driven)
        """
        if self.auc_score >= 0.8:
            return "strong"
        elif self.auc_score >= 0.6:
            return "moderate"
        return "weak"
    
    @property
    def top_factors(self) -> List[Tuple[str, float]]:
        """Get top 3 context factors by importance."""
        sorted_factors = sorted(
            self.context_factors.items(), 
            key=lambda x: abs(x[1]), 
            reverse=True
        )
        return sorted_factors[:3]
    
    @property
    def top_external_factors(self) -> List[Tuple[str, float]]:
        """Get top 3 external context factors (excluding autoregressive)."""
        external = {k: v for k, v in self.context_factors.items() 
                    if k in EXTERNAL_FEATURES}
        sorted_factors = sorted(
            external.items(), 
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
            'fragility_index': self.fragility_index,
            'fragility': self.fragility,
            'habit_strength': self.habit_strength,
            'auc_score': self.auc_score,
            'dependency_ratio': self.dependency_ratio,
            'autoregressive_weight': self.autoregressive_weight,
            'context_factors': self.context_factors,
            'external_dependency': self.external_dependency,
            'baseline_rate': self.baseline_rate,
            'predicted_rate': self.predicted_rate,
            'sample_size': self.sample_size,
            'confidence': self.confidence,
            'internal_strength': self.internal_strength,
            'external_sensitivity': self.external_sensitivity,
            'calculated_at': self.calculated_at.isoformat()
        }


@dataclass
class LaggedCorrelationResult:
    """Result of time-lagged cross-correlation analysis."""
    lag_days: int
    correlation: float
    sample_size: int
    
    @property
    def strength(self) -> str:
        """Interpret correlation strength."""
        abs_r = abs(self.correlation)
        if abs_r >= 0.7:
            return "strong"
        elif abs_r >= 0.4:
            return "moderate"
        elif abs_r >= 0.2:
            return "weak"
        return "negligible"


@dataclass
class GrangerCausalityResult:
    """Result of Granger causality test."""
    context_variable: str
    f_statistic: float
    p_value: float
    is_significant: bool  # p < 0.05
    
    @property
    def strength(self) -> str:
        """Interpret causality strength based on F-statistic."""
        if self.f_statistic > 10:
            return "strong"
        elif self.f_statistic > 5:
            return "moderate"
        elif self.f_statistic > 2:
            return "weak"
        return "negligible"


class PCSEngine:
    """
    Predictive Context Sensitivity calculation engine.
    
    Implements the PCS algorithm from Buyalskaya et al. (2023) PNAS paper.
    Uses LASSO regression for feature selection and AUC for habit strength.
    
    Key Features:
    - LASSO regression with coordinate descent
    - ROC-AUC calculation for habit predictability
    - Dependency ratio (external vs internal factors)
    - Fragility Index combining multiple metrics
    - Time-lagged cross-correlation for vulnerability windows
    - Granger causality for identifying habit triggers
    
    Example:
        engine = PCSEngine()
        
        # Calculate PCS for a habit
        score = engine.calculate_pcs(
            habit_id="habit-123",
            habit_name="Morning Run",
            completion_history=[True, False, True, True, ...],
            context_history=[ContextVariables(...), ...]
        )
        
        print(f"AUC Score: {score.auc_score}")
        print(f"Fragility Index: {score.fragility_index}")
        print(f"Habit Strength: {score.habit_strength}")
        print(f"Top External Factors: {score.top_external_factors}")
    """
    
    def __init__(
        self, 
        regularization: float = 0.1, 
        min_samples: int = 14,
        auc_weight: float = 0.6,
        dependency_weight: float = 0.4
    ):
        """
        Initialize PCS engine.
        
        Args:
            regularization: LASSO regularization strength (higher = more sparse)
            min_samples: Minimum samples needed for calculation (14+ recommended)
            auc_weight: Weight for AUC in fragility calculation
            dependency_weight: Weight for dependency ratio in fragility calculation
        """
        self.regularization = regularization
        self.min_samples = min_samples
        self.auc_weight = auc_weight
        self.dependency_weight = dependency_weight
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
        Calculate PCS score for a habit using research-based algorithm.
        
        Implements the methodology from Buyalskaya et al. (2023):
        1. Fit LASSO logistic regression
        2. Calculate AUC for habit predictability
        3. Compute dependency ratio (external vs internal)
        4. Calculate Fragility Index
        
        Args:
            habit_id: Unique identifier for the habit
            habit_name: Display name of the habit
            completion_history: List of completion status (True/False)
            context_history: List of context variables for each day
            
        Returns:
            PCSScore with comprehensive fragility assessment
        """
        n = len(completion_history)
        
        # Handle insufficient data
        if n < self.min_samples:
            return self._create_insufficient_data_score(
                habit_id, habit_name, completion_history, n
            )
        
        # Calculate baseline completion rate
        baseline_rate = sum(completion_history) / n
        
        # Prepare features
        X, y = self._prepare_features(context_history, completion_history)
        
        # Split data for AUC calculation (70/30 split)
        split_idx = int(len(X) * 0.7)
        X_train, X_test = X[:split_idx], X[split_idx:]
        y_train, y_test = y[:split_idx], y[split_idx:]
        
        # Fit LASSO regression on training data
        self._fit_lasso(X_train, y_train)
        
        # Calculate predictions on test data
        predictions = [self._predict(x) for x in X_test]
        
        # Calculate AUC (primary metric from research)
        auc_score = self._calculate_auc(y_test, predictions)
        
        # Calculate all predictions for other metrics
        all_predictions = [self._predict(x) for x in X]
        predicted_rate = sum(all_predictions) / len(all_predictions)
        
        # Calculate dependency ratio
        dependency_ratio, internal_strength, external_sensitivity = \
            self._calculate_dependency_ratio()
        
        # Calculate Fragility Index using research formula
        fragility_index = self._calculate_fragility_index(
            auc_score, dependency_ratio
        )
        
        # Extract feature importance
        context_factors, external_dependency, autoregressive_weight = \
            self._extract_feature_importance()
        
        # Calculate confidence based on sample size
        confidence = min(1.0, n / 30.0)  # Full confidence at 30+ samples
        
        return PCSScore(
            habit_id=habit_id,
            habit_name=habit_name,
            pcs_score=round(fragility_index, 1),  # Legacy field
            fragility_index=round(fragility_index, 1),
            auc_score=round(auc_score, 3),
            dependency_ratio=round(dependency_ratio, 3),
            autoregressive_weight=round(autoregressive_weight, 4),
            context_factors=context_factors,
            external_dependency=external_dependency,
            baseline_rate=round(baseline_rate, 3),
            predicted_rate=round(predicted_rate, 3),
            sample_size=n,
            confidence=round(confidence, 2),
            internal_strength=round(internal_strength, 3),
            external_sensitivity=round(external_sensitivity, 3),
            calculated_at=datetime.now()
        )
    
    def _create_insufficient_data_score(
        self,
        habit_id: str,
        habit_name: str,
        completion_history: List[bool],
        n: int
    ) -> PCSScore:
        """Create a score for insufficient data case."""
        baseline = sum(completion_history) / n if n > 0 else 0.0
        confidence = n / self.min_samples if self.min_samples > 0 else 0.0
        
        return PCSScore(
            habit_id=habit_id,
            habit_name=habit_name,
            pcs_score=0.0,
            fragility_index=0.0,
            auc_score=0.5,
            dependency_ratio=0.0,
            context_factors={},
            external_dependency={},
            baseline_rate=round(baseline, 3),
            predicted_rate=0.0,
            sample_size=n,
            confidence=round(min(1.0, confidence), 2)
        )
    
    def _calculate_auc(
        self, 
        y_true: List[float], 
        y_pred: List[float]
    ) -> float:
        """
        Calculate Area Under ROC Curve.
        
        AUC measures how well the model distinguishes between
        completed and non-completed days. AUC > 0.5 indicates
        the habit is predictable from context.
        
        Uses trapezoidal rule for AUC calculation.
        """
        if len(y_true) < 2:
            return 0.5
        
        # Create pairs and sort by prediction score (descending)
        pairs = list(zip(y_pred, y_true))
        pairs.sort(key=lambda x: x[0], reverse=True)
        
        # Count positives and negatives
        n_pos = sum(1 for _, y in pairs if y >= 0.5)
        n_neg = len(pairs) - n_pos
        
        if n_pos == 0 or n_neg == 0:
            return 0.5  # No discrimination possible
        
        # Calculate TPR and FPR at each threshold
        tp = 0
        fp = 0
        prev_pred = None
        auc = 0.0
        
        # Start from (0, 0)
        prev_tpr = 0.0
        prev_fpr = 0.0
        
        for pred, true in pairs:
            if pred != prev_pred:
                # Add trapezoid area
                tpr = tp / n_pos
                fpr = fp / n_neg
                auc += 0.5 * (fpr - prev_fpr) * (tpr + prev_tpr)
                prev_tpr = tpr
                prev_fpr = fpr
                prev_pred = pred
            
            if true >= 0.5:
                tp += 1
            else:
                fp += 1
        
        # Add final trapezoid to (1, 1)
        tpr = tp / n_pos
        fpr = fp / n_neg
        auc += 0.5 * (1.0 - prev_fpr) * (1.0 + prev_tpr)
        
        return auc
    
    def _calculate_dependency_ratio(self) -> Tuple[float, float, float]:
        """
        Calculate the ratio of external to internal dependency.
        
        From research:
        - Internal features (autoregressive) indicate self-sustaining habit
        - External features indicate context dependency
        
        Returns:
            Tuple of (dependency_ratio, internal_strength, external_sensitivity)
        """
        internal_sum = 0.0
        external_sum = 0.0
        
        for i, name in enumerate(FEATURE_NAMES):
            weight = abs(self.weights.get(f"f{i}", 0.0))
            
            if name in INTERNAL_FEATURES:
                internal_sum += weight
            else:
                external_sum += weight
        
        # Dependency ratio: higher = more fragile
        epsilon = 1e-6
        dependency_ratio = external_sum / (internal_sum + epsilon)
        
        # Normalize to 0-1 range for interpretability
        normalized_internal = internal_sum / (internal_sum + external_sum + epsilon)
        normalized_external = external_sum / (internal_sum + external_sum + epsilon)
        
        return dependency_ratio, normalized_internal, normalized_external
    
    def _calculate_fragility_index(
        self, 
        auc_score: float, 
        dependency_ratio: float
    ) -> float:
        """
        Calculate Fragility Index using research formula.
        
        Formula from research paper:
        Fragility = 100 × (w1 × (1 - AUC) + w2 × DependencyRatio_normalized)
        
        Where:
        - w1 = 0.6 (prioritize predictability)
        - w2 = 0.4 (context dependency)
        
        Args:
            auc_score: Area Under ROC Curve (0-1)
            dependency_ratio: External/Internal coefficient ratio
            
        Returns:
            Fragility index (0-100)
        """
        # Normalize dependency ratio to 0-1
        # Use sigmoid-like normalization to handle extreme values
        normalized_dependency = 1.0 - math.exp(-dependency_ratio)
        
        # Calculate fragility
        fragility = 100.0 * (
            self.auc_weight * (1.0 - auc_score) +
            self.dependency_weight * normalized_dependency
        )
        
        return min(100.0, max(0.0, fragility))
    
    def _extract_feature_importance(
        self
    ) -> Tuple[Dict[str, float], Dict[str, float], float]:
        """
        Extract feature importance from fitted model.
        
        Returns:
            Tuple of (all_factors, external_factors, autoregressive_weight)
        """
        context_factors = {}
        external_dependency = {}
        autoregressive_weight = 0.0
        
        for i, name in enumerate(FEATURE_NAMES):
            weight = self.weights.get(f"f{i}", 0.0)
            abs_weight = abs(weight)
            
            if abs_weight > 0.01:  # Only include non-zero weights
                context_factors[name] = round(abs_weight, 4)
                
                if name in INTERNAL_FEATURES:
                    autoregressive_weight = abs_weight
                else:
                    external_dependency[name] = round(abs_weight, 4)
        
        return context_factors, external_dependency, autoregressive_weight
    
    def time_lagged_correlation(
        self,
        habit_completions: List[bool],
        context_values: List[float],
        max_lag: int = 7
    ) -> List[LaggedCorrelationResult]:
        """
        Calculate time-lagged cross-correlation to find vulnerability windows.
        
        From research: Fragility often manifests at specific lags.
        A fragile habit shows immediate sensitivity (high Lag 0 correlation)
        to negative contexts. Robust habits show "decoupling."
        
        Args:
            habit_completions: Binary completion history
            context_values: Context variable values (e.g., sleep hours)
            max_lag: Maximum lag to test (days)
            
        Returns:
            List of correlation results at each lag
        """
        results = []
        y = [1.0 if c else 0.0 for c in habit_completions]
        
        for lag in range(max_lag + 1):
            if lag == 0:
                x = context_values
                y_lag = y
            else:
                # Context at t predicts habit at t+lag
                x = context_values[:-lag]
                y_lag = y[lag:]
            
            if len(x) >= 3:
                corr = self._pearson_correlation(x, y_lag)
                results.append(LaggedCorrelationResult(
                    lag_days=lag,
                    correlation=corr,
                    sample_size=len(x)
                ))
        
        return results
    
    def _pearson_correlation(
        self, 
        x: List[float], 
        y: List[float]
    ) -> float:
        """Calculate Pearson correlation coefficient."""
        n = len(x)
        if n != len(y) or n < 3:
            return 0.0
        
        mean_x = sum(x) / n
        mean_y = sum(y) / n
        
        sum_xy = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
        sum_x2 = sum((xi - mean_x) ** 2 for xi in x)
        sum_y2 = sum((yi - mean_y) ** 2 for yi in y)
        
        denominator = math.sqrt(sum_x2 * sum_y2)
        if denominator == 0:
            return 0.0
        
        return sum_xy / denominator
    
    def granger_causality_test(
        self,
        habit_completions: List[bool],
        context_series: List[float],
        max_lag: int = 3
    ) -> GrangerCausalityResult:
        """
        Test if context variable Granger-causes habit completion.
        
        From research: Granger causality identifies predictive precedence.
        If context X Granger-causes habit Y, knowing X's history improves
        prediction of Y beyond Y's own history.
        
        Uses simplified F-test comparing restricted vs unrestricted models.
        
        Args:
            habit_completions: Binary completion history
            context_series: Context variable values
            max_lag: Maximum lag for the test
            
        Returns:
            GrangerCausalityResult with F-statistic and significance
        """
        n = len(habit_completions)
        if n < max_lag + 5:
            return GrangerCausalityResult(
                context_variable="unknown",
                f_statistic=0.0,
                p_value=1.0,
                is_significant=False
            )
        
        y = [1.0 if c else 0.0 for c in habit_completions]
        
        # Calculate restricted model RSS (autoregressive only)
        restricted_rss = self._calculate_autoregressive_rss(y, max_lag)
        
        # Calculate unrestricted model RSS (with context)
        unrestricted_rss = self._calculate_var_rss(y, context_series, max_lag)
        
        # F-statistic
        num_restricted = max_lag  # Number of restrictions
        num_params = 2 * max_lag + 1  # Parameters in unrestricted model
        
        if unrestricted_rss <= 0:
            f_stat = 0.0
        else:
            f_stat = ((restricted_rss - unrestricted_rss) / num_restricted) / \
                     (unrestricted_rss / (n - num_params))
        
        # Approximate p-value using F-distribution
        p_value = self._f_distribution_pvalue(f_stat, num_restricted, n - num_params)
        
        return GrangerCausalityResult(
            context_variable="context",
            f_statistic=round(f_stat, 3),
            p_value=round(p_value, 4),
            is_significant=p_value < 0.05
        )
    
    def _calculate_autoregressive_rss(
        self, 
        y: List[float], 
        lag: int
    ) -> float:
        """Calculate residual sum of squares for autoregressive model."""
        n = len(y)
        rss = 0.0
        
        for t in range(lag, n):
            # Predict using past values
            pred = sum(y[t - k - 1] for k in range(lag)) / lag
            rss += (y[t] - pred) ** 2
        
        return rss
    
    def _calculate_var_rss(
        self, 
        y: List[float], 
        x: List[float], 
        lag: int
    ) -> float:
        """Calculate RSS for VAR model (y and x)."""
        n = len(y)
        rss = 0.0
        
        for t in range(lag, n):
            # Predict using past y and past x
            y_component = sum(y[t - k - 1] for k in range(lag)) / lag
            x_component = sum(x[t - k - 1] for k in range(lag)) / lag
            pred = 0.5 * y_component + 0.5 * x_component
            rss += (y[t] - pred) ** 2
        
        return rss
    
    def _f_distribution_pvalue(
        self, 
        f_stat: float, 
        df1: int, 
        df2: int
    ) -> float:
        """Approximate p-value from F-distribution."""
        if f_stat <= 0:
            return 1.0
        
        # Simplified approximation using chi-square for large df2
        if df2 > 30:
            x = df1 * f_stat
            # Chi-square approximation
            return math.exp(-x / 2) if x < 20 else 0.001
        
        # Use F-distribution approximation
        x = df2 / (df2 + df1 * f_stat)
        return x ** (df2 / 2)
    
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
        
        # Sort by Fragility Index (most fragile first)
        scores.sort(key=lambda s: s.fragility_index, reverse=True)
        return scores
    
    def get_protection_recommendations(self, score: PCSScore) -> List[str]:
        """
        Generate recommendations for protecting a habit based on fragility analysis.
        
        Uses research insights:
        - High external dependency → environmental design needed
        - Low AUC → habit not yet automatic
        - Specific context factors → targeted interventions
        
        Args:
            score: PCSScore for the habit
            
        Returns:
            List of actionable recommendations
        """
        recommendations = []
        
        if score.fragility == "robust":
            recommendations.append(
                f"✅ {score.habit_name} is well-established with strong automaticity. "
                "Keep up the great work!"
            )
            return recommendations
        
        # Analyze habit strength based on AUC
        if score.habit_strength == "weak":
            recommendations.append(
                f"📊 {score.habit_name} shows weak predictability (AUC: {score.auc_score:.2f}). "
                "Focus on consistency before intensity."
            )
        
        # Analyze dependency ratio
        if score.dependency_ratio > 2.0:
            recommendations.append(
                f"🔗 High external dependency detected (ratio: {score.dependency_ratio:.1f}). "
                "This habit relies heavily on external conditions."
            )
        
        # Analyze autoregressive strength
        if score.internal_strength < 0.1 and score.sample_size >= 14:
            recommendations.append(
                "🔄 Low self-sustaining momentum. "
                "Consider habit stacking with an existing routine."
            )
        
        # Analyze top external factors
        for factor, weight in score.top_external_factors:
            recommendation = self._get_factor_recommendation(factor, weight)
            if recommendation:
                recommendations.append(recommendation)
        
        # Add fragility-specific advice
        if score.fragility == "fragile":
            recommendations.insert(0,
                f"⚠️ {score.habit_name} is FRAGILE (Index: {score.fragility_index:.0f}). "
                "Consider implementing protection strategies:\n"
                "   • Reduce habit size on difficult days\n"
                "   • Create environmental cues\n"
                "   • Use implementation intentions ('When X, I will Y')"
            )
        elif score.fragility == "moderate":
            recommendations.insert(0,
                f"🔶 {score.habit_name} has moderate sensitivity (Index: {score.fragility_index:.0f}). "
                "Monitor the factors below for best results."
            )
        
        return recommendations
    
    def _get_factor_recommendation(
        self, 
        factor: str, 
        weight: float
    ) -> Optional[str]:
        """Generate recommendation for a specific context factor."""
        factor_recommendations = {
            'sleep_hours': (
                "😴 This habit is sensitive to sleep. "
                "Prioritize 7-8 hours of sleep for better success. "
                "Consider moving the habit to after a good night's rest."
            ),
            'stress_level': (
                "🧘 Stress affects this habit significantly. "
                "Consider a brief mindfulness practice before the habit, "
                "or schedule it during lower-stress periods."
            ),
            'energy_level': (
                "⚡ Energy levels matter for this habit. "
                "Schedule it during your peak energy hours, "
                "or reduce the habit size on low-energy days."
            ),
            'day_of_week': (
                "📅 This habit varies significantly by day. "
                "Consider different approaches for different days, "
                "or identify what makes certain days more successful."
            ),
            'location_home': (
                "🏠 Location strongly affects this habit. "
                "Create a consistent environment with clear cues, "
                "or prepare a 'travel version' for away days."
            ),
            'prev_completion': (
                "🔗 Momentum is critical. "
                "Focus on not breaking the chain once started. "
                "Consider using streak freezes for protection."
            ),
            'num_events': (
                "📆 Busy days affect this habit. "
                "Set reminders, reduce habit size on busy days, "
                "or schedule the habit before events begin."
            ),
            'weather_score': (
                "🌤️ Weather influences this habit. "
                "Create an indoor alternative for bad weather, "
                "or adjust expectations based on forecast."
            ),
            'mood_score': (
                "😊 Mood impacts this habit. "
                "Consider a mood-boosting prelude activity, "
                "or practice self-compassion on difficult days."
            ),
            'sleep_quality': (
                "💤 Sleep quality matters. "
                "Focus on sleep hygiene, or move the habit "
                "to when you typically feel most rested."
            )
        }
        
        if weight > 0.15:
            return factor_recommendations.get(factor)
        elif weight > 0.08:
            return factor_recommendations.get(factor, None)
        return None
    
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
        This isolates the "active ingredients" of the habit context.
        
        From research: LASSO is preferred because true habits are likely
        triggered by only a small subset of context variables.
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
                self.intercept -= self.weights[f"f{j}"] * \
                    sum(X[i][j] for i in range(n_samples)) / n_samples
            
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
            for i, name in enumerate(FEATURE_NAMES)
            if abs(self.weights.get(f"f{i}", 0.0)) > 0.01
        }


def calculate_fragility_index(
    completion_history: List[bool],
    context_history: List[ContextVariables],
    habit_id: str = "unknown",
    habit_name: str = "Unknown Habit"
) -> PCSScore:
    """
    Convenience function to calculate fragility index for a habit.
    
    Args:
        completion_history: List of completion status (True/False)
        context_history: List of context variables for each day
        habit_id: Optional habit identifier
        habit_name: Optional habit name
        
    Returns:
        PCSScore with fragility assessment
    """
    engine = PCSEngine()
    return engine.calculate_pcs(habit_id, habit_name, completion_history, context_history)