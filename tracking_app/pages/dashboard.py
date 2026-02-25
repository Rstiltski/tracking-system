"""
Dashboard Page - Main Overview

Streamlit page providing an overview of all tracking metrics with quick access
to habits and tasks, weekly progress charts, and motivational quotes.

Updated to use shared components and connect to brain models.

Usage:
    streamlit run tracking_app/pages/dashboard.py
"""

import streamlit as st
from datetime import datetime, date, timedelta
from typing import List, Dict, Any
import sys
import os
import random

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import shared components
from tracking_app.components.sidebar import render_sidebar
from tracking_app.components.session import (
    init_session_state, 
    get_storage, 
    get_level_from_xp,
    add_xp
)
from tracking_app.components.metrics import (
    render_habit_score_card,
    render_streak_card,
    render_burnout_risk_card
)
from tracking_app.components.charts import render_weekly_chart

# Import models
from tracking_app.storage import Storage
from tracking_app.models import Habit, Task, Goal, HabitEntry


# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="Dashboard - Veryfyn",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_todays_habits(storage: Storage) -> tuple:
    """Get habits and completion status for today."""
    habits = storage.get_habits()
    today = date.today()
    
    completed = 0
    total = len(habits)
    
    for habit in habits:
        entry = storage.get_habit_entry(habit.id, today)
        if entry and not entry.skipped:
            completed += 1
    
    return habits, completed, total


def get_active_tasks(storage: Storage) -> tuple:
    """Get active tasks and counts."""
    tasks = storage.get_tasks(include_completed=False)
    
    high_priority = len([t for t in tasks if t.priority == 'high'])
    due_today = len([t for t in tasks if t.due_date and t.due_date.date() == date.today()])
    overdue = len([t for t in tasks if t.due_date and t.due_date.date() < date.today()])
    
    return tasks, high_priority, due_today, overdue


def get_goals_progress(storage: Storage) -> tuple:
    """Get goals and overall progress."""
    goals = storage.get_goals()
    
    if not goals:
        return goals, 0
    
    total_progress = sum(g.progress_percentage for g in goals) / len(goals)
    return goals, total_progress


def get_weekly_habit_data(storage: Storage, days: int = 7) -> dict:
    """Get habit completion data for the past N days."""
    habits = storage.get_habits()
    today = date.today()
    
    data = {
        'dates': [],
        'completed': [],
        'total': []
    }
    
    for i in range(days - 1, -1, -1):
        check_date = today - timedelta(days=i)
        data['dates'].append(check_date.strftime('%a'))
        
        day_completed = 0
        day_total = len(habits)
        
        for habit in habits:
            entry = storage.get_habit_entry(habit.id, check_date)
            if entry and not entry.skipped:
                day_completed += 1
        
        data['completed'].append(day_completed)
        data['total'].append(day_total)
    
    return data


def calculate_habit_scores(storage: Storage) -> List[Dict[str, Any]]:
    """
    Calculate habit scores using the brain models algorithm.
    
    Returns list of dicts with habit name, score, and trend.
    """
    try:
        from brain.models.habit import HabitScore, ScoreList
        from brain.models.frequency import Frequency
        from brain.models.entry import EntryList
    except ImportError:
        # Fallback to simple calculation if brain models not available
        return calculate_simple_scores(storage)
    
    habits = storage.get_habits()
    today = date.today()
    results = []
    
    for habit in habits:
        entries = storage.get_habit_entries(habit.id)
        
        if not entries:
            # New habit, no score yet
            results.append({
                'name': habit.name,
                'icon': habit.icon,
                'id': habit.id,
                'score': 0.0,
                'trend': 0.0
            })
            continue
        
        # Calculate score using exponential smoothing
        # Simple implementation of the algorithm
        lookback_days = 60
        scores = []
        prev_score = 0.0
        prev_trend = 0.0
        
        for i in range(lookback_days - 1, -1, -1):
            check_date = today - timedelta(days=i)
            entry = storage.get_habit_entry(habit.id, check_date)
            checkmark = 1.0 if (entry and not entry.skipped) else 0.0
            
            # Use HabitScore.compute
            score = HabitScore.compute(
                frequency=1.0,  # Daily habit
                previous_score=prev_score,
                checkmark_value=checkmark,
                previous_trend=prev_trend
            )
            scores.append(score)
            prev_score = score.value
            prev_trend = score.trend
        
        if scores:
            latest = scores[-1]
            results.append({
                'name': habit.name,
                'icon': habit.icon,
                'id': habit.id,
                'score': latest.value,
                'trend': latest.trend
            })
    
    return results


