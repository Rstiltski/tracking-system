"""
Constants for the Achievements page.

Contains achievement definitions, categories, and configuration values.
"""

from typing import List, Dict

# XP calculations
BASE_XP_PER_LEVEL = 100
XP_INCREMENT_PER_LEVEL = 150

# Achievement categories
ACHIEVEMENT_CATEGORIES = {
    "streak": "🔥 Streak",
    "score": "📈 Score",
    "consistency": "✨ Consistency",
    "comeback": "🦅 Comeback",
    "mastery": "🧘 Mastery",
    "special": "🌟 Special",
    "habits": "🎯 Habits",
    "tasks": "📋 Tasks",
    "goals": "🎯 Goals",
    "finances": "💰 Finances",
    "health": "❤️ Health",
    "milestone": "⭐ Milestones",
}

# Default achievements (Phase 7.2 Enhanced - 29 total achievements)
DEFAULT_ACHIEVEMENTS: List[Dict] = [
    # Streak achievements
    {
        "id": "achieve_streak_7",
        "name": "Week Warrior",
        "description": "Maintain a 7-day streak",
        "icon": "🔥",
        "xp_reward": 50,
        "category": "streak",
        "tier": "bronze"
    },
    {
        "id": "achieve_streak_30",
        "name": "Month Master",
        "description": "Maintain a 30-day streak",
        "icon": "🌟",
        "xp_reward": 150,
        "category": "streak",
        "tier": "silver"
    },
    {
        "id": "achieve_streak_90",
        "name": "Quarter Queen/King",
        "description": "Maintain a 90-day streak",
        "icon": "👑",
        "xp_reward": 400,
        "category": "streak",
        "tier": "gold"
    },
    {
        "id": "achieve_streak_365",
        "name": "Yearly Legend",
        "description": "Maintain a 365-day streak",
        "icon": "🏆",
        "xp_reward": 1000,
        "category": "streak",
        "tier": "diamond"
    },
    
    # Score achievements
    {
        "id": "achieve_score_90",
        "name": "High Achiever",
        "description": "Maintain 90%+ score for 7 days",
        "icon": "📈",
        "xp_reward": 100,
        "category": "score",
        "tier": "silver"
    },
    
    # Consistency achievements (Unbreakable series)
    {
        "id": "achieve_unbreakable_7",
        "name": "Unbreakable Week",
        "description": "Don't miss a single day for 7 days straight",
        "icon": "🛡️",
        "xp_reward": 75,
        "category": "consistency",
        "tier": "bronze"
    },
    {
        "id": "achieve_unbreakable_14",
        "name": "Unbreakable Fortnight",
        "description": "Don't miss a single day for 14 days straight",
        "icon": "🏰",
        "xp_reward": 150,
        "category": "consistency",
        "tier": "silver"
    },
    {
        "id": "achieve_unbreakable_30",
        "name": "Unbreakable Month",
        "description": "Don't miss a single day for 30 days straight",
        "icon": "🏯",
        "xp_reward": 350,
        "category": "consistency",
        "tier": "gold"
    },
    {
        "id": "achieve_perfect_week",
        "name": "Perfect Week",
        "description": "Complete all habits for 7 days",
        "icon": "✨",
        "xp_reward": 300,
        "category": "consistency",
        "tier": "gold"
    },
    {
        "id": "achieve_flawless_week",
        "name": "Flawless Week",
        "description": "100% completion rate for a week",
        "icon": "💎",
        "xp_reward": 200,
        "category": "consistency",
        "tier": "silver"
    },
    {
        "id": "achieve_flawless_month",
        "name": "Flawless Month",
        "description": "100% completion rate for a month",
        "icon": "💫",
        "xp_reward": 750,
        "category": "consistency",
        "tier": "platinum"
    },
    
    # Comeback achievements
    {
        "id": "achieve_comeback",
        "name": "Phoenix Rising",
        "description": "Rebuild a streak after breaking it",
        "icon": "🦅",
        "xp_reward": 200,
        "category": "comeback",
        "tier": "silver"
    },
    {
        "id": "achieve_resilient",
        "name": "Resilient Soul",
        "description": "Recover from 0% to 80% score",
        "icon": "💪",
        "xp_reward": 200,
        "category": "comeback",
        "tier": "silver"
    },
    
    # Mastery achievements
    {
        "id": "achieve_mastery",
        "name": "Habit Master",
        "description": "Reach automaticity score of 6+",
        "icon": "🧘",
        "xp_reward": 500,
        "category": "mastery",
        "tier": "platinum"
    },
    
    # Special achievements
    {
        "id": "achieve_first_habit",
        "name": "First Step",
        "description": "Create your first habit",
        "icon": "🌱",
        "xp_reward": 25,
        "category": "special",
        "tier": "bronze"
    },
    {
        "id": "achieve_early_adopter",
        "name": "Early Bird",
        "description": "Complete a habit before 7 AM",
        "icon": "🌅",
        "xp_reward": 50,
        "category": "special",
        "tier": "bronze"
    },
    
    # Variety achievements (Renaissance)
    {
        "id": "achieve_variety_5",
        "name": "Renaissance Beginner",
        "description": "Track 5 different habits simultaneously",
        "icon": "🎨",
        "xp_reward": 100,
        "category": "special",
        "tier": "bronze"
    },
    {
        "id": "achieve_variety_10",
        "name": "Renaissance Enthusiast",
        "description": "Track 10 different habits simultaneously",
        "icon": "🎭",
        "xp_reward": 250,
        "category": "special",
        "tier": "silver"
    },
    {
        "id": "achieve_variety_15",
        "name": "Renaissance Master",
        "description": "Track 15 different habits simultaneously",
        "icon": "🎪",
        "xp_reward": 500,
        "category": "special",
        "tier": "gold"
    },
    
    # Dawn Patrol series (Early Bird expanded)
    {
        "id": "achieve_dawn_patrol_10",
        "name": "Dawn Patrol",
        "description": "Complete habits before 6 AM 10 times",
        "icon": "🌤️",
        "xp_reward": 75,
        "category": "special",
        "tier": "bronze"
    },
    {
        "id": "achieve_dawn_patrol_25",
        "name": "Early Riser",
        "description": "Complete habits before 6 AM 25 times",
        "icon": "🌄",
        "xp_reward": 175,
        "category": "special",
        "tier": "silver"
    },
    {
        "id": "achieve_dawn_patrol_50",
        "name": "Morning Champion",
        "description": "Complete habits before 6 AM 50 times",
        "icon": "☀️",
        "xp_reward": 400,
        "category": "special",
        "tier": "gold"
    },
    
    # Night Owl series
    {
        "id": "achieve_night_owl_10",
        "name": "Night Owl",
        "description": "Complete habits after 10 PM 10 times",
        "icon": "🌙",
        "xp_reward": 75,
        "category": "special",
        "tier": "bronze"
    },
    {
        "id": "achieve_night_owl_25",
        "name": "Midnight Worker",
        "description": "Complete habits after 10 PM 25 times",
        "icon": "🦉",
        "xp_reward": 175,
        "category": "special",
        "tier": "silver"
    },
    {
        "id": "achieve_night_owl_50",
        "name": "Nocturnal Legend",
        "description": "Complete habits after 10 PM 50 times",
        "icon": "🌟",
        "xp_reward": 400,
        "category": "special",
        "tier": "gold"
    },
    
    # Quantified Self series (Data Enthusiast)
    {
        "id": "achieve_data_100",
        "name": "Data Enthusiast",
        "description": "Log 100 habit entries",
        "icon": "📊",
        "xp_reward": 100,
        "category": "special",
        "tier": "bronze"
    },
    {
        "id": "achieve_data_500",
        "name": "Data Scientist",
        "description": "Log 500 habit entries",
        "icon": "📈",
        "xp_reward": 300,
        "category": "special",
        "tier": "silver"
    },
    {
        "id": "achieve_data_1000",
        "name": "Quantified Self Master",
        "description": "Log 1000 habit entries",
        "icon": "🏆",
        "xp_reward": 600,
        "category": "special",
        "tier": "gold"
    },
    
    # Hidden/Secret achievements
    {
        "id": "achieve_streak_freeze",
        "name": "???",
        "description": "Hidden achievement - keep tracking to discover!",
        "icon": "❓",
        "xp_reward": 50,
        "category": "special",
        "tier": "bronze",
        "is_hidden": True
    },
    {
        "id": "achieve_weekend_warrior",
        "name": "???",
        "description": "Hidden achievement - keep tracking to discover!",
        "icon": "❓",
        "xp_reward": 200,
        "category": "consistency",
        "tier": "silver",
        "is_hidden": True
    },
]

