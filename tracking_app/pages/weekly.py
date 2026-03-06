"""
Weekly Summary Page

Phase 7.4: Weekly summary view showing 7-day habit completion overview.
Provides insights into weekly performance and trends.

Features:
- 7-day completion chart
- Average scores
- Best/worst performing habits
- Week-over-week comparison
- Habit breakdown table
"""

import streamlit as st
from datetime import date, datetime, timedelta
from typing import List, Dict, Any, Optional

from brain.analysis.time_views import TimeViewsProcessor


def render_page():
    """Render the weekly summary page."""
    st.title("📊 Weekly Summary")
    st.markdown("View your habit performance over the past week.")
    
    # Get storage from session state
    storage = st.session_state.get('storage', None)
    
    # Initialize processor
    processor = TimeViewsProcessor(storage=storage)
    
    # Get week navigation
    col1, col2, col3 = st.columns([1, 2, 1])
    
    # Get current week start from session state
    if 'week_view_date' not in st.session_state:
        st.session_state.week_view_date = date.today()
    
    view_date = st.session_state.week_view_date
    
    # Get weekly summary
    with st.spinner("Loading weekly data..."):
        summary = processor.get_weekly_summary(target_date=view_date)
    
    # Get navigation helpers
    nav = processor.get_prev_next_week(view_date)
    
    with col1:
        if st.button("◀ Previous Week", key="prev_week"):
            st.session_state.week_view_date = nav['prev_week_start']
            st.rerun()
    
    with col2:
        st.markdown(f"### {summary['week_label']}")
    
    with col3:
        if st.button("Next Week ▶", key="next_week"):
            st.session_state.week_view_date = nav['next_week_start']
            st.rerun()
    
    # Quick navigation
    if st.button("This Week", key="this_week_btn"):
        st.session_state.week_view_date = date.today()
        st.rerun()
    
    # Render weekly overview
    _render_weekly_overview(summary)
    
    # Render daily breakdown
    _render_daily_breakdown(summary)
    
    # Render habit performance
    _render_habit_performance(summary)
    
    # Render week comparison
    _render_week_comparison(summary)


