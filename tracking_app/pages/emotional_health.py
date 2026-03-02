"""
Emotional Health Page - RGB Neurotransmitter-Based Emotion Tracking

Streamlit page for tracking emotions using the RGB neurotransmitter model.
Allows users to log emotional states using sliders or presets, view history,
and see pattern analysis.

Usage:
    streamlit run tracking_app/pages/emotional_health.py

Integration:
    - Uses brain.models.emotional_state for data models
    - Saves to SQLite database (emotional_states table)
    - Can be accessed from main navigation
"""

import streamlit as st

from tracking_app.pages.emotional_health import (
    init_session_state,
    render_header,
    render_quick_log,
    render_advanced_log,
    render_current_state,
    render_history,
    render_analytics,
)
from tracking_app.pages.emotional_health.constants import (
    PAGE_TITLE,
    PAGE_ICON,
    LAYOUT,
    INITIAL_SIDEBAR_STATE,
)
from tracking_app.components.sidebar import render_sidebar


# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout=LAYOUT,
    initial_sidebar_state=INITIAL_SIDEBAR_STATE
)


# =============================================================================
# MAIN FUNCTION
# =============================================================================

def main():
    """Main page entry point."""
    # Initialize
    init_session_state()
    
    # Render sidebar
    render_sidebar()
    
    # Render main content
    render_header()
    
    st.divider()
    
    # Quick log section
    render_quick_log()
    
    # Advanced log section
    render_advanced_log()
    
    st.divider()
    
    # Show last logged
    render_current_state()
    
    st.divider()
    
    # Two-column layout for history and analytics
    col1, col2 = st.columns(2)
    
    with col1:
        render_history()
    
    with col2:
        render_analytics()


if __name__ == "__main__":
    main()