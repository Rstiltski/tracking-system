"""
Habit Difficulty Widget - User interface for difficulty ratings.

Provides UI components for:
- Rating habit difficulty
- Viewing adjustment suggestions
- Applying adjustments
- Tracking adjustment history

Usage:
    from tracking_app.components.difficulty_widget import render_difficulty_widget
    
    render_difficulty_widget(storage, habit_id)
"""
import streamlit as st
from typing import Dict, Optional, Any, List
from datetime import date

from brain.models.habit_difficulty import (
    DifficultyRating,
    AdjustmentType,
    DifficultySuggestion,
    DifficultyAdjustment,
    SUGGESTION_TEMPLATES,
)
from brain.behavioral.difficulty_adjuster import DifficultyAdjuster, get_tiny_habit_version


# Rating emojis and labels
RATING_OPTIONS = {
    DifficultyRating.TOO_EASY: {
        "emoji": "📈",
        "label": "Too Easy",
        "description": "I could do more",
    },
    DifficultyRating.JUST_RIGHT: {
        "emoji": "✅",
        "label": "Just Right",
        "description": "Perfect challenge level",
    },
    DifficultyRating.TOO_HARD: {
        "emoji": "📉",
        "label": "Too Hard",
        "description": "I need to make it smaller",
    },
}


def render_difficulty_widget(
    storage: Any,
    habit_id: str,
    habit_name: str,
    current_target: float = 1.0,
    show_history: bool = True
) -> None:
    """
    Render the difficulty rating widget.

    Args:
        storage: Storage instance
        habit_id: ID of the habit
        habit_name: Name of the habit
        current_target: Current target value
        show_history: Whether to show adjustment history
    """
    # Initialize adjuster
    adjuster = DifficultyAdjuster(storage, habit_id)

    # Get current rating
    current_rating = storage.get_difficulty_rating(habit_id)

    # Widget container
    with st.container():
        st.markdown("**📊 How difficult is this habit?**")

        # Rating buttons
        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button(
                f"{RATING_OPTIONS[DifficultyRating.TOO_EASY]['emoji']} Too Easy",
                key=f"rate_easy_{habit_id}",
                help=RATING_OPTIONS[DifficultyRating.TOO_EASY]["description"],
                use_container_width=True
            ):
                _handle_rating(adjuster, DifficultyRating.TOO_EASY, habit_id)

        with col2:
            if st.button(
                f"{RATING_OPTIONS[DifficultyRating.JUST_RIGHT]['emoji']} Just Right",
                key=f"rate_right_{habit_id}",
                help=RATING_OPTIONS[DifficultyRating.JUST_RIGHT]["description"],
                use_container_width=True
            ):
                _handle_rating(adjuster, DifficultyRating.JUST_RIGHT, habit_id)

        with col3:
            if st.button(
                f"{RATING_OPTIONS[DifficultyRating.TOO_HARD]['emoji']} Too Hard",
                key=f"rate_hard_{habit_id}",
                help=RATING_OPTIONS[DifficultyRating.TOO_HARD]["description"],
                use_container_width=True
            ):
                _handle_rating(adjuster, DifficultyRating.TOO_HARD, habit_id)

        # Show current rating if exists
        if current_rating:
            rating_value = DifficultyRating(current_rating.get("rating", "just_right"))
            rating_info = RATING_OPTIONS[rating_value]
            st.caption(
                f"Last rating: {rating_info['emoji']} {rating_info['label']} "
                f"({current_rating.get('rated_at', 'Unknown')[:10]})"
            )

        # Show suggestion if available
        _render_suggestion_section(adjuster, habit_name, current_target)

        # Show history
        if show_history:
            _render_adjustment_history(adjuster)


def _handle_rating(
    adjuster: DifficultyAdjuster,
    rating: DifficultyRating,
    habit_id: str
) -> None:
    """
    Handle a difficulty rating submission.

    Args:
        adjuster: DifficultyAdjuster instance
        rating: User's rating
        habit_id: ID of the habit
    """
    # Record the rating
    adjuster.record_rating(rating)

    # Show feedback
    rating_info = RATING_OPTIONS[rating]
    st.success(f"✅ Recorded: {rating_info['emoji']} {rating_info['label']}")

    # Generate and show suggestion
    suggestion = adjuster.generate_suggestion()
    if suggestion:
        st.session_state[f"suggestion_{habit_id}"] = suggestion
    else:
        st.session_state[f"suggestion_{habit_id}"] = None

    st.rerun()


def _render_suggestion_section(
    adjuster: DifficultyAdjuster,
    habit_name: str,
    current_target: float
) -> None:
    """
    Render adjustment suggestion section.

    Args:
        adjuster: DifficultyAdjuster instance
        habit_name: Name of the habit
        current_target: Current target value
    """
    habit_id = adjuster.habit_id
    suggestion_key = f"suggestion_{habit_id}"

    # Check for existing suggestion in session state
    suggestion = st.session_state.get(suggestion_key)

    # If no suggestion in session, generate one
    if not suggestion:
        suggestion = adjuster.generate_suggestion()

    if not suggestion:
        return

    # Show suggestion card
    st.divider()
    st.markdown(f"**💡 Suggestion: {suggestion.title}**")
    st.markdown(suggestion.description)

    # Show details
    col1, col2 = st.columns(2)
    with col1:
        st.info(f"**Current:** {current_target}")
    with col2:
        st.success(f"**Suggested:** {suggestion.suggested_value}")

    st.caption(f"📝 {suggestion.reason}")
    st.caption(f"🎯 Confidence: {suggestion.confidence:.0%}")

    # Show tiny habit version for decrease suggestions
    if suggestion.suggestion_type == AdjustmentType.DECREASE_TARGET:
        tiny_version = get_tiny_habit_version(habit_name, current_target)
        st.markdown(f"**🐜 Tiny Version:** {tiny_version}")

    # Action buttons
    col_apply, col_skip = st.columns(2)

    with col_apply:
        if st.button(
            f"✓ {suggestion.get_action_text()}",
            key=f"apply_{habit_id}",
            type="primary",
            use_container_width=True
        ):
            _apply_suggestion(adjuster, suggestion, habit_id)

    with col_skip:
        if st.button(
            "Not Now",
            key=f"skip_{habit_id}",
            use_container_width=True
        ):
            st.session_state[suggestion_key] = None
            st.rerun()


