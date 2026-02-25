"""
Habits Page - Habit Tracking

Streamlit page for creating, tracking, and managing daily habits with streaks.

Usage:
    streamlit run tracking_app/pages/habits.py
"""

import streamlit as st
from datetime import datetime, date, timedelta
from typing import List, Optional
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tracking_app.storage import Storage, get_storage
from tracking_app.models import Habit, HabitEntry, FrequencyType


# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="Habits - Veryfyn",
    page_icon="✅",
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
    
    if 'editing_habit' not in st.session_state:
        st.session_state.editing_habit = None


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

def calculate_streak(storage: Storage, habit_id: str) -> int:
    """Calculate current streak for a habit."""
    streak = 0
    today = date.today()
    
    for i in range(365):  # Max 365 days
        check_date = today - timedelta(days=i)
        entry = storage.get_habit_entry(habit_id, check_date)
        
        if entry and not entry.skipped:
            streak += 1
        else:
            break
    
    return streak


def get_completion_rate(storage: Storage, habit_id: str, days: int = 30) -> float:
    """Get completion rate for a habit over N days."""
    today = date.today()
    completed = 0
    
    for i in range(days):
        check_date = today - timedelta(days=i)
        entry = storage.get_habit_entry(habit_id, check_date)
        if entry and not entry.skipped:
            completed += 1
    
    return (completed / days) * 100


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
    st.title("✅ Habits")
    st.markdown("Track your daily habits and build streaks!")


