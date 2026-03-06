"""
Calendar View Page

Phase 7.4: Monthly calendar view with habit completion visualization.
Shows a GitHub-style contribution heatmap for habit tracking.

Features:
- Monthly calendar grid with completion status
- Color-coded days by completion rate
- Navigation between months
- Day detail view
- Streak visualization
"""

import streamlit as st
from datetime import date, datetime, timedelta
from typing import List, Dict, Any, Optional

from brain.analysis.time_views import TimeViewsProcessor
from tracking_app.components.heatmap import render_heatmap, render_mini_heatmap


def render_page():
    """Render the calendar view page."""
    st.title("📅 Calendar View")
    st.markdown("View your habit completion history in a calendar format.")
    
    # Get storage from session state
    storage = st.session_state.get('storage', None)
    
    # Initialize processor
    processor = TimeViewsProcessor(storage=storage)
    
    # Get current view date from session state
    if 'calendar_view_date' not in st.session_state:
        st.session_state.calendar_view_date = date.today()
    
    view_date = st.session_state.calendar_view_date
    
    # Navigation controls
    col1, col2, col3 = st.columns([1, 3, 1])
    
    nav = processor.get_prev_next_month(view_date.year, view_date.month)
    
    with col1:
        if st.button(f"◀ {nav['prev_label']}", key="prev_month"):
            st.session_state.calendar_view_date = date(nav['prev_year'], nav['prev_month'], 1)
            st.rerun()
    
    with col2:
        st.markdown(f"### {view_date.strftime('%B %Y')}")
    
    with col3:
        if st.button(f"{nav['next_label']} ▶", key="next_month"):
            st.session_state.calendar_view_date = date(nav['next_year'], nav['next_month'], 1)
            st.rerun()
    
    # Quick navigation
    st.markdown("---")
    nav_col1, nav_col2, nav_col3 = st.columns([1, 2, 1])
    
    with nav_col1:
        if st.button("Today", key="today_btn"):
            st.session_state.calendar_view_date = date.today()
            st.rerun()
    
    with nav_col2:
        # Month selector
        month_options = []
        today = date.today()
        for i in range(12):
            m = today.month - i
            y = today.year
            if m < 1:
                m += 12
                y -= 1
            month_options.append(date(y, m, 1))
        
        selected_month = st.selectbox(
            "Jump to month",
            options=month_options,
            format_func=lambda x: x.strftime('%B %Y'),
            index=month_options.index(view_date.replace(day=1)) if view_date.replace(day=1) in month_options else 0,
            key="month_selector"
        )
        
        if selected_month != view_date.replace(day=1):
            st.session_state.calendar_view_date = selected_month
            st.rerun()
    
    # Get monthly view data
    with st.spinner("Loading calendar data..."):
        monthly_view = processor.get_monthly_view(view_date.year, view_date.month)
    
    # Render month summary
    _render_month_summary(monthly_view)
    
    # Render the calendar grid
    st.markdown("---")
    _render_calendar_grid(monthly_view)
    
    # Render day detail if selected
    _render_day_detail_view(processor)
    
    # Render streak information
    _render_streak_info(processor)


