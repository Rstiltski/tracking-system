"""
Time Page - Time Tracking

Streamlit page for tracking time with a built-in timer and time categorization.

Usage:
    streamlit run tracking_app/pages/time.py
"""

import streamlit as st
from datetime import datetime, date, timedelta
from typing import List, Optional
import sys
import os
import time as time_module

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from tracking_app.storage import Storage, get_storage


# =============================================================================
# PAGE CONFIGURATION
# =============================================================================

st.set_page_config(
    page_title="Time - Veryfyn",
    page_icon="⏱️",
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
    
    # Timer state
    if 'timer_running' not in st.session_state:
        st.session_state.timer_running = False
    
    if 'timer_start' not in st.session_state:
        st.session_state.timer_start = None
    
    if 'timer_elapsed' not in st.session_state:
        st.session_state.timer_elapsed = 0
    
    if 'timer_category' not in st.session_state:
        st.session_state.timer_category = "General"
    
    # Time entries
    if 'time_entries' not in st.session_state:
        st.session_state.time_entries = []


# =============================================================================
# HELPER FUNCTIONS
# =============================================================================

def format_duration(seconds: int) -> str:
    """Format seconds into HH:MM:SS."""
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{secs:02d}"


def format_hours(hours: float) -> str:
    """Format hours into readable string."""
    if hours < 1:
        return f"{int(hours * 60)}m"
    return f"{hours:.1f}h"


def get_current_elapsed() -> int:
    """Get current elapsed time including running timer."""
    if st.session_state.timer_running and st.session_state.timer_start:
        additional = int(time_module.time() - st.session_state.timer_start)
        return st.session_state.timer_elapsed + additional
    return st.session_state.timer_elapsed


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
        storage = st.session_state.storage
        xp = storage.get_xp()
        level = storage.get_level()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Level", level)
        with col2:
            st.metric("XP", xp)
        
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
    st.title("⏱️ Time Tracking")
    st.markdown("Track your time with a built-in timer and categorize your activities.")


def render_timer():
    """Render the main timer interface."""
    st.subheader("⏱️ Timer")
    
    # Categories
    categories = ["General", "Work", "Learning", "Exercise", "Personal", "Break", "Other"]
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        st.session_state.timer_category = st.selectbox(
            "Category",
            categories,
            index=categories.index(st.session_state.timer_category) if st.session_state.timer_category in categories else 0
        )
    
    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        if st.button("➕ New Category", use_container_width=True):
            st.info("Add custom categories in settings.")
    
    # Timer display
    elapsed = get_current_elapsed()
    
    # Large timer display
    st.markdown(
        f"""
        <div style="
            text-align: center;
            font-size: 72px;
            font-family: monospace;
            padding: 20px;
            background: linear-gradient(135deg, #1e293b 0%, #334155 100%);
            border-radius: 15px;
            margin: 20px 0;
            color: {'#10b981' if st.session_state.timer_running else '#f8fafc'};
        ">
            {format_duration(elapsed)}
        </div>
        """,
        unsafe_allow_html=True
    )
    
    # Timer controls
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        if not st.session_state.timer_running:
            if st.button("▶️ Start", use_container_width=True, type="primary"):
                st.session_state.timer_running = True
                st.session_state.timer_start = time_module.time()
                st.rerun()
        else:
            if st.button("⏸️ Pause", use_container_width=True, type="primary"):
                st.session_state.timer_elapsed = get_current_elapsed()
                st.session_state.timer_running = False
                st.session_state.timer_start = None
                st.rerun()
    
    with col2:
        if st.session_state.timer_elapsed > 0 or st.session_state.timer_running:
            if st.button("⏹️ Stop & Save", use_container_width=True):
                final_elapsed = get_current_elapsed()
                if final_elapsed > 0:
                    # Save time entry
                    entry = {
                        "id": datetime.now().strftime("%Y%m%d%H%M%S"),
                        "date": date.today().isoformat(),
                        "category": st.session_state.timer_category,
                        "duration_hours": final_elapsed / 3600,
                        "duration_seconds": final_elapsed,
                        "timestamp": datetime.now().isoformat()
                    }
                    st.session_state.time_entries.append(entry)
                    
                    # Award XP
                    storage = st.session_state.storage
                    xp_earned = max(5, int(final_elapsed / 60))  # 1 XP per minute, min 5
                    storage.add_xp(xp_earned)
                    st.success(f"✅ Time entry saved! +{xp_earned} XP")
                
                # Reset timer
                st.session_state.timer_running = False
                st.session_state.timer_start = None
                st.session_state.timer_elapsed = 0
                st.rerun()
    
    with col3:
        if st.session_state.timer_elapsed > 0 or st.session_state.timer_running:
            if st.button("🔄 Reset", use_container_width=True):
                st.session_state.timer_running = False
                st.session_state.timer_start = None
                st.session_state.timer_elapsed = 0
                st.rerun()
    
    with col4:
        # Manual entry
        if st.button("📝 Manual Entry", use_container_width=True):
            st.session_state.show_manual_entry = True


def render_manual_entry():
    """Render manual time entry form."""
    if not st.session_state.get('show_manual_entry', False):
        return
    
    st.subheader("📝 Manual Time Entry")
    
    categories = ["General", "Work", "Learning", "Exercise", "Personal", "Break", "Other"]
    
    with st.form("manual_time_form"):
        col1, col2 = st.columns(2)
        
        with col1:
            entry_date = st.date_input("Date", value=date.today())
            category = st.selectbox("Category", categories)
        
        with col2:
            hours = st.number_input("Hours", min_value=0, max_value=24, value=0)
            minutes = st.number_input("Minutes", min_value=0, max_value=59, value=30)
        
        notes = st.text_input("Notes (optional)")
        
        col1, col2 = st.columns(2)
        
        with col1:
            if st.form_submit_button("Save Entry", type="primary"):
                duration_hours = hours + (minutes / 60)
                if duration_hours > 0:
                    entry = {
                        "id": datetime.now().strftime("%Y%m%d%H%M%S"),
                        "date": entry_date.isoformat(),
                        "category": category,
                        "duration_hours": duration_hours,
                        "duration_seconds": int(duration_hours * 3600),
                        "notes": notes,
                        "timestamp": datetime.now().isoformat(),
                        "manual": True
                    }
                    st.session_state.time_entries.append(entry)
                    
                    # Award XP
                    storage = st.session_state.storage
                    xp_earned = int(duration_hours * 10)  # 10 XP per hour
                    storage.add_xp(xp_earned)
                    st.success(f"✅ Entry saved! +{xp_earned} XP")
                
                st.session_state.show_manual_entry = False
                st.rerun()
        
        with col2:
            if st.form_submit_button("Cancel"):
                st.session_state.show_manual_entry = False
                st.rerun()


def render_daily_summary():
    """Render daily time summary."""
    st.subheader("📊 Today's Summary")
    
    today = date.today()
    today_entries = [
        e for e in st.session_state.time_entries 
        if e.get('date') == today.isoformat()
    ]
    
    if not today_entries:
        st.info("No time tracked today. Start the timer to begin!")
        return
    
    total_hours = sum(e['duration_hours'] for e in today_entries)
    
    # Summary by category
    category_totals = {}
    for entry in today_entries:
        cat = entry['category']
        if cat not in category_totals:
            category_totals[cat] = 0
        category_totals[cat] += entry['duration_hours']
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Total Time Tracked", format_hours(total_hours))
    
    with col2:
        st.metric("Entries", len(today_entries))
    
    # Category breakdown
    st.markdown("#### By Category")
    
    for cat, hours in sorted(category_totals.items(), key=lambda x: x[1], reverse=True):
        percentage = (hours / total_hours * 100) if total_hours > 0 else 0
        
        col1, col2, col3 = st.columns([3, 1, 1])
        
        with col1:
            st.progress(percentage / 100)
        
        with col2:
            st.caption(f"{cat}")
        
        with col3:
            st.caption(f"{format_hours(hours)} ({percentage:.0f}%)")


def render_weekly_chart():
    """Render weekly time distribution chart."""
    st.subheader("📈 Weekly Overview")
    
    # Get entries from the past 7 days
    today = date.today()
    week_start = today - timedelta(days=6)
    
    # Aggregate by day
    daily_totals = {}
    category_totals = {}
    
    for i in range(7):
        day = week_start + timedelta(days=i)
        daily_totals[day] = 0
    
    for entry in st.session_state.time_entries:
        entry_date = date.fromisoformat(entry['date'])
        if week_start <= entry_date <= today:
            daily_totals[entry_date] += entry['duration_hours']
            
            cat = entry['category']
            if cat not in category_totals:
                category_totals[cat] = 0
            category_totals[cat] += entry['duration_hours']
    
    # Create chart
    import pandas as pd
    
    df = pd.DataFrame([
        {'Date': d.strftime('%a'), 'Hours': h}
        for d, h in sorted(daily_totals.items())
    ])
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Daily Hours**")
        st.bar_chart(df.set_index('Date'))
    
    with col2:
        st.markdown("**By Category**")
        if category_totals:
            cat_df = pd.DataFrame([
                {'Category': cat, 'Hours': hours}
                for cat, hours in sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
            ])
            st.bar_chart(cat_df.set_index('Category'))
        else:
            st.info("No data yet")


def render_time_entries():
    """Render list of time entries."""
    st.subheader("📜 Recent Entries")
    
    if not st.session_state.time_entries:
        st.info("No time entries yet. Start tracking your time!")
        return
    
    # Sort by timestamp (newest first)
    entries = sorted(
        st.session_state.time_entries,
        key=lambda x: x.get('timestamp', ''),
        reverse=True
    )
    
    for entry in entries[:10]:  # Show last 10
        with st.container():
            col1, col2, col3, col4 = st.columns([2, 2, 2, 1])
            
            with col1:
                entry_date = date.fromisoformat(entry['date'])
                st.markdown(f"**{entry_date.strftime('%b %d')}**")
            
            with col2:
                st.markdown(f"📁 {entry['category']}")
            
            with col3:
                st.markdown(f"⏱️ {format_hours(entry['duration_hours'])}")
            
            with col4:
                if st.button("🗑️", key=f"delete_time_{entry['id']}", help="Delete entry"):
                    st.session_state.time_entries.remove(entry)
                    st.rerun()
        
        st.divider()


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
    
    # Timer
    render_timer()
    st.divider()
    
    # Manual entry
    render_manual_entry()
    
    # Daily summary
    render_daily_summary()
    st.divider()
    
    # Weekly chart
    render_weekly_chart()
    st.divider()
    
    # Time entries
    render_time_entries()


if __name__ == "__main__":
    main()