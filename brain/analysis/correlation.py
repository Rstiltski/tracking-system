"""
Correlation Analysis Module

Provides statistical correlation analysis for habit data including:
- Pearson correlation coefficient
- Spearman rank correlation
- Time-lag correlation analysis

Based on research from open source habit trackers and behavioral science.
"""

from dataclasses import dataclass, field
from typing import List, Tuple, Optional, Dict, Any
from datetime import datetime, timedelta
import math


@dataclass(frozen=True)
class CorrelationResult:
    """Immutable result of a correlation analysis."""
    variable_x: str
    variable_y: str
    coefficient: float  # -1 to 1
    p_value: float
    sample_size: int
    lag_days: int = 0
    
    @property
    def strength(self) -> str:
        """Interpret correlation strength."""
        abs_r = abs(self.coefficient)
        if abs_r >= 0.7:
            return "strong"
        elif abs_r >= 0.4:
            return "moderate"
        elif abs_r >= 0.2:
            return "weak"
        return "negligible"
    
    @property
    def direction(self) -> str:
        """Interpret correlation direction."""
        return "positive" if self.coefficient > 0 else "negative"
    
    @property
    def is_significant(self) -> bool:
        """Check if correlation is statistically significant (p < 0.05)."""
        return self.p_value < 0.05
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'variable_x': self.variable_x,
            'variable_y': self.variable_y,
            'coefficient': self.coefficient,
            'p_value': self.p_value,
            'sample_size': self.sample_size,
            'lag_days': self.lag_days,
            'strength': self.strength,
            'direction': self.direction,
            'is_significant': self.is_significant
        }


@dataclass
class Insight:
    """A discovered insight from correlation analysis."""
    insight_type: str  # 'habit-habit', 'habit-health', 'habit-context', 'time-pattern'
    title: str
    description: str
    correlation: Optional[CorrelationResult] = None
    recommendation: Optional[str] = None
    confidence: float = 0.0  # 0-1
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'insight_type': self.insight_type,
            'title': self.title,
            'description': self.description,
            'correlation': self.correlation.to_dict() if self.correlation else None,
            'recommendation': self.recommendation,
            'confidence': self.confidence,
            'created_at': self.created_at.isoformat()
        }


