# Correlation Engine Research

**Phase 2.1: Correlation Engine Implementation Research**

**Created:** February 16, 2026  
**Status:** Complete

---

## Overview

This document consolidates research from open-source correlation engines relevant to Phase 2.1 of the TrackLife Intelligence Layer. The research focuses on:

1. Statistical correlation methods (Pearson, Spearman)
2. Time-lagged correlation analysis
3. Granger causality testing
4. Natural language insight generation

---

## Repositories Analyzed

| Repository | Language | Primary Focus | Relevance |
|------------|----------|---------------|-----------|
| roqua/autovar | R | VAR models, Granger causality | ⭐⭐⭐⭐⭐ |
| farhanaugustine/Temporal_Behavior_Analysis | Python | Time-lagged cross-correlation | ⭐⭐⭐⭐⭐ |
| p0lloc/perfice | TypeScript | Automatic insights, NLG | ⭐⭐⭐⭐ |
| gianlucatruda/quantified-sleep | Python | ML for lag detection | ⭐⭐⭐⭐ |
| markrai/fitbaus | Python | Correlation matrix dashboard | ⭐⭐⭐ |
| karlicoss/HPI | Python | Data unification infrastructure | ⭐⭐⭐ |

---

## 1. AutoVAR: Granger Causality Implementation

**Repository:** `docs/research/repos/autovar`

### Key Concepts

AutoVAR implements the gold standard for time-lagged causal analysis using Vector Autoregression (VAR) models.

### Granger Causality Algorithm

From `R/vargranger.r`:

```r
# Granger causality Wald tests
vargranger <- function(varest, log_level=0) {
  res <- vargranger_call(varest)
  tos <- vargranger_to_string(varest, res)
  # Returns significant Granger-causal relationships
}

# Core causality test
granger_causality <- function(varest, cause, equation) {
  gres <- causality2(varest, cause=cause, equation=equation)$Granger
  # Returns F-statistic and p-value
}
```

### Sign Direction Detection

AutoVAR detects the direction of causal relationships:

```r
granger_causality_sign <- function(varest, exname, eqname) {
  coefs <- summary(varest)$varresult[[eqname]]$coefficients
  # Returns:
  # "+"  - majority positive associations
  # "-"  - majority negative associations
  # "~"  - mixed pos/neg associations within models
  # " "  - no clear sign
}
```

### Key Insights for TrackLife

1. **Wald Test for Significance**: Use F-test or Chi-squared test for Granger causality
2. **Sign Detection**: Track coefficient signs to determine positive/negative relationships
3. **"Almost" Granger Causality**: Consider relationships with p < 0.10 as "almost significant"

### Python Translation for TrackLife

```python
def granger_causality_test(data, cause_col, effect_col, max_lag=7):
    """
    Perform Granger causality test.
    
    Returns:
        dict with 'f_stat', 'p_value', 'is_significant', 'sign'
    """
    from scipy import stats
    import numpy as np
    
    # Prepare lagged data
    # ... implementation details
    
    # F-test for joint significance of lagged coefficients
    f_stat, p_value = stats.f_test(...)
    
    # Determine sign from coefficient sum
    coef_sum = sum(lagged_coefficients)
    sign = "+" if coef_sum > 0 else "-" if coef_sum < 0 else "~"
    
    return {
        'f_stat': f_stat,
        'p_value': p_value,
        'is_significant': p_value < 0.05,
        'sign': sign
    }
```

---

## 2. Temporal Behavior Analysis: Time-Lagged Cross-Correlation

**Repository:** `docs/research/repos/Temporal_Behavior_Analysis`

### Key Implementation

From `scripts/time_lagged_cross_correlation.py`:

```python
def calculate_time_lagged_cross_correlation(csv_file_path, class_labels, 
                                             max_lag_frames=150, frame_rate=30):
    """Calculate time-lagged cross-correlation for behavior pairs."""
    
    for (class1, class2) in itertools.combinations(class_labels.values(), 2):
        signal1 = np.array([1 if label == class1 else 0 for label in all_labels])
        signal2 = np.array([1 if label == class2 else 0 for label in all_labels])
        
        lags = np.arange(-max_lag_frames, max_lag_frames + 1)
        xcorr = []
        
        for lag in lags:
            if lag >= 0:
                # Positive lag: signal1 leads signal2
                corr = np.corrcoef(
                    signal1[:len(signal1) - lag], 
                    signal2[lag:]
                )[0][1]
            else:
                # Negative lag: signal2 leads signal1
                corr = np.corrcoef(
                    signal1[-lag:], 
                    signal2[:len(signal2) + lag]
                )[0][1]
            xcorr.append(corr)
```

### Benjamini-Hochberg FDR Correction

