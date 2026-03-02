"""
Achievements page components.

Modular components for the Achievements & Gamification page.
"""

from tracking_app.pages.achievements.session_state import init_session_state
from tracking_app.pages.achievements.components import (
    render_header,
    render_level_progress,
    render_achievements_summary,
    render_achievements_grid,
    render_recent_unlocks,
    render_xp_history,
)

__all__ = [
    "init_session_state",
    "render_header",
    "render_level_progress",
    "render_achievements_summary",
    "render_achievements_grid",
    "render_recent_unlocks",
    "render_xp_history",
]