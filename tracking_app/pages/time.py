"""
Time Page - Time Tracking

Streamlit page for tracking time with a built-in timer and time categorization.

Usage:
    streamlit run tracking_app/pages/time.py
"""

import streamlit as st
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tracking_app.components.sidebar import render_sidebar
from tracking_app.pages.time.session_state import init_session_state
from tracking_app.pages.time.components import (
    render_header,
    render_timer,
    render_manual_entry,
    render_daily_summary,
    render_weekly_chart,
    render_time_entries,
)


# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="Time - Veryfyn",
    page_icon="⏱️",
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
    
    # Timer
    render_timer()
    st.divider()
    
    # Manual entry
    render_manual_entry()
    
    # Daily summary
    render_daily_summary()
    st.divider()
    
    # Weekly chart
    render_weekly_chart()
    st.divider()
    
    # Time entries
    render_time_entries()


if __name__ == "__main__":
    main()