"""
UI components for the Dashboard page.

Contains all render functions for the dashboard interface.
"""

import streamlit as st
from datetime import date
import random

from tracking_app.components.session import get_storage, add_xp
from tracking_app.components.metrics import (
    render_habit_score_card,
    render_streak_card,
    render_burnout_risk_card
)
from tracking_app.components.charts import render_weekly_chart

from .constants import (
    XP_HABIT_COMPLETE,
    XP_TASK_COMPLETE,
    DISPLAY_TASK_LIMIT,
    DISPLAY_GOAL_LIMIT,
    MOTIVATIONAL_QUOTES,
    PRIORITY_ICONS,
)
from .helpers import (
    get_todays_habits,
    get_active_tasks,
    get_goals_progress,
    get_weekly_habit_data,
    calculate_habit_scores,
    calculate_streak,
    get_recent_activity,
    get_burnout_risk,
)


def render_welcome():
    """Render welcome section."""
    st.title("🏠 Dashboard")
    
    level = st.session_state.get('user_level', 1)
    xp = st.session_state.get('user_xp', 0)
    
    st.markdown(f"""
    ### Welcome back! 👋
    
    You're currently at **Level {level}** with **{xp} XP**.
    """)


def render_quick_stats():
    """Render quick stats row with real data."""
    storage = get_storage()
    
    # Get data
    habits, habits_completed, habits_total = get_todays_habits(storage)
    tasks, high_priority, due_today, overdue = get_active_tasks(storage)
    goals, goals_progress = get_goals_progress(storage)
    streak = calculate_streak(storage, habits)
    
    # Display metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Habits Today", 
            f"{habits_completed}/{habits_total}",
            delta=None
        )
    
    with col2:
        delta = f"{overdue} overdue" if overdue > 0 else None
        st.metric("Active Tasks", len(tasks), delta=delta)
    
    with col3:
        st.metric("Goals Progress", f"{goals_progress:.0f}%")
    
    with col4:
        st.metric("Current Streak", f"{streak} days")


def render_habit_scores_section():
    """Render habit scores using brain models."""
    st.subheader("📊 Habit Scores")
    
    storage = get_storage()
    scores = calculate_habit_scores(storage)
    
    if not scores:
        st.info("No habits yet. Add habits to see your scores!")
        return
    
    # Display scores in columns
    cols = st.columns(min(len(scores), 3))
    
    for i, score_data in enumerate(scores):
        with cols[i % 3]:
            render_habit_score_card(
                score_value=score_data['score'],
                habit_name=f"{score_data['icon']} {score_data['name']}",
                trend=score_data['trend']
            )


def render_quick_actions():
    """Render quick action buttons."""
    st.subheader("⚡ Quick Actions")
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if st.button("✅ Log Habit", use_container_width=True):
            st.switch_page("pages/habits.py")
    
    with col2:
        if st.button("📋 Add Task", use_container_width=True):
            st.switch_page("pages/tasks.py")
    
    with col3:
        if st.button("🎯 Update Goal", use_container_width=True):
            st.switch_page("pages/goals.py")
    
    with col4:
        if st.button("📈 View Insights", use_container_width=True):
            st.switch_page("pages/insights.py")


def render_todays_habits():
    """Render today's habits section."""
    st.subheader("✅ Today's Habits")
    
    storage = get_storage()
    habits, completed, total = get_todays_habits(storage)
    today = date.today()
    
    if not habits:
        st.info("No habits yet. Add some habits to track!")
        if st.button("➕ Add Habit"):
            st.switch_page("pages/habits.py")
        return
    
    # Progress bar
    progress = completed / total if total > 0 else 0
    st.progress(progress, text=f"{completed}/{total} completed")
    
    # List habits
    for habit in habits:
        entry = storage.get_habit_entry(habit.id, today)
        is_complete = entry and not entry.skipped
        
        col1, col2 = st.columns([4, 1])
        
        with col1:
            icon = "✅" if is_complete else "⬜"
            st.markdown(f"{icon} {habit.icon} **{habit.name}**")
        
        with col2:
            if is_complete:
                if st.button("↩️", key=f"uncomplete_{habit.id}", help="Mark incomplete"):
                    storage.unmark_habit_complete(habit.id, today)
                    st.rerun()
            else:
                if st.button("✓", key=f"complete_{habit.id}", help="Mark complete"):
                    storage.mark_habit_complete(habit.id, today)
                    add_xp(XP_HABIT_COMPLETE)
                    st.success(f"+{XP_HABIT_COMPLETE} XP!")
                    st.rerun()


