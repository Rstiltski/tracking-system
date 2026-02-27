"""
Habit Template Browser - UI for browsing and applying templates.

Provides UI components for:
- Browsing templates by category
- Searching templates
- Template preview
- One-click template application

Usage:
    from tracking_app.components.template_browser import render_template_browser
    
    render_template_browser(storage, user_id)
"""
import streamlit as st
from typing import Dict, Optional, Any, List, Callable

from brain.models.habit_template import (
    HabitTemplate,
    TemplateCategory,
    TemplateDifficulty,
    DEFAULT_TEMPLATES,
)
from brain.behavioral.template_manager import TemplateManager


# Category emojis
CATEGORY_EMOJIS = {
    TemplateCategory.MORNING: "🌅",
    TemplateCategory.EVENING: "🌙",
    TemplateCategory.PRODUCTIVITY: "📊",
    TemplateCategory.HEALTH: "❤️",
    TemplateCategory.FITNESS: "💪",
    TemplateCategory.MENTAL: "🧘",
    TemplateCategory.LEARNING: "📚",
    TemplateCategory.NUTRITION: "🍎",
    TemplateCategory.SOCIAL: "👥",
    TemplateCategory.CUSTOM: "📋",
}

# Difficulty info
DIFFICULTY_INFO = {
    TemplateDifficulty.BEGINNER: {
        "emoji": "🌱",
        "label": "Beginner",
        "description": "1-3 habits, < 10 min",
    },
    TemplateDifficulty.INTERMEDIATE: {
        "emoji": "🌿",
        "label": "Intermediate",
        "description": "3-5 habits, < 20 min",
    },
    TemplateDifficulty.ADVANCED: {
        "emoji": "🌳",
        "label": "Advanced",
        "description": "5+ habits, < 30 min",
    },
}


def render_template_browser(
    storage: Any,
    user_id: str = "",
    on_template_applied: Optional[Callable] = None
) -> None:
    """
    Render the template browser.

    Args:
        storage: Storage instance
        user_id: User ID
        on_template_applied: Optional callback when template is applied
    """
    # Initialize manager
    manager = TemplateManager(storage, user_id)

    st.title("📋 Habit Templates")
    st.markdown("Start with pre-built habit collections!")

    # Search and filter
    col_search, col_category, col_difficulty = st.columns([2, 1, 1])

    with col_search:
        search_query = st.text_input(
            "Search templates",
            placeholder="Search by name, tag, or description..."
        )

    with col_category:
        category_filter = st.selectbox(
            "Category",
            options=["All"] + [c.value for c in TemplateCategory],
            format_func=lambda x: f"{CATEGORY_EMOJIS.get(TemplateCategory(x), '📋')} {x.title()}" if x != "All" else "All Categories"
        )

    with col_difficulty:
        difficulty_filter = st.selectbox(
            "Difficulty",
            options=["All"] + [d.value for d in TemplateDifficulty],
            format_func=lambda x: DIFFICULTY_INFO.get(TemplateDifficulty(x), {}).get("label", x) if x != "All" else "All Levels"
        )

    # Get templates
    templates = manager.get_all_templates()

    # Apply filters
    if search_query:
        templates = manager.search_templates(search_query)

    if category_filter != "All":
        templates = [
            t for t in templates
            if t.category.value == category_filter
        ]

    if difficulty_filter != "All":
        templates = [
            t for t in templates
            if t.difficulty.value == difficulty_filter
        ]

    st.divider()

    # Display templates
    if not templates:
        st.info("No templates found. Try adjusting your filters!")
        return

    # Display as cards
    for template in templates:
        _render_template_card(manager, template, on_template_applied)