class CorrelationEngine:
    """
    Statistical correlation analysis for habit data.
    
    Provides methods for calculating:
    - Pearson correlation (linear relationships)
    - Spearman correlation (monotonic relationships)
    - Time-lag correlations (predictive relationships)
    
    Example:
        engine = CorrelationEngine()
        
        # Pearson correlation
        result = engine.pearson([7, 8, 6, 7], [1, 1, 0, 1])
        print(f"r = {result.coefficient}, p = {result.p_value}")
        
        # Time-lag analysis
        lag_results = engine.time_lag_correlation(sleep_data, completion_data, max_lag=7)
        for r in lag_results:
            print(f"Lag {r.lag_days}: r = {r.coefficient}")
    """
    
    def __init__(self, significance_level: float = 0.05):
        """
        Initialize the correlation engine.
        
        Args:
            significance_level: Threshold for statistical significance (default 0.05)
        """
        self.significance_level = significance_level
    
    def pearson(
        self, 
        x: List[float], 
        y: List[float],
        x_name: str = "x",
        y_name: str = "y"
    ) -> CorrelationResult:
        """
        Calculate Pearson correlation coefficient.
        
        Measures linear relationship between two variables.
        Range: -1 (perfect negative) to +1 (perfect positive)
        
        Args:
            x: First variable values
            y: Second variable values
            x_name: Name of first variable
            y_name: Name of second variable
            
        Returns:
            CorrelationResult with coefficient, p-value, and metadata
            
        Raises:
            ValueError: If lists have different lengths or fewer than 3 observations
        """
        n = len(x)
        if n != len(y):
            raise ValueError(f"Lists must have same length: x has {len(x)}, y has {len(y)}")
        if n < 3:
            raise ValueError(f"Need at least 3 paired observations, got {n}")
        
        # Calculate means
        mean_x = sum(x) / n
        mean_y = sum(y) / n
        
        # Calculate components
        sum_xy = sum((xi - mean_x) * (yi - mean_y) for xi, yi in zip(x, y))
        sum_x2 = sum((xi - mean_x) ** 2 for xi in x)
        sum_y2 = sum((yi - mean_y) ** 2 for yi in y)
        
        # Calculate coefficient
        denominator = math.sqrt(sum_x2 * sum_y2)
        if denominator == 0:
            r = 0.0
        else:
            r = sum_xy / denominator
        
        # Clamp to valid range (floating point can exceed)
        r = max(-1.0, min(1.0, r))
        
        # Calculate p-value using t-distribution
        if abs(r) < 1:
            t_stat = r * math.sqrt((n - 2) / (1 - r ** 2 + 1e-10))
            p_value = self._t_distribution_pvalue(t_stat, n - 2)
        else:
            p_value = 0.0
        
        return CorrelationResult(
            variable_x=x_name,
            variable_y=y_name,
            coefficient=round(r, 4),
            p_value=round(p_value, 4),
            sample_size=n
        )
    
    def spearman(
        self, 
        x: List[float], 
        y: List[float],
        x_name: str = "x",
        y_name: str = "y"
    ) -> CorrelationResult:
        """
        Calculate Spearman rank correlation coefficient.
        
        Measures monotonic relationship between two variables.
        More robust to outliers than Pearson.
        
        Args:
            x: First variable values
            y: Second variable values
            x_name: Name of first variable
            y_name: Name of second variable
            
        Returns:
            CorrelationResult with coefficient, p-value, and metadata
        """
        n = len(x)
        if n != len(y):
            raise ValueError(f"Lists must have same length: x has {len(x)}, y has {len(y)}")
        if n < 3:
            raise ValueError(f"Need at least 3 paired observations, got {n}")
        
        # Convert to ranks
        rank_x = self._rank_values(x)
        rank_y = self._rank_values(y)
        
        # Calculate difference in ranks
        d_squared = sum((rx - ry) ** 2 for rx, ry in zip(rank_x, rank_y))
        
        # Spearman coefficient
        r_s = 1 - (6 * d_squared) / (n * (n ** 2 - 1))
        
        # Clamp to valid range
        r_s = max(-1.0, min(1.0, r_s))
        
        # P-value approximation
        p_value = self._spearman_pvalue(r_s, n)
        
        return CorrelationResult(
            variable_x=x_name,
            variable_y=y_name,
            coefficient=round(r_s, 4),
            p_value=round(p_value, 4),
            sample_size=n
        )
    
    def time_lag_correlation(
        self, 
        x: List[float], 
        y: List[float], 
        max_lag: int = 7,
        x_name: str = "x",
        y_name: str = "y"
    ) -> List[CorrelationResult]:
        """
        Calculate correlations at different time lags.
        
        Useful for discovering predictive relationships where
        one variable affects another with a delay.
        
        Example: Sleep tonight predicts workout completion tomorrow (lag=1)
        
        Args:
            x: Predictor variable (earlier in time)
            y: Outcome variable (later in time)
            max_lag: Maximum lag in days to analyze
            x_name: Name of predictor variable
            y_name: Name of outcome variable
            
        Returns:
            List of CorrelationResults for each lag
        """
        results = []
        
        for lag in range(max_lag + 1):
            if lag == 0:
                x_lagged = list(x)
                y_lagged = list(y)
            else:
                # x_t correlated with y_{t+lag}
                # x values from start to end-lag
                # y values from lag to end
                x_lagged = x[:-lag] if lag > 0 else x
                y_lagged = y[lag:] if lag > 0 else y
            
            if len(x_lagged) >= 3:
                try:
                    result = self.pearson(x_lagged, y_lagged, x_name, y_name)
                    # Create new result with lag
                    result = CorrelationResult(
                        variable_x=x_name,
                        variable_y=y_name,
                        coefficient=result.coefficient,
                        p_value=result.p_value,
                        sample_size=result.sample_size,
                        lag_days=lag
                    )
                    results.append(result)
                except ValueError:
                    pass  # Skip if not enough data
        
        return results
    
    def find_best_lag(
        self, 
        x: List[float], 
        y: List[float], 
        max_lag: int = 7,
        x_name: str = "x",
        y_name: str = "y"
    ) -> Optional[CorrelationResult]:
        """
        Find the time lag with the strongest correlation.
        
        Args:
            x: Predictor variable
            y: Outcome variable
            max_lag: Maximum lag to consider
            x_name: Name of predictor
            y_name: Name of outcome
            
        Returns:
            CorrelationResult with strongest absolute correlation, or None
        """
        results = self.time_lag_correlation(x, y, max_lag, x_name, y_name)
        
        if not results:
            return None
        
        # Find strongest correlation (by absolute value)
        return max(results, key=lambda r: abs(r.coefficient))
    
    def analyze_habit_correlations(
        self,
        habit_data: Dict[str, List[float]],
        min_samples: int = 7
    ) -> List[CorrelationResult]:
        """
        Analyze correlations between multiple habits.
        
        Args:
            habit_data: Dictionary mapping habit names to completion data
            min_samples: Minimum samples required for analysis
            
        Returns:
            List of significant correlations between habits
        """
        results = []
        habits = list(habit_data.keys())
        
        for i, habit_a in enumerate(habits):
            for habit_b in habits[i + 1:]:
                data_a = habit_data[habit_a]
                data_b = habit_data[habit_b]
                
                # Ensure same length
                min_len = min(len(data_a), len(data_b))
                if min_len < min_samples:
                    continue
                
                try:
                    result = self.pearson(
                        data_a[:min_len], 
                        data_b[:min_len],
                        habit_a, 
                        habit_b
                    )
                    
                    # Only include significant correlations
                    if result.is_significant and result.strength != "negligible":
                        results.append(result)
                except ValueError:
                    pass
        
        # Sort by absolute correlation strength
        results.sort(key=lambda r: abs(r.coefficient), reverse=True)
        return results
    
    def _rank_values(self, values: List[float]) -> List[float]:
        """Convert values to ranks, handling ties correctly."""
        n = len(values)
        sorted_pairs = sorted(enumerate(values), key=lambda p: p[1])
        ranks = [0.0] * n
        
        i = 0
        while i < n:
            j = i
            # Find ties
            while j < n - 1 and sorted_pairs[j][1] == sorted_pairs[j + 1][1]:
                j += 1
            # Average rank for ties
            avg_rank = (i + j) / 2 + 1
            for k in range(i, j + 1):
                ranks[sorted_pairs[k][0]] = avg_rank
            i = j + 1
        
        return ranks
    
    def _t_distribution_pvalue(self, t: float, df: int) -> float:
        """Approximate two-tailed p-value from t-statistic."""
        abs_t = abs(t)
        
        if df > 30:
            # Normal approximation for large samples
            p = 2 * (1 - self._normal_cdf(abs_t))
            return max(0.0, min(1.0, p))
        else:
            # Use approximation for small samples
            # Based on Abramowitz and Stegun approximation
            x = df / (df + abs_t ** 2)
            p = self._regularized_incomplete_beta(x, df / 2, 0.5)
            return max(0.0, min(1.0, p))
    
    def _normal_cdf(self, x: float) -> float:
        """Standard normal CDF using error function approximation."""
        # Approximation using Horner's method
        a1 = 0.254829592
        a2 = -0.284496736
        a3 = 1.421413741
        a4 = -1.453152027
        a5 = 1.061405429
        p = 0.3275911
        
        sign = 1 if x >= 0 else -1
        x = abs(x) / math.sqrt(2)
        
        t = 1.0 / (1.0 + p * x)
        y = 1.0 - (((((a5 * t + a4) * t) + a3) * t + a2) * t + a1) * t * math.exp(-x * x)
        
        return 0.5 * (1.0 + sign * y)
    
    def _regularized_incomplete_beta(self, x: float, a: float, b: float) -> float:
        """Approximate regularized incomplete beta function."""
        if x == 0:
            return 0.0
        if x == 1:
            return 1.0
        
        # Use continued fraction expansion
        # Simplified approximation
        if x < (a + 1) / (a + b + 2):
            return self._beta_cf(x, a, b) * math.exp(
                self._log_beta(a, b) + a * math.log(x) + b * math.log(1 - x)
            ) / a
        else:
            return 1 - self._regularized_incomplete_beta(1 - x, b, a)
    
    def _beta_cf(self, x: float, a: float, b: float, max_iter: int = 100) -> float:
        """Continued fraction for incomplete beta."""
        qab = a + b
        qap = a + 1
        qam = a - 1
        c = 1.0
        d = 1.0 - qab * x / qap
        if abs(d) < 1e-30:
            d = 1e-30
        d = 1.0 / d
        h = d
        
        for m in range(1, max_iter + 1):
            m2 = 2 * m
            aa = m * (b - m) * x / ((qam + m2) * (a + m2))
            d = 1.0 + aa * d
            if abs(d) < 1e-30:
                d = 1e-30
            c = 1.0 + aa / c
            if abs(c) < 1e-30:
                c = 1e-30
            d = 1.0 / d
            h *= d * c
            aa = -(a + m) * (qab + m) * x / ((a + m2) * (qap + m2))
            d = 1.0 + aa * d
            if abs(d) < 1e-30:
                d = 1e-30
            c = 1.0 + aa / c
            if abs(c) < 1e-30:
                c = 1e-30
            d = 1.0 / d
            delta = d * c
            h *= delta
            if abs(delta - 1.0) < 1e-10:
                break
        
        return h
    
    def _log_beta(self, a: float, b: float) -> float:
        """Log of beta function using log gamma."""
        return self._log_gamma(a) + self._log_gamma(b) - self._log_gamma(a + b)
    
    def _log_gamma(self, x: float) -> float:
        """Log gamma function approximation (Lanczos)."""
        if x <= 0:
            return float('inf')
        
        g = 7
        coef = [
            0.99999999999980993,
            676.5203681218851,
            -1259.1392167224028,
            771.32342877765313,
            -176.61502916214059,
            12.507343278686905,
            -0.13857109526572012,
            9.9843695780195716e-6,
            1.5056327351493116e-7
        ]
        
        if x < 0.5:
            return math.log(math.pi / math.sin(math.pi * x)) - self._log_gamma(1 - x)
        
        x -= 1
        tmp = (x + g + 0.5) * (x + g + 0.5) - (x + g + 0.5)
        ser = coef[0]
        for i in range(1, len(coef)):
            ser += coef[i] / (x + i)
        
        return 0.5 * math.log(2 * math.pi) + (x + 0.5) * math.log(x + g + 0.5) - (x + g + 0.5) + math.log(ser)
    
    def _spearman_pvalue(self, r_s: float, n: int) -> float:
        """Approximate p-value for Spearman correlation."""
        if n > 10:
            # Use t-approximation
            t = r_s * math.sqrt((n - 2) / (1 - r_s ** 2 + 1e-10))
            return self._t_distribution_pvalue(t, n - 2)
        else:
            # For small samples, use approximation
            # Critical values for Spearman at n <= 10
            critical_values = {
                4: 1.0, 5: 0.9, 6: 0.829, 7: 0.714, 8: 0.643,
                9: 0.6, 10: 0.564
            }
            if n in critical_values:
                critical = critical_values[n]
                if abs(r_s) >= critical:
                    return 0.05
                elif abs(r_s) >= critical * 0.8:
                    return 0.1
                else:
                    return 0.2
            return 0.5