def render_active_tasks():
    """Render active tasks section."""
    st.subheader("📋 Active Tasks")
    
    storage = get_storage()
    tasks, high_priority, due_today, overdue = get_active_tasks(storage)
    
    if not tasks:
        st.info("No active tasks. Add a task to get started!")
        if st.button("➕ Add Task"):
            st.switch_page("pages/tasks.py")
        return
    
    # Show warning for overdue
    if overdue > 0:
        st.warning(f"⚠️ {overdue} overdue task(s)")
    
    # Show tasks (limit to 5)
    for task in tasks[:DISPLAY_TASK_LIMIT]:
        col1, col2 = st.columns([4, 1])
        
        with col1:
            priority_icon = PRIORITY_ICONS.get(task.priority, "⚪")
            due_str = ""
            if task.due_date:
                if task.due_date.date() == date.today():
                    due_str = " (Today)"
                elif task.due_date.date() < date.today():
                    due_str = " (Overdue!)"
                else:
                    due_str = f" ({task.due_date.strftime('%b %d')})"
            
            st.markdown(f"{priority_icon} **{task.title}**{due_str}")
        
        with col2:
            if st.button("✓", key=f"complete_task_{task.id}"):
                storage.complete_task(task.id)
                xp = XP_TASK_COMPLETE.get(task.priority, 10)
                add_xp(xp)
                st.success(f"+{xp} XP!")
                st.rerun()
    
    if len(tasks) > DISPLAY_TASK_LIMIT:
        st.caption(f"...and {len(tasks) - DISPLAY_TASK_LIMIT} more")


def render_goals_progress():
    """Render goals progress section."""
    st.subheader("🎯 Goals Progress")
    
    storage = get_storage()
    goals, avg_progress = get_goals_progress(storage)
    
    if not goals:
        st.info("No goals set. Create a goal to track your progress!")
        if st.button("➕ Add Goal"):
            st.switch_page("pages/goals.py")
        return
    
    for goal in goals[:DISPLAY_GOAL_LIMIT]:
        st.markdown(f"**{goal.title}**")
        col1, col2 = st.columns([4, 1])
        with col1:
            st.progress(goal.progress_percentage / 100)
        with col2:
            st.caption(f"{goal.progress_percentage:.0f}%")


def render_burnout_indicator():
    """Render burnout risk indicator."""
    st.subheader("💚 Wellbeing Check")
    
    risk = get_burnout_risk(get_storage())
    
    render_burnout_risk_card(
        risk_score=risk['score'],
        risk_level=risk['level'],
        contributing_factors=risk.get('factors')
    )
    
    if risk.get('interventions'):
        with st.expander("💡 Recommendations"):
            for intervention in risk['interventions']:
                st.markdown(f"- {intervention}")


def render_activity_feed():
    """Render recent activity feed."""
    st.subheader("📜 Recent Activity")
    
    activities = get_recent_activity(get_storage())
    
    if not activities:
        st.info("No recent activity. Start tracking to see your progress!")
        return
    
    for activity in activities[:5]:
        date_str = ""
        if activity.get('date'):
            if isinstance(activity['date'], str):
                date_str = activity['date']
            else:
                date_str = activity['date'].strftime('%b %d')
        
        st.markdown(
            f"{activity['icon']} {activity['title']} "
            f"*{date_str}* +{activity.get('xp', 0)} XP"
        )


def render_motivational_quote():
    """Render a motivational quote."""
    quote, author = random.choice(MOTIVATIONAL_QUOTES)
    
    st.info(f'💬 *"{quote}"* — **{author}**')