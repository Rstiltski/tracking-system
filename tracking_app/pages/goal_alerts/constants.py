"""
Constants for the Goal Alerts page.

Contains page configuration and default settings.
"""

# Page configuration
PAGE_TITLE = "Goal Alerts"
PAGE_ICON = "🎯"
LAYOUT = "wide"

# Default user ID for demo
DEFAULT_USER_ID = "default"

# Default milestone percentages
DEFAULT_MILESTONES = [25, 50, 75, 100]
DEFAULT_CUSTOM_MILESTONES = [10, 90]

# Default deadline warning settings
DEFAULT_WARNING_DAYS = 7
DEFAULT_FINAL_WARNING_DAYS = 1
DEFAULT_PROGRESS_THRESHOLD = 75

# Celebration styles
CELEBRATION_STYLES = ["Simple notification", "Animated celebration", "Sound + Animation"]

# Goal categories with default settings
GOAL_CATEGORIES = [
    ('health', '🏃 Health & Fitness', True),
    ('finance', '💰 Financial', True),
    ('learning', '📚 Learning', True),
    ('career', '💼 Career', True),
    ('personal', '🏠 Personal', True),
]