"""
Habit Analytics Page - Advanced analytics dashboard.

Usage:
    streamlit run tracking_app/pages/habit_analytics.py
"""
import streamlit as st
from datetime import date, timedelta
from typing import Dict, Any

from brain.analytics.heatmap import HeatmapGenerator
from brain.analytics.analytics_components import CorrelationAnalyzer, TrendAnalyzer


# Page configuration
st.set_page_config(
    page_title="Habit Analytics - Veryfyn",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


def main():
    """Main analytics page."""
    # Initialize
    if 'storage' not in st.session_state:
        from tracking_app.storage import get_storage
        st.session_state.storage = get_storage()

    if 'user_id' not in st.session_state:
        st.session_state.user_id = ""

    storage = st.session_state.storage
    user_id = st.session_state.user_id

    # Header
    st.title("📊 Habit Analytics")
    st.markdown("Deep dive into your habit patterns and trends!")

    # Initialize analyzers
    heatmap_gen = HeatmapGenerator(storage, user_id)
    correlation_analyzer = CorrelationAnalyzer(storage, user_id)

    # Summary stats
    st.subheader("📈 Summary")
    summary = heatmap_gen.get_summary_stats()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Contributions", summary["total_contributions"])
    with col2:
        st.metric("Current Streak", f"🔥 {summary['current_streak']} days")
    with col3:
        st.metric("Best Streak", f"🏆 {summary['best_streak']} days")
    with col4:
        level_4_days = summary["levels"].get(4, 0)
        st.metric("Excellent Days", f"⭐ {level_4_days}")

    st.divider()

    # Contribution Heatmap
    st.subheader("🗓️ Contribution Heatmap")
    render_heatmap(heatmap_gen)

    st.divider()

    # Correlations
    st.subheader("🔗 Habit Correlations")
    render_correlations(correlation_analyzer)

    st.divider()

    # Day of Week Patterns
    st.subheader("📅 Day of Week Patterns")
    render_day_patterns(correlation_analyzer)


def render_heatmap(heatmap_gen: HeatmapGenerator) -> None:
    """
    Render contribution heatmap.

    Args:
        heatmap_gen: HeatmapGenerator instance
    """
    year = st.selectbox("Year", [2024, 2025, 2026], index=2)
    heatmap_data = heatmap_gen.generate_heatmap(year)

    # Create simple visualization
    import pandas as pd

    # Convert to DataFrame
    contributions = heatmap_data["contributions"]
    dates = list(contributions.keys())
    values = list(contributions.values())

    df = pd.DataFrame({
        "Date": pd.to_datetime(dates),
        "Contributions": values
    })
    df = df.set_index("Date")

    # Show as area chart
    st.area_chart(df, use_container_width=True, color="#6366f1")

    # Level legend
    st.caption("**Contribution Levels:**")
    cols = st.columns(5)
    colors = ["#ebedf0", "#9be9a8", "#40c463", "#30a14e", "#216e39"]
    for i, col in enumerate(cols):
        with col:
            st.markdown(
                f"""
                <div style="
                    width: 100%;
                    height: 20px;
                    background-color: {colors[i]};
                    border-radius: 3px;
                    text-align: center;
                    color: white;
                    font-size: 0.8rem;
                ">{i}</div>
                """,
                unsafe_allow_html=True
            )


def render_correlations(correlation_analyzer: CorrelationAnalyzer) -> None:
    """
    Render habit correlations.

    Args:
        correlation_analyzer: CorrelationAnalyzer instance
    """
    correlations = correlation_analyzer.calculate_habit_correlations()

    if not correlations:
        st.info("No significant correlations found yet. Keep tracking!")
        return

    for corr in correlations:
        strength_emoji = {
            "strong": "💪",
            "moderate": "👍",
            "weak": "📊"
        }.get(corr["strength"], "📊")

        direction = "↗️" if corr["correlation"] > 0 else "↘️"

        st.markdown(
            f"**{strength_emoji} {corr['habit1']}** {direction} **{corr['habit2']}**"
        )
        st.caption(
            f"Correlation: {corr['correlation']:.2f} ({corr['strength']})"
        )
        st.progress(min(1.0, abs(corr["correlation"])))


def render_day_patterns(correlation_analyzer: CorrelationAnalyzer) -> None:
    """
    Render day of week patterns.

    Args:
        correlation_analyzer: CorrelationAnalyzer instance
    """
    patterns = correlation_analyzer.get_day_of_week_patterns()

    if not patterns:
        st.info("Not enough data yet")
        return

    import pandas as pd

    df = pd.DataFrame({
        "Day": list(patterns.keys()),
        "Completion Rate": [v * 100 for v in patterns.values()]
    })

    st.bar_chart(df.set_index("Day"), use_container_width=True, color="#6366f1")

    # Best and worst days
    best_day = max(patterns, key=patterns.get)
    worst_day = min(patterns, key=patterns.get)

    col1, col2 = st.columns(2)
    with col1:
        st.success(f"🌟 Best Day: **{best_day}** ({patterns[best_day]*100:.0f}%)")
    with col2:
        st.warning(f"📉 Worst Day: **{worst_day}** ({patterns[worst_day]*100:.0f}%)")


if __name__ == "__main__":
    main()
