"""
Dashboard Page - Main Overview (Phase 12 Design System)

Streamlit page providing an overview of all tracking metrics with quick access
to habits and tasks, weekly progress charts, and motivational quotes.

This version uses the Phase 12 Design System for consistent, accessible, and
responsive UI components.

Improvements in this version:
- ✅ Phase 12 design system components (cards, buttons, alerts)
- ✅ Responsive layout that works on mobile, tablet, and desktop
- ✅ Accessibility features (focus indicators, skip links, ARIA labels)
- ✅ Better visual hierarchy with design tokens
- ✅ Loading states and empty states
- ✅ Improved color contrast (WCAG 2.1 AA compliant)
- ✅ Gamification elements (player card, XP progress)
- ✅ Quick stats with trend indicators

Usage:
    streamlit run tracking_app/app.py
    # Navigate to Dashboard from sidebar
"""

import streamlit as st
import sys
import os
from datetime import date, datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

# Import Phase 12 Design System
from tracking_app.design.theme import apply_design_system, get_current_theme
from tracking_app.design.components import (
    render_page_header,
    render_breadcrumbs,
    render_stat_card,
    render_card,
    render_button,
    render_button_group,
    render_progress_card,
    render_achievement_card,
    render_alert,
    render_success_alert,
    render_info_alert,
    render_empty_state,
    render_loading_state,
    render_section_header,
    render_tabs,
)
from tracking_app.design.utils import (
    get_responsive_columns,
    render_responsive_container,
    render_focus_styles,
    render_skip_link,
    is_mobile,
    render_spacer,
    render_divider,
)

# Import existing functionality
from tracking_app.components.sidebar import render_sidebar
from tracking_app.components.session import get_storage, add_xp, init_session_state
from tracking_app.theme import render_player_card

# Import dashboard-specific components
from tracking_app.pages.dashboard.session_state import init_session_state as init_dashboard_state
from tracking_app.pages.dashboard.components import (
    render_welcome,
    render_quick_stats,
    render_habit_scores_section,
    render_quick_actions,
    render_todays_habits,
    render_active_tasks,
    render_goals_progress,
    render_burnout_indicator,
    render_activity_feed,
    render_motivational_quote,
)
from tracking_app.pages.dashboard.helpers import get_weekly_habit_data
from tracking_app.components.charts import render_weekly_chart


# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="Dashboard - Veryfyn",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Apply Phase 12 Design System theme
apply_design_system(theme=get_current_theme())

# Render accessibility features
render_focus_styles()
render_skip_link("main-content")


# =============================================================================
# DASHBOARD COMPONENTS (Phase 12 Enhanced)
# =============================================================================

def render_dashboard_header():
    """Render dashboard header with user level and quick stats."""
    # Get user stats
    level = st.session_state.get('user_level', 1)
    xp = st.session_state.get('user_xp', 0)
    xp_to_next = level * 150  # Simple XP curve
    xp_progress = (xp % xp_to_next) / xp_to_next * 100
    
    # Get time-based greeting
    hour = datetime.now().hour
    if 5 <= hour < 12:
        greeting = "Good morning"
        greeting_icon = "🌅"
    elif 12 <= hour < 17:
        greeting = "Good afternoon"
        greeting_icon = "☀️"
    elif 17 <= hour < 21:
        greeting = "Good evening"
        greeting_icon = "🌆"
    else:
        greeting = "Time to wind down"
        greeting_icon = "🌙"
    
    # Render header
    render_page_header(
        title=f"{greeting_icon} {greeting}",
        subtitle=f"Level {level} Virtuoso • {xp} XP total • You're doing great!",
        icon="🏠",
        actions=[
            {"label": "🔄 Refresh", "key": "refresh_dashboard"},
        ],
        show_divider=False,
    )
    
    # Player card with XP progress
    render_player_card(
        level=level,
        xp_current=xp % xp_to_next,
        xp_max=xp_to_next,
        streak=st.session_state.get('user_streak', 0),
    )


