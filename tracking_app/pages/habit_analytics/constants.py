"""
Constants for the Habit Analytics page.

Contains page configuration and display settings.
"""

# Page configuration
PAGE_TITLE = "Habit Analytics - Veryfyn"
PAGE_ICON = "📊"
LAYOUT = "wide"
INITIAL_SIDEBAR_STATE = "expanded"

# Available years for analysis
AVAILABLE_YEARS = [2024, 2025, 2026]
DEFAULT_YEAR_INDEX = 2  # 2026

# Heatmap colors (GitHub-style)
HEATMAP_COLORS = ["#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"]

# Chart color
CHART_COLOR = "#6366f1"

# Correlation strength emojis
CORRELATION_EMOJIS = {
    "strong": "💪",
    "moderate": "👍",
    "weak": "📊"
}