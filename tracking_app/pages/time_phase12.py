"""
Time Page - Time Tracking (Phase 12 Design System)

Streamlit page for tracking time with a built-in timer and time categorization.

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
    # Navigate to Time from sidebar
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

# Import time page components
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
    render_time_header_phase12()
    render_divider()
    
    # Timer
    render_timer()
    render_divider()
    
    # Manual entry
    render_manual_entry()
    
    # Daily summary
    render_daily_summary()
    render_divider()
    
    # Weekly chart
    render_weekly_chart()
    render_divider()
    
    # Time entries
    render_time_entries()


def render_time_header_phase12():
    """Render enhanced time header with Phase 12 design system."""
    from datetime import datetime, timedelta
    
    # Get user stats for header
    level = st.session_state.get('user_level', 1)
    xp = st.session_state.get('user_xp', 0)
    
    # Get time entries for today
    today = datetime.now().strftime('%Y-%m-%d')
    time_entries = []
    total_hours = 0
    
    # Calculate this week's total
    week_start = (datetime.now() - timedelta(days=datetime.now().weekday())).strftime('%Y-%m-%d')
    week_entries = []
    week_hours = 0
    
    # Render page header
    render_page_header(
        title="Time Tracking",
        subtitle=f"Level {level} Virtuoso • {total_hours:.1f}h tracked today",
        icon="⏱️",
        actions=[
            {"label": "🔄 Refresh", "key": "refresh_time"},
        ],
        show_divider=False,
    )
    
    # Show summary cards
    cols = get_responsive_columns(4, mobile_stack=True)
    
    with cols[0]:
        render_card(
            title="Today",
            content=f"{total_hours:.1f}h",
            icon="📅",
            variant="stat"
        )
    
    with cols[1]:
        render_card(
            title="This Week",
            content=f"{week_hours:.1f}h",
            icon="📆",
            variant="stat"
        )
    
    with cols[2]:
        render_card(
            title="Entries Today",
            content=f"{len(time_entries)}",
            icon="📝",
            variant="stat"
        )
    
    with cols[3]:
        # Calculate productivity (assuming 8h target per day)
        target_hours = 8
        productivity = (total_hours / target_hours * 100) if target_hours > 0 else 0
        render_progress_card(
            title="Daily Target",
            current=min(productivity, 100),
            max_value=100,
            icon="🎯",
            show_percentage=True
        )
    
    # Show message if no time tracked
    if len(time_entries) == 0:
        render_info_alert(
            message="Start tracking your time! Use the timer or add manual.",
            icon=" entries⏱️"
        )


if __name__ == "__main__":
    main()