# XP earning tips
XP_TIPS = [
    ("✅ Complete Habits", "+10 XP per habit"),
    ("📋 Complete Tasks", "+5-20 XP based on priority"),
    ("🎯 Complete Goals", "+50 XP per goal"),
    ("⏱️ Track Time", "+1 XP per minute"),
    ("🔥 Maintain Streaks", "+25 XP for 7-day streak"),
    ("🏆 Unlock Achievements", "Variable XP rewards"),
]

# Tier colors for display
TIER_COLORS = {
    "bronze": "#CD7F32",
    "silver": "#C0C0C0",
    "gold": "#FFD700",
    "platinum": "#E5E4E2",
    "diamond": "#B9F2FF",
}

# Tier emojis for display
TIER_EMOJIS = {
    "bronze": "🥉",
    "silver": "🥈",
    "gold": "🥇",
    "platinum": "💎",
    "diamond": "💠",
}

# =============================================================================
# CACHED LOOKUP FUNCTIONS - O(1) dictionary access instead of O(n) list search
# =============================================================================

import streamlit as st
from typing import Optional, List, Dict, Any


@st.cache_data(ttl=3600, show_spinner=False)
def get_achievement_by_id(achievement_id: str) -> Optional[Dict[str, Any]]:
    """
    Get achievement data by ID using O(1) dictionary lookup.
    
    Args:
        achievement_id: The achievement ID to look up
        
    Returns:
        Achievement dictionary or None if not found
    """
    return _ACHIEVEMENT_BY_ID.get(achievement_id)


