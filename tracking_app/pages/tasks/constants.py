"""
Constants for the Tasks page.

Contains categories, priorities, and configuration values.
"""

import streamlit as st
from typing import Dict, List

# Task categories
CATEGORIES: List[str] = [
    "Work",
    "Personal",
    "Health",
    "Finance",
    "Learning",
    "Home",
    "Other",
]

# Priority levels
PRIORITIES: List[str] = ["low", "medium", "high"]

# Cached priority lookup for O(1) access
# TTL=86400 (24h) - static data that never changes
@st.cache_data(ttl=86400)
def get_priority_index_map() -> Dict[str, int]:
    """Create a mapping of priority to index for O(1) lookup."""
    return {p: idx for idx, p in enumerate(PRIORITIES)}


def get_priority_index(priority: str) -> int:
    """Get the index of a priority, returning 0 if not found."""
    priority_map = get_priority_index_map()
    return priority_map.get(priority.lower(), 1)  # Default to medium (index 1)

# Priority colors
PRIORITY_COLORS = {
    "high": "#ef4444",
    "medium": "#f59e0b",
    "low": "#10b981",
}

# Priority icons
PRIORITY_ICONS = {
    "high": "🔴",
    "medium": "🟡",
    "low": "🟢",
}

# Priority labels with icons
PRIORITY_LABELS = {
    "low": "🟢 Low",
    "medium": "🟡 Medium",
    "high": "🔴 High",
}

# XP rewards for completing tasks by priority
XP_REWARDS = {
    "high": 20,
    "medium": 10,
    "low": 5,
}

# Status filter options
STATUS_OPTIONS = {
    "all": "All Tasks",
    "active": "Active",
    "completed": "Completed",
    "overdue": "Overdue",
}

# XP calculations
BASE_XP_PER_LEVEL = 100
XP_INCREMENT_PER_LEVEL = 150