"""
Dashboard Page - Main Overview

Streamlit page providing an overview of all tracking metrics with quick access
to habits and tasks, weekly progress charts, and motivational quotes.

Usage:
    streamlit run tracking_app/pages/dashboard.py
"""

import streamlit as st
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tracking_app.components.sidebar import render_sidebar
from tracking_app.components.session import get_storage
from tracking_app.pages.dashboard.session_state import init_session_state
from tracking_app.pages.dashboard.components import (
    render_welcome,
    render_quick_stats,
    render_habit_scores_section,
    render_quick_actions,
    render_todays_habits,
    render_active_tasks,
    render_goals_progress,
    render_burnout_indicator,
    render_activity_feed,
    render_motivational_quote,
)
from tracking_app.pages.dashboard.helpers import get_weekly_habit_data
from tracking_app.components.charts import render_weekly_chart


# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="Dashboard - Veryfyn",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =============================================================================
# MAIN FUNCTION
# =============================================================================

def main():
    """Main page entry point."""
    # Initialize session state
    init_session_state()
    
    # Render sidebar
    render_sidebar()
    
    # Main content
    render_welcome()
    st.divider()
    
    # Quick stats
    render_quick_stats()
    st.divider()
    
    # Habit scores (new feature from brain models)
    render_habit_scores_section()
    st.divider()
    
    # Quick actions
    render_quick_actions()
    st.divider()
    
    # Two column layout
    col1, col2 = st.columns(2)
    
    with col1:
        render_todays_habits()
    
    with col2:
        render_active_tasks()
    
    st.divider()
    
    # Goals and weekly chart
    col1, col2 = st.columns(2)
    
    with col1:
        render_goals_progress()
    
    with col2:
        # Weekly chart
        storage = get_storage()
        weekly_data = get_weekly_habit_data(storage)
        render_weekly_chart(weekly_data)
    
    st.divider()
    
    # Wellbeing and Activity
    col1, col2 = st.columns(2)
    
    with col1:
        render_burnout_indicator()
    
    with col2:
        render_activity_feed()
    
    st.divider()
    
    # Motivational quote
    render_motivational_quote()


if __name__ == "__main__":
    main()