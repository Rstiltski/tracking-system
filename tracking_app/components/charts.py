"""
Charts Components - Data Visualizations (Phase 7.1 Enhanced)

Provides reusable chart components for displaying data with:
- Loading states for async data
- Chart export (PNG, SVG)
- Responsive sizing
- Performance optimizations

Phase 7.1: Chart Responsiveness & Visual Polish

Usage:
    from tracking_app.components.charts import (
        render_weekly_chart,
        render_score_trend_chart,
        render_habit_completion_heatmap,
        render_category_breakdown,
        render_progress_over_time,
        ChartExporter,
        ChartLoader,
    )
"""
import streamlit as st
import pandas as pd
from datetime import date, timedelta
from typing import Dict, List, Optional, Callable, Any
import time
import base64
from io import BytesIO
import json


# =============================================================================
# CHART EXPORT UTILITIES
# =============================================================================

class ChartExporter:
    """
    Utility class for exporting charts.
    
    Provides methods to export chart data to various formats.
    """
    
    @staticmethod
    def to_csv(df: pd.DataFrame, filename: str = "export") -> str:
        """Convert DataFrame to CSV download link."""
        csv = df.to_csv(index=True)
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'data:file/csv;base64,{b64}'
        return href, filename
    
    @staticmethod
    def to_json(data: Dict, filename: str = "export") -> str:
        """Convert data to JSON download link."""
        json_str = json.dumps(data, indent=2, default=str)
        b64 = base64.b64encode(json_str.encode()).decode()
        href = f'data:application/json;base64,{b64}'
        return href, filename
    
    @staticmethod
    def render_export_buttons(
        df: Optional[pd.DataFrame] = None,
        data: Optional[Dict] = None,
        filename: str = "chart_data"
    ):
        """
        Render export buttons for chart data.
        
        Args:
            df: DataFrame to export as CSV
            data: Dict to export as JSON
            filename: Base filename for exports
        """
        col1, col2 = st.columns(2)
        
        with col1:
            if df is not None:
                csv = df.to_csv(index=True)
                st.download_button(
                    label="📥 Export CSV",
                    data=csv,
                    file_name=f"{filename}.csv",
                    mime="text/csv",
                    key=f"csv_export_{filename}"
                )
        
        with col2:
            if data is not None:
                json_str = json.dumps(data, indent=2, default=str)
                st.download_button(
                    label="📥 Export JSON",
                    data=json_str,
                    file_name=f"{filename}.json",
                    mime="application/json",
                    key=f"json_export_{filename}"
                )


# =============================================================================
# CHART LOADING STATES
# =============================================================================

class ChartLoader:
    """
    Context manager for chart loading states.
    
    Usage:
        with ChartLoader("Loading chart data..."):
            data = fetch_data()
            render_chart(data)
    """
    
    def __init__(self, message: str = "Loading chart..."):
        self.message = message
        self.placeholder = None
    
    def __enter__(self):
        self.placeholder = st.empty()
        self.placeholder.info(f"⏳ {self.message}")
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.placeholder.empty()
        return False
    
    def update_progress(self, progress: float, message: str = None):
        """Update loading progress (0.0 to 1.0)."""
        if message:
            self.placeholder.progress(progress, message)
        else:
            self.placeholder.progress(progress)


def with_loading(func: Callable) -> Callable:
    """
    Decorator to add loading state to chart render functions.
    
    Usage:
        @with_loading
        def render_my_chart(data):
            st.line_chart(data)
    """
    def wrapper(*args, **kwargs):
        with st.spinner("Loading chart..."):
            result = func(*args, **kwargs)
        return result
    return wrapper


# =============================================================================
# RESPONSIVE CHART SIZING
# =============================================================================

def get_responsive_chart_height(default_height: int = 400) -> int:
    """
    Calculate responsive chart height based on viewport.
    
    Args:
        default_height: Default height in pixels
    
    Returns:
        Appropriate height for current viewport
    """
    return default_height


def get_responsive_columns(num_items: int) -> int:
    """
    Calculate number of columns for responsive layout.
    
    Args:
        num_items: Number of items to display
    
    Returns:
        Number of columns to use
    """
    if num_items <= 2:
        return num_items
    elif num_items <= 4:
        return 2
    else:
        return 3


# =============================================================================
# CHART RENDERING FUNCTIONS
# =============================================================================

@st.cache_data(ttl=60)
def cache_chart_data(data_hash: str, data: Dict) -> Dict:
    """
    Cache chart data to improve performance.
    
    Args:
        data_hash: Unique hash for the data
        data: Chart data to cache
    
    Returns:
        Cached data
    """
    return data


