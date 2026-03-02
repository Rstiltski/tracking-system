"""
Habits Page - Habit Tracking

Streamlit page for creating, tracking, and managing daily habits with streaks
and scientific habit scoring using exponential smoothing algorithm.

Usage:
    streamlit run tracking_app/pages/habits.py

Features:
- Habit Score: 0-100% using exponential smoothing (forgiving, gradual decay)
- Score Categories: Excellent, Strong, Developing, Building, Starting
- Trend Indicators: Shows if habit is improving or declining
- Streak Tracking: Current and best streak counts
- Sorting & Filtering: Sort by name, score, streak; filter by status
- Accessibility: Text labels for colorblind users
- Streak Freeze: Visual indicators and easy-to-use freeze system
- Enhanced Table: Sticky columns, progress bars, weekend/today highlighting
"""
import streamlit as st
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tracking_app.storage import get_storage
from tracking_app.components.sidebar import render_sidebar

# Import all components from the habits package
from tracking_app.pages.habits import (
    # Session state
    init_session_state,
    # Components
    render_habit_header,
    render_edit_habit_modal,
    render_habits_list,
)


# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="Habits - Veryfyn",
    page_icon="✅",
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
    
    # Render sidebar with streak freeze section
    render_sidebar(show_streak_freeze=True)
    
    # Render page header with gamification elements
    render_habit_header()
    st.divider()
    
    # Render edit form modal if a habit is being edited
    render_edit_habit_modal()
    
    # Render main habits list (includes spreadsheet view with add habit button)
    render_habits_list()


if __name__ == "__main__":
    main()