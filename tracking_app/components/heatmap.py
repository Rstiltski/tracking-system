"""
Heatmap Component

Phase 7.4: Provides completion heatmap visualization for habit tracking.
Similar to GitHub contribution graph style.

Features:
- Color-coded completion rates
- Interactive hover tooltips
- Configurable date range
- Streak highlighting
"""

import streamlit as st
from datetime import date, datetime, timedelta
from typing import List, Dict, Any, Optional


def render_heatmap(
    data: List[Dict[str, Any]],
    title: str = "Completion Heatmap",
    color_scale: Optional[Dict[str, str]] = None,
    show_streak: bool = True,
) -> None:
    """
    Render a completion heatmap.
    
    Args:
        data: List of day data dictionaries
        title: Title for the heatmap
        color_scale: Optional color scale mapping
        show_streak: Whether to show streak information
    """
    st.subheader(title)
    
    # Default color scale
    if color_scale is None:
        color_scale = {
            "complete": "#22c55e",      # Green
            "partial": "#eab308",       # Yellow
            "low": "#f97316",           # Orange
            "missed": "#ef4444",        # Red
            "no_habits": "#e5e7eb",     # Gray
            "future": "#f3f4f6",        # Light gray
        }
    
    # Render heatmap grid
    _render_heatmap_grid(data, color_scale)
    
    # Show legend
    _render_heatmap_legend(color_scale)
    
    # Show streak info if enabled
    if show_streak:
        streak = _calculate_streak(data)
        st.metric("Current Streak", f"{streak} days")


def _render_heatmap_grid(
    data: List[Dict[str, Any]],
    color_scale: Dict[str, str]
) -> None:
    """
    Render the heatmap as a grid.
    
    Args:
        data: List of day data
        color_scale: Color mapping
    """
    if not data:
        st.info("No data available for heatmap")
        return
    
    # Group data by weeks
    weeks = _group_by_weeks(data)
    
    # Day labels
    day_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    
    # Build HTML for heatmap
    html_parts = [
        '<div style="display: flex; flex-direction: column; gap: 2px;">',
    ]
    
    # Day labels column
    html_parts.append('<div style="display: flex; gap: 2px;">')
    html_parts.append('<div style="width: 30px;"></div>')  # Spacer for month labels
    
    # Week headers (show month for first week of each month)
    current_month = None
    for week in weeks:
        first_day = week[0] if week else None
        if first_day:
            month_name = first_day.get('date', date.today()).strftime('%b')
            if month_name != current_month:
                html_parts.append(f'<div style="width: 40px; font-size: 10px; text-align: center;">{month_name}</div>')
                current_month = month_name
            else:
                html_parts.append('<div style="width: 40px;"></div>')
    
    html_parts.append('</div>')
    
    # Render each row (day of week)
    for day_idx in range(7):
        html_parts.append('<div style="display: flex; gap: 2px; align-items: center;">')
        html_parts.append(f'<div style="width: 30px; font-size: 10px; color: #64748b;">{day_labels[day_idx]}</div>')
        
        for week in weeks:
            if day_idx < len(week):
                day = week[day_idx]
                
                # Check if this is an empty placeholder
                if not day or not day.get('date'):
                    html_parts.append('<div style="width: 40px; height: 40px;"></div>')
                    continue
                
                color = _get_color_for_day(day, color_scale)
                opacity = 0.3 if day.get('is_future', False) else 1.0
                
                # Tooltip text
                tooltip = _get_tooltip_text(day)
                
                # Get the day number safely
                day_date = day.get('date')
                if isinstance(day_date, str):
                    day_date = datetime.strptime(day_date, '%Y-%m-%d').date()
                day_num = day_date.day if day_date else ''
                
                html_parts.append(f'''
                    <div style="
                        width: 40px;
                        height: 40px;
                        background-color: {color};
                        opacity: {opacity};
                        border-radius: 4px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        font-size: 10px;
                        color: white;
                        cursor: pointer;
                        title: '{tooltip}';
                    " title="{tooltip}">
                        {day_num}
                    </div>
                ''')
            else:
                html_parts.append('<div style="width: 40px; height: 40px;"></div>')
        
        html_parts.append('</div>')
    
    html_parts.append('</div>')
    
    st.markdown(''.join(html_parts), unsafe_allow_html=True)


