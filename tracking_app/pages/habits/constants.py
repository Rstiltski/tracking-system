"""
Constants for the Habits page.

Contains all module-level constants including icons, colors, score categories,
and magic numbers as named constants.
"""

import streamlit as st
from typing import Dict, List, Tuple

# Icon options for habits
HABIT_ICONS: List[str] = ["🎯", "🏃", "📚", "💧", "🧘", "💪", "🌅", "📝", "🍎", "🛏️",
               "🚭", "💊", "🧹", "🎨", "🎵", "💻", "🧠", "❤️", "🌱", "⭐"]

# Cached icon lookup dict for O(1) access (avoids O(n) list.index())
# TTL=86400 (24h) - static data that never changes
@st.cache_data(ttl=86400)
def get_icon_index_map() -> Dict[str, int]:
    """Create a mapping of icon to index for O(1) lookup."""
    return {icon: idx for idx, icon in enumerate(HABIT_ICONS)}


def get_icon_index(icon: str) -> int:
    """Get the index of an icon, returning 0 if not found."""
    icon_map = get_icon_index_map()
    return icon_map.get(icon, 0)

# Color options for habits (name, hex)
HABIT_COLORS = [
    ("Indigo", "#6366f1"),
    ("Blue", "#3b82f6"),
    ("Green", "#10b981"),
    ("Yellow", "#f59e0b"),
    ("Red", "#ef4444"),
    ("Purple", "#8b5cf6"),
    ("Pink", "#ec4899"),
    ("Teal", "#14b8a6"),
]

# Score category thresholds
SCORE_CATEGORIES = {
    "excellent": {"min": 0.85, "label": "Excellent", "color": "#4CAF50", "emoji": "🌟"},
    "strong": {"min": 0.70, "label": "Strong", "color": "#8BC34A", "emoji": "💪"},
    "developing": {"min": 0.50, "label": "Developing", "color": "#FFC107", "emoji": "🌱"},
    "building": {"min": 0.30, "label": "Building", "color": "#FF9800", "emoji": "🔧"},
    "starting": {"min": 0.0, "label": "Starting", "color": "#F44336", "emoji": "🆕"},
}

# Magic numbers as named constants
MAX_STREAK_LOOKBACK_DAYS = 365
DEFAULT_SCORE_LOOKBACK_DAYS = 90
DEFAULT_COMPLETION_RATE_DAYS = 30
XP_PER_COMPLETION = 10
INITIAL_STREAK_FREEZE_COUNT = 1
STREAK_FREEZE_LIMIT = 5  # Maximum streak freezes a user can hold

# XP level thresholds (cumulative XP needed for each level)
XP_LEVELS = {
    1: 0,
    2: 100,
    3: 250,
    4: 450,
    5: 700,
    6: 1000,
    7: 1400,
    8: 1900,
    9: 2500,
    10: 3200,
}

# Category colors for habit tags (matching HTML research)
CATEGORY_COLORS = {
    "health": {"bg": "#fee2e2", "color": "#991b1b", "icon": "❤️"},
    "productivity": {"bg": "#e0e7ff", "color": "#3730a3", "icon": "📊"},
    "mindfulness": {"bg": "#d1fae5", "color": "#065f46", "icon": "🧘"},
    "fitness": {"bg": "#fef3c7", "color": "#92400e", "icon": "💪"},
    "learning": {"bg": "#e0f2fe", "color": "#075985", "icon": "📚"},
    "other": {"bg": "#e5e7eb", "color": "#6b7280", "icon": "📌"},
}

# Category options for selection
CATEGORY_OPTIONS = [
    ("health", "Health", "❤️"),
    ("productivity", "Productivity", "📊"),
    ("mindfulness", "Mindfulness", "🧘"),
    ("fitness", "Fitness", "💪"),
    ("learning", "Learning", "📚"),
    ("other", "Other", "📌"),
]