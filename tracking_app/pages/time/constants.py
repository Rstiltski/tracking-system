"""
Constants for the Time page.

Contains time categories, XP rates, and configuration values.
"""

import streamlit as st
from typing import Dict, List

# Time categories
TIME_CATEGORIES: List[str] = [
    "General",
    "Work",
    "Learning",
    "Exercise",
    "Personal",
    "Break",
    "Other",
]

# Cached category lookup for O(1) access
# TTL=86400 (24h) - static data that never changes
@st.cache_data(ttl=86400)
def get_time_category_index_map() -> Dict[str, int]:
    """Create a mapping of time category to index for O(1) lookup."""
    return {cat: idx for idx, cat in enumerate(TIME_CATEGORIES)}


def get_time_category_index(category: str) -> int:
    """Get the index of a time category, returning 0 if not found."""
    category_map = get_time_category_index_map()
    return category_map.get(category, 0)

# XP rates
XP_PER_MINUTE = 1  # 1 XP per minute tracked
XP_PER_HOUR = 60   # 60 XP per hour for manual entry (consistent with timer)
XP_MINIMUM = 5     # Minimum XP for saving a time entry

# Timer display colors
TIMER_COLOR_RUNNING = "#10b981"  # Green
TIMER_COLOR_PAUSED = "#f8fafc"   # White/light

# Display settings
MAX_ENTRIES_DISPLAY = 10  # Maximum entries to show in recent entries list
