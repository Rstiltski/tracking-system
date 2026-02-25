"""
Veryfyn Tracking System - Main Streamlit Application

Main entry point for the Streamlit-based tracking application.
Provides navigation to all tracking modules.

Usage:
    streamlit run tracking_app/app.py
"""

import streamlit as st
from datetime import datetime
import os
import sys

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Try imports for optional features
try:
    from tracking_app.storage import Storage
    STORAGE_AVAILABLE = True
except ImportError:
    STORAGE_AVAILABLE = False


# ============================================================================
# Page Configuration
# ============================================================================

st.set_page_config(
    page_title="Veryfyn - Personal Tracking System",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/Rstiltski/tracking-system',
        'Report a bug': 'https://github.com/Rstiltski/tracking-system/issues',
        'About': """
        # Veryfyn - Personal Tracking System
        
        A gamified personal tracking system for habits, finances, tasks, 
        health, time, and goals.
        
        Version: 1.0.0
        """
    }
)

# ============================================================================
# Session State Management
# ============================================================================

def init_session_state():
    """Initialize session state variables."""
    # User data
    if "user_xp" not in st.session_state:
        st.session_state.user_xp = 0
    if "user_level" not in st.session_state:
        st.session_state.user_level = 1
    
    # Theme preference
    if "theme" not in st.session_state:
        st.session_state.theme = "light"


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


# ============================================================================
# Sidebar Navigation
# ============================================================================

def render_sidebar():
    """Render the main sidebar with navigation."""
    with st.sidebar:
        # Logo/Title
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
            st.session_state.theme = "dark" if st.session_state.theme == "light" else "light"
            st.rerun()
        
        # Footer
        st.divider()
        st.caption(f"Version 1.0.0")
        st.caption(f"© {datetime.now().year} Veryfyn")


# ============================================================================
# Main Content
# ============================================================================

def render_dashboard():
    """Render the main dashboard content."""
    st.title("🏠 Dashboard")
    
    # Welcome message
    st.markdown(f"""
    ### Welcome back! 👋
    
    You're currently at **Level {st.session_state.user_level}** with **{st.session_state.user_xp} XP**.
    """)
    
    # Quick Stats
    st.subheader("📊 Quick Stats")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Habits Today", "0", delta=None)
    with col2:
        st.metric("Active Tasks", "0", delta=None)
    with col3:
        st.metric("Goals Progress", "0%", delta=None)
    with col4:
        st.metric("Current Streak", "0 days", delta=None)
    
    st.divider()
    
    # Quick Actions
    st.subheader("⚡ Quick Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("✅ Log Habit", use_container_width=True):
            st.switch_page("pages/habits.py")
    
    with col2:
        if st.button("📋 Add Task", use_container_width=True):
            st.switch_page("pages/tasks.py")
    
    with col3:
        if st.button("📊 View Charts", use_container_width=True):
            st.switch_page("pages/achievements.py")
    
    st.divider()
    
    # Features Overview
    st.subheader("🎯 Features")
    
    st.info("""
    **Tracking Modules Available:**
    
    • **Habits** - Track daily habits with streaks
    • **Tasks** - Manage todos with priorities
    • **Finances** - Monitor income and expenses
    • **Health** - Log weight, sleep, and mood
    • **Time** - Track time with built-in timer
    • **Goals** - Set and monitor goals
    
    **Gamification:**
    • Earn XP for completing tasks
    • Level up as you progress
    • Unlock achievements
    """)
    
    st.divider()
    
    # Recent Activity
    st.subheader("📈 Recent Activity")
    st.info("No recent activity to display. Start tracking to see your progress!")
    
    st.divider()
    
    # Getting Started Guide
    st.subheader("🚀 Getting Started")
    
    with st.expander("New to Veryfyn? Click here for a quick guide."):
        st.markdown("""
        ### Welcome to Veryfyn! 🎯
        
        Veryfyn is a comprehensive personal tracking system.
        
        #### Core Features:
        
        1. **📊 Tracking Modules**
           - **Habits**: Track daily habits with streaks
           - **Tasks**: Manage todos with priorities
           - **Finances**: Monitor income and expenses
           - **Health**: Log weight, sleep, and mood
           - **Time**: Track time with built-in timer
           - **Goals**: Set and monitor goals
        
        2. **🎮 Gamification**
           - Earn XP for completing tasks
           - Level up as you progress
           - Unlock achievements
        
        3. **📦 Data Management**
           - Export data in JSON, CSV, or SQLite
           - Import from previous exports
           - Automated backups with retention policies
        
        #### Quick Start:
        
        1. Navigate to **Habits** and create your first habit
        2. Add a task in **Tasks**
        3. Check **Achievements** for motivation
        """)


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Main application entry point."""
    # Initialize session state
    init_session_state()
    
    # Update level based on XP
    st.session_state.user_level = get_level_from_xp(st.session_state.user_xp)
    
    # Render sidebar
    render_sidebar()
    
    # Render main dashboard
    render_dashboard()


if __name__ == "__main__":
    main()