def calculate_simple_scores(storage: Storage) -> List[Dict[str, Any]]:
    """Simple score calculation fallback."""
    habits = storage.get_habits()
    today = date.today()
    results = []
    
    for habit in habits:
        # Calculate 30-day completion rate
        completed = 0
        for i in range(30):
            check_date = today - timedelta(days=i)
            entry = storage.get_habit_entry(habit.id, check_date)
            if entry and not entry.skipped:
                completed += 1
        
        score = completed / 30.0 if completed > 0 else 0.0
        
        results.append({
            'name': habit.name,
            'icon': habit.icon,
            'id': habit.id,
            'score': score,
            'trend': 0.0
        })
    
    return results


def calculate_streak(storage: Storage, habits: List[Habit]) -> int:
    """Calculate the overall streak (all habits completed)."""
    streak = 0
    today = date.today()
    
    for i in range(365):
        check_date = today - timedelta(days=i)
        day_complete = True
        
        for habit in habits:
            entry = storage.get_habit_entry(habit.id, check_date)
            if not entry or entry.skipped:
                day_complete = False
                break
        
        if day_complete:
            streak += 1
        else:
            break
    
    return streak


def get_recent_activity(storage: Storage, limit: int = 10) -> List[Dict[str, Any]]:
    """Get recent activity for the activity feed."""
    activities = []
    today = date.today()
    
    # Get recent habit completions
    habits = storage.get_habits()
    for habit in habits:
        entries = storage.get_habit_entries(habit.id, end_date=today)
        for entry in entries[:3]:  # Last 3 entries per habit
            activities.append({
                'type': 'habit',
                'icon': habit.icon,
                'title': f"Completed {habit.name}",
                'date': entry.entry_date,
                'xp': 10
            })
    
    # Get recent task completions
    tasks = storage.get_tasks(include_completed=True)
    for task in tasks:
        if task.completed:
            activities.append({
                'type': 'task',
                'icon': '📋',
                'title': f"Completed: {task.title}",
                'date': task.completed_at if hasattr(task, 'completed_at') else today,
                'xp': {"high": 20, "medium": 10, "low": 5}.get(task.priority, 10)
            })
    
    # Sort by date (most recent first)
    activities.sort(key=lambda x: x['date'] if x['date'] else today, reverse=True)
    
    return activities[:limit]


def get_burnout_risk(storage: Storage) -> Dict[str, Any]:
    """
    Calculate burnout risk using brain/analysis/burnout.py.
    
    Returns dict with risk_score, risk_level, and contributing_factors.
    """
    try:
        from brain.analysis.burnout import BurnoutPredictor, BurnoutIndicators
        
        # Gather indicators from storage
        habits = storage.get_habits()
        tasks = storage.get_tasks(include_completed=False)
        today = date.today()
        
        # Calculate completion rate trend
        recent_completed = 0
        previous_completed = 0
        for habit in habits:
            for i in range(7):
                entry = storage.get_habit_entry(habit.id, today - timedelta(days=i))
                if entry and not entry.skipped:
                    recent_completed += 1
            for i in range(7, 14):
                entry = storage.get_habit_entry(habit.id, today - timedelta(days=i))
                if entry and not entry.skipped:
                    previous_completed += 1
        
        if previous_completed > 0:
            completion_trend = (recent_completed - previous_completed) / previous_completed
        else:
            completion_trend = 0
        
        # Get health data
        health_entries = storage.get_health_entries(
            start_date=today - timedelta(days=14),
            end_date=today
        )
        
        avg_sleep = sum(e.sleep_hours or 0 for e in health_entries) / len(health_entries) if health_entries else 7
        sleep_deviation = avg_sleep - 7.5  # Baseline is 7.5 hours
        
        # Create indicators
        indicators = BurnoutIndicators(
            completion_rate_trend=completion_trend,
            sleep_deviation=sleep_deviation,
            stress_level=5,  # Default, would come from user input
            days_since_checkin=0,  # They're checking in now
            streak_breaks=0,
            mood_trend=0,
            task_overload=len(tasks) / 10,  # Normalize
            habit_load=len(habits),
            missed_days=0
        )
        
        # Calculate risk
        predictor = BurnoutPredictor()
        risk = predictor.assess_risk(indicators)
        
        return {
            'score': risk.risk_score,
            'level': risk.risk_level,
            'factors': risk.contributing_factors,
            'interventions': risk.interventions[:3] if risk.interventions else []
        }
        
    except (ImportError, Exception):
        # Fallback to simple calculation
        return calculate_simple_burnout_risk(storage)


