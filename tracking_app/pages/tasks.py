"""
Tasks Page - Task/Todo Management

Streamlit page for creating, managing, and completing tasks with priorities
and categories.

Usage:
    streamlit run tracking_app/pages/tasks.py
"""

import streamlit as st
from datetime import datetime, date, timedelta
from typing import List, Optional
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tracking_app.storage import Storage, get_storage
from tracking_app.models import Task, Priority


# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="Tasks - Veryfyn",
    page_icon="📋",
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
    
    if 'editing_task' not in st.session_state:
        st.session_state.editing_task = None
    
    if 'filter_status' not in st.session_state:
        st.session_state.filter_status = "all"
    
    if 'filter_priority' not in st.session_state:
        st.session_state.filter_priority = "all"


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

def get_priority_color(priority: str) -> str:
    """Get color for priority level."""
    colors = {
        "high": "#ef4444",
        "medium": "#f59e0b",
        "low": "#10b981"
    }
    return colors.get(priority, "#6b7280")


def get_priority_icon(priority: str) -> str:
    """Get icon for priority level."""
    icons = {
        "high": "🔴",
        "medium": "🟡",
        "low": "🟢"
    }
    return icons.get(priority, "⚪")


def is_overdue(due_date: Optional[datetime]) -> bool:
    """Check if a task is overdue."""
    if not due_date:
        return False
    return due_date.date() < date.today()


def is_due_today(due_date: Optional[datetime]) -> bool:
    """Check if a task is due today."""
    if not due_date:
        return False
    return due_date.date() == date.today()


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
    st.title("📋 Tasks")
    st.markdown("Manage your tasks and todos with priorities and deadlines.")


