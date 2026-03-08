"""
Constants for the Dashboard page.

Contains XP values, quotes, and configuration values.
"""

from typing import List, Tuple

# XP rewards
XP_HABIT_COMPLETE = 10
XP_TASK_COMPLETE = {"high": 20, "medium": 10, "low": 5}

# Activity settings
ACTIVITY_LIMIT = 10  # Maximum activities to fetch
DISPLAY_TASK_LIMIT = 5  # Maximum tasks to display
DISPLAY_GOAL_LIMIT = 5  # Maximum goals to display

# Score calculation
SCORE_LOOKBACK_DAYS = 60
SIMPLE_SCORE_LOOKBACK = 30

# Streak calculation
MAX_STREAK_DAYS = 365

# Weekly chart
WEEKLY_CHART_DAYS = 7

# Motivational quotes
MOTIVATIONAL_QUOTES: List[Tuple[str, str]] = [
    ("The secret of getting ahead is getting started.", "Mark Twain"),
    ("It's not about perfect. It's about effort.", "Jillian Michaels"),
    ("Small daily improvements are the key to staggering long-term results.", "Unknown"),
    ("Success is the sum of small efforts repeated day in and day out.", "Robert Collier"),
    ("The only way to do great work is to love what you do.", "Steve Jobs"),
    ("Don't watch the clock; do what it does. Keep going.", "Sam Levenson"),
    ("Your limitation—it's only your imagination.", "Unknown"),
    ("Push yourself, because no one else is going to do it for you.", "Unknown"),
]

# Priority icons
PRIORITY_ICONS = {
    "high": "🔴",
    "medium": "🟡",
    "low": "🟢",
}

# Burnout thresholds
BURNOUT_HIGH_THRESHOLD = 50
BURNOUT_MODERATE_THRESHOLD = 25

# =============================================================================
# CACHED LOOKUP FUNCTIONS
# =============================================================================

import random
import streamlit as st
from typing import List, Tuple, Optional


@st.cache_data(ttl=3600, show_spinner=False)
def get_random_quote() -> Tuple[str, str]:
    """
    Get a random motivational quote.
    
    Returns:
        Tuple of (quote, author)
    """
    return random.choice(MOTIVATIONAL_QUOTES)


# TTL=86400 (24h) - static lookup
@st.cache_data(ttl=86400, show_spinner=False)
def get_priority_icon(priority: str) -> str:
    """
    Get icon for priority level using O(1) lookup.
    
    Args:
        priority: Priority level (high, medium, low)
        
    Returns:
        Priority emoji
    """
    return PRIORITY_ICONS.get(priority, "⚪")


# TTL=86400 (24h) - static calculation
@st.cache_data(ttl=86400, show_spinner=False)
def get_xp_for_task_priority(priority: str) -> int:
    """
    Get XP reward for task completion by priority.
    
    Args:
        priority: Task priority (high, medium, low)
        
    Returns:
        XP amount
    """
    return XP_TASK_COMPLETE.get(priority, 5)