def render_add_habit_form():
    """Render form to add a new habit."""
    st.subheader("➕ Add New Habit")
    
    with st.form("add_habit_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        
        with col1:
            name = st.text_input("Habit Name", placeholder="e.g., Morning Exercise")
            description = st.text_area("Description (optional)", placeholder="Why is this habit important?")
            
            # Icon selection
            icons = ["🎯", "🏃", "📚", "💧", "🧘", "💪", "🌅", "📝", "🍎", "🛏️", 
                     "🚭", "💊", "🧹", "🎨", "🎵", "💻", "🧠", "❤️", "🌱", "⭐"]
            icon = st.selectbox("Icon", icons, index=0)
        
        with col2:
            frequency = st.selectbox(
                "Frequency",
                ["daily", "weekly"],
                help="How often do you want to track this habit?"
            )
            
            # Color selection
            colors = [
                ("Indigo", "#6366f1"),
                ("Blue", "#3b82f6"),
                ("Green", "#10b981"),
                ("Yellow", "#f59e0b"),
                ("Red", "#ef4444"),
                ("Purple", "#8b5cf6"),
                ("Pink", "#ec4899"),
                ("Teal", "#14b8a6"),
            ]
            color_name = st.selectbox("Color", [c[0] for c in colors])
            color = next(c[1] for c in colors if c[0] == color_name)
            
            habit_type = st.selectbox(
                "Type",
                ["boolean", "numerical"],
                help="Boolean = simple yes/no. Numerical = track a number."
            )
            
            if habit_type == "numerical":
                target_value = st.number_input("Target Value", min_value=0.0, value=1.0)
                target_type = st.selectbox("Goal", ["at_least", "at_most"])
            else:
                target_value = 0.0
                target_type = "at_least"
        
        submitted = st.form_submit_button("Add Habit", use_container_width=True, type="primary")
        
        if submitted and name:
            storage = st.session_state.storage
            habit = storage.create_habit(
                name=name,
                description=description,
                frequency=frequency,
                icon=icon,
                color=color,
                habit_type=habit_type,
                target_value=target_value,
                target_type=target_type
            )
            st.success(f"✅ Created habit: {habit.name}")
            st.rerun()


def render_habits_list():
    """Render the list of habits with tracking."""
    st.subheader("📋 Your Habits")
    
    storage = st.session_state.storage
    habits = storage.get_habits()
    today = date.today()
    
    if not habits:
        st.info("No habits yet. Add your first habit above!")
        return
    
    # Filter tabs
    tab1, tab2, tab3 = st.tabs(["Active", "Today's Progress", "Archived"])
    
    with tab1:
        for habit in habits:
            if habit.archived:
                continue
            
            render_habit_card(habit, storage, today)
    
    with tab2:
        # Today's progress
        completed = 0
        for habit in habits:
            if habit.archived:
                continue
            entry = storage.get_habit_entry(habit.id, today)
            if entry and not entry.skipped:
                completed += 1
        
        active_habits = [h for h in habits if not h.archived]
        if active_habits:
            progress = completed / len(active_habits)
            st.progress(progress, text=f"{completed}/{len(active_habits)} completed today")
            
            st.divider()
            
            for habit in active_habits:
                entry = storage.get_habit_entry(habit.id, today)
                is_complete = entry and not entry.skipped
                
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
                            st.rerun()
                    else:
                        if st.button("✓", key=f"do_{habit.id}", help="Mark complete"):
                            storage.mark_habit_complete(habit.id, today)
                            st.session_state.user_xp = storage.add_xp(10)
                            st.session_state.user_level = get_level_from_xp(st.session_state.user_xp)
                            st.success(f"+10 XP!")
                            st.rerun()
        else:
            st.info("No active habits")
    
    with tab3:
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


def render_habit_card(habit: Habit, storage: Storage, today: date):
    """Render a single habit card."""
    entry = storage.get_habit_entry(habit.id, today)
    is_complete = entry and not entry.skipped
    streak = calculate_streak(storage, habit.id)
    completion_rate = get_completion_rate(storage, habit.id)
    
    with st.container():
        col1, col2, col3, col4 = st.columns([1, 4, 2, 2])
        
        with col1:
            # Color indicator
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
            status = "✅" if is_complete else "⬜"
            st.markdown(f"### {status} {habit.name}")
            if habit.description:
                st.caption(habit.description)
        
        with col3:
            st.metric("Streak", f"{streak} 🔥")
            st.caption(f"{completion_rate:.0f}% completion (30d)")
        
        with col4:
            # Actions
            col_a, col_b, col_c = st.columns(3)
            
            with col_a:
                if is_complete:
                    if st.button("↩️", key=f"uncomplete_{habit.id}", help="Mark incomplete"):
                        storage.unmark_habit_complete(habit.id, today)
                        st.rerun()
                else:
                    if st.button("✓", key=f"complete_{habit.id}", help="Mark complete"):
                        storage.mark_habit_complete(habit.id, today)
                        st.session_state.user_xp = storage.add_xp(10)
                        st.session_state.user_level = get_level_from_xp(st.session_state.user_xp)
                        st.success(f"+10 XP!")
                        st.rerun()
            
            with col_b:
                if st.button("✏️", key=f"edit_{habit.id}", help="Edit habit"):
                    st.session_state.editing_habit = habit.id
            
            with col_c:
                if st.button("🗑️", key=f"delete_{habit.id}", help="Delete habit"):
                    storage.archive_habit(habit.id)
                    st.rerun()
        
        st.divider()


def render_edit_form():
    """Render edit form if a habit is being edited."""
    if not st.session_state.editing_habit:
        return
    
    storage = st.session_state.storage
    habit = storage.get_habit(st.session_state.editing_habit)
    
    if not habit:
        st.session_state.editing_habit = None
        return
    
    st.subheader(f"✏️ Edit: {habit.name}")
    
    with st.form("edit_habit_form"):
        name = st.text_input("Habit Name", value=habit.name)
        description = st.text_area("Description", value=habit.description)
        
        icons = ["🎯", "🏃", "📚", "💧", "🧘", "💪", "🌅", "📝", "🍎", "🛏️", 
                 "🚭", "💊", "🧹", "🎨", "🎵", "💻", "🧠", "❤️", "🌱", "⭐"]
        icon_index = icons.index(habit.icon) if habit.icon in icons else 0
        icon = st.selectbox("Icon", icons, index=icon_index)
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.form_submit_button("Save Changes", type="primary"):
                storage.update_habit(habit.id, name=name, description=description, icon=icon)
                st.session_state.editing_habit = None
                st.success("Habit updated!")
                st.rerun()
        
        with col2:
            if st.form_submit_button("Cancel"):
                st.session_state.editing_habit = None
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
    
    # Add habit form
    render_add_habit_form()
    st.divider()
    
    # Edit form if needed
    render_edit_form()
    
    # Habits list
    render_habits_list()


if __name__ == "__main__":
    main()