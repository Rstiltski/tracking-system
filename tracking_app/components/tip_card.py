"""
Environment Tip Card - Display environment design tips.

Provides UI components for:
- Tip card display
- Tip carousel
- "I tried this" tracking

Usage:
    from tracking_app.components.tip_card import render_tip_card
    
    render_tip_card(storage, tip, habit_id, user_id)
"""
import streamlit as st
from typing import Dict, Optional, Any, List
from brain.models.environment_tip import (
    EnvironmentTip,
    TipCategory,
    HabitType,
    UserTipInteraction,
    DEFAULT_TIPS,
)
from brain.behavioral.tip_engine import TipEngine


# Category emojis
CATEGORY_EMOJIS = {
    TipCategory.CUE_DESIGN: "🎯",
    TipCategory.FRICTION_REDUCTION: "⚡",
    TipCategory.IMPLEMENTATION: "📋",
    TipCategory.SOCIAL: "👥",
    TipCategory.PHYSICAL: "🏠",
    TipCategory.DIGITAL: "💻",
}


def render_tip_card(
    storage: Any,
    tip: EnvironmentTip,
    habit_id: str,
    user_id: str = "",
    show_action: bool = True
) -> None:
    """
    Render a single tip card.

    Args:
        storage: Storage instance
        tip: Tip to display
        habit_id: Habit ID
        user_id: User ID
        show_action: Whether to show action buttons
    """
    category_emoji = CATEGORY_EMOJIS.get(
        tip.category,
        CATEGORY_EMOJIS[TipCategory.CUE_DESIGN]
    )

    with st.container():
        # Tip header
        st.markdown(
            f"""
            <div style="
                padding: 1rem;
                border-radius: 0.5rem;
                border-left: 4px solid #6366f1;
                background: rgba(255,255,255,0.05);
                margin: 0.5rem 0;
            ">
                <div style="font-size: 1.1rem; font-weight: bold;">
                    {category_emoji} {tip.title}
                </div>
                <div style="font-size: 0.9rem; color: gray; margin: 0.5rem 0;">
                    {tip.description}
                </div>
                <div style="font-size: 0.85rem; color: #6366f1; font-style: italic;">
                    💡 Example: {tip.example}
                </div>
                <div style="font-size: 0.8rem; color: gray; margin-top: 0.5rem;">
                    {tip.get_difficulty_emoji()} {tip.difficulty.title()} · 
                    {tip.get_effectiveness_stars()} ({tip.effectiveness}/5)
                </div>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Action buttons
        if show_action:
            col1, col2 = st.columns(2)
            with col1:
                if st.button(
                    "✓ I Tried This",
                    key=f"tip_tried_{tip.id}_{habit_id}",
                    use_container_width=True
                ):
                    _record_tip_interaction(
                        storage,
                        tip.id,
                        habit_id,
                        user_id,
                        "tried"
                    )
            with col2:
                if st.button(
                    "👍 Helpful",
                    key=f"tip_helpful_{tip.id}_{habit_id}",
                    use_container_width=True
                ):
                    _record_tip_interaction(
                        storage,
                        tip.id,
                        habit_id,
                        user_id,
                        "helpful"
                    )


def render_tip_section(
    storage: Any,
    habit_id: str,
    user_id: str = "",
    limit: int = 2
) -> None:
    """
    Render environment tips section.

    Args:
        storage: Storage instance
        habit_id: Habit ID
        user_id: User ID
        limit: Number of tips to show
    """
    # Get personalized tips
    engine = TipEngine(storage, user_id)
    tips = engine.get_personalized_tips(habit_id, limit=limit)

    if not tips:
        return

    st.divider()
    st.markdown("**🌍 Optimize Your Environment**")
    st.caption("Small changes to your environment can make habits easier!")

    # Show tips
    for tip in tips:
        render_tip_card(storage, tip, habit_id, user_id)

    # Show more tips button
    if len(tips) >= limit:
        if st.button("📋 View More Tips"):
            st.session_state[f"show_all_tips_{habit_id}"] = True


def render_all_tips(
    storage: Any,
    habit_id: str,
    user_id: str = ""
) -> None:
    """
    Render all available tips.

    Args:
        storage: Storage instance
        habit_id: Habit ID
        user_id: User ID
    """
    st.markdown("**📚 All Environment Tips**")

    # Get all tips
    engine = TipEngine(storage, user_id)

    # Group by category
    categories = [
        TipCategory.CUE_DESIGN,
        TipCategory.FRICTION_REDUCTION,
        TipCategory.IMPLEMENTATION,
        TipCategory.SOCIAL,
        TipCategory.PHYSICAL,
        TipCategory.DIGITAL,
    ]

    for category in categories:
        tips = engine.get_tips_by_category(category, limit=10)
        if tips:
            with st.expander(
                f"{CATEGORY_EMOJIS[category]} {category.value.replace('_', ' ').title()}"
            ):
                for tip in tips:
                    render_tip_card(storage, tip, habit_id, user_id)


def _record_tip_interaction(
    storage: Any,
    tip_id: str,
    habit_id: str,
    user_id: str,
    action: str
) -> None:
    """
    Record tip interaction.

    Args:
        storage: Storage instance
        tip_id: Tip ID
        habit_id: Habit ID
        user_id: User ID
        action: Action type
    """
    engine = TipEngine(storage, user_id)
    engine.record_tip_interaction(
        tip_id=tip_id,
        habit_id=habit_id,
        action=action
    )

    # Show feedback
    if action == "tried":
        st.success("✅ Great! You tried this tip!")
    elif action == "helpful":
        st.success("👍 Thanks for the feedback!")

    st.rerun()


def render_tip_stats(
    storage: Any,
    user_id: str
) -> None:
    """
    Render tip interaction statistics.

    Args:
        storage: Storage instance
        user_id: User ID
    """
    stats = storage.get_tip_stats(user_id)

    if stats["viewed"] == 0:
        return

    st.markdown("**📊 Tip Statistics**")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Tips Viewed", stats["viewed"])
    with col2:
        st.metric("Tips Tried", stats["tried"])
    with col3:
        st.metric("Found Helpful", stats["helpful"])


__all__ = [
    "render_tip_card",
    "render_tip_section",
    "render_all_tips",
    "render_tip_stats",
]
