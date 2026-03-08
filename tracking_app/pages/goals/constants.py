"""
Constants for the Goals page.

Contains goal icons, status colors, and configuration values.
"""

import streamlit as st
from typing import Dict, List

# Goal icons
GOAL_ICONS: List[str] = ["🎯", "📚", "💪", "💰", "🏃", "🎨", "💼", "🧠", "❤️", "🏠", "✈️", "🎸"]

# Cached icon lookup for O(1) access
@st.cache_data(ttl=3600)
def get_goal_icon_index_map() -> Dict[str, int]:
    """Create a mapping of icon to index for O(1) lookup."""
    return {icon: idx for idx, icon in enumerate(GOAL_ICONS)}


def get_goal_icon_index(icon: str) -> int:
    """Get the index of an icon, returning 0 if not found."""
    icon_map = get_goal_icon_index_map()
    return icon_map.get(icon, 0)

# Status colors
STATUS_COLORS = {
    "completed": "#10b981",  # Green
    "overdue": "#ef4444",    # Red
    "warning": "#f59e0b",    # Yellow/Orange
    "active": "#6366f1",     # Indigo
}

# XP rewards
XP_GOAL_COMPLETED = 50

# Days thresholds
OVERDUE_THRESHOLD = 0
WARNING_DAYS_THRESHOLD = 7