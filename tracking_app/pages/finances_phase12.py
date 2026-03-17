"""
Finances Page - Financial Tracking (Phase 12 Design System)

Streamlit page for tracking income, expenses, and budget monitoring.

This version uses the Phase 12 Design System for consistent, accessible, and
responsive UI components.

Features (Phase 12):
- ✅ Phase 12 design system components (cards, buttons, alerts)
- ✅ Responsive layout that works on mobile, tablet, and desktop
- ✅ Accessibility features (focus indicators, skip links, ARIA labels)
- ✅ Better visual hierarchy with design tokens
- ✅ Loading states and empty states
- ✅ Improved color contrast (WCAG 2.1 AA compliant)

Usage:
    streamlit run tracking_app/app.py
    # Navigate to Finances from sidebar
"""

import streamlit as st
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import Phase 12 Design System
from tracking_app.design.theme import apply_design_system, get_current_theme
from tracking_app.design.components import (
    render_page_header,
    render_section_header,
    render_card,
    render_button,
    render_button_group,
    render_alert,
    render_success_alert,
    render_warning_alert,
    render_info_alert,
    render_empty_state,
    render_loading_state,
    render_progress_card,
)
from tracking_app.design.utils import (
    get_responsive_columns,
    render_responsive_container,
    render_focus_styles,
    render_skip_link,
    is_mobile,
    render_spacer,
    render_divider,
)

# Import existing functionality
from tracking_app.components.sidebar import render_sidebar

# Import finances page components
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

# Apply Phase 12 Design System theme
apply_design_system(theme=get_current_theme())

# Render accessibility features
render_focus_styles()
render_skip_link("main-content")


# =============================================================================
# MAIN FUNCTION
# =============================================================================

def main():
    """Main page entry point."""
    # Initialize session state
    init_session_state()
    
    # Render sidebar
    render_sidebar()
    
    # Render Phase 12 header
    render_finances_header_phase12()
    render_divider()
    
    # Summary
    render_summary()
    render_divider()
    
    # Add transaction form
    render_add_transaction_form()
    render_divider()
    
    # Filters
    render_filters()
    render_divider()
    
    # Category breakdown
    render_category_breakdown()
    render_divider()
    
    # Transactions list
    render_transactions_list()


def render_finances_header_phase12():
    """Render enhanced finances header with Phase 12 design system."""
    from tracking_app.storage import get_storage
    
    storage = get_storage()
    
    # Get user stats for header
    level = st.session_state.get('user_level', 1)
    xp = st.session_state.get('user_xp', 0)
    
    # Get finances stats
    transactions = storage.get_transactions()
    
    # Calculate totals
    income = sum(t.amount for t in transactions if t.type == 'income')
    expenses = sum(t.amount for t in transactions if t.type == 'expense')
    balance = income - expenses
    
    # Render page header
    render_page_header(
        title="Finances",
        subtitle=f"Level {level} Virtuoso • Balance: ${balance:,.2f}",
        icon="💰",
        actions=[
            {"label": "🔄 Refresh", "key": "refresh_finances"},
        ],
        show_divider=False,
    )
    
    # Show summary cards
    cols = get_responsive_columns(4, mobile_stack=True)
    
    with cols[0]:
        render_card(
            title="Total Income",
            content=f"${income:,.2f}",
            icon="📈",
            variant="stat"
        )
    
    with cols[1]:
        render_card(
            title="Total Expenses",
            content=f"${expenses:,.2f}",
            icon="📉",
            variant="stat"
        )
    
    with cols[2]:
        render_card(
            title="Balance",
            content=f"${balance:,.2f}",
            icon="💵",
            variant="stat"
        )
    
    with cols[3]:
        # Budget usage calculation (assuming $2000 default budget)
        budget = 2000
        budget_used = (expenses / budget * 100) if budget > 0 else 0
        render_progress_card(
            title="Budget Used",
            current=budget_used,
            max_value=100,
            icon="📊",
            show_percentage=True
        )
    
    # Show warning if over budget
    if expenses > budget:
        render_warning_alert(
            message=f"You've exceeded your budget by ${expenses - budget:,.2f}!",
            icon="⚠️"
        )


if __name__ == "__main__":
    main()
