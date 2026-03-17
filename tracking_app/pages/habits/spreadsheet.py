"""
Spreadsheet view component for the Habits page.

Renders the interactive spreadsheet-style habit tracking matrix.
"""

import streamlit as st
import pandas as pd
from datetime import datetime, date, timedelta
import calendar
from typing import List

from tracking_app.models import Habit

from .constants import XP_PER_COMPLETION
from .helpers import (
    get_week_start,
    get_month_start,
    get_local_date,
    is_entry_completed,
    calculate_streak,
    get_level_from_xp,
)
from .navigation import render_navigation_controls


def render_enhanced_matrix_view(storage, habits: List[Habit], current_date: date):
    """
    Render an interactive spreadsheet matrix view for habit tracking using st.data_editor.
    
    Features:
    - Interactive checkboxes - click to toggle completion for any day
    - Visual distinction for weekend/today/past/future
    - Streak indicators next to habit names
    - Progress column with percentage
    - Full editing capability for all visible days
    
    Args:
        storage: Storage instance for data access
        habits: List of all habits
        current_date: Current date for period calculation
    """
    view_mode = st.session_state.habit_view_mode
    
    # Render navigation controls
    render_navigation_controls(current_date, view_mode)
    
    st.divider()
    
    # Determine date range based on view mode
    if view_mode == 'week':
        start_date = get_week_start(current_date)
        days_in_period = 7
        end_date = start_date + timedelta(days=days_in_period - 1)
    else:
        start_date = get_month_start(current_date)
        days_in_period = calendar.monthrange(current_date.year, current_date.month)[1]
        end_date = start_date + timedelta(days=days_in_period - 1)
    
    date_range = [start_date + timedelta(days=x) for x in range(days_in_period)]
    today = get_local_date()
    
    # Filter to active habits only
    active_habits = [h for h in habits if not h.archived]
    
    if not active_habits:
        st.info("No active habits. Click 'Add Habit' to create your first habit!")
        if st.button("➕ Add Habit", key="add_habit_empty", type="primary"):
            st.session_state.show_add_habit_form = True
            st.rerun()
        return

    # Build column headers with day info - short format for editor
    column_headers = []
    for d in date_range:
        day_name = d.strftime('%a')[:3]  # Abbreviated day name
        day_num = d.day
        is_weekend = d.weekday() >= 5
        is_today = d == today
        
        # Simple headers for the editor
        header = f"{day_name} {day_num}"
        column_headers.append(header)
    
    # Build data for the editable table using boolean values
    data = []
    habit_id_list = []
    
    for habit in active_habits:
        habit_id_list.append(habit.id)
        
        # Calculate streak for display
        streak = calculate_streak(storage, habit.id)
        streak_text = f" 🔥{streak}" if streak > 0 else ""
        
        # Build row data with habit name as first column
        row = {
            'Habit': f"{habit.icon} {habit.name}{streak_text}",
        }
        
        # Add day columns with boolean completion status
        for idx, d in enumerate(date_range):
            col_name = column_headers[idx]
            entry = storage.get_habit_entry(habit.id, d)
            is_complete = is_entry_completed(entry)
            is_skipped = hasattr(entry, 'skipped') and entry.skipped if entry else False
            
            # Use boolean for editable cells (skipped counts as incomplete for editing)
            row[col_name] = is_complete and not is_skipped
        
        # Calculate progress percentage
        completed = 0
        total_valid_days = 0
        for d in date_range:
            if d <= today:
                total_valid_days += 1
                entry = storage.get_habit_entry(habit.id, d)
                if is_entry_completed(entry):
                    completed += 1
        
        percentage = int((completed / total_valid_days) * 100) if total_valid_days > 0 else 0
        row['Progress'] = percentage  # Store as number for progress bar
        
        data.append(row)
    
    # Create DataFrame
    df = pd.DataFrame(data)
    
    # Configure column properties for the data editor
    column_config = {
        'Habit': st.column_config.TextColumn(
            'Habit',
            width='medium',
            disabled=True,
        ),
        'Progress': st.column_config.ProgressColumn(
            'Progress',
            width='small',
            format='%d%%',
            min_value=0,
            max_value=100,
        ),
    }
    
    # Add boolean column config for each day
    for idx, d in enumerate(date_range):
        col_name = column_headers[idx]
        is_today = d == today
        is_weekend = d.weekday() >= 5
        is_past = d < today
        is_future = d > today
        
        # Create label with visual indicators
        if is_today:
            label = f"📍 {col_name}"
        elif is_weekend:
            label = f"🌙 {col_name}"
        else:
            label = col_name
        
        column_config[col_name] = st.column_config.CheckboxColumn(
            label,
            default=False,
            width='small',
        )
    
    # Display the interactive data editor
    st.markdown("""
    <style>
    /* Style the data editor */
    .stDataFrame {
        border: 1px solid #e2e8f0;
        border-radius: 8px;
    }
    /* Instructions */
    .edit-instructions {
        background: linear-gradient(135deg, #e0e7ff 0%, #c7d2fe 100%);
        padding: 8px 16px;
        border-radius: 8px;
        margin-bottom: 12px;
        font-size: 0.9rem;
        color: #4f46e5;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown('<div class="edit-instructions">💡 Click checkboxes to mark habits complete/incomplete. Changes are saved automatically.</div>', unsafe_allow_html=True)
    
    # Use data_editor for interactive editing
    edited_df = st.data_editor(
        df,
        column_config=column_config,
        use_container_width=True,
        hide_index=True,
        height=min(600, 50 + len(active_habits) * 45),
        key=f"habit_editor_{view_mode}_{current_date.strftime('%Y%m')}"
    )
    
    # Detect and process changes
    changes_made = False
    for i, habit in enumerate(active_habits):
        for idx, d in enumerate(date_range):
            col_name = column_headers[idx]
            original_value = df.iloc[i][col_name]
            edited_value = edited_df.iloc[i][col_name]
            
            # Check if this cell was changed
            if original_value != edited_value:
                changes_made = True
                if edited_value:
                    # Mark as complete
                    storage.mark_habit_complete(habit.id, d)
                    if d == today:
                        st.session_state.user_xp = storage.add_xp(XP_PER_COMPLETION)
                        st.session_state.user_level = get_level_from_xp(st.session_state.user_xp)
                        st.toast(f"✅ {habit.name} completed! +{XP_PER_COMPLETION} XP", icon="🎉")
                else:
                    # Mark as incomplete
                    storage.unmark_habit_complete(habit.id, d)
                    if d == today:
                        st.session_state.user_xp = max(0, st.session_state.user_xp - XP_PER_COMPLETION)
                        st.session_state.user_level = get_level_from_xp(st.session_state.user_xp)
                        st.toast(f"↩️ {habit.name} unmarked", icon="↩️")
    
    # Save last update timestamp (without rerun to avoid full page refresh)
    if changes_made:
        st.session_state.matrix_last_update = datetime.now().isoformat()
        # No st.rerun() - data_editor handles UI update automatically
    
    st.divider()
    
    # Quick actions section
    st.subheader("⚡ Quick Actions")
    
    col_add, col_edit, col_fill = st.columns(3)
    
    with col_add:
        if st.button("➕ Add New Habit", key="add_habit_bottom", type="primary", use_container_width=True):
            st.session_state.show_add_habit_form = True
            st.rerun()
    
    with col_edit:
        # Quick edit dropdown for managing habits
        habit_names = {h.id: f"{h.icon} {h.name}" for h in active_habits}
        if habit_names:
            selected_habit = st.selectbox(
                "Quick Edit",
                options=list(habit_names.keys()),
                format_func=lambda x: habit_names.get(x, ""),
                key="quick_edit_select"
            )
            if selected_habit:
                if st.button("✏️ Edit Selected", key="edit_selected_btn", use_container_width=True):
                    st.session_state.editing_habit = selected_habit
                    st.rerun()
    
    with col_fill:
        # Quick fill all today's habits
        if st.button("✅ Complete All Today", key="fill_all_today", use_container_width=True):
            for habit in active_habits:
                entry = storage.get_habit_entry(habit.id, today)
                if not is_entry_completed(entry):
                    storage.mark_habit_complete(habit.id, today)
                    st.session_state.user_xp = storage.add_xp(XP_PER_COMPLETION)
            st.session_state.user_level = get_level_from_xp(st.session_state.user_xp)
            st.toast(f"🎉 All habits marked complete!", icon="🎉")
            st.rerun()


def render_matrix_view(storage, habits: List[Habit], current_date: date):
    """
    Render the spreadsheet-style habit matrix view.
    
    This is the main view for tracking habits with a grid layout.
    
    Args:
        storage: Storage instance for data access
        habits: List of all habits
        current_date: Current date for period calculation
    """
    # Render the enhanced matrix (which includes navigation controls)
    render_enhanced_matrix_view(storage, habits, current_date)