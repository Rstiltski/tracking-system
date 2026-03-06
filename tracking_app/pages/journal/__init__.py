"""
Journal page components package.

This package contains modular components for the Journal tracking page.

Components:
- constants: Shared constants and configuration values
- helpers: Helper functions for category handling
- session_state: Session state management
- components: UI components for journal entries
"""

from .constants import (
    JOURNAL_CATEGORIES,
    JOURNAL_CATEGORY_EMOJIS,
    JOURNAL_PROMPTS,
)

from .helpers import (
    get_category_emoji,
    get_category_color,
)

from .session_state import init_session_state

from .components import (
    render_header,
    render_add_entry_form,
    render_entry_card,
    render_entry_list,
    render_search,
    render_edit_form,
)

__all__ = [
    # Constants
    "JOURNAL_CATEGORIES",
    "JOURNAL_CATEGORY_EMOJIS",
    "JOURNAL_PROMPTS",
    # Helpers
    "get_category_emoji",
    "get_category_color",
    # Session state
    "init_session_state",
    # Components
    "render_header",
    "render_add_entry_form",
    "render_entry_card",
    "render_entry_list",
    "render_search",
    "render_edit_form",
]