```python
def benjamini_hochberg(p_values, alpha=0.05):
    """Applies the Benjamini-Hochberg procedure (FDR correction)."""
    p_values = np.array(p_values)
    ranked_p_values = np.argsort(p_values)
    m = len(p_values)
    adjusted_p_values = np.zeros(m)
    
    for i, rank in enumerate(ranked_p_values):
        adjusted_p_values[rank] = p_values[rank] * m / (i + 1)
    
    adjusted_p_values = np.minimum(adjusted_p_values, 1)
    # Ensure monotonicity
    for i in range(m - 2, -1, -1):
        adjusted_p_values[ranked_p_values[i]] = min(
            adjusted_p_values[ranked_p_values[i]], 
            adjusted_p_values[ranked_p_values[i + 1]]
        )
    return adjusted_p_values
```

### Key Insights for TrackLife

1. **Bidirectional Lags**: Test both positive and negative lags to find optimal alignment
2. **FDR Correction**: Essential when testing multiple lags to avoid false positives
3. **Peak Detection**: Find the lag with maximum absolute correlation

### Recommended Implementation

```python
def cross_correlation_function(x, y, max_lag=7):
    """
    Compute cross-correlation function (CCF) for all lags.
    
    Returns dict mapping lag -> correlation coefficient
    """
    n = len(x)
    ccf = {}
    
    for lag in range(-max_lag, max_lag + 1):
        if lag == 0:
            corr = np.corrcoef(x, y)[0, 1]
        elif lag > 0:
            # x leads y by 'lag' periods
            corr = np.corrcoef(x[:-lag], y[lag:])[0, 1]
        else:
            # y leads x by abs(lag) periods
            corr = np.corrcoef(x[-lag:], y[:lag])[0, 1]
        
        ccf[lag] = corr
    
    return ccf

def find_optimal_lag(ccf):
    """Find the lag with strongest correlation."""
    best_lag = max(ccf.keys(), key=lambda k: abs(ccf[k]))
    return best_lag, ccf[best_lag]
```

---

## 3. Perfice: Natural Language Insight Generation

**Repository:** `docs/research/repos/perfice`

### Insight Text Generation

From `client/src/services/analytics/display.ts`:

```typescript
export function getInsightText(insight: HistoricalQuantitativeInsight, 
                               questionType: FormQuestionDataType): InsightText {
    let direction = insight.ratio > 1 ? "increased" : "decreased";
    let sign = insight.ratio > 1 ? "+" : "-";
    
    let percentage = numberToMaxDecimals(insight.diff * 100, 1);
    let currentFormatted = formatValueAsDataType(insight.current, questionType);
    let averageFormatted = formatValueAsDataType(insight.average, questionType);
    
    return {
        text: `greatly ${direction} (${currentFormatted}) compared to average ${averageFormatted}`,
        percentage: `(${sign}${percentage}%)`
    };
}
```

### Correlation Display Templates

```typescript
export function convertResultKey(key: string, result: CorrelationResult, 
                                  timeScope: SimpleTimeScopeType): CorrelationDisplay {
    if (result.lagged) {
        return {
            first: secondConverted,
            second: firstConverted,
            between: `after ${TIME_SCOPE_UNITS[timeScope]} with`
        }
    }
    
    return {
        first: firstConverted,
        second: secondConverted,
        between: "when"
    }
}
```

### Insight Templates for TrackLife

Based on Perfice's approach, here are recommended templates:

| Relationship Type | Template |
|-------------------|----------|
| Positive correlation | "{X} is higher when {Y} is higher (r={coef})" |
| Negative correlation | "{X} is lower when {Y} is higher (r={coef})" |
| Time-lagged (positive) | "{X} increases {lag} days after {Y} (r={coef})" |
| Time-lagged (negative) | "{X} decreases {lag} days after {Y} (r={coef})" |
| Categorical | "{X} is {direction} when '{category}' is tagged" |
| Week day pattern | "{X} is {direction} on {day}" |

### Python Implementation

```python
class InsightTemplates:
    """Natural language templates for correlation insights."""
    
    @staticmethod
    def format_correlation(var_x: str, var_y: str, coef: float, 
                           lag: int = 0, p_value: float = None) -> str:
        direction = "positively" if coef > 0 else "negatively"
        strength = interpret_strength(abs(coef))
        
        if lag == 0:
            template = f"{var_x} is {strength} {direction} correlated with {var_y}"
        else:
            template = f"{var_x} {lag} days ago {strength} predicts {var_y}"
        
        if p_value is not None and p_value < 0.05:
            template += f" (r={coef:.2f}, p={p_value:.3f})"
        else:
            template += f" (r={coef:.2f})"
        
        return template
    
    @staticmethod
    def format_recommendation(var_x: str, var_y: str, coef: float, 
                               lag: int = 0) -> str:
        if coef > 0:
            if lag > 0:
                return f"Focus on {var_x} today to improve {var_y} in {lag} days."
            else:
                return f"Consider stacking {var_x} with {var_y} for better consistency."
        else:
            if lag > 0:
                return f"Be mindful that high {var_x} may reduce {var_y} after {lag} days."
            else:
                return f"Monitor how {var_x} and {var_y} interact in your routine."
```

