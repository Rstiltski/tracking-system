"""
Momentum Counter Component - 4-Day Momentum Display

Implements the visual momentum indicator for habits:
- Shows current momentum day (1-4+)
- Displays progress bar to Day 4 threshold
- Shows milestone celebrations
- Provides motivational messages

Based on Task 11.1.8 from PHASE_11_INTEGRATION_ROADMAP.md

Usage:
    from tracking_app.components.momentum_counter import (
        render_momentum_indicator,
        render_momentum_card,
        check_and_show_momentum_celebration
    )
"""

import streamlit as st
from typing import Optional, Dict
from datetime import date

# Import the momentum model
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
from brain.models.momentum import (
    MomentumTracker,
    MomentumData,
    MomentumPhase,
    MOMENTUM_THRESHOLD_DAY,
    MOMENTUM_MESSAGES,
    MOMENTUM_CELEBRATIONS,
    calculate_momentum_from_streak
)


# =============================================================================
# STREAMLIT COMPONENTS
# =============================================================================

def render_momentum_indicator(
    momentum: MomentumData,
    show_message: bool = True,
    compact: bool = False
):
    """
    Render a momentum progress indicator.
    
    Args:
        momentum: The MomentumData to display
        show_message: Whether to show the motivational message
        compact: Whether to use compact mode (smaller UI)
    """
    current_day = momentum.current_day
    progress = min(current_day / MOMENTUM_THRESHOLD_DAY, 1.0)
    
    # Determine colors based on phase
    phase = _get_phase_info(momentum)
    
    if compact:
        # Compact view - just the day and progress
        cols = st.columns([1, 3])
        with cols[0]:
            st.markdown(f"**Day {current_day}**")
        with cols[1]:
            st.progress(progress)
    else:
        # Full momentum card
        st.markdown(f"""
        <div style="
            padding: 1rem;
            border-radius: 0.5rem;
            border-left: 4px solid {phase['color']};
            background: rgba(255,255,255,0.05);
            margin-bottom: 1rem;
        ">
            <div style="display: flex; align-items: center; gap: 0.5rem; margin-bottom: 0.5rem;">
                <span style="font-size: 1.5rem;">{phase['icon']}</span>
                <span style="font-size: 1.25rem; font-weight: bold;">Day {current_day}</span>
                <span style="color: {phase['color']};">• {phase['name']}</span>
            </div>
        """, unsafe_allow_html=True)
        
        # Progress bar
        st.progress(progress)
        
        # Show days indicator
        days_html = _render_days_indicator(current_day)
        st.markdown(days_html, unsafe_allow_html=True)
        
        # Show message
        if show_message:
            message = MOMENTUM_MESSAGES.get(current_day, f"Day {current_day} - Keep going!")
            st.markdown(f"*{message}*")
        
        st.markdown("</div>", unsafe_allow_html=True)


def render_momentum_card(
    habit_name: str,
    momentum: MomentumData,
    show_celebration: bool = True
):
    """
    Render a full momentum card for a habit.
    
    Args:
        habit_name: Name of the habit
        momentum: The MomentumData to display
        show_celebration: Whether to show milestone celebrations
    """
    current_day = momentum.current_day
    phase = _get_phase_info(momentum)
    progress = min(current_day / MOMENTUM_THRESHOLD_DAY, 1.0)
    
    # Check for new milestone
    celebration = None
    if show_celebration and momentum.last_milestone in MOMENTUM_CELEBRATIONS:
        celebration = MOMENTUM_CELEBRATIONS[momentum.last_milestone]
    
    # Main card container
    with st.container():
        # Header
        col1, col2 = st.columns([3, 1])
        with col1:
            st.subheader(f"🔥 {habit_name}")
        with col2:
            st.markdown(f"**Day {current_day}**")
        
        # Progress bar
        st.progress(progress)
        
        # Days visualization
        st.markdown(_render_days_indicator(current_day), unsafe_allow_html=True)
        
        # Phase indicator
        st.markdown(f":{phase['icon']} **{phase['name']}** - {phase['description']}")
        
        # Message
        message = MOMENTUM_MESSAGES.get(current_day, "Keep building your momentum!")
        st.info(message)
        
        # Celebration if applicable
        if celebration and momentum.last_milestone == current_day:
            st.success(f"🎉 {celebration}")
        
        # Streak count (for context)
        if momentum.consecutive_completions > current_day:
            st.caption(f"Total streak: {momentum.consecutive_completions} days")


def check_and_show_momentum_celebration(
    momentum: MomentumData,
    previous_milestone: int
) -> Optional[str]:
    """
    Check if a new milestone was achieved and show celebration.
    
    Args:
        momentum: Current momentum data
        previous_milestone: The milestone that was shown previously
        
    Returns:
        Celebration message if new milestone, None otherwise
    """
    new_milestone = momentum.last_milestone
    
    if new_milestone > previous_milestone and new_milestone in MOMENTUM_CELEBRATIONS:
        return MOMENTUM_CELEBRATIONS[new_milestone]
    
    return None


