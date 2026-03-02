"""
Rewards Page - Variable Rewards UI.

This page provides a gamified reward system using B.F. Skinner's
Variable Ratio reinforcement schedule.

Features:
- View reward inventory
- Roll for rewards on habit completion
- View reward statistics
- Display rarity badges

Architecture:
- Constants defined in constants.py
- Helpers in helpers.py
- Session state in session_state.py
- UI components in components.py
"""

import streamlit as st

from .rewards.constants import PAGE_TITLE, PAGE_ICON, PAGE_LAYOUT
from .rewards.session_state import init_session_state, get_user_xp, get_user_level
from .rewards.components import (
    render_header,
    render_roll_section,
    render_inventory,
    render_reward_catalog,
    render_stats,
    render_science,
)


def render_sidebar() -> None:
    """Render sidebar with navigation."""
    with st.sidebar:
        st.title("🎯 Veryfyn")
        st.caption("Personal Tracking System")
        st.divider()
        
        # User Stats
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Level", get_user_level())
        with col2:
            st.metric("XP", get_user_xp())
        
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
        
        st.divider()
        st.page_link("pages/insights.py", label="🧠 Insights", icon="🧠")
        st.page_link("pages/stacks.py", label="📚 Stacks", icon="📚")
        st.page_link("pages/rewards.py", label="🎁 Rewards", icon="🎁")


def main() -> None:
    """Main page entry point."""
    # Page configuration
    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon=PAGE_ICON,
        layout=PAGE_LAYOUT
    )
    
    # Initialize session state
    init_session_state()
    
    # Render sidebar
    render_sidebar()
    
    # Main content
    render_header()
    st.divider()
    
    # Roll section
    render_roll_section()
    st.divider()
    
    # Tabs for different views
    tab1, tab2, tab3 = st.tabs(["Inventory", "Catalog", "Statistics"])
    
    with tab1:
        render_inventory()
    
    with tab2:
        render_reward_catalog()
    
    with tab3:
        render_stats()
    
    st.divider()
    render_science()


if __name__ == "__main__":
    main()