def render_quick_stats_enhanced():
    """Render enhanced quick stats with Phase 12 cards."""
    render_section_header(
        title="Today's Overview",
        icon="📊",
        show_divider=True,
    )
    
    storage = get_storage()
    
    # Get real data
    habits, habits_completed, habits_total = get_todays_habits(storage)
    tasks, high_priority, due_today, overdue = get_active_tasks(storage)
    goals, goals_progress = get_goals_progress(storage)
    streak = calculate_streak(storage, habits)
    
    # Calculate deltas
    habits_delta = f"{habits_completed}/{habits_total}"
    tasks_delta = f"{overdue} overdue" if overdue > 0 else "All caught up!"
    goals_delta = f"{goals} active"
    streak_delta = "Personal best!" if streak > st.session_state.get('best_streak', 0) else f"Best: {st.session_state.get('best_streak', 0)}"
    
    # Responsive columns
    cols = get_responsive_columns(4, mobile_stack=True)
    
    with cols[0]:
        render_stat_card(
            label="Habits",
            value=habits_delta,
            delta=None,
            icon="✅",
            trend="up" if habits_completed == habits_total else "neutral",
            size="md"
        )
    
    with cols[1]:
        render_stat_card(
            label="Tasks",
            value=str(len(tasks)),
            delta=tasks_delta,
            icon="📝",
            trend="down" if overdue > 0 else "neutral",
            size="md"
        )
    
    with cols[2]:
        render_stat_card(
            label="Goals",
            value=f"{goals_progress:.0f}%",
            delta=goals_delta,
            icon="🎯",
            trend="up" if goals_progress > 50 else "neutral",
            size="md"
        )
    
    with cols[3]:
        render_stat_card(
            label="Streak",
            value=f"{streak} days",
            delta=streak_delta,
            icon="🔥",
            trend="up" if streak > 0 else "neutral",
            size="md"
        )


def render_motivational_message():
    """Render motivational message based on user's progress."""
    storage = get_storage()
    
    # Get data for context
    habits, habits_completed, habits_total = get_todays_habits(storage)
    tasks, high_priority, due_today, overdue = get_active_tasks(storage)
    streak = calculate_streak(storage, habits)
    
    # Determine message based on progress
    if habits_total == 0:
        message = "🌱 Start your journey! Add your first habit to begin tracking."
        variant = "info"
    elif habits_completed == habits_total and len(tasks) == 0:
        message = "🎉 Amazing! You've completed everything for today! Time for a well-deserved break!"
        variant = "success"
    elif habits_completed > habits_total / 2:
        message = "💪 You're doing great! Keep up the momentum - you're more than halfway there!"
        variant = "success"
    elif streak > 7:
        message = f"🔥 Incredible {streak}-day streak! Your dedication is inspiring!"
        variant = "success"
    elif overdue > 0:
        message = f"⚡ You have {overdue} overdue task(s). Let's tackle them together!"
        variant = "warning"
    elif high_priority > 0:
        message = f"🎯 Focus time! You have {high_priority} high-priority task(s) waiting."
        variant = "info"
    else:
        message = "🌟 Every small step counts. Let's make today count!"
        variant = "info"
    
    # Render as alert
    render_info_alert(
        title=message,
        message="Keep going! You're building lasting habits." if habits_completed < habits_total else "Enjoy your free time or tackle some goals!",
        dismissible=True,
        key="dashboard_motivation",
    )


