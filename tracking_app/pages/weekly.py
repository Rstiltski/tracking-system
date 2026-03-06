"""
Weekly Summary Page

Phase 7.4: Weekly summary view showing 7-day habit completion overview.
Provides insights into weekly performance and trends.

Features:
- 7-day completion chart
- Average scores
- Best/worst performing habits
- Week-over-week comparison
"""

import streamlit as st
from datetime import date, datetime, timedelta
from typing import List, Dict, Any, Optional

from brain.analysis.time_views import CalendarProcessor, WeekData


def render_page():
    """Render the weekly summary page."""
    st.title("📊 Weekly Summary")
    st.markdown("View your habit performance over the past week.")
    
    # Get storage from session state
    storage = st.session_state.get('storage', None)
    
    # Initialize calendar processor
    processor = CalendarProcessor(storage=storage)
    
    # Get week navigation
    col1, col2, col3 = st.columns([1, 2, 1])
    
    # Get current week start from session state
    if 'week_start_date' not in st.session_state:
        st.session_state.week_start_date = date.today() - timedelta(days=date.today().weekday())
    
    week_start = st.session_state.week_start_date
    week_end = week_start + timedelta(days=6)
    
    with col1:
        if st.button("◀ Previous Week", key="prev_week"):
            st.session_state.week_start_date = week_start - timedelta(days=7)
            st.rerun()
    
    with col2:
        st.markdown(f"### {week_start.strftime('%B %d')} - {week_end.strftime('%B %d, %Y')}")
    
    with col3:
        if st.button("Next Week ▶", key="next_week"):
            st.session_state.week_start_date = week_start + timedelta(days=7)
            st.rerun()
    
    # Quick navigation
    if st.button("This Week", key="this_week_btn"):
        st.session_state.week_start_date = date.today() - timedelta(days=date.today().weekday())
        st.rerun()
    
    # Get week data
    with st.spinner("Loading weekly data..."):
        week_data = processor.get_week_data(start_date=week_start)
    
    # Render weekly overview
    _render_weekly_overview(week_data)
    
    # Render daily breakdown
    _render_daily_breakdown(week_data)
    
    # Render habit performance
    _render_habit_performance(week_data, storage)
    
    # Render week comparison
    _render_week_comparison(processor, week_start)


