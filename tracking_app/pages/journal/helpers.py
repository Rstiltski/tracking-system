"""Helper functions for the Journal page."""

from .constants import JOURNAL_CATEGORY_EMOJIS, JOURNAL_CATEGORY_COLORS

def get_category_emoji(category: str) -> str:
    return JOURNAL_CATEGORY_EMOJIS.get(category, "✍️")

def get_category_color(category: str) -> str:
    return JOURNAL_CATEGORY_COLORS.get(category, "#64748b")