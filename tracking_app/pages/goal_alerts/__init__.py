"""
Goal Alerts Settings page package.

Provides goal milestone celebrations and deadline warnings configuration.
"""

from .session_state import init_session_state
from .components import (
    render_general_settings,
    render_milestone_settings,
    render_deadline_settings,
    render_category_settings,
    render_individual_goal_settings,
    render_recent_milestones,
    render_progress_overview,
)

__all__ = [
    'init_session_state',
    'render_general_settings',
    'render_milestone_settings',
    'render_deadline_settings',
    'render_category_settings',
    'render_individual_goal_settings',
    'render_recent_milestones',
    'render_progress_overview',
]