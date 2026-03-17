"""
Goals Page - Goal Tracking (Phase 12 Design System)

Streamlit page for setting, tracking, and achieving personal goals.

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
    # Navigate to Goals from sidebar
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

# Import goals page components
from tracking_app.pages.goals.session_state import init_session_state
from tracking_app.pages.goals.components import (
    render_header,
    render_add_goal_form,
    render_goals_summary,
    render_goals_list,
    render_edit_form,
)


# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="Goals - Veryfyn",
    page_icon="🎯",
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
    render_goals_header_phase12()
    render_divider()
    
    # Summary
    render_goals_summary()
    render_divider()
    
    # Add goal form
    render_add_goal_form()
    render_divider()
    
    # Edit form if needed
    render_edit_form()
    
    # Goals list
    render_goals_list()


def render_goals_header_phase12():
    """Render enhanced goals header with Phase 12 design system."""
    from tracking_app.storage import get_storage
    
    storage = get_storage()
    
    # Get user stats for header
    level = st.session_state.get('user_level', 1)
    xp = st.session_state.get('user_xp', 0)
    
    # Get goals stats
    goals = storage.get_goals()
    active_goals = [g for g in goals if not g.completed]
    completed_goals = [g for g in goals if g.completed]
    
    # Calculate overall progress
    if goals:
        total_progress = sum(g.progress for g in goals) / len(goals)
    else:
        total_progress = 0
    
    # Render page header
    render_page_header(
        title="Goals",
        subtitle=f"Level {level} Virtuoso • {len(active_goals)} active • {total_progress:.0f}% overall progress",
        icon="🎯",
        actions=[
            {"label": "🔄 Refresh", "key": "refresh_goals"},
        ],
        show_divider=False,
    )
    
    # Show summary cards
    cols = get_responsive_columns(4, mobile_stack=True)
    
    with cols[0]:
        render_card(
            title="Total Goals",
            content=f"{len(goals)}",
            icon="🎯",
            variant="stat"
        )
    
    with cols[1]:
        render_card(
            title="Active",
            content=f"{len(active_goals)}",
            icon="⏳",
            variant="stat"
        )
    
    with cols[2]:
        render_card(
            title="Completed",
            content=f"{len(completed_goals)}",
            icon="✅",
            variant="stat"
        )
    
    with cols[3]:
        render_progress_card(
            title="Overall Progress",
            current=total_progress,
            max_value=100,
            icon="📊",
            show_percentage=True
        )
    
    # Show motivational message based on progress
    if total_progress >= 80:
        render_success_alert(
            message="You're almost there! Keep pushing to achieve your goals! 💪",
            icon="🚀"
        )
    elif total_progress >= 50:
        render_info_alert(
            message="Great progress! You're halfway to achieving your goals! 🎉",
            icon="💡"
        )


if __name__ == "__main__":
    main()
