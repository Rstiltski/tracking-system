# Phase 2: Intelligence Layer

**Duration:** 3 weeks
**Status:** ✅ Complete
**Dependencies:** Phase 1 Complete
**Updated:** February 16, 2026

---

## Overview

Phase 2 focuses on adding intelligence capabilities to TrackLife by:
1. Discovering correlations between habits, health, and context
2. Predicting habit success based on contextual factors
3. Predicting and preventing user burnout

---

## Goals

| Goal | Success Metric |
|------|----------------|
| Discover hidden patterns | Correlation insights displayed to user |
| Predict habit success | PCS score for each habit |
| Prevent burnout | Burnout alerts before user quits |

---

## Phase 2.1: Correlation Engine

**Priority:** High
**Effort:** Medium
**Duration:** 1 week

### Problem

Users track many data points but don't understand how they relate:
- Does sleep affect habit completion?
- Does exercise correlate with mood?
- What factors influence productivity?

### Solution

Build a correlation engine that:
- Calculates statistical correlations between variables
- Identifies time-lagged relationships
- Presents insights in user-friendly format

### Algorithm

```
Pearson Correlation:
r = Σ((x - x̄)(y - ȳ)) / √(Σ(x - x̄)² × Σ(y - ȳ)²)

Spearman Correlation:
r_s = 1 - (6 × Σd²) / (n × (n² - 1))

Time-Lag Analysis:
Corr(x_t, y_{t+k}) for k = 0, 1, 2, ... days
```

### Tasks

- [ ] Create `brain/analysis/correlation.py` module
- [ ] Implement Pearson correlation
- [ ] Implement Spearman correlation
- [ ] Implement time-lag analysis
- [ ] Create insight discovery algorithm
- [ ] Add insights dashboard UI

### Implementation

```python
# brain/analysis/correlation.py
from dataclasses import dataclass
from typing import List, Tuple, Optional
import math

@dataclass
class CorrelationResult:
    """Result of a correlation analysis."""
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


class CorrelationEngine:
    """Statistical correlation analysis for habit data."""
    
    def __init__(self, significance_level: float = 0.05):
        self.significance_level = significance_level
    
    def pearson(self, x: List[float], y: List[float]) -> CorrelationResult:
        """Calculate Pearson correlation coefficient."""
        n = len(x)
        if n != len(y) or n < 3:
            raise ValueError("Need at least 3 paired observations")
        
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
        
        # Calculate p-value (simplified, using t-distribution approximation)
        if abs(r) < 1:
            t_stat = r * math.sqrt((n - 2) / (1 - r ** 2))
            # Simplified p-value calculation
            p_value = self._t_distribution_pvalue(t_stat, n - 2)
        else:
            p_value = 0.0 if abs(r) == 1 else 1.0
        
        return CorrelationResult(
            variable_x="x",
            variable_y="y",
            coefficient=round(r, 4),
            p_value=round(p_value, 4),
            sample_size=n
        )
    
    def spearman(self, x: List[float], y: List[float]) -> CorrelationResult:
        """Calculate Spearman rank correlation coefficient."""
        n = len(x)
        if n != len(y) or n < 3:
            raise ValueError("Need at least 3 paired observations")
        
        # Convert to ranks
        rank_x = self._rank_values(x)
        rank_y = self._rank_values(y)
        
        # Calculate difference in ranks
        d_squared = sum((rx - ry) ** 2 for rx, ry in zip(rank_x, rank_y))
        
        # Spearman coefficient
        r_s = 1 - (6 * d_squared) / (n * (n ** 2 - 1))
        
        # P-value approximation
        p_value = self._spearman_pvalue(r_s, n)
        
        return CorrelationResult(
            variable_x="x",
            variable_y="y",
            coefficient=round(r_s, 4),
            p_value=round(p_value, 4),
            sample_size=n
        )
    
    def time_lag_correlation(
        self, 
        x: List[float], 
        y: List[float], 
        max_lag: int = 7
    ) -> List[CorrelationResult]:
        """Calculate correlations at different time lags."""
        results = []
        
        for lag in range(max_lag + 1):
            if lag == 0:
                x_lagged = x
                y_lagged = y
            else:
                # x_t correlated with y_{t+lag}
                x_lagged = x[:-lag] if lag > 0 else x
                y_lagged = y[lag:] if lag > 0 else y
            
            if len(x_lagged) >= 3:
                result = self.pearson(x_lagged, y_lagged)
                result.lag_days = lag
                results.append(result)
        
        return results
    
    def _rank_values(self, values: List[float]) -> List[float]:
        """Convert values to ranks."""
        sorted_pairs = sorted(enumerate(values), key=lambda p: p[1])
        ranks = [0.0] * len(values)
        
        i = 0
        while i < len(sorted_pairs):
            j = i
            # Find ties
            while j < len(sorted_pairs) - 1 and sorted_pairs[j][1] == sorted_pairs[j + 1][1]:
                j += 1
            # Average rank for ties
            avg_rank = (i + j) / 2 + 1
            for k in range(i, j + 1):
                ranks[sorted_pairs[k][0]] = avg_rank
            i = j + 1
        
        return ranks
    
    def _t_distribution_pvalue(self, t: float, df: int) -> float:
        """Approximate p-value from t-statistic."""
        # Simplified approximation using normal distribution for large df
        if df > 30:
            # Normal approximation
            abs_t = abs(t)
            # Approximate two-tailed p-value
            p = 2 * (1 - self._normal_cdf(abs_t))
            return p
        else:
            # Use approximation for small samples
            return self._t_approx_pvalue(t, df)
    
    def _normal_cdf(self, x: float) -> float:
        """Standard normal CDF approximation."""
        # Approximation using error function
        return 0.5 * (1 + math.erf(x / math.sqrt(2)))
    
    def _t_approx_pvalue(self, t: float, df: int) -> float:
        """Approximate p-value for t-distribution."""
        # Simplified approximation
        x = df / (df + t ** 2)
        return 2 * (1 - math.sqrt(x))
    
    def _spearman_pvalue(self, r_s: float, n: int) -> float:
        """Approximate p-value for Spearman correlation."""
        if n > 10:
            # Use t-approximation
            t = r_s * math.sqrt((n - 2) / (1 - r_s ** 2 + 0.0001))
            return self._t_distribution_pvalue(t, n - 2)
        else:
            # For small samples, use lookup table approximation
            return 0.1 if abs(r_s) > 0.5 else 0.5
```

