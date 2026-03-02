"""
Habit Analytics Page - Advanced analytics dashboard.

Usage:
    streamlit run tracking_app/pages/habit_analytics.py
"""
import streamlit as st

from tracking_app.pages.habit_analytics import (
    init_session_state,
    render_summary_stats,
    render_heatmap,
    render_correlations,
    render_day_patterns,
)
from tracking_app.pages.habit_analytics.constants import (
    PAGE_TITLE,
    PAGE_ICON,
    LAYOUT,
)
from tracking_app.pages.habit_analytics.components import render_year_selector


# Page configuration
st.set_page_config(
    page_title=PAGE_TITLE,
    page_icon=PAGE_ICON,
    layout=LAYOUT
)


def main():
    """Main analytics page."""
    # Initialize
    init_session_state()
    
    storage = st.session_state.storage
    user_id = st.session_state.user_id
    
    # Header
    st.title("📊 Habit Analytics")
    st.markdown("Deep dive into your habit patterns and trends!")
    
    # Initialize analyzers
    from brain.analytics.heatmap import HeatmapGenerator
    from brain.analytics.analytics_components import CorrelationAnalyzer, TrendAnalyzer
    
    heatmap_gen = HeatmapGenerator(storage, user_id)
    correlation_analyzer = CorrelationAnalyzer(storage, user_id)
    
    # Summary stats
    summary = heatmap_gen.get_summary_stats()
    render_summary_stats(summary)
    
    # Contribution Heatmap
    st.subheader("🗓️ Contribution Heatmap")
    year = render_year_selector()
    render_heatmap(heatmap_gen, year)
    
    st.divider()
    
    # Correlations
    st.subheader("🔗 Habit Correlations")
    correlations = correlation_analyzer.calculate_habit_correlations()
    render_correlations(correlations)
    
    st.divider()
    
    # Day of Week Patterns
    st.subheader("📅 Day of Week Patterns")
    patterns = correlation_analyzer.get_day_of_week_patterns()
    render_day_patterns(patterns)


if __name__ == "__main__":
    main()