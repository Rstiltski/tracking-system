"""
Goals Page - Goal Tracking

Streamlit page for setting, tracking, and achieving personal goals.

Usage:
    streamlit run tracking_app/pages/goals.py
"""

import streamlit as st
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tracking_app.components.sidebar import render_sidebar
from tracking_app.pages.goals.session_state import init_session_state
from tracking_app.pages.goals.components import (
    render_header,
    render_add_goal_form,
    render_goals_summary,
    render_goals_list,
    render_edit_form,
)


# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="Goals - Veryfyn",
    page_icon="🎯",
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
    
    # Summary
    render_goals_summary()
    st.divider()
    
    # Add goal form
    render_add_goal_form()
    st.divider()
    
    # Edit form if needed
    render_edit_form()
    
    # Goals list
    render_goals_list()


if __name__ == "__main__":
    main()