def _render_weekly_overview(summary: dict) -> None:
    """Render the weekly overview metrics."""
    st.markdown("---")
    st.markdown("### 📈 Weekly Overview")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        rate = summary['overall_completion_rate']
        st.metric(
            "Completion Rate",
            f"{rate:.0%}"
        )
    
    with col2:
        st.metric(
            "Average Score",
            f"{summary['overall_average_score']:.1f}"
        )
    
    with col3:
        st.metric(
            "Days with Data",
            f"{summary['days_with_data']}/7"
        )
    
    with col4:
        best = summary.get('best_habit', 'N/A')
        st.metric(
            "Best Habit",
            best if best else "N/A"
        )
    
    # Best and worst habit highlights
    if summary.get('best_habit') or summary.get('worst_habit'):
        st.markdown("**Habit Highlights:**")
        
        best_col, worst_col = st.columns(2)
        
        with best_col:
            best = summary.get('best_habit')
            if best and best in summary.get('habit_breakdown', {}):
                info = summary['habit_breakdown'][best]
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #22c55e 0%, #16a34a 100%); 
                            padding: 10px; border-radius: 8px; color: white;">
                    <strong>🏆 Best Performing</strong><br>
                    {best}<br>
                    {info['rate']:.0%} completion ({info['completed_days']}/{info['total_days']} days)
                </div>
                """, unsafe_allow_html=True)
        
        with worst_col:
            worst = summary.get('worst_habit')
            if worst and worst in summary.get('habit_breakdown', {}):
                info = summary['habit_breakdown'][worst]
                st.markdown(f"""
                <div style="background: linear-gradient(135deg, #f97316 0%, #ea580c 100%); 
                            padding: 10px; border-radius: 8px; color: white;">
                    <strong>📉 Needs Improvement</strong><br>
                    {worst}<br>
                    {info['rate']:.0%} completion ({info['completed_days']}/{info['total_days']} days)
                </div>
                """, unsafe_allow_html=True)


def _render_daily_breakdown(summary: dict) -> None:
    """Render the daily breakdown chart."""
    st.markdown("---")
    st.markdown("### 📊 Daily Breakdown")
    
    # Create bar chart data
    days = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]
    completion_rates = []
    
    for i, day_data in enumerate(summary['days']):
        rate = day_data['completion_rate'] * 100 if day_data['has_data'] else 0
        completion_rates.append(rate)
    
    # Display using Streamlit bar chart
    import pandas as pd
    
    chart_df = pd.DataFrame({
        "Day": days,
        "Completion %": completion_rates
    })
    
    st.bar_chart(chart_df.set_index("Day"))
    
    # Day details table
    st.markdown("**Day Details:**")
    
    day_data_rows = []
    for day in summary['days']:
        day_data_rows.append({
            "Day": day['date'].strftime('%a %b %d'),
            "Habits": f"{day['completed_habits']}/{day['total_habits']}",
            "Rate": f"{day['completion_rate']:.0%}",
            "Score": f"{day['average_score']:.1f}" if day['average_score'] > 0 else "N/A",
            "Status": _get_status_emoji(day['completion_rate'])
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


def _render_habit_performance(summary: dict) -> None:
    """Render habit performance breakdown."""
    st.markdown("---")
    st.markdown("### 🎯 Habit Performance")
    
    habit_breakdown = summary.get('habit_breakdown', {})
    
    if not habit_breakdown:
        st.info("No habit data available for this week.")
        return
    
    # Create performance table
    performance_rows = []
    for habit_name, stats in habit_breakdown.items():
        performance_rows.append({
            "Habit": habit_name,
            "Completed": f"{stats['completed_days']}/{stats['total_days']}",
            "Rate": f"{stats['rate']:.0%}",
            "Avg Score": f"{stats['avg_score']:.1f}" if stats['avg_score'] > 0 else "N/A",
            "Status": _get_status_emoji(stats['rate'])
        })
    
    # Sort by completion rate (extract numeric rate)
    performance_rows.sort(key=lambda x: float(x['Rate'].rstrip('%')) / 100, reverse=True)
    
    st.table(performance_rows)


def _render_week_comparison(summary: dict) -> None:
    """Render week-over-week comparison."""
    st.markdown("---")
    st.markdown("### 📈 Week Comparison")
    
    comparison = summary.get('comparison', {})
    
    if not comparison:
        st.info("No comparison data available.")
        return
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        rate_delta = comparison.get('completion_delta', 0)
        delta_str = f"+{rate_delta:.1%}" if rate_delta > 0 else f"{rate_delta:.1%}"
        st.metric(
            "Completion Rate",
            f"{comparison['curr_completion_rate']:.0%}",
            delta=delta_str
        )
    
    with col2:
        score_delta = comparison.get('score_delta', 0)
        delta_str = f"+{score_delta:.1f}" if score_delta > 0 else f"{score_delta:.1f}"
        st.metric(
            "Average Score",
            f"{comparison['curr_average_score']:.1f}",
            delta=delta_str
        )
    
    with col3:
        trend = comparison.get('completion_trend', 'flat')
        trend_icon = "📈" if trend == "up" else ("📉" if trend == "down" else "➡️")
        st.metric(
            "Trend",
            f"{trend_icon} {trend.title()}"
        )
    
    # Show comparison summary
    rate_delta = comparison.get('completion_delta', 0)
    if rate_delta > 0.01:
        st.success(f"🎉 You improved by {rate_delta:.1%} compared to last week!")
    elif rate_delta < -0.01:
        st.info(f"Keep going! Last week was {-rate_delta:.1%} better. You can do it!")
    else:
        st.info("You're at the same level as last week. Push for improvement!")


def render_mini_weekly(storage: Optional[Any] = None) -> None:
    """
    Render a mini weekly summary for dashboard use.
    
    Args:
        storage: Storage backend
    """
    processor = TimeViewsProcessor(storage=storage)
    summary = processor.get_weekly_summary()
    
    # Create mini summary
    st.markdown(f"**This Week:** {summary['overall_completion_rate']:.0%}")
    
    # Mini progress bar
    progress = summary['overall_completion_rate']
    st.progress(progress)
    
    # Quick stats
    st.caption(f"{summary['days_with_data']}/7 days tracked")


# Page configuration
PAGE_CONFIG = {
    "title": "Weekly Summary",
    "icon": "📊",
    "description": "View weekly habit performance",
    "sidebar_order": 5,
}


if __name__ == "__main__":
    render_page()