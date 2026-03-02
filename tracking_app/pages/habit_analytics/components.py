"""
UI components for the Habit Analytics page.

Contains all render functions for the analytics dashboard.
"""

from typing import Dict, Any, List

import streamlit as st

from .constants import (
    AVAILABLE_YEARS,
    DEFAULT_YEAR_INDEX,
    HEATMAP_COLORS,
    CHART_COLOR,
    CORRELATION_EMOJIS,
)
from .helpers import (
    prepare_chart_data,
    calculate_best_worst_days,
)


def render_summary_stats(summary: Dict[str, Any]) -> None:
    """
    Render summary statistics section.
    
    Args:
        summary: Dictionary with summary statistics
    """
    st.subheader("📈 Summary")
    
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


def render_heatmap(heatmap_gen, year: int) -> None:
    """
    Render contribution heatmap.
    
    Args:
        heatmap_gen: HeatmapGenerator instance
        year: Year to display heatmap for
    """
    heatmap_data = heatmap_gen.generate_heatmap(year)
    
    # Convert to DataFrame
    contributions = heatmap_data["contributions"]
    df = prepare_chart_data(contributions)
    
    # Show as area chart
    st.area_chart(df, use_container_width=True, color=CHART_COLOR)
    
    # Level legend
    st.caption("**Contribution Levels:**")
    cols = st.columns(5)
    
    for i, col in enumerate(cols):
        with col:
            st.markdown(
                f"""
                <div style="
                    width: 100%;
                    height: 20px;
                    background-color: {HEATMAP_COLORS[i]};
                    border-radius: 3px;
                    text-align: center;
                    color: white;
                    font-size: 0.8rem;
                ">{i}</div>
                """,
                unsafe_allow_html=True
            )


def render_year_selector() -> int:
    """
    Render year selector for analytics.
    
    Returns:
        Selected year
    """
    return st.selectbox(
        "Year",
        AVAILABLE_YEARS,
        index=DEFAULT_YEAR_INDEX
    )


def render_correlations(correlations: List[Dict[str, Any]]) -> None:
    """
    Render habit correlations.
    
    Args:
        correlations: List of correlation dictionaries
    """
    if not correlations:
        st.info("No significant correlations found yet. Keep tracking!")
        return
    
    for corr in correlations:
        strength_emoji = CORRELATION_EMOJIS.get(corr["strength"], "📊")
        direction = "↗️" if corr["correlation"] > 0 else "↘️"
        
        st.markdown(
            f"**{strength_emoji} {corr['habit1']}** {direction} **{corr['habit2']}**"
        )
        st.caption(
            f"Correlation: {corr['correlation']:.2f} ({corr['strength']})"
        )
        st.progress(min(1.0, abs(corr["correlation"])))


def render_day_patterns(patterns: Dict[str, float]) -> None:
    """
    Render day of week patterns.
    
    Args:
        patterns: Dictionary mapping day names to completion rates
    """
    if not patterns:
        st.info("Not enough data yet")
        return
    
    import pandas as pd
    
    df = pd.DataFrame({
        "Day": list(patterns.keys()),
        "Completion Rate": [v * 100 for v in patterns.values()]
    })
    
    st.bar_chart(df.set_index("Day"), use_container_width=True, color=CHART_COLOR)
    
    # Best and worst days
    best_day, worst_day = calculate_best_worst_days(patterns)
    
    if best_day and worst_day:
        col1, col2 = st.columns(2)
        
        with col1:
            st.success(f"🌟 Best Day: **{best_day}** ({patterns[best_day]*100:.0f}%)")
        
        with col2:
            st.warning(f"📉 Worst Day: **{worst_day}** ({patterns[worst_day]*100:.0f}%)")