---

## 4. Quantified Sleep: ML-Based Lag Detection

**Repository:** `docs/research/repos/gianlucatruda/quantified-sleep`

### Markov Unfolding for Lag Features

This project uses a machine learning approach to identify optimal lags:

```python
# Create lagged features
def create_lagged_features(df, columns, max_lag=7):
    """Create time-lagged features for ML models."""
    lagged_df = df.copy()
    
    for col in columns:
        for lag in range(1, max_lag + 1):
            lagged_df[f"{col}_lag{lag}"] = df[col].shift(lag)
    
    return lagged_df.dropna()

# Use LASSO to identify important lags
from sklearn.linear_model import Lasso

def identify_important_lags(X, y, alpha=0.1):
    """
    LASSO automatically selects relevant lags by shrinking
    irrelevant coefficients to zero.
    """
    model = Lasso(alpha=alpha)
    model.fit(X, y)
    
    # Extract non-zero coefficients
    important_features = [
        (feat, coef) 
        for feat, coef in zip(X.columns, model.coef_) 
        if abs(coef) > 0.001
    ]
    
    return sorted(important_features, key=lambda x: abs(x[1]), reverse=True)
```

### Key Insights for TrackLife

1. **Automatic Lag Selection**: LASSO regression automatically identifies relevant lags
2. **Feature Importance**: Coefficient magnitude indicates lag importance
3. **Sparse Solutions**: Regularization prevents overfitting with many lag features

---

## 5. FitBaus: Correlation Matrix Dashboard

**Repository:** `docs/research/repos/markrai/fitbaus`

### Correlation Matrix Visualization

FitBaus provides a heatmap-based correlation matrix:

```python
# Correlation matrix as heatmap
import seaborn as sns
import matplotlib.pyplot as plt

def plot_correlation_matrix(df, title="Correlation Matrix"):
    """Plot correlation matrix as heatmap."""
    corr = df.corr()
    
    plt.figure(figsize=(12, 10))
    sns.heatmap(
        corr,
        annot=True,
        cmap='RdYlGn',  # Red for negative, Green for positive
        center=0,
        fmt='.2f',
        square=True
    )
    plt.title(title)
    plt.tight_layout()
    return plt
```

### Life-Event Impact Analysis

FitBaus includes interrupted time series analysis:

```python
def life_event_impact(df, event_date, metric, before_days=30, after_days=30):
    """
    Compare metrics before and after a life event.
    """
    before = df[df['date'] < event_date].tail(before_days)
    after = df[df['date'] >= event_date].head(after_days)
    
    from scipy import stats
    t_stat, p_value = stats.ttest_ind(before[metric], after[metric])
    
    return {
        'before_mean': before[metric].mean(),
        'after_mean': after[metric].mean(),
        'change': after[metric].mean() - before[metric].mean(),
        'p_value': p_value,
        'significant': p_value < 0.05
    }
```

---

## 6. HPI: Data Unification for Cross-Domain Correlation

**Repository:** `docs/research/repos/karlicoss/HPI`

### Module Ecosystem

HPI provides unified access to personal data from multiple sources:

```python
# Example: Cross-domain correlation
from my import body, github, browser

def correlate_productivity_with_sleep():
    """Correlate coding productivity with sleep quality."""
    # Get sleep data
    sleep = body.sleep.get_sleep_data()
    
    # Get GitHub activity
    commits = github.events.get_commit_events()
    
    # Merge by date
    merged_data = merge_by_date(sleep, commits)
    
    # Calculate correlation
    correlation = pearsonr(merged_data['sleep_quality'], 
                          merged_data['commit_count'])
    
    return correlation
```

### Timezone Normalization

```python
def normalize_timezones(events, location_history):
    """
    Use location history to infer correct timezone for each event.
    """
    for event in events:
        location = location_history.get_location_at(event.timestamp)
        timezone = infer_timezone(location)
        event.local_time = event.timestamp.astimezone(timezone)
    
    return events
```

---

## Comparison with Current Implementation

### Current `brain/analysis/correlation.py`

