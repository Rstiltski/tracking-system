"""
Calendar Page - Monthly Calendar View

Phase 10: Calendar view showing habit completions on a monthly grid.
Visualize your activity patterns and navigate through your tracking history.
"""

import streamlit as st
from datetime import date, timedelta
from typing import Dict, Any

from tracking_app.storage import get_storage
from tracking_app.components.heatmap import render_heatmap

from .constants import (
    PAGE_TITLE,
    PAGE_ICON,
    LAYOUT,
    INITIAL_SIDEBAR_STATE,
    get_month_name,
    get_completion_color,
    WEEKDAY_LABELS,
    COMPLETION_COLORS,
    HEATMAP_MONTHS,
)
from .session_state import (
    init_session_state,
    get_view_date,
    set_view_date,
    get_selected_date,
    set_selected_date,
    clear_selected_date,
)
from .helpers import (
    get_month_calendar_dates,
    get_month_completion_data,
    get_day_detail_data,
    navigate_month,
    format_date_display,
)


def render_page():
    """Render the calendar page."""
    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon=PAGE_ICON,
        layout=LAYOUT,
        initial_sidebar_state=INITIAL_SIDEBAR_STATE,
    )
    
    # Initialize session state
    init_session_state()
    
    # Get storage
    storage = get_storage()
    
    # Page header
    st.title("📅 Calendar")
    st.markdown("View your habit completions on a monthly calendar.")
    
    # Get current view date
    view_date = get_view_date()
    today = date.today()
    
    # Navigation controls
    col_prev, col_title, col_next, col_today = st.columns([1, 3, 1, 1])
    
    with col_prev:
        if st.button("◀ Previous", key="prev_month"):
            set_view_date(navigate_month(view_date, -1))
            st.rerun()
    
    with col_title:
        month_name = get_month_name(view_date.month)
        st.markdown(f"### {month_name} {view_date.year}")
    
    with col_next:
        if st.button("Next ▶", key="next_month"):
            set_view_date(navigate_month(view_date, 1))
            st.rerun()
    
    with col_today:
        if st.button("Today", key="go_today"):
            set_view_date(today)
            clear_selected_date()
            st.rerun()
    
    st.markdown("---")
    
    # Get habits
    habits = storage.get_habits()
    active_habits = [h for h in habits if not getattr(h, 'archived', False)]
    habit_ids = [h.id for h in active_habits]
    
    if not habit_ids:
        st.info("No habits to display. Create some habits first!")
        return
    
    # Get calendar dates
    first_day, last_day, calendar_dates = get_month_calendar_dates(view_date)
    
    # Get completion data
    with st.spinner("Loading calendar data..."):
        completion_data = get_month_completion_data(storage, habit_ids, calendar_dates)
    
    # Render calendar grid
    _render_calendar_grid(calendar_dates, completion_data, view_date)
    
    st.markdown("---")
    
    # Render heatmap
    _render_year_heatmap(storage, habit_ids, today)
    
    # Render day detail if selected
    selected_date = get_selected_date()
    if selected_date:
        _render_day_detail(storage, selected_date, habit_ids)


def _render_calendar_grid(
    dates: list[date],
    completion_data: Dict[date, Dict[str, Any]],
    view_date: date
) -> None:
    """Render the monthly calendar grid."""
    today = date.today()
    
    # Render weekday headers
    cols = st.columns(7)
    for i, weekday in enumerate(WEEKDAY_LABELS):
        with cols[i]:
            st.markdown(f"**{weekday}**", help=WEEKDAY_LABELS[i])
    
    st.markdown("")
    
    # Render calendar days in rows of 7
    for week_start in range(0, 42, 7):
        cols = st.columns(7)
        week_dates = dates[week_start:week_start + 7]
        
        for i, d in enumerate(week_dates):
            with cols[i]:
                _render_calendar_day(d, completion_data.get(d, {}), today)


def _render_calendar_day(
    d: date,
    data: Dict[str, Any],
    today: date
) -> None:
    """Render a single calendar day."""
    # Determine background color
    if data.get("is_future"):
        bg_color = COMPLETION_COLORS["future"]
    elif data.get("is_today"):
        bg_color = COMPLETION_COLORS["today"]
    else:
        bg_color = get_completion_color(data.get("rate", 0))
    
    # Calculate text color (dark for light backgrounds)
    is_light_bg = d > today or data.get("is_today")
    text_color = "#1f2937" if is_light_bg else "#ffffff"
    
    # Style for the day cell
    padding = "8px"
    border_radius = "6px"
    margin = "2px"
    
    st.markdown(
        f"""
        <div style="
            background-color: {bg_color};
            color: {text_color};
            padding: {padding};
            border-radius: {border_radius};
            margin: {margin};
            text-align: center;
            cursor: pointer;
            font-weight: {'bold' if d == today else 'normal'};
        ">
            <div style="font-size: 14px;">{d.day}</div>
            {f'<div style="font-size: 10px;">{data.get("completed", 0)}/{data.get("total", 0)}</div>' if not data.get("is_future") and data.get("total", 0) > 0 else ''}
        </div>
        """,
        unsafe_allow_html=True,
    )
    
    # Make the day clickable
    if st.button(
        f"📅{d.isoformat()}",
        key=f"day_{d.isoformat()}",
        help=f"View details for {format_date_display(d)}" if d <= today else None,
    ):
        if d <= today:
            set_selected_date(d)
            st.rerun()


def _render_year_heatmap(storage: Any, habit_ids: list[str], today: date) -> None:
    """Render a year-long heatmap of completions."""
    st.markdown("### 🔥 Activity Heatmap")
    
    # Generate dates for last 12 months
    heatmap_dates = []
    for i in range(HEATMAP_MONTHS * 30):
        d = today - timedelta(days=i)
        heatmap_dates.append(d)
    heatmap_dates.reverse()
    
    # Get heatmap data
    heatmap_data = get_month_completion_data(storage, habit_ids, heatmap_dates)
    
    # Format for heatmap component
    formatted_data = []
    for d in heatmap_dates:
        data = heatmap_data.get(d, {})
        formatted_data.append({
            "date": d.isoformat(),
            "value": data.get("rate", 0) * 100,
            "count": data.get("completed", 0),
        })
    
    # Render using existing heatmap component
    render_heatmap(
        data=formatted_data,
        title="Last 12 Months",
        show_streak=True,
    )


def _render_day_detail(
    storage: Any,
    selected_date: date,
    habit_ids: list[str]
) -> None:
    """Render detailed view for a selected day."""
    st.markdown("---")
    
    col_detail, col_close = st.columns([6, 1])
    
    with col_detail:
        st.markdown(f"### 📋 Details for {format_date_display(selected_date)}")
    
    with col_close:
        if st.button("✕ Close", key="close_detail"):
            clear_selected_date()
            st.rerun()
    
    # Get day data
    detail_data = get_day_detail_data(storage, selected_date, habit_ids)
    
    # Show habits
    if detail_data["habits"]:
        st.markdown("**Completed Habits:**")
        for habit in detail_data["habits"]:
            icon = "✅" if habit["completed"] else "❌"
            st.markdown(f"{icon} {habit['icon']} {habit['name']}")
    else:
        st.info("No habit data for this day.")
