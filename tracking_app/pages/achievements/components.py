"""
UI components for the Achievements page.

Contains all render functions for the achievements and gamification interface.
"""

import streamlit as st
from datetime import datetime
from typing import List, Dict

from tracking_app.models import Achievement

from .constants import DEFAULT_ACHIEVEMENTS, ACHIEVEMENT_CATEGORIES, XP_TIPS
from .helpers import (
    get_xp_progress,
    get_xp_remaining,
    format_xp,
)


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
        st.markdown(f"### XP: {format_xp(xp)}")
        st.progress(percentage / 100)
        st.caption(f"{format_xp(xp_in_level)} / {format_xp(xp_needed)} XP to Level {level + 1}")
        
        # XP to next level
        remaining = get_xp_remaining(xp, level)
        st.info(f"🎯 {format_xp(remaining)} XP needed for next level")
    
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
    achievements = DEFAULT_ACHIEVEMENTS
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
    
    achievements = DEFAULT_ACHIEVEMENTS
    storage = st.session_state.storage
    
    # Get unlocked achievements
    unlocked = storage.get_achievements(unlocked_only=True)
    unlocked_ids = [a.id for a in unlocked]
    
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
    
    col1, col2 = st.columns(2)
    
    for i, (action, reward) in enumerate(XP_TIPS):
        with col1 if i < 3 else col2:
            st.markdown(f"**{action}**")
            st.caption(reward)