def calculate_simple_burnout_risk(storage: Storage) -> Dict[str, Any]:
    """Simple burnout risk calculation fallback."""
    habits = storage.get_habits()
    tasks = storage.get_tasks(include_completed=False)
    today = date.today()
    
    # Simple heuristics
    missed_days = 0
    for habit in habits:
        entry = storage.get_habit_entry(habit.id, today - timedelta(days=1))
        if not entry or entry.skipped:
            missed_days += 1
    
    task_overload = len(tasks) > 10
    habit_overload = len(habits) > 10
    
    risk_score = 0
    if missed_days > len(habits) / 2:
        risk_score += 30
    if task_overload:
        risk_score += 25
    if habit_overload:
        risk_score += 20
    
    if risk_score >= 50:
        level = "high"
    elif risk_score >= 25:
        level = "moderate"
    else:
        level = "low"
    
    return {
        'score': risk_score,
        'level': level,
        'factors': {'missed_days': missed_days, 'task_count': len(tasks)},
        'interventions': []
    }


# =============================================================================
# RENDER FUNCTIONS
# =============================================================================

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
                    add_xp(10)
                    st.success("+10 XP!")
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
    for task in tasks[:5]:
        col1, col2 = st.columns([4, 1])
        
        with col1:
            priority_icon = {"high": "🔴", "medium": "🟡", "low": "🟢"}.get(task.priority, "⚪")
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
                xp = {"high": 20, "medium": 10, "low": 5}.get(task.priority, 10)
                add_xp(xp)
                st.success(f"+{xp} XP!")
                st.rerun()
    
    if len(tasks) > 5:
        st.caption(f"...and {len(tasks) - 5} more")


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
    
    for goal in goals[:5]:
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
    quotes = [
        ("The secret of getting ahead is getting started.", "Mark Twain"),
        ("It's not about perfect. It's about effort.", "Jillian Michaels"),
        ("Small daily improvements are the key to staggering long-term results.", "Unknown"),
        ("Success is the sum of small efforts repeated day in and day out.", "Robert Collier"),
        ("The only way to do great work is to love what you do.", "Steve Jobs"),
        ("Don't watch the clock; do what it does. Keep going.", "Sam Levenson"),
        ("Your limitation—it's only your imagination.", "Unknown"),
        ("Push yourself, because no one else is going to do it for you.", "Unknown"),
    ]
    
    quote, author = random.choice(quotes)
    
    st.info(f'💬 *"{quote}"* — **{author}**')


# =============================================================================
# MAIN FUNCTION
# =============================================================================

def main():
    """Main page entry point."""
    # Initialize session state
    init_session_state()
    
    # Render sidebar
    render_sidebar()
    
    # Main content
    render_welcome()
    st.divider()
    
    # Quick stats
    render_quick_stats()
    st.divider()
    
    # Habit scores (new feature from brain models)
    render_habit_scores_section()
    st.divider()
    
    # Quick actions
    render_quick_actions()
    st.divider()
    
    # Two column layout
    col1, col2 = st.columns(2)
    
    with col1:
        render_todays_habits()
    
    with col2:
        render_active_tasks()
    
    st.divider()
    
    # Goals and weekly chart
    col1, col2 = st.columns(2)
    
    with col1:
        render_goals_progress()
    
    with col2:
        # Weekly chart
        storage = get_storage()
        weekly_data = get_weekly_habit_data(storage)
        render_weekly_chart(weekly_data)
    
    st.divider()
    
    # Wellbeing and Activity
    col1, col2 = st.columns(2)
    
    with col1:
        render_burnout_indicator()
    
    with col2:
        render_activity_feed()
    
    st.divider()
    
    # Motivational quote
    render_motivational_quote()


if __name__ == "__main__":
    main()