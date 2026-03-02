"""
Constants for the Habit Reminders page.
"""

# Page configuration
PAGE_TITLE = "Habit Reminders"
PAGE_ICON = "🎯"
PAGE_LAYOUT = "wide"

# Default values
DEFAULT_REMINDER_TIME_HOUR = 8
DEFAULT_REMINDER_TIME_MINUTE = 0
DEFAULT_SNOOZE_DURATION = 5  # minutes

# Smart scheduling defaults
DEFAULT_MIN_SAMPLES = 5
DEFAULT_CONFIDENCE_THRESHOLD = 0.7
MIN_SAMPLES_RANGE = (3, 14)
CONFIDENCE_RANGE = (0.5, 0.95)

# Streak protection defaults
DEFAULT_WARNING_HOURS = 8
DEFAULT_ESCALATION_HOURS = 4
DEFAULT_CRITICAL_HOURS = 2

# Snooze options
DEFAULT_SNOOZE_OPTIONS = [5, 10, 15, 30]
ALL_SNOOZE_OPTIONS = [5, 10, 15, 20, 30, 45, 60]
DEFAULT_MAX_SNOOZES = 3
MAX_SNOOZES_RANGE = (1, 10)

# Days of week
DAYS_OF_WEEK = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']