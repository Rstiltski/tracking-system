"""
Health Page - Health Metrics Tracking

Streamlit page for tracking weight, sleep, mood, and other health metrics.

Usage:
    streamlit run tracking_app/pages/health.py
"""

import streamlit as st
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tracking_app.components.sidebar import render_sidebar
from tracking_app.pages.health.session_state import init_session_state
from tracking_app.pages.health.components import (
    render_header,
    render_quick_log,
    render_summary,
    render_charts,
    render_history,
)


# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="Health - Veryfyn",
    page_icon="❤️",
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
    
    # Quick log
    render_quick_log()
    st.divider()
    
    # Summary
    render_summary()
    st.divider()
    
    # Charts
    render_charts()
    st.divider()
    
    # History
    render_history()


if __name__ == "__main__":
    main()