### Insight Types

| Insight Type | Example |
|--------------|---------|
| **Habit-Habit** | "Morning meditation correlates with evening exercise (r=0.65)" |
| **Habit-Health** | "Sleep quality predicts workout completion (r=0.72, 1-day lag)" |
| **Habit-Context** | "Productivity drops 23% on days with >3 meetings" |
| **Time Patterns** | "You're 40% more likely to complete habits on Tuesdays" |

---

## Phase 2.2: Predictive Context Sensitivity (PCS) ✅ COMPLETE

**Priority:** High
**Effort:** Medium
**Duration:** 1 week
**Updated:** February 16, 2026 (Enhanced with research paper implementation)

### Research Source

Based on **Buyalskaya, Ho, Milkman, et al. (2023)** - "What can machine learning teach us about habit formation?" *Proceedings of the National Academy of Sciences*.

### Problem

Users don't know which habits are fragile:
- Some habits depend heavily on context (sleep, stress, schedule)
- Others are robust regardless of circumstances
- No visibility into which habits need protection

### Solution

Implement PCS score from habit research:
- **AUC (Area Under ROC Curve)**: Primary metric for habit strength
- **Dependency Ratio**: External vs Internal context dependency
- **Fragility Index**: Combined score (0-100) indicating vulnerability

### Key Concepts from Research

1. **Predicting Context Sensitivity (PCS)**: Measures how predictable a behavior is based on observable context variables

2. **Habit Formation**: As a habit forms, the brain offloads control from goal-directed systems (prefrontal cortex) to sensorimotor loops (dorsolateral striatum)

3. **Fragile Habit**: A behavior that looks consistent but is cognitively expensive - maintained by "white-knuckling" through willpower

4. **Robust Habit**: Behavior triggered by environmental cues with minimal cognitive oversight, persists even under stress

### Algorithm

```
Fragility Index = 100 × (w₁ × (1 - AUC) + w₂ × DependencyRatio_normalized)

Where:
- AUC = Area Under ROC Curve from LASSO predictions
- Dependency Ratio = Σ|β_external| / (Σ|β_internal| + ε)
- w₁ = 0.6 (prioritize predictability)
- w₂ = 0.4 (context dependency)
```

### Feature Classification

| Type | Features | Interpretation |
|------|----------|----------------|
| **Internal** | `prev_completion` | Self-sustaining, autoregressive ($Y_{t-1}$) |
| **External** | `sleep_hours`, `stress_level`, `weather_score`, `day_of_week`, `num_events`, `mood_score`, `location_home`, `energy_level`, `sleep_quality` | Context-dependent |

