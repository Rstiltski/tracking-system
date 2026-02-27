"""
Achievement Card - Display achievements and progress.

Provides UI components for:
- Achievement showcase
- Progress tracking
- Unlock notifications

Usage:
    from tracking_app.components.achievement_card import render_achievement_card
    
    render_achievement_card(storage, user_id)
"""
import streamlit as st
from typing import Dict, Optional, Any, List

from brain.models.achievement import (
    Achievement,
    AchievementCategory,
    AchievementTier,
    DEFAULT_ACHIEVEMENTS,
)
from brain.behavioral.achievement_tracker import AchievementTracker


# Tier colors
TIER_COLORS = {
    AchievementTier.BRONZE: "#CD7F32",
    AchievementTier.SILVER: "#C0C0C0",
    AchievementTier.GOLD: "#FFD700",
    AchievementTier.PLATINUM: "#E5E4E2",
    AchievementTier.DIAMOND: "#B9F2FF",
}

# Tier emojis
TIER_EMOJIS = {
    AchievementTier.BRONZE: "🥉",
    AchievementTier.SILVER: "🥈",
    AchievementTier.GOLD: "🥇",
    AchievementTier.PLATINUM: "💎",
    AchievementTier.DIAMOND: "💠",
}


def render_achievement_card(
    storage: Any,
    user_id: str = ""
) -> None:
    """
    Render achievement showcase.

    Args:
        storage: Storage instance
        user_id: User ID
    """
    # Initialize tracker
    tracker = AchievementTracker(storage, user_id)

    st.markdown("## 🏆 Achievements")

    # Get achievements
    unlocked = tracker.get_unlocked_achievements()
    locked = tracker.get_locked_achievements()

    # Summary stats
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            label="Unlocked",
            value=f"{len(unlocked)}/{len(unlocked) + len(locked)}"
        )

    with col2:
        multiplier = tracker.get_xp_multiplier()
        st.metric(
            label="XP Multiplier",
            value=f"{multiplier:.2f}x"
        )

    with col3:
        total_xp = sum(ua.xp_awarded for ua in unlocked)
        st.metric(
            label="XP from Achievements",
            value=total_xp
        )

    st.divider()

    # Show unlocked achievements
    if unlocked:
        st.markdown("**✅ Unlocked Achievements**")
        cols = st.columns(min(len(unlocked), 3))

        for i, ua in enumerate(unlocked):
            achievement = next(
                (a for a in DEFAULT_ACHIEVEMENTS if a.id == ua.achievement_id),
                None
            )

            if achievement:
                with cols[i % 3]:
                    _render_unlocked_achievement(achievement, ua)

        st.divider()

    # Show locked achievements
    if locked:
        st.markdown("**🔒 Locked Achievements**")

        # Show in expandable sections by category
        categories = {}
        for achievement in locked:
            cat = achievement.category.value
            if cat not in categories:
                categories[cat] = []
            categories[cat].append(achievement)

        for category, achievements in categories.items():
            with st.expander(
                f"{_get_category_emoji(category)} {category.title()} "
                f"({len(achievements)})"
            ):
                for achievement in achievements:
                    _render_locked_achievement(tracker, achievement)


def _render_unlocked_achievement(
    achievement: Achievement,
    user_achievement: Any
) -> None:
    """
    Render an unlocked achievement.

    Args:
        achievement: Achievement definition
        user_achievement: User's achievement record
    """
    tier_emoji = TIER_EMOJIS.get(
        achievement.tier,
        TIER_EMOJIS[AchievementTier.BRONZE]
    )

    st.markdown(
        f"""
        <div style="
            padding: 1rem;
            border-radius: 0.5rem;
            border: 2px solid {TIER_COLORS.get(achievement.tier, '#CD7F32')};
            background: rgba(255,255,255,0.05);
            text-align: center;
        ">
            <div style="font-size: 2rem;">
                {tier_emoji} {achievement.icon}
            </div>
            <div style="font-weight: bold; margin: 0.5rem 0;">
                {achievement.name}
            </div>
            <div style="font-size: 0.8rem; color: gray;">
                {achievement.description}
            </div>
            <div style="font-size: 0.8rem; color: gray; margin-top: 0.5rem;">
                +{user_achievement.xp_awarded} XP
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )


def _render_locked_achievement(
    tracker: AchievementTracker,
    achievement: Achievement
) -> None:
    """
    Render a locked achievement with progress.

    Args:
        tracker: AchievementTracker instance
        achievement: Achievement definition
    """
    tier_emoji = TIER_EMOJIS.get(
        achievement.tier,
        TIER_EMOJIS[AchievementTier.BRONZE]
    )

    # Get progress
    progress = tracker.get_progress_toward_achievement(achievement)

    with st.container():
        col1, col2 = st.columns([3, 1])

        with col1:
            st.markdown(f"**{tier_emoji} {achievement.name}**")
            st.caption(achievement.description)
            st.caption(f"Requirement: {achievement.requirement}")

            # Progress bar
            st.progress(progress["percentage"] / 100)
            st.caption(
                f"Progress: {progress['current']}/{progress['required']} "
                f"({progress['percentage']:.0f}%)"
            )

        with col2:
            st.markdown(f"<div style='font-size: 2rem; text-align: center;'>🔒</div>", unsafe_allow_html=True)


def render_achievement_notification(
    newly_unlocked: List[Achievement]
) -> None:
    """
    Render achievement unlock notification.

    Args:
        newly_unlocked: List of newly unlocked achievements
    """
    if not newly_unlocked:
        return

    for achievement in newly_unlocked:
        tier_emoji = TIER_EMOJIS.get(
            achievement.tier,
            TIER_EMOJIS[AchievementTier.BRONZE]
        )

        st.success(
            f"""
            🎉 **Achievement Unlocked!** {tier_emoji}

            **{achievement.name}** - {achievement.description}

            +{achievement.xp_reward} XP
            """,
            icon="🏆"
        )


def render_achievement_progress(
    storage: Any,
    user_id: str = ""
) -> None:
    """
    Render achievement progress summary.

    Args:
        storage: Storage instance
        user_id: User ID
    """
    tracker = AchievementTracker(storage, user_id)

    st.markdown("### 📊 Achievement Progress")

    # Get progress for all locked achievements
    locked = tracker.get_locked_achievements()

    if not locked:
        st.success("🎉 All achievements unlocked!")
        return

    # Show progress for key achievements
    key_achievements = [
        a for a in locked
        if a.tier in [AchievementTier.BRONZE, AchievementTier.SILVER]
    ][:5]

    for achievement in key_achievements:
        progress = tracker.get_progress_toward_achievement(achievement)

        st.markdown(f"**{achievement.name}**")
        st.progress(progress["percentage"] / 100)
        st.caption(
            f"{progress['current']}/{progress['required']} "
            f"({progress['percentage']:.0f}% complete)"
        )


def _get_category_emoji(category: str) -> str:
    """Get emoji for achievement category."""
    emojis = {
        "streak": "🔥",
        "score": "📈",
        "comeback": "🦅",
        "consistency": "✨",
        "mastery": "🧘",
        "special": "🌟",
    }
    return emojis.get(category, "🏆")


__all__ = [
    "render_achievement_card",
    "render_achievement_notification",
    "render_achievement_progress",
]
