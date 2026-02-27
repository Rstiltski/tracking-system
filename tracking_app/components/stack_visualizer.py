"""
Habit Stack Visualizer - Visual component for habit stacks.

Provides UI components for:
- Stack visualization (flowchart style)
- Stack builder wizard
- Stack completion tracking

Usage:
    from tracking_app.components.stack_visualizer import render_stack_visualizer
    
    render_stack_visualizer(storage, user_id)
"""
import streamlit as st
from typing import Dict, Optional, Any, List
from datetime import date

from brain.behavioral.habit_stacking import (
    HabitStackingEngine,
    HabitStack,
    StackItem,
    AnchorCategory,
    DEFAULT_ANCHOR_PRESETS,
)


# Anchor category emojis
ANCHOR_EMOJIS = {
    AnchorCategory.MORNING: "🌅",
    AnchorCategory.TRANSIT: "🚗",
    AnchorCategory.EVENING: "🌙",
    AnchorCategory.WORK: "💼",
    AnchorCategory.MEAL: "🍽️",
    AnchorCategory.HYGIENE: "🚿",
    AnchorCategory.EXERCISE: "🏃",
    AnchorCategory.CUSTOM: "📌",
}


def render_stack_visualizer(
    storage: Any,
    user_id: str = ""
) -> None:
    """
    Render habit stack visualizer.

    Args:
        storage: Storage instance
        user_id: User ID
    """
    st.title("📦 Habit Stacking")
    st.markdown("Link habits together using BJ Fogg's method!")

    # Initialize engine
    engine = HabitStackingEngine()

    # Get user's stacks
    stacks = storage.get_habit_stacks(user_id, active_only=True)

    if not stacks:
        _render_empty_state(engine, storage, user_id)
    else:
        _render_stacks_list(engine, storage, user_id, stacks)


def _render_empty_state(
    engine: HabitStackingEngine,
    storage: Any,
    user_id: str
) -> None:
    """
    Render empty state for new users.

    Args:
        engine: HabitStackingEngine instance
        storage: Storage instance
        user_id: User ID
    """
    st.info(
        """
        **🎯 What is Habit Stacking?**
        
        Habit stacking links new habits to existing ones using the formula:
        
        > "After I [CURRENT HABIT], I will [NEW HABIT]"
        
        **Examples:**
        - After I brew coffee, I will drink a glass of water
        - After I brush my teeth, I will meditate for 1 minute
        - After I sit at my desk, I will plan my top 3 tasks
        
        Research shows stacked habits are **3x more likely** to stick!
        """
    )

    # Quick start button
    if st.button("➕ Create Your First Stack", type="primary"):
        st.session_state.show_stack_builder = True
        st.rerun()

    # Show anchor presets
    st.divider()
    st.markdown("**💡 Popular Anchors:**")

    cols = st.columns(4)
    for i, preset in enumerate(DEFAULT_ANCHOR_PRESETS[:8]):
        with cols[i % 4]:
            category_emoji = ANCHOR_EMOJIS.get(
                preset.category,
                ANCHOR_EMOJIS[AnchorCategory.CUSTOM]
            )
            st.markdown(f"**{category_emoji} {preset.name}**")
            st.caption(preset.example_trigger[:50] + "...")


def _render_stacks_list(
    engine: HabitStackingEngine,
    storage: Any,
    user_id: str,
    stacks: List[Dict[str, Any]]
) -> None:
    """
    Render list of user's stacks.

    Args:
        engine: HabitStackingEngine instance
        storage: Storage instance
        user_id: User ID
        stacks: List of stack data
    """
    # Show existing stacks
    for stack in stacks:
        _render_stack_card(storage, stack)

    st.divider()

    # Add new stack button
    col1, col2 = st.columns(2)
    with col1:
        if st.button("➕ Create New Stack", use_container_width=True):
            st.session_state.show_stack_builder = True
            st.rerun()

    with col2:
        if st.button("📊 View Analytics", use_container_width=True):
            st.session_state.show_stack_analytics = True
            st.rerun()

    # Show builder if requested
    if st.session_state.get("show_stack_builder", False):
        _render_stack_builder(engine, storage, user_id)

    # Show analytics if requested
    if st.session_state.get("show_stack_analytics", False):
        _render_stack_analytics(storage, user_id)


def _render_stack_card(
    storage: Any,
    stack: Dict[str, Any]
) -> None:
    """
    Render a single stack card.

    Args:
        storage: Storage instance
        stack: Stack data
    """
    anchor_emoji = ANCHOR_EMOJIS.get(
        AnchorCategory(stack.get('anchor_category', 'custom')),
        "📌"
    )

    with st.expander(
        f"{anchor_emoji} **{stack['name']}** - {len(stack.get('items', []))} habits",
        expanded=False
    ):
        # Show trigger
        if stack.get('trigger_description'):
            st.markdown(f"**Trigger:** {stack['trigger_description']}")

        # Show stack items
        st.markdown("**Stack:**")
        for i, item in enumerate(stack.get('items', []), 1):
            habit_name = _get_habit_name(storage, item.get('habit_id'))
            
            col1, col2 = st.columns([4, 1])
            with col1:
                st.markdown(f"**{i}.** {habit_name}")
                if item.get('tiny_description'):
                    st.caption(f"🐜 {item['tiny_description']}")
                if item.get('delay_seconds', 0) > 0:
                    st.caption(f"⏱️ Wait {item['delay_seconds']}s before starting")
            
            with col2:
                if st.button("✕", key=f"remove_item_{item['id']}"):
                    storage.remove_item_from_stack(stack['id'], item['id'])
                    st.rerun()

        # Completion tracking
        st.divider()
        col1, col2 = st.columns(2)
        with col1:
            if st.button(
                "✓ Mark Complete",
                key=f"complete_stack_{stack['id']}",
                use_container_width=True
            ):
                _record_stack_completion(storage, stack)
        with col2:
            if st.button(
                "📊 Stats",
                key=f"stats_stack_{stack['id']}",
                use_container_width=True
            ):
                st.session_state.show_stack_analytics = True
                st.rerun()