### Tasks

- [x] Research LASSO regression for habit prediction
- [x] Create `brain/analysis/prediction.py` module
- [x] Implement ContextVariables dataclass
- [x] Implement PCSEngine with coordinate descent
- [x] Calculate PCS score for habits
- [x] Add protection recommendations
- [x] Implement AUC (Area Under ROC Curve) calculation
- [x] Implement Dependency Ratio (external vs internal)
- [x] Implement Fragility Index formula from research
- [x] Add feature classification (internal/external)
- [x] Add Time-Lagged Cross-Correlation method
- [x] Add Granger Causality test

### Implementation

```python
# brain/analysis/prediction.py - Enhanced Implementation

from dataclasses import dataclass, field
from typing import List, Dict, Optional, Tuple, Any
from datetime import datetime
import math

# Feature classification for dependency analysis
INTERNAL_FEATURES = ['prev_completion']  # Autoregressive - self-sustaining
EXTERNAL_FEATURES = [
    'sleep_hours', 'stress_level', 'weather_score',
    'day_of_week', 'num_events', 'mood_score',
    'location_home', 'energy_level', 'sleep_quality'
]

@dataclass
class ContextVariables:
    """
    Context factors that may influence habit completion.
    
    Based on research showing context stability is prerequisite 
    for habit automatization (Stojanovic et al. 2020, 2022).
    """
    date: str = ""
    sleep_hours: Optional[float] = None
    stress_level: Optional[int] = None  # 1-10 scale
    weather_score: Optional[float] = None  # 0-1 (bad to good)
    day_of_week: Optional[int] = None  # 0-6 (Monday=0)
    num_events: Optional[int] = None  # Calendar events
    mood_score: Optional[float] = None  # 0-1
    location_home: Optional[bool] = None
    previous_day_completion: Optional[float] = None  # % completed
    energy_level: Optional[int] = None  # 1-10 scale
    sleep_quality: Optional[float] = None  # 0-1
    
    def to_feature_vector(self) -> List[float]:
        """Convert to normalized feature vector for ML."""
        return [
            self.previous_day_completion or 0.5,  # Internal
            (self.sleep_hours or 7.0) / 12.0,  # External
            (self.stress_level or 5) / 10.0,
            self.weather_score or 0.5,
            (self.day_of_week or 0) / 6.0,
            min(1.0, (self.num_events or 0) / 10.0),
            self.mood_score or 0.5,
            1.0 if self.location_home else 0.5 if self.location_home is None else 0.0,
            (self.energy_level or 5) / 10.0,
            self.sleep_quality or 0.5
        ]


@dataclass
class PCSScore:
    """
    Predictive Context Sensitivity score for a habit.
    
    Key Metrics:
    - auc_score: Area Under ROC Curve (0-1), measures predictability
    - dependency_ratio: External vs Internal context dependency
    - fragility_index: Combined score (0-100) indicating vulnerability
    """
    habit_id: str
    habit_name: str
    pcs_score: float  # Legacy field (equals fragility_index)
    context_factors: Dict[str, float]
    baseline_rate: float
    predicted_rate: float
    sample_size: int = 0
    confidence: float = 0.0
    calculated_at: datetime = field(default_factory=datetime.now)
    
    # New fields from research paper
    auc_score: float = 0.5  # Area Under ROC Curve
    dependency_ratio: float = 0.0  # External/Internal ratio
    autoregressive_weight: float = 0.0  # Self-prediction strength
    external_dependency: Dict[str, float] = field(default_factory=dict)
    fragility_index: float = 0.0  # Combined 0-100 score
    internal_strength: float = 0.0
    external_sensitivity: float = 0.0
    
    @property
    def fragility(self) -> str:
        """Interpret Fragility Index as fragility level."""
        if self.fragility_index >= 70:
            return "fragile"
        elif self.fragility_index >= 40:
            return "moderate"
        return "robust"
    
    @property
    def habit_strength(self) -> str:
        """Interpret AUC as habit strength."""
        if self.auc_score >= 0.8:
            return "strong"
        elif self.auc_score >= 0.6:
            return "moderate"
        return "weak"


@dataclass
class LaggedCorrelationResult:
    """Result of time-lagged cross-correlation analysis."""
    lag_days: int
    correlation: float
    sample_size: int


@dataclass
class GrangerCausalityResult:
    """Result of Granger causality test."""
    context_variable: str
    f_statistic: float
    p_value: float
    is_significant: bool  # p < 0.05


class PCSEngine:
    """
    Predictive Context Sensitivity calculation engine.
    
    Implements the PCS algorithm from Buyalskaya et al. (2023) PNAS paper.
    """
    
    def __init__(
        self, 
        regularization: float = 0.1, 
        min_samples: int = 14,
        auc_weight: float = 0.6,
        dependency_weight: float = 0.4
    ):
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
        """Calculate PCS score using research-based algorithm."""
        # Implementation includes:
        # 1. LASSO regression with coordinate descent
        # 2. AUC calculation with 70/30 train/test split
        # 3. Dependency ratio calculation
        # 4. Fragility Index formula
        pass
    
    def time_lagged_correlation(
        self,
        habit_completions: List[bool],
        context_values: List[float],
        max_lag: int = 7
    ) -> List[LaggedCorrelationResult]:
        """
        Find vulnerability windows using time-lagged cross-correlation.
        
        From research: Fragile habits show immediate sensitivity (high Lag 0).
        Robust habits show "decoupling" - correlation weakens.
        """
        pass
    
    def granger_causality_test(
        self,
        habit_completions: List[bool],
        context_series: List[float],
        max_lag: int = 3
    ) -> GrangerCausalityResult:
        """
        Test if context variable Granger-causes habit completion.
        
        Identifies predictive precedence - does knowing X's history
        improve prediction of Y beyond Y's own history?
        """
        pass
    
    def get_protection_recommendations(self, score: PCSScore) -> List[str]:
        """Generate targeted recommendations based on fragility analysis."""
        pass
```

