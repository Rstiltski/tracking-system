"""
Card view component for the Habits page.

Renders individual habit cards with scores, streaks, and actions.
"""

import streamlit as st
from datetime import date, datetime
from typing import List

from tracking_app.models import Habit
from tracking_app.components.burnout_card import render_burnout_risk_card, is_warning_dismissed
from tracking_app.components.difficulty_widget import render_difficulty_widget
from tracking_app.components.relapse_plan_wizard import render_plan_wizard
from tracking_app.components.srbai_survey import render_automaticity_badge, render_survey_prompt, render_srbai_survey
from tracking_app.components.tip_card import render_tip_section, render_all_tips
from tracking_app.components.suggestion_card import render_suggestions_section, render_all_suggestions
from tracking_app.components.timing_indicator import render_timing_indicator
from tracking_app.components.momentum_counter import (
    update_habit_momentum,
    get_habit_momentum,
    render_momentum_indicator
)

from .constants import XP_PER_COMPLETION
from .helpers import (
    get_local_date,
    is_entry_completed,
    calculate_streak,
    get_completion_rate,
    calculate_habit_score,
    get_score_category,
    get_trend_indicator,
    check_streak_break_yesterday,
    get_level_from_xp,
)
from .session_state import use_streak_freeze_for_habit


def render_habit_card(habit: Habit, storage, today: date):
    """
    Render a single habit card with score, streak, and actions.

    Displays:
    - Habit icon and name
    - Habit Score (0-100%) with category badge and trend
    - Current streak
    - Streak freeze option for broken streaks
    - Burnout risk indicator with interventions
    - Completion actions (complete/edit/delete)
    - Accessibility: Text labels for colorblind users
    
    Args:
        habit: The Habit object to render
        storage: Storage instance for data access
        today: Current date
    """
    entry = storage.get_habit_entry(habit.id, today)
    is_complete = is_entry_completed(entry)
    streak = calculate_streak(storage, habit.id)
    completion_rate = get_completion_rate(storage, habit.id)
    
    # Get momentum tracking (Task 11.1.8: 4-Day Momentum)
    momentum = get_habit_momentum(habit.id)

    # Calculate habit score using exponential smoothing
    habit_score = calculate_habit_score(storage, habit.id)
    score_category = get_score_category(habit_score.value)
    trend_indicator = get_trend_indicator(habit_score.trend)

    # Calculate burnout risk
    from brain.behavioral.burnout_detection import BurnoutDetector
    detector = BurnoutDetector(storage, habit.id)
    burnout_risk = detector.calculate_risk()
    
    # Save the risk assessment
    detector.save_risk_assessment(burnout_risk)

    # Check if streak was broken yesterday and can be frozen
    can_use_freeze = check_streak_break_yesterday(storage, habit.id)
    streak_freeze = st.session_state.streak_freeze

    # Check if burnout warning is dismissed
    warning_dismissed = is_warning_dismissed(habit.id, burnout_risk.assessment_date)
    
    with st.container():
        # Main row with habit info
        col1, col2, col3, col4 = st.columns([1, 4, 2, 2])
        
        with col1:
            # Color indicator with icon
            st.markdown(
                f"""
                <div style="
                    width: 40px;
                    height: 40px;
                    background-color: {habit.color};
                    border-radius: 50%;
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 20px;
                ">{habit.icon}</div>
                """,
                unsafe_allow_html=True
            )
        
        with col2:
            # Name and description
            status = "✅" if is_complete else "⬜"
            st.markdown(f"### {status} {habit.name}")
            if habit.description:
                st.caption(habit.description)

            # Show streak freeze warning if streak was broken yesterday
            if can_use_freeze and streak_freeze.is_available:
                st.warning("⚠️ Streak broken yesterday! Use a freeze to save it.")

            # Show automaticity badge if survey taken
            render_automaticity_badge(storage, habit.id, show_history=False)

            # Show timing indicator
            render_timing_indicator(storage, habit.id, habit.name)

            # Show survey prompt if eligible
            render_survey_prompt(storage, habit.id, habit.name)

            # Show survey form if requested
            if st.session_state.get(f"show_survey_{habit.id}", False):
                render_srbai_survey(storage, habit.id, st.session_state.get('user_id', ''))
                if st.button("Close Survey"):
                    st.session_state[f"show_survey_{habit.id}"] = False
                    st.rerun()
        
        with col3:
            # Habit Score with category badge and trend
            score_percentage = habit_score.percentage
            st.markdown(
                f"""
                <div style="
                    padding: 0.5rem;
                    border-radius: 0.5rem;
                    border-left: 4px solid {score_category['color']};
                    background: rgba(255,255,255,0.05);
                    margin-bottom: 0.5rem;
                ">
                    <div style="font-size: 1.3rem; font-weight: bold;">
                        {score_category['emoji']} {score_percentage}%
                        <span style="font-size: 0.9rem; color: {trend_indicator['color']};">
                            {trend_indicator['icon']}
                        </span>
                    </div>
                    <div style="font-size: 0.75rem; color: gray;">
                        {score_category['label']} · {trend_indicator['label']}
                    </div>
                </div>
                """,
                unsafe_allow_html=True
            )
            # Streak below score
            st.caption(f"🔥 {streak} day streak · {completion_rate:.0f}% (30d)")
            
            # Show momentum indicator (compact view) - Task 11.1.8
            if momentum.current_day > 0:
                render_momentum_indicator(momentum, show_message=False, compact=True)
        
        with col4:
            # Actions
            col_a, col_b, col_c = st.columns(3)

            with col_a:
                if is_complete:
                    if st.button("↩️", key=f"uncomplete_{habit.id}", help="Mark incomplete"):
                        storage.unmark_habit_complete(habit.id, today)
                        # Deduct XP when unmarking (prevent XP farming)
                        st.session_state.user_xp = max(0, st.session_state.user_xp - XP_PER_COMPLETION)
                        st.session_state.user_level = get_level_from_xp(st.session_state.user_xp)
                        st.rerun()
                else:
                    if st.button("✓", key=f"complete_{habit.id}", help="Mark complete"):
                        storage.mark_habit_complete(habit.id, today)
                        st.session_state.user_xp = storage.add_xp(XP_PER_COMPLETION)
                        st.session_state.user_level = get_level_from_xp(st.session_state.user_xp)
                        
                        # Update momentum tracking (Task 11.1.8: 4-Day Momentum)
                        momentum = update_habit_momentum(habit.id, today)
                        if momentum.current_day == 4:
                            st.balloons()
                            st.success("🎉 Day 4 MOMENTUM ACHIEVED! You've crossed the threshold!")
                        
                        st.rerun()

            with col_b:
                if st.button("✏️", key=f"edit_{habit.id}", help="Edit habit"):
                    st.session_state.editing_habit = habit.id

            with col_c:
                # Delete button with confirmation dialog
                delete_confirm_key = f"confirm_delete_{habit.id}"
                if delete_confirm_key not in st.session_state:
                    st.session_state[delete_confirm_key] = False
                
                if st.session_state[delete_confirm_key]:
                    # Show confirmation buttons
                    col_del1, col_del2 = st.columns(2)
                    with col_del1:
                        if st.button("⚠️ Confirm", key=f"confirm_del_yes_{habit.id}", help="Permanently delete"):
                            storage.delete_habit(habit.id)
                            st.session_state[delete_confirm_key] = False
                            st.session_state.matrix_last_update = datetime.now().isoformat()
                            st.success(f"🗑️ Deleted '{habit.name}'")
                            st.rerun()
                    with col_del2:
                        if st.button("Cancel", key=f"confirm_del_no_{habit.id}"):
                            st.session_state[delete_confirm_key] = False
                            st.rerun()
                else:
                    if st.button("🗑️", key=f"delete_{habit.id}", help="Delete habit"):
                        st.session_state[delete_confirm_key] = True
                        st.rerun()

        # Streak freeze action row (if applicable)
        if can_use_freeze and streak_freeze.is_available:
            if st.button(f"❄️ Use Streak Freeze ({streak_freeze.count} available)",
                        key=f"freeze_{habit.id}",
                        help="Preserve your streak by using a freeze",
                        use_container_width=True):
                if use_streak_freeze_for_habit(habit.id):
                    st.success("❄️ Streak frozen! Your streak is preserved.")
                    st.rerun()
                else:
                    st.error("Could not use freeze. Please try again.")

        # Burnout risk card (if moderate or higher and not dismissed)
        if not warning_dismissed and burnout_risk.risk_level.value in ["moderate", "high", "critical"]:
            st.divider()
            dismissed = render_burnout_risk_card(burnout_risk, storage, habit.id)
            if dismissed:
                st.rerun()

        # Difficulty rating widget
        st.divider()
        render_difficulty_widget(
            storage,
            habit.id,
            habit.name,
            habit.target_value if hasattr(habit, 'target_value') else 1.0,
            show_history=False
        )

        # Relapse prevention plans
        st.divider()
        render_plan_wizard(storage, habit.id, habit.name)

        # Environment tips section
        st.divider()
        render_tip_section(storage, habit.id, st.session_state.get('user_id', ''))

        # Show all tips if requested
        if st.session_state.get(f"show_all_tips_{habit.id}", False):
            render_all_tips(storage, habit.id, st.session_state.get('user_id', ''))
            if st.button("Close Tips"):
                st.session_state[f"show_all_tips_{habit.id}"] = False
                st.rerun()

        # Smart suggestions section
        st.divider()
        render_suggestions_section(storage, st.session_state.get('user_id', ''), limit=2, key_prefix=f"habit_{habit.id}")

        # Show all suggestions if requested
        if st.session_state.get("show_all_suggestions", False):
            render_all_suggestions(storage, st.session_state.get('user_id', ''))
            if st.button("Close Suggestions"):
                st.session_state.show_all_suggestions = False
                st.rerun()

        st.divider()