def _render_stack_builder(
    engine: HabitStackingEngine,
    storage: Any,
    user_id: str
) -> None:
    """
    Render stack builder wizard.

    Args:
        engine: HabitStackingEngine instance
        storage: Storage instance
        user_id: User ID
    """
    st.markdown("### ➕ Create New Stack")

    with st.form("stack_builder_form"):
        # Stack name
        name = st.text_input("Stack Name", placeholder="e.g., Morning Routine")

        # Anchor selection
        st.markdown("**Anchor Habit (the IF part):**")
        anchor_type = st.selectbox(
            "Choose an anchor",
            options=["preset", "custom"],
            format_func=lambda x: "📋 Preset" if x == "preset" else "✏️ Custom"
        )

        if anchor_type == "preset":
            preset_options = [
                f"{ANCHOR_EMOJIS[p.category]} {p.name}"
                for p in DEFAULT_ANCHOR_PRESETS
            ]
            selected_preset = st.selectbox("Select preset", preset_options)
            preset_idx = preset_options.index(selected_preset)
            preset = DEFAULT_ANCHOR_PRESETS[preset_idx]
            trigger_description = preset.example_trigger
            anchor_category = preset.category.value
        else:
            trigger_description = st.text_input(
                "Describe your anchor",
                placeholder="After I..."
            )
            anchor_category = st.selectbox(
                "Category",
                options=[c.value for c in AnchorCategory]
            )

        # Add habits to stack
        st.markdown("**Stacked Habits (the THEN part):**")
        habits = storage.get_habits(include_archived=False)
        habit_options = {f"{h.icon} {h.name}": h.id for h in habits}

        selected_habits = st.multiselect(
            "Select habits to stack",
            options=list(habit_options.keys()),
            help="Choose 2-5 habits to link together"
        )

        submitted = st.form_submit_button("Create Stack", type="primary")

        if submitted and name and selected_habits:
            # Create the stack
            stack_id = storage.create_habit_stack(
                user_id=user_id,
                name=name,
                trigger_description=trigger_description,
                anchor_category=anchor_category
            )

            # Add items to stack
            for i, habit_label in enumerate(selected_habits):
                storage.add_item_to_stack(
                    stack_id=stack_id,
                    habit_id=habit_options[habit_label],
                    position=i
                )

            st.success(f"✅ Created stack: {name}")
            st.session_state.show_stack_builder = False
            st.rerun()

        # Cancel button
        if st.form_submit_button("Cancel"):
            st.session_state.show_stack_builder = False
            st.rerun()


def _render_stack_analytics(
    storage: Any,
    user_id: str
) -> None:
    """
    Render stack analytics.

    Args:
        storage: Storage instance
        user_id: User ID
    """
    st.markdown("### 📊 Stack Analytics")

    stacks = storage.get_habit_stacks(user_id)

    if not stacks:
        st.info("No stacks to analyze")
        return

    for stack in stacks:
        stats = storage.get_stack_completion_stats(stack['id'])

        st.markdown(f"**{stack['name']}**")

        col1, col2 = st.columns(2)
        with col1:
            st.metric(
                "Total Completions",
                stats['total_completions']
            )
        with col2:
            st.metric(
                "Avg Conversion",
                f"{stats['average_conversion']:.0%}"
            )

        st.divider()


def _get_habit_name(storage: Any, habit_id: Optional[str]) -> str:
    """
    Get habit name by ID.

    Args:
        storage: Storage instance
        habit_id: Habit ID

    Returns:
        Habit name or "Unknown"
    """
    if not habit_id:
        return "Custom Step"

    habit = storage.get_habit(habit_id)
    if habit:
        return f"{habit.icon if hasattr(habit, 'icon') else '🎯'} {habit.name}"
    return "Unknown Habit"


def _record_stack_completion(
    storage: Any,
    stack: Dict[str, Any]
) -> None:
    """
    Record a stack completion.

    Args:
        storage: Storage instance
        stack: Stack data
    """
    # In a full implementation, this would track which items were completed
    # For now, we'll just record a simple completion
    item_ids = [item['id'] for item in stack.get('items', [])]

    storage.record_stack_completion(
        stack_id=stack['id'],
        completed_items=item_ids,
        completion_order=item_ids,
        conversion_rate=1.0 if item_ids else 0.0
    )

    st.success("✅ Stack completion recorded!")


__all__ = [
    "render_stack_visualizer",
]
