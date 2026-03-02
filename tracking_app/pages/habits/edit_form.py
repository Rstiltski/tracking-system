"""
Edit habit form component for the Habits page.

Renders forms for editing existing habits.
"""

import streamlit as st
from datetime import datetime

from .constants import HABIT_ICONS


def render_edit_habit_form(habit):
    """
    Render form to edit an existing habit.
    
    Displays a form with:
    - Habit name (required)
    - Description (optional)
    - Icon selection
    - Frequency selection
    - Color picker
    - Archive/Unarchive option
    - Save/Cancel buttons
    
    Args:
        habit: The Habit object to edit
    """
    st.subheader(f"✏️ Edit Habit: {habit.name}")
    
    storage = st.session_state.storage
    habits = storage.get_habits()
    existing_names = {h.name.lower() for h in habits if h.id != habit.id}
    
    with st.form("edit_habit_form"):
        name = st.text_input("Habit Name", value=habit.name)
        description = st.text_area("Description (optional)", value=habit.description or "")
        
        col1, col2 = st.columns(2)
        
        with col1:
            # Find current icon index
            current_icon_index = HABIT_ICONS.index(habit.icon) if habit.icon in HABIT_ICONS else 0
            icon = st.selectbox("Icon", HABIT_ICONS, index=current_icon_index)
        
        with col2:
            frequency = st.selectbox(
                "Frequency",
                ["daily", "weekly"],
                index=0 if habit.frequency == "daily" else 1,
                help="How often do you want to track this habit?"
            )
        
        # Color picker
        color = st.color_picker("Color", value=habit.color or "#6366f1")
        
        # Archive option
        archive = st.checkbox("Archive this habit", value=habit.archived)
        
        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            submitted = st.form_submit_button("Save Changes", type="primary", use_container_width=True)
        with col_btn2:
            cancelled = st.form_submit_button("Cancel", use_container_width=True)
        
        if cancelled:
            st.session_state.editing_habit = None
            st.rerun()
        
        if submitted:
            # Validate: Check for duplicate names
            if name.lower() in existing_names:
                st.error(f"❌ A habit with the name '{name}' already exists. Please choose a different name.")
            elif not name.strip():
                st.error("❌ Habit name cannot be empty.")
            else:
                try:
                    # Update habit
                    habit.name = name
                    habit.description = description
                    habit.icon = icon
                    habit.frequency = frequency
                    habit.color = color
                    habit.archived = archive
                    habit.updated_at = datetime.now().isoformat()
                    
                    storage.update_habit(habit)
                    
                    st.session_state.editing_habit = None
                    st.session_state.matrix_last_update = datetime.now().isoformat()
                    
                    st.success(f"✅ Updated habit: {habit.name}")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Failed to update habit: {str(e)}")


def render_edit_habit_modal():
    """
    Render edit habit form as a modal-style component.
    
    Checks session state for 'editing_habit' to determine if the form should be shown.
    """
    if not st.session_state.get('editing_habit'):
        return None
    
    storage = st.session_state.storage
    habit = storage.get_habit_by_id(st.session_state.editing_habit)
    
    if not habit:
        st.session_state.editing_habit = None
        return None
    
    # Render the edit form
    st.divider()
    render_edit_habit_form(habit)
    return True