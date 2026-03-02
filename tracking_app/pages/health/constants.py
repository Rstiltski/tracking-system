"""
Constants for the Health page.

Contains mood options, icons, colors, and configuration values.
"""

from tracking_app.models import Mood


# Mood options with icons
MOOD_OPTIONS = {
    Mood.GREAT.value: "😊 Great",
    Mood.GOOD.value: "🙂 Good",
    Mood.OKAY.value: "😐 Okay",
    Mood.BAD.value: "😔 Bad",
}

# Mood icons mapping
MOOD_ICONS = {
    Mood.GREAT.value: "😊",
    Mood.GOOD.value: "🙂",
    Mood.OKAY.value: "😐",
    Mood.BAD.value: "😔",
}

# Mood colors mapping
MOOD_COLORS = {
    Mood.GREAT.value: "#10b981",
    Mood.GOOD.value: "#6366f1",
    Mood.OKAY.value: "#f59e0b",
    Mood.BAD.value: "#ef4444",
}

# Mood numeric values for charts
MOOD_VALUES = {
    Mood.GREAT.value: 4,
    Mood.GOOD.value: 3,
    Mood.OKAY.value: 2,
    Mood.BAD.value: 1,
}

# Default values
DEFAULT_MOOD = Mood.GOOD.value

# Weight range
WEIGHT_MIN = 0.0
WEIGHT_MAX = 500.0

# Sleep range
SLEEP_MIN = 0.0
SLEEP_MAX = 24.0

# History display limit
HISTORY_LIMIT = 10