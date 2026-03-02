"""
Finances Page - Financial Tracking

Streamlit page for tracking income, expenses, and budget monitoring.

Usage:
    streamlit run tracking_app/pages/finances.py
"""

import streamlit as st
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tracking_app.components.sidebar import render_sidebar
from tracking_app.pages.finances.session_state import init_session_state
from tracking_app.pages.finances.components import (
    render_header,
    render_summary,
    render_add_transaction_form,
    render_filters,
    render_category_breakdown,
    render_transactions_list,
)


# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="Finances - Veryfyn",
    page_icon="💰",
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
    render_summary()
    st.divider()
    
    # Add transaction form
    render_add_transaction_form()
    st.divider()
    
    # Filters
    render_filters()
    st.divider()
    
    # Category breakdown
    render_category_breakdown()
    st.divider()
    
    # Transactions list
    render_transactions_list()


if __name__ == "__main__":
    main()