"""
Calendar View Page

Simple monthly calendar view with habit completion visualization.
"""

import streamlit as st
from datetime import date, datetime, timedelta
from typing import List, Dict, Any

from tracking_app.storage import get_storage

def _is_habit_completed(storage, habit_id, date_val):
    if isinstance(date_val, str):
        try:
            date_val = datetime.strptime(date_val, '%Y-%m-%d').date()
        except Exception:
            pass
    entry = storage.get_habit_entry(habit_id, date_val)
    if not entry:
        return False
    if isinstance(entry, dict):
        return entry.get('completed', False)
    return getattr(entry, 'completed', False)


def render_page():
    """Render the calendar view page."""
    st.title("📅 Calendar View")
    st.markdown("View your habit completion history in a calendar format.")
    
    # Get storage correctly
    storage = get_storage()
    
    # Get current view date from session state
    if 'calendar_view_date' not in st.session_state:
        st.session_state.calendar_view_date = date.today()
    
    view_date = st.session_state.calendar_view_date
    
    # Navigation controls
    col1, col2, col3 = st.columns([1, 3, 1])
    
    with col1:
        prev_month = view_date.replace(day=1) - timedelta(days=1)
        if st.button(f"◀ {prev_month.strftime('%b')}", key="prev_month"):
            st.session_state.calendar_view_date = prev_month.replace(day=1)
            st.rerun()
    
    with col2:
        st.markdown(f"### {view_date.strftime('%B %Y')}")
    
    with col3:
        next_month = (view_date.replace(day=28) + timedelta(days=4)).replace(day=1)
        if st.button(f"{next_month.strftime('%b')} ▶", key="next_month"):
            st.session_state.calendar_view_date = next_month
            st.rerun()
    
    # Quick navigation
    st.markdown("---")
    nav_col1, nav_col2 = st.columns([1, 2])
    
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
            index=0,
            key="month_selector"
        )
        
        if selected_month != view_date.replace(day=1):
            st.session_state.calendar_view_date = selected_month
            st.rerun()
    
    # Get monthly data directly from storage
    with st.spinner("Loading calendar data..."):
        monthly_data = _get_monthly_data(storage, view_date.year, view_date.month)
    
    # Render month summary
    _render_month_summary(monthly_data)
    
    # Render the calendar grid
    st.markdown("---")
    _render_calendar_grid(monthly_data, view_date.year, view_date.month)
    
    # Render day detail if selected
    _render_day_detail_view(storage)
    
    # Render streak information
    _render_streak_info(storage)


def _get_monthly_data(storage, year: int, month: int) -> Dict[str, Any]:
    """Get monthly data from storage."""
    # Get habits
    habits = storage.get_habits()
    
    # Get the first and last day of the month
    first_day = date(year, month, 1)
    if month == 12:
        last_day = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        last_day = date(year, month + 1, 1) - timedelta(days=1)
    
    # Build daily data
    daily_data = {}
    days_tracked = 0
    total_completion = 0
    
    current = first_day
    while current <= last_day:
        date_str = current.strftime('%Y-%m-%d')
        
        # Count completed habits for this day
        completed = 0
        total = len(habits)
        
        for habit in habits:
            if _is_habit_completed(storage, habit.id, date_str):
                completed += 1
        
        completion_rate = completed / total if total > 0 else 0
        
        daily_data[date_str] = {
            'date': current,
            'completed': completed,
            'total': total,
            'completion_rate': completion_rate,
            'has_data': total > 0
        }
        
        if total > 0:
            days_tracked += 1
            total_completion += completion_rate
        
        current += timedelta(days=1)
    
    # Calculate monthly stats
    overall_completion_rate = total_completion / days_tracked if days_tracked > 0 else 0
    overall_average_score = (total_completion / days_tracked * 100) if days_tracked > 0 else 0
    
    # Calculate streak
    current_streak = _calculate_current_streak(storage, habits, first_day)
    best_streak = _calculate_best_streak(storage, habits)
    
    return {
        'year': year,
        'month': month,
        'first_day': first_day,
        'last_day': last_day,
        'num_days': (last_day - first_day).days + 1,
        'days_tracked': days_tracked,
        'overall_completion_rate': overall_completion_rate,
        'overall_average_score': overall_average_score,
        'current_streak': current_streak,
        'best_streak': best_streak,
        'daily_data': daily_data,
        'total_habits': len(habits)
    }


def _calculate_current_streak(storage, habits, reference_date: date) -> int:
    """Calculate current streak."""
    if not habits:
        return 0
    
    streak = 0
    current = reference_date
    
    # Check up to 365 days back
    for _ in range(365):
        date_str = current.strftime('%Y-%m-%d')
        all_completed = True
        
        for habit in habits:
            if not _is_habit_completed(storage, habit.id, date_str):
                all_completed = False
                break
        
        if all_completed:
            streak += 1
            current -= timedelta(days=1)
        else:
            break
    
    return streak


def _calculate_best_streak(storage, habits) -> int:
    """Calculate best streak."""
    if not habits:
        return 0
    
    # Get all completion dates
    completion_dates = set()
    
    for habit in habits:
        entries = storage.get_habit_entries(habit.id) if hasattr(storage, 'get_habit_entries') else []
        for entry in entries:
            if hasattr(entry, 'date'):
                completion_dates.add(entry.date)
    
    if not completion_dates:
        return 0
    
    # Sort dates
    sorted_dates = sorted(completion_dates)
    
    # Calculate best streak
    best_streak = 0
    current_streak = 1
    
    for i in range(1, len(sorted_dates)):
        if (sorted_dates[i] - sorted_dates[i-1]).days == 1:
            current_streak += 1
            best_streak = max(best_streak, current_streak)
        else:
            current_streak = 1
    
    return max(best_streak, current_streak)


