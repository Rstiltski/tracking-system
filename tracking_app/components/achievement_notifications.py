"""
Achievement Notifications Component

Phase 7.2: Achievement notification system for unlock celebrations.
Provides in-app toast notifications and celebration effects.

Usage:
    from tracking_app.components.achievement_notifications import (
        show_achievement_unlocked,
        show_level_up,
        show_streak_milestone,
    )
"""

import streamlit as st
from datetime import datetime
from typing import Optional, Dict, Any


def show_achievement_unlocked(
    achievement_name: str,
    achievement_icon: str,
    xp_reward: int,
    tier: str = "bronze"
) -> None:
    """
    Show achievement unlocked notification.
    
    Args:
        achievement_name: Name of the unlocked achievement
        achievement_icon: Emoji icon for the achievement
        xp_reward: XP awarded for the achievement
        tier: Achievement tier (bronze/silver/gold/platinum/diamond)
    """
    tier_colors = {
        "bronze": "#CD7F32",
        "silver": "#C0C0C0",
        "gold": "#FFD700",
        "platinum": "#E5E4E2",
        "diamond": "#B9F2FF",
    }
    
    tier_emojis = {
        "bronze": "🥉",
        "silver": "🥈",
        "gold": "🥇",
        "platinum": "💎",
        "diamond": "💠",
    }
    
    color = tier_colors.get(tier, "#CD7F32")
    tier_emoji = tier_emojis.get(tier, "🥉")
    
    # Show celebration message
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
            border: 3px solid {color};
            border-radius: 20px;
            padding: 20px;
            text-align: center;
            animation: pulse 0.5s ease-in-out;
            margin-bottom: 20px;
        ">
            <div style="font-size: 48px; margin-bottom: 10px;">{achievement_icon}</div>
            <div style="font-size: 14px; color: {color}; margin-bottom: 5px;">{tier_emoji} {tier.upper()} ACHIEVEMENT UNLOCKED!</div>
            <div style="font-size: 20px; font-weight: bold; color: white; margin-bottom: 10px;">{achievement_name}</div>
            <div style="font-size: 16px; color: #10b981; font-weight: bold;">+{xp_reward} XP</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Also show a toast notification
    st.toast(f"🏆 Achievement Unlocked: {achievement_name} (+{xp_reward} XP)", icon="🎉")


def show_level_up(
    new_level: int,
    total_xp: int,
    rewards_unlocked: Optional[list] = None
) -> None:
    """
    Show level up celebration.
    
    Args:
        new_level: New level achieved
        total_xp: Total XP earned
        rewards_unlocked: List of rewards unlocked at this level
    """
    st.markdown(
        f"""
        <div style="
            background: linear-gradient(135deg, #6366f1 0%, #8b5cf6 100%);
            border-radius: 20px;
            padding: 25px;
            text-align: center;
            margin-bottom: 20px;
        ">
            <div style="font-size: 48px; margin-bottom: 10px;">🎉</div>
            <div style="font-size: 14px; color: #c7d2fe; margin-bottom: 5px;">LEVEL UP!</div>
            <div style="font-size: 36px; font-weight: bold; color: white; margin-bottom: 10px;">Level {new_level}</div>
            <div style="font-size: 14px; color: #c7d2fe;">Total XP: {total_xp:,}</div>
        </div>
        """,
        unsafe_allow_html=True
    )
    
    if rewards_unlocked:
        st.markdown("**🎁 Rewards Unlocked:**")
        for reward in rewards_unlocked:
            st.markdown(f"- {reward}")
    
    st.toast(f"🎉 Level Up! You're now Level {new_level}!", icon="🎊")


def show_streak_milestone(
    streak_days: int,
    habit_name: str
) -> None:
    """
    Show streak milestone celebration.
    
    Args:
        streak_days: Number of days in streak
        habit_name: Name of the habit
    """
    # Determine milestone type
    if streak_days >= 365:
        milestone = "LEGENDARY"
        emoji = "🏆"
    elif streak_days >= 90:
        milestone = "AMAZING"
        emoji = "👑"
    elif streak_days >= 30:
        milestone = "IMPRESSIVE"
        emoji = "🌟"
    elif streak_days >= 14:
        milestone = "GREAT"
        emoji = "🔥"
    elif streak_days >= 7:
        milestone = "SOLID"
        emoji = "💪"
    else:
        milestone = "STARTING"
        emoji = "🌱"
    
    st.toast(f"{emoji} {streak_days} day streak on {habit_name}!", icon="🔥")


def render_achievement_notification_container(
    unlocked_achievements: list,
    max_display: int = 3
) -> None:
    """
    Render a container showing recent achievement notifications.
    
    Args:
        unlocked_achievements: List of recently unlocked achievements
        max_display: Maximum number to display
    """
    if not unlocked_achievements:
        return
    
    st.markdown("### 🎉 Recent Achievements")
    
    for achievement in unlocked_achievements[:max_display]:
        col1, col2 = st.columns([1, 4])
        
        with col1:
            st.markdown(f"### {achievement.get('icon', '🏆')}")
        
        with col2:
            st.markdown(f"**{achievement.get('name', 'Unknown')}**")
            st.caption(achievement.get('description', ''))
            st.markdown(f"+{achievement.get('xp_reward', 50)} XP")
        
        st.divider()


def check_and_notify_achievements(
    storage: Any,
    user_id: str = "default"
) -> list:
    """
    Check for newly unlocked achievements and return them for notification.
    
    Args:
        storage: Storage instance
        user_id: User ID to check
    
    Returns:
        List of newly unlocked achievements
    """
    newly_unlocked = []
    
    # Check session state for already notified achievements
    notified_key = f"notified_achievements_{user_id}"
    if notified_key not in st.session_state:
        st.session_state[notified_key] = set()
    
    # Get unlocked achievements
    if hasattr(storage, 'get_achievements'):
        unlocked = storage.get_achievements(unlocked_only=True)
        
        for ach in unlocked:
            ach_id = ach.id if hasattr(ach, 'id') else ach.get('id', '')
            
            if ach_id not in st.session_state[notified_key]:
                newly_unlocked.append(ach)
                st.session_state[notified_key].add(ach_id)
    
    return newly_unlocked


__all__ = [
    "show_achievement_unlocked",
    "show_level_up",
    "show_streak_milestone",
    "render_achievement_notification_container",
    "check_and_notify_achievements",
]