def render_focus_now():
    """Render Focus Now section - most important thing to do right now."""
    storage = get_storage()
    
    # Get incomplete habits
    habits, habits_completed, habits_total = get_todays_habits(storage)
    incomplete_habits = [h for h in habits if not (storage.get_habit_entry(h.id, date.today()) and not storage.get_habit_entry(h.id, date.today()).skipped)]
    
    # Get high priority tasks
    tasks, high_priority, due_today, overdue = get_active_tasks(storage)
    
    # Determine what to focus on
    focus_item = None
    focus_type = None
    
    # Priority 1: Overdue tasks
    if overdue > 0:
        overdue_tasks = [t for t in tasks if t.due_date and t.due_date.date() < date.today()]
        focus_item = overdue_tasks[0]
        focus_type = "task"
    # Priority 2: High priority tasks
    elif high_priority > 0:
        high_tasks = [t for t in tasks if t.priority == "high"]
        focus_item = high_tasks[0]
        focus_type = "task"
    # Priority 3: Incomplete habits
    elif incomplete_habits:
        focus_item = incomplete_habits[0]
        focus_type = "habit"
    
    if focus_item:
        render_section_header(
            title="🎯 Focus Now",
            icon="⚡",
            subtitle="Your most important task right now",
            show_divider=True,
        )
        
        if focus_type == "task":
            render_card(
                content=f"""
                <div style="display: flex; align-items: center; gap: 1rem; padding: 0.5rem;">
                    <div style="font-size: 2rem;">🔴</div>
                    <div style="flex: 1;">
                        <div style="font-weight: 700; font-size: 1.1rem;">{focus_item.title}</div>
                        <div style="color: var(--text-secondary); font-size: 0.875rem;">
                            Priority: {focus_item.priority.title()}
                            {f" • Due: {focus_item.due_date.strftime('%b %d')}" if focus_item.due_date else ""}
                        </div>
                    </div>
                </div>
                """,
                variant="elevated",
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Complete Task", key="focus_complete_task", use_container_width=True):
                    storage.complete_task(focus_item.id)
                    add_xp(20 if focus_item.priority == "high" else 10)
                    st.toast(f"✅ Task completed! +{20 if focus_item.priority == 'high' else 10} XP", icon="⭐")
                    st.rerun()
            with col2:
                if st.button("📝 Edit Task", key="focus_edit_task", use_container_width=True):
                    st.session_state.edit_task_id = focus_item.id
                    st.switch_page("pages/tasks_phase12.py")
                    
        else:  # habit
            render_card(
                content=f"""
                <div style="display: flex; align-items: center; gap: 1rem; padding: 0.5rem;">
                    <div style="font-size: 2rem;">{focus_item.icon}</div>
                    <div style="flex: 1;">
                        <div style="font-weight: 700; font-size: 1.1rem;">{focus_item.name}</div>
                        <div style="color: var(--text-secondary); font-size: 0.875rem;">
                            Habit • Score: {calculate_habit_score(storage, focus_item) * 100:.0f}%
                        </div>
                    </div>
                </div>
                """,
                variant="elevated",
            )
            
            col1, col2 = st.columns(2)
            with col1:
                if st.button("✅ Complete Habit", key="focus_complete_habit", use_container_width=True):
                    storage.mark_habit_complete(focus_item.id, date.today())
                    add_xp(10)
                    st.toast(f"✅ +10 XP!", icon="⭐")
                    st.rerun()
            with col2:
                if st.button("⏭️ Skip", key="focus_skip_habit", use_container_width=True):
                    storage.skip_habit(focus_item.id, date.today())
                    st.toast("Habit skipped for today", icon="⏭️")
                    st.rerun()
    else:
        # Everything is complete!
        render_section_header(
            title="🎉 All Caught Up!",
            icon="✨",
            subtitle="Great job! You've completed everything for today.",
            show_divider=True,
        )
        
        render_success_alert(
            title="Amazing Work!",
            message="You've finished all your tasks and habits for today. Take a well-deserved break or set some new goals!",
            dismissible=True,
            key="all_done_dashboard",
        )


def render_habit_scores_enhanced():
    """Render habit scores with Phase 12 cards."""
    render_section_header(
        title="Habit Scores",
        icon="📈",
        subtitle="Track your habit consistency over time",
        show_divider=True,
    )
    
    storage = get_storage()
    scores = calculate_habit_scores(storage)
    
    if not scores:
        render_empty_state(
            title="No Habits Yet",
            description="Add habits to start tracking your consistency scores!",
            icon="🌱",
            action_label="+ Add Your First Habit",
            action_key="add_first_habit_from_scores",
        )
        if st.button("➕ Add Habit", key="add_habit_empty"):
            st.switch_page("pages/habits.py")
        return
    
    # Display scores in responsive grid
    cols = get_responsive_columns(min(len(scores), 3))
    
    for i, score_data in enumerate(scores):
        with cols[i % 3]:
            # Determine trend
            trend = "up" if score_data['trend'] > 0.05 else "down" if score_data['trend'] < -0.05 else "neutral"
            delta_sign = "+" if score_data['trend'] > 0 else ""
            
            render_stat_card(
                label=score_data['name'],
                value=f"{score_data['score']:.0f}%",
                delta=f"{delta_sign}{score_data['trend']:.0%} this week",
                icon=score_data['icon'],
                trend=trend,
                size="sm"
            )


def render_quick_actions_enhanced():
    """Render quick actions with Phase 12 buttons."""
    render_section_header(
        title="Quick Actions",
        icon="⚡",
        show_divider=True,
    )
    
    # Use button group for clean layout
    render_button_group([
        {
            "label": "Log Habit",
            "icon": "✅",
            "variant": "success",
            "key": "quick_log_habit",
        },
        {
            "label": "Add Task",
            "icon": "📝",
            "variant": "primary",
            "key": "quick_add_task",
        },
        {
            "label": "Update Goal",
            "icon": "🎯",
            "variant": "secondary",
            "key": "quick_update_goal",
        },
        {
            "label": "View Insights",
            "icon": "📈",
            "variant": "outline",
            "key": "quick_insights",
        },
    ], gap="medium")
    
    # Handle button clicks
    if st.session_state.get('quick_log_habit'):
        st.switch_page("pages/habits.py")
    elif st.session_state.get('quick_add_task'):
        st.switch_page("pages/tasks.py")
    elif st.session_state.get('quick_update_goal'):
        st.switch_page("pages/goals.py")
    elif st.session_state.get('quick_insights'):
        st.switch_page("pages/insights.py")


def render_todays_habits_enhanced():
    """Render today's habits with Phase 12 cards."""
    render_section_header(
        title="Today's Habits",
        icon="✅",
        subtitle="Complete your habits to earn XP",
        action_label="+ Add Habit",
        action_key="add_habit_today",
    )
    
    storage = get_storage()
    habits, completed, total = get_todays_habits(storage)
    today = date.today()
    
    if not habits:
        render_empty_state(
            title="No Habits for Today",
            description="Start building positive habits today!",
            icon="🌱",
            action_label="Create Your First Habit",
            action_key="create_first_habit",
        )
        return
    
    # Progress bar with XP info
    progress = completed / total if total > 0 else 0
    xp_available = (total - completed) * 10  # XP per habit
    
    render_card(
        content=f"""
        <div style="margin-bottom: 1rem;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 0.5rem;">
                <span style="color: var(--text-secondary);">Progress</span>
                <span style="color: var(--accent-gold); font-weight: 700;">
                    {completed}/{total} completed • {xp_available} XP available
                </span>
            </div>
            <div style="height: 12px; background: var(--bg-tertiary); border-radius: var(--radius-full); overflow: hidden;">
                <div style="
                    height: 100%;
                    width: {progress * 100}%;
                    background: var(--gradient-xp);
                    border-radius: var(--radius-full);
                    box-shadow: 0 0 10px rgba(99, 102, 241, 0.5);
                    transition: width 0.3s ease;
                "></div>
            </div>
        </div>
        """,
        variant="elevated",
    )
    
    # List habits with checkboxes
    for habit in habits:
        entry = storage.get_habit_entry(habit.id, today)
        is_complete = entry and not entry.skipped
        
        # Use columns for layout
        habit_cols = st.columns([6, 1, 1])
        
        with habit_cols[0]:
            icon = "✅" if is_complete else "⬜"
            st.markdown(f"{icon} **{habit.icon} {habit.name}**")
        
        with habit_cols[1]:
            if is_complete:
                if st.button("↩️", key=f"uncomplete_{habit.id}", help="Mark incomplete"):
                    storage.unmark_habit_complete(habit.id, today)
                    st.session_state.xp -= 10  # Remove XP
                    st.rerun()
            else:
                if st.button("✓", key=f"complete_{habit.id}", help="Mark complete", type="primary"):
                    storage.mark_habit_complete(habit.id, today)
                    add_xp(10)
                    st.toast(f"✅ +10 XP!", icon="⭐")
                    st.rerun()
        
        with habit_cols[2]:
            # Show habit score mini-indicator
            score = calculate_habit_score(storage, habit)
            score_color = "var(--success)" if score >= 0.7 else "var(--warning)" if score >= 0.5 else "var(--error)"
            st.markdown(f"<span style='color: {score_color}; font-weight: 700;'>{score:.0f}%</span>", unsafe_allow_html=True)


def render_active_tasks_enhanced():
    """Render active tasks with Phase 12 cards."""
    render_section_header(
        title="Active Tasks",
        icon="📝",
        subtitle="Stay on top of your tasks",
        action_label="+ Add Task",
        action_key="add_task_dashboard",
    )
    
    storage = get_storage()
    tasks, high_priority, due_today, overdue = get_active_tasks(storage)
    
    if not tasks:
        render_empty_state(
            title="No Active Tasks",
            description="You're all caught up! Add a new task to stay productive.",
            icon="🎉",
            action_label="Create Task",
            action_key="create_task_empty",
        )
        return
    
    # Show overdue warning
    if overdue > 0:
        render_alert(
            title=f"⚠️ {overdue} Overdue Task(s)",
            message="You have tasks that are past their deadline. Consider rescheduling or completing them.",
            variant="warning",
            dismissible=True,
            key="overdue_tasks_alert",
        )
    
    # Show high priority count
    if high_priority > 0:
        render_info_alert(
            title=f"🔴 {high_priority} High Priority",
            message=f"You have {high_priority} high-priority task(s) to focus on.",
            dismissible=True,
            key="high_priority_alert",
        )
    
    # Display tasks (limit to 5 for dashboard)
    for task in tasks[:5]:
        task_cols = st.columns([5, 2, 1])
        
        with task_cols[0]:
            priority_icon = "🔴" if task.priority == "high" else "🟡" if task.priority == "medium" else "🟢"
            due_str = ""
            if task.due_date:
                if task.due_date.date() == date.today():
                    due_str = " • **Today**"
                elif task.due_date.date() < date.today():
                    due_str = " • 🔴 Overdue"
                else:
                    due_str = f" • Due {task.due_date.strftime('%b %d')}"
            
            st.markdown(f"{priority_icon} **{task.title}**{due_str}")
            if task.description:
                st.caption(task.description[:100] + "..." if len(task.description) > 100 else task.description)
        
        with task_cols[1]:
            category_tag = task.category if task.category else "General"
            st.markdown(f"<span style='background: var(--bg-tertiary); padding: 0.25rem 0.5rem; border-radius: var(--radius-sm); font-size: 0.75rem;'>{category_tag}</span>", unsafe_allow_html=True)
        
        with task_cols[2]:
            if st.button("✓", key=f"complete_task_{task.id}", help="Complete task"):
                storage.complete_task(task.id)
                add_xp(5 if task.priority == "low" else 10 if task.priority == "medium" else 20)
                st.toast(f"✅ Task completed! +{5 if task.priority == 'low' else 10 if task.priority == 'medium' else 20} XP", icon="⭐")
                st.rerun()


def render_goals_and_chart():
    """Render goals progress and weekly chart."""
    col1, col2 = st.columns(2)
    
    with col1:
        render_section_header(
            title="Goals Progress",
            icon="🎯",
            show_divider=False,
        )
        
        storage = get_storage()
        goals = storage.get_goals()
        
        if not goals:
            render_empty_state(
                title="No Goals Yet",
                description="Set goals to track your long-term progress!",
                icon="🌟",
                action_label="Set a Goal",
                action_key="set_first_goal",
            )
        else:
            for goal in goals[:3]:  # Show top 3 goals
                progress = (goal.current / goal.target * 100) if goal.target > 0 else 0
                render_progress_card(
                    title=f"{goal.icon} {goal.title}",
                    current=goal.current,
                    target=goal.target,
                    unit=goal.unit,
                    icon="🎯",
                    show_percentage=True,
                )
    
    with col2:
        render_section_header(
            title="Weekly Activity",
            icon="📊",
            show_divider=False,
        )
        
        storage = get_storage()
        weekly_data = get_weekly_habit_data(storage)
        
        if weekly_data:
            render_weekly_chart(weekly_data)
        else:
            render_empty_state(
                title="No Activity Yet",
                description="Complete habits to see your weekly activity!",
                icon="📈",
            )


def render_wellbeing_section():
    """Render wellbeing section with burnout indicator and activity feed."""
    col1, col2 = st.columns(2)
    
    with col1:
        render_section_header(
            title="Wellbeing Check",
            icon="💚",
            show_divider=False,
        )
        
        storage = get_storage()
        risk_data = get_burnout_risk(storage)
        
        if risk_data:
            render_burnout_indicator(risk_data)
        else:
            render_info_alert(
                title="Track Your Wellbeing",
                message="Log your emotional health and time entries to get burnout risk insights.",
                dismissible=False,
            )
    
    with col2:
        render_section_header(
            title="Recent Activity",
            icon="📜",
            show_divider=False,
        )
        
        render_activity_feed()


def render_footer():
    """Render dashboard footer with motivational quote."""
    render_divider()
    render_motivational_quote()
    
    # Footer with tips
    st.markdown("""
    <div style="
        text-align: center;
        padding: 2rem 0;
        color: var(--text-secondary);
        font-size: 0.875rem;
    ">
        <p>💡 <strong>Tip:</strong> Complete habits consistently to build streaks and earn achievements!</p>
        <p style="margin-top: 1rem; color: var(--text-disabled);">
            Veryfyn Personal Tracking System • Level <span id="footer-level">{}</span> • 
            <a href="pages/achievements.py" style="color: var(--primary);">View Achievements</a>
        </p>
    </div>
    """.format(st.session_state.get('user_level', 1)), unsafe_allow_html=True)


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_todays_habits(storage):
    """Get today's habits with completion status."""
    habits = storage.get_habits()
    today = date.today()
    completed = 0
    
    for habit in habits:
        entry = storage.get_habit_entry(habit.id, today)
        if entry and not entry.skipped:
            completed += 1
    
    return habits, completed, len(habits)


def get_active_tasks(storage):
    """Get active tasks with priority counts."""
    tasks = storage.get_tasks()
    active_tasks = [t for t in tasks if not t.completed]
    
    high_priority = sum(1 for t in active_tasks if t.priority == "high")
    due_today = sum(1 for t in active_tasks if t.due_date and t.due_date.date() == date.today())
    overdue = sum(1 for t in active_tasks if t.due_date and t.due_date.date() < date.today())
    
    return active_tasks, high_priority, due_today, overdue


def get_goals_progress(storage):
    """Get goals and overall progress."""
    goals = storage.get_goals()
    active_goals = [g for g in goals if not g.completed]
    
    if not active_goals:
        return 0, 0
    
    total_progress = sum(g.current / g.target if g.target > 0 else 0 for g in active_goals)
    avg_progress = total_progress / len(active_goals) * 100
    
    return len(active_goals), avg_progress


def calculate_streak(storage, habits):
    """Calculate current streak."""
    if not habits:
        return 0
    
    # Simple streak calculation
    today = date.today()
    streak = 0
    
    # Check consecutive days
    for i in range(365):  # Max 1 year streak
        check_date = today - __import__('datetime').timedelta(days=i)
        completed_any = False
        
        for habit in habits:
            entry = storage.get_habit_entry(habit.id, check_date)
            if entry and not entry.skipped:
                completed_any = True
                break
        
        if completed_any:
            streak += 1
        elif i > 0:
            break  # Stop at first missed day (except today)
    
    return streak


def calculate_habit_scores(storage):
    """Calculate habit scores for all habits."""
    habits = storage.get_habits()
    scores = []
    
    for habit in habits:
        score = calculate_habit_score(storage, habit)
        scores.append({
            'name': habit.name,
            'icon': habit.icon,
            'score': score * 100,
            'trend': 0.0,  # Would need historical data
        })
    
    return scores


def calculate_habit_score(storage, habit):
    """Calculate individual habit score."""
    today = date.today()
    completed_count = 0
    total_days = 0
    
    # Count completions in last 30 days
    for i in range(30):
        check_date = today - __import__('datetime').timedelta(days=i)
        entry = storage.get_habit_entry(habit.id, check_date)
        total_days += 1
        if entry and not entry.skipped:
            completed_count += 1
    
    return completed_count / total_days if total_days > 0 else 0


def get_burnout_risk(storage):
    """Get burnout risk assessment."""
    # Simple burnout risk based on task load and habit completion
    tasks = storage.get_tasks()
    overdue = sum(1 for t in tasks if not t.completed and t.due_date and t.due_date.date() < date.today())
    
    habits = storage.get_habits()
    today = date.today()
    completed = sum(1 for h in habits if storage.get_habit_entry(h.id, today) and not storage.get_habit_entry(h.id, today).skipped)
    completion_rate = completed / len(habits) if habits else 1.0
    
    risk_score = min(100, overdue * 20 + (1 - completion_rate) * 50)
    
    if risk_score < 30:
        level = "low"
    elif risk_score < 60:
        level = "moderate"
    elif risk_score < 80:
        level = "high"
    else:
        level = "critical"
    
    return {
        'score': risk_score,
        'level': level,
    }


# =============================================================================
# MAIN ENTRY POINT
# =============================================================================

def main():
    """Main dashboard entry point with Phase 12 Design System."""
    # Initialize session states
    init_session_state()
    init_dashboard_state()
    
    # Render sidebar (categorized navigation)
    render_sidebar()
    
    # Main content container
    with render_responsive_container(max_width="1400px"):
        # Header with player card
        render_dashboard_header()
        render_divider()
        
        # Motivational message based on progress
        render_motivational_message()
        render_divider()
        
        # Quick stats
        render_quick_stats_enhanced()
        render_divider()
        
        # Focus Now - most important task
        render_focus_now()
        render_divider()
        
        # Habit scores
        render_habit_scores_enhanced()
        render_divider()
        
        # Quick actions
        render_quick_actions_enhanced()
        render_divider()
        
        # Two column layout for habits and tasks
        col1, col2 = st.columns(2)
        with col1:
            render_todays_habits_enhanced()
        with col2:
            render_active_tasks_enhanced()
        
        render_divider()
        
        # Goals and weekly chart
        render_goals_and_chart()
        
        render_divider()
        
        # Wellbeing section
        render_wellbeing_section()
        
        # Footer
        render_footer()


if __name__ == "__main__":
    main()
