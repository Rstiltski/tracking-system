"""
Tasks Page - Task/Todo Management (Phase 12 Design System)

Streamlit page for creating, managing, and completing tasks with priorities
and categories.

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
    # Navigate to Tasks from sidebar
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

# Import tasks page components
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
    render_tasks_header_phase12()
    render_divider()
    
    # Main content
    render_add_task_form()
    render_divider()
    
    # Filters
    render_filters()
    render_divider()
    
    # Edit form if needed
    render_edit_form()
    
    # Tasks list
    render_tasks_list()


def render_tasks_header_phase12():
    """Render enhanced tasks header with Phase 12 design system."""
    from tracking_app.storage import get_storage
    
    storage = get_storage()
    
    # Get user stats for header
    level = st.session_state.get('user_level', 1)
    xp = st.session_state.get('user_xp', 0)
    
    # Get tasks stats
    tasks = storage.get_tasks()
    active_tasks = [t for t in tasks if not t.completed]
    completed_tasks = [t for t in tasks if t.get('completed', False)]
    overdue_tasks = [t for t in active_tasks if t.due_date and t.due_date < str(st.session_state.get('current_date', ''))]
    
    # Render page header
    render_page_header(
        title="Tasks",
        subtitle=f"Level {level} Virtuoso • {len(active_tasks)} active • {len(completed_tasks)} completed",
        icon="📋",
        actions=[
            {"label": "🔄 Refresh", "key": "refresh_tasks"},
        ],
        show_divider=False,
    )
    
    # Show summary cards
    cols = get_responsive_columns(4, mobile_stack=True)
    
    with cols[0]:
        render_card(
            title="Total Tasks",
            content=f"{len(tasks)}",
            icon="📋",
            variant="stat"
        )
    
    with cols[1]:
        render_card(
            title="Active",
            content=f"{len(active_tasks)}",
            icon="⏳",
            variant="stat"
        )
    
    with cols[2]:
        render_card(
            title="Completed",
            content=f"{len(completed_tasks)}",
            icon="✅",
            variant="stat"
        )
    
    with cols[3]:
        overdue_count = len(overdue_tasks)
        render_card(
            title="Overdue",
            content=f"{overdue_count}",
            icon="⚠️",
            variant="stat"
        )
        
    # Show warning if there are overdue tasks
    if overdue_count > 0:
        render_warning_alert(
            message=f"You have {overdue_count} overdue task(s). Consider prioritizing them!",
            icon="⚠️"
        )


if __name__ == "__main__":
    main()
