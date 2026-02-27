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
- Sorting & Filtering: Sort by name, score, streak; filter by status
- Accessibility: Text labels for colorblind users
- Streak Freeze: Visual indicators and easy-to-use freeze system
"""
import streamlit as st
from datetime import datetime, date, timedelta
from typing import List, Optional, Dict, Any, Callable
import sys
import os
import pandas as pd
import calendar
from functools import lru_cache

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tracking_app.storage import Storage, get_storage
from tracking_app.models import Habit, HabitEntry, FrequencyType

# Import brain modules for habit scoring
from brain.models.habit import HabitScore, ScoreList, HabitType as BrainHabitType, NumericalHabitTarget
from brain.models.frequency import Frequency
from brain.models.entry import EntryList, Entry, EntryType

# Import brain modules for streak freeze
from brain.models.streak import StreakFreeze, UserInventory

# Import UI components
from tracking_app.components.metrics import render_habit_score_card
from tracking_app.components.sidebar import render_sidebar
from tracking_app.components.burnout_card import render_burnout_risk_card, is_warning_dismissed
from tracking_app.components.difficulty_widget import render_difficulty_widget
from tracking_app.components.relapse_plan_wizard import render_plan_wizard, render_plan_quick_actions
from tracking_app.components.stack_visualizer import render_stack_visualizer
from tracking_app.components.srbai_survey import render_srbai_survey, render_automaticity_badge, render_survey_prompt
from tracking_app.components.tip_card import render_tip_section, render_all_tips
from tracking_app.components.suggestion_card import render_suggestions_section, render_all_suggestions
from tracking_app.components.timing_indicator import render_timing_indicator, render_timing_suggestions


# =============================================================================
# MODULE CONSTANTS
# =============================================================================

# Icon options for habits
HABIT_ICONS = ["🎯", "🏃", "📚", "💧", "🧘", "💪", "🌅", "📝", "🍎", "🛏️",
               "🚭", "💊", "🧹", "🎨", "🎵", "💻", "🧠", "❤️", "🌱", "⭐"]

# Color options for habits (name, hex)
HABIT_COLORS = [
    ("Indigo", "#6366f1"),
    ("Blue", "#3b82f6"),
    ("Green", "#10b981"),
    ("Yellow", "#f59e0b"),
    ("Red", "#ef4444"),
    ("Purple", "#8b5cf6"),
    ("Pink", "#ec4899"),
    ("Teal", "#14b8a6"),
]

# Score category thresholds
SCORE_CATEGORIES = {
    "excellent": {"min": 0.85, "label": "Excellent", "color": "#4CAF50", "emoji": "🌟"},
    "strong": {"min": 0.70, "label": "Strong", "color": "#8BC34A", "emoji": "💪"},
    "developing": {"min": 0.50, "label": "Developing", "color": "#FFC107", "emoji": "🌱"},
    "building": {"min": 0.30, "label": "Building", "color": "#FF9800", "emoji": "🔧"},
    "starting": {"min": 0.0, "label": "Starting", "color": "#F44336", "emoji": "🆕"},
}

# Magic numbers as named constants
MAX_STREAK_LOOKBACK_DAYS = 365
DEFAULT_SCORE_LOOKBACK_DAYS = 90
DEFAULT_COMPLETION_RATE_DAYS = 30
XP_PER_COMPLETION = 10
INITIAL_STREAK_FREEZE_COUNT = 1


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
    
    # Toggle for add habit form in spreadsheet view
    if 'show_add_habit_form' not in st.session_state:
        st.session_state.show_add_habit_form = False
    
    # Timestamp for forcing matrix widget refresh after changes
    if 'matrix_last_update' not in st.session_state:
        st.session_state.matrix_last_update = datetime.now().isoformat()


def get_local_date() -> date:
    """
    Get the current local date with timezone handling.

    Returns:
        Current date in local timezone
    """
    # Use datetime.now() for local time instead of date.today()
    # This respects the system's timezone settings
    return datetime.now().date()


def load_streak_freeze() -> StreakFreeze:
    """Load streak freeze inventory from storage."""
    storage = st.session_state.storage
    freeze_data = storage.get_user_data("streak_freeze", None)

    if freeze_data:
        return StreakFreeze.from_dict(freeze_data)
    return StreakFreeze(count=INITIAL_STREAK_FREEZE_COUNT)


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

def is_entry_completed(entry: Optional[HabitEntry]) -> bool:
    """
    Check if a habit entry represents a completion.

    Handles both boolean and numerical habit completion logic.

    Args:
        entry: The habit entry to check

    Returns:
        True if the entry represents a completed habit
    """
    if entry is None:
        return False

    # Check if explicitly skipped
    if hasattr(entry, 'skipped') and entry.skipped:
        return False

    # Check if completed (value > 0 means completed)
    if hasattr(entry, 'value'):
        return entry.value > 0

    return False


def calculate_streak(storage: Storage, habit_id: str) -> int:
    """Calculate current streak for a habit."""
    streak = 0
    today = get_local_date()

    for i in range(MAX_STREAK_LOOKBACK_DAYS):
        check_date = today - timedelta(days=i)
        entry = storage.get_habit_entry(habit_id, check_date)

        if is_entry_completed(entry):
            streak += 1
        else:
            break

    return streak


def get_completion_rate(storage: Storage, habit_id: str, days: int = DEFAULT_COMPLETION_RATE_DAYS) -> float:
    """Get completion rate for a habit over N days."""
    today = get_local_date()
    completed = 0

    for i in range(days):
        check_date = today - timedelta(days=i)
        entry = storage.get_habit_entry(habit_id, check_date)
        if is_entry_completed(entry):
            completed += 1

    return (completed / days) * 100


def calculate_habit_score(storage: Storage, habit_id: str, lookback_days: int = DEFAULT_SCORE_LOOKBACK_DAYS) -> HabitScore:
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
    today = get_local_date()
    from_date = today - timedelta(days=lookback_days)

    # Build entry list for score computation
    entries = EntryList(habit_id=habit_id)

    # Get habit to check if it's numerical
    habit = storage.get_habit(habit_id)
    is_numerical = habit and habit.habit_type == "numerical"
    target_value = habit.target_value if habit and hasattr(habit, 'target_value') else 0.0
    target_type = habit.target_type if habit and hasattr(habit, 'target_type') else "at_least"

    # Populate entries from storage
    # HabitEntry has: value (1.0 for completed), skipped (bool)
    for i in range(lookback_days + 1):
        check_date = from_date + timedelta(days=i)
        entry = storage.get_habit_entry(habit_id, check_date)

        if entry:
            if hasattr(entry, 'skipped') and entry.skipped:
                entries.mark_skipped(check_date)
            elif entry.value > 0:  # value > 0 means completed
                entries.mark_completed(check_date)

    # Create frequency (assume daily for now)
    frequency = Frequency.daily()

    # Create score list and recompute with proper numerical habit parameters
    score_list = ScoreList()
    score_list.recompute(
        frequency=frequency,
        entries=entries,
        from_date=from_date,
        to_date=today,
        is_numerical=is_numerical,
        target_value=target_value,
        numerical_target_type=NumericalHabitTarget(target_type) if target_type in ["at_least", "at_most"] else NumericalHabitTarget.AT_LEAST
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
    # Iterate through categories in order (highest to lowest threshold)
    for category in ["excellent", "strong", "developing", "building", "starting"]:
        if score >= SCORE_CATEGORIES[category]["min"]:
            return SCORE_CATEGORIES[category]
    return SCORE_CATEGORIES["starting"]


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
    today = get_local_date()
    yesterday = today - timedelta(days=1)

    # Check if yesterday was NOT completed
    yesterday_entry = storage.get_habit_entry(habit_id, yesterday)
    if is_entry_completed(yesterday_entry):
        return False  # Yesterday was completed, no break

    # Check if there was a streak before yesterday
    streak_before = 0
    for i in range(2, MAX_STREAK_LOOKBACK_DAYS):  # Start from day before yesterday
        check_date = today - timedelta(days=i)
        entry = storage.get_habit_entry(habit_id, check_date)

        if is_entry_completed(entry):
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
    yesterday = get_local_date() - timedelta(days=1)

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

    storage = st.session_state.storage
    habits = storage.get_habits()
    existing_names = {h.name.lower() for h in habits}

    with st.form("add_habit_form", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input("Habit Name", placeholder="e.g., Morning Exercise")
            description = st.text_area("Description (optional)", placeholder="Why is this habit important?")

            # Icon selection
            icon = st.selectbox("Icon", HABIT_ICONS, index=0)

        with col2:
            frequency = st.selectbox(
                "Frequency",
                ["daily", "weekly"],
                help="How often do you want to track this habit?"
            )

            # Color selection
            color_name = st.selectbox("Color", [c[0] for c in HABIT_COLORS])
            color = next(c[1] for c in HABIT_COLORS if c[0] == color_name)

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
            # Validate: Check for duplicate names
            if name.lower() in existing_names:
                st.error(f"❌ A habit with the name '{name}' already exists. Please choose a different name.")
            else:
                try:
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
                except Exception as e:
                    st.error(f"❌ Failed to create habit: {str(e)}")


def render_add_habit_form_inline():
    """Render inline form to add a new habit (for spreadsheet view)."""
    st.markdown("### ➕ Add New Habit")

    storage = st.session_state.storage
    habits = storage.get_habits()
    existing_names = {h.name.lower() for h in habits}

    with st.form("add_habit_form_inline", clear_on_submit=True):
        col1, col2 = st.columns(2)

        with col1:
            name = st.text_input("Habit Name", placeholder="e.g., Morning Exercise")
            description = st.text_area("Description (optional)", placeholder="Why is this habit important?")

            # Icon selection
            icon = st.selectbox("Icon", HABIT_ICONS, index=0)

        with col2:
            frequency = st.selectbox(
                "Frequency",
                ["daily", "weekly"],
                help="How often do you want to track this habit?"
            )

            # Color selection
            color_name = st.selectbox("Color", [c[0] for c in HABIT_COLORS])
            color = next(c[1] for c in HABIT_COLORS if c[0] == color_name)

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

        col_btn1, col_btn2 = st.columns(2)
        with col_btn1:
            submitted = st.form_submit_button("Add Habit", type="primary", use_container_width=True)
        with col_btn2:
            cancelled = st.form_submit_button("Cancel", use_container_width=True)

        if cancelled:
            st.session_state.show_add_habit_form = False
            st.rerun()

        if submitted and name:
            # Validate: Check for duplicate names
            if name.lower() in existing_names:
                st.error(f"❌ A habit with the name '{name}' already exists. Please choose a different name.")
            else:
                try:
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
                    st.session_state.show_add_habit_form = False
                    st.success(f"✅ Created habit: {habit.name}")
                    st.rerun()
                except Exception as e:
                    st.error(f"❌ Failed to create habit: {str(e)}")


def render_monthly_progress_rings(storage: Storage, habits: List[Habit], current_date: date):
    """
    Renders a 4-column grid of SVG-based circular progress gauges.
    Calculates exact monthly completion percentage per active habit.
    
    Args:
        storage: Storage instance for data access
        habits: List of all habits
        current_date: Current date for month calculation
    """
    _, month_days = calendar.monthrange(current_date.year, current_date.month)
    start_date = current_date.replace(day=1)
    
    active_habits = [h for h in habits if not h.archived]
    if not active_habits:
        return

    st.subheader("🎯 Monthly Completion Overview")
    
    # Inject core CSS parameters for SVG manipulation
    st.markdown("""
    <style>
    .ring-container {
        display: flex; flex-direction: column; align-items: center; margin-bottom: 24px;
    }
    .circular-chart {
        display: block; margin: 10px auto; max-width: 120px; max-height: 120px;
    }
    .circle-bg {
        fill: none; stroke: #f0f0f0; stroke-width: 3.8;
    }
    .circle {
        fill: none; stroke-width: 3.8; stroke-linecap: round;
        animation: progress 1s ease-out forwards;
    }
    .percentage {
        fill: #333; font-family: sans-serif; font-size: 0.5em; text-anchor: middle; font-weight: bold;
    }
    .habit-indicator {
        margin-top: 8px; width: 40px; height: 6px; background-color: #ff477e; border-radius: 4px;
    }
    .habit-title {
        margin-top: 8px; font-weight: bold; font-size: 1rem; text-align: center; color: #555;
    }
    </style>
    """, unsafe_allow_html=True)

    # Initialize a 4-column layout matrix
    cols = st.columns(4)
    
    for i, habit in enumerate(active_habits):
        # Calculate quantitative completion for the current month
        completed = 0
        for day in range(month_days):
            check_date = start_date + timedelta(days=day)
            entry = storage.get_habit_entry(habit.id, check_date)
            if is_entry_completed(entry):
                completed += 1

        # Prevent ZeroDivisionError and calculate raw percentage
        percentage = int((completed / month_days) * 100) if month_days > 0 else 0
        
        # SVG circumference normalized to ~100 via radius 15.9155
        dasharray = 100
        dashoffset = dasharray - percentage
        color = habit.color if hasattr(habit, 'color') and habit.color else "#00bbf9"
        
        # Construct isolated DOM elements per habit
        svg_html = f"""
        <div class="ring-container">
            <svg viewBox="0 0 36 36" class="circular-chart">
                <path class="circle-bg"
                    d="M18 2.0845
                    a 15.9155 15.9155 0 0 1 0 31.831
                    a 15.9155 15.9155 0 0 1 0 -31.831"
                />
                <path class="circle"
                    stroke="{color}"
                    stroke-dasharray="{dasharray}, {dasharray}"
                    stroke-dashoffset="{dashoffset}"
                    d="M18 2.0845
                    a 15.9155 15.9155 0 0 1 0 31.831
                    a 15.9155 15.9155 0 0 1 0 -31.831"
                />
                <text x="18" y="20.35" class="percentage">{percentage}%</text>
            </svg>
            <div class="habit-indicator"></div>
            <div class="habit-title">{habit.icon} {habit.name}</div>
        </div>
        """
        
        # Render within the designated spatial column
        with cols[i % 4]:
            st.markdown(svg_html, unsafe_allow_html=True)


def render_matrix_view(storage: Storage, habits: List[Habit], current_date: date):
    """
    Render a unified spreadsheet matrix view for habit tracking.
    
    Single table layout with:
    - Habit column (frozen as index)
    - Progress column (first data column for visibility)
    - Date columns (scrollable, following progress)
    
    Args:
        storage: Storage instance for data access
        habits: List of all habits
        current_date: Current date for month calculation
    """
    # Title with month name
    month_name = current_date.strftime("%B %Y")
    st.subheader(f"📅 {month_name}")
    
    # Add Habit button
    if not st.session_state.show_add_habit_form:
        if st.button("➕ Add Habit", type="primary", key="show_add_habit_btn"):
            st.session_state.show_add_habit_form = True
            st.rerun()
    else:
        # Show the add habit form inline
        st.container()
        render_add_habit_form_inline()
        st.divider()
    
    # 1. Temporal Generation (Full Month)
    start_date = current_date.replace(day=1)
    _, month_days = calendar.monthrange(current_date.year, current_date.month)
    end_date = current_date.replace(day=month_days)
    
    date_range = [start_date + timedelta(days=x) for x in range(month_days)]
    date_strs = [d.strftime("%a %d") for d in date_range]
    
    active_habits = [h for h in habits if not h.archived]
    if not active_habits:
        st.info("No active habits available for matrix tracking.")
        return

    # 2. Build Single DataFrame with columns: Habit (index) -> Progress -> Dates
    records = []
    habit_id_map = {}
    
    for h in active_habits:
        habit_label = f"{h.icon} {h.name}"
        habit_id_map[habit_label] = h.id

        # Build row: Habit label is the index, Progress first, then dates
        row = {"Habit": habit_label}
        completed_count = 0

        for d, d_str in zip(date_range, date_strs):
            entry = storage.get_habit_entry(h.id, d)
            is_completed = is_entry_completed(entry)
            row[d_str] = is_completed
            if is_completed:
                completed_count += 1

        # Calculate and insert Progress AFTER Habit, BEFORE dates
        row["Progress"] = (completed_count / month_days) * 100
        records.append(row)

    # Create DataFrame with explicit column order
    # Columns: Habit, Progress, Mon 01, Tue 02, ...
    df = pd.DataFrame(records)
    
    # Set Habit as index to freeze/pin it on the left
    df.set_index("Habit", inplace=True)
    
    # 3. Column Configuration
    # Order: Habit (frozen index) -> Progress -> Dates
    column_config = {
        "Progress": st.column_config.ProgressColumn(
            "Progress %",
            format="%d%%",
            min_value=0,
            max_value=100,
        )
    }
    for d_str in date_strs:
        column_config[d_str] = st.column_config.CheckboxColumn(d_str, default=False)
            
    # 4. Render Single Unified Table
    # Use timestamp in key to force widget refresh after changes
    edited_data = st.data_editor(
        df,
        column_config=column_config,
        use_container_width=True,
        key=f"habit_matrix_editor_{current_date.month}_{current_date.year}_{st.session_state.matrix_last_update}"
    )

    st.divider()

    # 5. Data Representation: Monthly Trend Analysis
    st.subheader("📈 Daily Completion Trend")
    # Vertically aggregate the boolean columns to get total completions per day
    # Use edited_data to reflect real-time changes
    daily_completions = edited_data[date_strs].sum()
    trend_df = pd.DataFrame({
        "Day": date_strs,
        "Completions": daily_completions.values
    }).set_index("Day")

    # Render an Area Chart for high visual appeal and immediate usability
    st.area_chart(trend_df, use_container_width=True, color="#10b981")

    # 6. Monthly Progress Rings - SVG Circular Gauges
    st.divider()
    render_monthly_progress_rings(storage, habits, current_date)

    # 7. Centralized Store Mutation Detection
    changes_detected = False
    for habit_name, row in edited_data.iterrows():
        habit_id = habit_id_map.get(str(habit_name))
        if not habit_id:
            continue
        for d, d_str in zip(date_range, date_strs):
            old_val = df.at[habit_name, d_str]
            new_val = row[d_str]

            if pd.isna(old_val):
                old_val = False
            if pd.isna(new_val):
                new_val = False

            if old_val != new_val:
                if new_val:
                    storage.mark_habit_complete(habit_id, d)
                    st.session_state.user_xp = storage.add_xp(XP_PER_COMPLETION)
                else:
                    storage.unmark_habit_complete(habit_id, d)
                    # Deduct XP when unmarking (prevent XP farming)
                    st.session_state.user_xp = max(0, st.session_state.user_xp - XP_PER_COMPLETION)
                changes_detected = True

    if changes_detected:
        st.session_state.user_level = get_level_from_xp(st.session_state.user_xp)
        # Update timestamp to force widget refresh on rerun
        st.session_state.matrix_last_update = datetime.now().isoformat()
        st.success("✅ Progress updated!")
        st.rerun()


def render_habits_list():
    """Render the list of habits with tracking."""
    st.subheader("📋 Your Habits")

    storage = st.session_state.storage
    habits = storage.get_habits()
    today = get_local_date()

    # Initialize sorting and filtering session state
    if 'habit_sort_by' not in st.session_state:
        st.session_state.habit_sort_by = 'name'
    if 'habit_sort_ascending' not in st.session_state:
        st.session_state.habit_sort_ascending = True
    if 'habit_filter_status' not in st.session_state:
        st.session_state.habit_filter_status = 'all'

    # Sorting and filtering controls
    with st.expander("🔧 Sort & Filter", expanded=False):
        col_sort1, col_sort2, col_filter = st.columns(3)
        with col_sort1:
            sort_by = st.selectbox(
                "Sort by",
                ["name", "score", "streak", "completion_rate"],
                index=["name", "score", "streak", "completion_rate"].index(st.session_state.habit_sort_by)
            )
        with col_sort2:
            sort_order = st.selectbox(
                "Order",
                ["ascending", "descending"],
                index=0 if st.session_state.habit_sort_ascending else 1
            )
        with col_filter:
            filter_status = st.selectbox(
                "Filter",
                ["all", "active", "archived"],
                index=["all", "active", "archived"].index(st.session_state.habit_filter_status)
            )

        # Update session state
        if sort_by != st.session_state.habit_sort_by or sort_order.replace("ascending", "") != str(st.session_state.habit_sort_ascending):
            st.session_state.habit_sort_by = sort_by
            st.session_state.habit_sort_ascending = sort_order == "ascending"
        if filter_status != st.session_state.habit_filter_status:
            st.session_state.habit_filter_status = filter_status

    # Apply filtering
    if filter_status == "active":
        habits = [h for h in habits if not h.archived]
    elif filter_status == "archived":
        habits = [h for h in habits if h.archived]

    # Apply sorting
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

    habits = sorted(habits, key=get_sort_key, reverse=not st.session_state.habit_sort_ascending and sort_by != "name")

    # Don't return early - always show tabs so "Add Habit" button is accessible
    # Update Tabs to prioritize the Matrix representation
    tab_matrix, tab_active, tab_stacks, tab_today, tab_archive = st.tabs([
        "📅 Spreadsheet Grid", "Card View", "📦 Habit Stacks", "Today's Progress", "Archived"
    ])

    with tab_matrix:
        render_matrix_view(storage, habits, today)

    with tab_active:
        if not habits:
            st.info("No habits yet. Go to the Spreadsheet Grid tab to add your first habit!")
        else:
            for habit in habits:
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
                                st.success(f"+{XP_PER_COMPLETION} XP!")
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


def render_habit_card(habit: Habit, storage: Storage, today: date):
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
    """
    entry = storage.get_habit_entry(habit.id, today)
    is_complete = is_entry_completed(entry)
    streak = calculate_streak(storage, habit.id)
    completion_rate = get_completion_rate(storage, habit.id)

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
                        st.success(f"+{XP_PER_COMPLETION} XP!")
                        st.rerun()

            with col_b:
                if st.button("✏️", key=f"edit_{habit.id}", help="Edit habit"):
                    st.session_state.editing_habit = habit.id

            with col_c:
                # Archive button with confirmation
                if st.button("🗑️", key=f"archive_{habit.id}", help="Archive habit"):
                    # Use session state to track confirmation
                    confirm_key = f"confirm_archive_{habit.id}"
                    if confirm_key not in st.session_state:
                        st.session_state[confirm_key] = False
                        st.rerun()
                    
                    if not st.session_state[confirm_key]:
                        st.session_state[confirm_key] = True
                        st.rerun()
                    else:
                        storage.archive_habit(habit.id)
                        st.session_state[confirm_key] = False
                        st.success(f"📦 Archived '{habit.name}'")
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
        render_suggestions_section(storage, st.session_state.get('user_id', ''), limit=2)

        # Show all suggestions if requested
        if st.session_state.get("show_all_suggestions", False):
            render_all_suggestions(storage, st.session_state.get('user_id', ''))
            if st.button("Close Suggestions"):
                st.session_state.show_all_suggestions = False
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
        description = st.text_area("Description", value=habit.description or "")

        # Icon selection
        icon_index = HABIT_ICONS.index(habit.icon) if habit.icon in HABIT_ICONS else 0
        icon = st.selectbox("Icon", HABIT_ICONS, index=icon_index)

        col1, col2 = st.columns(2)

        with col1:
            frequency = st.selectbox(
                "Frequency",
                ["daily", "weekly"],
                index=0 if habit.frequency == "daily" else 1
            )

            # Color selection
            color_index = next((i for i, c in enumerate(HABIT_COLORS) if c[1] == habit.color), 0)
            color_name = st.selectbox("Color", [c[0] for c in HABIT_COLORS], index=color_index)
            color = HABIT_COLORS[color_index][1]

        with col2:
            habit_type = st.selectbox(
                "Type",
                ["boolean", "numerical"],
                index=0 if habit.habit_type == "boolean" else 1
            )

            if habit_type == "numerical":
                target_value = st.number_input("Target Value", min_value=0.0, value=habit.target_value or 1.0)
                target_type = st.selectbox("Goal", ["at_least", "at_most"], index=0 if habit.target_type == "at_least" else 1)
            else:
                target_value = 0.0
                target_type = "at_least"

        # Difficulty adjustment quick actions
        st.divider()
        st.markdown("**⚡ Quick Difficulty Adjustment**")
        
        col_diff1, col_diff2, col_diff3 = st.columns(3)
        
        with col_diff1:
            if st.button(
                "📈 Increase 15%",
                key=f"edit_increase_{habit.id}",
                help="Make it more challenging",
                use_container_width=True
            ):
                new_target = habit.target_value * 1.15 if habit.target_value else 1.15
                storage.update_habit(habit.id, target_value=new_target)
                st.success(f"✅ Target increased to {new_target:.2f}")
                st.rerun()
        
        with col_diff2:
            if st.button(
                "🐜 Tiny Version",
                key=f"edit_tiny_{habit.id}",
                help="Reduce to 2-minute version",
                use_container_width=True
            ):
                new_target = max(0.1, (habit.target_value or 1.0) * 0.5)
                storage.update_habit(habit.id, target_value=new_target)
                st.success(f"✅ Target reduced to {new_target:.2f} (tiny version)")
                st.rerun()
        
        with col_diff3:
            if st.button(
                "✅ Keep Current",
                key=f"edit_keep_{habit.id}",
                help="No change needed",
                use_container_width=True
            ):
                st.info("👍 Keeping current difficulty level")

        col_save, col_cancel = st.columns(2)

        with col_save:
            submitted = st.form_submit_button("Save Changes", type="primary", use_container_width=True)
            if submitted:
                # Validate: Check for duplicate names (excluding current habit)
                habits = storage.get_habits()
                duplicate = any(h.name.lower() == name.lower() and h.id != habit.id for h in habits)
                if duplicate:
                    st.error(f"❌ A habit with the name '{name}' already exists. Please choose a different name.")
                else:
                    try:
                        storage.update_habit(
                            habit.id,
                            name=name,
                            description=description,
                            icon=icon,
                            frequency=frequency,
                            color=color,
                            habit_type=habit_type,
                            target_value=target_value,
                            target_type=target_type
                        )
                        st.session_state.editing_habit = None
                        st.success("Habit updated!")
                        st.rerun()
                    except Exception as e:
                        st.error(f"❌ Failed to update habit: {str(e)}")

        with col_cancel:
            cancelled = st.form_submit_button("Cancel", use_container_width=True)
            if cancelled:
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
    
    # Edit form if needed
    render_edit_form()
    
    # Habits list (includes spreadsheet view with add habit button)
    render_habits_list()


if __name__ == "__main__":
    main()