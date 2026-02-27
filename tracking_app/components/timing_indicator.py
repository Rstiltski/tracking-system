"""
Timing Indicator - Display optimal timing suggestions.

Provides UI components for:
- Best time badge
- Timing suggestions
- Schedule optimization

Usage:
    from tracking_app.components.timing_indicator import render_timing_indicator
    
    render_timing_indicator(storage, habit_id)
"""
import streamlit as st
from typing import Dict, Optional, Any
from brain.analytics.timing_optimizer import TimingOptimizer


def render_timing_indicator(
    storage: Any,
    habit_id: str,
    habit_name: str
) -> None:
    """
    Render timing indicator.

    Args:
        storage: Storage instance
        habit_id: Habit ID
        habit_name: Habit name
    """
    # Get timing analysis
    analysis = storage.get_timing_analysis(habit_id)

    if not analysis:
        return

    # Show best day badge
    best_day = analysis.get("best_day", "Monday")
    consistency = analysis.get("consistency_score", 0)

    st.caption(
        f"⏰ Best day: **{best_day}** (Consistency: {consistency:.0%})"
    )

    # Show optimization suggestion if consistency is low
    if consistency < 0.6:
        with st.expander("💡 Optimize Your Timing"):
            st.markdown(
                f"""
                **Current consistency: {consistency:.0%}**
                
                Your habit completion varies by day. Consider:
                - Performing this habit on **{best_day}**s
                - Setting a consistent time each day
                - Using implementation intentions
                """
            )

            if st.button(
                "Apply Recommendation",
                key=f"apply_timing_{habit_id}",
                use_container_width=True
            ):
                storage.save_timing_recommendation(
                    habit_id,
                    f"Perform on {best_day}s"
                )
                st.success(f"✅ Recommendation saved! Try {best_day}s.")


def render_timing_suggestions(
    storage: Any,
    habit_id: str,
    habit_name: str,
    habit_type: str = "general"
) -> None:
    """
    Render detailed timing suggestions.

    Args:
        storage: Storage instance
        habit_id: Habit ID
        habit_name: Habit name
        habit_type: Type of habit
    """
    optimizer = TimingOptimizer(storage, habit_id)
    suggestions = optimizer.get_best_times(habit_type)

    if not suggestions:
        return

    st.divider()
    st.markdown("**⏰ Timing Recommendations**")

    for suggestion in suggestions:
        icon = "📊" if suggestion.get("type") == "data-driven" else "📚"
        st.markdown(
            f"""
            <div style="
                padding: 0.5rem;
                border-radius: 0.5rem;
                background: rgba(255,255,255,0.05);
                margin: 0.5rem 0;
            ">
                <div style="font-size: 0.9rem;">
                    {icon} **{suggestion.get('recommendation', '')}**
                </div>
                <div style="font-size: 0.8rem; color: gray;">
                    {suggestion.get('reason', '')}
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )


def get_best_time_emoji(hour: int) -> str:
    """
    Get emoji for best time.

    Args:
        hour: Hour (0-23)

    Returns:
        Emoji string
    """
    if 5 <= hour < 12:
        return "🌅"
    elif 12 <= hour < 17:
        return "☀️"
    elif 17 <= hour < 21:
        return "🌆"
    else:
        return "🌙"


__all__ = [
    "render_timing_indicator",
    "render_timing_suggestions",
    "get_best_time_emoji",
]