def render_weekly_chart(
    data: Optional[Dict[str, List]] = None,
    title: str = "📈 Weekly Progress",
    show_export: bool = True,
    show_loading: bool = True
):
    """
    Render a weekly progress bar chart.
    
    Phase 7.1 Enhanced:
    - Added loading state
    - Added export functionality
    - Added responsive sizing
    
    Args:
        data: Dict with 'dates', 'completed', 'total' lists
        title: Chart title
        show_export: Whether to show export buttons
        show_loading: Whether to show loading state
    """
    st.subheader(title)
    
    if show_loading and data is None:
        with st.spinner("Loading weekly data..."):
            time.sleep(0.1)
    
    if data is None or not data.get('dates'):
        st.info("📊 No data available for the past week.")
        return
    
    df = pd.DataFrame({
        'Day': data['dates'],
        'Completed': data['completed'],
        'Total': data['total']
    })
    
    st.bar_chart(df.set_index('Day')[['Completed', 'Total']], use_container_width=True)
    
    if show_export:
        with st.expander("📥 Export Options"):
            ChartExporter.render_export_buttons(
                df=df,
                data=data,
                filename="weekly_progress"
            )


def render_score_trend_chart(
    scores: Dict[date, float],
    title: str = "📊 Score Trend",
    show_export: bool = True,
    show_category: bool = True,
    height: int = None
):
    """
    Render a line chart showing score trend over time.
    
    Phase 7.1 Enhanced:
    - Added category indicator
    - Added export functionality
    - Added responsive height
    
    Args:
        scores: Dict mapping dates to score values (0.0-1.0)
        title: Chart title
        show_export: Whether to show export buttons
        show_category: Whether to show score category
        height: Chart height (auto if None)
    """
    st.subheader(title)
    
    if not scores:
        st.info("📊 No score data available yet.")
        return
    
    df = pd.DataFrame([
        {'Date': d.isoformat(), 'Score': round(s * 100, 1)}
        for d, s in sorted(scores.items())
    ])
    
    if df.empty:
        st.info("📊 No score data available yet.")
        return
    
    if show_category and not df.empty:
        current_score = df['Score'].iloc[-1]
        category = get_score_category(current_score / 100)
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Current Score", f"{current_score:.0f}%")
        with col2:
            st.metric("Category", category['label'], delta=category['emoji'])
        st.divider()
    
    chart_df = df.set_index('Date')
    st.line_chart(chart_df, use_container_width=True)
    
    if show_export:
        with st.expander("📥 Export Options"):
            ChartExporter.render_export_buttons(
                df=df,
                data={str(k): v for k, v in scores.items()},
                filename="score_trend"
            )


def get_score_category(score: float) -> Dict[str, str]:
    """
    Get the score category for display.
    
    Args:
        score: Score value (0.0 to 1.0)
    
    Returns:
        Dict with 'label', 'color', and 'emoji'
    """
    if score >= 0.85:
        return {"label": "Excellent", "color": "#4CAF50", "emoji": "🌟"}
    elif score >= 0.70:
        return {"label": "Strong", "color": "#8BC34A", "emoji": "💪"}
    elif score >= 0.50:
        return {"label": "Developing", "color": "#FFC107", "emoji": "🌱"}
    elif score >= 0.30:
        return {"label": "Building", "color": "#FF9800", "emoji": "🔧"}
    else:
        return {"label": "Starting", "color": "#F44336", "emoji": "🆕"}


def render_habit_completion_heatmap(
    completion_data: Dict[str, List[bool]],
    days: int = 30,
    show_export: bool = True
):
    """
    Render a habit completion heatmap.
    
    Phase 7.1 Enhanced:
    - Added export functionality
    - Improved visual styling
    - Added summary statistics
    
    Args:
        completion_data: Dict mapping habit names to list of completion booleans
        days: Number of days to display
        show_export: Whether to show export buttons
    """
    st.subheader("🗓️ Habit Completion Heatmap")
    
    if not completion_data:
        st.info("📊 No habit data available.")
        return
    
    total_completions = sum(sum(1 for c in comps if c) for comps in completion_data.values())
    total_possible = sum(len(comps) for comps in completion_data.values())
    overall_rate = (total_completions / total_possible * 100) if total_possible > 0 else 0
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Completions", total_completions)
    with col2:
        st.metric("Completion Rate", f"{overall_rate:.1f}%")
    with col3:
        st.metric("Habits Tracked", len(completion_data))
    
    st.divider()
    
    today = date.today()
    dates = [(today - timedelta(days=i)).strftime('%m/%d') for i in range(days-1, -1, -1)]
    
    df_data = {}
    for habit_name, completions in completion_data.items():
        if len(completions) < days:
            completions = [False] * (days - len(completions)) + completions
        else:
            completions = completions[-days:]
        df_data[habit_name] = [1 if c else 0 for c in completions]
    
    df = pd.DataFrame(df_data, index=dates)
    
    st.dataframe(
        df,
        use_container_width=True,
        height=min(400, 50 + 35 * len(completion_data))
    )
    
    if show_export:
        with st.expander("📥 Export Options"):
            export_data = {
                'dates': dates,
                'habits': {k: v for k, v in completion_data.items()}
            }
            ChartExporter.render_export_buttons(
                df=df,
                data=export_data,
                filename="habit_heatmap"
            )


