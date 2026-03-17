"""
Health Page - Health Metrics Tracking (Phase 12 Design System)

Streamlit page for tracking weight, sleep, mood, and other health metrics.

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
    # Navigate to Health from sidebar
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

# Import health page components
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
    render_health_header_phase12()
    render_divider()
    
    # Quick log
    render_quick_log()
    render_divider()
    
    # Summary
    render_summary()
    render_divider()
    
    # Charts
    render_charts()
    render_divider()
    
    # History
    render_history()


def render_health_header_phase12():
    """Render enhanced health header with Phase 12 design system."""
    from tracking_app.storage import get_storage
    
    storage = get_storage()
    
    # Get user stats for header
    level = st.session_state.get('user_level', 1)
    xp = st.session_state.get('user_xp', 0)
    
    # Get health entries
    health_entries = storage.get_health_entries()
    
    # Calculate averages
    if health_entries:
        avg_sleep = sum(e.sleep_hours for e in health_entries) / len(health_entries)
        avg_mood = sum(e.mood_score for e in health_entries) / len(health_entries)
        avg_energy = sum(e.energy_level for e in health_entries) / len(health_entries)
    else:
        avg_sleep = avg_mood = avg_energy = 0
    
    # Get latest weight if available
    latest_weight = None
    if health_entries:
        sorted_entries = sorted(health_entries, key=lambda x: x.date, reverse=True)
        latest_weight = sorted_entries[0].weight
    
    # Render page header
    render_page_header(
        title="Health",
        subtitle=f"Level {level} Virtuoso • {len(health_entries)} entries",
        icon="❤️",
        actions=[
            {"label": "🔄 Refresh", "key": "refresh_health"},
        ],
        show_divider=False,
    )
    
    # Show summary cards
    cols = get_responsive_columns(4, mobile_stack=True)
    
    with cols[0]:
        sleep_quality = "Great" if avg_sleep >= 7 else "Good" if avg_sleep >= 6 else "Needs Work"
        render_card(
            title="Avg Sleep",
            content=f"{avg_sleep:.1f}h",
            icon="😴",
            variant="stat"
        )
    
    with cols[1]:
        render_card(
            title="Avg Mood",
            content=f"{avg_mood:.1f}/10",
            icon="😊",
            variant="stat"
        )
    
    with cols[2]:
        render_card(
            title="Avg Energy",
            content=f"{avg_energy:.1f}/10",
            icon="⚡",
            variant="stat"
        )
    
    with cols[3]:
        if latest_weight:
            render_card(
                title="Current Weight",
                content=f"{latest_weight} lbs",
                icon="⚖️",
                variant="stat"
            )
        else:
            render_card(
                title="Weight",
                content="Not set",
                icon="⚖️",
                variant="stat"
            )
    
    # Show motivational message based on metrics
    if avg_sleep >= 7 and avg_mood >= 7:
        render_success_alert(
            message="You're doing great! Keep up the healthy habits! 💪",
            icon="🌟"
        )
    elif avg_sleep < 6:
        render_warning_alert(
            message="You're not getting enough sleep. Aim for 7-9 hours per night!",
            icon="😴"
        )


if __name__ == "__main__":
    main()
