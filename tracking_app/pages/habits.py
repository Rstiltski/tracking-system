"""
Habits Page - Habit Tracking

Streamlit page for creating, tracking, and managing daily habits with streaks
and scientific habit scoring using exponential smoothing algorithm.

Usage:
    streamlit run tracking_app/pages/habits.py

Features:
- Habit Score: 0-100% using exponential smoothing (forgiving, gradual decay)
- Score Categories: Excellent, Strong, Developing, Building, Starting
- Trend Indicators: Shows if habit is improving or declining
- Streak Tracking: Current and best streak counts
"""
import streamlit as st
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tracking_app.storage import Storage, get_storage
from tracking_app.models import Habit, HabitEntry, FrequencyType

# Import brain modules for habit scoring
from brain.models.habit import HabitScore, ScoreList
from brain.models.frequency import Frequency
from brain.models.entry import EntryList, Entry, EntryType

# Import brain modules for streak freeze
from brain.models.streak import StreakFreeze, UserInventory

# Import UI components
from tracking_app.components.metrics import render_habit_score_card
from tracking_app.components.sidebar import render_sidebar


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
    
    # Streak freeze inventory
    if 'streak_freeze' not in st.session_state:
        st.session_state.streak_freeze = load_streak_freeze()


def load_streak_freeze() -> StreakFreeze:
    """Load streak freeze inventory from storage."""
    storage = st.session_state.storage
    freeze_data = storage.get_user_data("streak_freeze", None)
    
    if freeze_data:
        return StreakFreeze.from_dict(freeze_data)
    return StreakFreeze(count=1)  # Start with 1 free freeze


def save_streak_freeze(freeze: StreakFreeze) -> None:
    """Save streak freeze inventory to storage."""
    storage = st.session_state.storage
    storage.set_user_data("streak_freeze", freeze.to_dict())
    st.session_state.streak_freeze = freeze


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


def calculate_habit_score(storage: Storage, habit_id: str, lookback_days: int = 90) -> HabitScore:
    """
    Calculate habit score using exponential smoothing algorithm.
    
    This uses the scientific scoring system from brain/models/habit.py:
    - Score from 0.0 to 1.0 (displayed as 0-100%)
    - Frequency-aware multiplier: 0.5^(√frequency / 13)
    - Recent days have higher weight
    - Gradual decay on misses, not reset to zero
    
    Args:
        storage: Storage instance for data access
        habit_id: ID of the habit to calculate score for
        lookback_days: Number of days to consider (default: 90)
    
    Returns:
        HabitScore with value, trend, and timestamp
    """
    today = date.today()
    from_date = today - timedelta(days=lookback_days)
    
    # Build entry list for score computation
    entries = EntryList(habit_id=habit_id)
    
    # Populate entries from storage
    # HabitEntry has: value (1.0 for completed), skipped (bool)
    for i in range(lookback_days + 1):
        check_date = from_date + timedelta(days=i)
        entry = storage.get_habit_entry(habit_id, check_date)
        
        if entry:
            if entry.skipped:
                entries.mark_skipped(check_date)
            elif entry.value > 0:  # value > 0 means completed
                entries.mark_completed(check_date)
    
    # Create frequency (assume daily for now)
    frequency = Frequency.daily()
    
    # Create score list and recompute
    score_list = ScoreList()
    score_list.recompute(
        frequency=frequency,
        entries=entries,
        from_date=from_date,
        to_date=today
    )
    
    return score_list.current


def get_score_category(score: float) -> Dict[str, str]:
    """
    Get the score category for display.
    
    Args:
        score: Score value (0.0 to 1.0)
        
    Returns:
        Dict with 'label', 'color', and 'emoji' keys
    """
    if score >= 0.85:
        return {"label": "Excellent", "color": "#4CAF50", "emoji": "🌟"}
    elif score >= 0.70:
        return {"label": "Strong", "color": "#8BC34A", "emoji": "💪"}
    elif score >= 0.50:
        return {"label": "Developing", "color": "#FFC107", "emoji": "🌱"}
    elif score >= 0.30:
        return {"label": "Building", "color": "#FF9800", "emoji": "🔧"}
    else:
        return {"label": "Starting", "color": "#F44336", "emoji": "🆕"}


def get_trend_indicator(trend: float) -> Dict[str, str]:
    """
    Get trend indicator for display.
    
    Args:
        trend: Trend value (-1.0 to 1.0)
        
    Returns:
        Dict with 'icon' and 'color' keys
    """
    if trend > 0.01:
        return {"icon": "↑", "color": "green", "label": "improving"}
    elif trend < -0.01:
        return {"icon": "↓", "color": "red", "label": "declining"}
    else:
        return {"icon": "→", "color": "gray", "label": "stable"}


def check_streak_break_yesterday(storage: Storage, habit_id: str) -> bool:
    """
    Check if streak was broken yesterday (can be frozen).
    
    Returns True if:
    - Yesterday was NOT completed
    - There was a streak before yesterday
    """
    today = date.today()
    yesterday = today - timedelta(days=1)
    
    # Check if yesterday was NOT completed
    yesterday_entry = storage.get_habit_entry(habit_id, yesterday)
    if yesterday_entry and not yesterday_entry.skipped and yesterday_entry.value > 0:
        return False  # Yesterday was completed, no break
    
    # Check if there was a streak before yesterday
    streak_before = 0
    for i in range(2, 367):  # Start from day before yesterday
        check_date = today - timedelta(days=i)
        entry = storage.get_habit_entry(habit_id, check_date)
        
        if entry and not entry.skipped and entry.value > 0:
            streak_before += 1
        else:
            break
    
    # If there was a streak of at least 1 day before yesterday, the break can be frozen
    return streak_before >= 1


def use_streak_freeze_for_habit(habit_id: str) -> bool:
    """
    Use a streak freeze for a habit.
    
    Marks yesterday as "skipped" to preserve the streak.
    
    Returns True if freeze was used successfully.
    """
    streak_freeze = st.session_state.streak_freeze
    yesterday = date.today() - timedelta(days=1)
    
    if not streak_freeze.is_available:
        return False
    
    if streak_freeze.use_freeze(habit_id, yesterday):
        # Mark yesterday as skipped in storage
        storage = st.session_state.storage
        storage.mark_habit_skipped(habit_id, yesterday)
        
        # Save updated freeze inventory
        save_streak_freeze(streak_freeze)
        return True
    
    return False


# =============================================================================
# RENDER FUNCTIONS
# =============================================================================

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
    """
    Render a single habit card with score, streak, and actions.
    
    Displays:
    - Habit icon and name
    - Habit Score (0-100%) with category badge and trend
    - Current streak
    - Streak freeze option for broken streaks
    - Completion actions (complete/edit/delete)
    """
    entry = storage.get_habit_entry(habit.id, today)
    is_complete = entry and not entry.skipped
    streak = calculate_streak(storage, habit.id)
    completion_rate = get_completion_rate(storage, habit.id)
    
    # Calculate habit score using exponential smoothing
    habit_score = calculate_habit_score(storage, habit.id)
    score_category = get_score_category(habit_score.value)
    trend_indicator = get_trend_indicator(habit_score.trend)
    
    # Check if streak was broken yesterday and can be frozen
    can_use_freeze = check_streak_break_yesterday(storage, habit.id)
    streak_freeze = st.session_state.streak_freeze
    
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
    
    # Render sidebar with streak freeze section
    render_sidebar(show_streak_freeze=True)
    
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