"""
Goals Page - Goal Tracking

Streamlit page for setting, tracking, and achieving personal goals.

Usage:
    streamlit run tracking_app/pages/goals.py
"""

import streamlit as st
from datetime import datetime, date, timedelta
from typing import List, Optional
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tracking_app.storage import Storage, get_storage
from tracking_app.models import Goal


# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="Goals - Veryfyn",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =============================================================================
# SESSION STATE
# =============================================================================

def init_session_state():
    """Initialize session state variables."""
    if 'storage' not in st.session_state:
        st.session_state.storage = get_storage()
    
    if 'user_xp' not in st.session_state:
        st.session_state.user_xp = st.session_state.storage.get_xp()
    
    if 'user_level' not in st.session_state:
        st.session_state.user_level = st.session_state.storage.get_level()
    
    if 'editing_goal' not in st.session_state:
        st.session_state.editing_goal = None


def get_xp_for_level(level: int) -> int:
    """Calculate XP required for a given level."""
    if level <= 1:
        return 0
    return 100 + (level - 2) * 150


def get_level_from_xp(xp: int) -> int:
    """Calculate level from total XP."""
    level = 1
    while xp >= get_xp_for_level(level + 1):
        level += 1
    return level


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def get_days_remaining(deadline: Optional[datetime]) -> Optional[int]:
    """Get days remaining until deadline."""
    if not deadline:
        return None
    
    remaining = (deadline.date() - date.today()).days
    return remaining


def get_progress_status(goal: Goal) -> str:
    """Get status string for a goal."""
    if goal.completed:
        return "✅ Completed"
    
    days = get_days_remaining(goal.deadline)
    
    if days is None:
        return f"📊 {goal.progress_percentage:.0f}% complete"
    
    if days < 0:
        return f"⚠️ Overdue by {abs(days)} days"
    elif days == 0:
        return "📅 Due today!"
    elif days <= 7:
        return f"📅 {days} days left"
    else:
        return f"📊 {goal.progress_percentage:.0f}% • {days} days left"


def get_status_color(goal: Goal) -> str:
    """Get color for goal status."""
    if goal.completed:
        return "#10b981"  # Green
    
    days = get_days_remaining(goal.deadline)
    
    if days is None:
        return "#6366f1"  # Indigo
    
    if days < 0:
        return "#ef4444"  # Red
    elif days <= 7:
        return "#f59e0b"  # Yellow
    else:
        return "#6366f1"  # Indigo


# =============================================================================
# RENDER FUNCTIONS
# =============================================================================

def render_sidebar():
    """Render sidebar with navigation."""
    with st.sidebar:
        st.title("🎯 Veryfyn")
        st.caption("Personal Tracking System")
        st.divider()
        
        # User Stats
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Level", st.session_state.user_level)
        with col2:
            st.metric("XP", st.session_state.user_xp)
        
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


def render_header():
    """Render page header."""
    st.title("🎯 Goals")
    st.markdown("Set personal goals, track your progress, and celebrate achievements.")