def _group_by_weeks(data: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
    """
    Group day data by weeks.
    
    Args:
        data: List of day data
    
    Returns:
        List of weeks, each containing 7 days (Mon-Sun)
    """
    if not data:
        return []
    
    # Filter and sort data by date
    valid_data = []
    for d in data:
        day_date = d.get('date')
        if day_date is not None:
            valid_data.append(d)
    
    if not valid_data:
        return []
    
    # Sort by date
    def get_sort_key(d):
        day_date = d.get('date')
        if isinstance(day_date, str):
            return datetime.strptime(day_date, '%Y-%m-%d').date()
        return day_date
    
    sorted_data = sorted(valid_data, key=get_sort_key)
    
    # Get first date and calculate padding needed
    first_date = sorted_data[0].get('date')
    if isinstance(first_date, str):
        first_date = datetime.strptime(first_date, '%Y-%m-%d').date()
    
    # 0=Monday, 6=Sunday
    first_weekday = first_date.weekday()
    
    # Build weeks
    weeks = []
    current_week = [{}] * first_weekday  # Pad first week to start on correct weekday
    
    for day in sorted_data:
        current_week.append(day)
        
        # If week is complete (7 items), save it and start a new one
        if len(current_week) == 7:
            weeks.append(current_week)
            current_week = []
    
    # Pad last week if needed
    if current_week:
        while len(current_week) < 7:
            current_week.append({})
        weeks.append(current_week)
    
    return weeks


def _get_color_for_day(day: Dict[str, Any], color_scale: Dict[str, str]) -> str:
    """
    Get color for a day based on completion status.
    
    Args:
        day: Day data dictionary
        color_scale: Color mapping
    
    Returns:
        Hex color string
    """
    if day.get('is_future', False):
        return color_scale.get('future', '#f3f4f6')
    
    if day.get('total_habits', 0) == 0:
        return color_scale.get('no_habits', '#e5e7eb')
    
    rate = day.get('completion_rate', 0)
    
    if rate >= 1.0:
        return color_scale.get('complete', '#22c55e')
    elif rate >= 0.5:
        return color_scale.get('partial', '#eab308')
    elif rate > 0:
        return color_scale.get('low', '#f97316')
    else:
        return color_scale.get('missed', '#ef4444')


def _get_tooltip_text(day: Dict[str, Any]) -> str:
    """
    Get tooltip text for a day.
    
    Args:
        day: Day data dictionary
    
    Returns:
        Tooltip string
    """
    day_date = day.get('date', date.today())
    if isinstance(day_date, str):
        day_date = datetime.strptime(day_date, '%Y-%m-%d').date()
    
    date_str = day_date.strftime('%B %d, %Y')
    
    if day.get('is_future', False):
        return f"{date_str}: Future"
    
    total = day.get('total_habits', 0)
    completed = day.get('completed_habits', 0)
    rate = day.get('completion_rate', 0)
    
    return f"{date_str}: {completed}/{total} habits ({rate:.0%})"


def _render_heatmap_legend(color_scale: Dict[str, str]) -> None:
    """
    Render the heatmap legend.
    
    Args:
        color_scale: Color mapping
    """
    legend_items = [
        ("Complete (100%)", color_scale.get('complete', '#22c55e')),
        ("Partial (50-99%)", color_scale.get('partial', '#eab308')),
        ("Low (1-49%)", color_scale.get('low', '#f97316')),
        ("Missed (0%)", color_scale.get('missed', '#ef4444')),
        ("No Habits", color_scale.get('no_habits', '#e5e7eb')),
    ]
    
    html_parts = ['<div style="display: flex; gap: 15px; margin-top: 10px;">']
    
    for label, color in legend_items:
        html_parts.append(f'''
            <div style="display: flex; align-items: center; gap: 5px;">
                <div style="
                    width: 15px;
                    height: 15px;
                    background-color: {color};
                    border-radius: 2px;
                "></div>
                <span style="font-size: 11px; color: #64748b;">{label}</span>
            </div>
        ''')
    
    html_parts.append('</div>')
    
    st.markdown(''.join(html_parts), unsafe_allow_html=True)


def _calculate_streak(data: List[Dict[str, Any]]) -> int:
    """
    Calculate the current streak.
    
    Args:
        data: List of day data
    
    Returns:
        Current streak in days
    """
    streak = 0
    today = date.today()
    
    # Sort data by date descending
    sorted_data = sorted(
        [d for d in data if d.get('date')],
        key=lambda x: x.get('date', date.today()),
        reverse=True
    )
    
    for day in sorted_data:
        if day.get('is_future', False):
            continue
        
        if day.get('completion_rate', 0) >= 1.0:
            streak += 1
        else:
            break
    
    return streak


def render_mini_heatmap(
    data: List[Dict[str, Any]],
    days: int = 30
) -> None:
    """
    Render a compact mini heatmap for dashboard use.
    
    Args:
        data: List of day data
        days: Number of days to show
    """
    if not data:
        return
    
    # Take only the last N days
    recent_data = data[-days:] if len(data) > days else data
    
    color_scale = {
        "complete": "#22c55e",
        "partial": "#eab308",
        "low": "#f97316",
        "missed": "#ef4444",
        "no_habits": "#e5e7eb",
        "future": "#f3f4f6",
    }
    
    # Build compact HTML
    html_parts = ['<div style="display: flex; gap: 2px; flex-wrap: wrap;">']
    
    for day in recent_data:
        color = _get_color_for_day(day, color_scale)
        tooltip = _get_tooltip_text(day)
        
        html_parts.append(f'''
            <div style="
                width: 12px;
                height: 12px;
                background-color: {color};
                border-radius: 2px;
                title: '{tooltip}';
            " title="{tooltip}"></div>
        ''')
    
    html_parts.append('</div>')
    
    st.markdown(''.join(html_parts), unsafe_allow_html=True)


__all__ = [
    "render_heatmap",
    "render_mini_heatmap",
]