"""
Component render functions for the Weekly Review page.
"""

import streamlit as st
from datetime import date
from typing import Any

from brain.analytics.weekly_review import WeeklyReview, WeeklyReviewGenerator

from .constants import (
    PAGE_TITLE,
    PAGE_ICON,
    PAGE_LAYOUT,
    INITIAL_SIDEBAR_STATE,
    MIN_WEEK,
    MAX_WEEK,
    MIN_YEAR,
    MAX_YEAR,
    HISTORY_LIMIT,
    LABEL_ACTIVE_HABITS,
    LABEL_COMPLETIONS,
    LABEL_COMPLETION_RATE,
    LABEL_XP_EARNED,
    HEADER_INSIGHTS,
    HEADER_BEST_PERFORMER,
    HEADER_NEEDS_ATTENTION,
    HEADER_STREAK_MILESTONES,
    HEADER_DETAILED_BREAKDOWN,
    HEADER_HISTORICAL_COMPARISON,
)
from .helpers import (
    get_completion_emoji,
    count_weekly_completions,
    calculate_streak,
    get_habit_display_name,
)
from .session_state import (
    init_session_state,
    get_storage,
    clear_review_cache,
)


def render_week_selector() -> tuple:
    """
    Render week selector controls.

    Returns:
        Tuple of (selected_week, selected_year)
    """
    current_week = date.today().isocalendar().week
    current_year = date.today().isocalendar().year

    col_week, col_year, col_nav = st.columns(3)

    with col_week:
        selected_week = st.number_input(
            "Week",
            min_value=MIN_WEEK,
            max_value=MAX_WEEK,
            value=current_week
        )

    with col_year:
        selected_year = st.number_input(
            "Year",
            min_value=MIN_YEAR,
            max_value=MAX_YEAR,
            value=current_year
        )

    with col_nav:
        if st.button("Generate Review", type="primary", use_container_width=True):
            clear_review_cache()
            st.rerun()

    return selected_week, selected_year


def display_review(review: WeeklyReview) -> None:
    """
    Display a weekly review.

    Args:
        review: WeeklyReview to display
    """
    # Week header
    st.subheader(f"Week {review.week_number} of {review.year}")

    # Key metrics row
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.metric(
            label=LABEL_ACTIVE_HABITS,
            value=review.total_habits
        )

    with col2:
        st.metric(
            label=LABEL_COMPLETIONS,
            value=review.total_completions
        )

    with col3:
        completion_emoji = get_completion_emoji(review.completion_rate)
        st.metric(
            label=f"{completion_emoji} {LABEL_COMPLETION_RATE}",
            value=f"{review.completion_rate:.0f}%"
        )

    with col4:
        st.metric(
            label=LABEL_XP_EARNED,
            value=review.xp_earned
        )

    st.divider()

    # Insights section
    st.subheader(HEADER_INSIGHTS)
    for insight in review.insights:
        st.info(insight)

    st.divider()

    # Best performer
    if review.best_habit:
        st.subheader(HEADER_BEST_PERFORMER)
        best = review.best_habit
        st.success(
            f"{best['icon']} **{best['name']}** - "
            f"{best['completion_rate']:.0f}% completion rate "
            f"({best['completions']}/7 days)"
        )

    # Needs attention
    if review.needs_attention:
        st.subheader(HEADER_NEEDS_ATTENTION)
        for habit in review.needs_attention:
            st.warning(
                f"{habit['icon']} **{habit['name']}** - "
                f"{habit['completion_rate']:.0f}% completion rate. "
                f"{habit['reason']}"
            )

    # Streak milestones
    if review.streak_milestones:
        st.subheader(HEADER_STREAK_MILESTONES)
        for milestone in review.streak_milestones:
            st.success(
                f"🎉 **{milestone['habit_name']}** reached "
                f"{milestone['milestone']}-day streak!"
            )

    # Detailed breakdown
    st.divider()
    st.subheader(HEADER_DETAILED_BREAKDOWN)

    # Get detailed habit data
    storage = get_storage()
    habits = storage.get_habits(include_archived=False)

    if habits:
        # Create summary table
        habit_data = []
        for habit in habits:
            completions = count_weekly_completions(
                storage,
                habit.id,
                review.week_number,
                review.year
            )
            habit_data.append({
                'Habit': get_habit_display_name(habit),
                'Completions': completions,
                'Rate': f"{(completions/7)*100:.0f}%",
                'Streak': calculate_streak(storage, habit.id)
            })

        import pandas as pd
        df = pd.DataFrame(habit_data)
        st.dataframe(df, use_container_width=True, hide_index=True)


def display_historical_comparison(generator: WeeklyReviewGenerator) -> None:
    """
    Display historical review comparison.

    Args:
        generator: WeeklyReviewGenerator instance
    """
    st.subheader(HEADER_HISTORICAL_COMPARISON)

    # Get last 4 weeks
    reviews = generator.get_weekly_review_history(limit=HISTORY_LIMIT)

    if len(reviews) < 2:
        st.info("Not enough data for comparison yet. Keep tracking!")
        return

    # Create comparison table
    comparison_data = []
    for review in reversed(reviews):  # Oldest first
        comparison_data.append({
            'Week': f"W{review.week_number}",
            'Completion': f"{review.completion_rate:.0f}%",
            'Completions': review.total_completions,
            'XP': review.xp_earned,
            'Insights': len(review.insights)
        })

    import pandas as pd
    df = pd.DataFrame(comparison_data)
    st.dataframe(df, use_container_width=True, hide_index=True)

    # Trend chart
    if len(reviews) >= 2:
        st.markdown("**Completion Rate Trend**")
        trend_data = {
            'Week': [f"W{r.week_number}" for r in reversed(reviews)],
            'Rate': [r.completion_rate * 100 for r in reversed(reviews)]
        }
        trend_df = pd.DataFrame(trend_data).set_index('Week')
        st.line_chart(trend_df)


def render_weekly_review_page() -> None:
    """Render the complete weekly review page."""
    st.set_page_config(
        page_title=PAGE_TITLE,
        page_icon=PAGE_ICON,
        layout=PAGE_LAYOUT,
        initial_sidebar_state=INITIAL_SIDEBAR_STATE
    )

    # Initialize session state
    init_session_state()

    # Header
    st.title(f"{PAGE_ICON} Weekly Review")
    st.markdown("Reflect on your progress and plan for improvement!")

    # Week selector
    selected_week, selected_year = render_week_selector()

    # Generate review
    storage = get_storage()
    generator = WeeklyReviewGenerator(storage)

    with st.spinner("Generating your weekly review..."):
        review = generator.generate_review(selected_week, selected_year)

    # Display review
    display_review(review)

    # Historical comparison
    st.divider()
    display_historical_comparison(generator)