"""
Sidebar Component - Unified Navigation

Provides consistent sidebar navigation across all pages.

Usage:
    from tracking_app.components.sidebar import render_sidebar
"""
import streamlit as st
from datetime import datetime


def render_sidebar():
    """
    Render the main sidebar with navigation.
    
    Displays:
    - App title and logo
    - User stats (Level, XP)
    - Navigation links to all pages
    - Theme toggle
    """
    with st.sidebar:
        # Logo/Title
        st.title("🎯 Veryfyn")
        st.caption("Personal Tracking System")
        st.divider()
        
        # User Stats
        col1, col2 = st.columns(2)
        with col1:
            level = st.session_state.get('user_level', 1)
            st.metric("Level", level)
        with col2:
            xp = st.session_state.get('user_xp', 0)
            st.metric("XP", xp)
        
        # XP Progress Bar
        from tracking_app.components.session import get_xp_for_level
        current_xp = st.session_state.get('user_xp', 0)
        current_level = st.session_state.get('user_level', 1)
        next_level_xp = get_xp_for_level(current_level + 1)
        current_level_xp = get_xp_for_level(current_level)
        
        if next_level_xp > current_level_xp:
            progress = (current_xp - current_level_xp) / (next_level_xp - current_level_xp)
            st.progress(min(progress, 1.0), text=f"Progress to Level {current_level + 1}")
        
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


__all__ = ["render_sidebar"]