@st.cache_data(ttl=3600, show_spinner=False)
def get_achievements_by_category(category: str) -> List[Dict[str, Any]]:
    """
    Get all achievements in a category using O(1) dictionary lookup.
    
    Args:
        category: The category to filter by
        
    Returns:
        List of achievements in that category
    """
    return _ACHIEVEMENTS_BY_CATEGORY.get(category, [])


@st.cache_data(ttl=3600, show_spinner=False)
def get_tier_color(tier: str) -> str:
    """
    Get color for a tier using O(1) dictionary lookup.
    
    Args:
        tier: The tier name (bronze, silver, gold, platinum, diamond)
        
    Returns:
        Hex color code
    """
    return TIER_COLORS.get(tier, "#808080")


@st.cache_data(ttl=3600, show_spinner=False)
def get_tier_emoji(tier: str) -> str:
    """
    Get emoji for a tier using O(1) dictionary lookup.
    
    Args:
        tier: The tier name (bronze, silver, gold, platinum, diamond)
        
    Returns:
        Tier emoji
    """
    return TIER_EMOJIS.get(tier, "🏅")


@st.cache_data(ttl=3600, show_spinner=False)
def get_category_display(category_key: str) -> str:
    """
    Get display name for a category using O(1) dictionary lookup.
    
    Args:
        category_key: The category key
        
    Returns:
        Display name with icon
    """
    return ACHIEVEMENT_CATEGORIES.get(category_key, category_key)


@st.cache_data(ttl=3600, show_spinner=False)
def get_all_achievement_ids() -> List[str]:
    """
    Get list of all achievement IDs.
    
    Returns:
        List of achievement ID strings
    """
    return list(_ACHIEVEMENT_BY_ID.keys())


@st.cache_data(ttl=3600, show_spinner=False)
def get_categories() -> List[str]:
    """
    Get list of all category keys.
    
    Returns:
        List of category key strings
    """
    return list(ACHIEVEMENT_CATEGORIES.keys())


# Build O(1) lookup dictionaries at module load time
_ACHIEVEMENT_BY_ID: Dict[str, Dict[str, Any]] = {
    achievement["id"]: achievement for achievement in DEFAULT_ACHIEVEMENTS
}

_ACHIEVEMENTS_BY_CATEGORY: Dict[str, List[Dict[str, Any]]] = {}
for achievement in DEFAULT_ACHIEVEMENTS:
    category = achievement.get("category", "special")
    if category not in _ACHIEVEMENTS_BY_CATEGORY:
        _ACHIEVEMENTS_BY_CATEGORY[category] = []
    _ACHIEVEMENTS_BY_CATEGORY[category].append(achievement)