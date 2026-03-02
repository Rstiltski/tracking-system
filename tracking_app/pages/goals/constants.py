"""
Constants for the Goals page.

Contains goal icons, status colors, and configuration values.
"""

from typing import List

# Goal icons
GOAL_ICONS = ["🎯", "📚", "💪", "💰", "🏃", "🎨", "💼", "🧠", "❤️", "🏠", "✈️", "🎸"]

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