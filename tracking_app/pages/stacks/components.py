"""
Component render functions for the Stacks page.
"""

import streamlit as st
from typing import List, Dict, Any, Optional

from brain.behavioral.habit_stacking import (
    HabitStackingEngine, HabitStack, StackItem, AnchorPreset,
    AnchorCategory, DEFAULT_ANCHOR_PRESETS
)

from .constants import CUSTOM_ANCHOR_OPTION, DEFAULT_USER_ID
from .helpers import (
    get_category_options,
    filter_presets_by_category,
    get_anchor_options,
    get_preset_by_name,
)
from .session_state import (
    get_storage,
    get_stack_engine,
    save_stack_engine,
    get_user_xp,
    get_user_level,
)


def render_sidebar() -> None:
    """Render sidebar with navigation."""
    with st.sidebar:
        st.title("🎯 Veryfyn")
        st.caption("Personal Tracking System")
        st.divider()
        
        # User Stats
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Level", get_user_level())
        with col2:
            st.metric("XP", get_user_xp())
        
        st.divider()
        
        # Navigation
        st.subheader("📊 Tracking")
        st.page_link("pages/dashboard.py", label="🏠 Dashboard", icon="🏠")
        st.page_link("pages/habits.py", label="✅ Habits", icon="✅")
        st.page_link("pages/tasks.py", label="📋 Tasks", icon="📋")
        st.page_link("pages/finances.py", label="💰 Finances", icon="💰")
        st.page_link("pages/health.py", label="❤️ Health", icon="❤️")
        st.page_link("pages/emotional_health.py", label="🌈 Emotional Health", icon="🌈")
        st.page_link("pages/time.py", label="⏱️ Time", icon="⏱️")
        st.page_link("pages/goals.py", label="🎯 Goals", icon="🎯")
        st.page_link("pages/achievements.py", label="🏆 Achievements", icon="🏆")
        
        st.divider()
        st.page_link("pages/insights.py", label="🧠 Insights", icon="🧠")
        st.page_link("pages/stacks.py", label="📚 Stacks", icon="📚")


def render_header() -> None:
    """Render page header."""
    st.title("📚 Habit Stacks")
    st.markdown("""
    **Stack habits together using BJ Fogg's Tiny Habits methodology.**
    
    The formula: **After I [ANCHOR], I will [NEW HABIT]**
    
    By linking new habits to existing behaviors, you create automatic chains.
    """)


def render_create_stack_form() -> None:
    """Render form to create a new habit stack."""
    st.subheader("➕ Create New Stack")
    
    with st.form("create_stack_form", clear_on_submit=True):
        # Stack name
        name = st.text_input(
            "Stack Name",
            placeholder="e.g., Morning Routine, Evening Wind-down",
            help="Give your stack a memorable name"
        )
        
        # Anchor selection
        st.markdown("### Choose Your Anchor")
        st.caption("An anchor is an existing behavior that triggers your new habits")
        
        # Category filter
        categories = get_category_options()
        selected_category = st.selectbox("Filter by Category", categories)
        
        # Filter presets
        filtered_presets = filter_presets_by_category(selected_category)
        
        # Display anchor options
        anchor_options = get_anchor_options(filtered_presets, CUSTOM_ANCHOR_OPTION)
        selected_anchor = st.selectbox("Select Anchor", anchor_options)
        
        if selected_anchor == CUSTOM_ANCHOR_OPTION:
            custom_anchor = st.text_input(
                "Custom Anchor",
                placeholder="e.g., After I finish my morning coffee"
            )
            trigger = custom_anchor
            category = AnchorCategory.CUSTOM
        else:
            preset = get_preset_by_name(filtered_presets, selected_anchor)
            if preset:
                trigger = preset.example_trigger
                category = preset.category
                st.info(f"💡 {preset.description}")
            else:
                trigger = ""
                category = AnchorCategory.CUSTOM
        
        submitted = st.form_submit_button("Create Stack", type="primary")
        
        if submitted and name and trigger:
            engine = get_stack_engine()
            stack = engine.create_stack(
                user_id=DEFAULT_USER_ID,
                name=name,
                trigger=trigger,
                category=category
            )
            save_stack_engine(engine)
            st.success(f"✅ Created stack: {name}")
            st.rerun()