def render_momentum_summary(
    habits_momentum: Dict[str, MomentumData]
):
    """
    Render a summary of all habits' momentum.
    
    Args:
        habits_momentum: Dictionary of habit_id to MomentumData
    """
    if not habits_momentum:
        st.info("No habits with momentum data yet. Complete habits to build momentum!")
        return
    
    # Count by phase
    phases_count = {
        "momentum": 0,      # Day 4+
        "critical": 0,      # Day 3
        "novelty": 0,       # Days 1-2
        "not_started": 0    # Day 0
    }
    
    for hid, momentum in habits_momentum.items():
        phase = _get_phase_info(momentum)["key"]
        phases_count[phase] = phases_count.get(phase, 0) + 1
    
    # Display summary
    cols = st.columns(4)
    
    with cols[0]:
        st.metric("🎉 Momentum", phases_count.get("momentum", 0))
    with cols[1]:
        st.metric("🔥 Critical", phases_count.get("critical", 0))
    with cols[2]:
        st.metric("🌱 Building", phases_count.get("novelty", 0))
    with cols[3]:
        st.metric("⏳ Not Started", phases_count.get("not_started", 0))


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def _get_phase_info(momentum: MomentumData) -> Dict:
    """
    Get phase information for display.
    
    Returns:
        Dictionary with name, color, icon, description
    """
    day = momentum.current_day
    
    if day == 0:
        return {
            "key": "not_started",
            "name": "Not Started",
            "color": "#6b7280",
            "icon": "⏳",
            "description": "Start today to build momentum!"
        }
    elif day <= 2:
        return {
            "key": "novelty",
            "name": "Novelty Phase",
            "color": "#3b82f6",
            "icon": "🌱",
            "description": "Building new neural pathways"
        }
    elif day == 3:
        return {
            "key": "critical",
            "name": "Critical Point",
            "color": "#f59e0b",
            "icon": "⚡",
            "description": "Most people quit here. You're stronger!"
        }
    elif day >= MOMENTUM_THRESHOLD_DAY:
        return {
            "key": "momentum",
            "name": "Momentum Achieved!",
            "color": "#10b981",
            "icon": "🚀",
            "description": "Habit becoming automatic"
        }
    
    return {
        "key": "unknown",
        "name": "Building",
        "color": "#6b7280",
        "icon": "💪",
        "description": "Keep going!"
    }


def _render_days_indicator(current_day: int) -> str:
    """
    Render visual indicator for days 1-4+.
    
    Args:
        current_day: Current momentum day
        
    Returns:
        HTML string for the days indicator
    """
    days_html = '<div style="display: flex; gap: 0.5rem; margin: 0.5rem 0;">'
    
    for day in range(1, 5):
        if day < current_day:
            # Completed
            days_html += f'''
            <div style="
                flex: 1;
                padding: 0.5rem;
                border-radius: 0.25rem;
                background: #10b981;
                color: white;
                text-align: center;
                font-weight: bold;
            ">✓</div>'''
        elif day == current_day:
            # Current day
            days_html += f'''
            <div style="
                flex: 1;
                padding: 0.5rem;
                border-radius: 0.25rem;
                background: #f59e0b;
                color: white;
                text-align: center;
                font-weight: bold;
                animation: pulse 2s infinite;
            ">D{day}</div>'''
        else:
            # Future day
            days_html += f'''
            <div style="
                flex: 1;
                padding: 0.5rem;
                border-radius: 0.25rem;
                background: rgba(255,255,255,0.1);
                color: rgba(255,255,255,0.5);
                text-align: center;
            ">D{day}</div>'''
    
    days_html += '</div>'
    
    # Add CSS animation
    st.markdown("""
    <style>
    @keyframes pulse {
        0% { transform: scale(1); }
        50% { transform: scale(1.05); }
        100% { transform: scale(1); }
    }
    </style>
    """, unsafe_allow_html=True)
    
    return days_html


# =============================================================================
# SESSION STATE MANAGEMENT
# =============================================================================

@st.cache_data
def get_momentum_tracker() -> MomentumTracker:
    """
    Get or create the momentum tracker from session state.
    
    Returns:
        The MomentumTracker instance
    """
    if "momentum_tracker" not in st.session_state:
        st.session_state.momentum_tracker = MomentumTracker()
    
    return st.session_state.momentum_tracker


def update_habit_momentum(habit_id: str, completion_date: date = None) -> MomentumData:
    """
    Update momentum when a habit is completed.
    
    Args:
        habit_id: The habit being completed
        completion_date: The date of completion (default: today)
        
    Returns:
        Updated MomentumData
    """
    tracker = get_momentum_tracker()
    return tracker.update_on_completion(habit_id, completion_date)


def get_habit_momentum(habit_id: str) -> MomentumData:
    """
    Get momentum data for a habit.
    
    Args:
        habit_id: The habit ID
        
    Returns:
        MomentumData for the habit
    """
    tracker = get_momentum_tracker()
    return tracker.get_momentum(habit_id)
