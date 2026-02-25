"""
Veryfyn Tracking System - Main Streamlit Application

Main entry point for the Streamlit-based tracking application.
Redirects to the comprehensive dashboard page.

Usage:
    streamlit run tracking_app/app.py
"""

import streamlit as st
from datetime import datetime
import os
import sys

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Import shared components
from tracking_app.components.sidebar import render_sidebar
from tracking_app.components.session import init_session_state


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
        
        Version: 2.0.0
        """
    }
)


# ============================================================================
# Main Entry Point
# ============================================================================

def main():
    """Main application entry point - redirects to dashboard page."""
    # Initialize session state
    init_session_state()
    
    # Render sidebar
    render_sidebar()
    
    # Redirect to the comprehensive dashboard page
    st.switch_page("pages/dashboard.py")


if __name__ == "__main__":
    main()
