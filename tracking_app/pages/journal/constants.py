"""
Constants for the Journal page.

Defines categories, emojis, and writing prompts.
"""

# Journal categories
JOURNAL_CATEGORIES = [
    "reflection",
    "gratitude",
    "ideas",
    "dreams",
    "goals",
    "memories",
    "free_write",
]

# Category to emoji mapping
JOURNAL_CATEGORY_EMOJIS = {
    "reflection": "🪞",
    "gratitude": "🙏",
    "ideas": "💡",
    "dreams": "🌙",
    "goals": "🎯",
    "memories": "📸",
    "free_write": "✍️",
}

# Category to color mapping
JOURNAL_CATEGORY_COLORS = {
    "reflection": "#6366f1",  # indigo
    "gratitude": "#22c55e",  # green
    "ideas": "#eab308",      # yellow
    "dreams": "#8b5cf6",     # purple
    "goals": "#f97316",      # orange
    "memories": "#ec4899",   # pink
    "free_write": "#64748b", # slate
}

# Category descriptions
JOURNAL_CATEGORY_DESCRIPTIONS = {
    "reflection": "Look back on experiences and learnings",
    "gratitude": "Express appreciation for life's blessings",
    "ideas": "Capture creative thoughts and inspirations",
    "dreams": "Record nighttime dreams and aspirations",
    "goals": "Plan and track your objectives",
    "memories": "Preserve special moments and experiences",
    "free_write": "Write without constraints or structure",
}

# Writing prompts by category
JOURNAL_PROMPTS = {
    "reflection": [
        "What did I learn today?",
        "How did I grow this week?",
        "What would I do differently?",
        "What patterns am I noticing in my life?",
        "What challenged me recently?",
    ],
    "gratitude": [
        "What are three things I'm grateful for today?",
        "Who made a positive impact on my life recently?",
        "What simple pleasure brought me joy today?",
        "What accomplishment am I proud of?",
        "What opportunity am I thankful for?",
    ],
    "ideas": [
        "What problem would I like to solve?",
        "If I could create anything, what would it be?",
        "What would make life better for others?",
        "What's a wild idea I've been afraid to share?",
        "How could I combine two unrelated things?",
    ],
    "dreams": [
        "What dream do I remember from last night?",
        "What's a goal I've been afraid to pursue?",
        "Where do I see myself in 5 years?",
        "What would I do if I couldn't fail?",
        "What adventure is calling to me?",
    ],
    "goals": [
        "What's my most important goal right now?",
        "What small step can I take today?",
        "What habits do I want to build?",
        "What would success look like in 6 months?",
        "What obstacles might I face?",
    ],
    "memories": [
        "What's a childhood memory that makes me smile?",
        "What was the best day of my life so far?",
        "Who has influenced me the most?",
        "What lesson did I learn from a mistake?",
        "What moment would I want to relive?",
    ],
    "free_write": [
        "What's on my mind right now?",
        "How am I feeling at this moment?",
        "What do I need to let go of?",
        "What brings me peace?",
        "What am I looking forward to?",
    ],
}