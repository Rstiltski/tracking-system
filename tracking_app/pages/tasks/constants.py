"""
Constants for the Tasks page.

Contains categories, priorities, and configuration values.
"""

# Task categories
CATEGORIES = [
    "Work",
    "Personal",
    "Health",
    "Finance",
    "Learning",
    "Home",
    "Other",
]

# Priority levels
PRIORITIES = ["low", "medium", "high"]

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