def _render_template_card(
    manager: TemplateManager,
    template: HabitTemplate,
    on_template_applied: Optional[Callable] = None
) -> None:
    """
    Render a single template card.

    Args:
        manager: TemplateManager instance
        template: Template to display
        on_template_applied: Optional callback
    """
    category_emoji = CATEGORY_EMOJIS.get(
        template.category,
        CATEGORY_EMOJIS[TemplateCategory.CUSTOM]
    )

    difficulty_info = DIFFICULTY_INFO.get(
        template.difficulty,
        DIFFICULTY_INFO[TemplateDifficulty.BEGINNER]
    )

    with st.container():
        # Header
        col1, col2 = st.columns([4, 1])

        with col1:
            st.markdown(
                f"**{category_emoji} {template.name}**"
            )
            st.caption(template.description)

            # Tags
            if template.tags:
                tags_str = " • ".join(template.tags[:5])
                st.caption(f"🏷️ {tags_str}")

        with col2:
            # Apply button
            if st.button(
                "Use Template",
                key=f"apply_{template.id}",
                type="primary",
                use_container_width=True
            ):
                _apply_template(manager, template, on_template_applied)

        # Meta info
        col_meta1, col_meta2, col_meta3 = st.columns(3)

        with col_meta1:
            st.caption(
                f"{difficulty_info['emoji']} **{difficulty_info['label']}**"
            )
            st.caption(difficulty_info["description"])

        with col_meta2:
            st.caption(f"📝 **{template.get_habit_count()}** habits")

        with col_meta3:
            st.caption(f"⏱️ **{template.total_duration}** min")

        # Preview habits
        with st.expander(f"👁️ Preview {template.get_habit_count()} habits"):
            for i, habit in enumerate(template.habits, 1):
                st.markdown(
                    f"**{i}. {habit.icon} {habit.name}**"
                )
                if habit.description:
                    st.caption(habit.description)
                st.caption(f"⏱️ {habit.duration_minutes} min")
                if i < len(template.habits):
                    st.divider()

        st.divider()


def _apply_template(
    manager: TemplateManager,
    template: HabitTemplate,
    on_template_applied: Optional[Callable] = None
) -> None:
    """
    Apply a template.

    Args:
        manager: TemplateManager instance
        template: Template to apply
        on_template_applied: Optional callback
    """
    # Show confirmation
    st.session_state[f"confirm_template_{template.id}"] = True

    if st.session_state.get(f"confirm_template_{template.id}", False):
        with st.spinner(f"Applying '{template.name}'..."):
            result = manager.apply_template(template.id)

            if result["success"]:
                st.success(
                    f"✅ Created {result['habits_created']} habits from "
                    f"'{template.name}'!"
                )

                if on_template_applied:
                    on_template_applied(result)

                st.session_state[f"confirm_template_{template.id}"] = False
                st.rerun()
            else:
                st.error(f"❌ Failed: {result.get('error', 'Unknown error')}")
                st.session_state[f"confirm_template_{template.id}"] = False


def render_quick_templates(
    storage: Any,
    user_id: str = "",
    limit: int = 3
) -> None:
    """
    Render quick template suggestions.

    Args:
        storage: Storage instance
        user_id: User ID
        limit: Maximum templates to show
    """
    manager = TemplateManager(storage, user_id)

    # Get recommended templates
    recommendations = manager.get_recommended_templates(limit=limit)

    if not recommendations:
        return

    st.markdown("**💡 Recommended Templates for You:**")

    cols = st.columns(min(len(recommendations), 3))

    for i, template in enumerate(recommendations):
        with cols[i % 3]:
            category_emoji = CATEGORY_EMOJIS.get(
                template.category,
                "📋"
            )

            st.markdown(f"**{category_emoji} {template.name}**")
            st.caption(template.description)
            st.caption(f"⏱️ {template.total_duration} min")

            if st.button(
                "Use",
                key=f"quick_{template.id}",
                use_container_width=True
            ):
                _apply_template(manager, template)


def render_template_stats(storage: Any, user_id: str = "") -> None:
    """
    Render template usage statistics.

    Args:
        storage: Storage instance
        user_id: User ID
    """
    # This would query database for actual stats
    # For now, show placeholder
    st.caption("📊 Templates help you start faster!")
    st.caption("Users who start with templates are 3x more likely to stick with their habits.")


__all__ = [
    "render_template_browser",
    "render_quick_templates",
    "render_template_stats",
]