def _apply_suggestion(
    adjuster: DifficultyAdjustment,
    suggestion: DifficultySuggestion,
    habit_id: str
) -> None:
    """
    Apply a difficulty adjustment suggestion.

    Args:
        adjuster: DifficultyAdjuster instance
        suggestion: Suggestion to apply
        habit_id: ID of the habit
    """
    try:
        # Apply the suggestion
        adjustment = adjuster.apply_suggestion(suggestion)

        # Clear suggestion
        st.session_state[f"suggestion_{habit_id}"] = None

        # Show success
        st.success(
            f"✅ Habit adjusted! "
            f"{suggestion.suggestion_type.value.replace('_', ' ').title()} "
            f"from {suggestion.current_value} to {suggestion.suggested_value}"
        )

        # Show encouragement based on adjustment type
        if suggestion.suggestion_type == AdjustmentType.DECREASE_TARGET:
            st.info(
                "💡 Remember: The goal is consistency, not perfection. "
                "Once the tiny version becomes automatic, you can gradually increase!"
            )
        elif suggestion.suggestion_type == AdjustmentType.INCREASE_TARGET:
            st.info(
                "💡 Great progress! Increase gradually - about 10-15% at a time "
                "to avoid burnout."
            )

        st.rerun()

    except Exception as e:
        st.error(f"❌ Failed to apply adjustment: {str(e)}")


def _render_adjustment_history(
    adjuster: DifficultyAdjuster
) -> None:
    """
    Render adjustment history section.

    Args:
        adjuster: DifficultyAdjuster instance
    """
    history = adjuster.get_adjustment_history(limit=5)

    if not history:
        return

    st.divider()
    st.markdown("**📜 Adjustment History**")

    for adjustment in history:
        emoji = {
            AdjustmentType.INCREASE_TARGET: "⬆️",
            AdjustmentType.DECREASE_TARGET: "⬇️",
            AdjustmentType.CHANGE_FREQUENCY: "🔄",
            AdjustmentType.ADD_SUPPORT: "➕",
            AdjustmentType.NO_CHANGE: "⏸️",
        }.get(adjustment.adjustment_type, "⚪")

        adjusted_date = adjustment.adjusted_at[:10] if hasattr(adjustment.adjusted_at, '__str__') else str(adjustment.adjusted_at)[:10]

        with st.expander(f"{emoji} {adjusted_date}: {adjustment.adjustment_type.value.replace('_', ' ').title()}"):
            st.caption(f"From {adjustment.old_value} to {adjustment.new_value}")
            if adjustment.reason:
                st.caption(f"Reason: {adjustment.reason}")
            if adjustment.effectiveness:
                stars = "⭐" * adjustment.effectiveness
                st.caption(f"Effectiveness: {stars}")


def render_difficulty_quick_rating(
    storage: Any,
    habit_id: str,
    on_rate: Optional[callable] = None
) -> None:
    """
    Render a quick difficulty rating selector (compact version).

    Args:
        storage: Storage instance
        habit_id: ID of the habit
        on_rate: Optional callback function when rating is submitted
    """
    adjuster = DifficultyAdjuster(storage, habit_id)

    # Compact rating row
    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button(
            "📈 Easier",
            key=f"quick_easy_{habit_id}",
            help="Make it easier",
            use_container_width=True
        ):
            if on_rate:
                on_rate(DifficultyRating.TOO_EASY)
            else:
                adjuster.record_rating(DifficultyRating.TOO_EASY)
                st.rerun()

    with col2:
        if st.button(
            "✅ Perfect",
            key=f"quick_perfect_{habit_id}",
            help="Just right",
            use_container_width=True
        ):
            if on_rate:
                on_rate(DifficultyRating.JUST_RIGHT)
            else:
                adjuster.record_rating(DifficultyRating.JUST_RIGHT)
                st.rerun()

    with col3:
        if st.button(
            "📉 Harder",
            key=f"quick_hard_{habit_id}",
            help="Make it harder",
            use_container_width=True
        ):
            if on_rate:
                on_rate(DifficultyRating.TOO_HARD)
            else:
                adjuster.record_rating(DifficultyRating.TOO_HARD)
                st.rerun()


def get_difficulty_tips(rating: DifficultyRating) -> List[str]:
    """
    Get tips based on difficulty rating.

    Args:
        rating: The difficulty rating

    Returns:
        List of tip strings
    """
    tips = {
        DifficultyRating.TOO_EASY: [
            "Increase your target by 10-15%",
            "Add a related micro-habit",
            "Try doing it twice a day",
            "Increase duration or intensity",
        ],
        DifficultyRating.JUST_RIGHT: [
            "Keep up the great work!",
            "Focus on consistency",
            "Track your progress",
            "Celebrate small wins",
        ],
        DifficultyRating.TOO_HARD: [
            "Scale down to a 2-minute version",
            "Reduce the target by 50%",
            "Focus on showing up, not performance",
            "Remove friction from your environment",
            "Try implementation intentions (if-then planning)",
        ],
    }

    return tips.get(rating, [])


__all__ = [
    "render_difficulty_widget",
    "render_difficulty_quick_rating",
    "get_difficulty_tips",
]
