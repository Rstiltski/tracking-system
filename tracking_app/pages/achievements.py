"""
Achievements Page - Gamification & Rewards

Streamlit page for viewing achievements, XP progress, and unlocked rewards.

Usage:
    streamlit run tracking_app/pages/achievements.py
"""

import streamlit as st
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tracking_app.storage import Storage, get_storage
from tracking_app.models import Achievement


# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="Achievements - Veryfyn",
    page_icon="🏆",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =============================================================================
# SESSION STATE
# =============================================================================

def init_session_state():
    """Initialize session state variables."""
    if 'storage' not in st.session_state:
        st.session_state.storage = get_storage()
    
    if 'user_xp' not in st.session_state:
        st.session_state.user_xp = st.session_state.storage.get_xp()
    
    if 'user_level' not in st.session_state:
        st.session_state.user_level = st.session_state.storage.get_level()


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_xp_for_level(level: int) -> int:
    """Calculate XP required for a given level."""
    if level <= 1:
        return 0
    return 100 + (level - 2) * 150


def get_level_from_xp(xp: int) -> int:
    """Calculate level from total XP."""
    level = 1
    while xp >= get_xp_for_level(level + 1):
        level += 1
    return level


def get_xp_progress(xp: int, level: int) -> tuple:
    """Get XP progress towards next level. Returns (current, needed, percentage)."""
    current_level_xp = get_xp_for_level(level)
    next_level_xp = get_xp_for_level(level + 1)
    
    xp_in_level = xp - current_level_xp
    xp_needed = next_level_xp - current_level_xp
    
    percentage = (xp_in_level / xp_needed * 100) if xp_needed > 0 else 100
    
    return xp_in_level, xp_needed, percentage


