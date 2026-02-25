"""
Charts Components - Data Visualizations

Provides reusable chart components for displaying data.

Usage:
    from tracking_app.components.charts import (
        render_weekly_chart,
        render_score_trend_chart
    )
"""
import streamlit as st
import pandas as pd
from datetime import date, timedelta
from typing import Dict, List, Optional


def render_weekly_chart(
    data: Optional[Dict[str, List]] = None,
    title: str = "📈 Weekly Progress"
):
    """
    Render a weekly progress bar chart.
    
    Args:
        data: Dict with 'dates', 'completed', 'total' lists
        title: Chart title
    """
    st.subheader(title)
    
    if data is None or not data.get('dates'):
        st.info("No data available for the past week.")
        return
    
    df = pd.DataFrame({
        'Day': data['dates'],
        'Completed': data['completed'],
        'Total': data['total']
    })
    
    st.bar_chart(df.set_index('Day')[['Completed', 'Total']])


def render_score_trend_chart(
    scores: Dict[date, float],
    title: str = "📊 Score Trend"
):
    """
    Render a line chart showing score trend over time.
    
    Args:
        scores: Dict mapping dates to score values (0.0-1.0)
        title: Chart title
    """
    st.subheader(title)
    
    if not scores:
        st.info("No score data available yet.")
        return
    
    # Convert to DataFrame
    df = pd.DataFrame([
        {'Date': d.isoformat(), 'Score': round(s * 100, 1)}
        for d, s in sorted(scores.items())
    ])
    
    if df.empty:
        st.info("No score data available yet.")
        return
    
    st.line_chart(df.set_index('Date')['Score'])


def render_habit_completion_heatmap(
    completion_data: Dict[str, List[bool]],
    days: int = 30
):
    """
    Render a habit completion heatmap.
    
    Args:
        completion_data: Dict mapping habit names to list of completion booleans
        days: Number of days to display
    """
    st.subheader("🗓️ Habit Completion Heatmap")
    
    if not completion_data:
        st.info("No habit data available.")
        return
    
    # Create DataFrame
    today = date.today()
    dates = [(today - timedelta(days=i)).strftime('%m/%d') for i in range(days-1, -1, -1)]
    
    df_data = {}
    for habit_name, completions in completion_data.items():
        # Pad or trim to match days
        if len(completions) < days:
            completions = [False] * (days - len(completions)) + completions
        else:
            completions = completions[-days:]
        df_data[habit_name] = [1 if c else 0 for c in completions]
    
    df = pd.DataFrame(df_data, index=dates)
    
    # Display as dataframe with color styling
    st.dataframe(
        df,
        use_container_width=True,
        column_config={
            "all": st.column_config.ProgressColumn(
                "Progress",
                format="%.0f%%",
                min_value=0,
                max_value=1,
            )
        }
    )


def render_category_breakdown(
    categories: Dict[str, int],
    title: str = "📊 Category Breakdown"
):
    """
    Render a pie chart showing category breakdown.
    
    Args:
        categories: Dict mapping category names to counts
        title: Chart title
    """
    st.subheader(title)
    
    if not categories:
        st.info("No category data available.")
        return
    
    df = pd.DataFrame({
        'Category': list(categories.keys()),
        'Count': list(categories.values())
    })
    
    # Streamlit doesn't have native pie charts, use bar chart
    st.bar_chart(df.set_index('Category')['Count'])


def render_progress_over_time(
    data: Dict[str, List],
    metric_name: str = "Progress"
):
    """
    Render a multi-line chart showing progress over time.
    
    Args:
        data: Dict with 'dates' and metric name keys
        metric_name: Name of the metric being tracked
    """
    if not data or 'dates' not in data:
        st.info(f"No {metric_name.lower()} data available.")
        return
    
    df = pd.DataFrame(data)
    
    if 'dates' in df.columns:
        df = df.set_index('dates')
    
    st.line_chart(df)


__all__ = [
    "render_weekly_chart",
    "render_score_trend_chart",
    "render_habit_completion_heatmap",
    "render_category_breakdown",
    "render_progress_over_time",
]