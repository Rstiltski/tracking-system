"""
Constants for the Diary page.

Defines mood options, emojis, and writing prompts.
"""

# Diary mood options
DIARY_MOODS = [
    "amazing",
    "great",
    "good",
    "okay",
    "bad",
    "terrible",
]

# Mood to emoji mapping
DIARY_MOOD_EMOJIS = {
    "amazing": "🤩",
    "great": "😊",
    "good": "🙂",
    "okay": "😐",
    "bad": "😕",
    "terrible": "😢",
}

# Mood to color mapping
DIARY_MOOD_COLORS = {
    "amazing": "#22c55e",  # green
    "great": "#84cc16",    # lime
    "good": "#eab308",     # yellow
    "okay": "#f97316",     # orange
    "bad": "#ef4444",      # red
    "terrible": "#7c3aed", # purple
}

# Writing prompts for diary entries
DIARY_PROMPTS = [
    "What made you smile today?",
    "What are you grateful for today?",
    "What challenged you today?",
    "What did you learn today?",
    "How are you feeling right now?",
    "What's on your mind?",
    "Describe your day in three words.",
    "What would you do differently today?",
    "What's something that surprised you today?",
    "What are you looking forward to tomorrow?",
]

# Default tags for diary entries
DEFAULT_DIARY_TAGS = [
    "personal",
    "work",
    "family",
    "health",
    "goals",
    "memories",
    "dreams",
    "ideas",
    "gratitude",
    "reflection",
]