| Feature | Current Implementation | Research Recommendation |
|---------|----------------------|------------------------|
| Pearson correlation | ✅ Implemented | Complete |
| Spearman correlation | ✅ Implemented | Complete |
| Time-lag correlation | ✅ Basic implementation | Add CCF visualization |
| Granger causality | ❌ Not implemented | **Recommended addition** |
| FDR correction | ❌ Not implemented | **Recommended addition** |
| NLG insights | ✅ Basic templates | Enhance with Perfice patterns |
| Sign detection | ❌ Not implemented | Add from AutoVAR |
| Optimal lag detection | ✅ `find_best_lag` | Complete |

---

## Recommended Enhancements

### 1. Add Granger Causality Testing

```python
# brain/analysis/granger.py (new file)
from dataclasses import dataclass
from typing import List, Optional
import math

@dataclass
class GrangerResult:
    """Result of Granger causality test."""
    cause: str
    effect: str
    f_statistic: float
    p_value: float
    optimal_lag: int
    sign: str  # '+', '-', or '~'
    
    @property
    def is_significant(self) -> bool:
        return self.p_value < 0.05
    
    @property
    def is_almost_significant(self) -> bool:
        return self.p_value < 0.10


class GrangerCausalityEngine:
    """Granger causality testing for habit data."""
    
    def test_granger_causality(
        self,
        x: List[float],
        y: List[float],
        max_lag: int = 7,
        x_name: str = "x",
        y_name: str = "y"
    ) -> Optional[GrangerResult]:
        """
        Test if x Granger-causes y.
        
        Uses F-test for joint significance of lagged x coefficients
        in predicting y.
        """
        # Implementation using VAR or regression approach
        pass
```

### 2. Add FDR Correction for Multiple Tests

```python
def benjamini_hochberg_correction(p_values: List[float]) -> List[float]:
    """
    Apply Benjamini-Hochberg FDR correction.
    
    Essential when testing multiple correlations to control
    false discovery rate.
    """
    n = len(p_values)
    ranked_indices = sorted(range(n), key=lambda i: p_values[i])
    
    adjusted = [0.0] * n
    for rank, idx in enumerate(ranked_indices):
        adjusted[idx] = min(1.0, p_values[idx] * n / (rank + 1))
    
    # Ensure monotonicity
    for i in range(n - 2, -1, -1):
        adjusted[ranked_indices[i]] = min(
            adjusted[ranked_indices[i]],
            adjusted[ranked_indices[i + 1]]
        )
    
    return adjusted
```

### 3. Enhanced Insight Templates

```python
INSIGHT_TEMPLATES = {
    'positive_strong': {
        'template': "{x} strongly positively correlates with {y} (r={coef:.2f})",
        'recommendation': "These habits reinforce each other. Consider stacking them."
    },
    'positive_moderate': {
        'template': "{x} moderately correlates with {y} (r={coef:.2f})",
        'recommendation': "These habits may influence each other."
    },
    'negative_strong': {
        'template': "{x} strongly negatively correlates with {y} (r={coef:.2f})",
        'recommendation': "High {x} may be reducing {y}. Monitor this relationship."
    },
    'lagged_positive': {
        'template': "{x} {lag} days ago predicts higher {y} (r={coef:.2f})",
        'recommendation': "Focus on {x} today to improve {y} in {lag} days."
    },
    'lagged_negative': {
        'template': "{x} {lag} days ago predicts lower {y} (r={coef:.2f})",
        'recommendation': "Be mindful: high {x} may reduce {y} after {lag} days."
    },
    'granger_significant': {
        'template': "{x} Granger-causes {y} with {lag}-day lag (p={p:.3f})",
        'recommendation': "This is a predictive relationship worth leveraging."
    }
}
```

---

## Summary

### Key Takeaways

1. **Granger Causality** is the gold standard for time-lagged causal analysis - implement it
2. **FDR Correction** is essential when testing multiple correlations
3. **Natural Language Templates** from Perfice provide user-friendly insight generation
4. **Cross-Correlation Functions** visualize relationships across all lags
5. **Sign Detection** helps users understand positive vs negative relationships

### Implementation Priority

| Priority | Enhancement | Effort | Impact |
|----------|-------------|--------|--------|
| 1 | Granger causality testing | Medium | High |
| 2 | FDR correction | Low | High |
| 3 | Enhanced NLG templates | Low | Medium |
| 4 | CCF visualization | Medium | Medium |
| 5 | Sign detection | Low | Medium |

---

## References

- AutoVAR Documentation: http://autovarcore.nl/
- Perfice Repository: https://github.com/p0lloc/perfice
- Temporal Behavior Analysis: https://github.com/farhanaugustine/Temporal_Behavior_Analysis
- Quantified Sleep: https://github.com/gianlucatruda/quantified-sleep
- HPI: https://github.com/karlicoss/HPI
- FitBaus: https://github.com/markrai/fitbaus

---

*Last updated: February 2026*