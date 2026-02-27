"""
Sidebar Component - Unified Navigation

Provides consistent sidebar navigation across all pages.

Usage:
    from tracking_app.components.sidebar import render_sidebar
"""
import streamlit as st
from datetime import datetime
from typing import Optional


def render_sidebar(show_streak_freeze: bool = False):
    """
    Render the main sidebar with navigation.
    
    Displays:
    - App title and logo
    - User stats (Level, XP)
    - Navigation links to all pages
    - Optional Streak Freeze section (for habits page)
    - Theme toggle
    
    Args:
        show_streak_freeze: If True, show streak freeze inventory section
    """
    with st.sidebar:
        # Logo/Title
        st.title("🎯 Veryfyn")
        st.caption("Personal Tracking System")
        st.divider()
        
        # User Stats
        level = st.session_state.get('user_level', 1)
        xp = st.session_state.get('user_xp', 0)
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Level", level)
        with col2:
            st.metric("XP", xp)
        
        # XP Progress Bar
        from tracking_app.components.session import get_xp_for_level
        current_xp = xp
        current_level = level
        next_level_xp = get_xp_for_level(current_level + 1)
        current_level_xp = get_xp_for_level(current_level)
        
        if next_level_xp > current_level_xp:
            progress = (current_xp - current_level_xp) / (next_level_xp - current_level_xp)
            # Ensure progress is always between 0 and 1
            progress = max(0.0, min(1.0, progress))
            st.progress(progress, text=f"Progress to Level {current_level + 1}")
        
        st.divider()
        
        # Streak Freeze Inventory (optional - shown on habits page)
        if show_streak_freeze:
            _render_streak_freeze_section()
            st.divider()
        
        # Main Navigation
        st.subheader("📊 Tracking")
        
        # Core tracking modules
        tracking_pages = [
            ("🏠 Dashboard", "dashboard"),
            ("✅ Habits", "habits"),
            ("📋 Tasks", "tasks"),
            ("💰 Finances", "finances"),
            ("❤️ Health", "health"),
            ("🌈 Emotional Health", "emotional_health"),
            ("⏱️ Time", "time"),
            ("🎯 Goals", "goals"),
            ("🏆 Achievements", "achievements"),
        ]
        
        for page_name, page_file in tracking_pages:
            st.page_link(f"pages/{page_file}.py", label=page_name)
        
        st.divider()
        
        # Data Management
        st.subheader("📦 Data")
        
        data_pages = [
            ("📤 Export", "data_export"),
            ("📥 Import", "data_import"),
            ("💾 Backup", "backup_restore"),
            ("🔄 Lifecycle", "data_lifecycle"),
        ]
        
        for page_name, page_file in data_pages:
            st.page_link(f"pages/{page_file}.py", label=page_name)
        
        st.divider()
        
        # Notifications
        st.subheader("🔔 Alerts")
        
        notification_pages = [
            ("⚙️ Notifications", "notification_settings"),
            ("⏰ Habit Reminders", "habit_reminders"),
            ("📋 Task Alerts", "task_alerts"),
            ("🎯 Goal Alerts", "goal_alerts"),
        ]
        
        for page_name, page_file in notification_pages:
            st.page_link(f"pages/{page_file}.py", label=page_name)
        
        st.divider()
        
        # Theme toggle
        if st.button("🌙 Toggle Theme", use_container_width=True):
            current_theme = st.session_state.get('theme', 'light')
            new_theme = "dark" if current_theme == "light" else "light"
            st.session_state.theme = new_theme
            # Save to storage
            if 'storage' in st.session_state:
                st.session_state.storage.set_user_data('theme', new_theme)
            st.rerun()
        
        # Footer
        st.divider()
        st.caption(f"Version 2.0.0")
        st.caption(f"© {datetime.now().year} Veryfyn")


def _render_streak_freeze_section():
    """Render streak freeze inventory section."""
    try:
        from brain.models.streak import StreakFreeze
    except ImportError:
        st.caption("❄️ Streak Freeze unavailable")
        return
    
    # Load streak freeze inventory
    storage = st.session_state.get('storage')
    if not storage:
        return
    
    freeze_data = storage.get_user_data("streak_freeze", None)
    
    if freeze_data:
        streak_freeze = StreakFreeze.from_dict(freeze_data)
    else:
        streak_freeze = StreakFreeze(count=1)  # Start with 1 free freeze
    
    st.subheader("❄️ Streak Freezes")
    
    # Display freeze count with visual indicator
    freeze_progress = streak_freeze.count / streak_freeze.max_freezes
    st.progress(freeze_progress, text=f"{streak_freeze.count}/{streak_freeze.max_freezes} available")
    
    # Purchase freeze button
    if not streak_freeze.is_maxed:
        xp = st.session_state.get('user_xp', 0)
        if st.button(f"🛒 Buy Freeze ({streak_freeze.xp_cost} XP)", 
                    help="Purchase a streak freeze to protect your streaks",
                    use_container_width=True):
            success, new_xp = streak_freeze.purchase_freeze(xp)
            if success:
                st.session_state.user_xp = new_xp
                storage.set_user_data("streak_freeze", streak_freeze.to_dict())
                if 'storage' in st.session_state:
                    st.session_state.storage.set_xp(new_xp)
                st.success("❄️ Streak Freeze purchased!")
                st.rerun()
            else:
                st.error(f"Not enough XP! Need {streak_freeze.xp_cost} XP.")
    else:
        st.caption("✅ Max freezes reached!")
    
    # Update session state for use in other functions
    st.session_state.streak_freeze = streak_freeze


__all__ = ["render_sidebar"]