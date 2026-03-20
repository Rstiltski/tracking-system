"""
Add habit form component for the Habits page.

Renders forms for creating new habits.
"""

import streamlit as st
from datetime import datetime
from typing import Optional

from .constants import HABIT_ICONS

# Import achievement tracker
try:
    from brain.behavioral.achievement_tracker import AchievementTracker
    ACHIEVEMENTS_AVAILABLE = True
except ImportError:
    ACHIEVEMENTS_AVAILABLE = False


def render_add_habit_form():
    """
    Render form to add a new habit - SIMPLIFIED.
    
    Displays a form with:
    - Habit name (required)
    - Description (optional)
    - Icon selection
    - Frequency selection
    
    Creates habit with default color, type, and category.
    """
    st.subheader("➕ Add New Habit")

    storage = st.session_state.storage
    habits = storage.get_habits()
    existing_names = {h.name.lower() for h in habits}

    with st.form("add_habit_form", clear_on_submit=True):
        name = st.text_input("Habit Name", placeholder="e.g., Morning Exercise")
        description = st.text_area("Description (optional)", placeholder="Why is this habit important?")
        
        col1, col2 = st.columns(2)
        
        with col1:
            icon = st.selectbox("Icon", HABIT_ICONS, index=0)
        
        with col2:
            frequency = st.selectbox(
                "Frequency",
                ["daily", "weekly"],
                help="How often do you want to track this habit?"
            )

        submitted = st.form_submit_button("Add Habit", use_container_width=True, type="primary")

        if submitted and name:
            # Validate: Check for duplicate names
            if name.lower() in existing_names:
                st.error(f"❌ A habit with the name '{name}' already exists. Please choose a different name.")
            else:
                try:
                    # Use defaults for color, type, category
                    habit = storage.create_habit(
                        name=name,
                        description=description,
                        frequency=frequency,
                        icon=icon,
                        color="#6366f1",  # Default indigo
                        habit_type="boolean",  # Simple yes/no
                        target_value=0.0,
                        target_type="at_least",
                        category="general"  # Default category
                    )
                    
                    # Check and unlock achievements after creating habit
                    if ACHIEVEMENTS_AVAILABLE:
                        try:
                            tracker = AchievementTracker(storage, "default")
                            newly_unlocked = tracker.check_achievements()
                            if newly_unlocked:
                                for achievement in newly_unlocked:
                                    st.toast(f"🏆 Unlocked: {achievement.name}! +{achievement.xp_reward} XP", icon="🎉")
                        except Exception:
                            pass  # Silently handle achievement check errors
                    
                    st.success(f"✅ Created habit: {habit.name}")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Failed to create habit: {str(e)}")


def render_add_habit_form_inline():
    """
    Render inline form to add a new habit - SIMPLIFIED (for spreadsheet view).
    
    Displays a form with:
    - Habit name (required)
    - Description (optional)
    - Icon selection
    - Frequency selection
    - Add/Cancel buttons
    
    Creates habit with default color, type, and category.
    """
    st.markdown("### ➕ Add New Habit")

    storage = st.session_state.storage
    habits = storage.get_habits()
    existing_names = {h.name.lower() for h in habits}

    with st.form("add_habit_form_inline", clear_on_submit=True):
        name = st.text_input("Habit Name", placeholder="e.g., Morning Exercise")
        description = st.text_area("Description (optional)", placeholder="Why is this habit important?")
        
        col1, col2 = st.columns(2)
        
        with col1:
            icon = st.selectbox("Icon", HABIT_ICONS, index=0)
        
        with col2:
            frequency = st.selectbox(
                "Frequency",
                ["daily", "weekly"],
                help="How often do you want to track this habit?"
            )

        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            submitted = st.form_submit_button("Add Habit", type="primary", use_container_width=True)
        with col_btn2:
            cancelled = st.form_submit_button("Cancel", use_container_width=True)

        if cancelled:
            st.session_state.show_add_habit_form = False
            st.rerun()

        if submitted and name:
            # Validate: Check for duplicate names
            if name.lower() in existing_names:
                st.error(f"❌ A habit with the name '{name}' already exists. Please choose a different name.")
            else:
                try:
                    # Use defaults for color, type, category
                    habit = storage.create_habit(
                        name=name,
                        description=description,
                        frequency=frequency,
                        icon=icon,
                        color="#6366f1",  # Default indigo
                        habit_type="boolean",  # Simple yes/no
                        target_value=0.0,
                        target_type="at_least",
                        category="general"  # Default category
                    )
                    
                    # Check and unlock achievements after creating habit
                    if ACHIEVEMENTS_AVAILABLE:
                        try:
                            tracker = AchievementTracker(storage)
                            newly_unlocked = tracker.check_achievements()
                            if newly_unlocked:
                                for achievement in newly_unlocked:
                                    st.toast(f"🏆 Unlocked: {achievement.name}! +{achievement.xp_reward} XP", icon="🎉")
                        except Exception:
                            pass  # Silently handle achievement check errors
                    
                    st.session_state.show_add_habit_form = False
                    # Update timestamp to refresh all tabs
                    st.session_state.matrix_last_update = datetime.now().isoformat()
                    st.success(f"✅ Created habit: {habit.name}")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Failed to create habit: {str(e)}")