def _render_weekly_overview(week_data: WeekData) -> None:
    """Render the weekly overview metrics."""
    st.markdown("---")
    st.markdown("### 📈 Weekly Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Habits",
            week_data.total_habits
        )
    
    with col2:
        st.metric(
            "Completed",
            week_data.completed_habits
        )
    
    with col3:
        rate = week_data.completion_rate
        st.metric(
            "Completion Rate",
            f"{rate:.0%}"
        )
    
    with col4:
        st.metric(
            "Avg Score",
            f"{week_data.average_score:.1f}"
        )
    
    # Best and worst day
    if week_data.best_day and week_data.worst_day:
        st.markdown("**Day Highlights:**")
        best = week_data.best_day
        worst = week_data.worst_day
        
        best_col, worst_col = st.columns(2)
        
        with best_col:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%); 
                        padding: 10px; border-radius: 8px; color: white;">
                <strong>🏆 Best Day</strong><br>
                {best.date.strftime('%A, %b %d')}<br>
                {best.completion_rate:.0%} completion
            </div>
            """, unsafe_allow_html=True)
        
        with worst_col:
            st.markdown(f"""
            <div style="background: linear-gradient(135deg, #ef4444 0%, #dc2626 100%); 
                        padding: 10px; border-radius: 8px; color: white;">
                <strong>📉 Needs Work</strong><br>
                {worst.date.strftime('%A, %b %d')}<br>
                {worst.completion_rate:.0%} completion
            </div>
            """, unsafe_allow_html=True)


def _render_daily_breakdown(week_data: WeekData) -> None:
    """Render the daily breakdown chart."""
    st.markdown("---")
    st.markdown("### 📊 Daily Breakdown")
    
    # Create bar chart data
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    completion_rates = []
    
    for i, day_data in enumerate(week_data.days):
        completion_rates.append(day_data.completion_rate * 100)
    
    # Display using Streamlit bar chart
    chart_data = {
        "Day": days,
        "Completion %": completion_rates
    }
    
    st.bar_chart(chart_data, x="Day", y="Completion %")
    
    # Day details table
    st.markdown("**Day Details:**")
    
    day_data_rows = []
    for day in week_data.days:
        day_data_rows.append({
            "Day": day.date.strftime('%a %b %d'),
            "Habits": f"{day.completed_habits}/{day.total_habits}",
            "Rate": f"{day.completion_rate:.0%}",
            "Score": f"{day.score:.1f}" if day.score > 0 else "N/A",
            "Status": _get_status_emoji(day.completion_rate)
        })
    
    st.table(day_data_rows)


def _get_status_emoji(rate: float) -> str:
    """Get status emoji for completion rate."""
    if rate >= 1.0:
        return "✅ Perfect"
    elif rate >= 0.75:
        return "👍 Great"
    elif rate >= 0.5:
        return "👍 Good"
    elif rate > 0:
        return "⚠️ Low"
    else:
        return "❌ Missed"


def _render_habit_performance(week_data: WeekData, storage: Optional[Any]) -> None:
    """Render habit performance breakdown."""
    st.markdown("---")
    st.markdown("### 🎯 Habit Performance")
    
    # Collect all habits from the week
    habit_stats: Dict[str, Dict[str, Any]] = {}
    
    for day in week_data.days:
        for habit in day.habits:
            habit_name = habit.get('name', 'Unknown')
            if habit_name not in habit_stats:
                habit_stats[habit_name] = {
                    'total': 0,
                    'completed': 0,
                    'scores': []
                }
            
            habit_stats[habit_name]['total'] += 1
            if habit.get('completed', False):
                habit_stats[habit_name]['completed'] += 1
            if habit.get('score'):
                habit_stats[habit_name]['scores'].append(habit['score'])
    
    if not habit_stats:
        st.info("No habit data available for this week.")
        return
    
    # Create performance table
    performance_rows = []
    for habit_name, stats in habit_stats.items():
        rate = stats['completed'] / stats['total'] if stats['total'] > 0 else 0
        avg_score = sum(stats['scores']) / len(stats['scores']) if stats['scores'] else 0
        
        performance_rows.append({
            "Habit": habit_name,
            "Completed": f"{stats['completed']}/{stats['total']}",
            "Rate": f"{rate:.0%}",
            "Avg Score": f"{avg_score:.1f}" if avg_score > 0 else "N/A",
            "Status": _get_status_emoji(rate)
        })
    
    # Sort by completion rate
    performance_rows.sort(key=lambda x: int(x['Completed'].split('/')[0]), reverse=True)
    
    st.table(performance_rows)


def _render_week_comparison(processor: CalendarProcessor, current_week_start: date) -> None:
    """Render week-over-week comparison."""
    st.markdown("---")
    st.markdown("### 📈 Week Comparison")
    
    current_week_end = current_week_start + timedelta(days=6)
    previous_week_start = current_week_start - timedelta(days=7)
    previous_week_end = previous_week_start + timedelta(days=6)
    
    # Get comparison data
    comparison = processor.get_comparison_data(
        period1_start=current_week_start,
        period1_end=current_week_end,
        period2_start=previous_week_start,
        period2_end=previous_week_end
    )
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        rate_change = comparison.get('completion_rate_change', 0)
        delta_str = f"+{rate_change:.1%}" if rate_change > 0 else f"{rate_change:.1%}"
        st.metric(
            "Completion Rate Change",
            f"{comparison['period1']['completion_rate']:.0%}",
            delta=delta_str
        )
    
    with col2:
        habits_change = comparison.get('total_habits_change', 0)
        delta_str = f"+{habits_change}" if habits_change > 0 else str(habits_change)
        st.metric(
            "Total Habits Change",
            comparison['period1']['total_habits'],
            delta=delta_str
        )
    
    with col3:
        completed_change = comparison.get('completed_habits_change', 0)
        delta_str = f"+{completed_change}" if completed_change > 0 else str(completed_change)
        st.metric(
            "Completed Habits Change",
            comparison['period1']['completed_habits'],
            delta=delta_str
        )
    
    # Show comparison summary
    if rate_change > 0:
        st.success(f"🎉 You improved by {rate_change:.1%} compared to last week!")
    elif rate_change < 0:
        st.info(f"Keep going! Last week was {-rate_change:.1%} better. You can do it!")
    else:
        st.info("You're at the same level as last week. Push for improvement!")


def render_mini_weekly(storage: Optional[Any] = None) -> None:
    """
    Render a mini weekly summary for dashboard use.
    
    Args:
        storage: Storage backend
    """
    processor = CalendarProcessor(storage=storage)
    week_data = processor.get_week_data()
    
    # Create mini summary
    st.markdown(f"**This Week:** {week_data.completion_rate:.0%}")
    
    # Mini progress bar
    progress = week_data.completion_rate
    st.progress(progress)
    
    # Quick stats
    st.caption(f"{week_data.completed_habits}/{week_data.total_habits} habits completed")


# Page configuration
PAGE_CONFIG = {
    "title": "Weekly Summary",
    "icon": "📊",
    "description": "View weekly habit performance",
    "sidebar_order": 5,
}


if __name__ == "__main__":
    render_page()