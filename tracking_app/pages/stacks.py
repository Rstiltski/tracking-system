"""
Habit Stacks Page - Habit Stacking UI

Streamlit page for creating and managing habit stacks using BJ Fogg's Tiny Habits methodology.

Features:
- Create habit stacks with anchors
- Add habits to stacks
- Track stack completion
- View stack analytics

Usage:
    streamlit run tracking_app/pages/stacks.py
"""
import streamlit as st

from tracking_app.pages.stacks import (
    init_session_state,
    render_header,
    render_create_stack_form,
    render_stacks_list,
    render_tips,
)
from tracking_app.pages.stacks.components import render_sidebar
from tracking_app.pages.stacks.constants import PAGE_TITLE, PAGE_ICON, PAGE_LAYOUT


# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout=PAGE_LAYOUT,
    initial_sidebar_state="expanded"
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
    
    # Main content
    render_header()
    st.divider()
    
    # Tips
    render_tips()
    st.divider()
    
    # Create stack form
    render_create_stack_form()
    st.divider()
    
    # Stacks list
    render_stacks_list()


if __name__ == "__main__":
    main()