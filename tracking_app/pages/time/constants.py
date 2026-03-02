"""
Constants for the Time page.

Contains time categories, XP rates, and configuration values.
"""

from typing import List

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

# XP rates
XP_PER_MINUTE = 1  # 1 XP per minute tracked
XP_PER_HOUR = 10   # 10 XP per hour for manual entry
XP_MINIMUM = 5     # Minimum XP for saving a time entry

# Timer display colors
TIMER_COLOR_RUNNING = "#10b981"  # Green
TIMER_COLOR_PAUSED = "#f8fafc"   # White/light

# Display settings
MAX_ENTRIES_DISPLAY = 10  # Maximum entries to show in recent entries list