class InsightGenerator:
    """
    Generate human-readable insights from correlation analysis.
    
    Takes correlation results and produces actionable insights
    with recommendations for the user.
    """
    
    def generate_insights(
        self, 
        correlations: List[CorrelationResult],
        min_strength: str = "weak"
    ) -> List[Insight]:
        """
        Generate insights from correlation results.
        
        Args:
            correlations: List of correlation results
            min_strength: Minimum strength to include ("weak", "moderate", "strong")
            
        Returns:
            List of Insight objects
        """
        insights = []
        strength_order = {"negligible": 0, "weak": 1, "moderate": 2, "strong": 3}
        min_level = strength_order.get(min_strength, 1)
        
        for corr in correlations:
            if strength_order.get(corr.strength, 0) < min_level:
                continue
            
            if not corr.is_significant:
                continue
            
            insight = self._create_insight(corr)
            if insight:
                insights.append(insight)
        
        # Sort by confidence
        insights.sort(key=lambda i: i.confidence, reverse=True)
        return insights
    
    def _create_insight(self, corr: CorrelationResult) -> Optional[Insight]:
        """Create an insight from a correlation result."""
        direction = "positively" if corr.coefficient > 0 else "negatively"
        strength = corr.strength
        
        # Determine insight type
        x_lower = corr.variable_x.lower()
        y_lower = corr.variable_y.lower()
        
        if "sleep" in x_lower or "sleep" in y_lower:
            insight_type = "habit-health"
            if corr.lag_days > 0:
                title = f"Sleep predicts {corr.variable_y}"
                description = (
                    f"Your sleep {corr.lag_days} day(s) ago {strength} correlates "
                    f"with {corr.variable_y} completion (r={corr.coefficient:.2f})"
                )
                recommendation = (
                    f"Prioritize good sleep to improve your {corr.variable_y} success rate."
                )
            else:
                title = f"Sleep and {corr.variable_y} are connected"
                description = (
                    f"There's a {strength} {direction} correlation between "
                    f"{corr.variable_x} and {corr.variable_y} (r={corr.coefficient:.2f})"
                )
                recommendation = "Track your sleep patterns to optimize habit completion."
        
        elif "mood" in x_lower or "mood" in y_lower:
            insight_type = "habit-health"
            title = f"Mood and {corr.variable_x if 'mood' in y_lower else corr.variable_y}"
            description = (
                f"Your mood {strength} correlates with "
                f"{corr.variable_x if 'mood' in y_lower else corr.variable_y} (r={corr.coefficient:.2f})"
            )
            recommendation = "Consider mood-tracking to identify patterns affecting your habits."
        
        elif corr.lag_days > 0:
            insight_type = "habit-context"
            title = f"{corr.variable_x} predicts {corr.variable_y}"
            description = (
                f"{corr.variable_x} {corr.lag_days} day(s) earlier "
                f"{strength} predicts {corr.variable_y} (r={corr.coefficient:.2f})"
            )
            recommendation = (
                f"Focus on {corr.variable_x} to improve future {corr.variable_y} outcomes."
            )
        
        else:
            insight_type = "habit-habit"
            title = f"{corr.variable_x} and {corr.variable_y} connection"
            description = (
                f"These habits are {strength} {direction} correlated (r={corr.coefficient:.2f})"
            )
            recommendation = (
                f"Consider stacking these habits for better consistency."
            )
        
        # Calculate confidence based on strength and significance
        confidence_map = {"strong": 0.9, "moderate": 0.7, "weak": 0.5}
        confidence = confidence_map.get(strength, 0.3)
        if corr.p_value < 0.01:
            confidence = min(1.0, confidence + 0.1)
        
        return Insight(
            insight_type=insight_type,
            title=title,
            description=description,
            correlation=corr,
            recommendation=recommendation,
            confidence=confidence
        )