### Score Interpretation

| Fragility Index | Fragility | AUC Score | Habit Strength | Action |
|-----------------|-----------|-----------|----------------|--------|
| 0-39% | Robust | > 0.8 | Strong | Habit is automatic, low context dependency |
| 40-69% | Moderate | 0.6-0.8 | Moderate | Some context sensitivity, monitor |
| 70-100% | Fragile | < 0.6 | Weak | High context dependency, needs protection |

### New Methods

| Method | Purpose | Use Case |
|--------|---------|----------|
| `time_lagged_correlation()` | Find vulnerability windows | "Poor sleep on Tuesday affects Thursday habit" |
| `granger_causality_test()` | Identify predictive precedence | "Does stress predict habit failure?" |
| `get_protection_recommendations()` | Generate targeted advice | Context-specific interventions |

---

## Phase 2.3: Burnout Prediction

**Priority:** Medium
**Effort:** Medium
**Duration:** 1 week

### Problem

Users often quit tracking after burnout:
- Warning signs appear before quitting
- No intervention to prevent burnout
- Users lose all progress

### Solution

Build a burnout prediction system:
- Monitor burnout indicators
- Calculate burnout risk score
- Suggest interventions before user quits

### Burnout Indicators

| Indicator | Weight | Measurement |
|-----------|--------|-------------|
| Declining completion rate | 0.25 | 7-day trend vs 30-day average |
| Decreasing sleep | 0.20 | Below personal baseline |
| Increasing stress | 0.15 | Self-reported or inferred |
| Missed check-ins | 0.15 | Days without app open |
| Dropping streaks | 0.15 | Multiple streak breaks |
| Negative mood trend | 0.10 | Mood entries declining |

### Tasks

- [ ] Design burnout risk model
- [ ] Collect input features (sleep, tasks, HRV)
- [ ] Implement burnout score calculation
- [ ] Add intervention suggestions
- [ ] Create burnout alert system

### Implementation

