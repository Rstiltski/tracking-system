"""
Achievements Page - Gamification & Rewards

Streamlit page for viewing achievements, XP progress, and unlocked rewards.

Usage:
    streamlit run tracking_app/pages/achievements.py
"""

import streamlit as st
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tracking_app.components.sidebar import render_sidebar
from tracking_app.pages.achievements.session_state import init_session_state
from tracking_app.pages.achievements.components import (
    render_header,
    render_level_progress,
    render_achievements_summary,
    render_achievements_grid,
    render_recent_unlocks,
    render_xp_history,
)


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
# MAIN FUNCTION
# =============================================================================

def main():
    """Main page entry point."""
    # Initialize session state
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