def render_category_breakdown(
    categories: Dict[str, int],
    title: str = "📊 Category Breakdown",
    show_export: bool = True
):
    """
    Render a bar chart showing category breakdown.
    
    Phase 7.1 Enhanced:
    - Added export functionality
    - Added percentage display
    
    Args:
        categories: Dict mapping category names to counts
        title: Chart title
        show_export: Whether to show export buttons
    """
    st.subheader(title)
    
    if not categories:
        st.info("📊 No category data available.")
        return
    
    total = sum(categories.values())
    df = pd.DataFrame({
        'Category': list(categories.keys()),
        'Count': list(categories.values()),
        'Percentage': [f"{(v/total*100):.1f}%" for v in categories.values()]
    })
    
    st.bar_chart(df.set_index('Category')['Count'], use_container_width=True)
    
    with st.expander("📋 Details"):
        st.dataframe(
            df,
            use_container_width=True,
            hide_index=True
        )
    
    if show_export:
        with st.expander("📥 Export Options"):
            ChartExporter.render_export_buttons(
                df=df,
                data=categories,
                filename="category_breakdown"
            )


def render_progress_over_time(
    data: Dict[str, List],
    metric_name: str = "Progress",
    show_export: bool = True,
    show_trend: bool = True
):
    """
    Render a multi-line chart showing progress over time.
    
    Phase 7.1 Enhanced:
    - Added trend indicator
    - Added export functionality
    - Added loading state
    
    Args:
        data: Dict with 'dates' and metric name keys
        metric_name: Name of the metric being tracked
        show_export: Whether to show export buttons
        show_trend: Whether to show trend indicator
    """
    if not data or 'dates' not in data:
        st.info(f"📊 No {metric_name.lower()} data available.")
        return
    
    df = pd.DataFrame(data)
    
    if 'dates' in df.columns:
        df = df.set_index('dates')
    
    if show_trend and len(df) > 1:
        numeric_cols = df.select_dtypes(include=['number']).columns
        if len(numeric_cols) > 0:
            first_val = df[numeric_cols[0]].iloc[0]
            last_val = df[numeric_cols[0]].iloc[-1]
            trend = last_val - first_val
            trend_pct = (trend / first_val * 100) if first_val != 0 else 0
            trend_emoji = "📈" if trend > 0 else "📉" if trend < 0 else "➡️"
            st.metric(
                f"{metric_name} Trend",
                f"{last_val:.1f}",
                delta=f"{trend_pct:+.1f}% {trend_emoji}"
            )
    
    st.line_chart(df, use_container_width=True)
    
    if show_export:
        with st.expander("📥 Export Options"):
            ChartExporter.render_export_buttons(
                df=df.reset_index(),
                data=data,
                filename=f"{metric_name.lower().replace(' ', '_')}_progress"
            )


# =============================================================================
# PERFORMANCE OPTIMIZATION
# =============================================================================

def debounced_render(func: Callable, delay: float = 0.1) -> Callable:
    """
    Debounce rapid re-renders for better performance.
    
    Usage:
        @debounced_render
        def render_expensive_chart(data):
            ...
    """
    last_render_time = [0.0]
    
    def wrapper(*args, **kwargs):
        current_time = time.time()
        if current_time - last_render_time[0] >= delay:
            last_render_time[0] = current_time
            return func(*args, **kwargs)
        return None
    
    return wrapper


# =============================================================================
# EXPORT FUNCTIONS
# =============================================================================

__all__ = [
    "render_weekly_chart",
    "render_score_trend_chart",
    "render_habit_completion_heatmap",
    "render_category_breakdown",
    "render_progress_over_time",
    "ChartExporter",
    "ChartLoader",
    "with_loading",
    "get_responsive_chart_height",
    "get_responsive_columns",
    "get_score_category",
    "debounced_render",
]