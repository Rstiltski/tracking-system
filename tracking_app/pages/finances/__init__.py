"""
Finances Page Components.

Modular components for the Finances page.
"""

from .constants import (
    EXPENSE_CATEGORIES,
    INCOME_CATEGORIES,
    PERIOD_OPTIONS,
    TYPE_OPTIONS,
    DEFAULT_CURRENCY,
)
from .helpers import (
    get_date_range,
    calculate_totals,
    get_category_totals,
    format_currency,
)
from .session_state import init_session_state
from .components import (
    render_header,
    render_summary,
    render_add_transaction_form,
    render_filters,
    render_transactions_list,
    render_transaction_card,
    render_category_breakdown,
)

__all__ = [
    # Constants
    "EXPENSE_CATEGORIES",
    "INCOME_CATEGORIES",
    "PERIOD_OPTIONS",
    "TYPE_OPTIONS",
    "DEFAULT_CURRENCY",
    # Helpers
    "get_date_range",
    "calculate_totals",
    "get_category_totals",
    "format_currency",
    # Session state
    "init_session_state",
    # Components
    "render_header",
    "render_summary",
    "render_add_transaction_form",
    "render_filters",
    "render_transactions_list",
    "render_transaction_card",
    "render_category_breakdown",
]