def render_add_goal_form():
    """Render form to add a new goal."""
    st.subheader("➕ Add New Goal")
    
    with st.form("add_goal_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input("Goal Title", placeholder="e.g., Read 50 books this year")
            description = st.text_area("Description (optional)", placeholder="Why is this goal important to you?")
            
            # Category/Icon
            icons = ["🎯", "📚", "💪", "💰", "🏃", "🎨", "💼", "🧠", "❤️", "🏠", "✈️", "🎸"]
            icon = st.selectbox("Icon", icons, index=0)
        
        with col2:
            target = st.number_input("Target Value", min_value=0.0, value=1.0, step=0.1)
            unit = st.text_input("Unit", placeholder="e.g., books, kg, hours, $")
            
            # Deadline
            has_deadline = st.checkbox("Set a deadline")
            deadline = None
            if has_deadline:
                deadline = st.date_input(
                    "Deadline",
                    min_value=date.today(),
                    value=date.today() + timedelta(days=30)
                )
        
        submitted = st.form_submit_button("Add Goal", use_container_width=True, type="primary")
        
        if submitted and title:
            storage = st.session_state.storage
            
            deadline_dt = None
            if deadline:
                deadline_dt = datetime.combine(deadline, datetime.min.time())
            
            goal = storage.create_goal(
                title=title,
                description=description,
                target=target,
                unit=unit,
                deadline=deadline_dt
            )
            st.success(f"✅ Created goal: {goal.title}")
            st.rerun()


def render_goals_summary():
    """Render goals summary."""
    storage = st.session_state.storage
    goals = storage.get_goals(include_completed=True)
    
    if not goals:
        return
    
    active = [g for g in goals if not g.completed]
    completed = [g for g in goals if g.completed]
    overdue = [g for g in active if get_days_remaining(g.deadline) is not None and get_days_remaining(g.deadline) < 0]
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Active Goals", len(active))
    
    with col2:
        st.metric("Completed", len(completed))
    
    with col3:
        st.metric("Overdue", len(overdue), delta_color="inverse")


def render_goals_list():
    """Render the list of goals."""
    st.subheader("🎯 Your Goals")
    
    storage = st.session_state.storage
    goals = storage.get_goals(include_completed=True)
    
    if not goals:
        st.info("No goals yet. Add your first goal above!")
        return
    
    # Filter tabs
    tab1, tab2, tab3 = st.tabs(["Active", "Completed", "All"])
    
    with tab1:
        active_goals = [g for g in goals if not g.completed]
        if active_goals:
            for goal in active_goals:
                render_goal_card(goal)
        else:
            st.info("No active goals. Time to set a new goal!")
    
    with tab2:
        completed_goals = [g for g in goals if g.completed]
        if completed_goals:
            for goal in completed_goals:
                render_goal_card(goal)
        else:
            st.info("No completed goals yet. Keep working on your active goals!")
    
    with tab3:
        for goal in goals:
            render_goal_card(goal)


def render_goal_card(goal: Goal):
    """Render a single goal card."""
    storage = st.session_state.storage
    
    with st.container():
        # Header
        col1, col2, col3 = st.columns([1, 5, 2])
        
        with col1:
            # Progress circle
            progress = goal.progress_percentage / 100
            st.markdown(
                f"""
                <div style="
                    width: 60px;
                    height: 60px;
                    border-radius: 50%;
                    background: conic-gradient({get_status_color(goal)} {progress * 360}deg, #1e293b {progress * 360}deg);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-size: 24px;
                ">{goal.icon if hasattr(goal, 'icon') else '🎯'}</div>
                """,
                unsafe_allow_html=True
            )
        
        with col2:
            title_str = f"~~{goal.title}~~" if goal.completed else f"**{goal.title}**"
            st.markdown(f"### {title_str}")
            
            if goal.description:
                st.caption(goal.description)
            
            st.caption(get_progress_status(goal))
        
        with col3:
            # Progress bar
            st.progress(goal.progress_percentage / 100)
            st.caption(f"{goal.current:.1f} / {goal.target:.1f} {goal.unit}")
        
        # Actions
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            # Update progress
            new_value = st.number_input(
                "Progress",
                min_value=0.0,
                max_value=goal.target * 2 if goal.target > 0 else 1000.0,
                value=goal.current,
                key=f"progress_{goal.id}",
                label_visibility="collapsed"
            )
        
        with col2:
            if st.button("📝 Update", key=f"update_{goal.id}", use_container_width=True):
                storage.update_goal_progress(goal.id, new_value)
                
                # Check if just completed
                if new_value >= goal.target and not goal.completed:
                    st.session_state.user_xp = storage.add_xp(50)
                    st.session_state.user_level = get_level_from_xp(st.session_state.user_xp)
                    st.success(f"🎉 Goal completed! +50 XP!")
                else:
                    st.success("Progress updated!")
                st.rerun()
        
        with col3:
            if st.button("✏️ Edit", key=f"edit_{goal.id}", use_container_width=True):
                st.session_state.editing_goal = goal.id
        
        with col4:
            if st.button("🗑️", key=f"delete_{goal.id}", help="Delete goal"):
                storage.delete_goal(goal.id)
                st.rerun()
        
        st.divider()


def render_edit_form():
    """Render edit form if a goal is being edited."""
    if not st.session_state.editing_goal:
        return
    
    storage = st.session_state.storage
    goal = storage.get_goal(st.session_state.editing_goal)
    
    if not goal:
        st.session_state.editing_goal = None
        return
    
    st.subheader(f"✏️ Edit: {goal.title}")
    
    with st.form("edit_goal_form"):
        title = st.text_input("Goal Title", value=goal.title)
        description = st.text_area("Description", value=goal.description)
        
        col1, col2 = st.columns(2)
        
        with col1:
            target = st.number_input("Target Value", min_value=0.0, value=goal.target, step=0.1)
            unit = st.text_input("Unit", value=goal.unit)
        
        with col2:
            has_deadline = st.checkbox("Set a deadline", value=goal.deadline is not None)
            deadline = None
            if has_deadline:
                default_date = goal.deadline.date() if goal.deadline else date.today() + timedelta(days=30)
                deadline = st.date_input("Deadline", value=default_date, min_value=date.today())
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.form_submit_button("Save Changes", type="primary"):
                deadline_dt = None
                if deadline:
                    deadline_dt = datetime.combine(deadline, datetime.min.time())
                
                # Update goal
                storage._db.execute(
                    """UPDATE goals SET 
                       title = ?, description = ?, target = ?, unit = ?, deadline = ?, updated_at = ?
                       WHERE id = ?""",
                    (
                        title, description, target, unit,
                        deadline_dt.isoformat() if deadline_dt else None,
                        datetime.now().isoformat(),
                        goal.id
                    )
                )
                
                st.session_state.editing_goal = None
                st.success("Goal updated!")
                st.rerun()
        
        with col2:
            if st.form_submit_button("Cancel"):
                st.session_state.editing_goal = None
                st.rerun()


# =============================================================================
# MAIN FUNCTION
# =============================================================================

def main():
    """Main page entry point."""
    # Initialize
    init_session_state()
    
    # Render sidebar
    render_sidebar()
    
    # Main content
    render_header()
    st.divider()
    
    # Summary
    render_goals_summary()
    st.divider()
    
    # Add goal form
    render_add_goal_form()
    st.divider()
    
    # Edit form if needed
    render_edit_form()
    
    # Goals list
    render_goals_list()


if __name__ == "__main__":
    main()