def _render_month_summary(monthly_data: dict) -> None:
    """Render monthly summary statistics."""
    st.markdown("### 📊 Monthly Summary")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        rate = monthly_data['overall_completion_rate']
        st.metric(
            "Completion Rate",
            f"{rate:.0%}"
        )
    
    with col2:
        st.metric(
            "Average Score",
            f"{monthly_data['overall_average_score']:.1f}"
        )
    
    with col3:
        st.metric(
            "Days Tracked",
            f"{monthly_data['days_tracked']}/{monthly_data['num_days']}"
        )
    
    with col4:
        st.metric(
            "Total Habits",
            f"{monthly_data['total_habits']}"
        )


def _render_calendar_grid(monthly_data: dict, year: int, month: int) -> None:
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
    first_day = monthly_data['first_day']
    daily_data = monthly_data['daily_data']
    
    # Get the first day of the week (0 = Monday, 6 = Sunday)
    start_weekday = first_day.weekday()  # 0 = Monday
    
    # Create calendar weeks
    current_day = first_day - timedelta(days=start_weekday)
    
    for week in range(6):  # Max 6 weeks in a month
        html_parts.append('<div style="display: flex; gap: 2px; align-items: center;">')
        html_parts.append('<div style="width: 30px;"></div>')  # Spacer
        
        for day in range(7):
            if current_day.month == month and current_day <= today:
                # Get data for this day
                date_str = current_day.strftime('%Y-%m-%d')
                day_data = daily_data.get(date_str, {})
                
                rate = day_data.get('completion_rate', 0)
                has_data = day_data.get('has_data', False)
                completed = day_data.get('completed', 0)
                total = day_data.get('total', 0)
                
                # Calculate level based on completion rate
                if not has_data:
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
                is_today = current_day == today
                border = "2px solid #0969da" if is_today else "none"
                
                html_parts.append(f'''
                <div style="
                    width: 40px;
                    height: 50px;
                    background-color: {color};
                    opacity: {1.0 if current_day.month == month else 0.4};
                    border-radius: 4px;
                    border: {border};
                    display: flex;
                    flex-direction: column;
                    align-items: center;
                    justify-content: center;
                    font-size: 12px;
                    color: #24292f;
                    cursor: pointer;
                " title="{date_str}: {completed}/{total} completed">
                    <div style="font-weight: 600;">{current_day.day}</div>
                    <div style="font-size: 9px; color: #57606a;">{completed}/{total}</div>
                </div>
                ''')
            else:
                # Empty or future cell
                html_parts.append(f'''
                <div style="
                    width: 40px;
                    height: 50px;
                    background-color: #ebedf0;
                    opacity: 0.4;
                    border-radius: 4px;
                    border: none;
                ">
                </div>
                ''')
            
            current_day += timedelta(days=1)
        
        html_parts.append('</div>')
        
        # Stop after we've covered the month
        if current_day.month != month and current_day > today:
            break
    
    html_parts.append('</div>')
    
    # Legend
    html_parts.append('<div style="display: flex; gap: 12px; margin-top: 12px; font-size: 11px; color: #57606a;">')
    html_parts.append('<span>Less</span>')
    for level in range(5):
        html_parts.append(f'<div style="width: 12px; height: 12px; background-color: {colors[level-1]}; border-radius: 2px;"></div>')
    html_parts.append('<span>More</span>')
    html_parts.append('</div>')
    
    st.markdown(''.join(html_parts), unsafe_allow_html=True)


def _render_day_detail_view(storage) -> None:
    """Render day detail view."""
    st.markdown("### 📋 Day Detail")
    
    # Date selector
    today = date.today()
    selected_date = st.date_input(
        "Select a date to view details",
        value=today,
        max_value=today
    )
    
    date_str = selected_date.strftime('%Y-%m-%d')
    
    # Get habits
    habits = storage.get_habits()
    
    # Count completed
    completed = 0
    for habit in habits:
        if _is_habit_completed(storage, habit.id, date_str):
            completed += 1
    
    total = len(habits)
    completion_rate = completed / total if total > 0 else 0
    
    # Display metrics
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Date", selected_date.strftime('%Y/%m/%d'))
    
    with col2:
        st.metric("Completion", f"{completion_rate:.0%}")
    
    with col3:
        st.metric("Habits", f"{completed}/{total}")
    
    # Show habits list
    if habits:
        st.markdown("#### Habits")
        for habit in habits:
            is_completed = _is_habit_completed(storage, habit.id, date_str)
            icon = "✅" if is_completed else "⬜"
            st.markdown(f"{icon} {habit.name}")
    else:
        st.info("No habits found. Create some habits to see them here!")


def _render_streak_info(storage) -> None:
    """Render streak information."""
    st.markdown("### 🔥 Streaks")
    
    # Get habits
    habits = storage.get_habits()
    
    # Calculate current streak
    current_streak = _calculate_current_streak(storage, habits, date.today())
    
    # Calculate best streak
    best_streak = _calculate_best_streak(storage, habits)
    
    # Calculate total tracked days
    total_tracked = 0
    for habit in habits:
        entries = storage.get_habit_entries(habit.id) if hasattr(storage, 'get_habit_entries') else []
        if entries:
            total_tracked = len(entries)
            break
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Current Streak", f"{current_streak} days")
    
    with col2:
        st.metric("Best Streak", f"{best_streak} days")
    
    with col3:
        st.metric("Total Tracked", f"{total_tracked} days")

if __name__ == "__main__":
    render_page()
