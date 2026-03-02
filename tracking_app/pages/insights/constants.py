"""
Constants for the Insights page.

Contains configuration values and thresholds.
"""

from typing import Dict, Any

# Analysis lookback periods
COMPLETION_TREND_DAYS = 14
SLEEP_DEVIATION_DAYS = 14
MOOD_TREND_DAYS = 14
STREAK_BREAK_LOOKBACK = 7
PCS_MINIMUM_DAYS = 14
CORRELATION_DAYS = 30
MAX_MISSED_DAYS_LOOKBACK = 30

# Correlation settings
MIN_CORRELATION_SAMPLES = 7
MAX_CORRELATIONS_DISPLAY = 5

# Sleep baseline
SLEEP_BASELINE_HOURS = 7.5

# Mood mapping
MOOD_SCORES: Dict[str, float] = {
    "great": 1.0,
    "good": 0.75,
    "okay": 0.5,
    "bad": 0.25,
}

# Default stress level (when no data)
DEFAULT_STRESS_LEVEL = 5

# Burnout risk thresholds
BURNOUT_HIGH_THRESHOLD = 70
BURNOUT_MODERATE_THRESHOLD = 40

# Completion trend scaling
COMPLETION_TREND_SCALE = 5.0
MOOD_TREND_SCALE = 4.0