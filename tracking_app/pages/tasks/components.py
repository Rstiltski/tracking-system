"""
UI components for the Tasks page.

Contains all render functions for the task management interface.
"""

import streamlit as st
from datetime import datetime, date
from typing import List

from tracking_app.models import Task

from .constants import (
    CATEGORIES,
    PRIORITIES,
    PRIORITY_LABELS,
    STATUS_OPTIONS,
)
from .helpers import (
    get_priority_icon,
    is_overdue,
    is_due_today,
    get_level_from_xp,
    get_xp_reward,
    get_task_sort_key,
)


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
            
            category = st.selectbox("Category", CATEGORIES)
        
        with col2:
            priority = st.selectbox(
                "Priority",
                PRIORITIES,
                format_func=lambda x: PRIORITY_LABELS.get(x, x)
            )
            
            due_date = st.date_input(
                "Due Date (optional)",
                value=None,
                min_value=date.today()
            )
            
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
        st.session_state.filter_status = st.selectbox(
            "Status",
            options=list(STATUS_OPTIONS.keys()),
            format_func=lambda x: STATUS_OPTIONS[x]
        )
    
    with col2:
        priority_options = {"all": "All Priorities", **PRIORITY_LABELS}
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
    
    if st.session_state.filter_category != "All Categories":
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
    
    # Sort tasks
    tasks.sort(key=get_task_sort_key)
    
    # Render tasks
    for task in tasks:
        render_task_card(task)


def render_task_card(task: Task):
    """
    Render a single task card.
    
    Args:
        task: Task object to render
    """
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
                        xp = get_xp_reward(task.priority)
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
            category_index = CATEGORIES.index(task.category) if task.category in CATEGORIES else 0
            category = st.selectbox("Category", CATEGORIES, index=category_index)
            
            priority_index = PRIORITIES.index(task.priority) if task.priority in PRIORITIES else 1
            priority = st.selectbox(
                "Priority",
                PRIORITIES,
                index=priority_index,
                format_func=lambda x: PRIORITY_LABELS.get(x, x)
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