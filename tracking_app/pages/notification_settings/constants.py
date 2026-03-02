"""
Constants for the Notification Settings page.
"""

# Page configuration
PAGE_TITLE = "Notification Settings - Veryfyn"
PAGE_ICON = "🔔"
PAGE_LAYOUT = "wide"

# Default user ID
DEFAULT_USER_ID = "default"

# Notification type configurations
NOTIFICATION_TYPES = [
    ('habit', '🎯 Habits', 'Reminders for habit completion'),
    ('task', '📋 Tasks', 'Task deadline alerts'),
    ('goal', '🎯 Goals', 'Goal milestone celebrations'),
    ('achievement', '🏆 Achievements', 'Achievement unlock notifications'),
    ('streak_warning', '🔥 Streak Warnings', 'Alerts when streak is at risk'),
    ('daily_digest', '📰 Daily Digest', 'Morning summary of your day'),
]

# Quiet hours defaults
DEFAULT_QUIET_HOURS_START = (22, 0)  # 10 PM
DEFAULT_QUIET_HOURS_END = (7, 0)     # 7 AM

# Smart scheduling
MIN_LEAD_MINUTES = 5
MAX_LEAD_MINUTES = 60
DEFAULT_LEAD_MINUTES = 15

# Notification history limit
HISTORY_LIMIT = 10

# Type icons mapping
TYPE_ICONS = {
    'habit_reminder': '🎯',
    'task_due': '📋',
    'goal_deadline': '🎯',
    'streak_warning': '🔥',
    'achievement': '🏆',
    'system': '⚙️',
    'reward': '🎁',
    'daily_digest': '📰',
}