def render_add_habit_to_stack(stack: HabitStack) -> None:
    """Render form to add a habit to a stack."""
    storage = get_storage()
    habits = [h for h in storage.get_habits() if not h.archived]
    
    if not habits:
        st.info("Create some habits first in the Habits page.")
        return
    
    with st.expander("➕ Add Habit to Stack", expanded=False):
        # Habit selection
        habit_options = {f"{h.icon} {h.name}": h.id for h in habits}
        selected = st.selectbox("Select Habit", list(habit_options.keys()), key=f"add_habit_{stack.id}")
        habit_id = habit_options[selected]
        
        # Tiny version toggle
        is_tiny = st.checkbox("This is a 'Tiny' version (< 30 seconds)", value=True)
        
        if is_tiny:
            # Suggest tiny version
            habit = next(h for h in habits if h.id == habit_id)
            engine = get_stack_engine()
            suggested = engine.suggest_tiny_version(habit.name)
            tiny_description = st.text_input(
                "Tiny Version Description",
                value=suggested,
                help="Describe the tiny version of this habit"
            )
        else:
            tiny_description = None
        
        # Position
        position = st.number_input(
            "Position in Stack",
            min_value=0,
            max_value=len(stack.items),
            value=len(stack.items),
            help="Position 0 = first habit after the anchor"
        )
        
        if st.button("Add to Stack", key=f"add_btn_{stack.id}"):
            engine = get_stack_engine()
            try:
                engine.add_habit_to_stack(
                    stack_id=stack.id,
                    habit_id=habit_id,
                    position=position,
                    is_tiny=is_tiny,
                    tiny_description=tiny_description
                )
                save_stack_engine(engine)
                st.success("Habit added to stack!")
                st.rerun()
            except Exception as e:
                st.error(f"Error: {e}")


def render_stack_card(stack: HabitStack) -> None:
    """Render a single stack card."""
    storage = get_storage()
    engine = get_stack_engine()
    
    with st.container():
        # Stack header
        col1, col2 = st.columns([4, 1])
        
        with col1:
            st.markdown(f"### 📚 {stack.name}")
            st.caption(f"**Anchor:** {stack.trigger_description}")
        
        with col2:
            if st.button("🗑️", key=f"delete_stack_{stack.id}", help="Delete stack"):
                del engine.stacks[stack.id]
                save_stack_engine(engine)
                st.rerun()
        
        # Stack items
        if stack.items:
            st.markdown("**Chain:**")
            
            for item in sorted(stack.items, key=lambda x: x.position_index):
                habit = storage.get_habit(item.habit_id)
                if habit:
                    tiny_indicator = "🌱 " if item.is_tiny else ""
                    st.markdown(
                        f"{item.position_index + 1}. {tiny_indicator}{habit.icon} **{habit.name}**"
                    )
                    if item.is_tiny and item.tiny_version_description:
                        st.caption(f"   ↳ Tiny version: {item.tiny_version_description}")
        else:
            st.info("No habits in this stack yet. Add habits below.")
        
        # Add habit form
        render_add_habit_to_stack(stack)
        
        # Stack analytics
        if stack.items:
            analytics = engine.get_stack_analytics(stack.id)
            
            with st.expander("📊 View Analytics"):
                st.metric("Stack Depth", analytics.get('stack_depth', 0))
                st.metric("Conversion Rate", f"{analytics.get('conversion_rate', 0):.1%}")
                
                if analytics.get('weak_links'):
                    st.warning(f"⚠️ Weak links at positions: {analytics['weak_links']}")
        
        st.divider()


def render_stacks_list() -> None:
    """Render all user stacks."""
    st.subheader("📋 Your Stacks")
    
    engine = get_stack_engine()
    stacks = list(engine.stacks.values())
    
    if not stacks:
        st.info("""
        No stacks yet. Create your first stack above!
        
        **Tip:** Start with a simple stack tied to a daily anchor like 
        "After I brush my teeth" or "After I pour my coffee".
        """)
        return
    
    for stack in stacks:
        render_stack_card(stack)


def render_tips() -> None:
    """Render habit stacking tips."""
    with st.expander("💡 Tips for Effective Habit Stacking"):
        st.markdown("""
        ### The Tiny Habits Formula
        
        **After I [ANCHOR], I will [NEW HABIT]**
        
        ### Key Principles
        
        1. **Start Tiny**: Make the new habit take < 30 seconds
           - Instead of "meditate 20 minutes", try "take 3 deep breaths"
           - Instead of "exercise for 30 minutes", try "do 2 pushups"
        
        2. **Choose Reliable Anchors**: Pick behaviors you do automatically
           - Brushing teeth, pouring coffee, getting into bed
        
        3. **One at a Time**: Add habits one at a time until automatic
        
        4. **Chain Formation**: Once Habit A is automatic, add Habit B
        
        ### Example Stacks
        
        **Morning Stack:**
        - After I brew coffee...
        - → I will drink a glass of water
        - → I will take my vitamins
        - → I will do 2 pushups
        
        **Evening Stack:**
        - After I put on pajamas...
        - → I will floss one tooth
        - → I will read one page
        - → I will take 3 deep breaths
        
        ### Based on BJ Fogg's Research
        
        > "The key to habit formation isn't willpower—it's design."
        > — BJ Fogg, *Tiny Habits*
        """)