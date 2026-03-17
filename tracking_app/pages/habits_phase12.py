"""
Habits Page - Habit Tracking (Phase 12 Design System)

Streamlit page for creating, tracking, and managing daily habits with streaks
 using exponential smoothing algorithmand scientific habit scoring.

This version uses the Phase 12 Design System for consistent, accessible, and
responsive UI components.

Features (Phase 12):
- ✅ Phase 12 design system components (cards, buttons, alerts)
- ✅ Responsive layout that works on mobile, tablet, and desktop
- ✅ Accessibility features (focus indicators, skip links, ARIA labels)
- ✅ Better visual hierarchy with design tokens
- ✅ Loading states and empty states
- ✅ Improved color contrast (WCAG 2.1 AA compliant)
- ✅ Habit Score: 0-100% using exponential smoothing (forgiving, gradual decay)
- ✅ Score Categories: Excellent, Strong, Developing, Building, Starting
- ✅ Trend Indicators: Shows if habit is improving or declining
- ✅ Streak Tracking: Current and best streak counts
- ✅ Sorting & Filtering: Sort by name, score, streak; filter by status
- ✅ Accessibility: Text labels for colorblind users
- ✅ Streak Freeze: Visual indicators and easy-to-use freeze system
- ✅ Enhanced Table: Sticky columns, progress bars, weekend/today highlighting

Usage:
    streamlit run tracking_app/app.py
    # Navigate to Habits from sidebar
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
from tracking_app.storage import get_storage
from tracking_app.components.sidebar import render_sidebar
from tracking_app.components.session import init_session_state, add_xp

# Import all components from the habits package
from tracking_app.pages.habits import (
    # Session state
    init_session_state as init_habits_session_state,
    # Components
    render_habit_header,
    render_edit_habit_modal,
    render_habits_list,
)


# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="Habits - Veryfyn",
    page_icon="✅",
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
    init_habits_session_state()
    
    # Render sidebar with streak freeze section
    render_sidebar(show_streak_freeze=True)
    
    # Render Phase 12 page header with gamification elements
    render_habits_header_phase12()
    render_divider()
    
    # Render edit form modal if a habit is being edited
    render_edit_habit_modal()
    
    # Render main habits list (includes spreadsheet view with add habit button)
    render_habits_list()


def render_habits_header_phase12():
    """Render enhanced habits header with Phase 12 design system."""
    storage = get_storage()
    from datetime import datetime, timedelta
    
    # Get user stats for header
    level = st.session_state.get('user_level', 1)
    xp = st.session_state.get('user_xp', 0)
    streak = st.session_state.get('user_streak', 0)
    
    # Get habits stats
    habits = storage.get_habits()
    today = st.session_state.get('current_date', None)
    
    if today and habits:
        completed_today = sum(1 for h in habits if storage.is_habit_completed_on_date(h.id, today))
        total_habits = len(habits)
        completion_rate = (completed_today / total_habits * 100) if total_habits > 0 else 0
    else:
        completed_today = 0
        total_habits = len(habits) if habits else 0
        completion_rate = 0
    
    # Calculate time until midnight
    now = datetime.now()
    midnight = now.replace(hour=23, minute=59, second=59)
    time_left = midnight - now
    hours_left = time_left.seconds // 3600
    mins_left = (time_left.seconds % 3600) // 60
    
    # Calculate XP for today (assuming 10 XP per habit)
    xp_today = completed_today * 10
    
    # Render page header with quick actions
    render_page_header(
        title="Habits",
        subtitle=f"Level {level} Virtuoso • {streak} day streak • {completion_rate:.0f}% today",
        icon="✅",
        actions=[
            {"label": "🔄 Refresh", "key": "refresh_habits"},
            {"label": "➕ Add New", "key": "add_habit"},
        ],
        show_divider=False,
    )
    
    # Show summary cards with enhanced styling
    cols = get_responsive_columns(5, mobile_stack=True)
    
    with cols[0]:
        render_card(
            title="Total Habits",
            content=f"{total_habits}",
            icon="📊",
            variant="stat"
        )
    
    with cols[1]:
        render_card(
            title="Completed",
            content=f"{completed_today}/{total_habits}",
            icon="✅",
            variant="stat"
        )
    
    with cols[2]:
        render_card(
            title="Current Streak",
            content=f"{streak} days",
            icon="🔥",
            variant="stat"
        )
    
    with cols[3]:
        render_card(
            title="XP Today",
            content=f"+{xp_today}",
            icon="⭐",
            variant="stat"
        )
    
    with cols[4]:
        render_card(
            title="Time Left",
            content=f"{hours_left}h {mins_left}m",
            icon="⏰",
            variant="stat"
        )
    
    # Show progress bar section
    render_section_header(
        title="Today's Progress",
        icon="📈",
        show_divider=True
    )
    
    # Progress bar - handle edge cases
    if completion_rate <= 0:
        col_ratio = [0.01, 99.99]
    elif completion_rate >= 100:
        col_ratio = [99.99, 0.01]
    else:
        col_ratio = [completion_rate, 100 - completion_rate]
    
    cols = st.columns(col_ratio)
    with cols[0]:
        st.markdown(f"""
        <div style="
            background: linear-gradient(90deg, #6366f1 {completion_rate}%, #e5e7eb {completion_rate}%);
            height: 12px;
            border-radius: 6px;
            width: 100%;
        "></div>
        """, unsafe_allow_html=True)
    
    # Show quick habits preview
    if habits and len(habits) > 0:
        render_section_header(
            title="Quick View - Today's Habits",
            icon="👀",
            show_divider=True
        )
        
        # Display habits in a compact format with quick complete
        habit_cols = get_responsive_columns(3, mobile_stack=True)
        for idx, habit in enumerate(habits[:6]):  # Show first 6 habits
            is_completed = storage.is_habit_completed_on_date(habit.id, today) if today else False
            with habit_cols[idx % 3]:
                # Create clickable habit card
                st.markdown(f"""
                <div style="
                    background: var(--bg-tertiary);
                    border: 1px solid var(--border);
                    border-radius: var(--radius-md);
                    padding: 0.75rem;
                    margin-bottom: 0.5rem;
                    cursor: pointer;
                    transition: var(--transition-fast);
                ">
                    <div style="display: flex; align-items: center; gap: 0.5rem;">
                        <span style="font-size: 1.25rem;">{"✅" if is_completed else "⬜"}</span>
                        <span style="font-weight: 500; color: var(--text-primary);">{habit.name}</span>
                    </div>
                </div>
                """, unsafe_allow_html=True)
                
                # Quick complete button
                if not is_completed:
                    if st.button(f"Complete", key=f"quick_complete_{habit.id}", use_container_width=True):
                        storage.mark_habit_complete(habit.id, today)
                        add_xp(10)
                        st.toast(f"✅ {habit.name} completed! +10 XP", icon="⭐")
                        st.rerun()
                else:
                    st.caption("✓ Completed")
        
        if len(habits) > 6:
            st.caption(f"+ {len(habits) - 6} more habits...")
    
    # Show motivational or helpful messages
    if total_habits == 0:
        render_info_alert(
            title="Welcome to Habits!",
            message="Click 'Add New' to create your first habit and start building better routines!",
            icon="👋"
        )
    elif completion_rate == 100:
        render_success_alert(
            title="Amazing Work!",
            message="You've completed all your habits today! Keep up the great work!",
            icon="🌟"
        )
    elif completion_rate >= 80:
        render_info_alert(
            title="Almost There!",
            message=f"Just {total_habits - completed_today} more habit(s) to reach 100% today!",
            icon="💪"
        )
    elif completion_rate < 50:
        render_warning_alert(
            title="You've Got This!",
            message="Start with one habit and build from there. Every small step counts!",
            icon="🌱"
        )


if __name__ == "__main__":
    main()
