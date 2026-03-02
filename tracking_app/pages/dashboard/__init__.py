"""
Dashboard page components.

Modular components for the Dashboard page.
"""

from tracking_app.pages.dashboard.session_state import init_session_state
from tracking_app.pages.dashboard.components import (
    render_welcome,
    render_quick_stats,
    render_habit_scores_section,
    render_quick_actions,
    render_todays_habits,
    render_active_tasks,
    render_goals_progress,
    render_burnout_indicator,
    render_activity_feed,
    render_motivational_quote,
)

__all__ = [
    "init_session_state",
    "render_welcome",
    "render_quick_stats",
    "render_habit_scores_section",
    "render_quick_actions",
    "render_todays_habits",
    "render_active_tasks",
    "render_goals_progress",
    "render_burnout_indicator",
    "render_activity_feed",
    "render_motivational_quote",
]