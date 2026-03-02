"""
Constants for the Task Alerts page.
"""

# Page configuration
PAGE_TITLE = "Task Alerts"
PAGE_ICON = "📋"
PAGE_LAYOUT = "wide"

# Default user ID
DEFAULT_USER_ID = "default"

# Notification channel options
CHANNEL_OPTIONS = ["Email", "Browser", "In-App"]
ALL_CHANNELS_OPTION = "All Channels"

# Urgency levels
URGENCY_LOW = "low"
URGENCY_MEDIUM = "medium"
URGENCY_HIGH = "high"
URGENCY_CRITICAL = "critical"

# Urgency display info
URGENCY_COLORS = {
    'low': '🟢',
    'medium': '🟡',
    'high': '🟠',
    'critical': '🔴'
}

# Default threshold values
DEFAULT_EARLY_WARNING_HOURS = 24
DEFAULT_FINAL_WARNING_HOURS = 1
DEFAULT_MEDIUM_THRESHOLD_HOURS = 24
DEFAULT_HIGH_THRESHOLD_HOURS = 4

# Reminder frequency options
REMINDER_FREQUENCY_OPTIONS = ["Once", "Daily", "Every 4 hours", "Every hour"]

# Default digest time
DEFAULT_DIGEST_TIME_HOUR = 7
DEFAULT_DIGEST_TIME_MINUTE = 0

# Priority levels
PRIORITY_HIGH = "high"
PRIORITY_MEDIUM = "medium"
PRIORITY_LOW = "low"

# Priority icons
PRIORITY_ICONS = {
    'high': '🔴',
    'medium': '🟡',
    'low': '🟢'
}