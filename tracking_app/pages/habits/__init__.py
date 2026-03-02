"""
Habits page components package.

This package contains modular components for the Habits tracking page.

Components:
- constants: Shared constants and configuration values
- helpers: Helper functions for calculations and utilities
- session_state: Session state management
- header: Page header with gamification elements
- add_form: Form for adding new habits
- edit_form: Form for editing existing habits
- navigation: Navigation controls and period selector
- spreadsheet: Interactive spreadsheet-style habit matrix
- card_view: Individual habit cards with actions
- progress_rings: Visual progress ring components
"""

from .constants import (
    XP_PER_COMPLETION,
    XP_LEVELS,
    HABIT_ICONS,
    HABIT_COLORS,
    STREAK_FREEZE_LIMIT,
)

from .helpers import (
    get_local_date,
    get_week_start,
    get_month_start,
    get_time_until_midnight,
    is_entry_completed,
    calculate_streak,
    get_completion_rate,
    calculate_habit_score,
    get_score_category,
    get_trend_indicator,
    check_streak_break_yesterday,
    get_level_from_xp,
    get_xp_progress_in_level,
)

from .session_state import (
    init_session_state,
    load_streak_freeze,
    save_streak_freeze,
    use_streak_freeze_for_habit,
)

from .header import render_header as render_habit_header

from .add_form import render_add_habit_form, render_add_habit_form_inline

from .edit_form import render_edit_habit_form, render_edit_habit_modal

from .navigation import render_navigation_controls

from .spreadsheet import render_matrix_view, render_enhanced_matrix_view

from .card_view import render_habit_card, render_habits_list

from .progress_rings import (
    render_progress_ring,
    render_progress_summary,
    render_mini_progress_ring,
)

__all__ = [
    # Constants
    "XP_PER_COMPLETION",
    "XP_LEVELS",
    "HABIT_ICONS",
    "HABIT_COLORS",
    "STREAK_FREEZE_LIMIT",
    # Helpers
    "get_local_date",
    "get_week_start",
    "get_month_start",
    "get_time_until_midnight",
    "is_entry_completed",
    "calculate_streak",
    "get_completion_rate",
    "calculate_habit_score",
    "get_score_category",
    "get_trend_indicator",
    "check_streak_break_yesterday",
    "get_level_from_xp",
    "get_xp_progress_in_level",
    # Session state
    "init_session_state",
    "load_streak_freeze",
    "save_streak_freeze",
    "use_streak_freeze_for_habit",
    # Components
    "render_habit_header",
    "render_add_habit_form",
    "render_add_habit_form_inline",
    "render_edit_habit_form",
    "render_edit_habit_modal",
    "render_navigation_controls",
    "render_matrix_view",
    "render_enhanced_matrix_view",
    "render_habit_card",
    "render_habits_list",
    "render_progress_ring",
    "render_progress_summary",
    "render_mini_progress_ring",
]