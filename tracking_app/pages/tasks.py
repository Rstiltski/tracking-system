"""
Tasks Page - Task/Todo Management

Streamlit page for creating, managing, and completing tasks with priorities
and categories.

Usage:
    streamlit run tracking_app/pages/tasks.py
"""

import streamlit as st
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tracking_app.components.sidebar import render_sidebar
from tracking_app.pages.tasks.session_state import init_session_state
from tracking_app.pages.tasks.components import (
    render_header,
    render_add_task_form,
    render_filters,
    render_tasks_list,
    render_edit_form,
)


# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="Tasks - Veryfyn",
    page_icon="📋",
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
    
    # Add task form
    render_add_task_form()
    st.divider()
    
    # Filters
    render_filters()
    st.divider()
    
    # Edit form if needed
    render_edit_form()
    
    # Tasks list
    render_tasks_list()


if __name__ == "__main__":
    main()