def _render_month_summary(monthly_view: dict) -> None:
    """Render monthly summary statistics."""
    st.markdown("### 📊 Monthly Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        rate = monthly_view['overall_completion_rate']
        st.metric(
            "Completion Rate",
            f"{rate:.0%}"
        )
    
    with col2:
        st.metric(
            "Average Score",
            f"{monthly_view['overall_average_score']:.1f}"
        )
    
    with col3:
        st.metric(
            "Days Tracked",
            f"{monthly_view['total_days_tracked']}/{monthly_view['num_days']}"
        )
    
    with col4:
        trend = monthly_view.get('trend', {}).get('direction', 'N/A')
        trend_icon = "📈" if trend == "improving" else ("📉" if trend == "declining" else "➡️")
        st.metric(
            "Trend",
            f"{trend_icon} {trend.replace('_', ' ').title()}"
        )


def _render_calendar_grid(monthly_view: dict) -> None:
    """Render the calendar as an HTML grid."""
    st.markdown("### 📅 Calendar Grid")
    
    # Day labels
    day_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    
    # Color scheme
    colors = {
        -1: "#ebedf0",  # no data
        0: "#ebedf0",   # none
        1: "#9be9a8",   # low
        2: "#40c463",   # medium
        3: "#30a14e",   # high
        4: "#216e39",   # full
    }
    
    # Build HTML for calendar
    html_parts = ['<div style="display: flex; flex-direction: column; gap: 2px; font-family: -apple-system, BlinkMacSystemFont, sans-serif;">']
    
    # Header row with day names
    html_parts.append('<div style="display: flex; gap: 2px;">')
    html_parts.append('<div style="width: 30px;"></div>')  # Spacer
    for label in day_labels:
        html_parts.append(f'<div style="width: 40px; text-align: center; font-size: 11px; color: #57606a; font-weight: 600;">{label}</div>')
    html_parts.append('</div>')
    
    # Calendar rows
    today = date.today()
    for week_row in monthly_view['calendar_grid']:
        html_parts.append('<div style="display: flex; gap: 2px; align-items: center;">')
        html_parts.append('<div style="width: 30px;"></div>')  # Spacer
        
        for cell in week_row:
            if cell is None:
                # Empty cell (before first day or after last day)
                html_parts.append('<div style="width: 40px; height: 50px;"></div>')
            else:
                # Calculate level based on completion rate
                rate = cell['completion_rate']
                if not cell['has_data']:
                    level = -1
                elif rate == 0:
                    level = 0
                elif rate < 0.25:
                    level = 1
                elif rate < 0.5:
                    level = 2
                elif rate < 0.75:
                    level = 3
                else:
                    level = 4
                
                color = colors.get(level, colors[-1])
                
                # Today marker
                is_today = cell['date'] == today
                border = "2px solid #0969da" if is_today else "none"
                
                # Future marker
                opacity = 0.4 if cell['is_future'] else 1.0
                
                # Tooltip
                tooltip = f"{cell['date_str']}: {cell['completed_count']}/{cell['total_count']} completed"
                
                # Day number and score
                day_num = cell['date'].day
                score_text = f"{cell['average_score']:.0f}" if cell['has_data'] and cell['average_score'] > 0 else ""
                
                html_parts.append(f'''
                    <div style="
                        width: 40px;
                        height: 50px;
                        background-color: {color};
                        opacity: {opacity};
                        border-radius: 4px;
                        border: {border};
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                        justify-content: center;
                        font-size: 12px;
                        color: #24292f;
                        cursor: pointer;
                    " title="{tooltip}">
                        <div style="font-weight: 600;">{day_num}</div>
                        <div style="font-size: 9px; color: #57606a;">{score_text}</div>
                    </div>
                ''')
        
        html_parts.append('</div>')
    
    html_parts.append('</div>')
    
    # Legend
    html_parts.append('<div style="display: flex; gap: 12px; margin-top: 12px; font-size: 11px; color: #57606a;">')
    html_parts.append('<span>Less</span>')
    for level in range(0, 5):
        color = colors[level]
        html_parts.append(f'<div style="width: 12px; height: 12px; background-color: {color}; border-radius: 2px;"></div>')
    html_parts.append('<span>More</span>')
    html_parts.append('</div>')
    
    st.markdown(''.join(html_parts), unsafe_allow_html=True)


def _render_day_detail_view(processor: TimeViewsProcessor) -> None:
    """Render the day detail view."""
    st.markdown("---")
    st.markdown("### 📋 Day Detail")
    
    # Date selector
    selected_date = st.date_input(
        "Select a date to view details",
        value=date.today(),
        max_value=date.today(),
        key="calendar_day_select"
    )
    
    # Get day detail
    day = processor.get_day_detail(selected_date)
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Completion",
            f"{day['completion_rate']:.0%}"
        )
    
    with col2:
        st.metric(
            "Habits",
            f"{day['completed_habits']}/{day['total_habits']}"
        )
    
    with col3:
        st.metric(
            "Tasks",
            f"{day['completed_tasks']}/{day['total_tasks']}"
        )
    
    with col4:
        st.metric(
            "Avg Score",
            f"{day['average_score']:.1f}"
        )
    
    # Show habit breakdown if available
    if day['habits']:
        st.markdown("**Habit Breakdown:**")
        for habit_name, habit_info in day['habits'].items():
            completed = habit_info.get('completed', False)
            score = habit_info.get('score', 0)
            status = "✅" if completed else "❌"
            score_text = f" (score: {score})" if completed else ""
            st.markdown(f"{status} **{habit_name}**{score_text}")
    else:
        st.info(f"No habit data available for {selected_date.strftime('%B %d, %Y')}")


def _render_streak_info(processor: TimeViewsProcessor) -> None:
    """Render streak information."""
    st.markdown("---")
    st.markdown("### 🔥 Streaks")
    
    streaks = processor.get_streaks()
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric(
            "Current Streak",
            f"{streaks['current_streak']} days",
            delta=f"Best: {streaks['longest_streak']} days"
        )
    
    with col2:
        st.metric(
            "Total Tracked",
            f"{streaks['total_tracked_days']} days"
        )


def render_mini_calendar(
    storage: Optional[Any] = None,
    days: int = 30
) -> None:
    """
    Render a mini calendar for dashboard use.
    
    Args:
        storage: Storage backend
        days: Number of days to show
    """
    processor = TimeViewsProcessor(storage=storage)
    
    # Get heatmap data
    heatmap_data = processor.get_heatmap_data(days=days)
    
    # Convert to expected format
    formatted_data = []
    for day in heatmap_data:
        formatted_data.append({
            'date': day['date'],
            'total_habits': day['total_habits'],
            'completed_habits': day['completed_habits'],
            'completion_rate': day['completion_rate'],
            'is_today': day['is_today'],
            'is_future': day['is_future'],
        })
    
    render_mini_heatmap(formatted_data, days=days)


# Page configuration
PAGE_CONFIG = {
    "title": "Calendar",
    "icon": "📅",
    "description": "View habit completion history",
    "sidebar_order": 4,
}


if __name__ == "__main__":
    render_page()