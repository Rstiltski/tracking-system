"""
Weekly Review Page - Streamlit page for weekly habit reviews.

Provides a comprehensive weekly review interface with:
- Completion metrics
- Streak milestones
- Habit performance
- Actionable insights

Usage:
    streamlit run tracking_app/pages/weekly_review.py
"""
import streamlit as st
from datetime import date, timedelta
from typing import List, Dict, Any, Optional

from brain.analytics.weekly_review import WeeklyReview, WeeklyReviewGenerator


# Page configuration
st.set_page_config(
    page_title="Weekly Review - Veryfyn",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)


def main():
    """Main review page."""
    # Initialize
    if 'storage' not in st.session_state:
        from tracking_app.storage import get_storage
        st.session_state.storage = get_storage()

    # Header
    st.title("📊 Weekly Review")
    st.markdown("Reflect on your progress and plan for improvement!")

    # Week selector
    current_week = date.today().isocalendar().week
    current_year = date.today().isocalendar().year

    col_week, col_year, col_nav = st.columns(3)

    with col_week:
        selected_week = st.number_input(
            "Week",
            min_value=1,
            max_value=52,
            value=current_week
        )

    with col_year:
        selected_year = st.number_input(
            "Year",
            min_value=2024,
            max_value=2030,
            value=current_year
        )

    with col_nav:
        if st.button("Generate Review", type="primary", use_container_width=True):
            if 'review_cache' in st.session_state:
                del st.session_state.review_cache
            st.rerun()

    # Generate review
    storage = st.session_state.storage
    generator = WeeklyReviewGenerator(storage)

    with st.spinner("Generating your weekly review..."):
        review = generator.generate_review(selected_week, selected_year)

    # Display review
    display_review(review)

    # Historical comparison
    st.divider()
    display_historical_comparison(generator)


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
            label="📋 Active Habits",
            value=review.total_habits
        )

    with col2:
        st.metric(
            label="✅ Completions",
            value=review.total_completions
        )

    with col3:
        completion_emoji = get_completion_emoji(review.completion_rate)
        st.metric(
            label=f"{completion_emoji} Completion Rate",
            value=f"{review.completion_rate:.0f}%"
        )

    with col4:
        st.metric(
            label="⭐ XP Earned",
            value=review.xp_earned
        )

    st.divider()

    # Insights section
    st.subheader("💡 Insights")
    for insight in review.insights:
        st.info(insight)

    st.divider()

    # Best performer
    if review.best_habit:
        st.subheader("🌟 Best Performer")
        best = review.best_habit
        st.success(
            f"{best['icon']} **{best['name']}** - "
            f"{best['completion_rate']:.0f}% completion rate "
            f"({best['completions']}/7 days)"
        )

    # Needs attention
    if review.needs_attention:
        st.subheader("⚠️ Needs Attention")
        for habit in review.needs_attention:
            st.warning(
                f"{habit['icon']} **{habit['name']}** - "
                f"{habit['completion_rate']:.0f}% completion rate. "
                f"{habit['reason']}"
            )

    # Streak milestones
    if review.streak_milestones:
        st.subheader("🔥 Streak Milestones")
        for milestone in review.streak_milestones:
            st.success(
                f"🎉 **{milestone['habit_name']}** reached "
                f"{milestone['milestone']}-day streak!"
            )

    # Detailed breakdown
    st.divider()
    st.subheader("📈 Detailed Breakdown")

    # Get detailed habit data
    storage = st.session_state.storage
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
                'Habit': f"{habit.icon if hasattr(habit, 'icon') else '🎯'} {habit.name}",
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
    st.subheader("📅 Recent Weeks Comparison")

    # Get last 4 weeks
    reviews = generator.get_weekly_review_history(limit=4)

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
        import pandas as pd
        trend_df = pd.DataFrame(trend_data).set_index('Week')
        st.line_chart(trend_df)


def get_completion_emoji(rate: float) -> str:
    """
    Get emoji for completion rate.

    Args:
        rate: Completion rate (0.0-1.0)

    Returns:
        Emoji string
    """
    if rate >= 0.90:
        return "🌟"
    elif rate >= 0.70:
        return "👍"
    elif rate >= 0.50:
        return "💪"
    else:
        return "🌱"


def count_weekly_completions(
    storage: Any,
    habit_id: str,
    week_number: int,
    year: int
) -> int:
    """
    Count completions for a habit in a specific week.

    Args:
        storage: Storage instance
        habit_id: Habit ID
        week_number: ISO week number
        year: Year

    Returns:
        Number of completions
    """
    # Get week dates
    jan_4 = date(year, 1, 4)
    week_1_monday = jan_4 - timedelta(days=jan_4.weekday())
    week_start = week_1_monday + timedelta(weeks=week_number - 1)
    week_end = week_start + timedelta(days=6)

    # Count completions
    completions = 0
    current_date = week_start
    while current_date <= week_end:
        entry = storage.get_habit_entry(habit_id, current_date)
        if entry and hasattr(entry, 'value') and entry.value > 0:
            completions += 1
        current_date += timedelta(days=1)

    return completions


def calculate_streak(storage: Any, habit_id: str) -> int:
    """Calculate current streak for a habit."""
    streak = 0
    today = date.today()

    for i in range(365):
        check_date = today - timedelta(days=i)
        entry = storage.get_habit_entry(habit_id, check_date)
        if entry and hasattr(entry, 'value') and entry.value > 0:
            streak += 1
        else:
            break

    return streak


if __name__ == "__main__":
    main()