def get_default_achievements() -> List[Dict]:
    """Get list of default achievements."""
    return [
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


# =============================================================================
# RENDER FUNCTIONS
# =============================================================================

def render_sidebar():
    """Render sidebar with navigation."""
    with st.sidebar:
        st.title("🎯 Veryfyn")
        st.caption("Personal Tracking System")
        st.divider()
        
        # User Stats
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Level", st.session_state.user_level)
        with col2:
            st.metric("XP", st.session_state.user_xp)
        
        st.divider()
        
        # Navigation
        st.subheader("📊 Tracking")
        st.page_link("pages/dashboard.py", label="🏠 Dashboard", icon="🏠")
        st.page_link("pages/habits.py", label="✅ Habits", icon="✅")
        st.page_link("pages/tasks.py", label="📋 Tasks", icon="📋")
        st.page_link("pages/finances.py", label="💰 Finances", icon="💰")
        st.page_link("pages/health.py", label="❤️ Health", icon="❤️")
        st.page_link("pages/emotional_health.py", label="🌈 Emotional Health", icon="🌈")
        st.page_link("pages/time.py", label="⏱️ Time", icon="⏱️")
        st.page_link("pages/goals.py", label="🎯 Goals", icon="🎯")
        st.page_link("pages/achievements.py", label="🏆 Achievements", icon="🏆")


def render_header():
    """Render page header."""
    st.title("🏆 Achievements")
    st.markdown("Track your progress, earn XP, and unlock achievements!")


def render_level_progress():
    """Render level and XP progress."""
    st.subheader("📊 Level Progress")
    
    xp = st.session_state.user_xp
    level = st.session_state.user_level
    
    xp_in_level, xp_needed, percentage = get_xp_progress(xp, level)
    
    # Level display
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col1:
        # Large level badge
        st.markdown(
            f"""
            <div style="
                width: 100px;
                height: 100px;
                border-radius: 50%;
                background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 48px;
                font-weight: bold;
                color: white;
                margin: 0 auto;
                box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
            ">
                {level}
            </div>
            <p style="text-align: center; margin-top: 10px; font-weight: bold;">Level {level}</p>
            """,
            unsafe_allow_html=True
        )
    
    with col2:
        st.markdown(f"### XP: {xp:,}")
        st.progress(percentage / 100)
        st.caption(f"{xp_in_level:,} / {xp_needed:,} XP to Level {level + 1}")
        
        # XP to next level
        remaining = xp_needed - xp_in_level
        st.info(f"🎯 {remaining:,} XP needed for next level")
    
    with col3:
        next_level = level + 1
        st.markdown(
            f"""
            <div style="
                width: 80px;
                height: 80px;
                border-radius: 50%;
                background: #1e293b;
                border: 3px solid #334155;
                display: flex;
                align-items: center;
                justify-content: center;
                font-size: 36px;
                color: #64748b;
                margin: 0 auto;
            ">
                {next_level}
            </div>
            <p style="text-align: center; margin-top: 10px; color: #64748b;">Next Level</p>
            """,
            unsafe_allow_html=True
        )


def render_achievements_summary():
    """Render achievements summary."""
    achievements = get_default_achievements()
    storage = st.session_state.storage
    
    # Get unlocked achievements
    unlocked = storage.get_achievements(unlocked_only=True)
    unlocked_ids = [a.id for a in unlocked]
    
    total = len(achievements)
    unlocked_count = len([a for a in achievements if a['id'] in unlocked_ids])
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Achievements Unlocked", f"{unlocked_count}/{total}")
    
    with col2:
        total_xp_from_achievements = sum(
            a['xp_reward'] for a in achievements if a['id'] in unlocked_ids
        )
        st.metric("XP from Achievements", total_xp_from_achievements)
    
    with col3:
        locked = total - unlocked_count
        st.metric("Locked", locked)


def render_achievements_grid():
    """Render achievements in a grid by category."""
    st.subheader("🏅 Achievements")
    
    achievements = get_default_achievements()
    storage = st.session_state.storage
    
    # Get unlocked achievements
    unlocked = storage.get_achievements(unlocked_only=True)
    unlocked_ids = [a.id for a in unlocked]
    
    # Group by category
    categories = {
        "habits": "🎯 Habits",
        "tasks": "📋 Tasks",
        "goals": "🎯 Goals",
        "finances": "💰 Finances",
        "health": "❤️ Health",
        "milestone": "⭐ Milestones",
        "special": "🌟 Special"
    }
    
    # Tabs by category
    tab1, tab2, tab3, tab4 = st.tabs(["All", "Habits & Tasks", "Goals & Finances", "Milestones & Special"])
    
    with tab1:
        render_achievement_cards(achievements, unlocked_ids)
    
    with tab2:
        filtered = [a for a in achievements if a['category'] in ['habits', 'tasks']]
        render_achievement_cards(filtered, unlocked_ids)
    
    with tab3:
        filtered = [a for a in achievements if a['category'] in ['goals', 'finances', 'health']]
        render_achievement_cards(filtered, unlocked_ids)
    
    with tab4:
        filtered = [a for a in achievements if a['category'] in ['milestone', 'special']]
        render_achievement_cards(filtered, unlocked_ids)


def render_achievement_cards(achievements: List[Dict], unlocked_ids: List[str]):
    """Render achievement cards."""
    # Create rows of 3 achievements
    for i in range(0, len(achievements), 3):
        cols = st.columns(3)
        
        for j, col in enumerate(cols):
            if i + j < len(achievements):
                achievement = achievements[i + j]
                is_unlocked = achievement['id'] in unlocked_ids
                
                with col:
                    render_achievement_card(achievement, is_unlocked)


def render_achievement_card(achievement: Dict, is_unlocked: bool):
    """Render a single achievement card."""
    # Card styling based on unlock status
    if is_unlocked:
        bg_color = "linear-gradient(135deg, #1e293b 0%, #334155 100%)"
        border_color = "#10b981"
        opacity = "1.0"
    else:
        bg_color = "#0f172a"
        border_color = "#334155"
        opacity = "0.5"
    
    icon = achievement['icon'] if is_unlocked else "🔒"
    
    st.markdown(
        f"""
        <div style="
            background: {bg_color};
            border: 2px solid {border_color};
            border-radius: 15px;
            padding: 20px;
            text-align: center;
            opacity: {opacity};
            margin-bottom: 15px;
        ">
            <div style="font-size: 48px; margin-bottom: 10px;">{icon}</div>
            <div style="font-weight: bold; margin-bottom: 5px;">{achievement['name']}</div>
            <div style="font-size: 12px; color: #94a3b8; margin-bottom: 10px;">{achievement['description']}</div>
            <div style="color: #10b981; font-weight: bold;">+{achievement['xp_reward']} XP</div>
        </div>
        """,
        unsafe_allow_html=True
    )


def render_recent_unlocks():
    """Render recently unlocked achievements."""
    st.subheader("🎉 Recent Unlocks")
    
    storage = st.session_state.storage
    unlocked = storage.get_achievements(unlocked_only=True)
    
    if not unlocked:
        st.info("No achievements unlocked yet. Keep tracking to earn achievements!")
        return
    
    # Sort by unlock date (newest first)
    unlocked.sort(key=lambda a: a.unlocked_at if a.unlocked_at else datetime.min, reverse=True)
    
    # Show last 5 unlocked
    for achievement in unlocked[:5]:
        col1, col2, col3 = st.columns([1, 3, 2])
        
        with col1:
            st.markdown(f"### {achievement.icon}")
        
        with col2:
            st.markdown(f"**{achievement.name}**")
            st.caption(achievement.description)
        
        with col3:
            st.markdown(f"+{achievement.xp_reward} XP")
            if achievement.unlocked_at:
                st.caption(achievement.unlocked_at.strftime("%b %d, %Y"))
    
    if len(unlocked) > 5:
        st.caption(f"...and {len(unlocked) - 5} more achievements")


def render_xp_history():
    """Render XP earning tips."""
    st.subheader("💡 How to Earn XP")
    
    tips = [
        ("✅ Complete Habits", "+10 XP per habit"),
        ("📋 Complete Tasks", "+5-20 XP based on priority"),
        ("🎯 Complete Goals", "+50 XP per goal"),
        ("⏱️ Track Time", "+1 XP per minute"),
        ("🔥 Maintain Streaks", "+25 XP for 7-day streak"),
        ("🏆 Unlock Achievements", "Variable XP rewards"),
    ]
    
    col1, col2 = st.columns(2)
    
    for i, (action, reward) in enumerate(tips):
        with col1 if i < 3 else col2:
            st.markdown(f"**{action}**")
            st.caption(reward)


# =============================================================================
# MAIN FUNCTION
# =============================================================================

def main():
    """Main page entry point."""
    # Initialize
    init_session_state()
    
    # Render sidebar
    render_sidebar()
    
    # Main content
    render_header()
    st.divider()
    
    # Level progress
    render_level_progress()
    st.divider()
    
    # Achievements summary
    render_achievements_summary()
    st.divider()
    
    # Achievements grid
    render_achievements_grid()
    st.divider()
    
    # Recent unlocks
    render_recent_unlocks()
    st.divider()
    
    # XP tips
    render_xp_history()


if __name__ == "__main__":
    main()