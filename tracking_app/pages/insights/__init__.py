"""
Insights page module.

Provides AI-powered intelligence dashboard components.
"""

from .constants import *
from .helpers import (
    gather_burnout_indicators,
    calculate_completion_trend,
    calculate_sleep_deviation,
    calculate_mood_trend,
    count_recent_streak_breaks,
    count_consecutive_missed_days,
    gather_habit_data_for_pcs,
    calculate_habit_correlations,
)
from .session_state import init_session_state
from .components import (
    render_header,
    render_burnout_section,
    render_correlations_section,
    render_pcs_section,
    render_insights_summary,
)