def render_add_task_form():
    """Render form to add a new task."""
    st.subheader("➕ Add New Task")
    
    with st.form("add_task_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input("Task Title", placeholder="e.g., Complete project report")
            description = st.text_area("Description (optional)", placeholder="Add details about this task")
            
            # Category
            categories = ["Work", "Personal", "Health", "Finance", "Learning", "Home", "Other"]
            category = st.selectbox("Category", categories)
        
        with col2:
            priority = st.selectbox(
                "Priority",
                ["low", "medium", "high"],
                format_func=lambda x: {"low": "🟢 Low", "medium": "🟡 Medium", "high": "🔴 High"}.get(x, x)
            )
            
            due_date = st.date_input(
                "Due Date (optional)",
                value=None,
                min_value=date.today()
            )
            
            # Allow time selection
            due_time = st.time_input("Due Time (optional)", value=None)
        
        submitted = st.form_submit_button("Add Task", use_container_width=True, type="primary")
        
        if submitted and title:
            storage = st.session_state.storage
            
            # Combine date and time
            due_datetime = None
            if due_date:
                if due_time:
                    due_datetime = datetime.combine(due_date, due_time)
                else:
                    due_datetime = datetime.combine(due_date, datetime.min.time())
            
            task = storage.create_task(
                title=title,
                description=description,
                priority=priority,
                category=category,
                due_date=due_datetime
            )
            st.success(f"✅ Created task: {task.title}")
            st.rerun()


def render_filters():
    """Render filter controls."""
    col1, col2, col3 = st.columns(3)
    
    with col1:
        status_options = {"all": "All Tasks", "active": "Active", "completed": "Completed", "overdue": "Overdue"}
        st.session_state.filter_status = st.selectbox(
            "Status",
            options=list(status_options.keys()),
            format_func=lambda x: status_options[x]
        )
    
    with col2:
        priority_options = {"all": "All Priorities", "high": "🔴 High", "medium": "🟡 Medium", "low": "🟢 Low"}
        st.session_state.filter_priority = st.selectbox(
            "Priority",
            options=list(priority_options.keys()),
            format_func=lambda x: priority_options[x]
        )
    
    with col3:
        storage = st.session_state.storage
        all_tasks = storage.get_tasks(include_completed=True)
        categories = list(set(t.category for t in all_tasks if t.category))
        categories.insert(0, "All Categories")
        st.session_state.filter_category = st.selectbox("Category", categories)


def render_tasks_list():
    """Render the list of tasks."""
    st.subheader("📝 Your Tasks")
    
    storage = st.session_state.storage
    
    # Get tasks based on filters
    include_completed = st.session_state.filter_status in ["all", "completed"]
    tasks = storage.get_tasks(include_completed=include_completed)
    
    # Apply filters
    if st.session_state.filter_status == "active":
        tasks = [t for t in tasks if not t.completed]
    elif st.session_state.filter_status == "completed":
        tasks = [t for t in tasks if t.completed]
    elif st.session_state.filter_status == "overdue":
        tasks = [t for t in tasks if is_overdue(t.due_date) and not t.completed]
    
    if st.session_state.filter_priority != "all":
        tasks = [t for t in tasks if t.priority == st.session_state.filter_priority]
    
    if hasattr(st.session_state, 'filter_category') and st.session_state.filter_category != "All Categories":
        tasks = [t for t in tasks if t.category == st.session_state.filter_category]
    
    if not tasks:
        st.info("No tasks found. Add a task above or adjust your filters.")
        return
    
    # Summary stats
    total = len(tasks)
    completed = len([t for t in tasks if t.completed])
    overdue = len([t for t in tasks if is_overdue(t.due_date) and not t.completed])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total", total)
    with col2:
        st.metric("Completed", completed)
    with col3:
        st.metric("Overdue", overdue, delta_color="inverse")
    
    st.divider()
    
    # Sort tasks: overdue first, then by priority, then by due date
    def sort_key(task):
        overdue_score = 0 if is_overdue(task.due_date) and not task.completed else 1
        priority_score = {"high": 0, "medium": 1, "low": 2}.get(task.priority, 3)
        due_score = task.due_date.timestamp() if task.due_date else float('inf')
        return (task.completed, overdue_score, priority_score, due_score)
    
    tasks.sort(key=sort_key)
    
    # Render tasks
    for task in tasks:
        render_task_card(task)


def render_task_card(task: Task):
    """Render a single task card."""
    storage = st.session_state.storage
    
    with st.container():
        # Task row
        col1, col2, col3, col4 = st.columns([1, 5, 2, 2])
        
        with col1:
            priority_icon = get_priority_icon(task.priority)
            st.markdown(f"### {priority_icon}")
        
        with col2:
            # Title with strikethrough if completed
            if task.completed:
                st.markdown(f"~~**{task.title}**~~ ✅")
            else:
                st.markdown(f"**{task.title}**")
            
            # Description
            if task.description:
                st.caption(task.description[:100] + "..." if len(task.description) > 100 else task.description)
            
            # Due date and category
            due_str = ""
            if task.due_date:
                if is_overdue(task.due_date) and not task.completed:
                    due_str = f"⚠️ **Overdue** ({task.due_date.strftime('%b %d')})"
                elif is_due_today(task.due_date):
                    due_str = "📅 **Today**"
                else:
                    due_str = f"📅 {task.due_date.strftime('%b %d, %Y')}"
            
            category_str = f"📁 {task.category}" if task.category else ""
            
            if due_str or category_str:
                st.caption(f"{due_str}  {category_str}")
        
        with col3:
            if task.completed:
                st.caption(f"Completed: {task.completed_at.strftime('%b %d') if task.completed_at else 'N/A'}")
            else:
                st.caption(f"Priority: {task.priority.title()}")
        
        with col4:
            # Actions
            col_a, col_b, col_c = st.columns(3)
            
            with col_a:
                if not task.completed:
                    if st.button("✓", key=f"complete_{task.id}", help="Mark complete"):
                        storage.complete_task(task.id)
                        # Award XP
                        xp = {"high": 20, "medium": 10, "low": 5}.get(task.priority, 10)
                        st.session_state.user_xp = storage.add_xp(xp)
                        st.session_state.user_level = get_level_from_xp(st.session_state.user_xp)
                        st.success(f"+{xp} XP!")
                        st.rerun()
            
            with col_b:
                if st.button("✏️", key=f"edit_{task.id}", help="Edit task"):
                    st.session_state.editing_task = task.id
            
            with col_c:
                if st.button("🗑️", key=f"delete_{task.id}", help="Delete task"):
                    storage.delete_task(task.id)
                    st.rerun()
        
        st.divider()


def render_edit_form():
    """Render edit form if a task is being edited."""
    if not st.session_state.editing_task:
        return
    
    storage = st.session_state.storage
    task = storage.get_task(st.session_state.editing_task)
    
    if not task:
        st.session_state.editing_task = None
        return
    
    st.subheader(f"✏️ Edit: {task.title}")
    
    with st.form("edit_task_form"):
        title = st.text_input("Task Title", value=task.title)
        description = st.text_area("Description", value=task.description)
        
        col1, col2 = st.columns(2)
        
        with col1:
            categories = ["Work", "Personal", "Health", "Finance", "Learning", "Home", "Other"]
            category_index = categories.index(task.category) if task.category in categories else 0
            category = st.selectbox("Category", categories, index=category_index)
            
            priority_options = ["low", "medium", "high"]
            priority_index = priority_options.index(task.priority) if task.priority in priority_options else 1
            priority = st.selectbox(
                "Priority",
                priority_options,
                index=priority_index,
                format_func=lambda x: {"low": "🟢 Low", "medium": "🟡 Medium", "high": "🔴 High"}.get(x, x)
            )
        
        with col2:
            due_date = st.date_input(
                "Due Date",
                value=task.due_date.date() if task.due_date else None,
                min_value=date.today()
            )
            due_time = st.time_input(
                "Due Time",
                value=task.due_date.time() if task.due_date else None
            )
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.form_submit_button("Save Changes", type="primary"):
                due_datetime = None
                if due_date:
                    due_datetime = datetime.combine(due_date, due_time if due_time else datetime.min.time())
                
                storage.update_task(
                    task.id,
                    title=title,
                    description=description,
                    priority=priority,
                    category=category,
                    due_date=due_datetime
                )
                st.session_state.editing_task = None
                st.success("Task updated!")
                st.rerun()
        
        with col2:
            if st.form_submit_button("Cancel"):
                st.session_state.editing_task = None
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
    
    # Add task form
    render_add_task_form()
    st.divider()
    
    # Filters
    render_filters()
    st.divider()
    
    # Edit form if needed
    render_edit_form()
    
    # Tasks list
    render_tasks_list()


if __name__ == "__main__":
    main()