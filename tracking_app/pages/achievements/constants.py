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
    "habits": "🎯 Habits",
    "tasks": "📋 Tasks",
    "goals": "🎯 Goals",
    "finances": "💰 Finances",
    "health": "❤️ Health",
    "milestone": "⭐ Milestones",
    "special": "🌟 Special",
}

# Default achievements
DEFAULT_ACHIEVEMENTS: List[Dict] = [
    # Habits achievements
    {
        "id": "first_habit",
        "name": "First Steps",
        "description": "Create your first habit",
        "icon": "🎯",
        "xp_reward": 10,
        "category": "habits"
    },
    {
        "id": "habit_streak_7",
        "name": "Week Warrior",
        "description": "Maintain a 7-day habit streak",
        "icon": "🔥",
        "xp_reward": 25,
        "category": "habits"
    },
    {
        "id": "habit_streak_30",
        "name": "Monthly Master",
        "description": "Maintain a 30-day habit streak",
        "icon": "🌟",
        "xp_reward": 100,
        "category": "habits"
    },
    {
        "id": "habit_streak_100",
        "name": "Century Club",
        "description": "Maintain a 100-day habit streak",
        "icon": "💎",
        "xp_reward": 500,
        "category": "habits"
    },
    # Tasks achievements
    {
        "id": "first_task",
        "name": "Getting Things Done",
        "description": "Complete your first task",
        "icon": "✅",
        "xp_reward": 5,
        "category": "tasks"
    },
    {
        "id": "tasks_10",
        "name": "Productivity Starter",
        "description": "Complete 10 tasks",
        "icon": "📋",
        "xp_reward": 20,
        "category": "tasks"
    },
    {
        "id": "tasks_50",
        "name": "Task Master",
        "description": "Complete 50 tasks",
        "icon": "🎖️",
        "xp_reward": 50,
        "category": "tasks"
    },
    {
        "id": "tasks_100",
        "name": "Productivity Pro",
        "description": "Complete 100 tasks",
        "icon": "🏅",
        "xp_reward": 100,
        "category": "tasks"
    },
    # Goals achievements
    {
        "id": "first_goal",
        "name": "Dream Big",
        "description": "Set your first goal",
        "icon": "🎯",
        "xp_reward": 10,
        "category": "goals"
    },
    {
        "id": "goal_complete",
        "name": "Achiever",
        "description": "Complete a goal",
        "icon": "🏆",
        "xp_reward": 50,
        "category": "goals"
    },
    {
        "id": "goals_5",
        "name": "Goal Getter",
        "description": "Complete 5 goals",
        "icon": "⭐",
        "xp_reward": 100,
        "category": "goals"
    },
    # Finances achievements
    {
        "id": "first_transaction",
        "name": "Financial Awareness",
        "description": "Log your first transaction",
        "icon": "💰",
        "xp_reward": 5,
        "category": "finances"
    },
    {
        "id": "transactions_30",
        "name": "Budget Tracker",
        "description": "Log 30 transactions",
        "icon": "📊",
        "xp_reward": 30,
        "category": "finances"
    },
    # Health achievements
    {
        "id": "first_health",
        "name": "Health Conscious",
        "description": "Log your first health entry",
        "icon": "❤️",
        "xp_reward": 5,
        "category": "health"
    },
    {
        "id": "health_7",
        "name": "Week of Wellness",
        "description": "Log health entries for 7 days",
        "icon": "💪",
        "xp_reward": 25,
        "category": "health"
    },
    # Milestone achievements
    {
        "id": "level_5",
        "name": "Rising Star",
        "description": "Reach Level 5",
        "icon": "⭐",
        "xp_reward": 50,
        "category": "milestone"
    },
    {
        "id": "level_10",
        "name": "Dedicated Tracker",
        "description": "Reach Level 10",
        "icon": "🌟",
        "xp_reward": 100,
        "category": "milestone"
    },
    {
        "id": "level_25",
        "name": "Tracking Champion",
        "description": "Reach Level 25",
        "icon": "👑",
        "xp_reward": 250,
        "category": "milestone"
    },
    {
        "id": "level_50",
        "name": "Legendary Tracker",
        "description": "Reach Level 50",
        "icon": "🐉",
        "xp_reward": 500,
        "category": "milestone"
    },
    # Special achievements
    {
        "id": "early_bird",
        "name": "Early Bird",
        "description": "Complete a habit before 8 AM",
        "icon": "🌅",
        "xp_reward": 15,
        "category": "special"
    },
    {
        "id": "night_owl",
        "name": "Night Owl",
        "description": "Complete a task after midnight",
        "icon": "🦉",
        "xp_reward": 15,
        "category": "special"
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