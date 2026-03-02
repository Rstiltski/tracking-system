"""
Insights Page - Intelligence Dashboard

Streamlit page for displaying AI-powered insights about habits, health, and behavior.

Features:
- Burnout Risk Assessment with recommendations
- Habit Correlations (sleep ↔ mood, exercise ↔ energy)
- PCS Fragility Scores (habit predictability)
- Personalized recommendations

Usage:
    streamlit run tracking_app/pages/insights.py
"""

import streamlit as st
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tracking_app.components.sidebar import render_sidebar
from tracking_app.pages.insights.session_state import init_session_state
from tracking_app.pages.insights.components import (
    render_header,
    render_burnout_section,
    render_correlations_section,
    render_pcs_section,
    render_insights_summary,
)


# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="Insights - Veryfyn",
    page_icon="🧠",
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
    
    storage = st.session_state.storage
    
    # Render sections
    render_insights_summary(storage)
    st.divider()
    
    # Tabs for different insights
    tab1, tab2, tab3 = st.tabs(["Burnout Risk", "Correlations", "Habit Fragility"])
    
    with tab1:
        render_burnout_section(storage)
    
    with tab2:
        render_correlations_section(storage)
    
    with tab3:
        render_pcs_section(storage)


if __name__ == "__main__":
    main()