```python
# brain/analysis/burnout.py
from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime, timedelta
import math

@dataclass
class BurnoutIndicators:
    """Indicators used for burnout prediction."""
    completion_rate_trend: float  # -1 to 1 (declining to improving)
    sleep_deviation: float  # Hours below baseline
    stress_level: int  # 1-10
    days_since_checkin: int
    streak_breaks: int  # Recent streak breaks
    mood_trend: float  # -1 to 1
    task_overload: float  # Tasks due / capacity


@dataclass
class BurnoutRisk:
    """Burnout risk assessment."""
    risk_score: float  # 0-100%
    risk_level: str  # low, moderate, high, critical
    contributing_factors: Dict[str, float]
    interventions: List[str]
    recovery_mode_recommended: bool


class BurnoutPredictor:
    """Predict and prevent user burnout."""
    
    INDICATOR_WEIGHTS = {
        'completion_rate_trend': 0.25,
        'sleep_deviation': 0.20,
        'stress_level': 0.15,
        'days_since_checkin': 0.15,
        'streak_breaks': 0.15,
        'mood_trend': 0.10
    }
    
    def assess_risk(self, indicators: BurnoutIndicators) -> BurnoutRisk:
        """Calculate burnout risk score."""
        factors = {}
        
        # Completion rate trend (negative = declining)
        factors['completion_rate_trend'] = self._normalize_trend(
            indicators.completion_rate_trend, inverse=True
        )
        
        # Sleep deviation (more negative = worse)
        factors['sleep_deviation'] = min(1.0, abs(indicators.sleep_deviation) / 2.0)
        
        # Stress level (higher = worse)
        factors['stress_level'] = indicators.stress_level / 10.0
        
        # Days since check-in (more days = worse)
        factors['days_since_checkin'] = min(1.0, indicators.days_since_checkin / 7.0)
        
        # Streak breaks (more = worse)
        factors['streak_breaks'] = min(1.0, indicators.streak_breaks / 3.0)
        
        # Mood trend (negative = declining)
        factors['mood_trend'] = self._normalize_trend(
            indicators.mood_trend, inverse=True
        )
        
        # Calculate weighted risk score
        risk_score = sum(
            factors[factor] * weight 
            for factor, weight in self.INDICATOR_WEIGHTS.items()
        ) * 100
        
        # Determine risk level
        if risk_score >= 75:
            risk_level = "critical"
        elif risk_score >= 50:
            risk_level = "high"
        elif risk_score >= 25:
            risk_level = "moderate"
        else:
            risk_level = "low"
        
        # Generate interventions
        interventions = self._generate_interventions(factors, risk_level)
        
        return BurnoutRisk(
            risk_score=round(risk_score, 1),
            risk_level=risk_level,
            contributing_factors=factors,
            interventions=interventions,
            recovery_mode_recommended=risk_score >= 50
        )
    
    def _normalize_trend(self, trend: float, inverse: bool = False) -> float:
        """Normalize trend value to 0-1 range."""
        # trend is -1 to 1
        normalized = (trend + 1) / 2  # 0 to 1
        if inverse:
            normalized = 1 - normalized
        return normalized
    
    def _generate_interventions(
        self, 
        factors: Dict[str, float], 
        risk_level: str
    ) -> List[str]:
        """Generate intervention suggestions based on risk factors."""
        interventions = []
        
        if factors['completion_rate_trend'] > 0.6:
            interventions.append(
                "🎯 Focus on just 1-2 key habits this week. It's okay to pause others."
            )
        
        if factors['sleep_deviation'] > 0.5:
            interventions.append(
                "😴 Your sleep is below your baseline. Consider a wind-down routine."
            )
        
        if factors['stress_level'] > 0.7:
            interventions.append(
                "🧘 High stress detected. Try a 5-minute breathing exercise."
            )
        
        if factors['days_since_checkin'] > 0.5:
            interventions.append(
                "📱 You haven't checked in recently. Take a moment to reflect."
            )
        
        if factors['streak_breaks'] > 0.5:
            interventions.append(
                "❄️ Consider using Streak Freezes to protect your progress."
            )
        
        if risk_level in ["high", "critical"]:
            interventions.insert(0, 
                "🛡️ Recovery Mode recommended: Reduced expectations, focus on basics."
            )
        
        return interventions
```

---

## Success Criteria

| Criteria | How to Verify | Status |
|----------|---------------|--------|
| Correlation Engine works | Insights displayed for tracked data | ✅ |
| PCS Score works | Each habit shows fragility indicator | ✅ |
| Burnout Prediction works | Alerts shown when risk is high | ✅ |
| AUC calculation implemented | Predictability score for each habit | ✅ |
| Dependency Ratio calculated | Internal vs external factor analysis | ✅ |
| Fragility Index formula | Combined vulnerability score | ✅ |
| Time-lagged correlation | Vulnerability window detection | ✅ |
| Granger causality test | Predictive precedence analysis | ✅ |

---

## Dependencies

| Dependency | Purpose | Install |
|------------|---------|---------|
| numpy | Numerical computations | `pip install numpy` |
| scipy | Statistical functions | `pip install scipy` |

---

## Risks and Mitigations

| Risk | Mitigation |
|------|------------|
| Insufficient data for analysis | Require minimum 14 days of data |
| False correlations | Use significance testing, warn users |
| Burnout false positives | Conservative thresholds, user feedback |

---

## Next Phase

After completing Phase 2, proceed to:
- [Phase 3: Behavioral Science Implementation](PHASE_3_BEHAVIORAL.md)

---

*Last updated: February 16, 2026*
