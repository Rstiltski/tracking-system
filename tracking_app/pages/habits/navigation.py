"""
Navigation component for the Habits page.

Renders navigation controls including period navigation, view toggle,
and countdown timer.
"""

import streamlit as st
from datetime import date, timedelta
import calendar

from .helpers import (
    get_week_start,
    get_month_start,
    get_time_until_midnight,
    get_local_date,
    is_entry_completed,
)


def render_navigation_controls(current_date: date, view_mode: str):
    """
    Render navigation controls for the habit tracker.
    
    Includes:
    - Previous/Next period buttons
    - Today button
    - Week/Month view toggle
    - Current period display
    - Countdown timer to midnight reset
    
    Args:
        current_date: Current date for navigation
        view_mode: 'week' or 'month'
    """
    st.markdown("""
    <style>
    .nav-container {
        display: flex;
        align-items: center;
        justify-content: space-between;
        padding: 12px 16px;
        background: linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%);
        border-radius: 12px;
        margin-bottom: 16px;
        border: 1px solid #e2e8f0;
    }
    .nav-title {
        font-size: 1.25rem;
        font-weight: 700;
        color: #1e293b;
        min-width: 200px;
        text-align: center;
    }
    .nav-controls {
        display: flex;
        align-items: center;
        gap: 8px;
    }
    .view-toggle {
        display: flex;
        background: white;
        border-radius: 8px;
        padding: 2px;
        border: 1px solid #e2e8f0;
    }
    .stats-pill {
        font-size: 0.85rem;
        background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
        color: #4f46e5;
        padding: 6px 16px;
        border-radius: 20px;
        font-weight: 600;
    }
    .countdown-timer {
        font-size: 0.8rem;
        background: linear-gradient(135deg, #fef3c7 0%, #fde68a 100%);
        color: #92400e;
        padding: 6px 12px;
        border-radius: 20px;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 6px;
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Calculate period title
    if view_mode == 'week':
        week_start = get_week_start(current_date)
        week_end = week_start + timedelta(days=6)
        if week_start.month == week_end.month:
            period_title = f"{week_start.strftime('%B %Y')}"
        else:
            period_title = f"{week_start.strftime('%b %d')} - {week_end.strftime('%b %d, %Y')}"
        days_in_period = 7
    else:
        period_title = current_date.strftime('%B %Y')
        days_in_period = calendar.monthrange(current_date.year, current_date.month)[1]
    
    # Stats summary
    storage = st.session_state.storage
    habits = storage.get_habits()
    active_habits = [h for h in habits if not h.archived]
    today = get_local_date()
    
    completed_today = 0
    for habit in active_habits:
        entry = storage.get_habit_entry(habit.id, today)
        if is_entry_completed(entry):
            completed_today += 1
    
    stats_text = f"{completed_today}/{len(active_habits)} Completed Today"
    
    # Get time until midnight for countdown
    time_left = get_time_until_midnight()
    
    # Render controls using a clean 2-row layout to prevent overlapping/vertical text
    
    # ROW 1: Quick info and Views
    info_col, view_col1, view_col2, view_col3 = st.columns([4, 1, 1, 1])
    
    with info_col:
        st.markdown(f'<div style="display:flex;gap:16px;">'
                    f'<span class="stats-pill">📊 {stats_text}</span>'
                    f'<span class="countdown-timer" title="Time until daily reset">🔄 {time_left["hours"]:02d}h {time_left["minutes"]:02d}m</span>'
                    f'</div>', unsafe_allow_html=True)
    
    with view_col1:
        if st.button("📍 Today", key="nav_today", use_container_width=True):
            st.session_state.habit_current_date = get_local_date()
            st.rerun()
            
    with view_col2:
        if st.button("Week", key="view_week", use_container_width=True, type="primary" if view_mode == 'week' else "secondary"):
            st.session_state.habit_view_mode = 'week'
            st.rerun()
            
    with view_col3:
        if st.button("Month", key="view_month", use_container_width=True, type="primary" if view_mode == 'month' else "secondary"):
            st.session_state.habit_view_mode = 'month'
            st.rerun()

    st.write("") # Spacer

    # ROW 2: Date Navigation
    nav_col1, nav_col2, nav_col3 = st.columns([1, 4, 1])
    
    with nav_col1:
        if st.button("← Previous", key="nav_prev", use_container_width=True):
            if view_mode == 'week':
                st.session_state.habit_current_date = current_date - timedelta(days=7)
            else:
                new_date = current_date.replace(day=1) - timedelta(days=1)
                st.session_state.habit_current_date = new_date.replace(day=1)
            st.rerun()
            
    with nav_col2:
        st.markdown(f'<div class="nav-title">📅 {period_title}</div>', unsafe_allow_html=True)
        
    with nav_col3:
        if st.button("Next →", key="nav_next", use_container_width=True):
            if view_mode == 'week':
                st.session_state.habit_current_date = current_date + timedelta(days=7)
            else:
                if current_date.month == 12:
                    new_date = current_date.replace(year=current_date.year + 1, month=1, day=1)
                else:
                    new_date = current_date.replace(month=current_date.month + 1, day=1)
                st.session_state.habit_current_date = new_date
            st.rerun()