def render_habits_list():
    """
    Render the main habits list with tabs and filtering.
    
    Includes tabs for:
    - Spreadsheet Grid (main view)
    - Card View (individual habit cards)
    - Habit Stacks
    - Today's Progress
    - Archived habits
    """
    from .spreadsheet import render_matrix_view
    from .add_form import render_add_habit_form_inline
    from tracking_app.components.stack_visualizer import render_stack_visualizer
    
    storage = st.session_state.storage
    habits = storage.get_habits()
    today = get_local_date()
    current_date = st.session_state.habit_current_date
    
    # Show inline add habit form if requested
    if st.session_state.show_add_habit_form:
        render_add_habit_form_inline()
        return
    
    # Sorting and filtering controls
    col1, col2, col3 = st.columns([2, 2, 2])
    
    with col1:
        sort_by = st.selectbox(
            "Sort by",
            ["name", "score", "streak", "completion_rate"],
            format_func=lambda x: {"name": "Name", "score": "Score", "streak": "Streak", "completion_rate": "Completion Rate"}[x]
        )
    
    with col2:
        filter_status = st.selectbox(
            "Status",
            ["all", "active", "archived"],
            format_func=lambda x: {"all": "All Habits", "active": "Active Only", "archived": "Archived Only"}[x]
        )
    
    with col3:
        st.session_state.habit_sort_ascending = st.checkbox("Ascending", value=st.session_state.get('habit_sort_ascending', False))
    
    # Apply filtering
    if filter_status == "active":
        filtered_habits = [h for h in habits if not h.archived]
    elif filter_status == "archived":
        filtered_habits = [h for h in habits if h.archived]
    else:
        filtered_habits = habits

    # Apply sorting to filtered habits
    def get_sort_key(habit):
        if sort_by == "name":
            return habit.name.lower()
        elif sort_by == "score":
            score = calculate_habit_score(storage, habit.id)
            return -score.value if not st.session_state.habit_sort_ascending else score.value
        elif sort_by == "streak":
            streak = calculate_streak(storage, habit.id)
            return -streak if not st.session_state.habit_sort_ascending else streak
        elif sort_by == "completion_rate":
            rate = get_completion_rate(storage, habit.id)
            return -rate if not st.session_state.habit_sort_ascending else rate
        return habit.name.lower()

    filtered_habits = sorted(filtered_habits, key=get_sort_key, reverse=not st.session_state.habit_sort_ascending and sort_by != "name")

    # Don't return early - always show tabs so "Add Habit" button is accessible
    # Update Tabs to prioritize the Matrix representation
    tab_matrix, tab_active, tab_stacks, tab_today, tab_archive = st.tabs([
        "📅 Spreadsheet Grid", "Card View", "📦 Habit Stacks", "Today's Progress", "Archived"
    ])

    with tab_matrix:
        render_matrix_view(storage, filtered_habits, today)

    with tab_active:
        if not filtered_habits:
            st.info("No habits match your filters. Try adjusting the filter settings or add a new habit!")
        else:
            for habit in filtered_habits:
                if habit.archived:
                    continue

                render_habit_card(habit, storage, today)

    with tab_stacks:
        render_stack_visualizer(storage, st.session_state.user_id if hasattr(st.session_state, 'user_id') else "")

    with tab_today:
        if not habits:
            st.info("No habits yet. Go to the Spreadsheet Grid tab to add your first habit!")
        else:
            # Today's progress
            completed = 0
            for habit in habits:
                if habit.archived:
                    continue
                entry = storage.get_habit_entry(habit.id, today)
                if is_entry_completed(entry):
                    completed += 1

            active_habits = [h for h in habits if not h.archived]
            if active_habits:
                progress = completed / len(active_habits)
                st.progress(progress, text=f"{completed}/{len(active_habits)} completed today")

                st.divider()

                for habit in active_habits:
                    entry = storage.get_habit_entry(habit.id, today)
                    is_complete = is_entry_completed(entry)

                    col1, col2, col3 = st.columns([1, 4, 1])

                    with col1:
                        st.markdown(f"{habit.icon}")

                    with col2:
                        status = "✅" if is_complete else "⬜"
                        st.markdown(f"{status} **{habit.name}**")

                    with col3:
                        if is_complete:
                            if st.button("↩️", key=f"undo_{habit.id}", help="Mark incomplete"):
                                storage.unmark_habit_complete(habit.id, today)
                                # Deduct XP when unmarking (prevent XP farming)
                                st.session_state.user_xp = max(0, st.session_state.user_xp - XP_PER_COMPLETION)
                                st.session_state.user_level = get_level_from_xp(st.session_state.user_xp)
                                st.rerun()
                        else:
                            if st.button("✓", key=f"do_{habit.id}", help="Mark complete"):
                                storage.mark_habit_complete(habit.id, today)
                                st.session_state.user_xp = storage.add_xp(XP_PER_COMPLETION)
                                st.session_state.user_level = get_level_from_xp(st.session_state.user_xp)
                                
                                # Update momentum tracking (Task 11.1.8: 4-Day Momentum)
                                momentum = update_habit_momentum(habit.id, today)
                                if momentum.current_day == 4:
                                    st.balloons()
                                    st.success("🎉 Day 4 MOMENTUM ACHIEVED! You've crossed the threshold!")
                                
                                st.rerun()
            else:
                st.info("No active habits")
    
    with tab_archive:
        if not habits:
            st.info("No habits yet. Go to the Spreadsheet Grid tab to add your first habit!")
        else:
            archived_habits = [h for h in habits if h.archived]
            if archived_habits:
                for habit in archived_habits:
                    col1, col2 = st.columns([4, 1])
                    with col1:
                        st.markdown(f"{habit.icon} ~~{habit.name}~~")
                    with col2:
                        if st.button("↩️", key=f"unarchive_{habit.id}", help="Unarchive"):
                            storage.unarchive_habit(habit.id)
                            st.rerun()
            else:
                st.info("No archived habits")